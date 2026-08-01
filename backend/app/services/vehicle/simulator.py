from __future__ import annotations

from threading import RLock
from time import perf_counter
from typing import Any

from app.models.schemas import (
    VehicleExecutionResult,
    VehicleState,
    VehicleStatePatch,
    make_id,
    utc_now,
)


class SimulatorVehicleAdapter:
    """线程安全、配置驱动的确定性模拟器；从不发送真实报文。"""

    adapter_name = "simulator"

    def __init__(
        self,
        initial_state: VehicleState | None = None,
        action_config: dict[str, Any] | None = None,
    ) -> None:
        self._lock = RLock()
        started_at = utc_now()
        base_state = initial_state or VehicleState()
        self._initial_state = base_state.model_copy(
            update={
                "state_epoch_id": make_id("EPOCH"),
                "started_at": started_at,
                "reset_count": 0,
                "last_reset_at": None,
                "reset_reason": "service_started",
                "updated_at": started_at,
            }
        )
        self._state = self._initial_state.model_copy(deep=True)
        self._actions = dict((action_config or {}).get("actions", {}))
        self._last_feedback: VehicleExecutionResult | None = None

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

    @staticmethod
    def _apply_operation(state_data: dict[str, Any], operation: dict[str, Any]) -> None:
        field = str(operation["field"])
        kind = str(operation.get("operation", "set"))
        value = operation.get("value")
        if kind == "set":
            state_data[field] = value
            return
        current = state_data.get(field)
        if not isinstance(current, (int, float)) or not isinstance(value, (int, float)):
            raise ValueError(f"数值操作字段不可用: {field}")
        if kind == "increment":
            updated = current + value
        elif kind == "decrement":
            updated = current - value
        else:
            raise ValueError(f"未知车辆状态操作: {kind}")
        if "minimum" in operation:
            updated = max(float(operation["minimum"]), updated)
        if "maximum" in operation:
            updated = min(float(operation["maximum"]), updated)
        state_data[field] = updated

    def execute(self, action: str, target: str, area: str) -> VehicleExecutionResult:
        started = perf_counter()
        key = f"{action}|{target}"
        mapping = self._actions.get(key)
        if mapping is None:
            raise ValueError(f"模拟器不支持车辆动作: {key}")
        with self._lock:
            before = self._state.model_copy(deep=True)
            state_data = self._state.model_dump()
            for operation in mapping.get("operations", []):
                self._apply_operation(state_data, operation)
            state_data["updated_at"] = utc_now()
            self._state = VehicleState.model_validate(state_data)
            result = VehicleExecutionResult(
                adapter=self.adapter_name,
                simulated=True,
                status="SUCCEEDED",
                action=action,
                target=target,
                area=area,
                before_state=before,
                after_state=self._state.model_copy(deep=True),
                feedback=str(mapping.get("feedback", "模拟动作已执行")),
                duration_ms=round((perf_counter() - started) * 1000, 4),
            )
            self._last_feedback = result
            return result

    def get_feedback(self) -> VehicleExecutionResult | None:
        with self._lock:
            return self._last_feedback.model_copy(deep=True) if self._last_feedback else None

    def reset(self, reason: str = "manual_reset") -> VehicleState:
        with self._lock:
            reset_at = utc_now()
            next_count = self._state.reset_count + 1
            self._state = self._initial_state.model_copy(
                deep=True,
                update={
                    "state_epoch_id": make_id("EPOCH"),
                    "started_at": reset_at,
                    "reset_count": next_count,
                    "last_reset_at": reset_at,
                    "reset_reason": reason,
                    "updated_at": reset_at,
                },
            )
            self._last_feedback = None
            return self._state.model_copy(deep=True)
