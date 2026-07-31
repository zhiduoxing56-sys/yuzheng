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
    required_types: list[str] = Field(default_factory=list)
    optional_types: list[str] = Field(default_factory=list)
    priority: int = Field(default=0, ge=0, le=100)


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


class EvidenceSubgraph(StrictModel):
    graph_id: str = Field(default_factory=lambda: make_id("GRAPH"))
    turn_id: str
    nodes: list[EvidenceNode] = Field(default_factory=list)
    edges: list[EvidenceEdge] = Field(default_factory=list)
    required_types: list[str] = Field(default_factory=list)
    retrieved_types: list[str] = Field(default_factory=list)
    missing_types: list[str] = Field(default_factory=list)
    quality_metrics: dict[str, float] = Field(default_factory=dict)
    corrected_weights: dict[str, float] = Field(default_factory=dict)
    decision_confidence: float = Field(default=0, ge=0, le=1)


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


class SafetyGateResult(StrictModel):
    blocked: bool
    mandatory_evidence_missing: bool = False
    checks: list[GateCheck]
    reasons: list[str]


class DecisionScoreFactors(StrictModel):
    semantic_quality: float = Field(ge=0, le=1)
    evidence_coverage: float | None = Field(default=None, ge=0, le=1)
    evidence_coverage_applicable: bool
    applied_weights: dict[str, float] = Field(default_factory=dict)

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


class VehicleState(StrictModel):
    vehicle_speed: float | None = Field(default=0, ge=0)
    gear_position: str | None = "P"
    door_lock_state: str | None = "UNLOCKED"
    door_state: str | None = "CLOSED"
    occupant_role: str | None = "driver"
    speaker_zone: str | None = "driver"
    vehicle_mode: str | None = "REAL_DRIVING"
    authentication_state: str | None = "AUTHENTICATED"
    ambient_light: float | None = Field(default=100, ge=0)
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
    authentication_state: str | None = None
    ambient_light: float | None = Field(default=None, ge=0)
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


class TextCommandRequest(StrictModel):
    text: str = Field(min_length=1, max_length=500)
    speaker_zone: str = "driver"
    speaker_role: str = "driver"
    state_overrides: VehicleStatePatch | None = None

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
    evidence_subgraph: EvidenceSubgraph | None = None
    evidence_quality_metrics: dict[str, float] = Field(default_factory=dict)
    conflict_records: list[dict[str, Any]] = Field(default_factory=list)
    safety_gate_result: SafetyGateResult
    score_details: DecisionScoreFactors
    final_decision: DecisionResult
    review_process: list[dict[str, Any]] = Field(default_factory=list)
    vehicle_execution_request: dict[str, Any] | None = None
    vehicle_execution_feedback: dict[str, Any] | None = None
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
    safety_gate: SafetyGateResult
    decision: DecisionResult
    audit: AuditRecord


class HealthResponse(StrictModel):
    status: str
    service: str
    stage: str
    database: str
