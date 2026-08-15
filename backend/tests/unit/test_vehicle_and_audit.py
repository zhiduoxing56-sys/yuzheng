from __future__ import annotations

import datetime
import hashlib
import json
import sqlite3
import threading

from app.core.config import load_yaml
from app.core.pipeline import CommandPipeline
from app.models.schemas import TextCommandRequest, VehicleState, VehicleStatePatch, utc_now
from app.services.evidence.repository import EvidenceRepository
from app.services.vehicle.carla import CarlaVehicleAdapter
from app.services.vehicle.simulator import SimulatorVehicleAdapter


def test_simulator_update_is_visible_in_snapshot() -> None:
    simulator = SimulatorVehicleAdapter()
    updated = simulator.update_state(VehicleStatePatch(vehicle_speed=37, gear_position="D"))
    snapshot = simulator.get_state()
    assert updated.vehicle_speed == 37
    assert snapshot.vehicle_speed == 37
    assert snapshot.gear_position == "D"


def test_weather_ambient_light_link() -> None:
    """夜间/低照度天气应联动降低环境照度，显式照度不被覆盖。"""
    link = CommandPipeline._link_weather_ambient_light

    night = link(VehicleStatePatch(weather="NIGHT"))
    assert night.ambient_light == CommandPipeline._LOW_LIGHT_AMBIENT_LUX

    sunset = link(VehicleStatePatch(weather="SUNSET"))
    assert sunset.ambient_light == CommandPipeline._LOW_LIGHT_AMBIENT_LUX

    day = link(VehicleStatePatch(weather="CLEAR"))
    assert day.ambient_light == CommandPipeline._HIGH_LIGHT_AMBIENT_LUX

    explicit = link(VehicleStatePatch(weather="NIGHT", ambient_light=90))
    assert explicit.ambient_light == 90

    untouched = link(VehicleStatePatch(vehicle_speed=40))
    assert untouched.ambient_light is None


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


def test_audit_hash_chain_survives_compatible_model_evolution(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="把那个打开"))

    with sqlite3.connect(pipeline.audit_repository.database_path) as connection:
        row = connection.execute(
            "SELECT record_json FROM audit_records WHERE turn_id = ?", (result.turn_id,)
        ).fetchone()
        raw = json.loads(row[0])
        raw["safety_gate_result"].pop("mandatory_evidence_missing")
        raw["score_details"]["evidence_coverage"] = 1.0
        raw["score_details"].pop("evidence_coverage_applicable")
        raw["score_details"].pop("applied_weights")
        raw["final_decision"].pop("final_decision")
        raw["final_decision"].pop("score_decision")
        raw["final_decision"].pop("decision_sources")
        raw["final_decision"].pop("decision_merge_reason")
        raw["final_decision"].pop("soft_safety_score")
        raw["final_decision"]["safety_score"] = 0.6138
        raw["final_decision"]["score_factors"]["evidence_coverage"] = 1.0
        raw["final_decision"]["score_factors"].pop("evidence_coverage_applicable")
        raw["final_decision"]["score_factors"].pop("applied_weights")

        payload = dict(raw)
        payload.pop("previous_hash")
        payload.pop("current_hash")
        digest = hashlib.sha256(
            (
                raw["previous_hash"]
                + json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            ).encode("utf-8")
        ).hexdigest()
        raw["current_hash"] = digest
        connection.execute(
            "UPDATE audit_records SET record_json = ?, current_hash = ? WHERE turn_id = ?",
            (json.dumps(raw, ensure_ascii=False, separators=(",", ":")), digest, result.turn_id),
        )

    restored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert restored is not None
    assert restored.final_decision.soft_safety_score == restored.final_decision.safety_score
    assert restored.final_decision.score_decision == restored.final_decision.decision
    assert restored.final_decision.final_decision == restored.final_decision.decision
    assert restored.final_decision.score_factors.evidence_coverage_applicable is True
    assert pipeline.audit_repository.verify_chain() is True


def test_vehicle_state_sensor_fields_defaults() -> None:
    """VehicleState 传感器字段默认值：无碰撞、无周边对象列表。"""
    state = VehicleState()
    assert state.collision_state == "NONE"
    assert state.collision_target is None
    assert state.collision_at is None
    assert state.surrounding_objects == []


def test_carla_sensor_classify_and_collision_reset() -> None:
    """传感器类型归一化；碰撞事件超过阈值自动复位为 NONE。"""
    assert CarlaVehicleAdapter._classify("vehicle.tesla.model3") == "vehicle"
    assert CarlaVehicleAdapter._classify("walker.pedestrian.0000") == "pedestrian"
    assert CarlaVehicleAdapter._classify("static.prop.trafficcone01") == "obstacle"
    assert CarlaVehicleAdapter._classify("traffic.traffic_light") == "other"

    adapter = object.__new__(CarlaVehicleAdapter)
    adapter._lock = threading.RLock()
    adapter._COLLISION_RESET_SECONDS = 3.0
    adapter._sensor_state = {
        "front_obstacle_distance": 2.0,
        "rear_obstacle_distance": None,
        "collision_state": "COLLIDED",
        "collision_target": "static.prop.trafficcone01",
        "collision_at": utc_now(),
        "surrounding_objects": [],
    }
    # 刚碰撞：保持 COLLIDED
    assert adapter._sensor_snapshot()["collision_state"] == "COLLIDED"
    # 碰撞已过 10 秒：复位 NONE
    adapter._sensor_state["collision_at"] = utc_now() - datetime.timedelta(seconds=10)
    assert adapter._sensor_snapshot()["collision_state"] == "NONE"


def test_surrounding_object_state_flows_into_evidence() -> None:
    """CARLA 扫描到的周边对象应进入 SURROUNDING_OBJECT_STATE 证据的 objects。"""
    state = VehicleState(
        front_obstacle_distance=3.2,
        rear_obstacle_distance=9.0,
        collision_state="NONE",
        collision_target="walker.pedestrian.0000",
        surrounding_objects=[
            {"type": "pedestrian", "distance": 3.2, "ahead": True, "actor_id": 101},
            {"type": "vehicle", "distance": 9.0, "ahead": False, "actor_id": 202},
        ],
    )
    nodes = EvidenceRepository(load_yaml("evidence_quality.yaml")).ingest_vehicle_state(
        state,
        None,
        "TURN_SENSOR_FLOW",
    )
    by_type = {node.evidence_type: node for node in nodes}
    payload = by_type["SURROUNDING_OBJECT_STATE"].value
    assert payload["front_obstacle_distance"] == 3.2
    assert payload["rear_obstacle_distance"] == 9.0
    assert payload["objects"] == state.surrounding_objects
    # 传感器字段保留在 VehicleState 供 get_state/前端读取，但不进 SURROUNDING_OBJECT_STATE 证据
    assert state.collision_target == "walker.pedestrian.0000"
    assert state.collision_at is None
