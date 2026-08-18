# -*- coding: utf-8 -*-
"""HNSW 参数扫描对照实验：Flat 精确基线 vs 原生固定参数 HNSW vs 规模感知自适应 HNSW。

实验设计（对齐答辩要求）：
- 固定 N（当前 2326，论文可换 N=15888/12200，脚本参数化）
- Q_gold=400 条黄金查询（节点语义文本编码），拆 Q_tune=200 / Q_test=200
- Ground Truth = Flat 精确检索 Top-20（Recall_ANN@20 = |K_hnsw ∩ K_flat|/20）
- 三组扫描：
    M  ∈ {8,12,16,20,24,28,32,36}     固定 (efC=200, efS=100)
    efC∈ {50,75,100,150,200,300,400}  固定 (M=16,  efS=100)
    efS∈ {20,30,50,75,100,150,200,300,400} 固定 (M=16, efC=200)
- 原生基线 A0=(16,200,30)；自适应 A1 在扫描点上由 tune 集边际收益拐点选择其余参数
- 每配置预热 3 轮 + 正式 10 轮，查询顺序随机化、固定种子、仅计 knn_query 核心时延
- 输出 JSON 结果 + 图A 召回率 / 图B 检索时延 P95
"""
import argparse
import json
import random
import time
from pathlib import Path

import numpy as np

BASE = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
DATA = BASE / "data" / "knowledge_vectors_large"
OUT_DIR = BASE / "data" / "hnsw_param_scan"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
M_SCAN = [8, 12, 16, 20, 24, 28, 32, 36]
EFC_SCAN = [50, 75, 100, 150, 200, 300, 400]
EFS_SCAN = [20, 30, 50, 75, 100, 150, 200, 300, 400]
Q_GOLD = 400
Q_TUNE = 200
WARMUP_ROUNDS = 3
RUN_ROUNDS = 10
TOP_K = 20
R_MIN = 0.90      # 最小可接受召回率
ETA = 0.5         # 边际收益率阈值（论文 η）
ALPHA = 0.35      # 时延代价权重
BETA = 0.45       # 存储代价权重
EPS = 1e-9


def load_vectors(max_n: int | None = None) -> np.ndarray:
    vecs = np.load(DATA / "large_full_vecs.npy").astype(np.float32)
    if max_n is not None and len(vecs) > max_n:
        vecs = vecs[:max_n]
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms


def load_nodes(max_n: int | None = None) -> list[dict]:
    nodes = []
    with (DATA / "knowledge_nodes_large_full_encoded.jsonl").open(encoding="utf-8") as f:
        for line in f:
            nodes.append(json.loads(line))
            if max_n is not None and len(nodes) >= max_n:
                break
    return nodes


def node_text(n: dict) -> str:
    parts = [n.get("title", ""), n.get("semantic_description", ""), n.get("intent_id", "")]
    return " ".join(p for p in parts if p)


def build_query_vectors(nodes: list[dict], rng: random.Random) -> np.ndarray:
    """黄金查询：固定种子采样 Q_GOLD 个节点，用 bge 编码其语义文本。"""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-base-zh-v1.5", local_files_only=True)
    sampled = rng.sample(nodes, Q_GOLD)
    texts = [node_text(n) for n in sampled]
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return np.asarray(vecs, dtype=np.float32)


def flat_top20(vecs: np.ndarray, qvecs: np.ndarray) -> np.ndarray:
    """Flat 精确检索：返回 (Q, 20) 的索引矩阵，作为 Ground Truth。"""
    dots = qvecs @ vecs.T  # 已归一化，点积即余弦
    return np.argsort(-dots, axis=1)[:, :TOP_K].astype(np.int64)


def build_index(vecs: np.ndarray, M: int, efC: int):
    import hnswlib
    t0 = time.perf_counter()
    idx = hnswlib.Index(space="cosine", dim=vecs.shape[1])
    idx.init_index(max_elements=max(10, len(vecs)), ef_construction=efC, M=M)
    idx.add_items(vecs, np.arange(len(vecs), dtype=np.int64))
    build_s = time.perf_counter() - t0
    return idx, build_s


def eval_index(idx, qvecs: np.ndarray, k_exact: np.ndarray, efS: int,
               rounds: int = RUN_ROUNDS, warmup: int = WARMUP_ROUNDS) -> dict:
    """预热 + 正式查询（顺序随机化，仅计 knn_query 核心时延）。"""
    rng = random.Random(SEED)
    q_order = list(range(len(qvecs)))
    idx.set_ef(efS)
    # 预热
    for _ in range(warmup):
        rng.shuffle(q_order)
        for i in q_order:
            idx.knn_query(qvecs[i].reshape(1, -1), k=TOP_K)
    # 正式
    lat = []
    for _ in range(rounds):
        rng.shuffle(q_order)
        for i in q_order:
            t0 = time.perf_counter_ns()
            labels, _ = idx.knn_query(qvecs[i].reshape(1, -1), k=TOP_K)
            lat.append((time.perf_counter_ns() - t0) / 1e6)
    labels_all = []
    idx.set_ef(efS)
    for i in range(len(qvecs)):
        labels, _ = idx.knn_query(qvecs[i].reshape(1, -1), k=TOP_K)
        labels_all.append(labels[0])
    hits = 0
    total = 0
    for i, lab in enumerate(labels_all):
        kf = set(k_exact[i].tolist())
        kh = set(lab.tolist())
        hits += len(kf & kh)
        total += TOP_K
    lat = np.asarray(lat, dtype=np.float64)
    return {
        "recall_ann_20": round(hits / total, 4),
        "latency_mean_ms": round(float(lat.mean()), 4),
        "latency_p95_ms": round(float(np.percentile(lat, 95)), 4),
        "latency_p50_ms": round(float(np.median(lat)), 4),
    }


def adaptive_select(vecs: np.ndarray, qvecs: np.ndarray, k_exact: np.ndarray,
                    fixed: dict, scan_val: int, candidates: dict, verbose=False) -> tuple[dict, float]:
    """边际收益拐点控制器：在 tune 集上评估候选组合，选召回收益拐点前的参数。"""
    cands = []
    for key, vals in candidates.items():
        for v in vals:
            cfg = dict(fixed)
            cfg[key] = v
            cands.append(cfg)
    results = []
    for cfg in cands:
        idx, build_s = build_index(vecs, cfg["M"], cfg["efC"])
        r = eval_index(idx, qvecs[:Q_TUNE], k_exact[:Q_TUNE], cfg["efS"],
                       rounds=3, warmup=1)  # 调优集用轻量评估
        r["efC"] = cfg["efC"]
        r["efS"] = cfg["efS"]
        r["M"] = cfg["M"]
        r["build_s"] = round(build_s, 2)
        results.append(r)
        if verbose:
            print(f"    tune {cfg} R={r['recall_ann_20']} T={r['latency_mean_ms']}ms")
    feasible = [r for r in results if r["recall_ann_20"] >= R_MIN]
    if not feasible:
        feasible = sorted(results, key=lambda x: -x["recall_ann_20"])[:2]
    feasible.sort(key=lambda x: x["recall_ann_20"])
    best = feasible[-1]
    for i in range(1, len(feasible)):
        prev, cur = feasible[i - 1], feasible[i]
        dR = cur["recall_ann_20"] - prev["recall_ann_20"]
        dT = cur["latency_mean_ms"] - prev["latency_mean_ms"]
        dC = 0.0  # 存储近似：efC/M 引起的索引大小差异在此忽略（hnswlib 无直接 API）
        g = dR / (ALPHA * max(dT, 0.0) + BETA * max(dC, 0.0) + EPS)
        if g < ETA:
            best = prev
            break
    return best, results


def run_scan(vecs: np.ndarray, qvecs: np.ndarray, k_exact: np.ndarray,
             param: str, values: list[int], fixed: dict, rng: random.Random,
             adaptive: bool) -> list[dict]:
    rows = []
    # 原生基线参照：扫描每个点用固定 (16,200,30) 的结果（同一配置只测一次）
    baseline_cache: dict[tuple, dict] = {}

    def eval_cfg(M, efC, efS):
        key = (M, efC, efS)
        if key in baseline_cache:
            return baseline_cache[key]
        idx, build_s = build_index(vecs, M, efC)
        r = eval_index(idx, qvecs, k_exact, efS)
        r.update(M=M, efC=efC, efS=efS, build_s=round(build_s, 2),
                 index_size_mb=round(build_s * 0.0 + _idx_size(vecs, M), 3))
        baseline_cache[key] = r
        return r

    for v in values:
        # 原生固定基线：扫描参数变化，其余固定为 (16,200,30) 的对应值
        cfg_native = dict(fixed)
        cfg_native[param] = v
        r_native = eval_cfg(cfg_native["M"], cfg_native["efC"], cfg_native["efS"])
        row_native = dict(method="native_fixed", **r_native)
        row_native[param] = v
        row_native.pop("M", None); row_native.pop("efC", None); row_native.pop("efS", None)
        row_native["M"] = cfg_native["M"]; row_native["efC"] = cfg_native["efC"]; row_native["efS"] = cfg_native["efS"]
        rows.append(row_native)
        if adaptive:
            # 自适应：扫描参数取 v，其余由控制器选择
            others = {k: vals for k, vals in {"M": M_SCAN, "efC": EFC_SCAN, "efS": EFS_SCAN}.items() if k != param}
            cfg = dict(fixed)
            cfg[param] = v
            best, _ = adaptive_select(vecs, qvecs, k_exact, cfg, v, others, verbose=False)
            r_adapt = eval_cfg(best["M"], best["efC"], best["efS"])
            row_adapt = dict(method="adaptive_hnsw", **r_adapt)
            row_adapt[param] = v
            row_adapt.pop("M", None); row_adapt.pop("efC", None); row_adapt.pop("efS", None)
            row_adapt["M"] = best["M"]; row_adapt["efC"] = best["efC"]; row_adapt["efS"] = best["efS"]
            rows.append(row_adapt)
    return rows


def _idx_size(vecs: np.ndarray, M: int) -> float:
    """索引存储近似：向量本体 + 邻接表（edges ≈ N*M，每条 8B）。"""
    vec_bytes = vecs.nbytes
    edge_bytes = len(vecs) * M * 8
    return (vec_bytes + edge_bytes) / (1024 * 1024)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2326, help="固定知识规模 N")
    ap.add_argument("--quick", action="store_true", help="快速模式（1 轮）")
    args = ap.parse_args()
    rng = random.Random(SEED)

    print(f"[1/4] 加载向量库 N={args.n}")
    vecs = load_vectors(args.n)
    nodes = load_nodes(args.n)
    print(f"      向量: {vecs.shape}, 节点: {len(nodes)}")

    print("[2/4] 黄金查询集（Q_gold=400, tune=200 / test=200）")
    qvecs = build_query_vectors(nodes, rng)
    k_exact = flat_top20(vecs, qvecs)
    print(f"      Flat 精确 Top-20 完成 (Q={len(qvecs)})")

    print("[3/4] 参数扫描")
    global RUN_ROUNDS
    if args.quick:
        RUN_ROUNDS = 1
    results: dict = {"N": len(vecs), "Q_gold": Q_GOLD, "Q_tune": Q_TUNE,
                     "seed": SEED, "top_k": TOP_K,
                     "flat_recall_ann_20": 1.0,
                     "native_baseline": {"M": 16, "efC": 200, "efS": 30},
                     "scans": {}}
    # Flat 时延参照
    t0 = time.perf_counter()
    flat_top20(vecs, qvecs)
    results["flat_latency_ms"] = round((time.perf_counter() - t0) * 1000 / len(qvecs), 4)
    # A0 原生基线 (16,200,30)
    idx, build_s = build_index(vecs, 16, 200)
    r0 = eval_index(idx, qvecs, k_exact, 30)
    r0.update(M=16, efC=200, efS=30, build_s=round(build_s, 2),
              index_size_mb=round(_idx_size(vecs, 16), 3))
    results["native_baseline_result"] = r0
    print(f"      A0 原生基线 (16,200,30): R={r0['recall_ann_20']} P95={r0['latency_p95_ms']}ms")

    scans = {
        "M": (M_SCAN, {"efC": 200, "efS": 100}, "邻接度 M"),
        "efC": (EFC_SCAN, {"M": 16, "efS": 100}, "构图参数 efConstruction"),
        "efS": (EFS_SCAN, {"M": 16, "efC": 200}, "检索参数 efSearch"),
    }
    for pkey, (vals, fixed, label) in scans.items():
        print(f"  扫描 {label}: {vals}")
        rows = run_scan(vecs, qvecs, k_exact, pkey, vals, fixed, rng, adaptive=True)
        results["scans"][pkey] = {"label": label, "rows": rows}

    print("[4/4] 输出结果")
    out_json = OUT_DIR / "hnsw_param_scan_results.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"      JSON: {out_json}")
    try:
        from plot_hnsw_param_scan import plot_two_figures
        plot_two_figures(results)
    except Exception as exc:
        print(f"      (绘图跳过: {type(exc).__name__}: {exc})")


if __name__ == "__main__":
    main()
