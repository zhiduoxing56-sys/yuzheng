"""情报智能体 v3 —— Layer 8: Human Review + Layer 9: Trusted Integration

Layer 8：审核决策（REJECT / MERGE / PROMOTE），全程留痕
Layer 9：晋级集成
  - Conflict Check：候选知识 vs Trusted 是否存在冲突（同意图不同约束 / 语义矛盾）
  - 晋级流程：PROMOTE → 生成 Trusted 版本节点 → 版本记录 → 重建 HNSW 信号
  - 安全边界：未审核 L5 节点绝不进入 Trusted Evidence Requirement（Candidate Leakage=0）
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from safety_knowledge.intelligence.models import CandidateRiskNode, ReviewVerdict, now_iso


# ==================== Layer 8: Human Review ====================

class ReviewBoard:
    """人工审核面板（决策留痕）。"""

    def __init__(self, review_log_path: Path) -> None:
        self._log_path = review_log_path
        review_log_path.parent.mkdir(parents=True, exist_ok=True)
        self._decisions: list[dict] = []
        if review_log_path.exists():
            self._decisions = [json.loads(line) for line in
                               review_log_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def decide(self, node: CandidateRiskNode, decision: ReviewVerdict, reviewer: str,
               reason: str, merged_into: str | None = None) -> dict:
        rec = {
            "cluster_id": node.metadata.get("cluster_id"),
            "node_id": node.node_id,
            "decision": decision.value,
            "reviewer": reviewer,
            "reviewed_at": now_iso(),
            "reason": reason,
            "merged_into": merged_into,
            "node_snapshot": {
                "title": node.title,
                "canonical_action": node.canonical_action,
                "required_evidence": node.required_evidence,
                "novelty": node.metadata.get("novelty_label"),
                "priority": node.metadata.get("review_priority"),
            },
        }
        self._decisions.append(rec)
        self._log_path.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in self._decisions),
                                  encoding="utf-8")
        return rec

    def export(self) -> list[dict]:
        return self._decisions


# ==================== Layer 9: Trusted Integration ====================

@dataclass
class ConflictReport:
    """冲突检查结果。"""

    node_id: str
    status: str                      # CLEAR / CONFLICT / OVERLAP / NEW_INTENT
    details: list[dict] = field(default_factory=list)
    recommendation: str = ""


class TrustedIntegrator:
    """晋级集成：Conflict Check → Version → Trusted 节点生成。"""

    def __init__(self, trusted_nodes: list[dict]) -> None:
        self._trusted = trusted_nodes
        # 意图 → 节点
        self._intent_nodes: dict[str, list[dict]] = {}
        for n in trusted_nodes:
            action = n.get("canonical_action", "")
            if action:
                self._intent_nodes.setdefault(action, []).append(n)

    # ---------- Conflict Check ----------

    def check_conflict(self, node: CandidateRiskNode) -> ConflictReport:
        action = node.canonical_action
        if not action:
            return ConflictReport(
                node_id=node.node_id,
                status="NEW_INTENT",
                details=[{"note": "ABSTAIN/UNMAPPED 节点，无意图冲突对象，但存在本体覆盖缺口"}],
                recommendation="人工评估是否扩展本体；不自动晋级",
            )
        existing = self._intent_nodes.get(action, [])
        if not existing:
            return ConflictReport(
                node_id=node.node_id,
                status="NEW_INTENT",
                details=[{"note": f"意图 {action} 在 Trusted 无对应节点（知识盲区）"}],
                recommendation="晋级需人工确认该意图的裁决语义",
            )
        # 约束冲突：候选证据 vs 已有节点证据
        cand_ev = set(node.required_evidence)
        conflicts = []
        overlaps = []
        for n in existing:
            kb_ev = set(n.get("required_evidence", []))
            conflict_ev = kb_ev - cand_ev          # 已有但候选缺失
            new_ev = cand_ev - kb_ev               # 候选新增
            if conflict_ev:
                conflicts.append({
                    "node_id": n["node_id"],
                    "missing_in_candidate": sorted(conflict_ev),
                    "source": n.get("source"),
                })
            if new_ev:
                overlaps.append({
                    "node_id": n["node_id"],
                    "new_evidence_proposed": sorted(new_ev),
                })
        if conflicts:
            return ConflictReport(
                node_id=node.node_id,
                status="CONFLICT",
                details=conflicts,
                recommendation="候选证据集不完整或与现有知识冲突，需人工裁定",
            )
        if overlaps:
            return ConflictReport(
                node_id=node.node_id,
                status="OVERLAP",
                details=overlaps,
                recommendation="候选提出新证据，可晋级为补充知识（人工审核）",
            )
        return ConflictReport(
            node_id=node.node_id,
            status="CLEAR",
            details=[],
            recommendation="无冲突，可晋级",
        )

    # ---------- 晋级：生成 Trusted 节点 ----------

    def promote(self, node: CandidateRiskNode, trust_level: str = "L2", version: str = "1.0") -> dict:
        """候选 → Trusted 节点（保持 Schema 对齐）。"""
        trusted_node = {
            "node_id": node.node_id.replace("候选风险", "安全知识"),
            "node_type": "安全知识",
            "title": node.title.replace("候选: ", "安全: "),
            "semantic_description": node.semantic_description,
            "canonical_action": node.canonical_action,
            "conditions": node.conditions,
            "required_evidence": node.required_evidence,
            "optional_evidence": node.optional_evidence,
            "source": node.source,
            "chapter": "",
            "clause": "",
            "trust_level": trust_level,
            "vector": node.vector,
            "metadata": {
                **node.metadata,
                "promoted_from": node.node_id,
                "promoted_at": now_iso(),
                "version": version,
                "review_status": "TRUSTED",
            },
        }
        return trusted_node


if __name__ == "__main__":
    print("ReviewBoard + TrustedIntegrator 加载成功（Leakage=0 边界）")
