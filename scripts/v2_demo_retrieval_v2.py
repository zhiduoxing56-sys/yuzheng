# -*- coding: utf-8 -*-
"""演示检索链路 v2：语音指令 + NLU 意图先验（融合查询）→ Top-20 命中质量评估。
真实系统等价机制：trusted_knowledge.augment 的 exact_matches（canonical_action 精确匹配优先）。
"""
import json, sys, io, time
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

KC = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\knowledge-contract-v1\acceptance")
FILES = ["knowledge_constraints_v1.jsonl", "knowledge_constraints_v1_demo.jsonl",
         "knowledge_constraints_v1_shishitiaoli_v2.jsonl",
         "knowledge_constraints_v1_batch1.jsonl", "knowledge_constraints_v1_batch2.jsonl"]
nodes = []
for fn in FILES:
    nodes += [json.loads(l) for l in (KC / fn).read_text(encoding="utf-8").strip().splitlines()]

def knowledge_text(n):
    parts = [n["title"], n["semantic_description"], n["canonical_action"],
             *(f"REQUIRED {e}" for e in n["required_evidence"])]
    return " ".join(p for p in parts if p)

from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-base-zh-v1.5", local_files_only=True)
texts = [knowledge_text(n) for n in nodes]
vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

import hnswlib
idx = hnswlib.Index(space="cosine", dim=768)
idx.init_index(max_elements=max(10, len(nodes)), ef_construction=200, M=16)
idx.add_items(vecs, list(range(len(nodes))))
idx.set_ef(128)

# 演示场景：语音指令 + NLU 意图先验词 + 核心 node_id 验证集
SCENES = [
    ("① 夜间关闭大灯", "关闭大灯", "关闭 大灯 前照灯 头灯 近光 远光 夜间 灯光 关闭前照灯 关灯",
     {"知识.灯光.夜间关闭限制.001", "知识.灯光.会车150米内禁远光.001"},
     {"HEADLIGHT_SET_MODE", "LOW_BEAM_ON", "HIGH_BEAM_ON", "LOW_BEAM_OFF", "HIGH_BEAM_OFF", "PARKING_LIGHT_ON", "FOG_LIGHT_ON", "FOG_LIGHT_OFF"}),
    ("② 雨天关闭雨刮", "下雨了把雨刮关掉", "雨刮 雨刮器 关闭雨刮 雨天 降雨 刮水 前风窗 除水",
     {"知识.雨刮.雨天关闭限制.001", "知识.雨刮.雨天关闭雨刮禁止.005", "知识.雨刮.大雪禁止关闭雨刮.004"},
     {"WIPER_SET_MODE", "DEFROST_ON"}),
    ("③ 左后障碍向左变道", "我要往左边变道", "变道 变更车道 向左变道 左变道 超车 转向灯 左侧",
     {"知识.变道.左后障碍变道限制.001", "知识.灯光.变道转向灯.001", "知识.变道.影响车道变道限制.001"},
     {"LANE_CHANGE", "TURN_INDICATOR_ON", "LANE_KEEP", "EVASIVE_STEER"}),
    ("④ 无空间自动泊车", "帮我自动泊车", "自动泊车 泊车 停车 车位 泊入 找车位",
     {"知识.泊车.无空间自动泊车限制.001", "知识.泊车.空间可用概率低谨慎泊车.001"},
     {"AUTO_PARK_ENABLE"}),
    ("⑤ 突发障碍变道避让", "前面有障碍物快变道", "变道 避让 障碍物 紧急 制动 减速 让速不让道 避险",
     {"知识.变道.突发障碍变道复核.001", "知识.转向.紧急避险让速不让道.003", "知识.转向.突发障碍优先制动而非急转向.001"},
     {"LANE_CHANGE", "EVASIVE_STEER", "LANE_KEEP", "BRAKE", "EMERGENCY_BRAKE", "ACCELERATE"}),
]

out = []
summary = []
for name, voice, intent_words, expect_ids, rel_intents in SCENES:
    q = voice + " " + intent_words
    qv = model.encode([q], normalize_embeddings=True)[0]
    labels, dists = idx.knn_query(qv.reshape(1, -1), k=20)
    out.append(f"\n{'='*72}\n{name}\n  语音: [{voice}]\n  融合查询: [{q}]\n{'='*72}")
    hit_expected = []
    blocks = 0
    rel_hits = 0
    for rank, (label, d) in enumerate(zip(labels[0], dists[0]), 1):
        n = nodes[int(label)]
        sim = 1 - d
        if n["node_id"] in expect_ids:
            hit_expected.append((rank, n["node_id"]))
        if n["effect"]["then"] == "BLOCK":
            blocks += 1
        if n["command"]["intent_id"] in rel_intents:
            rel_hits += 1
        effect = n["effect"]["then"]
        mark = {"BLOCK": "⛔", "REVIEW": "⚠️", "ALLOW": "✅"}.get(effect, "?")
        out.append(f"{rank:>2}. [{effect}]{mark} sim={sim:.3f} | {n['node_id']}")
        out.append(f"      {n['title']} | {n['source']}")
    line = f"{name}: 核心命中 {len(hit_expected)}/{len(expect_ids)} {hit_expected} | Top20 BLOCK={blocks} 意图相关={rel_hits}/20"
    summary.append(line)
    out.append(f"  → {line}")

report = "\n".join(out)
outfile = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\demo_retrieval_v2_report.txt")
outfile.write_text(report, encoding="utf-8")
print(report)
print("\n\n=== 汇总 ===")
print("\n".join(summary))
print(f"\n报告: {outfile}")
