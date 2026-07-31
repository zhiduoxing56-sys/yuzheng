from __future__ import annotations

import json
from datetime import datetime
from threading import RLock
from time import perf_counter
from typing import Any

import numpy as np

from app.models.schemas import EvidenceNode, IndexStatus, RetrievalMetadata, utc_now
from app.services.vector.embedding import EmbeddingService


def evidence_text(node: EvidenceNode) -> str:
    return " ".join(
        [
            node.evidence_type,
            node.layer,
            node.source,
            json.dumps(node.value, ensure_ascii=False, sort_keys=True),
        ]
    )


class HNSWIndexService:
    """优先使用 hnswlib；不可用时执行相同接口的确定性精确余弦检索。"""

    def __init__(self, config: dict[str, Any], embedder: EmbeddingService) -> None:
        self.embedder = embedder
        self.dimension = embedder.dimension
        self.M = int(config.get("M", 16))
        self.ef_construction = int(config.get("ef_construction", 200))
        self.ef_search = int(config.get("ef_search", 30))
        self.top_k = int(config.get("top_k", 20))
        self._lock = RLock()
        self._nodes: dict[str, EvidenceNode] = {}
        self._vectors: dict[str, np.ndarray] = {}
        self._labels: dict[int, str] = {}
        self._node_labels: dict[str, int] = {}
        self._next_label = 0
        self._index: Any = None
        self._excluded_types: set[str] = set()
        self._last_built_at: datetime | None = None
        try:
            import hnswlib  # type: ignore

            self._hnswlib = hnswlib
            self.implementation = "hnswlib"
            self.degraded = False
            self.degradation_reason = None
        except Exception as exc:
            self._hnswlib = None
            self.implementation = "exact_cosine_fallback"
            self.degraded = True
            self.degradation_reason = f"hnswlib unavailable: {type(exc).__name__}: {exc}"

    def _encode_node(self, node: EvidenceNode) -> np.ndarray:
        vector, _ = self.embedder.encode(evidence_text(node))
        return np.asarray(vector, dtype=np.float32)

    def build(self, nodes: list[EvidenceNode], exclude_types: list[str] | None = None) -> IndexStatus:
        with self._lock:
            self._excluded_types = set(exclude_types or [])
            included = [node for node in nodes if node.evidence_type not in self._excluded_types]
            self._nodes = {node.node_id: node for node in included}
            self._vectors = {node.node_id: self._encode_node(node) for node in included}
            self._labels.clear()
            self._node_labels.clear()
            self._next_label = 0
            self._index = None
            if self._hnswlib is not None and included:
                self._index = self._hnswlib.Index(space="cosine", dim=self.dimension)
                self._index.init_index(
                    max_elements=max(100, len(included) * 2),
                    ef_construction=self.ef_construction,
                    M=self.M,
                )
                labels = np.arange(len(included), dtype=np.int64)
                matrix = np.vstack([self._vectors[node.node_id] for node in included])
                self._index.add_items(matrix, labels)
                self._index.set_ef(self.ef_search)
                for label, node in zip(labels.tolist(), included, strict=True):
                    self._labels[label] = node.node_id
                    self._node_labels[node.node_id] = label
                self._next_label = len(included)
            self._last_built_at = utc_now()
            return self.status()

    def upsert(self, nodes: list[EvidenceNode]) -> None:
        with self._lock:
            accepted = [node for node in nodes if node.evidence_type not in self._excluded_types]
            for node in accepted:
                self._nodes[node.node_id] = node
                self._vectors[node.node_id] = self._encode_node(node)
            if self._hnswlib is None or not accepted:
                return
            # 节点 ID 可能代表同一证据的更新。小规模车况索引直接原子重建，
            # 避免 hnswlib 中旧 label 与新 label 同时指向同一节点而返回重复候选。
            self.build(list(self._nodes.values()), list(self._excluded_types))

    def search(
        self, query_vector: list[float], top_k: int | None = None
    ) -> tuple[list[tuple[EvidenceNode, float]], RetrievalMetadata]:
        started = perf_counter()
        with self._lock:
            limit = min(top_k or self.top_k, max(1, len(self._nodes)))
            results: list[tuple[EvidenceNode, float]] = []
            if self._nodes:
                query = np.asarray(query_vector, dtype=np.float32)
                if self._index is not None:
                    labels, distances = self._index.knn_query(query.reshape(1, -1), k=limit)
                    for label, distance in zip(labels[0].tolist(), distances[0].tolist(), strict=True):
                        node_id = self._labels[int(label)]
                        results.append((self._nodes[node_id], float(np.clip(1.0 - distance, 0, 1))))
                else:
                    scored = [
                        (node_id, float(np.clip(np.dot(query, vector), 0, 1)))
                        for node_id, vector in self._vectors.items()
                    ]
                    scored.sort(key=lambda item: (-item[1], item[0]))
                    results = [(self._nodes[node_id], score) for node_id, score in scored[:limit]]
            duration_ms = (perf_counter() - started) * 1000
            metadata = RetrievalMetadata(
                implementation=self.implementation,
                index_node_count=len(self._nodes),
                vector_dimension=self.dimension,
                M=self.M,
                ef_construction=self.ef_construction,
                ef_search=self.ef_search,
                top_k=top_k or self.top_k,
                candidate_count=len(results),
                duration_ms=round(duration_ms, 4),
                empty_index=not self._nodes,
                degraded=self.degraded,
                degradation_reason=self.degradation_reason,
                excluded_types=sorted(self._excluded_types),
                last_built_at=self._last_built_at,
            )
            return results, metadata

    def status(self) -> IndexStatus:
        return IndexStatus(
            implementation=self.implementation,
            node_count=len(self._nodes),
            dimension=self.dimension,
            M=self.M,
            ef_construction=self.ef_construction,
            ef_search=self.ef_search,
            top_k=self.top_k,
            degraded=self.degraded,
            degradation_reason=self.degradation_reason,
            excluded_types=sorted(self._excluded_types),
            last_built_at=self._last_built_at,
        )
