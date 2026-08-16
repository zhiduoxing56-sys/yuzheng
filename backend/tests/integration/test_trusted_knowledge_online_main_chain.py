from __future__ import annotations

from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    AuditDatabaseRole,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleStatePatch,
)


def test_production_main_chain_uses_filtered_trusted_knowledge_hnsw(tmp_path) -> None:
    pipeline = CommandPipeline(
        database_path=tmp_path / "audit.db",
        token_secret=b"knowledge-hnsw-main-chain-secret",
        audit_database_role=AuditDatabaseRole.TEST,
    )
    response = pipeline.process_text(
        TextCommandRequest(text="打开右后车门"),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=30, gear_position="D"),
            subject_role="driver",
            subject_zone="driver",
            subject_source="knowledge_hnsw_integration",
            zone_source="knowledge_hnsw_integration",
        ),
    )
    assert response.semantic_frame.semantic_status == "OK"
    demand = response.evidence_demand.intent_demands[0]
    assert demand.intent_id == "DOOR_OPEN"
    assert demand.knowledge_hits
    assert all(hit["canonical_action"] == "DOOR_OPEN" for hit in demand.knowledge_hits)
    assert all(hit["match_route"] == "HNSW_FILTERED" for hit in demand.knowledge_hits)
    assert demand.knowledge_retrieval_metadata["raw_results"]
    assert demand.knowledge_query_text.startswith("意图=DOOR_OPEN")
    assert "DOOR_STATE" in demand.knowledge_augmented_types
    source = next(
        item
        for item in demand.knowledge_demand_sources
        if item["evidence_type"] == "DOOR_STATE"
    )
    assert source["matched_intent_id"] == "DOOR_OPEN"
    assert source["clause_index"] == 0
