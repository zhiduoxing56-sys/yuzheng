from __future__ import annotations

from pathlib import Path
from threading import RLock, Thread
from time import perf_counter
from typing import Any, Callable

from app.core.config import PROJECT_ROOT, load_yaml
from app.models.schemas import (
    AdvancedReasoningResult,
    AudioCommandResponse,
    AuditQualityMetadata,
    AuditRecord,
    AuditRecordQuality,
    CurrentEvidenceResponse,
    DecisionLabel,
    DecisionResult,
    DecisionScoreFactors,
    EvidenceDemand,
    EvidenceEdge,
    EvidenceNode,
    EvidenceObservationInput,
    EvidenceRelation,
    EvidenceSubgraph,
    EvidenceQualityMetrics,
    GateCheck,
    IndexStatus,
    PipelineEvent,
    RetrievalMetadata,
    RuntimeCapabilityStatus,
    SafetyGateResult,
    SemanticControlMode,
    TextCommandRequest,
    TextCommandResponse,
    TranscriptionResult,
    TurnTimeline,
    TurnTiming,
    VehicleState,
    VehicleStatePatch,
    VoiceTrustResult,
    SpectrumAnalysisResult,
    ZonePermissionResult,
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
from app.services.runtime.capability import RuntimeCapabilityService
from app.services.memory.service import DualMemoryService
from app.services.quality.evaluator import EvidenceQualityService
from app.services.quality.window import EvidenceQualityWindow
from app.services.review.service import ReviewService
from app.services.semantic.parser import SemanticFrameParser
from app.services.validation.advanced import AdvancedValidationService
from app.services.vector.embedding import build_embedding_service
from app.services.vehicle.simulator import SimulatorVehicleAdapter
from app.services.asr.whisper import ASRModelError, WhisperASRService
from app.services.voice.antispoof import Wav2Vec2AntiSpoofDetector
from app.services.voice.audio import AudioInputService, DecodedAudio
from app.services.voice.spectrum import SpectrumAnalyzer
from app.services.voice.trust import VoiceTrustScorer
from app.services.voice.zone import ZonePermissionService
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
        self.voice_config = load_yaml("voice.yaml")
        self.audio_input_service = AudioInputService(self.voice_config["audio"])
        self.spectrum_analyzer = SpectrumAnalyzer(self.voice_config["spectrum"])
        anomaly_penalty = float(
            self.voice_config["spectrum"].get("model_score_anomaly_penalty", 0.20)
        )
        self.la_detector = Wav2Vec2AntiSpoofDetector(
            self.voice_config["la"],
            detector_kind="LA",
            anomaly_penalty=anomaly_penalty,
            spectrum_auxiliary=self.voice_config["spectrum"].get("la_auxiliary"),
        )
        self.pa_detector = Wav2Vec2AntiSpoofDetector(
            self.voice_config["pa"],
            detector_kind="PA",
            anomaly_penalty=anomaly_penalty,
        )
        self.voice_trust_scorer = VoiceTrustScorer(self.voice_config["trust"])
        self.zone_permission_service = ZonePermissionService(
            self.voice_config["zone_permission"]
        )
        self.asr_service = WhisperASRService(self.voice_config["asr"])
        self.parser = SemanticFrameParser(load_yaml("semantic_rules.yaml"))
        self.embedder = build_embedding_service(load_yaml("embedding.yaml"))
        self.demand_service = EvidenceDemandService(
            load_yaml("action_evidence_map.yaml"), self.embedder
        )
        self.evidence_repository = EvidenceRepository(
            quality_config, load_yaml("evidence_retention.yaml")
        )
        safety_config = load_yaml("safety_rules.yaml")
        self._safety_rule_nodes = self.evidence_repository.ingest_safety_rules(
            safety_config.get("rules", [])
        )
        self.index = HNSWIndexService(load_yaml("index.yaml"), self.embedder)
        self.runtime_capability_service = RuntimeCapabilityService(self.embedder, self.index)
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
            capability_provider=self.runtime_capability,
        )
        self._causal_rebuild_thread: Thread | None = None
        self._refresh_causal_model(restore_stable=True)
        self.evidence_repository.begin_turn("SYSTEM_SEED")
        seed_nodes = self.evidence_repository.ingest_vehicle_state(
            self.vehicle.get_state(),
            {"speaker_role": "driver", "speaker_zone": "driver"},
            "SYSTEM_SEED",
        )
        self.index.build([*self._safety_rule_nodes, *seed_nodes])
        self.evidence_repository.complete_turn("SYSTEM_SEED")
        self._subgraphs: dict[str, EvidenceSubgraph] = {}
        self._turns: dict[str, TextCommandResponse] = {}
        self.review_service = ReviewService(self, self.review_config)
        self.execution_service = ExecutionService(self)

    def _refresh_causal_model(self, *, restore_stable: bool = False):
        status = self.audit_repository.learning_status()
        records = self.audit_repository.learning_records(
            self.causal_service.maximum_training_records
        )
        stored = self.audit_repository.load_causal_model_metadata() if restore_stable else None
        if stored is not None:
            training_ids = {
                str(value) for value in stored.get("training_record_ids", [])
            }
            if training_ids:
                records = [record for record in records if record.audit_id in training_ids]
            else:
                source_count = max(0, int(stored.get("source_audit_count", 0)))
                records = records[:source_count]
        rebuilt = self.causal_service.rebuild(
            records,
            status.excluded_record_count,
            restore_metadata=stored,
            source_audit_count=(
                int(stored.get("source_audit_count", 0))
                if stored is not None
                else status.learning_record_count
            ),
        )
        if stored is None:
            self.audit_repository.save_causal_model_metadata(
                self.causal_service.model_metadata()
            )
        return rebuilt

    def _run_background_causal_rebuild(self) -> None:
        try:
            self._refresh_causal_model()
        except Exception as exc:
            self.causal_service.record_rebuild_failure(
                SensitiveDataRedactor.redact_exception(exc)
            )

    def _schedule_causal_rebuild(self, audit: AuditRecord) -> bool:
        quality = audit.audit_quality
        if (
            not self.causal_service.auto_rebuild_enabled
            or quality is None
            or not quality.eligible_for_learning
        ):
            return False
        learning_count = self.audit_repository.learning_status().learning_record_count
        status = self.causal_service.status(learning_count)
        if (
            status.auto_rebuild_running
            or status.eligible_audits_since_rebuild
            < self.causal_service.rebuild_every_eligible_audits
        ):
            return False
        self.causal_service.set_auto_rebuild_running(True)
        self._causal_rebuild_thread = Thread(
            target=self._run_background_causal_rebuild,
            name="causal-model-rebuild",
            daemon=True,
        )
        self._causal_rebuild_thread.start()
        return True

    def wait_for_causal_rebuild(self, timeout: float = 10.0) -> None:
        thread = self._causal_rebuild_thread
        if thread is not None:
            thread.join(timeout)

    def runtime_capability(self) -> RuntimeCapabilityStatus:
        self.runtime_capability_service.embedder = self.embedder
        self.runtime_capability_service.index = self.index
        return self.runtime_capability_service.status()

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
    def _apply_voice_constraints(
        decision: DecisionResult,
        gate: SafetyGateResult,
        input_trust: VoiceTrustResult,
        zone_permission: ZonePermissionResult | None,
    ) -> tuple[DecisionResult, SafetyGateResult]:
        if input_trust.audio_source == "text_api":
            return decision, gate
        explanations = list(decision.explanations)
        reason_codes = list(decision.reason_codes)
        review_question = decision.review_question
        final = decision.final_decision
        constraint_applied = False

        if input_trust.input_trust_label == "BLOCK":
            constraint_applied = True
            reason = "语音输入可信检查阻断"
            check = GateCheck(
                rule_id="VOICE_TRUST_BLOCK",
                hit=True,
                reason=reason,
                observed={"trust_score": input_trust.trust_score},
            )
            gate = gate.model_copy(
                update={
                    "blocked": True,
                    "gate_blocked": True,
                    "checks": [*gate.checks, check],
                    "reasons": [*gate.reasons, reason],
                    "hit_rules": [*gate.hit_rules, "VOICE_TRUST_BLOCK"],
                }
            )
            final = DecisionLabel.BLOCK
            explanations.append(reason)
            reason_codes.append("VOICE_TRUST_BLOCK")
        elif input_trust.input_trust_label == "REVIEW" and final == DecisionLabel.PASS:
            constraint_applied = True
            final = DecisionLabel.REVIEW
            explanations.append("声学可信结果需要人工复核")
            reason_codes.append("VOICE_TRUST_REVIEW")
            review_question = "语音输入存在合成或重放风险，请确认是否为本人现场指令？"

        if zone_permission is not None:
            if zone_permission.permission_label == DecisionLabel.BLOCK:
                constraint_applied = True
                reason = "说话区域无权直接控制当前高风险对象"
                check = GateCheck(
                    rule_id="ZONE_PERMISSION_BLOCK",
                    hit=True,
                    reason=reason,
                    observed={
                        "speaker_zone": zone_permission.speaker_zone,
                        "permission_score": zone_permission.permission_score,
                        "target": zone_permission.target,
                    },
                )
                gate = gate.model_copy(
                    update={
                        "blocked": True,
                        "gate_blocked": True,
                        "checks": [*gate.checks, check],
                        "reasons": [*gate.reasons, reason],
                        "hit_rules": [*gate.hit_rules, "ZONE_PERMISSION_BLOCK"],
                    }
                )
                final = DecisionLabel.BLOCK
                explanations.append(reason)
                reason_codes.append("ZONE_PERMISSION_BLOCK")
                review_question = None
            elif (
                zone_permission.permission_label == DecisionLabel.REVIEW
                and final == DecisionLabel.PASS
            ):
                constraint_applied = True
                final = DecisionLabel.REVIEW
                explanations.append("说话区域权限需要人工复核")
                reason_codes.append("ZONE_PERMISSION_REVIEW")
                review_question = (
                    f"检测到说话区域为 {zone_permission.speaker_zone}，"
                    f"请确认是否允许{zone_permission.action}{zone_permission.target}？"
                )

        if not constraint_applied:
            return decision, gate
        gate_blocked = gate.blocked
        updated = decision.model_copy(
            update={
                "decision": final,
                "final_decision": final,
                "gate_blocked": gate_blocked,
                "gate_reasons": list(gate.reasons),
                "score_evaluation_mode": (
                    "diagnostic_after_gate" if gate_blocked else decision.score_evaluation_mode
                ),
                "explanations": explanations,
                "reason_codes": reason_codes,
                "review_question": review_question,
                "authorization_token": None,
            }
        )
        return updated, gate

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

    def _new_audit_quality(
        self, audit_id: str, *, stage5: bool = False
    ) -> AuditQualityMetadata:
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
            implementation_stage="stage5" if stage5 else "stage4.1",
            pipeline_version="5.0.0" if stage5 else "4.1.0",
            schema_version="5.0" if stage5 else "4.1",
        )

    def process_audio_bytes(
        self,
        audio_bytes: bytes,
        *,
        audio_source: str = "test_wav",
        speaker_zone: str = "unknown",
        speaker_role: str = "unknown",
        array_channel: str | None = None,
        channel_index: int | None = None,
        state_overrides: VehicleStatePatch | None = None,
        session_id: str | None = None,
        event_sink: Callable[[PipelineEvent], None] | None = None,
    ) -> AudioCommandResponse:
        decoded = self.audio_input_service.decode_wav(
            audio_bytes,
            audio_source=audio_source,
            speaker_zone=speaker_zone,
            array_channel=array_channel,
            channel_index=channel_index,
        )
        return self._process_decoded_audio(
            decoded,
            speaker_role=speaker_role,
            state_overrides=state_overrides,
            session_id=session_id,
            event_sink=event_sink,
        )

    def process_microphone(
        self,
        *,
        duration_seconds: float,
        device: int | str | None,
        speaker_zone: str,
        speaker_role: str,
        state_overrides: VehicleStatePatch | None = None,
        session_id: str | None = None,
        event_sink: Callable[[PipelineEvent], None] | None = None,
    ) -> AudioCommandResponse:
        decoded = self.audio_input_service.capture_microphone(
            duration_seconds,
            device=device,
            speaker_zone=speaker_zone,
        )
        return self._process_decoded_audio(
            decoded,
            speaker_role=speaker_role,
            state_overrides=state_overrides,
            session_id=session_id,
            event_sink=event_sink,
        )

    def _process_decoded_audio(
        self,
        decoded: DecodedAudio,
        *,
        speaker_role: str,
        state_overrides: VehicleStatePatch | None,
        session_id: str | None,
        event_sink: Callable[[PipelineEvent], None] | None,
    ) -> AudioCommandResponse:
        turn_id = make_id("TURN")
        root_turn_id = turn_id
        sequence = 0
        sink = event_sink or self.event_broker.publish
        event_started = perf_counter()

        def emit(stage: str, summary: str, payload: dict[str, Any] | None = None) -> None:
            nonlocal sequence, event_started
            safe_payload = SensitiveDataRedactor.redact(payload or {})
            if stage in {item.value for item in WorkflowEventType} and stage in {
                "VOICE_INPUT_RECEIVED",
                "SPECTRUM_ANALYZED",
                "LA_CHECKED",
                "PA_CHECKED",
                "VOICE_TRUST_DECIDED",
                "ASR_COMPLETED",
            }:
                self.workflow_repository.append_event(
                    root_turn_id=root_turn_id,
                    related_turn_id=turn_id,
                    event_type=WorkflowEventType(stage),
                    payload=safe_payload,
                )
            if session_id is None:
                return
            now = perf_counter()
            sequence += 1
            sink(
                PipelineEvent(
                    session_id=session_id,
                    turn_id=turn_id,
                    sequence=sequence,
                    stage=stage,
                    duration_ms=round((now - event_started) * 1000, 4),
                    summary=summary,
                    payload=safe_payload,
                )
            )
            event_started = now

        metadata = decoded.audit_metadata()
        emit(
            "VOICE_INPUT_RECEIVED",
            "真实音频输入已接收并完成摘要",
            metadata,
        )
        spectrum = self.spectrum_analyzer.analyze(decoded.waveform, decoded.sample_rate)
        emit(
            "SPECTRUM_ANALYZED",
            "真实波形频谱异常分析完成",
            spectrum.model_dump(mode="json"),
        )
        la = self.la_detector.score(
            decoded.waveform,
            decoded.sample_rate,
            spectrum_anomaly_score=spectrum.anomaly_score,
        )
        emit(
            "LA_CHECKED",
            "LA 合成音检测完成",
            {
                "la_score": la.bonafide_score,
                "inference_duration": la.inference_duration,
                "model": la.model_metadata,
            },
        )
        pa = self.pa_detector.score(
            decoded.waveform,
            decoded.sample_rate,
            spectrum_anomaly_score=spectrum.anomaly_score,
        )
        emit(
            "PA_CHECKED",
            "PA 重放攻击检测完成",
            {
                "pa_score": pa.bonafide_score,
                "inference_duration": pa.inference_duration,
                "model": pa.model_metadata,
            },
        )
        trust = self.voice_trust_scorer.score(
            turn_id=turn_id,
            audio_source=decoded.audio_source,
            speaker_zone=decoded.speaker_zone,
            speaker_role=speaker_role,
            la_score=la.bonafide_score,
            pa_score=pa.bonafide_score,
            audio_fingerprint=decoded.fingerprint,
            spectrum_anomaly_score=spectrum.anomaly_score,
            model_metadata={"la": la.model_metadata, "pa": pa.model_metadata},
            force_block_reason=("SILENCE_OR_LOW_ENERGY" if spectrum.silence_detected else None),
        )
        emit(
            "VOICE_TRUST_DECIDED",
            "报告公式的语音可信评分完成",
            trust.model_dump(mode="json"),
        )
        if trust.input_trust_label == DecisionLabel.BLOCK.value:
            transcription = TranscriptionResult(
                turn_id=turn_id,
                text="",
                confidence=None,
                adapter="not_run_due_voice_trust_block",
                model_inference_performed=False,
                model_name=self.asr_service.model_name,
                inference_duration=0.0,
            )
            return self._terminal_audio_response(
                trust=trust,
                spectrum=spectrum,
                transcription=transcription,
                reason_code="VOICE_TRUST_BLOCK",
                reason="声学可信检查为 BLOCK，ASR 与后续证据流水线未执行",
                audio_input_metadata=metadata,
                emit=emit,
            )
        try:
            transcription = self.asr_service.transcribe(
                turn_id,
                decoded.waveform,
                decoded.sample_rate,
            )
        except ASRModelError as exc:
            transcription = TranscriptionResult(
                turn_id=turn_id,
                text="",
                confidence=None,
                adapter="whisper_transformers_local_failed",
                model_inference_performed=False,
                model_name=self.asr_service.model_name,
                inference_duration=0.0,
            )
            emit(
                "ASR_COMPLETED",
                "ASR 推理失败",
                {"model_name": self.asr_service.model_name, "error": str(exc)},
            )
            return self._terminal_audio_response(
                trust=trust,
                spectrum=spectrum,
                transcription=transcription,
                reason_code="ASR_FAILED",
                reason="ASR 模型推理失败，未生成车控指令",
                audio_input_metadata=metadata,
                emit=emit,
            )
        emit(
            "ASR_COMPLETED",
            "本地中文 ASR 真实转写完成",
            transcription.model_dump(mode="json"),
        )
        if not transcription.transcribed_text.strip():
            return self._terminal_audio_response(
                trust=trust,
                spectrum=spectrum,
                transcription=transcription,
                reason_code="ASR_EMPTY",
                reason="ASR 返回空文本，未生成车控指令",
                audio_input_metadata=metadata,
                emit=emit,
            )
        pipeline_result = self.process_text(
            TextCommandRequest(
                text=transcription.transcribed_text,
                speaker_zone=decoded.speaker_zone,
                speaker_role=speaker_role,
                state_overrides=state_overrides,
                session_id=session_id,
            ),
            root_turn_id=root_turn_id,
            turn_id_override=turn_id,
            input_trust_override=trust,
            transcription_override=transcription,
            spectrum_analysis=spectrum,
            audio_input_metadata=metadata,
            zone_source=decoded.zone_source,
            event_sink=sink,
            event_sequence_start=sequence,
        )
        return AudioCommandResponse(
            turn_id=turn_id,
            voice_trust=trust,
            spectrum_analysis=spectrum,
            asr_result=transcription,
            zone_permission=pipeline_result.zone_permission_result,
            semantic_frame=pipeline_result.semantic_frame,
            evidence_subgraph=pipeline_result.evidence_subgraph,
            decision=pipeline_result.decision,
            audit=pipeline_result.audit,
            pipeline=pipeline_result,
        )

    def _terminal_audio_response(
        self,
        *,
        trust: VoiceTrustResult,
        spectrum: SpectrumAnalysisResult,
        transcription: TranscriptionResult,
        reason_code: str,
        reason: str,
        audio_input_metadata: dict[str, Any],
        emit: Callable[[str, str, dict[str, Any] | None], None],
    ) -> AudioCommandResponse:
        turn_id = trust.turn_id
        now = utc_now()
        frame = self.parser.parse(turn_id, "")
        demand = EvidenceDemand(
            turn_id=turn_id,
            action=frame.action,
            target=frame.target,
            risk_level=frame.risk_level,
            query_text="",
            query_vector=[],
            required_types=[],
            optional_types=[],
            priority=0,
            retrieval_scope="none_voice_terminal",
        )
        index_status = self.index.status()
        retrieval = RetrievalMetadata(
            implementation=index_status.implementation,
            index_node_count=index_status.node_count,
            vector_dimension=index_status.dimension,
            M=index_status.M,
            ef_construction=index_status.ef_construction,
            ef_search=index_status.ef_search,
            top_k=index_status.top_k,
            candidate_count=0,
            canonical_node_count=index_status.canonical_node_count,
            ephemeral_node_count=index_status.ephemeral_node_count,
            index_update_count=index_status.index_update_count,
            index_rebuild_count=index_status.index_rebuild_count,
            deduplicated_count=index_status.deduplicated_count,
            duration_ms=0,
            empty_index=index_status.node_count == 0,
            degraded=index_status.degraded,
            degradation_reason=index_status.degradation_reason,
            excluded_types=index_status.excluded_types,
            last_built_at=index_status.last_built_at,
        )
        quality = EvidenceQualityMetrics(
            ecr=None,
            evidence_coverage_applicable=False,
            ecs=0,
            ef=0,
            sas=0,
            eas=0,
        )
        subgraph = EvidenceSubgraph(
            turn_id=turn_id,
            quality_metrics=quality,
            retrieval_metadata=retrieval,
            advanced_reasoning_status="NOT_RUN_VOICE_TERMINAL",
        )
        check = GateCheck(rule_id=reason_code, hit=True, reason=reason)
        gate = SafetyGateResult(
            blocked=True,
            checks=[check],
            reasons=[reason],
            hit_rules=[reason_code],
        )
        factors = DecisionScoreFactors(
            semantic_quality=0,
            evidence_coverage=None,
            evidence_coverage_applicable=False,
            applied_weights={},
            five_factors={},
        )
        decision = DecisionResult(
            turn_id=turn_id,
            decision=DecisionLabel.BLOCK,
            final_decision=DecisionLabel.BLOCK,
            safety_score=trust.trust_score,
            soft_safety_score=trust.trust_score,
            gate_blocked=True,
            gate_reasons=[reason],
            score_evaluation_mode="diagnostic_after_gate",
            score_factors=factors,
            explanations=[reason, "该诊断分数不参与最终裁决"],
            reason_codes=[reason_code],
        )
        audit_id = make_id("AUD")
        audit_quality = self._new_audit_quality(audit_id, stage5=True).model_copy(
            update={
                "eligible_for_learning": False,
                "exclusion_reasons": ["pre-semantic voice terminal"],
            }
        )
        timing = TurnTiming(
            turn_started_at=trust.created_at,
            state_snapshot_at=now,
            decision_reference_time=now,
            completed_at=now,
            end_to_end_ms=0,
        )
        audit = AuditRecord(
            audit_id=audit_id,
            turn_id=turn_id,
            root_turn_id=turn_id,
            input_trust_result=trust,
            transcription_result=transcription,
            spectrum_analysis=spectrum,
            audio_input_metadata=audio_input_metadata,
            semantic_frame=frame,
            evidence_demand=demand,
            candidate_recall_results=[],
            retrieval_metadata=retrieval,
            evidence_subgraph=subgraph,
            evidence_subgraph_summary={
                "graph_id": subgraph.graph_id,
                "node_count": 0,
                "edge_count": 0,
                "missing_types": [],
                "terminal_reason": reason_code,
            },
            evidence_quality_metrics=quality,
            safety_gate_result=gate,
            score_details=factors,
            final_decision=decision,
            complete_gate_result=gate,
            audit_quality=audit_quality,
            turn_timing=timing,
            runtime_capability=self.runtime_capability(),
        )
        saved = self.audit_repository.save(audit)
        self._subgraphs[turn_id] = subgraph
        emit(
            "AUDIT_SAVED",
            "声学终止审计已追加保存",
            {"audit_id": saved.audit_id, "current_hash": saved.current_hash},
        )
        return AudioCommandResponse(
            turn_id=turn_id,
            voice_trust=trust,
            spectrum_analysis=spectrum,
            asr_result=transcription,
            semantic_frame=frame,
            evidence_subgraph=subgraph,
            decision=decision,
            audit=saved,
            pipeline=None,
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
        turn_id_override: str | None = None,
        input_trust_override: VoiceTrustResult | None = None,
        transcription_override: TranscriptionResult | None = None,
        spectrum_analysis: SpectrumAnalysisResult | None = None,
        audio_input_metadata: dict[str, Any] | None = None,
        zone_source: str | None = None,
        event_sequence_start: int = 0,
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
        turn_id = turn_id_override or make_id("TURN")
        root_turn_id = root_turn_id or turn_id
        self.evidence_repository.begin_turn(turn_id)
        sequence = event_sequence_start
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

        voice_preprocessed = input_trust_override is not None
        if not voice_preprocessed:
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
                    input_trust_override=input_trust_override,
                    transcription_override=transcription_override,
                    spectrum_analysis=spectrum_analysis,
                    audio_input_metadata=audio_input_metadata or {},
                    zone_source=zone_source,
                    emit=emit,
                )
        except Exception as exc:
            self.evidence_repository.complete_turn(turn_id)
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
        input_trust_override: VoiceTrustResult | None,
        transcription_override: TranscriptionResult | None,
        spectrum_analysis: SpectrumAnalysisResult | None,
        audio_input_metadata: dict[str, Any],
        zone_source: str | None,
        emit: Callable[[str, str, dict[str, Any] | None], None],
    ) -> TextCommandResponse:
        overall_started = perf_counter()
        turn_started_at = utc_now()
        state = (
            self.vehicle.update_state(request.state_overrides)
            if request.state_overrides is not None
            else self.vehicle.get_state()
        )
        input_trust = input_trust_override or VoiceTrustResult(
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
        if input_trust_override is not None and input_trust.turn_id != turn_id:
            input_trust = input_trust.model_copy(update={"turn_id": turn_id})
        transcription = transcription_override or TranscriptionResult(
            turn_id=turn_id,
            text=request.text,
            confidence=1.0,
            adapter="text_passthrough",
            model_inference_performed=False,
        )
        if transcription_override is not None and transcription.turn_id != turn_id:
            transcription = transcription.model_copy(update={"turn_id": turn_id})
        if input_trust_override is None:
            emit(
                "TRUST_CHECKED",
                "文本输入无需声学可信检查",
                {"label": input_trust.input_trust_label},
            )
            emit(
                "ASR_COMPLETED",
                "文本直通，无 ASR 模型推理",
                {"adapter": transcription.adapter},
            )
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
        zone_permission: ZonePermissionResult | None = None
        if zone_source is not None:
            zone_permission = self.zone_permission_service.evaluate(
                request.speaker_zone,
                frame.action,
                frame.target,
                zone_source=zone_source,
            )
            zone_payload = zone_permission.model_dump(mode="json")
            emit(
                "ZONE_PERMISSION_CHECKED",
                "座舱区域权限前置过滤完成",
                zone_payload,
            )
            self.workflow_repository.append_event(
                root_turn_id=root_turn_id,
                related_turn_id=turn_id,
                parent_turn_id=parent_turn_id,
                event_type=WorkflowEventType.ZONE_PERMISSION_CHECKED,
                payload=zone_payload,
            )
        runtime_capability = self.runtime_capability()
        emit(
            "SEMANTIC_PARSED",
            "语义帧已生成",
            {"action": frame.action, "target": frame.target, "risk_level": frame.risk_level},
        )
        capability_payload = runtime_capability.model_dump(mode="json")
        emit(
            "RUNTIME_CAPABILITY_CHECKED",
            "运行时语义与索引能力已检查",
            capability_payload,
        )
        self.workflow_repository.append_event(
            root_turn_id=root_turn_id,
            related_turn_id=turn_id,
            parent_turn_id=parent_turn_id,
            event_type=WorkflowEventType.RUNTIME_CAPABILITY_CHECKED,
            payload=capability_payload,
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
        gate = self.gate_service.evaluate(
            frame,
            reasoning_evidence,
            validation,
            memory,
            runtime_capability,
        )
        emit(
            "GATE_CHECKED",
            "硬性安全门检查完成",
            {"gate_blocked": gate.blocked, "hit_rules": gate.hit_rules},
        )
        scoring_started = perf_counter()
        decision = self.decision_service.decide(
            frame,
            reasoning_evidence,
            gate,
            validation,
            causal,
            memory,
            runtime_capability,
        )
        decision, gate = self._apply_voice_constraints(
            decision,
            gate,
            input_trust,
            zone_permission,
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
            spectrum_analysis=spectrum_analysis,
            zone_permission_result=zone_permission,
            audio_input_metadata=audio_input_metadata,
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
            audit_quality=self._new_audit_quality(
                audit_id, stage5=input_trust.audio_source != "text_api"
            ),
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
            runtime_capability=runtime_capability,
        )
        saved_audit = self.audit_repository.save(audit)
        emit(
            "AUDIT_SAVED",
            "裁决审计已追加保存",
            {"audit_id": saved_audit.audit_id, "current_hash": saved_audit.current_hash},
        )
        self._schedule_causal_rebuild(saved_audit)
        self.evidence_repository.complete_turn(turn_id)
        actionable = (
            demand.retrieval_scope == "control_evidence"
            and runtime_capability.semantic_control_mode == SemanticControlMode.FULL
        )
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
            zone_permission_result=zone_permission,
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
            runtime_capability=runtime_capability,
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
            repository_status=self.evidence_repository.status(),
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

    def causal_status(self):
        learning_count = self.audit_repository.learning_status().learning_record_count
        return self.causal_service.status(learning_count)

    def get_vehicle_state(self) -> VehicleState:
        return self.vehicle.get_state()

    def update_vehicle_state(self, patch: VehicleStatePatch) -> VehicleState:
        with self._command_lock:
            update_turn_id = make_id("STATE_UPDATE")
            self.evidence_repository.begin_turn(update_turn_id)
            state = self.vehicle.update_state(patch)
            nodes = self.evidence_repository.ingest_vehicle_state(
                state,
                {
                    "speaker_role": state.occupant_role or "unknown",
                    "speaker_zone": state.speaker_zone or "unknown",
                },
                update_turn_id,
            )
            self.index.upsert(nodes)
            self.evidence_repository.complete_turn(update_turn_id)
            return state

    def reset_vehicle_state(self) -> VehicleState:
        with self._command_lock:
            reset_turn_id = make_id("STATE_RESET")
            self.evidence_repository.begin_turn(reset_turn_id)
            state = self.vehicle.reset()
            nodes = self.evidence_repository.ingest_vehicle_state(
                state,
                {"speaker_role": "driver", "speaker_zone": "driver"},
                reset_turn_id,
            )
            self.index.upsert(nodes)
            self.evidence_repository.complete_turn(reset_turn_id)
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
