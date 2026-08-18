from __future__ import annotations

import numpy as np

from app.models.schemas import (
    EvidenceNode,
    EvidenceStatus,
    IntentEvidenceBinding,
    IntentEvidenceDemand,
    IntentEvidenceResolution,
    MandatoryRecallRecord,
    RetrievalOrigin,
)
from app.services.evidence.catalog import require_canonical_evidence_type
from app.services.evidence.repository import EvidenceRepository
from app.services.evidence.trust import select_canonical_evidence
from app.services.index.hnsw import evidence_text
from app.services.vector.embedding import EmbeddingService


class MandatoryRecallService:
    _DOOR_PHYSICAL_AREAS = frozenset(
        {"LEFT_FRONT", "RIGHT_FRONT", "LEFT_REAR", "RIGHT_REAR"}
    )

    def __init__(self, repository: EvidenceRepository, embedder: EmbeddingService) -> None:
        self.repository = repository
        self.embedder = embedder

    def _similarity(self, query_vector: list[float], node: EvidenceNode) -> float:
        vector, _ = self.embedder.encode(evidence_text(node))
        return float(np.clip(np.dot(query_vector, vector), 0, 1))

    @classmethod
    def _matching_candidates(
        cls,
        candidates: list[EvidenceNode],
        demand: IntentEvidenceDemand,
        evidence_type: str,
    ) -> list[EvidenceNode]:
        matching = [
            node for node in candidates if node.evidence_type == evidence_type
        ]
        if (
            evidence_type == "DOOR_STATE"
            and demand.area in cls._DOOR_PHYSICAL_AREAS
        ):
            return [
                node
                for node in matching
                if node.metadata.get("area") == demand.area
            ]
        return matching

    def _latest_for_demand(
        self, demand: IntentEvidenceDemand, evidence_type: str
    ) -> EvidenceNode | None:
        if (
            evidence_type == "DOOR_STATE"
            and demand.area in self._DOOR_PHYSICAL_AREAS
        ):
            return self.repository.latest_resolved_for_area(
                evidence_type, demand.area
            )
        return self.repository.latest_resolved(evidence_type)

    def resolve(
        self,
        candidates: list[EvidenceNode],
        demand: IntentEvidenceDemand,
        turn_id: str,
        missing_hard_gate: bool = True,
        candidate_similarities: dict[str, float] | None = None,
    ) -> tuple[list[EvidenceNode], IntentEvidenceResolution]:
        candidate_similarities = candidate_similarities or {}
        final_nodes = list(candidates)
        records: list[MandatoryRecallRecord] = []
        missing_types: list[str] = []
        missing_knowledge_types: list[str] = []
        bindings: list[IntentEvidenceBinding] = []

        hard_required = set(demand.required_types)
        demanded_types = list(
            dict.fromkeys(
                [*demand.required_types, *demand.knowledge_required_types]
            )
        )
        for evidence_type in demanded_types:
            requirement_level = (
                "REQUIRED" if evidence_type in hard_required else "KNOWLEDGE_REQUIRED"
            )
            missing_status = (
                "MISSING" if requirement_level == "REQUIRED" else "KNOWLEDGE_MISSING"
            )
            effective_missing_hard_gate = (
                missing_hard_gate if requirement_level == "REQUIRED" else False
            )
            require_canonical_evidence_type(evidence_type)
            matching_candidates = self._matching_candidates(
                candidates, demand, evidence_type
            )
            candidate_ids = [node.node_id for node in matching_candidates]
            current_turn_missing = next(
                (
                    node
                    for node in self.repository.turn_nodes(turn_id)
                    if node.evidence_type == evidence_type
                    and (
                        evidence_type != "DOOR_STATE"
                        or demand.area not in self._DOOR_PHYSICAL_AREAS
                        or node.metadata.get("area") == demand.area
                    )
                    and node.quality_label == EvidenceStatus.MISSING
                    and node.source != "missing_placeholder"
                ),
                None,
            )
            if current_turn_missing is not None:
                missing = self.repository.get_or_create_missing(
                    evidence_type,
                    turn_id,
                    missing_hard_gate=effective_missing_hard_gate,
                )
                final_nodes.append(missing)
                (
                    missing_types
                    if requirement_level == "REQUIRED"
                    else missing_knowledge_types
                ).append(evidence_type)
                bindings.append(
                    IntentEvidenceBinding(
                        clause_index=demand.clause_index,
                        intent_id=demand.intent_id,
                        evidence_type=evidence_type,
                        requirement_level=requirement_level,
                        node_id=missing.node_id,
                        resolution_status=missing_status,
                        retrieval_origin=RetrievalOrigin.NONE,
                        semantic_similarity=None,
                    )
                )
                records.append(
                    MandatoryRecallRecord(
                        clause_index=demand.clause_index,
                        intent_id=demand.intent_id,
                        evidence_type=evidence_type,
                        status="MISSING",
                        candidate_node_ids=candidate_ids,
                        recalled_node_id=missing.node_id,
                        source=missing.source,
                        retrieval_origin=RetrievalOrigin.NONE,
                        reason=(
                            "当前 occurrence 的本轮 observation 不可用，"
                            "使用本轮共享 MISSING 节点"
                        ),
                    )
                )
                continue
            if matching_candidates:
                selected = select_canonical_evidence(
                    [evidence_type], matching_candidates
                )[0]
                bindings.append(
                    IntentEvidenceBinding(
                        clause_index=demand.clause_index,
                        intent_id=demand.intent_id,
                        evidence_type=evidence_type,
                        requirement_level=requirement_level,
                        node_id=selected.node_id,
                        resolution_status="RETRIEVED",
                        retrieval_origin=RetrievalOrigin.HNSW,
                        semantic_similarity=candidate_similarities.get(selected.node_id),
                    )
                )
                records.append(
                    MandatoryRecallRecord(
                        clause_index=demand.clause_index,
                        intent_id=demand.intent_id,
                        evidence_type=evidence_type,
                        status=(
                            "ALREADY_COVERED"
                            if selected.quality_label
                            in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
                            else selected.quality_label.value
                        ),
                        candidate_node_ids=candidate_ids,
                        recalled_node_id=selected.node_id,
                        source=selected.source,
                        retrieval_origin=RetrievalOrigin.HNSW,
                        reason="当前 Intent 的 HNSW 候选已覆盖 required evidence",
                    )
                )
                continue

            latest = self._latest_for_demand(demand, evidence_type)
            if latest is not None:
                if latest.quality_label == EvidenceStatus.MISSING:
                    missing = self.repository.get_or_create_missing(
                        evidence_type,
                        turn_id,
                        missing_hard_gate=effective_missing_hard_gate,
                    )
                    final_nodes.append(missing)
                    (
                        missing_types
                        if requirement_level == "REQUIRED"
                        else missing_knowledge_types
                    ).append(evidence_type)
                    bindings.append(
                        IntentEvidenceBinding(
                            clause_index=demand.clause_index,
                            intent_id=demand.intent_id,
                            evidence_type=evidence_type,
                            requirement_level=requirement_level,
                            node_id=missing.node_id,
                            resolution_status=missing_status,
                            retrieval_origin=RetrievalOrigin.NONE,
                            semantic_similarity=None,
                        )
                    )
                    records.append(
                        MandatoryRecallRecord(
                            clause_index=demand.clause_index,
                            intent_id=demand.intent_id,
                            evidence_type=evidence_type,
                            status="MISSING",
                            candidate_node_ids=candidate_ids,
                            recalled_node_id=missing.node_id,
                            source=missing.source,
                            retrieval_origin=RetrievalOrigin.NONE,
                            reason="Newest exact-type observation is MISSING; using the shared turn placeholder",
                        )
                    )
                    continue

                recalled_similarity = round(
                    self._similarity(demand.query_vector, latest), 6
                )
                final_nodes.append(latest)
                bindings.append(
                    IntentEvidenceBinding(
                        clause_index=demand.clause_index,
                        intent_id=demand.intent_id,
                        evidence_type=evidence_type,
                        requirement_level=requirement_level,
                        node_id=latest.node_id,
                        resolution_status="MANDATORY_RECALLED",
                        retrieval_origin=RetrievalOrigin.MANDATORY_RECALL,
                        semantic_similarity=recalled_similarity,
                    )
                )
                records.append(
                    MandatoryRecallRecord(
                        clause_index=demand.clause_index,
                        intent_id=demand.intent_id,
                        evidence_type=evidence_type,
                        status=(
                            "RECALLED"
                            if latest.quality_label
                            in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
                            else latest.quality_label.value
                        ),
                        candidate_node_ids=candidate_ids,
                        recalled_node_id=latest.node_id,
                        source=latest.source,
                        retrieval_origin=RetrievalOrigin.MANDATORY_RECALL,
                        reason="当前 Intent 的 HNSW 候选未覆盖，已从证据流补召",
                    )
                )
                continue

            missing = self.repository.get_or_create_missing(
                evidence_type,
                turn_id,
                missing_hard_gate=effective_missing_hard_gate,
            )
            final_nodes.append(missing)
            (
                missing_types
                if requirement_level == "REQUIRED"
                else missing_knowledge_types
            ).append(evidence_type)
            bindings.append(
                IntentEvidenceBinding(
                    clause_index=demand.clause_index,
                    intent_id=demand.intent_id,
                    evidence_type=evidence_type,
                    requirement_level=requirement_level,
                    node_id=missing.node_id,
                    resolution_status=missing_status,
                    retrieval_origin=RetrievalOrigin.NONE,
                    semantic_similarity=None,
                )
            )
            records.append(
                MandatoryRecallRecord(
                    clause_index=demand.clause_index,
                    intent_id=demand.intent_id,
                    evidence_type=evidence_type,
                    status="MISSING",
                    candidate_node_ids=candidate_ids,
                    recalled_node_id=missing.node_id,
                    source=missing.source,
                    retrieval_origin=RetrievalOrigin.NONE,
                    reason="当前 Intent 强制补召失败，使用本轮共享 MISSING 节点",
                )
            )

        assessment_types = list(
            dict.fromkeys([*demand.assessment_types, *demand.optional_types])
        )
        for evidence_type in assessment_types:
            if (
                evidence_type in hard_required
                or evidence_type in demand.knowledge_required_types
            ):
                continue
            require_canonical_evidence_type(evidence_type)
            optional_candidates = self._matching_candidates(
                candidates, demand, evidence_type
            )
            selected_nodes = select_canonical_evidence(
                [evidence_type], optional_candidates
            )
            selected = selected_nodes[0] if selected_nodes else None
            bindings.append(
                IntentEvidenceBinding(
                    clause_index=demand.clause_index,
                    intent_id=demand.intent_id,
                    evidence_type=evidence_type,
                    requirement_level="ASSESSMENT",
                    node_id=selected.node_id if selected is not None else None,
                    resolution_status=(
                        "RETRIEVED" if selected is not None else "OPTIONAL_NOT_FOUND"
                    ),
                    retrieval_origin=(
                        RetrievalOrigin.HNSW
                        if selected is not None
                        else RetrievalOrigin.NONE
                    ),
                    semantic_similarity=(
                        candidate_similarities.get(selected.node_id)
                        if selected is not None
                        else None
                    ),
                )
            )

        return final_nodes, IntentEvidenceResolution(
            clause_index=demand.clause_index,
            intent_id=demand.intent_id,
            candidate_node_ids=[node.node_id for node in candidates],
            bindings=bindings,
            mandatory_recall_records=records,
            missing_required_types=missing_types,
            missing_knowledge_required_types=missing_knowledge_types,
        )
