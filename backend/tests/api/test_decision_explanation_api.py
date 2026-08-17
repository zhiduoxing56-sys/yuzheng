from __future__ import annotations


def test_decision_explanation_status_and_retry_are_isolated_from_command(api_client) -> None:
    client, pipeline = api_client
    pipeline.audit_explanation_service.provider = None

    command = client.post("/api/command/text", json={"text": "打开车窗"})
    assert command.status_code == 200
    turn_id = command.json()["turn_id"]

    status = client.get(f"/api/turns/{turn_id}/decision-explanation")
    assert status.status_code == 200
    assert status.json() == {
        "status": "FAILED",
        "explanation": None,
        "generated_at": None,
        "retryable": True,
    }

    retried = client.post(f"/api/turns/{turn_id}/decision-explanation/retry")
    assert retried.status_code == 200
    assert retried.json()["status"] == "FAILED"
    assert retried.json()["retryable"] is True

    stored = pipeline.audit_repository.get_by_turn(turn_id)
    assert stored is not None
    assert stored.final_decision.final_decision.value == command.json()["decision"]["final_decision"]


def test_decision_explanation_status_rejects_unknown_turn(api_client) -> None:
    client, _ = api_client
    response = client.get("/api/turns/TURN_NOT_REAL/decision-explanation")
    assert response.status_code == 404
    assert response.json()["error_code"] == "TURN_NOT_FOUND"
