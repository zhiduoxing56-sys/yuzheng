from app.models.schemas import (
    DecisionLabel,
    ReviewAction,
    ReviewRequest,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleStatePatch,
)


def _command(pipeline, text: str, *, speed: float = 0, gear: str = "P"):
    return pipeline.process_text(
        TextCommandRequest(
            text=text,
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(
                vehicle_speed=speed,
                gear_position=gear,
                door_state="CLOSED",
            ),
            subject_role="driver",
            subject_zone="driver",
            subject_source="scenario_test",
            zone_source="scenario_test",
        ),
    )


def test_sys_001_negated_open_door_stays_review_without_authorization_or_execution(
    pipeline,
) -> None:
    result = _command(pipeline, "不要打开车门")

    assert result.semantic_frame.raw_text == "不要打开车门"
    assert result.semantic_frame.semantic_status == "REVIEW"
    assert result.semantic_frame.intents == []
    assert result.semantic_frame.unresolved_clauses == ["不要打开车门"]
    assert result.evidence_demand.intent_demands == []
    assert result.decision.final_decision == DecisionLabel.REVIEW
    assert result.decision.authorization_token is None
    assert result.interpreter_result.candidate_interpretations == []
    assert "MOVING_DOOR_OPEN_PROHIBITED" not in result.safety_gate.hit_rules

    stored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert stored is not None
    assert stored.semantic_frame.raw_text == "不要打开车门"
    assert stored.semantic_frame == result.semantic_frame
    assert pipeline.workflow_repository.latest_token_for_root(result.turn_id) is None
    assert pipeline.workflow_repository.executions(result.turn_id) == []
    assert pipeline.vehicle.get_state().door_state == "CLOSED"

    confirmed = pipeline.review_service.review(
        result.turn_id,
        ReviewRequest(
            action=ReviewAction.CONFIRM,
            selected_candidate_id="CAND_FORBIDDEN_POSITIVE_ACTION",
        ),
    )
    assert confirmed.accepted is False
    assert confirmed.rejection_code == "NO_PERSISTED_REVIEW_CANDIDATES"
    assert confirmed.command_result is None
    assert pipeline.workflow_repository.latest_token_for_root(result.turn_id) is None
    assert pipeline.workflow_repository.executions(result.turn_id) == []
    assert pipeline.vehicle.get_state().door_state == "CLOSED"


def test_sys_001_explicit_positive_correction_reenters_normal_pipeline(pipeline) -> None:
    negated = _command(pipeline, "不要打开车门")

    corrected = pipeline.review_service.review(
        negated.turn_id,
        ReviewRequest(action=ReviewAction.CORRECT, corrected_text="打开车门"),
    )

    assert corrected.accepted is True
    assert corrected.command_result is not None
    assert corrected.command_result.semantic_frame.intents[0].action == "打开"
    assert corrected.command_result.semantic_frame.intents[0].target == "车门"
    assert corrected.command_result.decision.final_decision == DecisionLabel.PASS
    assert corrected.command_result.decision.authorization_token
    assert pipeline.workflow_repository.executions(negated.turn_id) == []
    assert pipeline.vehicle.get_state().door_state == "CLOSED"


def test_sys_001_positive_open_door_authorizes_with_formal_mandatory_facts(pipeline) -> None:
    result = _command(pipeline, "打开车门")

    assert result.semantic_frame.intents[0].action == "打开"
    assert result.semantic_frame.intents[0].target == "车门"
    assert result.semantic_frame.semantic_confidence == 1.0
    assert result.semantic_frame.ambiguity_score == 0.0
    assert result.decision.final_decision == DecisionLabel.PASS
    assert result.decision.authorization_token
    assert result.safety_gate.mandatory_evidence_missing is False
    assert pipeline.workflow_repository.executions(result.turn_id) == []


def test_sys_001_moving_open_door_still_hits_original_safety_gate(pipeline) -> None:
    result = _command(pipeline, "打开车门", speed=80, gear="D")

    assert result.semantic_frame.intents[0].action == "打开"
    assert result.semantic_frame.intents[0].target == "车门"
    assert "MOVING_DOOR_OPEN_PROHIBITED" in result.safety_gate.hit_rules
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert result.decision.authorization_token is None
    assert pipeline.workflow_repository.executions(result.turn_id) == []
    assert pipeline.vehicle.get_state().door_state == "CLOSED"
