from __future__ import annotations

from pathlib import Path

from app.core.config import PROJECT_ROOT, load_yaml
from app.models.schemas import (
    AuditRecord,
    CurrentEvidenceResponse,
    EvidenceNode,
    EvidenceSubgraph,
    IndexStatus,
    TextCommandRequest,
    TextCommandResponse,
    TranscriptionResult,
    VoiceTrustResult,
    make_id,
)
from app.services.audit.repository import AuditRepository
from app.services.decision.engine import DecisionService
from app.services.decision.safety_gate import SafetyGateService
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.recall import MandatoryRecallService
from app.services.evidence.repository import EvidenceRepository
from app.services.graph.builder import EvidenceSubgraphBuilder
from app.services.index.hnsw import HNSWIndexService
from app.services.quality.evaluator import EvidenceQualityService
from app.services.quality.window import EvidenceQualityWindow
from app.services.semantic.parser import SemanticFrameParser
from app.services.vector.embedding import build_embedding_service
from app.services.vehicle.simulator import SimulatorVehicleAdapter


class CommandPipeline:
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
        self.gate_service = SafetyGateService(safety_config)
        self.decision_service = DecisionService(load_yaml("decision_policy.yaml"))
        self.audit_repository = AuditRepository(
            database_path or PROJECT_ROOT / "data" / "database" / "yuzheng.db"
        )
        seed_nodes = self.evidence_repository.ingest_vehicle_state(
            self.vehicle.get_state(),
            {"occupant_role": "driver", "speaker_zone": "driver"},
            "SYSTEM_SEED",
        )
        self.index.build([*self._safety_rule_nodes, *seed_nodes])
        self._subgraphs: dict[str, EvidenceSubgraph] = {}

    @staticmethod
    def _candidate_copy(node: EvidenceNode, similarity: float) -> EvidenceNode:
        return node.model_copy(
            update={
                "semantic_similarity": round(similarity, 6),
                "metadata": {**node.metadata, "retrieval_origin": "semantic_retrieval"},
            }
        )

    def process_text(self, request: TextCommandRequest) -> TextCommandResponse:
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
            {"occupant_role": request.speaker_role, "speaker_zone": request.speaker_zone},
            turn_id,
        )
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

        # 对强制类型展开同一时间窗口的多来源节点，避免只保留一个来源而隐藏冲突。
        existing_ids = {node.node_id for node in evidence}
        for evidence_type in demand.required_types:
            for node in self.evidence_repository.latest_per_source(evidence_type):
                if node.node_id not in existing_ids:
                    evidence.append(node.model_copy(update={"mandatory": False}))
                    existing_ids.add(node.node_id)

        evaluated, quality_metrics, conflicts = self.quality_service.evaluate(
            evidence, demand.required_types
        )
        self.evidence_repository.update_nodes(evaluated)
        self.quality_window.update(evaluated, conflicts)
        quality_metrics = quality_metrics.model_copy(
            update={
                "short_term_availability": self.quality_window.short_term_availability(),
                "long_term_availability": self.quality_window.long_term_availability(),
            }
        )
        subgraph = self.graph_builder.build(
            frame,
            demand,
            evaluated,
            recall_records,
            recalled_types,
            missing_types,
            quality_metrics,
            retrieval_metadata,
            conflicts,
            self._safety_rule_nodes,
        )
        self._subgraphs[turn_id] = subgraph

        gate = self.gate_service.evaluate(frame, evaluated)
        decision = self.decision_service.decide(frame, evaluated, gate)
        vector_metadata = demand.vectorization_metadata
        audit = AuditRecord(
            turn_id=turn_id,
            input_trust_result=input_trust,
            transcription_result=transcription,
            semantic_frame=frame,
            evidence_demand=demand,
            candidate_recall_results=candidate_evidence,
            mandatory_supplement_records=[record.model_dump(mode="json") for record in recall_records],
            vectorization_metadata=vector_metadata,
            query_vector_digest=vector_metadata.vector_digest if vector_metadata else "",
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
            conflict_records=conflicts,
            safety_gate_result=gate,
            score_details=decision.score_factors,
            final_decision=decision,
        )
        saved_audit = self.audit_repository.save(audit)
        return TextCommandResponse(
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
        )

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

    def rebuild_index(self, exclude_types: list[str] | None = None) -> IndexStatus:
        return self.index.build(self.evidence_repository.all_nodes(), exclude_types)
