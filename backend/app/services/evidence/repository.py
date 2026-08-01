from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from threading import RLock
from typing import Any

from app.models.schemas import (
    EvidenceNode,
    EvidenceObservationInput,
    EvidenceStatus,
    VehicleState,
    make_id,
    utc_now,
)


UNIT_BY_TYPE = {
    "vehicle_speed": "km/h",
    "ambient_light": "lux",
    "front_obstacle_distance": "m",
    "rear_obstacle_distance": "m",
    "ultrasonic_distance": "m",
    "speed_limit": "km/h",
}

LAYER_BY_TYPE = {
    "brake_state": "L3_EMERGENCY",
    "front_obstacle_distance": "L3_EMERGENCY",
    "rear_obstacle_distance": "L3_EMERGENCY",
    "ultrasonic_distance": "L3_EMERGENCY",
    "vehicle_speed": "L2_DRIVING",
    "gear_position": "L2_DRIVING",
    "vehicle_mode": "L2_DRIVING",
    "speed_limit": "L2_DRIVING",
    "road_condition": "L2_DRIVING",
    "surround_camera_state": "L2_DRIVING",
    "occupant_role": "L1_CABIN",
    "speaker_role": "L1_CABIN",
    "speaker_zone": "L1_CABIN",
    "authentication_state": "L1_CABIN",
    "safety_constraint": "L3_EMERGENCY",
    "emergency_flag": "L3_EMERGENCY",
    "door_lock_state": "L1_CABIN",
    "door_state": "L1_CABIN",
    "window_state": "L1_CABIN",
    "headlight_state": "L1_CABIN",
    "ambient_light": "L1_CABIN",
    "weather": "L1_CABIN",
    "display_state": "L0_ENTERTAINMENT",
    "navigation_active": "L0_ENTERTAINMENT",
    "safety_rule": "L3_EMERGENCY",
    "sensor_health": "L2_DRIVING",
    "evidence_stream": "L2_DRIVING",
}

ENVIRONMENT_TYPES = {"ambient_light", "weather", "road_condition", "speed_limit"}
IDENTITY_TYPES = {"occupant_role", "speaker_role", "speaker_zone", "authentication_state"}
SYSTEM_TYPES = {"vehicle_mode", "safety_constraint", "emergency_flag"}


def source_for_type(evidence_type: str) -> str:
    if evidence_type in ENVIRONMENT_TYPES:
        return "environment_sensor"
    if evidence_type in IDENTITY_TYPES:
        return "cabin_identity"
    if evidence_type in SYSTEM_TYPES:
        return "system_context"
    return "simulator_vehicle_state"


class EvidenceRepository:
    """维护当前、多源与历史证据流；所有状态均来自实际输入快照或显式观测。"""

    def __init__(self, quality_config: dict[str, Any] | None = None) -> None:
        self._lock = RLock()
        self._nodes: dict[str, EvidenceNode] = {}
        self._streams: dict[str, list[str]] = {}
        self._turn_nodes: dict[str, list[str]] = {}
        self._freshness = (quality_config or {}).get("freshness", {})

    def _validity_seconds(self, evidence_type: str) -> float:
        default = self._freshness.get("default", {})
        specific = self._freshness.get(evidence_type, {})
        return float(specific.get("validity_seconds", default.get("validity_seconds", 30)))

    @staticmethod
    def _payload(
        evidence_type: str, source: str, value: Any, timestamp: datetime
    ) -> dict[str, Any]:
        return {
            "evidence_type": evidence_type,
            "source": source,
            "value": value,
            "timestamp": timestamp.isoformat(),
        }

    @staticmethod
    def _digest(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _make_node(
        self,
        *,
        evidence_type: str,
        source: str,
        value: Any,
        timestamp: datetime,
        expires_at: datetime,
        mandatory: bool = False,
        status: EvidenceStatus | None = None,
        unit: str | None = None,
        metadata: dict[str, Any] | None = None,
        integrity_valid: bool = True,
    ) -> EvidenceNode:
        label = status or (EvidenceStatus.MISSING if value is None else EvidenceStatus.VALID)
        payload = self._payload(evidence_type, source, value, timestamp)
        expected_hash = self._digest(payload)
        integrity_hash = expected_hash if integrity_valid else "0" * 64
        node_metadata = dict(metadata or {})
        node_metadata.update(
            {
                "integrity_payload": payload,
                "expected_integrity_hash": expected_hash,
            }
        )
        return EvidenceNode(
            evidence_type=evidence_type,
            layer=LAYER_BY_TYPE.get(evidence_type, "L1_CABIN"),
            source=source,
            value=value,
            unit=unit or UNIT_BY_TYPE.get(evidence_type),
            timestamp=timestamp,
            expires_at=expires_at,
            freshness=1.0 if label == EvidenceStatus.VALID else 0.0,
            consistency=1.0 if label == EvidenceStatus.VALID else 0.0,
            availability=1.0 if label == EvidenceStatus.VALID else 0.0,
            semantic_similarity=0.0,
            mandatory=mandatory,
            quality_label=label,
            integrity_hash=integrity_hash,
            metadata=node_metadata,
        )

    def _store(
        self,
        node: EvidenceNode,
        turn_id: str | None = None,
        *,
        recallable: bool = True,
    ) -> EvidenceNode:
        with self._lock:
            self._nodes[node.node_id] = node
            if recallable:
                self._streams.setdefault(node.evidence_type, []).append(node.node_id)
            if turn_id:
                self._turn_nodes.setdefault(turn_id, []).append(node.node_id)
        return node

    def ingest_vehicle_state(
        self, state: VehicleState, command_context: dict[str, Any], turn_id: str
    ) -> list[EvidenceNode]:
        values = state.model_dump(mode="json", exclude={"updated_at"})
        values.update(command_context)
        now = utc_now()
        nodes: list[EvidenceNode] = []
        for evidence_type, value in values.items():
            validity = self._validity_seconds(evidence_type)
            node = self._make_node(
                evidence_type=evidence_type,
                source=source_for_type(evidence_type),
                value=value,
                timestamp=now,
                expires_at=now + timedelta(seconds=validity),
                metadata={"turn_id": turn_id, "snapshot_updated_at": state.updated_at.isoformat()},
            )
            nodes.append(self._store(node, turn_id))

        health_value = {
            key: value is not None
            for key, value in values.items()
            if key not in IDENTITY_TYPES | SYSTEM_TYPES
        }
        health_node = self._make_node(
            evidence_type="sensor_health",
            source="sensor_health_monitor",
            value=health_value,
            timestamp=now,
            expires_at=now + timedelta(seconds=30),
            metadata={"turn_id": turn_id},
        )
        nodes.append(self._store(health_node, turn_id))
        return nodes

    def ingest_observations(
        self, observations: list[EvidenceObservationInput], turn_id: str
    ) -> list[EvidenceNode]:
        nodes: list[EvidenceNode] = []
        observed_at = utc_now()
        for observation in observations:
            timestamp = observed_at - timedelta(seconds=observation.age_seconds)
            validity = (
                observation.expires_in_seconds
                if observation.expires_in_seconds is not None
                else self._validity_seconds(observation.evidence_type)
            )
            expires_at = timestamp + timedelta(seconds=validity)
            if not observation.available:
                status = EvidenceStatus.MISSING
                value = None
            elif not observation.integrity_valid:
                status = EvidenceStatus.TAMPERED
                value = observation.value
            elif expires_at <= observed_at:
                status = EvidenceStatus.STALE
                value = observation.value
            else:
                status = EvidenceStatus.VALID
                value = observation.value
            node = self._make_node(
                evidence_type=observation.evidence_type,
                source=observation.source,
                value=value,
                timestamp=timestamp,
                expires_at=expires_at,
                status=status,
                unit=observation.unit,
                integrity_valid=observation.integrity_valid,
                metadata={"turn_id": turn_id, "explicit_observation": True},
            )
            nodes.append(self._store(node, turn_id))
        return nodes

    def ingest_safety_rules(self, rules: list[dict[str, Any]]) -> list[EvidenceNode]:
        now = utc_now()
        nodes: list[EvidenceNode] = []
        for rule in rules:
            node = self._make_node(
                evidence_type="safety_rule",
                source="safety_rule_config",
                value=rule,
                timestamp=now,
                expires_at=now + timedelta(days=3650),
                metadata={"rule_id": rule.get("id")},
            )
            nodes.append(self._store(node))
        return nodes

    def create_missing(self, evidence_type: str, turn_id: str, reason: str) -> EvidenceNode:
        now = utc_now()
        node = self._make_node(
            evidence_type=evidence_type,
            source="mandatory_recall",
            value=None,
            timestamp=now,
            expires_at=now,
            mandatory=True,
            status=EvidenceStatus.MISSING,
            metadata={"turn_id": turn_id, "missing_reason": reason, "retrieval_origin": "mandatory_recall"},
        )
        # MISSING 是本轮补召失败的可审计占位节点，不是外部证据流观测，
        # 因此不能被后续轮次当作历史传感器证据再次召回。
        return self._store(node, turn_id, recallable=False)

    def latest_observations(self, evidence_type: str) -> list[EvidenceNode]:
        with self._lock:
            node_ids = self._streams.get(evidence_type, [])
            nodes = [self._nodes[node_id] for node_id in node_ids]
        return sorted(nodes, key=lambda node: (node.timestamp, node.node_id), reverse=True)

    def latest_per_source(self, evidence_type: str) -> list[EvidenceNode]:
        latest: dict[str, EvidenceNode] = {}
        for node in self.latest_observations(evidence_type):
            latest.setdefault(node.source, node)
        return list(latest.values())

    def latest_usable(self, evidence_type: str) -> EvidenceNode | None:
        observations = self.latest_observations(evidence_type)
        if not observations:
            return None
        newest_timestamp = observations[0].timestamp
        newest = [node for node in observations if node.timestamp == newest_timestamp]
        usable = [
            node
            for node in newest
            if node.quality_label in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
            and node.expires_at > utc_now()
        ]
        return sorted(usable, key=lambda node: node.node_id)[0] if usable else None

    def all_nodes(self) -> list[EvidenceNode]:
        with self._lock:
            return list(self._nodes.values())

    def update_nodes(self, nodes: list[EvidenceNode]) -> None:
        with self._lock:
            for node in nodes:
                if node.node_id in self._nodes:
                    self._nodes[node.node_id] = node

    def current_nodes(self) -> list[EvidenceNode]:
        latest: dict[tuple[str, str], EvidenceNode] = {}
        for node in self.all_nodes():
            key = (node.evidence_type, node.source)
            current = latest.get(key)
            if current is None or (node.timestamp, node.node_id) > (current.timestamp, current.node_id):
                latest[key] = node
        return sorted(latest.values(), key=lambda node: (node.evidence_type, node.source))

    def turn_nodes(self, turn_id: str) -> list[EvidenceNode]:
        with self._lock:
            return [self._nodes[node_id] for node_id in self._turn_nodes.get(turn_id, [])]

    def from_vehicle_state(
        self,
        state: VehicleState,
        required_types: list[str],
        optional_types: list[str],
        command_context: dict[str, Any],
    ) -> list[EvidenceNode]:
        """保留阶段一直接快照接口；阶段二流水线使用 ingest_vehicle_state。"""
        values = state.model_dump(mode="json")
        values.update(command_context)
        now = utc_now()
        return [
            self._make_node(
                evidence_type=evidence_type,
                source=source_for_type(evidence_type),
                value=values.get(evidence_type),
                timestamp=now,
                expires_at=now + timedelta(seconds=self._validity_seconds(evidence_type)),
                mandatory=evidence_type in required_types,
                metadata={"snapshot_updated_at": state.updated_at.isoformat()},
            )
            for evidence_type in [*required_types, *optional_types]
        ]
