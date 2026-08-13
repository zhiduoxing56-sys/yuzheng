from app.models.schemas import EvidenceStatus, SemanticFrame, SemanticIntent, VehicleState
import math

import pytest

from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.demand_registry import EvidenceDemandRegistry
from app.services.evidence.repository import EvidenceRepository
from app.services.index.hnsw import evidence_text


def test_open_door_generates_exact_mandatory_evidence() -> None:
    frame = SemanticFrame(
        turn_id="TURN_DEMAND",
        raw_text="打开车门",
        normalized_text="打开车门",
        semantic_confidence=1,
        ambiguity_score=0,
        semantic_status="OK",
        intents=[
            SemanticIntent(
                clause_index=0,
                clause_text="打开车门",
                intent_id="DOOR_OPEN",
                action="打开",
                target="车门",
                control_domain="车身控制",
                semantic_confidence=1,
                ambiguity_score=0,
                risk_level="R3",
            )
        ],
    )
    demand = EvidenceDemandService(EvidenceDemandRegistry()).build(frame)
    intent_demand = demand.intent_demands[0]
    expected = [
        "VEHICLE_SPEED",
        "GEAR_STATE",
        "SURROUNDING_OBJECT_STATE",
    ]
    assert intent_demand.required_types == expected
    assert intent_demand.optional_types == ["DOOR_STATE", "OCCUPANT_STATE"]
    assert intent_demand.query_text == (
        "DOOR_OPEN 打开 车门 "
        "REQUIRED VEHICLE_SPEED GEAR_STATE SURROUNDING_OBJECT_STATE "
        "OPTIONAL DOOR_STATE OCCUPANT_STATE"
    )
    assert "R3" not in intent_demand.query_text
    assert "车身安全" not in intent_demand.query_text
    assert "运动中误操作" not in intent_demand.query_text
    assert intent_demand.priority == 0
    assert intent_demand.retrieval_scope == "control_evidence"
    assert len(intent_demand.query_vector) == 768
    assert math.sqrt(sum(value * value for value in intent_demand.query_vector)) == pytest.approx(1.0)
    assert intent_demand.vectorization_metadata is not None
    assert intent_demand.vectorization_metadata.dimension == 768
    assert intent_demand.vectorization_metadata.normalized is True
    repeated = EvidenceDemandService(EvidenceDemandRegistry()).build(frame)
    assert repeated.intent_demands[0].query_vector == intent_demand.query_vector
    assert (
        repeated.intent_demands[0].vectorization_metadata.vector_digest
        == intent_demand.vectorization_metadata.vector_digest
    )


def test_query_document_uses_final_demand_and_canonical_area_without_risk() -> None:
    frame = SemanticFrame(
        turn_id="TURN_AREA_DEMAND",
        raw_text="打开右前车门",
        normalized_text="打开右前车门",
        semantic_confidence=1,
        ambiguity_score=0,
        semantic_status="OK",
        intents=[
            SemanticIntent(
                clause_index=0,
                clause_text="打开右前车门",
                intent_id="DOOR_OPEN",
                action="打开",
                target="车门",
                area="RIGHT_FRONT",
                control_domain="车身控制",
                semantic_confidence=1,
                ambiguity_score=0,
                risk_level="R3",
                risk_tags=["车身安全", "运动中误操作"],
            )
        ],
    )

    demand = EvidenceDemandService(EvidenceDemandRegistry()).build(frame).intent_demands[0]

    assert demand.query_text == (
        "DOOR_OPEN 打开 车门 RIGHT_FRONT "
        "REQUIRED VEHICLE_SPEED GEAR_STATE SURROUNDING_OBJECT_STATE "
        "OPTIONAL DOOR_STATE OCCUPANT_STATE"
    )
    assert demand.required_types == [
        "VEHICLE_SPEED",
        "GEAR_STATE",
        "SURROUNDING_OBJECT_STATE",
    ]
    assert demand.optional_types == ["DOOR_STATE", "OCCUPANT_STATE"]


def test_node_document_is_canonical_stable_and_area_scoped() -> None:
    nodes = EvidenceRepository().ingest_vehicle_state(
        VehicleState(door_state="CLOSED"), None, "TURN_NODE_DOCUMENT"
    )
    right_front = next(
        node
        for node in nodes
        if node.evidence_type == "DOOR_STATE"
        and node.metadata.get("area") == "RIGHT_FRONT"
    )
    document = evidence_text(right_front)
    changed = right_front.model_copy(update={"value": {"state": "OPEN", "position": 50}})

    assert document == (
        "DOOR_STATE 车门开闭与开度状态 目标车门当前开闭与开度。 RIGHT_FRONT"
    )
    assert evidence_text(changed) == document
    assert right_front.layer not in document
    assert right_front.source not in document
    assert "CLOSED" not in document


def test_minimal_repository_uses_real_snapshot_values() -> None:
    state = VehicleState(vehicle_speed=80, gear_position="D")
    nodes = EvidenceRepository().ingest_vehicle_state(
        state, None, "TURN_STATE"
    )
    values = {node.evidence_type: node.value for node in nodes}
    assert values["VEHICLE_SPEED"] == 80.0
    assert values["GEAR_STATE"]["current_gear"] == "D"
    assert all(
        node.quality_label == EvidenceStatus.VALID
        for node in nodes
        if node.evidence_type != "AUTHORIZATION_STATE"
    )
    assert next(
        node for node in nodes if node.evidence_type == "AUTHORIZATION_STATE"
    ).quality_label == EvidenceStatus.MISSING
    assert all(len(node.integrity_hash) == 64 for node in nodes)


def test_repository_marks_unavailable_mandatory_value_missing() -> None:
    state = VehicleState(vehicle_speed=None)
    nodes = EvidenceRepository().ingest_vehicle_state(state, {}, "TURN_MISSING_STATE")
    node = next(item for item in nodes if item.evidence_type == "VEHICLE_SPEED")
    assert node.value is None
    assert node.quality_label == EvidenceStatus.MISSING
    assert node.availability == 0
