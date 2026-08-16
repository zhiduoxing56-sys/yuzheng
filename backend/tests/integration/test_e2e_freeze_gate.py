from __future__ import annotations

from typing import Any


def _intent_demand(body: dict[str, Any]) -> dict[str, Any]:
    return body["evidence_demand"]["intent_demands"][0]


def _selected_required_evidence(
    body: dict[str, Any], evidence_type: str
) -> dict[str, Any]:
    assessment = body["decision"]["intent_safety_assessments"][0]
    selected = next(
        item
        for item in assessment["score_factors"]["validated_trust_values"]
        if item["evidence_type"] == evidence_type
    )
    return next(
        item
        for item in body["evidence"]
        if item["node_id"] == selected["selected_node_id"]
    )


def test_activated_risk_scenario_rebuilds_fine_simulation_evidence_for_text_api(
    api_client,
) -> None:
    client, _ = api_client
    activated = client.post(
        "/api/scenarios/knowledge_door_right_rear_bicycle_risk/load"
    )
    assert activated.status_code == 200

    response = client.post(
        "/api/command/text",
        json={"text": "打开右后车门", "session_id": "e2e-risk-door"},
    )
    assert response.status_code == 200
    body = response.json()
    demand = _intent_demand(body)
    assert demand["required_types"] == [
        "VEHICLE_SPEED",
        "GEAR_STATE",
        "SURROUNDING_OBJECT_STATE",
        "DOOR_STATE",
    ]
    surrounding = _selected_required_evidence(body, "SURROUNDING_OBJECT_STATE")
    assert surrounding["source"] == "SIMULATION"
    assert surrounding["metadata"]["turn_id"] == body["turn_id"]
    assert surrounding["metadata"]["explicit_observation"] is True
    target = surrounding["value"]["objects"][0]
    assert target == {
        "object_id": "bicycle-right-rear",
        "entity_kind": "BICYCLE",
        "region": "REAR_RIGHT",
        "exists": True,
        "distance": 3.0,
        "relative_speed": -5.0,
        "motion_state": "APPROACHING",
        "risk_level": "HIGH",
        "source_kind": "SIMULATION",
        "ground_truth": True,
    }
    context_sources = demand["knowledge_retrieval_metadata"]["context_sources"]
    assert {
        item["query_field"]
        for item in context_sources
        if item["evidence_type"] == "SURROUNDING_OBJECT_STATE"
    } >= {
        "目标区域",
        "区域目标",
        "目标类型",
        "目标距离",
        "目标相对速度",
        "目标运动",
        "目标风险",
    }
    assert all(
        item["source"] == "SIMULATION"
        for item in context_sources
        if item["evidence_type"] == "SURROUNDING_OBJECT_STATE"
    )
    assert body["decision"]["final_decision"] == "BLOCK"
    assert body["decision"]["authorization_token"] is None
    audit = client.get(f"/api/audits/{body['audit']['audit_id']}")
    assert audit.status_code == 200
    assert audit.json()["execution_summary"]["status"] == "NOT_EXECUTED"


def test_activated_headlight_scenario_reaches_block_with_fresh_visibility(
    api_client,
) -> None:
    client, _ = api_client
    activated = client.post(
        "/api/scenarios/knowledge_headlight_night_low_visibility/load"
    )
    assert activated.status_code == 200

    response = client.post(
        "/api/command/text",
        json={"text": "关闭前照灯", "session_id": "e2e-night-headlight"},
    )
    assert response.status_code == 200
    body = response.json()
    environment = _selected_required_evidence(body, "ENVIRONMENT_CONDITIONS")
    assert environment["source"] == "SIMULATION"
    assert environment["metadata"]["turn_id"] == body["turn_id"]
    assert environment["value"]["visibility"] == 60
    lighting = _selected_required_evidence(body, "LIGHTING_STATE")
    assert lighting["value"]["headlight_state"] == "ON"
    assert body["decision"]["final_decision"] == "BLOCK"
    assert body["decision"]["authorization_token"] is None
    audit = client.get(f"/api/audits/{body['audit']['audit_id']}")
    assert audit.status_code == 200
    assert audit.json()["execution_summary"]["status"] == "NOT_EXECUTED"


def test_supported_headlight_pass_issues_token_and_executes_through_api(
    api_client,
) -> None:
    client, _ = api_client
    client.post("/api/state/reset")
    state = client.patch(
        "/api/state",
        json={
            "vehicle_speed": 0,
            "gear_position": "P",
            "ambient_light": 100,
            "headlight_state": "ON",
            "weather": "CLEAR",
        },
    )
    assert state.status_code == 200

    response = client.post(
        "/api/command/text",
        json={"text": "关闭前照灯", "session_id": "e2e-pass-headlight"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["final_decision"] == "PASS"
    token = body["decision"]["authorization_token"]
    interaction = body["interaction_request"]
    assert token
    assert interaction["interaction_type"] == "EXECUTION_CONFIRMATION"

    confirmed = client.post(
        f"/api/turns/{body['turn_id']}/interaction",
        json={
            "interaction_id": interaction["interaction_id"],
            "action": "EXECUTE",
        },
    )
    assert confirmed.status_code == 200
    executed = client.post(
        f"/api/turns/{body['turn_id']}/execute",
        json={
            "authorization_token": token,
            "interaction_id": interaction["interaction_id"],
            "session_id": "e2e-pass-headlight-execution",
        },
    )
    assert executed.status_code == 200
    execution = executed.json()
    assert execution["accepted"] is True
    assert execution["execution"]["adapter"] == "simulator"
    assert execution["execution"]["status"] == "SUCCEEDED"
    assert execution["execution"]["after_state"]["headlight_state"] == "OFF"

    audit = client.get(f"/api/audits/{body['audit']['audit_id']}")
    assert audit.status_code == 200
    assert audit.json()["execution_summary"]["status"] == "SUCCEEDED"


def test_specific_door_area_remains_fail_closed_when_adapter_is_global_only(
    api_client,
) -> None:
    client, _ = api_client
    client.post("/api/scenarios/knowledge_door_right_rear_safe_park/load")

    response = client.post(
        "/api/command/text", json={"text": "打开右后车门"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["semantic_frame"]["intents"][0]["area"] == "RIGHT_REAR"
    assert body["decision"]["final_decision"] == "PASS"
    assert body["decision"]["authorization_token"] is None
    assert body["interaction_request"] is None
    audit = client.get(f"/api/audits/{body['audit']['audit_id']}")
    assert audit.status_code == 200
    assert audit.json()["execution_summary"]["status"] == "NOT_EXECUTED"
