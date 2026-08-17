from app.services.vehicle.scenario_summary import scenario_conditions


def test_scenario_conditions_render_state_and_explicit_missing_value() -> None:
    conditions = scenario_conditions(
        {
            "state": {
                "vehicle_speed": None,
                "gear_position": "P",
                "weather": "CLEAR",
                "occupant_role": "driver",
            }
        }
    )

    assert conditions == [
        "车速：未提供",
        "挡位：P（驻车）",
        "天气：晴朗",
        "身份：驾驶员",
    ]


def test_scenario_conditions_expand_environment_and_surrounding_object() -> None:
    conditions = scenario_conditions(
        {
            "state": {"vehicle_speed": 42, "gear_position": "D"},
            "evidence_overrides": [
                {
                    "evidence_type": "ENVIRONMENT_CONDITIONS",
                    "source": "SIMULATION",
                    "value": {
                        "time_of_day": "NIGHT",
                        "ambient_illumination": 5,
                        "visibility": 60,
                        "weather": "CLEAR",
                    },
                },
                {
                    "evidence_type": "SURROUNDING_OBJECT_STATE",
                    "source": "SIMULATION",
                    "value": {
                        "objects": [
                            {
                                "region": "REAR_RIGHT",
                                "entity_kind": "BICYCLE",
                                "distance": 3,
                                "motion_state": "APPROACHING",
                                "risk_level": "HIGH",
                            }
                        ]
                    },
                },
            ],
        }
    )

    assert conditions == [
        "车速：42 km/h",
        "挡位：D（前进）",
        "环境：时段夜间、照度5 lux、能见度60 m、天气晴朗",
        "周边目标：右后方自行车距离3 m接近高风险",
    ]
