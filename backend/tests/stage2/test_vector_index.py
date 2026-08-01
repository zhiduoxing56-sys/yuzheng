from __future__ import annotations

import builtins
import math

import pytest

from app.core.config import load_yaml
from app.models.schemas import VehicleState
from app.services.evidence.repository import EvidenceRepository
from app.services.index.hnsw import HNSWIndexService, evidence_key
from app.services.vector import embedding as embedding_module
from app.services.vector.embedding import DeterministicHashEmbeddingService, build_embedding_service


@pytest.fixture(scope="module")
def real_bge_embedder():
    service = build_embedding_service(load_yaml("embedding.yaml"))
    assert service.implementation == "local_sentence_transformer"
    assert service.model_name == "BAAI/bge-base-zh-v1.5"
    assert service.real_model_inference is True
    assert service.degradation_reason is None
    return service


def test_configured_bge_performs_real_768_dimensional_normalized_inference(
    real_bge_embedder,
) -> None:
    query, metadata = real_bge_embedder.encode("打开车门")
    repeated_query, repeated_metadata = real_bge_embedder.encode("打开车门")
    related, _ = real_bge_embedder.encode("开启驾驶员侧车门")
    unrelated, _ = real_bge_embedder.encode("播放一首轻音乐")
    related_similarity = sum(left * right for left, right in zip(query, related))
    unrelated_similarity = sum(left * right for left, right in zip(query, unrelated))

    assert metadata.implementation == "local_sentence_transformer"
    assert metadata.model_name == "BAAI/bge-base-zh-v1.5"
    assert metadata.real_model_inference is True
    assert metadata.degradation_reason is None
    assert repeated_query == query
    assert repeated_metadata.vector_digest == metadata.vector_digest
    assert len(query) == 768
    assert math.sqrt(sum(value * value for value in query)) == pytest.approx(1.0, abs=1e-6)
    assert related_similarity > unrelated_similarity


def test_configured_index_uses_real_hnswlib(real_bge_embedder) -> None:
    index = HNSWIndexService(load_yaml("index.yaml"), real_bge_embedder)
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    nodes = repository.from_vehicle_state(
        VehicleState(vehicle_speed=30, gear_position="D"),
        ["vehicle_speed", "gear_position"],
        [],
        {},
    )
    status = index.build(nodes)
    query, _ = real_bge_embedder.encode("当前车辆速度")
    results, metadata = index.search(query, top_k=2)

    assert status.implementation == "hnswlib"
    assert status.degraded is False
    assert status.degradation_reason is None
    assert status.node_count == 2
    assert len(results) == 2
    assert metadata.implementation == "hnswlib"
    assert metadata.degraded is False


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


def test_embedding_factory_only_falls_back_when_real_model_raises(monkeypatch) -> None:
    def fail_real_model(*args, **kwargs):
        raise RuntimeError("forced model load failure")

    monkeypatch.setattr(
        embedding_module,
        "LocalSentenceTransformerEmbeddingService",
        fail_real_model,
    )
    service = build_embedding_service(load_yaml("embedding.yaml"))
    _, metadata = service.encode("异常路径验证")

    assert metadata.implementation == "deterministic_hash_768"
    assert metadata.real_model_inference is False
    assert "forced model load failure" in metadata.degradation_reason


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
    expected = max(0.0, sum(a * b for a, b in zip(query, index._vectors[evidence_key(results[0][0])])))
    assert results[0][1] == pytest.approx(expected, abs=1e-6)
