from __future__ import annotations

import pytest

from app.core.config import load_yaml
from app.models.schemas import EvidenceObservationInput, EvidenceStatus, VehicleState
from app.services.evidence.repository import EvidenceRepository
from app.services.quality.evaluator import EvidenceQualityService
from app.services.quality.window import EvidenceQualityWindow


def test_quality_detects_multisource_speed_conflict_and_reduces_ecs() -> None:
    config = load_yaml("evidence_quality.yaml")
    repository = EvidenceRepository(config)
    nodes = repository.ingest_vehicle_state(VehicleState(vehicle_speed=80, gear_position="D"), {}, "T1")
    nodes += repository.ingest_observations(
        [EvidenceObservationInput(evidence_type="VEHICLE_SPEED", source="wheel_speed_sensor", value=20)],
        "T1",
    )
    speed_nodes = [node for node in nodes if node.evidence_type == "VEHICLE_SPEED"]

    evaluated, metrics, conflicts = EvidenceQualityService(config).evaluate(
        speed_nodes,
        ["VEHICLE_SPEED"],
        frozenset(node.node_id for node in speed_nodes),
    )

    assert any(item["type"] == "VEHICLE_SPEED_SOURCE_CONFLICT" for item in conflicts)
    assert metrics.ecr == 1.0
    assert metrics.ecs < 1.0
    assert metrics.eas < 1.0
    assert all(node.quality_label == EvidenceStatus.SUSPICIOUS for node in evaluated)


def test_quality_marks_expired_evidence_stale_and_nulls_non_applicable_ecr() -> None:
    config = load_yaml("evidence_quality.yaml")
    repository = EvidenceRepository(config)
    stale = repository.ingest_observations(
        [
            EvidenceObservationInput(
                evidence_type="VEHICLE_SPEED",
                source="wheel_speed_sensor",
                value=10,
                age_seconds=10,
            )
        ],
        "T2",
    )[0]
    evaluated, metrics, _ = EvidenceQualityService(config).evaluate(
        [stale], [], frozenset()
    )

    assert evaluated[0].quality_label == EvidenceStatus.STALE
    assert evaluated[0].freshness < 1.0
    assert metrics.ecr is None
    assert metrics.evidence_coverage_applicable is False
    expected = (0.25 * metrics.ecs + 0.20 * metrics.ef + 0.20 * metrics.sas) / 0.65
    assert metrics.eas == pytest.approx(expected, abs=1e-6)


def test_sliding_window_records_support_conflict_and_uninvolved_values() -> None:
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    state_nodes = repository.ingest_vehicle_state(
        VehicleState(vehicle_speed=0, gear_position="P"), {}, "T_WINDOW"
    )
    speed = next(node for node in state_nodes if node.evidence_type == "VEHICLE_SPEED")
    gear = next(node for node in state_nodes if node.evidence_type == "GEAR_STATE")
    window = EvidenceQualityWindow(short_length=2)

    first = window.update([speed], [])
    second = window.update(
        [gear],
        [{"evidence_types": ["GEAR_STATE"], "type": "TEST_CONFLICT"}],
    )
    third = window.update([speed], [])

    assert first == {"VEHICLE_SPEED": 1}
    assert second["VEHICLE_SPEED"] == 0
    assert second["GEAR_STATE"] == -1
    assert third["VEHICLE_SPEED"] == 1
    assert third["GEAR_STATE"] == 0
    assert len(window.matrix()) == 2
    assert window.short_term_availability()["VEHICLE_SPEED"] == 1.0
    assert window.short_term_availability()["GEAR_STATE"] == 0.0
    assert window.long_term_availability()["VEHICLE_SPEED"] == 1.0
    assert window.long_term_availability()["GEAR_STATE"] == 0.0
