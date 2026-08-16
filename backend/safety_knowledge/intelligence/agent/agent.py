"""情报智能体 v3 —— 主编排（9 层管线）

```
1. Source & Provenance → 2. Normalize+Dedup/Cluster → 3. Analyzer
→ 4. Mapping v2（三路+ABSTAIN）→ 5. Novelty v2 → 6. Priority P0/P1/P2
→ 7. Candidate Node Builder → 8. Review → 9. Trusted Integration
```
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from safety_knowledge.intelligence.agent.source_layer import ProvenanceFetcher, RawIncidentRecord
from safety_knowledge.intelligence.agent.clusterer import IncidentClusterer
from safety_knowledge.intelligence.agent.analyzer import IncidentAnalyzer, AnalysisResult
from safety_knowledge.intelligence.agent.mapping_v2 import SafetyMapper, MappingResult
from safety_knowledge.intelligence.agent.novelty_engine import NoveltyEngine, NoveltyResult
from safety_knowledge.intelligence.agent.prioritizer import ReviewPrioritizer, PriorityResult
from safety_knowledge.intelligence.agent.node_builder import CandidateNodeBuilder
from safety_knowledge.intelligence.agent.integrator import ReviewBoard, TrustedIntegrator, ConflictReport
from safety_knowledge.intelligence.agent.reporter import IntegrationReporter
from safety_knowledge.intelligence.models import (
    CandidateRiskNode,
    IncidentCluster,
    MappingStatus,
    ReviewPriority,
)


class IncidentIntelligenceAgentV3:
    """9 层情报收集智能体。"""

    def __init__(self, trusted_nodes: list[dict], work_dir: Path, embedder=None) -> None:
        self._trusted = trusted_nodes
        self._work_dir = work_dir
        self._embedder = embedder  # BGE embedder（由运行器注入）

        # 各层实例
        self.fetcher = ProvenanceFetcher()
        self.clusterer = IncidentClusterer()
        self.analyzer = IncidentAnalyzer()
        self.mapper = SafetyMapper(trusted_nodes)
        self.novelty = NoveltyEngine(trusted_nodes)
        self.prioritizer = ReviewPrioritizer()
        self.node_builder = CandidateNodeBuilder(self._intent_evidence(trusted_nodes))
        self.board = ReviewBoard(work_dir / "review_decisions.jsonl")
        self.integrator = TrustedIntegrator(trusted_nodes)
        self.reporter = IntegrationReporter()

        self._embedder_injected = embedder is not None

    @staticmethod
    def _intent_evidence(trusted_nodes: list[dict]) -> dict[str, list[str]]:
        ev: dict[str, set[str]] = {}
        for n in trusted_nodes:
            action = n.get("canonical_action", "")
            if action:
                ev.setdefault(action, set()).update(n.get("required_evidence", []))
        return {k: sorted(v) for k, v in ev.items()}

    # ---------- 注入 embedder ----------

    def inject_embedder(self, embedder) -> None:
        self._embedder = embedder
        self._embedder_injected = True

    # ---------- 主管线 ----------

    def run(self, records: list[RawIncidentRecord], round_id: str = "auto") -> dict:
        """完整 9 层管线。"""
        # L1 → L2：聚类
        clusters = self.clusterer.cluster(records)

        # L3-L7：逐 cluster 分析
        analyses: list[AnalysisResult] = []
        mappings: list[MappingResult] = []
        novelties: list[NoveltyResult] = []
        priorities: list[ReviewPriority] = []
        nodes: list[CandidateRiskNode] = []

        for cluster in clusters:
            a = self.analyzer.analyze(cluster)
            m = self.mapper.map(a, embedder=self._embedder if self._embedder_injected else None)
            nv = self.novelty.evaluate(a,
                                       embedder=self._embedder if self._embedder_injected else None,
                                       mapping_status=m.mapping_status,
                                       mapped_intents=m.candidate_intents)
            pr = self.prioritizer.prioritize(a, nv, m.mapping_status, mapped_intents=m.candidate_intents)

            analyses.append(a)
            mappings.append(m)
            novelties.append(nv)
            priorities.append(pr.priority)

            # L7：生成候选节点（所有 cluster 都生成，P2 也保留记录；审核阶段再处理）
            node = self.node_builder.build(a, m, nv, pr.priority, len(nodes) + 1)
            # 注入向量
            if self._embedder_injected and not node.vector:
                vec, _ = self._embedder.encode(
                    f"{node.title} {node.semantic_description} 动作:{node.canonical_action} "
                    f"条件:{' '.join(node.conditions)} 证据:{' '.join(node.required_evidence)}"
                )
                node.vector = vec
            nodes.append(node)

        # L9：冲突检查（全部候选）
        conflict_reports = [self.integrator.check_conflict(n) for n in nodes]

        # I4：报告
        report_md = self.reporter.generate(
            round_id=round_id,
            raw_count=len(records),
            clusters=clusters,
            analyses=analyses,
            mappings=mappings,
            novelties=novelties,
            priorities=priorities,
            nodes=nodes,
            trusted=self._trusted,
            conflict_reports=conflict_reports,
        )

        # 持久化
        self._persist(clusters, analyses, mappings, novelties, priorities, nodes, report_md, round_id)

        return {
            "round_id": round_id,
            "raw_count": len(records),
            "cluster_count": len(clusters),
            "node_count": len(nodes),
            "clusters": clusters,
            "analyses": analyses,
            "mappings": mappings,
            "novelties": novelties,
            "priorities": priorities,
            "nodes": nodes,
            "conflict_reports": conflict_reports,
            "report_md": report_md,
        }

    # ---------- 持久化 ----------

    def _persist(self, clusters, analyses, mappings, novelties, priorities, nodes, report_md, round_id) -> None:
        self._work_dir.mkdir(parents=True, exist_ok=True)

        # 候选节点（KnowledgeNode v2 格式）
        node_path = self._work_dir / f"candidate_nodes_{round_id}.jsonl"
        node_path.write_text("\n".join(json.dumps(n.to_knowledge_node(), ensure_ascii=False) for n in nodes),
                             encoding="utf-8")

        # 分析明细
        detail_path = self._work_dir / f"analysis_{round_id}.json"
        details = []
        for a, m, nv, pr, n in zip(analyses, mappings, novelties, priorities, nodes):
            details.append({
                "cluster_id": a.cluster_id,
                "subject": a.subject,
                "component_family": a.component_family,
                "component_sub": a.component_sub,
                "capability_domain": a.capability_domain,
                "failure_modes": [x.value for x in a.failure_modes],
                "operating_conditions": [x.value for x in a.operating_conditions],
                "consequences": [x.value for x in a.consequences],
                "severity": a.severity,
                "mapping_status": m.mapping_status.value,
                "candidate_intents": m.candidate_intents,
                "abstain_reason": m.abstain_reason,
                "ontology_miss": m.ontology_miss,
                "novelty": nv.label.value,
                "novelty_score": nv.score,
                "priority": pr.value,
                "provenance": a.provenance,
                "node_id": n.node_id,
            })
        detail_path.write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")

        # 报告
        (self._work_dir / f"integration_report_{round_id}.md").write_text(report_md, encoding="utf-8")

    def close(self) -> None:
        self.fetcher.close()


if __name__ == "__main__":
    print("情报智能体 v3 主编排加载成功（9 层管线）")
