from app.models.schemas import DecisionLabel


def test_health_reports_real_database_connection(api_client) -> None:
    client, _ = api_client
    response = client.get("/api/health")
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["service"] == "语证后端"
    assert body["stage"] == "阶段五：可信语音输入、LA/PA 检测与 ASR 链路"
    assert body["database"] == "connected"
    assert body["model_ready"] is True
    assert body["embedding_implementation"] == "local_sentence_transformer"
    assert body["index_ready"] is True
    assert body["index_implementation"] == "hnswlib"
    assert body["vehicle_adapter"] == "simulator"
    assert body["token_secret_source"] == "injected_test_secret"
    assert body["workflow_event_store"] == "connected"
    assert body["websocket_ready"] is True


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
    assert body["safety_gate"]["mandatory_evidence_missing"] is False
    assert body["decision"]["decision"] == DecisionLabel.BLOCK.value
    assert body["decision"]["final_decision"] == DecisionLabel.BLOCK.value
    assert body["decision"]["soft_safety_score"] == 0.975
    assert body["decision"]["score_evaluation_mode"] == "diagnostic_after_gate"
    assert body["decision"]["gate_blocked"] is True
    assert body["decision"]["gate_reasons"] == ["行驶中禁止打开车门"]
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


def test_text_api_preserves_explicit_null_as_missing_mandatory_evidence(api_client) -> None:
    client, pipeline = api_client
    response = client.post(
        "/api/command/text",
        json={
            "text": "打开车门",
            "speaker_zone": "driver",
            "speaker_role": "driver",
            "state_overrides": {"vehicle_speed": None, "gear_position": "P"},
        },
    )
    body = response.json()
    speed_node = next(node for node in body["evidence"] if node["evidence_type"] == "vehicle_speed")

    assert response.status_code == 200
    assert speed_node["value"] is None
    assert speed_node["quality_label"] == "MISSING"
    assert body["safety_gate"]["mandatory_evidence_missing"] is True
    assert body["decision"]["gate_blocked"] is True
    assert body["decision"]["final_decision"] == DecisionLabel.BLOCK.value
    assert pipeline.audit_repository.get_by_turn(body["turn_id"]) is not None
    assert pipeline.audit_repository.verify_chain() is True
