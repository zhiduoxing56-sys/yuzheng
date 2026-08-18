from __future__ import annotations

from typing import Any

import pytest

from app.models.schemas import (
    EvidenceNode,
    EvidenceStatus,
    SemanticFrame,
    SemanticIntent,
    utc_now,
)
from app.services.bayesian_diagnostic import BayesianDiagnosticService


def _intent(intent_id: str, *, mode: str | None = None, direction: str | None = None) -> SemanticIntent:
    return SemanticIntent(
        clause_index=0,
        clause_text=intent_id,
        intent_id=intent_id,
        action="测试动作",
        target="测试对象",
        mode=mode,
        direction=direction,
        semantic_confidence=1.0,
        ambiguity_score=0.0,
    )


def _frame(intent: SemanticIntent, turn_id: str = "TURN_BAYES") -> SemanticFrame:
    return SemanticFrame(
        turn_id=turn_id,
        raw_text=intent.clause_text,
        normalized_text=intent.clause_text,
        semantic_confidence=1.0,
        ambiguity_score=0.0,
        semantic_status="OK",
        intents=[intent],
    )


def _node(evidence_type: str, value: Any) -> EvidenceNode:
    now = utc_now()
    return EvidenceNode(
        evidence_type=evidence_type,
        layer="PHYSICAL",
        source="TEST",
        value=value,
        timestamp=now,
        expires_at=None,
        freshness=1.0,
        consistency=1.0,
        availability=1.0,
        quality_label=EvidenceStatus.VALID,
        integrity_hash=f"hash-{evidence_type}",
    )


CASES = [
    (
        _intent("HEADLIGHT_SET_MODE", mode="OFF"),
        [
            _node("ENVIRONMENT_CONDITIONS", {"ambient_illumination": 5, "visibility": 60}),
            _node("VEHICLE_SPEED", 80),
        ],
        [
            _node("ENVIRONMENT_CONDITIONS", {"ambient_illumination": 500, "visibility": 1000}),
            _node("VEHICLE_SPEED", 0),
        ],
    ),
    (
        _intent("WIPER_SET_MODE", mode="OFF"),
        [
            _node("ENVIRONMENT_CONDITIONS", {"weather": "HEAVY_RAIN", "visibility": 50}),
            _node("VEHICLE_SPEED", 90),
        ],
        [
            _node("ENVIRONMENT_CONDITIONS", {"weather": "CLEAR", "visibility": 1000}),
            _node("VEHICLE_SPEED", 0),
        ],
    ),
    (
        _intent("AUTO_PARK_ENABLE"),
        [
            _node("VEHICLE_SPEED", 20),
            _node("GEAR_STATE", {"current_gear": "N"}),
            _node("SURROUNDING_OBJECT_STATE", {"objects": [{"exists": True, "distance": 1}]}),
            _node("FREE_SPACE_STATE", {"available": False}),
            _node("SYSTEM_MODE", {"safety_constraint": "DISABLED"}),
        ],
        [
            _node("VEHICLE_SPEED", 0),
            _node("GEAR_STATE", {"current_gear": "P"}),
            _node("SURROUNDING_OBJECT_STATE", {"objects": []}),
            _node("FREE_SPACE_STATE", {"available": True}),
            _node("SYSTEM_MODE", {"safety_constraint": "ENABLED"}),
        ],
    ),
    (
        _intent("LANE_CHANGE", direction="LEFT"),
        [
            _node("VEHICLE_SPEED", 110),
            _node("SURROUNDING_OBJECT_STATE", {"objects": [{"exists": True, "region": "REAR_LEFT", "distance": 1.5, "risk_level": "HIGH"}]}),
            _node("LANE_STATE", {"target_lane_available": False}),
            _node("ROAD_FRICTION_STATE", {"road_condition": "ICY"}),
        ],
        [
            _node("VEHICLE_SPEED", 30),
            _node("SURROUNDING_OBJECT_STATE", {"objects": []}),
            _node("LANE_STATE", {"target_lane_available": True}),
            _node("ROAD_FRICTION_STATE", {"road_condition": "DRY"}),
        ],
    ),
]


@pytest.mark.parametrize(("intent", "dangerous", "safe"), CASES)
def test_four_profiles_return_numeric_monotonic_risk(
    intent: SemanticIntent,
    dangerous: list[EvidenceNode],
    safe: list[EvidenceNode],
) -> None:
    service = BayesianDiagnosticService()
    dangerous_result = service.evaluate("TURN_DANGER", _frame(intent, "TURN_DANGER"), dangerous)
    safe_result = service.evaluate("TURN_SAFE", _frame(intent, "TURN_SAFE"), safe)

    dangerous_item = dangerous_result.diagnostics[0]
    safe_item = safe_result.diagnostics[0]
    assert dangerous_item.supported is True
    assert dangerous_item.estimate_mode == "FULL_EVIDENCE"
    assert dangerous_item.risk_probability is not None
    assert dangerous_item.safe_probability is not None
    assert dangerous_item.risk_probability + dangerous_item.safe_probability == pytest.approx(1.0)
    assert safe_item.risk_probability is not None
    assert dangerous_item.risk_probability > safe_item.risk_probability
    assert dangerous_result.display_only is True
    assert dangerous_result.affects_decision is False
    assert dangerous_result.calculation_stage == "POST_DECISION_READ_ONLY"


def test_missing_evidence_uses_explicit_prior_but_still_returns_number() -> None:
    intent = _intent("LANE_CHANGE", direction="RIGHT")
    result = BayesianDiagnosticService().evaluate("TURN_PRIOR", _frame(intent, "TURN_PRIOR"), [])
    item = result.diagnostics[0]

    assert item.supported is True
    assert item.estimate_mode == "PARTIAL_PRIOR"
    assert item.risk_probability is not None
    assert item.safe_probability is not None
    assert item.missing_evidence_types == [
        "SURROUNDING_OBJECT_STATE",
        "VEHICLE_SPEED",
        "LANE_STATE",
        "ROAD_FRICTION_STATE",
    ]
    assert all(input_item.used_prior for input_item in item.evidence_inputs)


def test_unconfigured_intent_is_explicitly_unsupported() -> None:
    intent = _intent("MUSIC_PLAY")
    item = BayesianDiagnosticService().evaluate("TURN_OTHER", _frame(intent), []).diagnostics[0]

    assert item.supported is False
    assert item.estimate_mode == "UNSUPPORTED"
    assert item.risk_probability is None

