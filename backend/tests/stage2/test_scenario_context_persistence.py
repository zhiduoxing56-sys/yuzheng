from __future__ import annotations

from app.models.schemas import DecisionLabel, TextCommandRequest, VehicleStatePatch


def _open_door(pipeline):
    return pipeline.process_text(
        TextCommandRequest(text="打开车门", speaker_role="driver", speaker_zone="driver")
    )


def test_loaded_conflicting_speed_remains_active_for_following_commands(pipeline) -> None:
    pipeline.load_scenario("conflicting_speed")

    first = _open_door(pipeline)
    second = _open_door(pipeline)

    assert first.decision.final_decision in {DecisionLabel.REVIEW, DecisionLabel.BLOCK}
    assert second.decision.final_decision in {DecisionLabel.REVIEW, DecisionLabel.BLOCK}
    assert any(item["type"] == "VEHICLE_SPEED_SOURCE_CONFLICT" for item in first.audit.conflict_records)
    assert any(item["type"] == "VEHICLE_SPEED_SOURCE_CONFLICT" for item in second.audit.conflict_records)


def test_manual_speed_change_replaces_loaded_speed_conflict(pipeline) -> None:
    pipeline.load_scenario("conflicting_speed")
    pipeline.update_vehicle_state(VehicleStatePatch(vehicle_speed=30, gear_position="D"))

    result = _open_door(pipeline)

    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert not any(item["type"] == "VEHICLE_SPEED_SOURCE_CONFLICT" for item in result.audit.conflict_records)
