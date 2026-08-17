from app.models.schemas import EvidenceObservationInput, VehicleStatePatch
from app.services.vehicle.capabilities import PhysicalVehicleCommand
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


def _speed_observation(source: str, value: float) -> EvidenceObservationInput:
    return EvidenceObservationInput(
        evidence_type="VEHICLE_SPEED", source=source, value=value
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
    assert len(adapter.current_simulation_evidence()) == 1


def test_manual_state_update_replaces_only_matching_scenario_evidence() -> None:
    adapter = SimulatorVehicleAdapter()
    adapter.activate_scenario(
        VehicleStatePatch(vehicle_speed=0, gear_position="P"),
        [
            _speed_observation("speed_a", 0),
            _speed_observation("speed_b", 20),
            _object_observation(),
        ],
    )

    adapter.update_state(VehicleStatePatch(vehicle_speed=30))

    active = adapter.current_simulation_evidence()
    assert adapter.get_state().vehicle_speed == 30
    assert {item.evidence_type for item in active} == {"SURROUNDING_OBJECT_STATE"}


def test_execution_keeps_unrelated_scenario_evidence() -> None:
    adapter = SimulatorVehicleAdapter()
    adapter.activate_scenario(
        VehicleStatePatch(vehicle_speed=0, gear_position="P"),
        [_speed_observation("speed_a", 0), _speed_observation("speed_b", 20)],
    )

    adapter.execute(
        PhysicalVehicleCommand(
            action="打开",
            target="车门",
            area="unknown",
            kind="state_operations",
            operations=(
                {"field": "door_state", "operation": "set", "value": "OPEN"},
            ),
            controls={},
        )
    )

    assert adapter.get_state().door_state == "OPEN"
    assert [item.source for item in adapter.current_simulation_evidence()] == ["speed_a", "speed_b"]


def test_reset_clears_persistent_scenario_evidence() -> None:
    adapter = SimulatorVehicleAdapter()
    adapter.activate_scenario(VehicleStatePatch(), [_object_observation()])

    adapter.reset()

    assert adapter.current_simulation_evidence() == []


def test_manual_simulation_context_replaces_current_observations() -> None:
    adapter = SimulatorVehicleAdapter()

    stored = adapter.set_simulation_evidence([_object_observation()])

    assert stored[0].source == "SIMULATION"
    assert adapter.current_simulation_evidence()[0].evidence_type == "SURROUNDING_OBJECT_STATE"
    adapter.set_simulation_evidence([])
    assert adapter.current_simulation_evidence() == []
