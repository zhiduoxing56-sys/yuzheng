import math

import pytest

from app.core.config import load_yaml
from app.models.schemas import SemanticFrame
from app.services.validation.advanced import AdvancedValidationService


def _frame() -> SemanticFrame:
    return SemanticFrame(
        turn_id="TURN_JB",
        raw_text="查询车速",
        normalized_text="查询车速",
        action="查询",
        target="速度",
        area="unknown",
        control_domain="驾驶控制",
        semantic_confidence=1.0,
        ambiguity_score=0.0,
        risk_level="R1",
    )


def test_jailbreak_formula_is_zero_without_conflicts() -> None:
    result = AdvancedValidationService(load_yaml("jailbreak_policy.yaml")).validate(
        _frame(), [], []
    )

    assert result.conflict_count == 0
    assert result.max_severity == 0
    assert result.jailbreak_risk_base == 0
    assert result.jailbreak_risk_severity_component == 0
    assert result.jailbreak_risk == 0
    assert result.jailbreak_flag is False


def test_jailbreak_formula_uses_exponential_base_and_report_severity() -> None:
    result = AdvancedValidationService(load_yaml("jailbreak_policy.yaml")).validate(
        _frame(), [],
        [
            {
                "type": "TEST_CONFLICT",
                "severity": 1,
                "node_ids": [],
                "evidence_types": ["exact_type"],
            }
        ],
    )

    assert result.conflict_count == 1
    assert result.max_severity == 1
    assert result.jailbreak_risk_base == pytest.approx(1 - math.exp(-0.5), abs=1e-6)
    assert result.jailbreak_risk_severity_component == pytest.approx(2 / 3, abs=1e-6)
    assert result.jailbreak_risk == result.jailbreak_risk_severity_component
    assert result.jailbreak_flag is True


def test_jailbreak_severity_is_clamped_before_formula() -> None:
    result = AdvancedValidationService(load_yaml("jailbreak_policy.yaml")).validate(
        _frame(), [],
        [{"type": "SEVERE", "severity": 99, "node_ids": [], "evidence_types": []}],
    )

    assert result.max_severity == 3
    assert result.jailbreak_risk_severity_component == 1
    assert result.jailbreak_risk == 1


def test_multiple_light_conflicts_can_make_count_risk_dominant() -> None:
    conflicts = [
        {"type": f"LIGHT_{index}", "severity": 1, "node_ids": [], "evidence_types": []}
        for index in range(4)
    ]
    result = AdvancedValidationService(load_yaml("jailbreak_policy.yaml")).validate(
        _frame(), [], conflicts
    )

    assert result.jailbreak_risk_base == pytest.approx(1 - math.exp(-2), abs=1e-6)
    assert result.jailbreak_risk_base > result.jailbreak_risk_severity_component
    assert result.jailbreak_risk == result.jailbreak_risk_base
    assert 0 <= result.jailbreak_risk <= 1
