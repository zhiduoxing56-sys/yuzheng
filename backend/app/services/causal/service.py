from __future__ import annotations

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
    CausalStatus,
    DecisionLabel,
    EvidenceNode,
    MemoryPropagationResult,
    SemanticFrame,
    utc_now,
)


class CausalCorrectionService:
    """使用裁决前冻结的历史模型执行因果排序，不参与覆盖 Safety Gate。"""

    def __init__(self, config: dict[str, Any]) -> None:
        self.alpha = float(config.get("laplace_alpha", 1.0))
        self.outcome_count = int(config.get("outcome_count", 3))
        self.minimum_sample_count = int(
            config.get("minimum_samples_for_confidence", 20)
        )
        self.prior_floor = float(config.get("prior_floor", 0.001))
        self.auto_rebuild_enabled = bool(config.get("auto_rebuild_enabled", True))
        self.rebuild_every_eligible_audits = int(
            config.get("rebuild_every_eligible_audits", 20)
        )
        self.maximum_training_records = int(config.get("maximum_training_records", 5000))
        self.risk_priors = {
            key: float(value) for key, value in config.get("risk_priors", {}).items()
        }
        self._lock = RLock()
        self._records: list[AuditRecord] = []
        self._candidate_edges: list[CausalEdge] = []
        self._pruned_edges: list[CausalEdge] = []
        self._removed_edges: list[CausalEdge] = []
        self._last_rebuilt_at = None
        self._excluded_count = 0
        self._model_version = "causal-v0"
        self._source_audit_count = 0
        self._auto_rebuild_running = False
        self._last_rebuild_error: str | None = None

    @staticmethod
    def _semantic_node(record: AuditRecord) -> str:
        frame = record.semantic_frame
        return f"semantic:{frame.action}|{frame.target}|{frame.risk_level}"

    @staticmethod
    def _evidence_nodes(record: AuditRecord) -> list[str]:
        if record.evidence_subgraph is None:
            return []
        required = set(record.semantic_frame.required_evidence_types)
        return sorted(
            {
                f"evidence:{node.evidence_type}:{node.quality_label.value}"
                for node in record.evidence_subgraph.nodes
                if node.evidence_type in required
            }
        )

    @staticmethod
    def _next_version(current: str) -> str:
        try:
            return f"causal-v{int(current.rsplit('v', 1)[1]) + 1}"
        except (IndexError, ValueError):
            return "causal-v1"

    @staticmethod
    def _build_edges(records: list[AuditRecord]) -> list[CausalEdge]:
        edge_counts: dict[tuple[str, str, str], int] = defaultdict(int)
        for record in records:
            semantic = CausalCorrectionService._semantic_node(record)
            decision = f"decision:{record.final_decision.final_decision.value}"
            evidence_nodes = CausalCorrectionService._evidence_nodes(record)
            if not evidence_nodes:
                edge_counts[(semantic, decision, "SEMANTIC_OUTCOME")] += 1
            for evidence in evidence_nodes:
                edge_counts[(semantic, evidence, "SEMANTIC_GROUNDS_EVIDENCE")] += 1
                edge_counts[(evidence, decision, "EVIDENCE_SUPPORTS_OUTCOME")] += 1
        denominator = max(1, len(records))
        return [
            CausalEdge(
                source=source,
                target=target,
                relation=relation,
                support=min(1.0, count / denominator),
                sample_count=count,
                reason="可信历史审计中的时间有序共现",
            )
            for (source, target, relation), count in sorted(edge_counts.items())
        ]

    def rebuild(
        self,
        records: list[AuditRecord],
        excluded_record_count: int,
        *,
        restore_metadata: dict[str, Any] | None = None,
        source_audit_count: int | None = None,
    ) -> CausalStatus:
        bounded = list(records[-self.maximum_training_records :])
        candidates = self._build_edges(bounded)
        pruned, removed = self.prune_candidate_edges(candidates)
        built_at = utc_now()
        with self._lock:
            self._records = bounded
            self._excluded_count = excluded_record_count
            self._candidate_edges = candidates
            self._pruned_edges = pruned
            self._removed_edges = removed
            if restore_metadata:
                self._model_version = str(
                    restore_metadata.get("model_version", self._model_version)
                )
                self._last_rebuilt_at = restore_metadata.get("model_built_at") or built_at
            else:
                self._model_version = self._next_version(self._model_version)
                self._last_rebuilt_at = built_at
            self._source_audit_count = (
                int(source_audit_count)
                if source_audit_count is not None
                else len(bounded)
            )
            self._last_rebuild_error = None
            self._auto_rebuild_running = False
        return self.status()

    def model_metadata(self) -> dict[str, Any]:
        with self._lock:
            return {
                "model_version": self._model_version,
                "model_built_at": (
                    self._last_rebuilt_at.isoformat()
                    if hasattr(self._last_rebuilt_at, "isoformat")
                    else self._last_rebuilt_at
                ),
                "source_audit_count": self._source_audit_count,
                "minimum_sample_count": self.minimum_sample_count,
                "training_record_ids": [record.audit_id for record in self._records],
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
            nodes = {
                endpoint
                for edge in self._pruned_edges
                for endpoint in (edge.source, edge.target)
            }
            eligible = (
                self._source_audit_count
                if eligible_audit_count is None
                else eligible_audit_count
            )
            return CausalStatus(
                learning_record_count=len(self._records),
                excluded_record_count=self._excluded_count,
                candidate_edge_count=len(self._candidate_edges),
                pruned_edge_count=len(self._pruned_edges),
                removed_edge_count=len(self._removed_edges),
                graph_node_count=len(nodes),
                graph_edge_count=len(self._pruned_edges),
                last_rebuilt_at=self._last_rebuilt_at,
                data_sufficiency=(
                    "sufficient"
                    if len(self._records) >= self.minimum_sample_count
                    else "insufficient"
                ),
                minimum_sample_count=self.minimum_sample_count,
                model_version=self._model_version,
                model_built_at=self._last_rebuilt_at,
                source_audit_count=self._source_audit_count,
                auto_rebuild_enabled=self.auto_rebuild_enabled,
                rebuild_every_eligible_audits=self.rebuild_every_eligible_audits,
                eligible_audits_since_rebuild=max(0, eligible - self._source_audit_count),
                auto_rebuild_running=self._auto_rebuild_running,
                last_rebuild_error=self._last_rebuild_error,
            )

    @staticmethod
    def prune_candidate_edges(
        edges: list[CausalEdge],
    ) -> tuple[list[CausalEdge], list[CausalEdge]]:
        """Deterministically remove edges that would introduce a directed cycle."""
        graph = nx.DiGraph()
        kept: list[CausalEdge] = []
        removed: list[CausalEdge] = []
        for edge in sorted(
            edges,
            key=lambda item: (
                item.source,
                item.target,
                item.relation,
                -item.support,
                -item.sample_count,
            ),
        ):
            graph.add_edge(edge.source, edge.target)
            if nx.is_directed_acyclic_graph(graph):
                kept.append(edge)
                continue
            graph.remove_edge(edge.source, edge.target)
            removed.append(
                edge.model_copy(
                    update={
                        "reason": (
                            f"removed to preserve DAG: adding {edge.source}->{edge.target} "
                            "would create a directed cycle"
                        )
                    }
                )
            )
        return kept, removed

    @staticmethod
    def _rounded_distribution(values: dict[str, float]) -> dict[str, float]:
        keys = list(values)
        if not keys:
            return {}
        rounded: dict[str, float] = {}
        running = 0.0
        for key in keys[:-1]:
            value = round(values[key], 8)
            rounded[key] = value
            running += value
        rounded[keys[-1]] = round(max(0.0, 1.0 - running), 8)
        return rounded

    def apply(
        self,
        frame: SemanticFrame,
        evidence: list[EvidenceNode],
        memory: MemoryPropagationResult,
    ) -> CausalCorrectionResult:
        started = perf_counter()
        with self._lock:
            records = list(self._records)
            candidates = list(self._candidate_edges)
            pruned = list(self._pruned_edges)
            removed = list(self._removed_edges)
            excluded_count = self._excluded_count
            model_version = self._model_version
            model_built_at = self._last_rebuilt_at
            source_audit_count = self._source_audit_count

        current_nodes = [node for node in evidence if node.mandatory]
        if not current_nodes:
            keys = ["semantic_only"]
        else:
            latest: dict[str, EvidenceNode] = {}
            for node in current_nodes:
                latest[node.evidence_type] = node
            current_nodes = [latest[key] for key in sorted(latest)]
            keys = [node.node_id for node in current_nodes]

        used_features = [
            f"semantic.action={frame.action}",
            f"semantic.target={frame.target}",
            f"semantic.risk_level={frame.risk_level}",
        ]
        used_features.extend(
            f"evidence.{node.evidence_type}.status={node.quality_label.value}"
            for node in current_nodes
        )
        used_features.extend(
            f"memory.pre_decision_weight.{node.evidence_type}={memory.post_weights.get(node.node_id, 0.5):.6f}"
            for node in current_nodes
        )

        risk_prior = self.risk_priors.get(frame.risk_level, 0.75)
        raw_priors: dict[str, float] = {}
        historical: dict[str, float] = {}
        raw_posterior: dict[str, float] = {}
        for key in keys:
            node = next((item for item in current_nodes if item.node_id == key), None)
            memory_weight = memory.post_weights.get(key, 0.5) if node else 0.5
            prior = max(self.prior_floor, risk_prior * (0.5 + 0.5 * memory_weight))
            raw_priors[key] = prior
            if node is None:
                matching = records
            else:
                matching = [
                    record
                    for record in records
                    if record.evidence_subgraph is not None
                    and any(
                        historical_node.evidence_type == node.evidence_type
                        and historical_node.quality_label == node.quality_label
                        for historical_node in record.evidence_subgraph.nodes
                    )
                ]
            pass_count = sum(
                record.final_decision.final_decision == DecisionLabel.PASS
                for record in matching
            )
            support = (pass_count + self.alpha) / (
                len(matching) + self.alpha * self.outcome_count
            )
            historical[key] = support
            raw_posterior[key] = max(self.prior_floor, prior * support)

        prior_total = sum(raw_priors.values()) or 1.0
        semantic_prior = {key: value / prior_total for key, value in raw_priors.items()}
        posterior_total = sum(raw_posterior.values()) or 1.0
        posterior = {key: value / posterior_total for key, value in raw_posterior.items()}
        entropy = -sum(
            probability * math.log(probability)
            for probability in posterior.values()
            if probability > 0
        )
        normalized_entropy = (
            entropy / math.log(len(posterior)) if len(posterior) > 1 else 0.0
        )
        concentration = max(0.0, min(1.0, 1.0 - normalized_entropy))
        sample_count = len(records)
        if len(posterior) < 2:
            confidence_status = "SINGLE_NODE_UNDEFINED"
            decision_confidence = None
        elif model_built_at is None:
            confidence_status = "MODEL_NOT_READY"
            decision_confidence = None
        elif sample_count < self.minimum_sample_count:
            confidence_status = "INSUFFICIENT_DATA"
            decision_confidence = None
        else:
            confidence_status = "AVAILABLE"
            decision_confidence = round(concentration, 8)

        graph_nodes = sorted(
            {endpoint for edge in pruned for endpoint in (edge.source, edge.target)}
        )
        duration_ms = (perf_counter() - started) * 1000
        return CausalCorrectionResult(
            causal_graph={
                "nodes": graph_nodes,
                "edges": [edge.model_dump(mode="json") for edge in pruned],
                "removed_edges": [edge.model_dump(mode="json") for edge in removed],
                "acyclic": True,
            },
            candidate_edges=candidates,
            pruned_edges=pruned,
            removed_edges=removed,
            semantic_prior=self._rounded_distribution(semantic_prior),
            historical_support={key: round(value, 8) for key, value in historical.items()},
            posterior_weights=self._rounded_distribution(posterior),
            corrected_weights=self._rounded_distribution(posterior),
            posterior_concentration=round(concentration, 8),
            decision_confidence=decision_confidence,
            confidence_status=confidence_status,
            sample_count=sample_count,
            minimum_sample_count=self.minimum_sample_count,
            data_sufficiency=(
                "sufficient" if sample_count >= self.minimum_sample_count else "insufficient"
            ),
            entropy=round(max(0.0, entropy), 8),
            normalized_entropy=round(max(0.0, min(1.0, normalized_entropy)), 8),
            model_version=model_version,
            model_built_at=model_built_at,
            source_audit_count=source_audit_count,
            learning_record_ids=[record.audit_id for record in records],
            excluded_record_count=excluded_count,
            advanced_reasoning_applied=True,
            feature_cutoff="pre_decision",
            used_features=used_features,
            duration_ms=round(duration_ms, 4),
        )
