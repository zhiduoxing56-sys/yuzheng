from __future__ import annotations

from collections.abc import Iterable

from app.models.schemas import EvidenceNode, EvidenceStatus


PDF_EVIDENCE_TRUST_VALUES: dict[EvidenceStatus, float] = {
    EvidenceStatus.VALID: 1.0,
    EvidenceStatus.SUSPICIOUS: 0.5,
    EvidenceStatus.STALE: 0.3,
    EvidenceStatus.TAMPERED: 0.0,
    EvidenceStatus.MISSING: 0.0,
}


def evidence_trust_value(status: EvidenceStatus) -> float:
    """Return the report-defined Q(status) value from formulas 2.10-2.14."""

    return PDF_EVIDENCE_TRUST_VALUES[status]


def _selection_key(node: EvidenceNode) -> tuple[str, str]:
    return (
        node.timestamp.isoformat() if node.timestamp else "",
        node.node_id,
    )


def select_canonical_evidence(
    evidence_types: Iterable[str],
    evidence: Iterable[EvidenceNode],
    *,
    allowed_node_ids: Iterable[str] | None = None,
) -> list[EvidenceNode]:
    """Select exactly one final canonical node for each requested evidence type.

    Intent-scoped callers provide allowed_node_ids from canonical bindings.
    Ties use the latest timestamp and then the stable node id. MISSING and
    TAMPERED nodes remain selectable; callers must not silently discard them.
    """

    nodes = list(evidence)
    allowed = set(allowed_node_ids) if allowed_node_ids is not None else None
    selected: list[EvidenceNode] = []
    seen_types: set[str] = set()
    for evidence_type in evidence_types:
        if evidence_type in seen_types:
            continue
        seen_types.add(evidence_type)
        candidates = [
            node
            for node in nodes
            if node.evidence_type == evidence_type
            and (allowed is None or node.node_id in allowed)
        ]
        if candidates:
            selected.append(max(candidates, key=_selection_key))
    return selected


def trust_trace(nodes: Iterable[EvidenceNode]) -> list[dict[str, object]]:
    return [
        {
            "evidence_type": node.evidence_type,
            "selected_node_id": node.node_id,
            "selected_status": node.quality_label.value,
            "trust_value": evidence_trust_value(node.quality_label),
            "selection_source": str(
                node.metadata.get("retrieval_origin", node.source)
            ),
        }
        for node in nodes
    ]
