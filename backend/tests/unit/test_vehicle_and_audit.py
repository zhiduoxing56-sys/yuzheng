from __future__ import annotations

import sqlite3

from app.models.schemas import TextCommandRequest, VehicleStatePatch
from app.services.vehicle.simulator import SimulatorVehicleAdapter


def test_simulator_update_is_visible_in_snapshot() -> None:
    simulator = SimulatorVehicleAdapter()
    updated = simulator.update_state(VehicleStatePatch(vehicle_speed=37, gear_position="D"))
    snapshot = simulator.get_state()
    assert updated.vehicle_speed == 37
    assert snapshot.vehicle_speed == 37
    assert snapshot.gear_position == "D"


def test_audit_hash_chain_detects_database_tampering(pipeline) -> None:
    pipeline.process_text(TextCommandRequest(text="打开车门"))
    pipeline.process_text(TextCommandRequest(text="把那个打开"))
    assert pipeline.audit_repository.count() == 2
    assert pipeline.audit_repository.verify_chain() is True

    with sqlite3.connect(pipeline.audit_repository.database_path) as connection:
        connection.execute(
            "UPDATE audit_records SET current_hash = ? WHERE rowid = 1",
            ("f" * 64,),
        )
    assert pipeline.audit_repository.verify_chain() is False
