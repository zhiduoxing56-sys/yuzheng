from __future__ import annotations

from app.core.config import load_yaml
from app.models.schemas import TextCommandRequest, VehicleState, VehicleStatePatch
from app.services.evidence.repository import EvidenceRepository


def test_active_turn_is_protected_then_dynamic_stream_is_trimmed() -> None:
    repository = EvidenceRepository(
        load_yaml("evidence_quality.yaml"), load_yaml("evidence_retention.yaml")
    )
    state = VehicleState()
    repository.begin_turn("ACTIVE")
    for _ in range(20):
        repository.ingest_vehicle_state(state, {}, "ACTIVE")
    speed_key = "vehicle_speed|simulator_vehicle_state|global"
    assert len(repository._stream_nodes[speed_key]) == 20
    assert len(repository.turn_nodes("ACTIVE")) > 0

    repository.complete_turn("ACTIVE")
    assert len(repository._stream_nodes[speed_key]) == 16
    assert repository.status().evicted_node_count > 0


def test_one_thousand_turns_keep_repository_and_hnsw_bounded(pipeline) -> None:
    initial_canonical = pipeline.index.status().canonical_node_count
    first_turn_id = None
    last_result = None
    request = TextCommandRequest(
        text="查询当前速度",
        speaker_role="driver",
        speaker_zone="driver",
        state_overrides=VehicleStatePatch(vehicle_speed=42, gear_position="D"),
    )
    for _ in range(1000):
        last_result = pipeline.process_text(request)
        first_turn_id = first_turn_id or last_result.turn_id

    assert last_result is not None and first_turn_id is not None
    index_status = pipeline.index.status()
    repository_status = pipeline.evidence_repository.status()
    assert index_status.degraded is False
    assert index_status.canonical_node_count == initial_canonical
    assert repository_status.retained_turn_count <= 64
    assert all(
        len(node_ids) <= 16
        for key, node_ids in pipeline.evidence_repository._stream_nodes.items()
        if not any(
            node_id in pipeline.evidence_repository._static_node_ids
            for node_id in node_ids
        )
    )
    theoretical_limit = repository_status.stream_count * 16 + repository_status.static_node_count
    assert repository_status.resident_node_count <= theoretical_limit
    assert any(
        node.evidence_type == "safety_rule"
        for node in pipeline.evidence_repository.current_nodes()
    )
    latest_speed = next(
        node
        for node in pipeline.evidence_repository.current_nodes()
        if node.evidence_type == "vehicle_speed"
        and node.source == "simulator_vehicle_state"
    )
    assert latest_speed.value == 42
    assert pipeline.audit_repository.get_by_turn(first_turn_id) is not None
    assert pipeline.audit_repository.verify_chain() is True
    assert pipeline.workflow_repository.verify_chain(first_turn_id).valid is True
    assert pipeline.workflow_repository.verify_chain(last_result.root_turn_id).valid is True
