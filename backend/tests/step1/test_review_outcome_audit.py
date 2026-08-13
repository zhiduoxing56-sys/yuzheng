from __future__ import annotations

import sqlite3
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.schemas import (
    ReviewAction,
    ReviewRequest,
    TextCommandRequest,
    WorkflowEventType,
)


FORBIDDEN_OUTCOME_FIELDS = {
    "input_trust_result",
    "transcription_result",
    "semantic_frame",
    "evidence_demand",
    "candidate_recall_results",
    "evidence_subgraph",
    "evidence_quality_metrics",
    "score_details",
}


def test_cancel_appends_terminal_audit_and_all_public_reads_use_effective_state(
    api_client,
) -> None:
    client, pipeline = api_client
    command = client.post("/api/command/text", json={"text": "把那个打开"})
    assert command.status_code == 200
    turn_id = command.json()["turn_id"]
    original = pipeline.audit_repository.get_by_turn(turn_id)
    assert original is not None
    original_json = original.model_dump_json()
    original_hash = original.current_hash
    assert original.final_decision.final_decision.value == "REVIEW"

    response = client.post(
        f"/api/turns/{turn_id}/review", json={"action": "CANCEL"}
    )
    assert response.status_code == 200
    body = response.json()
    terminal_audit_id = body["audit_id"]
    assert body["new_decision"] == "BLOCK"
    assert body["decision"]["score_decision"] == original.final_decision.score_decision.value
    assert body["decision"]["final_decision"] == "BLOCK"
    assert "USER_REVIEW" in body["decision"]["decision_sources"]
    assert body["token_issued"] is False

    restored_original = pipeline.audit_repository.get_by_id(original.audit_id)
    assert restored_original is not None
    assert restored_original.model_dump_json() == original_json
    assert restored_original.current_hash == original_hash
    outcome = pipeline.audit_repository.outcome_for_original(original.audit_id)
    assert outcome is not None
    assert outcome.audit_id == terminal_audit_id
    assert outcome.record_type == "REVIEW_OUTCOME"
    assert outcome.original_turn_id == turn_id
    assert outcome.original_final_decision.value == "REVIEW"
    assert outcome.effective_final_decision.value == "BLOCK"
    assert not FORBIDDEN_OUTCOME_FIELDS & set(outcome.model_dump())

    presentation = client.get(f"/api/turns/{turn_id}/presentation").json()
    assert presentation["decision_result"]["score_decision"] == (
        original.final_decision.score_decision.value
    )
    assert presentation["decision_result"]["final_decision"] == "BLOCK"
    assert "USER_REVIEW" in presentation["decision_result"]["decision_sources"]
    assert presentation["decision_result"]["execution_allowed"] is False
    assert presentation["review"]["status"] == "CANCELLED"
    assert presentation["review"]["user_action"] == "CANCEL"

    detail = client.get(f"/api/audits/{original.audit_id}").json()
    assert detail["command_summary"]["raw_command"] == original.semantic_frame.raw_text
    assert detail["command_summary"]["final_decision"] == "BLOCK"
    assert detail["decision_summary"]["final_decision"] == "BLOCK"
    assert "original_decision" not in detail
    assert "effective_outcome" not in detail

    blocked = client.get("/api/audits?decision=BLOCK&page_size=100").json()
    reviewed = client.get("/api/audits?decision=REVIEW&page_size=100").json()
    blocked_items = [item for item in blocked["items"] if item["raw_command"] == original.semantic_frame.raw_text]
    reviewed_items = [item for item in reviewed["items"] if item["raw_command"] == original.semantic_frame.raw_text]
    assert len(blocked_items) == 1
    assert blocked_items[0]["final_decision"] == "BLOCK"
    assert blocked_items[0]["review_occurred"] is True
    assert reviewed_items == []

    timeline = client.get(f"/api/turns/{turn_id}/timeline").json()
    stages = [item["stage"] for item in timeline["items"]]
    assert "REVIEW_CANCELLED" in stages
    assert "FINAL_DECISION_UPDATED" in stages
    assert "AUDIT_OUTCOME_APPENDED" in stages

    verification = client.get(f"/api/audits/{original.audit_id}/verify").json()
    assert verification["record_hash_valid"] is True
    assert verification["terminal_audit_id"] == terminal_audit_id
    assert verification["terminal_record_hash_valid"] is True
    assert verification["relationship_valid"] is True
    assert verification["merge_decision_valid"] is True
    assert verification["effective_outcome_valid"] is True
    assert verification["audit_chain_valid"] is True
    assert verification["workflow_chain_valid"] is True

    repeated = client.post(
        f"/api/turns/{turn_id}/review", json={"action": "CANCEL"}
    )
    assert repeated.status_code == 409
    assert terminal_audit_id in repeated.json()["message"]
    assert len(pipeline.audit_repository.outcomes()) == 1
    event_counts = Counter(
        event.event_type
        for event in pipeline.workflow_repository.events(turn_id)
    )
    assert event_counts[WorkflowEventType.REVIEW_CANCELLED] == 1
    assert event_counts[WorkflowEventType.FINAL_DECISION_UPDATED] == 1
    assert event_counts[WorkflowEventType.AUDIT_OUTCOME_APPENDED] == 1

    restarted = create_app(
        database_path=pipeline.audit_repository.database_path,
        token_secret=b"stage4-fixed-test-secret-32-bytes",
    audit_database_role="TEST",
    )
    with TestClient(restarted) as restarted_client:
        restarted_presentation = restarted_client.get(
            f"/api/turns/{turn_id}/presentation"
        ).json()
        restarted_detail = restarted_client.get(
            f"/api/audits/{original.audit_id}"
        ).json()
    assert restarted_presentation["decision_result"]["final_decision"] == "BLOCK"
    assert restarted_detail["decision_summary"]["final_decision"] == "BLOCK"


def test_concurrent_cancel_has_one_outcome_and_one_terminal_event_group(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="把那个打开"))

    def cancel() -> str:
        try:
            reviewed = pipeline.review_service.review(
                result.turn_id, ReviewRequest(action=ReviewAction.CANCEL)
            )
            return reviewed.terminal_audit_id or "missing"
        except ValueError as exc:
            return str(exc)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: cancel(), range(2)))

    outcomes = pipeline.audit_repository.outcomes()
    assert len(outcomes) == 1
    assert any(outcomes[0].audit_id in item for item in results)
    counts = Counter(
        event.event_type
        for event in pipeline.workflow_repository.events(result.turn_id)
    )
    assert counts[WorkflowEventType.REVIEW_CANCELLED] == 1
    assert counts[WorkflowEventType.FINAL_DECISION_UPDATED] == 1
    assert counts[WorkflowEventType.AUDIT_OUTCOME_APPENDED] == 1
    assert pipeline.audit_repository.verify_chain() is True
    assert pipeline.workflow_repository.verify_chain(result.turn_id).valid is True


def test_review_outcome_unique_index_rejects_direct_duplicate_insert(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="把那个打开"))
    reviewed = pipeline.review_service.review(
        result.turn_id, ReviewRequest(action=ReviewAction.CANCEL)
    )
    outcome = pipeline.audit_repository.outcome_for_original(result.audit.audit_id)

    assert outcome is not None
    assert reviewed.terminal_audit_id == outcome.audit_id
    with sqlite3.connect(pipeline.audit_repository.database_path) as connection:
        index_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' "
            "AND name='idx_review_outcome_unique'"
        ).fetchone()
        assert index_sql is not None
        assert "original_audit_id, review_action" in index_sql[0]
        stored = connection.execute(
            "SELECT created_at, decision, action, target, risk_types, record_json, "
            "previous_hash FROM audit_records WHERE audit_id = ?",
            (outcome.audit_id,),
        ).fetchone()
        assert stored is not None
        with pytest.raises(
            sqlite3.IntegrityError,
            match="UNIQUE constraint failed: audit_records.original_audit_id, audit_records.review_action",
        ):
            connection.execute(
                """
                INSERT INTO audit_records (
                    audit_id, turn_id, created_at, decision, action, target,
                    risk_types, record_json, previous_hash, current_hash,
                    record_type, original_audit_id, review_action, idempotency_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "AUD_duplicate_outcome",
                    "OUTCOME_duplicate_turn",
                    stored[0],
                    stored[1],
                    stored[2],
                    stored[3],
                    stored[4],
                    stored[5],
                    stored[6],
                    "duplicate-current-hash",
                    "REVIEW_OUTCOME",
                    outcome.original_audit_id,
                    "CANCEL",
                    "duplicate-idempotency-key",
                ),
            )

    assert len(pipeline.audit_repository.outcomes()) == 1
    assert pipeline.audit_repository.verify_chain() is True
    assert pipeline.workflow_repository.verify_chain(result.turn_id).valid is True
