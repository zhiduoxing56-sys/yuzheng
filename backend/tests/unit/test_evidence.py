from app.core.config import load_yaml
from app.models.schemas import EvidenceStatus, SemanticFrame, VehicleState
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.repository import EvidenceRepository


def test_open_door_generates_exact_mandatory_evidence() -> None:
    frame = SemanticFrame(
        turn_id="TURN_DEMAND",
        raw_text="打开车门",
        normalized_text="打开车门",
        action="打开",
        target="车门",
        area="unknown",
        control_domain="车身控制",
        semantic_confidence=1,
        ambiguity_score=0,
        risk_level="R3",
    )
    updated, demand = EvidenceDemandService(load_yaml("action_evidence_map.yaml")).build(frame)
    expected = [
        "vehicle_speed",
        "gear_position",
        "door_lock_state",
        "occupant_role",
        "speaker_zone",
        "vehicle_mode",
    ]
    assert demand.required_types == expected
    assert updated.required_evidence_types == expected
    assert demand.priority == 100
    assert demand.query_vector == []


def test_minimal_repository_uses_real_snapshot_values() -> None:
    state = VehicleState(vehicle_speed=80, gear_position="D")
    nodes = EvidenceRepository().from_vehicle_state(
        state,
        ["vehicle_speed", "gear_position"],
        [],
        {"occupant_role": "driver", "speaker_zone": "driver"},
    )
    values = {node.evidence_type: node.value for node in nodes}
    assert values == {"vehicle_speed": 80.0, "gear_position": "D"}
    assert all(node.quality_label == EvidenceStatus.VALID for node in nodes)
    assert all(len(node.integrity_hash) == 64 for node in nodes)


def test_repository_marks_unavailable_mandatory_value_missing() -> None:
    state = VehicleState(vehicle_speed=None)
    node = EvidenceRepository().from_vehicle_state(state, ["vehicle_speed"], [], {})[0]
    assert node.value is None
    assert node.quality_label == EvidenceStatus.MISSING
    assert node.availability == 0
