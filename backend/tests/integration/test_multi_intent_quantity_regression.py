from __future__ import annotations

from pathlib import Path

import pytest

from app.core.pipeline import CommandPipeline
from app.models.schemas import AuditDatabaseRole, TextCommandRequest


FORMAL_CLAUSES = [
    "打开右前门",
    "关闭左前车窗",
    "打开天窗",
    "打开后备箱",
    "打开近光灯",
]
FORMAL_INTENT_IDS = [
    "DOOR_OPEN",
    "WINDOW_CLOSE",
    "SUNROOF_OPEN",
    "TRUNK_OPEN",
    "LOW_BEAM_ON",
]


@pytest.fixture(scope="module")
def quantity_pipeline(tmp_path_factory: pytest.TempPathFactory) -> CommandPipeline:
    pipeline = CommandPipeline(
        database_path=Path(tmp_path_factory.mktemp("multi-intent-quantity"))
        / "audit.db",
        token_secret=b"multi-intent-quantity-test-secret",
        audit_database_role=AuditDatabaseRole.TEST,
    )
    yield pipeline
    pipeline.semantic_service.close()


@pytest.mark.parametrize("count", range(1, 6))
def test_one_to_five_formal_intents_flow_to_evidence_and_per_intent_decision(
    quantity_pipeline: CommandPipeline,
    count: int,
) -> None:
    text = "，".join(FORMAL_CLAUSES[:count])
    resolution = quantity_pipeline.semantic_service._orchestrator.clause_resolver.resolve(
        text
    )
    result = quantity_pipeline.process_text(TextCommandRequest(text=text))

    assert len(resolution.clauses) == count
    assert list(resolution.clauses) == FORMAL_CLAUSES[:count]
    assert result.semantic_frame.semantic_status == "OK"
    assert [intent.intent_id for intent in result.semantic_frame.intents] == (
        FORMAL_INTENT_IDS[:count]
    )
    assert [intent.clause_index for intent in result.semantic_frame.intents] == list(
        range(count)
    )
    assert result.semantic_frame.unresolved_clauses == []
    assert result.semantic_frame.review_reasons == []
    assert len(result.evidence_demand.intent_demands) == count
    assert len(result.decision.intent_safety_assessments) == count


@pytest.mark.parametrize(
    ("text", "expected_ids", "unresolved_clause"),
    [
        (
            "打开右前门，设置车窗开度，打开天窗",
            ["DOOR_OPEN", "SUNROOF_OPEN"],
            "设置车窗开度",
        ),
        (
            "打开右前门，打开天窗，设置车窗开度",
            ["DOOR_OPEN", "SUNROOF_OPEN"],
            "设置车窗开度",
        ),
    ],
)
def test_unreliable_middle_or_last_clause_stays_out_of_formal_intents(
    quantity_pipeline: CommandPipeline,
    text: str,
    expected_ids: list[str],
    unresolved_clause: str,
) -> None:
    result = quantity_pipeline.process_text(TextCommandRequest(text=text))

    assert result.semantic_frame.semantic_status == "REVIEW"
    assert [intent.intent_id for intent in result.semantic_frame.intents] == expected_ids
    assert result.semantic_frame.unresolved_clauses == [unresolved_clause]
    assert "MULTI_INTENT_INCOMPLETE" in result.semantic_frame.review_reasons
    assert result.evidence_demand.intent_demands == []
    assert result.decision.intent_safety_assessments == []


def test_multiple_candidates_in_one_clause_are_review_only(
    quantity_pipeline: CommandPipeline,
) -> None:
    result = quantity_pipeline.process_text(
        TextCommandRequest(text="打开车门和车窗")
    )

    assert result.semantic_frame.semantic_status == "REVIEW"
    assert result.semantic_frame.intents == []
    assert result.semantic_frame.unresolved_clauses == ["打开车门和车窗"]
    assert "MULTI_INTENT_INCOMPLETE" in result.semantic_frame.review_reasons
    assert result.semantic_frame.review_candidates
    assert result.evidence_demand.intent_demands == []
    assert result.decision.intent_safety_assessments == []


def test_repeated_intent_ids_keep_occurrence_order_through_decision(
    quantity_pipeline: CommandPipeline,
) -> None:
    result = quantity_pipeline.process_text(
        TextCommandRequest(text="打开左前车窗，打开右后车窗")
    )

    assert result.semantic_frame.semantic_status == "OK"
    assert [intent.intent_id for intent in result.semantic_frame.intents] == [
        "WINDOW_OPEN",
        "WINDOW_OPEN",
    ]
    assert [intent.clause_index for intent in result.semantic_frame.intents] == [0, 1]
    assert len(result.evidence_demand.intent_demands) == 2
    assert len(result.decision.intent_safety_assessments) == 2
    assert [
        (item.clause_index, item.intent_id)
        for item in result.decision.intent_safety_assessments
    ] == [(0, "WINDOW_OPEN"), (1, "WINDOW_OPEN")]
