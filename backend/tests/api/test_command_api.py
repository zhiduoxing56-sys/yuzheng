from app.models.schemas import DecisionLabel


def test_health_reports_real_database_connection(api_client) -> None:
    client, _ = api_client
    response = client.get("/api/health")
    body = response.json()
    assert response.status_code == 200
    assert body == {
        "status": "ok",
        "service": "语证后端",
        "stage": "阶段一：最小安全闭环",
        "database": "connected",
    }


def test_text_api_returns_pipeline_data_and_persists_audit(api_client) -> None:
    client, pipeline = api_client
    response = client.post(
        "/api/command/text",
        json={
            "text": "打开车门",
            "speaker_zone": "driver",
            "speaker_role": "driver",
            "state_overrides": {"vehicle_speed": 80, "gear_position": "D"},
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["semantic_frame"]["action"] == "打开"
    assert body["semantic_frame"]["target"] == "车门"
    assert "vehicle_speed" in body["evidence_demand"]["required_types"]
    assert body["safety_gate"]["blocked"] is True
    assert body["decision"]["decision"] == DecisionLabel.BLOCK.value
    assert body["audit"]["current_hash"]
    assert pipeline.audit_repository.count() == 1
    saved = pipeline.audit_repository.get_by_turn(body["turn_id"])
    assert saved is not None
    assert saved.final_decision.decision == DecisionLabel.BLOCK


def test_blank_text_is_rejected_before_pipeline(api_client) -> None:
    client, pipeline = api_client
    response = client.post("/api/command/text", json={"text": "   "})
    assert response.status_code == 422
    assert "text 不能只包含空白字符" in response.text
    assert pipeline.audit_repository.count() == 0
