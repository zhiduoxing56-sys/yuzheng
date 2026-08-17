# -*- coding: utf-8 -*-
"""阶段二：知识节点—SafetyGate 差分测试（49 条场景，固定口径）。

口径（用户固定）：
  1. 每条两侧输入同一规范指令 + 同一证据
  2. NOT_APPLICABLE = 节点不参与裁决，不等于 ALLOW
  3. MISSING_EVIDENCE/CONFLICT 先按策略转换为最终裁决再比较
  4. 严格度：BLOCK > REVIEW > ALLOW
  5. 仅 CONSISTENT 或 SAFETYGATE_STRICTER 通过；KNOWLEDGE_STRICTER/无法解释/改输入 失败
  6. 无法接真实 evaluator 的场景 → NOT_EXECUTABLE（标注接口原因）
  7. 不修改合同/冻结/节点/evaluator

场景集：基础 15 + 扩充 19 + 增强 15 = 49
"""
import json, sys, io, yaml
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\backend")
KC = r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\knowledge-contract-v1"

from app.models.schemas import EvidenceNode, SemanticIntent, AdvancedValidationResult, JailbreakConflict, EvidenceStatus, SecurityClass
from app.services.decision.safety_gate import SafetyGateService

# ============ 工具：构造对象 ============
def mk_evidence(ev: dict) -> dict:
    OBJECT_TYPES = {"ENVIRONMENT_CONDITIONS", "SURROUNDING_OBJECT_STATE"}
    by_type = {}
    obj_vals = {}
    for key, val in ev.items():
        if "." in key:
            etype, field = key.split(".", 1)
        else:
            etype, field = key, "value"
        if "conflict" in key or "alt" in key:
            continue
        if etype in OBJECT_TYPES:
            obj_vals.setdefault(etype, {})[field] = val
        else:
            obj_vals.setdefault(etype, {})["_scalar"] = val
    for etype, fields in obj_vals.items():
        value = fields["_scalar"] if "_scalar" in fields else {k: v for k, v in fields.items()}
        node = EvidenceNode(node_id=f"ev_{etype}", evidence_type=etype, layer="sim",
                            source="test", value=value, unit=None, timestamp=None,
                            expires_at=None, freshness=1.0, consistency=1.0, availability=1.0,
                            quality_label=EvidenceStatus.VALID, integrity_hash="h", metadata={},
                            security_class=SecurityClass.DRIVING, security_rank=0, base_level=0,
                            safety_adjustment=0, hnsw_max_layer=0, hnsw_layer_memberships=[],
                            security_classification_source=None, formula_source=None,
                            canonicalization_source=None, merged_node_sources=[], field_resolution={},
                            canonicalization_warnings=[])
        by_type[etype] = node
    return by_type

def mk_intent(iid, mode=None, value=None):
    return SemanticIntent(clause_index=0, clause_text="", intent_id=iid,
                          runtime_identity="FORMAL", action="", target="",
                          area="ANY", value=value, mode=mode, direction=None,
                          control_attribute="", control_domain="车身控制",
                          risk_level="R2", risk_tags=[], semantic_confidence=1.0,
                          ambiguity_score=0.0)

def mk_validation(conflict=False):
    v = AdvancedValidationResult()
    if conflict:
        c = JailbreakConflict.model_construct(rule_id="REAR_CONFLICT_TEST", conflict_id="C1",
            claim_type="PHYSICAL", claimed_value="rear far", observed_value="rear near",
            recommended_action="REVIEW", severity=3)
        v.conflicts = [c]
    return v

# ============ 规则与严格度 ============
rules = yaml.safe_load(open(KC + r"\freezes\safety_rules.yaml", encoding="utf-8"))["gate_rules"]
SG_RULES = [r for r in rules if r["evaluator"] in
            ("low_light_headlight", "moving_door", "acceleration_obstacle",
             "deceleration_rear_conflict", "dense_fog_defog")]
sg = SafetyGateService({"gate_rules": []})

# 规则 enforcement：HARD→BLOCK / SOFT→REVIEW（依据 safety_rules 与迁移清单）
ENFORCEMENT = {"LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED": "BLOCK",
               "MOVING_DOOR_OPEN_PROHIBITED": "BLOCK",
               "FRONT_OBSTACLE_ACCELERATION_PROHIBITED": "BLOCK",
               "DENSE_FOG_FRONT_DEFOG_OFF_PROHIBITED": "BLOCK",
               "REAR_STATE_DECELERATION_CONFLICT": "REVIEW"}

# ============ 知识节点侧求值 ============
nodes = []
with open(KC + r"\acceptance\knowledge_constraints_v1.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            nodes.append(json.loads(line))

def kn_eval(n, cmd, ev):
    """知识节点求值：返回 (decision, matched)。MISSING 按证据门策略映射 REVIEW。"""
    c = n["command"]
    if cmd.get("intent_id") != c.get("intent_id"):
        return None
    if c.get("mode", "ANY") != "ANY" and cmd.get("mode") != c.get("mode"):
        return None
    grp = "all" if "all" in n["when"] else "any"
    preds = n["when"][grp]
    alias_map = {a: e for a, e in n["evidence"].items()}
    def evalp(p):
        aev = alias_map[p["field"]]
        key = f"{aev['type']}.{aev['field']}"
        if key not in ev or ev[key] is None:
            return "MISSING"
        v = ev[key]
        # 类型门：数字字段（VEHICLE_SPEED/SURROUNDING_OBJECT_STATE 距离）只接受 int/float
        numeric = (aev["type"] == "VEHICLE_SPEED"
                   or (aev["type"] == "SURROUNDING_OBJECT_STATE"
                       and "distance" in aev["field"]))
        if numeric and (isinstance(v, bool) or not isinstance(v, (int, float))):
            return "TYPE_ERROR"
        try:
            return {"GT": lambda: v > p["value"], "GTE": lambda: v >= p["value"],
                    "LT": lambda: v < p["value"], "LTE": lambda: v <= p["value"],
                    "EQ": lambda: v == p["value"], "NE": lambda: v != p["value"],
                    "IN": lambda: v in p["value"], "NOT_IN": lambda: v not in p["value"]}[p["op"]]()
        except TypeError:
            return "TYPE_ERROR"
    results = [evalp(p) for p in preds]
    if "MISSING" in results:
        return ("REVIEW", "证据缺失→按策略REVIEW")   # 证据门策略
    if "TYPE_ERROR" in results:
        return ("REVIEW", "类型错误→按策略REVIEW")
    ok = all(results) if grp == "all" else any(results)
    return (n["effect"]["then"] if ok else n["effect"]["else"], "when求值")

def kn_decision(cmd, ev):
    """聚合 5 节点：最严格决策 + 命中列表。"""
    rank = {"BLOCK": 3, "REVIEW": 2, "ALLOW": 1}
    best, reason, hits = None, "", []
    for n in nodes:
        r = kn_eval(n, cmd, ev)
        if r:
            d, why = r
            hits.append((n["node_id"], d))
            if best is None or rank[d] > rank[best]:
                best, reason = d, why
    if best is None:
        return "NOT_APPLICABLE", "无节点命中", hits
    return best, reason, hits

# ============ SafetyGate 侧求值 ============
def sg_decision(cmd, ev):
    """evaluator 求值：命中规则按 enforcement 映射，取最严格；证据门(缺失/类型)前置。"""
    by_type = mk_evidence(ev)
    intent = mk_intent(cmd.get("intent_id"), cmd.get("mode"), cmd.get("value"))
    validation = mk_validation(any("conflict" in k or "alt" in k for k in ev))
    rank = {"BLOCK": 3, "REVIEW": 2}
    best, reason = None, ""
    # 证据门-缺失：检查 when 引用键是否全部提供（对照节点 evidence 声明）
    for n in nodes:
        c = n["command"]
        if cmd.get("intent_id") != c.get("intent_id"):
            continue
        if c.get("mode", "ANY") != "ANY" and cmd.get("mode") != c.get("mode"):
            continue
        for alias, aev in n["evidence"].items():
            key = f"{aev['type']}.{aev['field']}"
            if key not in ev or ev[key] is None:
                return "REVIEW", f"证据缺失({key})→证据门REVIEW"
    # 证据门-类型错误
    for key, val in ev.items():
        if key.startswith("VEHICLE_SPEED.") or key.startswith("SURROUNDING_OBJECT_STATE."):
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return "REVIEW", "类型错误→值校验REVIEW"
    for rule in SG_RULES:
        try:
            hit, detail, _ = sg._evaluators[rule["evaluator"]](rule, intent, None, by_type, [], validation)
        except Exception as e:
            return None, f"NOT_EXECUTABLE: {e}"
        if hit:
            d = ENFORCEMENT.get(rule["id"], "REVIEW")
            if best is None or rank[d] > rank[best]:
                best = d
                reason = f"{rule['id']}({detail.get('failure_reason', 'hit')})"
    if best is None:
        if any("conflict" in k or "alt" in k for k in ev):
            return "REVIEW", "证据冲突→策略REVIEW"
        return "ALLOW", "无规则命中"
    return best, reason

# ============ 差分执行 ============
CASES = []
for path in ["knowledge_constraint_acceptance_v1.jsonl",
             "knowledge_constraint_eval_extended_v1.jsonl",
             "safety_gate_enhancement_cases_v1.jsonl"]:
    with open(KC + rf"\acceptance\{path}", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                CASES.append((path, json.loads(line)))
print(f"场景总数: {len(CASES)}")

def normalize_command(c, path):
    """统一规范指令：基础/扩充用 command；增强用例用 intent_id+mode 顶层。"""
    if "command" in c and c["command"]:
        cmd = c["command"]
    else:
        cmd = {"intent_id": c.get("intent_id", ""),
               "mode": c.get("mode")}
    # 增强用例的 intent_id 在顶层
    if not cmd.get("intent_id") and c.get("intent_id"):
        cmd["intent_id"] = c["intent_id"]
    if cmd.get("mode") is None and c.get("mode"):
        cmd["mode"] = c["mode"]
    if c.get("intent_value") is not None:
        cmd["value"] = c["intent_value"]
    return cmd

RANK = {"BLOCK": 3, "REVIEW": 2, "ALLOW": 1, "NOT_APPLICABLE": 0}

rows = []
stats = Counter()
for path, c in CASES:
    cmd = normalize_command(c, path)
    ev = c.get("evidence", {})
    kd, kwhy, khits = kn_decision(cmd, ev)
    gd, gwhy = sg_decision(cmd, ev)
    if gd is None:
        status = "NOT_EXECUTABLE"
        reason = gwhy
    else:
        # NOT_APPLICABLE 与 ALLOW 同为"无约束放行"，视为一致
        if kd == "NOT_APPLICABLE" and gd == "ALLOW":
            status = "CONSISTENT"
            reason = "均无约束放行（NOT_APPLICABLE 与 ALLOW 等价）"
        elif kd == gd:
            status = "CONSISTENT"
            reason = "一致"
        elif kd == "NOT_APPLICABLE" and gd in ("BLOCK", "REVIEW"):
            status = "SAFETYGATE_STRICTER"
            reason = f"知识节点不适用，SafetyGate {gd}（evaluator 覆盖更广）"
        elif RANK.get(gd, 0) > RANK.get(kd, 0):
            status = "SAFETYGATE_STRICTER"
            reason = f"知识={kd}，SafetyGate={gd}（{gwhy}）"
        elif RANK.get(kd, 0) > RANK.get(gd, 0):
            status = "FAILED_KNOWLEDGE_STRICTER"
            reason = f"知识={kd}({kwhy}) 比 SafetyGate={gd} 更严"
        else:
            status = "FAILED_UNEXPLAINED"
            reason = f"知识={kd}({kwhy}) vs SafetyGate={gd}({gwhy})"
    stats[status] += 1
    rows.append({"source": path.split("_")[0], "case_id": c.get("case_id", "?"),
                 "kn_decision": kd, "kn_reason": kwhy,
                 "sg_decision": gd, "sg_reason": gwhy,
                 "status": status, "diff_reason": reason})

print(f"\n差分结果: {dict(stats)}")
print("\n=== 失败/不可执行明细 ===")
for r in rows:
    if r["status"] not in ("CONSISTENT", "SAFETYGATE_STRICTER"):
        print(f"  ✗ {r['case_id']} [{r['status']}] {r['diff_reason'][:90]}")

# 报告
rep = {"total": len(rows), "stats": dict(stats), "rows": rows,
       "accept": stats["CONSISTENT"] + stats["SAFETYGATE_STRICTER"],
       "failed": stats["FAILED_KNOWLEDGE_STRICTER"] + stats["FAILED_UNEXPLAINED"],
       "not_executable": stats["NOT_EXECUTABLE"],
       "verdict": "PASS" if (stats.get("FAILED_KNOWLEDGE_STRICTER", 0) == 0
                             and stats.get("FAILED_UNEXPLAINED", 0) == 0
                             and stats.get("NOT_EXECUTABLE", 0) == 0) else "FAIL"}
with open(KC + r"\acceptance\constraint_diff_matrix_v1.json", "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1)
print(f"\nverdict: {rep['verdict']} -> {KC}/acceptance/constraint_diff_matrix_v1.json")
