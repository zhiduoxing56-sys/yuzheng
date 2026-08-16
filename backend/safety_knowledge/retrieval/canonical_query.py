"""Canonical Safety Query Builder v2

目标：把口语化 raw query 改写为结构化规范检索文本，
     提升 BGE 检索对法规语义节点的命中率（重点修复"把灯灭掉/拉手刹"类失败）。

设计：canonical = intent 中文语义短语 + canonical_action + canonical_target
                + 适用条件 + 证据枚举名（与节点 embedding_text 同空间锚点）

组件：
  1. CanonicalQueryBuilder.build(raw_query, intent_id) -> canonical_text
  2. KnowledgeNode.retrieval_text 扩展（仅由 Schema 字段生成，禁止自由知识）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from safety_knowledge.ontology.intent_alias_map import INTENT_KEYWORDS  # noqa: E402


class CanonicalQueryBuilder:
    """基于 intent_id 的规范检索文本生成器。"""

    def __init__(self) -> None:
        snapshot = json.loads((ROOT / "data" / "ontology_snapshot.json").read_text(encoding="utf-8"))
        self._intent_meta = snapshot.get("intent_details", {})

    def build(self, raw_query: str, intent_id: str, required_evidence: list[str] | None = None) -> str:
        meta = self._intent_meta.get(intent_id, {})
        action = meta.get("canonical_action", "")
        target = meta.get("canonical_target", "")
        family = meta.get("family", "")
        keywords = INTENT_KEYWORDS.get(intent_id, ())

        # 中文语义核心词（取前 3 个关键词）
        core = " ".join(keywords[:3]) if keywords else raw_query
        # 意图家族语义
        family_cn = family.replace("_", " ").lower()
        # 证据锚点（与节点 embedding_text 的 证据: 前缀对齐）
        ev = " ".join(required_evidence) if required_evidence else ""

        parts = [core]
        if action:
            parts.append(f"动作:{action}")
        if target:
            parts.append(f"对象:{target}")
        parts.append(f"领域:{family_cn}")
        if ev:
            parts.append(f"证据:{ev}")
        return " ".join(parts)

    def build_bare(self, raw_query: str) -> str:
        """无 intent 信息时仅返回 raw（对照基线）。"""
        return raw_query


def build_retrieval_text(node: dict) -> str:
    """KnowledgeNode 独立检索文本（仅由审核后 Schema 字段拼接）。"""
    parts = [
        node.get("title", ""),
        node.get("semantic_description", ""),
        f"动作:{node.get('canonical_action', '')}",
    ]
    conds = node.get("conditions", [])
    if conds:
        parts.append(f"条件:{' '.join(conds)}")
    req = node.get("required_evidence", [])
    if req:
        parts.append(f"证据:{' '.join(req)}")
    opt = node.get("optional_evidence", [])
    if opt:
        parts.append(f"辅助证据:{' '.join(opt)}")
    src = node.get("source", "")
    if src:
        parts.append(f"来源:{src} {node.get('clause', '')}")
    return " ".join(parts)


def main() -> int:
    builder = CanonicalQueryBuilder()
    test = [
        ("现在把灯灭掉", "HEADLIGHT_SET_MODE"),
        ("拉手刹", "PARKING_BRAKE_APPLY"),
        ("松开手刹准备起步", "PARKING_BRAKE_RELEASE"),
        ("踩刹车减速", "BRAKE"),
        ("远光灯调亮一点", "HIGH_BEAM_ON"),
        ("帮我把车门打开", "DOOR_OPEN"),
    ]
    print("Canonical Query Builder v2 示例:")
    for q, iid in test:
        print(f"\n  raw      : {q}")
        print(f"  canonical: {builder.build(q, iid)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
