from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from threading import RLock
from typing import Any

from app.models.schemas import (
    EvidenceNode,
    EvidenceObservationInput,
    EvidenceRepositoryStatus,
    EvidenceStatus,
    VehicleState,
    make_id,
    utc_now,
)
from app.services.evidence.catalog import (
    evidence_runtime_mapping,
    require_canonical_evidence_type,
)
from app.services.evidence.value_contract import validate_evidence_value
from app.services.evidence.security_classification import (
    production_security_classification,
)


class EvidenceRepository:
    """维护当前、多源与历史证据流；所有状态均来自实际输入快照或显式观测。"""

    DOOR_PHYSICAL_AREAS = (
        "LEFT_FRONT",
        "RIGHT_FRONT",
        "LEFT_REAR",
        "RIGHT_REAR",
    )

    def __init__(
        self,
        quality_config: dict[str, Any] | None = None,
        retention_config: dict[str, Any] | None = None,
    ) -> None:
        self._lock = RLock()
        self._nodes: dict[str, EvidenceNode] = {}
        self._streams: dict[str, list[str]] = {}
        self._stream_nodes: dict[str, list[str]] = {}
        self._node_stream_keys: dict[str, str] = {}
        self._turn_nodes: dict[str, list[str]] = {}
        self._missing_nodes: dict[tuple[str, str], str] = {}
        self._freshness = (quality_config or {}).get("freshness", {})
        retention = retention_config or {}
        self.dynamic_stream_window = int(retention.get("dynamic_stream_window", 16))
        self.retained_turns = int(retention.get("retained_turns", 64))
        self.cleanup_after_audit = bool(retention.get("cleanup_after_audit", True))
        self.retain_static_nodes = bool(retention.get("retain_static_nodes", True))
        self.retain_rule_nodes = bool(retention.get("retain_rule_nodes", False))
        self._static_evidence_types = set(retention.get("static_evidence_types", []))
        self._static_sources = set(retention.get("static_sources", []))
        self._static_node_ids: set[str] = set()
        self._active_turns: set[str] = set()
        self._turn_order: list[str] = []
        self._evicted_node_count = 0

    @staticmethod
    def _entity_id(node: EvidenceNode) -> str:
        return str(
            node.metadata.get("entity_id")
            or node.metadata.get("rule_id")
            or node.metadata.get("area")
            or "global"
        )

    @classmethod
    def stream_key(cls, node: EvidenceNode) -> str:
        return f"{node.evidence_type}|{node.source}|{cls._entity_id(node)}"

    def _is_static(self, node: EvidenceNode) -> bool:
        return (
            node.evidence_type in self._static_evidence_types
            or node.source in self._static_sources
        )

    @staticmethod
    def _is_ephemeral(node: EvidenceNode) -> bool:
        return (
            node.quality_label == EvidenceStatus.MISSING
            or node.source == "mandatory_recall"
            or bool(node.metadata.get("ephemeral"))
            or bool(node.metadata.get("derived_conflict"))
            or bool(node.metadata.get("explanation_node"))
        )

    def begin_turn(self, turn_id: str) -> None:
        with self._lock:
            self._active_turns.add(turn_id)
            self._turn_nodes.setdefault(turn_id, [])

    def _remove_node(self, node_id: str, *, evicted: bool) -> None:
        node = self._nodes.pop(node_id, None)
        if node is None:
            return
        self._missing_nodes = {
            key: value for key, value in self._missing_nodes.items() if value != node_id
        }
        self._static_node_ids.discard(node_id)
        stream_key = self._node_stream_keys.pop(node_id, None)
        if stream_key is not None:
            retained = [value for value in self._stream_nodes.get(stream_key, []) if value != node_id]
            if retained:
                self._stream_nodes[stream_key] = retained
            else:
                self._stream_nodes.pop(stream_key, None)
        type_nodes = [value for value in self._streams.get(node.evidence_type, []) if value != node_id]
        if type_nodes:
            self._streams[node.evidence_type] = type_nodes
        else:
            self._streams.pop(node.evidence_type, None)
        if evicted:
            self._evicted_node_count += 1

    def _enforce_stream_window(self, stream_key: str) -> None:
        node_ids = self._stream_nodes.get(stream_key, [])
        while len(node_ids) > self.dynamic_stream_window:
            removable_index = next(
                (
                    index
                    for index, node_id in enumerate(node_ids)
                    if str(self._nodes[node_id].metadata.get("turn_id", ""))
                    not in self._active_turns
                ),
                None,
            )
            if removable_index is None:
                break
            self._remove_node(node_ids[removable_index], evicted=True)
            node_ids = self._stream_nodes.get(stream_key, [])

    def complete_turn(self, turn_id: str) -> EvidenceRepositoryStatus:
        """审计保存后清理临时节点，并执行确定性的流与轮次保留。"""
        with self._lock:
            self._active_turns.discard(turn_id)
            if self.cleanup_after_audit:
                for node_id in list(self._turn_nodes.get(turn_id, [])):
                    node = self._nodes.get(node_id)
                    if node is not None and self._is_ephemeral(node):
                        self._remove_node(node_id, evicted=True)
                self._turn_nodes[turn_id] = [
                    node_id
                    for node_id in self._turn_nodes.get(turn_id, [])
                    if node_id in self._nodes
                ]
            for stream_key in list(self._stream_nodes):
                if not any(
                    node_id in self._static_node_ids
                    for node_id in self._stream_nodes.get(stream_key, [])
                ):
                    self._enforce_stream_window(stream_key)
            if turn_id not in self._turn_order:
                self._turn_order.append(turn_id)
            while len(self._turn_order) > self.retained_turns:
                expired_turn = self._turn_order.pop(0)
                self._turn_nodes.pop(expired_turn, None)
            return self.status()

    def _validity_seconds(self, evidence_type: str) -> float:
        default = self._freshness.get("default", {})
        specific = self._freshness.get(evidence_type, {})
        return float(specific.get("validity_seconds", default.get("validity_seconds", 30)))

    @staticmethod
    def _payload(
        evidence_type: str, source: str, value: Any, timestamp: datetime | None
    ) -> dict[str, Any]:
        return {
            "evidence_type": evidence_type,
            "source": source,
            "value": value,
            "timestamp": timestamp.isoformat() if timestamp is not None else None,
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
        timestamp: datetime | None,
        expires_at: datetime | None,
        status: EvidenceStatus | None = None,
        metadata: dict[str, Any] | None = None,
        integrity_valid: bool = True,
    ) -> EvidenceNode:
        require_canonical_evidence_type(evidence_type)
        mapping = evidence_runtime_mapping()[evidence_type]
        security = production_security_classification().info(evidence_type)
        label = status or (EvidenceStatus.MISSING if value is None else EvidenceStatus.VALID)
        validation = validate_evidence_value(evidence_type, value)
        node_metadata = dict(metadata or {})
        if validation.applicable and not validation.usable:
            value = None
            if label != EvidenceStatus.TAMPERED:
                label = EvidenceStatus.MISSING
            node_metadata.update(validation.audit_metadata())
        payload = self._payload(evidence_type, source, value, timestamp)
        expected_hash = self._digest(payload)
        integrity_hash = expected_hash if integrity_valid else "0" * 64
        node_metadata.update(
            {
                "integrity_payload": payload,
                "expected_integrity_hash": expected_hash,
            }
        )
        return EvidenceNode(
            evidence_type=evidence_type,
            layer=security.node_layer_label,
            source=source,
            value=value,
            unit=dict(mapping["value_schema"]).get("unit"),
            timestamp=timestamp,
            expires_at=expires_at,
            freshness=1.0 if label == EvidenceStatus.VALID else 0.0,
            consistency=1.0 if label == EvidenceStatus.VALID else 0.0,
            availability=1.0 if label == EvidenceStatus.VALID else 0.0,
            quality_label=label,
            integrity_hash=integrity_hash,
            metadata=node_metadata,
            security_class=security.name,
            security_rank=security.rank,
            security_classification_source=security.mapping_source,
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
                stream_key = self.stream_key(node)
                self._stream_nodes.setdefault(stream_key, []).append(node.node_id)
                self._node_stream_keys[node.node_id] = stream_key
                if self._is_static(node):
                    self._static_node_ids.add(node.node_id)
                else:
                    self._enforce_stream_window(stream_key)
            if turn_id:
                self._turn_nodes.setdefault(turn_id, []).append(node.node_id)
        return node

    def ingest_vehicle_state(
        self,
        state: VehicleState,
        authorization_fact: dict[str, Any] | None,
        turn_id: str,
    ) -> list[EvidenceNode]:
        values = state.model_dump(mode="json")
        facts: list[tuple[str, Any]] = [
            ("VEHICLE_SPEED", state.vehicle_speed),
            (
                "GEAR_STATE",
                {
                    "current_gear": state.gear_position,
                    "selected_gear": None,
                    "change_mode": None,
                },
            ),
            (
                "SERVICE_BRAKE_STATE",
                {
                    "brake_state": state.brake_state,
                    "emergency_braking_detected": state.emergency_flag,
                },
            ),
            (
                "ROAD_FRICTION_STATE",
                {
                    "road_condition": state.road_condition,
                    "lower_bound": None,
                    "most_probable": None,
                    "upper_bound": None,
                },
            ),
            ("DOOR_STATE", {"state": state.door_state, "position": None}),
            (
                "DOOR_LOCK_STATE",
                {"lock_state": state.door_lock_state, "child_lock_active": None},
            ),
            (
                "WINDOW_STATE",
                {
                    "state": state.window_state,
                    "position": None,
                    "child_lock_active": None,
                },
            ),
            (
                "LIGHTING_STATE",
                {
                    "headlight_state": state.headlight_state,
                    "high_beam": None,
                    "fog": None,
                    "parking": None,
                    "hazard": None,
                    "direction_indicator": None,
                },
            ),
            (
                "WIPER_STATE",
                {
                    "area": "FRONT",
                    "mode": state.wiper_mode,
                    "intensity": state.wiper_intensity,
                    "frequency": state.wiper_frequency,
                    "wiping": state.wiper_wiping,
                    "error": state.wiper_error,
                },
            ),
            (
                "SURROUNDING_OBJECT_STATE",
                {
                    "front_obstacle_distance": state.front_obstacle_distance,
                    "rear_obstacle_distance": state.rear_obstacle_distance,
                    "collision_state": state.collision_state,
                    "objects": state.surrounding_objects or None,
                },
            ),
            ("SPEED_LIMIT_STATE", state.speed_limit),
            (
                "ENVIRONMENT_CONDITIONS",
                {
                    "ambient_illumination": state.ambient_light,
                    "weather": state.weather,
                    "precipitation": None,
                    "fog": None,
                    "time_of_day": None,
                },
            ),
            (
                "AUTHORIZATION_STATE",
                authorization_fact
                or {
                    "authentication_state": state.authentication_state,
                    "authenticated": None,
                    "subject_role": None,
                    "subject_zone": None,
                    "intent_authorizations": [],
                    "authorized_for_request": None,
                },
            ),
            (
                "SYSTEM_MODE",
                {
                    "vehicle_mode": state.vehicle_mode,
                    "safety_constraint": state.safety_constraint,
                },
            ),
        ]
        runtime_mapping = evidence_runtime_mapping()
        now = utc_now()
        nodes: list[EvidenceNode] = []
        for evidence_type, value in facts:
            mapping = runtime_mapping[evidence_type]
            source_fields = list(mapping["source_fields"])
            if evidence_type == "AUTHORIZATION_STATE":
                raw_sources = {
                    "authentication_state": state.authentication_state,
                    "subject_role": value.get("subject_role"),
                    "subject_zone": value.get("subject_zone"),
                    "zone_permission": value.get("intent_authorizations"),
                }
                source_providers = {
                    "authentication_state": "simulator_vehicle_state",
                    "subject_role": "trusted_runtime_context",
                    "subject_zone": "trusted_runtime_context",
                    "zone_permission": "zone_permission_service",
                }
            else:
                raw_sources = {name: values.get(name) for name in source_fields}
                source_providers = {
                    name: "simulator_vehicle_state" for name in source_fields
                }
            areas: tuple[str | None, ...] = (
                self.DOOR_PHYSICAL_AREAS
                if evidence_type == "DOOR_STATE"
                else (None,)
            )
            for area in areas:
                validity = self._validity_seconds(evidence_type)
                metadata = {
                    "turn_id": turn_id,
                    "snapshot_updated_at": state.updated_at.isoformat(),
                    "state_epoch_id": state.state_epoch_id,
                    "provider": mapping["provider"],
                    "source_fields": source_fields,
                    "derivation_method": mapping["derivation"],
                    "raw_sources": raw_sources,
                    "raw_source_providers": source_providers,
                    "source_field_availability": {
                        name: raw_sources.get(name) is not None for name in source_fields
                    },
                }
                if area is not None:
                    metadata["area"] = area
                node = self._make_node(
                    evidence_type=evidence_type,
                    source=str(mapping["provider"]),
                    value=value,
                    timestamp=now,
                    expires_at=now + timedelta(seconds=validity),
                    metadata=metadata,
                )
                nodes.append(self._store(node, turn_id))
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
                integrity_valid=observation.integrity_valid,
                metadata={"turn_id": turn_id, "explicit_observation": True},
            )
            nodes.append(self._store(node, turn_id))
        return nodes

    def get_or_create_missing(
        self,
        evidence_type: str,
        turn_id: str,
        *,
        missing_hard_gate: bool = True,
    ) -> EvidenceNode:
        key = (turn_id, evidence_type)
        with self._lock:
            existing_id = self._missing_nodes.get(key)
            if existing_id is not None and existing_id in self._nodes:
                return self._nodes[existing_id]
            node = self._make_node(
                evidence_type=evidence_type,
                source="missing_placeholder",
                value=None,
                timestamp=None,
                expires_at=None,
                status=EvidenceStatus.MISSING,
                metadata={
                    "turn_id": turn_id,
                    "missing_reason": "required evidence unavailable in current turn",
                    "retrieval_origin": "NONE",
                    "missing_hard_gate": missing_hard_gate,
                    "placeholder_kind": "unavailable",
                },
            )
            # Intent-neutral MISSING 是本轮补召失败的可审计占位节点，不是
            # 外部证据流观测，因此不能进入跨轮召回流或 HNSW。
            stored = self._store(node, turn_id, recallable=False)
            self._missing_nodes[key] = stored.node_id
            return stored

    def latest_observations(self, evidence_type: str) -> list[EvidenceNode]:
        with self._lock:
            node_ids = self._streams.get(evidence_type, [])
            nodes = [self._nodes[node_id] for node_id in node_ids]
        return sorted(
            nodes,
            key=lambda node: (
                node.timestamp.isoformat() if node.timestamp else "",
                node.node_id,
            ),
            reverse=True,
        )

    def latest_per_source(self, evidence_type: str) -> list[EvidenceNode]:
        latest: dict[str, EvidenceNode] = {}
        for node in self.latest_observations(evidence_type):
            latest.setdefault(node.source, node)
        return list(latest.values())

    def recent_per_source(
        self, evidence_type: str, *, limit_per_source: int = 2
    ) -> list[EvidenceNode]:
        """Return bounded source history for the runtime graph only.

        These nodes already exist in the evidence repository.  The caller must
        not upsert this historical view into the global semantic index.
        """
        if limit_per_source < 1:
            return []
        grouped: dict[str, list[EvidenceNode]] = {}
        for node in self.latest_observations(evidence_type):
            source_nodes = grouped.setdefault(node.source, [])
            if len(source_nodes) < limit_per_source:
                source_nodes.append(node)
        return [
            node
            for source in sorted(grouped)
            for node in grouped[source]
        ]

    def latest_resolved(self, evidence_type: str) -> EvidenceNode | None:
        """Return the newest exact-type observation, including abnormal states."""

        observations = self.latest_observations(evidence_type)
        return observations[0] if observations else None

    def latest_resolved_for_area(
        self, evidence_type: str, area: str
    ) -> EvidenceNode | None:
        observations = [
            node
            for node in self.latest_observations(evidence_type)
            if node.metadata.get("area") == area
        ]
        return observations[0] if observations else None

    def all_nodes(self) -> list[EvidenceNode]:
        with self._lock:
            return list(self._nodes.values())

    def update_nodes(self, nodes: list[EvidenceNode]) -> None:
        with self._lock:
            for node in nodes:
                if node.node_id in self._nodes:
                    self._nodes[node.node_id] = node

    def current_nodes(self) -> list[EvidenceNode]:
        with self._lock:
            latest = [
                self._nodes[node_ids[-1]]
                for node_ids in self._stream_nodes.values()
                if node_ids and node_ids[-1] in self._nodes
            ]
        return sorted(
            latest,
            key=lambda node: (node.evidence_type, node.source, self._entity_id(node)),
        )

    def turn_nodes(self, turn_id: str) -> list[EvidenceNode]:
        with self._lock:
            return [
                self._nodes[node_id]
                for node_id in self._turn_nodes.get(turn_id, [])
                if node_id in self._nodes
            ]

    def status(self) -> EvidenceRepositoryStatus:
        with self._lock:
            static_count = len(self._static_node_ids & self._nodes.keys())
            resident_count = len(self._nodes)
            return EvidenceRepositoryStatus(
                resident_node_count=resident_count,
                dynamic_node_count=resident_count - static_count,
                static_node_count=static_count,
                stream_count=sum(bool(node_ids) for node_ids in self._stream_nodes.values()),
                retained_turn_count=len(self._turn_nodes),
                evicted_node_count=self._evicted_node_count,
                retention_window=self.dynamic_stream_window,
            )

    def clear_explicit_observations(self) -> int:
        """Clear scenario/test override streams without touching persisted audit nodes."""
        with self._lock:
            removed = {
                node_id
                for node_id, node in self._nodes.items()
                if bool(node.metadata.get("explicit_observation"))
            }
            for node_id in removed:
                self._remove_node(node_id, evicted=True)
            for turn_id, node_ids in list(self._turn_nodes.items()):
                self._turn_nodes[turn_id] = [
                    node_id for node_id in node_ids if node_id not in removed
                ]
            return len(removed)
