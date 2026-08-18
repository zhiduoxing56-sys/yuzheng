from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeNode(BaseModel):
    """主系统侧的知识节点模型，对齐 intelligence-agent 的 KnowledgeNode v2 JSONL。

    - `canonical_action` 存的是主系统 intent_id（如 HEADLIGHT_SET_MODE）。
    - `required_evidence` / `optional_evidence` 取值空间是 Evidence Space v1 的 canonical evidence type。
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
    command: dict[str, Any] = Field(default_factory=dict)
    evidence: dict[str, dict[str, Any]] = Field(default_factory=dict)
    when: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)
    effect: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_trusted(self) -> bool:
        """识别经审核的在线安全知识发布格式。"""
        if self.node_type == "安全知识" and self.metadata.get("review_status") == "TRUSTED":
            return True
        if self.node_type == "Trusted" and self.metadata.get("status") == "ACTIVE":
            return True
        # knowledge_nodes_v4.jsonl 是当前正式发布集。它由离线审核链产出，
        # 以 knowledge_id、约束策略和 L1/L2 可信等级表达已审核状态，而不是
        # 再重复写入 review_status。三个标记必须同时存在，避免把候选节点放行。
        if (
            self.node_type in {"安全知识", "rule"}
            and isinstance(self.metadata.get("knowledge_id"), str)
            and bool(self.metadata["knowledge_id"].strip())
            and self.metadata.get("constraint")
            in {"ALLOW_WITH_CONDITION", "REQUIRE_EXTRA_EVIDENCE"}
            and self.trust_level in {"L1", "L2"}
        ):
            return True
        return False


def load_trusted_nodes(
    path: Path,
    canonical_types: frozenset[str],
    *,
    allowed_node_ids: frozenset[str] | None = None,
) -> list[KnowledgeNode]:
    """逐行解析知识节点 JSONL，仅保留 Trusted 节点并严格校验证据类型。

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
            if allowed_node_ids is not None and node.node_id not in allowed_node_ids:
                continue
            node.required_evidence = _canonical_unique(
                node.required_evidence,
                canonical_types,
                node_id=node.node_id,
                field_name="required_evidence",
            )
            node.optional_evidence = _canonical_unique(
                node.optional_evidence,
                canonical_types,
                node_id=node.node_id,
                field_name="optional_evidence",
            )
            nodes[node.node_id] = node
    return list(nodes.values())


def _canonical_unique(
    values: list[str],
    canonical_types: frozenset[str],
    *,
    node_id: str,
    field_name: str,
) -> list[str]:
    """严格要求 canonical 证据类型，并在验证后保持顺序去重。"""
    invalid = list(dict.fromkeys(value for value in values if value not in canonical_types))
    if invalid:
        raise ValueError(
            f"trusted knowledge node {node_id!r} has non-canonical "
            f"{field_name}: {invalid}"
        )
    seen: dict[str, None] = {}
    for value in values:
        seen.setdefault(value, None)
    return list(seen)
