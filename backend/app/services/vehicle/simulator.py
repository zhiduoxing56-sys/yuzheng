from __future__ import annotations

from threading import RLock

from app.models.schemas import VehicleState, VehicleStatePatch, utc_now


class SimulatorVehicleAdapter:
    """线程安全、确定性的车辆状态模拟器；阶段一不发送任何车控报文。"""

    def __init__(self, initial_state: VehicleState | None = None) -> None:
        self._lock = RLock()
        self._state = initial_state or VehicleState()

    def get_state(self) -> VehicleState:
        with self._lock:
            return self._state.model_copy(deep=True)

    def update_state(self, patch: VehicleStatePatch) -> VehicleState:
        # exclude_unset 区分“未提供字段”和“显式设置为 null（证据不可用）”。
        updates = patch.model_dump(exclude_unset=True)
        with self._lock:
            state_data = self._state.model_dump()
            state_data.update(updates)
            state_data["updated_at"] = utc_now()
            self._state = VehicleState.model_validate(state_data)
            return self._state.model_copy(deep=True)
