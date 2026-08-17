# -*- coding: utf-8 -*-
"""第5项：真实应用全链路 E2E。

链路：应用启动(加载合同+5节点+overlay)
  → 语义指令(HEADLIGHT_SET_MODE OFF)
  → 证据需求与证据绑定(VEHICLE_SPEED + ENVIRONMENT_CONDITIONS)
  → SafetyGate(正式模式 constraint_required=True)
  → 知识参数命中(light<20 & speed>0 → BLOCK)
  → 审计记录 knowledge_trace
"""
import sys, io, yaml, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\backend")
KC = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\knowledge-contract-v1")

from app.services.knowledge.constraint_parameter_loader import load_constraint_parameters
from app.services.knowledge.constraint_adapter import build_rule_overlay
from app.services.decision.safety_gate import SafetyGateService
from app.models.schemas import (EvidenceNode, SemanticIntent, SemanticFrame, EvidenceStatus, SecurityClass,
                                AdvancedValidationResult, EvidenceDemand, IntentEvidenceDemand,
                                MemoryPropagationResult, RuntimeCapabilityStatus, RuntimeSafetyContext,
                                SemanticControlMode, IntentEvidenceResolution, IntentEvidenceBinding,
                                RetrievalOrigin)
from datetime import datetime, timezone

print("=" * 70)
print("真实应用全链路 E2E（正式模式 constraint_required=True）")
print("=" * 70)

# ========== 1. 应用启动：加载合同 + 5 节点 + overlay + 预检 ==========
print("\n[1] 应用启动：加载知识合同与约束")
params = load_constraint_parameters(KC / "acceptance" / "knowledge_constraints_v1.jsonl",
                                    KC / "freezes" / "knowledge_constraint_contract_v1.yaml")
overlay = build_rule_overlay(params)
print(f"    合同哈希校验 ✓ | 加载 {len(params)} 条约束 | overlay {len(overlay)} 条")

# 加载 safety_rules（冻结输入，仅路由）
rules = yaml.safe_load((KC / "freezes" / "safety_rules.yaml").read_text(encoding="utf-8"))["gate_rules"]
BUSINESS = ["LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED", "MOVING_DOOR_OPEN_PROHIBITED",
            "FRONT_OBSTACLE_ACCELERATION_PROHIBITED", "REAR_STATE_DECELERATION_CONFLICT",
            "DENSE_FOG_FRONT_DEFOG_OFF_PROHIBITED"]
rules = [r for r in rules if r["id"] in BUSINESS]

# 正式模式：constraint_required=True → 启动预检（5 节点 + 参数）
sg = SafetyGateService({"gate_rules": rules, "constraint_overlay": overlay,
                        "constraint_required": True})
print(f"    SafetyGate 正式模式启动 ✓（预检 5 条节点 + 参数通过）")

# ========== 2. 语义指令 ==========
print("\n[2] 语义指令：关闭前照灯（HEADLIGHT_SET_MODE OFF）")
intent = SemanticIntent(clause_index=0, clause_text="", intent_id="HEADLIGHT_SET_MODE",
    runtime_identity="FORMAL", action="SWITCH_MODE", target="HEADLIGHT", area="ANY",
    value=None, mode="OFF", direction=None, control_attribute="MODE",
    control_domain="车身控制", risk_level="R3", risk_tags=["驾驶视野"],
    semantic_confidence=1.0, ambiguity_score=0.0)
frame = SemanticFrame(frame_id="f1", turn_id="t1", raw_text="关闭前照灯", normalized_text="关闭前照灯",
    semantic_confidence=1.0, ambiguity_score=0.0, semantic_status="CLEAR", review_reasons=[],
    review_candidates=[], unresolved_clauses=[], security_signals=[], intents=[intent])

# ========== 3. 证据需求与绑定 ==========
print("[3] 证据需求与绑定")
demand = EvidenceDemand(demand_id="d1", turn_id="t1", intent_demands=[
    IntentEvidenceDemand.model_construct(intent_id="HEADLIGHT_SET_MODE", clause_index=0,
        action="SWITCH_MODE", target="HEADLIGHT", area="ANY", value=None, risk_level="R3",
        query_text="关闭前照灯", query_vector=[], vectorization_metadata=None,
        required_types=["VEHICLE_SPEED", "ENVIRONMENT_CONDITIONS"], optional_types=[],
        knowledge_augmented_types=[], knowledge_hits=[], priority=1, retrieval_scope="FORMAL")
])

def mk_ev(ev):
    OBJECT = {"ENVIRONMENT_CONDITIONS", "SURROUNDING_OBJECT_STATE"}
    obj = {}
    for key, val in ev.items():
        etype, field = key.split(".", 1)
        obj.setdefault(etype, {})[field] = val
    out = []
    for etype, fields in obj.items():
        v = fields if etype in OBJECT else fields.get("value")
        out.append(EvidenceNode(node_id=f"ev_{etype}", evidence_type=etype, layer="sim",
            source="test", value=v, unit=None, timestamp=datetime.now(timezone.utc),
            expires_at=None, freshness=1.0, consistency=1.0, availability=1.0,
            quality_label=EvidenceStatus.VALID, integrity_hash="h", metadata={},
            security_class=SecurityClass.DRIVING, security_rank=0, base_level=0, safety_adjustment=0,
            hnsw_max_layer=0, hnsw_layer_memberships=[], security_classification_source=None,
            formula_source=None, canonicalization_source=None, merged_node_sources=[],
            field_resolution={}, canonicalization_warnings=[]))
    return out

# 夜间+行驶场景：speed=60, illumination=5（应触发 BLOCK）
evidence = mk_ev({"VEHICLE_SPEED.value": 60, "ENVIRONMENT_CONDITIONS.ambient_illumination": 5})
print(f"    证据：speed=60km/h, ambient_illumination=5lux（夜间行驶场景）")

resolution = IntentEvidenceResolution(
    clause_index=0, intent_id="HEADLIGHT_SET_MODE",
    candidate_node_ids=["ev_VEHICLE_SPEED", "ev_ENVIRONMENT_CONDITIONS"],
    bindings=[
        IntentEvidenceBinding(clause_index=0, intent_id="HEADLIGHT_SET_MODE",
            evidence_type="VEHICLE_SPEED", requirement_level="REQUIRED",
            node_id="ev_VEHICLE_SPEED", resolution_status="RETRIEVED",
            retrieval_origin=RetrievalOrigin.HNSW),
        IntentEvidenceBinding(clause_index=0, intent_id="HEADLIGHT_SET_MODE",
            evidence_type="ENVIRONMENT_CONDITIONS", requirement_level="REQUIRED",
            node_id="ev_ENVIRONMENT_CONDITIONS", resolution_status="RETRIEVED",
            retrieval_origin=RetrievalOrigin.HNSW),
    ],
    mandatory_recall_records=[], missing_required_types=[])

# ========== 4. SafetyGate 裁决 ==========
print("\n[4] SafetyGate 裁决（正式模式）")
result = sg.evaluate(
    frame=frame, demand=demand, evidence=evidence,
    intent_evidence_resolutions=[resolution],
    validation=AdvancedValidationResult(),
    memory=MemoryPropagationResult(),
    runtime_capability=RuntimeCapabilityStatus(embedding_implementation="x", embedding_model="m",
        embedding_dimension=768, real_model_inference=False, embedding_degraded=False,
        index_implementation="hnsw", index_degraded=False, semantic_control_mode=SemanticControlMode.FULL,
        degradation_reasons=[], checked_at=datetime.now(timezone.utc)),
    runtime_safety_context=RuntimeSafetyContext(),
)
print(f"    blocked={result.blocked} | hit_rules={result.hit_rules}")

# ========== 5. 审计记录 knowledge_trace ==========
print("\n[5] 审计记录（knowledge_trace）")
traces = getattr(result, "knowledge_trace", [])
for t in traces:
    if t["gate_hit"]:
        print(f"    → 命中: {t['node_id']}")
        print(f"      证据: {t['evidence']}")
        print(f"      谓词: {t['predicates']}")
        print(f"      runtime_parameter_source: {t['runtime_parameter_source']}")
        print(f"      basis_reference: {t['basis_reference'][:60]}")
        print(f"      gate_reason: {t['gate_reason']}")

low_hit = [t for t in traces if t["rule_id"] == "LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED" and t["gate_hit"]]
ok = (result.blocked is True and len(low_hit) >= 1
      and low_hit[0]["evidence"]["ENVIRONMENT_CONDITIONS.ambient_illumination"] == 5)
print(f"\nE2E verdict: {'PASS' if ok else 'FAIL'}")
print(f"    场景：夜间+行驶+关闭前照灯 → BLOCK（知识节点 知识.灯光.夜间关闭限制.001 命中）")
