"""情报收集智能体 v2（Incident Intelligence Agent）

设计原则（严谨逻辑）：
  1. 事实链可追溯：任何字段必须能追溯到原始事故文本（content/consequence/correctiveAction）
  2. 结构标准化：Component → (family, sub) ；Failure Mode → 枚举；Consequence → 枚举
  3. 意图/证据从真实知识库推导（非固定表）：component → 能力域 → 知识库节点 → mandatory evidence 并集
  4. 风险评分可解释：官方确认 + 危害等级 + 车控相关性 + 影响范围，加权可见
  5. 候选节点不自动进 Trusted（L5 / PENDING_REVIEW），审核晋级需记录理由

管线：Source → Normalize → Analyze → Intent/Evidence → RiskScore → Novelty → NodeBuild → Review
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from safety_knowledge.ontology.node_schema_v2 import build_node_id  # noqa: E402
from safety_knowledge.retrieval.canonical_query import build_retrieval_text  # noqa: E402

# ==================== 枚举与映射表（人工审核，可扩展） ====================

# NHTSA Component 前缀 → (能力域, 候选意图列表)
COMPONENT_INTENT_MAP: dict[str, tuple[str, list[str]]] = {
    "EXTERIOR LIGHTING": ("灯光", ["HEADLIGHT_SET_MODE", "LOW_BEAM_ON", "FOG_LIGHT_ON", "PARKING_LIGHT_ON", "HAZARD_LIGHT_ON"]),
    "INTERIOR LIGHTING": ("灯光", ["HEADLIGHT_SET_MODE"]),
    "LIGHTING": ("灯光", ["HEADLIGHT_SET_MODE"]),
    "SERVICE BRAKES": ("行驶控制", ["BRAKE", "EMERGENCY_BRAKE"]),
    "PARKING BRAKE": ("泊车驻车", ["PARKING_BRAKE_APPLY", "PARKING_BRAKE_RELEASE"]),
    "STEERING": ("行驶控制", ["EVASIVE_STEER", "LANE_CHANGE", "LANE_KEEP"]),
    "SUSPENSION": ("行驶控制", ["LANE_KEEP"]),
    "POWER TRAIN": ("动力传动", ["ACCELERATE", "GEAR_SET"]),
    "ENGINE AND ENGINE COOLING": ("动力传动", ["ACCELERATE", "GEAR_SET"]),
    "FUEL SYSTEM": ("动力传动", ["ACCELERATE"]),
    "ELECTRICAL SYSTEM:ADAS": ("行驶控制", ["LANE_CHANGE", "EMERGENCY_BRAKE", "EVASIVE_STEER"]),
    "ELECTRICAL SYSTEM": ("信息与安全", ["SEC_COMMUNICATION", "SEC_LOG_AUDIT"]),
    "FORWARD COLLISION": ("行驶控制", ["EMERGENCY_BRAKE", "EVASIVE_STEER"]),
    "BACK OVER PREVENTION": ("泊车驻车", ["AUTO_PARK_ENABLE"]),
    "LATCHES": ("车身", ["DOOR_OPEN", "DOOR_LOCK", "DOOR_CLOSE"]),
    "SEAT BELTS": ("车身", []),
    "AIR BAGS": ("车身", []),
    "SEATS": ("车身", []),
    "TIRES": ("动力传动", ["LANE_KEEP"]),
    "INSTRUMENT CLUSTER": ("信息与安全", ["SEC_LOG_AUDIT"]),
    "BODY CONTROL": ("车身", ["SEC_ACCESS_CONTROL"]),
    "WHEELS": ("行驶控制", ["LANE_KEEP"]),
    "VISIBILITY": ("视野", ["WIPER_SET_MODE", "DEFROST_ON", "SUNROOF_OPEN"]),
    "EQUIPMENT": ("信息与安全", []),
    "UNKNOWN": ("其他", []),
}

# 失败模式提取（正则 → 枚举）
FAILURE_MODE_PATTERNS: list[tuple[str, str]] = [
    (r"intermittent|间歇|时好时坏", "INTERMITTENT_FAILURE"),
    (r"fail\s*to|失效|失灵|无法", "FUNCTION_LOSS"),
    (r"corrosion|锈蚀|腐蚀", "CORROSION"),
    (r"software|software update|软件", "SOFTWARE_DEFECT"),
    (r"improper|未正确|不正确|错误地", "IMPROPER_ASSEMBLY"),
    (r"may allow|可能导致|may cause", "UNSAFE_BEHAVIOR"),
    (r"leak|泄漏|渗漏", "LEAKAGE"),
    (r"overheat|过热", "OVERHEATING"),
    (r"loose|松动|脱落", "LOOSE_CONNECTION"),
    (r"noise|异响", "NOISE"),
    (r"warning|报警|提示", "FALSE_WARNING"),
    (r"reduce|降低|degrad|性能下降", "PERFORMANCE_DEGRADATION"),
]

# 后果提取（正则 → 枚举 + 危害等级）
CONSEQUENCE_PATTERNS: list[tuple[str, str, int]] = [
    (r"injury|受伤|伤亡|death|死亡", "INJURY_RISK", 1),
    (r"crash|碰撞|撞车|accident", "CRASH_RISK", 2),
    (r"loss of control|失控", "LOSS_OF_CONTROL", 1),
    (r"fire|自燃|起火", "FIRE_RISK", 2),
    (r"unintended accel|误加速|sudden accel", "UNINTENDED_ACCELERATION", 1),
    (r"unintended brake|误制动", "UNINTENDED_BRAKING", 1),
    (r"visibility|视野|能见度", "REDUCED_VISIBILITY", 3),
    (r"noncompliance|不符合|comply", "FMVSS_NONCOMPLIANCE", 4),
    (r"failure", "COMPONENT_FAILURE", 3),
]

SEVERITY_LABEL = {1: "SEV1_伤亡失控", 2: "SEV2_碰撞火灾", 3: "SEV3_功能失效", 4: "SEV4_合规一般"}


# ==================== 数据结构 ====================

@dataclass
class AnalyzedIncident:
    """标准化+分析后的事故情报。"""

    incident_id: str
    title: str
    content: str
    url: str
    source_id: str
    published_at: str
    vehicle_make: str | None
    vehicle_model: str | None
    component_family: str                 # 标准化部件族
    component_sub: str                    # 部件子项
    failure_modes: list[str]              # 失效模式枚举
    consequences: list[str]               # 后果枚举
    severity: int                         # 危害等级 1-4
    severity_label: str
    intents: list[str]                    # 派生意图（从知识库映射）
    evidence: list[str]                   # 派生必要证据（从知识库节点推导）
    domain: str                           # 能力域
    official_confirmed: bool
    risk_score: float                     # 0-1 可解释评分
    risk_reason: dict[str, Any]           # 评分明细
    raw: dict[str, Any] = field(default_factory=dict)

    def to_candidate(self) -> dict:
        return {
            "incident_id": self.incident_id, "title": self.title, "content": self.content,
            "url": self.url, "source_id": self.source_id, "published_at": self.published_at,
            "vehicle_make": self.vehicle_make, "vehicle_model": self.vehicle_model,
            "component_family": self.component_family, "component_sub": self.component_sub,
            "failure_modes": self.failure_modes, "consequences": self.consequences,
            "severity": self.severity, "severity_label": self.severity_label,
            "intents": self.intents, "evidence": self.evidence, "domain": self.domain,
            "official_confirmed": self.official_confirmed,
            "risk_score": round(self.risk_score, 4), "risk_reason": self.risk_reason,
            "candidate_status": "PENDING_REVIEW",
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }


# ==================== 智能体核心 ====================

class IncidentIntelligenceAgent:
    """情报收集智能体 v2。"""

    def __init__(self, trusted_nodes: list[dict]) -> None:
        self._trusted = trusted_nodes
        # 意图 → 证据并集（从真实知识库推导，保证与裁决链一致）
        self._intent_evidence: dict[str, set[str]] = {}
        for n in trusted_nodes:
            action = n.get("canonical_action", "")
            if action:
                self._intent_evidence.setdefault(action, set()).update(n.get("required_evidence", []))
        # 能力域索引（节点域）
        self._domain_nodes: dict[str, list[dict]] = {}
        for n in trusted_nodes:
            domain = n["node_id"].split(".")[1]
            self._domain_nodes.setdefault(domain, []).append(n)

    # ---------- 1. 分析 ----------

    def analyze(self, incident: dict) -> AnalyzedIncident:
        title = incident.get("title", "")
        content = incident.get("content", "")
        full = f"{title} {content}"

        # Component 标准化
        comp = incident.get("component", "")
        family = comp.split(":")[0] if ":" in comp else (comp or "UNKNOWN")
        sub = comp.split(":", 1)[1] if ":" in comp else ""

        # Failure Mode
        fm = []
        for pattern, label in FAILURE_MODE_PATTERNS:
            if re.search(pattern, full, re.IGNORECASE):
                if label not in fm:
                    fm.append(label)

        # Consequence + 危害等级
        cons = []
        sev = 4  # 默认最低
        for pattern, label, level in CONSEQUENCE_PATTERNS:
            if re.search(pattern, full, re.IGNORECASE):
                if label not in cons:
                    cons.append(label)
                sev = min(sev, level)

        # 意图映射（component → 候选意图；用 component_sub 细化）
        domain, intent_candidates = COMPONENT_INTENT_MAP.get(family, ("其他", []))
        sub_upper = sub.upper()
        if "TAIL" in sub_upper and "HEADLIGHT_SET_MODE" in intent_candidates:
            intent_candidates = ["HEADLIGHT_SET_MODE"]  # 尾灯属灯光域
        if "AUTOMATED" in sub_upper or "ADAPTIVE" in sub_upper:
            intent_candidates = ["LANE_CHANGE", "EVASIVE_STEER"]
        if "HYDRAULIC" in sub_upper:
            intent_candidates = ["BRAKE"]
        # 过滤：意图必须在知识库中存在；无候选意图 → 空（不兜底，防误判）
        intents = [i for i in intent_candidates if i in self._intent_evidence]

        # 证据推导（主意图 → 知识库证据并集；无意图则空）
        evidence = sorted(self._intent_evidence.get(intents[0], set())) if intents else []

        # 风险评分（可解释加权；无车控意图则 control 权重为 0）
        official = incident.get("official_confirmed", False)
        w_official = 0.30 if official else 0.10
        w_severity = {1: 0.35, 2: 0.25, 3: 0.15, 4: 0.05}[sev]
        w_control = 0.25 if intents else 0.0
        w_failure = 0.10 if fm else 0.0
        score = round(min(1.0, w_official + w_severity + w_control + w_failure), 4)
        risk_reason = {
            "official_confirmed": official, "severity": sev, "intent_derived": intents,
            "weights": {"official": w_official, "severity": w_severity, "control": w_control, "failure": w_failure},
        }

        return AnalyzedIncident(
            incident_id=incident.get("incident_id", "UNKNOWN"),
            title=title, content=content, url=incident.get("url", ""),
            source_id=incident.get("source_id", ""), published_at=incident.get("published_at", ""),
            vehicle_make=incident.get("vehicle_make"), vehicle_model=incident.get("vehicle_model"),
            component_family=family, component_sub=sub,
            failure_modes=fm, consequences=cons, severity=sev,
            severity_label=SEVERITY_LABEL[sev],
            intents=intents, evidence=evidence, domain=domain,
            official_confirmed=official, risk_score=score, risk_reason=risk_reason,
            raw={k: v for k, v in incident.items() if k in ("Consequence", "CorrectiveAction", "Component", "Summary")},
        )
    # ---------- 2. 分诊（是否进入候选库） ----------

    def triage(self, inc: AnalyzedIncident) -> tuple[bool, str]:
        """进入候选库的条件（严谨：每条都要有理由）。"""
        reasons = []
        if inc.official_confirmed:
            reasons.append("官方召回")
        if inc.intents:
            reasons.append(f"涉及车控/安全意图({','.join(inc.intents[:2])})")
        if inc.consequences:
            reasons.append(f"危害后果({','.join(inc.consequences[:2])})")
        if inc.severity <= 3:
            reasons.append(f"危害等级{inc.severity}")
        if not reasons:
            return False, "无官方确认/无车控意图/无危害后果"
        return True, "+".join(reasons)

    # ---------- 3. 知识节点生成（KnowledgeNode v2 Schema） ----------

    def build_node(self, inc: AnalyzedIncident, seq: int, novelty_label: str) -> dict:
        semantic_key = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "", inc.component_family)[:8] or "incident"
        node_id = build_node_id("事故情报", semantic_key, seq)
        description = (
            f"事故/召回情报：{inc.title}。{inc.content[:300]} "
            f"部件:{inc.component_family}({inc.component_sub or '-'}) "
            f"失效模式:{','.join(inc.failure_modes) or '未明确'} "
            f"后果:{','.join(inc.consequences) or '未明确'} "
            f"危害等级:{inc.severity_label} 涉及意图:{','.join(inc.intents)}"
        )
        return {
            "node_id": node_id,
            "node_type": "事故情报",
            "title": f"情报: {inc.title[:50]}",
            "semantic_description": description,
            "canonical_action": inc.intents[0] if inc.intents else "",
            "conditions": ["VEHICLE_MOVING"],
            "required_evidence": inc.evidence,
            "optional_evidence": [],
            "source": inc.source_id,
            "chapter": "",
            "clause": inc.published_at or "",
            "trust_level": "L5",
            "metadata": {
                "incident_id": inc.incident_id,
                "component_family": inc.component_family,
                "component_sub": inc.component_sub,
                "failure_modes": inc.failure_modes,
                "consequences": inc.consequences,
                "severity": inc.severity,
                "intents": inc.intents,
                "risk_score": inc.risk_score,
                "risk_reason": inc.risk_reason,
                "novelty": novelty_label,
                "url": inc.url,
                "official_confirmed": inc.official_confirmed,
                "review_status": "PENDING_REVIEW",
            },
        }

    # ---------- 4. 新颖性判定（结构重叠，复用 v2 逻辑） ----------

    def novelty(self, inc: AnalyzedIncident, threshold_known: float = 0.75) -> str:
        """判定：KNOWN / PARTIAL_NOVEL / NOVEL
        规则：component 域在知识库存在 + 意图重叠 → KNOWN；
             域存在但意图/证据不完整 → PARTIAL_NOVEL；否则 NOVEL。"""
        domain_nodes = self._domain_nodes.get(inc.domain, [])
        if not domain_nodes:
            return "NOVEL"
        intent_overlap = any(n.get("canonical_action") in inc.intents for n in domain_nodes)
        ev_overlap = any(len(set(n.get("required_evidence", [])) & set(inc.evidence)) > 0 for n in domain_nodes)
        if intent_overlap and ev_overlap:
            return "KNOWN"
        if domain_nodes:
            return "PARTIAL_NOVEL"
        return "NOVEL"

    # ---------- 5. 审核晋级（可追溯） ----------

    def review(self, inc: AnalyzedIncident, novelty_label: str, auto_promote_threshold: float = 0.75) -> tuple[str, str]:
        """晋级判定：风险分高 + 官方确认 + 新颖 → 建议晋级；无车控意图 → LOW_VALUE；否则人工复核。"""
        if not inc.intents:
            return "LOW_VALUE", f"无车控/安全意图（{inc.component_family}），与语音车控裁决链无关"
        if inc.risk_score >= auto_promote_threshold and inc.official_confirmed:
            return "PROMOTE_RECOMMENDED", f"risk={inc.risk_score:.2f}>=0.75 且官方确认，建议晋级审核"
        if novelty_label == "NOVEL" and inc.severity <= 2:
            return "PROMOTE_RECOMMENDED", f"新风险且危害等级{inc.severity}，建议晋级审核"
        return "MANUAL_REVIEW", f"risk={inc.risk_score:.2f} 或需人工复核"


def run_pipeline(trusted_nodes: list[dict], incidents: list[dict], save_candidates: bool = True) -> dict:
    """完整管线：analyze → triage → novelty → node → review。"""
    agent = IncidentIntelligenceAgent(trusted_nodes)
    accepted: list[dict] = []
    rejected: list[dict] = []
    nodes: list[dict] = []

    for incident in incidents:
        analyzed = agent.analyze(incident)
        keep, reason = agent.triage(analyzed)
        if not keep:
            rejected.append({"incident_id": analyzed.incident_id, "reason": reason})
            continue
        novelty_label = agent.novelty(analyzed)
        review_verdict, review_reason = agent.review(analyzed, novelty_label)
        candidate = analyzed.to_candidate()
        candidate["novelty"] = novelty_label
        candidate["review_verdict"] = review_verdict
        candidate["review_reason"] = review_reason
        candidate["triage_reason"] = reason
        accepted.append(candidate)

        # LOW_VALUE 情报（无车控意图）不生成候选风险节点，避免污染候选库
        if review_verdict == "LOW_VALUE":
            continue

        node = agent.build_node(analyzed, len(nodes) + 1, novelty_label)
        node["metadata"]["review_verdict"] = review_verdict
        nodes.append(node)

    if save_candidates:
        out = ROOT / "data" / "incident_intelligence" / "analyzed_candidates_v2.jsonl"
        out.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in accepted), encoding="utf-8")
        out_nodes = ROOT / "data" / "candidate_risk_nodes_v2.jsonl"
        out_nodes.write_text("\n".join(json.dumps(n, ensure_ascii=False) for n in nodes), encoding="utf-8")

    return {
        "total": len(incidents),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "rejected_detail": rejected,
        "candidates": accepted,
        "nodes": nodes,
    }
