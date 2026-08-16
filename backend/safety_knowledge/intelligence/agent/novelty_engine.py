"""情报智能体 v3 —— Layer 5: Novelty Engine v2

设计要点（用户反馈 #6）：
  - 独立于 Mapping 判定（不依赖"来自知识库的 intent"，打破循环论证）
  - 结构重叠三维度：Component 域覆盖 + Evidence 重叠 + Embedding 相似
  - 输出：KNOWN / PARTIAL_NOVEL / NOVEL + novelty_score + 逐条 reasons

判定规则：
  1. component 域在知识库无节点            → NOVEL
  2. 域有节点 且 证据重叠 ≥ 0.5 且 嵌入相似 ≥ 0.75 → KNOWN
  3. 域有节点但证据/嵌入不完全            → PARTIAL_NOVEL
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any

import hnswlib
import numpy as np

from safety_knowledge.intelligence.agent.analyzer import AnalysisResult
from safety_knowledge.intelligence.models import NoveltyLabel

THRESH_EMBED_KNOWN = 0.75
THRESH_EV_KNOWN = 0.5

# 非语音车控组件（气囊/安全带/燃油/座椅/标签/传动轴/车桥/轮胎/悬架/发动机机械）
# 注：ENGINE 的 ELECTRONIC CONTROL MODULE（ECM/TCM/SOFTWARE）除外——属电子安全域
NON_VOICE_COMPONENTS = (
    "AIR BAGS", "SEAT BELTS", "FUEL", "SEATS", "EQUIPMENT",
    "TIRES", "WHEELS", "SUSPENSION", "DRIVELINE", "AXLE",
    "STRUCTURE", "BODY",
)
# 引擎机械（非电子控制）也属非车控；带 CONTROL MODULE/SOFTWARE 的例外
NON_VOICE_EXCEPTIONS = ("CONTROL MODULE", "ECM", "TCM", "SOFTWARE", "ELECTRICAL", "HYBRID")
# POWER TRAIN 子项中非语音车控的（传动轴/车桥/轮毂）
POWER_TRAIN_NON_VOICE_SUB = ("DRIVELINE", "AXLE", "HUB", "PROPSHAFT", "SHAFT")

# 知识库已知部件清单（F3：从 Trusted 节点语义提取，人工审核可追溯）
# 命中 → 部件概念已被知识库覆盖；未命中 → 概念级新（NOVEL 候选）
KB_SUB_COMPONENTS = (
    "前照灯", "大灯", "远光", "近光", "雾灯", "示廓灯", "驻车灯", "危险警告", "危险报警",
    "转向灯", "转向信号", "喇叭", "雨刮", "刮水器", "后视镜", "除霜", "除雾",
    "天窗", "车窗", "车门", "乘客门", "后备箱", "行李箱", "巡航", "车道保持", "换道",
    "行车制动", "液压制动", "气压制动", "应急制动", "驻车制动", "防抱制动", "自动泊车",
    "档位", "限速", "超速", "光束", "制动踏板", "喇叭声级", "牵引", "灯光", "照明",
    "安全玻璃", "座椅", "轮胎", "充电", "电池",
    # 英文已知部件（F3 补充）
    "HEADLIGHT", "LIGHT", "BRAKE", "LANE", "CRUISE", "WIPER", "MIRROR", "DEFROST",
    "HORN", "DOOR", "WINDOW", "SUNROOF", "TRUNK", "PARKING BRAKE", "GEAR", "SEAT",
    "AUTOMATED PARKING", "PARK ASSIST", "BACK OVER", "ACCELER", "LIMIT", "SPEED",
    "FOG", "HAZARD", "TURN SIGNAL", "INDICATOR",
)

# 明确"概念级新"的子项触发词（F3 白名单：命中 → NOVEL，即使家族已映射）
NOVEL_TRIGGER_SUB = (
    "POWER ASSIST", "COLUMN", "CONTROL MODULE", "TCM", "ECM", "TRAILER",
    "HIGH VOLTAGE", "THERMAL RUNAWAY", "PROPULSION", "ELECTRIC POWER", "ASSIST",
    "BATTERY PACK", "STEERING GEAR", "AIRBAG", "INFLATOR",
)


def sub_known(component_family: str, component_sub: str) -> bool:
    """子项/家族是否命中知识库已知部件。"""
    text = f"{component_family} {component_sub}".upper()
    return any(kw.upper() in text for kw in KB_SUB_COMPONENTS)


@dataclass
class NoveltyResult:
    label: NoveltyLabel
    score: float
    reasons: list[str]
    details: dict[str, Any] = field(default_factory=dict)


class NoveltyEngine:
    """Layer 5 实现。"""

    def __init__(self, trusted_nodes: list[dict]) -> None:
        self._trusted = trusted_nodes
        # 域 → 节点
        self._domain_nodes: dict[str, list[dict]] = {}
        # 域 → 证据全集
        self._domain_evidence: dict[str, set[str]] = {}
        for n in trusted_nodes:
            domain = n["node_id"].split(".")[1] if len(n["node_id"].split(".")) > 1 else "其他"
            self._domain_nodes.setdefault(domain, []).append(n)
            self._domain_evidence.setdefault(domain, set()).update(n.get("required_evidence", []))

        # HNSW（嵌入相似）
        self._index = None
        if trusted_nodes:
            dim = len(trusted_nodes[0].get("vector", [])) or 768
            self._index = hnswlib.Index(space="cosine", dim=dim)
            self._index.init_index(max_elements=max(10000, len(trusted_nodes) * 2),
                                   ef_construction=200, M=16)
            self._index.set_ef(50)
            vecs = np.asarray([n.get("vector") or np.zeros(dim, dtype=np.float32) for n in trusted_nodes],
                              dtype=np.float32)
            self._index.add_items(vecs, np.arange(len(trusted_nodes)))

    def evaluate(self, a: AnalysisResult, embedder=None, mapping_status=None, mapped_intents=None) -> NoveltyResult:
        reasons: list[str] = []
        details: dict[str, Any] = {}

        # 0. IRRELEVANT 判定（非语音车控组件——四分类架构修复）
        fam = a.component_family.upper()
        sub = a.component_sub.upper()
        is_non_voice = any(fam.startswith(x) for x in NON_VOICE_COMPONENTS)
        # POWER TRAIN 子项判定（传动轴/车桥/轮毂 → 非车控；变速箱 → 车控）
        if fam.startswith("POWER TRAIN") and any(x in sub for x in POWER_TRAIN_NON_VOICE_SUB):
            is_non_voice = True
        if is_non_voice and not any(x in sub for x in NON_VOICE_EXCEPTIONS):
            return NoveltyResult(
                label=NoveltyLabel.IRRELEVANT,
                score=0.0,
                reasons=[f"组件 '{a.component_family}' 属非语音车控范畴（知识库范围外），不作新颖性判定"],
                details={"domain": a.capability_domain, "non_voice": True},
            )
        # 发动机机械（非电子控制）
        if fam.startswith("ENGINE AND ENGINE COOLING") and not any(x in sub for x in NON_VOICE_EXCEPTIONS):
            return NoveltyResult(
                label=NoveltyLabel.IRRELEVANT,
                score=0.0,
                reasons=[f"组件 '{a.component_family}'（发动机机械）非语音车控范畴"],
                details={"domain": a.capability_domain, "non_voice": True},
            )

        # 1. Component 域覆盖
        domain = a.capability_domain
        domain_nodes = self._domain_nodes.get(domain, [])
        details["domain_covered"] = bool(domain_nodes)
        details["domain"] = domain
        if not domain_nodes:
            return NoveltyResult(
                label=NoveltyLabel.NOVEL,
                score=0.0,
                reasons=[f"能力域 '{domain}' 在知识库无节点（覆盖盲区）"],
                details=details,
            )

        # 2. Evidence 重叠（候选证据 vs 域证据全集）
        cand_ev = set(a.full_text() and self._extract_evidence_keywords(a))
        details["candidate_evidence_keywords"] = sorted(cand_ev)
        domain_ev = self._domain_evidence.get(domain, set())
        overlap = len(cand_ev & domain_ev)
        ev_ratio = overlap / len(cand_ev) if cand_ev else 0.0
        details["evidence_overlap_ratio"] = round(ev_ratio, 3)
        details["evidence_overlap"] = sorted(cand_ev & domain_ev)
        if ev_ratio >= THRESH_EV_KNOWN:
            reasons.append(f"证据重叠 {ev_ratio:.2f} ≥ {THRESH_EV_KNOWN}（与域 '{domain}' 证据体系重合）")
        else:
            reasons.append(f"证据重叠 {ev_ratio:.2f} < {THRESH_EV_KNOWN}（候选证据在域内较新）")

        # 3. Embedding 相似（与域内最相似节点）
        max_sim = 0.0
        if self._index is not None and embedder is not None:
            vec, _ = embedder.encode(a.full_text()[:512])
            q = np.asarray(vec, dtype=np.float32).reshape(1, -1)
            labels, distances = self._index.knn_query(q, k=3)
            best = None
            for l, d in zip(labels[0], distances[0]):
                if int(l) == -1:
                    continue
                sim = float(1.0 - d)
                if sim > max_sim:
                    max_sim = sim
                    best = self._trusted[int(l)]
            details["max_embedding_sim"] = round(max_sim, 4)
            details["closest_node"] = best["node_id"] if best else None
            if max_sim >= THRESH_EMBED_KNOWN:
                reasons.append(f"嵌入相似 {max_sim:.2f} ≥ {THRESH_EMBED_KNOWN}（与 '{best['title']}' 语义重合）")
            else:
                reasons.append(f"嵌入相似 {max_sim:.2f} < {THRESH_EMBED_KNOWN}（语义与现有知识差异大）")
        else:
            details["max_embedding_sim"] = None

        # 融合判定（F3 v3.5）
        # 映射路信号：仅"具体组件意图"（HEADLIGHT_SET_MODE）可作为覆盖证据；
        # 泛化安全域意图（SEC_*/DATA_*/OTA_*）不证明事故概念被覆盖
        GENERIC_INTENT_PREFIXES = ("SEC_", "DATA_", "OTA_", "LAW_", "DSSAD_")
        specific_mapped = bool(mapped_intents) and mapping_status is not None and \
                          mapping_status.value == "MAPPED" and \
                          not any(mapped_intents[0].startswith(p) for p in GENERIC_INTENT_PREFIXES)
        if specific_mapped:
            reasons.append(f"Mapping 已映射到具体意图 {mapped_intents[:2]}（本体已覆盖该风险领域）")
            if ev_ratio >= THRESH_EV_KNOWN and max_sim >= THRESH_EMBED_KNOWN:
                label, score = NoveltyLabel.KNOWN, 0.9
            elif any(t in a.component_sub.upper() for t in NOVEL_TRIGGER_SUB) or \
                 any(t in a.component_family.upper() for t in NOVEL_TRIGGER_SUB):
                # 子项/家族命中"概念级新"触发词（EPS 助力/变速箱/ECM/拖车/高压电池）
                reasons.append(f"部件 '{a.component_sub}' 属概念级新（知识库无该部件概念）")
                label, score = NoveltyLabel.NOVEL, 0.3
            else:
                # 部件已知，失效模式/细节差异 → PARTIAL
                label, score = NoveltyLabel.PARTIAL_NOVEL, 0.5
        elif ev_ratio >= THRESH_EV_KNOWN and max_sim >= THRESH_EMBED_KNOWN:
            label, score = NoveltyLabel.KNOWN, 0.9
        elif ev_ratio >= THRESH_EV_KNOWN or max_sim >= THRESH_EMBED_KNOWN:
            label, score = NoveltyLabel.PARTIAL_NOVEL, 0.5
        else:
            label, score = NoveltyLabel.NOVEL, 0.2

        return NoveltyResult(label=label, score=score, reasons=reasons, details=details)

    @staticmethod
    def _extract_evidence_keywords(a: AnalysisResult) -> set[str]:
        """从事故文本提取候选证据关键词（证据枚举匹配）。"""
        # 证据枚举全表（与 schema 的 evidence ontology 对齐）
        from safety_knowledge.intelligence.agent.evidence_ontology import EVIDENCE_KEYWORDS
        text = a.full_text().lower()
        hits = set()
        for ev, kws in EVIDENCE_KEYWORDS.items():
            if any(kw in text for kw in kws):
                hits.add(ev)
        return hits


if __name__ == "__main__":
    print("Novelty Engine v2 加载成功（结构重叠三维度，独立判定）")
