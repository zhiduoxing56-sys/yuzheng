from __future__ import annotations

from dataclasses import dataclass

from app.models.schemas import (
    IntentEvidenceBinding,
    IntentEvidenceResolution,
    MandatoryRecallRecord,
    RetrievalOrigin,
)


OccurrenceKey = tuple[int, str]


def _stable_unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


@dataclass(frozen=True)
class EvidenceResolutionProjection:
    by_occurrence: dict[OccurrenceKey, IntentEvidenceResolution]
    required_node_ids_by_occurrence: dict[OccurrenceKey, frozenset[str]]
    resolved_node_ids_by_occurrence: dict[OccurrenceKey, frozenset[str]]
    required_types_by_occurrence: dict[OccurrenceKey, list[str]]
    knowledge_required_types_by_occurrence: dict[OccurrenceKey, list[str]]
    validated_types_by_occurrence: dict[OccurrenceKey, list[str]]
    retrieval_origins_by_occurrence: dict[OccurrenceKey, dict[str, RetrievalOrigin]]
    required_semantic_similarities_by_occurrence: dict[OccurrenceKey, list[float]]
    resolved_semantic_similarities_by_occurrence: dict[OccurrenceKey, list[float]]
    required_types_union: list[str]
    validated_types_union: list[str]
    missing_required_types_union: list[str]
    missing_knowledge_required_types_union: list[str]
    recalled_types_union: list[str]
    required_node_ids: frozenset[str]
    resolved_physical_node_ids: frozenset[str]
    mandatory_recall_records: list[MandatoryRecallRecord]
    retrieval_origins_by_node_id: dict[str, RetrievalOrigin]
    required_semantic_similarities: list[float]
    resolved_semantic_similarities: list[float]
    semantic_similarity_by_node_id: dict[str, float]

    def required_bindings(
        self, clause_index: int, intent_id: str
    ) -> list[IntentEvidenceBinding]:
        resolution = self.by_occurrence[(clause_index, intent_id)]
        return [
            binding
            for binding in resolution.bindings
            if binding.requirement_level == "REQUIRED"
        ]

    def optional_bindings(
        self, clause_index: int, intent_id: str
    ) -> list[IntentEvidenceBinding]:
        return [
            binding
            for binding in self.by_occurrence[(clause_index, intent_id)].bindings
            if binding.requirement_level in {"ASSESSMENT", "OPTIONAL"}
        ]

    def resolved_bindings(
        self, clause_index: int, intent_id: str
    ) -> list[IntentEvidenceBinding]:
        return [
            binding
            for binding in self.by_occurrence[(clause_index, intent_id)].bindings
            if binding.node_id is not None
            and binding.resolution_status in {"RETRIEVED", "MANDATORY_RECALLED"}
        ]

    def missing_bindings(
        self, clause_index: int, intent_id: str
    ) -> list[IntentEvidenceBinding]:
        return [
            binding
            for binding in self.by_occurrence[(clause_index, intent_id)].bindings
            if binding.resolution_status
            in {"MISSING", "KNOWLEDGE_MISSING", "OPTIONAL_NOT_FOUND"}
        ]


def project_evidence_resolutions(
    resolutions: list[IntentEvidenceResolution],
) -> EvidenceResolutionProjection:
    by_occurrence: dict[OccurrenceKey, IntentEvidenceResolution] = {}
    required_node_ids_by_occurrence: dict[OccurrenceKey, frozenset[str]] = {}
    resolved_node_ids_by_occurrence: dict[OccurrenceKey, frozenset[str]] = {}
    required_types_by_occurrence: dict[OccurrenceKey, list[str]] = {}
    knowledge_required_types_by_occurrence: dict[OccurrenceKey, list[str]] = {}
    validated_types_by_occurrence: dict[OccurrenceKey, list[str]] = {}
    retrieval_origins_by_occurrence: dict[OccurrenceKey, dict[str, RetrievalOrigin]] = {}
    required_similarities_by_occurrence: dict[OccurrenceKey, list[float]] = {}
    resolved_similarities_by_occurrence: dict[OccurrenceKey, list[float]] = {}
    required_types: list[str] = []
    validated_types: list[str] = []
    missing_types: list[str] = []
    missing_knowledge_types: list[str] = []
    recalled_types: list[str] = []
    required_node_ids: set[str] = set()
    resolved_node_ids: set[str] = set()
    records: list[MandatoryRecallRecord] = []
    origins_by_node: dict[str, set[RetrievalOrigin]] = {}
    required_similarities: list[float] = []
    resolved_similarities: list[float] = []
    similarities_by_node: dict[str, list[float]] = {}

    for resolution in resolutions:
        key = (resolution.clause_index, resolution.intent_id)
        if key in by_occurrence:
            raise ValueError(
                "IntentEvidenceResolution occurrence 重复: "
                f"{resolution.clause_index}:{resolution.intent_id}"
            )
        by_occurrence[key] = resolution
        occurrence_required_ids: set[str] = set()
        occurrence_resolved_ids: set[str] = set()
        occurrence_required_types: list[str] = []
        occurrence_knowledge_required_types: list[str] = []
        occurrence_validated_types: list[str] = []
        occurrence_origins: dict[str, set[RetrievalOrigin]] = {}
        occurrence_required_similarities: list[float] = []
        occurrence_resolved_similarities: list[float] = []
        missing_types.extend(resolution.missing_required_types)
        missing_knowledge_types.extend(resolution.missing_knowledge_required_types)
        records.extend(resolution.mandatory_recall_records)
        for binding in resolution.bindings:
            if (binding.clause_index, binding.intent_id) != key:
                raise ValueError("IntentEvidenceBinding 与所属 resolution occurrence 不一致")
            if binding.node_id is not None:
                validated_types.append(binding.evidence_type)
                occurrence_validated_types.append(binding.evidence_type)
            if binding.requirement_level == "REQUIRED":
                required_types.append(binding.evidence_type)
                occurrence_required_types.append(binding.evidence_type)
                if binding.node_id is not None:
                    occurrence_required_ids.add(binding.node_id)
                    required_node_ids.add(binding.node_id)
                    required_similarities.append(binding.semantic_similarity or 0.0)
                    occurrence_required_similarities.append(binding.semantic_similarity or 0.0)
            elif binding.requirement_level == "KNOWLEDGE_REQUIRED":
                occurrence_knowledge_required_types.append(binding.evidence_type)
            if binding.resolution_status == "MANDATORY_RECALLED":
                recalled_types.append(binding.evidence_type)
            if binding.node_id is not None:
                occurrence_resolved_ids.add(binding.node_id)
                resolved_node_ids.add(binding.node_id)
                similarity = binding.semantic_similarity or 0.0
                resolved_similarities.append(similarity)
                occurrence_resolved_similarities.append(similarity)
                similarities_by_node.setdefault(binding.node_id, []).append(similarity)
                origins_by_node.setdefault(binding.node_id, set()).add(
                    binding.retrieval_origin
                )
                occurrence_origins.setdefault(binding.node_id, set()).add(
                    binding.retrieval_origin
                )
        required_node_ids_by_occurrence[key] = frozenset(occurrence_required_ids)
        resolved_node_ids_by_occurrence[key] = frozenset(occurrence_resolved_ids)
        required_types_by_occurrence[key] = _stable_unique(occurrence_required_types)
        knowledge_required_types_by_occurrence[key] = _stable_unique(
            occurrence_knowledge_required_types
        )
        validated_types_by_occurrence[key] = _stable_unique(occurrence_validated_types)
        required_similarities_by_occurrence[key] = occurrence_required_similarities
        resolved_similarities_by_occurrence[key] = occurrence_resolved_similarities
        retrieval_origins_by_occurrence[key] = {
            node_id: (
                RetrievalOrigin.BOTH
                if {RetrievalOrigin.HNSW, RetrievalOrigin.MANDATORY_RECALL} <= origins
                else next(iter(origins), RetrievalOrigin.NONE)
            )
            for node_id, origins in occurrence_origins.items()
        }

    origin_projection: dict[str, RetrievalOrigin] = {}
    for node_id, origins in origins_by_node.items():
        effective = origins - {RetrievalOrigin.NONE}
        if {
            RetrievalOrigin.HNSW,
            RetrievalOrigin.MANDATORY_RECALL,
        } <= effective or RetrievalOrigin.BOTH in effective:
            origin_projection[node_id] = RetrievalOrigin.BOTH
        elif RetrievalOrigin.MANDATORY_RECALL in effective:
            origin_projection[node_id] = RetrievalOrigin.MANDATORY_RECALL
        elif RetrievalOrigin.HNSW in effective:
            origin_projection[node_id] = RetrievalOrigin.HNSW
        else:
            origin_projection[node_id] = RetrievalOrigin.NONE

    return EvidenceResolutionProjection(
        by_occurrence=by_occurrence,
        required_node_ids_by_occurrence=required_node_ids_by_occurrence,
        resolved_node_ids_by_occurrence=resolved_node_ids_by_occurrence,
        required_types_by_occurrence=required_types_by_occurrence,
        knowledge_required_types_by_occurrence=knowledge_required_types_by_occurrence,
        validated_types_by_occurrence=validated_types_by_occurrence,
        retrieval_origins_by_occurrence=retrieval_origins_by_occurrence,
        required_semantic_similarities_by_occurrence=required_similarities_by_occurrence,
        resolved_semantic_similarities_by_occurrence=resolved_similarities_by_occurrence,
        required_types_union=_stable_unique(required_types),
        validated_types_union=_stable_unique(validated_types),
        missing_required_types_union=_stable_unique(missing_types),
        missing_knowledge_required_types_union=_stable_unique(missing_knowledge_types),
        recalled_types_union=_stable_unique(recalled_types),
        required_node_ids=frozenset(required_node_ids),
        resolved_physical_node_ids=frozenset(resolved_node_ids),
        mandatory_recall_records=records,
        retrieval_origins_by_node_id=origin_projection,
        required_semantic_similarities=required_similarities,
        resolved_semantic_similarities=resolved_similarities,
        semantic_similarity_by_node_id={
            node_id: max(values) for node_id, values in similarities_by_node.items()
        },
    )
