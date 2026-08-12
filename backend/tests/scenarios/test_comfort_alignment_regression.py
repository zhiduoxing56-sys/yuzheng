from __future__ import annotations

from app.models.schemas import (
    DecisionLabel,
    EvidenceObservationInput,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleStatePatch,
)


def _run(pipeline, text: str, **state):
    return pipeline.process_text(
        TextCommandRequest(
            text=text,
            speaker_role="driver",
            speaker_zone="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(**state),
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )


def test_unregistered_air_conditioning_command_follows_frozen_review_boundary(pipeline) -> None:
    result = _run(pipeline, "帮我打开空调")

    assert result.semantic_frame.semantic_status == "REVIEW"
    assert result.semantic_frame.intents == []
    assert result.evidence_demand.intent_demands == []
    assert result.quality_metrics.evidence_coverage_applicable is False
    assert result.quality_metrics.evidence_alignment_route == "EVIDENCE_PASS"
    assert result.safety_gate.blocked is False
    assert result.decision.score_decision == DecisionLabel.REVIEW
    assert result.decision.final_decision == DecisionLabel.REVIEW


def test_moving_air_conditioning_command_is_normally_allowed(pipeline) -> None:
    result = _run(
        pipeline,
        "帮我打开空调",
        vehicle_speed=60,
        gear_position="D",
        vehicle_mode="REAL_DRIVING",
    )

    assert result.semantic_frame.intents == []
    assert result.evidence_demand.intent_demands == []
    assert result.safety_gate.blocked is False
    assert result.decision.score_decision == DecisionLabel.REVIEW
    assert result.decision.final_decision == DecisionLabel.REVIEW


def test_vague_open_command_still_requires_review(pipeline) -> None:
    result = _run(pipeline, "把那个打开")

    assert result.semantic_frame.intents == []
    assert result.retrieval_scopes == []
    assert result.decision.final_decision == DecisionLabel.REVIEW


def test_dense_fog_front_defog_off_is_blocked_by_separate_safety_rule(pipeline) -> None:
    result = _run(
        pipeline,
        "帮我关闭前挡风除雾",
        weather="DENSE_FOG",
        vehicle_speed=40,
        gear_position="D",
    )

    assert result.semantic_frame.intents[0].action == "关闭"
    assert result.semantic_frame.intents[0].target == "前挡风除雾"
    assert result.semantic_frame.intents[0].risk_level == "R3"
    assert set(result.evidence_demand.intent_demands[0].required_types) == {
        "ENVIRONMENT_CONDITIONS",
        "VEHICLE_SPEED",
    }
    assert "DENSE_FOG_FRONT_DEFOG_OFF_PROHIBITED" in result.safety_gate.hit_rules
    assert result.decision.final_decision == DecisionLabel.BLOCK


def test_sensor_conflict_does_not_pass_comfort_command(pipeline) -> None:
    result = pipeline.process_text(
        TextCommandRequest(
            text="帮我打开空调",
            speaker_role="driver",
            speaker_zone="driver",
        ),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=30, gear_position="D"),
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="VEHICLE_SPEED", source="speed_sensor_a", value=20
                ),
                EvidenceObservationInput(
                    evidence_type="VEHICLE_SPEED", source="speed_sensor_b", value=80
                ),
            ],
            subject_role="driver", subject_zone="driver",
            subject_source="scenario_test", zone_source="scenario_test",
        ),
    )

    assert result.quality_metrics.evidence_alignment_route == "EVIDENCE_PASS"
    assert result.quality_metrics.conflict_count > 0
    assert result.decision.final_decision in {DecisionLabel.REVIEW, DecisionLabel.BLOCK}


def test_unregistered_climate_controls_preserve_frozen_semantic_outputs(
    pipeline,
) -> None:
    frozen = _run(pipeline, "关闭空调")
    assert [item.intent_id for item in frozen.semantic_frame.intents] == ["DEFROST_OFF"]

    for text in ("调节温度", "调高风量"):
        result = _run(pipeline, text)
        assert result.semantic_frame.semantic_status == "REVIEW"
        assert result.semantic_frame.intents == []
        assert result.evidence_demand.intent_demands == []
