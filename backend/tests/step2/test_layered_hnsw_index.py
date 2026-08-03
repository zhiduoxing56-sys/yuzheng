from __future__ import annotations

from datetime import timedelta
from threading import Event, Thread

import numpy as np
import pytest

from app.core.config import load_yaml
from app.models.schemas import EvidenceNode, EvidenceStatus
from app.services.index.hnsw import HNSWIndexService, TRACE_SOURCE
from app.services.vector.embedding import DeterministicHashEmbeddingService
from app.models.schemas import utc_now


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
        semantic_similarity=0,
        mandatory=False,
        quality_label=EvidenceStatus.VALID,
        integrity_hash=f"{index:064x}",
        metadata={"entity_id": str(index)},
    )


@pytest.fixture
def built_index() -> tuple[HNSWIndexService, DeterministicHashEmbeddingService]:
    embedder = DeterministicHashEmbeddingService(768)
    service = HNSWIndexService(load_yaml("index.yaml"), embedder)
    types = [
        "music_state",
        "display_state",
        "door_state",
        "occupant_role",
        "vehicle_speed",
        "front_camera",
        "safety_rule",
        "front_lidar",
    ]
    service.build([_node(evidence_type, index) for index, evidence_type in enumerate(types)])
    return service, embedder


def test_layer_queries_are_real_descending_and_base_produces_final_top_k(built_index) -> None:
    service, embedder = built_index
    query, _ = embedder.encode("vehicle speed front camera safety rule")
    results, metadata = service.search(query, top_k=4)
    navigation = metadata.security_layer_navigation

    assert navigation is not None
    assert navigation.trace_kind == "SECURITY_LAYER_INDEX_TRACE"
    assert navigation.trace_source == TRACE_SOURCE
    assert navigation.is_internal_hnsw_trace is False
    assert navigation.internal_trace_available is False
    assert navigation.internal_hnsw_entry_point is None
    assert navigation.internal_hnsw_visited_nodes is None
    layers = [step.layer for step in navigation.steps]
    assert layers == sorted(layers, reverse=True)
    assert layers[-1] == 0
    assert all(step.returned_count <= service.ef_search for step in navigation.steps)
    assert all(step.selected_anchor_node_id in {c.node_id for c in step.candidates} for step in navigation.steps)

    snapshot = service._snapshot
    assert snapshot is not None
    labels, distances = service.layer_indices[0].knn_query(
        np.asarray(query, dtype=np.float32).reshape(1, -1), k=4
    )
    expected = []
    for label, distance in zip(labels[0].tolist(), distances[0].tolist(), strict=True):
        key = snapshot.layer_labels[0][int(label)]
        expected.append((snapshot.nodes[key].node_id, float(np.clip(1 - distance, 0, 1))))
    expected.sort(key=lambda item: (-item[1], item[0]))

    assert [node.node_id for node, _ in results] == [node_id for node_id, _ in expected]
    assert navigation.final_top_k_node_ids == [node.node_id for node, _ in results]
    assert metadata.final_top_k_node_ids == navigation.final_top_k_node_ids


def test_visualization_path_only_references_real_candidates_or_final_nodes(built_index) -> None:
    service, embedder = built_index
    query, _ = embedder.encode("door status")
    _, metadata = service.search(query, top_k=5)
    navigation = metadata.security_layer_navigation
    assert navigation is not None
    allowed = set(navigation.final_top_k_node_ids)
    allowed.update(candidate.node_id for step in navigation.steps for candidate in step.candidates)

    assert metadata.retrieval_visualization_path
    for edge in metadata.retrieval_visualization_path:
        assert edge.from_node_id in allowed
        assert edge.to_node_id in allowed
        assert edge.source in {TRACE_SOURCE, "BASE_REAL_HNSWLIB_INDEX"}


def test_repeated_query_on_same_snapshot_is_deterministic(built_index) -> None:
    service, embedder = built_index
    query, _ = embedder.encode("same deterministic query")
    first_results, first = service.search(query, top_k=5)
    second_results, second = service.search(query, top_k=5)

    assert [node.node_id for node, _ in first_results] == [node.node_id for node, _ in second_results]
    def without_timings(metadata):
        payload = metadata.security_layer_navigation.model_dump(
            exclude={"total_elapsed_ms"}
        )
        for step in payload["steps"]:
            step.pop("elapsed_ms", None)
        return payload

    assert without_timings(first) == without_timings(second)
    assert first.retrieval_visualization_path == second.retrieval_visualization_path
    assert first.index_build_id == second.index_build_id


def test_failed_build_keeps_previous_snapshot(monkeypatch, built_index) -> None:
    service, _ = built_index
    before = service.status()

    def fail(*args, **kwargs):
        raise RuntimeError("forced atomic build failure")

    monkeypatch.setattr(service, "_construct_snapshot", fail)
    with pytest.raises(RuntimeError, match="forced atomic"):
        service.build([_node("vehicle_speed", 99)])

    after = service.status()
    assert after.index_build_id == before.index_build_id
    assert after.node_set_digest == before.node_set_digest
    assert after.per_layer_node_count == before.per_layer_node_count


def test_concurrent_reader_never_sees_half_built_snapshot(monkeypatch, built_index) -> None:
    service, embedder = built_index
    before = service.status().index_build_id
    entered = Event()
    release = Event()
    original = service._construct_snapshot

    def delayed(*args, **kwargs):
        entered.set()
        assert release.wait(timeout=10)
        return original(*args, **kwargs)

    monkeypatch.setattr(service, "_construct_snapshot", delayed)
    worker = Thread(target=lambda: service.build([_node("vehicle_speed", 101)]), daemon=True)
    worker.start()
    assert entered.wait(timeout=10)
    query, _ = embedder.encode("read while rebuilding")
    _, during = service.search(query, top_k=2)
    assert during.index_build_id == before
    assert len(service.layer_indices) == 4
    release.set()
    worker.join(timeout=10)
    assert not worker.is_alive()
    assert service.status().index_build_id != before


def test_audit_metadata_contains_no_vector_or_private_hnsw_structure(built_index) -> None:
    service, embedder = built_index
    query, _ = embedder.encode("audit metadata")
    _, metadata = service.search(query)
    payload = metadata.model_dump_json()

    assert "query_vector" not in payload
    assert "embedding_vector" not in payload
    assert "private_pointer" not in payload
    assert "internal_hnsw_visited_nodes\":null" in payload
