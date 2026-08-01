from __future__ import annotations

from pathlib import Path
from threading import RLock
from time import perf_counter
from typing import Any, Callable

from app.core.config import PROJECT_ROOT, load_yaml
from app.models.schemas import (
    AdvancedReasoningResult,
    AuditQualityMetadata,
    AuditRecord,
    AuditRecordQuality,
    CurrentEvidenceResponse,
    DecisionLabel,
    EvidenceEdge,
    EvidenceNode,
    EvidenceObservationInput,
    EvidenceRelation,
    EvidenceSubgraph,
    IndexStatus,
    PipelineEvent,
    TextCommandRequest,
    TextCommandResponse,
    TranscriptionResult,
    TurnTimeline,
    TurnTiming,
    VehicleState,
    VehicleStatePatch,
    VoiceTrustResult,
    WorkflowEventType,
    make_id,
    utc_now,
)
from app.services.audit.repository import AuditRepository
from app.services.authorization.service import AuthorizationTokenError, AuthorizationTokenService
from app.services.causal.service import CausalCorrectionService
from app.services.decision.engine import DecisionService
from app.services.decision.safety_gate import SafetyGateService
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.recall import MandatoryRecallService
from app.services.evidence.repository import EvidenceRepository
from app.services.execution.service import ExecutionService
from app.services.graph.builder import EvidenceSubgraphBuilder
from app.services.index.hnsw import HNSWIndexService
from app.services.memory.service import DualMemoryService
from app.services.quality.evaluator import EvidenceQualityService
from app.services.quality.window import EvidenceQualityWindow
from app.services.review.service import ReviewService
from app.services.semantic.parser import SemanticFrameParser
from app.services.validation.advanced import AdvancedValidationService
from app.services.vector.embedding import build_embedding_service
from app.services.vehicle.simulator import SimulatorVehicleAdapter
from app.services.workflow.repository import WorkflowRepository
from app.websocket.broker import PipelineEventBroker
from app.core.redaction import SensitiveDataRedactor


class CommandPipeline:
    """Stage-three deterministic command pipeline.

    The hard gate is evaluated independently and after all evidence validation.
    Its result always overrides the five-factor soft score.
    """

    def __init__(
        self,
        database_path: Path | None = None,
        *,
        token_secret: bytes | None = None,
        event_broker: PipelineEventBroker | None = None,
    ) -> None:
        self._command_lock = RLock()
        quality_config = load_yaml("evidence_quality.yaml")
        self.vehicle_config = load_yaml("vehicle_actions.yaml")
        self.vehicle = SimulatorVehicleAdapter(action_config=self.vehicle_config)
        self.event_broker = event_broker or PipelineEventBroker()
        self.review_config = load_yaml("review_policy.yaml")
        self.scenario_config = load_yaml("demo_scenarios.yaml")
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
        self.workflow_repository = WorkflowRepository(self.audit_repository.database_path)
        self.authorization_service = AuthorizationTokenService(
            load_yaml("authorization.yaml"),
            self.workflow_repository,
            secret=token_secret,
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
        self.review_service = ReviewService(self, self.review_config)
        self.execution_service = ExecutionService(self)

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
            implementation_stage="stage4",
            pipeline_version="4.0.0",
            schema_version="4.0",
        )

    def process_text(
        self,
        request: TextCommandRequest,
        *,
        root_turn_id: str | None = None,
        parent_turn_id: str | None = None,
        attempt_no: int = 0,
        workflow_type: str = "INITIAL",
        confirmed: bool = False,
        suppress_authorization: bool = False,
        event_sink: Callable[[PipelineEvent], None] | None = None,
    ) -> TextCommandResponse:
        # Preserve Pydantic's fields-set information on VehicleStatePatch: rebuilding
        # the whole request would turn every omitted state field into an explicit null.
        request = request.model_copy(
            update={
                "text": SensitiveDataRedactor.redact_text(request.text),
                "speaker_zone": SensitiveDataRedactor.redact_text(request.speaker_zone),
                "speaker_role": SensitiveDataRedactor.redact_text(request.speaker_role),
                "session_id": (
                    SensitiveDataRedactor.redact_text(request.session_id)
                    if request.session_id
                    else None
                ),
                "evidence_overrides": [
                    item.model_copy(
                        update=SensitiveDataRedactor.redact(item.model_dump(mode="json"))
                    )
                    for item in request.evidence_overrides
                ],
            }
        )
        turn_id = make_id("TURN")
        root_turn_id = root_turn_id or turn_id
        sequence = 0
        sink = event_sink or self.event_broker.publish
        event_started = perf_counter()

        def emit(stage: str, summary: str, payload: dict[str, Any] | None = None) -> None:
            nonlocal sequence, event_started
            if request.session_id is None:
                return
            now = perf_counter()
            sequence += 1
            sink(
                PipelineEvent(
                    session_id=request.session_id,
                    turn_id=turn_id,
                    sequence=sequence,
                    stage=stage,
                    duration_ms=round((now - event_started) * 1000, 4),
                    summary=summary,
                    payload=payload or {},
                )
            )
            event_started = now

        emit("INPUT_RECEIVED", "文本指令已接收", {"input_source": "text_api"})
        try:
            with self._command_lock:
                return self._process_text_locked(
                    request,
                    turn_id=turn_id,
                    root_turn_id=root_turn_id,
                    parent_turn_id=parent_turn_id,
                    attempt_no=attempt_no,
                    workflow_type=workflow_type,
                    confirmed=confirmed,
                    suppress_authorization=suppress_authorization,
                    emit=emit,
                )
        except Exception as exc:
            emit(
                "PIPELINE_FAILED",
                "流水线处理失败",
                {
                    "error_type": type(exc).__name__,
                    "message": SensitiveDataRedactor.redact_exception(exc),
                },
            )
            raise

    def _process_text_locked(
        self,
        request: TextCommandRequest,
        *,
        turn_id: str,
        root_turn_id: str,
        parent_turn_id: str | None,
        attempt_no: int,
        workflow_type: str,
        confirmed: bool,
        suppress_authorization: bool,
        emit: Callable[[str, str, dict[str, Any] | None], None],
    ) -> TextCommandResponse:
        overall_started = perf_counter()
        turn_started_at = utc_now()
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
        emit("TRUST_CHECKED", "文本输入无需声学可信检查", {"label": input_trust.input_trust_label})
        transcription = TranscriptionResult(
            turn_id=turn_id,
            text=request.text,
            confidence=1.0,
            adapter="text_passthrough",
            model_inference_performed=False,
        )
        emit("ASR_COMPLETED", "文本直通，无 ASR 模型推理", {"adapter": transcription.adapter})
        frame = self.parser.parse(turn_id, request.text)
        if confirmed and frame.action != "unknown" and frame.target != "unknown":
            frame = frame.model_copy(
                update={
                    "semantic_confidence": max(
                        float(self.review_config.get("confirm_semantic_confidence_floor", 0.95)),
                        frame.semantic_confidence,
                    ),
                    "ambiguity_score": frame.ambiguity_score
                    * float(self.review_config.get("confirm_ambiguity_multiplier", 0.5)),
                }
            )
        frame, demand = self.demand_service.build(frame)
        emit(
            "SEMANTIC_PARSED",
            "语义帧已生成",
            {"action": frame.action, "target": frame.target, "risk_level": frame.risk_level},
        )

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
        emit(
            "EVIDENCE_RETRIEVED",
            "语义候选检索完成",
            {"candidate_count": len(candidate_evidence), "implementation": retrieval_metadata.implementation},
        )
        evidence, recall_records, recalled_types, missing_types = self.recall_service.supplement(
            candidate_evidence,
            demand.required_types,
            demand.query_vector,
            turn_id,
        )
        emit(
            "MANDATORY_SUPPLEMENTED",
            "强制证据覆盖检查完成",
            {"recalled_types": recalled_types, "missing_types": missing_types},
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
        emit(
            "GRAPH_BUILT",
            "运行时证据子图已构建",
            {"node_count": len(subgraph.nodes), "edge_count": len(subgraph.edges)},
        )

        reasoning_evidence = self._merge_latest(snapshot_nodes, override_nodes, evaluated)
        memory = self.memory_service.propagate(reasoning_evidence, frame, physical_conflicts)
        emit(
            "MEMORY_PROPAGATED",
            "横向与纵向记忆传播完成",
            {
                "horizontal_links": len(memory.horizontal_links),
                "vertical_links": len(memory.vertical_links),
            },
        )
        causal = self.causal_service.apply(frame, evaluated, memory)
        emit(
            "CAUSAL_CORRECTED",
            "因果贝叶斯修正完成",
            {"sample_count": causal.sample_count, "feature_cutoff": causal.feature_cutoff},
        )
        validation = self.validation_service.validate(frame, reasoning_evidence, physical_conflicts)
        emit(
            "EVIDENCE_VALIDATED",
            "证据与上下文声明校验完成",
            {"conflict_count": validation.conflict_count, "jailbreak_risk": validation.jailbreak_risk},
        )
        gate = self.gate_service.evaluate(frame, reasoning_evidence, validation, memory)
        emit(
            "GATE_CHECKED",
            "硬性安全门检查完成",
            {"gate_blocked": gate.blocked, "hit_rules": gate.hit_rules},
        )
        scoring_started = perf_counter()
        decision = self.decision_service.decide(
            frame, reasoning_evidence, gate, validation, causal, memory
        )
        emit(
            "DECISION_COMPLETED",
            "最终裁决完成",
            {
                "final_decision": decision.final_decision.value,
                "soft_safety_score": decision.soft_safety_score,
                "gate_blocked": decision.gate_blocked,
            },
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
            root_turn_id=root_turn_id,
            parent_turn_id=parent_turn_id,
            attempt_no=attempt_no,
            workflow_type=workflow_type,
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
        emit(
            "AUDIT_SAVED",
            "裁决审计已追加保存",
            {"audit_id": saved_audit.audit_id, "current_hash": saved_audit.current_hash},
        )
        actionable = demand.retrieval_scope == "control_evidence"
        if decision.final_decision == DecisionLabel.REVIEW:
            self.workflow_repository.append_event(
                root_turn_id=root_turn_id,
                related_turn_id=turn_id,
                parent_turn_id=parent_turn_id,
                event_type=WorkflowEventType.REVIEW_REQUESTED,
                payload={
                    "review_question": decision.review_question,
                    "action": frame.action,
                    "target": frame.target,
                    "attempt_no": attempt_no,
                },
            )
            emit(
                "REVIEW_REQUIRED",
                "当前轮次需要用户复核",
                {"review_question": decision.review_question},
            )

        response_decision = decision
        if (
            not suppress_authorization
            and decision.final_decision == DecisionLabel.PASS
            and not decision.gate_blocked
            and actionable
            and self.authorization_service.is_executable(frame)
        ):
            try:
                grant = self.authorization_service.issue(
                    root_turn_id=root_turn_id,
                    turn_id=turn_id,
                    frame=frame,
                    state=state,
                )
                response_decision = decision.model_copy(
                    update={"authorization_token": grant.authorization_token}
                )
                emit(
                    "TOKEN_ISSUED",
                    "一次性车辆执行授权已签发",
                    {
                        "token_id": grant.metadata.token_id,
                        "expires_at": grant.metadata.expires_at.isoformat(),
                    },
                )
            except AuthorizationTokenError as exc:
                self.workflow_repository.append_event(
                    root_turn_id=root_turn_id,
                    related_turn_id=turn_id,
                    event_type=WorkflowEventType.TOKEN_REJECTED,
                    payload={"reason": str(exc)},
                )
        response = TextCommandResponse(
            turn_id=turn_id,
            root_turn_id=root_turn_id,
            parent_turn_id=parent_turn_id,
            attempt_no=attempt_no,
            workflow_type=workflow_type,
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
            decision=response_decision,
            audit=saved_audit,
            actionable=actionable,
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
        # 原始令牌只存在于本次返回对象；内存缓存与 SQLite 均保存去敏版本。
        self._turns[turn_id] = response.model_copy(
            update={
                "decision": response.decision.model_copy(
                    update={"authorization_token": None}
                )
            }
        )
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

    def get_vehicle_state(self) -> VehicleState:
        return self.vehicle.get_state()

    def update_vehicle_state(self, patch: VehicleStatePatch) -> VehicleState:
        with self._command_lock:
            state = self.vehicle.update_state(patch)
            nodes = self.evidence_repository.ingest_vehicle_state(
                state,
                {
                    "speaker_role": state.occupant_role or "unknown",
                    "speaker_zone": state.speaker_zone or "unknown",
                },
                make_id("STATE_UPDATE"),
            )
            self.index.upsert(nodes)
            return state

    def reset_vehicle_state(self) -> VehicleState:
        with self._command_lock:
            state = self.vehicle.reset()
            nodes = self.evidence_repository.ingest_vehicle_state(
                state,
                {"speaker_role": "driver", "speaker_zone": "driver"},
                make_id("STATE_RESET"),
            )
            self.index.upsert(nodes)
            return state

    def scenarios(self) -> list[dict[str, Any]]:
        values = self.scenario_config.get("scenarios", {})
        return [
            {
                "scenario_id": scenario_id,
                "name": scenario.get("name", scenario_id),
                "text": scenario.get("text", ""),
            }
            for scenario_id, scenario in values.items()
        ]

    def load_scenario(self, scenario_id: str) -> VehicleState:
        scenario = self.scenario_config.get("scenarios", {}).get(scenario_id)
        if scenario is None:
            raise KeyError(f"未找到场景: {scenario_id}")
        with self._command_lock:
            self.evidence_repository.clear_explicit_observations()
            self.index.build([*self._safety_rule_nodes, *self.evidence_repository.current_nodes()])
            self.reset_vehicle_state()
            return self.update_vehicle_state(
                VehicleStatePatch.model_validate(scenario.get("state", {}))
            )

    def run_scenario(self, scenario_id: str, *, session_id: str | None = None) -> TextCommandResponse:
        scenario = self.scenario_config.get("scenarios", {}).get(scenario_id)
        if scenario is None:
            raise KeyError(f"未找到场景: {scenario_id}")
        state = self.load_scenario(scenario_id)
        observations = [
            EvidenceObservationInput.model_validate(value)
            for value in scenario.get("evidence_overrides", [])
        ]
        return self.process_text(
            TextCommandRequest(
                text=str(scenario.get("text", "")),
                speaker_role=state.occupant_role or "unknown",
                speaker_zone=state.speaker_zone or "unknown",
                evidence_overrides=observations,
                session_id=session_id,
            )
        )

    def timeline(self, turn_id: str) -> TurnTimeline:
        root = self.review_service.root_for_turn(turn_id)
        audits = self.audit_repository.records_for_root(root)
        if not audits:
            root_audit = self.audit_repository.get_by_turn(root)
            audits = [root_audit] if root_audit else []
        events = self.workflow_repository.events(root)
        ordered = [
            {
                "kind": "AUDIT",
                "timestamp": audit.created_at.isoformat(),
                "turn_id": audit.turn_id,
                "audit_id": audit.audit_id,
                "workflow_type": audit.workflow_type,
                "decision": audit.final_decision.final_decision.value,
            }
            for audit in audits
        ]
        ordered.extend(
            {
                "kind": "WORKFLOW_EVENT",
                "timestamp": event.created_at.isoformat(),
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "related_turn_id": event.related_turn_id,
                "sequence_no": event.sequence_no,
            }
            for event in events
        )
        ordered.sort(key=lambda item: (item["timestamp"], item["kind"]))
        return TurnTimeline(
            root_turn_id=root,
            audits=audits,
            workflow_events=events,
            ordered_items=ordered,
            historical_execution_state=self.workflow_repository.executions(root),
            current_simulator_state=self.vehicle.get_state(),
        )
