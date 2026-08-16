from app.models.schemas import EvidenceObservationInput, VehicleStatePatch
from app.services.vehicle.simulator import SimulatorVehicleAdapter


def _object_observation() -> EvidenceObservationInput:
    return EvidenceObservationInput(
        evidence_type="SURROUNDING_OBJECT_STATE",
        source="SIMULATION",
        value={
            "objects": [
                {
                    "entity_kind": "BICYCLE",
                    "region": "REAR_RIGHT",
                    "distance": 3.0,
                    "relative_speed": -5.0,
                    "motion_state": "APPROACHING",
                    "risk_level": "HIGH",
                }
            ]
        },
    )


def test_scenario_evidence_lives_in_the_single_simulator_state_provider() -> None:
    adapter = SimulatorVehicleAdapter()

    adapter.activate_scenario(
        VehicleStatePatch(vehicle_speed=42, gear_position="D"),
        [_object_observation()],
    )

    assert adapter.get_state().vehicle_speed == 42
    active = adapter.current_simulation_evidence()
    assert len(active) == 1
    assert active[0].source == "SIMULATION"
    assert active[0].value["objects"][0]["region"] == "REAR_RIGHT"

    adapter.update_state(VehicleStatePatch(vehicle_speed=0))
    assert adapter.current_simulation_evidence() == []


def test_reset_clears_persistent_scenario_evidence() -> None:
    adapter = SimulatorVehicleAdapter()
    adapter.activate_scenario(VehicleStatePatch(), [_object_observation()])

    adapter.reset()

    assert adapter.current_simulation_evidence() == []
