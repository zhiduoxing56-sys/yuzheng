from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import ConfigDict, Field, model_validator

from app.models.schemas import (
    AdvancedValidationResult,
    DecisionLabel,
    DecisionExplanation,
    DecisionSource,
    EvidenceEdge,
    EvidenceNode,
    EvidenceQualityMetrics,
    EvidenceSubgraph,
    LayerIndexStatus,
    LayerNavigationAvailability,
    MemoryDegreeStatistics,
    MemoryNodeLayer,
    MemoryPropagationStep,
    MemoryRelationEdge,
    ParentStateStatistics,
    CausalEdge,
    CausalNodeWeight,
    CausalPriorComponents,
    RecoveryRecommendation,
    ReviewCandidateInterpretation,
    InterpreterGenerationMetadata,
    RetrievalVisualizationPath,
    SecurityClass,
    SecurityLayerNavigation,
    ReviewAction,
    SafetyGateResult,
    SemanticFrame,
    SpectrumAnalysisResult,
    StrictModel,
    DecisionResult,
    TextCommandResponse,
    TranscriptionResult,
    TurnWorkflowStatus,
    WorkflowEvent,
)


class EvidenceDemandStatus(str, Enum):
    RETRIEVED = "RETRIEVED"
    MANDATORY_RECALLED = "MANDATORY_RECALLED"
    MISSING = "MISSING"
    STALE = "STALE"
    CONFLICT = "CONFLICT"
    TAMPERED = "TAMPERED"


class RetrievalOrigin(str, Enum):
    HNSW = "HNSW"
    MANDATORY_RECALL = "MANDATORY_RECALL"
    BOTH = "BOTH"
    NONE = "NONE"


class Availability(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ErrorCode(str, Enum):
    TURN_NOT_FOUND = "TURN_NOT_FOUND"
    AUDIT_NOT_FOUND = "AUDIT_NOT_FOUND"
    NODE_NOT_FOUND = "NODE_NOT_FOUND"
    NODE_NOT_IN_TURN = "NODE_NOT_IN_TURN"
    REVIEW_NOT_ALLOWED = "REVIEW_NOT_ALLOWED"
    NO_PERSISTED_REVIEW_CANDIDATES = "NO_PERSISTED_REVIEW_CANDIDATES"
    SELECTED_CANDIDATE_REQUIRED = "SELECTED_CANDIDATE_REQUIRED"
    REVIEW_CANDIDATE_NOT_FOUND = "REVIEW_CANDIDATE_NOT_FOUND"
    REVIEW_CANDIDATE_NOT_VALID = "REVIEW_CANDIDATE_NOT_VALID"
    CORRECTED_TEXT_REQUIRED = "CORRECTED_TEXT_REQUIRED"
    TURN_ALREADY_FINALIZED = "TURN_ALREADY_FINALIZED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    INVALID_FILTER = "INVALID_FILTER"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"


class ErrorResponse(StrictModel):
    error_code: ErrorCode
    message: str
    turn_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class InputPresentation(StrictModel):
    input_type: Literal["text", "audio"]
    input_source: str
    audio_fingerprint: str | None = None
    speaker_zone: str
    speaker_role: str
    speaker_source: str | None = None
    spectrum_result: SpectrumAnalysisResult | None = None
    la_score: float | None = Field(default=None, ge=0, le=1)
    synthetic_risk: float | None = Field(default=None, ge=0, le=1)
    pa_raw_score: float | None = None
    pa_score: float | None = Field(default=None, ge=0, le=1)
    replay_risk: float | None = Field(default=None, ge=0, le=1)
    trust_score: float | None = Field(default=None, ge=0, le=1)
    input_trust_label: str
    authorization_effect_applied: bool
    asr_raw_text: str
    normalized_text: str
    asr_confidence: float | None = Field(default=None, ge=0, le=1)
    asr_confidence_method: str | None = None
    zone_permission_result: str | None = None
    zone_permission_reasons: list[str] = Field(default_factory=list)
    preliminary_decision: DecisionLabel | None = None
    preliminary_reasons: list[str] = Field(default_factory=list)


class EvidenceDemandItem(StrictModel):
    evidence_type: str
    required: bool
    status: EvidenceDemandStatus
    node_ids: list[str] = Field(default_factory=list)
    retrieval_origin: RetrievalOrigin
    reason: str


class EvidenceDemandPresentation(StrictModel):
    demand_id: str
    turn_id: str
    action: str
    target: str
    risk_level: str
    query_text: str
    required_types: list[str] = Field(default_factory=list)
    optional_types: list[str] = Field(default_factory=list)
    priority: int
    retrieval_scope: str
    demand_items: list[EvidenceDemandItem] = Field(default_factory=list)


class RetrievalCandidate(StrictModel):
    node_id: str
    evidence_type: str
    display_name: str
    sas: float = Field(ge=0, le=1)
    quality_label: str
    source: str
    timestamp: datetime | None
    mandatory: bool
    retrieval_origin: RetrievalOrigin
    security_class: SecurityClass | None = None
    security_rank: int | None = Field(default=None, ge=0, le=3)
    hnsw_max_layer: int | None = Field(default=None, ge=0)
    layer_memberships: list[int] = Field(default_factory=list)


class RetrievalSummary(StrictModel):
    top_k: int | None = Field(default=None, ge=1)
    candidate_count: int = Field(ge=0)
    elapsed_ms: float | None = Field(default=None, ge=0)
    index_implementation: str | None = None
    embedding_model: str | None = None
    embedding_dimension: int | None = Field(default=None, gt=0)
    degraded: bool | None = None
    candidates: list[RetrievalCandidate] = Field(default_factory=list)
    mandatory_recall: list[dict[str, Any]] = Field(default_factory=list)
    missing_types: list[str] = Field(default_factory=list)
    index_build_id: str | None = None
    index_config_digest: str | None = None
    node_set_digest: str | None = None
    layering_mode: str | None = None
    security_layer_count: int = Field(default=0, ge=0)
    security_layers: list[LayerIndexStatus] = Field(default_factory=list)
    per_layer_node_count: dict[int, int] = Field(default_factory=dict)
    mapping_coverage: float | None = Field(default=None, ge=0, le=1)
    unclassified_types: list[str] = Field(default_factory=list)
    security_layer_navigation: SecurityLayerNavigation | None = None
    retrieval_visualization_path: list[RetrievalVisualizationPath] = Field(
        default_factory=list
    )
    final_top_k_node_ids: list[str] = Field(default_factory=list)
    mandatory_supplemented_node_ids: list[str] = Field(default_factory=list)
    internal_hnsw_trace_available: bool = False
    internal_hnsw_trace_reason: str | None = None
    availability: LayerNavigationAvailability = (
        LayerNavigationAvailability.LEGACY_NOT_RECORDED
    )


class QualityMetricsPresentation(StrictModel):
    ecr: float | None = Field(default=None, ge=0, le=1)
    ecs: float | None = Field(default=None, ge=0, le=1)
    ef: float | None = Field(default=None, ge=0, le=1)
    sas: float | None = Field(default=None, ge=0, le=1)
    eas: float | None = Field(default=None, ge=0, le=1)
    evidence_pair_count: int | None = Field(default=None, ge=0)
    conflict_pair_count: int | None = Field(default=None, ge=0)
    eas_weight_profile: str | None = None
    eas_weight_source: str | None = None
    eas_weights: dict[str, float] | None = None
    evidence_alignment_route: str | None = None
    availability: dict[str, Availability] = Field(default_factory=dict)


class EvidencePresentation(StrictModel):
    semantic_frame: SemanticFrame
    evidence_demand: EvidenceDemandPresentation
    evidence_subgraph: EvidenceSubgraph | None = None
    conflicts: list[Any] = Field(default_factory=list)
    corrected_weights: dict[str, float] = Field(default_factory=dict)
    decision_confidence: float | None = Field(default=None, ge=0, le=1)
    quality_metrics: QualityMetricsPresentation
    memory: "MemoryPresentation" = Field(default_factory=lambda: MemoryPresentation())
    causal: "CausalPresentation" = Field(default_factory=lambda: CausalPresentation())


class MemoryPresentation(StrictModel):
    availability: str = "LEGACY_NOT_RECORDED"
    layered_graph: dict[str, Any] = Field(default_factory=dict)
    relation_edges: list[MemoryRelationEdge] = Field(default_factory=list)
    degree_statistics: MemoryDegreeStatistics = Field(default_factory=MemoryDegreeStatistics)
    propagation_steps: list[MemoryPropagationStep] = Field(default_factory=list)
    node_confidences: dict[str, dict[str, float | None]] = Field(default_factory=dict)
    node_layers: list[MemoryNodeLayer] = Field(default_factory=list)
    alpha: float | None = Field(default=None, gt=0, lt=1)
    alpha_source: str | None = None
    configuration_version: str | None = None
    warnings: list[str] = Field(default_factory=list)


class CausalPresentation(StrictModel):
    availability: str = "LEGACY_NOT_RECORDED"
    model_build_id: str | None = None
    history_sample_count: int = Field(default=0, ge=0)
    dag_edges: list[CausalEdge] = Field(default_factory=list)
    parent_state_signatures: list[ParentStateStatistics] = Field(default_factory=list)
    prior_components: list[CausalPriorComponents] = Field(default_factory=list)
    node_weights: list[CausalNodeWeight] = Field(default_factory=list)
    entropy: float | None = Field(default=None, ge=0)
    decision_confidence: float | None = Field(default=None, ge=0, le=1)
    confidence_status: str = "LEGACY_NOT_RECORDED"
    insufficiency_reason: str | None = None


class GateCheckPresentation(StrictModel):
    rule_id: str
    rule_name: str
    hit: bool
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)
    severity: Literal["INFO", "WARNING", "HIGH"]
    observed: dict[str, Any] = Field(default_factory=dict)


class GateResultPresentation(StrictModel):
    blocked: bool
    overall_status: Literal["PASSED", "BLOCKED"]
    checks: list[GateCheckPresentation] = Field(default_factory=list)


class ScoreResultPresentation(StrictModel):
    semantic_clarity: float | None = Field(default=None, ge=0, le=1)
    evidence_support: float | None = Field(default=None, ge=0, le=1)
    evidence_trust: float | None = Field(default=None, ge=0, le=1)
    jailbreak_suppression: float | None = Field(default=None, ge=0, le=1)
    scene_necessity: float | None = Field(default=None, ge=0, le=1)
    safety_score: float = Field(ge=0, le=1)
    semantic_confidence: float | None = Field(default=None, ge=0, le=1)
    ambiguity_penalty: float | None = Field(default=None, ge=0, le=1)
    semantic_ambiguity_beta: float | None = Field(default=None, ge=0)
    beta_source: str | None = None
    validated_evidence_count: int = Field(default=0, ge=0)
    validated_trust_values: list[dict[str, Any]] = Field(default_factory=list)
    trust_formula: str | None = None
    trust_value_source: str | None = None


class ValidationResultPresentation(StrictModel):
    grounding_failures: list[Any] = Field(default_factory=list)
    conflicts: list[Any] = Field(default_factory=list)
    jailbreak_flag: bool
    jailbreak_risk: float = Field(ge=0, le=1)
    jailbreak_risk_base: float | None = Field(default=None, ge=0, le=1)
    jailbreak_risk_severity: int | None = Field(default=None, ge=0, le=3)


class DecisionResultPresentation(StrictModel):
    initial_decision: DecisionLabel
    score_decision: DecisionLabel
    final_decision: DecisionLabel
    decision_sources: list[DecisionSource] = Field(default_factory=list)
    decision_merge_reason: str
    safety_score: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)
    explanation: str
    review_required: bool
    execution_allowed: bool
    decision_explanation: DecisionExplanation | None = None


class ReviewPresentation(StrictModel):
    status: str
    original_instruction: str
    ambiguity_field: str | None = None
    ambiguity_value: Any = None
    candidate_interpretations: list[ReviewCandidateInterpretation] = Field(default_factory=list)
    candidate_availability: str = "LEGACY_NOT_RECORDED"
    recommended_recovery: RecoveryRecommendation | None = None
    review_question: str | None = None
    generation_metadata: InterpreterGenerationMetadata | None = None
    supporting_evidence: list[str] = Field(default_factory=list)
    conflicting_evidence: list[str] = Field(default_factory=list)
    user_action: ReviewAction | None = None
    corrected_text: str | None = None
    review_result: DecisionLabel | None = None
    review_turn_id: str | None = None


class AuthorizationPresentation(StrictModel):
    token_issued: bool
    token_status: str | None = None
    expires_at: datetime | None = None
    consumed: bool
    execution_allowed: bool


class ExecutionPresentation(StrictModel):
    adapter: str | None = None
    request_status: str
    execution_status: str
    action: str | None = None
    target: str | None = None
    result: str | None = None
    failure_reason: str | None = None
    created_at: datetime | None = None


class TurnAuditPresentation(StrictModel):
    audit_id: str
    record_hash: str
    previous_hash: str
    audit_chain_valid: bool
    workflow_chain_valid: bool
    workflow_event_count: int = Field(ge=0)


class TurnPresentationResponse(StrictModel):
    turn_id: str
    created_at: datetime
    updated_at: datetime
    current_stage: str
    processing_status: str
    voice_trust_mode: Literal["enforce", "observe"]
    input: InputPresentation
    semantic_frame: SemanticFrame
    evidence_demand: EvidenceDemandPresentation
    retrieval_summary: RetrievalSummary
    evidence: EvidencePresentation
    gate_result: GateResultPresentation
    score_result: ScoreResultPresentation
    validation_result: ValidationResultPresentation
    decision_result: DecisionResultPresentation
    review: ReviewPresentation
    authorization: AuthorizationPresentation
    execution: ExecutionPresentation
    audit: TurnAuditPresentation


class EvidenceNodeDetail(StrictModel):
    turn_id: str
    node_id: str
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
    semantic_similarity: float = Field(ge=0, le=1)
    mandatory: bool
    quality_label: str
    integrity_hash: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    incoming_edges: list[EvidenceEdge] = Field(default_factory=list)
    outgoing_edges: list[EvidenceEdge] = Field(default_factory=list)
    security_class: SecurityClass | None = None
    security_rank: int | None = Field(default=None, ge=0, le=3)
    base_level: int | None = Field(default=None, ge=0)
    safety_adjustment: int | None = Field(default=None, ge=0)
    hnsw_max_layer: int | None = Field(default=None, ge=0)
    layer_memberships: list[int] = Field(default_factory=list)
    classification_source: str | None = None
    formula_source: str | None = None
    initial_memory_confidence: float | None = Field(default=None, ge=0)
    memory_initial_confidence: float | None = Field(default=None, ge=0)
    final_memory_confidence: float | None = Field(default=None, ge=0)
    canonicalization_source: str | None = None
    merged_node_sources: list[str] = Field(default_factory=list)
    field_resolution: dict[str, str] = Field(default_factory=dict)
    canonicalization_warnings: list[str] = Field(default_factory=list)
    incoming_propagation: list[MemoryPropagationStep] = Field(default_factory=list)
    causal_parents: list[str] = Field(default_factory=list)
    prior_probability: float | None = Field(default=None, ge=0, le=1)
    causal_support: float | None = Field(default=None, ge=0, le=1)
    corrected_weight: float | None = Field(default=None, ge=0, le=1)


class ReviewSubmission(StrictModel):
    model_config = ConfigDict(
        extra="forbid",
        protected_namespaces=(),
        json_schema_extra={
            "allOf": [
                {
                    "if": {
                        "properties": {"action": {"const": "CONFIRM"}},
                        "required": ["action"],
                    },
                    "then": {"required": ["selected_candidate_id"]},
                }
            ]
        },
    )
    action: ReviewAction
    corrected_text: str | None = Field(default=None, max_length=2048)
    selected_candidate_id: str | None = Field(default=None, max_length=128)

    @model_validator(mode="after")
    def validate_action_payload(self) -> "ReviewSubmission":
        if self.action == ReviewAction.CORRECT:
            if not (self.corrected_text or "").strip():
                raise ValueError("CORRECTED_TEXT_REQUIRED")
            if "selected_candidate_id" in self.model_fields_set:
                raise ValueError("CORRECT 不接受 selected_candidate_id")
        elif self.action == ReviewAction.CONFIRM:
            if "corrected_text" in self.model_fields_set:
                raise ValueError("CONFIRM 不接受 corrected_text")
            if not (self.selected_candidate_id or "").strip():
                raise ValueError("SELECTED_CANDIDATE_REQUIRED")
        elif self.model_fields_set & {"corrected_text", "selected_candidate_id"}:
            raise ValueError("CANCEL 不接受 corrected_text 或 selected_candidate_id")
        return self


class ReviewSubmissionResponse(StrictModel):
    original_turn_id: str
    review_turn_id: str
    user_action: ReviewAction
    new_decision: DecisionLabel
    token_issued: bool
    execution_status: str
    audit_id: str
    accepted: bool
    message: str
    root_turn_id: str
    related_turn_id: str
    action: ReviewAction
    reason: str
    workflow_status: TurnWorkflowStatus
    decision: DecisionResult
    review_question: str | None = None
    command_result: TextCommandResponse | None = None


class AuditListItem(StrictModel):
    audit_id: str
    turn_id: str
    created_at: datetime
    instruction_summary: str
    initial_decision: DecisionLabel
    original_decision: DecisionLabel
    final_decision: DecisionResult
    execution_status: str
    semantic_frame: SemanticFrame


class AuditListResponse(StrictModel):
    items: list[AuditListItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)


class OriginalDecisionAuditView(StrictModel):
    audit_id: str
    score_decision: DecisionLabel
    final_decision: DecisionLabel
    record_hash: str


class EffectiveOutcomeAuditView(StrictModel):
    final_decision: DecisionLabel
    source: DecisionSource
    review_action: ReviewAction
    terminal_audit_id: str
    terminal_record_hash: str
    created_at: datetime
    token_issued: Literal[False] = False
    execution_allowed: Literal[False] = False


class AuditDetailResponse(StrictModel):
    audit_id: str
    turn_id: str
    created_at: datetime
    input_summary: InputPresentation
    voice_trust: dict[str, Any]
    transcription: TranscriptionResult
    semantic_frame: SemanticFrame
    evidence_demand: EvidenceDemandPresentation
    retrieval_summary: RetrievalSummary
    mandatory_recall: list[dict[str, Any]] = Field(default_factory=list)
    evidence_graph_summary: dict[str, Any]
    quality_metrics: QualityMetricsPresentation
    memory: MemoryPresentation = Field(default_factory=MemoryPresentation)
    causal: CausalPresentation = Field(default_factory=CausalPresentation)
    validation_result: ValidationResultPresentation
    gate_result: GateResultPresentation
    score_factors: ScoreResultPresentation
    initial_decision: DecisionLabel
    original_decision: OriginalDecisionAuditView
    effective_outcome: EffectiveOutcomeAuditView | None = None
    review_process: ReviewPresentation
    final_decision: DecisionResultPresentation
    decision_explanation: DecisionExplanation | None = None
    generation_metadata: InterpreterGenerationMetadata | None = None
    authorization_status: AuthorizationPresentation
    execution_status: ExecutionPresentation
    workflow_events: list[WorkflowEvent] = Field(default_factory=list)
    previous_hash: str
    record_hash: str
    audit_chain_valid: bool
    workflow_chain_valid: bool


class AuditVerificationResponse(StrictModel):
    audit_id: str
    record_hash_valid: bool
    previous_link_valid: bool
    audit_chain_valid: bool
    workflow_chain_valid: bool
    terminal_audit_id: str | None = None
    terminal_record_hash_valid: bool | None = None
    terminal_previous_link_valid: bool | None = None
    relationship_valid: bool = True
    merge_decision_valid: bool = True
    effective_outcome_valid: bool = True
    failure_reason: str | None = None


class TimelineItem(StrictModel):
    sequence: int = Field(ge=1)
    stage: str
    timestamp: datetime
    status: str
    summary: str
    turn_id: str | None = None
    event_id: str | None = None
    audit_id: str | None = None
