from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
SCENARIOS = yaml.safe_load((ROOT / "config" / "demo_scenarios.yaml").read_text(encoding="utf-8"))["scenarios"]


def test_all_formal_scenarios_share_the_single_contract_shape() -> None:
    required = {
        "scenario_id", "name", "input_text", "state", "expected_semantic_units",
        "expected_intent_id", "expected_slots", "expected_runtime_identity",
        "expected_required_evidence", "expected_hit_rules", "required_reason_codes",
        "forbidden_reason_codes", "expected_decision", "expected_actionable",
        "expected_token", "expected_execution",
    }
    assert len(SCENARIOS) == 23
    assert set(SCENARIOS) == {item["scenario_id"] for item in SCENARIOS.values()}
    assert all(required <= set(item) for item in SCENARIOS.values())


def test_contaminated_scenarios_have_distinct_semantic_contracts() -> None:
    moving = SCENARIOS["moving_open_door"]
    ambiguous = SCENARIOS["ambiguous_command"]
    assert moving["input_text"] == "打开左前车门"
    assert moving["expected_slots"] == {"area": "LEFT_FRONT"}
    assert "AREA_AMBIGUOUS" in moving["forbidden_reason_codes"]
    assert ambiguous["input_text"] == "打开车门"
    assert ambiguous["expected_hit_rules"] == ["AREA_AMBIGUOUS"]
    for scenario_id in ("token_reuse", "state_changed_before_execution"):
        assert SCENARIOS[scenario_id]["expected_intent_id"] == "HEADLIGHT_SET_MODE"
        assert SCENARIOS[scenario_id]["expected_slots"] == {"mode": "OFF"}
