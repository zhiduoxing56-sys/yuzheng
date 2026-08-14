from __future__ import annotations

import pytest

from semantic_orchestrator_v2.clause_resolver import OrderedClauseResolver
from semantic_orchestrator_v2.multi_intent_guard import MultiIntentCompletenessGuard
from semantic_orchestrator_v2.orchestrator import SemanticOrchestratorV2


FORMAL_CLAUSES = [
    "打开右前门",
    "关闭左前车窗",
    "打开天窗",
    "打开后备箱",
    "打开近光灯",
]


EXPLICIT_MULTI_ACTION_CASES = [
    ("打开灯并打开天窗", ["打开灯", "打开天窗"]),
    ("把灯打开并把天窗打开", ["把灯打开", "把天窗打开"]),
    ("打开空调和播放音乐", ["打开空调", "播放音乐"]),
    ("打开天窗打开空调", ["打开天窗", "打开空调"]),
    ("播放音乐和打开天窗", ["播放音乐", "打开天窗"]),
    ("关闭前照灯和打开左前车窗", ["关闭前照灯", "打开左前车窗"]),
    ("打开车门和打开后备箱", ["打开车门", "打开后备箱"]),
    ("打开车窗和打开天窗", ["打开车窗", "打开天窗"]),
    ("先打开车窗再打开天窗", ["打开车窗", "打开天窗"]),
    ("打开车窗打开天窗", ["打开车窗", "打开天窗"]),
    ("打开车门并关闭车窗", ["打开车门", "关闭车窗"]),
    ("关闭车门并打开车窗", ["关闭车门", "打开车窗"]),
    ("打开前照灯并关闭车窗", ["打开前照灯", "关闭车窗"]),
    ("关闭前照灯并打开天窗", ["关闭前照灯", "打开天窗"]),
    ("打开雾灯并打开天窗", ["打开雾灯", "打开天窗"]),
    ("打开近光灯并关闭车门", ["打开近光灯", "关闭车门"]),
    ("打开空调并打开蓝牙", ["打开空调", "打开蓝牙"]),
    ("打开蓝牙并关闭空调", ["打开蓝牙", "关闭空调"]),
    ("打开阅读灯并打开天窗", ["打开阅读灯", "打开天窗"]),
    ("关闭屏幕并打开车窗", ["关闭屏幕", "打开车窗"]),
    ("打开香氛并打开天窗", ["打开香氛", "打开天窗"]),
    ("打开车内摄像头并关闭蓝牙", ["打开车内摄像头", "关闭蓝牙"]),
    ("解锁车门然后打开车门", ["解锁车门", "打开车门"]),
    ("关闭车门然后锁定车门", ["关闭车门", "锁定车门"]),
    ("打开后备箱然后关闭前照灯", ["打开后备箱", "关闭前照灯"]),
    ("打开车窗再打开天窗", ["打开车窗", "打开天窗"]),
    ("打开车窗，然后打开天窗", ["打开车窗", "打开天窗"]),
    ("打开车窗；打开天窗", ["打开车窗", "打开天窗"]),
    ("打开车窗。打开天窗", ["打开车窗", "打开天窗"]),
    ("打开车窗同时打开天窗", ["打开车窗", "打开天窗"]),
    ("打开蓝牙接着播放音乐", ["打开蓝牙", "播放音乐"]),
    ("播放音乐以及打开空调", ["播放音乐", "打开空调"]),
    ("打开前照灯，播放音乐", ["打开前照灯", "播放音乐"]),
    ("打开空调播放音乐", ["打开空调", "播放音乐"]),
    ("播放音乐关闭蓝牙", ["播放音乐", "关闭蓝牙"]),
    ("打开车窗并打开天窗然后关闭空调", ["打开车窗", "打开天窗", "关闭空调"]),
    ("播放音乐接着打开蓝牙再关闭空调", ["播放音乐", "打开蓝牙", "关闭空调"]),
    ("打开灯；打开天窗；播放音乐", ["打开灯", "打开天窗", "播放音乐"]),
    ("打开空调同时播放音乐同时打开蓝牙", ["打开空调", "播放音乐", "打开蓝牙"]),
    ("关闭前照灯打开车窗打开天窗", ["关闭前照灯", "打开车窗", "打开天窗"]),
]


@pytest.mark.parametrize(("text", "expected"), EXPLICIT_MULTI_ACTION_CASES)
def test_explicit_complete_actions_split_without_object_registry_validation(
    text: str, expected: list[str]
) -> None:
    resolution = OrderedClauseResolver().resolve(text)

    assert list(resolution.clauses) == expected
    assert resolution.split is True


@pytest.mark.parametrize(
    "text",
    [
        "打开空调",
        "关闭空调",
        "把空调打开",
        "打开车窗和天窗",
        "打开车门和后备箱",
        "关闭车窗和天窗",
        "加速并变道",
    ],
)
def test_single_or_elliptical_actions_do_not_gain_extra_clauses(text: str) -> None:
    resolution = OrderedClauseResolver().resolve(text)

    assert resolution.clauses == (text,)
    assert resolution.split is False


@pytest.mark.parametrize("count", range(1, 6))
def test_punctuation_split_supports_one_to_five_ordered_clauses(count: int) -> None:
    resolution = OrderedClauseResolver().resolve("，".join(FORMAL_CLAUSES[:count]))

    assert list(resolution.clauses) == FORMAL_CLAUSES[:count]
    assert resolution.split is (count > 1)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("打开右前门；关闭左前车窗；打开天窗", FORMAL_CLAUSES[:3]),
        ("打开右前门。关闭左前车窗。打开天窗", FORMAL_CLAUSES[:3]),
        ("打开右前门并关闭左前车窗并打开天窗", FORMAL_CLAUSES[:3]),
        ("打开右前门然后关闭左前车窗然后打开天窗", FORMAL_CLAUSES[:3]),
        ("打开右前门接着关闭左前车窗接着打开天窗", FORMAL_CLAUSES[:3]),
        ("打开右前门，同时关闭左前车窗；接着打开天窗", FORMAL_CLAUSES[:3]),
        ("打开右前门后再关闭左前车窗后重新打开天窗", FORMAL_CLAUSES[:3]),
    ],
)
def test_supported_boundaries_share_one_ordered_split_path(
    text: str, expected: list[str]
) -> None:
    resolution = OrderedClauseResolver().resolve(text)

    assert list(resolution.clauses) == expected
    assert resolution.split is True


def test_implicit_action_boundaries_continue_until_all_clauses_are_split() -> None:
    resolution = OrderedClauseResolver().resolve(
        "打开右前门关闭左前车窗打开天窗打开后备箱打开近光灯"
    )

    assert list(resolution.clauses) == FORMAL_CLAUSES


def test_object_coordination_without_a_second_action_remains_one_clause() -> None:
    resolution = OrderedClauseResolver().resolve("打开车门和车窗")

    assert resolution.clauses == ("打开车门和车窗",)
    assert resolution.split is False


def test_object_coordination_does_not_hide_a_later_control_clause() -> None:
    resolution = OrderedClauseResolver().resolve(
        "打开车门和车窗，然后打开天窗"
    )

    assert resolution.clauses == ("打开车门和车窗", "打开天窗")


def _clause_result(
    clause: str,
    accepted: list[str],
    *,
    reliable: bool,
) -> dict:
    return {
        "clause": clause,
        "accepted_intent_ids": accepted,
        "resolved_params": {intent_id: {} for intent_id in accepted},
        "reliable": reliable,
    }


@pytest.mark.parametrize(
    ("results", "expected_resolved", "expected_unresolved"),
    [
        (
            [
                _clause_result("打开右前门", ["DOOR_OPEN"], reliable=True),
                _clause_result("未知动作", ["WINDOW_CLOSE"], reliable=False),
                _clause_result("打开天窗", ["SUNROOF_OPEN"], reliable=True),
            ],
            [(0, "DOOR_OPEN"), (2, "SUNROOF_OPEN")],
            ["未知动作"],
        ),
        (
            [
                _clause_result("打开右前门", ["DOOR_OPEN"], reliable=True),
                _clause_result("未知动作", [], reliable=False),
            ],
            [(0, "DOOR_OPEN")],
            ["未知动作"],
        ),
        (
            [
                _clause_result(
                    "打开车门和车窗",
                    ["DOOR_OPEN", "WINDOW_OPEN"],
                    reliable=True,
                )
            ],
            [],
            ["打开车门和车窗"],
        ),
    ],
)
def test_completeness_guard_keeps_only_reliable_single_result_occurrences(
    results: list[dict],
    expected_resolved: list[tuple[int, str]],
    expected_unresolved: list[str],
) -> None:
    decision = MultiIntentCompletenessGuard().check(results)

    assert [
        (item.clause_index, item.intent_id)
        for item in decision.resolved_occurrences
    ] == expected_resolved
    assert list(decision.unresolved_clauses) == expected_unresolved
    assert decision.incomplete is True

    rows = SemanticOrchestratorV2._occurrence_rows(
        results,
        decision.resolved_occurrences,
    )
    assert [item["intent_id"] for item in rows] == [
        intent_id for _clause_index, intent_id in expected_resolved
    ]


def test_repeated_intent_ids_remain_distinct_ordered_occurrences() -> None:
    results = [
        _clause_result("打开左前车窗", ["WINDOW_OPEN"], reliable=True),
        _clause_result("打开右后车窗", ["WINDOW_OPEN"], reliable=True),
    ]

    decision = MultiIntentCompletenessGuard().check(results)

    assert decision.incomplete is False
    assert [
        (item.clause_index, item.intent_id)
        for item in decision.resolved_occurrences
    ] == [(0, "WINDOW_OPEN"), (1, "WINDOW_OPEN")]
    assert [
        item["intent_id"]
        for item in SemanticOrchestratorV2._occurrence_rows(
            results,
            decision.resolved_occurrences,
        )
    ] == ["WINDOW_OPEN", "WINDOW_OPEN"]
