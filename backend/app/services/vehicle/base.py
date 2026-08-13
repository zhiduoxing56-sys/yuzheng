from __future__ import annotations

from typing import Protocol

from app.models.schemas import VehicleExecutionResult, VehicleState, VehicleStatePatch
from app.services.vehicle.capabilities import PhysicalVehicleCommand


class VehicleAdapter(Protocol):
    adapter_name: str

    def get_state(self) -> VehicleState: ...

    def update_state(self, patch: VehicleStatePatch) -> VehicleState: ...

    def execute(self, command: PhysicalVehicleCommand) -> VehicleExecutionResult: ...

    def get_feedback(self) -> VehicleExecutionResult | None: ...

    def reset(self) -> VehicleState: ...
