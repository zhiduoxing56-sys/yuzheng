from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
from pathlib import Path
from threading import Thread

import pytest

from app.core.pipeline import CommandPipeline
from app.core.redaction import (
    REDACTED_AUTHORIZATION_TOKEN,
    SensitiveDataRedactor,
)
from app.models.schemas import (
    AuthorizationTokenStatus,
    ExecuteRequest,
    PipelineEvent,
    TextCommandRequest,
    VehicleStatePatch,
    WorkflowEventType,
)
from app.services.authorization.service import AuthorizationTokenError
from app.services.vehicle.simulator import SimulatorVehicleAdapter
from app.websocket.broker import PipelineEventBroker


TEST_SECRET = b"stage4-fixed-test-secret-32-bytes"


class DeterministicFailingAdapter(SimulatorVehicleAdapter):
    adapter_name = "failing_simulator"

    def execute(self, action: str, target: str, area: str):
        del action, target, area
        raise RuntimeError("受控车辆适配器失败")


def _capture_execution(client, turn_id: str, token: str, session_id: str):
    holder = []
    with client.websocket_connect(f"/ws/pipeline/{session_id}") as websocket:
        worker = Thread(
            target=lambda: holder.append(
                client.post(
                    f"/api/turns/{turn_id}/execute",
                    json={"authorization_token": token, "session_id": session_id},
                )
            )
        )
        worker.start()
        events = []
        while not events or not (
            events[-1]["stage"] == "AUDIT_SAVED"
            and "status" in events[-1]["payload"]
        ):
            events.append(websocket.receive_json())
        worker.join(timeout=30)
    assert not worker.is_alive()
    assert holder
    return holder[0], events


def _tail(events: list[dict]) -> list[str]:
    stages = [event["stage"] for event in events]
    return stages[stages.index("VEHICLE_PRECHECKED") :]


def test_adapter_execution_failure(tmp_path: Path) -> None:
    pipeline = CommandPipeline(tmp_path / "adapter-failure.db", token_secret=TEST_SECRET)
    command = pipeline.process_text(
        TextCommandRequest(
            text="打开车门",
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
        )
    )
    token = command.decision.authorization_token
    pipeline.vehicle = DeterministicFailingAdapter(
        initial_state=pipeline.vehicle.get_state(), action_config=pipeline.vehicle_config
    )
    result = pipeline.execution_service.execute(command.turn_id, token)
    assert result.accepted is False
    assert result.token_status == AuthorizationTokenStatus.CONSUMED
    assert result.execution.status == "FAILED"
    assert "受控车辆适配器失败" in result.reason
    events = pipeline.workflow_repository.events(command.turn_id)
    types = [event.event_type for event in events]
    assert WorkflowEventType.TOKEN_CONSUMED in types
    assert WorkflowEventType.EXECUTION_FAILED in types
    assert WorkflowEventType.EXECUTION_SUCCEEDED not in types
    with pytest.raises(AuthorizationTokenError, match="CONSUMED"):
        pipeline.execution_service.execute(command.turn_id, token)
    next_command = pipeline.process_text(TextCommandRequest(text="查询当前速度"))
    assert next_command.decision.final_decision.value == "PASS"


def test_websocket_success_sequence(api_client) -> None:
    client, _ = api_client
    command = client.post("/api/scenarios/parked_open_door/run").json()
    token = command["decision"]["authorization_token"]
    response, events = _capture_execution(client, command["turn_id"], token, "ws-success")
    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert _tail(events) == [
        "VEHICLE_PRECHECKED",
        "TOKEN_CONSUMED",
        "VEHICLE_EXECUTED",
        "AUDIT_SAVED",
    ]
    assert [event["sequence"] for event in events] == list(range(1, len(events) + 1))
    assert token not in json.dumps(events, ensure_ascii=False)


def test_websocket_failure_sequence(api_client) -> None:
    client, pipeline = api_client
    command = client.post("/api/scenarios/parked_open_door/run").json()
    token = command["decision"]["authorization_token"]
    pipeline.vehicle = DeterministicFailingAdapter(
        initial_state=pipeline.vehicle.get_state(), action_config=pipeline.vehicle_config
    )
    response, events = _capture_execution(client, command["turn_id"], token, "ws-failure")
    assert response.status_code == 200
    assert response.json()["accepted"] is False
    assert _tail(events) == [
        "VEHICLE_PRECHECKED",
        "TOKEN_CONSUMED",
        "EXECUTION_FAILED",
        "AUDIT_SAVED",
    ]
    assert "VEHICLE_EXECUTED" not in _tail(events)
    assert token not in json.dumps(events, ensure_ascii=False)


def test_websocket_precheck_failure_stops_execution(api_client) -> None:
    client, _ = api_client
    command = client.post("/api/scenarios/parked_open_door/run").json()
    token = command["decision"]["authorization_token"]
    client.patch("/api/state", json={"vehicle_speed": 80, "gear_position": "D"})
    response, events = _capture_execution(client, command["turn_id"], token, "ws-precheck-failed")
    assert response.json()["accepted"] is False
    assert _tail(events) == ["VEHICLE_PRECHECKED", "AUDIT_SAVED"]
    prechecked = next(event for event in events if event["stage"] == "VEHICLE_PRECHECKED")
    assert prechecked["payload"]["status"] == "FAILED"
    assert token not in json.dumps(events, ensure_ascii=False)


def test_sensitive_data_redaction(api_client, caplog: pytest.LogCaptureFixture) -> None:
    client, pipeline = api_client
    issued = client.post("/api/scenarios/parked_open_door/run").json()
    token = issued["decision"]["authorization_token"]
    assert token and token not in repr(ExecuteRequest(authorization_token=token))

    ordinary = client.post(
        "/api/command/text", json={"text": f"查询当前速度 {token}"}
    ).json()
    assert token not in ordinary["semantic_frame"]["raw_text"]
    assert REDACTED_AUTHORIZATION_TOKEN in ordinary["semantic_frame"]["raw_text"]

    vague = client.post("/api/command/text", json={"text": "把那个打开"}).json()
    confirmation = client.post(
        f"/api/turns/{vague['turn_id']}/review",
        json={"action": "CONFIRM", "confirmation_text": token},
    )
    assert token not in confirmation.text
    correction = client.post(
        f"/api/turns/{vague['turn_id']}/review",
        json={"action": "CORRECT", "corrected_text": f"打开左侧车窗 {token}"},
    )
    assert token not in correction.text
    pipeline.workflow_repository.append_event(
        root_turn_id=vague["turn_id"],
        related_turn_id=vague["turn_id"],
        event_type=WorkflowEventType.REVIEW_CONFIRM_REJECTED,
        payload={"extra": token, "authorization_token": token, "token_id": "TOK_TRACE"},
    )

    invalid = client.post(
        "/api/command/text",
        json={"text": "查询当前速度", "authorization_token": token},
    )
    assert invalid.status_code == 422
    assert token not in invalid.text
    assert REDACTED_AUTHORIZATION_TOKEN in invalid.text

    async def websocket_redaction() -> str:
        broker = PipelineEventBroker()
        subscription = broker.subscribe("redaction")
        broker.publish(
            PipelineEvent(
                session_id="redaction",
                turn_id="TURN_REDACTION",
                sequence=1,
                stage="TEST",
                summary=f"unsafe {token}",
                payload={"raw_token": token, "message": token},
            )
        )
        event = await asyncio.wait_for(subscription[1].get(), timeout=1)
        broker.unsubscribe("redaction", subscription)
        return event.model_dump_json()

    websocket_payload = asyncio.run(websocket_redaction())
    assert token not in websocket_payload
    assert REDACTED_AUTHORIZATION_TOKEN in websocket_payload

    with caplog.at_level(logging.WARNING, logger="uvicorn.error"):
        logging.getLogger("uvicorn.error").warning("received token %s", token)
    assert token not in caplog.text
    assert REDACTED_AUTHORIZATION_TOKEN in caplog.text

    database = pipeline.audit_repository.database_path
    serialized_rows: list[str] = []
    with sqlite3.connect(database) as connection:
        for table, column in (
            ("audit_records", "record_json"),
            ("turn_workflow_events", "payload_json"),
            ("vehicle_execution_events", "result_json"),
        ):
            serialized_rows.extend(
                str(row[0])
                for row in connection.execute(f"SELECT {column} FROM {table}").fetchall()
            )
    page = client.get("/api/audits?page_size=100").json()
    exports = [
        client.get(f"/api/audits/{item['audit_id']}/export").json()
        for item in page["items"]
    ]
    full_scan = "\n".join(serialized_rows) + json.dumps(exports, ensure_ascii=False)
    assert token not in full_scan
    assert SensitiveDataRedactor.redact_text("正常非敏感文本") == "正常非敏感文本"


def test_simulator_epoch_reset(api_client, tmp_path: Path) -> None:
    client, pipeline = api_client
    initial = client.get("/api/state").json()
    assert initial["state_epoch_id"]
    assert initial["reset_count"] == 0
    reset = client.post("/api/state/reset").json()
    assert reset["state_epoch_id"] != initial["state_epoch_id"]
    assert reset["reset_count"] == 1
    assert reset["last_reset_at"]
    assert reset["reset_reason"] == "manual_reset"

    command = client.post("/api/scenarios/parked_open_door/run").json()
    token = command["decision"]["authorization_token"]
    executed = client.post(
        f"/api/turns/{command['turn_id']}/execute",
        json={"authorization_token": token},
    ).json()
    assert executed["accepted"] is True
    historical_epoch = executed["execution"]["after_state"]["state_epoch_id"]
    database = pipeline.audit_repository.database_path
    restarted = CommandPipeline(database, token_secret=TEST_SECRET)
    timeline = restarted.timeline(command["turn_id"])
    assert timeline.historical_execution_state
    assert timeline.historical_execution_state[0].after_state.state_epoch_id == historical_epoch
    assert timeline.current_simulator_state.state_epoch_id != historical_epoch
    assert timeline.current_simulator_state.reset_reason == "service_started"
