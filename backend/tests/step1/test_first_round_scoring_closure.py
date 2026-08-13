import pytest

from app.models.schemas import TextCommandRequest, TrustedRuntimeContext, VehicleStatePatch


def _run(pipeline, text: str, **state):
    return pipeline.process_text(
        TextCommandRequest(text=text, speaker_role="driver", speaker_zone="driver"),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(**state),
            subject_role="driver",
            subject_zone="driver",
            subject_source="first_round_scoring_test",
            zone_source="first_round_scoring_test",
        ),
    )


def test_ordinary_window_control_excludes_scene_necessity(pipeline) -> None:
    result = _run(
        pipeline,
        "关闭右前车窗",
        vehicle_speed=0,
        gear_position="P",
        window_state="OPEN",
    )

    factor = result.decision.score_factors.five_factors["Cnec"]
    assert factor.value is None
    assert factor.applicable is False
    assert factor.actual_weight == 0
    assert factor.contribution == 0
    assert sum(
        item.actual_weight
        for item in result.decision.score_factors.five_factors.values()
    ) == pytest.approx(1, abs=2e-6)
    assert result.decision.score_decision.value == "PASS"
    assert result.decision.final_decision.value == "PASS"


def test_existing_emergency_brake_keeps_scene_necessity_formula(pipeline) -> None:
    result = _run(
        pipeline,
        "正常刹车",
        emergency_flag=True,
        vehicle_speed=60,
        gear_position="D",
        brake_state="REQUIRED",
    )

    factor = result.decision.score_factors.five_factors["Cnec"]
    assert result.semantic_frame.intents[0].intent_id == "BRAKE"
    assert factor.value == 1
    assert factor.applicable is True
    assert factor.configured_weight == 0.025
    assert factor.actual_weight == 0.025
    assert factor.contribution == 0.025
