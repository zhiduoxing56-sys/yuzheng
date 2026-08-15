"""情报智能体 v3 —— I4: 动态安全知识整合报告生成器

每轮采集自动生成可读报告（不是默默堆 JSON）：
  - 本轮抓取/去重/聚类统计
  - 高危相关、NOVEL/PARTIAL/KNOWN 分布
  - 新增能力域 / 候选意图 / 无法映射组件 / 候选新证据 / Trusted 覆盖缺口
  - P0 人工审核列表
  - 潜在冲突 / 重复知识
"""
from __future__ import annotations

import io
import sys
from collections import Counter
from pathlib import Path

from safety_knowledge.intelligence.agent.analyzer import AnalysisResult
from safety_knowledge.intelligence.agent.mapping_v2 import MappingResult
from safety_knowledge.intelligence.agent.novelty_engine import NoveltyResult
from safety_knowledge.intelligence.models import CandidateRiskNode, MappingStatus, ReviewPriority


class IntegrationReporter:
    """整合报告生成器。"""

    def generate(
        self,
        round_id: str,
        raw_count: int,
        clusters: list,
        analyses: list[AnalysisResult],
        mappings: list[MappingResult],
        novelties: list[NoveltyResult],
        priorities: list[ReviewPriority],
        nodes: list[CandidateRiskNode],
        trusted: list[dict],
        conflict_reports: list | None = None,
    ) -> str:
        buf = io.StringIO()
        w = buf.write

        w(f"# 动态安全知识整合报告（第 {round_id} 轮）\n\n")
        w(f"- 生成时间：2026-08-15\n")
        w(f"- Trusted 知识库：{len(trusted)} 节点\n\n")

        # ---------- 1. 采集统计 ----------
        w("## 1. 采集与聚合统计\n\n")
        w("| 指标 | 数量 |\n|---|---|\n")
        w(f"| 原始情报记录 | {raw_count} |\n")
        w(f"| 去重后 Cluster | {len(clusters)} |\n")
        w(f"| 去重压缩率 | {1 - len(clusters) / max(1, raw_count):.1%} |\n")
        w(f"| 进入分析 | {len(analyses)} |\n\n")

        # ---------- 2. 结构化分布 ----------
        w("## 2. 结构化分析分布\n\n")
        sev = Counter(a.severity_label for a in analyses)
        fm = Counter(m.value for a in analyses for m in a.failure_modes)
        cons = Counter(c.value for a in analyses for c in a.consequences)
        dom = Counter(a.capability_domain for a in analyses)
        w("### 危害等级\n\n")
        for k, v in sorted(sev.items()):
            w(f"- {k}: {v}\n")
        w("\n### 失效模式（Top）\n\n")
        for k, v in fm.most_common(8):
            w(f"- {k}: {v}\n")
        w("\n### 后果（Top）\n\n")
        for k, v in cons.most_common(8):
            w(f"- {k}: {v}\n")
        w("\n### 能力域分布\n\n")
        for k, v in dom.most_common():
            w(f"- {k}: {v}\n")

        # ---------- 3. Mapping / Novelty ----------
        w("\n## 3. 映射与新颖性\n\n")
        map_status = Counter(m.mapping_status.value for m in mappings)
        nov = Counter(n.label.value for n in novelties)
        w(f"### 映射状态\n\n")
        for k, v in map_status.items():
            w(f"- {k}: {v}\n")
        w("\n### 新颖性\n\n")
        for k, v in nov.items():
            w(f"- {k}: {v}\n")

        # 无法映射组件（ABSTAIN）
        abstain = [(a, m) for a, m in zip(analyses, mappings) if m.mapping_status == MappingStatus.ABSTAIN]
        if abstain:
            w("\n### 无法映射组件（本体覆盖缺口）\n\n")
            for a, m in abstain:
                w(f"- {a.component_family}:{a.component_sub or '-'}（{a.subject[:40]}）→ {m.abstain_reason}\n")

        # 候选新证据
        w("\n### 候选新证据（超出知识库意图证据并集）\n\n")
        kb_ev = set()
        for n in trusted:
            kb_ev.update(n.get("required_evidence", []))
        new_ev = set()
        for n in nodes:
            new_ev.update(n.required_evidence)
        extra = new_ev - kb_ev
        if extra:
            for e in sorted(extra):
                w(f"- {e}\n")
        else:
            w("- 无（候选证据全部来自知识库意图推导）\n")

        # ---------- 4. P0 审核列表 ----------
        w("\n## 4. P0 优先人工审核列表\n\n")
        p0 = [(n, p) for n, p in zip(nodes, priorities) if p == ReviewPriority.P0]
        if p0:
            w("| Node | 部件 | 意图 | 新颖性 | 危害 |\n|---|---|---|---|---|\n")
            for n, _ in p0:
                m = n.metadata
                w(f"| {n.node_id} | {m.get('component_family')}:{m.get('component_sub', '')} | {n.canonical_action or 'UNMAPPED'} | {m.get('novelty_label')} | {m.get('severity_label')} |\n")
        else:
            w("- 无\n")

        # ---------- 5. 冲突与覆盖缺口 ----------
        w("\n## 5. 冲突检查与知识覆盖缺口\n\n")
        if conflict_reports:
            for cr in conflict_reports:
                w(f"- **{cr.node_id}** [{cr.status}]：{cr.recommendation}\n")
        else:
            w("- 未执行冲突检查\n")

        return buf.getvalue()
