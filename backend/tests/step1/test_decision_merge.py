from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    DecisionLabel,
    DecisionResult,
    DecisionScoreFactors,
    DecisionSource,
    SafetyGateResult,
)
from app.services.decision.merge import apply_merge_outcome, merge_decision
from scripts.generate_backend_contract import contract_payload
from scripts.verify_step1_truth_checks import scan_final_decision_writes


def _gate(blocked: bool = False) -> SafetyGateResult:
    return SafetyGateResult(
        blocked=blocked,
        gate_blocked=blocked,
        checks=[],
        reasons=["test hard gate"] if blocked else [],
        hit_rules=["TEST_HARD_GATE"] if blocked else [],
    )


@pytest.mark.parametrize(
    ("gate_blocked", "route", "score", "expected"),
    [
        (True, "EVIDENCE_PASS", DecisionLabel.PASS, DecisionLabel.BLOCK),
        (True, "EVIDENCE_REVIEW", DecisionLabel.REVIEW, DecisionLabel.BLOCK),
        (True, "EVIDENCE_BLOCK", DecisionLabel.BLOCK, DecisionLabel.BLOCK),
        (False, "EVIDENCE_BLOCK", DecisionLabel.PASS, DecisionLabel.BLOCK),
        (False, "EVIDENCE_BLOCK", DecisionLabel.REVIEW, DecisionLabel.BLOCK),
        (False, "EVIDENCE_REVIEW", DecisionLabel.PASS, DecisionLabel.REVIEW),
        (False, "EVIDENCE_REVIEW", DecisionLabel.REVIEW, DecisionLabel.REVIEW),
        (False, "EVIDENCE_REVIEW", DecisionLabel.BLOCK, DecisionLabel.BLOCK),
        (False, "EVIDENCE_PASS", DecisionLabel.PASS, DecisionLabel.PASS),
        (False, "EVIDENCE_PASS", DecisionLabel.REVIEW, DecisionLabel.REVIEW),
        (False, "EVIDENCE_PASS", DecisionLabel.BLOCK, DecisionLabel.BLOCK),
    ],
)
def test_conservative_decision_merge_matrix(
    gate_blocked: bool,
    route: str,
    score: DecisionLabel,
    expected: DecisionLabel,
) -> None:
    outcome = merge_decision(_gate(gate_blocked), route, score)  # type: ignore[arg-type]

    assert outcome.final_decision == expected
    assert outcome.decision_sources == (
        DecisionSource.SAFETY_GATE,
        DecisionSource.EVIDENCE_ALIGNMENT,
        DecisionSource.SAFETY_SCORE,
    )
    assert outcome.decision_merge_reason


def _decision_payload() -> dict[str, object]:
    return {
        "turn_id": "TURN_test",
        "decision": "PASS",
        "score_decision": "PASS",
        "final_decision": "REVIEW",
        "decision_sources": [
            "SAFETY_GATE",
            "EVIDENCE_ALIGNMENT",
            "SAFETY_SCORE",
        ],
        "decision_merge_reason": "EVIDENCE_ALIGNMENT required REVIEW",
        "safety_score": 0.9,
        "soft_safety_score": 0.9,
        "gate_blocked": False,
        "score_factors": DecisionScoreFactors(
            semantic_quality=0.9,
            evidence_coverage=None,
            evidence_coverage_applicable=False,
        ).model_dump(mode="json"),
    }


def _pass_decision() -> DecisionResult:
    payload = _decision_payload()
    payload.update(
        final_decision="PASS",
        decision_merge_reason="initial PASS",
    )
    return DecisionResult.model_validate(payload)


def test_decision_and_score_decision_are_identical_in_new_object() -> None:
    decision = DecisionResult.model_validate(_decision_payload())

    assert decision.decision == DecisionLabel.PASS
    assert decision.score_decision == DecisionLabel.PASS
    assert decision.final_decision == DecisionLabel.REVIEW


def test_divergent_decision_and_score_decision_are_rejected() -> None:
    payload = _decision_payload()
    payload["score_decision"] = "BLOCK"

    with pytest.raises(ValidationError, match="decision 与 score_decision 必须一致"):
        DecisionResult.model_validate(payload)


def test_legacy_payload_without_score_decision_uses_decision() -> None:
    payload = _decision_payload()
    payload.pop("score_decision")
    payload.pop("decision_sources")
    payload.pop("decision_merge_reason")

    restored = DecisionResult.model_validate(payload)

    assert restored.score_decision == restored.decision == DecisionLabel.PASS
    assert DecisionSource.LEGACY_COMPATIBILITY in restored.decision_sources


@pytest.mark.parametrize(
    ("route", "score", "expected"),
    [
        ("EVIDENCE_REVIEW", DecisionLabel.PASS, DecisionLabel.REVIEW),
        ("EVIDENCE_BLOCK", DecisionLabel.REVIEW, DecisionLabel.BLOCK),
    ],
)
def test_model_preserves_score_decision_when_evidence_route_is_stricter(
    route: str,
    score: DecisionLabel,
    expected: DecisionLabel,
) -> None:
    outcome = merge_decision(_gate(), route, score)  # type: ignore[arg-type]
    payload = _decision_payload()
    payload.update(
        decision=score,
        score_decision=score,
        final_decision=outcome.final_decision,
        decision_sources=list(outcome.decision_sources),
        decision_merge_reason=outcome.decision_merge_reason,
    )

    result = DecisionResult.model_validate(payload)

    assert result.decision == result.score_decision == score
    assert result.final_decision == expected


def test_hard_gate_preserves_score_decision_and_blocks_final() -> None:
    score = DecisionLabel.PASS
    outcome = merge_decision(_gate(True), "EVIDENCE_PASS", score)
    payload = _decision_payload()
    payload.update(
        decision=score,
        score_decision=score,
        final_decision=outcome.final_decision,
        decision_sources=list(outcome.decision_sources),
        decision_merge_reason=outcome.decision_merge_reason,
        gate_blocked=True,
    )

    result = DecisionResult.model_validate(payload)

    assert result.score_decision == DecisionLabel.PASS
    assert result.final_decision == DecisionLabel.BLOCK


def test_contract_pending_steps_keep_unimplemented_follow_up_work() -> None:
    metadata = contract_payload()

    assert metadata["contract_status"] == "DRAFT"
    assert metadata["frozen"] is False
    assert metadata["pending_steps"] == [
        "step2_hnsw_safety_layer_and_visualization",
        "step5_explanation_and_review_generation",
    ]
    assert metadata["step_status"]["step1_formula_action_alignment"] == "COMPLETE"


def test_contract_decision_sources_come_from_complete_production_enum() -> None:
    metadata = contract_payload()

    assert metadata["enums"]["DecisionSource"] == [
        source.value for source in DecisionSource
    ]
    assert set(metadata["enum_descriptions"]["DecisionSource"]) == {
        source.value for source in DecisionSource
    }
    normal = merge_decision(_gate(), "EVIDENCE_PASS", DecisionLabel.PASS)
    assert DecisionSource.LEGACY_COMPATIBILITY not in normal.decision_sources


@pytest.mark.parametrize(
    ("source", "constraint_level", "expected"),
    [
        (None, "PASS", DecisionLabel.PASS),
        (DecisionSource.RUNTIME_CAPABILITY, "BLOCK", DecisionLabel.BLOCK),
        (DecisionSource.VOICE_TRUST, "REVIEW", DecisionLabel.REVIEW),
        (DecisionSource.VOICE_TRUST, "BLOCK", DecisionLabel.BLOCK),
        (DecisionSource.ZONE_PERMISSION, "REVIEW", DecisionLabel.REVIEW),
        (DecisionSource.ZONE_PERMISSION, "BLOCK", DecisionLabel.BLOCK),
    ],
)
def test_runtime_voice_zone_constraints_use_one_merge_entry(
    source: DecisionSource | None,
    constraint_level: str,
    expected: DecisionLabel,
) -> None:
    review = [source] if source is not None and constraint_level == "REVIEW" else []
    block = [source] if source is not None and constraint_level == "BLOCK" else []
    merged = merge_decision(
        _gate(),
        "EVIDENCE_PASS",
        DecisionLabel.PASS,
        review_constraints=review,
        block_constraints=block,
    )
    result = apply_merge_outcome(_pass_decision(), merged)

    assert result.decision == result.score_decision == DecisionLabel.PASS
    assert result.final_decision == expected
    assert result.authorization_token is None
    if source is not None:
        assert source in result.decision_sources
    assert DecisionSource.LEGACY_COMPATIBILITY not in result.decision_sources


def test_eas_review_plus_runtime_block_and_gate_block_are_conservative() -> None:
    runtime = merge_decision(
        _gate(),
        "EVIDENCE_REVIEW",
        DecisionLabel.PASS,
        block_constraints=[DecisionSource.RUNTIME_CAPABILITY],
    )
    gated = merge_decision(
        _gate(True),
        "EVIDENCE_PASS",
        DecisionLabel.PASS,
        review_constraints=[DecisionSource.VOICE_TRUST],
        block_constraints=[DecisionSource.RUNTIME_CAPABILITY],
    )

    assert runtime.final_decision == DecisionLabel.BLOCK
    assert gated.final_decision == DecisionLabel.BLOCK
    assert DecisionSource.RUNTIME_CAPABILITY in runtime.decision_sources
    assert DecisionSource.VOICE_TRUST in gated.decision_sources
    assert DecisionSource.RUNTIME_CAPABILITY in gated.decision_sources


def _apply_constraints_in_order(
    ordered: list[tuple[DecisionSource, DecisionLabel]],
) -> DecisionResult:
    result = _pass_decision()
    for source, level in ordered:
        merged = merge_decision(
            _gate(),
            "EVIDENCE_PASS",
            result.score_decision,
            review_constraints=[source] if level == DecisionLabel.REVIEW else [],
            block_constraints=[source] if level == DecisionLabel.BLOCK else [],
            prior_final_decision=result.final_decision,
            prior_decision_sources=result.decision_sources,
        )
        result = apply_merge_outcome(result, merged)
    return result


def test_constraint_order_is_stable_and_duplicate_application_is_idempotent() -> None:
    constraints = [
        (DecisionSource.ZONE_PERMISSION, DecisionLabel.REVIEW),
        (DecisionSource.RUNTIME_CAPABILITY, DecisionLabel.BLOCK),
    ]
    forward = _apply_constraints_in_order(constraints)
    reverse = _apply_constraints_in_order(list(reversed(constraints)))
    duplicate = _apply_constraints_in_order(
        [
            (DecisionSource.VOICE_TRUST, DecisionLabel.REVIEW),
            (DecisionSource.VOICE_TRUST, DecisionLabel.REVIEW),
        ]
    )

    expected_sources = [
        DecisionSource.SAFETY_GATE,
        DecisionSource.EVIDENCE_ALIGNMENT,
        DecisionSource.SAFETY_SCORE,
        DecisionSource.RUNTIME_CAPABILITY,
        DecisionSource.ZONE_PERMISSION,
    ]
    assert forward.final_decision == reverse.final_decision == DecisionLabel.BLOCK
    assert forward.decision_sources == reverse.decision_sources == expected_sources
    assert forward.decision == forward.score_decision == DecisionLabel.PASS
    assert reverse.decision == reverse.score_decision == DecisionLabel.PASS
    assert duplicate.final_decision == DecisionLabel.REVIEW
    assert duplicate.decision_sources.count(DecisionSource.VOICE_TRUST) == 1
    assert "RUNTIME_CAPABILITY" in forward.decision_merge_reason
    assert "ZONE_PERMISSION" in forward.decision_merge_reason


def test_apply_merge_outcome_rejects_terminal_field_overrides() -> None:
    merged = merge_decision(_gate(), "EVIDENCE_PASS", DecisionLabel.PASS)

    with pytest.raises(ValueError, match="不得覆盖统一裁决字段"):
        apply_merge_outcome(
            _pass_decision(),
            merged,
            field_updates={"final_decision": DecisionLabel.BLOCK},
        )


def test_ast_scanner_detects_multiline_and_equivalent_writes(tmp_path: Path) -> None:
    sample = tmp_path / "backend" / "app" / "sample.py"
    sample.parent.mkdir(parents=True)
    sample.write_text(
        """
def forbidden(decision, payload):
    decision.model_copy(
        update={
            \"final_decision\": \"BLOCK\",
        }
    )
    decision.final_decision = \"BLOCK\"
    payload.update_copy({\"final_decision\": \"BLOCK\"})
""",
        encoding="utf-8",
    )

    allowed, forbidden = scan_final_decision_writes(tmp_path)

    assert allowed == []
    assert len(forbidden) == 3
    assert {item.operation for item in forbidden} == {
        ".model_copy(...) writes final_decision",
        "direct .final_decision assignment",
        ".update_copy(...) writes final_decision",
    }
    assert all(item.file == "backend/app/sample.py" for item in forbidden)
    assert all(item.function == "forbidden" for item in forbidden)


def test_production_ast_final_decision_scan_has_no_forbidden_writes() -> None:
    allowed, forbidden = scan_final_decision_writes()

    assert forbidden == []
    assert {(item.file, item.function) for item in allowed} == {
        (
            "backend/app/models/schemas.py",
            "DecisionResult.fill_compatibility_fields",
        ),
        (
            "backend/app/services/decision/merge.py",
            "apply_merge_outcome",
        ),
    }
