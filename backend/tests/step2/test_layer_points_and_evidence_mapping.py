from __future__ import annotations

from datetime import timedelta

import pytest

from app.core.config import load_yaml
from app.models.schemas import EvidenceNode, EvidenceStatus, utc_now
from app.services.index.hnsw import HNSWIndexService
from app.services.vector.embedding import DeterministicHashEmbeddingService


def _node(evidence_type: str, index: int) -> EvidenceNode:
    now = utc_now()
    return EvidenceNode(
        evidence_type=evidence_type,
        layer="TEST_LAYER",
        source=f"source_{index}",
        value={"index": index},
        timestamp=now,
        expires_at=now + timedelta(minutes=1),
        freshness=1,
        consistency=1,
        availability=1,
        quality_label=EvidenceStatus.VALID,
        integrity_hash=f"{index:064x}",
        metadata={"entity_id": str(index)},
    )


TYPES = [
    "SYSTEM_MODE",
    "LIGHTING_STATE",
    "DOOR_STATE",
    "OCCUPANT_STATE",
    "VEHICLE_SPEED",
    "LANE_STATE",
    "SERVICE_BRAKE_STATE",
    "SURROUNDING_OBJECT_STATE",
]


@pytest.fixture
def built_index() -> tuple[HNSWIndexService, DeterministicHashEmbeddingService]:
    embedder = DeterministicHashEmbeddingService(768)
    service = HNSWIndexService(load_yaml("index.yaml"), embedder)
    service.build(
        [_node(evidence_type, index) for index, evidence_type in enumerate(TYPES)]
    )
    return service, embedder


@pytest.fixture
def empty_service() -> HNSWIndexService:
    embedder = DeterministicHashEmbeddingService(768)
    return HNSWIndexService(load_yaml("index.yaml"), embedder)


def test_layer_points_counts_match_per_layer_node_count(built_index) -> None:
    service, _ = built_index
    status = service.status()
    points = service.all_layer_points()
    assert set(points) == set(range(status.layer_count))
    for layer in range(status.layer_count):
        assert len(points[layer]) == status.per_layer_node_count[layer]
        # 单层接口与全量接口一致
        assert service.layer_points(layer) == points[layer]
    # 层 0 恒含全部节点
    assert len(points[0]) == len(TYPES)


def test_each_layer_points_are_subset_and_consistent(built_index) -> None:
    service, _ = built_index
    all_points = service.all_layer_points()
    layer0_ids = {p.node_id for p in all_points[0]}
    for layer, pts in all_points.items():
        ids = {p.node_id for p in pts}
        assert ids <= layer0_ids
        for point in pts:
            assert point.layer == layer
            assert point.hnsw_max_layer is not None
            assert point.hnsw_max_layer >= layer
            assert point.evidence_type in TYPES
            assert point.display_name == point.evidence_type


def test_layer_points_stable_and_labelled(built_index) -> None:
    service, _ = built_index
    first = service.layer_points(0)
    second = service.layer_points(0)
    assert first == second  # 幂等
    labels = [point.label for point in first]
    assert labels == sorted(labels)
    assert labels == list(range(len(TYPES)))
    internal_keys = {point.internal_key for point in first}
    assert len(internal_keys) == len(TYPES)
    assert all(point.evidence_key for point in first)


def test_node_evidence_map_bijective(built_index) -> None:
    service, _ = built_index
    mapping = service.node_evidence_map()
    assert set(mapping) == set(TYPES)
    flat = [node_id for ids in mapping.values() for node_id in ids]
    assert len(flat) == len(TYPES)
    assert len(set(flat)) == len(TYPES)  # 每个节点出现且仅一次
    for evidence_type, node_ids in mapping.items():
        for node_id in node_ids:
            point = service.point_by_node_id(node_id)
            assert point is not None
            assert point.evidence_type == evidence_type
            assert point.node_id == node_id


def test_point_by_node_id_miss(built_index) -> None:
    service, _ = built_index
    assert service.point_by_node_id("EVI_nope_000") is None


def test_empty_service_returns_empty(built_index, empty_service) -> None:
    service = empty_service
    assert service.all_layer_points() == {
        layer: [] for layer in range(service.max_layer + 1)
    }
    assert service.node_evidence_map() == {}
    assert service.layer_points(0) == []
    assert service.point_by_node_id("anything") is None
