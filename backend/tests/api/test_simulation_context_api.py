def test_simulation_context_endpoint_replaces_current_formal_observations(api_client) -> None:
    client, _ = api_client
    payload = [
        {
            "evidence_type": "SURROUNDING_OBJECT_STATE",
            "source": "SIMULATION",
            "value": {
                "objects": [
                    {
                        "object_id": "manual-bicycle",
                        "entity_kind": "BICYCLE",
                        "region": "REAR_RIGHT",
                        "distance": 3,
                        "relative_speed": -5,
                        "motion_state": "APPROACHING",
                        "risk_level": "HIGH",
                    }
                ]
            },
        }
    ]

    stored = client.put("/api/state/simulation-context", json=payload)
    assert stored.status_code == 200
    assert stored.json()[0]["source"] == "SIMULATION"

    current = client.get("/api/state/simulation-context")
    assert current.status_code == 200
    assert current.json()[0]["value"]["objects"][0]["region"] == "REAR_RIGHT"

    cleared = client.put("/api/state/simulation-context", json=[])
    assert cleared.status_code == 200
    assert cleared.json() == []

