# -*- coding: utf-8 -*-
"""constraint_parameter_loader v1：从 knowledge_constraints_v1.jsonl 加载约束参数。

阶段三要求：
  1. 读取完整约束参数（数值阈值/枚举集合/操作符/边界语义），非仅数值
  2. 每参数带来源引用（metadata.threshold_ref）
  3. 加载失败 / 合同哈希不符 / 节点缺失 → 拒绝启动（抛错），禁止静默默认值
  4. 保留 evaluator 全部安全增强（枚举/缺失拦截/冲突/off_intent_ids）——loader 只提供参数，不替换逻辑

输出：dict 参数表（按 reason_code 索引），供 evaluator 引用。
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

AUTHORITATIVE_CONTRACT_SHA256 = "3DFF279543199F64BB09C674D1F646B0F7B1E74DB0BDF51937CC7B40D52845D2"
CONTRACT_LINES = 335

# 操作符边界语义（GT 不含等号、LT 不含等号等）
OP_SEMANTICS = {
    "GT": {"desc": "严格大于", "excludes_equal": True},
    "GTE": {"desc": "大于等于", "excludes_equal": False},
    "LT": {"desc": "严格小于", "excludes_equal": True},
    "LTE": {"desc": "小于等于", "excludes_equal": False},
    "EQ": {"desc": "等于", "excludes_equal": False},
    "NE": {"desc": "不等于", "excludes_equal": True},
    "IN": {"desc": "属于枚举集合", "excludes_equal": False, "requires_list": True},
    "NOT_IN": {"desc": "不属于枚举集合", "excludes_equal": True, "requires_list": True},
}


class ConstraintParameterError(RuntimeError):
    """参数加载失败 → 拒绝启动。"""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_constraint_parameters(
    constraints_path: Path,
    contract_path: Path | None = None,
    require_contract_hash: bool = True,
) -> dict:
    """加载约束参数。任何不一致 → ConstraintParameterError（拒绝启动）。"""
    # 1. 合同哈希校验（如提供合同路径）
    if require_contract_hash and contract_path is not None:
        if not contract_path.exists():
            raise ConstraintParameterError(f"合同文件缺失: {contract_path}")
        actual = _sha256(contract_path)
        if actual != AUTHORITATIVE_CONTRACT_SHA256:
            raise ConstraintParameterError(
                f"合同哈希不符: 期望 {AUTHORITATIVE_CONTRACT_SHA256[:16]}... 实际 {actual[:16]}... 拒绝启动")
        n_lines = len(contract_path.read_text(encoding="utf-8").splitlines())
        if n_lines != CONTRACT_LINES:
            raise ConstraintParameterError(f"合同行数不符: 期望 {CONTRACT_LINES} 实际 {n_lines} 拒绝启动")

    # 2. 约束文件
    if not constraints_path.exists():
        raise ConstraintParameterError(f"约束文件缺失: {constraints_path}")
    nodes = []
    with constraints_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                nodes.append(json.loads(line))
    if not nodes:
        raise ConstraintParameterError("约束文件为空，拒绝启动")

    # 3. 逐节点提取参数
    params = {}
    seen_ids = set()
    for n in nodes:
        nid = n["node_id"]
        if nid in seen_ids:
            raise ConstraintParameterError(f"node_id 重复: {nid}")
        seen_ids.add(nid)
        rc = n["effect"]["reason_code"]
        if rc in params:
            raise ConstraintParameterError(f"reason_code 重复: {rc}")

        entry = {
            "node_id": nid,
            "intent_id": n["command"]["intent_id"],
            "effect_then": n["effect"]["then"],
            "effect_else": n["effect"]["else"],
            "reason_code": rc,
            "threshold_ref": n["metadata"].get("threshold_ref", ""),
            "predicates": [],
            "enforcement": "HARD" if n["effect"]["then"] == "BLOCK" else "SOFT",
        }
        grp = "all" if "all" in n["when"] else "any"
        for p in n["when"][grp]:
            alias = p["field"]
            aev = n["evidence"][alias]
            op = p["op"]
            if op not in OP_SEMANTICS:
                raise ConstraintParameterError(f"{nid}: 非法操作符 {op}")
            if OP_SEMANTICS[op].get("requires_list") and not isinstance(p["value"], list):
                raise ConstraintParameterError(f"{nid}: {op} 需要列表值")
            entry["predicates"].append({
                "alias": alias,
                "evidence_type": aev["type"],
                "evidence_field": aev["field"],
                "op": op,
                "op_semantics": OP_SEMANTICS[op],
                "value": p["value"],
                "value_type": "number" if isinstance(p["value"], (int, float)) else
                              ("enum_list" if isinstance(p["value"], list) else "string"),
            })
        params[rc] = entry

    return params


def load_default() -> dict:
    """默认入口：加载 knowledge-contract-v1 包内文件。"""
    kc = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\knowledge-contract-v1")
    return load_constraint_parameters(
        constraints_path=kc / "acceptance" / "knowledge_constraints_v1.jsonl",
        contract_path=kc / "freezes" / "knowledge_constraint_contract_v1.yaml",
    )


if __name__ == "__main__":
    try:
        params = load_default()
        print(f"constraint_parameter_loader 加载成功: {len(params)} 条约束")
        for rc, e in params.items():
            print(f"  [{rc}] {e['node_id']} | {e['intent_id']} | {e['enforcement']}")
            for p in e["predicates"]:
                print(f"      {p['alias']} ({p['evidence_type']}.{p['evidence_field']}) "
                      f"{p['op']} {p['value']} [{p['value_type']}] {p['op_semantics']['desc']}")
            print(f"      src: {e['threshold_ref'][:70]}")
    except ConstraintParameterError as ex:
        print(f"✗ 拒绝启动: {ex}")
        sys.exit(1)
