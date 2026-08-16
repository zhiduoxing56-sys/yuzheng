"""安全知识库：重建 HNSW 索引 + 检索演示

用法：
  1. 重建索引（knowledge_nodes_v4.jsonl → regulation_kb_v8/）
     python scripts/run_knowledge_retrieval.py --rebuild
  2. 检索演示
     python scripts/run_knowledge_retrieval.py --query "关闭大灯" --k 5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\backend")
ROOT = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean")
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.services.regulation.service import RegulationKnowledgeBase  # noqa: E402
from app.services.vector.embedding import LocalSentenceTransformerEmbeddingService  # noqa: E402

KB_DIR = ROOT / "data" / "regulation_kb_v8"
NODES_FILE = ROOT / "data" / "knowledge_nodes_v4.jsonl"


def rebuild() -> None:
    """从知识节点文件重建 HNSW 索引。"""
    embedder = LocalSentenceTransformerEmbeddingService(model_name="BAAI/bge-base-zh-v1.5", dimension=768)
    kb = RegulationKnowledgeBase(embedder)
    count = 0
    with open(NODES_FILE, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            n = json.loads(line)
            content = f"{n['title']} {n['semantic_description']} 约束:{n['canonical_action']} 证据:{' '.join(n['required_evidence'])}"
            kb.add_document(
                content=content,
                standard_id=n["source"],
                clause=n["clause"],
                source=n["source"],
            )
            count += 1
    kb.save(KB_DIR)
    print(f"知识库索引重建完成: {count} 节点 → {KB_DIR}")


def search(query: str, k: int) -> None:
    """检索演示。"""
    embedder = LocalSentenceTransformerEmbeddingService(model_name="BAAI/bge-base-zh-v1.5", dimension=768)
    kb = RegulationKnowledgeBase(embedder)
    if not (KB_DIR / "index.bin").exists():
        print("索引不存在，先执行 --rebuild")
        return
    kb.load(KB_DIR)
    hits = kb.search(query, k=k)
    print(f"查询: {query}")
    for h in hits:
        print(f"  [{h.score:.4f}] {h.standard_id} {h.clause} | {h.content[:60]}... | 证据: {h.evidence_types[:4]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="安全知识库检索入口")
    parser.add_argument("--rebuild", action="store_true", help="重建 HNSW 索引")
    parser.add_argument("--query", type=str, help="检索查询文本")
    parser.add_argument("--k", type=int, default=5, help="Top-K")
    args = parser.parse_args()
    if args.rebuild:
        rebuild()
    if args.query:
        search(args.query, args.k)
    if not args.rebuild and not args.query:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
