from __future__ import annotations

import json
from pathlib import Path

from app.models.schemas import (
    EvidenceDemand,
    IntentEvidenceDemand,
    VehicleState,
    VectorizationMetadata,
)
from app.services.evidence.catalog import CANONICAL_EVIDENCE_TYPES
from app.services.evidence.repository import EvidenceRepository
from app.services.index.trusted_knowledge import TrustedKnowledgeIndexService
from app.services.vector.embedding import DeterministicHashEmbeddingService


class ContextEmbedding:
    dimension = 8

    @staticmethod
    def _metadata(vector: list[float]) -> VectorizationMetadata:
        return VectorizationMetadata(
            implementation="test_context_embedding",
            model_name="test-context",
            dimension=len(vector),
            normalized=True,
            real_model_inference=False,
            vector_digest="test",
        )

    def encode(self, text: str):
        if "夜间" in text or "低照度" in text or "NIGHT" in text:
            vector = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        else:
            vector = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        return vector, self._metadata(vector)


def _node(
    node_id: str,
    action: str,
    *,
    title: str | None = None,
    required: list[str] | None = None,
    optional: list[str] | None = None,
    conditions: list[str] | None = None,
    vector: list[float] | None = None,
) -> dict:
    return {
        "node_id": node_id,
        "node_type": "Trusted",
        "title": title or node_id,
        "semantic_description": title or node_id,
        "canonical_action": action,
        "conditions": conditions or [],
        "required_evidence": required or [],
        "optional_evidence": optional or [],
        "source": "TEST",
        "chapter": "1",
        "clause": "1.1",
        "trust_level": "L1",
        "vector": vector,
        "metadata": {"status": "ACTIVE"},
    }


def _write(path: Path, rows: list[dict]) -> Path:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    return path


def _service(
    path: Path,
    *,
    min_similarity: float = 0.0,
    embedder=None,
) -> TrustedKnowledgeIndexService:
    actual_embedder = embedder or DeterministicHashEmbeddingService(64)
    service = TrustedKnowledgeIndexService(
        {
            "enabled": True,
            "data_path": str(path),
            "top_k": 5,
            "min_similarity": min_similarity,
            "M": 16,
            "ef_construction": 100,
            "ef_search": 30,
            "context": {"low_light_max_lux": 20, "high_speed_min_kph": 80},
        },
        actual_embedder,
        CANONICAL_EVIDENCE_TYPES,
    )
    service.load()
    return service


def _intent(
    intent_id: str,
    clause_index: int,
    action: str,
    target: str,
    *,
    area: str = "unknown",
    required: list[str] | None = None,
    optional: list[str] | None = None,
) -> IntentEvidenceDemand:
    return IntentEvidenceDemand(
        intent_id=intent_id,
        clause_index=clause_index,
        action=action,
        target=target,
        area=area,
        risk_level="R3",
        query_text="",
        required_types=required or [],
        optional_types=optional or [],
    )


def _augment(
    service: TrustedKnowledgeIndexService,
    intents: list[IntentEvidenceDemand],
    state: VehicleState | None = None,
) -> list[IntentEvidenceDemand]:
    demand = EvidenceDemand(turn_id="TURN_KNOWLEDGE_HNSW", intent_demands=intents)
    context_nodes = (
        EvidenceRepository().ingest_vehicle_state(
            state,
            None,
            demand.turn_id,
        )
        if state is not None
        else []
    )
    return service.augment(
        demand,
        context_evidence_nodes=context_nodes,
    ).intent_demands


def test_native_hnsw_filter_prevents_cross_intent_leakage(tmp_path: Path) -> None:
    rows = [
        _node("WINDOW", "WINDOW_OPEN", required=["WINDOW_STATE"]),
        _node("DOOR", "DOOR_OPEN", title="打开车窗极其相似", required=["DOOR_STATE"]),
        _node("SUNROOF", "SUNROOF_OPEN", required=["SUNROOF_STATE"]),
        _node("WINDOW_CLOSE", "WINDOW_CLOSE", required=["WINDOW_STATE"]),
    ]
    service = _service(_write(tmp_path / "nodes.jsonl", rows))
    result = _augment(service, [_intent("WINDOW_OPEN", 0, "打开", "车窗")])[0]
    assert result.knowledge_hits
    assert {hit["canonical_action"] for hit in result.knowledge_hits} == {"WINDOW_OPEN"}
    assert result.knowledge_retrieval_metadata["match_route"] == "HNSW_FILTERED"


def test_same_action_context_changes_hnsw_ranking(tmp_path: Path) -> None:
    rows = [
        _node(
            "NIGHT",
            "HEADLIGHT_SET_MODE",
            title="夜间行驶低照度前照灯安全",
            conditions=["VEHICLE_MOVING", "NIGHT"],
        ),
        _node(
            "DAY",
            "HEADLIGHT_SET_MODE",
            title="白天驻车前照灯检查",
            conditions=["VEHICLE_STATIONARY", "DAY"],
        ),
    ]
    service = _service(
        _write(tmp_path / "nodes.jsonl", rows), embedder=ContextEmbedding()
    )
    state = VehicleState(vehicle_speed=30, weather="NIGHT", ambient_light=5)
    result = _augment(
        service,
        [_intent("HEADLIGHT_SET_MODE", 0, "设置", "前照灯")],
        state,
    )[0]
    assert result.knowledge_hits[0]["node_id"] == "NIGHT"
    assert "运动状态=行驶" in result.knowledge_query_text
    assert "光照=低照度" in result.knowledge_query_text


def test_missing_context_is_omitted_without_excluding_knowledge(tmp_path: Path) -> None:
    service = _service(
        _write(
            tmp_path / "nodes.jsonl",
            [_node("WINDOW", "WINDOW_OPEN", required=["WINDOW_STATE"])],
        )
    )
    state = VehicleState(vehicle_speed=None, weather=None, ambient_light=None)
    result = _augment(
        service, [_intent("WINDOW_OPEN", 0, "打开", "车窗")], state
    )[0]
    assert result.knowledge_hits
    assert "天气=" not in result.knowledge_query_text
    assert "光照=" not in result.knowledge_query_text


def test_dynamic_demands_merge_and_retain_node_provenance(tmp_path: Path) -> None:
    service = _service(
        _write(
            tmp_path / "nodes.jsonl",
            [
                _node(
                    "DOOR_SAFETY",
                    "DOOR_OPEN",
                    required=["VEHICLE_SPEED", "SURROUNDING_OBJECT_STATE"],
                    optional=["OCCUPANT_STATE"],
                )
            ],
        )
    )
    result = _augment(
        service,
        [
            _intent(
                "DOOR_OPEN",
                0,
                "打开",
                "车门",
                required=["VEHICLE_SPEED", "DOOR_STATE"],
            )
        ],
    )[0]
    assert result.required_types == [
        "VEHICLE_SPEED",
        "DOOR_STATE",
        "SURROUNDING_OBJECT_STATE",
    ]
    assert "OCCUPANT_STATE" in result.optional_types
    source = next(
        item
        for item in result.knowledge_demand_sources
        if item["evidence_type"] == "SURROUNDING_OBJECT_STATE"
    )
    assert source["source_knowledge_node_ids"] == ["DOOR_SAFETY"]
    assert source["matched_intent_id"] == "DOOR_OPEN"
    assert source["clause_index"] == 0


def test_duplicate_evidence_keeps_hit_without_duplicate_type(tmp_path: Path) -> None:
    service = _service(
        _write(
            tmp_path / "nodes.jsonl",
            [_node("SPEED_RULE", "DOOR_OPEN", required=["VEHICLE_SPEED"])],
        )
    )
    result = _augment(
        service,
        [_intent("DOOR_OPEN", 0, "打开", "车门", required=["VEHICLE_SPEED"])],
    )[0]
    assert result.required_types == ["VEHICLE_SPEED"]
    assert result.knowledge_augmented_types == []
    assert [hit["node_id"] for hit in result.knowledge_hits] == ["SPEED_RULE"]


def test_multi_intent_occurrences_are_searched_and_audited_independently(
    tmp_path: Path,
) -> None:
    service = _service(
        _write(
            tmp_path / "nodes.jsonl",
            [
                _node("WINDOW_RULE", "WINDOW_OPEN", required=["WINDOW_STATE"]),
                _node("DOOR_RULE", "DOOR_LOCK", required=["DOOR_LOCK_STATE"]),
            ],
        )
    )
    window, door = _augment(
        service,
        [
            _intent("WINDOW_OPEN", 0, "打开", "车窗"),
            _intent("DOOR_LOCK", 1, "锁定", "车门"),
        ],
    )
    assert [(hit["node_id"], hit["clause_index"]) for hit in window.knowledge_hits] == [
        ("WINDOW_RULE", 0)
    ]
    assert [(hit["node_id"], hit["clause_index"]) for hit in door.knowledge_hits] == [
        ("DOOR_RULE", 1)
    ]


def test_empty_action_knowledge_preserves_mandatory_demands(tmp_path: Path) -> None:
    service = _service(
        _write(tmp_path / "nodes.jsonl", [_node("WINDOW", "WINDOW_OPEN")])
    )
    result = _augment(
        service,
        [_intent("AUTO_PARK_ENABLE", 0, "启用", "自动泊车", required=["VEHICLE_SPEED"])],
    )[0]
    assert result.required_types == ["VEHICLE_SPEED"]
    assert result.knowledge_hits == []
    assert result.knowledge_retrieval_metadata["status"] == "NO_ELIGIBLE_KNOWLEDGE"


def test_low_similarity_produces_no_hits_or_dynamic_demands(tmp_path: Path) -> None:
    service = _service(
        _write(
            tmp_path / "nodes.jsonl",
            [
                _node(
                    "ORTHOGONAL",
                    "WINDOW_OPEN",
                    required=["WINDOW_STATE"],
                    vector=[0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                )
            ],
        ),
        min_similarity=0.9,
        embedder=ContextEmbedding(),
    )
    state = VehicleState(weather="NIGHT", ambient_light=5)
    result = _augment(
        service, [_intent("WINDOW_OPEN", 0, "打开", "车窗")], state
    )[0]
    assert result.knowledge_hits == []
    assert result.knowledge_augmented_types == []


def test_illegal_canonical_action_fails_closed_at_load(tmp_path: Path) -> None:
    service = _service(
        _write(tmp_path / "nodes.jsonl", [_node("BAD", "NOT_A_FORMAL_INTENT")])
    )
    status = service.status()
    assert status["ready"] is False
    assert "NOT_A_FORMAL_INTENT" in status["load_error"]


def test_reload_replaces_nodes_labels_and_lookup_as_one_release(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "nodes.jsonl",
        [_node("WINDOW_OLD", "WINDOW_OPEN", required=["WINDOW_STATE"])],
    )
    service = _service(path)
    assert _augment(service, [_intent("WINDOW_OPEN", 0, "打开", "车窗")])[0].knowledge_hits

    _write(path, [_node("DOOR_NEW", "DOOR_OPEN", required=["DOOR_STATE"])])
    service.load()
    window = _augment(service, [_intent("WINDOW_OPEN", 0, "打开", "车窗")])[0]
    door = _augment(service, [_intent("DOOR_OPEN", 0, "打开", "车门")])[0]
    assert window.knowledge_hits == []
    assert window.knowledge_retrieval_metadata["eligible_node_count"] == 0
    assert [hit["node_id"] for hit in door.knowledge_hits] == ["DOOR_NEW"]
