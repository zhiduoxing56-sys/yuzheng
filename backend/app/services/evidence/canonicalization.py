from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from typing import Any

from app.models.schemas import EvidenceNode, EvidenceStatus


CANONICALIZATION_SOURCE = "FIELD_LEVEL_EVIDENCE_NODE_MERGE"

_SOURCE_PRIORITY = {
    "REQUIRED_MISSING_OR_TAMPERED": 0,
    "HNSW_QUERY_EVALUATED": 10,
    "MANDATORY_RECALL_EVALUATED": 20,
    "QUALITY_EVALUATED": 30,
    "EVIDENCE_OVERRIDE": 40,
    "EVIDENCE_REPOSITORY": 50,
    "SAFETY_RULE_REPOSITORY": 60,
    "GRAPH_AUXILIARY": 70,
}
_STABLE_SOURCE_PRIORITY = {
    "SAFETY_RULE_REPOSITORY": 0,
    "EVIDENCE_REPOSITORY": 10,
    "EVIDENCE_OVERRIDE": 20,
    "HNSW_QUERY_EVALUATED": 30,
    "MANDATORY_RECALL_EVALUATED": 40,
    "QUALITY_EVALUATED": 50,
    "REQUIRED_MISSING_OR_TAMPERED": 60,
    "GRAPH_AUXILIARY": 70,
}
_SEVERE_QUALITY_PRIORITY = {
    EvidenceStatus.TAMPERED: 0,
    EvidenceStatus.MISSING: 1,
}
_STABLE_FIELDS = (
    "evidence_type",
    "source",
    "unit",
)
_QUERY_FIELDS = (
    "semantic_similarity",
    "mandatory",
)
_QUALITY_FIELDS = (
    "freshness",
    "consistency",
    "availability",
    "quality_label",
    "integrity_hash",
)
_CONTENT_FIELDS = (
    "value",
    "timestamp",
    "expires_at",
)
_DISPLAY_FIELDS = (
    "layer",
    "security_class",
    "security_rank",
    "base_level",
    "safety_adjustment",
    "hnsw_max_layer",
    "hnsw_layer_memberships",
    "security_classification_source",
    "formula_source",
)
_QUERY_METADATA_KEYS = {
    "retrieval_origin",
    "retrieval_rank",
    "mandatory_recall",
    "runtime_graph_history",
}
_STABLE_METADATA_KEYS = {
    "original_evidence_type",
    "canonical_evidence_type",
    "mapping_source",
    "entity_id",
    "rule_id",
    "area",
    "unit",
    "display_name",
}
_QUALITY_METADATA_KEYS = {
    "integrity_result",
    "integrity_payload",
    "expected_integrity_hash",
    "quality_source",
}


def evaluated_node_source(node: EvidenceNode) -> str:
    """Return an auditable source role without using a runtime UUID."""

    if node.quality_label in {EvidenceStatus.MISSING, EvidenceStatus.TAMPERED}:
        return "REQUIRED_MISSING_OR_TAMPERED"
    origin = str(node.metadata.get("retrieval_origin", "")).upper()
    if "MANDATORY" in origin:
        return "MANDATORY_RECALL_EVALUATED"
    if origin in {"SEMANTIC_RETRIEVAL", "HNSW", "BOTH"}:
        return "HNSW_QUERY_EVALUATED"
    return "QUALITY_EVALUATED"


def _priority(source: str, *, stable: bool = False) -> tuple[int, str]:
    priorities = _STABLE_SOURCE_PRIORITY if stable else _SOURCE_PRIORITY
    return priorities.get(source, 1000), source


def _stable_value(value: Any) -> str:
    if hasattr(value, "value"):
        value = value.value
    if hasattr(value, "isoformat"):
        value = value.isoformat()
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _missing(value: Any) -> bool:
    return value is None or value == ""


def _select(
    contributions: Sequence[tuple[str, EvidenceNode]],
    field: str,
    *,
    stable: bool = False,
) -> tuple[Any, str, bool]:
    candidates = [
        (source, getattr(node, field))
        for source, node in contributions
        if not _missing(getattr(node, field))
    ]
    if not candidates:
        source, node = min(contributions, key=lambda item: _priority(item[0], stable=stable))
        return getattr(node, field), source, False
    candidates.sort(key=lambda item: (_priority(item[0], stable=stable), _stable_value(item[1])))
    distinct = {_stable_value(value) for _, value in candidates}
    source, value = candidates[0]
    return value, source, len(distinct) > 1


def _select_quality_label(
    contributions: Sequence[tuple[str, EvidenceNode]],
) -> tuple[EvidenceStatus, str, bool]:
    severe = [
        (source, node.quality_label)
        for source, node in contributions
        if node.quality_label in _SEVERE_QUALITY_PRIORITY
    ]
    candidates = severe or [(source, node.quality_label) for source, node in contributions]
    candidates.sort(
        key=lambda item: (
            _SEVERE_QUALITY_PRIORITY.get(item[1], 100),
            _priority(item[0]),
            item[1].value,
        )
    )
    source, value = candidates[0]
    return value, source, len({item.value for _, item in candidates}) > 1


def _metadata_priority(key: str, source: str) -> tuple[int, str]:
    if key in _STABLE_METADATA_KEYS:
        return _priority(source, stable=True)
    if key in _QUERY_METADATA_KEYS or key.startswith("retrieval_"):
        return _priority(source)
    if key in _QUALITY_METADATA_KEYS or key.startswith("quality_"):
        return _priority(source)
    return _priority(source)


def _merge_one(contributions: Sequence[tuple[str, EvidenceNode]]) -> EvidenceNode:
    ordered = sorted(
        contributions,
        key=lambda item: (
            _priority(item[0]),
            _stable_value(
                item[1].model_dump(
                    mode="json",
                    exclude={
                        "canonicalization_source",
                        "merged_node_sources",
                        "field_resolution",
                        "canonicalization_warnings",
                    },
                )
            ),
        ),
    )
    base_source, base = ordered[0]
    updates: dict[str, Any] = {}
    resolution: dict[str, str] = {}
    conflict_fields: set[str] = set()

    for field in _STABLE_FIELDS:
        value, source, conflict = _select(ordered, field, stable=True)
        updates[field] = value
        resolution[field] = source
        if conflict:
            conflict_fields.add(field)

    for field in (*_QUERY_FIELDS, *_CONTENT_FIELDS, *_DISPLAY_FIELDS):
        value, source, conflict = _select(ordered, field)
        updates[field] = value
        resolution[field] = source
        if conflict:
            conflict_fields.add(field)

    quality_label, quality_source, quality_conflict = _select_quality_label(ordered)
    updates["quality_label"] = quality_label
    resolution["quality_label"] = quality_source
    if quality_conflict:
        conflict_fields.add("quality_label")

    severe_source = quality_source if quality_label in _SEVERE_QUALITY_PRIORITY else None
    for field in ("freshness", "consistency", "availability", "integrity_hash"):
        if severe_source is not None:
            severe_nodes = [item for item in ordered if item[0] == severe_source]
            value, source, conflict = _select(severe_nodes, field)
        else:
            value, source, conflict = _select(ordered, field)
        updates[field] = value
        resolution[field] = source
        if conflict:
            conflict_fields.add(field)

    if quality_label == EvidenceStatus.MISSING:
        updates["value"] = None
        resolution["value"] = quality_source
    if quality_label in _SEVERE_QUALITY_PRIORITY:
        updates["availability"] = 0.0
        resolution["availability"] = quality_source

    metadata: dict[str, Any] = {}
    metadata_keys = sorted({key for _, node in ordered for key in node.metadata})
    for key in metadata_keys:
        candidates = [
            (source, node.metadata[key])
            for source, node in ordered
            if key in node.metadata and not _missing(node.metadata[key])
        ]
        if not candidates:
            continue
        candidates.sort(key=lambda item: (_metadata_priority(key, item[0]), _stable_value(item[1])))
        source, value = candidates[0]
        metadata[key] = value
        resolution[f"metadata.{key}"] = source
        if len({_stable_value(item) for _, item in candidates}) > 1:
            conflict_fields.add(f"metadata.{key}")
    updates["metadata"] = metadata

    warnings = [
        f"CANONICAL_FIELD_CONFLICT:{field}:RESOLVED_BY:{resolution[field]}"
        for field in sorted(conflict_fields)
    ]
    sources = sorted({source for source, _ in ordered}, key=_priority)
    updates.update(
        {
            "canonicalization_source": CANONICALIZATION_SOURCE,
            "merged_node_sources": sources,
            "field_resolution": dict(sorted(resolution.items())),
            "canonicalization_warnings": warnings,
        }
    )
    # Warnings are persisted on the canonical EvidenceNode so audit replay does
    # not depend on process logs and high-volume turns do not emit duplicate noise.
    return base.model_copy(update=updates)


def canonicalize_evidence_nodes(
    source_groups: Iterable[tuple[str, Iterable[EvidenceNode]]],
) -> list[EvidenceNode]:
    """Merge duplicate node IDs by field category with deterministic source priorities.

    Stable identity fields prefer repository/rule definitions. Query, quality, content,
    and display fields prefer the current evaluated node and are never replaced by a
    repository default. MISSING/TAMPERED quality is safety-preserving and cannot be
    downgraded. Ordering and runtime UUID values do not decide field precedence.
    """

    grouped: dict[str, list[tuple[str, EvidenceNode]]] = {}
    for source, nodes in source_groups:
        for node in nodes:
            grouped.setdefault(node.node_id, []).append((source, node))
    return [_merge_one(grouped[node_id]) for node_id in sorted(grouped)]
