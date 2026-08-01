from __future__ import annotations

from typing import Any

from app.models.schemas import VehicleExecutionResult, VehicleState
from app.services.vehicle.simulator import SimulatorVehicleAdapter


class MockBenchAdapter(SimulatorVehicleAdapter):
    """No-hardware bench adapter with deterministic simulated feedback."""

    adapter_name = "mock_bench"

    def __init__(
        self,
        initial_state: VehicleState | None = None,
        action_config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(initial_state, action_config)

    def execute(self, action: str, target: str, area: str) -> VehicleExecutionResult:
        result = super().execute(action, target, area)
        updated = result.model_copy(
            update={"feedback": f"确定性台架模拟反馈：{result.feedback}", "simulated": True}
        )
        with self._lock:
            self._last_feedback = updated
        return updated
