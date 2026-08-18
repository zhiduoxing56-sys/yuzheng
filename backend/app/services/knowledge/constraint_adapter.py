# -*- coding: utf-8 -*-
"""SafetyGate 知识参数接入层（knowledge_constraint_adapter）

目标（用户五步第一步）：
  SafetyGate 实际通过 constraint_parameter_loader 取得：
    speed GT 0 / light LT 20 / front_dist LT 5 / rear_dist LT 1.5 / weather IN [...]
    then/else / BLOCK-REVIEW 等级 / 节点ID / reason_code / 来源引用

设计原则：
  1. evaluator 阈值从知识参数读取（替换 rule.get 默认值），缺失 → 抛错拒绝启动
  2. 保留全部安全增强：枚举(LOW/DARK/NIGHT)、fail-closed、冲突、off_intent_ids、DOOR_SET_POSITION、DECELERATE
  3. 浓雾中文归一化（证据标准化）：浓雾→DENSE_FOG、大雾→HEAVY_FOG
  4. 裁决溯源：记录命中的知识节点/证据值/操作符/阈值/是否增强

接入方式：
  - adapter.build_rule_overlay(constraint_params) → {reason_code: {extra_params}}
  - SafetyGate.evaluate 中 rule.update(overlay) 注入知识参数
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.config import PROJECT_ROOT
from app.services.knowledge.constraint_parameter_loader import (
    ConstraintParameterError, load_constraint_parameters,
)

# 浓雾中文 → 英文 归一化（证据标准化，非节点参数扩展）
FOG_NORMALIZATION = {
    "浓雾": "DENSE_FOG",
    "大雾": "HEAVY_FOG",
    "雾": "FOG",
}

def normalize_fog(value: Any) -> Any:
    """证据标准化：中文浓雾枚举 → 英文。输入可以是 str 或 列表。"""
    if isinstance(value, str):
        return FOG_NORMALIZATION.get(value.strip(), value)
    if isinstance(value, list):
        return [normalize_fog(v) for v in value]
    return value


def build_rule_overlay(constraint_params: dict) -> dict:
    """把知识约束参数 → safety_rules overlay。

    overlay: {reason_code: {参数键: 值}}，供 evaluate 中 rule.update(overlay[reason_code]) 使用。
    只注入"基础条件参数"，安全增强逻辑仍在 evaluator。
    """
    overlay = {}
    for rc, e in constraint_params.items():
        entry: dict[str, Any] = {
            "_constraint_node_id": e["node_id"],
            "_constraint_intent_id": e["intent_id"],
            "_constraint_threshold_ref": e["threshold_ref"],
            "_constraint_predicates": [],
        }
        for p in e["predicates"]:
            entry["_constraint_predicates"].append({
                "evidence_type": p["evidence_type"],
                "evidence_field": p["evidence_field"],
                "op": p["op"],
                "value": p["value"],
            })
            # 兼容现有 evaluator 读取方式（低照度/障碍/后方）
            if p["evidence_field"] == "ambient_illumination" and p["op"] == "LT":
                entry["low_light_lux"] = p["value"]
            if p["evidence_field"] == "front_obstacle_distance" and p["op"] == "LT":
                entry["threshold_m"] = p["value"]
            if p["evidence_field"] == "rear_obstacle_distance" and p["op"] == "LT":
                entry["threshold_m"] = p["value"]
            if p["evidence_field"] == "weather" and p["op"] == "IN":
                # 知识枚举 + 中文归一化扩展（保证等价，证据标准化）
                entry["dense_fog_values"] = sorted(
                    {str(v) for v in p["value"]} | {"浓雾", "大雾"})
        overlay[rc] = entry
    return overlay


def load_knowledge_overlay() -> dict:
    """默认入口：加载 knowledge-contract-v1 包 → overlay。"""
    kc = PROJECT_ROOT / "data" / "knowledge_constraints" / "v1"
    params = load_constraint_parameters(
        constraints_path=kc / "acceptance" / "knowledge_constraints_v1.jsonl",
        contract_path=kc / "freezes" / "knowledge_constraint_contract_v1.yaml",
        manifest_path=kc / "MANIFEST.json",
    )
    return build_rule_overlay(params)


if __name__ == "__main__":
    overlay = load_knowledge_overlay()
    print(f"knowledge overlay 构建成功: {len(overlay)} 条")
    for rc, e in overlay.items():
        print(f"\n[{rc}] node={e['_constraint_node_id']}")
        for k, v in e.items():
            if k.startswith("_"):
                continue
            print(f"  {k}: {v}")
        print(f"  谓词: {e['_constraint_predicates']}")
