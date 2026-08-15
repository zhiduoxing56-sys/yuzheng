from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeNode(BaseModel):
    """主系统侧的知识节点模型，对齐 intelligence-agent 的 KnowledgeNode v2 JSONL。

    - `canonical_action` 存的是主系统 intent_id（如 HEADLIGHT_SET_MODE）。
    - `required_evidence` / `optional_evidence` 取值空间是主系统 32 类 canonical evidence type。
    """

    model_config = ConfigDict(extra="ignore")

    node_id: str
    node_type: str
    title: str = ""
    semantic_description: str = ""
    canonical_action: str = ""
    conditions: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    optional_evidence: list[str] = Field(default_factory=list)
    source: str = ""
    chapter: str = ""
    clause: str = ""
    trust_level: str = ""
    vector: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_trusted(self) -> bool:
        """兼容两种 Trusted 表示：代码现状(安全知识+TRUSTED) 与设计文档(Trusted+ACTIVE)。"""
        if self.node_type == "安全知识" and self.metadata.get("review_status") == "TRUSTED":
            return True
        if self.node_type == "Trusted" and self.metadata.get("status") == "ACTIVE":
            return True
        return False


def load_trusted_nodes(
    path: Path, canonical_types: frozenset[str]
) -> list[KnowledgeNode]:
    """逐行解析知识节点 JSONL，仅保留 Trusted 节点并净化证据类型。

    单行 JSON 损坏跳过不抛；按 node_id 去重；非 Trusted(候选/PENDING) 直接排除，保证 Leakage=0。
    """
    if not path.exists():
        return []
    nodes: dict[str, KnowledgeNode] = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            node = KnowledgeNode.model_validate(raw)
            if not node.is_trusted:
                continue
            node.required_evidence = _canonical_unique(
                node.required_evidence, canonical_types
            )
            node.optional_evidence = _canonical_unique(
                node.optional_evidence, canonical_types
            )
            nodes[node.node_id] = node
    return list(nodes.values())


def _canonical_unique(
    values: list[str], canonical_types: frozenset[str]
) -> list[str]:
    """过滤到 canonical 证据类型并保持顺序去重。"""
    seen: dict[str, None] = {}
    for value in values:
        if value in canonical_types:
            seen.setdefault(value, None)
    return list(seen)
