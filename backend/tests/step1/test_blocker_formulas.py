from __future__ import annotations

import pytest

from app.models.schemas import (
    EvidenceObservationInput,
    EvidenceStatus,
    RuntimeSafetyContext,
    TextCommandRequest,
    TrustedRuntimeContext,
)
from app.services.evidence.trust import evidence_trust_value
from app.services.presentation.assembler import PresentationAssembler


def _gate_check(result, rule_id: str):
    return next(check for check in result.safety_gate.checks if check.rule_id == rule_id)


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (EvidenceStatus.VALID, 1.0),
        (EvidenceStatus.SUSPICIOUS, 0.5),
        (EvidenceStatus.STALE, 0.3),
        (EvidenceStatus.TAMPERED, 0.0),
        (EvidenceStatus.MISSING, 0.0),
    ],
)
def test_pdf_q_mapping_is_single_and_exact(status, expected) -> None:
    assert evidence_trust_value(status) == expected


def test_unavailable_required_fact_cannot_be_forced_stale_by_override(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="向左变道",
        ),
        trusted_context=TrustedRuntimeContext(
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="LANE_STATE",
                    source="simulated_test_source",
                    value={"boundaries": []},
                    age_seconds=31,
                    expires_in_seconds=30,
                ),
            ],
        ),
    )

    observed = _gate_check(result, "MANDATORY_TRUST_THRESHOLD").observed
    values = {item["evidence_type"]: item for item in observed["required_trust_values"]}
    assert observed["required_evidence_count"] == 3
    assert values["LANE_STATE"]["selected_status"] == "MISSING"
    assert values["LANE_STATE"]["trust_value"] == 0.0
    assert values["SURROUNDING_OBJECT_STATE"]["trust_value"] == 1.0
    assert values["VEHICLE_SPEED"]["trust_value"] == 1.0
    assert observed["required_trust_average"] == pytest.approx(2 / 3, abs=1e-6)


def test_csem_beta_and_validated_ctrust_are_persisted(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="向右变道",
        ),
        trusted_context=TrustedRuntimeContext(
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="LANE_STATE",
                    source="simulated_test_source",
                    value={"boundaries": []},
                    integrity_valid=False,
                ),
            ],
        ),
    )

    factors = result.decision.score_factors
    expected_csem = max(
        0.0,
        min(
            1.0,
            factors.semantic_confidence
            * (1 - factors.semantic_ambiguity_beta * factors.ambiguity_penalty),
        ),
    )
    assert factors.semantic_ambiguity_beta == 1.0
    assert factors.beta_source == "ENGINEERING_PROFILE"
    assert factors.five_factors["Csem"].value == round(expected_csem, 6)
    assert factors.validated_evidence_count == 4
    trust = {item["evidence_type"]: item for item in factors.validated_trust_values}
    assert trust["SURROUNDING_OBJECT_STATE"]["trust_value"] == 1.0
    assert trust["LANE_STATE"]["trust_value"] == 0.0
    assert factors.five_factors["Ctrust"].value == 0.75
    assert factors.trust_formula == "Ctrust=mean(Q(status)) over canonical Evalidated"
    assert result.safety_gate.gate_blocked is True
    assert "MANDATORY_EVIDENCE_INTEGRITY" in result.safety_gate.hit_rules
    presentation = PresentationAssembler(pipeline).assemble(result.audit)
    assert presentation.score_result.semantic_ambiguity_beta == 1.0
    assert presentation.score_result.validated_evidence_count == 4
    trust_check = next(
        check
        for check in presentation.gate_result.checks
        if check.rule_id == "MANDATORY_TRUST_THRESHOLD"
    )
    assert trust_check.observed["required_trust_average"] == pytest.approx(
        2 / 3, abs=1e-6
    )


def test_missing_required_is_in_validated_ctrust_and_deduplicated(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="向左变道"))
    factors = result.decision.score_factors

    assert factors.validated_evidence_count == 4
    assert {item["evidence_type"] for item in factors.validated_trust_values} == {
        "SURROUNDING_OBJECT_STATE",
        "LANE_STATE",
        "VEHICLE_SPEED",
        "ENVIRONMENT_CONDITIONS",
    }
    assert {item["trust_value"] for item in factors.validated_trust_values} == {0.0, 1.0}
    assert factors.five_factors["Ctrust"].value == 0.75

    required_nodes = [
        node.model_copy(
            update={
                "metadata": {**node.metadata, "missing_hard_gate": False}
            }
        )
        for node in result.evidence_subgraph.nodes
        if node.evidence_type in result.evidence_demand.intent_demands[0].required_types
    ]
    reevaluated = pipeline.gate_service.evaluate(
        result.semantic_frame,
        result.evidence_demand,
        required_nodes,
        result.evidence_subgraph.intent_evidence_resolutions,
        runtime_safety_context=RuntimeSafetyContext.from_vehicle_state(
            pipeline.get_vehicle_state()
        ),
    )
    assert "MANDATORY_EVIDENCE_AVAILABLE" in reevaluated.hit_rules


def test_optional_missing_is_not_added_to_required_missing_types(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="打开自动泊车",
        ),
        trusted_context=TrustedRuntimeContext(
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="OCCUPANT_STATE",
                    source="simulated_test_source",
                    value=None,
                    available=False,
                ),
            ],
        ),
    )

    missing_check = _gate_check(result, "MANDATORY_EVIDENCE_AVAILABLE")
    assert missing_check.hit is True
    assert missing_check.observed.get("missing_types") == ["FREE_SPACE_STATE"]
    assert "OCCUPANT_STATE" not in missing_check.observed.get(
        "missing_types", []
    )
    required_trust = _gate_check(result, "MANDATORY_TRUST_THRESHOLD").observed
    assert {
        item["evidence_type"] for item in required_trust["required_trust_values"]
    } == {
        "VEHICLE_SPEED",
        "GEAR_STATE",
        "FREE_SPACE_STATE",
        "SURROUNDING_OBJECT_STATE",
    }
