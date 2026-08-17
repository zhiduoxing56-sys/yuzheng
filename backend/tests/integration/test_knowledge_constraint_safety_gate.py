# -*- coding: utf-8 -*-
"""第三步验证：
  1. SafetyGate 可导入（语法正确）
  2. 无 overlay 时兼容（旧行为不变）
  3. 有 overlay 时用知识参数（5m 边界）
  4. overlay 缺参数 → 拒绝启动（ValueError）
  5. 增强用例回归（15 条）
"""
import sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
KC = PROJECT_ROOT / "data" / "knowledge_constraints" / "v1"

from app.services.decision.safety_gate import SafetyGateService, _knowledge_threshold
from app.services.knowledge.constraint_parameter_loader import load_constraint_parameters
from app.services.knowledge.constraint_adapter import build_rule_overlay
from app.models.schemas import EvidenceNode, SemanticIntent, EvidenceStatus, SecurityClass, AdvancedValidationResult
import json
import yaml

results = []
def check(n, c, d=""):
    results.append(c)
    print(f"  {'✓' if c else '✗'} {n} {d}")

# 1 导入成功
print("=== 1. 导入 ===")
check("SafetyGate 导入", callable(SafetyGateService) and callable(_knowledge_threshold))

# 2 无 overlay 兼容
print("\n=== 2. 无 overlay 兼容（旧行为） ===")
sg = SafetyGateService({"gate_rules": []})
rule = {"id": "FRONT_OBSTACLE_ACCELERATION_PROHIBITED", "evaluator": "acceleration_obstacle",
        "intent_ids": ["ACCELERATE"], "threshold_m": 5, "reason": "x"}
by_type = {}
node = EvidenceNode(node_id="e1", evidence_type="SURROUNDING_OBJECT_STATE", layer="sim", source="t",
    value={"front_obstacle_distance": 4.9}, unit=None, timestamp=None, expires_at=None, freshness=1.0,
    consistency=1.0, availability=1.0, quality_label=EvidenceStatus.VALID, integrity_hash="h",
    metadata={}, security_class=SecurityClass.DRIVING, security_rank=0, base_level=0, safety_adjustment=0,
    hnsw_max_layer=0, hnsw_layer_memberships=[], security_classification_source=None, formula_source=None,
    canonicalization_source=None, merged_node_sources=[], field_resolution={}, canonicalization_warnings=[])
by_type["SURROUNDING_OBJECT_STATE"] = node
intent = SemanticIntent(clause_index=0, clause_text="", intent_id="ACCELERATE", runtime_identity="FORMAL",
    action="", target="", area="ANY", value=None, mode=None, direction=None, control_attribute="",
    control_domain="车身控制", risk_level="R2", risk_tags=[], semantic_confidence=1.0, ambiguity_score=0.0)
hit, _, _ = sg._evaluators["acceleration_obstacle"](rule, intent, None, by_type, [], AdvancedValidationResult())
check("无 overlay: 4.9m 命中（旧规则 5m）", hit is True)

# 3 有 overlay 用知识参数（注入 _knowledge_params）
print("\n=== 3. 有 overlay 用知识参数 ===")
params = load_constraint_parameters(KC / "acceptance" / "knowledge_constraints_v1.jsonl",
                                    KC / "freezes" / "knowledge_constraint_contract_v1.yaml")
overlay = build_rule_overlay(params)
rule2 = dict(rule)
rule2["_knowledge_params"] = overlay["FRONT_OBSTACLE_ACCELERATION_PROHIBITED"]
by_type["SURROUNDING_OBJECT_STATE"].value = {"front_obstacle_distance": 4.9}
hit2, _, _ = sg._evaluators["acceleration_obstacle"](rule2, intent, None, by_type, [], AdvancedValidationResult())
by_type["SURROUNDING_OBJECT_STATE"].value = {"front_obstacle_distance": 5.0}
hit3, _, _ = sg._evaluators["acceleration_obstacle"](rule2, intent, None, by_type, [], AdvancedValidationResult())
check("overlay: 4.9m 命中（<5）", hit2 is True)
check("overlay: 5.0m 不命中（LT 不含等号）", hit3 is False)

# 4 overlay 缺参数 → 拒绝启动
print("\n=== 4. overlay 缺参数 → 拒绝启动 ===")
rule3 = dict(rule)
rule3["_knowledge_params"] = {"_constraint_node_id": "x"}  # 无 threshold_m
try:
    sg._evaluators["acceleration_obstacle"](rule3, intent, None, by_type, [], AdvancedValidationResult())
    check("缺参数拒绝启动", False)
except ValueError as ex:
    check("缺参数拒绝启动", "拒绝启动" in str(ex), str(ex)[:60])

# 5 增强用例回归
print("\n=== 5. 增强用例回归（15 条，注入 overlay） ===")
cases = []
with (KC / "acceptance" / "safety_gate_enhancement_cases_v1.jsonl").open(encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            cases.append(json.loads(line))
rules = yaml.safe_load((KC / "freezes" / "safety_rules.yaml").read_text(encoding="utf-8"))["gate_rules"]
rules = {r["evaluator"]: r for r in rules}

def mk_ev2(ev):
    OBJECT = {"ENVIRONMENT_CONDITIONS", "SURROUNDING_OBJECT_STATE"}
    by_type, obj = {}, {}
    for key, val in ev.items():
        if "validation_conflict" in key:
            continue
        if "." in key:
            etype, field = key.split(".", 1)
        else:
            etype, field = key, "value"
        obj.setdefault(etype, {})[field] = val
    for etype, fields in obj.items():
        v = fields if etype in OBJECT else fields.get("value")
        by_type[etype] = EvidenceNode(node_id=f"ev_{etype}", evidence_type=etype, layer="sim",
            source="test", value=v, unit=None, timestamp=None, expires_at=None, freshness=1.0,
            consistency=1.0, availability=1.0, quality_label=EvidenceStatus.VALID, integrity_hash="h",
            metadata={}, security_class=SecurityClass.DRIVING, security_rank=0, base_level=0,
            safety_adjustment=0, hnsw_max_layer=0, hnsw_layer_memberships=[], security_classification_source=None,
            formula_source=None, canonicalization_source=None, merged_node_sources=[], field_resolution={},
            canonicalization_warnings=[])
    return by_type

def mk_intent2(iid, mode=None, value=None):
    return SemanticIntent(clause_index=0, clause_text="", intent_id=iid, runtime_identity="FORMAL",
        action="", target="", area="ANY", value=value, mode=mode, direction=None, control_attribute="",
        control_domain="车身控制", risk_level="R2", risk_tags=[], semantic_confidence=1.0, ambiguity_score=0.0)

pass_n = 0
for c in cases:
    r = dict(rules[c["evaluator"]])
    # 注入 overlay（按规则 id 匹配）
    r["_knowledge_params"] = overlay.get(r["id"])
    by_type = mk_ev2(c["evidence"])
    intent = mk_intent2(c["intent_id"], c.get("mode"), c.get("intent_value"))
    try:
        hit, _, _ = sg._evaluators[c["evaluator"]](r, intent, None, by_type, [], AdvancedValidationResult())
        if hit == c["expected"]["hit"]:
            pass_n += 1
        else:
            print(f"  ✗ {c['case_id']} 预期 {c['expected']['hit']} 实际 {hit}")
    except ValueError as ex:
        print(f"  ✗ {c['case_id']} ValueError: {str(ex)[:60]}")
check(f"增强用例回归 {pass_n}/15", pass_n == 15)

print(f"\nverdict: {'PASS' if all(results) else 'FAIL'}")
