from __future__ import annotations

from time import perf_counter
from typing import Any

from app.models.schemas import (
    EvidenceNode,
    EvidenceRelation,
    EvidenceStatus,
    MemoryLink,
    MemoryPropagationResult,
    SemanticFrame,
)


STATUS_WEIGHT = {
    EvidenceStatus.VALID: 1.0,
    EvidenceStatus.SUSPICIOUS: 0.5,
    EvidenceStatus.STALE: 0.2,
    EvidenceStatus.TAMPERED: 0.0,
    EvidenceStatus.MISSING: 0.0,
}


class DualMemoryService:
    """确定性横向关联与仅从高安全层向低层的纵向传播。"""

    def __init__(self, config: dict[str, Any]) -> None:
        self.layers = {key: int(value) for key, value in config.get("layers", {}).items()}
        self.horizontal = config.get("horizontal", {})
        self.vertical = config.get("vertical", {})
        self.functional_pairs = {
            frozenset(pair) for pair in self.horizontal.get("functional_pairs", [])
        }
        self.allowed_paths = {
            tuple(pair) for pair in self.vertical.get("allowed_support_paths", [])
        }

    @staticmethod
    def _latest_nodes(nodes: list[EvidenceNode]) -> list[EvidenceNode]:
        latest: dict[tuple[str, str], EvidenceNode] = {}
        for node in nodes:
            key = (node.evidence_type, node.source)
            current = latest.get(key)
            if current is None or (node.timestamp, node.node_id) > (
                current.timestamp,
                current.node_id,
            ):
                latest[key] = node
        return sorted(latest.values(), key=lambda item: item.node_id)

    @staticmethod
    def _base_weight(node: EvidenceNode) -> float:
        status = STATUS_WEIGHT[node.quality_label]
        return max(
            0.0,
            min(1.0, status * node.freshness * max(0.0, node.consistency)),
        )

    def propagate(
        self,
        nodes: list[EvidenceNode],
        frame: SemanticFrame,
        conflicts: list[dict[str, Any]],
    ) -> MemoryPropagationResult:
        started = perf_counter()
        current = self._latest_nodes(nodes)
        pre = {node.node_id: round(self._base_weight(node), 6) for node in current}
        adjusted = dict(pre)
        conflict_pairs = {
            frozenset((left, right))
            for conflict in conflicts
            for index, left in enumerate(conflict.get("node_ids", []))
            for right in conflict.get("node_ids", [])[index + 1 :]
        }
        factors = self.horizontal.get("factors", {})
        time_window = float(self.horizontal.get("time_window_seconds", 30))
        support_coefficient = float(self.horizontal.get("support_coefficient", 0.08))
        conflict_penalty = float(self.horizontal.get("conflict_penalty", 0.25))
        horizontal_links: list[MemoryLink] = []
        support_weights: list[float] = []
        horizontal_conflicts = 0
        horizontal_started = perf_counter()

        for index, left in enumerate(current):
            for right in current[index + 1 :]:
                if left.layer != right.layer:
                    continue
                reasons: list[str] = []
                score = 0.0
                delta = abs((left.timestamp - right.timestamp).total_seconds())
                if delta <= time_window:
                    score += float(factors.get("same_time_window", 0))
                    reasons.append("同一时间窗口")
                if left.metadata.get("area") and left.metadata.get("area") == right.metadata.get("area"):
                    score += float(factors.get("same_area", 0))
                    reasons.append("同一区域")
                if left.source == right.source:
                    score += float(factors.get("same_source", 0))
                    reasons.append("相同来源")
                if left.evidence_type != right.evidence_type:
                    score += float(factors.get("semantic_complement", 0))
                    reasons.append("语义互补")
                if frozenset((left.evidence_type, right.evidence_type)) in self.functional_pairs:
                    score += float(factors.get("functional_dependency", 0))
                    reasons.append("功能依赖")
                if (
                    left.evidence_type in frame.required_evidence_types
                    and right.evidence_type in frame.required_evidence_types
                ):
                    score += float(factors.get("common_action_support", 0))
                    reasons.append("共同支持动作")
                if left.mandatory and right.mandatory:
                    score += float(factors.get("common_target_constraint", 0))
                    reasons.append("共同约束对象")
                score = max(0.0, min(1.0, score))
                if score == 0:
                    continue
                is_conflict = (
                    frozenset((left.node_id, right.node_id)) in conflict_pairs
                    or left.quality_label == EvidenceStatus.SUSPICIOUS
                    or right.quality_label == EvidenceStatus.SUSPICIOUS
                )
                if is_conflict:
                    horizontal_conflicts += 1
                    adjusted[left.node_id] = max(
                        0.0, adjusted[left.node_id] - conflict_penalty * score
                    )
                    adjusted[right.node_id] = max(
                        0.0, adjusted[right.node_id] - conflict_penalty * score
                    )
                    reasons.append("冲突抑制，禁止抬高可信度")
                else:
                    support_weights.append(score)
                    adjusted[left.node_id] = min(
                        1.0, adjusted[left.node_id] + support_coefficient * score * pre[right.node_id]
                    )
                    adjusted[right.node_id] = min(
                        1.0, adjusted[right.node_id] + support_coefficient * score * pre[left.node_id]
                    )
                horizontal_links.append(
                    MemoryLink(
                        source=left.node_id,
                        target=right.node_id,
                        relation=EvidenceRelation.HORIZONTAL_MEMORY,
                        weight=round(score, 6),
                        layer=left.layer,
                        reason="、".join(reasons),
                        conflict=is_conflict,
                    )
                )

        horizontal_duration_ms = (perf_counter() - horizontal_started) * 1000

        alpha = float(self.vertical.get("alpha", 0.3))
        risk_penalty = float(self.vertical.get("risk_penalty", 0.3))
        support_bonus = float(self.vertical.get("support_bonus", 0.05))
        vertical_links: list[MemoryLink] = []
        paths: list[dict[str, Any]] = []
        vertical_started = perf_counter()
        for source in current:
            source_rank = self.layers.get(source.layer, 0)
            for target in current:
                target_rank = self.layers.get(target.layer, 0)
                if source_rank <= target_rank:
                    continue
                source_risky = source.quality_label in {
                    EvidenceStatus.SUSPICIOUS,
                    EvidenceStatus.STALE,
                    EvidenceStatus.TAMPERED,
                    EvidenceStatus.MISSING,
                }
                support_allowed = (
                    source.evidence_type,
                    target.evidence_type,
                ) in self.allowed_paths
                if not source_risky and not support_allowed:
                    continue
                before = adjusted[target.node_id]
                if source_risky:
                    risk = max(1.0 - pre[source.node_id], 0.5)
                    after = max(0.0, before - alpha * risk_penalty * risk)
                    reason = "高安全层异常风险向低层单向传播"
                else:
                    after = min(1.0, before + alpha * support_bonus * pre[source.node_id])
                    reason = "领域规则允许的高层有效支持"
                if target.quality_label in {EvidenceStatus.TAMPERED, EvidenceStatus.MISSING}:
                    after = 0.0
                adjusted[target.node_id] = after
                link_weight = min(1.0, alpha * max(pre[source.node_id], 1.0 - pre[source.node_id]))
                vertical_links.append(
                    MemoryLink(
                        source=source.node_id,
                        target=target.node_id,
                        relation=EvidenceRelation.VERTICAL_PROPAGATION,
                        weight=round(link_weight, 6),
                        layer=f"{source.layer}->{target.layer}",
                        reason=reason,
                        conflict=source_risky,
                    )
                )
                paths.append(
                    {
                        "source": source.node_id,
                        "target": target.node_id,
                        "from_layer": source.layer,
                        "to_layer": target.layer,
                        "before": round(before, 6),
                        "after": round(after, 6),
                        "reason": reason,
                    }
                )

        vertical_duration_ms = (perf_counter() - vertical_started) * 1000

        post = {node_id: round(max(0.0, min(1.0, value)), 6) for node_id, value in adjusted.items()}
        duration_ms = (perf_counter() - started) * 1000
        return MemoryPropagationResult(
            horizontal_links=horizontal_links,
            horizontal_support=(
                round(sum(support_weights) / len(support_weights), 6)
                if support_weights
                else 0.0
            ),
            horizontal_conflicts=horizontal_conflicts,
            horizontal_adjustments=post,
            vertical_links=vertical_links,
            propagation_paths=paths,
            pre_weights=pre,
            post_weights=post,
            horizontal_duration_ms=round(horizontal_duration_ms, 4),
            vertical_duration_ms=round(vertical_duration_ms, 4),
            duration_ms=round(duration_ms, 4),
        )
