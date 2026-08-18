# -*- coding: utf-8 -*-
"""演示检索链路：169 条 V1 节点 + bge-base-zh-v1.5 + hnswlib cosine。
中文语音指令 → Top-20 中文安全规则展示（模拟演示页）。
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

print(f"加载节点: {len(nodes)}")
from sentence_transformers import SentenceTransformer
t0 = time.perf_counter()
model = SentenceTransformer("BAAI/bge-base-zh-v1.5", local_files_only=True)
print(f"模型加载: {time.perf_counter()-t0:.1f}s")

texts = [knowledge_text(n) for n in nodes]
vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
print(f"编码完成: {vecs.shape}")

import hnswlib
idx = hnswlib.Index(space="cosine", dim=768)
idx.init_index(max_elements=max(10, len(nodes)), ef_construction=200, M=16)
idx.add_items(vecs, list(range(len(nodes))))
idx.set_ef(64)

QUERIES = {
    "① 夜间行驶关闭大灯": "把大灯关了",
    "② 雨天关闭雨刮": "下雨了把雨刮关掉",
    "③ 左后方有障碍物要向左变道": "我要往左边变道",
    "④ 没有停车位想自动泊车": "帮我自动泊车",
    "⑤ 前方突然有障碍物快变道": "前面有障碍物，快变道避让",
}

out = []
for qname, q in QUERIES.items():
    qv = model.encode([q], normalize_embeddings=True)[0]
    labels, dists = idx.knn_query(qv.reshape(1, -1), k=20)
    out.append(f"\n{'='*70}\n{'- ' * 0}{qname}\n  指令: [{q}]\n{'='*70}")
    for rank, (label, d) in enumerate(zip(labels[0], dists[0]), 1):
        n = nodes[int(label)]
        sim = 1 - d
        effect = n["effect"]["then"]
        mark = {"BLOCK": "⛔", "REVIEW": "⚠️", "ALLOW": "✅"}.get(effect, "?")
        evs = ",".join(sorted({a["type"] for a in n["evidence"].values()}))
        out.append(f"{rank:>2}. [{effect}]{mark} sim={sim:.3f} | {n['node_id']}\n"
                   f"      {n['title']} | 证据:{evs} | {n['source']}")
        out.append(f"      → {n['semantic_description']}")

report = "\n".join(out)
outfile = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\demo_retrieval_report.txt")
outfile.write_text(report, encoding="utf-8")
print(report[:6000])
print(f"\n\n完整报告已写入: {outfile}")
