from __future__ import annotations

from typing import Any

from app.models.schemas import VehicleExecutionResult, VehicleState, VehicleStatePatch
from app.services.vehicle.capabilities import PhysicalVehicleCommand


class CanVehicleAdapter:
    """Disabled-by-default CAN boundary; contains no CAN identifiers or send logic."""

    adapter_name = "can_disabled"

    def __init__(self, config: dict[str, Any]) -> None:
        can_config = config.get("can", {})
        self.enabled = bool(can_config.get("enabled", False))
        self.whitelist = list(can_config.get("whitelist", []))
        self._state = VehicleState()

    def get_state(self) -> VehicleState:
        return self._state.model_copy(deep=True)

    def update_state(self, patch: VehicleStatePatch) -> VehicleState:
        del patch
        raise PermissionError("真实 CAN 适配器模式禁止任意修改车辆状态")

    def execute(self, command: PhysicalVehicleCommand) -> VehicleExecutionResult:
        del command
        if not self.enabled or not self.whitelist:
            raise PermissionError("CAN 适配器为 DISABLED，且未配置显式动作白名单")
        raise PermissionError("本阶段不实现真实 CAN 报文发送")

    def get_feedback(self) -> VehicleExecutionResult | None:
        return None

    def reset(self) -> VehicleState:
        raise PermissionError("真实 CAN 适配器模式禁止重置车辆状态")
