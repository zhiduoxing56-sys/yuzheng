from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())


class EvidenceStatus(str, Enum):
    VALID = "VALID"
    SUSPICIOUS = "SUSPICIOUS"
    STALE = "STALE"
    TAMPERED = "TAMPERED"
    MISSING = "MISSING"


class DecisionLabel(str, Enum):
    PASS = "PASS"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


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


class AuditRecordQuality(str, Enum):
    VALID = "VALID"
    KNOWN_BUG = "KNOWN_BUG"
    ENCODING_ERROR = "ENCODING_ERROR"
    SUPERSEDED = "SUPERSEDED"
    TEST_ONLY = "TEST_ONLY"
    LEGACY_MODEL = "LEGACY_MODEL"


class VoiceTrustResult(StrictModel):
    turn_id: str
    audio_source: str
    speaker_zone: str
    speaker_role: str
    la_score: float = Field(ge=0, le=1)
    pa_score: float = Field(ge=0, le=1)
    replay_risk: float = Field(ge=0, le=1)
    synthetic_risk: float = Field(ge=0, le=1)
    zone_risk: float = Field(ge=0, le=1)
    trust_score: float = Field(ge=0, le=1)
    input_trust_label: str
    audio_fingerprint: str
    created_at: datetime = Field(default_factory=utc_now)


class TranscriptionResult(StrictModel):
    turn_id: str
    text: str
    confidence: float = Field(ge=0, le=1)
    adapter: str
    model_inference_performed: bool
    created_at: datetime = Field(default_factory=utc_now)


class SemanticFrame(StrictModel):
    frame_id: str = Field(default_factory=lambda: make_id("SEM"))
    turn_id: str
    raw_text: str
    normalized_text: str
    action: str
    target: str
    area: str
    value: str | None = None
    control_domain: str
    semantic_confidence: float = Field(ge=0, le=1)
    ambiguity_score: float = Field(ge=0, le=1)
    risk_level: str
    risk_tags: list[str] = Field(default_factory=list)
    context_claims: dict[str, Any] = Field(default_factory=dict)
    required_evidence_types: list[str] = Field(default_factory=list)
    optional_evidence_types: list[str] = Field(default_factory=list)


class EvidenceDemand(StrictModel):
    demand_id: str = Field(default_factory=lambda: make_id("DEM"))
    turn_id: str
    action: str
    target: str
    risk_level: str
    query_text: str
    query_vector: list[float] = Field(default_factory=list)
    vectorization_metadata: "VectorizationMetadata | None" = None
    required_types: list[str] = Field(default_factory=list)
    optional_types: list[str] = Field(default_factory=list)
    priority: int = Field(default=0, ge=0, le=100)
    retrieval_scope: str = "control_evidence"


class EvidenceNode(StrictModel):
    node_id: str = Field(default_factory=lambda: make_id("EVI"))
    evidence_type: str
    layer: str
    source: str
    value: Any
    unit: str | None = None
    timestamp: datetime
    expires_at: datetime
    freshness: float = Field(ge=0, le=1)
    consistency: float = Field(ge=0, le=1)
    availability: float = Field(ge=0, le=1)
    semantic_similarity: float = Field(ge=0, le=1)
    mandatory: bool
    quality_label: EvidenceStatus
    integrity_hash: str
    metadata: dict[str, Any] = Field(default_factory=dict)


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


class RetrievalMetadata(StrictModel):
    implementation: str
    index_node_count: int = Field(ge=0)
    vector_dimension: int = Field(gt=0)
    M: int = Field(gt=0)
    ef_construction: int = Field(gt=0)
    ef_search: int = Field(gt=0)
    top_k: int = Field(gt=0)
    candidate_count: int = Field(ge=0)
    duration_ms: float = Field(ge=0)
    empty_index: bool
    degraded: bool
    degradation_reason: str | None = None
    excluded_types: list[str] = Field(default_factory=list)
    last_built_at: datetime | None = None


class MandatoryRecallRecord(StrictModel):
    evidence_type: str
    status: str
    candidate_node_ids: list[str] = Field(default_factory=list)
    recalled_node_id: str | None = None
    source: str | None = None
    reason: str


class EvidenceQualityMetrics(StrictModel):
    ecr: float | None = Field(default=None, ge=0, le=1)
    evidence_coverage_applicable: bool
    ecs: float = Field(ge=0, le=1)
    ef: float = Field(ge=0, le=1)
    sas: float = Field(ge=0, le=1)
    eas: float = Field(ge=0, le=1)
    conflict_count: int = Field(default=0, ge=0)
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
    required_types: list[str] = Field(default_factory=list)
    retrieved_types: list[str] = Field(default_factory=list)
    mandatory_recalled_types: list[str] = Field(default_factory=list)
    missing_types: list[str] = Field(default_factory=list)
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


class MemoryPropagationResult(StrictModel):
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


class CausalCorrectionResult(StrictModel):
    causal_graph: dict[str, Any] = Field(default_factory=dict)
    candidate_edges: list[CausalEdge] = Field(default_factory=list)
    pruned_edges: list[CausalEdge] = Field(default_factory=list)
    semantic_prior: dict[str, float] = Field(default_factory=dict)
    historical_support: dict[str, float] = Field(default_factory=dict)
    posterior_weights: dict[str, float] = Field(default_factory=dict)
    corrected_weights: dict[str, float] = Field(default_factory=dict)
    entropy: float = Field(default=0, ge=0, le=1)
    decision_confidence: float = Field(default=0, ge=0, le=1)
    sample_count: int = Field(default=0, ge=0)
    data_sufficiency: str = "insufficient"
    learning_record_ids: list[str] = Field(default_factory=list)
    excluded_record_count: int = Field(default=0, ge=0)
    advanced_reasoning_applied: bool = True
    duration_ms: float = Field(default=0, ge=0)


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
    decision_confidence: float = Field(default=0, ge=0, le=1)
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


class DecisionResult(StrictModel):
    turn_id: str
    decision: DecisionLabel
    final_decision: DecisionLabel
    safety_score: float = Field(ge=0, le=1)
    soft_safety_score: float = Field(ge=0, le=1)
    gate_blocked: bool
    gate_reasons: list[str] = Field(default_factory=list)
    score_factors: DecisionScoreFactors
    explanations: list[str] = Field(default_factory=list)
    review_question: str | None = None
    authorization_token: str | None = None
    jailbreak_risk: float = Field(default=0, ge=0, le=1)
    decision_confidence: float = Field(default=0, ge=0, le=1)
    advanced_reasoning: AdvancedReasoningResult | None = None
    causal_correction: CausalCorrectionResult | None = None
    memory_propagation: MemoryPropagationResult | None = None
    grounding_failures: list[GroundingFailure] = Field(default_factory=list)
    conflicts: list[JailbreakConflict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="before")
    @classmethod
    def fill_compatibility_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            data.setdefault("final_decision", data.get("decision"))
            data.setdefault("soft_safety_score", data.get("safety_score"))
        return data

    @model_validator(mode="after")
    def validate_compatibility_fields(self) -> "DecisionResult":
        if self.decision != self.final_decision:
            raise ValueError("decision 与 final_decision 必须一致")
        if abs(self.safety_score - self.soft_safety_score) > 1e-9:
            raise ValueError("safety_score 是 soft_safety_score 的兼容字段，两者必须一致")
        return self


class AdvancedDecisionResult(StrictModel):
    """Complete final decision together with its auditable reasoning trace."""

    decision: DecisionResult
    reasoning: AdvancedReasoningResult
    gate_result: SafetyGateResult


class VehicleState(StrictModel):
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
    weather: str | None = "CLEAR"
    window_state: str | None = "CLOSED"
    navigation_active: bool | None = False
    reverse_camera_active: bool | None = False
    display_state: str | None = "ON"
    front_obstacle_distance: float | None = Field(default=100, ge=0)
    speed_limit: float | None = Field(default=120, ge=0)
    brake_state: str | None = "RELEASED"
    rear_obstacle_distance: float | None = Field(default=100, ge=0)
    road_condition: str | None = "DRY"
    ultrasonic_distance: float | None = Field(default=5, ge=0)
    surround_camera_state: str | None = "AVAILABLE"
    emergency_flag: bool | None = False
    safety_constraint: str | None = "ENABLED"
    updated_at: datetime = Field(default_factory=utc_now)


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
    weather: str | None = None
    window_state: str | None = None
    navigation_active: bool | None = None
    reverse_camera_active: bool | None = None
    display_state: str | None = None
    front_obstacle_distance: float | None = Field(default=None, ge=0)
    speed_limit: float | None = Field(default=None, ge=0)
    brake_state: str | None = None
    rear_obstacle_distance: float | None = Field(default=None, ge=0)
    road_condition: str | None = None
    ultrasonic_distance: float | None = Field(default=None, ge=0)
    surround_camera_state: str | None = None
    emergency_flag: bool | None = None
    safety_constraint: str | None = None


class EvidenceObservationInput(StrictModel):
    evidence_type: str
    source: str
    value: Any = None
    unit: str | None = None
    age_seconds: float = Field(default=0, ge=0)
    available: bool = True
    integrity_valid: bool = True
    expires_in_seconds: float | None = None


class TextCommandRequest(StrictModel):
    text: str = Field(min_length=1, max_length=500)
    speaker_zone: str = "driver"
    speaker_role: str = "driver"
    state_overrides: VehicleStatePatch | None = None
    evidence_overrides: list[EvidenceObservationInput] = Field(default_factory=list)

    @model_validator(mode="after")
    def reject_blank_text(self) -> "TextCommandRequest":
        if not self.text.strip():
            raise ValueError("text 不能只包含空白字符")
        return self


class AuditRecord(StrictModel):
    audit_id: str = Field(default_factory=lambda: make_id("AUD"))
    turn_id: str
    input_trust_result: VoiceTrustResult
    transcription_result: TranscriptionResult
    semantic_frame: SemanticFrame
    evidence_demand: EvidenceDemand
    candidate_recall_results: list[EvidenceNode]
    mandatory_supplement_records: list[dict[str, Any]] = Field(default_factory=list)
    vectorization_metadata: VectorizationMetadata | None = None
    query_vector_digest: str = ""
    retrieval_metadata: RetrievalMetadata | None = None
    mandatory_recall_records: list[MandatoryRecallRecord] = Field(default_factory=list)
    missing_evidence_types: list[str] = Field(default_factory=list)
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
    causal_posterior: dict[str, float] = Field(default_factory=dict)
    causal_entropy: float | None = Field(default=None, ge=0, le=1)
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
    advanced_reasoning: AdvancedReasoningResult | None = None
    turn_timing: TurnTiming | None = None
    previous_hash: str = ""
    current_hash: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class TextCommandResponse(StrictModel):
    turn_id: str
    input_trust_result: VoiceTrustResult
    transcription_result: TranscriptionResult
    semantic_frame: SemanticFrame
    evidence_demand: EvidenceDemand
    evidence: list[EvidenceNode]
    query_vector: list[float]
    retrieval_metadata: RetrievalMetadata
    candidate_evidence: list[EvidenceNode]
    mandatory_recall_records: list[MandatoryRecallRecord]
    evidence_subgraph: EvidenceSubgraph
    quality_metrics: EvidenceQualityMetrics
    safety_gate: SafetyGateResult
    decision: DecisionResult
    audit: AuditRecord
    actionable: bool = True
    retrieval_scope: str = "control_evidence"
    advanced_reasoning: AdvancedReasoningResult | None = None
    memory_propagation: MemoryPropagationResult | None = None
    causal_correction: CausalCorrectionResult | None = None
    grounding_failures: list[GroundingFailure] = Field(default_factory=list)
    jailbreak_conflicts: list[JailbreakConflict] = Field(default_factory=list)
    jailbreak_risk: float = Field(default=0, ge=0, le=1)
    score_factors: dict[str, ScoreFactor] = Field(default_factory=dict)
    decision_confidence: float = Field(default=0, ge=0, le=1)
    turn_timing: TurnTiming | None = None


class HealthResponse(StrictModel):
    status: str
    service: str
    stage: str
    database: str


class IndexRebuildRequest(StrictModel):
    exclude_types: list[str] = Field(default_factory=list)


class IndexStatus(StrictModel):
    implementation: str
    node_count: int = Field(ge=0)
    dimension: int = Field(gt=0)
    M: int = Field(gt=0)
    ef_construction: int = Field(gt=0)
    ef_search: int = Field(gt=0)
    top_k: int = Field(gt=0)
    degraded: bool
    degradation_reason: str | None = None
    excluded_types: list[str] = Field(default_factory=list)
    last_built_at: datetime | None = None


class CurrentEvidenceResponse(StrictModel):
    nodes: list[EvidenceNode]
    evidence_type_count: int = Field(ge=0)
    node_count: int = Field(ge=0)
    short_term_availability: dict[str, float | None] = Field(default_factory=dict)
    long_term_availability: dict[str, float | None] = Field(default_factory=dict)


class CausalStatus(StrictModel):
    learning_record_count: int = Field(default=0, ge=0)
    excluded_record_count: int = Field(default=0, ge=0)
    candidate_edge_count: int = Field(default=0, ge=0)
    pruned_edge_count: int = Field(default=0, ge=0)
    graph_node_count: int = Field(default=0, ge=0)
    graph_edge_count: int = Field(default=0, ge=0)
    last_rebuilt_at: datetime | None = None
    data_sufficiency: str = "insufficient"


class LearningAuditStatus(StrictModel):
    total_records: int = Field(default=0, ge=0)
    learning_record_count: int = Field(default=0, ge=0)
    excluded_record_count: int = Field(default=0, ge=0)
    quality_distribution: dict[str, int] = Field(default_factory=dict)
    records: list[AuditQualityMetadata] = Field(default_factory=list)
