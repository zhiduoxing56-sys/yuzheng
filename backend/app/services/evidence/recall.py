from __future__ import annotations

from typing import Any

import numpy as np

from app.models.schemas import EvidenceNode, EvidenceStatus, MandatoryRecallRecord
from app.services.evidence.repository import EvidenceRepository
from app.services.index.hnsw import evidence_text
from app.services.vector.embedding import EmbeddingService


class MandatoryRecallService:
    def __init__(self, repository: EvidenceRepository, embedder: EmbeddingService) -> None:
        self.repository = repository
        self.embedder = embedder

    def _similarity(self, query_vector: list[float], node: EvidenceNode) -> float:
        vector, _ = self.embedder.encode(evidence_text(node))
        return float(np.clip(np.dot(query_vector, vector), 0, 1))

    def supplement(
        self,
        candidates: list[EvidenceNode],
        required_types: list[str],
        query_vector: list[float],
        turn_id: str,
        missing_hard_gate: bool = True,
    ) -> tuple[list[EvidenceNode], list[MandatoryRecallRecord], list[str], list[str]]:
        final_nodes = [node.model_copy(update={"mandatory": False}) for node in candidates]
        records: list[MandatoryRecallRecord] = []
        recalled_types: list[str] = []
        missing_types: list[str] = []

        for evidence_type in required_types:
            candidate_indexes = [
                index for index, node in enumerate(final_nodes) if node.evidence_type == evidence_type
            ]
            candidate_ids = [final_nodes[index].node_id for index in candidate_indexes]
            latest = self.repository.latest_resolved(evidence_type)
            matching_index = next(
                (
                    index
                    for index in candidate_indexes
                    if latest is not None
                    and final_nodes[index].node_id == latest.node_id
                ),
                None,
            )
            if matching_index is not None:
                final_nodes[matching_index] = final_nodes[matching_index].model_copy(
                    update={
                        "mandatory": True,
                        "metadata": {
                            **final_nodes[matching_index].metadata,
                            "retrieval_origin": "semantic_retrieval",
                            "required_resolution": True,
                        },
                    }
                )
                records.append(
                    MandatoryRecallRecord(
                        evidence_type=evidence_type,
                        status=(
                            "ALREADY_COVERED"
                            if latest.quality_label
                            in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
                            else latest.quality_label.value
                        ),
                        candidate_node_ids=candidate_ids,
                        recalled_node_id=latest.node_id,
                        source=latest.source,
                        retrieval_origin="HNSW",
                        reason="语义候选已包含最新可用强制证据",
                    )
                )
                continue

            if latest is not None:
                recalled = latest.model_copy(
                    update={
                        "mandatory": True,
                        "semantic_similarity": round(self._similarity(query_vector, latest), 6),
                        "metadata": {
                            **latest.metadata,
                            "retrieval_origin": "mandatory_recall",
                            "recalled_from_stream": evidence_type,
                            "required_resolution": True,
                        },
                    }
                )
                final_nodes.append(recalled)
                recalled_types.append(evidence_type)
                records.append(
                    MandatoryRecallRecord(
                        evidence_type=evidence_type,
                        status=(
                            "RECALLED"
                            if latest.quality_label
                            in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
                            else latest.quality_label.value
                        ),
                        candidate_node_ids=candidate_ids,
                        recalled_node_id=recalled.node_id,
                        source=recalled.source,
                        retrieval_origin="MANDATORY_RECALL",
                        reason="普通语义候选未覆盖，已从最新证据流补召",
                    )
                )
                continue

            missing = self.repository.create_missing(
                evidence_type,
                turn_id,
                "最新证据不可用、过期、篡改或证据流为空",
                missing_hard_gate=missing_hard_gate,
            )
            final_nodes.append(missing)
            missing_types.append(evidence_type)
            records.append(
                MandatoryRecallRecord(
                    evidence_type=evidence_type,
                    status="MISSING",
                    candidate_node_ids=candidate_ids,
                    recalled_node_id=missing.node_id,
                    source=missing.source,
                    retrieval_origin="NONE",
                    reason="强制补召失败，已生成 MISSING 节点",
                )
            )

        return final_nodes, records, recalled_types, missing_types
