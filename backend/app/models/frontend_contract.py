from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import Field, model_validator

from app.models.schemas import (
    AdvancedValidationResult,
    DecisionLabel,
    EvidenceEdge,
    EvidenceNode,
    EvidenceQualityMetrics,
    EvidenceSubgraph,
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
    timestamp: datetime
    mandatory: bool
    retrieval_origin: RetrievalOrigin


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


class GateCheckPresentation(StrictModel):
    rule_id: str
    rule_name: str
    hit: bool
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)
    severity: Literal["INFO", "WARNING", "HIGH"]


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


class ValidationResultPresentation(StrictModel):
    grounding_failures: list[Any] = Field(default_factory=list)
    conflicts: list[Any] = Field(default_factory=list)
    jailbreak_flag: bool
    jailbreak_risk: float = Field(ge=0, le=1)
    jailbreak_risk_base: float | None = Field(default=None, ge=0, le=1)
    jailbreak_risk_severity: int | None = Field(default=None, ge=0, le=3)


class DecisionResultPresentation(StrictModel):
    initial_decision: DecisionLabel
    final_decision: DecisionLabel
    safety_score: float = Field(ge=0, le=1)
    reasons: list[str] = Field(default_factory=list)
    explanation: str
    review_required: bool
    execution_allowed: bool


class ReviewPresentation(StrictModel):
    status: str
    original_instruction: str
    ambiguity_field: str | None = None
    ambiguity_value: Any = None
    candidate_interpretations: list[str] = Field(default_factory=list)
    recommended_recovery: str | None = None
    review_question: str | None = None
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
    timestamp: datetime
    expires_at: datetime
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


class ReviewSubmission(StrictModel):
    action: ReviewAction
    corrected_text: str | None = Field(default=None, max_length=2048)

    @model_validator(mode="after")
    def validate_action_payload(self) -> "ReviewSubmission":
        if self.action == ReviewAction.CORRECT:
            if not (self.corrected_text or "").strip():
                raise ValueError("CORRECTED_TEXT_REQUIRED")
        elif "corrected_text" in self.model_fields_set:
            raise ValueError(f"{self.action.value} 不接受 corrected_text")
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
    final_decision: DecisionResult
    execution_status: str
    semantic_frame: SemanticFrame


class AuditListResponse(StrictModel):
    items: list[AuditListItem]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)


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
    validation_result: ValidationResultPresentation
    gate_result: GateResultPresentation
    score_factors: ScoreResultPresentation
    initial_decision: DecisionLabel
    review_process: ReviewPresentation
    final_decision: DecisionResultPresentation
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
