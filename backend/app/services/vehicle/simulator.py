from __future__ import annotations

from threading import RLock
from time import perf_counter
from typing import Any

from app.models.schemas import (
    EvidenceObservationInput,
    VehicleExecutionResult,
    VehicleState,
    VehicleStatePatch,
    make_id,
    utc_now,
)
from app.services.vehicle.capabilities import PhysicalVehicleCommand


class SimulatorVehicleAdapter:
    """线程安全、配置驱动的确定性模拟器；从不发送真实报文。"""

    adapter_name = "simulator"
    supports_multisource_scenario_evidence = True

    _STATE_EVIDENCE_TYPES: dict[str, frozenset[str]] = {
        "vehicle_speed": frozenset({"VEHICLE_SPEED"}),
        "gear_position": frozenset({"GEAR_STATE"}),
        "door_lock_state": frozenset({"DOOR_LOCK_STATE"}),
        "door_state": frozenset({"DOOR_STATE"}),
        "occupant_role": frozenset({"AUTHORIZATION_STATE"}),
        "speaker_zone": frozenset({"AUTHORIZATION_STATE"}),
        "vehicle_mode": frozenset({"SYSTEM_MODE"}),
        "authentication_state": frozenset({"AUTHORIZATION_STATE"}),
        "ambient_light": frozenset({"ENVIRONMENT_CONDITIONS"}),
        "headlight_state": frozenset({"LIGHTING_STATE"}),
        "wiper_mode": frozenset({"WIPER_STATE"}),
        "wiper_intensity": frozenset({"WIPER_STATE"}),
        "wiper_frequency": frozenset({"WIPER_STATE"}),
        "wiper_wiping": frozenset({"WIPER_STATE"}),
        "wiper_error": frozenset({"WIPER_STATE"}),
        "weather": frozenset({"ENVIRONMENT_CONDITIONS"}),
        "window_state": frozenset({"WINDOW_STATE"}),
        "front_obstacle_distance": frozenset({"SURROUNDING_OBJECT_STATE"}),
        "rear_obstacle_distance": frozenset({"SURROUNDING_OBJECT_STATE"}),
        "speed_limit": frozenset({"SPEED_LIMIT_STATE"}),
        "brake_state": frozenset({"SERVICE_BRAKE_STATE"}),
        "road_condition": frozenset({"ROAD_FRICTION_STATE"}),
        "emergency_flag": frozenset({"SERVICE_BRAKE_STATE"}),
        "collision_state": frozenset({"SURROUNDING_OBJECT_STATE"}),
        "safety_constraint": frozenset({"SYSTEM_MODE"}),
    }

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
        self._scenario_evidence: tuple[EvidenceObservationInput, ...] = ()

    def get_state(self) -> VehicleState:
        with self._lock:
            return self._state.model_copy(deep=True)

    def update_state(self, patch: VehicleStatePatch) -> VehicleState:
        # exclude_unset 区分“未提供字段”和“显式设置为 null（证据不可用）”。
        updates = patch.model_dump(exclude_unset=True)
        with self._lock:
            self._discard_scenario_evidence_for_fields(updates)
            state_data = self._state.model_dump()
            state_data.update(updates)
            state_data["updated_at"] = utc_now()
            self._state = VehicleState.model_validate(state_data)
            return self._state.model_copy(deep=True)

    def activate_scenario(
        self,
        patch: VehicleStatePatch,
        evidence: list[EvidenceObservationInput],
    ) -> VehicleState:
        """Replace the single current simulation state, including fine evidence."""

        updates = patch.model_dump(exclude_unset=True)
        with self._lock:
            state_data = self._state.model_dump()
            state_data.update(updates)
            state_data["updated_at"] = utc_now()
            self._state = VehicleState.model_validate(state_data)
            self._scenario_evidence = tuple(
                item.model_copy(deep=True) for item in evidence
            )
            return self._state.model_copy(deep=True)

    def current_simulation_evidence(self) -> list[EvidenceObservationInput]:
        """Return values used to create fresh EvidenceNodes for the next turn."""

        with self._lock:
            return [item.model_copy(deep=True) for item in self._scenario_evidence]

    def set_simulation_evidence(
        self, evidence: list[EvidenceObservationInput]
    ) -> list[EvidenceObservationInput]:
        if any(item.source != "SIMULATION" for item in evidence):
            raise ValueError("manual simulation evidence must use SIMULATION")
        with self._lock:
            self._scenario_evidence = tuple(
                item.model_copy(deep=True) for item in evidence
            )
            return [item.model_copy(deep=True) for item in self._scenario_evidence]

    def _discard_scenario_evidence_for_fields(self, fields: dict[str, Any]) -> None:
        evidence_types = set().union(
            *(self._STATE_EVIDENCE_TYPES.get(field, frozenset()) for field in fields)
        ) if fields else set()
        if evidence_types:
            self._scenario_evidence = tuple(
                item
                for item in self._scenario_evidence
                if item.evidence_type not in evidence_types
            )

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

    def execute(self, command: PhysicalVehicleCommand) -> VehicleExecutionResult:
        started = perf_counter()
        if command.kind != "state_operations" or not command.operations:
            raise ValueError(
                f"模拟器不支持物理命令类型: {command.kind}"
            )
        with self._lock:
            before = self._state.model_copy(deep=True)
            state_data = self._state.model_dump()
            for operation in command.operations:
                self._apply_operation(state_data, operation)
            self._discard_scenario_evidence_for_fields(
                {str(operation["field"]): operation.get("value") for operation in command.operations}
            )
            state_data["updated_at"] = utc_now()
            self._state = VehicleState.model_validate(state_data)
            result = VehicleExecutionResult(
                adapter=self.adapter_name,
                simulated=True,
                status="SUCCEEDED",
                action=command.action,
                target=command.target,
                area=command.area,
                before_state=before,
                after_state=self._state.model_copy(deep=True),
                feedback=f"模拟物理动作已执行：{command.action}{command.target}",
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
            self._scenario_evidence = ()
            return self._state.model_copy(deep=True)
