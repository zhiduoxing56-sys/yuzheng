"""知识节点 Schema v2（对齐用户给定结构）

节点结构（用户给定）：
  节点ID / 节点类型 / 标题 / 语义描述 / 规范动作 / 适用条件
  必要证据 / 辅助证据 / 来源 / 章节 / 条款 / 可信级别 / 向量

节点ID 格式：知识.<能力域>.<语义标识>.<序号>
  例：知识.灯光.低照度关闭约束.001

向量：BGE 768维（由 embedding 文本生成，运行时计算或持久化）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# ---------- 枚举（与 safety_knowledge/ontology/schema.py 对齐） ----------

CAPABILITY_DOMAIN = [
    "灯光", "行驶控制", "泊车驻车", "车身", "信息与安全",
    "舒适", "动力传动", "视野", "其他",
    "网络安全", "数据安全", "OTA升级", "事故记录", "法规合规",
]

TRUST_LEVEL = ["L1", "L2", "L3", "L4", "L5"]  # 与 source_level 一致

NODE_TYPE = ["安全知识", "事故情报", "候选风险"]


@dataclass(frozen=True, slots=True)
class KnowledgeNode:
    """标准知识节点（v2 Schema）。"""

    node_id: str                # 知识.灯光.低照度关闭约束.001
    node_type: str              # 安全知识 / 事故情报 / 候选风险
    title: str                  # 低照度行驶关闭前照灯安全约束
    semantic_description: str   # 语义描述
    canonical_action: str       # 规范动作（intent_id）
    conditions: list[str]       # 适用条件（枚举）
    required_evidence: list[str]  # 必要证据（枚举）
    optional_evidence: list[str]  # 辅助证据（枚举）
    source: str                 # 来源（标准号/文档）
    chapter: str                # 章节
    clause: str                 # 条款
    trust_level: str            # 可信级别（L1-L5）
    vector: list[float] | None = None   # BGE 768 维
    metadata: dict[str, Any] = field(default_factory=dict)  # 扩展字段

    @property
    def embedding_text(self) -> str:
        """向量嵌入文本：标题 + 语义 + 动作 + 条件 + 证据。"""
        return (
            f"{self.title} {self.semantic_description} "
            f"动作:{self.canonical_action} "
            f"条件:{' '.join(self.conditions)} "
            f"证据:{' '.join(self.required_evidence)}"
        )


def build_node_id(domain: str, semantic_key: str, seq: int) -> str:
    """生成节点 ID：知识.灯光.低照度关闭约束.001"""
    return f"知识.{domain}.{semantic_key}.{seq:03d}"


def validate_node(node: KnowledgeNode) -> list[str]:
    """节点校验（结构 + 枚举）。"""
    errors: list[str] = []
    if not node.node_id.startswith("知识."):
        errors.append(f"node_id 格式非法: {node.node_id}")
    if node.node_type not in NODE_TYPE:
        errors.append(f"node_type 非法: {node.node_type}")
    if node.trust_level not in TRUST_LEVEL:
        errors.append(f"trust_level 非法: {node.trust_level}")
    if not node.canonical_action:
        errors.append("缺少规范动作")
    if not node.required_evidence:
        errors.append("缺少必要证据")
    return errors


if __name__ == "__main__":
    # 示例：用户给定结构 → KnowledgeNode
    node = KnowledgeNode(
        node_id="知识.灯光.低照度关闭约束.001",
        node_type="安全知识",
        title="低照度行驶关闭前照灯安全约束",
        semantic_description="车辆处于行驶状态且外部照度不足时，关闭前照灯会降低主动照明能力，执行前需要检查环境光、车辆速度、道路可见度以及当前灯光状态。",
        canonical_action="HEADLIGHT_SET_MODE",
        conditions=["VEHICLE_MOVING", "LOW_LIGHT", "NIGHT"],
        required_evidence=["ENVIRONMENT_CONDITIONS", "VEHICLE_SPEED", "LIGHTING_STATE"],
        optional_evidence=["ROAD_FRICTION_STATE"],
        source="GB 7258-2017",
        chapter="第8章",
        clause="8.2",
        trust_level="L1",
    )
    errors = validate_node(node)
    print("节点示例:")
    print(f"  node_id: {node.node_id}")
    print(f"  标题: {node.title}")
    print(f"  语义: {node.semantic_description[:40]}...")
    print(f"  动作: {node.canonical_action}")
    print(f"  条件: {node.conditions}")
    print(f"  必要证据: {node.required_evidence}")
    print(f"  辅助证据: {node.optional_evidence}")
    print(f"  来源: {node.source} {node.chapter} {node.clause}")
    print(f"  可信级别: {node.trust_level}")
    print(f"  嵌入文本: {node.embedding_text[:80]}...")
    print(f"  校验: {'✅ 通过' if not errors else errors}")
