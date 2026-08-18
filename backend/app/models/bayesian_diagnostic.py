from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.models.schemas import StrictModel, utc_now


class BayesianEvidenceInput(StrictModel):
    factor_id: str
    label: str
    evidence_type: str
    evidence_field: str | None = None
    source_node_id: str | None = None
    observed_value: Any = None
    normalized_risk: float = Field(ge=0, le=1)
    reliability: float = Field(ge=0, le=1)
    weight: float = Field(gt=0, le=1)
    used_prior: bool = False
    prior_risk: float = Field(ge=0, le=1)


class BayesianFactorContribution(StrictModel):
    factor_id: str
    label: str
    risk_with_factor: float = Field(ge=0, le=1)
    risk_without_factor: float = Field(ge=0, le=1)
    contribution: float = Field(ge=0, le=1)


class BayesianIntentDiagnostic(StrictModel):
    clause_index: int = Field(ge=0)
    intent_id: str
    action: str
    target: str
    supported: bool
    profile_id: str | None = None
    model_version: str | None = None
    risk_probability: float | None = Field(default=None, ge=0, le=1)
    safe_probability: float | None = Field(default=None, ge=0, le=1)
    entropy: float | None = Field(default=None, ge=0, le=1)
    estimate_mode: Literal["FULL_EVIDENCE", "PARTIAL_PRIOR", "UNSUPPORTED"]
    base_risk: float | None = Field(default=None, ge=0, le=1)
    missing_evidence_types: list[str] = Field(default_factory=list)
    evidence_inputs: list[BayesianEvidenceInput] = Field(default_factory=list)
    factor_contributions: list[BayesianFactorContribution] = Field(default_factory=list)
    explanation: str


class BayesianDiagnosticResponse(StrictModel):
    turn_id: str
    display_only: Literal[True] = True
    affects_decision: Literal[False] = False
    calculation_stage: Literal["POST_DECISION_READ_ONLY"] = "POST_DECISION_READ_ONLY"
    formula: Literal[
        "risk=1-(1-base_risk)*product(1-weight_i*normalized_risk_i)"
    ] = "risk=1-(1-base_risk)*product(1-weight_i*normalized_risk_i)"
    generated_at: datetime = Field(default_factory=utc_now)
    diagnostics: list[BayesianIntentDiagnostic] = Field(default_factory=list)

