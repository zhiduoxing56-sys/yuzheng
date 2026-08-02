from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timedelta
from typing import Any

from app.models.schemas import EvidenceNode, EvidenceQualityMetrics, EvidenceStatus, utc_now


class EvidenceQualityService:
    ECS_AUXILIARY_TYPES = {
        "semantic_frame",
        "instruction",
        "evidence_demand",
        "control_target",
        "frontend_display",
        "conflict_event",
        "evidence_stream",
    }

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.weights = config.get("alignment_weights", {})
        self.profiles = config.get("alignment_profiles", {"default": self.weights})
        self.profile_selection = config.get("profile_selection", {})
        self.freshness_config = config.get("freshness", {})
        self.conflict_config = config.get("conflicts", {})
        for name, weights in self.profiles.items():
            if set(weights) != {"ecr", "ecs", "ef", "sas"}:
                raise ValueError(f"EAS profile {name} must contain only ECR/ECS/EF/SAS")
            if abs(sum(float(value) for value in weights.values()) - 1.0) > 1e-9:
                raise ValueError(f"EAS profile {name} weights must sum to 1")

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
        if node.timestamp is None:
            return node.model_copy(
                update={
                    "timestamp": None,
                    "expires_at": None,
                    "freshness": 0.0,
                    "consistency": 0.0,
                    "availability": 0.0,
                    "quality_label": EvidenceStatus.MISSING,
                }
            )
        decay, validity_seconds = self._freshness_parameters(node.evidence_type)
        age_seconds = max(0.0, (now - node.timestamp).total_seconds())
        freshness = max(0.0, min(1.0, math.exp(-decay * age_seconds)))
        configured_expiry = node.timestamp + timedelta(seconds=validity_seconds)
        expires_at = min(node.expires_at, configured_expiry) if node.expires_at else configured_expiry
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
            node_key = (node.timestamp.isoformat() if node.timestamp else "", node.node_id)
            current_key = (
                current.timestamp.isoformat() if current.timestamp else "",
                current.node_id,
            ) if current is not None else None
            if current is None or node_key > current_key:
                latest[node.source] = node
        return list(latest.values())

    def _select_profile(self, nodes: list[EvidenceNode]) -> str:
        usable = [node for node in nodes if node.quality_label != EvidenceStatus.MISSING]
        road_values = {
            str(node.value).strip().upper()
            for node in usable
            if node.evidence_type == "road_condition" and node.value is not None
        }
        complex_values = {
            str(value).strip().upper()
            for value in self.profile_selection.get("complex_road_values", [])
        }
        if road_values & complex_values and "complex_road" in self.profiles:
            return "complex_road"
        speeds = [
            float(node.value)
            for node in usable
            if node.evidence_type == "vehicle_speed" and isinstance(node.value, (int, float))
        ]
        threshold = float(self.profile_selection.get("high_speed_threshold_kmh", 80))
        if speeds and max(speeds) >= threshold and "high_speed" in self.profiles:
            return "high_speed"
        return "default"

    @staticmethod
    def alignment_route(eas: float) -> str:
        if eas >= 0.85:
            return "EVIDENCE_PASS"
        if eas >= 0.60:
            return "EVIDENCE_REVIEW"
        return "EVIDENCE_BLOCK"

    @classmethod
    def _ecs_identity(cls, node: EvidenceNode) -> str:
        for field in ("physical_evidence_id", "original_node_id", "reference_node_id"):
            value = node.metadata.get(field)
            if isinstance(value, str) and value:
                return value
        return node.node_id

    @classmethod
    def _annotate_ecs_eligibility(
        cls, nodes: list[EvidenceNode]
    ) -> tuple[list[EvidenceNode], dict[str, str]]:
        seen: set[str] = set()
        comparable: dict[str, str] = {}
        annotated: list[EvidenceNode] = []
        for node in nodes:
            identity = cls._ecs_identity(node)
            reason: str | None = None
            if node.quality_label not in {
                EvidenceStatus.VALID,
                EvidenceStatus.SUSPICIOUS,
            }:
                reason = f"QUALITY_{node.quality_label.value}"
            elif node.value is None:
                reason = "VALUE_UNAVAILABLE"
            elif node.metadata.get("ecs_eligible") is False:
                reason = str(
                    node.metadata.get("ecs_exclusion_reason")
                    or "EXPLICIT_AUXILIARY_NODE"
                )
            elif node.evidence_type in cls.ECS_AUXILIARY_TYPES:
                reason = "AUXILIARY_GRAPH_NODE"
            elif identity in seen:
                reason = "DUPLICATE_PHYSICAL_EVIDENCE_REFERENCE"
            else:
                seen.add(identity)
                comparable[node.node_id] = identity
            annotated.append(
                node.model_copy(
                    update={
                        "metadata": {
                            **node.metadata,
                            "ecs_identity": identity,
                            "included_in_ecs": reason is None,
                            "ecs_exclusion_reason": reason,
                        }
                    }
                )
            )
        return annotated, comparable

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

        latest_speed = max(
            speed_nodes,
            key=lambda node: node.timestamp.isoformat() if node.timestamp else "",
            default=None,
        )
        gear_nodes = self._latest_per_source(nodes, "gear_position")
        latest_gear = max(
            gear_nodes,
            key=lambda node: node.timestamp.isoformat() if node.timestamp else "",
            default=None,
        )
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

        door = max(
            self._latest_per_source(nodes, "door_state"),
            key=lambda node: node.timestamp.isoformat() if node.timestamp else "",
            default=None,
        )
        lock = max(
            self._latest_per_source(nodes, "door_lock_state"),
            key=lambda node: node.timestamp.isoformat() if node.timestamp else "",
            default=None,
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
        scene_nodes: list[EvidenceNode] | None = None,
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

        evaluated, comparable_by_id = self._annotate_ecs_eligibility(evaluated)
        comparable_ids = set(comparable_by_id)
        evidence_pair_count = len(comparable_ids) * (len(comparable_ids) - 1) // 2
        conflict_pairs = {
            tuple(sorted((left, right)))
            for conflict in conflicts
            for index, left in enumerate(dict.fromkeys(conflict.get("node_ids", [])))
            for right in list(dict.fromkeys(conflict.get("node_ids", [])))[index + 1 :]
            if left in comparable_ids and right in comparable_ids and left != right
        }
        conflict_pair_count = len(conflict_pairs)
        ecs = (
            1.0
            if len(comparable_ids) < 2
            else 1.0 - conflict_pair_count / evidence_pair_count
        )
        ecs = max(0.0, min(1.0, ecs))
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
        profile = self._select_profile(scene_nodes if scene_nodes is not None else evaluated)
        configured_weights = self.profiles[profile]
        active_weights = {name: float(configured_weights.get(name, 0)) for name in values}
        weight_sum = sum(active_weights.values())
        normalized_weights = (
            {name: weight / weight_sum for name, weight in active_weights.items()}
            if weight_sum > 0
            else {name: 0.0 for name in active_weights}
        )
        exposed_weights = {name: round(value, 6) for name, value in normalized_weights.items()}
        if weight_sum > 0 and exposed_weights:
            last_name = next(reversed(exposed_weights))
            exposed_weights[last_name] = round(
                1.0 - sum(
                    value for name, value in exposed_weights.items() if name != last_name
                ),
                6,
            )
        eas = (
            sum(values[name] * normalized_weights[name] for name in values)
            if weight_sum > 0
            else 0.0
        )
        eas = max(0.0, min(1.0, eas))
        route = self.alignment_route(eas)
        metrics = EvidenceQualityMetrics(
            ecr=(round(ecr, 6) if ecr is not None else None),
            evidence_coverage_applicable=coverage_applicable,
            ecs=round(ecs, 6),
            ef=round(max(0.0, min(1.0, ef)), 6),
            sas=round(max(0.0, min(1.0, sas)), 6),
            eas=round(max(0.0, min(1.0, eas)), 6),
            conflict_count=len(conflicts),
            evidence_pair_count=evidence_pair_count,
            conflict_pair_count=conflict_pair_count,
            eas_weight_profile=profile,
            eas_weight_source=f"ENGINEERING_PROFILE:evidence_quality.yaml#{profile}",
            eas_weights=exposed_weights,
            evidence_alignment_route=route,
        )
        return evaluated, metrics, conflicts
