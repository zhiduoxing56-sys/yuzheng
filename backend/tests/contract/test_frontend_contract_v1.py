from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.pipeline import CommandPipeline
from app.main import create_app
from app.models.frontend_contract import ReviewSubmission
from app.models.schemas import PipelineEvent, ReviewAction, ReviewRequest
from app.services.review.adapter import adapt_review_submission
from app.websocket.broker import PipelineEventBroker


TEST_SECRET = b"frontend-contract-v1-fixed-secret-32-bytes"
ASSET = Path(__file__).resolve().parents[1] / "assets" / "stage5" / "public_human_zh.wav"


@pytest.fixture(scope="module")
def contract_context(tmp_path_factory: pytest.TempPathFactory):
    database = tmp_path_factory.mktemp("frontend-contract-v1") / "contract.db"
    app = create_app(database_path=database, token_secret=TEST_SECRET)
    with TestClient(app) as client:
        yield client, app.state.pipeline, database


@pytest.fixture(scope="module")
def prepared(contract_context):
    client, _, _ = contract_context
    passed = client.post("/api/scenarios/parked_open_door/run").json()
    reviewable = client.post(
        "/api/command/text",
        json={
            "text": "可能播放音乐",
            "state_overrides": {"vehicle_speed": 0, "gear_position": "P"},
        },
    ).json()
    ambiguous = client.post("/api/command/text", json={"text": "把那个打开"}).json()
    cancelled = client.post("/api/command/text", json={"text": "把那个打开"}).json()
    client.patch("/api/state", json={"vehicle_speed": None, "gear_position": "P"})
    missing = client.post("/api/command/text", json={"text": "打开车门"}).json()
    client.post("/api/state/reset")
    tampered = client.post(
        "/api/command/text",
        json={
            "text": "打开车门",
            "evidence_overrides": [
                {
                    "evidence_type": "vehicle_speed",
                    "source": "contract_tampered_sensor",
                    "value": 0,
                    "integrity_valid": False,
                }
            ],
        },
    ).json()
    blocked = client.post("/api/scenarios/moving_open_door/run").json()
    return {
        "passed": passed,
        "reviewable": reviewable,
        "ambiguous": ambiguous,
        "cancelled": cancelled,
        "missing": missing,
        "tampered": tampered,
        "blocked": blocked,
    }


def test_01_presentation_returns_complete_same_turn_snapshot(contract_context, prepared):
    client, _, _ = contract_context
    turn_id = prepared["passed"]["turn_id"]
    body = client.get(f"/api/turns/{turn_id}/presentation").json()
    assert body["turn_id"] == turn_id
    assert {
        "input",
        "semantic_frame",
        "evidence_demand",
        "retrieval_summary",
        "evidence",
        "gate_result",
        "score_result",
        "validation_result",
        "decision_result",
        "review",
        "authorization",
        "execution",
        "audit",
    } <= body.keys()


def test_02_presentation_does_not_rerun_pipeline(contract_context, prepared, monkeypatch):
    client, pipeline, _ = contract_context
    monkeypatch.setattr(
        pipeline, "process_text", lambda *args, **kwargs: pytest.fail("pipeline reran")
    )
    response = client.get(
        f"/api/turns/{prepared['passed']['turn_id']}/presentation"
    )
    assert response.status_code == 200


def test_03_presentation_decision_matches_audit(contract_context, prepared):
    client, pipeline, _ = contract_context
    turn_id = prepared["passed"]["turn_id"]
    stored = pipeline.audit_repository.get_by_turn(turn_id)
    body = client.get(f"/api/turns/{turn_id}/presentation").json()
    assert body["decision_result"]["final_decision"] == stored.final_decision.final_decision.value


@pytest.mark.parametrize("forbidden", ["raw_audio", "query_vector", "logits"])
def test_04_06_presentation_excludes_sensitive_or_vector_fields(
    contract_context, prepared, forbidden
):
    client, _, _ = contract_context
    text = client.get(
        f"/api/turns/{prepared['passed']['turn_id']}/presentation"
    ).text.lower()
    assert forbidden not in text


def test_07_node_detail_is_limited_to_turn(contract_context, prepared):
    client, _, _ = contract_context
    missing_node = next(
        node
        for node in prepared["missing"]["evidence_subgraph"]["nodes"]
        if node["quality_label"] == "MISSING"
    )
    response = client.get(
        f"/api/turns/{prepared['passed']['turn_id']}/evidence/{missing_node['node_id']}"
    )
    assert response.status_code == 409
    assert response.json()["error_code"] == "NODE_NOT_IN_TURN"


def test_08_missing_node_is_readable(contract_context, prepared):
    client, _, _ = contract_context
    node = next(
        node
        for node in prepared["missing"]["evidence_subgraph"]["nodes"]
        if node["quality_label"] == "MISSING"
    )
    body = client.get(
        f"/api/turns/{prepared['missing']['turn_id']}/evidence/{node['node_id']}"
    ).json()
    assert body["node_id"] == node["node_id"]
    assert body["quality_label"] == "MISSING"


def test_09_tampered_node_is_readable(contract_context, prepared):
    client, _, _ = contract_context
    node = next(
        node
        for node in prepared["tampered"]["evidence_subgraph"]["nodes"]
        if node["quality_label"] == "TAMPERED"
    )
    body = client.get(
        f"/api/turns/{prepared['tampered']['turn_id']}/evidence/{node['node_id']}"
    ).json()
    assert body["quality_label"] == "TAMPERED"


def test_10_review_confirm_reexecutes_full_flow(contract_context, prepared):
    client, _, _ = contract_context
    original = prepared["reviewable"]["turn_id"]
    body = client.post(
        f"/api/turns/{original}/review", json={"action": "CONFIRM"}
    ).json()
    assert body["accepted"] is True
    assert body["review_turn_id"] != original
    assert body["new_decision"] == "PASS"
    assert body["token_issued"] is True


def test_11_review_correct_requires_text(contract_context, prepared):
    client, _, _ = contract_context
    response = client.post(
        f"/api/turns/{prepared['ambiguous']['turn_id']}/review",
        json={"action": "CORRECT"},
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "CORRECTED_TEXT_REQUIRED"


def test_12_review_cancel_never_issues_token(contract_context, prepared):
    client, _, _ = contract_context
    body = client.post(
        f"/api/turns/{prepared['cancelled']['turn_id']}/review",
        json={"action": "CANCEL"},
    ).json()
    assert body["new_decision"] == "BLOCK"
    assert body["token_issued"] is False
    assert body["execution_status"] == "CANCELLED"


@pytest.mark.parametrize("key", ["passed", "blocked"])
def test_13_pass_and_block_cannot_be_reviewed(contract_context, prepared, key):
    client, _, _ = contract_context
    response = client.post(
        f"/api/turns/{prepared[key]['turn_id']}/review", json={"action": "CONFIRM"}
    )
    assert response.status_code == 409
    assert response.json()["error_code"] == "REVIEW_NOT_ALLOWED"


def test_14_audit_list_supports_time_filter(contract_context):
    client, _, _ = contract_context
    response = client.get(
        "/api/audits?start_time=2000-01-01T00:00:00Z&end_time=2100-01-01T00:00:00Z"
    )
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_15_audit_list_supports_decision_filter(contract_context):
    client, _, _ = contract_context
    body = client.get("/api/audits?decision=PASS&page_size=100").json()
    assert body["items"]
    assert all(item["final_decision"]["final_decision"] == "PASS" for item in body["items"])


def test_16_audit_detail_contains_document_sections(contract_context, prepared):
    client, _, _ = contract_context
    audit_id = prepared["passed"]["audit"]["audit_id"]
    body = client.get(f"/api/audits/{audit_id}").json()
    required = {
        "input_summary",
        "voice_trust",
        "transcription",
        "semantic_frame",
        "evidence_demand",
        "retrieval_summary",
        "mandatory_recall",
        "evidence_graph_summary",
        "quality_metrics",
        "validation_result",
        "gate_result",
        "score_factors",
        "initial_decision",
        "review_process",
        "final_decision",
        "authorization_status",
        "execution_status",
        "workflow_events",
        "previous_hash",
        "record_hash",
        "audit_chain_valid",
        "workflow_chain_valid",
    }
    assert required <= body.keys()
    assert "weights_path" not in json.dumps(body, ensure_ascii=False)


def test_17_audit_verify_is_read_only(contract_context, prepared):
    client, pipeline, _ = contract_context
    audit_id = prepared["passed"]["audit"]["audit_id"]
    before = pipeline.audit_repository.count()
    body = client.get(f"/api/audits/{audit_id}/verify").json()
    assert body["record_hash_valid"] is True
    assert body["previous_link_valid"] is True
    assert body["audit_chain_valid"] is True
    assert body["workflow_chain_valid"] is True
    assert pipeline.audit_repository.count() == before


def test_18_timeline_items_are_sequence_sorted(contract_context, prepared):
    client, _, _ = contract_context
    items = client.get(
        f"/api/turns/{prepared['reviewable']['turn_id']}/timeline"
    ).json()["items"]
    assert [item["sequence"] for item in items] == list(range(1, len(items) + 1))
    assert all({"sequence", "stage", "timestamp", "status", "summary"} <= item.keys() for item in items)


def test_19_websocket_envelope_contains_turn_id():
    event = PipelineEvent(
        session_id="contract",
        turn_id="TURN_CONTRACT",
        sequence=1,
        stage="INPUT_RECEIVED",
        summary="received",
    ).model_dump(mode="json")
    assert event["turn_id"] == "TURN_CONTRACT"
    assert {"event_id", "turn_id", "sequence", "event_type", "stage", "status", "timestamp", "payload"} <= event.keys()


def test_20_different_turn_events_are_not_overwritten():
    async def exercise() -> list[PipelineEvent]:
        broker = PipelineEventBroker()
        subscription = broker.subscribe("same-session")
        for index in (1, 2):
            broker.publish(
                PipelineEvent(
                    session_id="same-session",
                    turn_id=f"TURN_{index}",
                    sequence=1,
                    stage="INPUT_RECEIVED",
                    summary=str(index),
                )
            )
        events = [await subscription[1].get(), await subscription[1].get()]
        broker.unsubscribe("same-session", subscription)
        return events

    events = asyncio.run(exercise())
    assert [event.turn_id for event in events] == ["TURN_1", "TURN_2"]
    assert [event.sequence for event in events] == [1, 2]


def test_21_disconnected_turn_recovers_via_presentation(contract_context):
    client, _, _ = contract_context
    command = client.post("/api/command/text", json={"text": "查询当前速度"}).json()
    response = client.get(f"/api/turns/{command['turn_id']}/presentation")
    assert response.status_code == 200
    assert response.json()["turn_id"] == command["turn_id"]


def test_22_observe_and_enforce_mode_are_reported(contract_context, prepared):
    client, pipeline, _ = contract_context
    turn_id = prepared["passed"]["turn_id"]
    original = pipeline.voice_trust_mode
    try:
        pipeline.voice_trust_mode = "observe"
        assert client.get(f"/api/turns/{turn_id}/presentation").json()["voice_trust_mode"] == "observe"
        pipeline.voice_trust_mode = "enforce"
        assert client.get(f"/api/turns/{turn_id}/presentation").json()["voice_trust_mode"] == "enforce"
    finally:
        pipeline.voice_trust_mode = original


def test_23_text_interface_does_not_fake_asr_confidence(contract_context):
    client, _, _ = contract_context
    command = client.post(
        "/api/command/text", json={"text": "查询当前速度", "session_id": "text-contract"}
    ).json()
    assert command["accepted"] is True
    assert command["input_type"] == "text"
    assert command["websocket_channel"] == "/ws/pipeline/text-contract"
    presentation = client.get(f"/api/turns/{command['turn_id']}/presentation").json()
    assert presentation["input"]["asr_confidence"] is None


def test_24_audio_interface_does_not_persist_raw_audio(contract_context):
    client, _, database = contract_context
    audio = ASSET.read_bytes()
    response = client.post(
        "/api/command/audio?audio_source=contract_wav&speaker_zone=driver&speaker_role=driver",
        content=audio,
        headers={"content-type": "audio/wav"},
    )
    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["input_type"] == "audio"
    with sqlite3.connect(database) as connection:
        rows = [row[0] for row in connection.execute("SELECT record_json FROM audit_records")]
    serialized = "\n".join(rows)
    assert audio.hex()[:80] not in serialized
    assert '"raw_audio_persisted":false' in serialized.replace(" ", "")


def test_25_no_fake_hnsw_path_is_returned(contract_context, prepared):
    client, _, _ = contract_context
    retrieval = client.get(
        f"/api/turns/{prepared['passed']['turn_id']}/presentation"
    ).json()["retrieval_summary"]
    forbidden = {"visited_nodes", "entry_point", "navigation_path", "recall"}
    assert forbidden.isdisjoint(retrieval)


def test_strict_review_rejects_unrelated_fields(contract_context, prepared):
    client, _, _ = contract_context
    response = client.post(
        f"/api/turns/{prepared['ambiguous']['turn_id']}/review",
        json={"action": "CONFIRM", "confirmation_text": "旧字段"},
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "INVALID_REQUEST"


def test_openapi_exposes_only_new_review_contract(contract_context):
    client, _, _ = contract_context
    openapi = client.get("/openapi.json").json()
    operation = openapi["paths"]["/api/turns/{turn_id}/review"]["post"]
    schema_ref = operation["requestBody"]["content"]["application/json"]["schema"]["$ref"]
    schema = openapi["components"]["schemas"][schema_ref.rsplit("/", 1)[-1]]
    assert set(schema["properties"]) == {"action", "corrected_text"}
    assert "confirmation_text" not in json.dumps(operation)
    assert "cancel_reason" not in json.dumps(operation)


def test_openapi_audit_list_has_only_public_filters(contract_context):
    client, _, _ = contract_context
    operation = client.get("/openapi.json").json()["paths"]["/api/audits"]["get"]
    names = {parameter["name"] for parameter in operation["parameters"]}
    assert names == {"start_time", "end_time", "decision", "page", "page_size"}


def test_review_adapter_preserves_action_and_text_exactly():
    public = ReviewSubmission(action=ReviewAction.CORRECT, corrected_text="  打开左窗  ")
    internal = adapt_review_submission(public)
    assert internal.action is ReviewAction.CORRECT
    assert internal.corrected_text == "  打开左窗  "


def test_internal_review_model_remains_backward_compatible():
    legacy = ReviewRequest(
        action=ReviewAction.CONFIRM, confirmation_text="内部旧调用"
    )
    assert legacy.confirmation_text == "内部旧调用"


def test_missing_turn_uses_contract_error(contract_context):
    client, _, _ = contract_context
    body = client.get("/api/turns/TURN_NOT_REAL/presentation").json()
    assert body == {
        "error_code": "TURN_NOT_FOUND",
        "message": "未找到指定轮次",
        "turn_id": "TURN_NOT_REAL",
        "details": {},
    }


def test_invalid_audit_filter_uses_contract_error(contract_context):
    client, _, _ = contract_context
    response = client.get("/api/audits?decision=ALLOW")
    assert response.status_code == 422
    assert response.json()["error_code"] == "INVALID_FILTER"
