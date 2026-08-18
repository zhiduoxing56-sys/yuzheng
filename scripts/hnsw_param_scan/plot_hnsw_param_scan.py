# -*- coding: utf-8 -*-
"""图A 召回率 / 图B 检索时延 P95：原生固定 HNSW（斜线柱）vs 自适应 HNSW（实色柱）。
参照线：Flat 精确检索召回率=1.0（虚线）、Flat 时延（灰虚线）。模仿论文风格。"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
OUT_DIR = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\hnsw_param_scan")
FIG_DIR = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\docs\figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

HATCH = "///"   # 原生固定 HNSW 斜线
COLOR_NATIVE = "#9AA7B1"
COLOR_ADAPT = "#2E5A88"


def load() -> dict:
    return json.loads((OUT_DIR / "hnsw_param_scan_results.json").read_text(encoding="utf-8"))


def plot_two_figures(results: dict | None = None) -> None:
    if results is None:
        results = load()
    scans = results["scans"]
    group_titles = ["邻接度 M 扫描", "构图参数 efConstruction 扫描", "检索参数 efSearch 扫描"]

    # ---------- 图 A：召回率 ----------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
    for ax, (gkey, xlabel, gtitle) in zip(axes, [
            ("M", "邻接度 M", "邻接度 M 扫描"),
            ("efC", "ef Construction", "构图参数 efConstruction 扫描"),
            ("efS", "ef Search", "检索参数 efSearch 扫描")]):
        rows = scans[gkey]["rows"]
        native = [r for r in rows if r["method"] == "native_fixed"]
        adapt = [r for r in rows if r["method"] == "adaptive_hnsw"]
        xvals = [r[gkey] for r in native]
        r_nat = [r["recall_ann_20"] for r in native]
        r_ada = [r["recall_ann_20"] for r in adapt]
        x = np.arange(len(xvals))
        w = 0.36
        ax.bar(x - w / 2, r_nat, width=w, color=COLOR_NATIVE, hatch=HATCH,
               edgecolor="#666666", linewidth=0.6, label="原生固定 HNSW")
        ax.bar(x + w / 2, r_ada, width=w, color=COLOR_ADAPT,
               edgecolor="#123456", linewidth=0.6, label="自适应 HNSW")
        ax.axhline(1.0, color="#B03030", linestyle="--", linewidth=1.2)
        ax.text(len(xvals) - 0.5, 1.005, "Flat=1.0", color="#B03030", fontsize=9, ha="right")
        ax.set_xticks(x)
        ax.set_xticklabels([str(v) for v in xvals], fontsize=9)
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_title(gtitle, fontsize=11)
        ax.set_ylim(0.5, 1.03)
        ax.grid(axis="y", alpha=0.3)
        ax.tick_params(axis="y", labelsize=9)
    axes[0].set_ylabel("Recall@20 (Recall_ANN@20)", fontsize=10)
    handles = [
        mpatches.Patch(facecolor=COLOR_NATIVE, hatch=HATCH, edgecolor="#666666", label="原生固定 HNSW"),
        mpatches.Patch(facecolor=COLOR_ADAPT, edgecolor="#123456", label="自适应 HNSW"),
        plt.Line2D([0], [0], color="#B03030", linestyle="--", label="Flat 精确检索上限"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=9,
               bbox_to_anchor=(0.5, -0.03), frameon=False)
    fig.suptitle("图 A：固定知识规模下 HNSW 参数扫描的召回率对比（Top-20）", fontsize=12, y=1.00)
    fig.tight_layout(rect=(0, 0.06, 1, 0.98))
    figA = FIG_DIR / "hnsw_recall_baseline_vs_adaptive.png"
    fig.savefig(figA, dpi=200, bbox_inches="tight")
    print(f"图A: {figA}")

    # ---------- 图 B：检索时延 P95 ----------
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=False)
    for ax, (gkey, xlabel, gtitle) in zip(axes, [
            ("M", "邻接度 M", "邻接度 M 扫描"),
            ("efC", "ef Construction", "构图参数 efConstruction 扫描"),
            ("efS", "ef Search", "检索参数 efSearch 扫描")]):
        rows = scans[gkey]["rows"]
        native = [r for r in rows if r["method"] == "native_fixed"]
        adapt = [r for r in rows if r["method"] == "adaptive_hnsw"]
        xvals = [r[gkey] for r in native]
        t_nat = [r["latency_p95_ms"] for r in native]
        t_ada = [r["latency_p95_ms"] for r in adapt]
        x = np.arange(len(xvals))
        w = 0.36
        ax.bar(x - w / 2, t_nat, width=w, color=COLOR_NATIVE, hatch=HATCH,
               edgecolor="#666666", linewidth=0.6, label="原生固定 HNSW")
        ax.bar(x + w / 2, t_ada, width=w, color=COLOR_ADAPT,
               edgecolor="#123456", linewidth=0.6, label="自适应 HNSW")
        flat_lat = results.get("flat_latency_ms", 0)
        if flat_lat:
            ax.axhline(flat_lat, color="#666666", linestyle=":", linewidth=1.2)
            ax.text(0.5, flat_lat * 1.02, f"Flat ≈{flat_lat:.1f}ms",
                    color="#666666", fontsize=8, ha="left")
        ax.set_xticks(x)
        ax.set_xticklabels([str(v) for v in xvals], fontsize=9)
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_title(gtitle, fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        ax.tick_params(axis="y", labelsize=9)
    axes[0].set_ylabel("P95 Query Latency (ms)", fontsize=10)
    handles = [
        mpatches.Patch(facecolor=COLOR_NATIVE, hatch=HATCH, edgecolor="#666666", label="原生固定 HNSW"),
        mpatches.Patch(facecolor=COLOR_ADAPT, edgecolor="#123456", label="自适应 HNSW"),
        plt.Line2D([0], [0], color="#666666", linestyle=":", label="Flat 精确检索时延"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=9,
               bbox_to_anchor=(0.5, -0.03), frameon=False)
    fig.suptitle("图 B：固定知识规模下 HNSW 参数扫描的检索时延对比（P95, HNSW 核心查询）",
                 fontsize=12, y=1.00)
    fig.tight_layout(rect=(0, 0.06, 1, 0.98))
    figB = FIG_DIR / "hnsw_latency_baseline_vs_adaptive.png"
    fig.savefig(figB, dpi=200, bbox_inches="tight")
    print(f"图B: {figB}")


if __name__ == "__main__":
    plot_two_figures()
