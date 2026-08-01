from __future__ import annotations

from typing import Any

from app.models.schemas import EvidenceDemand, SemanticFrame
from app.services.vector.embedding import DeterministicHashEmbeddingService, EmbeddingService


class EvidenceDemandService:
    def __init__(self, config: dict[str, Any], embedder: EmbeddingService | None = None) -> None:
        self._mapping = config.get("actions", {})
        self._embedder = embedder or DeterministicHashEmbeddingService()

    def build(self, frame: SemanticFrame) -> tuple[SemanticFrame, EvidenceDemand]:
        rule = self._mapping.get(f"{frame.action}|{frame.target}", {})
        required = list(rule.get("required", []))
        optional = list(rule.get("optional", []))
        updated_frame = frame.model_copy(
            update={
                "required_evidence_types": required,
                "optional_evidence_types": optional,
            }
        )
        query_parts = [frame.action, frame.target, frame.area, frame.risk_level, *frame.risk_tags]
        query_text = " ".join(part for part in query_parts if part and part != "unknown")
        query_vector, vectorization_metadata = self._embedder.encode(query_text)
        demand = EvidenceDemand(
            turn_id=frame.turn_id,
            action=frame.action,
            target=frame.target,
            risk_level=frame.risk_level,
            query_text=query_text,
            query_vector=query_vector,
            vectorization_metadata=vectorization_metadata,
            required_types=required,
            optional_types=optional,
            priority=int(rule.get("priority", 0)),
            retrieval_scope=(
                "diagnostic_only"
                if frame.action == "unknown" or frame.target == "unknown"
                else "control_evidence"
            ),
        )
        return updated_frame, demand
