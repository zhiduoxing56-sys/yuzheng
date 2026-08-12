from __future__ import annotations

from datetime import timedelta

import pytest
from pydantic import ValidationError

from app.core.config import load_yaml
from app.models.schemas import (
    EvidenceNode,
    EvidenceStatus,
    MemoryRelationType,
    SecurityClass,
    SemanticFrame,
    SemanticIntent,
    utc_now,
)
from app.services.memory.service import DualMemoryService
from app.services.evidence.catalog import CANONICAL_EVIDENCE_TYPES


LAYER_NAME = {
    SecurityClass.ENTERTAINMENT: "L0_ENTERTAINMENT",
    SecurityClass.COCKPIT: "L1_CABIN",
    SecurityClass.DRIVING: "L2_DRIVING",
    SecurityClass.EMERGENCY: "L3_EMERGENCY",
    SecurityClass.UNCLASSIFIED: "UNCLASSIFIED",
}
RANK = {
    SecurityClass.ENTERTAINMENT: 0,
    SecurityClass.COCKPIT: 1,
    SecurityClass.DRIVING: 2,
    SecurityClass.EMERGENCY: 3,
}


def _frame() -> SemanticFrame:
    return SemanticFrame(
        turn_id="TURN_MEMORY",
        raw_text="test",
        normalized_text="test",
        semantic_confidence=0.9,
        ambiguity_score=0.1,
        semantic_status="OK",
        intents=[
            SemanticIntent(
                clause_index=0,
                clause_text="test",
                intent_id="LANE_CHANGE",
                action="change_lane",
                target="left_lane",
                area="left",
                control_domain="vehicle_control",
                semantic_confidence=0.9,
                ambiguity_score=0.1,
                risk_level="R3",
            )
        ],
    )


def _node(
    node_id: str,
    evidence_type: str,
    security_class: SecurityClass,
    *,
    source: str | None = None,
    sas: float = 0.5,
    quality: EvidenceStatus = EvidenceStatus.VALID,
    timestamp=None,
    metadata: dict | None = None,
) -> EvidenceNode:
    observed_at = utc_now() if timestamp is ... else timestamp
    rank = RANK.get(security_class)
    return EvidenceNode(
        node_id=node_id,
        evidence_type=evidence_type,
        layer=LAYER_NAME[security_class],
        source=source or f"source_{evidence_type}",
        value=None if quality == EvidenceStatus.MISSING else 1,
        timestamp=observed_at,
        expires_at=(observed_at + timedelta(minutes=1)) if observed_at else None,
        freshness=1.0,
        consistency=1.0,
        availability=0.0 if quality == EvidenceStatus.MISSING else 1.0,
        quality_label=quality,
        integrity_hash=f"hash-{node_id}",
        metadata={**(metadata or {}), "test_semantic_similarity": sas},
        security_class=security_class,
        security_rank=rank,
        security_classification_source=(
            "UNCLASSIFIED" if rank is None else "EXISTING_PROJECT_MAPPING"
        ),
    )


def _service() -> DualMemoryService:
    return DualMemoryService(load_yaml("memory.yaml"))


def _similarities(nodes: list[EvidenceNode]) -> dict[str, float]:
    return {
        node.node_id: float(node.metadata["test_semantic_similarity"])
        for node in nodes
    }


def test_four_relation_types_are_evidence_backed_and_auditable() -> None:
    observed_at = utc_now()
    nodes = [
        _node(
            "RADAR",
            "SURROUNDING_OBJECT_STATE",
            SecurityClass.DRIVING,
            timestamp=observed_at,
            metadata={"area": "left_rear"},
        ),
        _node(
            "CAMERA",
            "LANE_STATE",
            SecurityClass.DRIVING,
            timestamp=observed_at + timedelta(milliseconds=20),
            metadata={"area": "left_rear"},
        ),
    ]
    result = _service().propagate(nodes, _frame(), [], semantic_similarity_by_node_id=_similarities(nodes), retrieval_origins={"RADAR": "HNSW", "CAMERA": "MANDATORY_RECALL"})

    assert len(result.relation_edges) == 1
    edge = result.relation_edges[0]
    assert set(edge.relation_types) == set(MemoryRelationType)
    assert edge.created_by == "ALGORITHM_2"
    assert edge.direction == "UNDIRECTED"
    assert edge.criteria["temporal"] == {
        "time_delta_ms": 20.0,
        "sync_window_ms": 30000,
        "window_source": "ENGINEERING_CONFIG",
    }
    assert edge.criteria_sources["spatial"] == "OBSERVED_EVIDENCE_METADATA"
    assert edge.criteria_sources["semantic"] == "ACTION_EVIDENCE_DEPENDENCY"
    assert edge.criteria_sources["sensor_topology"] == "ENGINEERING_CONFIG"
    assert result.retrieval_origins == {"CAMERA": "MANDATORY_RECALL", "RADAR": "HNSW"}


def test_no_real_relation_evidence_means_no_edge() -> None:
    nodes = [
        _node("A", "PARKING_BRAKE_STATE", SecurityClass.DRIVING, timestamp=None),
        _node("B", "MIRROR_STATE", SecurityClass.COCKPIT, timestamp=None),
    ]
    result = _service().propagate(nodes, _frame(), [], semantic_similarity_by_node_id=_similarities(nodes))
    assert result.relation_edges == []
    assert result.propagation_steps == []


def test_sparse_pruning_is_deterministic_and_average_degree_is_bounded() -> None:
    observed_at = utc_now()
    evidence_types = sorted(CANONICAL_EVIDENCE_TYPES)[:20]
    nodes = [
        _node(
            f"N{index:02d}",
            evidence_types[index],
            SecurityClass.DRIVING,
            timestamp=observed_at,
            metadata={"area": "same"},
        )
        for index in range(20)
    ]
    service = _service()
    first = service.propagate(nodes, _frame(), [], semantic_similarity_by_node_id=_similarities(nodes))
    second = service.propagate(list(reversed(nodes)), _frame(), [], semantic_similarity_by_node_id=_similarities(nodes))

    assert first.degree_statistics.candidate_edge_count == 190
    assert first.degree_statistics.retained_edge_count == 160
    assert first.degree_statistics.average_degree == 16
    assert first.degree_statistics.pruned_edge_count == 30
    assert [edge.model_dump() for edge in first.relation_edges] == [
        edge.model_dump() for edge in second.relation_edges
    ]
    assert len({edge.edge_id for edge in first.relation_edges}) == 160
    assert all(edge.source_node_id != edge.target_node_id for edge in first.relation_edges)


def test_confidence_propagates_only_through_adjacent_descending_layers() -> None:
    observed_at = utc_now()
    nodes = [
        _node("G3A", "SERVICE_BRAKE_STATE", SecurityClass.EMERGENCY, sas=0.8, timestamp=observed_at),
        _node("G3B", "ESC_STATE", SecurityClass.EMERGENCY, sas=0.4, timestamp=observed_at),
        _node("G2", "VEHICLE_SPEED", SecurityClass.DRIVING, sas=0.2, timestamp=observed_at),
        _node("G1", "DOOR_STATE", SecurityClass.COCKPIT, sas=0.1, timestamp=observed_at),
        _node("G0", "SUNROOF_STATE", SecurityClass.ENTERTAINMENT, sas=0.05, timestamp=observed_at),
    ]
    result = _service().propagate(nodes, _frame(), [], semantic_similarity_by_node_id=_similarities(nodes))

    assert result.initial_confidences == {
        "G0": 0.05,
        "G1": 0.1,
        "G2": 0.2,
        "G3A": 0.8,
        "G3B": 0.4,
    }
    assert all(step.parent_layer - step.child_layer == 1 for step in result.propagation_steps)
    assert all(step.parent_layer > step.child_layer for step in result.propagation_steps)
    assert not any(
        step.parent_layer == 3 and step.child_layer < 2
        for step in result.propagation_steps
    )
    assert result.final_confidences["G2"] == pytest.approx(0.2 + 0.3 * 0.8 + 0.3 * 0.4)
    assert result.final_confidences["G1"] == pytest.approx(
        0.1 + 0.3 * result.final_confidences["G2"]
    )
    assert result.final_confidences["G0"] == pytest.approx(
        0.05 + 0.3 * result.final_confidences["G1"]
    )
    assert [step.sequence for step in result.propagation_steps] == list(
        range(1, len(result.propagation_steps) + 1)
    )


@pytest.mark.parametrize("quality", [EvidenceStatus.MISSING, EvidenceStatus.TAMPERED])
def test_missing_and_tampered_remain_zero_and_cannot_propagate(quality: EvidenceStatus) -> None:
    observed_at = utc_now()
    nodes = [
        _node("BAD", "SERVICE_BRAKE_STATE", SecurityClass.EMERGENCY, sas=0.99, quality=quality, timestamp=observed_at),
        _node("LOW", "SYSTEM_MODE", SecurityClass.ENTERTAINMENT, sas=0.2, timestamp=observed_at),
    ]
    result = _service().propagate(nodes, _frame(), [], semantic_similarity_by_node_id=_similarities(nodes))
    layer = next(item for item in result.node_layers if item.node_id == "BAD")
    assert layer.propagation_eligible is False
    assert result.initial_confidences["BAD"] == 0
    assert result.final_confidences["BAD"] == 0
    assert all(step.parent_node_id != "BAD" for step in result.propagation_steps)


def test_non_catalog_evidence_cannot_enter_memory() -> None:
    observed_at = utc_now()
    with pytest.raises(ValidationError):
        _node(
            "UNKNOWN",
            "unknown_sensor",
            SecurityClass.UNCLASSIFIED,
            sas=0.9,
            timestamp=observed_at,
        )
