from __future__ import annotations

import pytest

from app.models.schemas import DecisionLabel, TextCommandRequest, VehicleStatePatch


@pytest.mark.parametrize(
    "text",
    [
        "开启雨刮自动模式",
        "雨刮切到自动",
        "把雨刮设成自动模式",
    ],
)
def test_wiper_auto_mode_phrases_resolve_in_wiper_mode_space(pipeline, text: str) -> None:
    """The shared WIPER mode surface, rather than a scenario/text exception, owns 自动模式."""
    pipeline.load_scenario("knowledge_wiper_clear")

    result = pipeline.process_text(TextCommandRequest(text=text))

    assert result.decision.intent_id == "WIPER_SET_MODE"
    assert result.decision.slots["mode"] == "RAIN_SENSOR"
    assert result.decision.final_decision == DecisionLabel.PASS


def test_rain_wiper_scene_is_not_rejected_for_missing_evidence(pipeline) -> None:
    pipeline.load_scenario("knowledge_wiper_rain")

    result = pipeline.process_text(TextCommandRequest(text="开启自动雨刮"))

    demand = result.evidence_demand.intent_demands[0]
    assert demand.intent_id == "WIPER_SET_MODE"
    assert "WIPER_STATE" not in demand.required_types
    assert "WIPER_STATE" in demand.knowledge_required_types
    resolution = result.evidence_subgraph.intent_evidence_resolutions[0]
    assert resolution.missing_knowledge_required_types == []
    assert {hit["applicability_status"] for hit in demand.knowledge_hits} == {"EVALUABLE"}
    assert result.safety_gate.blocked is False
    assert result.decision.final_decision == DecisionLabel.PASS


def test_missing_wiper_state_routes_to_review_not_hard_gate(pipeline) -> None:
    pipeline.load_scenario("knowledge_wiper_rain")
    pipeline.update_vehicle_state(
        VehicleStatePatch(
            wiper_mode=None,
            wiper_intensity=None,
            wiper_frequency=None,
            wiper_wiping=None,
            wiper_error=None,
        )
    )

    result = pipeline.process_text(TextCommandRequest(text="开启自动雨刮"))

    resolution = result.evidence_subgraph.intent_evidence_resolutions[0]
    assert "WIPER_STATE" in resolution.missing_knowledge_required_types
    assert "INSUFFICIENT_CONTEXT" in {
        hit["applicability_status"] for hit in result.evidence_demand.intent_demands[0].knowledge_hits
    }
    assert result.safety_gate.mandatory_evidence_missing is False
    assert result.safety_gate.blocked is False
    assert result.quality_metrics.evidence_alignment_route == "EVIDENCE_PASS"
    assert result.decision.final_decision == DecisionLabel.PASS
    assert "KNOWLEDGE_EVIDENCE_MISSING" not in result.decision.reason_codes


def test_hard_required_evidence_still_blocks(pipeline) -> None:
    pipeline.update_vehicle_state(VehicleStatePatch(vehicle_speed=None))

    result = pipeline.process_text(TextCommandRequest(text="打开左前车门"))

    assert "VEHICLE_SPEED" in result.evidence_demand.intent_demands[0].required_types
    assert result.safety_gate.mandatory_evidence_missing is True
    assert result.decision.final_decision == DecisionLabel.BLOCK
