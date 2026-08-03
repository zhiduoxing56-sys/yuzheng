from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from threading import RLock
from time import perf_counter
from typing import Any

import networkx as nx

from app.models.schemas import (
    AuditRecord,
    CausalCorrectionResult,
    CausalEdge,
    CausalModelSnapshot,
    CausalNodeWeight,
    CausalPriorComponents,
    CausalStatus,
    EvidenceNode,
    EvidenceStatus,
    MemoryPropagationResult,
    ParentStateStatistics,
    SemanticFrame,
    utc_now,
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


class CausalCorrectionService:
    """Report Algorithm 3 over a frozen, eligible historical command set."""

    def __init__(
        self,
        config: dict[str, Any],
        *,
        memory_config: dict[str, Any] | None = None,
    ) -> None:
        self.config = config
        self.formula_version = str(
            config.get("formula_version", "REPORT_FORMULAS_2_9_TO_2_15_V1")
        )
        self.variable_identity_version = str(
            config.get("variable_identity_version", "NORMALIZED_EVIDENCE_TYPE_V1")
        )
        self.variable_identity_level = str(
            config.get("variable_identity_level", "NORMALIZED_EVIDENCE_TYPE")
        )
        self.variable_identity_source = str(
            config.get("variable_identity_source", "ENGINEERING_REALIZATION")
        )
        self.theta_causal = float(config.get("theta_causal", 0.0))
        self.lambda_values = {
            key: float(value)
            for key, value in config.get(
                "lambda_values",
                {
                    "sas": 0.30,
                    "layer_confidence": 0.25,
                    "freshness": 0.15,
                    "historical_availability": 0.10,
                    "mandatory": 0.20,
                },
            ).items()
        }
        required_lambdas = {
            "sas",
            "layer_confidence",
            "freshness",
            "historical_availability",
            "mandatory",
        }
        if set(self.lambda_values) != required_lambdas:
            raise ValueError("lambda_values 必须精确包含式2.10五项")
        if abs(sum(self.lambda_values.values()) - 1.0) > 1e-9:
            raise ValueError("lambda_values 必须归一化为1")
        self.laplace_epsilon = float(
            config.get("laplace_epsilon", config.get("laplace_alpha", 1.0))
        )
        self.numeric_epsilon = float(config.get("numeric_epsilon", 1e-12))
        self.minimum_sample_count = int(
            config.get(
                "minimum_history_samples",
                config.get("minimum_samples_for_confidence", 20),
            )
        )
        self.auto_rebuild_enabled = bool(config.get("auto_rebuild_enabled", True))
        self.rebuild_every_eligible_audits = int(
            config.get("rebuild_every_eligible_audits", 20)
        )
        self.maximum_training_records = int(config.get("maximum_training_records", 5000))
        self._domain_pairs = self._load_domain_pairs(memory_config or {})
        self._lock = RLock()
        self._records: list[AuditRecord] = []
        self._samples: list[dict[str, Any]] = []
        self._candidate_edges: list[CausalEdge] = []
        self._pruned_edges: list[CausalEdge] = []
        self._removed_edges: list[CausalEdge] = []
        self._last_rebuilt_at = None
        self._excluded_count = 0
        self._model_build_id = "CAUSAL_BUILD_UNBUILT"
        self._model_version = self._model_build_id
        self._source_audit_count = 0
        self._auto_rebuild_running = False
        self._last_rebuild_error: str | None = None
        self._history_digest = _sha([])
        self._command_vocabulary_digest = _sha([])
        self._dag_digest = _sha([])
        self._parameter_digest = self._parameters_digest()
        self._topological_order: list[str] = []

    @staticmethod
    def _load_domain_pairs(memory_config: dict[str, Any]) -> set[frozenset[str]]:
        values = [
            *memory_config.get("semantic_complement_rules", []),
            *memory_config.get("sensor_topology", []),
        ]
        pairs: set[frozenset[str]] = set()
        for value in values:
            if isinstance(value, dict):
                left = str(value.get("from_type", ""))
                right = str(value.get("to_type", ""))
            else:
                left, right = (str(item) for item in value)
            if left and right and left != right:
                pairs.add(frozenset((left, right)))
        return pairs

    @staticmethod
    def _command_class(record: AuditRecord) -> str:
        return f"{record.semantic_frame.action}|{record.semantic_frame.target}"

    @staticmethod
    def _record_nodes(record: AuditRecord) -> list[EvidenceNode]:
        if record.evidence_subgraph is None:
            return []
        nodes = record.evidence_subgraph.nodes
        memory = record.memory_propagation
        if memory is not None and memory.candidate_node_ids:
            allowed = set(memory.candidate_node_ids)
            return [node for node in nodes if node.node_id in allowed]
        required = set(record.semantic_frame.required_evidence_types)
        return [node for node in nodes if node.evidence_type in required or node.mandatory]

    @classmethod
    def _sample_from_record(cls, record: AuditRecord) -> dict[str, Any] | None:
        nodes = cls._record_nodes(record)
        if not nodes:
            return None
        timestamps: dict[str, str] = {}
        qualities: dict[str, str] = {}
        for node in nodes:
            variable = node.evidence_type
            timestamp = node.timestamp.isoformat() if node.timestamp is not None else ""
            if variable not in timestamps or timestamp < timestamps[variable]:
                timestamps[variable] = timestamp
            qualities[variable] = node.quality_label.value
        active = sorted(timestamps)
        return {
            "sample_audit_id": record.audit_id,
            "turn_id": record.turn_id,
            "command_class": cls._command_class(record),
            "decision_y": record.final_decision.final_decision.value,
            "active_evidence_variables": active,
            "parent_state_variables": active,
            "event_time": record.created_at.isoformat(),
            "timestamps": timestamps,
            "quality_labels": qualities,
            "learning_eligibility": True,
            "exclusion_reason": None,
        }

    def _parameters_digest(self) -> str:
        return _sha(
            {
                "formula_version": self.formula_version,
                "variable_identity_version": self.variable_identity_version,
                "theta_causal": self.theta_causal,
                "lambda_values": self.lambda_values,
                "laplace_epsilon": self.laplace_epsilon,
                "numeric_epsilon": self.numeric_epsilon,
                "minimum_history_samples": self.minimum_sample_count,
            }
        )

    def _build_edges(self, samples: list[dict[str, Any]]) -> list[CausalEdge]:
        variables = sorted(
            {
                variable
                for sample in samples
                for variable in sample["active_evidence_variables"]
            }
        )
        active_sets = [set(sample["active_evidence_variables"]) for sample in samples]
        edges: list[CausalEdge] = []
        for left_index, left in enumerate(variables):
            for right in variables[left_index + 1 :]:
                both = sum(left in active and right in active for active in active_sets)
                if both == 0:
                    continue
                left_count = sum(left in active for active in active_sets)
                right_count = sum(right in active for active in active_sets)
                total = len(samples)
                p_right_given_left = both / left_count if left_count else 0.0
                not_left_count = total - left_count
                right_without_left = right_count - both
                p_right_given_not_left = (
                    right_without_left / not_left_count if not_left_count else 0.0
                )
                right_delta = abs(p_right_given_left - p_right_given_not_left)
                p_left_given_right = both / right_count if right_count else 0.0
                not_right_count = total - right_count
                left_without_right = left_count - both
                p_left_given_not_right = (
                    left_without_right / not_right_count if not_right_count else 0.0
                )
                left_delta = abs(p_left_given_right - p_left_given_not_right)

                left_before = 0
                right_before = 0
                for sample in samples:
                    active = set(sample["active_evidence_variables"])
                    if left not in active or right not in active:
                        continue
                    left_time = sample["timestamps"].get(left, "")
                    right_time = sample["timestamps"].get(right, "")
                    if left_time and right_time:
                        if left_time < right_time:
                            left_before += 1
                        elif right_time < left_time:
                            right_before += 1
                if left_before > right_before:
                    parent, child = left, right
                    p_child_parent = p_right_given_left
                    p_child_not = p_right_given_not_left
                    dependency = right_delta
                    temporal_valid = True
                elif right_before > left_before:
                    parent, child = right, left
                    p_child_parent = p_left_given_right
                    p_child_not = p_left_given_not_right
                    dependency = left_delta
                    temporal_valid = True
                else:
                    parent, child = sorted((left, right))
                    if parent == left:
                        p_child_parent = p_right_given_left
                        p_child_not = p_right_given_not_left
                        dependency = right_delta
                    else:
                        p_child_parent = p_left_given_right
                        p_child_not = p_left_given_not_right
                        dependency = left_delta
                    temporal_valid = False
                domain_pair = frozenset((left, right)) in self._domain_pairs
                accepted = dependency >= self.theta_causal and (temporal_valid or domain_pair)
                source = f"evidence:{parent}"
                target = f"evidence:{child}"
                edges.append(
                    CausalEdge(
                        source=source,
                        target=target,
                        relation="CONDITIONAL_DEPENDENCY",
                        support=round(dependency, 8),
                        sample_count=both,
                        reason=(
                            "历史条件依赖与时间方向"
                            if temporal_valid
                            else "Algorithm 2正式关系约束与稳定变量方向"
                        ),
                        parent_variable=parent,
                        child_variable=child,
                        support_count=both,
                        p_child_given_parent=round(p_child_parent, 8),
                        p_child_given_not_parent=round(p_child_not, 8),
                        dependency_delta=round(dependency, 8),
                        temporal_order_valid=temporal_valid,
                        domain_rule_source=(
                            "ALGORITHM_2_CONFIGURED_RELATION" if domain_pair else "NONE"
                        ),
                        threshold=self.theta_causal,
                        accepted=accepted,
                    )
                )
        return sorted(
            edges,
            key=lambda edge: (
                -(edge.dependency_delta or 0.0),
                edge.source,
                edge.target,
            ),
        )

    @staticmethod
    def prune_candidate_edges(
        edges: list[CausalEdge],
    ) -> tuple[list[CausalEdge], list[CausalEdge]]:
        """Keep strongest edges first; reject invalid or cyclic edges deterministically."""
        graph = nx.DiGraph()
        kept: list[CausalEdge] = []
        removed: list[CausalEdge] = []
        ordered = sorted(
            edges,
            key=lambda edge: (
                -(edge.dependency_delta if edge.dependency_delta is not None else edge.support),
                edge.source,
                edge.target,
                edge.relation,
            ),
        )
        seen: set[tuple[str, str]] = set()
        for edge in ordered:
            pair = (edge.source, edge.target)
            reason: str | None = None
            if edge.source == edge.target:
                reason = "SELF_LOOP"
            elif pair in seen:
                reason = "DUPLICATE_EDGE"
            elif edge.accepted is False:
                reason = "BELOW_THRESHOLD_OR_NO_VALID_DIRECTION"
            if reason is not None:
                removed.append(
                    edge.model_copy(update={"accepted": False, "prune_reason": reason})
                )
                continue
            seen.add(pair)
            graph.add_edge(edge.source, edge.target)
            if nx.is_directed_acyclic_graph(graph):
                kept.append(edge.model_copy(update={"accepted": True, "prune_reason": None}))
                continue
            graph.remove_edge(edge.source, edge.target)
            removed.append(
                edge.model_copy(
                    update={
                        "accepted": False,
                        "prune_reason": "CYCLE_WEAKEST_EDGE",
                        "reason": f"{edge.reason}; removed to preserve DAG",
                    }
                )
            )
        return kept, removed

    def rebuild(
        self,
        records: list[AuditRecord],
        excluded_record_count: int,
        *,
        restore_metadata: dict[str, Any] | None = None,
        source_audit_count: int | None = None,
    ) -> CausalStatus:
        unique: dict[str, AuditRecord] = {}
        for record in records[-self.maximum_training_records :]:
            unique.setdefault(record.turn_id, record)
        bounded = sorted(unique.values(), key=lambda item: (item.created_at, item.turn_id))
        samples = [
            sample
            for record in bounded
            if (sample := self._sample_from_record(record)) is not None
        ]
        candidates = self._build_edges(samples)
        pruned, removed = self.prune_candidate_edges(candidates)
        history_payload = [
            {
                "command_class": sample["command_class"],
                "decision_y": sample["decision_y"],
                "active_evidence_variables": sample["active_evidence_variables"],
                "parent_state_variables": sample["parent_state_variables"],
                "event_time": sample["event_time"],
                "quality_labels": sample["quality_labels"],
            }
            for sample in samples
        ]
        history_digest = _sha(history_payload)
        command_classes = sorted({sample["command_class"] for sample in samples})
        vocabulary_digest = _sha(command_classes)
        dag_payload = [
            {
                "parent": edge.parent_variable,
                "child": edge.child_variable,
                "dependency_delta": edge.dependency_delta,
            }
            for edge in pruned
        ]
        dag_digest = _sha(dag_payload)
        parameter_digest = self._parameters_digest()
        build_id = "CAUSAL_BUILD_" + _sha(
            {
                "history_digest": history_digest,
                "dag_digest": dag_digest,
                "parameter_digest": parameter_digest,
                "formula_version": self.formula_version,
                "variable_identity_version": self.variable_identity_version,
            }
        )[:20]
        graph = nx.DiGraph()
        graph.add_edges_from((edge.source, edge.target) for edge in pruned)
        topological_order = (
            list(nx.lexicographical_topological_sort(graph)) if graph.nodes else []
        )
        built_at = (
            restore_metadata.get("model_built_at")
            if restore_metadata and restore_metadata.get("model_build_id") == build_id
            else utc_now()
        )
        with self._lock:
            self._records = bounded
            self._samples = samples
            self._excluded_count = excluded_record_count + (len(bounded) - len(samples))
            self._candidate_edges = candidates
            self._pruned_edges = pruned
            self._removed_edges = removed
            self._model_build_id = build_id
            self._model_version = build_id
            self._last_rebuilt_at = built_at
            self._source_audit_count = (
                int(source_audit_count) if source_audit_count is not None else len(samples)
            )
            self._history_digest = history_digest
            self._command_vocabulary_digest = vocabulary_digest
            self._dag_digest = dag_digest
            self._parameter_digest = parameter_digest
            self._topological_order = topological_order
            self._last_rebuild_error = None
            self._auto_rebuild_running = False
        return self.status()

    def model_metadata(self) -> dict[str, Any]:
        with self._lock:
            return {
                "model_build_id": self._model_build_id,
                "model_version": self._model_build_id,
                "model_built_at": (
                    self._last_rebuilt_at.isoformat()
                    if hasattr(self._last_rebuilt_at, "isoformat")
                    else self._last_rebuilt_at
                ),
                "source_audit_count": self._source_audit_count,
                "minimum_sample_count": self.minimum_sample_count,
                "training_record_ids": [record.audit_id for record in self._records],
                "history_digest": self._history_digest,
                "dag_digest": self._dag_digest,
                "parameter_digest": self._parameter_digest,
            }

    def set_auto_rebuild_running(self, running: bool) -> None:
        with self._lock:
            self._auto_rebuild_running = running

    def record_rebuild_failure(self, message: str) -> None:
        with self._lock:
            self._auto_rebuild_running = False
            self._last_rebuild_error = message

    def status(self, eligible_audit_count: int | None = None) -> CausalStatus:
        with self._lock:
            variables = {
                endpoint
                for edge in self._pruned_edges
                for endpoint in (edge.source, edge.target)
            }
            eligible = self._source_audit_count if eligible_audit_count is None else eligible_audit_count
            sufficient = len(self._samples) >= self.minimum_sample_count
            return CausalStatus(
                learning_record_count=len(self._samples),
                excluded_record_count=self._excluded_count,
                candidate_edge_count=len(self._candidate_edges),
                pruned_edge_count=len(self._pruned_edges),
                removed_edge_count=len(self._removed_edges),
                graph_node_count=len(variables),
                graph_edge_count=len(self._pruned_edges),
                last_rebuilt_at=self._last_rebuilt_at,
                data_sufficiency="sufficient" if sufficient else "insufficient",
                minimum_sample_count=self.minimum_sample_count,
                model_version=self._model_build_id,
                model_built_at=self._last_rebuilt_at,
                source_audit_count=self._source_audit_count,
                auto_rebuild_enabled=self.auto_rebuild_enabled,
                rebuild_every_eligible_audits=self.rebuild_every_eligible_audits,
                eligible_audits_since_rebuild=max(0, eligible - self._source_audit_count),
                auto_rebuild_running=self._auto_rebuild_running,
                last_rebuild_error=self._last_rebuild_error,
            )

    @staticmethod
    def _softmax(values: dict[str, float]) -> dict[str, float]:
        if not values:
            return {}
        maximum = max(values.values())
        exponentials = {key: math.exp(value - maximum) for key, value in values.items()}
        denominator = sum(exponentials.values())
        if denominator <= 0:
            return {}
        return {key: value / denominator for key, value in exponentials.items()}

    def _snapshot(self, confidence_status: str) -> CausalModelSnapshot:
        history_times = sorted(sample["event_time"] for sample in self._samples)
        return CausalModelSnapshot(
            model_build_id=self._model_build_id,
            built_at=self._last_rebuilt_at,
            formula_version=self.formula_version,
            causal_variable_version=self.variable_identity_version,
            history_sample_count=len(self._samples),
            history_start_time=history_times[0] if history_times else None,
            history_end_time=history_times[-1] if history_times else None,
            history_digest=self._history_digest,
            command_class_vocabulary_digest=self._command_vocabulary_digest,
            candidate_edge_count=len(self._candidate_edges),
            causal_edge_count=len(self._pruned_edges),
            dag_digest=self._dag_digest,
            parameter_digest=self._parameter_digest,
            minimum_history_samples=self.minimum_sample_count,
            confidence_status=confidence_status,
            topological_order=list(self._topological_order),
            variable_identity_level=self.variable_identity_level,
            variable_identity_source=self.variable_identity_source,
        )

    @staticmethod
    def _representative_nodes(evidence: list[EvidenceNode]) -> dict[str, EvidenceNode]:
        by_type: dict[str, EvidenceNode] = {}
        for node in evidence:
            current = by_type.get(node.evidence_type)
            node_key = (
                node.timestamp.isoformat() if node.timestamp is not None else "",
                node.integrity_hash,
                node.source,
            )
            if current is None:
                by_type[node.evidence_type] = node
                continue
            current_key = (
                current.timestamp.isoformat() if current.timestamp is not None else "",
                current.integrity_hash,
                current.source,
            )
            if node_key > current_key:
                by_type[node.evidence_type] = node
        return dict(sorted(by_type.items()))

    def apply(
        self,
        frame: SemanticFrame,
        evidence: list[EvidenceNode],
        memory: MemoryPropagationResult,
        *,
        availability_by_type: dict[str, float | None] | None = None,
        availability_source: str = "QUALITY_WINDOW_SHORT_TERM_AT_DECISION",
        current_turn_id: str | None = None,
    ) -> CausalCorrectionResult:
        started = perf_counter()
        with self._lock:
            records = list(self._records)
            samples = list(self._samples)
            candidates = list(self._candidate_edges)
            pruned = list(self._pruned_edges)
            removed = list(self._removed_edges)
            excluded_count = self._excluded_count
            model_build_id = self._model_build_id
            model_built_at = self._last_rebuilt_at
            source_audit_count = self._source_audit_count
        if current_turn_id is not None:
            records = [record for record in records if record.turn_id != current_turn_id]
            samples = [sample for sample in samples if sample["turn_id"] != current_turn_id]

        nodes = self._representative_nodes(evidence)
        availability_values = availability_by_type
        effective_availability_source = availability_source
        if availability_values is None:
            # Internal compatibility only; production passes the frozen quality-window values.
            availability_values = {key: node.availability for key, node in nodes.items()}
            effective_availability_source = "LEGACY_INTERNAL_CALL_CURRENT_NODE_AVAILABILITY"

        prior_components: list[CausalPriorComponents] = []
        raw_scores: dict[str, float] = {}
        missing_availability: list[str] = []
        for variable, node in nodes.items():
            availability = availability_values.get(variable)
            status = "AVAILABLE" if availability is not None else "INSUFFICIENT_AVAILABILITY"
            if availability is None:
                missing_availability.append(variable)
            mandatory_component = (
                1.0
                if node.mandatory
                and node.quality_label not in {EvidenceStatus.MISSING, EvidenceStatus.TAMPERED}
                and node.availability > 0
                else 0.0
            )
            layer_confidence = memory.final_confidences.get(
                node.node_id, memory.post_weights.get(node.node_id)
            )
            raw_score = None
            if availability is not None and layer_confidence is not None:
                raw_score = (
                    self.lambda_values["sas"] * node.semantic_similarity
                    + self.lambda_values["layer_confidence"] * float(layer_confidence)
                    + self.lambda_values["freshness"] * node.freshness
                    + self.lambda_values["historical_availability"] * float(availability)
                    + self.lambda_values["mandatory"] * mandatory_component
                )
                raw_scores[variable] = raw_score
            prior_components.append(
                CausalPriorComponents(
                    node_id=node.node_id,
                    causal_variable=variable,
                    sas_component=node.semantic_similarity,
                    layer_confidence_component=layer_confidence,
                    freshness_component=node.freshness,
                    availability_component=availability,
                    mandatory_component=mandatory_component,
                    lambda_values=dict(self.lambda_values),
                    raw_prior_score=round(raw_score, 12) if raw_score is not None else None,
                    availability_source=effective_availability_source,
                    availability_status=status,
                )
            )

        priors = self._softmax(raw_scores)
        prior_by_node = {
            nodes[variable].node_id: value for variable, value in priors.items()
        }
        prior_node_weights = [
            CausalNodeWeight(
                node_id=nodes[variable].node_id,
                causal_variable=variable,
                prior_probability=round(priors[variable], 12),
            )
            for variable in sorted(priors)
        ]

        base_payload: dict[str, Any] = {
            "causal_graph": {
                "variables": sorted(nodes),
                "C": f"{frame.action}|{frame.target}",
                "Y": "HISTORICAL_FINAL_DECISION",
                "Zi": "BINARY_ACTIVATION",
                "Ecausal": [edge.model_dump(mode="json") for edge in pruned],
                "Theta": "HISTORICAL_CONDITIONAL_COUNTS",
                "acyclic": True,
            },
            "candidate_edges": candidates,
            "pruned_edges": pruned,
            "removed_edges": removed,
            "prior_components": prior_components,
            "sample_count": len(samples),
            "minimum_sample_count": self.minimum_sample_count,
            "model_version": model_build_id,
            "model_built_at": model_built_at,
            "source_audit_count": source_audit_count,
            "learning_record_ids": [record.audit_id for record in records],
            "excluded_record_count": excluded_count,
            "formula_version": self.formula_version,
            "variable_identity_version": self.variable_identity_version,
            "advanced_reasoning_applied": True,
            "feature_cutoff": "pre_decision",
            "used_features": [
                f"semantic.command_class={frame.action}|{frame.target}",
                *[f"evidence.variable={value}" for value in sorted(nodes)],
            ],
        }

        if len(samples) < self.minimum_sample_count:
            status = "INSUFFICIENT_HISTORY"
            return CausalCorrectionResult(
                **base_payload,
                model_snapshot=self._snapshot(status),
                prior_probabilities={
                    key: round(value, 12) for key, value in priors.items()
                },
                semantic_prior={
                    key: round(value, 12) for key, value in priors.items()
                },
                node_weights=prior_node_weights,
                confidence_status=status,
                data_sufficiency="insufficient",
                posterior_weights={
                    key: round(value, 12) for key, value in prior_by_node.items()
                },
                insufficiency_reason=(
                    f"history_sample_count={len(samples)} < "
                    f"minimum_history_samples={self.minimum_sample_count}"
                ),
                duration_ms=round((perf_counter() - started) * 1000, 4),
            )
        if missing_availability:
            status = "INSUFFICIENT_AVAILABILITY"
            return CausalCorrectionResult(
                **base_payload,
                model_snapshot=self._snapshot(status),
                prior_probabilities={
                    key: round(value, 12) for key, value in priors.items()
                },
                semantic_prior={
                    key: round(value, 12) for key, value in priors.items()
                },
                node_weights=prior_node_weights,
                confidence_status=status,
                data_sufficiency="sufficient",
                insufficiency_reason="missing availability: " + ",".join(missing_availability),
                duration_ms=round((perf_counter() - started) * 1000, 4),
            )
        if not raw_scores:
            status = "INSUFFICIENT"
            return CausalCorrectionResult(
                **base_payload,
                model_snapshot=self._snapshot(status),
                prior_probabilities={
                    key: round(value, 12) for key, value in priors.items()
                },
                semantic_prior={
                    key: round(value, 12) for key, value in priors.items()
                },
                node_weights=prior_node_weights,
                confidence_status=status,
                data_sufficiency="sufficient",
                insufficiency_reason="no eligible causal variables",
                duration_ms=round((perf_counter() - started) * 1000, 4),
            )
        if len(priors) == 1:
            status = "SINGLE_NODE_UNDEFINED"
            return CausalCorrectionResult(
                **base_payload,
                model_snapshot=self._snapshot(status),
                prior_probabilities={
                    key: round(value, 12) for key, value in priors.items()
                },
                semantic_prior={
                    key: round(value, 12) for key, value in priors.items()
                },
                node_weights=prior_node_weights,
                posterior_weights={
                    key: round(value, 12) for key, value in prior_by_node.items()
                },
                confidence_status=status,
                data_sufficiency="sufficient",
                insufficiency_reason=(
                    "equation 2.15 entropy normalization is undefined for n=1"
                ),
                duration_ms=round((perf_counter() - started) * 1000, 4),
            )
        command_class = f"{frame.action}|{frame.target}"
        class_vocabulary = sorted({sample["command_class"] for sample in samples})
        class_cardinality = len(class_vocabulary)
        parents_by_variable: dict[str, list[str]] = defaultdict(list)
        for edge in pruned:
            if edge.parent_variable and edge.child_variable:
                parents_by_variable[edge.child_variable].append(edge.parent_variable)
        for variable in parents_by_variable:
            parents_by_variable[variable] = sorted(set(parents_by_variable[variable]))

        parent_stats: list[ParentStateStatistics] = []
        rho_values: dict[str, float] = {}
        current_active = set(nodes)
        for variable in sorted(nodes):
            parents = parents_by_variable.get(variable, [])
            signature_bits = [1 if parent in current_active else 0 for parent in parents]
            signature = "EMPTY" if not parents else ",".join(
                f"{parent}={bit}" for parent, bit in zip(parents, signature_bits, strict=True)
            )

            def matches_parent_state(sample: dict[str, Any]) -> bool:
                active = set(sample["active_evidence_variables"])
                return all(
                    (parent in active) == bool(bit)
                    for parent, bit in zip(parents, signature_bits, strict=True)
                )

            node_parent_count = sum(
                variable in set(sample["active_evidence_variables"])
                and matches_parent_state(sample)
                for sample in samples
            )
            class_count = sum(
                sample["command_class"] == command_class
                and variable in set(sample["active_evidence_variables"])
                and matches_parent_state(sample)
                for sample in samples
            )
            rho = (class_count + self.laplace_epsilon) / (
                node_parent_count + self.laplace_epsilon * class_cardinality
            )
            rho_values[variable] = rho
            parent_stats.append(
                ParentStateStatistics(
                    node_id=nodes[variable].node_id,
                    causal_variable=variable,
                    parent_variables=parents,
                    parent_state_signature=signature,
                    class_count_with_node_and_parents=class_count,
                    node_parent_count=node_parent_count,
                    class_cardinality=class_cardinality,
                    smoothing_epsilon=self.laplace_epsilon,
                    rho=round(rho, 12),
                )
            )

        unnormalized = {
            variable: priors[variable] * rho_values[variable]
            for variable in sorted(nodes)
        }
        total_unnormalized = sum(unnormalized.values())
        if total_unnormalized <= 0:
            status = "INSUFFICIENT"
            return CausalCorrectionResult(
                **base_payload,
                model_snapshot=self._snapshot(status),
                parent_state_statistics=parent_stats,
                prior_probabilities=priors,
                semantic_prior=priors,
                node_weights=prior_node_weights,
                rho_values=rho_values,
                confidence_status=status,
                data_sufficiency="sufficient",
                insufficiency_reason="all unnormalized posterior weights are zero",
                duration_ms=round((perf_counter() - started) * 1000, 4),
            )
        denominator = total_unnormalized + self.numeric_epsilon
        corrected_by_variable = {
            variable: value / denominator for variable, value in unnormalized.items()
        }
        entropy = -sum(
            weight * math.log(weight + self.numeric_epsilon)
            for weight in corrected_by_variable.values()
        )
        node_count = len(corrected_by_variable)
        entropy_normalizer = math.log(node_count + self.numeric_epsilon)
        calibration_factor = (
            1.0 - entropy / entropy_normalizer if entropy_normalizer > 0 else 1.0
        )
        confidence = max(corrected_by_variable.values()) * calibration_factor
        if -1e-9 <= confidence <= 1 + 1e-9:
            confidence = min(1.0, max(0.0, confidence))
        else:
            raise ValueError(f"式2.15结果越界: {confidence}")
        node_weights = [
            CausalNodeWeight(
                node_id=nodes[variable].node_id,
                causal_variable=variable,
                prior_probability=round(priors[variable], 12),
                causal_support=round(rho_values[variable], 12),
                unnormalized_weight=round(unnormalized[variable], 12),
                corrected_weight=round(corrected_by_variable[variable], 12),
            )
            for variable in sorted(nodes)
        ]
        corrected_by_node = {
            item.node_id: float(item.corrected_weight or 0.0) for item in node_weights
        }
        normalized_entropy = (
            entropy / entropy_normalizer if entropy_normalizer > 0 else 0.0
        )
        status = "AVAILABLE"
        return CausalCorrectionResult(
            **base_payload,
            model_snapshot=self._snapshot(status),
            parent_state_statistics=parent_stats,
            prior_probabilities={key: round(value, 12) for key, value in priors.items()},
            semantic_prior={key: round(value, 12) for key, value in priors.items()},
            rho_values={key: round(value, 12) for key, value in rho_values.items()},
            historical_support={key: round(value, 12) for key, value in rho_values.items()},
            posterior_weights=corrected_by_node,
            corrected_weights=corrected_by_node,
            node_weights=node_weights,
            posterior_concentration=round(max(corrected_by_variable.values()), 12),
            decision_confidence=round(confidence, 12),
            confidence_status=status,
            data_sufficiency="sufficient",
            entropy=round(entropy, 12),
            normalized_entropy=round(max(0.0, min(1.0, normalized_entropy)), 12),
            duration_ms=round((perf_counter() - started) * 1000, 4),
        )
