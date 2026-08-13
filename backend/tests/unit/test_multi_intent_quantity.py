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
