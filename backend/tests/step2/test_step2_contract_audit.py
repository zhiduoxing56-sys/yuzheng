from __future__ import annotations

import builtins
import json
import sqlite3
from pathlib import Path

from app.core.config import load_yaml
from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    LayerNavigationAvailability,
    RetrievalMetadata,
    ReviewOutcomeRecord,
    TextCommandRequest,
    EvidenceObservationInput,
    TrustedRuntimeContext,
)
from app.services.index.hnsw import HNSWIndexService
from app.services.presentation.assembler import PresentationAssembler
from app.services.vector.embedding import DeterministicHashEmbeddingService


STEP2_METADATA_FIELDS = {
    "index_build_id",
    "index_config_digest",
    "node_set_digest",
    "stable_identity_version",
    "stable_identity_source",
    "content_identity_version",
    "content_identity_source",
    "index_fingerprint_version",
    "node_set_digest_version",
    "build_id_payload_version",
    "classification_mapping_digest",
    "formula_version",
    "formula_source",
    "L",
    "L_source",
    "security_mapping_version",
    "security_rank_mapping_source",
    "index_seed_digest",
    "index_seed_source",
    "random_level_distribution",
    "random_level_source",
    "implementation_source",
    "layering_mode",
    "security_layer_count",
    "security_layers",
    "per_layer_node_count",
    "mapping_coverage",
    "unclassified_types",
    "security_layer_navigation",
    "retrieval_visualization_path",
    "final_top_k_node_ids",
    "mandatory_supplemented_node_ids",
    "internal_hnsw_trace_available",
    "internal_hnsw_trace_reason",
    "navigation_availability",
}


def test_pipeline_persists_real_layer_trace_and_emits_bounded_websocket_summary(pipeline) -> None:
    events = []
    result = pipeline.process_text(
        TextCommandRequest(text="打开车门", session_id="step2-contract"),
        event_sink=events.append,
    )
    metadata = result.retrieval_metadata
    record = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert record is not None

    assert metadata.implementation == "hnswlib"
    assert metadata.degraded is False
    assert metadata.navigation_availability == LayerNavigationAvailability.AVAILABLE
    assert metadata.security_layer_count == 4
    assert len(metadata.security_layers) == 4
    assert metadata.mapping_coverage == 1.0
    assert metadata.unclassified_types == []
    assert metadata.stable_identity_version == "STABLE_PHYSICAL_IDENTITY_V1"
    assert metadata.stable_identity_source == "EXISTING_EVIDENCE_STREAM_KEY"
    assert metadata.content_identity_version == "INDEX_CONTENT_IDENTITY_V1"
    assert metadata.index_fingerprint_version == "STABLE_INDEX_FINGERPRINT_V1"
    assert metadata.node_set_digest_version == "LOGICAL_NODE_MULTISET_V1"
    assert metadata.build_id_payload_version == "HNSW_BUILD_ID_V2"
    assert metadata.classification_mapping_digest is not None
    assert metadata.security_layer_navigation is not None
    assert metadata.security_layer_navigation.is_internal_hnsw_trace is False
    assert metadata.internal_hnsw_trace_available is False
    assert metadata.internal_hnsw_trace_reason == "UNSUPPORTED_BY_PUBLIC_HNSWLIB_API"
    assert record.retrieval_metadata == metadata
    assert record.candidate_recall_results
    assert all(node.security_class is not None for node in record.candidate_recall_results)
    graph_nodes = {node.node_id: node for node in record.evidence_subgraph.nodes}
    assert all(
        graph_nodes[node_id].security_class is not None
        for node_id in metadata.final_top_k_node_ids
    )

    retrieved = next(event for event in events if event.stage == "EVIDENCE_RETRIEVED")
    assert retrieved.payload["index_build_id"] == metadata.index_build_id
    assert retrieved.payload["per_layer_node_count"] == metadata.per_layer_node_count
    assert retrieved.payload["trace_kind"] == "SECURITY_LAYER_INDEX_TRACE"
    assert retrieved.payload["internal_trace_available"] is False
    assert all(
        len(item["candidate_node_ids"]) <= pipeline.index.websocket_candidates_per_layer
        for item in retrieved.payload["per_layer_candidates"]
    )
    assert "query_vector" not in retrieved.model_dump_json()


def test_presentation_and_node_detail_use_persisted_trace_without_requery(api_client, monkeypatch) -> None:
    client, pipeline = api_client
    command = client.post("/api/command/text", json={"text": "打开车门"})
    assert command.status_code == 200
    body = command.json()
    turn_id = body["turn_id"]
    expected_build = body["retrieval_metadata"]["index_build_id"]

    def forbidden_search(*args, **kwargs):
        raise AssertionError("presentation不得重新查询HNSW")

    monkeypatch.setattr(pipeline.index, "search", forbidden_search)
    first = client.get(f"/api/turns/{turn_id}/presentation")
    second = client.get(f"/api/turns/{turn_id}/presentation")
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    summary = first.json()["retrieval_summary"]
    assert summary["index_build_id"] == expected_build
    assert summary["availability"] == "AVAILABLE"
    assert summary["security_layer_count"] == 4
    assert summary["security_layer_navigation"]["trace_kind"] == "SECURITY_LAYER_INDEX_TRACE"
    assert summary["internal_hnsw_trace_available"] is False
    assert "query_vector" not in first.text

    node_id = summary["final_top_k_node_ids"][0]
    detail = client.get(f"/api/turns/{turn_id}/evidence/{node_id}")
    assert detail.status_code == 200
    assert detail.json()["security_class"] in {
        "ENTERTAINMENT",
        "COCKPIT",
        "DRIVING",
        "EMERGENCY",
    }
    assert detail.json()["hnsw_max_layer"] in {0, 1, 2, 3}
    assert detail.json()["classification_source"] is not None


def test_persisted_trace_replays_after_pipeline_restart(tmp_path: Path, monkeypatch) -> None:
    database = tmp_path / "step2-restart.db"
    secret = b"step2-restart-fixed-secret-32byte"
    first_pipeline = CommandPipeline(database_path=database, token_secret=secret, audit_database_role="TEST")
    result = first_pipeline.process_text(TextCommandRequest(text="打开车门"))
    original = result.retrieval_metadata.model_dump(mode="json")

    restarted = CommandPipeline(database_path=database, token_secret=secret, audit_database_role="TEST")
    record = restarted.audit_repository.get_by_turn(result.turn_id)
    assert record is not None

    def forbidden_search(*args, **kwargs):
        raise AssertionError("重启回放不得查询当前索引")

    monkeypatch.setattr(restarted.index, "search", forbidden_search)
    summary = PresentationAssembler(restarted).retrieval(record)
    assert summary.index_build_id == original["index_build_id"]
    assert summary.security_layer_navigation.model_dump(mode="json") == original[
        "security_layer_navigation"
    ]
    assert summary.retrieval_visualization_path == record.retrieval_metadata.retrieval_visualization_path
    assert restarted.audit_repository.verify_chain() is True
    root = record.root_turn_id or record.turn_id
    assert restarted.workflow_repository.verify_chain(root).valid is True


def test_legacy_metadata_is_not_fabricated_as_current_layer_trace(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="打开车门"))
    payload = result.retrieval_metadata.model_dump(mode="json", exclude=STEP2_METADATA_FIELDS)
    legacy = RetrievalMetadata.model_validate(payload)
    record = result.audit.model_copy(update={"retrieval_metadata": legacy})

    summary = PresentationAssembler(pipeline).retrieval(record)
    assert summary.availability == LayerNavigationAvailability.LEGACY_NOT_RECORDED
    assert summary.security_layer_navigation is None
    assert summary.retrieval_visualization_path == []
    assert summary.index_build_id is None


def test_exact_cosine_degradation_has_no_fake_layer_navigation(monkeypatch) -> None:
    real_import = builtins.__import__

    def deny_hnswlib(name, *args, **kwargs):
        if name == "hnswlib":
            raise ImportError("forced step2 degradation")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", deny_hnswlib)
    service = HNSWIndexService(
        load_yaml("index.yaml"), DeterministicHashEmbeddingService(768)
    )
    from app.models.schemas import VehicleState
    from app.services.evidence.repository import EvidenceRepository

    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    nodes = repository.ingest_vehicle_state(
        VehicleState(vehicle_speed=10), {}, "step2-degradation"
    )
    service.build(nodes)
    query, _ = service.embedder.encode("current speed")
    _, metadata = service.search(query)

    assert metadata.degraded is True
    assert metadata.navigation_availability == LayerNavigationAvailability.DEGRADED_UNAVAILABLE
    assert metadata.security_layer_navigation is None
    assert metadata.retrieval_visualization_path == []
    assert metadata.internal_hnsw_trace_available is False


def test_review_outcome_schema_does_not_duplicate_hnsw_trace() -> None:
    fields = set(ReviewOutcomeRecord.model_fields)
    assert fields.isdisjoint(STEP2_METADATA_FIELDS)
    assert "retrieval_metadata" not in fields


def test_tampering_persisted_layer_trace_breaks_audit_chain(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="打开车门"))
    assert pipeline.audit_repository.verify_chain() is True

    with sqlite3.connect(pipeline.audit_repository.database_path) as connection:
        row = connection.execute(
            "SELECT record_json FROM audit_records WHERE turn_id = ?", (result.turn_id,)
        ).fetchone()
        payload = json.loads(row[0])
        payload["retrieval_metadata"]["security_layer_navigation"]["anchor_path"].append(
            "FAKE_NODE"
        )
        connection.execute(
            "UPDATE audit_records SET record_json = ? WHERE turn_id = ?",
            (json.dumps(payload, ensure_ascii=False), result.turn_id),
        )

    assert pipeline.audit_repository.verify_chain() is False


def test_openapi_exposes_step2_presentation_contract(api_client) -> None:
    client, _ = api_client
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    retrieval = schemas["RetrievalSummary"]["properties"]
    candidate = schemas["RetrievalCandidate"]["properties"]
    detail = schemas["EvidenceNodeDetail"]["properties"]

    for field in (
        "index_build_id",
        "layering_mode",
        "security_layer_count",
        "security_layers",
        "mapping_coverage",
        "unclassified_types",
        "security_layer_navigation",
        "retrieval_visualization_path",
        "internal_hnsw_trace_available",
        "internal_hnsw_trace_reason",
        "availability",
    ):
        assert field in retrieval
    for field in ("security_class", "security_rank", "hnsw_max_layer", "layer_memberships"):
        assert field in candidate
    for field in (
        "security_class",
        "security_rank",
        "hnsw_max_layer",
        "layer_memberships",
        "classification_source",
    ):
        assert field in detail


def test_mandatory_recall_stays_after_base_top_k_and_never_masquerades_as_hnsw(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="向左变道"))
    metadata = result.retrieval_metadata
    mandatory_ids = {
        record.recalled_node_id
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for record in resolution.mandatory_recall_records
        if record.recalled_node_id is not None
    }

    assert {
        evidence_type
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for evidence_type in resolution.missing_required_types
    } == {"LANE_STATE"}
    supplemented_ids = set(metadata.mandatory_supplemented_node_ids)
    assert supplemented_ids <= mandatory_ids
    assert mandatory_ids == supplemented_ids | (
        mandatory_ids & set(metadata.final_top_k_node_ids)
    )
    assert supplemented_ids.isdisjoint(metadata.final_top_k_node_ids)
    assert all(
        edge.source == "MANDATORY_RECALL_SERVICE"
        for edge in metadata.retrieval_visualization_path
        if edge.to_node_id in supplemented_ids
    )
    assert result.safety_gate.mandatory_evidence_missing is True
    assert result.decision.final_decision.value == "BLOCK"
    assert result.decision.authorization_token is None

    complete = pipeline.process_text(
        TextCommandRequest(text="向左变道"),
        trusted_context=TrustedRuntimeContext(
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="SURROUNDING_OBJECT_STATE",
                    source="simulated_test_source",
                    value={"clear": True},
                ),
                EvidenceObservationInput(
                    evidence_type="LANE_STATE",
                    source="simulated_test_source",
                    value={"clear": True},
                ),
            ],
        ),
    )
    assert {
        evidence_type
        for resolution in complete.evidence_subgraph.intent_evidence_resolutions
        for evidence_type in resolution.missing_required_types
    } == {"LANE_STATE", "SURROUNDING_OBJECT_STATE"}
    assert set(complete.evidence_demand.intent_demands[0].required_types) == {
        "VEHICLE_SPEED",
        "SURROUNDING_OBJECT_STATE",
        "LANE_STATE",
    }
