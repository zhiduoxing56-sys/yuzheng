from __future__ import annotations

from app.models.schemas import (
    DecisionLabel,
    ReviewAction,
    ReviewRequest,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleStatePatch,
)


def _multi_intent_command(pipeline):
    return pipeline.process_text(
        TextCommandRequest(
            text="打开车门并打开车窗",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(
                vehicle_speed=0,
                gear_position="P",
                door_state="CLOSED",
                window_state="CLOSED",
            ),
            subject_role="driver",
            subject_zone="driver",
            subject_source="scenario_test",
            zone_source="scenario_test",
        ),
    )


def test_sys_003_multi_intent_blocks_at_semantic_stage_without_authorization_or_execution(
    pipeline,
) -> None:
    result = _multi_intent_command(pipeline)

    assert result.semantic_frame.raw_text == "打开车门并打开车窗"
    assert result.semantic_frame.semantic_status == "OK"
    assert [item.intent_id for item in result.semantic_frame.intents] == [
        "DOOR_OPEN",
        "WINDOW_OPEN",
    ]
    assert [item.clause_index for item in result.semantic_frame.intents] == [0, 1]
    assert [item.intent_id for item in result.evidence_demand.intent_demands] == [
        "DOOR_OPEN",
        "WINDOW_OPEN",
    ]
    assert all(
        item.retrieval_scope == "control_evidence"
        for item in result.evidence_demand.intent_demands
    )
    assert result.safety_gate.blocked is False
    assert result.decision.gate_blocked is False
    assert result.decision.final_decision == DecisionLabel.REVIEW
    assert result.decision.authorization_token is None
    assert len(result.interpreter_result.candidate_interpretations) == 2
    assert result.interpreter_result.candidate_availability == "AVAILABLE"
    assert result.interpreter_result.validation_result["semantic_reason_codes"] == [
        "MULTIPLE_CONTROL_INTENTS"
    ]
    assert result.interpreter_result.validation_result["multi_intent_diagnostic"] == {
        "reason_code": "MULTIPLE_CONTROL_INTENTS",
        "detected_intent_count": 2,
        "unresolved_clause_count": 0,
    }
    assert result.interpreter_result.review_question == (
        "检测到多个独立车控意图，请明确纠正为一个单独指令。"
    )

    stored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert stored is not None
    assert stored.semantic_frame.raw_text == "打开车门并打开车窗"
    assert [item.intent_id for item in stored.semantic_frame.intents] == [
        "DOOR_OPEN",
        "WINDOW_OPEN",
    ]
    assert stored.interpreter_validation_result["semantic_reason_codes"] == [
        "MULTIPLE_CONTROL_INTENTS"
    ]
    assert "MULTIPLE_CONTROL_INTENTS" in stored.decision_explanation.reason_code_citations
    assert pipeline.workflow_repository.latest_token_for_root(result.turn_id) is None
    assert pipeline.workflow_repository.executions(result.turn_id) == []
    state = pipeline.vehicle.get_state()
    assert state.door_state == "CLOSED"
    assert state.window_state == "CLOSED"


def test_sys_003_confirm_cannot_select_an_action_but_explicit_correction_reenters_pipeline(
    pipeline,
) -> None:
    result = _multi_intent_command(pipeline)
    original_audits = pipeline.audit_repository.records_for_root(result.turn_id)

    confirmation = pipeline.review_service.review(
        result.turn_id,
        ReviewRequest(action=ReviewAction.CONFIRM),
    )
    assert confirmation.accepted is False
    assert confirmation.rejection_code == "NO_PERSISTED_REVIEW_CANDIDATES"
    assert len(pipeline.audit_repository.records_for_root(result.turn_id)) == len(original_audits)
    assert pipeline.workflow_repository.executions(result.turn_id) == []
    assert pipeline.vehicle.get_state().door_state == "CLOSED"
    assert pipeline.vehicle.get_state().window_state == "CLOSED"
