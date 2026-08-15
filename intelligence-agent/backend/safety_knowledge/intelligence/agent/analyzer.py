"""情报智能体 v3 —— Layer 3: Incident Analyzer

职责：把 IncidentCluster → 结构化分析结果
  - Component 标准化（family / sub）
  - FailureMode 提取（枚举）
  - OperatingCondition 提取（枚举）
  - Consequence 提取（枚举）+ Severity 分级（取最严重）
  - 全字段可追溯到原文（抽取时记录触发句）

输出：AnalysisResult（供 Mapping / Novelty / Priority 层使用）
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from typing import Any

from safety_knowledge.intelligence.models import (
    Consequence,
    FailureMode,
    IncidentCluster,
    OperatingCondition,
    SourceRecord,
    SourceAuthority,
)

# 组件家族 → 能力域锚点（Ontology Anchor，供 Mapping Layer 复用）
COMPONENT_DOMAIN_MAP: dict[str, tuple[str, list[str]]] = {
    "EXTERIOR LIGHTING": ("灯光", ["HEADLIGHT_SET_MODE", "LOW_BEAM_ON", "HIGH_BEAM_ON", "FOG_LIGHT_ON", "PARKING_LIGHT_ON", "HAZARD_LIGHT_ON", "TURN_INDICATOR_ON"]),
    "INTERIOR LIGHTING": ("灯光", ["HEADLIGHT_SET_MODE", "READING_LIGHT_ON"]),
    "LIGHTING": ("灯光", ["HEADLIGHT_SET_MODE"]),
    "SERVICE BRAKES": ("行驶控制", ["BRAKE", "EMERGENCY_BRAKE"]),
    "PARKING BRAKE": ("泊车驻车", ["PARKING_BRAKE_APPLY", "PARKING_BRAKE_RELEASE"]),
    "STEERING": ("行驶控制", ["EVASIVE_STEER", "LANE_CHANGE", "LANE_KEEP"]),
    "SUSPENSION": ("行驶控制", ["LANE_KEEP"]),
    "POWER TRAIN": ("行驶控制", ["GEAR_SET", "ACCELERATE"]),
    "ENGINE AND ENGINE COOLING": ("行驶控制", ["ACCELERATE", "GEAR_SET"]),
    "FUEL SYSTEM": ("动力传动", ["ACCELERATE"]),
    "ELECTRICAL SYSTEM:ADAS": ("行驶控制", ["LANE_CHANGE", "EMERGENCY_BRAKE", "EVASIVE_STEER"]),
    "ELECTRICAL SYSTEM": ("网络安全", ["SEC_COMMUNICATION", "SEC_LOG_AUDIT", "SEC_ACCESS_CONTROL"]),
    "FORWARD COLLISION": ("行驶控制", ["EMERGENCY_BRAKE", "EVASIVE_STEER"]),
    "BACK OVER PREVENTION": ("泊车驻车", ["AUTO_PARK_ENABLE"]),
    "VEHICLE SPEED CONTROL": ("行驶控制", ["ACCELERATE", "CRUISE_SET_SPEED", "CRUISE_ENABLE"]),
    "LATCHES": ("车身", ["DOOR_OPEN", "DOOR_LOCK", "DOOR_CLOSE", "TRUNK_OPEN", "TRUNK_LOCK"]),
    "SEAT BELTS": ("车身", []),
    "AIR BAGS": ("车身", []),
    "SEATS": ("车身", []),
    "TIRES": ("信息与安全", ["SEC_LOG_AUDIT"]),
    "WHEELS": ("行驶控制", ["LANE_KEEP"]),
    "INSTRUMENT CLUSTER": ("网络安全", ["SEC_LOG_AUDIT"]),
    "BODY CONTROL": ("网络安全", ["SEC_ACCESS_CONTROL"]),
    "VISIBILITY": ("视野", ["WIPER_SET_MODE", "DEFROST_ON", "SUNROOF_OPEN"]),
    "EQUIPMENT": ("网络安全", []),
    "BACK OVER PREVENTION": ("泊车驻车", ["AUTO_PARK_ENABLE"]),
    "HORN": ("车身", ["HORN_ACTIVATE"]),
    "AUTOMATED PARKING": ("泊车驻车", ["AUTO_PARK_ENABLE"]),
    "UNKNOWN": ("其他", []),
}

# 组件子项 → 意图细化（如 TAIL LIGHTS 属灯光域）
SUB_INTENT_OVERRIDES: dict[str, list[str]] = {
    "AUTOMATED": ["LANE_CHANGE", "EVASIVE_STEER"],
    "ADAPTIVE": ["LANE_CHANGE", "EVASIVE_STEER"],
    "HYDRAULIC": ["BRAKE"],
    "ELECTRICAL": ["PARKING_BRAKE_APPLY", "PARKING_BRAKE_RELEASE"],
    "TAIL": ["HEADLIGHT_SET_MODE", "PARKING_LIGHT_ON"],
    "DOORS": ["DOOR_OPEN", "DOOR_LOCK", "DOOR_CLOSE"],
    "HOOD": ["TRUNK_OPEN", "DOOR_OPEN"],
}


@dataclass
class AnalysisResult:
    """Layer 3 输出（结构化）。"""

    cluster_id: str
    subject: str
    component_family: str
    component_sub: str
    capability_domain: str
    failure_modes: list[FailureMode]
    operating_conditions: list[OperatingCondition]
    consequences: list[Consequence]
    severity: int                          # 1-4
    severity_label: str
    source_authority: SourceAuthority
    official_confirmed: bool
    corroboration_count: int
    ontology_intents: list[str]            # Ontology Anchor 候选（含空=无锚点）
    text_evidence: dict[str, list[str]]    # 抽取触发句（可追溯）
    provenance: list[str] = field(default_factory=list)

    def full_text(self) -> str:
        """合并所有记录的原始文本（供检索/分析）。"""
        return " ".join(self.text_evidence.get("raw", []))


class IncidentAnalyzer:
    """Layer 3 实现。"""

    SEVERITY_LABEL = {1: "SEV1_伤亡失控", 2: "SEV2_碰撞火灾", 3: "SEV3_功能失效", 4: "SEV4_合规一般"}

    @staticmethod
    def _resolve_domain(family: str) -> tuple[str, list[str]]:
        """最长前缀匹配 COMPONENT_DOMAIN_MAP（容忍变体）。"""
        best_domain, best_intents, best_len = "其他", [], -1
        for key, (dom, intents) in COMPONENT_DOMAIN_MAP.items():
            if family.startswith(key.upper()) and len(key) > best_len:
                best_domain, best_intents, best_len = dom, intents, len(key)
        return best_domain, best_intents

    def analyze(self, cluster: IncidentCluster) -> AnalysisResult:
        # 合并全文
        texts = [f"{r.raw_title} {r.raw_content}" for r in cluster.records]
        full = " ".join(texts)

        # Component（最长前缀匹配，容忍逗号/斜杠变体）
        raw_family = cluster.component_family
        family = re.split(r"[,/]", raw_family)[0].strip().upper()
        sub = cluster.component_sub
        domain, ontology_intents = self._resolve_domain(family)
        # 子项细化
        sub_upper = sub.upper()
        for key, intents in SUB_INTENT_OVERRIDES.items():
            if key in sub_upper:
                ontology_intents = intents
                break

        # 枚举提取
        fm = FailureMode.from_text(full)
        conds = OperatingCondition.from_text(full)
        cons = Consequence.from_text(full)

        # Severity（取最严重后果）
        sev = min((c.severity for c in cons), default=4)
        if sev == 4 and fm and FailureMode.UNKNOWN not in fm:
            sev = 3  # 有明确失效模式但无后果描述 → 功能失效级

        # 触发句（可追溯）
        text_evidence = {
            "raw": texts,
            "failure_sentences": [t for t in texts if any(x in t.lower() for x in
                                 ("fail", "intermitt", "corros", "improper", "leak", "loose", "软件", "失效", "间歇"))][:3],
            "consequence_sentences": [t for t in texts if any(x in t.lower() for x in
                                     ("crash", "injury", "fire", "loss of control", "碰撞", "受伤", "失控"))][:3],
        }

        # 权威等级（取记录中最高）
        authority = max((r.source_type for r in cluster.records),
                        key=lambda a: {
                            SourceAuthority.OFFICIAL_REGULATOR: 3, SourceAuthority.OEM_OFFICIAL: 2,
                            SourceAuthority.GOVERNMENT: 2, SourceAuthority.MEDIA: 1,
                            SourceAuthority.USER_REPORT: 0}.get(a, 0))

        return AnalysisResult(
            cluster_id=cluster.cluster_id,
            subject=cluster.subject,
            component_family=family,
            component_sub=sub,
            capability_domain=domain,
            failure_modes=fm,
            operating_conditions=conds,
            consequences=cons,
            severity=sev,
            severity_label=self.SEVERITY_LABEL[sev],
            source_authority=authority,
            official_confirmed=cluster.official_confirmed,
            corroboration_count=cluster.corroboration_count,
            ontology_intents=ontology_intents,
            text_evidence=text_evidence,
            provenance=[f"{r.source_id}@{r.retrieved_at} hash={r.content_hash[:8]}" for r in cluster.records],
        )


if __name__ == "__main__":
    from safety_knowledge.intelligence.agent.source_layer import ProvenanceFetcher
    from safety_knowledge.intelligence.agent.clusterer import IncidentClusterer

    f = ProvenanceFetcher()
    r1 = f.from_legacy({"incident_id": "A1", "title": "召回: EXTERIOR LIGHTING:TAIL LIGHTS",
                        "content": "One or both taillights may intermittently fail to illuminate, reducing visibility.",
                        "source_id": "NHTSA-RCL", "official_confirmed": True})
    c = IncidentClusterer().cluster([r1])[0]
    a = IncidentAnalyzer().analyze(c)
    print(f"{a.cluster_id} | {a.component_family} | domain={a.capability_domain}")
    print(f"  FM={[m.value for m in a.failure_modes]} | CONS={[x.value for x in a.consequences]} | SEV={a.severity}")
    print(f"  ontology_intents={a.ontology_intents}")
    f.close()
