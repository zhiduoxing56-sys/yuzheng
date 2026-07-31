from __future__ import annotations

import builtins
import math

from app.core.config import load_yaml
from app.models.schemas import VehicleState
from app.services.evidence.repository import EvidenceRepository
from app.services.index.hnsw import HNSWIndexService
from app.services.vector.embedding import DeterministicHashEmbeddingService


def test_hash_vector_is_deterministic_normalized_and_768_dimensional() -> None:
    service = DeterministicHashEmbeddingService(768, "test fallback")
    first, first_metadata = service.encode("打开车门 vehicle_speed")
    second, second_metadata = service.encode("打开车门 vehicle_speed")

    assert first == second
    assert len(first) == 768
    assert math.sqrt(sum(value * value for value in first)) == pytest.approx(1.0)
    assert first_metadata.vector_digest == second_metadata.vector_digest
    assert first_metadata.real_model_inference is False
    assert first_metadata.degradation_reason == "test fallback"


def test_index_build_search_empty_fallback_and_status(monkeypatch) -> None:
    real_import = builtins.__import__

    def deny_hnswlib(name, *args, **kwargs):
        if name == "hnswlib":
            raise ImportError("forced unavailable for deterministic fallback test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", deny_hnswlib)
    embedder = DeterministicHashEmbeddingService(768)
    index = HNSWIndexService(load_yaml("index.yaml"), embedder)
    query, _ = embedder.encode("vehicle_speed 当前车速")

    empty_results, empty_metadata = index.search(query)
    assert empty_results == []
    assert empty_metadata.empty_index is True
    assert empty_metadata.candidate_count == 0

    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    nodes = repository.from_vehicle_state(
        VehicleState(vehicle_speed=30, gear_position="D"),
        ["vehicle_speed", "gear_position"],
        [],
        {},
    )
    status = index.build(nodes)
    results, metadata = index.search(query, top_k=2)

    assert status.node_count == 2
    assert status.M == 16
    assert status.ef_construction == 200
    assert status.ef_search == 30
    assert status.top_k == 20
    assert status.implementation == "exact_cosine_fallback"
    assert status.degraded is True
    assert "forced unavailable" in status.degradation_reason
    assert len(results) == 2
    assert all(0 <= similarity <= 1 for _, similarity in results)
    assert metadata.empty_index is False
    assert metadata.candidate_count == 2
    expected = max(0.0, sum(a * b for a, b in zip(query, index._vectors[results[0][0].node_id])))
    assert results[0][1] == pytest.approx(expected, abs=1e-6)


import pytest
