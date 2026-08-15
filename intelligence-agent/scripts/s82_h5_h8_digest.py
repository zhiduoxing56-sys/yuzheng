"""H5+H8: 跨源 Normalize/Dedup/Cluster 跑批 + Safety Intelligence Digest

对 Raw Lake（7638 条）：
  1. 跨源去重（content_hash）
  2. IncidentCluster 聚类（component_family 分桶 + 主题 Jaccard）
  3. Analyzer 风险模式提取（Component/FailureMode/Consequence/Severity）
  4. 生成 Safety Intelligence Digest 报告
analysis_version = v3.8b（Raw 永久保留，后续可重跑）
"""
from __future__ import annotations

import json
import io
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from safety_knowledge.intelligence.agent.clusterer import IncidentClusterer
from safety_knowledge.intelligence.agent.analyzer import IncidentAnalyzer
from safety_knowledge.intelligence.agent.source_layer import ProvenanceFetcher, RawIncidentRecord

LAKE = ROOT / "data" / "safety_intelligence"


def load_lake() -> list[dict]:
    records = []
    for f in sorted((LAKE / "raw").rglob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except Exception:
                pass  # 容错：跳过损坏行（raw 源文件保留）
    return records


def main() -> int:
    raw = load_lake()
    print(f"Raw Lake 总量: {len(raw)} 条")
    by_src = Counter(r["source_id"] for r in raw)
    print(f"来源分布: {dict(by_src)}")

    # 跨源去重
    seen = set()
    uniq = []
    for r in raw:
        h = r["content_hash"]
        if h in seen:
            continue
        seen.add(h)
        uniq.append(r)
    print(f"去重后: {len(uniq)}（去重率 {1 - len(uniq) / len(raw):.1%}）")

    # 转 RawIncidentRecord（复用 clusterer/analyzer）
    fetcher = ProvenanceFetcher()
    records = []
    for u in uniq:
        rec = RawIncidentRecord(
            record_id=u["record_id"], source_id=u["source_id"],
            source_type=fetcher.SOURCE_META.get(u["source_id"], {"type": None}).get("type"),
            retrieved_at=u["retrieved_at"], url=u["source_url"],
            raw_title=u["title"], raw_content=u["raw_text"],
            content_hash=u["content_hash"], parser_version=u["parser_version"],
            official_confirmed=u["official_confirmed"], raw_data=u.get("extra", {}),
            extra={},
        )
        # from_legacy 兼容：直接构造（source_type 类型需枚举——简化处理）
        records.append(rec)

    # 聚类
    clusterer = IncidentClusterer()
    clusters = clusterer.cluster(records)
    print(f"IncidentCluster: {len(clusters)}")

    # 分析（抽样 500 条做风险模式统计，全量 analyzer 可后续跑批）
    analyzer = IncidentAnalyzer()
    analyzed = []
    sample = clusters[:800]
    for cl in sample:
        try:
            a = analyzer.analyze(cl)
            analyzed.append({
                "cluster_id": a.cluster_id,
                "component_family": a.component_family,
                "capability_domain": a.capability_domain,
                "failure_modes": [m.value for m in a.failure_modes],
                "consequences": [c.value for c in a.consequences],
                "severity": a.severity,
                "subject": a.subject[:50],
            })
        except Exception as e:
            print(f"analyze error {cl.cluster_id}: {e}")

    # ---------- Digest ----------
    fm_all = Counter()
    cons_all = Counter()
    dom_all = Counter()
    sev_all = Counter()
    for a in analyzed:
        for fm in a["failure_modes"]:
            fm_all[fm] += 1
        for c in a["consequences"]:
            cons_all[c] += 1
        dom_all[a["capability_domain"]] += 1
        sev_all[a["severity"]] += 1

    # 高风险候选（SEV<=2 且 有车控域）
    high_sev = [a for a in analyzed if a["severity"] <= 2 and a["capability_domain"] in
                ("灯光", "行驶控制", "泊车驻车", "视野", "网络安全")]
    print(f"\n高风险候选: {len(high_sev)}")

    buf = io.StringIO()
    w = buf.write
    w("# Safety Intelligence Digest（H 阶段第一轮）\n\n")
    w(f"- 生成时间：2026-08-15 | analysis_version = v3.8b\n")
    w(f"- Raw Lake 总量：**{len(raw)} 条**（来源分布：{dict(by_src)}）\n")
    w(f"- 去重后：{len(uniq)}（去重率 {1 - len(uniq) / len(raw):.1%}）\n")
    w(f"- IncidentCluster：{len(clusters)}（抽样分析 {len(analyzed)}）\n\n")

    w("## 风险模式分布（抽样）\n\n")
    w("### 失效模式 Top\n\n")
    for k, v in fm_all.most_common(10):
        w(f"- {k}: {v}\n")
    w("\n### 后果 Top\n\n")
    for k, v in cons_all.most_common(10):
        w(f"- {k}: {v}\n")
    w("\n### 能力域分布\n\n")
    for k, v in dom_all.most_common():
        w(f"- {k}: {v}\n")
    w("\n### 危害等级\n\n")
    for k, v in sorted(sev_all.items()):
        w(f"- SEV{k}: {v}\n")

    w("\n## 高优先级候选（SEV<=2 且车控相关，抽样）\n\n")
    for a in high_sev[:20]:
        w(f"- {a['cluster_id']} {a['component_family'][:30]} | {a['failure_modes'][:2]} | {a['subject'][:40]}\n")

    w("\n## 知识库覆盖缺口线索（新组件家族）\n\n")
    known_families = set()
    for cl in clusters:
        known_families.add(cl.component_family)
    for fam in sorted(known_families)[:30]:
        w(f"- {fam}\n")

    digest_path = LAKE / "digests" / "digest_2026-08-15.md"
    digest_path.parent.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(buf.getvalue(), encoding="utf-8")

    print("\n" + "=" * 60)
    print("Safety Intelligence Digest 摘要")
    print("=" * 60)
    print(f"Raw: {len(raw)} | 去重: {len(uniq)} | Cluster: {len(clusters)}")
    print(f"抽样分析: {len(analyzed)} | 高风险候选: {len(high_sev)}")
    print(f"FM Top: {dict(fm_all.most_common(5))}")
    print(f"CONS Top: {dict(cons_all.most_common(5))}")
    print(f"已保存: {digest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
