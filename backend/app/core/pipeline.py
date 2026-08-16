from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from threading import RLock
from time import perf_counter
from typing import Any, Callable

from app.core.config import ConfigurationError, PROJECT_ROOT, load_yaml

_LOGGER = logging.getLogger(__name__)

# 法规相关性过滤时排除的通用证据类型：几乎每个车控指令/法规条文都有，无区分度。
_GENERIC_EVIDENCE_TYPES = frozenset(
    {
        "VEHICLE_SPEED",
        "GEAR_STATE",
        "ENVIRONMENT_CONDITIONS",
        "SPEED_LIMIT_STATE",
        "ROAD_FRICTION_STATE",
    }
)
from app.core.performance import mark_stage, set_metric
from app.models.schemas import (
    AdvancedReasoningResult,
    AudioCommandResponse,
    AuditQualityMetadata,
    AuditDatabaseRole,
    AuditRecord,
    AuditRecordQuality,
    CurrentEvidenceResponse,
    DecisionLabel,
    DecisionResult,
    DecisionScoreFactors,
    DecisionSource,
    EvidenceDemand,
    EvidenceEdge,
    EvidenceNode,
    EvidenceObservationInput,
    EvidenceRelation,
    EvidenceSubgraph,
    EvidenceQualityMetrics,
    ExecutionTokenView,
    GateCheck,
    IndexStatus,
    IndexParametersRequest,
    IntentEvidenceResolution,
    OccurrenceLayerNavigation,
    MemoryRelationType,
    PipelineEvent,
    RegulationHit,
    RegulationRationale,
    RetrievalMetadata,
    RuntimeCapabilityStatus,
    RuntimeSafetyContext,
    SafetyGateResult,
    SemanticUnitKind,
    SemanticControlMode,
    TextCommandRequest,
    TextCommandResponse,
    TrustedRuntimeContext,
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
from app.services.audit.recall_ai import RecallAIAuditService
from app.services.audit.effective import EffectiveAuditResolver
from app.services.audit.explanation import AuditExplanationService
from app.services.authorization.service import AuthorizationTokenError, AuthorizationTokenService
from app.services.causal.service import CausalCorrectionService
from app.services.claim.service import ClaimCheckResult, ContextClaimService
from app.services.clarification.service import ClarificationService
from app.services.interaction.service import InteractionService
from app.services.decision.engine import DecisionService
from app.services.decision.merge import (
    apply_merge_outcome,
    merge_decision,
)
from app.services.decision.safety_gate import SafetyGateService
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.demand_registry import EvidenceDemandRegistry
from app.services.evidence.recall import MandatoryRecallService
from app.services.evidence.repository import EvidenceRepository
from app.services.evidence.resolution import project_evidence_resolutions
from app.services.execution.service import ExecutionService
from app.services.graph.builder import EvidenceSubgraphBuilder
from app.services.index.hnsw import HNSWIndexService
from app.services.index.trusted_knowledge import TrustedKnowledgeIndexService
from app.services.interpreter.service import InterpreterService
from app.services.presentation.audit_snapshot import AuditSnapshotBuilder
from app.services.regulation.service import RegulationKnowledgeBase
from app.services.runtime.capability import RuntimeCapabilityService
from app.services.memory.service import DualMemoryService
from app.services.quality.evaluator import EvidenceQualityService
from app.services.quality.window import EvidenceQualityWindow
from app.services.review.service import ReviewService
from app.services.semantic.orchestrator import SemanticOrchestratorService
from app.services.request_routing.service import RequestRoutingService
from app.services.semantic.area import allowed_areas_for_intent
from app.services.validation.advanced import AdvancedValidationService
from app.services.vector.embedding import build_embedding_service
from app.services.vehicle.carla import CarlaVehicleAdapter
from app.services.vehicle.capabilities import CanonicalCapabilityRegistry
from app.services.vehicle.simulator import SimulatorVehicleAdapter
from app.services.asr.whisper import ASRModelError, WhisperASRService
from app.services.voice.antispoof import (
    ASVspoofLADetector,
    ASVspoofPADetector,
    AntiSpoofScore,
)
from app.services.voice.audio import AudioInputService, DecodedAudio
from app.services.voice.spectrum import SpectrumAnalyzer
from app.services.voice.trust import VoiceTrustScorer
from app.services.voice.zone import ZonePermissionService


class _DisabledAntiSpoofDetector:
    """Compatibility detector that never loads or executes an LA/PA model."""

    def __init__(self, detector_kind: str, task: str) -> None:
        self.detector_kind = detector_kind
        self.task = task

    def score(self, *_args: Any, **_kwargs: Any) -> AntiSpoofScore:
        return AntiSpoofScore(
            bonafide_score=1.0,
            inference_duration=0.0,
            model_status="DISABLED",
            model_metadata={
                "detector_kind": self.detector_kind,
                "task": self.task,
                "model_name": f"disabled-{self.detector_kind.lower()}",
                "model_status": "DISABLED",
                "antispoof_enabled": False,
                "scores_semantics": "PLACEHOLDER_NOT_MODEL_OUTPUT",
            },
            raw_score=None,
        )
from app.services.workflow.repository import WorkflowRepository
from app.websocket.broker import PipelineEventBroker
from app.core.redaction import SensitiveDataRedactor


class CommandPipeline:
    """Stage-three deterministic command pipeline.

    The hard gate and evidence-alignment route are evaluated independently.
    A single conservative merge preserves the raw score verdict and produces
    the final decision used by review and authorization.
    """

    def __init__(
        self,
        database_path: Path | None = None,
        *,
        token_secret: bytes | None = None,
        event_broker: PipelineEventBroker | None = None,
        audit_database_role: AuditDatabaseRole = AuditDatabaseRole.PRODUCTION,
        knowledge_data_path: Path | None = None,
    ) -> None:
        self._command_lock = RLock()
        audit_database_role = AuditDatabaseRole(audit_database_role)
        quality_config = load_yaml("evidence_quality.yaml")
        self.vehicle_config = load_yaml("vehicle_actions.yaml")
        adapter_type = os.getenv(
            "YUZHENG_VEHICLE_ADAPTER",
            str(self.vehicle_config.get("adapter", "simulator")),
        ).strip().lower()
        if adapter_type == "carla":
            try:
                carla_options = dict(self.vehicle_config.get("carla", {}))
                self.vehicle = CarlaVehicleAdapter(
                    action_config=self.vehicle_config, **carla_options
                )
            except Exception:
                _LOGGER.warning(
                    "CARLA 适配器初始化失败，回退到确定性模拟器适配器",
                    exc_info=True,
                )
                self.vehicle = SimulatorVehicleAdapter(action_config=self.vehicle_config)
        else:
            self.vehicle = SimulatorVehicleAdapter(action_config=self.vehicle_config)
        self.command_capability_registry = CanonicalCapabilityRegistry(
            self.vehicle_config
        )
        self.event_broker = event_broker or PipelineEventBroker()
        self.review_config = load_yaml("review_policy.yaml")
        self.interpreter_config = load_yaml("interpreter.yaml")
        self.scenario_config = load_yaml("demo_scenarios.yaml")
        self.voice_config = load_yaml("voice.yaml")
        self.antispoof_enabled = bool(self.voice_config.get("antispoof_enabled", True))
        configured_voice_mode = str(
            self.voice_config.get("voice_trust_mode", "enforce")
        ).strip().lower()
        self.voice_trust_mode = os.getenv(
            "YUZHENG_VOICE_TRUST_MODE", configured_voice_mode
        ).strip().lower()
        if self.voice_trust_mode not in {"enforce", "observe"}:
            raise ConfigurationError(
                "YUZHENG_VOICE_TRUST_MODE 必须为 enforce 或 observe，"
                f"实际为 {self.voice_trust_mode!r}"
            )
        self.audio_input_service = AudioInputService(self.voice_config["audio"])
        self.spectrum_analyzer = SpectrumAnalyzer(self.voice_config["spectrum"])
        # LA/PA 模型暂时停用。保留实现和配置，便于后续通过开关恢复。
        self.la_detector = (
            ASVspoofLADetector(self.voice_config["la"])
            if self.antispoof_enabled
            else _DisabledAntiSpoofDetector("LA", "logical_access_synthetic")
        )
        self.pa_detector = (
            ASVspoofPADetector(self.voice_config["pa"])
            if self.antispoof_enabled
            else _DisabledAntiSpoofDetector("PA", "physical_access_replay")
        )
        self.voice_trust_scorer = VoiceTrustScorer(self.voice_config["trust"])
        self.zone_permission_service = ZonePermissionService(
            self.voice_config["zone_permission"]
        )
        self.asr_service = WhisperASRService(self.voice_config["asr"])
        self.semantic_service = SemanticOrchestratorService()
        self.request_routing_service = RequestRoutingService()
        self.claim_service = ContextClaimService()
        self.embedder = build_embedding_service(load_yaml("embedding.yaml"))
        self.evidence_demand_registry = EvidenceDemandRegistry()
        self.demand_service = EvidenceDemandService(
            registry=self.evidence_demand_registry,
            embedder=self.embedder,
        )
        self.interpreter_service = InterpreterService(self.interpreter_config)
        audit_explanation_provider = self.interpreter_service.provider
        self.audit_explanation_service = AuditExplanationService(
            audit_explanation_provider
        )
        self.evidence_repository = EvidenceRepository(
            quality_config, load_yaml("evidence_retention.yaml")
        )
        safety_config = load_yaml("safety_rules.yaml")
        self.index = HNSWIndexService(load_yaml("index.yaml"), self.embedder)
        # Trusted 安全知识库：知识库辅助证据需求（追加并集）
        knowledge_config = load_yaml("knowledge.yaml")
        env_knowledge_path = os.getenv("YUZHENG_KNOWLEDGE_DATA_PATH")
        if env_knowledge_path:
            knowledge_config = {**knowledge_config, "data_path": env_knowledge_path}
        if knowledge_data_path is not None:
            knowledge_config = {**knowledge_config, "data_path": str(knowledge_data_path)}
        self.knowledge_index = TrustedKnowledgeIndexService(
            knowledge_config,
            self.embedder,
            self.evidence_demand_registry.canonical_evidence_types,
        )
        self.knowledge_index.load()
        self.runtime_capability_service = RuntimeCapabilityService(self.embedder, self.index)
        self.recall_service = MandatoryRecallService(self.evidence_repository, self.embedder)
        self.quality_service = EvidenceQualityService(quality_config)
        self.quality_window = EvidenceQualityWindow(
            int(quality_config.get("window", {}).get("short_length", 8))
        )
        self.graph_builder = EvidenceSubgraphBuilder()
        memory_config = load_yaml("memory.yaml")
        self.memory_service = DualMemoryService(memory_config)
        self.validation_service = AdvancedValidationService(load_yaml("jailbreak_policy.yaml"))
        self.causal_service = CausalCorrectionService(load_yaml("causal_policy.yaml"))
        self.gate_service = SafetyGateService(safety_config)
        self.decision_service = DecisionService(load_yaml("decision_policy.yaml"))
        self.regulation_kb_dir = PROJECT_ROOT / "data" / "regulation_kb_v8"
        self.regulation_kb = RegulationKnowledgeBase(self.embedder)
        self._init_regulation_kb()
        self.audit_repository = AuditRepository(
            database_path
            or PROJECT_ROOT / "data" / "database" / "yuzheng_evidence_v3.db",
            database_role=audit_database_role,
        )
        self.recall_ai_audit_service = RecallAIAuditService(self.audit_repository)
        self.effective_audit_resolver = EffectiveAuditResolver(self.audit_repository)
        self.workflow_repository = WorkflowRepository(self.audit_repository.database_path)
        self.authorization_service = AuthorizationTokenService(
            load_yaml("authorization.yaml"),
            self.workflow_repository,
            secret=token_secret,
            capability_provider=self.runtime_capability,
            command_capability_registry=self.command_capability_registry,
            vehicle_adapter_provider=lambda: self.vehicle.adapter_name,
        )
        self.evidence_repository.begin_turn("SYSTEM_SEED")
        seed_nodes = self.evidence_repository.ingest_vehicle_state(
            self.vehicle.get_state(),
            None,
            "SYSTEM_SEED",
        )
        self.index.build(seed_nodes)
        self.evidence_repository.complete_turn("SYSTEM_SEED")
        self._subgraphs: dict[str, EvidenceSubgraph] = {}
        self._turns: dict[str, TextCommandResponse] = {}
        self.clarification_service = ClarificationService(self, self.review_config)
        self.interaction_service = InteractionService(self, self.review_config)
        self.review_service = ReviewService(self, self.review_config)
        self.execution_service = ExecutionService(self)

    def runtime_capability(self) -> RuntimeCapabilityStatus:
        self.runtime_capability_service.embedder = self.embedder
        self.runtime_capability_service.index = self.index
        return self.runtime_capability_service.status()

    def _init_regulation_kb(self) -> None:
        """加载法规知识库；index.bin 与当前 hnswlib 不兼容时从 documents.json 重建。

        法规库仅作裁决后的法规依据附加展示，不参与安全裁决。
        """
        try:
            self.regulation_kb.load(self.regulation_kb_dir)
            return
        except Exception:
            self.regulation_kb = RegulationKnowledgeBase(self.embedder)
        try:
            documents = json.loads(
                (self.regulation_kb_dir / "documents.json").read_text(encoding="utf-8")
            )
            for doc in documents:
                self.regulation_kb.add_document(
                    content=str(doc.get("content", "")),
                    standard_id=str(doc.get("standard_id", "")),
                    clause=str(doc.get("clause", "")),
                    source=str(doc.get("source", "")),
                )
            self.regulation_kb.save(self.regulation_kb_dir)
            self.regulation_kb.load(self.regulation_kb_dir)
        except Exception:
            self.regulation_kb = None

    def _regulation_rationale(
        self,
        demand_text: str,
        search_k: int = 10,
        min_score: float = 0.45,
        required_types: list[str] | None = None,
    ) -> RegulationRationale | None:
        if self.regulation_kb is None or not demand_text:
            return None
        rationale = self.regulation_kb.rationale(demand_text, k=search_k)
        # 命中到多少展示多少：相似度≥min_score 且（有条文 evidence_types 时）与
        # 本指令所需证据类型有交集；无交集条文视为语义不相关，过滤掉。
        # 排除 VEHICLE_SPEED/ENVIRONMENT_CONDITIONS 等通用证据——它们几乎每条法规
        # 和每个指令都有，无区分度，会造成误保留。
        req = set(required_types or []) - _GENERIC_EVIDENCE_TYPES
        hits: list[RegulationHit] = []
        for hit in rationale.hits:
            if hit.score < min_score:
                continue
            ev = set(hit.evidence_types)
            if req and ev and not (ev & req):
                continue
            hits.append(hit)
        return RegulationRationale(
            demand_text=rationale.demand_text,
            hits=[
                RegulationHit(
                    standard_id=hit.standard_id,
                    clause=hit.clause,
                    content=hit.content,
                    source=hit.source,
                    score=hit.score,
                    evidence_types=list(hit.evidence_types),
                )
                for hit in hits
            ],
            missing_types=list(rationale.missing_types),
        )

    def regulation_for_text(
        self,
        demand_text: str,
        search_k: int = 10,
        min_score: float = 0.45,
        required_types: list[str] | None = None,
    ) -> list[RegulationHit]:
        """公开入口：检索法规依据，返回命中条文（相似度+证据类型交集过滤，动态数量）。"""
        rationale = self._regulation_rationale(
            demand_text, search_k=search_k, min_score=min_score, required_types=required_types
        )
        return list(rationale.hits) if rationale else []

    @staticmethod
    def _candidate_copy(node: EvidenceNode) -> EvidenceNode:
        return node.model_copy(
            update={
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

    def _apply_voice_constraints(
        self,
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
        constraint_applied = False
        review_constraints: list[DecisionSource] = []
        block_constraints: list[DecisionSource] = []
        constraint_reasons: dict[DecisionSource, str] = {}
        prior_sources = [
            source
            for source in decision.decision_sources
            if source
            not in {
                DecisionSource.SAFETY_GATE,
                DecisionSource.EVIDENCE_ALIGNMENT,
                DecisionSource.SAFETY_SCORE,
                DecisionSource.LEGACY_COMPATIBILITY,
            }
        ]

        if (
            self.voice_trust_mode == "enforce"
            and input_trust.input_trust_label == "BLOCK"
        ):
            constraint_applied = True
            block_constraints.append(DecisionSource.VOICE_TRUST)
            reason = "语音输入可信检查阻断"
            constraint_reasons[DecisionSource.VOICE_TRUST] = reason
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
            explanations.append(reason)
            reason_codes.append("VOICE_TRUST_BLOCK")
        elif (
            self.voice_trust_mode == "enforce"
            and input_trust.input_trust_label == "REVIEW"
        ):
            constraint_applied = True
            review_constraints.append(DecisionSource.VOICE_TRUST)
            reason = "声学可信结果需要人工复核"
            constraint_reasons[DecisionSource.VOICE_TRUST] = reason
            explanations.append(reason)
            reason_codes.append("VOICE_TRUST_REVIEW")
            review_question = "语音输入存在合成或重放风险，请确认是否为本人现场指令？"

        if zone_permission is not None:
            if zone_permission.permission_label == DecisionLabel.BLOCK:
                constraint_applied = True
                block_constraints.append(DecisionSource.ZONE_PERMISSION)
                reason = "说话区域无权直接控制当前高风险对象"
                constraint_reasons[DecisionSource.ZONE_PERMISSION] = reason
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
                explanations.append(reason)
                reason_codes.append("ZONE_PERMISSION_BLOCK")
                review_question = None
            elif (
                zone_permission.permission_label == DecisionLabel.REVIEW
            ):
                constraint_applied = True
                review_constraints.append(DecisionSource.ZONE_PERMISSION)
                reason = "说话区域权限需要人工复核"
                constraint_reasons[DecisionSource.ZONE_PERMISSION] = reason
                explanations.append(reason)
                reason_codes.append("ZONE_PERMISSION_REVIEW")
                review_question = (
                    f"检测到说话区域为 {zone_permission.speaker_zone}，"
                    f"请确认是否允许{zone_permission.action}{zone_permission.target}？"
                )

        if not constraint_applied:
            return decision, gate
        gate_blocked = gate.blocked
        merged = merge_decision(
            gate,
            "EVIDENCE_PASS",
            decision.score_decision,
            review_constraints=review_constraints,
            block_constraints=block_constraints,
            constraint_reasons=constraint_reasons,
            prior_final_decision=decision.final_decision,
            prior_decision_sources=prior_sources,
        )
        final = merged.final_decision
        if final == DecisionLabel.BLOCK:
            review_question = None
        updated = apply_merge_outcome(
            decision,
            merged,
            field_updates={
                "gate_blocked": gate_blocked,
                "gate_reasons": list(gate.reasons),
                "score_evaluation_mode": (
                    "diagnostic_after_gate" if gate_blocked else decision.score_evaluation_mode
                ),
                "explanations": explanations,
                "reason_codes": reason_codes,
                "review_question": review_question,
                "authorization_token": None,
            },
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
        test_only = self.audit_repository.database_role == AuditDatabaseRole.TEST
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

    @staticmethod
    def _authenticated(value: str | bool | None) -> bool | None:
        if isinstance(value, bool):
            return value
        if value is None:
            return None
        normalized = str(value).strip().upper()
        if normalized in {"AUTHENTICATED", "AUTHORIZED"}:
            return True
        if normalized in {"UNAUTHENTICATED", "UNAUTHORIZED", "DENIED"}:
            return False
        return None

    def _authorization_fact(
        self,
        state: VehicleState,
        intents: list[Any],
        trusted_context: TrustedRuntimeContext | None,
        zone_results: list[ZonePermissionResult],
    ) -> dict[str, Any]:
        authenticated = self._authenticated(state.authentication_state)
        trusted_subject = bool(
            trusted_context is not None
            and trusted_context.subject_role is not None
            and trusted_context.subject_zone is not None
            and trusted_context.subject_source is not None
            and trusted_context.zone_source is not None
            and len(zone_results) == len(intents)
        )
        authorizations: list[dict[str, Any]] = []
        if trusted_subject and trusted_context is not None:
            for intent, permission in zip(intents, zone_results, strict=True):
                driving = intent.control_domain == "驾驶控制"
                role_permitted = (
                    trusted_context.subject_role.strip().lower() == "driver"
                    or not driving
                )
                authorized = (
                    authenticated is True and permission.passed and role_permitted
                    if authenticated is not None
                    else None
                )
                authorizations.append(
                    {
                        "clause_index": intent.clause_index,
                        "intent_id": intent.intent_id,
                        "control_domain": intent.control_domain,
                        "permission_label": (
                            permission.permission_label.value
                            if role_permitted
                            else DecisionLabel.BLOCK.value
                        ),
                        "permission_score": (
                            permission.permission_score if role_permitted else 0.0
                        ),
                        "authorized": authorized,
                    }
                )
        request_authorized = (
            all(item["authorized"] is True for item in authorizations)
            if authorizations
            and all(item["authorized"] is not None for item in authorizations)
            else None
        )
        return {
            "authentication_state": state.authentication_state,
            "authenticated": authenticated,
            "subject_role": (
                trusted_context.subject_role if trusted_subject and trusted_context else None
            ),
            "subject_zone": (
                trusted_context.subject_zone if trusted_subject and trusted_context else None
            ),
            "intent_authorizations": authorizations,
            "authorized_for_request": request_authorized,
        }

    def process_audio_bytes(
        self,
        audio_bytes: bytes,
        *,
        audio_source: str = "test_wav",
        speaker_zone: str = "unknown",
        speaker_role: str = "unknown",
        array_channel: str | None = None,
        channel_index: int | None = None,
        trusted_context: TrustedRuntimeContext | None = None,
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
            trusted_context=trusted_context,
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
            trusted_context=None,
            session_id=session_id,
            event_sink=event_sink,
        )

    def _process_decoded_audio(
        self,
        decoded: DecodedAudio,
        *,
        speaker_role: str,
        trusted_context: TrustedRuntimeContext | None,
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
        verified_zone = (
            decoded.speaker_zone
            if decoded.zone_source.startswith("simulated_array_channel:")
            else (
                trusted_context.subject_zone
                if trusted_context is not None
                and trusted_context.subject_zone is not None
                and trusted_context.zone_source is not None
                else "unknown"
            )
        )
        verified_role = (
            trusted_context.subject_role
            if trusted_context is not None
            and trusted_context.subject_role is not None
            and trusted_context.subject_source is not None
            else "unknown"
        )
        metadata["declared_speaker_zone"] = decoded.speaker_zone
        metadata["declared_speaker_role"] = speaker_role
        metadata["trusted_speaker_zone"] = verified_zone
        metadata["trusted_speaker_role"] = verified_role
        metadata["asr_semantic_fusion_status"] = (
            "NO_EXPLICIT_ASR_SEMANTIC_FUSION_FORMULA"
        )
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
                "model_status": la.model_status,
                "inference_duration": la.inference_duration,
                "model": {
                    "name": la.model_metadata["model_name"],
                    "task": la.model_metadata["task"],
                    "status": la.model_status,
                },
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
                "pa_raw_score": pa.raw_score,
                "pa_score": pa.bonafide_score,
                "model_status": pa.model_status,
                "inference_duration": pa.inference_duration,
                "model": {
                    "name": pa.model_metadata["model_name"],
                    "task": pa.model_metadata["task"],
                    "status": pa.model_status,
                },
            },
        )
        trust = self.voice_trust_scorer.score(
            turn_id=turn_id,
            audio_source=decoded.audio_source,
            speaker_zone=verified_zone,
            speaker_role=verified_role,
            la_score=la.bonafide_score,
            pa_raw_score=pa.raw_score,
            pa_score=pa.bonafide_score,
            audio_fingerprint=decoded.fingerprint,
            spectrum_anomaly_score=spectrum.anomaly_score,
            model_metadata={
                "la": la.model_metadata,
                "pa": pa.model_metadata,
                "voice_trust_mode": self.voice_trust_mode,
                "authorization_effect_applied": (
                    self.voice_trust_mode == "enforce" and self.antispoof_enabled
                ),
            },
            force_block_reason=("SILENCE_OR_LOW_ENERGY" if spectrum.silence_detected else None),
        )
        emit(
            "VOICE_TRUST_DECIDED",
            "报告公式的语音可信评分完成",
            {
                "la_score": trust.la_score,
                "pa_raw_score": trust.pa_raw_score,
                "pa_score": trust.pa_score,
                "synthetic_risk": trust.synthetic_risk,
                "replay_risk": trust.replay_risk,
                "zone_risk": trust.zone_risk,
                "trust_score": trust.trust_score,
                "input_trust_label": trust.input_trust_label,
                "voice_trust_mode": self.voice_trust_mode,
                "authorization_effect_applied": (
                    self.voice_trust_mode == "enforce" and self.antispoof_enabled
                ),
                "la_model_status": la.model_status,
                "pa_model_status": pa.model_status,
                "spectrum_anomaly_score": trust.spectrum_anomaly_score,
            },
        )
        input_validity_blocked = bool(
            trust.model_metadata.get("input_validity_block_reason")
        )
        if trust.input_trust_label == DecisionLabel.BLOCK.value and (
            input_validity_blocked or self.voice_trust_mode == "enforce"
        ):
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
                session_id=session_id,
            ),
            trusted_context=(
                trusted_context
                or (
                    TrustedRuntimeContext(
                        subject_zone=decoded.speaker_zone,
                        subject_source="verified_audio_array",
                        zone_source=decoded.zone_source,
                    )
                    if decoded.zone_source.startswith("simulated_array_channel:")
                    else None
                )
            ),
            root_turn_id=root_turn_id,
            turn_id_override=turn_id,
            input_trust_override=trust,
            transcription_override=transcription,
            spectrum_analysis=spectrum,
            audio_input_metadata=metadata,
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
            clarification_request=pipeline_result.clarification_request,
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
        frame = self.semantic_service.parse_ordered_units(turn_id, "", [])
        demand = self.demand_service.build(frame)
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
        merged = merge_decision(gate, "EVIDENCE_BLOCK", DecisionLabel.BLOCK)
        decision = DecisionResult(
            turn_id=turn_id,
            decision=DecisionLabel.BLOCK,
            score_decision=DecisionLabel.BLOCK,
            final_decision=merged.final_decision,
            decision_sources=list(merged.decision_sources),
            decision_merge_reason=merged.decision_merge_reason,
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
            request_routing=request_routing,
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

    def _semantic_terminal_response(
        self,
        *,
        frame,
        demand: EvidenceDemand,
        input_trust: VoiceTrustResult,
        transcription: TranscriptionResult,
        root_turn_id: str,
        parent_turn_id: str | None,
        attempt_no: int,
        workflow_type: str,
        turn_started_at,
        emit: Callable[[str, str, dict[str, Any] | None], None],
        terminal_kind: str,
        request_routing=None,
    ) -> TextCommandResponse:
        """Finish Known PASS or semantic REVIEW before every downstream service."""

        if demand.intent_demands:
            raise RuntimeError("semantic terminal route created EvidenceDemand")
        is_review = terminal_kind == "SEMANTIC_REVIEW"
        is_non_vehicle = terminal_kind == "NON_VEHICLE_CONTROL"
        now = utc_now()
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
            turn_id=frame.turn_id,
            quality_metrics=quality,
            retrieval_metadata=retrieval,
            advanced_reasoning_status=(
                "NOT_INVOKED_SEMANTIC_REVIEW"
                if is_review
                else (
                    "NOT_APPLICABLE_NON_VEHICLE_CONTROL"
                    if is_non_vehicle
                    else "NOT_APPLICABLE_KNOWN_NON_EXECUTABLE"
                )
            ),
        )
        # This is an audit representation of a route that did not invoke SafetyGate.
        gate = SafetyGateResult(blocked=False, checks=[], reasons=[])
        factors = DecisionScoreFactors(
            semantic_quality=frame.semantic_confidence,
            evidence_coverage=None,
            evidence_coverage_applicable=False,
            applied_weights={},
            five_factors={},
        )
        decision = DecisionResult(
            turn_id=frame.turn_id,
            decision=DecisionLabel.REVIEW if is_review else DecisionLabel.PASS,
            score_decision=DecisionLabel.REVIEW if is_review else DecisionLabel.PASS,
            final_decision=DecisionLabel.REVIEW if is_review else DecisionLabel.PASS,
            decision_sources=[],
            decision_merge_reason=(
                "SEMANTIC_REVIEW terminal; downstream services were not invoked"
                if is_review
                else (
                    "NON_VEHICLE_CONTROL passed through; downstream vehicle services were not invoked"
                    if is_non_vehicle
                    else "KNOWN_NON_EXECUTABLE semantic PASS; downstream safety and execution chains are not applicable"
                )
            ),
            safety_score=1,
            soft_safety_score=1,
            gate_blocked=False,
            score_factors=factors,
            explanations=[
                "语义信息不完整或存在歧义；需要用户复核。"
                if is_review
                else (
                    "本安全网关放行，未涉及受本系统保护的车辆物理控制，交由原车语音助手继续处理。"
                    if is_non_vehicle
                    else "系统已明确理解该 Known 意图；PASS 不表示允许车辆执行。"
                )
            ],
            reason_codes=(
                ["SEMANTIC_REVIEW_TERMINAL"]
                if is_review
                else (
                    ["NON_VEHICLE_CONTROL_PASS"]
                    if is_non_vehicle
                    else ["KNOWN_NON_EXECUTABLE_SEMANTIC_PASS"]
                )
            ),
        )
        timing = TurnTiming(
            turn_started_at=turn_started_at,
            state_snapshot_at=now,
            decision_reference_time=now,
            completed_at=now,
            end_to_end_ms=max(0, (now - turn_started_at).total_seconds() * 1000),
        )
        audit_id = make_id("AUD")
        audit_quality = self._new_audit_quality(
            audit_id, stage5=input_trust.audio_source != "text_api"
        ).model_copy(
            update={
                "eligible_for_learning": False,
                "exclusion_reasons": [
                    "semantic review terminal"
                    if is_review
                    else "known non-executable semantic terminal"
                ],
            }
        )
        runtime_capability = self.runtime_capability()
        audit = AuditRecord(
            audit_id=audit_id,
            turn_id=frame.turn_id,
            root_turn_id=root_turn_id,
            parent_turn_id=parent_turn_id,
            attempt_no=attempt_no,
            workflow_type=workflow_type,
            input_trust_result=input_trust,
            transcription_result=transcription,
            semantic_frame=frame,
            request_routing=request_routing,
            evidence_demand=demand,
            candidate_recall_results=[],
            retrieval_metadata=retrieval,
            evidence_subgraph=subgraph,
            evidence_subgraph_summary={
                "graph_id": subgraph.graph_id,
                "node_count": 0,
                "edge_count": 0,
                "terminal_reason": terminal_kind,
            },
            evidence_quality_metrics=quality,
            safety_gate_result=gate,
            score_details=factors,
            final_decision=decision,
            complete_gate_result=gate,
            audit_quality=audit_quality,
            turn_timing=timing,
            runtime_capability=runtime_capability,
        )
        saved_audit = self.audit_repository.save(audit)
        clarification_request = None
        if is_review:
            self.workflow_repository.append_event(
                root_turn_id=root_turn_id,
                related_turn_id=frame.turn_id,
                parent_turn_id=parent_turn_id,
                event_type=WorkflowEventType.REVIEW_REQUESTED,
                payload={
                    "review_question": (
                        frame.normalized_text
                    ),
                    "candidate_count": (
                        0
                    ),
                    "intent_ids": [intent.intent_id for intent in frame.intents],
                    "attempt_no": attempt_no,
                },
            )
        interaction_request = self.interaction_service.project(saved_audit)
        response = TextCommandResponse(
            turn_id=frame.turn_id,
            root_turn_id=root_turn_id,
            parent_turn_id=parent_turn_id,
            attempt_no=attempt_no,
            workflow_type=workflow_type,
            input_trust_result=input_trust,
            transcription_result=transcription,
            semantic_frame=frame,
            request_routing=request_routing,
            evidence_demand=demand,
            evidence=[],
            query_vectors=[],
            retrieval_metadata=retrieval,
            candidate_evidence=[],
            evidence_subgraph=subgraph,
            quality_metrics=quality,
            safety_gate=gate,
            decision=decision,
            audit=saved_audit,
            actionable=False,
            retrieval_scopes=[],
            turn_timing=timing,
            runtime_capability=runtime_capability,
            interaction_request=interaction_request,
            clarification_request=clarification_request,
        )
        self._subgraphs[frame.turn_id] = subgraph
        self._turns[frame.turn_id] = response
        emit(
            "SEMANTIC_REVIEW_REQUIRED" if is_review else "KNOWN_NON_EXECUTABLE_COMPLETED",
            (
                "语义结果需要复核，已在证据需求构建前终止。"
                if is_review
                else (
                    "本安全网关放行，交由原车语音助手继续处理。"
                    if is_non_vehicle
                    else "已知不可执行意图已在语义层完成，不进入证据、安全或执行链。"
                )
            ),
            {
                "intent_ids": [intent.intent_id for intent in frame.intents],
                "review_candidates": frame.review_candidates[:4] if is_review else [],
            },
        )
        self.evidence_repository.complete_turn(frame.turn_id)
        return response

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
        event_sequence_start: int = 0,
        trusted_context: TrustedRuntimeContext | None = None,
    ) -> TextCommandResponse:
        if trusted_context is not None and not isinstance(
            trusted_context, TrustedRuntimeContext
        ):
            trusted_context = TrustedRuntimeContext.model_validate(trusted_context)
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
                    audio_input_metadata={
                        **(audio_input_metadata or {}),
                        **({"session_id": request.session_id} if request.session_id else {}),
                    },
                    trusted_context=trusted_context,
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
        trusted_context: TrustedRuntimeContext | None,
        emit: Callable[[str, str, dict[str, Any] | None], None],
    ) -> TextCommandResponse:
        overall_started = perf_counter()
        turn_started_at = utc_now()
        state = (
            self.vehicle.update_state(trusted_context.state_overrides)
            if trusted_context is not None
            and trusted_context.state_overrides is not None
            else self.vehicle.get_state()
        )
        runtime_safety_context = RuntimeSafetyContext.from_vehicle_state(state)
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
            confidence=None,
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
        request_routing = self.request_routing_service.route(request.text)
        frame = self.semantic_service.parse_ordered_units(
            turn_id, request.text, request_routing.units
        )
        if not request_routing.contains_vehicle_control:
            return self._semantic_terminal_response(
                frame=frame,
                demand=EvidenceDemand(turn_id=frame.turn_id, intent_demands=[]),
                input_trust=input_trust,
                transcription=transcription,
                root_turn_id=root_turn_id,
                parent_turn_id=parent_turn_id,
                attempt_no=attempt_no,
                workflow_type=workflow_type,
                turn_started_at=turn_started_at,
                emit=emit,
                terminal_kind=(
                    "SEMANTIC_REVIEW"
                    if any(unit.kind == SemanticUnitKind.UNCERTAIN for unit in request_routing.units)
                    else "NON_VEHICLE_CONTROL"
                ),
                request_routing=request_routing,
            )
        if confirmed and frame.intents:
            confirmed_intents = [
                intent.model_copy(
                    update={
                        "semantic_confidence": max(
                            float(
                                self.review_config.get(
                                    "confirm_semantic_confidence_floor", 0.95
                                )
                            ),
                            intent.semantic_confidence,
                        ),
                        "ambiguity_score": intent.ambiguity_score
                        * float(
                            self.review_config.get(
                                "confirm_ambiguity_multiplier", 0.5
                            )
                        ),
                    }
                )
                for intent in frame.intents
            ]
            frame = frame.model_copy(
                update={
                    "semantic_confidence": max(
                        float(self.review_config.get("confirm_semantic_confidence_floor", 0.95)),
                        frame.semantic_confidence,
                    ),
                    "ambiguity_score": frame.ambiguity_score
                    * float(self.review_config.get("confirm_ambiguity_multiplier", 0.5)),
                    "intents": confirmed_intents,
                }
            )
        mark_stage("semantic_complete")
        semantic_occurrences = list(frame.intents)
        formal_occurrences = [
            intent for intent in semantic_occurrences if intent.runtime_identity == "FORMAL"
        ]
        mixed_runtime_identity = bool(formal_occurrences) and len(formal_occurrences) != len(
            semantic_occurrences
        )
        continue_review_security_diagnostics = (
            frame.semantic_status == "REVIEW"
            and bool(formal_occurrences)
            and bool(frame.security_signals)
        )
        if frame.semantic_status != "OK" and not continue_review_security_diagnostics:
            return self._semantic_terminal_response(
                frame=frame,
                demand=EvidenceDemand(turn_id=frame.turn_id, intent_demands=[]),
                input_trust=input_trust,
                transcription=transcription,
                root_turn_id=root_turn_id,
                parent_turn_id=parent_turn_id,
                attempt_no=attempt_no,
                workflow_type=workflow_type,
                turn_started_at=turn_started_at,
                emit=emit,
                terminal_kind="SEMANTIC_REVIEW",
                request_routing=request_routing,
            )
        if (
            bool(frame.intents)
            and all(
                intent.runtime_identity == "KNOWN_NON_EXECUTABLE"
                for intent in semantic_occurrences
            )
        ):
            return self._semantic_terminal_response(
                frame=frame,
                demand=EvidenceDemand(turn_id=frame.turn_id, intent_demands=[]),
                input_trust=input_trust,
                transcription=transcription,
                root_turn_id=root_turn_id,
                parent_turn_id=parent_turn_id,
                attempt_no=attempt_no,
                workflow_type=workflow_type,
                turn_started_at=turn_started_at,
                emit=emit,
                terminal_kind="KNOWN_NON_EXECUTABLE",
                request_routing=request_routing,
            )
        demand = self.demand_service.build(frame)
        demand = self.knowledge_index.augment(demand)
        zone_permission: ZonePermissionResult | None = None
        zone_results: list[ZonePermissionResult] = []
        if (
            trusted_context is not None
            and trusted_context.subject_zone is not None
            and trusted_context.zone_source is not None
            and formal_occurrences
        ):
            zone_results = [
                self.zone_permission_service.evaluate(
                    trusted_context.subject_zone,
                    intent,
                    zone_source=trusted_context.zone_source,
                )
                for intent in formal_occurrences
            ]
            zone_permission = min(
                zone_results,
                key=lambda item: (item.permission_score, item.permission_label.value),
            )
            zone_payload = zone_permission.model_dump(mode="json")
            zone_payload["evaluated_intent_count"] = len(zone_results)
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
            {
                "semantic_status": frame.semantic_status,
                "security_signals": frame.security_signals,
                "intents": [
                    {
                        "clause_index": intent.clause_index,
                        "intent_id": intent.intent_id,
                        "action": intent.action,
                        "target": intent.target,
                        "risk_level": intent.risk_level,
                    }
                    for intent in semantic_occurrences
                ],
            },
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

        # Downstream services receive only FORMAL occurrences. The public frame
        # remains the sole frame and is restored before audit/response assembly.
        frame.intents = formal_occurrences

        authorization_fact = self._authorization_fact(
            state, frame.intents, trusted_context, zone_results if zone_permission else []
        )
        snapshot_nodes = self.evidence_repository.ingest_vehicle_state(
            state, authorization_fact, turn_id
        )
        state_snapshot_at = max(node.timestamp for node in snapshot_nodes)
        decision_reference_time = state_snapshot_at
        override_nodes = self.evidence_repository.ingest_observations(
            trusted_context.evidence_overrides if trusted_context is not None else [],
            turn_id,
        )
        self.index.upsert([*snapshot_nodes, *override_nodes])
        search_batches: list[list[EvidenceNode]] = []
        similarity_batches: list[dict[str, float]] = []
        retrieval_batches: list[RetrievalMetadata] = []
        for intent_demand in demand.intent_demands:
            search_results, intent_retrieval = self.index.search(
                intent_demand.query_vector
            )
            search_batches.append(
                [
                    self._candidate_copy(node)
                    for node, similarity in search_results
                ]
            )
            similarity_batches.append(
                {
                    node.node_id: round(similarity, 6)
                    for node, similarity in search_results
                }
            )
            retrieval_batches.append(intent_retrieval)
        if retrieval_batches:
            retrieval_metadata = retrieval_batches[0].model_copy(
                update={
                    "candidate_count": sum(
                        item.candidate_count for item in retrieval_batches
                    ),
                    "duration_ms": round(
                        sum(item.duration_ms for item in retrieval_batches), 4
                    ),
                    "final_top_k_node_ids": list(
                        dict.fromkeys(
                            node_id
                            for item in retrieval_batches
                            for node_id in item.final_top_k_node_ids
                        )
                    ),
                    "occurrence_layer_navigations": [
                        OccurrenceLayerNavigation(
                            clause_index=intent_demand.clause_index,
                            intent_id=intent_demand.intent_id,
                            navigation=item.security_layer_navigation,
                        )
                        for intent_demand, item in zip(
                            demand.intent_demands, retrieval_batches
                        )
                        if item.security_layer_navigation is not None
                    ],
                }
            )
        else:
            _, retrieval_metadata = self.index.search(
                [0.0] * self.index.status().dimension
            )
            retrieval_metadata = retrieval_metadata.model_copy(
                update={"candidate_count": 0, "final_top_k_node_ids": []}
            )
        candidate_by_id: dict[str, EvidenceNode] = {}
        for batch in search_batches:
            for node in batch:
                candidate_by_id.setdefault(node.node_id, node)
        candidate_evidence = list(candidate_by_id.values())
        emit(
            "EVIDENCE_RETRIEVED",
            "语义候选检索完成",
            {
                "candidate_count": len(candidate_evidence),
                "implementation": retrieval_metadata.implementation,
                **self.index.websocket_summary(retrieval_metadata),
            },
        )
        evidence_by_id: dict[str, EvidenceNode] = {}
        intent_evidence_resolutions: list[IntentEvidenceResolution] = []
        for intent_demand, intent_candidates, intent_similarities in zip(
            demand.intent_demands, search_batches, similarity_batches
        ):
            intent_evidence, intent_resolution = self.recall_service.resolve(
                intent_candidates,
                intent_demand,
                turn_id,
                missing_hard_gate=self.demand_service.missing_is_hard_gate(),
                candidate_similarities=intent_similarities,
            )
            for node in intent_evidence:
                evidence_by_id.setdefault(node.node_id, node)
            intent_evidence_resolutions.append(intent_resolution)
        resolution_projection = project_evidence_resolutions(
            intent_evidence_resolutions
        )
        recall_records = resolution_projection.mandatory_recall_records
        recalled_types = resolution_projection.recalled_types_union
        missing_types = resolution_projection.missing_required_types_union
        required_types = resolution_projection.required_types_union
        evidence = list(evidence_by_id.values())
        evidence = self.index.classify_nodes(evidence)
        retrieval_metadata = self.index.finalize_retrieval_metadata(
            retrieval_metadata, recall_records
        )
        mark_stage("retrieval_complete")
        emit(
            "MANDATORY_SUPPLEMENTED",
            "强制证据覆盖检查完成",
            {"recalled_types": recalled_types, "missing_types": missing_types},
        )
        existing_ids = {node.node_id for node in evidence}
        for evidence_type in required_types:
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
                                "metadata": {
                                    **node.metadata,
                                    "runtime_graph_history": True,
                                    "retrieval_origin": "mandatory_recall_history",
                                },
                            }
                        )
                    )
                    existing_ids.add(node.node_id)

        quality_started = perf_counter()
        evaluated, quality_metrics, physical_conflicts = self.quality_service.evaluate(
            evidence,
            required_types,
            resolution_projection.required_node_ids,
            (
                resolution_projection.required_semantic_similarities
                if required_types
                else resolution_projection.resolved_semantic_similarities
            ),
            now=decision_reference_time,
            scene_nodes=[*snapshot_nodes, *override_nodes],
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
        quality_metrics_by_occurrence = {}
        availability_snapshot = {
            "short_term_availability": quality_metrics.short_term_availability,
            "long_term_availability": quality_metrics.long_term_availability,
        }
        for intent in frame.intents:
            occurrence = (intent.clause_index, intent.intent_id)
            if occurrence not in resolution_projection.by_occurrence:
                continue
            occurrence_ids = (
                resolution_projection.resolved_node_ids_by_occurrence[occurrence]
                | resolution_projection.required_node_ids_by_occurrence[occurrence]
            )
            occurrence_nodes = [
                node for node in evaluated if node.node_id in occurrence_ids
            ]
            occurrence_required_types = resolution_projection.required_types_by_occurrence[
                occurrence
            ]
            occurrence_similarities = (
                resolution_projection.required_semantic_similarities_by_occurrence[occurrence]
                if occurrence_required_types
                else resolution_projection.resolved_semantic_similarities_by_occurrence[occurrence]
            )
            occurrence_metrics = self.quality_service.evaluate_occurrence(
                occurrence_nodes,
                occurrence_required_types,
                resolution_projection.required_node_ids_by_occurrence[occurrence],
                occurrence_similarities,
                scene_nodes=[*snapshot_nodes, *override_nodes],
                physical_conflicts=physical_conflicts,
            ).model_copy(update=availability_snapshot)
            quality_metrics_by_occurrence[occurrence] = occurrence_metrics
        emit(
            "EVIDENCE_QUALITY_EVALUATED",
            "证据质量与独立对齐路由计算完成",
            {
                "ecr": quality_metrics.ecr,
                "ecs": quality_metrics.ecs,
                "ef": quality_metrics.ef,
                "sas": quality_metrics.sas,
                "eas": quality_metrics.eas,
                "evidence_pair_count": quality_metrics.evidence_pair_count,
                "conflict_pair_count": quality_metrics.conflict_pair_count,
                "eas_weight_profile": quality_metrics.eas_weight_profile,
                "eas_weight_source": quality_metrics.eas_weight_source,
                "eas_weights": quality_metrics.eas_weights,
                "evidence_alignment_route": quality_metrics.evidence_alignment_route,
            },
        )

        subgraph = self.graph_builder.build(
            frame,
            evaluated,
            intent_evidence_resolutions,
            quality_metrics,
            retrieval_metadata,
            physical_conflicts,
        )
        graph_nodes_by_id = {node.node_id: node for node in subgraph.nodes}
        evaluated_node_ids = list(dict.fromkeys(node.node_id for node in evaluated))
        canonical_evidence = [
            graph_nodes_by_id[node_id]
            for node_id in evaluated_node_ids
            if node_id in graph_nodes_by_id
        ]
        emit(
            "GRAPH_BUILT",
            "运行时证据子图已构建",
            {
                "node_count": len(subgraph.nodes),
                "edge_count": len(subgraph.edges),
                "canonical_nodes": [
                    {
                        "node_id": node.node_id,
                        "semantic_similarity": resolution_projection.semantic_similarity_by_node_id.get(
                            node.node_id, 0.0
                        ),
                        "quality_label": node.quality_label.value,
                        "canonicalization_source": node.canonicalization_source,
                    }
                    for node in canonical_evidence[:20]
                ],
            },
        )

        reasoning_evidence = self._merge_latest(
            snapshot_nodes, override_nodes, canonical_evidence
        )
        final_top_k_ids = set(retrieval_metadata.final_top_k_node_ids)
        recall_origins = resolution_projection.retrieval_origins_by_node_id
        algorithm2_ids = final_top_k_ids | set(
            resolution_projection.resolved_physical_node_ids
        )
        memory_evidence = [
            node for node in canonical_evidence if node.node_id in algorithm2_ids
        ]
        retrieval_origins: dict[str, str] = {}
        for node in memory_evidence:
            from_hnsw = node.node_id in final_top_k_ids
            recall_origin = recall_origins.get(node.node_id)
            if recall_origin is not None and recall_origin.value == "BOTH":
                retrieval_origins[node.node_id] = "BOTH"
            elif from_hnsw and recall_origin is not None and recall_origin.value == "MANDATORY_RECALL":
                retrieval_origins[node.node_id] = "BOTH"
            elif from_hnsw:
                retrieval_origins[node.node_id] = "HNSW"
            elif recall_origin is not None and recall_origin.value == "MANDATORY_RECALL":
                retrieval_origins[node.node_id] = "MANDATORY_RECALL"
            else:
                retrieval_origins[node.node_id] = "NONE"
        memory = self.memory_service.propagate(
            memory_evidence,
            frame,
            physical_conflicts,
            semantic_similarity_by_node_id=(
                resolution_projection.semantic_similarity_by_node_id
            ),
            retrieval_origins=retrieval_origins,
        )
        emit(
            "MEMORY_PROPAGATED",
            "Algorithm 2稀疏关系图与相邻层传播完成",
            {
                "layer_counts": {
                    key: len(value)
                    for key, value in memory.layered_memory_graph.get("layers", {}).items()
                },
                "relation_edge_counts": {
                    relation.value: sum(
                        relation in edge.relation_types for edge in memory.relation_edges
                    )
                    for relation in MemoryRelationType
                },
                "average_degree": memory.degree_statistics.average_degree,
                "propagation_count": len(memory.propagation_steps),
            },
        )
        causal = self.causal_service.apply(
            frame,
            memory_evidence,
            memory,
            intent_evidence_resolutions=intent_evidence_resolutions,
        )
        emit(
            "CAUSAL_CORRECTED",
            "确定性因果支持修正完成",
            {
                "model_build_id": (
                    causal.model_snapshot.model_build_id
                    if causal.model_snapshot is not None
                    else causal.model_version
                ),
                "history_count": causal.sample_count,
                "causal_edge_count": len(causal.pruned_edges),
                "confidence_status": causal.confidence_status,
                "decision_confidence": causal.decision_confidence,
                "top_corrected_nodes": [
                    item.model_dump(mode="json")
                    for item in sorted(
                        causal.node_weights,
                        key=lambda value: -(value.corrected_weight or 0.0),
                    )[:5]
                ],
            },
        )
        validation = self.validation_service.validate(frame, reasoning_evidence, physical_conflicts)
        emit(
            "EVIDENCE_VALIDATED",
            "证据与上下文声明校验完成",
            {
                "conflict_count": validation.conflict_count,
                "max_severity": validation.max_severity,
                "jailbreak_risk_base": validation.jailbreak_risk_base,
                "jailbreak_risk_severity_component": validation.jailbreak_risk_severity_component,
                "jailbreak_risk": validation.jailbreak_risk,
                "jailbreak_flag": validation.jailbreak_flag,
            },
        )
        gate = self.gate_service.evaluate(
            frame,
            demand,
            reasoning_evidence,
            intent_evidence_resolutions,
            validation,
            memory,
            runtime_capability,
            runtime_safety_context,
        )
        emit(
            "GATE_CHECKED",
            "硬性安全门检查完成",
            gate.model_dump(mode="json"),
        )
        scoring_started = perf_counter()
        assessments, aggregate_safety_decision = self.decision_service.assess_intents(
            frame,
            reasoning_evidence,
            gate,
            validation,
            causal,
            memory,
            runtime_capability,
            resolution_projection,
            quality_metrics_by_occurrence,
        )
        if assessments:
            priority = {
                DecisionLabel.PASS: 0,
                DecisionLabel.REVIEW: 1,
                DecisionLabel.BLOCK: 2,
            }
            lowest = min(
                assessments,
                key=lambda assessment: (assessment.safety_score, assessment.clause_index),
            )
            projected_score_decision = max(
                (assessment.score_decision for assessment in assessments),
                key=lambda value: priority[value],
            )
            final_decision = aggregate_safety_decision or DecisionLabel.REVIEW
            reason_codes = list(
                dict.fromkeys(
                    code
                    for assessment in assessments
                    for code in assessment.reason_codes
                )
            )
            decision_sources = list(
                dict.fromkeys(
                    source
                    for assessment in assessments
                    if assessment.final_safety_decision == aggregate_safety_decision
                    for source in assessment.decision_sources
                )
            )
            explanations = [
                "完整 per-intent 安全评价见 intent_safety_assessments。",
                *[
                    f"occurrence {assessment.clause_index}:{assessment.intent_id} "
                    f"安全裁决={assessment.final_safety_decision.value}"
                    for assessment in assessments
                ],
            ]
            if len(frame.intents) > 1:
                # 多意图不再无条件强制 REVIEW：是否需复核由决策后的「需复核意图判定」
                # 统一决定（有意图需复核 → 弹窗复核；全部明确 → 直接放行）。
                reason_codes.append("MULTI_INTENT_GROUP")
                explanations.append(
                    "检测到多意图组合；是否需复核由后续需复核意图判定决定。"
                )
            if frame.semantic_status == "REVIEW" and final_decision == DecisionLabel.PASS:
                final_decision = DecisionLabel.REVIEW
                explanations.append("SemanticFrame 为 REVIEW，整轮最终裁决至少保持 REVIEW。")
            decision = DecisionResult(
                turn_id=frame.turn_id,
                decision=projected_score_decision,
                score_decision=projected_score_decision,
                final_decision=final_decision,
                decision_sources=decision_sources,
                decision_merge_reason=(
                    f"Intent safety aggregate={aggregate_safety_decision.value}; "
                    f"top-level score is conservative projection from "
                    f"{len(assessments)} occurrence assessments"
                ),
                safety_score=lowest.safety_score,
                soft_safety_score=lowest.safety_score,
                gate_blocked=gate.blocked,
                gate_reasons=list(gate.reasons),
                score_evaluation_mode=(
                    "diagnostic_after_gate" if gate.blocked else "normal"
                ),
                score_factors=lowest.score_factors,
                explanations=explanations,
                review_question=(
                    "请确认是否继续执行当前指令。"
                    if final_decision == DecisionLabel.REVIEW
                    else None
                ),
                jailbreak_risk=validation.jailbreak_risk,
                decision_confidence=causal.decision_confidence,
                reason_codes=reason_codes,
                causal_correction=causal,
                memory_propagation=memory,
                grounding_failures=validation.grounding_failures,
                conflicts=validation.conflicts,
                intent_safety_assessments=assessments,
                aggregate_safety_decision=aggregate_safety_decision,
            )
        else:
            diagnostic_decision = self.decision_service.decide(
                frame,
                reasoning_evidence,
                gate,
                quality_metrics.evidence_alignment_route,
                validation,
                causal,
                memory,
                runtime_capability,
                required_types=resolution_projection.required_types_union,
                validated_types=resolution_projection.validated_types_union,
                required_node_ids=resolution_projection.required_node_ids,
                resolved_node_ids=resolution_projection.resolved_physical_node_ids,
            )
            decision = diagnostic_decision.model_copy(
                update={
                    "intent_safety_assessments": [],
                    "aggregate_safety_decision": None,
                }
            )
        decision, gate = self._apply_voice_constraints(
            decision,
            gate,
            input_trust,
            zone_permission,
        )
        # 需复核意图判定：
        #  - 单意图：区域歧义（DOOR/WINDOW 未指定哪一侧）也算需复核 → 弹窗选区域。
        #  - 多意图：区域歧义不算需复核（动作已明确，只是区域未指定）；只有安全裁决
        #    REVIEW 的意图才需复核。
        # 仅当 final_decision 为 PASS 且有需复核意图时升级 REVIEW（触发复核弹窗）；
        # BLOCK 优先保持（BLOCK 意图不弹窗）；全部明确则保持 PASS 直接放行（多意图不签令牌）。
        multi_intent = len(frame.intents) > 1
        review_required_intents: list[str] = []
        for intent in frame.intents:
            if not multi_intent:
                area_ambiguous = (
                    intent.area in (None, "unknown")
                    and intent.target in ("车门", "车窗")
                    and any(
                        area in allowed_areas_for_intent(intent.intent_id)
                        for area in ("LEFT_FRONT", "RIGHT_FRONT", "LEFT_REAR", "RIGHT_REAR")
                    )
                )
                if area_ambiguous:
                    review_required_intents.append(intent.intent_id)
                    continue
            assessment = next(
                (
                    item
                    for item in (decision.intent_safety_assessments or [])
                    if item.clause_index == intent.clause_index
                ),
                None,
            )
            if assessment and assessment.final_safety_decision == DecisionLabel.REVIEW:
                review_required_intents.append(intent.intent_id)

        if decision.final_decision == DecisionLabel.PASS and review_required_intents:
            all_area_only = all(
                intent.area in (None, "unknown") and intent.target in ("车门", "车窗")
                for intent in frame.intents
                if intent.intent_id in review_required_intents
            )
            review_reason = (
                "AREA_AMBIGUOUS" if all_area_only else "MULTI_INTENT_REVIEW_REQUIRED"
            )
            decision = decision.model_copy(
                update={
                    "final_decision": DecisionLabel.REVIEW,
                    "reason_codes": list(
                        dict.fromkeys([*decision.reason_codes, review_reason])
                    ),
                    "explanations": [
                        *decision.explanations,
                        "检测到需复核的操作，需用户确认后再执行。",
                    ],
                }
            )
            emit(
                "REVIEW_REQUIRED_INTENTS",
                "存在需复核的意图",
                {"intent_ids": review_required_intents, "reason": review_reason},
            )
        # 最终一致性复核层：用户对车辆现状的状态声明 与 本次裁决已取得的证据核验。
        # 仅在 base_decision 为 PASS 时参与；声明冲突将 PASS 提升为 REVIEW，
        # 原 REVIEW/BLOCK 保持不变（BLOCK > REVIEW > PASS 顺序永不破坏）。
        claim_check: ClaimCheckResult | None = None
        if decision.final_decision == DecisionLabel.PASS and frame.intents:
            claim_check = self.claim_service.check(frame.raw_text, canonical_evidence)
            if claim_check.has_conflict:
                conflict_items = claim_check.conflict_items
                decision = decision.model_copy(
                    update={
                        "final_decision": DecisionLabel.REVIEW,
                        "reason_codes": list(
                            dict.fromkeys([*decision.reason_codes, "CONTEXT_CLAIM_CONFLICT"])
                        ),
                        "explanations": [
                            *decision.explanations,
                            "用户对车辆现状的状态声明与本次裁决的可信证据冲突，"
                            "PASS 降级为 REVIEW（冲突声明："
                            + "、".join(f"“{item.matched_span}”" for item in conflict_items)
                            + "）。",
                        ],
                    }
                )
                emit(
                    "CLAIM_CONFLICT",
                    "用户状态声明与车辆证据冲突",
                    {
                        "conflict_items": [
                            {
                                "claim_type": item.claim_type.value,
                                "matched_span": item.matched_span,
                                "evidence_type": item.evidence_type,
                            }
                            for item in conflict_items
                        ],
                    },
                )
        clarification_context = audio_input_metadata.get("clarification_context", {})
        expected_identity = (
            clarification_context.get("expected_canonical_identity")
            if isinstance(clarification_context, dict)
            else None
        )
        if isinstance(expected_identity, dict) and expected_identity.get("intent_id"):
            expected_slots = expected_identity.get("slots", {})
            if not isinstance(expected_slots, dict):
                expected_slots = {}
            identity_matches = any(
                intent.intent_id == expected_identity.get("intent_id")
                and intent.runtime_identity == expected_identity.get("runtime_identity")
                and all(
                    getattr(intent, key, None) == value
                    for key, value in expected_slots.items()
                )
                for intent in frame.intents
            )
            if not identity_matches:
                decision = decision.model_copy(
                    update={
                        "decision": DecisionLabel.REVIEW,
                        "score_decision": DecisionLabel.REVIEW,
                        "final_decision": DecisionLabel.REVIEW,
                        "authorization_token": None,
                        "execution_tokens": [],
                        "reason_codes": list(
                            dict.fromkeys(
                                [
                                    *decision.reason_codes,
                                    "CLARIFICATION_REPARSE_MISMATCH",
                                ]
                            )
                        ),
                        "explanations": [
                            *decision.explanations,
                            "澄清候选重解析后的语义与候选承诺不一致，已保持 REVIEW。",
                        ],
                        "review_question": "候选语义校验未通过，请重新描述指令。",
                    }
                )
                emit(
                    "CLARIFICATION_REPARSE_MISMATCH",
                    "澄清候选与子轮次语义不一致，禁止授权与执行",
                    {"expected_identity": expected_identity},
                )
        emit(
            "DECISION_COMPLETED",
            "最终裁决完成",
            {
                "final_decision": decision.final_decision.value,
                "score_decision": decision.score_decision.value,
                "decision_sources": [source.value for source in decision.decision_sources],
                "decision_merge_reason": decision.decision_merge_reason,
                "soft_safety_score": decision.soft_safety_score,
                "gate_blocked": decision.gate_blocked,
            },
        )
        scoring_ms = (perf_counter() - scoring_started) * 1000
        interpreter = self.interpreter_service.generate(
            frame=frame,
            demand=demand,
            evidence=canonical_evidence,
            missing_types=missing_types,
            gate=gate,
            decision=decision,
            causal=causal,
            decision_sources=[source.value for source in decision.decision_sources],
            decision_merge_reason=decision.decision_merge_reason,
            vehicle_state=self.vehicle.get_state().model_dump(mode="json"),
        )
        if interpreter.review_question != decision.review_question:
            decision = decision.model_copy(
                update={"review_question": interpreter.review_question}
            )
        emit(
            "EXPLANATION_GENERATED",
            "受限解释与复核数据生成完成",
            {
                "generation_mode": interpreter.generation_metadata.generation_mode,
                "candidate_count": len(interpreter.candidate_interpretations),
                "validation_status": interpreter.generation_metadata.validation_status,
            },
        )
        advanced = AdvancedReasoningResult(
            memory_propagation=memory,
            causal_correction=causal,
            validation=validation,
            five_factor_score=decision.score_factors.five_factors,
            decision_confidence=causal.decision_confidence,
            explanations=decision.explanations,
            recognized_command={
                "semantic_status": frame.semantic_status,
                "security_signals": frame.security_signals,
                "intents": [
                    {
                        "clause_index": intent.clause_index,
                        "intent_id": intent.intent_id,
                        "action": intent.action,
                        "target": intent.target,
                        "risk_level": intent.risk_level,
                    }
                    for intent in semantic_occurrences
                ],
                "retrieval_scopes": [
                    item.retrieval_scope for item in demand.intent_demands
                ],
            },
            mandatory_evidence_complete=not missing_types,
            supporting_evidence_ids=[
                node.node_id
                for node in canonical_evidence
                if node.node_id in resolution_projection.required_node_ids
                and node.quality_label.value in {"VALID", "SUSPICIOUS"}
            ],
            conflicting_evidence_ids=sorted(
                {
                    node_id
                    for conflict in validation.conflicts
                    for node_id in conflict.evidence_node_ids
                }
            ),
            hit_rules=gate.hit_rules,
            review_question=interpreter.review_question,
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
        core_decision_ms = round((perf_counter() - overall_started) * 1000, 4)
        set_metric("core_decision_ms", core_decision_ms)
        mark_stage("core_decision_complete")
        timing = TurnTiming(
            turn_started_at=turn_started_at,
            state_snapshot_at=state_snapshot_at,
            decision_reference_time=decision_reference_time,
            completed_at=completed_at,
            end_to_end_ms=core_decision_ms,
        )
        audit_id = make_id("AUD")
        audit_build_started = perf_counter()
        frame.intents = semantic_occurrences
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
            request_routing=request_routing,
            evidence_demand=demand,
            candidate_recall_results=[
                node
                for node in canonical_evidence
                if node.node_id in {item.node_id for item in candidate_evidence}
            ],
            vectorization_metadata=[
                item.vectorization_metadata
                for item in demand.intent_demands
                if item.vectorization_metadata is not None
            ],
            query_vector_digests=[
                item.vectorization_metadata.vector_digest
                for item in demand.intent_demands
                if item.vectorization_metadata is not None
            ],
            retrieval_metadata=retrieval_metadata,
            evidence_subgraph=subgraph,
            evidence_subgraph_summary={
                "graph_id": subgraph.graph_id,
                "node_count": len(subgraph.nodes),
                "edge_count": len(subgraph.edges),
                "canonicalization_source": "FIELD_LEVEL_EVIDENCE_NODE_MERGE",
                "canonicalization_warning_count": sum(
                    len(node.canonicalization_warnings) for node in canonical_evidence
                ),
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
            decision_explanation=interpreter.decision_explanation,
            candidate_interpretations=interpreter.candidate_interpretations,
            candidate_availability=interpreter.candidate_availability,
            interpreter_review_question=interpreter.review_question,
            recommended_recovery=interpreter.recommended_recovery,
            generation_metadata=interpreter.generation_metadata,
            interpreter_validation_result=interpreter.validation_result,
            interpreter_result=interpreter,
            advanced_reasoning=advanced,
            turn_timing=timing,
            runtime_capability=runtime_capability,
        )
        set_metric(
            "audit_build_ms", round((perf_counter() - audit_build_started) * 1000, 4)
        )
        set_metric("turn_id", turn_id)
        set_metric("audit_id", audit_id)
        mark_stage("audit_object_built")
        saved_audit = self.audit_repository.save(audit)
        persisted_decision_snapshot = AuditSnapshotBuilder.from_audit(saved_audit)
        if persisted_decision_snapshot is not None:
            self.workflow_repository.append_event(
                root_turn_id=root_turn_id,
                related_turn_id=turn_id,
                parent_turn_id=parent_turn_id,
                event_type=WorkflowEventType.DECISION_SNAPSHOT_CAPTURED,
                payload={
                    "audit_id": saved_audit.audit_id,
                    "decision_snapshot": persisted_decision_snapshot.model_dump(
                        mode="json"
                    ),
                },
            )
        emit(
            "AUDIT_SAVED",
            "裁决审计已追加保存",
            {"audit_id": saved_audit.audit_id, "current_hash": saved_audit.current_hash},
        )
        self.evidence_repository.complete_turn(turn_id)
        actionable = (
            frame.semantic_status == "OK"
            and bool(demand.intent_demands)
            and not mixed_runtime_identity
            and all(intent.runtime_identity == "FORMAL" for intent in frame.intents)
            and all(
                item.retrieval_scope == "control_evidence"
                for item in demand.intent_demands
            )
            and runtime_capability.semantic_control_mode == SemanticControlMode.FULL
            # A multi-operation utterance must be reduced to one selected
            # operation by the unified interaction before any token exists.
            and len(frame.intents) == 1
        )
        clarification_request = None
        if decision.final_decision == DecisionLabel.REVIEW:
            self.workflow_repository.append_event(
                root_turn_id=root_turn_id,
                related_turn_id=turn_id,
                parent_turn_id=parent_turn_id,
                event_type=WorkflowEventType.REVIEW_REQUESTED,
                payload={
                    "review_question": interpreter.review_question,
                    "candidate_count": len(interpreter.candidate_interpretations),
                    "intent_ids": [intent.intent_id for intent in frame.intents],
                    "attempt_no": attempt_no,
                },
            )
            emit(
                "REVIEW_REQUIRED",
                "当前轮次需要用户复核",
                {
                    "review_question": interpreter.review_question,
                    "candidate_count": len(interpreter.candidate_interpretations),
                },
            )

        response_decision = decision
        if (
            not suppress_authorization
            and decision.final_decision == DecisionLabel.PASS
            and not decision.gate_blocked
            and actionable
        ):
            try:
                token_issue_started = perf_counter()
                if len(frame.intents) <= 1:
                    if self.authorization_service.is_executable(frame):
                        grant = self.authorization_service.issue(
                            root_turn_id=root_turn_id,
                            turn_id=turn_id,
                            frame=frame,
                            state=state,
                        )
                        response_decision = decision.model_copy(
                            update={"authorization_token": grant.authorization_token}
                        )
                else:
                    grants = self.authorization_service.issue_multi(
                        root_turn_id=root_turn_id,
                        turn_id=turn_id,
                        frame=frame,
                        state=state,
                    )
                    intent_by_id = {intent.intent_id: intent for intent in frame.intents}
                    execution_tokens = [
                        ExecutionTokenView(
                            token=grant.authorization_token,
                            intent_id=grant.metadata.intent_id or "",
                            label=f"{intent_by_id.get(grant.metadata.intent_id, frame.intents[0]).action}"
                            f"{intent_by_id.get(grant.metadata.intent_id, frame.intents[0]).target or ''}",
                            action=intent_by_id.get(grant.metadata.intent_id, frame.intents[0]).action,
                            target=intent_by_id.get(grant.metadata.intent_id, frame.intents[0]).target,
                            area=intent_by_id.get(grant.metadata.intent_id, frame.intents[0]).area,
                        )
                        for grant in grants
                        if grant.metadata.intent_id in intent_by_id
                    ]
                    if execution_tokens:
                        response_decision = decision.model_copy(
                            update={"execution_tokens": execution_tokens}
                        )
                set_metric(
                    "token_issue_ms",
                    round((perf_counter() - token_issue_started) * 1000, 4),
                )
                set_metric("token_was_issued", True)
                mark_stage("token_issued")
                issued_views = response_decision.execution_tokens
                issued_ids = (
                    [view.token[:16] for view in issued_views]
                    if issued_views
                    else [str(response_decision.authorization_token or "")[:16]]
                )
                emit(
                    "TOKEN_ISSUED",
                    "一次性车辆执行授权已签发",
                    {
                        "token_count": len(issued_ids),
                        "token_ids": issued_ids,
                    },
                )
            except AuthorizationTokenError as exc:
                self.workflow_repository.append_event(
                    root_turn_id=root_turn_id,
                    related_turn_id=turn_id,
                    event_type=WorkflowEventType.TOKEN_REJECTED,
                    payload={"reason": str(exc)},
                )
        interaction_request = self.interaction_service.project(
            saved_audit,
            execution_allowed=bool(
                response_decision.authorization_token or response_decision.execution_tokens
            ),
        )
        regulation_rationale = self._regulation_rationale(
            " ".join(item.query_text for item in demand.intent_demands)
            or frame.raw_text,
            required_types=[
                item for intent_demand in demand.intent_demands for item in intent_demand.required_types
            ],
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
            request_routing=request_routing,
            evidence_demand=demand,
            evidence=canonical_evidence,
            query_vectors=[item.query_vector for item in demand.intent_demands],
            retrieval_metadata=retrieval_metadata,
            candidate_evidence=[
                node
                for node in canonical_evidence
                if node.node_id in {item.node_id for item in candidate_evidence}
            ],
            evidence_subgraph=subgraph,
            quality_metrics=quality_metrics,
            safety_gate=gate,
            decision=response_decision,
            audit=saved_audit,
            actionable=actionable,
            retrieval_scopes=[item.retrieval_scope for item in demand.intent_demands],
            advanced_reasoning=advanced,
            memory_propagation=memory,
            causal_correction=causal,
            interpreter_result=interpreter,
            grounding_failures=validation.grounding_failures,
            jailbreak_conflicts=validation.conflicts,
            jailbreak_risk=validation.jailbreak_risk,
            score_factors=decision.score_factors.five_factors,
            decision_confidence=causal.decision_confidence,
            turn_timing=timing,
            runtime_capability=runtime_capability,
            interaction_request=interaction_request,
            clarification_request=clarification_request,
            regulation_rationale=regulation_rationale,
        )
        mark_stage("response_ready")
        # 原始令牌只存在于本次返回对象；内存缓存与 SQLite 均保存去敏版本。
        self._turns[turn_id] = response.model_copy(
            update={
                "decision": response.decision.model_copy(
                    update={"authorization_token": None}
                )
            }
        )
        try:
            decision_snapshot = persisted_decision_snapshot
            explanation_context = self.audit_explanation_service.context(
                saved_audit,
                decision_snapshot=(
                    decision_snapshot.model_dump(mode="json")
                    if decision_snapshot is not None
                    else None
                ),
            )
            explanation_context = explanation_context.model_copy(
                update={
                    "authorization_status": (
                        "AUTHORIZED"
                        if response_decision.authorization_token is not None
                        else "NOT_AUTHORIZED"
                    ),
                    "execution_status": None,
                }
            )
            explanation_result = self.audit_explanation_service.generate(
                explanation_context
            )
            self.workflow_repository.append_event(
                root_turn_id=root_turn_id,
                related_turn_id=turn_id,
                parent_turn_id=parent_turn_id,
                event_type=WorkflowEventType.LLM_EXPLANATION_GENERATED,
                payload={
                    "audit_id": saved_audit.audit_id,
                    "llm_explanation_status": explanation_result.status,
                    "llm_explanation": explanation_result.explanation,
                    "llm_model": explanation_result.model,
                    "llm_generated_at": explanation_result.generated_at.isoformat(),
                    "failure_reason": explanation_result.failure_reason,
                },
            )
        except Exception:
            # Explanation is strictly post-decision and must never invalidate the
            # persisted audit, authorization grant, or command response.
            _LOGGER.warning("AI audit explanation append failed", exc_info=True)
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

    @staticmethod
    def trusted_context_from_audit(audit: AuditRecord) -> TrustedRuntimeContext | None:
        nodes = audit.evidence_subgraph.nodes if audit.evidence_subgraph is not None else []
        authorization = next(
            (
                node
                for node in reversed(nodes)
                if node.evidence_type == "AUTHORIZATION_STATE"
                and isinstance(node.value, dict)
                and node.value.get("subject_role") is not None
                and node.value.get("subject_zone") is not None
            ),
            None,
        )
        if authorization is None:
            return None
        return TrustedRuntimeContext(
            subject_role=str(authorization.value["subject_role"]),
            subject_zone=str(authorization.value["subject_zone"]),
            subject_source="preserved_audit_authorization",
            zone_source="preserved_audit_authorization",
        )

    def get_reasoning(self, turn_id: str) -> AdvancedReasoningResult | None:
        turn = self.get_turn(turn_id)
        if turn is None:
            return None
        return turn.advanced_reasoning

    def rebuild_index(self, exclude_types: list[str] | None = None) -> IndexStatus:
        return self.index.build(self.evidence_repository.all_nodes(), exclude_types)

    def update_index_parameters(self, request: IndexParametersRequest) -> IndexStatus:
        return self.index.update_parameters(request)

    def rebuild_causal(self):
        return self.causal_service.status()

    def causal_status(self):
        return self.causal_service.status()

    # 天气 → 环境照度联动:夜间/低照度天气自动反映为低照度,晴朗/多云恢复高照度。
    # 安全规则 LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED 依赖 ambient_light 判定"夜间/低照度",
    # 若不联动,用户只设 weather=NIGHT 时 ambient_light 仍为白天值,夜间关前照灯会漏拦截。
    _LOW_LIGHT_WEATHERS = frozenset(
        {"NIGHT", "SUNSET", "RAIN", "FOG", "夜间", "黄昏", "雨", "雾"}
    )
    _HIGH_LIGHT_WEATHERS = frozenset({"CLEAR", "CLOUDY", "晴朗", "多云"})
    _LOW_LIGHT_AMBIENT_LUX = 5
    _HIGH_LIGHT_AMBIENT_LUX = 100

    @staticmethod
    def _link_weather_ambient_light(patch: VehicleStatePatch) -> VehicleStatePatch:
        updates = patch.model_dump(exclude_unset=True)
        weather = updates.get("weather")
        if weather is None or "ambient_light" in updates:
            return patch
        code = str(weather).strip().upper()
        if code in CommandPipeline._LOW_LIGHT_WEATHERS:
            return patch.model_copy(
                update={"ambient_light": CommandPipeline._LOW_LIGHT_AMBIENT_LUX}
            )
        if code in CommandPipeline._HIGH_LIGHT_WEATHERS:
            return patch.model_copy(
                update={"ambient_light": CommandPipeline._HIGH_LIGHT_AMBIENT_LUX}
            )
        return patch

    def get_vehicle_state(self) -> VehicleState:
        return self.vehicle.get_state()

    def update_vehicle_state(self, patch: VehicleStatePatch) -> VehicleState:
        with self._command_lock:
            update_turn_id = make_id("STATE_UPDATE")
            self.evidence_repository.begin_turn(update_turn_id)
            state = self.vehicle.update_state(
                self._link_weather_ambient_light(patch)
            )
            nodes = self.evidence_repository.ingest_vehicle_state(
                state,
                None,
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
                None,
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
            self.index.build(self.evidence_repository.current_nodes())
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
                session_id=session_id,
            ),
            trusted_context=TrustedRuntimeContext(
                evidence_overrides=observations,
                subject_role=state.occupant_role or "unknown",
                subject_zone=state.speaker_zone or "unknown",
                subject_source="demo_scenario",
                zone_source="demo_scenario",
            ),
        )

    def timeline(self, turn_id: str) -> TurnTimeline:
        root = self.review_service.root_for_turn(turn_id)
        audits = self.audit_repository.records_for_root(root)
        if not audits:
            root_audit = self.audit_repository.get_by_turn(root)
            audits = [root_audit] if root_audit else []
        events = self.workflow_repository.events(root)
        ordered: list[dict[str, Any]] = [
            {
                "kind": "AUDIT",
                "timestamp": audit.created_at.isoformat(),
                "turn_id": audit.turn_id,
                "audit_id": audit.audit_id,
                "workflow_type": audit.workflow_type,
                "decision": self.effective_audit_resolver.resolve(
                    audit
                ).effective_decision.final_decision.value,
                "original_decision": audit.final_decision.final_decision.value,
            }
            for audit in audits
        ]
        for audit in audits:
            timestamp = audit.created_at.isoformat()
            memory = audit.memory_propagation
            if memory is not None:
                relation_edge_counts: dict[str, int] = {}
                for edge in memory.relation_edges:
                    for relation_type in edge.relation_types:
                        key = relation_type.value
                        relation_edge_counts[key] = relation_edge_counts.get(key, 0) + 1
                ordered.append(
                    {
                        "kind": "PIPELINE_STAGE",
                        "stage": "MEMORY_PROPAGATED",
                        "timestamp": timestamp,
                        "turn_id": audit.turn_id,
                        "audit_id": audit.audit_id,
                        "status": "COMPLETED",
                        "summary": {
                            "layer_counts": memory.layered_memory_graph.get("layer_counts", {}),
                            "relation_edge_counts": relation_edge_counts,
                            "average_degree": memory.degree_statistics.average_degree,
                            "propagation_count": len(memory.propagation_steps),
                        },
                    }
                )
            causal = audit.causal_correction
            if causal is not None:
                ordered.append(
                    {
                        "kind": "PIPELINE_STAGE",
                        "stage": "CAUSAL_CORRECTED",
                        "timestamp": timestamp,
                        "turn_id": audit.turn_id,
                        "audit_id": audit.audit_id,
                        "status": causal.confidence_status,
                        "summary": {
                            "model_build_id": (
                                causal.model_snapshot.model_build_id
                                if causal.model_snapshot is not None
                                else causal.model_version
                            ),
                            "history_sample_count": causal.sample_count,
                            "causal_edge_count": len(causal.pruned_edges),
                            "confidence_status": causal.confidence_status,
                            "decision_confidence": causal.decision_confidence,
                        },
                    }
                )
            metadata = audit.generation_metadata
            if metadata is not None:
                ordered.append(
                    {
                        "kind": "PIPELINE_STAGE",
                        "stage": "EXPLANATION_GENERATED",
                        "timestamp": timestamp,
                        "turn_id": audit.turn_id,
                        "audit_id": audit.audit_id,
                        "status": metadata.validation_status,
                        "summary": {
                            "generation_mode": metadata.generation_mode,
                            "candidate_count": len(audit.candidate_interpretations),
                            "validation_status": metadata.validation_status,
                        },
                    }
                )
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
        kind_order = {"PIPELINE_STAGE": 0, "AUDIT": 1, "WORKFLOW_EVENT": 2}
        stage_order = {
            "MEMORY_PROPAGATED": 0,
            "CAUSAL_CORRECTED": 1,
            "EXPLANATION_GENERATED": 2,
        }
        ordered.sort(
            key=lambda item: (
                item["timestamp"],
                kind_order[item["kind"]],
                stage_order.get(str(item.get("stage", "")), 0),
            )
        )
        timeline_items: list[dict[str, Any]] = []
        for sequence, item in enumerate(ordered, 1):
            if item["kind"] == "PIPELINE_STAGE":
                timeline_items.append(
                    {
                        "sequence": sequence,
                        "stage": item["stage"],
                        "timestamp": item["timestamp"],
                        "status": item["status"],
                        "summary": item["summary"],
                        "turn_id": item["turn_id"],
                        "audit_id": item["audit_id"],
                    }
                )
                continue
            if item["kind"] == "AUDIT":
                timeline_items.append(
                    {
                        "sequence": sequence,
                        "stage": "AUDIT_SAVED",
                        "timestamp": item["timestamp"],
                        "status": item["decision"],
                        "summary": f"轮次审计已保存，裁决={item['decision']}",
                        "turn_id": item["turn_id"],
                        "audit_id": item["audit_id"],
                    }
                )
                continue
            event = next(
                workflow_event
                for workflow_event in events
                if workflow_event.event_id == item["event_id"]
            )
            event_type = event.event_type.value
            failed = any(
                marker in event_type
                for marker in ("FAILED", "REJECTED", "REVOKED", "EXPIRED", "CANCELLED")
            )
            timeline_items.append(
                {
                    "sequence": sequence,
                    "stage": event_type,
                    "timestamp": item["timestamp"],
                    "status": "FAILED" if failed else "COMPLETED",
                    "summary": str(event.payload.get("reason", event_type)),
                    "turn_id": event.related_turn_id,
                    "event_id": event.event_id,
                }
            )
        return TurnTimeline(
            root_turn_id=root,
            audits=audits,
            workflow_events=events,
            ordered_items=ordered,
            items=timeline_items,
            historical_execution_state=self.workflow_repository.executions(root),
            current_simulator_state=self.vehicle.get_state(),
        )
