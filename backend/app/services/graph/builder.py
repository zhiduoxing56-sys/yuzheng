from __future__ import annotations

from typing import Any

from app.models.schemas import (
    EvidenceEdge,
    EvidenceNode,
    EvidenceQualityMetrics,
    EvidenceRelation,
    EvidenceSubgraph,
    IntentEvidenceResolution,
    RetrievalMetadata,
    SemanticFrame,
    make_id,
)
from app.services.evidence.canonicalization import (
    canonicalize_evidence_nodes,
    evaluated_node_source,
)


class EvidenceSubgraphBuilder:
    @staticmethod
    def _edge(
        source: str,
        target: str,
        relation: EvidenceRelation,
        weight: float,
        reason: str,
    ) -> EvidenceEdge:
        return EvidenceEdge(
            source=source,
            target=target,
            relation=relation,
            weight=weight,
            reason=reason,
        )

    def build(
        self,
        frame: SemanticFrame,
        evidence_nodes: list[EvidenceNode],
        intent_evidence_resolutions: list[IntentEvidenceResolution],
        quality_metrics: EvidenceQualityMetrics,
        retrieval_metadata: RetrievalMetadata,
        conflicts: list[dict[str, Any]],
    ) -> EvidenceSubgraph:
        evaluated_groups: dict[str, list[EvidenceNode]] = {}
        for node in evidence_nodes:
            evaluated_groups.setdefault(evaluated_node_source(node), []).append(node)
        canonical_nodes = canonicalize_evidence_nodes(sorted(evaluated_groups.items()))
        nodes_by_id = {node.node_id: node for node in canonical_nodes}
        edges: list[EvidenceEdge] = []

        for conflict in conflicts:
            node_ids = [node_id for node_id in conflict.get("node_ids", []) if node_id in nodes_by_id]
            for index, left in enumerate(node_ids):
                for right in node_ids[index + 1 :]:
                    edges.append(
                        self._edge(
                            left,
                            right,
                            EvidenceRelation.CONFLICTS,
                            min(1.0, float(conflict.get("severity", 1)) / 3),
                            str(conflict.get("reason", "多源证据冲突")),
                        )
                    )

        grouped: dict[tuple[str, str], list[EvidenceNode]] = {}
        for node in evidence_nodes:
            grouped.setdefault((node.evidence_type, node.source), []).append(node)
        for history in grouped.values():
            history.sort(
                key=lambda node: (
                    node.timestamp.isoformat() if node.timestamp else "",
                    node.node_id,
                )
            )
            for previous, current in zip(history, history[1:]):
                edges.append(
                    self._edge(
                        previous.node_id,
                        current.node_id,
                        EvidenceRelation.TEMPORAL,
                        0.8,
                        "同一证据流的时间演化",
                    )
                )

        return EvidenceSubgraph(
            graph_id=make_id("GRAPH"),
            turn_id=frame.turn_id,
            nodes=list(nodes_by_id.values()),
            edges=edges,
            intent_evidence_resolutions=intent_evidence_resolutions,
            retrieved_types=sorted({node.evidence_type for node in evidence_nodes}),
            quality_metrics=quality_metrics,
            retrieval_metadata=retrieval_metadata,
            corrected_weights={},
            decision_confidence=None,
            advanced_reasoning_applied=False,
            advanced_reasoning_status="NOT_APPLICABLE_STAGE2",
        )
