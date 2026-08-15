"""E1: Frozen Intelligence Test 正式评估

评估（规则冻结，不改动）：
  - Triage P/R/F1（IRRELEVANT vs 其他）
  - Novelty P/R/F1（重点 NOVEL Precision）
  - Macro-F1（四分类）
门槛对照：Frozen Triage F1 >= 0.95 | Novel Precision >= 0.85 | Novel Recall >= 0.80
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.vector.embedding import LocalSentenceTransformerEmbeddingService  # noqa: E402
from safety_knowledge.intelligence.agent.agent import IncidentIntelligenceAgentV3  # noqa: E402
from safety_knowledge.intelligence.agent.source_layer import ProvenanceFetcher  # noqa: E402


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def compute_prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 4), round(r, 4), round(f1, 4)


def main() -> int:
    trusted = load_jsonl(ROOT / "data" / "knowledge_nodes_v4.jsonl")
    frozen = json.loads((ROOT / "data" / "intelligence_agent_v3" / "frozen_intelligence_test_v1.json")
                        .read_text(encoding="utf-8"))
    cases = frozen["cases"]
    print(f"Frozen Test Set: {len(cases)} 条（KNOWN 9 / PARTIAL 14 / NOVEL 11 / IRRELEVANT 19）")

    embedder = LocalSentenceTransformerEmbeddingService(model_name="BAAI/bge-base-zh-v1.5", dimension=768)
    fetcher = ProvenanceFetcher()
    records = [fetcher.from_legacy(c) for c in cases]

    work_dir = ROOT / "data" / "intelligence_agent_v3" / "e1_eval"
    agent = IncidentIntelligenceAgentV3(trusted, work_dir, embedder=embedder)
    result = agent.run(records, round_id="e1_frozen")
    agent.close()

    # ---------- 按 cluster 对齐 ground truth ----------
    cluster_by_id = {c.cluster_id: c for c in result["clusters"]}
    gt_by_hash = {c["content"]: c["label"] for c in cases}  # 用 content 匹配
    gt_by_hash2 = {}
    for c in cases:
        gt_by_hash2[c["content"][:80]] = c["label"]

    rows = []
    for a, m, nv, pr, n in zip(result["analyses"], result["mappings"], result["novelties"],
                                result["priorities"], result["nodes"]):
        cluster = cluster_by_id.get(a.cluster_id)
        if cluster is None:
            continue
        # ground truth：通过任一 record 的 content 匹配
        gt = None
        for rec in cluster.records:
            for content, label in gt_by_hash.items():
                if rec.raw_content == content:
                    gt = label
                    break
            if gt:
                break
        if gt is None:
            for rec in cluster.records:
                for c, label in gt_by_hash2.items():
                    if rec.raw_content[:80] == c:
                        gt = label
                        break
                if gt:
                    break
        rows.append({
            "cluster_id": a.cluster_id, "component": a.component_family,
            "gt": gt or "UNKNOWN", "novelty": nv.label.value, "mapped": m.mapping_status.value,
            "intents": m.candidate_intents, "priority": pr.value,
        })

    matched = [r for r in rows if r["gt"] != "UNKNOWN"]
    print(f"对齐成功: {len(matched)}/{len(rows)}")

    # ---------- 1. Triage：IRRELEVANT vs 其他 ----------
    tp = sum(1 for r in matched if r["gt"] != "IRRELEVANT" and r["novelty"] != "NOVEL_IRRELEVANT_PLACEHOLDER")
    # 智能体相关判定：MAPPED 或 P0/P1（非 P2 归档）
    tp = sum(1 for r in matched if r["gt"] != "IRRELEVANT" and r["priority"] in ("P0", "P1"))
    fp = sum(1 for r in matched if r["gt"] == "IRRELEVANT" and r["priority"] in ("P0", "P1"))
    fn = sum(1 for r in matched if r["gt"] != "IRRELEVANT" and r["priority"] == "P2")
    tn = sum(1 for r in matched if r["gt"] == "IRRELEVANT" and r["priority"] == "P2")
    triage_p, triage_r, triage_f1 = compute_prf(tp, fp, fn)

    # ---------- 2. Novelty 四分类 ----------
    labels = ["KNOWN", "PARTIAL_NOVEL", "NOVEL", "IRRELEVANT"]
    per_class = {}
    for lab in labels:
        tpp = sum(1 for r in matched if r["gt"] == lab and r["novelty"] == lab)
        fpp = sum(1 for r in matched if r["gt"] != lab and r["novelty"] == lab)
        fnn = sum(1 for r in matched if r["gt"] == lab and r["novelty"] != lab)
        per_class[lab] = compute_prf(tpp, fpp, fnn)

    macro_f1 = round(sum(v[2] for v in per_class.values()) / len(labels), 4)

    # NOVEL 重点
    novel_p, novel_r, novel_f1 = per_class["NOVEL"]

    # ---------- 门槛对照 ----------
    gates = {
        "Frozen Triage F1 >= 0.95": triage_f1,
        "Novel Precision >= 0.85": novel_p,
        "Novel Recall >= 0.80": novel_r,
    }

    print("\n" + "=" * 72)
    print("E1 Frozen Test 正式评估")
    print("=" * 72)
    print(f"Triage: Precision={triage_p:.4f} Recall={triage_r:.4f} F1={triage_f1:.4f} (TP{tp} FP{fp} FN{fn} TN{tn})")
    print(f"Novelty per-class:")
    for lab in labels:
        print(f"  {lab:15s} P={per_class[lab][0]:.4f} R={per_class[lab][1]:.4f} F1={per_class[lab][2]:.4f}")
    print(f"Macro-F1: {macro_f1}")
    print(f"\n门槛对照:")
    for gate, val in gates.items():
        passed = val >= 0.95 if "Triage" in gate else (val >= 0.85 if "Precision" in gate else val >= 0.80)
        print(f"  {'PASS' if passed else 'FAIL'} {gate}: {val:.4f}")

    print("\n逐条明细（GT vs 判定 不一致的）：")
    for r in matched:
        if r["gt"] != r["novelty"]:
            print(f"  X {r['cluster_id']} {r['component'][:30]} | GT={r['gt']} | 判定={r['novelty']} | mapped={r['mapped']} {r['intents'][:2]}")

    out = ROOT / "data" / "intelligence_agent_v3" / "e1_eval" / "e1_results.json"
    out.write_text(json.dumps({
        "triage": {"precision": triage_p, "recall": triage_r, "f1": triage_f1,
                   "tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "novelty": per_class, "macro_f1": macro_f1,
        "gates": {k: v for k, v in gates.items()},
        "rows": matched,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已保存: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
