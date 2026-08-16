"""情报智能体 v3 —— Layer 4: Safety Mapping Layer（Mapping v2）

设计要点（用户反馈 #1，核心修改）：
  - 三路融合，不允许只依赖 Trusted KB：
      M_final = M_ontology ∪ M_retrieval ∪ M_incident
  - M_ontology  ：固定本体锚点（Component → CapabilityDomain → CandidateIntentSet）
                 不依赖知识库，任何事故都能得到稳定的领域锚点
  - M_retrieval ：Trusted KB HNSW 相似检索（已有知识中是否有相似安全动作/条件/证据）
                 只作为增强，不作为必要条件
  - M_incident  ：事故自身结构推断（FailureMode/Consequence → 意图）
  - 允许 ABSTAIN：三路都无法给出合理意图时输出 UNMAPPED，
                  标记"现有语义本体存在覆盖缺口"（这是知识发现结果，不是失败）
  - 输出：候选意图列表（带来源路标记）+ mapping_status + 每条的理由

NOT 循环论证：Novelty 判定不再使用 mapping 结果中的"来自知识库的意图"
              —— 而是独立使用 component 覆盖 + 证据重叠 + 嵌入相似度。
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any

import hnswlib
import numpy as np

from safety_knowledge.intelligence.agent.analyzer import AnalysisResult, COMPONENT_DOMAIN_MAP, SUB_INTENT_OVERRIDES
from safety_knowledge.intelligence.models import Consequence, FailureMode, MappingStatus

# ==================== M_incident：失效模式/后果 → 意图推断 ====================

FAILURE_TO_INTENT: dict[FailureMode, list[str]] = {
    FailureMode.UNINTENDED_ACTIVATION: ["SEC_ACCESS_CONTROL", "SEC_ANTI_REPLAY", "SEC_MALICIOUS_DATA"],
    FailureMode.FAIL_TO_ACTIVATE: ["SEC_COMMUNICATION", "SEC_OTA_PACKAGE"],
    FailureMode.DATA_CORRUPTION: ["SEC_ANTI_TAMPER", "SEC_LOG_AUDIT", "DSSAD_SECURITY"],
    FailureMode.AUTHENTICATION_BYPASS: ["SEC_IDENTITY_AUTH", "SEC_ACCESS_CONTROL", "SEC_KEY_MANAGEMENT"],
    FailureMode.LOSS_OF_FUNCTION: ["SEC_MALICIOUS_DATA", "SEC_COMMUNICATION"],
    FailureMode.SOFTWARE_DEFECT: ["SEC_OTA_PACKAGE", "OTA_ROLLBACK", "SEC_LOG_AUDIT"],
}

CONSEQUENCE_TO_INTENT: dict[Consequence, list[str]] = {
    Consequence.LOSS_OF_CONTROL: ["EVASIVE_STEER", "ESC_ENABLE"],
    Consequence.UNINTENDED_ACCELERATION: ["ACCELERATE", "BRAKE", "SEC_ANTI_REPLAY"],
    Consequence.UNINTENDED_BRAKING: ["BRAKE", "SEC_ANTI_REPLAY"],
    Consequence.FAILURE_TO_STOP: ["BRAKE", "EMERGENCY_BRAKE"],
    Consequence.STEERING_DEVIATION: ["EVASIVE_STEER", "LANE_KEEP"],
    Consequence.REDUCED_VISIBILITY: ["HEADLIGHT_SET_MODE", "WIPER_SET_MODE", "DEFROST_ON"],
    Consequence.UNINTENDED_ACCESS: ["SEC_ACCESS_CONTROL", "SEC_IDENTITY_AUTH", "SEC_OBD_PROTECTION"],
    Consequence.COLLISION: ["EMERGENCY_BRAKE", "EVASIVE_STEER"],
    Consequence.FIRE: ["SEC_INCIDENT_RESPONSE", "SEC_LOG_AUDIT"],
}


@dataclass
class MappingResult:
    """Layer 4 输出。"""

    capability_domains: list[str]
    candidate_intents: list[str]            # 融合后排序候选
    intent_sources: dict[str, list[str]]    # intent → 来源路（ontology/retrieval/incident）
    mapping_status: MappingStatus
    abstain_reason: str | None = None
    ontology_miss: bool = False             # 本体覆盖缺口标记
    retrieval_hits: list[dict] = field(default_factory=list)  # Trusted 相似节点（证据参考）


class SafetyMapper:
    """Mapping v2 三路融合。"""

    def __init__(self, trusted_nodes: list[dict]) -> None:
        self._trusted = trusted_nodes
        self._intent_nodes: dict[str, list[dict]] = {}
        for n in trusted_nodes:
            action = n.get("canonical_action", "")
            if action:
                self._intent_nodes.setdefault(action, []).append(n)
        # HNSW（retrieval 路）
        self._index = None
        self._vecs: list[np.ndarray] = []
        if trusted_nodes:
            dim = len(trusted_nodes[0].get("vector", [])) or 768
            self._dim = dim
            self._index = hnswlib.Index(space="cosine", dim=dim)
            self._index.init_index(max_elements=max(10000, len(trusted_nodes) * 2),
                                   ef_construction=200, M=16)
            self._index.set_ef(50)
            vecs = np.asarray([n.get("vector") or np.zeros(dim, dtype=np.float32) for n in trusted_nodes],
                              dtype=np.float32)
            self._index.add_items(vecs, np.arange(len(trusted_nodes)))
            self._vecs = list(vecs)
        else:
            self._dim = 768
            self._index = None

    # ---------- 路 1: Ontology Anchor（稳定，不依赖 KB） ----------

    def _m_ontology(self, a: AnalysisResult) -> list[str]:
        return list(a.ontology_intents)

    # ---------- 路 2: Trusted Retrieval（增强，非必要） ----------

    def _m_retrieval(self, a: AnalysisResult) -> tuple[list[str], list[dict]]:
        if self._index is None:
            return [], []
        import numpy as np
        # 用 cluster 全文检索
        query = a.full_text()[:512]
        # 无 embedder 时跳过（由 pipeline 注入 embedder 后调用 search_retrieval）
        return [], []

    def search_retrieval(self, query_text: str, embedder, k: int = 5) -> tuple[list[str], list[dict]]:
        """使用外部 embedder 检索 Trusted KB。"""
        if self._index is None:
            return [], []
        vec, _ = embedder.encode(query_text)
        q = np.asarray(vec, dtype=np.float32).reshape(1, -1)
        labels, distances = self._index.knn_query(q, k=k)
        hits = []
        intents = []
        for l, d in zip(labels[0], distances[0]):
            if int(l) == -1:
                continue
            n = self._trusted[int(l)]
            sim = round(float(1.0 - d), 4)
            hits.append({"node_id": n["node_id"], "title": n["title"],
                         "canonical_action": n["canonical_action"], "score": sim,
                         "evidence": n.get("required_evidence", [])})
            # 阈值 0.68：只接受语义强相关的（防噪音污染）
            if sim >= 0.68 and n["canonical_action"] not in intents:
                intents.append(n["canonical_action"])
        return intents, hits

    # ---------- 路 3: Incident Self Evidence ----------

    def _m_incident(self, a: AnalysisResult) -> list[str]:
        intents: list[str] = []
        for fm in a.failure_modes:
            for i in FAILURE_TO_INTENT.get(fm, []):
                if i not in intents:
                    intents.append(i)
        for cons in a.consequences:
            for i in CONSEQUENCE_TO_INTENT.get(cons, []):
                if i not in intents:
                    intents.append(i)
        return intents

    # ---------- 融合 ----------

    # 意图 → 所属域（从知识库节点推导；SEC_*/DATA_*/OTA_*/DSSAD_*/LAW_* 为安全域）
    SECURITY_INTENTS = {"SEC_", "DATA_", "OTA_", "DSSAD_", "LAW_"}

    # 电子/软件类部件（允许跨域到安全域；纯机械部件如 机油/安全带/气囊 不允许）
    ELECTRONIC_PREFIXES = (
        "ELECTRICAL", "SOFTWARE", "ADAS", "INSTRUMENT", "COMPUTER", "SENSOR",
        "BACK OVER", "FORWARD COLLISION", "AUTOMATED", "CONTROL", "DISPLAY",
        "PROPULSION", "TELECOMMUNICATION", "WIRELESS", "KEYLESS", "ENTERTAINMENT",
        "BODY CONTROL",
    )

    def _domain_guard(self, intent: str, capability_domain: str, component_family: str = "") -> bool:
        """域守卫：候选意图必须属于事故能力域；安全域意图仅对电子/软件类部件放行。"""
        if any(intent.startswith(p) for p in self.SECURITY_INTENTS):
            return any(prefix in component_family.upper() for prefix in self.ELECTRONIC_PREFIXES)
        for n in self._intent_nodes.get(intent, []):
            node_domain = n["node_id"].split(".")[1] if len(n["node_id"].split(".")) > 1 else ""
            if node_domain == capability_domain:
                return True
        # 意图在知识库但域信息缺失 → 保守拒绝
        return False

    def map(self, a: AnalysisResult, embedder=None) -> MappingResult:
        m_onto = self._m_ontology(a)
        m_inc = self._m_incident(a)

        retrieval_intents: list[str] = []
        retrieval_hits: list[dict] = []
        if embedder is not None:
            retrieval_intents, retrieval_hits = self.search_retrieval(a.full_text()[:512], embedder)

        # 融合（保序 + 去重 + 域守卫）
        sources: dict[str, list[str]] = {}
        order: list[str] = []
        for intent, route in [(i, "ontology") for i in m_onto] + \
                             [(i, "retrieval") for i in retrieval_intents] + \
                             [(i, "incident") for i in m_inc]:
            if not self._domain_guard(intent, a.capability_domain, a.component_family):
                continue
            if intent not in sources:
                sources[intent] = [route]
                order.append(intent)
            else:
                if route not in sources[intent]:
                    sources[intent].append(route)

        # 过滤：意图必须在知识库中存在（否则即使映射也无可执行语义）
        final_intents = [i for i in order if i in self._intent_nodes]
        unknown_intents = [i for i in order if i not in self._intent_nodes]

        # ABSTAIN 判定：无任何可执行候选
        if not final_intents:
            reason_parts = []
            if not order:
                reason_parts.append("三路均无意图候选")
            else:
                reason_parts.append(f"候选意图 {unknown_intents[:3]} 不在知识库本体中")
            return MappingResult(
                capability_domains=[a.capability_domain],
                candidate_intents=[],
                intent_sources={},
                mapping_status=MappingStatus.ABSTAIN,
                abstain_reason="；".join(reason_parts),
                ontology_miss=True,
                retrieval_hits=retrieval_hits,
            )

        return MappingResult(
            capability_domains=[a.capability_domain],
            candidate_intents=final_intents,
            intent_sources={i: sources[i] for i in final_intents},
            mapping_status=MappingStatus.MAPPED,
            retrieval_hits=retrieval_hits,
        )


if __name__ == "__main__":
    print("Mapping v2 模块加载成功（三路融合 + ABSTAIN 机制）")
