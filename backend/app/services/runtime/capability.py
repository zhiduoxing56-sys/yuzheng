from __future__ import annotations

from app.models.schemas import RuntimeCapabilityStatus, SemanticControlMode
from app.services.index.hnsw import HNSWIndexService
from app.services.vector.embedding import EmbeddingService


class RuntimeCapabilityService:
    """从当前嵌入与索引实现生成单一、可审计的运行能力快照。"""

    def __init__(self, embedder: EmbeddingService, index: HNSWIndexService) -> None:
        self.embedder = embedder
        self.index = index

    def status(self) -> RuntimeCapabilityStatus:
        index_status = self.index.status()
        real_model = bool(getattr(self.embedder, "real_model_inference", False))
        embedding_reason = getattr(self.embedder, "degradation_reason", None)
        embedding_degraded = not real_model
        reasons: list[str] = []
        if embedding_degraded:
            reasons.append(embedding_reason or "真实语义模型推理不可用")
        if index_status.degraded:
            reasons.append(index_status.degradation_reason or "HNSW索引不可用，使用精确余弦")

        # 精确余弦仍使用真实 BGE 向量，只影响效率；哈希嵌入则限制车控。
        mode = (
            SemanticControlMode.RESTRICTED
            if embedding_degraded
            else SemanticControlMode.FULL
        )
        return RuntimeCapabilityStatus(
            embedding_implementation=str(getattr(self.embedder, "implementation", "unknown")),
            embedding_model=str(getattr(self.embedder, "model_name", "unknown")),
            embedding_dimension=int(getattr(self.embedder, "dimension", 768)),
            real_model_inference=real_model,
            embedding_degraded=embedding_degraded,
            index_implementation=index_status.implementation,
            index_degraded=index_status.degraded,
            semantic_control_mode=mode,
            degradation_reasons=reasons,
        )
