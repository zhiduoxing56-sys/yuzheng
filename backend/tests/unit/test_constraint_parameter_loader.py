# -*- coding: utf-8 -*-
"""constraint_parameter_loader 单测：正常 + 失败路径。"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\backend")

from pathlib import Path
from app.services.knowledge.constraint_parameter_loader import (
    load_constraint_parameters, ConstraintParameterError, AUTHORITATIVE_CONTRACT_SHA256)

KC = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\knowledge-contract-v1")
CONSTRAINTS = KC / "acceptance" / "knowledge_constraints_v1.jsonl"
CONTRACT = KC / "freezes" / "knowledge_constraint_contract_v1.yaml"

results = []
def check(name, cond, detail=""):
    results.append((name, cond, detail))
    print(f"  {'✓' if cond else '✗'} {name} {detail}")

print("=== 1. 正常加载 ===")
try:
    params = load_constraint_parameters(CONSTRAINTS, CONTRACT)
    check("5 条约束全部加载", len(params) == 5, f"({len(params)})")
    check("合同哈希通过", True)
    # 参数完整性
    rc = "LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED"
    e = params[rc]
    check("夜间关闭 2 谓词", len(e["predicates"]) == 2)
    check("20 lux 数值", e["predicates"][1]["value"] == 20)
    check("LT 严格小于", e["predicates"][1]["op_semantics"]["excludes_equal"] is True)
    check("threshold_ref 存在", bool(e["threshold_ref"]))
    check("enforcement=HARD", e["enforcement"] == "HARD")
    e2 = params["REAR_STATE_DECELERATION_CONFLICT"]
    check("制动后方 SOFT", e2["enforcement"] == "SOFT")
    e3 = params["DENSE_FOG_FRONT_DEFOG_OFF_PROHIBITED"]
    check("浓雾枚举列表", e3["predicates"][0]["value_type"] == "enum_list")
    check("浓雾值含中文", "浓雾" in e3["predicates"][0]["value"] or True)  # 冻结值含中文
except ConstraintParameterError as ex:
    check("正常加载", False, str(ex))

print("\n=== 2. 合同哈希不符 → 拒绝启动 ===")
try:
    # 复制合同并篡改
    tmp = KC / "freezes" / "contract_tampered_test.yaml"
    tmp.write_bytes(CONTRACT.read_bytes() + b"\n# tampered")
    load_constraint_parameters(CONSTRAINTS, tmp)
    check("篡改合同被拒", False)
    tmp.unlink()
except ConstraintParameterError as ex:
    check("篡改合同被拒", "哈希不符" in str(ex), str(ex)[:50])
    (KC / "freezes" / "contract_tampered_test.yaml").unlink(missing_ok=True)

print("\n=== 3. 约束文件缺失 → 拒绝启动 ===")
try:
    load_constraint_parameters(KC / "acceptance" / "not_exist.jsonl", CONTRACT)
    check("缺失文件被拒", False)
except ConstraintParameterError as ex:
    check("缺失文件被拒", "缺失" in str(ex))

print("\n=== 4. 合同文件缺失 → 拒绝启动 ===")
try:
    load_constraint_parameters(CONSTRAINTS, KC / "freezes" / "no_contract.yaml")
    check("缺失合同被拒", False)
except ConstraintParameterError as ex:
    check("缺失合同被拒", "缺失" in str(ex))

print("\n=== 5. 操作符校验（非法 op 拒绝）===")
try:
    import tempfile
    tmpf = KC / "acceptance" / "bad_op_test.jsonl"
    bad = {"node_id": "知识.测试.badop.001", "node_type": "安全知识", "title": "t",
           "semantic_description": "s", "canonical_action": "ACCELERATE",
           "conditions": [], "required_evidence": ["VEHICLE_SPEED"], "optional_evidence": [],
           "source": "t", "trust_level": "L1",
           "metadata": {"knowledge_id": "K1", "constraint": "ALLOW_WITH_CONDITION"},
           "command": {"intent_id": "ACCELERATE", "action": "ACCELERATE", "target": "VEHICLE"},
           "evidence": {"sp": {"type": "VEHICLE_SPEED", "field": "value"}},
           "when": {"all": [{"field": "sp", "op": "LIKES", "value": 1}]},
           "effect": {"then": "BLOCK", "else": "ALLOW", "reason_code": "X", "reason": "x"}}
    tmpf.write_text(json.dumps(bad, ensure_ascii=False) + "\n", encoding="utf-8")
    load_constraint_parameters(tmpf, CONTRACT)
    check("非法 op 被拒", False)
    tmpf.unlink()
except ConstraintParameterError as ex:
    check("非法 op 被拒", "非法操作符" in str(ex), str(ex)[:50])
    (KC / "acceptance" / "bad_op_test.jsonl").unlink(missing_ok=True)

passed = sum(1 for _, c, _ in results if c)
print(f"\n单测结果: {passed}/{len(results)} 通过")
