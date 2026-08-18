# -*- coding: utf-8 -*-
"""合并 5 个知识库文件为单文件（供队友直接加载）。"""
import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
KC = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\knowledge-contract-v1\acceptance")
FILES = ["knowledge_constraints_v1.jsonl", "knowledge_constraints_v1_demo.jsonl",
         "knowledge_constraints_v1_shishitiaoli_v2.jsonl",
         "knowledge_constraints_v1_batch1.jsonl", "knowledge_constraints_v1_batch2.jsonl"]
OUT = KC / "knowledge_constraints_v1_merged.jsonl"

nodes = []
seen = set()
for fn in FILES:
    for l in (KC / fn).read_text(encoding="utf-8").strip().splitlines():
        n = json.loads(l)
        if n["node_id"] in seen:
            print(f"!! 重复 node_id: {n['node_id']} (跳过)")
            continue
        seen.add(n["node_id"])
        nodes.append(n)

with OUT.open("w", encoding="utf-8") as f:
    for n in nodes:
        f.write(json.dumps(n, ensure_ascii=False) + "\n")

from collections import Counter
print(f"合并完成: {len(nodes)} 条 -> {OUT.name}")
print("效果分布:", dict(Counter(n["effect"]["then"] for n in nodes)))
print("来源分布:", dict(Counter(n["source"] for n in nodes)))
