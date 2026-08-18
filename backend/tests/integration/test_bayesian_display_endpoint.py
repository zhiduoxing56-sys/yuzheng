from __future__ import annotations


def test_bayesian_diagnostic_endpoint_covers_demo_intents_and_is_read_only(
    api_client,
) -> None:
    client, _pipeline = api_client
    commands = [
        ("关闭前照灯", "HEADLIGHT_OFF"),
        ("关闭雨刮器", "WIPER_OFF"),
        ("打开自动泊车", "AUTO_PARK_ENABLE"),
        ("向左变道", "LANE_CHANGE"),
    ]
    first_turn_id = None
    for text, expected_profile in commands:
        command = client.post("/api/command/text", json={"text": text})
        assert command.status_code == 200, command.text
        turn_id = command.json()["turn_id"]
        first_turn_id = first_turn_id or turn_id
        diagnostic = client.get(f"/api/turns/{turn_id}/bayesian-diagnostic")
        assert diagnostic.status_code == 200, diagnostic.text
        item = diagnostic.json()["diagnostics"][0]
        assert item["supported"] is True
        assert item["profile_id"] == expected_profile
        assert isinstance(item["risk_probability"], float)

    assert first_turn_id is not None
    before = client.get(f"/api/turns/{first_turn_id}")
    diagnostic = client.get(f"/api/turns/{first_turn_id}/bayesian-diagnostic")
    after = client.get(f"/api/turns/{first_turn_id}")

    assert before.status_code == 200
    assert diagnostic.status_code == 200, diagnostic.text
    assert after.status_code == 200
    assert before.json() == after.json()
    body = diagnostic.json()
    assert body["display_only"] is True
    assert body["affects_decision"] is False
    assert body["calculation_stage"] == "POST_DECISION_READ_ONLY"
    assert isinstance(body["diagnostics"][0]["risk_probability"], float)
    response = client.get("/api/turns/TURN_NOT_REAL/bayesian-diagnostic")
    assert response.status_code == 404
