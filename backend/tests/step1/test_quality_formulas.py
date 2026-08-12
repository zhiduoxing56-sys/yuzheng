import pytest
from pydantic import ValidationError

from app.core.config import load_yaml
from app.models.schemas import EvidenceObservationInput, EvidenceStatus
from app.services.evidence.repository import EvidenceRepository
from app.services.quality.evaluator import EvidenceQualityService


def _valid_nodes(count: int):
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    fixtures = [
        ("VEHICLE_SPEED", 1),
        ("SPEED_LIMIT_STATE", 2),
        ("GEAR_STATE", {"current_gear": "D"}),
        ("DOOR_STATE", {"state": "CLOSED"}),
    ]
    return repository.ingest_observations(
        [
            EvidenceObservationInput(
                evidence_type=fixtures[index][0],
                source="simulated_test_source",
                value=fixtures[index][1],
            )
            for index in range(count)
        ],
        "TURN_ECS",
    )


def _valid_named(evidence_type: str, value=1):
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    return repository.ingest_observations(
        [
            EvidenceObservationInput(
                evidence_type=evidence_type,
                source="simulated_test_source",
                value=value,
            )
        ],
        "TURN_ECS_AUXILIARY",
    )[0]


def test_ecs_uses_unique_unordered_pairs_and_excludes_missing(monkeypatch) -> None:
    service = EvidenceQualityService(load_yaml("evidence_quality.yaml"))
    valid = _valid_nodes(4)
    missing = valid[0].model_copy(
        update={
            "node_id": "EVI_MISSING",
            "value": None,
            "timestamp": None,
            "expires_at": None,
            "quality_label": EvidenceStatus.MISSING,
            "availability": 0.0,
        }
    )
    conflicts = [
        {"type": "MULTI", "severity": 2, "node_ids": [valid[0].node_id, valid[1].node_id, valid[2].node_id]},
        {"type": "DUPLICATE", "severity": 1, "node_ids": [valid[2].node_id, valid[1].node_id, missing.node_id]},
    ]
    monkeypatch.setattr(service, "_detect_conflicts", lambda nodes: conflicts)

    _, metrics, detected = service.evaluate([*valid, missing], [], frozenset())

    assert detected == conflicts
    assert metrics.conflict_count == 2  # event count remains an audit fact
    assert metrics.evidence_pair_count == 6  # C(4, 2); MISSING is excluded
    assert metrics.conflict_pair_count == 3  # multi-node event expands and pairs deduplicate
    assert metrics.ecs == 0.5


@pytest.mark.parametrize(
    ("node_count", "conflict_indexes", "pair_count", "conflict_pair_count", "ecs"),
    [
        (0, [], 0, 0, 1.0),
        (1, [], 0, 0, 1.0),
        (2, [], 1, 0, 1.0),
        (2, [(0, 1)], 1, 1, 0.0),
        (3, [(0, 1)], 3, 1, 2 / 3),
        (4, [(0, 1), (2, 3)], 6, 2, 2 / 3),
    ],
)
def test_ecs_report_boundaries(
    monkeypatch, node_count, conflict_indexes, pair_count, conflict_pair_count, ecs
) -> None:
    service = EvidenceQualityService(load_yaml("evidence_quality.yaml"))
    nodes = _valid_nodes(node_count)
    conflicts = [
        {
            "type": f"PAIR_{left}_{right}",
            "severity": 1,
            "node_ids": [nodes[left].node_id, nodes[right].node_id],
        }
        for left, right in conflict_indexes
    ]
    monkeypatch.setattr(service, "_detect_conflicts", lambda evaluated: conflicts)

    _, metrics, _ = service.evaluate(nodes, [], frozenset())

    assert metrics.evidence_pair_count == pair_count
    assert metrics.conflict_pair_count == conflict_pair_count
    assert metrics.conflict_pair_count <= metrics.evidence_pair_count
    assert metrics.ecs == pytest.approx(ecs, abs=1e-6)


@pytest.mark.parametrize("auxiliary_type", ["semantic_frame", "control_target"])
def test_non_evidence_graph_objects_cannot_enter_observation_contract(auxiliary_type) -> None:
    with pytest.raises(ValidationError):
        EvidenceObservationInput(
            evidence_type=auxiliary_type,
            source="invalid_graph_object",
            value={"display_only": True},
        )


def test_ecs_deduplicates_references_to_same_physical_evidence() -> None:
    service = EvidenceQualityService(load_yaml("evidence_quality.yaml"))
    physical = _valid_nodes(2)
    duplicate = physical[0].model_copy(
        update={
            "node_id": "EVI_DUPLICATE_REFERENCE",
            "metadata": {
                **physical[0].metadata,
                "physical_evidence_id": physical[0].node_id,
            },
        }
    )

    evaluated, metrics, _ = service.evaluate(
        [*physical, duplicate], [], frozenset()
    )

    assert metrics.evidence_pair_count == 1
    audited = next(node for node in evaluated if node.node_id == duplicate.node_id)
    assert audited.metadata["included_in_ecs"] is False
    assert (
        audited.metadata["ecs_exclusion_reason"]
        == "DUPLICATE_PHYSICAL_EVIDENCE_REFERENCE"
    )


def test_ecs_new_real_evidence_increases_unordered_pair_denominator() -> None:
    service = EvidenceQualityService(load_yaml("evidence_quality.yaml"))

    _, two_nodes, _ = service.evaluate(_valid_nodes(2), [], frozenset())
    _, three_nodes, _ = service.evaluate(_valid_nodes(3), [], frozenset())

    assert two_nodes.evidence_pair_count == 1
    assert three_nodes.evidence_pair_count == 3


def test_eas_routes_from_real_components_and_active_weights() -> None:
    service = EvidenceQualityService(load_yaml("evidence_quality.yaml"))
    valid = _valid_nodes(2)
    service._detect_conflicts = lambda nodes: []

    _, complete, _ = service.evaluate(
        valid,
        [node.evidence_type for node in valid],
        frozenset(node.node_id for node in valid),
        [1.0, 1.0],
    )
    missing = valid[1].model_copy(
        update={
            "node_id": "EVI_REQUIRED_MISSING",
            "value": None,
            "timestamp": None,
            "expires_at": None,
            "quality_label": EvidenceStatus.MISSING,
            "availability": 0.0,
            "freshness": 0.0,
        }
    )
    _, partial, _ = service.evaluate(
        [valid[0], missing],
        [valid[0].evidence_type, missing.evidence_type],
        frozenset({valid[0].node_id, missing.node_id}),
        [1.0, 0.0],
    )
    _, absent, _ = service.evaluate(
        [
            valid[0].model_copy(
                update={
                    "value": None,
                    "timestamp": None,
                    "expires_at": None,
                    "quality_label": EvidenceStatus.MISSING,
                    "availability": 0.0,
                    "freshness": 0.0,
                }
            )
        ],
        [valid[0].evidence_type],
        frozenset({valid[0].node_id}),
        [0.0],
    )

    assert complete.ecr == 1.0
    assert complete.evidence_alignment_route == "EVIDENCE_PASS"
    assert partial.ecr == 0.5
    assert partial.evidence_alignment_route == "EVIDENCE_REVIEW"
    assert absent.ecr == 0.0
    assert absent.evidence_alignment_route == "EVIDENCE_BLOCK"
    assert sum(complete.eas_weights.values()) == 1.0


def test_high_speed_profile_is_traceable_engineering_configuration() -> None:
    service = EvidenceQualityService(load_yaml("evidence_quality.yaml"))
    speed = _valid_nodes(1)[0].model_copy(
        update={"evidence_type": "VEHICLE_SPEED", "value": 100.0}
    )
    service._detect_conflicts = lambda nodes: []

    _, metrics, _ = service.evaluate([speed], [], frozenset())

    assert metrics.eas_weight_profile == "high_speed"
    assert metrics.eas_weight_source == "ENGINEERING_PROFILE:evidence_quality.yaml#high_speed"
    assert metrics.eas_weights == {
        "ecs": 0.285714,
        "ef": 0.428571,
        "sas": 0.285715,
    }
    assert sum(metrics.eas_weights.values()) == 1.0


def test_complex_road_profile_emphasizes_ecs() -> None:
    service = EvidenceQualityService(load_yaml("evidence_quality.yaml"))
    road = _valid_nodes(1)[0].model_copy(
        update={
            "evidence_type": "ROAD_FRICTION_STATE",
            "value": {"road_condition": "COMPLEX_INTERSECTION"},
        }
    )
    service._detect_conflicts = lambda nodes: []

    _, metrics, _ = service.evaluate([road], [], frozenset())

    assert metrics.eas_weight_profile == "complex_road"
    assert metrics.eas_weight_source.endswith("#complex_road")


@pytest.mark.parametrize(
    ("eas", "expected"),
    [
        (0.85, "EVIDENCE_PASS"),
        (0.60, "EVIDENCE_REVIEW"),
        (0.599999, "EVIDENCE_BLOCK"),
    ],
)
def test_evidence_alignment_route_boundaries(eas, expected) -> None:
    assert EvidenceQualityService.alignment_route(eas) == expected
