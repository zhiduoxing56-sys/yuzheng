from app.models.schemas import DecisionLabel, TextCommandRequest, VehicleStatePatch


OPEN_DOOR_REQUIRED = {
    "vehicle_speed",
    "gear_position",
    "door_lock_state",
    "occupant_role",
    "speaker_zone",
    "vehicle_mode",
}


def test_parked_driver_open_door_passes_and_is_audited(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            speaker_zone="driver",
            speaker_role="driver",
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
        )
    )
    evidence = {node.evidence_type: node.value for node in result.evidence}
    assert result.semantic_frame.action == "打开"
    assert result.semantic_frame.target == "车门"
    assert set(result.evidence_demand.required_types) == OPEN_DOOR_REQUIRED
    assert evidence["vehicle_speed"] == 0
    assert evidence["gear_position"] == "P"
    assert result.safety_gate.blocked is False
    assert result.decision.decision == DecisionLabel.PASS
    assert pipeline.audit_repository.get_by_turn(result.turn_id) is not None
    assert pipeline.audit_repository.count() == 1


def test_moving_driver_open_door_hits_hard_gate_and_blocks(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            speaker_zone="driver",
            speaker_role="driver",
            state_overrides=VehicleStatePatch(vehicle_speed=80, gear_position="D"),
        )
    )
    moving_rule = next(
        check for check in result.safety_gate.checks if check.rule_id == "MOVING_DOOR_OPEN_PROHIBITED"
    )
    assert result.semantic_frame.action == "打开"
    assert result.semantic_frame.target == "车门"
    assert set(result.evidence_demand.required_types) == OPEN_DOOR_REQUIRED
    assert moving_rule.hit is True
    assert moving_rule.observed["value"] == 80
    assert "行驶中禁止打开车门" in result.decision.gate_reasons
    assert result.decision.decision == DecisionLabel.BLOCK
    assert result.decision.safety_score == 1.0
    assert pipeline.audit_repository.get_by_turn(result.turn_id).final_decision.decision == DecisionLabel.BLOCK


def test_ambiguous_target_requests_review_and_is_audited(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="把那个打开"))
    assert result.semantic_frame.action == "打开"
    assert result.semantic_frame.target == "unknown"
    assert result.evidence_demand.required_types == []
    assert result.safety_gate.blocked is False
    assert result.decision.decision == DecisionLabel.REVIEW
    assert result.decision.review_question == "您想打开哪个设备？请明确说出车门、车窗、灯光或其他目标。"
    assert pipeline.audit_repository.get_by_turn(result.turn_id) is not None
