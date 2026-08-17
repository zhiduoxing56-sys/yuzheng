from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
import math
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())


def _validate_vehicle_source_fields(data: Any) -> Any:
    if not isinstance(data, dict):
        return data
    numeric_fields = {
        "vehicle_speed",
        "front_obstacle_distance",
        "rear_obstacle_distance",
        "ultrasonic_distance",
        "speed_limit",
    }
    for field_name in numeric_fields:
        if field_name not in data or data[field_name] is None:
            continue
        value = data[field_name]
        valid = (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and (not isinstance(value, float) or math.isfinite(value))
        )
        if not valid:
            raise ValueError(
                f"{field_name} violates FINITE_INT_OR_FLOAT_EXCLUDING_BOOL: "
                f"INVALID_VALUE_TYPE ({type(value).__name__})"
            )
    if "ambient_light" in data and data["ambient_light"] is not None:
        value = data["ambient_light"]
        valid = (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and (not isinstance(value, float) or math.isfinite(value))
        ) or (isinstance(value, str) and value.upper() in {"LOW", "DARK", "NIGHT"})
        if not valid:
            raise ValueError(
                "ambient_light violates FINITE_INT_OR_FLOAT_EXCLUDING_BOOL_OR_"
                f"LOW_DARK_NIGHT: INVALID_VALUE_TYPE ({type(value).__name__})"
            )
    return data


class EvidenceStatus(str, Enum):
    VALID = "VALID"
    SUSPICIOUS = "SUSPICIOUS"
    STALE = "STALE"
    TAMPERED = "TAMPERED"
    MISSING = "MISSING"


class RetrievalOrigin(str, Enum):
    HNSW = "HNSW"
    MANDATORY_RECALL = "MANDATORY_RECALL"
    BOTH = "BOTH"
    NONE = "NONE"


class DecisionLabel(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class DecisionSource(str, Enum):
    SAFETY_GATE = "SAFETY_GATE"
    EVIDENCE_ALIGNMENT = "EVIDENCE_ALIGNMENT"
    SAFETY_SCORE = "SAFETY_SCORE"
    RUNTIME_CAPABILITY = "RUNTIME_CAPABILITY"
    VOICE_TRUST = "VOICE_TRUST"
    ZONE_PERMISSION = "ZONE_PERMISSION"
    USER_REVIEW = "USER_REVIEW"
    LEGACY_COMPATIBILITY = "LEGACY_COMPATIBILITY"


DECISION_SOURCE_DESCRIPTIONS: dict[DecisionSource, str] = {
    DecisionSource.SAFETY_GATE: "硬规则门控",
    DecisionSource.EVIDENCE_ALIGNMENT: "EAS证据路由",
    DecisionSource.SAFETY_SCORE: "五因子原始裁决",
    DecisionSource.RUNTIME_CAPABILITY: "运行能力安全约束",
    DecisionSource.VOICE_TRUST: "语音可信约束",
    DecisionSource.ZONE_PERMISSION: "乘员区域权限约束",
    DecisionSource.USER_REVIEW: "用户复核约束",
    DecisionSource.LEGACY_COMPATIBILITY: "旧记录兼容读取来源",
}
DecisionSource.__doc__ = "公开裁决来源：" + "；".join(
    f"{source.value}={description}"
    for source, description in DECISION_SOURCE_DESCRIPTIONS.items()
)


class SemanticControlMode(str, Enum):
    FULL = "FULL"
    RESTRICTED = "RESTRICTED"
    QUERY_ONLY = "QUERY_ONLY"


class SecurityClass(str, Enum):
    ENTERTAINMENT = "ENTERTAINMENT"
    COCKPIT = "COCKPIT"
    DRIVING = "DRIVING"
    EMERGENCY = "EMERGENCY"
    UNCLASSIFIED = "UNCLASSIFIED"


class LayerNavigationAvailability(str, Enum):
    AVAILABLE = "AVAILABLE"
    DEGRADED_UNAVAILABLE = "DEGRADED_UNAVAILABLE"
    LEGACY_NOT_RECORDED = "LEGACY_NOT_RECORDED"


class EvidenceRelation(str, Enum):
    TEMPORAL = "TEMPORAL"
    SPATIAL = "SPATIAL"
    FUNCTIONAL = "FUNCTIONAL"
    SUPPORTS = "SUPPORTS"
    CONFLICTS = "CONFLICTS"
    REQUIRES = "REQUIRES"
    DERIVED_FROM = "DERIVED_FROM"
    PERMISSION_BOUND = "PERMISSION_BOUND"
    RULE_CONSTRAINED = "RULE_CONSTRAINED"
    HORIZONTAL_MEMORY = "HORIZONTAL_MEMORY"
    VERTICAL_PROPAGATION = "VERTICAL_PROPAGATION"


class MemoryRelationType(str, Enum):
    SPATIAL_COOCCURRENCE = "SPATIAL_COOCCURRENCE"
    TEMPORAL_SYNCHRONIZATION = "TEMPORAL_SYNCHRONIZATION"
    SEMANTIC_COMPLEMENT = "SEMANTIC_COMPLEMENT"
    SENSOR_TOPOLOGY = "SENSOR_TOPOLOGY"


class AuditRecordQuality(str, Enum):
    VALID = "VALID"
    KNOWN_BUG = "KNOWN_BUG"
    ENCODING_ERROR = "ENCODING_ERROR"
    SUPERSEDED = "SUPERSEDED"
    TEST_ONLY = "TEST_ONLY"
    LEGACY_MODEL = "LEGACY_MODEL"


class AuditDatabaseRole(str, Enum):
    PRODUCTION = "PRODUCTION"
    TEST = "TEST"


class AuditRecordType(str, Enum):
    COMMAND = "COMMAND"
    REVIEW_OUTCOME = "REVIEW_OUTCOME"


class ReviewAction(str, Enum):
    CONFIRM = "CONFIRM"
    CORRECT = "CORRECT"
    CANCEL = "CANCEL"


class InteractionState(str, Enum):
    """The only backend-authoritative state for a turn's user interaction."""

    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    PASS = "PASS"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCK = "BLOCK"


class InteractionType(str, Enum):
    """The sole user-facing interaction taxonomy.

    ``None`` means the turn is terminal and deliberately has no modal.
    Decision labels and semantic reason codes are internal inputs to the
    interaction generator; clients must never infer this value themselves.
    """

    MULTI_INTENT_SELECTION = "MULTI_INTENT_SELECTION"
    PARAMETER_COMPLETION = "PARAMETER_COMPLETION"
    SEMANTIC_DISAMBIGUATION = "SEMANTIC_DISAMBIGUATION"
    UNRESOLVED_VEHICLE_CONTROL = "UNRESOLVED_VEHICLE_CONTROL"
    SAFETY_REVIEW = "SAFETY_REVIEW"
    EXECUTION_CONFIRMATION = "EXECUTION_CONFIRMATION"


class InteractionAction(str, Enum):
    SELECT_CANDIDATE = "SELECT_CANDIDATE"
    REPHRASE = "REPHRASE"
    CANCEL = "CANCEL"
    CONFIRM = "CONFIRM"
    CLOSE = "CLOSE"
    EXECUTE = "EXECUTE"
    SUBMIT_PARAMETERS = "SUBMIT_PARAMETERS"


class AuthorizationTokenStatus(str, Enum):
    ISSUED = "ISSUED"
    CONSUMED = "CONSUMED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    REJECTED = "REJECTED"


class WorkflowEventType(str, Enum):
    VOICE_INPUT_RECEIVED = "VOICE_INPUT_RECEIVED"
    SPECTRUM_ANALYZED = "SPECTRUM_ANALYZED"
    LA_CHECKED = "LA_CHECKED"
    PA_CHECKED = "PA_CHECKED"
    VOICE_TRUST_DECIDED = "VOICE_TRUST_DECIDED"
    ASR_COMPLETED = "ASR_COMPLETED"
    ZONE_PERMISSION_CHECKED = "ZONE_PERMISSION_CHECKED"
    RUNTIME_CAPABILITY_CHECKED = "RUNTIME_CAPABILITY_CHECKED"
    REVIEW_REQUESTED = "REVIEW_REQUESTED"
    REVIEW_CONFIRM_REJECTED = "REVIEW_CONFIRM_REJECTED"
    REVIEW_CONFIRMED = "REVIEW_CONFIRMED"
    REVIEW_CORRECTED = "REVIEW_CORRECTED"
    REVIEW_CANCELLED = "REVIEW_CANCELLED"
    INTERACTION_CONFIRMED = "INTERACTION_CONFIRMED"
    CLARIFICATION_REQUESTED = "CLARIFICATION_REQUESTED"
    CLARIFICATION_RESOLVED = "CLARIFICATION_RESOLVED"
    FINAL_DECISION_UPDATED = "FINAL_DECISION_UPDATED"
    AUDIT_OUTCOME_APPENDED = "AUDIT_OUTCOME_APPENDED"
    REDECISION_STARTED = "REDECISION_STARTED"
    REDECISION_COMPLETED = "REDECISION_COMPLETED"
    TOKEN_ISSUED = "TOKEN_ISSUED"
    TOKEN_REJECTED = "TOKEN_REJECTED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_CONSUMED = "TOKEN_CONSUMED"
    TOKEN_REVOKED = "TOKEN_REVOKED"
    KEY_INVALIDATED = "KEY_INVALIDATED"
    EXECUTION_REQUESTED = "EXECUTION_REQUESTED"
    PRE_EXECUTION_CHECK_PASSED = "PRE_EXECUTION_CHECK_PASSED"
    PRE_EXECUTION_CHECK_FAILED = "PRE_EXECUTION_CHECK_FAILED"
    EXECUTION_SUCCEEDED = "EXECUTION_SUCCEEDED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    DECISION_SNAPSHOT_CAPTURED = "DECISION_SNAPSHOT_CAPTURED"
    LLM_EXPLANATION_GENERATED = "LLM_EXPLANATION_GENERATED"


class VoiceTrustResult(StrictModel):
    turn_id: str
    audio_source: str
    speaker_zone: str
    speaker_role: str
    la_score: float = Field(ge=0, le=1)
    pa_raw_score: float | None = Field(
        default=None,
        description="官方 PA 模型原始、未校准的 bonafide 方向标量",
    )
    pa_score: float = Field(
        ge=0,
        le=1,
        description="sigmoid 映射后的 0～1 归一化真人可信分数，不是校准概率",
    )
    replay_risk: float = Field(
        ge=0,
        le=1,
        description="由归一化 PA 分数生成的工程风险值：1 - pa_score",
    )
    synthetic_risk: float = Field(ge=0, le=1)
    zone_risk: float = Field(ge=0, le=1)
    trust_score: float = Field(ge=0, le=1)
    input_trust_label: str
    audio_fingerprint: str
    spectrum_anomaly_score: float | None = Field(default=None, ge=0, le=1)
    model_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="before")
    @classmethod
    def discard_legacy_research_fields(cls, data: Any) -> Any:
        """Read older audit rows without re-emitting removed research fields."""
        if isinstance(data, dict):
            data = dict(data)
            for field in (
                "la_model_score",
                "pa_model_score",
                "la_model_status",
                "pa_model_status",
                "spectrum_score_applied",
                "score_weights",
                "score_thresholds",
            ):
                data.pop(field, None)
        return data


class TranscriptionResult(StrictModel):
    turn_id: str
    text: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    adapter: str
    model_inference_performed: bool
    transcribed_text: str = ""
    asr_confidence: float | None = Field(default=None, ge=0, le=1)
    asr_confidence_method: str | None = None
    mean_token_logprob: float | None = None
    confidence_token_count: int = Field(default=0, ge=0)
    model_name: str = ""
    inference_duration: float = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="before")
    @classmethod
    def fill_report_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("transcribed_text", data.get("text", ""))
            data.setdefault("text", data.get("transcribed_text", ""))
            data.setdefault("asr_confidence", data.get("confidence"))
            data.setdefault("confidence", data.get("asr_confidence"))
            data.setdefault("model_name", data.get("adapter", ""))
            data.setdefault("adapter", data.get("model_name", ""))
        return data

    @model_validator(mode="after")
    def validate_report_aliases(self) -> "TranscriptionResult":
        if self.text != self.transcribed_text:
            raise ValueError("text 与 transcribed_text 必须一致")
        if self.confidence != self.asr_confidence:
            raise ValueError("confidence 与 asr_confidence 必须一致")
        return self


class SpectrumAnalysisResult(StrictModel):
    sample_rate: int = Field(gt=0)
    duration_seconds: float = Field(ge=0)
    rms_energy: float = Field(ge=0)
    low_band_energy_ratio: float = Field(ge=0, le=1)
    speech_band_energy_ratio: float = Field(ge=0, le=1)
    high_band_energy_ratio: float = Field(ge=0, le=1)
    high_frequency_anomaly: float = Field(ge=0, le=1)
    silence_detected: bool
    clipping_ratio: float = Field(ge=0, le=1)
    peak_anomaly: float = Field(ge=0, le=1)
    anomaly_score: float = Field(ge=0, le=1)


class ZonePermissionResult(StrictModel):
    passed: bool
    permission_score: float = Field(ge=0, le=1)
    permission_label: DecisionLabel
    risk_items: list[str] = Field(default_factory=list)
    speaker_zone: str
    zone_source: str
    action: str
    target: str
    target_risk: float = Field(ge=0, le=1)
    calculated_risk: float = Field(ge=0, le=1)


class SemanticIntent(StrictModel):
    clause_index: int = Field(ge=0)
    clause_text: str
    intent_id: str
    runtime_identity: Literal["FORMAL", "KNOWN_NON_EXECUTABLE"] = "FORMAL"
    action: str
    target: str
    area: str = "unknown"
    value: Any | None = None
    mode: str | None = None
    direction: str | None = None
    control_attribute: str = "unknown"
    control_domain: str = "unknown"
    risk_level: str = "R1"
    risk_tags: list[str] = Field(default_factory=list)
    semantic_confidence: float = Field(ge=0, le=1)
    ambiguity_score: float = Field(ge=0, le=1)


class SemanticFrame(StrictModel):
    frame_id: str = Field(default_factory=lambda: make_id("SEM"))
    turn_id: str
    raw_text: str
    normalized_text: str
    semantic_confidence: float = Field(ge=0, le=1)
    ambiguity_score: float = Field(ge=0, le=1)
    semantic_status: str
    review_reasons: list[str] = Field(default_factory=list)
    review_candidates: list[str] = Field(default_factory=list)
    unresolved_clauses: list[str] = Field(default_factory=list)
    security_signals: list[str] = Field(default_factory=list)
    intents: list[SemanticIntent] = Field(default_factory=list)


class RequestDomain(str, Enum):
    VEHICLE_CONTROL = "VEHICLE_CONTROL"
    MEDIA_SERVICE = "MEDIA_SERVICE"
    NAVIGATION_SERVICE = "NAVIGATION_SERVICE"
    COMMUNICATION_SERVICE = "COMMUNICATION_SERVICE"
    CABIN_APP_SERVICE = "CABIN_APP_SERVICE"
    INFORMATION_QUERY = "INFORMATION_QUERY"
    GENERAL_ASSISTANT = "GENERAL_ASSISTANT"
    UNKNOWN = "UNKNOWN"


class ControlRelevance(str, Enum):
    VEHICLE_CONTROL = "VEHICLE_CONTROL"
    NON_CONTROL = "NON_CONTROL"
    UNCERTAIN = "UNCERTAIN"


class SemanticUnitKind(str, Enum):
    CONTEXT = "CONTEXT"
    ASSISTANT = "ASSISTANT"
    UNCERTAIN = "UNCERTAIN"
    VEHICLE_CONTROL = "VEHICLE_CONTROL"


class OrderedSemanticUnit(StrictModel):
    """The 4B normalizer's ordered, text-only production contract."""

    unit_index: int = Field(ge=0)
    kind: SemanticUnitKind
    normalized_text: str = Field(min_length=1)


class RequestRouting(StrictModel):
    raw_text: str
    units: list[OrderedSemanticUnit] = Field(default_factory=list)
    contains_vehicle_control: bool = False
    enters_vehicle_safety_chain: bool = False
    model_call_count: int = Field(default=0, ge=0)
    model_metrics: dict[str, Any] = Field(default_factory=dict)


class ClarificationType(str, Enum):
    VOICE_CONFIRMATION = "VOICE_CONFIRMATION"
    SEMANTIC_CONFIRMATION = "SEMANTIC_CONFIRMATION"


class ClarificationCandidateSource(str, Enum):
    ASR_NBEST = "ASR_NBEST"
    TEXT_SIMILARITY = "TEXT_SIMILARITY"
    SEMANTIC_REVIEW_CANDIDATE = "SEMANTIC_REVIEW_CANDIDATE"
    SLOT_COMPLETION = "SLOT_COMPLETION"


class ClarificationResolution(str, Enum):
    SELECTED = "SELECTED"
    NONE_OF_ABOVE = "NONE_OF_ABOVE"


class InteractionCandidate(StrictModel):
    candidate_id: str
    display_text: str = Field(min_length=1, max_length=2048)
    canonical_text: str = Field(min_length=1, max_length=2048)
    canonical_intent_id: str | None = None
    canonical_slots: dict[str, Any] = Field(default_factory=dict)
    source: str


class UserReason(StrictModel):
    code: str
    title: str
    description: str
    details: list[dict[str, Any]] = Field(default_factory=list)


class InteractionRequest(StrictModel):
    interaction_id: str = Field(default_factory=lambda: make_id("INT"))
    turn_id: str
    unit_index: int | None = Field(default=None, ge=0)
    intent_id: str | None = None
    state: InteractionState
    interaction_type: InteractionType | None = None
    canonical_operation: str | None = None
    reason_codes: list[str] = Field(default_factory=list)
    reason_details: list[dict[str, Any]] = Field(default_factory=list)
    allowed_actions: list[InteractionAction] = Field(default_factory=list)
    candidates: list[InteractionCandidate] = Field(default_factory=list, max_length=16)
    user_reason: UserReason | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    expires_at: datetime | None = None
    consumed: bool = False

    @model_validator(mode="after")
    def validate_interaction_contract(self) -> "InteractionRequest":
        if self.interaction_type is None:
            raise ValueError("persisted interaction requires interaction_type")
        if self.state == InteractionState.NEEDS_REVIEW and self.candidates:
            raise ValueError("NEEDS_REVIEW must not expose semantic candidates")
        if self.state == InteractionState.BLOCK and self.allowed_actions != [InteractionAction.CLOSE]:
            raise ValueError("BLOCK only allows CLOSE")
        if self.state == InteractionState.PASS and self.candidates:
            raise ValueError("PASS must not expose candidates")
        return self


class InteractionSubmission(StrictModel):
    interaction_id: str = Field(min_length=1, max_length=128)
    action: InteractionAction
    candidate_id: str | None = Field(default=None, min_length=1, max_length=128)
    text: str | None = Field(default=None, min_length=1, max_length=2048)
    parameters: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> "InteractionSubmission":
        if self.action == InteractionAction.SELECT_CANDIDATE and not self.candidate_id:
            raise ValueError("SELECT_CANDIDATE requires candidate_id")
        if self.action == InteractionAction.REPHRASE and not (self.text or "").strip():
            raise ValueError("REPHRASE requires text")
        if self.action == InteractionAction.SUBMIT_PARAMETERS and not self.parameters:
            raise ValueError("SUBMIT_PARAMETERS requires parameters")
        if self.action not in {InteractionAction.SELECT_CANDIDATE, InteractionAction.REPHRASE, InteractionAction.SUBMIT_PARAMETERS} and (
            self.candidate_id is not None or self.text is not None
        ):
            raise ValueError("action does not accept candidate_id or text")
        return self


class ClarificationCandidate(StrictModel):
    candidate_id: str
    display_text: str = Field(min_length=1, max_length=2048)
    candidate_source: ClarificationCandidateSource
    source_rank: int = Field(ge=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    # Canonical identity is server-authored metadata.  Clients submit only
    # candidate_id; it is retained so the selected clarification can be
    # compared with the child turn after the full pipeline is re-run.
    canonical_intent_id: str | None = None
    canonical_runtime_identity: Literal["FORMAL", "KNOWN_NON_EXECUTABLE"] | None = None
    canonical_slots: dict[str, Any] = Field(default_factory=dict)
    # 分组复核：同一候选组（对应一个待复核意图）用相同 group 标识，
    # group_label 用于前端分组标题（如「打开车窗」）。None = 非分组候选（单意图）。
    group: str | None = None
    group_label: str | None = None


class ClarificationRequest(StrictModel):
    clarification_id: str
    turn_id: str
    clarification_type: ClarificationType
    prompt: str = Field(min_length=1, max_length=500)
    original_text: str = Field(max_length=2048)
    candidates: list[ClarificationCandidate] = Field(default_factory=list, max_length=16)


class ClarificationResolutionRecord(StrictModel):
    clarification_id: str
    source_turn_id: str
    resolution: ClarificationResolution
    selected_candidate_id: str | None = None
    selected_candidate_text: str | None = None
    child_turn_id: str | None = None
    resolved_at: datetime = Field(default_factory=utc_now)


class IntentEvidenceDemand(StrictModel):
    intent_id: str
    clause_index: int = Field(ge=0)
    action: str
    target: str
    area: str = "unknown"
    value: Any | None = None
    risk_level: str
    query_text: str
    query_vector: list[float] = Field(default_factory=list)
    vectorization_metadata: "VectorizationMetadata | None" = None
    required_types: list[str] = Field(default_factory=list)
    assessment_types: list[str] = Field(default_factory=list)
    knowledge_required_types: list[str] = Field(default_factory=list)
    optional_types: list[str] = Field(default_factory=list)
    knowledge_augmented_types: list[str] = Field(default_factory=list)
    knowledge_augmented_optional_types: list[str] = Field(default_factory=list)
    knowledge_hits: list[dict[str, Any]] = Field(default_factory=list)
    knowledge_query_text: str = ""
    knowledge_retrieval_metadata: dict[str, Any] = Field(default_factory=dict)
    knowledge_demand_sources: list[dict[str, Any]] = Field(default_factory=list)
    priority: int = Field(default=0, ge=0, le=100)
    retrieval_scope: str = "control_evidence"


class EvidenceDemand(StrictModel):
    demand_id: str = Field(default_factory=lambda: make_id("DEM"))
    turn_id: str
    intent_demands: list[IntentEvidenceDemand] = Field(default_factory=list)


class EvidenceNode(StrictModel):
    node_id: str = Field(default_factory=lambda: make_id("EVI"))
    evidence_type: str
    layer: str
    source: str
    value: Any
    unit: str | None = None
    timestamp: datetime | None
    expires_at: datetime | None
    freshness: float = Field(ge=0, le=1)
    consistency: float = Field(ge=0, le=1)
    availability: float = Field(ge=0, le=1)
    quality_label: EvidenceStatus
    integrity_hash: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    security_class: SecurityClass | None = None
    security_rank: int | None = Field(default=None, ge=0, le=3)
    base_level: int | None = Field(default=None, ge=0)
    safety_adjustment: int | None = Field(default=None, ge=0)
    hnsw_max_layer: int | None = Field(default=None, ge=0)
    hnsw_layer_memberships: list[int] = Field(default_factory=list)
    security_classification_source: str | None = None
    formula_source: str | None = None
    canonicalization_source: str | None = None
    merged_node_sources: list[str] = Field(default_factory=list)
    field_resolution: dict[str, str] = Field(default_factory=dict)
    canonicalization_warnings: list[str] = Field(default_factory=list)

    @field_validator("evidence_type")
    @classmethod
    def canonical_evidence_type_only(cls, value: str) -> str:
        from app.services.evidence.catalog import require_canonical_evidence_type

        return require_canonical_evidence_type(value)


class EvidenceEdge(StrictModel):
    edge_id: str = Field(default_factory=lambda: make_id("EDGE"))
    source: str
    target: str
    relation: EvidenceRelation
    weight: float = Field(ge=0, le=1)
    reason: str


class VectorizationMetadata(StrictModel):
    implementation: str
    model_name: str
    dimension: int = Field(gt=0)
    normalized: bool
    real_model_inference: bool
    vector_digest: str
    degradation_reason: str | None = None
    cache_hit: bool = False
    cache_hits: int = Field(default=0, ge=0)
    cache_misses: int = Field(default=0, ge=0)


class RuntimeCapabilityStatus(StrictModel):
    embedding_implementation: str
    embedding_model: str
    embedding_dimension: int = Field(gt=0)
    real_model_inference: bool
    embedding_degraded: bool
    index_implementation: str
    index_degraded: bool
    semantic_control_mode: SemanticControlMode
    degradation_reasons: list[str] = Field(default_factory=list)
    checked_at: datetime = Field(default_factory=utc_now)


class SecurityClassInfo(StrictModel):
    name: SecurityClass
    rank: int | None = Field(default=None, ge=0, le=3)
    report_label: str
    node_layer_label: str
    mapping_source: str


class LayerIndexStatus(StrictModel):
    layer: int = Field(ge=0)
    security_classes: list[SecurityClass] = Field(default_factory=list)
    index_instance_id: str
    node_count: int = Field(ge=0)
    implementation: str
    degraded: bool
    empty: bool
    build_id: str


class LayerPoint(StrictModel):
    """HNSW 分层索引中某一层的单个点（证据节点），对外暴露层内全部节点。"""

    layer: int = Field(ge=0)
    label: int = Field(ge=0)               # 该层 hnswlib 索引内的 label
    internal_key: str                       # 索引内部稳定 key（evidence_key 复合）
    node_id: str                            # 证据节点 id
    evidence_type: str
    display_name: str
    security_class: SecurityClass | None = None
    security_rank: int | None = Field(default=None, ge=0, le=3)
    hnsw_max_layer: int | None = Field(default=None, ge=0)
    evidence_key: str                       # stable physical identity（evidence_key(node)）


class LayerCandidate(StrictModel):
    node_id: str
    evidence_type: str
    display_name: str
    distance: float = Field(ge=0)
    sas: float = Field(ge=0, le=1)
    rank_in_layer: int = Field(ge=1)
    security_class: SecurityClass
    hnsw_max_layer: int = Field(ge=0)
    retrieval_origin: Literal["HNSW"] = "HNSW"


class LayerSearchStep(StrictModel):
    sequence: int = Field(ge=1)
    layer: int = Field(ge=0)
    layer_name: str
    index_instance_id: str
    node_count: int = Field(ge=0)
    requested_k: int = Field(ge=0)
    returned_count: int = Field(ge=0)
    candidates: list[LayerCandidate] = Field(default_factory=list)
    selected_anchor_node_id: str | None = None
    previous_anchor_node_id: str | None = None
    elapsed_ms: float = Field(ge=0)
    search_mode: Literal["REAL_HNSWLIB_LAYER_QUERY"] = "REAL_HNSWLIB_LAYER_QUERY"


class SecurityLayerNavigation(StrictModel):
    availability: LayerNavigationAvailability
    trace_kind: Literal["SECURITY_LAYER_INDEX_TRACE"] = "SECURITY_LAYER_INDEX_TRACE"
    trace_source: Literal["REAL_HNSWLIB_LAYER_QUERIES"] = (
        "REAL_HNSWLIB_LAYER_QUERIES"
    )
    is_internal_hnsw_trace: Literal[False] = False
    internal_trace_available: Literal[False] = False
    internal_trace_reason: Literal["UNSUPPORTED_BY_PUBLIC_HNSWLIB_API"] = (
        "UNSUPPORTED_BY_PUBLIC_HNSWLIB_API"
    )
    internal_hnsw_entry_point: None = None
    internal_hnsw_node_levels: None = None
    internal_hnsw_visited_nodes: None = None
    internal_hnsw_navigation_path: None = None
    build_id: str
    highest_nonempty_layer: int | None = Field(default=None, ge=0)
    entry_anchor_node_id: str | None = None
    steps: list[LayerSearchStep] = Field(default_factory=list)
    anchor_path: list[str] = Field(default_factory=list)
    final_top_k_node_ids: list[str] = Field(default_factory=list)
    mandatory_supplemented_node_ids: list[str] = Field(default_factory=list)
    total_elapsed_ms: float = Field(ge=0)


class OccurrenceLayerNavigation(StrictModel):
    """The real HNSW layer queries made for one semantic intent occurrence."""

    clause_index: int = Field(ge=0)
    intent_id: str
    navigation: SecurityLayerNavigation


class RetrievalVisualizationPath(StrictModel):
    sequence: int = Field(ge=1)
    from_node_id: str
    to_node_id: str
    from_layer: int = Field(ge=0)
    to_layer: int = Field(ge=0)
    edge_type: Literal[
        "SECURITY_LAYER_DESCENT", "BASE_TOP_K_SELECTION", "MANDATORY_SUPPLEMENT"
    ]
    reason: str
    source: str


class RetrievalMetadata(StrictModel):
    implementation: str
    index_node_count: int = Field(ge=0)
    vector_dimension: int = Field(gt=0)
    M: int = Field(gt=0)
    ef_construction: int = Field(gt=0)
    ef_search: int = Field(gt=0)
    top_k: int = Field(gt=0)
    candidate_count: int = Field(ge=0)
    canonical_node_count: int = Field(default=0, ge=0)
    ephemeral_node_count: int = Field(default=0, ge=0)
    index_update_count: int = Field(default=0, ge=0)
    index_rebuild_count: int = Field(default=0, ge=0)
    deduplicated_count: int = Field(default=0, ge=0)
    duration_ms: float = Field(ge=0)
    empty_index: bool
    degraded: bool
    degradation_reason: str | None = None
    excluded_types: list[str] = Field(default_factory=list)
    last_built_at: datetime | None = None
    index_build_id: str | None = None
    index_config_digest: str | None = None
    node_set_digest: str | None = None
    stable_identity_version: str | None = None
    stable_identity_source: str | None = None
    content_identity_version: str | None = None
    content_identity_source: str | None = None
    index_fingerprint_version: str | None = None
    node_set_digest_version: str | None = None
    build_id_payload_version: str | None = None
    classification_mapping_digest: str | None = None
    formula_version: str | None = None
    formula_source: str | None = None
    L: int | None = Field(default=None, ge=0)
    L_source: str | None = None
    security_mapping_version: str | None = None
    security_rank_mapping_source: str | None = None
    index_seed_digest: str | None = None
    index_seed_source: str | None = None
    random_level_distribution: str | None = None
    random_level_source: str | None = None
    implementation_source: str | None = None
    layering_mode: str | None = None
    security_layer_count: int = Field(default=0, ge=0)
    security_layers: list[LayerIndexStatus] = Field(default_factory=list)
    per_layer_node_count: dict[int, int] = Field(default_factory=dict)
    mapping_coverage: float | None = Field(default=None, ge=0, le=1)
    unclassified_types: list[str] = Field(default_factory=list)
    security_layer_navigation: SecurityLayerNavigation | None = None
    occurrence_layer_navigations: list[OccurrenceLayerNavigation] = Field(
        default_factory=list
    )
    retrieval_visualization_path: list[RetrievalVisualizationPath] = Field(
        default_factory=list
    )
    final_top_k_node_ids: list[str] = Field(default_factory=list)
    mandatory_supplemented_node_ids: list[str] = Field(default_factory=list)
    internal_hnsw_trace_available: bool = False
    internal_hnsw_trace_reason: str | None = None
    navigation_availability: LayerNavigationAvailability = (
        LayerNavigationAvailability.LEGACY_NOT_RECORDED
    )


class MandatoryRecallRecord(StrictModel):
    clause_index: int = Field(ge=0)
    intent_id: str
    evidence_type: str
    status: str
    candidate_node_ids: list[str] = Field(default_factory=list)
    recalled_node_id: str | None = None
    source: str | None = None
    retrieval_origin: RetrievalOrigin = RetrievalOrigin.NONE
    reason: str


class IntentEvidenceBinding(StrictModel):
    clause_index: int = Field(ge=0)
    intent_id: str
    evidence_type: str
    requirement_level: Literal["REQUIRED", "KNOWLEDGE_REQUIRED", "ASSESSMENT", "OPTIONAL"]
    node_id: str | None = None
    resolution_status: Literal[
        "RETRIEVED",
        "MANDATORY_RECALLED",
        "MISSING",
        "KNOWLEDGE_MISSING",
        "OPTIONAL_NOT_FOUND",
    ]
    retrieval_origin: RetrievalOrigin
    semantic_similarity: float | None = Field(default=None, ge=0, le=1)


class IntentEvidenceResolution(StrictModel):
    clause_index: int = Field(ge=0)
    intent_id: str
    candidate_node_ids: list[str] = Field(default_factory=list)
    bindings: list[IntentEvidenceBinding] = Field(default_factory=list)
    mandatory_recall_records: list[MandatoryRecallRecord] = Field(default_factory=list)
    missing_required_types: list[str] = Field(default_factory=list)
    missing_knowledge_required_types: list[str] = Field(default_factory=list)


class EvidenceQualityMetrics(StrictModel):
    ecr: float | None = Field(default=None, ge=0, le=1)
    evidence_coverage_applicable: bool
    ecs: float = Field(ge=0, le=1)
    ef: float = Field(ge=0, le=1)
    sas: float = Field(ge=0, le=1)
    eas: float = Field(ge=0, le=1)
    conflict_count: int = Field(default=0, ge=0)
    evidence_pair_count: int | None = Field(default=None, ge=0)
    conflict_pair_count: int | None = Field(default=None, ge=0)
    eas_weight_profile: str | None = None
    eas_weight_source: str | None = None
    eas_weights: dict[str, float] | None = None
    evidence_alignment_route: Literal[
        "EVIDENCE_PASS", "EVIDENCE_REVIEW", "EVIDENCE_BLOCK"
    ] | None = None
    short_term_availability: dict[str, float | None] = Field(default_factory=dict)
    long_term_availability: dict[str, float | None] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_coverage_semantics(self) -> "EvidenceQualityMetrics":
        if self.evidence_coverage_applicable != (self.ecr is not None):
            raise ValueError("ECR 与 evidence_coverage_applicable 语义不一致")
        return self


class EvidenceSubgraph(StrictModel):
    graph_id: str = Field(default_factory=lambda: make_id("GRAPH"))
    turn_id: str
    nodes: list[EvidenceNode] = Field(default_factory=list)
    edges: list[EvidenceEdge] = Field(default_factory=list)
    intent_evidence_resolutions: list[IntentEvidenceResolution] = Field(
        default_factory=list
    )
    retrieved_types: list[str] = Field(default_factory=list)
    quality_metrics: EvidenceQualityMetrics | None = None
    retrieval_metadata: RetrievalMetadata | None = None
    corrected_weights: dict[str, float] = Field(default_factory=dict)
    decision_confidence: float | None = Field(default=None, ge=0, le=1)
    advanced_reasoning_applied: bool = False
    advanced_reasoning_status: str = "NOT_APPLICABLE_STAGE2"


class ContextClaim(StrictModel):
    claim_type: str
    claimed_value: Any
    matched_text: list[str] = Field(default_factory=list)
    source_text: str


class GroundingFailure(StrictModel):
    claim: str
    expected_evidence: list[str] = Field(default_factory=list)
    observed_evidence: dict[str, Any] = Field(default_factory=dict)
    severity: int = Field(ge=1, le=3)
    explanation: str
    supporting_node_ids: list[str] = Field(default_factory=list)


class JailbreakConflict(StrictModel):
    conflict_id: str = Field(default_factory=lambda: make_id("CONFLICT"))
    claim_type: str
    claimed_value: Any
    observed_value: Any
    evidence_node_ids: list[str] = Field(default_factory=list)
    severity: int = Field(ge=1, le=3)
    reason: str
    rule_id: str
    recommended_action: str


class AdvancedValidationResult(StrictModel):
    context_claims: list[ContextClaim] = Field(default_factory=list)
    conflicts: list[JailbreakConflict] = Field(default_factory=list)
    grounding_failures: list[GroundingFailure] = Field(default_factory=list)
    jailbreak_flag: bool = False
    jailbreak_risk: float = Field(default=0, ge=0, le=1)
    jailbreak_risk_base: float | None = Field(default=None, ge=0, le=1)
    jailbreak_risk_severity_component: float | None = Field(default=None, ge=0, le=1)
    conflict_count: int = Field(default=0, ge=0)
    max_severity: int = Field(default=0, ge=0, le=3)
    severity_distribution: dict[str, int] = Field(default_factory=dict)
    duration_ms: float = Field(default=0, ge=0)


class MemoryLink(StrictModel):
    link_id: str = Field(default_factory=lambda: make_id("MEM"))
    source: str
    target: str
    relation: EvidenceRelation
    weight: float = Field(ge=0, le=1)
    layer: str
    reason: str
    conflict: bool = False
    support_adjustment: float = 0.0
    risk_adjustment: float = 0.0
    final_adjustment: float = 0.0


class MemoryRelationEdge(StrictModel):
    edge_id: str
    source_node_id: str
    target_node_id: str
    relation_types: list[MemoryRelationType] = Field(default_factory=list)
    direction: Literal["UNDIRECTED", "DIRECTED"] = "UNDIRECTED"
    criteria: dict[str, Any] = Field(default_factory=dict)
    criteria_sources: dict[str, str] = Field(default_factory=dict)
    score_components: dict[str, float] = Field(default_factory=dict)
    created_by: Literal["ALGORITHM_2"] = "ALGORITHM_2"
    configuration_version: str


class MemoryNodeLayer(StrictModel):
    node_id: str
    stable_physical_identity: str
    security_class: SecurityClass
    security_rank: int | None = Field(default=None, ge=0, le=3)
    memory_layer: int | None = Field(default=None, ge=0, le=3)
    mapping_source: str
    retrieval_origin: Literal["HNSW", "MANDATORY_RECALL", "BOTH", "NONE"]
    propagation_eligible: bool = True

    @model_validator(mode="after")
    def validate_layer_mapping(self) -> "MemoryNodeLayer":
        if self.security_class != SecurityClass.UNCLASSIFIED:
            if self.security_rank is None or self.memory_layer != self.security_rank:
                raise ValueError("memory_layer 必须等于唯一 security_rank")
        elif self.security_rank is not None or self.memory_layer is not None:
            raise ValueError("UNCLASSIFIED 不能伪装成已分类 memory layer")
        return self


class MemoryDegreeStatistics(StrictModel):
    node_count: int = Field(default=0, ge=0)
    candidate_edge_count: int = Field(default=0, ge=0)
    retained_edge_count: int = Field(default=0, ge=0)
    average_degree: float = Field(default=0, ge=0)
    max_degree: int = Field(default=0, ge=0)
    pruned_edge_count: int = Field(default=0, ge=0)
    degree_limit: int = Field(default=16, ge=1)


class MemoryPropagationStep(StrictModel):
    sequence: int = Field(ge=1)
    parent_node_id: str
    child_node_id: str
    parent_layer: int = Field(ge=1, le=3)
    child_layer: int = Field(ge=0, le=2)
    alpha: float = Field(gt=0, lt=1)
    parent_confidence_at_step: float = Field(ge=0)
    contribution: float = Field(ge=0)
    child_confidence_before: float = Field(ge=0)
    child_confidence_after: float = Field(ge=0)
    relation_edge_ids: list[str] = Field(default_factory=list)


class MemoryPropagationResult(StrictModel):
    layered_memory_graph: dict[str, Any] = Field(default_factory=dict)
    relation_edges: list[MemoryRelationEdge] = Field(default_factory=list)
    degree_statistics: MemoryDegreeStatistics = Field(default_factory=MemoryDegreeStatistics)
    node_layers: list[MemoryNodeLayer] = Field(default_factory=list)
    initial_confidences: dict[str, float | None] = Field(default_factory=dict)
    final_confidences: dict[str, float | None] = Field(default_factory=dict)
    propagation_steps: list[MemoryPropagationStep] = Field(default_factory=list)
    incoming_contributions: dict[str, list[int]] = Field(default_factory=dict)
    alpha: float | None = Field(default=None, gt=0, lt=1)
    alpha_source: str | None = None
    configuration_version: str | None = None
    warnings: list[str] = Field(default_factory=list)
    candidate_node_ids: list[str] = Field(default_factory=list)
    retrieval_origins: dict[str, str] = Field(default_factory=dict)
    horizontal_links: list[MemoryLink] = Field(default_factory=list)
    horizontal_support: float = Field(default=0, ge=0, le=1)
    horizontal_conflicts: int = Field(default=0, ge=0)
    horizontal_adjustments: dict[str, float] = Field(default_factory=dict)
    vertical_links: list[MemoryLink] = Field(default_factory=list)
    propagation_paths: list[dict[str, Any]] = Field(default_factory=list)
    pre_weights: dict[str, float] = Field(default_factory=dict)
    post_weights: dict[str, float] = Field(default_factory=dict)
    horizontal_duration_ms: float = Field(default=0, ge=0)
    vertical_duration_ms: float = Field(default=0, ge=0)
    duration_ms: float = Field(default=0, ge=0)


class CausalEdge(StrictModel):
    source: str
    target: str
    relation: str
    support: float = Field(default=0, ge=0, le=1)
    sample_count: int = Field(default=0, ge=0)
    reason: str
    parent_variable: str | None = None
    child_variable: str | None = None
    support_count: int = Field(default=0, ge=0)
    p_child_given_parent: float | None = Field(default=None, ge=0, le=1)
    p_child_given_not_parent: float | None = Field(default=None, ge=0, le=1)
    dependency_delta: float | None = Field(default=None, ge=0, le=1)
    temporal_order_valid: bool | None = None
    domain_rule_source: str | None = None
    threshold: float | None = Field(default=None, ge=0, le=1)
    accepted: bool | None = None
    prune_reason: str | None = None


class CausalPriorComponents(StrictModel):
    node_id: str
    causal_variable: str
    clause_index: int | None = Field(default=None, ge=0)
    intent_id: str | None = None
    binding_similarity: float | None = Field(default=None, ge=0, le=1)
    requirement_level: Literal[
        "REQUIRED", "KNOWLEDGE_REQUIRED", "ASSESSMENT", "OPTIONAL"
    ] | None = None
    memory_initial_confidence: float | None = Field(default=None, ge=0)
    sas_component: float | None = Field(default=None, ge=0, le=1)
    layer_confidence_component: float | None = Field(default=None, ge=0)
    freshness_component: float | None = Field(default=None, ge=0, le=1)
    availability_component: float | None = Field(default=None, ge=0, le=1)
    mandatory_component: float = Field(default=0, ge=0, le=1)
    lambda_values: dict[str, float] = Field(default_factory=dict)
    raw_prior_score: float | None = None
    availability_source: str | None = None
    availability_status: str = "AVAILABLE"


class ParentStateStatistics(StrictModel):
    node_id: str
    causal_variable: str
    parent_variables: list[str] = Field(default_factory=list)
    parent_state_signature: str
    class_count_with_node_and_parents: int = Field(default=0, ge=0)
    node_parent_count: int = Field(default=0, ge=0)
    class_cardinality: int = Field(default=0, ge=0)
    smoothing_epsilon: float = Field(gt=0)
    rho: float | None = Field(default=None, ge=0, le=1)


class CausalNodeWeight(StrictModel):
    node_id: str
    causal_variable: str
    clause_index: int | None = Field(default=None, ge=0)
    intent_id: str | None = None
    prior_probability: float | None = Field(default=None, ge=0, le=1)
    causal_support: float | None = Field(default=None, ge=0, le=1)
    unnormalized_weight: float | None = Field(default=None, ge=0)
    corrected_weight: float | None = Field(default=None, ge=0, le=1)


class CausalModelSnapshot(StrictModel):
    model_build_id: str
    built_at: datetime | None = None
    formula_version: str
    causal_variable_version: str
    history_sample_count: int = Field(default=0, ge=0)
    history_start_time: datetime | None = None
    history_end_time: datetime | None = None
    history_digest: str
    command_class_vocabulary_digest: str
    candidate_edge_count: int = Field(default=0, ge=0)
    causal_edge_count: int = Field(default=0, ge=0)
    dag_digest: str
    parameter_digest: str
    minimum_history_samples: int = Field(default=20, ge=1)
    confidence_status: str
    topological_order: list[str] = Field(default_factory=list)
    variable_identity_level: str = "NORMALIZED_EVIDENCE_TYPE"
    variable_identity_source: str = "ENGINEERING_REALIZATION"


class CausalCorrectionResult(StrictModel):
    mode: str = "HISTORICAL_LEGACY"
    corrected_weights_projection: str = "LEGACY_AUTHORITATIVE"
    model_snapshot: CausalModelSnapshot | None = None
    parent_state_statistics: list[ParentStateStatistics] = Field(default_factory=list)
    prior_components: list[CausalPriorComponents] = Field(default_factory=list)
    prior_probabilities: dict[str, float] = Field(default_factory=dict)
    rho_values: dict[str, float] = Field(default_factory=dict)
    node_weights: list[CausalNodeWeight] = Field(default_factory=list)
    insufficiency_reason: str | None = None
    formula_version: str | None = None
    variable_identity_version: str | None = None
    causal_graph: dict[str, Any] = Field(default_factory=dict)
    candidate_edges: list[CausalEdge] = Field(default_factory=list)
    pruned_edges: list[CausalEdge] = Field(default_factory=list)
    removed_edges: list[CausalEdge] = Field(default_factory=list)
    semantic_prior: dict[str, float] = Field(default_factory=dict)
    historical_support: dict[str, float] = Field(default_factory=dict)
    posterior_weights: dict[str, float] = Field(default_factory=dict)
    corrected_weights: dict[str, float] = Field(default_factory=dict)
    posterior_concentration: float = Field(default=0, ge=0, le=1)
    decision_confidence: float | None = Field(default=None, ge=0, le=1)
    confidence_status: Literal[
        "AVAILABLE",
        "INSUFFICIENT_DATA",
        "INSUFFICIENT_HISTORY",
        "INSUFFICIENT_AVAILABILITY",
        "INSUFFICIENT",
        "SINGLE_NODE_UNDEFINED",
        "MODEL_NOT_READY",
    ] = "MODEL_NOT_READY"
    sample_count: int = Field(default=0, ge=0)
    minimum_sample_count: int = Field(default=20, ge=1)
    data_sufficiency: str = "insufficient"
    entropy: float = Field(default=0, ge=0)
    normalized_entropy: float = Field(default=0, ge=0, le=1)
    model_version: str = "causal-unbuilt"
    model_built_at: datetime | None = None
    source_audit_count: int = Field(default=0, ge=0)
    learning_record_ids: list[str] = Field(default_factory=list)
    excluded_record_count: int = Field(default=0, ge=0)
    advanced_reasoning_applied: bool = True
    feature_cutoff: Literal["pre_decision"] = "pre_decision"
    used_features: list[str] = Field(default_factory=list)
    duration_ms: float = Field(default=0, ge=0)


class EvidenceCitation(StrictModel):
    node_id: str
    reason: str


class DecisionExplanation(StrictModel):
    summary: str
    decision_label: DecisionLabel
    decision_basis: list[str] = Field(default_factory=list)
    hard_gate_reasons: list[str] = Field(default_factory=list)
    evidence_alignment_summary: str
    score_summary: str
    causal_summary: str
    missing_or_conflicting_evidence: list[str] = Field(default_factory=list)
    safe_next_step: str
    evidence_citations: list[EvidenceCitation] = Field(default_factory=list)
    reason_code_citations: list[str] = Field(default_factory=list)
    generation_mode: Literal["DETERMINISTIC_FALLBACK", "LLM_INTERPRETER"]
    provider: str | None = None
    model: str | None = None
    prompt_template_version: str
    input_digest: str
    validation_status: str
    fallback_reason: str | None = None


class ReviewCandidateInterpretation(StrictModel):
    candidate_id: str
    turn_id: str
    canonical_text: str
    action: str
    target: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    control_domain: str
    risk_level: str
    why_possible: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    conflicting_evidence_ids: list[str] = Field(default_factory=list)
    source: str
    validation_status: Literal["VALID", "INVALID"]


class RecoveryRecommendation(StrictModel):
    recovery_code: Literal[
        "SUPPLY_ACTION_TARGET",
        "CLARIFY_AREA_OR_DIRECTION",
        "REPHRASE_COMMAND",
        "WAIT_FOR_SENSOR_RECOVERY",
        "SWITCH_TO_SAFE_QUERY",
        "CANCEL_OPERATION",
    ]
    message: str
    required_user_input: str | None = None
    affected_evidence_types: list[str] = Field(default_factory=list)
    source: str
    generation_mode: Literal["DETERMINISTIC_FALLBACK", "LLM_INTERPRETER"]


class InterpreterGenerationMetadata(StrictModel):
    generation_mode: Literal["DETERMINISTIC_FALLBACK", "LLM_INTERPRETER"]
    provider_status: str
    provider: str | None = None
    model: str | None = None
    prompt_template_version: str
    input_digest: str
    input_truncated: bool = False
    output_truncated: bool = False
    fallback_reason: str | None = None
    validation_status: str
    duration_ms: float = Field(default=0, ge=0)


class InterpreterResult(StrictModel):
    decision_explanation: DecisionExplanation
    candidate_interpretations: list[ReviewCandidateInterpretation] = Field(default_factory=list)
    candidate_availability: Literal["AVAILABLE", "NO_VALID_CANDIDATES"]
    review_question: str | None = None
    recommended_recovery: RecoveryRecommendation | None = None
    generation_metadata: InterpreterGenerationMetadata
    validation_result: dict[str, Any] = Field(default_factory=dict)


class ScoreFactor(StrictModel):
    name: str
    value: float | None = Field(default=None, ge=0, le=1)
    applicable: bool
    configured_weight: float = Field(ge=0, le=1)
    actual_weight: float = Field(ge=0, le=1)
    contribution: float = Field(ge=0, le=1)
    reason: str


class AuditQualityMetadata(StrictModel):
    audit_id: str
    record_quality: AuditRecordQuality
    eligible_for_learning: bool
    exclusion_reasons: list[str] = Field(default_factory=list)
    implementation_stage: str
    pipeline_version: str
    schema_version: str
    superseded_by: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class TurnTiming(StrictModel):
    turn_started_at: datetime
    state_snapshot_at: datetime
    decision_reference_time: datetime
    completed_at: datetime | None = None
    end_to_end_ms: float = Field(default=0, ge=0)


class AdvancedReasoningResult(StrictModel):
    memory_propagation: MemoryPropagationResult = Field(default_factory=MemoryPropagationResult)
    causal_correction: CausalCorrectionResult = Field(default_factory=CausalCorrectionResult)
    validation: AdvancedValidationResult = Field(default_factory=AdvancedValidationResult)
    five_factor_score: dict[str, ScoreFactor] = Field(default_factory=dict)
    decision_confidence: float | None = Field(default=None, ge=0, le=1)
    explanations: list[str] = Field(default_factory=list)
    recognized_command: dict[str, Any] = Field(default_factory=dict)
    mandatory_evidence_complete: bool = False
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    conflicting_evidence_ids: list[str] = Field(default_factory=list)
    hit_rules: list[str] = Field(default_factory=list)
    review_question: str | None = None
    performance_ms: dict[str, float] = Field(default_factory=dict)
    advanced_reasoning_applied: bool = True


class ValidationResult(StrictModel):
    validated_nodes: list[EvidenceNode] = Field(default_factory=list)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    jailbreak_flag: bool = False
    jailbreak_risk: float = Field(default=0, ge=0, le=1)
    evidence_trust_required: float = Field(default=0, ge=0, le=1)
    grounding_failures: list[str] = Field(default_factory=list)


class GateCheck(StrictModel):
    rule_id: str
    hit: bool
    reason: str
    observed: dict[str, Any] = Field(default_factory=dict)
    supporting_evidence_ids: list[str] = Field(default_factory=list)


class SafetyGateResult(StrictModel):
    blocked: bool
    mandatory_evidence_missing: bool = False
    checks: list[GateCheck]
    reasons: list[str]
    gate_blocked: bool | None = None
    hit_rules: list[str] = Field(default_factory=list)
    observed_values: dict[str, Any] = Field(default_factory=dict)
    supporting_evidence_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def fill_gate_alias(self) -> "SafetyGateResult":
        if self.gate_blocked is None:
            self.gate_blocked = self.blocked
        return self


class DecisionScoreFactors(StrictModel):
    semantic_quality: float = Field(ge=0, le=1)
    evidence_coverage: float | None = Field(default=None, ge=0, le=1)
    evidence_coverage_applicable: bool
    applied_weights: dict[str, float] = Field(default_factory=dict)
    five_factors: dict[str, ScoreFactor] = Field(default_factory=dict)
    semantic_confidence: float | None = Field(default=None, ge=0, le=1)
    ambiguity_penalty: float | None = Field(default=None, ge=0, le=1)
    semantic_ambiguity_beta: float | None = Field(default=None, ge=0)
    beta_source: str | None = None
    validated_evidence_count: int = Field(default=0, ge=0)
    validated_trust_values: list[dict[str, Any]] = Field(default_factory=list)
    trust_formula: str | None = None
    trust_value_source: str | None = None

    @model_validator(mode="before")
    @classmethod
    def infer_legacy_applicability(cls, data: Any) -> Any:
        if isinstance(data, dict) and "evidence_coverage_applicable" not in data:
            data = dict(data)
            data["evidence_coverage_applicable"] = data.get("evidence_coverage") is not None
        return data

    @model_validator(mode="after")
    def validate_coverage_semantics(self) -> "DecisionScoreFactors":
        if self.evidence_coverage_applicable != (self.evidence_coverage is not None):
            raise ValueError("evidence_coverage 与 evidence_coverage_applicable 语义不一致")
        return self


class IntentSafetyAssessment(StrictModel):
    clause_index: int = Field(ge=0)
    intent_id: str
    quality_metrics: EvidenceQualityMetrics
    gate_blocked: bool
    gate_hit_rules: list[str] = Field(default_factory=list)
    gate_reasons: list[str] = Field(default_factory=list)
    gate_observed: dict[str, Any] = Field(default_factory=dict)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    score_factors: DecisionScoreFactors
    safety_score: float = Field(ge=0, le=1)
    score_decision: DecisionLabel
    final_safety_decision: DecisionLabel
    decision_sources: list[DecisionSource] = Field(default_factory=list)
    decision_merge_reason: str
    reason_codes: list[str] = Field(default_factory=list)
    explanations: list[str] = Field(default_factory=list)


class ExecutionTokenView(StrictModel):
    """多意图放行时为每个意图签发的执行令牌展示视图。"""

    token: str = Field(repr=False)
    intent_id: str
    label: str = ""
    action: str = ""
    target: str = ""
    area: str = "unknown"


class DecisionResult(StrictModel):
    turn_id: str
    decision: DecisionLabel
    score_decision: DecisionLabel
    final_decision: DecisionLabel
    decision_sources: list[DecisionSource]
    decision_merge_reason: str
    safety_score: float = Field(ge=0, le=1)
    soft_safety_score: float = Field(ge=0, le=1)
    gate_blocked: bool
    gate_reasons: list[str] = Field(default_factory=list)
    score_evaluation_mode: Literal["normal", "diagnostic_after_gate"] = "normal"
    score_factors: DecisionScoreFactors
    explanations: list[str] = Field(default_factory=list)
    review_question: str | None = None
    authorization_token: str | None = Field(default=None, repr=False)
    execution_tokens: list[ExecutionTokenView] = Field(default_factory=list)
    jailbreak_risk: float = Field(default=0, ge=0, le=1)
    decision_confidence: float | None = Field(default=None, ge=0, le=1)
    reason_codes: list[str] = Field(default_factory=list)
    advanced_reasoning: AdvancedReasoningResult | None = None
    causal_correction: CausalCorrectionResult | None = None
    memory_propagation: MemoryPropagationResult | None = None
    grounding_failures: list[GroundingFailure] = Field(default_factory=list)
    conflicts: list[JailbreakConflict] = Field(default_factory=list)
    intent_safety_assessments: list[IntentSafetyAssessment] = Field(default_factory=list)
    aggregate_safety_decision: DecisionLabel | None = None
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="before")
    @classmethod
    def fill_compatibility_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("score_decision", data.get("decision"))
            data.setdefault("final_decision", data.get("decision"))
            data.setdefault(
                "decision_sources",
                [DecisionSource.SAFETY_SCORE, DecisionSource.LEGACY_COMPATIBILITY],
            )
            data.setdefault(
                "decision_merge_reason",
                "LEGACY_COMPATIBILITY: final_decision inherited from decision",
            )
            data.setdefault("soft_safety_score", data.get("safety_score"))
        return data

    @model_validator(mode="after")
    def validate_compatibility_fields(self) -> "DecisionResult":
        if self.decision != self.score_decision:
            raise ValueError("decision 与 score_decision 必须一致")
        if abs(self.safety_score - self.soft_safety_score) > 1e-9:
            raise ValueError("safety_score 是 soft_safety_score 的兼容字段，两者必须一致")
        return self


class AdvancedDecisionResult(StrictModel):
    """Complete final decision together with its auditable reasoning trace."""

    decision: DecisionResult
    reasoning: AdvancedReasoningResult
    gate_result: SafetyGateResult


class VehicleState(StrictModel):
    state_epoch_id: str = ""
    started_at: datetime = Field(default_factory=utc_now)
    reset_count: int = Field(default=0, ge=0)
    last_reset_at: datetime | None = None
    reset_reason: str | None = None
    vehicle_speed: float | None = Field(default=0, ge=0)
    gear_position: str | None = "P"
    door_lock_state: str | None = "UNLOCKED"
    door_state: str | None = "CLOSED"
    occupant_role: str | None = "driver"
    speaker_zone: str | None = "driver"
    vehicle_mode: str | None = "REAL_DRIVING"
    authentication_state: str | bool | None = "AUTHENTICATED"
    ambient_light: float | int | str | None = 100
    headlight_state: str | None = "OFF"
    wiper_mode: str | None = "OFF"
    wiper_intensity: float | None = Field(default=0, ge=0)
    wiper_frequency: float | None = Field(default=0, ge=0)
    wiper_wiping: bool | None = False
    wiper_error: bool | None = False
    weather: str | None = "CLEAR"
    window_state: str | None = "CLOSED"
    sunroof_state: str | None = "CLOSED"
    navigation_active: bool | None = False
    reverse_camera_active: bool | None = False
    display_state: str | None = "ON"
    music_state: str | None = "STOPPED"
    ac_state: str | None = "OFF"
    front_obstacle_distance: float | None = Field(default=100, ge=0)
    speed_limit: float | None = Field(default=120, ge=0)
    brake_state: str | None = "RELEASED"
    rear_obstacle_distance: float | None = Field(default=100, ge=0)
    road_condition: str | None = "DRY"
    ultrasonic_distance: float | None = Field(default=5, ge=0)
    surround_camera_state: str | None = "AVAILABLE"
    emergency_flag: bool | None = False
    collision_state: str | bool | None = "NONE"
    collision_target: str | None = None
    collision_at: datetime | None = None
    surrounding_objects: list[dict[str, Any]] = Field(default_factory=list)
    safety_constraint: str | None = "ENABLED"
    updated_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="before")
    @classmethod
    def reject_wide_numeric_evidence_values(cls, data: Any) -> Any:
        return _validate_vehicle_source_fields(data)


class VehicleStatePatch(StrictModel):
    vehicle_speed: float | None = Field(default=None, ge=0)
    gear_position: str | None = None
    door_lock_state: str | None = None
    door_state: str | None = None
    occupant_role: str | None = None
    speaker_zone: str | None = None
    vehicle_mode: str | None = None
    authentication_state: str | bool | None = None
    ambient_light: float | int | str | None = None
    headlight_state: str | None = None
    wiper_mode: str | None = None
    wiper_intensity: float | None = Field(default=None, ge=0)
    wiper_frequency: float | None = Field(default=None, ge=0)
    wiper_wiping: bool | None = None
    wiper_error: bool | None = None
    weather: str | None = None
    window_state: str | None = None
    sunroof_state: str | None = None
    navigation_active: bool | None = None
    reverse_camera_active: bool | None = None
    display_state: str | None = None
    music_state: str | None = None
    ac_state: str | None = None
    front_obstacle_distance: float | None = Field(default=None, ge=0)
    speed_limit: float | None = Field(default=None, ge=0)
    brake_state: str | None = None
    rear_obstacle_distance: float | None = Field(default=None, ge=0)
    road_condition: str | None = None
    ultrasonic_distance: float | None = Field(default=None, ge=0)
    surround_camera_state: str | None = None
    emergency_flag: bool | None = None
    collision_state: str | bool | None = None
    safety_constraint: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_wide_numeric_evidence_values(cls, data: Any) -> Any:
        return _validate_vehicle_source_fields(data)


class RuntimeSafetyContext(StrictModel):
    """Trusted non-evidence runtime values used only by direct safety interlocks."""

    navigation_active: bool | None = None
    display_state: str | None = None
    music_state: str | None = None
    reverse_camera_active: bool | None = None
    surround_camera_state: str | None = None
    ultrasonic_distance: float | None = Field(default=None, ge=0)

    @classmethod
    def from_vehicle_state(cls, state: VehicleState) -> "RuntimeSafetyContext":
        return cls(
            navigation_active=state.navigation_active,
            display_state=state.display_state,
            music_state=state.music_state,
            reverse_camera_active=state.reverse_camera_active,
            surround_camera_state=state.surround_camera_state,
            ultrasonic_distance=state.ultrasonic_distance,
        )


class EvidenceObservationInput(StrictModel):
    evidence_type: str
    source: str
    value: Any = None
    unit: str | None = None
    age_seconds: float = Field(default=0, ge=0)
    available: bool = True
    integrity_valid: bool = True
    expires_in_seconds: float | None = None

    @field_validator("evidence_type")
    @classmethod
    def canonical_evidence_type_only(cls, value: str) -> str:
        from app.services.evidence.catalog import require_canonical_evidence_type

        return require_canonical_evidence_type(value)


class TrustedRuntimeContext(StrictModel):
    """Backend-only trust boundary for simulator, scenario, and verified audio inputs."""

    state_overrides: VehicleStatePatch | None = None
    evidence_overrides: list[EvidenceObservationInput] = Field(default_factory=list)
    subject_role: str | None = None
    subject_zone: str | None = None
    subject_source: str | None = None
    zone_source: str | None = None


class TextCommandRequest(StrictModel):
    text: str = Field(min_length=1, max_length=2048)
    speaker_zone: str = "driver"
    speaker_role: str = "driver"
    session_id: str | None = Field(default=None, min_length=1, max_length=100)

    @model_validator(mode="after")
    def reject_blank_text(self) -> "TextCommandRequest":
        if not self.text.strip():
            raise ValueError("text 不能只包含空白字符")
        return self


class MicrophoneCommandRequest(StrictModel):
    duration_seconds: float = Field(default=4.0, ge=0.5, le=15.0)
    device: int | str | None = None
    speaker_zone: Literal[
        "driver", "front_passenger", "rear_left", "rear_right", "outside", "unknown"
    ] = "unknown"
    speaker_role: str = "unknown"
    session_id: str | None = Field(default=None, min_length=1, max_length=100)


class AuditRecord(StrictModel):
    record_type: Literal["COMMAND"] = "COMMAND"
    audit_id: str = Field(default_factory=lambda: make_id("AUD"))
    turn_id: str
    root_turn_id: str | None = None
    parent_turn_id: str | None = None
    attempt_no: int = Field(default=0, ge=0)
    workflow_type: str = "INITIAL"
    input_trust_result: VoiceTrustResult
    transcription_result: TranscriptionResult
    spectrum_analysis: SpectrumAnalysisResult | None = None
    zone_permission_result: ZonePermissionResult | None = None
    audio_input_metadata: dict[str, Any] = Field(default_factory=dict)
    active_scenario: dict[str, Any] = Field(default_factory=dict)
    semantic_frame: SemanticFrame
    request_routing: RequestRouting | None = None
    evidence_demand: EvidenceDemand
    candidate_recall_results: list[EvidenceNode]
    vectorization_metadata: list[VectorizationMetadata] = Field(default_factory=list)
    query_vector_digests: list[str] = Field(default_factory=list)
    retrieval_metadata: RetrievalMetadata | None = None
    evidence_subgraph: EvidenceSubgraph | None = None
    evidence_subgraph_summary: dict[str, Any] = Field(default_factory=dict)
    evidence_quality_metrics: EvidenceQualityMetrics | dict[str, float] = Field(default_factory=dict)
    conflict_records: list[dict[str, Any]] = Field(default_factory=list)
    safety_gate_result: SafetyGateResult
    score_details: DecisionScoreFactors
    final_decision: DecisionResult
    review_process: list[dict[str, Any]] = Field(default_factory=list)
    vehicle_execution_request: dict[str, Any] | None = None
    vehicle_execution_feedback: dict[str, Any] | None = None
    audit_quality: AuditQualityMetadata | None = None
    horizontal_memory: list[MemoryLink] = Field(default_factory=list)
    vertical_propagation: list[MemoryLink] = Field(default_factory=list)
    causal_candidate_edges: list[CausalEdge] = Field(default_factory=list)
    causal_pruned_edges: list[CausalEdge] = Field(default_factory=list)
    causal_removed_edges: list[CausalEdge] = Field(default_factory=list)
    causal_posterior: dict[str, float] = Field(default_factory=dict)
    causal_entropy: float | None = Field(default=None, ge=0)
    decision_confidence: float | None = Field(default=None, ge=0, le=1)
    context_claims: list[ContextClaim] = Field(default_factory=list)
    grounding_failures: list[GroundingFailure] = Field(default_factory=list)
    jailbreak_conflicts: list[JailbreakConflict] = Field(default_factory=list)
    jailbreak_risk: float = Field(default=0, ge=0, le=1)
    complete_gate_result: SafetyGateResult | None = None
    five_factor_score: dict[str, ScoreFactor] = Field(default_factory=dict)
    advanced_explanations: list[str] = Field(default_factory=list)
    memory_propagation: MemoryPropagationResult | None = None
    causal_correction: CausalCorrectionResult | None = None
    decision_explanation: DecisionExplanation | None = None
    candidate_interpretations: list[ReviewCandidateInterpretation] = Field(default_factory=list)
    candidate_availability: str = "LEGACY_NOT_RECORDED"
    interpreter_review_question: str | None = None
    recommended_recovery: RecoveryRecommendation | None = None
    generation_metadata: InterpreterGenerationMetadata | None = None
    interpreter_validation_result: dict[str, Any] = Field(default_factory=dict)
    interpreter_result: InterpreterResult | None = None
    advanced_reasoning: AdvancedReasoningResult | None = None
    turn_timing: TurnTiming | None = None
    runtime_capability: RuntimeCapabilityStatus | None = None
    previous_hash: str = ""
    current_hash: str = ""
    signature: str | None = None
    signature_algorithm: str | None = None
    signature_key_id: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class ReviewOutcomeRecord(StrictModel):
    audit_id: str = Field(default_factory=lambda: make_id("AUD"))
    record_type: Literal["REVIEW_OUTCOME"] = "REVIEW_OUTCOME"
    original_audit_id: str
    original_turn_id: str
    root_turn_id: str
    review_action: Literal[ReviewAction.CANCEL] = ReviewAction.CANCEL
    original_final_decision: Literal[DecisionLabel.REVIEW] = DecisionLabel.REVIEW
    effective_final_decision: Literal[DecisionLabel.BLOCK] = DecisionLabel.BLOCK
    effective_decision_sources: list[DecisionSource]
    decision_merge_reason: str = Field(min_length=1)
    token_issued: Literal[False] = False
    execution_allowed: Literal[False] = False
    idempotency_key: str
    created_at: datetime = Field(default_factory=utc_now)
    previous_hash: str = ""
    current_hash: str = ""
    signature: str | None = None
    signature_algorithm: str | None = None
    signature_key_id: str | None = None

    @model_validator(mode="after")
    def validate_review_outcome(self) -> "ReviewOutcomeRecord":
        expected_key = f"{self.original_audit_id}:{self.review_action.value}"
        if self.idempotency_key != expected_key:
            raise ValueError("REVIEW_OUTCOME idempotency_key 与关联审计不一致")
        if DecisionSource.USER_REVIEW not in self.effective_decision_sources:
            raise ValueError("REVIEW_OUTCOME 必须包含 USER_REVIEW 裁决来源")
        return self


AuditChainRecord = AuditRecord | ReviewOutcomeRecord


class RegulationHit(StrictModel):
    """法规检索命中的单条条文。"""

    standard_id: str
    clause: str
    content: str
    source: str
    score: float = Field(ge=0, le=1)
    evidence_types: list[str] = Field(default_factory=list)


class RegulationRationale(StrictModel):
    """一条指令检索到的法规依据集合（附加展示，不参与裁决）。"""

    demand_text: str
    hits: list[RegulationHit] = Field(default_factory=list)
    missing_types: list[str] = Field(default_factory=list)


class TextCommandResponse(StrictModel):
    turn_id: str
    root_turn_id: str | None = None
    parent_turn_id: str | None = None
    attempt_no: int = Field(default=0, ge=0)
    workflow_type: str = "INITIAL"
    input_trust_result: VoiceTrustResult
    transcription_result: TranscriptionResult
    zone_permission_result: ZonePermissionResult | None = None
    semantic_frame: SemanticFrame
    request_routing: RequestRouting | None = None
    evidence_demand: EvidenceDemand
    evidence: list[EvidenceNode]
    query_vectors: list[list[float]]
    retrieval_metadata: RetrievalMetadata
    candidate_evidence: list[EvidenceNode]
    evidence_subgraph: EvidenceSubgraph
    quality_metrics: EvidenceQualityMetrics
    safety_gate: SafetyGateResult
    decision: DecisionResult
    audit: AuditRecord
    actionable: bool = True
    retrieval_scopes: list[str] = Field(default_factory=list)
    advanced_reasoning: AdvancedReasoningResult | None = None
    memory_propagation: MemoryPropagationResult | None = None
    causal_correction: CausalCorrectionResult | None = None
    interpreter_result: InterpreterResult | None = None
    grounding_failures: list[GroundingFailure] = Field(default_factory=list)
    jailbreak_conflicts: list[JailbreakConflict] = Field(default_factory=list)
    jailbreak_risk: float = Field(default=0, ge=0, le=1)
    score_factors: dict[str, ScoreFactor] = Field(default_factory=dict)
    decision_confidence: float | None = Field(default=None, ge=0, le=1)
    turn_timing: TurnTiming | None = None
    runtime_capability: RuntimeCapabilityStatus | None = None
    accepted: bool = True
    input_type: Literal["text"] = "text"
    websocket_channel: str | None = None
    interaction_request: InteractionRequest | None = None
    clarification_request: ClarificationRequest | None = None
    regulation_rationale: RegulationRationale | None = None


class AudioCommandResponse(StrictModel):
    turn_id: str
    voice_trust: VoiceTrustResult
    spectrum_analysis: SpectrumAnalysisResult
    asr_result: TranscriptionResult | None = None
    zone_permission: ZonePermissionResult | None = None
    semantic_frame: SemanticFrame | None = None
    evidence_subgraph: EvidenceSubgraph | None = None
    decision: DecisionResult
    audit: AuditRecord
    pipeline: TextCommandResponse | None = None
    accepted: bool = True
    input_type: Literal["audio"] = "audio"
    websocket_channel: str | None = None
    interaction_request: InteractionRequest | None = None
    clarification_request: ClarificationRequest | None = None


class HealthResponse(StrictModel):
    status: str
    service: str
    stage: str
    database: str
    model_ready: bool = True
    embedding_implementation: str = ""
    index_ready: bool = True
    index_implementation: str = ""
    vehicle_adapter: str = ""
    token_secret_source: str = ""
    token_key_id: str = ""
    token_key_version: int = Field(default=0, ge=0)
    token_key_status: str = ""
    revoked_tokens_on_startup: int = Field(default=0, ge=0)
    workflow_event_store: str = ""
    websocket_ready: bool = False
    voice_trust_mode: Literal["enforce", "observe"] = "enforce"
    runtime_capability: RuntimeCapabilityStatus | None = None
    evidence_repository: "EvidenceRepositoryStatus | None" = None


class IndexRebuildRequest(StrictModel):
    exclude_types: list[str] = Field(default_factory=list)


class IndexParametersRequest(StrictModel):
    M: int = Field(gt=0)
    ef_construction: int = Field(gt=0)
    ef_search: int = Field(gt=0)
    layer_count: int = Field(gt=0)


class CarlaObstacleRequest(StrictModel):
    type: str = Field(default="obstacle", pattern="^(pedestrian|vehicle|obstacle)$")


class CarlaTrafficLightRequest(StrictModel):
    state: str = Field(default="RED", pattern="^(RED|GREEN|YELLOW)$")


class IndexStatus(StrictModel):
    implementation: str
    node_count: int = Field(ge=0)
    dimension: int = Field(gt=0)
    M: int = Field(gt=0)
    ef_construction: int = Field(gt=0)
    ef_search: int = Field(gt=0)
    layer_count: int = Field(gt=0)
    top_k: int = Field(gt=0)
    canonical_node_count: int = Field(default=0, ge=0)
    ephemeral_node_count: int = Field(default=0, ge=0)
    index_update_count: int = Field(default=0, ge=0)
    index_rebuild_count: int = Field(default=0, ge=0)
    deduplicated_count: int = Field(default=0, ge=0)
    degraded: bool
    degradation_reason: str | None = None
    excluded_types: list[str] = Field(default_factory=list)
    last_built_at: datetime | None = None
    index_build_id: str | None = None
    index_config_digest: str | None = None
    node_set_digest: str | None = None
    stable_identity_version: str | None = None
    stable_identity_source: str | None = None
    content_identity_version: str | None = None
    content_identity_source: str | None = None
    index_fingerprint_version: str | None = None
    node_set_digest_version: str | None = None
    build_id_payload_version: str | None = None
    classification_mapping_digest: str | None = None
    formula_version: str | None = None
    formula_source: str | None = None
    security_mapping_version: str | None = None
    security_rank_mapping_source: str | None = None
    index_seed_digest: str | None = None
    index_seed_source: str | None = None
    random_level_distribution: str | None = None
    random_level_source: str | None = None
    implementation_source: str | None = None
    layering_mode: str | None = None
    security_layer_count: int = Field(default=0, ge=0)
    security_layers: list[LayerIndexStatus] = Field(default_factory=list)
    per_layer_node_count: dict[int, int] = Field(default_factory=dict)
    mapping_coverage: float | None = Field(default=None, ge=0, le=1)
    unclassified_types: list[str] = Field(default_factory=list)


class CurrentEvidenceResponse(StrictModel):
    nodes: list[EvidenceNode]
    evidence_type_count: int = Field(ge=0)
    node_count: int = Field(ge=0)
    short_term_availability: dict[str, float | None] = Field(default_factory=dict)
    long_term_availability: dict[str, float | None] = Field(default_factory=dict)
    repository_status: "EvidenceRepositoryStatus | None" = None


class EvidenceRepositoryStatus(StrictModel):
    resident_node_count: int = Field(default=0, ge=0)
    dynamic_node_count: int = Field(default=0, ge=0)
    static_node_count: int = Field(default=0, ge=0)
    stream_count: int = Field(default=0, ge=0)
    retained_turn_count: int = Field(default=0, ge=0)
    evicted_node_count: int = Field(default=0, ge=0)
    retention_window: int = Field(default=16, ge=1)


class CausalStatus(StrictModel):
    learning_record_count: int = Field(default=0, ge=0)
    excluded_record_count: int = Field(default=0, ge=0)
    candidate_edge_count: int = Field(default=0, ge=0)
    pruned_edge_count: int = Field(default=0, ge=0)
    removed_edge_count: int = Field(default=0, ge=0)
    graph_node_count: int = Field(default=0, ge=0)
    graph_edge_count: int = Field(default=0, ge=0)
    last_rebuilt_at: datetime | None = None
    data_sufficiency: str = "insufficient"
    minimum_sample_count: int = Field(default=20, ge=1)
    model_version: str = "causal-unbuilt"
    model_built_at: datetime | None = None
    source_audit_count: int = Field(default=0, ge=0)
    auto_rebuild_enabled: bool = False
    rebuild_every_eligible_audits: int = Field(default=20, ge=1)
    eligible_audits_since_rebuild: int = Field(default=0, ge=0)
    auto_rebuild_running: bool = False
    last_rebuild_error: str | None = None


class LearningAuditStatus(StrictModel):
    total_records: int = Field(default=0, ge=0)
    learning_record_count: int = Field(default=0, ge=0)
    excluded_record_count: int = Field(default=0, ge=0)
    quality_distribution: dict[str, int] = Field(default_factory=dict)
    records: list[AuditQualityMetadata] = Field(default_factory=list)


class WorkflowEvent(StrictModel):
    event_id: str = Field(default_factory=lambda: make_id("WFE"))
    root_turn_id: str
    related_turn_id: str | None = None
    parent_turn_id: str | None = None
    sequence_no: int = Field(ge=1)
    event_type: WorkflowEventType
    payload: dict[str, Any] = Field(default_factory=dict)
    previous_event_hash: str
    current_event_hash: str
    created_at: datetime = Field(default_factory=utc_now)


class WorkflowChainVerification(StrictModel):
    root_turn_id: str
    valid: bool
    event_count: int = Field(ge=0)
    failure_event_id: str | None = None


class ReviewRequest(StrictModel):
    action: ReviewAction
    confirmation_text: str | None = Field(default=None, max_length=2048)
    corrected_text: str | None = Field(default=None, max_length=2048)
    cancel_reason: str | None = Field(default=None, max_length=500)
    selected_candidate_id: str | None = Field(default=None, max_length=128)

    @model_validator(mode="after")
    def validate_action_payload(self) -> "ReviewRequest":
        if self.action == ReviewAction.CORRECT and not (self.corrected_text or "").strip():
            raise ValueError("CORRECT 必须提供 corrected_text")
        if self.action != ReviewAction.CONFIRM and self.selected_candidate_id is not None:
            raise ValueError("selected_candidate_id 仅允许用于 CONFIRM")
        return self


class AuthorizationTokenMetadata(StrictModel):
    token_id: str
    root_turn_id: str
    turn_id: str
    action: str
    target: str
    area: str
    intent_id: str | None = None
    mode: str | None = None
    value: Any | None = None
    direction: str | None = None
    control_attribute: str | None = None
    capability_contract_id: str | None = None
    capability_contract_version: int | None = Field(default=None, ge=1)
    capability_contract_digest: str | None = None
    capability_adapter: str | None = None
    issued_at: datetime
    expires_at: datetime
    state_snapshot_digest: str
    token_digest: str
    key_id: str = "legacy"
    key_version: int | None = Field(default=None, ge=1)
    nonce_digest: str | None = None
    status: AuthorizationTokenStatus


class AuthorizationKeyMetadata(StrictModel):
    key_id: str
    key_version: int = Field(ge=1)
    created_at: datetime
    fingerprint: str
    source: str
    status: str


class AuthorizationGrant(StrictModel):
    authorization_token: str = Field(repr=False)
    metadata: AuthorizationTokenMetadata


class VehicleExecutionResult(StrictModel):
    execution_id: str = Field(default_factory=lambda: make_id("EXEC"))
    adapter: str
    simulated: bool
    status: str
    action: str
    target: str
    area: str
    intent_id: str | None = None
    mode: str | None = None
    value: Any | None = None
    direction: str | None = None
    control_attribute: str | None = None
    capability_contract_digest: str | None = None
    before_state: VehicleState
    after_state: VehicleState
    feedback: str
    duration_ms: float = Field(ge=0)
    created_at: datetime = Field(default_factory=utc_now)


class ExecuteRequest(StrictModel):
    authorization_token: str = Field(min_length=20, repr=False)
    interaction_id: str = Field(min_length=1, max_length=128)
    intent_id: str | None = Field(default=None, min_length=1, max_length=128)
    session_id: str | None = Field(default=None, min_length=1, max_length=100)


class ExecuteResult(StrictModel):
    root_turn_id: str
    turn_id: str
    accepted: bool
    token_status: AuthorizationTokenStatus
    reason: str
    precheck_turn_id: str | None = None
    precheck_decision: DecisionLabel | None = None
    execution: VehicleExecutionResult | None = None


class TurnWorkflowStatus(StrictModel):
    root_turn_id: str
    current_turn_id: str
    status: str
    review_attempts: int = Field(ge=0)
    max_review_attempts: int = Field(ge=1)
    latest_decision: DecisionLabel
    token_status: AuthorizationTokenStatus | None = None
    event_count: int = Field(ge=0)
    terminal: bool


class ReviewResult(StrictModel):
    root_turn_id: str
    related_turn_id: str
    action: ReviewAction
    accepted: bool
    reason: str
    workflow_status: TurnWorkflowStatus
    decision: DecisionResult
    review_question: str | None = None
    command_result: TextCommandResponse | None = None
    terminal_audit_id: str | None = None
    rejection_code: str | None = None
    rejection_status_code: int | None = Field(default=None, ge=400, le=499)


class PipelineEvent(StrictModel):
    event_id: str = Field(default_factory=lambda: make_id("PIPE"))
    session_id: str
    turn_id: str
    sequence: int = Field(ge=1)
    event_type: str = "PIPELINE_STAGE"
    stage: str
    status: str = "COMPLETED"
    timestamp: datetime = Field(default_factory=utc_now)
    duration_ms: float = Field(default=0, ge=0)
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def fill_public_envelope(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            stage = str(data.get("stage", "PIPELINE_STAGE"))
            data.setdefault("event_type", stage)
            payload = data.get("payload")
            payload_status = payload.get("status") if isinstance(payload, dict) else None
            if payload_status is not None:
                data.setdefault("status", str(payload_status))
            elif any(term in stage for term in ("FAILED", "REJECTED", "BLOCKED")):
                data.setdefault("status", "FAILED")
            else:
                data.setdefault("status", "COMPLETED")
        return data


class AuditPage(StrictModel):
    items: list[AuditRecord]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)


class TurnTimeline(StrictModel):
    root_turn_id: str
    audits: list[AuditRecord] = Field(default_factory=list)
    workflow_events: list[WorkflowEvent] = Field(default_factory=list)
    ordered_items: list[dict[str, Any]] = Field(default_factory=list)
    items: list[dict[str, Any]] = Field(default_factory=list)
    historical_execution_state: list[VehicleExecutionResult] = Field(default_factory=list)
    current_simulator_state: VehicleState
