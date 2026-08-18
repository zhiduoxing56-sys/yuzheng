# -*- coding: utf-8 -*-
"""V1 中文安全知识库 演示检索脚本（自包含版，队友可直接运行）。

功能：中文语音指令（可带 NLU 意图先验词）→ 向量检索 → Top-20 中文安全规则展示。

环境要求：
    pip install sentence-transformers hnswlib numpy
    模型：BAAI/bge-base-zh-v1.5（首次运行自动下载，或设置 HF_HOME 指向已缓存目录）

用法：
    python v2_demo_retrieval_standalone.py [--kb 知识库jsonl路径] [--top-k 20] [--model BAAI/bge-base-zh-v1.5]

输出：data/demo_retrieval_report.txt（Top-20 明细 + 命中统计）
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace") if hasattr(sys.stdout, "reconfigure") else None


def knowledge_text(n: dict) -> str:
    """节点检索文本（对齐主系统 trusted_knowledge.knowledge_text 拼接风格）。
    重要：与线上 trusted_knowledge.py 的字段拼接一致，保证检索语义与线上一致。"""
    parts = [
        n["title"],
        n["semantic_description"],
        n["canonical_action"],
        *(f"REQUIRED {e}" for e in n.get("required_evidence", [])),
    ]
    return " ".join(p for p in parts if p)


def load_nodes(path: Path) -> list[dict]:
    nodes = []
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if line.strip():
            nodes.append(json.loads(line))
    return nodes


# 5 个演示场景：语音指令 + NLU 意图先验词 + 核心节点验证集 + 相关意图集合
DEMO_SCENES = [
    ("① 夜间关闭大灯", "关闭大灯",
     "关闭 大灯 前照灯 头灯 近光 远光 夜间 灯光 关闭前照灯 关灯",
     {"知识.灯光.夜间关闭限制.001", "知识.灯光.会车150米内禁远光.001"},
     {"HEADLIGHT_SET_MODE", "LOW_BEAM_ON", "HIGH_BEAM_ON", "LOW_BEAM_OFF", "HIGH_BEAM_OFF",
      "PARKING_LIGHT_ON", "FOG_LIGHT_ON", "FOG_LIGHT_OFF"}),
    ("② 雨天关闭雨刮", "下雨了把雨刮关掉",
     "雨刮 雨刮器 关闭雨刮 雨天 降雨 刮水 前风窗 除水",
     {"知识.雨刮.雨天关闭限制.001", "知识.雨刮.雨天关闭雨刮禁止.005",
      "知识.雨刮.大雪禁止关闭雨刮.004"},
     {"WIPER_SET_MODE", "DEFROST_ON"}),
    ("③ 左后障碍向左变道", "我要往左边变道",
     "变道 变更车道 向左变道 左变道 超车 转向灯 左侧",
     {"知识.变道.左后障碍变道限制.001", "知识.灯光.变道转向灯.001",
      "知识.变道.影响车道变道限制.001"},
     {"LANE_CHANGE", "TURN_INDICATOR_ON", "LANE_KEEP", "EVASIVE_STEER"}),
    ("④ 无空间自动泊车", "帮我自动泊车",
     "自动泊车 泊车 停车 车位 泊入 找车位",
     {"知识.泊车.无空间自动泊车限制.001", "知识.泊车.空间可用概率低谨慎泊车.001"},
     {"AUTO_PARK_ENABLE"}),
    ("⑤ 突发障碍变道避让", "前面有障碍物快变道",
     "变道 避让 障碍物 紧急 制动 减速 让速不让道 避险",
     {"知识.变道.突发障碍变道复核.001", "知识.转向.紧急避险让速不让道.003",
      "知识.转向.突发障碍优先制动而非急转向.001"},
     {"LANE_CHANGE", "EVASIVE_STEER", "LANE_KEEP", "BRAKE", "EMERGENCY_BRAKE", "ACCELERATE"}),
]

EFFECT_MARK = {"BLOCK": "⛔", "REVIEW": "⚠️", "ALLOW": "✅"}


def main() -> None:
    ap = argparse.ArgumentParser(description="V1 中文安全知识库演示检索")
    ap.add_argument("--kb", default="knowledge_constraints_v1_merged.jsonl",
                    help="知识库 jsonl 路径（默认取脚本同目录或当前目录）")
    ap.add_argument("--top-k", type=int, default=20)
    ap.add_argument("--model", default="BAAI/bge-base-zh-v1.5")
    args = ap.parse_args()

    kb_path = Path(args.kb)
    if not kb_path.is_absolute():
        here = Path(__file__).parent
        for cand in (here / args.kb, Path.cwd() / args.kb):
            if cand.exists():
                kb_path = cand
                break
    if not kb_path.exists():
        sys.exit(f"知识库不存在: {kb_path}")

    print(f"[1/4] 加载知识库: {kb_path}")
    nodes = load_nodes(kb_path)
    print(f"       {len(nodes)} 条 | 效果分布: {dict(Counter(n['effect']['then'] for n in nodes))}")

    print(f"[2/4] 加载嵌入模型: {args.model} (首次运行自动下载)")
    from sentence_transformers import SentenceTransformer
    t0 = time.perf_counter()
    model = SentenceTransformer(args.model)
    print(f"       模型加载耗时 {time.perf_counter() - t0:.1f}s")

    print("[3/4] 编码节点 + 构建 hnswlib cosine 索引")
    texts = [knowledge_text(n) for n in nodes]
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    import hnswlib
    idx = hnswlib.Index(space="cosine", dim=vecs.shape[1])
    idx.init_index(max_elements=max(10, len(nodes)), ef_construction=200, M=16)
    idx.add_items(vecs, list(range(len(nodes))))
    idx.set_ef(128)

    print(f"[4/4] 演示检索 Top-{args.top_k}\n")
    out = []
    summary = []
    for name, voice, intent_words, expect_ids, rel_intents in DEMO_SCENES:
        q = voice + " " + intent_words
        qv = model.encode([q], normalize_embeddings=True)[0]
        labels, dists = idx.knn_query(qv.reshape(1, -1), k=args.top_k)
        out.append(f"\n{'=' * 72}\n{name}\n  语音指令: [{voice}]\n  融合查询: [{q}]\n{'=' * 72}")
        hit_expected, blocks, rel_hits = [], 0, 0
        for rank, (label, d) in enumerate(zip(labels[0], dists[0]), 1):
            n = nodes[int(label)]
            sim = 1.0 - d
            if n["node_id"] in expect_ids:
                hit_expected.append((rank, n["node_id"]))
            if n["effect"]["then"] == "BLOCK":
                blocks += 1
            if n["command"]["intent_id"] in rel_intents:
                rel_hits += 1
            effect = n["effect"]["then"]
            evs = ",".join(sorted({a["type"] for a in n["evidence"].values()}))
            out.append(f"{rank:>2}. [{effect}]{EFFECT_MARK.get(effect, '?')} sim={sim:.3f} | {n['node_id']}")
            out.append(f"      {n['title']} | 证据:{evs} | {n['source']}")
        line = (f"{name}: 核心命中 {len(hit_expected)}/{len(expect_ids)} {hit_expected}"
                f" | Top{args.top_k} BLOCK={blocks} 意图相关={rel_hits}/{args.top_k}")
        summary.append(line)
        out.append(f"  → {line}")

    report = "\n".join(out)
    outfile = Path(__file__).parent / "demo_retrieval_report.txt"
    outfile.write_text(report, encoding="utf-8")
    print(report)
    print("\n=== 汇总 ===")
    print("\n".join(summary))
    print(f"\n完整报告: {outfile}")


if __name__ == "__main__":
    main()
