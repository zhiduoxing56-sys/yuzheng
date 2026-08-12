from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from app.core.config import load_yaml
from app.core.pipeline import CommandPipeline
from app.main import create_app
from app.models.schemas import (
    EvidenceDemand,
    EvidenceNode,
    EvidenceQualityMetrics,
    EvidenceStatus,
    IntentEvidenceResolution,
    IntentEvidenceDemand,
    RetrievalMetadata,
    SecurityClass,
    SemanticFrame,
    SemanticIntent,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleStatePatch,
    utc_now,
)
from app.services.audit.repository import canonical_json
from app.services.evidence.canonicalization import canonicalize_evidence_nodes
from app.services.evidence.resolution import project_evidence_resolutions
from app.services.graph.builder import EvidenceSubgraphBuilder
from app.services.memory.service import DualMemoryService
from app.services.presentation.assembler import PresentationAssembler


TEST_SECRET = b"step5-freeze-blocker-test-secret-32-bytes"


def _node(
    *,
    sas: float,
    quality: EvidenceStatus = EvidenceStatus.VALID,
    metadata: dict | None = None,
) -> EvidenceNode:
    observed_at = utc_now()
    return EvidenceNode(
        node_id="EVI_CANONICAL_FIXED",
        evidence_type="SERVICE_BRAKE_STATE",
        layer="L3_EMERGENCY",
        source="brake_state_repository",
        value={"brake_state": "RELEASED", "emergency_braking_detected": False},
        timestamp=observed_at,
        expires_at=observed_at + timedelta(minutes=5),
        freshness=0.91,
        consistency=0.92,
        availability=0.93,
        quality_label=quality,
        integrity_hash="fixed-integrity-hash",
        metadata=metadata or {},
        security_class=SecurityClass.EMERGENCY,
        security_rank=3,
        security_classification_source="EXISTING_PROJECT_MAPPING",
    )


def _frame() -> SemanticFrame:
    return SemanticFrame(
        turn_id="TURN_CANONICAL_FIXED",
        raw_text="打开车门",
        normalized_text="打开车门",
        semantic_confidence=0.9,
        ambiguity_score=0.1,
        semantic_status="OK",
        intents=[
            SemanticIntent(
                clause_index=0,
                clause_text="打开车门",
                intent_id="DOOR_OPEN",
                action="打开",
                target="车门",
                area="全车",
                control_domain="vehicle_control",
                semantic_confidence=0.9,
                ambiguity_score=0.1,
                risk_level="R3",
            )
        ],
    )


def _demand() -> EvidenceDemand:
    return EvidenceDemand(
        turn_id="TURN_CANONICAL_FIXED",
        intent_demands=[
            IntentEvidenceDemand(
                intent_id="DOOR_OPEN",
                clause_index=0,
                action="打开",
                target="车门",
                area="全车",
                risk_level="R3",
                query_text="打开 车门",
                required_types=[],
            )
        ],
    )


def _quality() -> EvidenceQualityMetrics:
    return EvidenceQualityMetrics(
        ecr=1.0,
        evidence_coverage_applicable=True,
        ecs=1.0,
        ef=1.0,
        sas=0.668181,
        eas=1.0,
    )


def _retrieval() -> RetrievalMetadata:
    return RetrievalMetadata(
        implementation="hnswlib",
        index_node_count=1,
        vector_dimension=768,
        M=16,
        ef_construction=200,
        ef_search=64,
        top_k=5,
        candidate_count=1,
        duration_ms=1.0,
        empty_index=False,
        degraded=False,
        final_top_k_node_ids=["EVI_CANONICAL_FIXED"],
    )


def test_field_level_canonicalization_is_order_independent_and_excludes_query_sas() -> None:
    query_node = _node(
        sas=0.668181,
        metadata={"retrieval_origin": "semantic_retrieval", "retrieval_rank": 1},
    )
    repository_node = _node(
        sas=0.0,
        metadata={"entity_id": "brake", "area": "door"},
    )
    first = canonicalize_evidence_nodes(
        [
            ("HNSW_QUERY_EVALUATED", [query_node]),
            ("EVIDENCE_REPOSITORY", [repository_node]),
        ]
    )
    second = canonicalize_evidence_nodes(
        [
            ("EVIDENCE_REPOSITORY", [repository_node]),
            ("HNSW_QUERY_EVALUATED", [query_node]),
        ]
    )

    assert [item.model_dump(mode="json") for item in first] == [
        item.model_dump(mode="json") for item in second
    ]
    canonical = first[0]
    assert "semantic_similarity" not in canonical.model_dump()
    assert canonical.metadata["retrieval_rank"] == 1
    assert canonical.metadata["entity_id"] == "brake"
    assert "semantic_similarity" not in canonical.field_resolution
    assert canonical.canonicalization_warnings == []


@pytest.mark.parametrize("status", [EvidenceStatus.MISSING, EvidenceStatus.TAMPERED])
def test_canonicalization_never_downgrades_missing_or_tampered(status: EvidenceStatus) -> None:
    protected = _node(sas=0.9, quality=status)
    weaker = _node(sas=0.7, quality=EvidenceStatus.VALID)
    canonical = canonicalize_evidence_nodes(
        [
            ("REQUIRED_MISSING_OR_TAMPERED", [protected]),
            ("EVIDENCE_REPOSITORY", [weaker]),
        ]
    )[0]
    memory = DualMemoryService(load_yaml("memory.yaml")).propagate(
        [canonical],
        _frame(),
        [],
        semantic_similarity_by_node_id={canonical.node_id: 0.9},
    )

    assert canonical.quality_label == status
    assert memory.initial_confidences[canonical.node_id] == 0
    assert memory.final_confidences[canonical.node_id] == 0


def test_graph_and_memory_use_the_same_canonical_node() -> None:
    query_node = _node(
        sas=0.668181,
        metadata={"retrieval_origin": "semantic_retrieval", "retrieval_rank": 1},
    )
    repository_node = _node(
        sas=0.0,
        metadata={"entity_id": "brake", "area": "door"},
    )
    graph = EvidenceSubgraphBuilder().build(
        _frame(),
        [query_node],
        [
            IntentEvidenceResolution(
                clause_index=0,
                intent_id="DOOR_OPEN",
                candidate_node_ids=[query_node.node_id],
            )
        ],
        _quality(),
        _retrieval(),
        [],
    )
    canonical = next(node for node in graph.nodes if node.node_id == query_node.node_id)
    memory = DualMemoryService(load_yaml("memory.yaml")).propagate(
        [canonical],
        _frame(),
        [],
        semantic_similarity_by_node_id={canonical.node_id: 0.668181},
        retrieval_origins={canonical.node_id: "HNSW"},
    )

    assert "semantic_similarity" not in canonical.model_dump()
    assert memory.initial_confidences[canonical.node_id] == pytest.approx(
        0.668181
    )


def test_pipeline_persists_sas_on_bindings_across_audit_and_restart(tmp_path) -> None:
    database = tmp_path / "canonical-restart.db"
    pipeline = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    result = pipeline.process_text(
        TextCommandRequest(text="打开车门"),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
        ),
    )
    record = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert record is not None
    assert record.evidence_subgraph is not None
    assert record.memory_propagation is not None
    graph_by_id = {node.node_id: node for node in record.evidence_subgraph.nodes}
    projection = project_evidence_resolutions(
        record.evidence_subgraph.intent_evidence_resolutions
    )
    normal_ids = [
        node_id
        for node_id in record.memory_propagation.candidate_node_ids
        if graph_by_id[node_id].quality_label
        not in {EvidenceStatus.MISSING, EvidenceStatus.TAMPERED}
    ]
    assert normal_ids

    presentation = PresentationAssembler(pipeline).assemble(record)
    presented_by_id = {
        node.node_id: node for node in presentation.evidence.evidence_subgraph.nodes
    }
    for node_id in normal_ids:
        graph_node = graph_by_id[node_id]
        initial = record.memory_propagation.initial_confidences[node_id]
        detail = PresentationAssembler(pipeline).node_detail(record, node_id)
        assert detail is not None
        assert "semantic_similarity" not in graph_node.model_dump()
        assert "semantic_similarity" not in presented_by_id[node_id].model_dump()
        assert "semantic_similarity" not in detail.model_dump()
        assert initial == pytest.approx(
            projection.semantic_similarity_by_node_id.get(node_id, 0.0)
        )
        assert detail.memory_initial_confidence == pytest.approx(initial)
        assert detail.canonicalization_source == graph_node.canonicalization_source

    restarted = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    restored = restarted.audit_repository.get_by_turn(result.turn_id)
    assert restored is not None
    restored_projection = project_evidence_resolutions(
        restored.evidence_subgraph.intent_evidence_resolutions
    )
    for node_id in normal_ids:
        assert restored.memory_propagation.initial_confidences[node_id] == pytest.approx(
            restored_projection.semantic_similarity_by_node_id.get(node_id, 0.0)
        )


def _clear_persisted_candidates(database, audit_id: str) -> None:
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT record_json, previous_hash FROM audit_records WHERE audit_id=?",
            (audit_id,),
        ).fetchone()
        raw = json.loads(row[0])
        raw["candidate_interpretations"] = []
        raw["candidate_availability"] = "NO_VALID_CANDIDATES"
        raw["interpreter_result"]["candidate_interpretations"] = []
        raw["interpreter_result"]["candidate_availability"] = "NO_VALID_CANDIDATES"
        raw["current_hash"] = ""
        digest = hashlib.sha256(
            (row[1] + canonical_json(raw)).encode("utf-8")
        ).hexdigest()
        raw["current_hash"] = digest
        connection.execute(
            "UPDATE audit_records SET record_json=?, current_hash=? WHERE audit_id=?",
            (json.dumps(raw, ensure_ascii=False, separators=(",", ":")), digest, audit_id),
        )


def _invalidate_persisted_candidate(database, audit_id: str) -> str:
    with sqlite3.connect(database) as connection:
        row = connection.execute(
            "SELECT record_json, previous_hash FROM audit_records WHERE audit_id=?",
            (audit_id,),
        ).fetchone()
        raw = json.loads(row[0])
        candidate_id = raw["candidate_interpretations"][0]["candidate_id"]
        raw["candidate_interpretations"][0]["validation_status"] = "INVALID"
        raw["interpreter_result"]["candidate_interpretations"][0][
            "validation_status"
        ] = "INVALID"
        raw["current_hash"] = ""
        digest = hashlib.sha256(
            (row[1] + canonical_json(raw)).encode("utf-8")
        ).hexdigest()
        raw["current_hash"] = digest
        connection.execute(
            "UPDATE audit_records SET record_json=?, current_hash=? WHERE audit_id=?",
            (json.dumps(raw, ensure_ascii=False, separators=(",", ":")), digest, audit_id),
        )
        return candidate_id


def _persist_review_with_no_candidates(database) -> dict:
    app = create_app(database_path=database, token_secret=TEST_SECRET, audit_database_role="TEST")
    with TestClient(app) as client:
        original = app.state.pipeline.process_text(
            TextCommandRequest(text="关闭车门然后锁车门"),
            trusted_context=TrustedRuntimeContext(
                state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P")
            ),
        ).model_dump(mode="json")
    assert original["decision"]["final_decision"] == "REVIEW"
    _clear_persisted_candidates(database, original["audit"]["audit_id"])
    return original


def _database_counts(database, original_turn_id: str) -> dict[str, int]:
    with sqlite3.connect(database) as connection:
        return {
            "audits": connection.execute("SELECT COUNT(*) FROM audit_records").fetchone()[0],
            "children": connection.execute(
                "SELECT COUNT(*) FROM turn_workflow_events WHERE parent_turn_id=?",
                (original_turn_id,),
            ).fetchone()[0],
            "tokens": connection.execute(
                "SELECT COUNT(*) FROM authorization_tokens"
            ).fetchone()[0],
        }


def _confirm_rejection_count(database, original_turn_id: str) -> int:
    with sqlite3.connect(database) as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM turn_workflow_events "
            "WHERE root_turn_id=? AND event_type='REVIEW_CONFIRM_REJECTED'",
            (original_turn_id,),
        ).fetchone()[0]


def test_public_confirm_rejects_empty_persisted_candidates_without_business_side_effects(
    tmp_path,
) -> None:
    database = tmp_path / "empty-candidate.db"
    original = _persist_review_with_no_candidates(database)
    before = _database_counts(database, original["turn_id"])
    original_decision = original["decision"]["final_decision"]

    restarted = create_app(database_path=database, token_secret=TEST_SECRET, audit_database_role="TEST")
    with TestClient(restarted) as client:
        response = client.post(
            f"/api/turns/{original['turn_id']}/review",
            json={"action": "CONFIRM", "selected_candidate_id": "CAND_NOT_PRESENT"},
        )
        repeated = client.post(
            f"/api/turns/{original['turn_id']}/review",
            json={"action": "CONFIRM", "selected_candidate_id": "CAND_NOT_PRESENT"},
        )
        missing_selection = client.post(
            f"/api/turns/{original['turn_id']}/review",
            json={"action": "CONFIRM"},
        )
        presentation = client.get(
            f"/api/turns/{original['turn_id']}/presentation"
        ).json()

    after = _database_counts(database, original["turn_id"])
    assert response.status_code == repeated.status_code == 409
    assert response.json()["error_code"] == "NO_PERSISTED_REVIEW_CANDIDATES"
    assert repeated.json()["error_code"] == "NO_PERSISTED_REVIEW_CANDIDATES"
    assert missing_selection.status_code == 422
    assert missing_selection.json()["error_code"] == "SELECTED_CANDIDATE_REQUIRED"
    assert after == before
    assert _confirm_rejection_count(database, original["turn_id"]) == 1
    assert presentation["decision_result"]["final_decision"] == original_decision


def test_invalid_persisted_candidate_is_rejected_without_child_or_token(tmp_path) -> None:
    database = tmp_path / "invalid-candidate.db"
    app = create_app(database_path=database, token_secret=TEST_SECRET, audit_database_role="TEST")
    with TestClient(app) as client:
        original = app.state.pipeline.process_text(
            TextCommandRequest(text="关闭车门然后锁车门"),
            trusted_context=TrustedRuntimeContext(
                state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P")
            ),
        ).model_dump(mode="json")
    candidate_id = _invalidate_persisted_candidate(
        database, original["audit"]["audit_id"]
    )
    before = _database_counts(database, original["turn_id"])
    restarted = create_app(database_path=database, token_secret=TEST_SECRET, audit_database_role="TEST")
    with TestClient(restarted) as client:
        response = client.post(
            f"/api/turns/{original['turn_id']}/review",
            json={"action": "CONFIRM", "selected_candidate_id": candidate_id},
        )
    assert response.status_code == 409
    assert response.json()["error_code"] == "REVIEW_CANDIDATE_NOT_VALID"
    assert _database_counts(database, original["turn_id"]) == before


def test_empty_candidate_review_still_allows_correct_and_cancel(tmp_path) -> None:
    correct_database = tmp_path / "empty-candidate-correct.db"
    correct_original = _persist_review_with_no_candidates(correct_database)
    correct_before = _database_counts(correct_database, correct_original["turn_id"])
    correct_app = create_app(database_path=correct_database, token_secret=TEST_SECRET, audit_database_role="TEST")
    with TestClient(correct_app) as client:
        corrected = client.post(
            f"/api/turns/{correct_original['turn_id']}/review",
            json={"action": "CORRECT", "corrected_text": "播放音乐"},
        )
    assert corrected.status_code == 200
    assert corrected.json()["accepted"] is True
    assert corrected.json()["related_turn_id"] != correct_original["turn_id"]
    correct_after = _database_counts(correct_database, correct_original["turn_id"])
    assert correct_after["audits"] == correct_before["audits"] + 1
    assert correct_after["children"] > correct_before["children"]

    cancel_database = tmp_path / "empty-candidate-cancel.db"
    cancel_original = _persist_review_with_no_candidates(cancel_database)
    cancel_before = _database_counts(cancel_database, cancel_original["turn_id"])
    cancel_app = create_app(database_path=cancel_database, token_secret=TEST_SECRET, audit_database_role="TEST")
    with TestClient(cancel_app) as client:
        cancelled = client.post(
            f"/api/turns/{cancel_original['turn_id']}/review",
            json={"action": "CANCEL"},
        )
        presentation = client.get(
            f"/api/turns/{cancel_original['turn_id']}/presentation"
        ).json()
    assert cancelled.status_code == 200
    assert cancelled.json()["accepted"] is True
    assert cancelled.json()["new_decision"] == "BLOCK"
    cancel_after = _database_counts(cancel_database, cancel_original["turn_id"])
    assert cancel_after["audits"] == cancel_before["audits"] + 1
    assert cancel_after["children"] == cancel_before["children"]
    assert cancel_after["tokens"] == cancel_before["tokens"]
    assert presentation["decision_result"]["final_decision"] == "BLOCK"
