from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from app.core.config import PROJECT_ROOT
from app.models.knowledge import KnowledgeNode, load_trusted_nodes
from app.models.schemas import EvidenceDemand, IntentEvidenceDemand
from app.services.evidence.demand import EvidenceDemandService
from app.services.vector.embedding import EmbeddingService


def knowledge_text(node: KnowledgeNode) -> str:
    """知识节点的检索文本（对齐 hnsw.py 的字段拼接风格）。"""
    parts = [
        node.title,
        node.semantic_description,
        node.canonical_action,
        *(node.conditions),
        *(f"REQUIRED {evidence}" for evidence in node.required_evidence),
    ]
    return " ".join(part for part in parts if part)


class TrustedKnowledgeIndexService:
    """Trusted 安全知识节点索引，供在线裁决辅助证据需求。

    复用主系统 embedder（bge 768 维）与 hnswlib cosine 模式；知识库为空/缺失时优雅降级。
    """

    def __init__(
        self,
        config: dict[str, Any],
        embedder: EmbeddingService,
        canonical_types: frozenset[str],
    ) -> None:
        self._enabled = bool(config.get("enabled", True))
        raw_path = str(config.get("data_path", "data/knowledge/trusted_nodes.jsonl"))
        self._data_path = Path(raw_path)
        if not self._data_path.is_absolute():
            self._data_path = PROJECT_ROOT / self._data_path
        self._top_k = int(config.get("top_k", 5))
        self._m = int(config.get("M", 16))
        self._ef_construction = int(config.get("ef_construction", 200))
        self._ef_search = int(config.get("ef_search", 30))
        self._min_similarity = float(config.get("min_similarity", 0.6))
        self._embedder = embedder
        self._canonical_types = frozenset(canonical_types)
        self._dimension = int(embedder.dimension)
        self._ready = False
        self._nodes: list[KnowledgeNode] = []
        self._vectors: np.ndarray | None = None
        self._index: Any | None = None
        self._degraded = False
        self._load_error: str | None = None

    # ------------------------------------------------------------- 生命周期

    def load(self) -> None:
        """读取 data_path JSONL 并构建索引；文件缺失/异常置 ready=False，绝不 raise。"""
        if not self._enabled:
            self._ready = False
            return
        try:
            nodes = load_trusted_nodes(self._data_path, self._canonical_types)
            self._build(nodes)
            self._ready = bool(nodes)
        except Exception as exc:  # 知识库异常不影响在线裁决
            self._ready = False
            self._load_error = f"{type(exc).__name__}: {exc}"

    def _build(self, nodes: list[KnowledgeNode]) -> None:
        if not nodes:
            self._nodes = []
            self._vectors = None
            self._index = None
            return
        vectors = np.vstack(
            [self._encode_node(node) for node in nodes]
        ).astype(np.float32)
        try:
            import hnswlib
        except Exception:
            self._degraded = True
            self._index = None
        else:
            self._degraded = False
            index = hnswlib.Index(space="cosine", dim=self._dimension)
            index.init_index(
                max_elements=max(10, len(nodes)),
                ef_construction=self._ef_construction,
                M=self._m,
            )
            index.add_items(vectors, np.arange(len(nodes), dtype=np.int64))
            index.set_ef(self._ef_search)
            self._index = index
        self._nodes = nodes
        self._vectors = vectors

    def _encode_node(self, node: KnowledgeNode) -> np.ndarray:
        # 优先复用情报侧预计算向量（校验维度 + L2 归一化），否则用 knowledge_text 嵌入
        if node.vector and len(node.vector) == self._dimension:
            vector = np.asarray(node.vector, dtype=np.float32)
            norm = float(np.linalg.norm(vector))
            return vector / norm if norm > 0 else np.zeros(
                self._dimension, dtype=np.float32
            )
        vector, _ = self._embedder.encode(knowledge_text(node))
        return np.asarray(vector, dtype=np.float32)

    # ------------------------------------------------------------- 检索与增强

    def search(
        self, query_vector: list[float], top_k: int | None = None
    ) -> list[tuple[KnowledgeNode, float]]:
        """返回 (节点, 相似度) 列表；相似度 = clip(1 - cosine_distance, 0, 1)。"""
        if not self._ready or not self._nodes:
            return []
        k = min(top_k or self._top_k, len(self._nodes))
        query = np.asarray(query_vector, dtype=np.float32)
        if self._index is not None:
            labels, distances = self._index.knn_query(query.reshape(1, -1), k=k)
            items: list[tuple[KnowledgeNode, float]] = []
            for idx, label in enumerate(labels[0].tolist()):
                if 0 <= label < len(self._nodes):
                    similarity = float(np.clip(1.0 - float(distances[0][idx]), 0.0, 1.0))
                    items.append((self._nodes[label], similarity))
            return items
        # hnswlib 不可用：精确余弦回退（点积，向量已归一化）
        dots = self._vectors @ query
        order = np.argsort(-dots)[:k].tolist()
        return [
            (self._nodes[i], float(np.clip(float(dots[i]), 0.0, 1.0)))
            for i in order
            if 0 <= i < len(self._nodes)
        ]

    def status(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "ready": self._ready,
            "data_path": str(self._data_path),
            "node_count": len(self._nodes),
            "top_k": self._top_k,
            "degraded": self._degraded,
            "load_error": self._load_error,
        }

    def augment(self, demand: EvidenceDemand) -> EvidenceDemand:
        """把命中知识节点的 required_evidence 并集追加进各 intent 的 required_types。

        只做确定性精确匹配：知识节点 canonical_action 必须与意图 intent_id 完全一致，
        避免跨意图串扰（如「打开车门」误命中「打开车窗」节点导致其证据被强制追加）。
        追加后重算 query_text / query_vector，保证下游证据 HNSW 检索一致。
        知识库未就绪时原样返回，不影响现有裁决。
        """
        if not self._ready or not demand.intent_demands:
            return demand
        nodes_by_action: dict[str, list[KnowledgeNode]] = {}
        for node in self._nodes:
            nodes_by_action.setdefault(node.canonical_action, []).append(node)
        augmented: list[IntentEvidenceDemand] = []
        for intent_demand in demand.intent_demands:
            chosen = nodes_by_action.get(intent_demand.intent_id, [])
            added: list[str] = []
            hit_nodes: list[dict[str, Any]] = []
            for node in chosen:
                hit_nodes.append(
                    {
                        "node_id": node.node_id,
                        "title": node.title,
                        "canonical_action": node.canonical_action,
                        "trust_level": node.trust_level,
                    }
                )
                for evidence in node.required_evidence:
                    if (
                        evidence in self._canonical_types
                        and evidence not in intent_demand.required_types
                        and evidence not in added
                    ):
                        added.append(evidence)
            if not added:
                augmented.append(intent_demand)
                continue
            added_set = set(added)
            draft = intent_demand.model_copy(
                update={
                    "required_types": [*intent_demand.required_types, *added],
                    "optional_types": [
                        item
                        for item in intent_demand.optional_types
                        if item not in added_set
                    ],
                    "knowledge_augmented_types": added,
                    "knowledge_hits": hit_nodes,
                }
            )
            query_text = EvidenceDemandService.query_text_for(draft)
            query_vector, vectorization_metadata = self._embedder.encode(query_text)
            augmented.append(
                draft.model_copy(
                    update={
                        "query_text": query_text,
                        "query_vector": query_vector,
                        "vectorization_metadata": vectorization_metadata,
                    }
                )
            )
        return demand.model_copy(update={"intent_demands": augmented})
