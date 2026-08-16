from app.models.schemas import EvidenceObservationInput
from app.services.vehicle.carla import CarlaVehicleAdapter


def _observation(evidence_type: str, value: object) -> EvidenceObservationInput:
    return EvidenceObservationInput(
        evidence_type=evidence_type,
        source="SIMULATION",
        value=value,
    )


def test_carla_scenario_context_keeps_only_supplemental_evidence() -> None:
    evidence = [
        _observation("VEHICLE_SPEED", 42),
        _observation("GEAR_STATE", {"current_gear": "D"}),
        _observation(
            "ENVIRONMENT_CONDITIONS",
            {
                "weather": "RAIN",
                "visibility": 300,
                "precipitation": "RAIN",
            },
        ),
        _observation(
            "SURROUNDING_OBJECT_STATE",
            {"objects": [{"entity_kind": "BICYCLE", "region": "REAR_RIGHT"}]},
        ),
    ]

    supplemental = CarlaVehicleAdapter._supplemental_scenario_evidence(evidence)

    assert [item.evidence_type for item in supplemental] == [
        "ENVIRONMENT_CONDITIONS",
        "SURROUNDING_OBJECT_STATE",
    ]
    assert supplemental[0].value == {
        "visibility": 300,
        "precipitation": "RAIN",
    }


def test_carla_scenario_context_does_not_mutate_loaded_scenario() -> None:
    environment = _observation(
        "ENVIRONMENT_CONDITIONS",
        {"weather": "CLEAR", "fog": "NONE"},
    )

    CarlaVehicleAdapter._supplemental_scenario_evidence([environment])

    assert environment.value == {"weather": "CLEAR", "fog": "NONE"}
