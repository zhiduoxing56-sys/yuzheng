from __future__ import annotations

from pathlib import Path
from time import perf_counter

from app.core.config import PROJECT_ROOT, load_yaml
from app.models.schemas import (
    AdvancedReasoningResult,
    AuditQualityMetadata,
    AuditRecord,
    AuditRecordQuality,
    CurrentEvidenceResponse,
    EvidenceEdge,
    EvidenceNode,
    EvidenceRelation,
    EvidenceSubgraph,
    IndexStatus,
    TextCommandRequest,
    TextCommandResponse,
    TranscriptionResult,
    TurnTiming,
    VoiceTrustResult,
    make_id,
    utc_now,
)
from app.services.audit.repository import AuditRepository
from app.services.causal.service import CausalCorrectionService
from app.services.decision.engine import DecisionService
from app.services.decision.safety_gate import SafetyGateService
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.recall import MandatoryRecallService
from app.services.evidence.repository import EvidenceRepository
from app.services.graph.builder import EvidenceSubgraphBuilder
from app.services.index.hnsw import HNSWIndexService
from app.services.memory.service import DualMemoryService
from app.services.quality.evaluator import EvidenceQualityService
from app.services.quality.window import EvidenceQualityWindow
from app.services.semantic.parser import SemanticFrameParser
from app.services.validation.advanced import AdvancedValidationService
from app.services.vector.embedding import build_embedding_service
from app.services.vehicle.simulator import SimulatorVehicleAdapter


class CommandPipeline:
    """Stage-three deterministic command pipeline.

    The hard gate is evaluated independently and after all evidence validation.
    Its result always overrides the five-factor soft score.
    """

    def __init__(self, database_path: Path | None = None) -> None:
        quality_config = load_yaml("evidence_quality.yaml")
        self.vehicle = SimulatorVehicleAdapter()
        self.parser = SemanticFrameParser(load_yaml("semantic_rules.yaml"))
        self.embedder = build_embedding_service(load_yaml("embedding.yaml"))
        self.demand_service = EvidenceDemandService(
            load_yaml("action_evidence_map.yaml"), self.embedder
        )
        self.evidence_repository = EvidenceRepository(quality_config)
        safety_config = load_yaml("safety_rules.yaml")
        self._safety_rule_nodes = self.evidence_repository.ingest_safety_rules(
            safety_config.get("rules", [])
        )
        self.index = HNSWIndexService(load_yaml("index.yaml"), self.embedder)
        self.recall_service = MandatoryRecallService(self.evidence_repository, self.embedder)
        self.quality_service = EvidenceQualityService(quality_config)
        self.quality_window = EvidenceQualityWindow(
            int(quality_config.get("window", {}).get("short_length", 8))
        )
        self.graph_builder = EvidenceSubgraphBuilder()
        self.memory_service = DualMemoryService(load_yaml("memory.yaml"))
        self.validation_service = AdvancedValidationService(load_yaml("jailbreak_policy.yaml"))
        self.causal_service = CausalCorrectionService(load_yaml("causal_policy.yaml"))
        self.gate_service = SafetyGateService(safety_config)
        self.decision_service = DecisionService(load_yaml("decision_policy.yaml"))
        self.audit_repository = AuditRepository(
            database_path or PROJECT_ROOT / "data" / "database" / "yuzheng.db"
        )
        self._refresh_causal_model()
        seed_nodes = self.evidence_repository.ingest_vehicle_state(
            self.vehicle.get_state(),
            {"speaker_role": "driver", "speaker_zone": "driver"},
            "SYSTEM_SEED",
        )
        self.index.build([*self._safety_rule_nodes, *seed_nodes])
        self._subgraphs: dict[str, EvidenceSubgraph] = {}
        self._turns: dict[str, TextCommandResponse] = {}

    def _refresh_causal_model(self) -> IndexStatus | object:
        status = self.audit_repository.learning_status()
        return self.causal_service.rebuild(
            self.audit_repository.learning_records(), status.excluded_record_count
        )

    @staticmethod
    def _candidate_copy(node: EvidenceNode, similarity: float) -> EvidenceNode:
        return node.model_copy(
            update={
                "semantic_similarity": round(similarity, 6),
                "metadata": {**node.metadata, "retrieval_origin": "semantic_retrieval"},
            }
        )

    @staticmethod
    def _merge_latest(*groups: list[EvidenceNode]) -> list[EvidenceNode]:
        merged: dict[str, EvidenceNode] = {}
        for group in groups:
            for node in group:
                merged[node.node_id] = node
        return list(merged.values())

    @staticmethod
    def _add_memory_edges(
        subgraph: EvidenceSubgraph, memory
    ) -> EvidenceSubgraph:
        edges = list(subgraph.edges)
        existing_nodes = {node.node_id for node in subgraph.nodes}
        for link in [*memory.horizontal_links, *memory.vertical_links]:
            if link.source not in existing_nodes or link.target not in existing_nodes:
                continue
            edges.append(
                EvidenceEdge(
                    source=link.source,
                    target=link.target,
                    relation=link.relation,
                    weight=link.weight,
                    reason=link.reason,
                )
            )
        return subgraph.model_copy(update={"edges": edges})

    def _new_audit_quality(self, audit_id: str) -> AuditQualityMetadata:
        test_only = self.audit_repository.database_path.name != "yuzheng.db"
        index_status = self.index.status()
        real_stack = (
            getattr(self.embedder, "model_name", "") == "BAAI/bge-base-zh-v1.5"
            and index_status.implementation == "hnswlib"
            and not index_status.degraded
        )
        if test_only:
            quality = AuditRecordQuality.TEST_ONLY
            reasons = ["isolated test database"]
        elif not real_stack:
            quality = AuditRecordQuality.LEGACY_MODEL
            reasons = ["real BGE and hnswlib stack was not simultaneously active"]
        else:
            quality = AuditRecordQuality.VALID
            reasons = []
        return AuditQualityMetadata(
            audit_id=audit_id,
            record_quality=quality,
            eligible_for_learning=quality == AuditRecordQuality.VALID,
            exclusion_reasons=reasons,
            implementation_stage="stage3",
            pipeline_version="3.0.0",
            schema_version="3.0",
        )

    def process_text(self, request: TextCommandRequest) -> TextCommandResponse:
        overall_started = perf_counter()
        turn_started_at = utc_now()
        turn_id = make_id("TURN")
        state = (
            self.vehicle.update_state(request.state_overrides)
            if request.state_overrides is not None
            else self.vehicle.get_state()
        )
        input_trust = VoiceTrustResult(
            turn_id=turn_id,
            audio_source="text_api",
            speaker_zone=request.speaker_zone,
            speaker_role=request.speaker_role,
            la_score=0.0,
            pa_score=0.0,
            replay_risk=0.0,
            synthetic_risk=0.0,
            zone_risk=0.0,
            trust_score=1.0,
            input_trust_label="NOT_APPLICABLE_TEXT_INPUT",
            audio_fingerprint="",
        )
        transcription = TranscriptionResult(
            turn_id=turn_id,
            text=request.text,
            confidence=1.0,
            adapter="text_passthrough",
            model_inference_performed=False,
        )
        frame = self.parser.parse(turn_id, request.text)
        frame, demand = self.demand_service.build(frame)

        snapshot_nodes = self.evidence_repository.ingest_vehicle_state(
            state,
            {"speaker_role": request.speaker_role, "speaker_zone": request.speaker_zone},
            turn_id,
        )
        state_snapshot_at = max(node.timestamp for node in snapshot_nodes)
        decision_reference_time = state_snapshot_at
        override_nodes = self.evidence_repository.ingest_observations(
            request.evidence_overrides, turn_id
        )
        self.index.upsert([*snapshot_nodes, *override_nodes])
        search_results, retrieval_metadata = self.index.search(demand.query_vector)
        candidate_evidence = [
            self._candidate_copy(node, similarity) for node, similarity in search_results
        ]
        evidence, recall_records, recalled_types, missing_types = self.recall_service.supplement(
            candidate_evidence,
            demand.required_types,
            demand.query_vector,
            turn_id,
        )
        existing_ids = {node.node_id for node in evidence}
        for evidence_type in demand.required_types:
            # Keep at most two observations per source in this turn's graph so
            # temporal edges remain explainable after canonical HNSW updates.
            # This bounded history is never written back to the global index.
            for node in self.evidence_repository.recent_per_source(
                evidence_type, limit_per_source=2
            ):
                if node.node_id not in existing_ids:
                    evidence.append(
                        node.model_copy(
                            update={
                                "mandatory": False,
                                "metadata": {
                                    **node.metadata,
                                    "runtime_graph_history": True,
                                },
                            }
                        )
                    )
                    existing_ids.add(node.node_id)

        quality_started = perf_counter()
        evaluated, quality_metrics, physical_conflicts = self.quality_service.evaluate(
            evidence, demand.required_types, now=decision_reference_time
        )
        quality_ms = (perf_counter() - quality_started) * 1000
        self.evidence_repository.update_nodes(evaluated)
        self.quality_window.update(evaluated, physical_conflicts)
        quality_metrics = quality_metrics.model_copy(
            update={
                "short_term_availability": self.quality_window.short_term_availability(),
                "long_term_availability": self.quality_window.long_term_availability(),
            }
        )

        reasoning_evidence = self._merge_latest(snapshot_nodes, override_nodes, evaluated)
        memory = self.memory_service.propagate(reasoning_evidence, frame, physical_conflicts)
        causal = self.causal_service.apply(frame, evaluated, memory)
        validation = self.validation_service.validate(frame, reasoning_evidence, physical_conflicts)
        gate = self.gate_service.evaluate(frame, reasoning_evidence, validation, memory)
        scoring_started = perf_counter()
        decision = self.decision_service.decide(
            frame, reasoning_evidence, gate, validation, causal, memory
        )
        scoring_ms = (perf_counter() - scoring_started) * 1000
        advanced = AdvancedReasoningResult(
            memory_propagation=memory,
            causal_correction=causal,
            validation=validation,
            five_factor_score=decision.score_factors.five_factors,
            decision_confidence=causal.decision_confidence,
            explanations=decision.explanations,
            recognized_command={
                "action": frame.action,
                "target": frame.target,
                "risk_level": frame.risk_level,
                "retrieval_scope": demand.retrieval_scope,
            },
            mandatory_evidence_complete=not missing_types,
            supporting_evidence_ids=[
                node.node_id
                for node in evaluated
                if node.mandatory and node.quality_label.value in {"VALID", "SUSPICIOUS"}
            ],
            conflicting_evidence_ids=sorted(
                {
                    node_id
                    for conflict in validation.conflicts
                    for node_id in conflict.evidence_node_ids
                }
            ),
            hit_rules=gate.hit_rules,
            review_question=decision.review_question,
            performance_ms={
                "quality": round(quality_ms, 4),
                "horizontal_memory": memory.horizontal_duration_ms,
                "vertical_propagation": memory.vertical_duration_ms,
                "memory_total": memory.duration_ms,
                "causal": causal.duration_ms,
                "validation": validation.duration_ms,
                "scoring": round(scoring_ms, 4),
            },
        )
        decision = decision.model_copy(update={"advanced_reasoning": advanced})

        subgraph = self.graph_builder.build(
            frame,
            demand,
            evaluated,
            recall_records,
            recalled_types,
            missing_types,
            quality_metrics,
            retrieval_metadata,
            physical_conflicts,
            self._safety_rule_nodes,
        )
        subgraph = self._add_memory_edges(subgraph, memory).model_copy(
            update={
                "corrected_weights": causal.corrected_weights,
                "decision_confidence": causal.decision_confidence,
                "advanced_reasoning_applied": True,
                "advanced_reasoning_status": causal.data_sufficiency,
            }
        )
        self._subgraphs[turn_id] = subgraph

        completed_at = utc_now()
        timing = TurnTiming(
            turn_started_at=turn_started_at,
            state_snapshot_at=state_snapshot_at,
            decision_reference_time=decision_reference_time,
            completed_at=completed_at,
            end_to_end_ms=round((perf_counter() - overall_started) * 1000, 4),
        )
        audit_id = make_id("AUD")
        audit = AuditRecord(
            audit_id=audit_id,
            turn_id=turn_id,
            input_trust_result=input_trust,
            transcription_result=transcription,
            semantic_frame=frame,
            evidence_demand=demand,
            candidate_recall_results=candidate_evidence,
            mandatory_supplement_records=[record.model_dump(mode="json") for record in recall_records],
            vectorization_metadata=demand.vectorization_metadata,
            query_vector_digest=(demand.vectorization_metadata.vector_digest if demand.vectorization_metadata else ""),
            retrieval_metadata=retrieval_metadata,
            mandatory_recall_records=recall_records,
            missing_evidence_types=missing_types,
            evidence_subgraph=subgraph,
            evidence_subgraph_summary={
                "graph_id": subgraph.graph_id,
                "node_count": len(subgraph.nodes),
                "edge_count": len(subgraph.edges),
                "missing_types": subgraph.missing_types,
            },
            evidence_quality_metrics=quality_metrics,
            conflict_records=physical_conflicts,
            safety_gate_result=gate,
            score_details=decision.score_factors,
            final_decision=decision,
            audit_quality=self._new_audit_quality(audit_id),
            horizontal_memory=memory.horizontal_links,
            vertical_propagation=memory.vertical_links,
            causal_candidate_edges=causal.candidate_edges,
            causal_pruned_edges=causal.pruned_edges,
            causal_removed_edges=causal.removed_edges,
            causal_posterior=causal.posterior_weights,
            causal_entropy=causal.entropy,
            decision_confidence=causal.decision_confidence,
            context_claims=validation.context_claims,
            grounding_failures=validation.grounding_failures,
            jailbreak_conflicts=validation.conflicts,
            jailbreak_risk=validation.jailbreak_risk,
            complete_gate_result=gate,
            five_factor_score=decision.score_factors.five_factors,
            advanced_explanations=decision.explanations,
            memory_propagation=memory,
            causal_correction=causal,
            advanced_reasoning=advanced,
            turn_timing=timing,
        )
        saved_audit = self.audit_repository.save(audit)
        response = TextCommandResponse(
            turn_id=turn_id,
            input_trust_result=input_trust,
            transcription_result=transcription,
            semantic_frame=frame,
            evidence_demand=demand,
            evidence=evaluated,
            query_vector=demand.query_vector,
            retrieval_metadata=retrieval_metadata,
            candidate_evidence=candidate_evidence,
            mandatory_recall_records=recall_records,
            evidence_subgraph=subgraph,
            quality_metrics=quality_metrics,
            safety_gate=gate,
            decision=decision,
            audit=saved_audit,
            actionable=demand.retrieval_scope == "control_evidence",
            retrieval_scope=demand.retrieval_scope,
            advanced_reasoning=advanced,
            memory_propagation=memory,
            causal_correction=causal,
            grounding_failures=validation.grounding_failures,
            jailbreak_conflicts=validation.conflicts,
            jailbreak_risk=validation.jailbreak_risk,
            score_factors=decision.score_factors.five_factors,
            decision_confidence=causal.decision_confidence,
            turn_timing=timing,
        )
        self._turns[turn_id] = response
        return response

    def current_evidence(self) -> CurrentEvidenceResponse:
        nodes = self.evidence_repository.current_nodes()
        return CurrentEvidenceResponse(
            nodes=nodes,
            evidence_type_count=len({node.evidence_type for node in nodes}),
            node_count=len(nodes),
            short_term_availability=self.quality_window.short_term_availability(),
            long_term_availability=self.quality_window.long_term_availability(),
        )

    def get_subgraph(self, turn_id: str) -> EvidenceSubgraph | None:
        if turn_id in self._subgraphs:
            return self._subgraphs[turn_id]
        audit = self.audit_repository.get_by_turn(turn_id)
        return audit.evidence_subgraph if audit else None

    def get_turn(self, turn_id: str) -> TextCommandResponse | AuditRecord | None:
        return self._turns.get(turn_id) or self.audit_repository.get_by_turn(turn_id)

    def get_reasoning(self, turn_id: str) -> AdvancedReasoningResult | None:
        turn = self.get_turn(turn_id)
        if turn is None:
            return None
        return turn.advanced_reasoning

    def rebuild_index(self, exclude_types: list[str] | None = None) -> IndexStatus:
        return self.index.build(self.evidence_repository.all_nodes(), exclude_types)

    def rebuild_causal(self):
        return self._refresh_causal_model()
