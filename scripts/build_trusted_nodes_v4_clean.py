"""生成 Trusted 知识节点净化副本（供在线裁决知识库使用）。

输入: data/knowledge_nodes_v4.jsonl（队友上传的 120 个节点）
处理:
  1. 注入 metadata.review_status = "TRUSTED"（v4 数据本身缺 Trusted 标记, load_trusted_nodes 会全过滤）
  2. 过滤 required_evidence / optional_evidence 中的 non-canonical 类型
     （v4 含 SECURITY_STATE / DATA_* 等安全/数据域类型, 不在主系统 38 种车辆控制
      canonical 证据空间内, 与知识库严格校验冲突）
输出: data/knowledge/trusted_nodes_v4_clean.jsonl（不改队友原文件）

用法: python scripts/build_trusted_nodes_v4_clean.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.config import PROJECT_ROOT  # noqa: E402
from app.services.evidence.catalog import CANONICAL_EVIDENCE_TYPES  # noqa: E402

SOURCE = PROJECT_ROOT / "data" / "knowledge_nodes_v4.jsonl"
TARGET = PROJECT_ROOT / "data" / "knowledge" / "trusted_nodes_v4_clean.jsonl"


def main() -> int:
    if not SOURCE.exists():
        print(f"源文件不存在: {SOURCE}")
        return 1
    canonical = set(CANONICAL_EVIDENCE_TYPES)
    rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line.strip()]
    total = len(rows)
    dropped_evidence = 0
    for row in rows:
        metadata = row.setdefault("metadata", {})
        metadata["review_status"] = "TRUSTED"
        for field in ("required_evidence", "optional_evidence"):
            before = row.get(field, [])
            row[field] = [value for value in before if value in canonical]
            dropped_evidence += len(before) - len(row[field])
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    print(f"已生成 {TARGET}")
    print(f"  节点数: {total}, 过滤 non-canonical 证据条目: {dropped_evidence}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
