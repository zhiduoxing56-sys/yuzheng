from __future__ import annotations

from app.models.schemas import DecisionLabel, TextCommandRequest, VehicleStatePatch


def test_rain_wiper_scene_is_not_rejected_for_missing_evidence(pipeline) -> None:
    pipeline.load_scenario("knowledge_wiper_rain")

    result = pipeline.process_text(TextCommandRequest(text="开启自动雨刮"))

    demand = result.evidence_demand.intent_demands[0]
    assert demand.intent_id == "WIPER_SET_MODE"
    assert "WIPER_STATE" not in demand.required_types
    assert "WIPER_STATE" in demand.knowledge_required_types
    assert result.safety_gate.blocked is False
    assert result.decision.final_decision != DecisionLabel.BLOCK


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
    assert result.safety_gate.mandatory_evidence_missing is False
    assert result.safety_gate.blocked is False
    assert result.quality_metrics.evidence_alignment_route == "EVIDENCE_REVIEW"
    assert result.decision.final_decision == DecisionLabel.REVIEW
    assert "KNOWLEDGE_EVIDENCE_MISSING" in result.decision.reason_codes


def test_hard_required_evidence_still_blocks(pipeline) -> None:
    pipeline.update_vehicle_state(VehicleStatePatch(vehicle_speed=None))

    result = pipeline.process_text(TextCommandRequest(text="打开左前车门"))

    assert "VEHICLE_SPEED" in result.evidence_demand.intent_demands[0].required_types
    assert result.safety_gate.mandatory_evidence_missing is True
    assert result.decision.final_decision == DecisionLabel.BLOCK
