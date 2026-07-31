from __future__ import annotations

import json
import sqlite3


def test_stage2_evidence_and_index_apis_return_runtime_data(api_client) -> None:
    client, _ = api_client
    command = client.post(
        "/api/command/text",
        json={"text": "打开车门", "state_overrides": {"vehicle_speed": 0, "gear_position": "P"}},
    )
    body = command.json()
    turn_id = body["turn_id"]

    assert command.status_code == 200
    assert len(body["query_vector"]) == 768
    assert body["evidence_demand"]["vectorization_metadata"]["model_name"] == "BAAI/bge-base-zh-v1.5"
    assert body["evidence_demand"]["vectorization_metadata"]["real_model_inference"] is True
    assert body["retrieval_metadata"]["implementation"] == "hnswlib"
    assert body["retrieval_metadata"]["degraded"] is False
    assert body["retrieval_metadata"]["candidate_count"] == len(body["candidate_evidence"])
    assert body["evidence_subgraph"]["turn_id"] == turn_id
    assert body["quality_metrics"]["ecr"] == 1.0

    current = client.get("/api/evidence/current")
    graph = client.get(f"/api/evidence/turn/{turn_id}")
    status = client.get("/api/index/status")
    rebuild = client.post("/api/index/rebuild", json={"exclude_types": ["vehicle_speed"]})

    assert current.status_code == 200
    assert current.json()["node_count"] == len(current.json()["nodes"])
    assert graph.status_code == 200
    assert graph.json()["nodes"] and graph.json()["edges"]
    assert status.json()["dimension"] == 768
    assert rebuild.json()["excluded_types"] == ["vehicle_speed"]
    assert rebuild.json()["node_count"] < status.json()["node_count"]
    assert client.get("/api/evidence/turn/NOT_FOUND").status_code == 404


def test_tampering_new_retrieval_field_breaks_audit_chain(pipeline) -> None:
    from app.models.schemas import TextCommandRequest

    result = pipeline.process_text(TextCommandRequest(text="打开车门"))
    assert pipeline.audit_repository.verify_chain() is True

    with sqlite3.connect(pipeline.audit_repository.database_path) as connection:
        row = connection.execute(
            "SELECT record_json FROM audit_records WHERE turn_id = ?", (result.turn_id,)
        ).fetchone()
        record = json.loads(row[0])
        record["retrieval_metadata"]["duration_ms"] += 1
        connection.execute(
            "UPDATE audit_records SET record_json = ? WHERE turn_id = ?",
            (json.dumps(record, ensure_ascii=False), result.turn_id),
        )

    assert pipeline.audit_repository.verify_chain() is False
