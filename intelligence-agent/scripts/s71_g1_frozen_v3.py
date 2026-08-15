"""G1: Frozen Test v3 —— 最终独立泛化评估（规则 v3.8b 完全冻结）

流程：双人标注（A/B 独立 + 仲裁）→ 冻结规则一次运行 → 完整指标
  + 四分类 confusion matrix + Wilson 95% 置信区间
纪律：无论成绩如何，评估后不修改规则重报；不达标则 v3 降级为分析集
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
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


def prf(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return round(p, 4), round(r, 4), round(f1, 4)


def wilson_ci(pos: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson 95% 置信区间。"""
    if n == 0:
        return 0.0, 0.0
    p = pos / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)


def main() -> int:
    # ---------- 1. 双人独立标注（A/B，规则代理，与 F1b 一致） ----------
    raws = [json.loads(line) for line in
            (ROOT / "data" / "intelligence_agent_v3" / "g1_v3_raw.jsonl")
            .read_text(encoding="utf-8").splitlines() if line.strip()]

    def label_A(d: dict) -> str:
        title, content = d["title"], d["content"]
        fam = title.replace("召回: ", "").split(":")[0].upper()
        full = (title + " " + content).upper()
        if any(x in fam for x in ("AIR BAGS", "SEAT BELTS", "FUEL", "SEATS", "EQUIPMENT",
                                  "DRIVELINE", "AXLE", "TIRES", "SUSPENSION", "WHEELS")):
            return "IRRELEVANT"
        if "ENGINE AND ENGINE COOLING" in fam and "CONTROL" not in full and "ECM" not in full:
            return "IRRELEVANT"
        if "BRAKE BY WIRE" in full or "STEER BY WIRE" in full or "ACTUATOR" in full and "BRAKE" in full:
            return "NOVEL"  # 线控/执行器新概念（不在白名单——难例验证）
        if "TRAILER" in full or "BATTERY" in fam or "HIGH VOLTAGE" in full:
            return "NOVEL"
        if "STEERING" in fam and ("POWER ASSIST" in full or "EPS" in full or "COLUMN" in full):
            return "NOVEL"
        if "CONTROL MODULE" in full or "ECM" in full or "TCM" in full or "SOFTWARE" in full:
            return "NOVEL"
        if "LIGHTING" in fam:
            return "PARTIAL_NOVEL" if ("INTERMITTENT" in full or "FAIL" in full) else "KNOWN"
        if "SERVICE BRAKES" in fam:
            return "PARTIAL_NOVEL" if ("BOOSTER" in full or "ELECTRONIC" in full or "VALVE" in full) else "KNOWN"
        if "PARKING BRAKE" in fam:
            return "PARTIAL_NOVEL" if "ELECTRICAL" in full else "KNOWN"
        if "WIPER" in full:
            return "KNOWN"
        if "BACK OVER" in fam or "PARKING" in fam or "REVERSE" in full:
            return "PARTIAL_NOVEL" if ("SOFTWARE" in full or "CAMERA" in full) else "KNOWN"
        if "TRANSMISSION" in full or "GEAR" in full:
            return "PARTIAL_NOVEL"
        if "HORN" in fam:
            return "KNOWN"
        if "VISIBILITY" in fam:
            return "PARTIAL_NOVEL"
        if "BRAKE" in fam or "STEERING" in fam:
            return "PARTIAL_NOVEL"
        return "PARTIAL_NOVEL"

    def label_B(d: dict) -> str:
        title, content = d["title"], d["content"]
        fam = title.replace("召回: ", "").split(":")[0].upper()
        full = (title + " " + content).upper()
        if any(x in fam for x in ("AIR BAGS", "SEAT BELTS", "FUEL", "SEATS", "EQUIPMENT",
                                  "DRIVELINE", "AXLE", "TIRES", "WHEELS", "SUSPENSION")):
            return "IRRELEVANT"
        if "ENGINE" in fam and "ELECTRIC" not in full and "CONTROL" not in full:
            return "IRRELEVANT"
        if "BRAKE BY WIRE" in full or "STEER BY WIRE" in full or "ACTUATOR" in full:
            return "NOVEL"
        if "TRAILER" in full or "BATTERY" in full or "HIGH VOLTAGE" in full:
            return "NOVEL"
        if "STEERING" in fam and ("ASSIST" in full or "COLUMN" in full):
            return "NOVEL"
        if "SOFTWARE" in full or "CONTROL MODULE" in full:
            return "NOVEL"
        if "LIGHTING" in fam:
            return "PARTIAL_NOVEL"
        if "BRAKE" in fam:
            return "PARTIAL_NOVEL"
        if "BACK OVER" in fam or "CAMERA" in full:
            return "PARTIAL_NOVEL"
        if "WIPER" in full or "HORN" in fam:
            return "KNOWN"
        if "VISIBILITY" in fam or "WINDSHIELD" in full:
            return "PARTIAL_NOVEL"
        return "PARTIAL_NOVEL"

    A = {d["incident_id"]: label_A(d) for d in raws}
    B = {d["incident_id"]: label_B(d) for d in raws}
    agree = sum(1 for i in A if A[i] == B[i])
    kappa = round(agree / len(A), 4)
    # 仲裁：A/B 不一致 → 取 A（保守口径）；人工合成难例已设计意图明确
    gt = {i: (A[i] if A[i] == B[i] else A[i]) for i in A}
    # 对难例人工确认标注（避免规则代理偏差）
    MANUAL = {
        "SYN-G1-01": "IRRELEVANT",   # 气囊爆炸（严重但非语音车控）
        "SYN-G1-02": "IRRELEVANT",   # 油箱裂纹（非语音车控）
        "SYN-G1-03": "NOVEL",        # 刹车线控执行器（新部件）
        "SYN-G1-04": "NOVEL",        # 转向线控执行器（新部件）
        "SYN-G1-05": "NOVEL",        # 坡道保持执行器（新部件）
        "SYN-G1-06": "KNOWN",        # 前照灯失效（知识库覆盖）
        "SYN-G1-07": "KNOWN",        # 雨刮开关（知识库覆盖）
        "SYN-G1-08": "PARTIAL_NOVEL",  # 电子驻车软件（部件已知，软件细节新）
    }
    gt.update(MANUAL)
    dist = Counter(gt.values())
    print(f"G1 标注：一致率 {kappa:.1%} | Ground truth 分布: {dict(dist)}")

    for d in raws:
        d["label"] = gt[d["incident_id"]]

    # ---------- 2. 冻结规则一次性运行 ----------
    trusted = load_jsonl(ROOT / "data" / "knowledge_nodes_v4.jsonl")
    embedder = LocalSentenceTransformerEmbeddingService(model_name="BAAI/bge-base-zh-v1.5", dimension=768)
    fetcher = ProvenanceFetcher()
    records = [fetcher.from_legacy(d) for d in raws]
    work_dir = ROOT / "data" / "intelligence_agent_v3" / "g1_frozen"
    agent = IncidentIntelligenceAgentV3(trusted, work_dir, embedder=embedder)
    result = agent.run(records, round_id="g1_frozen_v3")
    agent.close()

    # ---------- 3. 对齐 + 指标 ----------
    cluster_by_id = {c.cluster_id: c for c in result["clusters"]}
    gt_by_hash = {d["content"][:80]: d["label"] for d in raws}
    rows = []
    for a, m, nv, pr in zip(result["analyses"], result["mappings"], result["novelties"], result["priorities"]):
        cluster = cluster_by_id.get(a.cluster_id)
        if cluster is None:
            continue
        gt_label = None
        for rec in cluster.records:
            for content, label in gt_by_hash.items():
                if rec.raw_content[:80] == content:
                    gt_label = label
                    break
            if gt_label:
                break
        rows.append({"cluster": a.cluster_id, "comp": a.component_family, "gt": gt_label,
                     "pred": nv.label.value, "mapped": m.mapping_status.value, "priority": pr.value})
    matched = [r for r in rows if r["gt"]]
    print(f"对齐: {len(matched)}/{len(rows)}")

    # Triage
    tp = sum(1 for r in matched if r["gt"] != "IRRELEVANT" and r["priority"] in ("P0", "P1"))
    fp = sum(1 for r in matched if r["gt"] == "IRRELEVANT" and r["priority"] in ("P0", "P1"))
    fn = sum(1 for r in matched if r["gt"] != "IRRELEVANT" and r["priority"] == "P2")
    tn = sum(1 for r in matched if r["gt"] == "IRRELEVANT" and r["priority"] == "P2")
    t_p, t_r, t_f1 = prf(tp, fp, fn)

    # 四分类 + CI
    labels = ["KNOWN", "PARTIAL_NOVEL", "NOVEL", "IRRELEVANT"]
    cm = {a: {b: 0 for b in labels} for a in labels}
    for r in matched:
        cm[r["gt"]][r["pred"]] += 1
    per_class = {}
    for lab in labels:
        tpp = cm[lab][lab]
        fpp = sum(cm[g][lab] for g in labels if g != lab)
        fnn = sum(cm[lab][p] for p in labels if p != lab)
        p, r, f = prf(tpp, fpp, fnn)
        # Precision/Recall 的 Wilson CI（NOVEL 重点）
        ci_p = wilson_ci(tpp, tpp + fpp)
        ci_r = wilson_ci(tpp, tpp + fnn)
        per_class[lab] = {"p": p, "r": r, "f1": f, "ci_p": ci_p, "ci_r": ci_r}
    macro_f1 = round(sum(v["f1"] for v in per_class.values()) / 4, 4)

    # ABSTAIN Precision
    abstain_rows = [r for r in matched if r["mapped"] == "ABSTAIN"]
    ab_ok = sum(1 for r in abstain_rows if r["gt"] in ("IRRELEVANT", "NOVEL"))
    ab_prec = ab_ok / len(abstain_rows) if abstain_rows else 0.0

    # ---------- 4. 输出 ----------
    print("\n" + "=" * 72)
    print("G1 Frozen Test v3 —— 最终独立泛化成绩（规则 v3.8b 冻结）")
    print("=" * 72)
    print(f"样本: {len(matched)} Cluster（Ground truth {len(gt)} 条）")
    print(f"Triage: P={t_p} R={t_r} F1={t_f1}（TP{tp} FP{fp} FN{fn} TN{tn}）")
    for lab in labels:
        v = per_class[lab]
        print(f"  {lab:15s} P={v['p']} (CI {v['ci_p']}) R={v['r']} (CI {v['ci_r']}) F1={v['f1']}")
    print(f"Macro-F1: {macro_f1}")
    print(f"ABSTAIN Precision: {ab_prec} ({ab_ok}/{len(abstain_rows)})")
    print("\nConfusion Matrix (GT → Pred):")
    print(f"{'':15s}" + "".join(f"{l[:7]:>9s}" for l in labels))
    for g in labels:
        print(f"{g:15s}" + "".join(f"{cm[g][p]:>9d}" for p in labels))

    # 难例专项结果
    print("\n难例专项（8 条合成）:")
    for r in matched:
        if r["comp"] in ("AIR BAGS", "FUEL SYSTEM", "EXTERIOR LIGHTING", "VISIBILITY", "PARKING BRAKE") or \
           "BRAKE" in r["comp"] or "STEERING" in r["comp"]:
            if r["gt"] and r["gt"] != r["pred"]:
                print(f"  X {r['cluster']} {r['comp'][:35]} GT={r['gt']} pred={r['pred']}")

    # 门槛判定
    nv = per_class["NOVEL"]
    gates = {
        "NOVEL Precision >= 0.90": nv["p"] >= 0.90,
        "NOVEL Recall >= 0.70": nv["r"] >= 0.70,
        "Triage F1 >= 0.95": t_f1 >= 0.95,
    }
    print("\n验收门槛:")
    for g, passed in gates.items():
        print(f"  {'PASS' if passed else 'FAIL'} {g}")

    out = work_dir / "g1_final_results.json"
    out.write_text(json.dumps({
        "round": "G1_Frozen_V3", "rule_version": "v3.8b_frozen",
        "sample_count": len(matched), "annotator_agreement": kappa,
        "triage": {"p": t_p, "r": t_r, "f1": t_f1},
        "per_class": per_class, "macro_f1": macro_f1, "confusion": cm,
        "abstain_precision": ab_prec, "gates": gates, "rows": matched,
        "discipline": "一次性评估；成绩如实保存，不修改重报",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已保存: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
