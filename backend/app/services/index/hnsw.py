from __future__ import annotations

import json
from datetime import datetime
from threading import RLock
from time import perf_counter
from typing import Any

import numpy as np

from app.models.schemas import EvidenceNode, EvidenceStatus, IndexStatus, RetrievalMetadata, utc_now
from app.services.vector.embedding import EmbeddingService


EPHEMERAL_EVIDENCE_TYPES = {"evidence_demand", "control_target", "evidence_stream"}


def evidence_text(node: EvidenceNode) -> str:
    return " ".join(
        [
            node.evidence_type,
            node.layer,
            node.source,
            json.dumps(node.value, ensure_ascii=False, sort_keys=True),
        ]
    )


def evidence_key(node: EvidenceNode) -> str:
    """Stable identity for one updateable evidence stream."""
    entity = (
        node.metadata.get("entity_id")
        or node.metadata.get("rule_id")
        or node.metadata.get("area")
        or "global"
    )
    return f"{node.evidence_type}|{node.source}|{entity}"


class HNSWIndexService:
    """Bounded canonical evidence index with stable labels and explicit transient isolation."""

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
        self._key_labels: dict[str, int] = {}
        self._next_label = 0
        self._max_elements = 0
        self._index: Any = None
        self._excluded_types: set[str] = set()
        self._last_built_at: datetime | None = None
        self._ephemeral_node_count = 0
        self._index_update_count = 0
        self._index_rebuild_count = 0
        self._deduplicated_count = 0
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

    @staticmethod
    def _is_ephemeral(node: EvidenceNode) -> bool:
        return (
            node.quality_label == EvidenceStatus.MISSING
            or node.source == "mandatory_recall"
            or node.evidence_type in EPHEMERAL_EVIDENCE_TYPES
            or bool(node.metadata.get("ephemeral"))
            or bool(node.metadata.get("derived_conflict"))
        )

    def _encode_node(self, node: EvidenceNode) -> np.ndarray:
        vector, _ = self.embedder.encode(evidence_text(node))
        return np.asarray(vector, dtype=np.float32)

    @staticmethod
    def _latest_by_key(nodes: list[EvidenceNode]) -> dict[str, EvidenceNode]:
        latest: dict[str, EvidenceNode] = {}
        for node in nodes:
            key = evidence_key(node)
            current = latest.get(key)
            if current is None or (node.timestamp, node.node_id) > (
                current.timestamp,
                current.node_id,
            ):
                latest[key] = node
        return latest

    def build(self, nodes: list[EvidenceNode], exclude_types: list[str] | None = None) -> IndexStatus:
        with self._lock:
            self._excluded_types = set(exclude_types or [])
            persistent: list[EvidenceNode] = []
            ephemeral = 0
            for node in nodes:
                if node.evidence_type in self._excluded_types:
                    continue
                if self._is_ephemeral(node):
                    ephemeral += 1
                    continue
                persistent.append(node)
            canonical = self._latest_by_key(persistent)
            self._ephemeral_node_count += ephemeral
            self._deduplicated_count += max(0, len(persistent) - len(canonical))
            self._nodes = {key: canonical[key] for key in sorted(canonical)}
            self._vectors = {key: self._encode_node(node) for key, node in self._nodes.items()}
            self._labels.clear()
            self._key_labels.clear()
            self._index = None
            keys = list(self._nodes)
            self._max_elements = max(100, len(keys) * 2)
            if self._hnswlib is not None and keys:
                self._index = self._hnswlib.Index(space="cosine", dim=self.dimension)
                self._index.init_index(
                    max_elements=self._max_elements,
                    ef_construction=self.ef_construction,
                    M=self.M,
                )
                labels = np.arange(len(keys), dtype=np.int64)
                matrix = np.vstack([self._vectors[key] for key in keys])
                self._index.add_items(matrix, labels)
                self._index.set_ef(self.ef_search)
                for label, key in zip(labels.tolist(), keys, strict=True):
                    self._labels[label] = key
                    self._key_labels[key] = label
            else:
                for label, key in enumerate(keys):
                    self._labels[label] = key
                    self._key_labels[key] = label
            self._next_label = len(keys)
            self._index_rebuild_count += 1
            self._last_built_at = utc_now()
            return self.status()

    def upsert(self, nodes: list[EvidenceNode]) -> None:
        with self._lock:
            accepted: list[EvidenceNode] = []
            rebuild_required = False
            for node in nodes:
                if node.evidence_type in self._excluded_types:
                    continue
                if self._is_ephemeral(node):
                    self._ephemeral_node_count += 1
                    if node.quality_label == EvidenceStatus.MISSING:
                        key = evidence_key(node)
                        if key in self._nodes:
                            self._nodes.pop(key, None)
                            self._vectors.pop(key, None)
                            rebuild_required = True
                    continue
                accepted.append(node)
            canonical = self._latest_by_key(accepted)
            self._deduplicated_count += max(0, len(accepted) - len(canonical))
            for key in sorted(canonical):
                node = canonical[key]
                vector = self._encode_node(node)
                existing = key in self._nodes
                self._nodes[key] = node
                self._vectors[key] = vector
                if existing:
                    self._index_update_count += 1
                    self._deduplicated_count += 1
                    label = self._key_labels[key]
                else:
                    label = self._next_label
                    self._next_label += 1
                    self._labels[label] = key
                    self._key_labels[key] = label
                if self._index is not None:
                    if not existing and self._next_label > self._max_elements:
                        self._max_elements = max(self._next_label * 2, self._max_elements * 2)
                        self._index.resize_index(self._max_elements)
                    self._index.add_items(vector.reshape(1, -1), np.asarray([label], dtype=np.int64))
            if rebuild_required:
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
                        key = self._labels[int(label)]
                        results.append((self._nodes[key], float(np.clip(1.0 - distance, 0, 1))))
                else:
                    scored = [
                        (key, float(np.clip(np.dot(query, vector), 0, 1)))
                        for key, vector in self._vectors.items()
                    ]
                    scored.sort(key=lambda item: (-item[1], item[0]))
                    results = [(self._nodes[key], score) for key, score in scored[:limit]]
            duration_ms = (perf_counter() - started) * 1000
            status = self.status()
            metadata = RetrievalMetadata(
                implementation=self.implementation,
                index_node_count=len(self._nodes),
                vector_dimension=self.dimension,
                M=self.M,
                ef_construction=self.ef_construction,
                ef_search=self.ef_search,
                top_k=top_k or self.top_k,
                candidate_count=len(results),
                canonical_node_count=status.canonical_node_count,
                ephemeral_node_count=status.ephemeral_node_count,
                index_update_count=status.index_update_count,
                index_rebuild_count=status.index_rebuild_count,
                deduplicated_count=status.deduplicated_count,
                duration_ms=round(duration_ms, 4),
                empty_index=not self._nodes,
                degraded=self.degraded,
                degradation_reason=self.degradation_reason,
                excluded_types=sorted(self._excluded_types),
                last_built_at=self._last_built_at,
            )
            return results, metadata

    def label_for_key(self, key: str) -> int | None:
        with self._lock:
            return self._key_labels.get(key)

    def status(self) -> IndexStatus:
        return IndexStatus(
            implementation=self.implementation,
            node_count=len(self._nodes),
            canonical_node_count=len(self._nodes),
            ephemeral_node_count=self._ephemeral_node_count,
            index_update_count=self._index_update_count,
            index_rebuild_count=self._index_rebuild_count,
            deduplicated_count=self._deduplicated_count,
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
