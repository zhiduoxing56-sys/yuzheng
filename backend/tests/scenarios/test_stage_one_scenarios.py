from app.models.schemas import (
    DecisionLabel,
    EvidenceStatus,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleStatePatch,
)


OPEN_DOOR_REQUIRED = {
    "VEHICLE_SPEED",
    "GEAR_STATE",
    "SURROUNDING_OBJECT_STATE",
}


def test_parked_driver_open_door_passes_with_formal_mandatory_facts(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )
    evidence = {node.evidence_type: node.value for node in result.evidence}
    assert result.semantic_frame.intents[0].action == "打开"
    assert result.semantic_frame.intents[0].target == "车门"
    assert set(result.evidence_demand.intent_demands[0].required_types) == OPEN_DOOR_REQUIRED
    assert evidence["VEHICLE_SPEED"] == 0
    assert evidence["GEAR_STATE"]["current_gear"] == "P"
    assert result.safety_gate.blocked is False
    assert result.safety_gate.mandatory_evidence_missing is False
    assert result.decision.decision == DecisionLabel.PASS
    assert result.decision.final_decision == DecisionLabel.PASS
    assert result.decision.authorization_token
    assert result.decision.score_factors.evidence_coverage == 1.0
    assert result.decision.score_factors.evidence_coverage_applicable is True
    assert pipeline.audit_repository.get_by_turn(result.turn_id) is not None
    assert pipeline.audit_repository.count() == 1


def test_moving_driver_open_door_hits_hard_gate_and_blocks(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=80, gear_position="D"),
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )
    moving_rule = next(
        check for check in result.safety_gate.checks if check.rule_id == "MOVING_DOOR_OPEN_PROHIBITED"
    )
    assert result.semantic_frame.intents[0].action == "打开"
    assert result.semantic_frame.intents[0].target == "车门"
    assert set(result.evidence_demand.intent_demands[0].required_types) == OPEN_DOOR_REQUIRED
    assert moving_rule.hit is True
    assert moving_rule.observed["value"] == 80
    assert "行驶中禁止打开车门" in result.decision.gate_reasons
    assert result.decision.decision == result.decision.score_decision
    assert result.decision.score_decision == DecisionLabel.PASS
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert result.decision.gate_blocked is True
    assert result.decision.soft_safety_score == 1.0
    assert result.decision.safety_score == 1.0
    assert result.decision.score_factors.five_factors["Cnec"].value is None
    assert result.decision.score_factors.five_factors["Cnec"].applicable is False
    assert result.decision.score_evaluation_mode == "diagnostic_after_gate"
    stored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert stored.final_decision.decision == stored.final_decision.score_decision
    assert stored.final_decision.final_decision == DecisionLabel.BLOCK


def test_ambiguous_target_requests_review_and_is_audited(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="把那个打开"))
    assert result.semantic_frame.intents == []
    assert result.evidence_demand.intent_demands == []
    assert result.safety_gate.blocked is False
    assert result.safety_gate.mandatory_evidence_missing is False
    assert result.decision.decision == DecisionLabel.REVIEW
    assert result.decision.final_decision == DecisionLabel.REVIEW
    # Compatibility scalar remains populated; empty five_factors marks this turn unscored.
    assert result.decision.soft_safety_score == 1.0
    assert result.decision.score_factors.five_factors == {}
    assert result.decision.score_factors.evidence_coverage is None
    assert result.decision.score_factors.evidence_coverage_applicable is False
    assert result.decision.score_factors.applied_weights == {}
    assert result.decision.review_question is not None
    assert pipeline.audit_repository.get_by_turn(result.turn_id) is not None


def test_missing_vehicle_speed_blocks_and_preserves_audit_chain(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=None, gear_position="P"),
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )
    speed_binding = next(
        binding
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for binding in resolution.bindings
        if binding.evidence_type == "VEHICLE_SPEED"
        and binding.requirement_level == "REQUIRED"
    )
    speed_node = next(
        node for node in result.evidence if node.node_id == speed_binding.node_id
    )
    missing_check = next(
        check for check in result.safety_gate.checks if check.rule_id == "MANDATORY_EVIDENCE_AVAILABLE"
    )

    assert speed_node.value is None
    assert speed_node.quality_label == EvidenceStatus.MISSING
    assert result.safety_gate.mandatory_evidence_missing is True
    assert missing_check.hit is True
    assert set(missing_check.observed["missing_types"]) == {"VEHICLE_SPEED"}
    assert "强制证据缺失" in result.safety_gate.reasons
    assert result.decision.gate_blocked is True
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert result.decision.soft_safety_score < 1.0

    saved = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert saved is not None
    assert saved.safety_gate_result.mandatory_evidence_missing is True
    assert saved.final_decision.final_decision == DecisionLabel.BLOCK
    assert pipeline.audit_repository.count() == 1
    assert pipeline.audit_repository.verify_chain() is True
