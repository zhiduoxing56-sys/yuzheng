from __future__ import annotations

import math
from collections import defaultdict
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
    """使用可学习审计记录构建无环共现图并执行平滑后验修正。"""

    def __init__(self, config: dict[str, Any]) -> None:
        self.alpha = float(config.get("laplace_alpha", 1.0))
        self.outcome_count = int(config.get("outcome_count", 3))
        self.sufficient_count = int(config.get("sufficient_sample_count", 5))
        self.prior_floor = float(config.get("prior_floor", 0.001))
        self.risk_priors = {
            key: float(value) for key, value in config.get("risk_priors", {}).items()
        }
        self._records: list[AuditRecord] = []
        self._candidate_edges: list[CausalEdge] = []
        self._pruned_edges: list[CausalEdge] = []
        self._last_rebuilt_at = None
        self._excluded_count = 0

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

    def rebuild(
        self, records: list[AuditRecord], excluded_record_count: int
    ) -> CausalStatus:
        self._records = list(records)
        self._excluded_count = excluded_record_count
        edge_counts: dict[tuple[str, str, str], int] = defaultdict(int)
        for record in self._records:
            semantic = self._semantic_node(record)
            decision = f"decision:{record.final_decision.final_decision.value}"
            evidence_nodes = self._evidence_nodes(record)
            if not evidence_nodes:
                edge_counts[(semantic, decision, "SEMANTIC_OUTCOME")] += 1
            for evidence in evidence_nodes:
                edge_counts[(semantic, evidence, "SEMANTIC_GROUNDS_EVIDENCE")] += 1
                edge_counts[(evidence, decision, "EVIDENCE_SUPPORTS_OUTCOME")] += 1

        denominator = max(1, len(self._records))
        candidates = [
            CausalEdge(
                source=source,
                target=target,
                relation=relation,
                support=min(1.0, count / denominator),
                sample_count=count,
                reason="可信审计中的时间有序共现",
            )
            for (source, target, relation), count in sorted(edge_counts.items())
        ]
        graph = nx.DiGraph()
        pruned: list[CausalEdge] = []
        for edge in candidates:
            graph.add_edge(edge.source, edge.target)
            if nx.is_directed_acyclic_graph(graph):
                pruned.append(edge)
            else:
                graph.remove_edge(edge.source, edge.target)
        self._candidate_edges = candidates
        self._pruned_edges = pruned
        self._last_rebuilt_at = utc_now()
        return self.status()

    def status(self) -> CausalStatus:
        nodes = {
            endpoint
            for edge in self._pruned_edges
            for endpoint in (edge.source, edge.target)
        }
        return CausalStatus(
            learning_record_count=len(self._records),
            excluded_record_count=self._excluded_count,
            candidate_edge_count=len(self._candidate_edges),
            pruned_edge_count=len(self._pruned_edges),
            graph_node_count=len(nodes),
            graph_edge_count=len(self._pruned_edges),
            last_rebuilt_at=self._last_rebuilt_at,
            data_sufficiency=(
                "sufficient" if len(self._records) >= self.sufficient_count else "insufficient"
            ),
        )

    @staticmethod
    def _rounded_distribution(values: dict[str, float]) -> dict[str, float]:
        """Round deterministically while preserving an exact serialized sum of one."""
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
        current_nodes = [node for node in evidence if node.mandatory]
        if not current_nodes:
            # 无强制证据时仍显式返回单一语义先验，避免空概率。
            keys = ["semantic_only"]
        else:
            latest: dict[str, EvidenceNode] = {}
            for node in current_nodes:
                latest[node.evidence_type] = node
            current_nodes = [latest[key] for key in sorted(latest)]
            keys = [node.node_id for node in current_nodes]

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
                matching: list[AuditRecord] = self._records
            else:
                matching = [
                    record
                    for record in self._records
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
        if len(posterior) <= 1:
            entropy = 0.0
        else:
            entropy = -sum(
                probability * math.log(probability)
                for probability in posterior.values()
                if probability > 0
            ) / math.log(len(posterior))
        confidence = max(0.0, min(1.0, 1.0 - entropy))
        graph_nodes = sorted(
            {
                endpoint
                for edge in self._pruned_edges
                for endpoint in (edge.source, edge.target)
            }
        )
        duration_ms = (perf_counter() - started) * 1000
        serialized_prior = self._rounded_distribution(semantic_prior)
        serialized_posterior = self._rounded_distribution(posterior)
        return CausalCorrectionResult(
            causal_graph={
                "nodes": graph_nodes,
                "edges": [edge.model_dump(mode="json") for edge in self._pruned_edges],
                "acyclic": True,
            },
            candidate_edges=self._candidate_edges,
            pruned_edges=self._pruned_edges,
            semantic_prior=serialized_prior,
            historical_support={key: round(value, 8) for key, value in historical.items()},
            posterior_weights=serialized_posterior,
            corrected_weights=serialized_posterior,
            entropy=round(max(0.0, min(1.0, entropy)), 8),
            decision_confidence=round(confidence, 8),
            sample_count=len(self._records),
            data_sufficiency=(
                "sufficient" if len(self._records) >= self.sufficient_count else "insufficient"
            ),
            learning_record_ids=[record.audit_id for record in self._records],
            excluded_record_count=self._excluded_count,
            advanced_reasoning_applied=True,
            duration_ms=round(duration_ms, 4),
        )
