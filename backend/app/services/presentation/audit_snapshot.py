from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from app.models.frontend_contract import (
    AuditSensorSummary,
    AuditSnapshotFact,
    AuditVehicleSnapshot,
)
from app.models.schemas import AuditRecord, EvidenceNode, EvidenceStatus, VehicleState


_VALID_STATUSES = {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}

_EVIDENCE_FACTS: dict[str, tuple[str, str, str | None, str]] = {
    "VEHICLE_SPEED": ("vehicle_speed", "车速", "km/h", "vehicle"),
    "SPEED_LIMIT_STATE": ("speed_limit", "道路限速", "km/h", "vehicle"),
    "GEAR_STATE": ("gear_position", "挡位", None, "vehicle"),
    "SERVICE_BRAKE_STATE": ("brake_state", "制动", None, "vehicle"),
    "DOOR_STATE": ("door_state", "车门", None, "vehicle"),
    "DOOR_LOCK_STATE": ("door_lock_state", "车门锁", None, "vehicle"),
    "WINDOW_STATE": ("window_state", "车窗", None, "vehicle"),
    "LIGHTING_STATE": ("headlight_state", "前照灯", None, "vehicle"),
    "ENVIRONMENT_CONDITIONS": ("environment", "环境", None, "environment"),
    "SURROUNDING_OBJECT_STATE": ("surroundings", "周边目标", None, "environment"),
    "ROAD_FRICTION_STATE": ("road_condition", "道路", None, "environment"),
}

_STATE_FACTS: tuple[tuple[str, str, str | None, str], ...] = (
    ("vehicle_speed", "车速", "km/h", "vehicle"),
    ("gear_position", "挡位", None, "vehicle"),
    ("brake_state", "制动", None, "vehicle"),
    ("headlight_state", "前照灯", None, "vehicle"),
    ("door_state", "车门", None, "vehicle"),
    ("door_lock_state", "车门锁", None, "vehicle"),
    ("window_state", "车窗", None, "vehicle"),
    ("speed_limit", "道路限速", "km/h", "vehicle"),
    ("ambient_light", "环境光照", "lux", "environment"),
    ("weather", "天气", None, "environment"),
    ("front_obstacle_distance", "前方最近目标", "m", "environment"),
    ("rear_obstacle_distance", "后方最近目标", "m", "environment"),
    ("road_condition", "道路", None, "environment"),
)


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and value.strip().lower() in {
        "",
        "unknown",
        "n/a",
        "not_applicable",
        "--",
    }:
        return False
    return True


def _nested(value: Any, *keys: str) -> Any:
    if not isinstance(value, dict):
        return value
    for key in keys:
        candidate = value.get(key)
        if _present(candidate):
            return candidate
    return None


def _node_facts(node: EvidenceNode) -> list[AuditSnapshotFact]:
    source = node.source or None
    value = node.value
    facts: list[AuditSnapshotFact] = []
    if node.evidence_type == "GEAR_STATE":
        value = _nested(value, "current_gear", "selected_gear")
    elif node.evidence_type == "SERVICE_BRAKE_STATE":
        value = _nested(value, "brake_state")
    elif node.evidence_type == "DOOR_STATE":
        value = _nested(value, "state")
    elif node.evidence_type == "DOOR_LOCK_STATE":
        value = _nested(value, "lock_state")
    elif node.evidence_type == "WINDOW_STATE":
        value = _nested(value, "position", "state")
    elif node.evidence_type == "LIGHTING_STATE":
        value = _nested(value, "headlight_state")
    elif node.evidence_type == "ROAD_FRICTION_STATE":
        value = _nested(value, "road_condition", "most_probable")
    elif node.evidence_type == "ENVIRONMENT_CONDITIONS":
        for key, label, unit in (
            ("time_of_day", "环境", None),
            ("ambient_illumination", "环境光照", "lux"),
            ("weather", "天气", None),
        ):
            candidate = _nested(value, key)
            if _present(candidate):
                facts.append(
                    AuditSnapshotFact(
                        key=key, label=label, value=candidate, unit=unit, source=source
                    )
                )
        return facts
    elif node.evidence_type == "SURROUNDING_OBJECT_STATE":
        for key, label in (
            ("front_obstacle_distance", "前方最近目标"),
            ("rear_obstacle_distance", "后方最近目标"),
        ):
            candidate = _nested(value, key)
            if _present(candidate):
                facts.append(
                    AuditSnapshotFact(
                        key=key, label=label, value=candidate, unit="m", source=source
                    )
                )
        return facts
    definition = _EVIDENCE_FACTS.get(node.evidence_type)
    if definition is None or not _present(value):
        return []
    key, label, unit, _section = definition
    return [AuditSnapshotFact(key=key, label=label, value=value, unit=unit, source=source)]


class AuditSnapshotBuilder:
    """Builds immutable audit views only from facts already persisted for the turn."""

    @staticmethod
    def facts_for_node(node: EvidenceNode) -> list[AuditSnapshotFact]:
        return _node_facts(node)

    @staticmethod
    def from_audit(record: AuditRecord) -> AuditVehicleSnapshot | None:
        nodes = record.evidence_subgraph.nodes if record.evidence_subgraph else []
        eligible = [node for node in nodes if node.quality_label in _VALID_STATUSES]
        if not eligible:
            return None
        captured_at = (
            record.turn_timing.decision_reference_time
            if record.turn_timing is not None
            else max((node.timestamp for node in eligible if node.timestamp), default=record.created_at)
        )
        return AuditSnapshotBuilder._from_nodes(eligible, captured_at=captured_at)

    @staticmethod
    def _from_nodes(
        nodes: Iterable[EvidenceNode], *, captured_at: datetime
    ) -> AuditVehicleSnapshot | None:
        vehicle: dict[str, AuditSnapshotFact] = {}
        environment: dict[str, AuditSnapshotFact] = {}
        sources: set[str] = set()
        sensors: dict[str, AuditSensorSummary] = {}
        for node in nodes:
            definition = _EVIDENCE_FACTS.get(node.evidence_type)
            if definition is None:
                continue
            sources.add(node.source)
            section = definition[3]
            target = vehicle if section == "vehicle" else environment
            for fact in _node_facts(node):
                target.setdefault(fact.key, fact)
            lowered = node.source.lower()
            for marker, label in (
                ("radar", "Radar"),
                ("lidar", "LiDAR"),
                ("camera", "Camera RGB"),
                ("imu", "IMU"),
                ("gnss", "GNSS"),
            ):
                if marker in lowered:
                    sensors.setdefault(
                        label,
                        AuditSensorSummary(sensor=label, source=node.source),
                    )
        if not vehicle and not environment and not sensors:
            return None
        source = ", ".join(sorted(source for source in sources if source)) or "PERSISTED_EVIDENCE"
        return AuditVehicleSnapshot(
            captured_at=captured_at,
            source=source,
            vehicle_state=list(vehicle.values()),
            environment_state=list(environment.values()),
            sensor_summary=list(sensors.values()),
        )

    @staticmethod
    def from_vehicle_state(state: VehicleState, *, source: str) -> AuditVehicleSnapshot:
        vehicle: list[AuditSnapshotFact] = []
        environment: list[AuditSnapshotFact] = []
        for key, label, unit, section in _STATE_FACTS:
            value = getattr(state, key)
            if not _present(value):
                continue
            fact = AuditSnapshotFact(
                key=key, label=label, value=value, unit=unit, source=source
            )
            (vehicle if section == "vehicle" else environment).append(fact)
        return AuditVehicleSnapshot(
            captured_at=state.updated_at,
            source=source,
            vehicle_state=vehicle,
            environment_state=environment,
        )
