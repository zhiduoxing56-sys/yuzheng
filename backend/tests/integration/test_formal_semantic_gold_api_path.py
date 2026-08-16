from __future__ import annotations

import pytest

from app.services.request_routing.service import RequestRoutingService
from app.services.semantic.orchestrator import SemanticOrchestratorService
from intent_judge_3b_minimal.judge import MinimalCandidateJudge


@pytest.fixture(scope="module")
def formal_semantic_chain():
    """The semantic prefix used by POST /api/command/text, without downstream gates."""
    routing = RequestRoutingService()
    semantic = SemanticOrchestratorService()
    try:
        yield routing, semantic
    finally:
        routing.close()
        semantic._orchestrator.close()  # noqa: SLF001 - owned integration fixture


def _run_formal_semantic_chain(formal_semantic_chain, text: str):
    routing, semantic = formal_semantic_chain
    request_routing = routing.route(text)
    frame = semantic.parse_ordered_units("formal-semantic-gold", text, request_routing.units)
    return request_routing, frame


def _intent_ids(frame) -> list[str]:
    return [item.intent_id for item in frame.intents]


def test_formal_api_gold_h01_h02_h04_h05_h06_uses_one_qwen_and_no_candidate_judge(
    formal_semantic_chain, monkeypatch
) -> None:
    """Production semantic Gold: the exact semantic prefix of the public API."""
    judge_calls = 0

    def prohibited_candidate_judge(*_args, **_kwargs):
        nonlocal judge_calls
        judge_calls += 1
        raise AssertionError("MinimalCandidateJudge is forbidden on the formal API path")

    monkeypatch.setattr(MinimalCandidateJudge, "_stream_chat", prohibited_candidate_judge)

    gold = (
        ("h01", "把车门关好", "DOOR_CLOSE"),
        ("h02", "车门锁一下", "DOOR_LOCK"),
        ("h04", "天窗关闭", "SUNROOF_CLOSE"),
        ("h05", "展开后视镜", "MIRROR_UNFOLD"),
        ("h06", "打开远光灯", "HIGH_BEAM_ON"),
    )
    for case_id, text, expected_intent in gold:
        routing, frame = _run_formal_semantic_chain(formal_semantic_chain, text)
        assert routing.model_call_count == 1, case_id
        assert routing.model_metrics.get("fallback") is not True, case_id
        assert frame.semantic_status == "OK", case_id
        assert _intent_ids(frame) == [expected_intent], case_id

    assert judge_calls == 0


def test_formal_api_preserves_explicit_action_direction(formal_semantic_chain) -> None:
    """Direction safety regressions traverse the exact formal semantic prefix."""
    cases = (
        ("车门锁一下", "DOOR_LOCK", "DOOR_UNLOCK"),
        ("把车门解锁", "DOOR_UNLOCK", "DOOR_LOCK"),
        ("打开车门", "DOOR_OPEN", "DOOR_CLOSE"),
        ("关闭车门", "DOOR_CLOSE", "DOOR_OPEN"),
        ("打开远光灯", "HIGH_BEAM_ON", "HIGH_BEAM_OFF"),
        ("关闭远光灯", "HIGH_BEAM_OFF", "HIGH_BEAM_ON"),
        ("加速", "ACCELERATE", "DECELERATE"),
        ("减速", "DECELERATE", "ACCELERATE"),
    )
    for text, expected_intent, opposite_intent in cases:
        routing, frame = _run_formal_semantic_chain(formal_semantic_chain, text)
        assert routing.model_call_count == 1
        assert frame.semantic_status == "OK"
        assert _intent_ids(frame) == [expected_intent]
        assert opposite_intent not in _intent_ids(frame)


def test_formal_api_gold_h03_window_open_without_area(
    formal_semantic_chain, monkeypatch
) -> None:
    """h03 is accepted through the same formal semantic chain as all other Gold."""
    judge_calls = 0

    def prohibited_candidate_judge(*_args, **_kwargs):
        nonlocal judge_calls
        judge_calls += 1
        raise AssertionError("MinimalCandidateJudge is forbidden on the formal API path")

    monkeypatch.setattr(MinimalCandidateJudge, "_stream_chat", prohibited_candidate_judge)
    routing, frame = _run_formal_semantic_chain(formal_semantic_chain, "把窗户打开")

    assert routing.model_call_count == 1
    assert frame.semantic_status == "OK"
    assert _intent_ids(frame) == ["WINDOW_OPEN"]
    assert judge_calls == 0
