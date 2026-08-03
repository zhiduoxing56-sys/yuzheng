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
    RetrievalMetadata,
    SecurityClass,
    SemanticFrame,
    TextCommandRequest,
    VehicleStatePatch,
    utc_now,
)
from app.services.audit.repository import canonical_json
from app.services.evidence.canonicalization import canonicalize_evidence_nodes
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
        evidence_type="safety_rule",
        layer="L3_EMERGENCY",
        source="safety_rule_repository",
        value={"action": "打开", "target": "车门", "rule_id": "RULE_DOOR"},
        timestamp=observed_at,
        expires_at=observed_at + timedelta(minutes=5),
        freshness=0.91,
        consistency=0.92,
        availability=0.93,
        semantic_similarity=sas,
        mandatory=False,
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
        action="打开",
        target="车门",
        area="全车",
        control_domain="vehicle_control",
        semantic_confidence=0.9,
        ambiguity_score=0.1,
        risk_level="R3",
    )


def _demand() -> EvidenceDemand:
    return EvidenceDemand(
        turn_id="TURN_CANONICAL_FIXED",
        action="打开",
        target="车门",
        risk_level="R3",
        query_text="打开 车门",
        required_types=[],
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


def test_field_level_canonicalization_is_order_independent_and_preserves_query_sas() -> None:
    query_node = _node(
        sas=0.668181,
        metadata={"retrieval_origin": "semantic_retrieval", "retrieval_rank": 1},
    )
    repository_node = _node(
        sas=0.0,
        metadata={"rule_id": "RULE_DOOR", "area": "door"},
    )
    first = canonicalize_evidence_nodes(
        [
            ("HNSW_QUERY_EVALUATED", [query_node]),
            ("SAFETY_RULE_REPOSITORY", [repository_node]),
        ]
    )
    second = canonicalize_evidence_nodes(
        [
            ("SAFETY_RULE_REPOSITORY", [repository_node]),
            ("HNSW_QUERY_EVALUATED", [query_node]),
        ]
    )

    assert [item.model_dump(mode="json") for item in first] == [
        item.model_dump(mode="json") for item in second
    ]
    canonical = first[0]
    assert canonical.semantic_similarity == pytest.approx(0.668181)
    assert canonical.metadata["retrieval_rank"] == 1
    assert canonical.metadata["rule_id"] == "RULE_DOOR"
    assert canonical.field_resolution["semantic_similarity"] == "HNSW_QUERY_EVALUATED"
    assert canonical.canonicalization_warnings


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
        [canonical], _frame(), []
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
        metadata={"rule_id": "RULE_DOOR", "area": "door"},
    )
    graph = EvidenceSubgraphBuilder().build(
        _frame(),
        _demand(),
        [query_node],
        [],
        [],
        [],
        _quality(),
        _retrieval(),
        [],
        [repository_node],
    )
    canonical = next(node for node in graph.nodes if node.node_id == query_node.node_id)
    memory = DualMemoryService(load_yaml("memory.yaml")).propagate(
        [canonical],
        _frame(),
        [],
        retrieval_origins={canonical.node_id: "HNSW"},
    )

    assert canonical.semantic_similarity == pytest.approx(0.668181)
    assert memory.initial_confidences[canonical.node_id] == pytest.approx(
        canonical.semantic_similarity
    )


def test_pipeline_persists_one_sas_across_graph_audit_presentation_and_restart(tmp_path) -> None:
    database = tmp_path / "canonical-restart.db"
    pipeline = CommandPipeline(database, token_secret=TEST_SECRET)
    result = pipeline.process_text(
        TextCommandRequest(
            text="驻车打开车门",
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
        )
    )
    record = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert record is not None
    assert record.evidence_subgraph is not None
    assert record.memory_propagation is not None
    graph_by_id = {node.node_id: node for node in record.evidence_subgraph.nodes}
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
        assert graph_node.semantic_similarity == pytest.approx(initial)
        assert presented_by_id[node_id].semantic_similarity == pytest.approx(initial)
        assert detail.semantic_similarity == pytest.approx(initial)
        assert detail.memory_initial_confidence == pytest.approx(initial)
        assert detail.canonicalization_source == graph_node.canonicalization_source

    restarted = CommandPipeline(database, token_secret=TEST_SECRET)
    restored = restarted.audit_repository.get_by_turn(result.turn_id)
    assert restored is not None
    restored_graph = {node.node_id: node for node in restored.evidence_subgraph.nodes}
    for node_id in normal_ids:
        assert restored_graph[node_id].semantic_similarity == pytest.approx(
            restored.memory_propagation.initial_confidences[node_id]
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
    app = create_app(database_path=database, token_secret=TEST_SECRET)
    with TestClient(app) as client:
        original = client.post(
            "/api/command/text",
            json={
                "text": "可能播放音乐",
                "state_overrides": {"vehicle_speed": 0, "gear_position": "P"},
            },
        ).json()
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

    restarted = create_app(database_path=database, token_secret=TEST_SECRET)
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
    app = create_app(database_path=database, token_secret=TEST_SECRET)
    with TestClient(app) as client:
        original = client.post(
            "/api/command/text",
            json={
                "text": "可能播放音乐",
                "state_overrides": {"vehicle_speed": 0, "gear_position": "P"},
            },
        ).json()
    candidate_id = _invalidate_persisted_candidate(
        database, original["audit"]["audit_id"]
    )
    before = _database_counts(database, original["turn_id"])
    restarted = create_app(database_path=database, token_secret=TEST_SECRET)
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
    correct_app = create_app(database_path=correct_database, token_secret=TEST_SECRET)
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
    cancel_app = create_app(database_path=cancel_database, token_secret=TEST_SECRET)
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
