import pytest

from app.models.schemas import TextCommandRequest, TrustedRuntimeContext, VehicleStatePatch


def _run(pipeline, text: str):
    return pipeline.process_text(
        TextCommandRequest(text=text, speaker_role="driver", speaker_zone="driver"),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
            subject_role="driver",
            subject_zone="driver",
            subject_source="semantic_ambiguity_closure_test",
            zone_source="semantic_ambiguity_closure_test",
        ),
    )


def _assert_scored_csem_matches_confidence(result) -> None:
    assert result.semantic_frame.semantic_status == "OK"
    assert result.semantic_frame.ambiguity_score == 0
    confidence_by_occurrence = {
        (intent.clause_index, intent.intent_id): intent.semantic_confidence
        for intent in result.semantic_frame.intents
    }
    assert all(intent.ambiguity_score == 0 for intent in result.semantic_frame.intents)
    assert len(result.decision.intent_safety_assessments) == len(result.semantic_frame.intents)
    for assessment in result.decision.intent_safety_assessments:
        confidence = confidence_by_occurrence[
            (assessment.clause_index, assessment.intent_id)
        ]
        assert assessment.score_factors.five_factors["Csem"].value == pytest.approx(
            confidence,
            abs=1e-6,
        )


def test_clear_single_intents_remove_duplicate_semantic_penalty(pipeline) -> None:
    exact = _run(pipeline, "打开右前车门")
    natural = _run(pipeline, "请帮我把右前车门打开一下")

    _assert_scored_csem_matches_confidence(exact)
    _assert_scored_csem_matches_confidence(natural)
    assert exact.semantic_frame.semantic_confidence == 1
    assert exact.decision.score_factors.five_factors["Csem"].value == 1


def test_clear_multi_intent_keeps_order_and_scores_each_confidence(pipeline) -> None:
    result = _run(pipeline, "打开右前车门然后关闭右前车窗")

    _assert_scored_csem_matches_confidence(result)
    assert [intent.intent_id for intent in result.semantic_frame.intents] == [
        "DOOR_OPEN",
        "WINDOW_CLOSE",
    ]
    assert [intent.clause_index for intent in result.semantic_frame.intents] == [0, 1]


@pytest.mark.parametrize(
    ("text", "expected_reasons"),
    [
        ("设置车窗开度", {"MISSING_REQUIRED_VALUE"}),
        ("把那个打开", set()),
        (
            "打开右前车门，然后设置车窗开度",
            {"MULTI_INTENT_INCOMPLETE", "MISSING_REQUIRED_VALUE"},
        ),
    ],
)
def test_incomplete_semantics_still_terminate_before_scoring(
    pipeline,
    text: str,
    expected_reasons: set[str],
) -> None:
    result = _run(pipeline, text)

    assert result.semantic_frame.semantic_status == "REVIEW"
    assert expected_reasons.issubset(result.semantic_frame.review_reasons)
    assert result.decision.score_factors.five_factors == {}
    assert result.decision.score_decision.value == "REVIEW"
    assert result.decision.final_decision.value == "REVIEW"
