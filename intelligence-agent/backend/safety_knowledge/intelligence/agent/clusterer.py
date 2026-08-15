"""情报智能体 v3 —— Layer 2: Normalize + Deduplicate + Cluster

设计要点（用户反馈 #4）：
  - 基本单元是 IncidentCluster（同一事故的多源记录聚合）
  - 去重在 Cluster 层做（先聚合再去重），避免"同事故生成多个节点"
  - 多源记录 → corroboration_count 增加可信度

聚类算法：
  1. 按 component_family 分桶（如 EXTERIOR LIGHTING）
  2. 桶内按 subject 语义相似度（token Jaccard）合并：>= 阈值视为同一事故
  3. 同 cluster 记录共享 cluster_id，保留全部 SourceRecord（provenance）
"""
from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass, field

from safety_knowledge.intelligence.agent.source_layer import RawIncidentRecord
from safety_knowledge.intelligence.models import IncidentCluster, SourceRecord

# 组件家族提取：取 Component 第一段大写层级
STOPWORDS = {"the", "a", "an", "vehicle", "vehicles", "certain", "system", "with", "and", "or", "of"}


def normalize_text(text: str) -> str:
    """标题/主题归一化：小写、去符号。"""
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", text.lower()).strip()


def tokenize(text: str) -> set[str]:
    toks = {t for t in normalize_text(text).split() if t and t not in STOPWORDS and len(t) > 1}
    return toks


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b) if (a | b) else 0.0


def extract_subject(record: RawIncidentRecord) -> str:
    """从内容提取主题词（英文取关键短语，中文取 8 字内片段）。"""
    content = record.raw_content or record.raw_title
    if re.search(r"[\u4e00-\u9fff]", content):
        return content[:24]
    return content[:80]


class IncidentClusterer:
    """Normalize + Dedup + Cluster。"""

    def __init__(self, subject_threshold: float = 0.55) -> None:
        self.subject_threshold = subject_threshold

    def cluster(self, records: list[RawIncidentRecord]) -> list[IncidentCluster]:
        # 1. 按 component_family 分桶
        buckets: dict[str, list[RawIncidentRecord]] = defaultdict(list)
        for r in records:
            comp = r.component.split(":")[0] if r.component else "UNKNOWN"
            buckets[comp.upper()].append(r)

        clusters: list[IncidentCluster] = []
        seq = 0
        for comp_family, bucket in sorted(buckets.items()):
            # 2. 桶内主题聚类（贪心）
            groups: list[list[RawIncidentRecord]] = []
            for rec in bucket:
                subject = extract_subject(rec)
                toks = tokenize(subject)
                placed = False
                for g in groups:
                    g_subject = extract_subject(g[0])
                    g_toks = tokenize(g_subject)
                    sim = jaccard(toks, g_toks)
                    if sim >= self.subject_threshold:
                        g.append(rec)
                        placed = True
                        break
                if not placed:
                    groups.append([rec])

            # 3. 生成 Cluster
            for g in groups:
                seq += 1
                cluster_id = f"IC-{seq:04d}"
                first = g[0]
                cluster = IncidentCluster(
                    cluster_id=cluster_id,
                    subject=extract_subject(first)[:60],
                    component_family=comp_family,
                    component_sub=first.component.split(":", 1)[1] if ":" in first.component else "",
                )
                for rec in sorted(g, key=lambda x: x.retrieved_at):
                    cluster.add_record(SourceRecord(
                        source_id=rec.source_id,
                        source_type=rec.source_type,
                        retrieved_at=rec.retrieved_at,
                        url=rec.url,
                        raw_title=rec.raw_title,
                        raw_content=rec.raw_content,
                        content_hash=rec.content_hash,
                        parser_version=rec.parser_version,
                        official_confirmed=rec.official_confirmed,
                    ))
                clusters.append(cluster)

        return clusters


def dedup_fingerprint(cluster: IncidentCluster) -> str:
    """Cluster 级去重指纹（供跨轮次去重）。"""
    payload = f"{cluster.component_family}::{cluster.component_sub}::{normalize_text(cluster.subject)[:24]}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


if __name__ == "__main__":
    # 冒烟测试
    from safety_knowledge.intelligence.agent.source_layer import ProvenanceFetcher
    f = ProvenanceFetcher()
    r1 = f.from_legacy({"incident_id": "A1", "title": "召回: EXTERIOR LIGHTING:TAIL LIGHTS",
                        "content": "Tesla recalls certain Model 3 vehicles. One or both taillights may intermittently fail to illuminate.",
                        "source_id": "NHTSA-RCL", "official_confirmed": True})
    r2 = f.from_legacy({"incident_id": "A2", "title": "投诉: EXTERIOR LIGHTING:TAIL LIGHTS",
                        "content": "My taillights fail intermittently on my 2023 Model Y.",
                        "source_id": "NHTSA-CSI", "official_confirmed": False})
    r3 = f.from_legacy({"incident_id": "B1", "title": "召回: AIR BAGS:FRONTAL",
                        "content": "Air bag inflator may rupture.",
                        "source_id": "NHTSA-RCL", "official_confirmed": True})
    c = IncidentClusterer()
    clusters = c.cluster([r1, r2, r3])
    for cl in clusters:
        print(f"{cl.cluster_id} | {cl.component_family} | n={cl.corroboration_count} | official={cl.official_confirmed} | {cl.subject[:40]}")
    f.close()
