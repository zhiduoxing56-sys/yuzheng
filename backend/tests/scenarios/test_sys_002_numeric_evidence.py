from __future__ import annotations

import pytest

from app.models.schemas import (
    DecisionLabel,
    EvidenceObservationInput,
    EvidenceStatus,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleStatePatch,
)


def _check(result, rule_id: str):
    return next(check for check in result.safety_gate.checks if check.rule_id == rule_id)


def test_sys_002_string_speed_blocks_before_authorization_and_execution(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(
                vehicle_speed=0,
                gear_position="P",
                door_state="CLOSED",
            ),
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="VEHICLE_SPEED",
                    source="string_sensor",
                    value="20",
                )
            ],
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )

    speed = next(
        node
        for node in result.evidence
        if node.evidence_type == "VEHICLE_SPEED" and node.source == "string_sensor"
    )
    missing = _check(result, "MANDATORY_EVIDENCE_AVAILABLE")
    moving = _check(result, "MOVING_DOOR_OPEN_PROHIBITED")
    trust = next(
        item
        for item in result.decision.score_factors.validated_trust_values
        if item["evidence_type"] == "VEHICLE_SPEED"
    )

    assert any(
        binding.evidence_type == "VEHICLE_SPEED"
        and binding.requirement_level == "REQUIRED"
        and binding.resolution_status == "MISSING"
        and binding.node_id != speed.node_id
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for binding in resolution.bindings
    )
    assert speed.value is None
    assert speed.quality_label == EvidenceStatus.MISSING
    assert speed.metadata["value_validation_reason"] == "INVALID_NUMBER:value"
    assert speed.metadata["received_value_type"] == "str"
    assert speed.metadata["raw_value_retained"] is False
    assert speed.metadata["integrity_payload"]["value"] is None
    assert result.quality_metrics.ecr == pytest.approx(2 / 3, abs=1e-6)
    assert trust["selected_status"] == "MISSING"
    assert trust["trust_value"] == 0
    assert missing.hit is True
    assert set(missing.observed["missing_types"]) == {"VEHICLE_SPEED"}
    assert missing.observed["upstream_value_contract_violations"] == []
    assert moving.hit is False
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert result.decision.authorization_token is None
    assert pipeline.workflow_repository.latest_token_for_root(result.turn_id) is None
    assert pipeline.workflow_repository.executions(result.turn_id) == []
    assert pipeline.vehicle.get_state().door_state == "CLOSED"

    stored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert stored is not None
    audited_speed = next(
        node
        for node in stored.evidence_subgraph.nodes
        if node.evidence_type == "VEHICLE_SPEED" and node.source == "string_sensor"
    )
    assert audited_speed.value is None
    assert audited_speed.quality_label == EvidenceStatus.MISSING
    assert audited_speed.metadata["value_validation_reason"] == "INVALID_NUMBER:value"
    assert stored.final_decision.final_decision == DecisionLabel.BLOCK
    assert stored.final_decision.authorization_token is None


def test_numeric_speed_twenty_remains_valid_and_hits_moving_door_rule(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(
                vehicle_speed=20,
                gear_position="D",
                door_state="CLOSED",
            ),
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )
    required_ids = {
        binding.node_id
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for binding in resolution.bindings
        if binding.requirement_level == "REQUIRED" and binding.node_id is not None
    }
    speed = next(
        node
        for node in result.evidence
        if node.evidence_type == "VEHICLE_SPEED" and node.node_id in required_ids
    )

    assert speed.value == 20
    assert speed.quality_label == EvidenceStatus.VALID
    assert _check(result, "MOVING_DOOR_OPEN_PROHIBITED").hit is True
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert result.decision.authorization_token is None
    assert pipeline.workflow_repository.executions(result.turn_id) == []
    assert pipeline.vehicle.get_state().door_state == "CLOSED"


def test_numeric_front_obstacle_three_remains_valid_and_hits_original_rule(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="速度再快一点",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(
                vehicle_speed=20,
                gear_position="D",
                front_obstacle_distance=3,
            ),
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )
    required_ids = {
        binding.node_id
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for binding in resolution.bindings
        if binding.requirement_level == "REQUIRED" and binding.node_id is not None
    }
    obstacle = next(
        node
        for node in result.evidence
        if node.evidence_type == "SURROUNDING_OBJECT_STATE"
        and node.node_id in required_ids
    )

    assert obstacle.value["front_obstacle_distance"] == 3
    assert obstacle.quality_label == EvidenceStatus.VALID
    assert _check(result, "FRONT_OBSTACLE_ACCELERATION_PROHIBITED").hit is True
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert result.decision.authorization_token is None


def test_string_front_obstacle_cannot_bypass_acceleration_safety(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="速度再快一点",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=20, gear_position="D"),
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="SURROUNDING_OBJECT_STATE",
                    source="string_front_sensor",
                    value={"front_obstacle_distance": "3"},
                )
            ],
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )
    obstacle = next(
        node
        for node in result.evidence
        if node.evidence_type == "SURROUNDING_OBJECT_STATE"
        and node.source == "string_front_sensor"
    )

    assert obstacle.value is None
    assert obstacle.quality_label == EvidenceStatus.MISSING
    assert obstacle.metadata["value_validation_reason"] == (
        "INVALID_NUMBER:value.front_obstacle_distance"
    )
    assert _check(result, "MANDATORY_EVIDENCE_AVAILABLE").hit is True
    assert _check(result, "FRONT_OBSTACLE_ACCELERATION_PROHIBITED").hit is False
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert result.decision.authorization_token is None
    assert pipeline.workflow_repository.latest_token_for_root(result.turn_id) is None
    assert pipeline.workflow_repository.executions(result.turn_id) == []


def test_stationary_numeric_speed_zero_keeps_formal_pass_behavior(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(
                vehicle_speed=0,
                gear_position="P",
                door_state="CLOSED",
            ),
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )

    assert _check(result, "MANDATORY_EVIDENCE_AVAILABLE").hit is False
    assert _check(result, "MOVING_DOOR_OPEN_PROHIBITED").hit is False
    assert result.decision.final_decision == DecisionLabel.PASS
    assert result.decision.authorization_token
    assert pipeline.workflow_repository.executions(result.turn_id) == []
    assert pipeline.vehicle.get_state().door_state == "CLOSED"
