"""I1+I2: 全量分析跑批（6,882 Cluster 100%）+ 投诉早期风险挖掘

I1: 全量 Analyzer + VCRelevance + CoverageImpact 统计
I2: 投诉 Risk Pattern 聚合——UNINTENDED_ACTIVATION/INTERMITTENT_FAILURE 等
    重复模式 × (车型/部件/时间/严重后果/是否已有 Recall)
    频度仅用于情报审核，不进入 CBN
"""
from __future__ import annotations

import json
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from safety_knowledge.intelligence.agent.clusterer import IncidentClusterer
from safety_knowledge.intelligence.agent.analyzer import IncidentAnalyzer
from safety_knowledge.intelligence.agent.relevance import voice_control_relevance
from safety_knowledge.intelligence.agent.source_layer import RawIncidentRecord, ProvenanceFetcher

LAKE = ROOT / "data" / "safety_intelligence"
OUT = LAKE / "analysis_full"


def load_lake() -> list[dict]:
    records = []
    for f in sorted((LAKE / "raw").rglob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                pass
    return records


def to_incident(u: dict) -> RawIncidentRecord:
    return RawIncidentRecord(
        record_id=u["record_id"], source_id=u["source_id"],
        source_type=None, retrieved_at=u["retrieved_at"], url=u["source_url"],
        raw_title=u["title"], raw_content=u["raw_text"],
        content_hash=u["content_hash"], parser_version=u["parser_version"],
        official_confirmed=u["official_confirmed"], raw_data=u.get("extra", {}), extra={},
    )


def main() -> int:
    raw = load_lake()
    print(f"Raw Lake: {len(raw)}")

    # 跨源去重
    seen = set()
    uniq = []
    for r in raw:
        if r["content_hash"] in seen:
            continue
        seen.add(r["content_hash"])
        uniq.append(r)
    print(f"去重: {len(uniq)}")

    records = [to_incident(u) for u in uniq]
    clusterer = IncidentClusterer()
    clusters = clusterer.cluster(records)
    print(f"Cluster: {len(clusters)}")

    # ---------- I1: 全量分析 ----------
    analyzer = IncidentAnalyzer()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for idx, cl in enumerate(clusters):
        try:
            a = analyzer.analyze(cl)
            # VCRelevance（用 ontology 意图）
            rel = voice_control_relevance(a.component_family, a.component_sub, a.ontology_intents)
            rows.append({
                "cluster_id": a.cluster_id,
                "source_ids": sorted({p.split("@")[0] for p in a.provenance}),
                "component_family": a.component_family,
                "component_sub": a.component_sub[:40],
                "capability_domain": a.capability_domain,
                "failure_modes": [m.value for m in a.failure_modes],
                "operating_conditions": [c.value for c in a.operating_conditions],
                "consequences": [c.value for c in a.consequences],
                "severity": a.severity,
                "severity_label": a.severity_label,
                "voice_control_relevance": rel,
                "subject": a.subject[:60],
                "corroboration": a.corroboration_count,
                "official": a.official_confirmed,
            })
        except Exception as e:
            print(f"err {cl.cluster_id}: {e}")
        if (idx + 1) % 2000 == 0:
            print(f"  分析进度: {idx + 1}/{len(clusters)}")

    print(f"全量分析完成: {len(rows)}/{len(clusters)} (Coverage {len(rows) / len(clusters):.1%})")
    with (OUT / "analyzed_clusters_full.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # ---------- 统计 ----------
    fm_all = Counter()
    cons_all = Counter()
    dom_all = Counter()
    sev_all = Counter()
    rel_all = Counter()
    for r in rows:
        for fm in r["failure_modes"]:
            fm_all[fm] += 1
        for c in r["consequences"]:
            cons_all[c] += 1
        dom_all[r["capability_domain"]] += 1
        sev_all[r["severity"]] += 1
        rel_all[r["voice_control_relevance"]] += 1

    fm_total = sum(fm_all.values())
    unknown_rate = fm_all.get("UNKNOWN", 0) / fm_total if fm_total else 0

    print("\n" + "=" * 60)
    print("I1 全量统计")
    print("=" * 60)
    print(f"FM 分布: {dict(fm_all.most_common(8))}")
    print(f"FM UNKNOWN 率: {unknown_rate:.1%}（基线，I6 专项）")
    print(f"CONS Top: {dict(cons_all.most_common(5))}")
    print(f"域分布: {dict(dom_all)}")
    print(f"Severity: {dict(sev_all)}")
    print(f"VCRelevance: {dict(rel_all)}")

    # ---------- I2: 投诉早期风险挖掘 ----------
    print("\n" + "=" * 60)
    print("I2 投诉早期风险挖掘")
    print("=" * 60)
    # 关注：UNINTENDED_ACTIVATION / INTERMITTENT_FAILURE / FAIL_TO_ACTIVATE
    EARLY_FM = {"UNINTENDED_ACTIVATION", "INTERMITTENT_FAILURE", "FAIL_TO_ACTIVATE",
                "UNCOMMANDED_MOVEMENT", "LOSS_OF_FUNCTION"}
    complaint_rows = [r for r in rows if "US-NHTSA-CSI" in r["source_ids"]]
    early = [r for r in complaint_rows if any(fm in EARLY_FM for fm in r["failure_modes"])]
    print(f"投诉行: {len(complaint_rows)} | 早期风险模式: {len(early)}")

    # 模式聚合：component_family × failure_mode
    pattern = Counter()
    for r in early:
        for fm in r["failure_modes"]:
            if fm in EARLY_FM:
                pattern[(r["component_family"], fm)] += 1
    print("\n早期风险模式 Top（component × FM）:")
    for (fam, fm), cnt in pattern.most_common(15):
        print(f"  {cnt:4d}  {fam[:30]:32s} {fm}")

    # 严重后果 + 是否已有对应召回
    serious = [r for r in early if r["severity"] <= 2]
    print(f"\n严重后果（SEV<=2）早期投诉: {len(serious)}")
    # 对照：同一 component_family 是否已有官方召回（RCL）
    rcl_families = {r["component_family"] for r in rows if "US-NHTSA-RCL" in r["source_ids"]}
    no_recall = [r for r in early if r["component_family"] not in rcl_families]
    print(f"无对应召回（潜在未成形风险）: {len(no_recall)}")
    for r in no_recall[:10]:
        print(f"  {r['component_family'][:35]:38s} {r['failure_modes'][:2]} | {r['subject'][:40]}")

    # ---------- 报告 ----------
    buf = io.StringIO()
    w = buf.write
    w("# I 阶段全量分析报告\n\n")
    w(f"- Raw: {len(raw)} | 去重: {len(uniq)} | Cluster: {len(clusters)} | 分析: {len(rows)}（Coverage {len(rows)/len(clusters):.1%}）\n")
    w(f"- FM UNKNOWN 基线: {unknown_rate:.1%}\n\n")
    w("## 全量统计\n\n")
    w("| 维度 | 分布 |\n|---|---|\n")
    w(f"| FM Top | {dict(fm_all.most_common(6))} |\n")
    w(f"| CONS Top | {dict(cons_all.most_common(5))} |\n")
    w(f"| 域 | {dict(dom_all)} |\n")
    w(f"| Severity | {dict(sev_all)} |\n")
    w(f"| VCRelevance | {dict(rel_all)} |\n\n")
    w("## 投诉早期风险模式（Top 15）\n\n")
    for (fam, fm), cnt in pattern.most_common(15):
        w(f"- {cnt} × {fam} | {fm}\n")
    w("\n## 无对应召回的早期风险（Top 10）\n\n")
    for r in no_recall[:10]:
        w(f"- {r['component_family']} | {r['failure_modes'][:2]} | {r['subject'][:40]}\n")
    (LAKE / "digests" / "I阶段全量分析报告.md").write_text(buf.getvalue(), encoding="utf-8")
    print(f"\n已保存: {OUT}/ + digests/I阶段全量分析报告.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
