from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timedelta
from typing import Any

from app.models.schemas import EvidenceNode, EvidenceQualityMetrics, EvidenceStatus, utc_now


class EvidenceQualityService:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.weights = config.get("alignment_weights", {})
        self.freshness_config = config.get("freshness", {})
        self.conflict_config = config.get("conflicts", {})

    def _freshness_parameters(self, evidence_type: str) -> tuple[float, float]:
        default = self.freshness_config.get("default", {})
        specific = self.freshness_config.get(evidence_type, {})
        return (
            float(specific.get("decay_coefficient", default.get("decay_coefficient", 0.02))),
            float(specific.get("validity_seconds", default.get("validity_seconds", 30))),
        )

    @staticmethod
    def _integrity_valid(node: EvidenceNode) -> bool:
        payload = node.metadata.get("integrity_payload")
        if not isinstance(payload, dict):
            return False
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return digest == node.integrity_hash

    def _refresh_node(self, node: EvidenceNode, now: datetime) -> EvidenceNode:
        decay, validity_seconds = self._freshness_parameters(node.evidence_type)
        age_seconds = max(0.0, (now - node.timestamp).total_seconds())
        freshness = max(0.0, min(1.0, math.exp(-decay * age_seconds)))
        expires_at = min(node.expires_at, node.timestamp + timedelta(seconds=validity_seconds))
        if not self._integrity_valid(node):
            label = EvidenceStatus.TAMPERED
        elif node.value is None or node.quality_label == EvidenceStatus.MISSING:
            label = EvidenceStatus.MISSING
        elif now >= expires_at or node.quality_label == EvidenceStatus.STALE:
            label = EvidenceStatus.STALE
        elif node.quality_label == EvidenceStatus.TAMPERED:
            label = EvidenceStatus.TAMPERED
        else:
            label = node.quality_label
        availability = 1.0 if label in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS} else 0.0
        return node.model_copy(
            update={
                "expires_at": expires_at,
                "freshness": round(freshness, 6),
                "availability": availability,
                "quality_label": label,
            }
        )

    @staticmethod
    def _latest_per_source(nodes: list[EvidenceNode], evidence_type: str) -> list[EvidenceNode]:
        latest: dict[str, EvidenceNode] = {}
        for node in nodes:
            if node.evidence_type != evidence_type:
                continue
            current = latest.get(node.source)
            if current is None or (node.timestamp, node.node_id) > (current.timestamp, current.node_id):
                latest[node.source] = node
        return list(latest.values())

    def _detect_conflicts(self, nodes: list[EvidenceNode]) -> list[dict[str, Any]]:
        conflicts: list[dict[str, Any]] = []
        speed_nodes = [
            node
            for node in self._latest_per_source(nodes, "vehicle_speed")
            if isinstance(node.value, (int, float))
            and node.quality_label in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
        ]
        threshold = float(self.conflict_config.get("vehicle_speed_delta", 8.0))
        for left_index, left in enumerate(speed_nodes):
            for right in speed_nodes[left_index + 1 :]:
                delta = abs(float(left.value) - float(right.value))
                if delta > threshold:
                    conflicts.append(
                        {
                            "type": "VEHICLE_SPEED_SOURCE_CONFLICT",
                            "severity": 2,
                            "node_ids": [left.node_id, right.node_id],
                            "evidence_types": ["vehicle_speed"],
                            "reason": f"车速来源差值 {delta:.3f} km/h 超过阈值 {threshold:.3f}",
                        }
                    )

        latest_speed = max(speed_nodes, key=lambda node: node.timestamp, default=None)
        gear_nodes = self._latest_per_source(nodes, "gear_position")
        latest_gear = max(gear_nodes, key=lambda node: node.timestamp, default=None)
        moving_threshold = float(self.conflict_config.get("moving_speed_threshold", 5.0))
        if (
            latest_speed is not None
            and latest_gear is not None
            and float(latest_speed.value) > moving_threshold
            and str(latest_gear.value).upper() == "P"
        ):
            conflicts.append(
                {
                    "type": "GEAR_SPEED_LOGIC_CONFLICT",
                    "severity": 2,
                    "node_ids": [latest_speed.node_id, latest_gear.node_id],
                    "evidence_types": ["vehicle_speed", "gear_position"],
                    "reason": "车辆处于运动速度但挡位为 P",
                }
            )

        door = max(self._latest_per_source(nodes, "door_state"), key=lambda n: n.timestamp, default=None)
        lock = max(
            self._latest_per_source(nodes, "door_lock_state"), key=lambda n: n.timestamp, default=None
        )
        if door is not None and lock is not None and str(door.value).upper() == "OPEN" and str(lock.value).upper() == "LOCKED":
            conflicts.append(
                {
                    "type": "DOOR_LOCK_LOGIC_CONFLICT",
                    "severity": 1,
                    "node_ids": [door.node_id, lock.node_id],
                    "evidence_types": ["door_state", "door_lock_state"],
                    "reason": "车门为 OPEN 但门锁为 LOCKED",
                }
            )

        for evidence_type in ("vehicle_mode", "occupant_role"):
            source_nodes = self._latest_per_source(nodes, evidence_type)
            values = {json.dumps(node.value, ensure_ascii=False, sort_keys=True) for node in source_nodes}
            if len(values) > 1:
                conflicts.append(
                    {
                        "type": f"{evidence_type.upper()}_SOURCE_CONFLICT",
                        "severity": 2,
                        "node_ids": [node.node_id for node in source_nodes],
                        "evidence_types": [evidence_type],
                        "reason": f"{evidence_type} 多来源取值不一致",
                    }
                )
        return conflicts

    def evaluate(
        self,
        nodes: list[EvidenceNode],
        required_types: list[str],
        now: datetime | None = None,
    ) -> tuple[list[EvidenceNode], EvidenceQualityMetrics, list[dict[str, Any]]]:
        evaluated = [self._refresh_node(node, now or utc_now()) for node in nodes]
        conflicts = self._detect_conflicts(evaluated)
        conflict_ids = {node_id for conflict in conflicts for node_id in conflict["node_ids"]}
        evaluated = [
            node.model_copy(
                update={"quality_label": EvidenceStatus.SUSPICIOUS, "consistency": 0.0}
            )
            if node.node_id in conflict_ids and node.quality_label == EvidenceStatus.VALID
            else node
            for node in evaluated
        ]

        required_set = set(required_types)
        coverage_applicable = bool(required_set)
        covered_types = {
            node.evidence_type
            for node in evaluated
            if node.mandatory
            and node.evidence_type in required_set
            and node.quality_label in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
        }
        ecr = len(covered_types) / len(required_set) if coverage_applicable else None

        comparable_pairs = max(1, len(conflicts) + 1)
        ecs = max(0.0, 1.0 - len(conflicts) / comparable_pairs)
        metric_nodes = [node for node in evaluated if node.mandatory] or evaluated
        ef = (
            sum(node.freshness for node in metric_nodes) / len(metric_nodes) if metric_nodes else 1.0
        )
        sas = (
            sum(node.semantic_similarity for node in metric_nodes) / len(metric_nodes)
            if metric_nodes
            else 0.0
        )

        values: dict[str, float] = {"ecs": ecs, "ef": ef, "sas": sas}
        if ecr is not None:
            values["ecr"] = ecr
        active_weights = {name: float(self.weights.get(name, 0)) for name in values}
        weight_sum = sum(active_weights.values())
        eas = (
            sum(values[name] * active_weights[name] for name in values) / weight_sum
            if weight_sum > 0
            else 0.0
        )
        metrics = EvidenceQualityMetrics(
            ecr=(round(ecr, 6) if ecr is not None else None),
            evidence_coverage_applicable=coverage_applicable,
            ecs=round(ecs, 6),
            ef=round(max(0.0, min(1.0, ef)), 6),
            sas=round(max(0.0, min(1.0, sas)), 6),
            eas=round(max(0.0, min(1.0, eas)), 6),
            conflict_count=len(conflicts),
        )
        return evaluated, metrics, conflicts
