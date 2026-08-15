from __future__ import annotations

import math
import threading
import time
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
from app.services.vehicle.capabilities import PhysicalVehicleCommand


class CarlaVehicleAdapter:
    """连接云服务器上的 CARLA 模拟器；把语证动作映射为真实车辆控制，并回读真实状态。

    CARLA 0.9.16 限制（如实保留）：
      - 无 set_door_open_state：车门/车窗/大屏/音乐等动作只更新镜像状态，无物理动画。
      - 车速用 throttle/brake 比例控制逼近，是“接近”而非精确瞬移。
      - CARLA 断开时 get_state 回退镜像状态，health 的 adapter_name 如实反映。
    """

    adapter_name = "carla"

    # 该 CARLA 0.9.16 构建的可用预设：无 RainyNoon/FoggyNoon，雨天用 MidRainyNoon，
    # 雾天无预设，改用自定义 WeatherParameters(fog_density=80)。
    WEATHER_MAP = {
        "CLEAR": "ClearNoon",
        "CLOUDY": "CloudyNoon",
        "RAIN": "MidRainyNoon",
        "NIGHT": "ClearNight",
        "SUNSET": "ClearSunset",
    }

    # 传感器扫描关注的相关 actor 前缀：车辆 / 行人 / 静态障碍物。
    _OBSTACLE_ACTOR_PREFIXES = (
        "vehicle.",
        "walker.pedestrian.",
        "static.prop.",
    )
    # 碰撞后延迟复位为 NONE 的秒数，避免状态永远粘住。
    _COLLISION_RESET_SECONDS = 3.0

    def __init__(
        self,
        action_config: dict[str, Any] | None = None,
        *,
        host: str = "127.0.0.1",
        port: int = 2000,
        timeout: float = 10.0,
        autopilot_port: int = 8000,
    ) -> None:
        import carla

        self._carla = carla
        self._lock = RLock()
        self._actions = dict((action_config or {}).get("actions", {}))
        self._last_feedback: VehicleExecutionResult | None = None
        self._connected = False

        started_at = utc_now()
        base_state = VehicleState()
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
        self._mirror = self._initial_state.model_copy(deep=True)
        self._spawned_obstacles: list[Any] = []
        self._obstacle_counter = 0
        self._cleanup_stale_obstacles()

        self._client = carla.Client(host, port)
        self._client.set_timeout(float(timeout))
        self._world = self._client.get_world()
        self._autopilot_port = int(autopilot_port)
        self._vehicle = self._find_or_spawn_vehicle()
        if self._vehicle is None:
            raise RuntimeError("CARLA 中无法找到或生成车辆")
        self._connected = True
        # 默认假设车辆处于自动驾驶；后续 set_autopilot 调用会同步更新此标志
        self._autopilot_enabled = True
        # —— 传感器子系统（碰撞 + 障碍物/行人扫描）——
        self._sensor_state: dict[str, Any] = {
            "front_obstacle_distance": None,
            "rear_obstacle_distance": None,
            "collision_state": "NONE",
            "collision_target": None,
            "collision_at": None,
            "surrounding_objects": [],
        }
        self._collision_sensor: Any | None = None
        self._ensure_collision_sensor()
        threading.Thread(target=self._scan_surroundings, daemon=True).start()
        threading.Thread(target=self._stuck_monitor, daemon=True).start()

    # ------------------------------------------------------------------ 内部

    def _find_or_spawn_vehicle(self) -> Any | None:
        for actor in self._world.get_actors().filter("vehicle.*"):
            if actor.is_alive:
                return actor
        blueprints = self._world.get_blueprint_library().filter("vehicle.tesla.model3")
        if not blueprints:
            blueprints = self._world.get_blueprint_library().filter("vehicle.*")
        for spawn_point in self._world.get_map().get_spawn_points():
            vehicle = self._world.try_spawn_actor(blueprints[0], spawn_point)
            if vehicle is not None:
                return vehicle
        return None

    def _current_speed_kmh(self) -> float:
        velocity = self._vehicle.get_velocity()
        return math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2) * 3.6

    def _apply_weather(self, code: str) -> None:
        if code == "FOG":
            # 该构建无 FoggyNoon 预设，构造自定义大雾天气
            self._world.set_weather(
                self._carla.WeatherParameters(
                    cloudiness=50.0,
                    precipitation=0.0,
                    fog_density=80.0,
                    fog_distance=15.0,
                )
            )
            return
        preset = self.WEATHER_MAP.get(code)
        if preset is None:
            return
        weather = getattr(self._carla.WeatherParameters, preset, None)
        if weather is None:
            return
        self._world.set_weather(weather)

    def _weather_to_code(self, weather: Any) -> str:
        precipitation = float(weather.precipitation or 0)
        fog = float(weather.fog_density or 0)
        cloudiness = float(weather.cloudiness or 0)
        try:
            sun = float(getattr(weather, "sun_altitude_angle", 90) or 90)
        except Exception:
            sun = 90.0
        # 先用太阳高度区分昼夜/黄昏：夜间预设(ClearNight)的 fog_density 也偏高，
        # 若用 fog 判断会误判为 FOG
        if sun < -5:
            return "NIGHT"
        if sun < 18:
            return "SUNSET"
        if precipitation > 20:
            return "RAIN"
        if fog > 20:
            return "FOG"
        if cloudiness > 40:
            return "CLOUDY"
        return "CLEAR"

    def _apply_headlight(self, on: bool) -> None:
        # CARLA 0.9.16 的 VehicleLightState 不支持位运算 int，直接设 LowBeam / NONE
        self._vehicle.set_light_state(
            self._carla.VehicleLightState.LowBeam if on else self._carla.VehicleLightState.NONE
        )

    def _apply_control_impulse(
        self, throttle: float, brake: float, duration_s: float
    ) -> None:
        def run() -> None:
            try:
                self._vehicle.set_autopilot(False)
                self._autopilot_enabled = False
                self._vehicle.apply_control(
                    self._carla.VehicleControl(throttle=float(throttle), brake=float(brake))
                )
                time.sleep(float(duration_s))
                self._vehicle.apply_control(self._carla.VehicleControl())
                self._vehicle.set_autopilot(True)
                self._autopilot_enabled = True
            except Exception:
                pass

        threading.Thread(target=run, daemon=True).start()

    def _drive_to_speed(self, target_kmh: float) -> None:
        def run() -> None:
            try:
                self._vehicle.set_autopilot(False)
                self._autopilot_enabled = False
                for _ in range(90):  # 最长 ~9 秒
                    speed = self._current_speed_kmh()
                    diff = target_kmh - speed
                    control = self._carla.VehicleControl()
                    if diff > 3.0:
                        control.throttle = min(0.8, 0.25 + abs(diff) / 80.0)
                    elif diff < -3.0:
                        control.brake = min(0.9, 0.15 + abs(diff) / 80.0)
                    else:
                        control.throttle = 0.3
                    self._vehicle.apply_control(control)
                    time.sleep(0.1)
                    if abs(diff) <= 3.0 and speed > 1.0:
                        break  # 已达目标速度
                self._vehicle.apply_control(self._carla.VehicleControl())
                # 目标速度 0 → 保持驻车(状态稳定,便于指令执行)；>0 → 恢复自动驾驶
                if target_kmh > 0:
                    self._vehicle.set_autopilot(True)
                    self._autopilot_enabled = True
            except Exception:
                pass

        threading.Thread(target=run, daemon=True).start()

    # ------------------------------------------------------------ 环境控制

    def _point_ahead(self, distance: float = 20.0) -> Any:
        transform = self._vehicle.get_transform()
        yaw_rad = math.radians(transform.rotation.yaw)
        location = self._carla.Location(
            x=transform.location.x + distance * math.cos(yaw_rad),
            y=transform.location.y + distance * math.sin(yaw_rad),
            z=transform.location.z + 0.5,
        )
        return self._carla.Transform(location, transform.rotation)

    def _road_point_ahead(self, distance: float = 30.0) -> Any | None:
        """找一个位于自车前方、且在同一条车道方向上的道路点(供车辆障碍生成)。

        优先用地图 waypoint 沿当前车道前进(保证在道路上，任意停车位可用)；
        失败再回退到放宽横向/前方条件的 spawn point 搜索。
        """
        transform = self._vehicle.get_transform()
        try:
            waypoint = self._world.get_map().get_waypoint(transform.location)
            target: Any = waypoint
            traveled = 0.0
            while traveled < distance:
                nxt = target.next(5.0)
                if not nxt:
                    break
                target = nxt[0]
                traveled += 5.0
            if target is not None:
                return target.transform
        except Exception:
            pass
        # 回退：前方一定范围、横向容忍较大的最近 spawn point
        yaw_rad = math.radians(transform.rotation.yaw)
        forward = (math.cos(yaw_rad), math.sin(yaw_rad))
        best: Any | None = None
        best_score = float("inf")
        for spawn in self._world.get_map().get_spawn_points():
            dx = spawn.location.x - transform.location.x
            dy = spawn.location.y - transform.location.y
            ahead = dx * forward[0] + dy * forward[1]
            lateral = abs(-dx * forward[1] + dy * forward[0])
            if ahead > 5 and lateral < 12:
                score = lateral + abs(ahead - distance)
                if score < best_score:
                    best_score = score
                    best = spawn
        return best

    def _road_points_ahead(self, distance: float = 40.0, count: int = 8) -> list[Any]:
        """沿当前车道返回一系列候选道路点(从近到远)，供车辆障碍生成逐个尝试。"""
        try:
            waypoint = self._world.get_map().get_waypoint(
                self._vehicle.get_transform().location
            )
        except Exception:
            return []
        points: list[Any] = []
        target: Any = waypoint
        traveled = 0.0
        while len(points) < count and traveled < distance + 20:
            nxt = target.next(5.0)
            if not nxt:
                break
            target = nxt[0]
            traveled += 5.0
            if traveled >= 8:  # 跳过太近的位置
                points.append(target.transform)
        return points

    def _ordered_vehicle_spawns(self, limit: int = 20) -> list[Any]:
        """返回自车前方按(横向偏移+距离)排序的地图车辆出生点，供障碍车逐个尝试。

        地图 spawn_points 是车辆可出生位置；按前方优先、横向接近排序，
        第一个能成功 spawn 的位置即为有效点(waypoint 点常因车辆碰撞体放不下)。
        """
        transform = self._vehicle.get_transform()
        yaw_rad = math.radians(transform.rotation.yaw)
        forward = (math.cos(yaw_rad), math.sin(yaw_rad))
        scored: list[tuple[float, Any]] = []
        for spawn in self._world.get_map().get_spawn_points():
            dx = spawn.location.x - transform.location.x
            dy = spawn.location.y - transform.location.y
            ahead = dx * forward[0] + dy * forward[1]
            if ahead <= 5:
                continue
            lateral = abs(-dx * forward[1] + dy * forward[0])
            scored.append((lateral + ahead, spawn))
        scored.sort(key=lambda item: item[0])
        return [spawn for _, spawn in scored[:limit]]

    def _cleanup_stale_obstacles(self) -> None:
        """清理可能遗留的障碍物 actor（后端重启后 _spawned_obstacles 丢失追踪）。

        只清理本适配器会生成的类型（行人 / 交通锥），不动地图默认装饰。
        """
        try:
            for actor in self._world.get_actors():
                if actor.type_id.startswith("walker.pedestrian") or actor.type_id == "static.prop.trafficcone01":
                    if actor.is_alive:
                        actor.destroy()
        except Exception:
            pass

    def spawn_obstacle(self, kind: str) -> bool:
        """在自车前方生成障碍物：pedestrian 行人 / vehicle 车辆 / obstacle 静态物。"""
        blueprints = self._world.get_blueprint_library()
        try:
            if kind == "pedestrian":
                candidates = blueprints.filter("walker.pedestrian.*")
                blueprint = candidates[self._obstacle_counter % len(candidates)]
                location = self._point_ahead(20.0)
            elif kind == "vehicle":
                candidates = blueprints.filter("vehicle.tesla.model3")
                if not candidates:
                    candidates = blueprints.filter("vehicle.*")
                blueprint = candidates[self._obstacle_counter % len(candidates)]
                self._obstacle_counter += 1
                # 用地图车辆出生点(保证可 spawn)沿前方逐个尝试
                for spawn in self._ordered_vehicle_spawns():
                    actor = self._world.try_spawn_actor(blueprint, spawn)
                    if actor is not None:
                        self._spawned_obstacles.append(actor)
                        return True
                return False
            elif kind == "obstacle":
                candidates = blueprints.filter("static.prop.trafficcone01")
                if not candidates:
                    candidates = blueprints.filter("static.prop.*")
                blueprint = candidates[self._obstacle_counter % len(candidates)]
                location = self._point_ahead(20.0)
            else:
                return False
        except Exception:
            return False
        self._obstacle_counter += 1
        actor = self._world.try_spawn_actor(blueprint, location)
        if actor is None:
            return False
        self._spawned_obstacles.append(actor)
        return True

    def clear_obstacles(self) -> int:
        cleared = 0
        for actor in list(self._spawned_obstacles):
            try:
                if actor.is_alive:
                    actor.destroy()
                cleared += 1
            except Exception:
                pass
        self._spawned_obstacles.clear()
        return cleared

    def obstacle_count(self) -> int:
        return len(self._spawned_obstacles)

    def _teleport_to_safe_spawn(self) -> None:
        """把车传送到可靠出生点(第 0 个)并重新启用自动驾驶，用于脱困/复位。"""
        spawn_points = self._world.get_map().get_spawn_points()
        if not spawn_points:
            return
        try:
            self._vehicle.set_autopilot(False)
            self._autopilot_enabled = False
            self._vehicle.set_simulate_physics(False)
            self._vehicle.set_transform(spawn_points[0])
            time.sleep(0.2)
            self._vehicle.set_simulate_physics(True)
            self._vehicle.apply_control(self._carla.VehicleControl())
            time.sleep(0.5)
            self._vehicle.set_autopilot(True, self._autopilot_port)
            self._autopilot_enabled = True
        except Exception:
            self._connected = False

    def _stuck_monitor(self) -> None:
        """后台线程：自动驾驶中低速且不在红绿灯连续超过 15 秒 → 判定卡住，自动传送到可靠出生点。

        手动驻车(autopilot 关闭)不算卡住，避免误传送破坏驻车状态。
        """
        low_speed_since: float | None = None
        while True:
            time.sleep(3)
            try:
                speed = self._current_speed_kmh()
                at_light = bool(self._vehicle.is_at_traffic_light())
                if speed < 1.0 and not at_light and self._autopilot_enabled:
                    if low_speed_since is None:
                        low_speed_since = time.time()
                    elif time.time() - low_speed_since > 15:
                        self._teleport_to_safe_spawn()
                        low_speed_since = None
                else:
                    low_speed_since = None
            except Exception:
                pass

    def set_traffic_light(self, state: str) -> bool:
        """把全部交通灯设为指定状态 RED / GREEN / YELLOW。"""
        lights = list(self._world.get_actors().filter("traffic.traffic_light"))
        if not lights:
            return False
        state_map = {
            "RED": self._carla.TrafficLightState.Red,
            "GREEN": self._carla.TrafficLightState.Green,
            "YELLOW": self._carla.TrafficLightState.Yellow,
        }
        selected = state_map.get(state.upper())
        if selected is None:
            return False
        for light in lights:
            try:
                light.set_state(selected)
            except Exception:
                pass
        return True

    # ------------------------------------------------------------------ 传感器

    @staticmethod
    def _classify(type_id: str) -> str:
        """把 CARLA actor type_id 归一化为 vehicle / pedestrian / obstacle。"""
        if type_id.startswith("vehicle."):
            return "vehicle"
        if type_id.startswith("walker.pedestrian."):
            return "pedestrian"
        if type_id.startswith("static.prop."):
            return "obstacle"
        return "other"

    def _ensure_collision_sensor(self) -> None:
        """确保碰撞传感器已挂到自车；失败置 None 由扫描线程重试。"""
        if self._vehicle is None or not self._vehicle.is_alive:
            return
        if self._collision_sensor is not None and self._collision_sensor.is_alive:
            return
        try:
            blueprint = self._world.get_blueprint_library().find(
                "sensor.other.collision"
            )
            blueprint.set_attribute("sensor_tick", "0.5")
            sensor = self._world.spawn_actor(
                blueprint,
                self._carla.Transform(self._carla.Location(x=0, y=0, z=0)),
                attach_to=self._vehicle,
            )
            sensor.listen(self._on_collision)
            self._collision_sensor = sensor
        except Exception:
            self._collision_sensor = None

    def _on_collision(self, event: Any) -> None:
        """碰撞回调：记录碰撞状态、对象类型与时间。"""
        other = getattr(event, "other_actor", None)
        with self._lock:
            self._sensor_state["collision_state"] = "COLLIDED"
            self._sensor_state["collision_target"] = (
                other.type_id if other is not None else None
            )
            self._sensor_state["collision_at"] = utc_now()

    def _scan_surroundings(self) -> None:
        """低频(~5Hz)遍历场景 actor，维护前后最近障碍物与 surrounding_objects。"""
        while True:
            time.sleep(0.2)
            try:
                if self._vehicle is None or not self._vehicle.is_alive:
                    continue
                self._ensure_collision_sensor()
                transform = self._vehicle.get_transform()
                vehicle_loc = transform.location
                yaw = math.radians(transform.rotation.yaw)
                forward = (math.cos(yaw), math.sin(yaw))
                front: tuple[int, float] | None = None
                rear: tuple[int, float] | None = None
                objects: list[dict[str, Any]] = []
                for actor in self._world.get_actors():
                    try:
                        if actor.id == self._vehicle.id or not actor.is_alive:
                            continue
                        type_id = actor.type_id
                        if not type_id.startswith(self._OBSTACLE_ACTOR_PREFIXES):
                            continue
                        loc = actor.get_location()
                        dx = loc.x - vehicle_loc.x
                        dy = loc.y - vehicle_loc.y
                        dist = math.hypot(dx, dy)
                        dot = dx * forward[0] + dy * forward[1]
                        objects.append(
                            {
                                "type": self._classify(type_id),
                                "distance": round(dist, 1),
                                "ahead": dot >= 0,
                                "actor_id": actor.id,
                            }
                        )
                        if dot >= 0 and (front is None or dist < front[1]):
                            front = (actor.id, dist)
                        elif dot < 0 and (rear is None or dist < rear[1]):
                            rear = (actor.id, dist)
                    except Exception:
                        continue
                with self._lock:
                    self._sensor_state["front_obstacle_distance"] = (
                        round(front[1], 1) if front is not None else None
                    )
                    self._sensor_state["rear_obstacle_distance"] = (
                        round(rear[1], 1) if rear is not None else None
                    )
                    self._sensor_state["surrounding_objects"] = objects
            except Exception:
                with self._lock:
                    self._connected = False

    def _sensor_snapshot(self) -> dict[str, Any]:
        """返回传感器状态快照；碰撞超过 3 秒自动复位 COLLIDED → NONE。"""
        with self._lock:
            snapshot = dict(self._sensor_state)
        if snapshot.get("collision_at") is not None:
            age = (utc_now() - snapshot["collision_at"]).total_seconds()
            if age > self._COLLISION_RESET_SECONDS:
                snapshot["collision_state"] = "NONE"
        return snapshot

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

    # ------------------------------------------------------------- Protocol

    def get_state(self) -> VehicleState:
        with self._lock:
            state_data = self._mirror.model_dump()
            try:
                if self._vehicle is not None:
                    state_data["vehicle_speed"] = round(self._current_speed_kmh(), 1)
                    gear = self._vehicle.get_control().gear
                    if gear >= 1:
                        state_data["gear_position"] = "D"
                    elif gear <= -1:
                        state_data["gear_position"] = "R"
                    control = self._vehicle.get_control()
                    state_data["brake_state"] = "ACTIVE" if control.brake > 0.05 else "RELEASED"
                    light = self._vehicle.get_light_state()
                    state_data["headlight_state"] = (
                        "ON" if light == self._carla.VehicleLightState.LowBeam else "OFF"
                    )
                    state_data["weather"] = self._weather_to_code(self._world.get_weather())
                    # 全量合并传感器快照：无障碍方向 front/rear 显式置 None，
                    # 避免默认值 100 被前端误判为 100m 障碍
                    state_data.update(self._sensor_snapshot())
                    state_data["updated_at"] = utc_now()
                    self._connected = True
            except Exception:
                self._connected = False
            return VehicleState.model_validate(state_data)

    def update_state(self, patch: VehicleStatePatch) -> VehicleState:
        updates = patch.model_dump(exclude_unset=True)
        with self._lock:
            if updates.get("weather") is not None:
                try:
                    self._apply_weather(str(updates["weather"]))
                except Exception:
                    self._connected = False
            if updates.get("headlight_state") is not None:
                try:
                    self._apply_headlight(str(updates["headlight_state"]) == "ON")
                except Exception:
                    self._connected = False
            target_speed = updates.pop("vehicle_speed", None)
            state_data = self._mirror.model_dump()
            for key, value in updates.items():
                if key in state_data:
                    state_data[key] = value
            state_data["updated_at"] = utc_now()
            self._mirror = VehicleState.model_validate(state_data)
        if target_speed is not None:
            try:
                self._drive_to_speed(float(target_speed))
            except Exception:
                self._connected = False
        return self.get_state()

    def execute(self, command: PhysicalVehicleCommand) -> VehicleExecutionResult:
        started = perf_counter()
        before = self.get_state()
        if command.kind == "state_operations" and command.operations:
            with self._lock:
                state_data = self._mirror.model_dump()
                for operation in command.operations:
                    self._apply_operation(state_data, operation)
                state_data["updated_at"] = utc_now()
                self._mirror = VehicleState.model_validate(state_data)
            feedback = f"CARLA 镜像物理动作已执行：{command.action}{command.target}"
        elif command.kind == "carla_control" and command.controls:
            controls = command.controls
            try:
                if "light_on" in controls or "light_off" in controls:
                    self._apply_headlight(bool(controls.get("light_on")))
                elif "throttle" in controls or "brake" in controls:
                    self._apply_control_impulse(
                        float(controls.get("throttle", 0.0)),
                        float(controls.get("brake", 0.0)),
                        float(controls.get("duration_s", 1.0)),
                    )
                else:
                    raise ValueError(
                        f"未知 CARLA 物理控制: {sorted(controls)}"
                    )
                feedback = f"动作已在 CARLA 中执行：{command.action}{command.target}"
            except Exception as exc:
                raise RuntimeError(f"CARLA 执行失败: {type(exc).__name__}: {exc}") from exc
        else:
            raise ValueError(f"CARLA 不支持物理命令类型: {command.kind}")
        after = self.get_state()
        result = VehicleExecutionResult(
            adapter=self.adapter_name,
            simulated=True,
            status="SUCCEEDED",
            action=command.action,
            target=command.target,
            area=command.area,
            before_state=before,
            after_state=after,
            feedback=feedback,
            duration_ms=round((perf_counter() - started) * 1000, 4),
        )
        with self._lock:
            self._last_feedback = result
        return result

    def get_feedback(self) -> VehicleExecutionResult | None:
        with self._lock:
            return self._last_feedback.model_copy(deep=True) if self._last_feedback else None

    def reset(self, reason: str = "manual_reset") -> VehicleState:
        with self._lock:
            reset_at = utc_now()
            next_count = self._mirror.reset_count + 1
            self._mirror = self._initial_state.model_copy(
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
            # 复位后传感器环境已变，清空碰撞痕迹，障碍物由扫描线程重新计算
            self._sensor_state["collision_state"] = "NONE"
            self._sensor_state["collision_target"] = None
            self._sensor_state["collision_at"] = None
            try:
                self._world.set_weather(self._carla.WeatherParameters.ClearNoon)
                self._apply_headlight(False)
                self._teleport_to_safe_spawn()
            except Exception:
                self._connected = False
            return self.get_state()

    def close(self) -> None:
        """销毁碰撞传感器；供进程退出/适配器更换时的清理钩子调用。"""
        with self._lock:
            sensor, self._collision_sensor = self._collision_sensor, None
        if sensor is not None:
            try:
                if sensor.is_alive:
                    sensor.stop()
                sensor.destroy()
            except Exception:
                pass
