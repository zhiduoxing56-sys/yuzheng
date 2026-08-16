"""情报智能体 v3 —— Layer 7: Candidate Node Builder

职责：AnalyzedIncident → CandidateRiskNode（KnowledgeNode v2 Schema / L5 / PENDING_REVIEW）
  - 全部字段可追溯到 provenance
  - ABSTAIN 节点：canonical_action=""，metadata 标记本体覆盖缺口
  - 向量由 pipeline 注入 embedder 后计算
"""
from __future__ import annotations

import re
import sys

from safety_knowledge.ontology.node_schema_v2 import build_node_id  # noqa: E402
from safety_knowledge.intelligence.agent.analyzer import AnalysisResult
from safety_knowledge.intelligence.agent.novelty_engine import NoveltyResult
from safety_knowledge.intelligence.models import CandidateRiskNode, MappingStatus, ReviewPriority
from safety_knowledge.intelligence.agent.mapping_v2 import MappingResult


class CandidateNodeBuilder:
    """Layer 7 实现。"""

    def __init__(self, intent_evidence: dict[str, list[str]] | None = None) -> None:
        # 意图 → 证据（从 Trusted 知识库推导，供候选节点参考）
        self._intent_evidence = intent_evidence or {}

    def build(
        self,
        a: AnalysisResult,
        mapping: MappingResult,
        novelty: NoveltyResult,
        priority: ReviewPriority,
        seq: int,
    ) -> CandidateRiskNode:
        semantic_key = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "", a.component_family)[:8] or "incident"
        node_id = build_node_id("候选风险", semantic_key, seq)

        # 标题与描述（含全部结构化信息 + 追溯）
        fm_str = ",".join(m.value for m in a.failure_modes) or "UNKNOWN"
        cons_str = ",".join(c.value for c in a.consequences) or "UNKNOWN"
        cond_str = ",".join(c.value for c in a.operating_conditions) or "UNKNOWN"
        intent_str = ",".join(mapping.candidate_intents) if mapping.mapping_status == MappingStatus.MAPPED else "UNMAPPED"
        title = f"候选: {a.component_family} {a.component_sub} | {fm_str} | {cons_str}"
        description = (
            f"候选风险知识（源自事故情报）：{a.subject}。"
            f"部件 {a.component_family}({a.component_sub or '-'}) "
            f"失效模式:{fm_str} 运行条件:{cond_str} 后果:{cons_str} "
            f"危害等级:{a.severity_label} 能力域:{a.capability_domain} "
            f"意图:{intent_str} 新颖性:{novelty.label.value} "
            f"来源:{a.corroboration_count}条记录(权威:{a.source_authority.value}) "
            f"官方确认:{a.official_confirmed}"
        )

        # 主意图证据（若有映射，从知识库推导参考证据）
        main_intent = mapping.candidate_intents[0] if mapping.candidate_intents else ""
        evidence = list(self._intent_evidence.get(main_intent, [])) if main_intent else []

        # 来源（provenance 中源标识去重）
        source_ids = sorted({p.split("@")[0] for p in a.provenance}) if a.provenance else ["INTEL"]

        metadata = {
            "cluster_id": a.cluster_id,
            "subject": a.subject,
            "component_family": a.component_family,
            "component_sub": a.component_sub,
            "capability_domain": a.capability_domain,
            "failure_modes": [m.value for m in a.failure_modes],
            "operating_conditions": [c.value for c in a.operating_conditions],
            "consequences": [c.value for c in a.consequences],
            "severity": a.severity,
            "severity_label": a.severity_label,
            "source_authority": a.source_authority.value,
            "official_confirmed": a.official_confirmed,
            "corroboration_count": a.corroboration_count,
            "mapping_status": mapping.mapping_status.value,
            "candidate_intents": mapping.candidate_intents,
            "intent_sources": mapping.intent_sources,
            "ontology_miss": mapping.ontology_miss,
            "abstain_reason": mapping.abstain_reason,
            "novelty_label": novelty.label.value,
            "novelty_score": novelty.score,
            "novelty_reasons": novelty.reasons,
            "review_priority": priority.value,
            "provenance": a.provenance,
            "evidence_candidates": evidence,
            "review_status": "PENDING_REVIEW",
            "analysis_version": "v3.0",
        }

        return CandidateRiskNode(
            node_id=node_id,
            title=title[:80],
            semantic_description=description,
            canonical_action=main_intent,
            conditions=["VEHICLE_MOVING"] if main_intent else [],
            required_evidence=evidence,
            optional_evidence=[],
            source="+".join(source_ids),
            metadata=metadata,
        )
