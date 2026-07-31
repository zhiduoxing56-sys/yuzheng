from __future__ import annotations

import hashlib
import json
from datetime import timedelta
from typing import Any

from app.models.schemas import (
    EvidenceDemand,
    EvidenceEdge,
    EvidenceNode,
    EvidenceQualityMetrics,
    EvidenceRelation,
    EvidenceStatus,
    EvidenceSubgraph,
    MandatoryRecallRecord,
    RetrievalMetadata,
    SemanticFrame,
    make_id,
    utc_now,
)


class EvidenceSubgraphBuilder:
    @staticmethod
    def _runtime_node(
        evidence_type: str, source: str, value: Any, layer: str, turn_id: str
    ) -> EvidenceNode:
        now = utc_now()
        payload = {
            "evidence_type": evidence_type,
            "source": source,
            "value": value,
            "timestamp": now.isoformat(),
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return EvidenceNode(
            evidence_type=evidence_type,
            layer=layer,
            source=source,
            value=value,
            timestamp=now,
            expires_at=now + timedelta(minutes=5),
            freshness=1,
            consistency=1,
            availability=1,
            semantic_similarity=1,
            mandatory=False,
            quality_label=EvidenceStatus.VALID,
            integrity_hash=digest,
            metadata={"turn_id": turn_id, "integrity_payload": payload, "expected_integrity_hash": digest},
        )

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
        demand: EvidenceDemand,
        evidence_nodes: list[EvidenceNode],
        recall_records: list[MandatoryRecallRecord],
        recalled_types: list[str],
        missing_types: list[str],
        quality_metrics: EvidenceQualityMetrics,
        retrieval_metadata: RetrievalMetadata,
        conflicts: list[dict[str, Any]],
        safety_rule_nodes: list[EvidenceNode],
    ) -> EvidenceSubgraph:
        nodes_by_id = {node.node_id: node for node in evidence_nodes}
        demand_node = self._runtime_node(
            "evidence_demand",
            "semantic_pipeline",
            {"action": frame.action, "target": frame.target, "query_text": demand.query_text},
            "L2_DRIVING",
            frame.turn_id,
        )
        target_node = self._runtime_node(
            "control_target", "semantic_pipeline", frame.target, "L1_CABIN", frame.turn_id
        )
        nodes_by_id[demand_node.node_id] = demand_node
        nodes_by_id[target_node.node_id] = target_node
        edges: list[EvidenceEdge] = []

        mandatory_nodes = [node for node in evidence_nodes if node.mandatory]
        for node in mandatory_nodes:
            edges.append(
                self._edge(
                    demand_node.node_id,
                    node.node_id,
                    EvidenceRelation.REQUIRES,
                    1.0,
                    f"{frame.action}|{frame.target} 强制要求 {node.evidence_type}",
                )
            )

        for node in evidence_nodes:
            if node.evidence_type not in {"safety_rule", "evidence_stream"}:
                edges.append(
                    self._edge(
                        node.node_id,
                        target_node.node_id,
                        EvidenceRelation.SUPPORTS,
                        max(0.1, node.availability * max(node.freshness, 0.1)),
                        f"{node.evidence_type} 为控制对象 {frame.target} 提供状态证据",
                    )
                )
            if node.evidence_type == "occupant_role":
                edges.append(
                    self._edge(
                        node.node_id,
                        target_node.node_id,
                        EvidenceRelation.PERMISSION_BOUND,
                        1.0,
                        "乘员角色约束控制对象权限",
                    )
                )

        for rule_node in safety_rule_nodes:
            rule = rule_node.value if isinstance(rule_node.value, dict) else {}
            if rule.get("action") == frame.action and rule.get("target") == frame.target:
                nodes_by_id[rule_node.node_id] = rule_node
                edges.append(
                    self._edge(
                        rule_node.node_id,
                        target_node.node_id,
                        EvidenceRelation.RULE_CONSTRAINED,
                        1.0,
                        str(rule.get("reason", "安全规则约束")),
                    )
                )

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
            history.sort(key=lambda node: (node.timestamp, node.node_id))
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

        for record in recall_records:
            if record.status != "RECALLED" or record.recalled_node_id not in nodes_by_id:
                continue
            stream_node = self._runtime_node(
                "evidence_stream",
                "evidence_repository",
                record.evidence_type,
                "L2_DRIVING",
                frame.turn_id,
            )
            nodes_by_id[stream_node.node_id] = stream_node
            edges.append(
                self._edge(
                    record.recalled_node_id,
                    stream_node.node_id,
                    EvidenceRelation.DERIVED_FROM,
                    1.0,
                    "强制补召节点来自最新证据流",
                )
            )

        return EvidenceSubgraph(
            graph_id=make_id("GRAPH"),
            turn_id=frame.turn_id,
            nodes=list(nodes_by_id.values()),
            edges=edges,
            required_types=demand.required_types,
            retrieved_types=sorted({node.evidence_type for node in evidence_nodes}),
            mandatory_recalled_types=sorted(recalled_types),
            missing_types=sorted(missing_types),
            quality_metrics=quality_metrics,
            retrieval_metadata=retrieval_metadata,
            corrected_weights={},
            decision_confidence=None,
            advanced_reasoning_applied=False,
            advanced_reasoning_status="NOT_APPLICABLE_STAGE2",
        )
