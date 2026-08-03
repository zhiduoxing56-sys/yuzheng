from __future__ import annotations

import asyncio
from threading import Thread

from app.core.pipeline import CommandPipeline
from app.models.schemas import PipelineEvent, ReviewAction, ReviewRequest, TextCommandRequest
from app.websocket.broker import PipelineEventBroker


TEST_SECRET = b"stage4-fixed-test-secret-32-bytes"


def test_state_scenario_audit_timeline_and_restart_apis(api_client, tmp_path) -> None:
    client, pipeline = api_client
    initial = client.get("/api/state").json()
    assert initial["vehicle_speed"] == 0
    patched = client.patch(
        "/api/state", json={"vehicle_speed": None, "gear_position": "P"}
    ).json()
    assert patched["vehicle_speed"] is None
    missing = client.post(
        "/api/command/text", json={"text": "打开车门"}
    ).json()
    speed = next(
        node for node in missing["evidence"] if node["evidence_type"] == "vehicle_speed"
    )
    assert speed["quality_label"] == "MISSING"
    assert missing["decision"]["final_decision"] == "BLOCK"
    reset = client.post("/api/state/reset").json()
    assert reset["vehicle_speed"] == 0
    assert reset["door_state"] == "CLOSED"

    scenarios = client.get("/api/scenarios").json()
    ids = {item["scenario_id"] for item in scenarios}
    assert {
        "parked_open_door",
        "moving_open_door",
        "normal_music",
        "emergency_braking",
        "token_reuse",
        "state_changed_before_execution",
    } <= ids
    loaded = client.post("/api/scenarios/night_headlight_off/load").json()
    assert loaded["vehicle_speed"] == 80
    assert loaded["ambient_light"] == 5
    scenario = client.post("/api/scenarios/parked_open_door/run").json()
    assert scenario["semantic_frame"]["action"] == "打开"
    assert scenario["semantic_frame"]["target"] == "车门"
    assert scenario["decision"]["final_decision"] == "PASS"
    assert scenario["decision"]["authorization_token"]

    vague = client.post("/api/scenarios/ambiguous_command/run").json()
    corrected = client.post(
        f"/api/turns/{vague['turn_id']}/review",
        json={"action": "CORRECT", "corrected_text": "打开左侧车窗"},
    ).json()
    assert corrected["accepted"] is True
    assert corrected["root_turn_id"] == vague["turn_id"]
    assert corrected["decision"]["final_decision"] == "PASS"

    page = client.get("/api/audits?page=1&page_size=2&decision=PASS").json()
    assert page["page"] == 1
    assert page["page_size"] == 2
    assert page["total"] >= 2
    assert len(page["items"]) == 2
    assert all(item["final_decision"]["final_decision"] == "PASS" for item in page["items"])
    target_page = client.get("/api/audits?target=车窗").json()
    assert target_page["total"] >= 1
    assert all(item["semantic_frame"]["target"] == "车窗" for item in target_page["items"])
    audit_id = corrected["command_result"]["audit"]["audit_id"]
    detail = client.get(f"/api/audits/{audit_id}").json()
    assert detail["audit_id"] == audit_id
    exported = client.get(f"/api/audits/{audit_id}/export").json()
    assert exported["audit"]["audit_id"] == audit_id
    assert exported["audit_chain_valid"] is True
    assert exported["workflow_chain"]["valid"] is True
    timeline = client.get(f"/api/turns/{vague['turn_id']}/timeline").json()
    assert len(timeline["audits"]) == 2
    event_types = {event["event_type"] for event in timeline["workflow_events"]}
    assert {"REVIEW_REQUESTED", "REVIEW_CORRECTED", "REDECISION_COMPLETED"} <= event_types
    assert client.get(
        f"/api/turns/{vague['turn_id']}/verify-workflow-chain"
    ).json()["valid"] is True

    database_path = pipeline.audit_repository.database_path
    restarted = CommandPipeline(database_path, token_secret=TEST_SECRET)
    restored_status = restarted.review_service.status(vague["turn_id"])
    restored_timeline = restarted.timeline(vague["turn_id"])
    assert restored_status.current_turn_id == corrected["related_turn_id"]
    assert len(restored_timeline.audits) == 2
    assert restarted.audit_repository.verify_chain() is True


def test_websocket_events_are_real_ordered_safe_and_session_isolated(api_client) -> None:
    client, _ = api_client
    response_holder = []
    with client.websocket_connect("/ws/pipeline/session-a") as websocket:
        worker = Thread(
            target=lambda: response_holder.append(
                client.post(
                    "/api/command/text",
                    json={
                        "text": "打开车门",
                        "session_id": "session-a",
                        "state_overrides": {"vehicle_speed": 0, "gear_position": "P"},
                    },
                )
            )
        )
        worker.start()
        events = []
        while not events or events[-1]["stage"] != "TOKEN_ISSUED":
            events.append(websocket.receive_json())
        worker.join(timeout=30)
    assert response_holder and response_holder[0].status_code == 200
    turn_id = response_holder[0].json()["turn_id"]
    assert all(event["turn_id"] == turn_id for event in events)
    assert [event["sequence"] for event in events] == list(range(1, len(events) + 1))
    stages = [event["stage"] for event in events]
    expected = [
        "INPUT_RECEIVED",
        "TRUST_CHECKED",
            "ASR_COMPLETED",
            "SEMANTIC_PARSED",
            "RUNTIME_CAPABILITY_CHECKED",
            "EVIDENCE_RETRIEVED",
        "MANDATORY_SUPPLEMENTED",
        "EVIDENCE_QUALITY_EVALUATED",
        "GRAPH_BUILT",
        "MEMORY_PROPAGATED",
        "CAUSAL_CORRECTED",
        "EVIDENCE_VALIDATED",
        "GATE_CHECKED",
        "DECISION_COMPLETED",
        "EXPLANATION_GENERATED",
        "AUDIT_SAVED",
        "TOKEN_ISSUED",
    ]
    assert stages == expected
    quality_event = next(
        event for event in events if event["stage"] == "EVIDENCE_QUALITY_EVALUATED"
    )
    assert quality_event["payload"]["evidence_alignment_route"] in {
        "EVIDENCE_PASS",
        "EVIDENCE_REVIEW",
        "EVIDENCE_BLOCK",
    }
    assert sum(quality_event["payload"]["eas_weights"].values()) == 1.0
    decision_event = next(
        event for event in events if event["stage"] == "DECISION_COMPLETED"
    )
    assert {
        "score_decision",
        "final_decision",
        "decision_sources",
        "decision_merge_reason",
    } <= decision_event["payload"].keys()
    assert decision_event["payload"]["score_decision"] == response_holder[0].json()["decision"]["score_decision"]
    serialized = str(events)
    raw_token = response_holder[0].json()["decision"]["authorization_token"]
    assert raw_token not in serialized

    executable = response_holder[0].json()
    with client.websocket_connect("/ws/pipeline/execution-session") as websocket:
        execution_holder = []
        worker = Thread(
            target=lambda: execution_holder.append(
                client.post(
                    f"/api/turns/{executable['turn_id']}/execute",
                    json={
                        "authorization_token": executable["decision"]["authorization_token"],
                        "session_id": "execution-session",
                    },
                )
            )
        )
        worker.start()
        execution_events = []
        while not execution_events or not (
            execution_events[-1]["stage"] == "AUDIT_SAVED"
            and "status" in execution_events[-1]["payload"]
        ):
            execution_events.append(websocket.receive_json())
        worker.join(timeout=30)
    assert execution_holder[0].json()["accepted"] is True
    execution_stages = [event["stage"] for event in execution_events]
    execution_tail = execution_stages[execution_stages.index("VEHICLE_PRECHECKED") :]
    assert execution_tail == [
        "VEHICLE_PRECHECKED",
        "TOKEN_CONSUMED",
        "VEHICLE_EXECUTED",
        "AUDIT_SAVED",
    ]
    assert [event["sequence"] for event in execution_events] == list(
        range(1, len(execution_events) + 1)
    )
    assert executable["decision"]["authorization_token"] not in str(execution_events)

    async def verify_isolation() -> None:
        broker = PipelineEventBroker()
        first = broker.subscribe("a")
        second = broker.subscribe("b")
        broker.publish(
            PipelineEvent(
                session_id="a",
                turn_id="TURN_TEST",
                sequence=1,
                stage="INPUT_RECEIVED",
                summary="test",
            )
        )
        received = await asyncio.wait_for(first[1].get(), timeout=1)
        assert received.session_id == "a"
        broker.publish(
            PipelineEvent(
                session_id="a",
                turn_id="TURN_TEST_2",
                sequence=1,
                stage="AUDIT_SAVED",
                summary="second request",
            )
        )
        received_second = await asyncio.wait_for(first[1].get(), timeout=1)
        assert received_second.sequence == received.sequence + 1
        assert second[1].empty()
        broker.unsubscribe("a", first)
        broker.unsubscribe("b", second)

    asyncio.run(verify_isolation())


def test_real_bge_hnsw_and_canonical_index_remain_stable(tmp_path) -> None:
    pipeline = CommandPipeline(tmp_path / "stable.db", token_secret=TEST_SECRET)
    cold = pipeline.index.status()
    for _ in range(100):
        result = pipeline.process_text(
            TextCommandRequest(
                text="打开车门",
                state_overrides={"vehicle_speed": 0, "gear_position": "P"},
            ),
            suppress_authorization=True,
        )
        assert result.decision.final_decision.value == "PASS"
    stable = pipeline.index.status()
    assert getattr(pipeline.embedder, "model_name", "") == "BAAI/bge-base-zh-v1.5"
    assert pipeline.embedder.implementation == "local_sentence_transformer"
    assert cold.implementation == "hnswlib"
    assert stable.implementation == "hnswlib"
    assert stable.degraded is False
    assert stable.canonical_node_count <= cold.canonical_node_count + 1
