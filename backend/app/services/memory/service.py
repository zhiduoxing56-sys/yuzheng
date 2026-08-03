from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from datetime import datetime
from time import perf_counter
from typing import Any

from app.models.schemas import (
    EvidenceNode,
    EvidenceRelation,
    EvidenceStatus,
    MemoryDegreeStatistics,
    MemoryLink,
    MemoryNodeLayer,
    MemoryPropagationResult,
    MemoryPropagationStep,
    MemoryRelationEdge,
    MemoryRelationType,
    SecurityClass,
    SemanticFrame,
)
from app.services.evidence.repository import EvidenceRepository


SECURITY_RANKS: dict[SecurityClass, int] = {
    SecurityClass.ENTERTAINMENT: 0,
    SecurityClass.COCKPIT: 1,
    SecurityClass.DRIVING: 2,
    SecurityClass.EMERGENCY: 3,
}
LEGACY_LAYER_CLASSES = {
    "L0_ENTERTAINMENT": SecurityClass.ENTERTAINMENT,
    "L1_CABIN": SecurityClass.COCKPIT,
    "CABIN": SecurityClass.COCKPIT,
    "L1_COCKPIT": SecurityClass.COCKPIT,
    "L2_DRIVING": SecurityClass.DRIVING,
    "L3_EMERGENCY": SecurityClass.EMERGENCY,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(prefix: str, value: Any, length: int = 20) -> str:
    raw = hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()[:length]
    return f"{prefix}_{raw}"


class DualMemoryService:
    """Report Algorithm 2 over the already-retrieved candidate set.

    The service never embeds, searches HNSW, or reads the evidence repository.  It
    builds one auditable sparse relation graph and propagates confidence only over
    adjacent descending safety layers.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.configuration_version = str(
            config.get("configuration_version", config.get("topology_version", "MEMORY_V1"))
        )
        self.topology_version = str(config.get("topology_version", "SENSOR_TOPOLOGY_V1"))
        self.temporal_sync_window_ms = int(config.get("temporal_sync_window_ms", 30_000))
        self.average_degree_limit = int(config.get("average_degree_limit", 16))
        self.alpha = float(
            config.get("propagation_alpha", config.get("vertical", {}).get("alpha", 0.3))
        )
        self.alpha_source = str(config.get("propagation_alpha_source", "REPORT_EXPLICIT"))
        self.propagation_direction = str(
            config.get("propagation_direction", "G3_TO_G2_TO_G1_TO_G0")
        )
        self.unknown_type_policy = str(config.get("unknown_type_policy", "KEEP_UNCLASSIFIED"))
        self.relation_priority = {
            str(key): int(value)
            for key, value in config.get(
                "relation_priority",
                {
                    "SENSOR_TOPOLOGY": 4,
                    "SEMANTIC_COMPLEMENT": 3,
                    "SPATIAL_COOCCURRENCE": 2,
                    "TEMPORAL_SYNCHRONIZATION": 1,
                },
            ).items()
        }
        self.semantic_pairs = self._pair_rules(config.get("semantic_complement_rules", []))
        self.sensor_pairs = self._topology_rules(config.get("sensor_topology", []))

    @staticmethod
    def _pair_rules(values: list[Any]) -> dict[frozenset[str], dict[str, Any]]:
        rules: dict[frozenset[str], dict[str, Any]] = {}
        for value in values:
            if isinstance(value, dict):
                left = str(value.get("from_type", ""))
                right = str(value.get("to_type", ""))
                payload = dict(value)
            else:
                left, right = (str(item) for item in value)
                payload = {"source": "ENGINEERING_CONFIG"}
            if left and right and left != right:
                rules[frozenset((left, right))] = payload
        return rules

    @staticmethod
    def _topology_rules(values: list[Any]) -> dict[frozenset[str], dict[str, Any]]:
        return DualMemoryService._pair_rules(values)

    @staticmethod
    def _stable_identity(node: EvidenceNode) -> str:
        return EvidenceRepository.stream_key(node)

    @staticmethod
    def _node_content_key(node: EvidenceNode) -> tuple[str, str]:
        timestamp = node.timestamp.isoformat() if node.timestamp is not None else ""
        payload = {
            "identity": EvidenceRepository.stream_key(node),
            "timestamp": timestamp,
            "value": node.value,
            "quality": node.quality_label.value,
            "integrity_hash": node.integrity_hash,
        }
        return timestamp, hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()

    def _deduplicate(self, nodes: list[EvidenceNode]) -> list[EvidenceNode]:
        by_node_id: dict[str, EvidenceNode] = {}
        for node in nodes:
            by_node_id.setdefault(node.node_id, node)
        by_identity: dict[str, EvidenceNode] = {}
        for node in by_node_id.values():
            identity = self._stable_identity(node)
            current = by_identity.get(identity)
            if current is None or self._node_content_key(node) > self._node_content_key(current):
                by_identity[identity] = node
        return sorted(by_identity.values(), key=lambda node: self._stable_identity(node))

    @staticmethod
    def _normalize_class(node: EvidenceNode) -> tuple[SecurityClass, int | None, str]:
        security_class = node.security_class
        source = node.security_classification_source or "STEP2_SECURITY_CLASSIFICATION"
        if security_class is None:
            security_class = LEGACY_LAYER_CLASSES.get(node.layer, SecurityClass.UNCLASSIFIED)
            source = (
                "LEGACY_LAYER_COMPATIBILITY"
                if security_class != SecurityClass.UNCLASSIFIED
                else "UNCLASSIFIED"
            )
        if security_class == SecurityClass.UNCLASSIFIED:
            return security_class, None, source
        rank = SECURITY_RANKS[security_class]
        if node.security_rank is not None and node.security_rank != rank:
            raise ValueError(
                f"security_rank mismatch for {node.evidence_type}: "
                f"{node.security_rank}!={rank}"
            )
        return security_class, rank, source

    @staticmethod
    def _origin(node: EvidenceNode, explicit: dict[str, str]) -> str:
        value = explicit.get(node.node_id)
        if value in {"HNSW", "MANDATORY_RECALL", "BOTH", "NONE"}:
            return value
        raw = str(node.metadata.get("retrieval_origin", "")).upper()
        if raw in {"SEMANTIC_RETRIEVAL", "HNSW"}:
            return "HNSW"
        if raw in {"MANDATORY_RECALL", "MANDATORY_RECALL_HISTORY"}:
            return "MANDATORY_RECALL"
        return "NONE" if node.quality_label == EvidenceStatus.MISSING else "HNSW"

    @staticmethod
    def _location(node: EvidenceNode) -> tuple[str | None, str | None]:
        for field in ("area", "region", "location"):
            value = node.metadata.get(field)
            if value not in (None, ""):
                return field, str(value)
        return None, None

    def _candidate_edge(self, left: EvidenceNode, right: EvidenceNode) -> MemoryRelationEdge | None:
        relation_types: list[MemoryRelationType] = []
        criteria: dict[str, Any] = {}
        sources: dict[str, str] = {}
        scores: dict[str, float] = {}

        left_field, left_location = self._location(left)
        right_field, right_location = self._location(right)
        if left_location is not None and left_location == right_location:
            relation_types.append(MemoryRelationType.SPATIAL_COOCCURRENCE)
            criteria["spatial"] = {
                "left_field": left_field,
                "right_field": right_field,
                "value": left_location,
            }
            sources["spatial"] = "OBSERVED_EVIDENCE_METADATA"
            scores["spatial"] = 1.0

        time_delta_ms: float | None = None
        if left.timestamp is not None and right.timestamp is not None:
            time_delta_ms = abs((left.timestamp - right.timestamp).total_seconds()) * 1000
            if time_delta_ms <= self.temporal_sync_window_ms:
                relation_types.append(MemoryRelationType.TEMPORAL_SYNCHRONIZATION)
                criteria["temporal"] = {
                    "time_delta_ms": round(time_delta_ms, 3),
                    "sync_window_ms": self.temporal_sync_window_ms,
                    "window_source": "ENGINEERING_CONFIG",
                }
                sources["temporal"] = "OBSERVED_TIMESTAMPS"
                scores["temporal"] = max(
                    0.0, 1.0 - time_delta_ms / max(1, self.temporal_sync_window_ms)
                )

        pair = frozenset((left.evidence_type, right.evidence_type))
        semantic_rule = self.semantic_pairs.get(pair)
        if semantic_rule is not None:
            relation_types.append(MemoryRelationType.SEMANTIC_COMPLEMENT)
            criteria["semantic"] = {
                "from_type": left.evidence_type,
                "to_type": right.evidence_type,
                "rule": semantic_rule.get("relation", "COMPLEMENTARY"),
            }
            sources["semantic"] = str(
                semantic_rule.get("source", "ENGINEERING_CONFIG")
            )
            scores["semantic"] = 1.0

        topology_rule = self.sensor_pairs.get(pair)
        if topology_rule is not None:
            relation_types.append(MemoryRelationType.SENSOR_TOPOLOGY)
            criteria["sensor_topology"] = {
                "from_type": str(topology_rule.get("from_type", left.evidence_type)),
                "to_type": str(topology_rule.get("to_type", right.evidence_type)),
                "relation": str(topology_rule.get("relation", "EXPLICIT_TOPOLOGY")),
                "direction": str(topology_rule.get("direction", "BIDIRECTIONAL")),
                "topology_version": self.topology_version,
            }
            sources["sensor_topology"] = str(
                topology_rule.get("source", "ENGINEERING_CONFIG")
            )
            scores["sensor_topology"] = 1.0

        if not relation_types:
            return None
        relation_types = sorted(set(relation_types), key=lambda item: item.value)
        identities = sorted((self._stable_identity(left), self._stable_identity(right)))
        edge_id = _digest(
            "MRE",
            {
                "identities": identities,
                "relations": [item.value for item in relation_types],
                "configuration_version": self.configuration_version,
            },
        )
        return MemoryRelationEdge(
            edge_id=edge_id,
            source_node_id=left.node_id,
            target_node_id=right.node_id,
            relation_types=relation_types,
            criteria=criteria,
            criteria_sources=sources,
            score_components={key: round(value, 8) for key, value in scores.items()},
            configuration_version=self.configuration_version,
        )

    def _edge_sort_key(
        self, edge: MemoryRelationEdge, by_id: dict[str, EvidenceNode]
    ) -> tuple[Any, ...]:
        relation_values = {item.value for item in edge.relation_types}
        strongest = max((self.relation_priority.get(value, 0) for value in relation_values), default=0)
        time_delta = float(
            edge.criteria.get("temporal", {}).get("time_delta_ms", math.inf)
        )
        identities = sorted(
            (
                self._stable_identity(by_id[edge.source_node_id]),
                self._stable_identity(by_id[edge.target_node_id]),
            )
        )
        return (-len(relation_values), -strongest, time_delta, identities[0], identities[1])

    def propagate(
        self,
        nodes: list[EvidenceNode],
        frame: SemanticFrame,
        conflicts: list[dict[str, Any]],
        *,
        retrieval_origins: dict[str, str] | None = None,
    ) -> MemoryPropagationResult:
        del frame  # Algorithm 2 uses persisted SAS and explicit relation criteria only.
        started = perf_counter()
        current = self._deduplicate(nodes)
        by_id = {node.node_id: node for node in current}
        origins = retrieval_origins or {}
        warnings: list[str] = []
        node_layers: list[MemoryNodeLayer] = []
        layer_by_id: dict[str, int | None] = {}
        eligible: dict[str, bool] = {}

        for node in current:
            security_class, rank, mapping_source = self._normalize_class(node)
            propagation_eligible = (
                rank is not None
                and node.quality_label not in {EvidenceStatus.MISSING, EvidenceStatus.TAMPERED}
            )
            node_layers.append(
                MemoryNodeLayer(
                    node_id=node.node_id,
                    stable_physical_identity=self._stable_identity(node),
                    security_class=security_class,
                    security_rank=rank,
                    memory_layer=rank,
                    mapping_source=mapping_source,
                    retrieval_origin=self._origin(node, origins),
                    propagation_eligible=propagation_eligible,
                )
            )
            layer_by_id[node.node_id] = rank
            eligible[node.node_id] = propagation_eligible
            if rank is None:
                warnings.append(
                    f"UNCLASSIFIED_EVIDENCE_TYPE:{node.evidence_type}:{self.unknown_type_policy}"
                )

        horizontal_started = perf_counter()
        candidates: list[MemoryRelationEdge] = []
        for index, left in enumerate(current):
            for right in current[index + 1 :]:
                edge = self._candidate_edge(left, right)
                if edge is not None:
                    candidates.append(edge)
        candidates.sort(key=lambda edge: self._edge_sort_key(edge, by_id))
        node_count = len(current)
        max_edges = (node_count * self.average_degree_limit) // 2
        retained = candidates[:max_edges]
        pruned_count = len(candidates) - len(retained)
        degrees: dict[str, int] = defaultdict(int)
        for edge in retained:
            degrees[edge.source_node_id] += 1
            degrees[edge.target_node_id] += 1
        average_degree = (2 * len(retained) / node_count) if node_count else 0.0
        degree_statistics = MemoryDegreeStatistics(
            node_count=node_count,
            candidate_edge_count=len(candidates),
            retained_edge_count=len(retained),
            average_degree=round(average_degree, 8),
            max_degree=max(degrees.values(), default=0),
            pruned_edge_count=pruned_count,
            degree_limit=self.average_degree_limit,
        )
        if average_degree > self.average_degree_limit + 1e-9:
            raise ValueError("Algorithm 2 average degree limit violated")
        horizontal_duration_ms = (perf_counter() - horizontal_started) * 1000

        initial: dict[str, float | None] = {}
        final: dict[str, float | None] = {}
        for node in current:
            value = float(node.semantic_similarity)
            if node.quality_label in {EvidenceStatus.MISSING, EvidenceStatus.TAMPERED}:
                value = 0.0
            initial[node.node_id] = round(value, 8)
            final[node.node_id] = round(value, 8)

        adjacency: dict[frozenset[str], list[str]] = defaultdict(list)
        for edge in retained:
            adjacency[frozenset((edge.source_node_id, edge.target_node_id))].append(edge.edge_id)
        conflict_pairs = {
            frozenset((left, right))
            for conflict in conflicts
            for index, left in enumerate(conflict.get("node_ids", []))
            for right in conflict.get("node_ids", [])[index + 1 :]
        }
        conflict_node_ids = set().union(*conflict_pairs) if conflict_pairs else set()

        vertical_started = perf_counter()
        steps: list[MemoryPropagationStep] = []
        incoming: dict[str, list[int]] = defaultdict(list)
        sequence = 0
        stable_by_id = {node.node_id: self._stable_identity(node) for node in current}
        for parent_layer in (3, 2, 1):
            child_layer = parent_layer - 1
            parents = sorted(
                (
                    node_id
                    for node_id, layer in layer_by_id.items()
                    if layer == parent_layer and eligible[node_id]
                ),
                key=lambda node_id: stable_by_id[node_id],
            )
            for parent_id in parents:
                children = sorted(
                    (
                        node_id
                        for node_id, layer in layer_by_id.items()
                        if layer == child_layer
                        and eligible[node_id]
                        and frozenset((parent_id, node_id)) in adjacency
                    ),
                    key=lambda node_id: stable_by_id[node_id],
                )
                for child_id in children:
                    parent_confidence = float(final[parent_id] or 0.0)
                    before = float(final[child_id] or 0.0)
                    contribution = self.alpha * parent_confidence
                    after = before + contribution
                    sequence += 1
                    step = MemoryPropagationStep(
                        sequence=sequence,
                        parent_node_id=parent_id,
                        child_node_id=child_id,
                        parent_layer=parent_layer,
                        child_layer=child_layer,
                        alpha=self.alpha,
                        parent_confidence_at_step=round(parent_confidence, 8),
                        contribution=round(contribution, 8),
                        child_confidence_before=round(before, 8),
                        child_confidence_after=round(after, 8),
                        relation_edge_ids=sorted(adjacency[frozenset((parent_id, child_id))]),
                    )
                    steps.append(step)
                    incoming[child_id].append(sequence)
                    final[child_id] = round(after, 8)
        vertical_duration_ms = (perf_counter() - vertical_started) * 1000

        # Safety constraint: unavailable or tampered evidence never acquires confidence.
        for node in current:
            if node.quality_label in {EvidenceStatus.MISSING, EvidenceStatus.TAMPERED}:
                final[node.node_id] = 0.0

        # The fields below are retained as a compatibility projection for old internal
        # callers.  Algorithm 2 itself is represented only by relation_edges,
        # initial/final_confidences, and propagation_steps above.
        compatibility_post = {
            node_id: float(value or 0.0) for node_id, value in initial.items()
        }
        horizontal_links: list[MemoryLink] = []
        support_weights: list[float] = []
        horizontal_conflicts = 0
        conflict_penalty = float(self.config.get("horizontal", {}).get("conflict_penalty", 0.25))
        for edge in retained:
            score = round(max(edge.score_components.values(), default=0.0), 8)
            pair = frozenset((edge.source_node_id, edge.target_node_id))
            left = by_id[edge.source_node_id]
            right = by_id[edge.target_node_id]
            conflict = (
                pair in conflict_pairs
                or left.quality_label == EvidenceStatus.SUSPICIOUS
                or right.quality_label == EvidenceStatus.SUSPICIOUS
            )
            if conflict:
                horizontal_conflicts += 1
                conflict_node_ids.update((left.node_id, right.node_id))
                compatibility_post[left.node_id] = max(
                    0.0, compatibility_post[left.node_id] - conflict_penalty * score
                )
                compatibility_post[right.node_id] = max(
                    0.0, compatibility_post[right.node_id] - conflict_penalty * score
                )
            else:
                support_weights.append(score)
            horizontal_links.append(
                MemoryLink(
                    link_id=edge.edge_id,
                    source=edge.source_node_id,
                    target=edge.target_node_id,
                    relation=EvidenceRelation.HORIZONTAL_MEMORY,
                    weight=score,
                    layer="RELATION_GRAPH",
                    reason=",".join(item.value for item in edge.relation_types),
                    conflict=conflict,
                )
            )

        legacy_layer_names = {
            0: "L0_ENTERTAINMENT",
            1: "L1_CABIN",
            2: "L2_DRIVING",
            3: "L3_EMERGENCY",
        }
        risk_penalty = float(self.config.get("vertical", {}).get("risk_penalty", 0.3))
        vertical_links: list[MemoryLink] = []
        propagation_paths: list[dict[str, Any]] = []
        for step in steps:
            parent = by_id[step.parent_node_id]
            before = compatibility_post[step.child_node_id]
            source_risky = parent.quality_label in {
                EvidenceStatus.SUSPICIOUS,
                EvidenceStatus.STALE,
                EvidenceStatus.TAMPERED,
                EvidenceStatus.MISSING,
            }
            support_adjustment = 0.0 if source_risky else step.contribution
            risk_adjustment = (
                -self.alpha
                * risk_penalty
                * max(1.0 - float(initial[parent.node_id] or 0.0), 0.5)
                if source_risky
                else 0.0
            )
            after = max(0.0, min(1.0, before + support_adjustment + risk_adjustment))
            if step.child_node_id in conflict_node_ids:
                after = min(after, float(initial[step.child_node_id] or 0.0))
            compatibility_post[step.child_node_id] = after
            final_adjustment = after - before
            from_layer = legacy_layer_names[step.parent_layer]
            to_layer = legacy_layer_names[step.child_layer]
            vertical_links.append(
                MemoryLink(
                    link_id=_digest(
                        "MVP",
                        {
                            "sequence": step.sequence,
                            "parent": step.parent_node_id,
                            "child": step.child_node_id,
                        },
                    ),
                    source=step.parent_node_id,
                    target=step.child_node_id,
                    relation=EvidenceRelation.VERTICAL_PROPAGATION,
                    weight=round(step.alpha, 8),
                    layer=f"{from_layer}->{to_layer}",
                    reason=(
                        "REPORT_ALGORITHM_2_ADJACENT_LAYER_PROPAGATION; "
                        f"support_adjustment={support_adjustment:.8f}; "
                        f"risk_adjustment={risk_adjustment:.8f}; "
                        f"final_adjustment={final_adjustment:.8f}"
                    ),
                    conflict=source_risky,
                    support_adjustment=round(support_adjustment, 8),
                    risk_adjustment=round(risk_adjustment, 8),
                    final_adjustment=round(final_adjustment, 8),
                )
            )
            propagation_paths.append(
                {
                    "source": step.parent_node_id,
                    "target": step.child_node_id,
                    "from_layer": from_layer,
                    "to_layer": to_layer,
                    "before": round(before, 8),
                    "support_adjustment": round(support_adjustment, 8),
                    "risk_adjustment": round(risk_adjustment, 8),
                    "final_adjustment": round(final_adjustment, 8),
                    "after": round(after, 8),
                    "reason": "REPORT_ALGORITHM_2_ADJACENT_LAYER_PROPAGATION",
                    "step_sequence": step.sequence,
                    "relation_edge_ids": step.relation_edge_ids,
                }
            )
        graph_layers = {
            f"G{rank}": [
                item.node_id
                for item in node_layers
                if item.memory_layer == rank
            ]
            for rank in range(4)
        }
        graph_layers["UNCLASSIFIED"] = [
            item.node_id for item in node_layers if item.memory_layer is None
        ]
        duration_ms = (perf_counter() - started) * 1000
        return MemoryPropagationResult(
            layered_memory_graph={
                "layers": graph_layers,
                "layer_counts": {
                    layer: len(node_ids) for layer, node_ids in graph_layers.items()
                },
                "relation_edge_ids": [edge.edge_id for edge in retained],
                "propagation_direction": self.propagation_direction,
                "acyclic_vertical_propagation": True,
            },
            relation_edges=retained,
            degree_statistics=degree_statistics,
            node_layers=node_layers,
            initial_confidences=initial,
            final_confidences=final,
            propagation_steps=steps,
            incoming_contributions={key: value for key, value in sorted(incoming.items())},
            alpha=self.alpha,
            alpha_source=self.alpha_source,
            configuration_version=self.configuration_version,
            warnings=sorted(set(warnings)),
            candidate_node_ids=[node.node_id for node in current],
            retrieval_origins={item.node_id: item.retrieval_origin for item in node_layers},
            horizontal_links=horizontal_links,
            horizontal_support=(
                round(sum(support_weights) / len(support_weights), 8)
                if support_weights
                else 0.0
            ),
            horizontal_conflicts=horizontal_conflicts,
            horizontal_adjustments={
                key: round(value, 8) for key, value in compatibility_post.items()
            },
            vertical_links=vertical_links,
            propagation_paths=propagation_paths,
            pre_weights={key: float(value or 0.0) for key, value in initial.items()},
            post_weights={key: round(value, 8) for key, value in compatibility_post.items()},
            horizontal_duration_ms=round(horizontal_duration_ms, 4),
            vertical_duration_ms=round(vertical_duration_ms, 4),
            duration_ms=round(duration_ms, 4),
        )
