# -*- coding: utf-8 -*-
"""编码 3256 候选节点 → 向量库（N=3256）。"""
import json, io, sys, time
import numpy as np
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

src = r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\knowledge_nodes_large_candidate.jsonl"
out_dir = r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\knowledge_vectors_large"

from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-base-zh-v1.5", local_files_only=True)

nodes, texts = [], []
with open(src, encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        t = " ".join([str(d.get("title", "")), str(d.get("semantic_description", "")), str(d.get("intent_id", ""))])
        nodes.append(d)
        texts.append(t)

t0 = time.perf_counter()
vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
print(f"encode {len(vecs)} 耗时 {time.perf_counter()-t0:.0f}s")
vecs = np.asarray(vecs, dtype=np.float32)
norms = np.linalg.norm(vecs, axis=1, keepdims=True)
norms[norms == 0] = 1.0
vecs = vecs / norms
np.save(out_dir + r"\full_3256_vecs.npy", vecs)
with open(out_dir + r"\full_3256_nodes.jsonl", "w", encoding="utf-8") as f:
    for d in nodes:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")
print("saved", vecs.shape)
