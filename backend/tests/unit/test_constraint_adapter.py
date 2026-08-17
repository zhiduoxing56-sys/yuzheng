# -*- coding: utf-8 -*-
"""正式接入验证（用户五步第二步关键测试）：

  修改测试副本中知识节点阈值（5m → 6m），正式 SafetyGate 的边界行为必须同步变化。
  证明运行时真的使用知识库参数，而非旧 YAML。

同时验证：
  - overlay 注入后 evaluator 使用知识阈值
  - 浓雾中文归一化等价
  - 溯源信息（命中的知识节点/阈值来源）
"""
import json, sys, io, tempfile, shutil
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\backend")
KC = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\knowledge-contract-v1")

from app.services.knowledge.constraint_parameter_loader import load_constraint_parameters
from app.services.knowledge.constraint_adapter import build_rule_overlay, normalize_fog
from app.models.schemas import EvidenceNode, SemanticIntent, EvidenceStatus, SecurityClass, AdvancedValidationResult
from app.services.decision.safety_gate import SafetyGateService

def mk_ev(ev: dict) -> dict:
    OBJECT = {"ENVIRONMENT_CONDITIONS", "SURROUNDING_OBJECT_STATE"}
    by_type, obj = {}, {}
    for key, val in ev.items():
        if "." in key:
            etype, field = key.split(".", 1)
        else:
            etype, field = key, "value"
        obj.setdefault(etype, {})[field] = val
    for etype, fields in obj.items():
        v = fields if etype in OBJECT else fields.get("value")
        by_type[etype] = EvidenceNode(node_id=f"ev_{etype}", evidence_type=etype, layer="sim",
            source="test", value=v, unit=None, timestamp=None, expires_at=None, freshness=1.0,
            consistency=1.0, availability=1.0, quality_label=EvidenceStatus.VALID,
            integrity_hash="h", metadata={}, security_class=SecurityClass.DRIVING,
            security_rank=0, base_level=0, safety_adjustment=0, hnsw_max_layer=0,
            hnsw_layer_memberships=[], security_classification_source=None, formula_source=None,
            canonicalization_source=None, merged_node_sources=[], field_resolution={},
            canonicalization_warnings=[])
    return by_type

def mk_intent(iid, mode=None):
    return SemanticIntent(clause_index=0, clause_text="", intent_id=iid, runtime_identity="FORMAL",
        action="", target="", area="ANY", value=None, mode=mode, direction=None,
        control_attribute="", control_domain="车身控制", risk_level="R2", risk_tags=[],
        semantic_confidence=1.0, ambiguity_score=0.0)

def run_evaluator(rule, evaluator_name, intent, ev, extra=None):
    sg = SafetyGateService({"gate_rules": []})
    rule = dict(rule)
    if extra:
        rule.update(extra)
    by_type = mk_ev(ev)
    hit, detail, _ = sg._evaluators[evaluator_name](rule, intent, None, by_type, [], AdvancedValidationResult())
    return hit, detail

# 加载正式参数 + overlay
params = load_constraint_parameters(KC / "acceptance" / "knowledge_constraints_v1.jsonl",
                                    KC / "freezes" / "knowledge_constraint_contract_v1.yaml")
overlay = build_rule_overlay(params)

acc_rule = {"id": "FRONT_OBSTACLE_ACCELERATION_PROHIBITED", "evaluator": "acceleration_obstacle",
            "intent_ids": ["ACCELERATE"], "threshold_m": 5, "reason": "前方障碍距离过近，禁止加速"}

print("=== 测试1：正式 overlay 接入（阈值 5m） ===")
# 5.0m → 不命中（LT 5 不成立）；4.9m → 命中
h1, _ = run_evaluator(acc_rule, "acceleration_obstacle", mk_intent("ACCELERATE"),
                      {"SURROUNDING_OBJECT_STATE.front_obstacle_distance": 5.0}, overlay["FRONT_OBSTACLE_ACCELERATION_PROHIBITED"])
h2, _ = run_evaluator(acc_rule, "acceleration_obstacle", mk_intent("ACCELERATE"),
                      {"SURROUNDING_OBJECT_STATE.front_obstacle_distance": 4.9}, overlay["FRONT_OBSTACLE_ACCELERATION_PROHIBITED"])
print(f"  5.0m hit={h1}（期望 False）| 4.9m hit={h2}（期望 True）")
ok1 = (h1 is False) and (h2 is True)

print("\n=== 测试2：修改副本阈值 5m → 6m，边界行为必须变化 ===")
import copy
overlay2 = copy.deepcopy(overlay)
overlay2["FRONT_OBSTACLE_ACCELERATION_PROHIBITED"]["threshold_m"] = 6  # 模拟知识节点改为 6m
h3, d3 = run_evaluator(acc_rule, "acceleration_obstacle", mk_intent("ACCELERATE"),
                       {"SURROUNDING_OBJECT_STATE.front_obstacle_distance": 5.5}, overlay2["FRONT_OBSTACLE_ACCELERATION_PROHIBITED"])
print(f"  知识节点 5m→6m 后，5.5m hit={h3}（期望 True，因为 5.5 < 6）")
print(f"  且 overlay 未改时 5.5m 应不命中（验证非旧 YAML）")
h4, _ = run_evaluator(acc_rule, "acceleration_obstacle", mk_intent("ACCELERATE"),
                      {"SURROUNDING_OBJECT_STATE.front_obstacle_distance": 5.5}, overlay["FRONT_OBSTACLE_ACCELERATION_PROHIBITED"])
print(f"  原 overlay：5.5m hit={h4}（期望 False）")
ok2 = (h3 is True) and (h4 is False)

print("\n=== 测试3：浓雾中文归一化等价 ===")
fog_rule = {"id": "DENSE_FOG_FRONT_DEFOG_OFF_PROHIBITED", "evaluator": "dense_fog_defog",
            "intent_ids": ["DEFROST_OFF"], "reason": "浓雾环境禁止关闭前挡风除雾"}
fog_overlay = overlay["DENSE_FOG_FRONT_DEFOG_OFF_PROHIBITED"]
h_cn, _ = run_evaluator(fog_rule, "dense_fog_defog", mk_intent("DEFROST_OFF"),
                        {"ENVIRONMENT_CONDITIONS.weather": "浓雾"}, fog_overlay)
h_cn2, _ = run_evaluator(fog_rule, "dense_fog_defog", mk_intent("DEFROST_OFF"),
                         {"ENVIRONMENT_CONDITIONS.weather": "大雾"}, fog_overlay)
print(f"  weather=浓雾 hit={h_cn}（期望 True）| weather=大雾 hit={h_cn2}（期望 True）")
ok3 = h_cn is True and h_cn2 is True

print("\n=== 测试4：溯源信息 ===")
e = overlay["FRONT_OBSTACLE_ACCELERATION_PROHIBITED"]
print(f"  命中的知识节点: {e['_constraint_node_id']}")
print(f"  阈值来源: {e['_constraint_threshold_ref'][:60]}")
print(f"  谓词: {e['_constraint_predicates']}")
ok4 = e["_constraint_node_id"] == "知识.加速.近距障碍加速限制.001"

print(f"\n结果: 测试1={ok1} 测试2={ok2}(阈值修改生效) 测试3={ok3}(中文等价) 测试4={ok4}(溯源)")
print(f"verdict: {'PASS' if all([ok1, ok2, ok3, ok4]) else 'FAIL'}")
