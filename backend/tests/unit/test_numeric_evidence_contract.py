from __future__ import annotations

import hashlib
import json
from datetime import timedelta

import pytest
from pydantic import ValidationError

from app.core.config import load_yaml
from app.models.schemas import (
    EvidenceNode,
    EvidenceDemand,
    EvidenceObservationInput,
    EvidenceStatus,
    IntentEvidenceBinding,
    IntentEvidenceDemand,
    IntentEvidenceResolution,
    RetrievalOrigin,
    SemanticFrame,
    SemanticIntent,
    RuntimeSafetyContext,
    VehicleState,
    VehicleStatePatch,
    utc_now,
)
from app.services.decision.safety_gate import SafetyGateService
from app.services.evidence.repository import EvidenceRepository
from app.services.evidence.catalog import evidence_runtime_mapping
from app.services.evidence.value_contract import (
    is_finite_number,
    validate_evidence_value,
)
from app.services.quality.evaluator import EvidenceQualityService


class OpaqueValue:
    pass


def _observation_node(evidence_type: str, value: object) -> EvidenceNode:
    repository = EvidenceRepository()
    return repository.ingest_observations(
        [
            EvidenceObservationInput(
                evidence_type=evidence_type,
                source="contract_test_sensor",
                value=value,
            )
        ],
        "TURN_VALUE_CONTRACT",
    )[0]


def _bypass_node(evidence_type: str, value: object) -> EvidenceNode:
    timestamp = utc_now()
    payload = {
        "evidence_type": evidence_type,
        "source": "bypass_test_sensor",
        "value": value,
        "timestamp": timestamp.isoformat(),
    }
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return EvidenceNode(
        evidence_type=evidence_type,
        layer="L2_DRIVING",
        source="bypass_test_sensor",
        value=value,
        timestamp=timestamp,
        expires_at=timestamp + timedelta(seconds=30),
        freshness=1,
        consistency=1,
        availability=1,
        quality_label=EvidenceStatus.VALID,
        integrity_hash=digest,
        metadata={
            "integrity_payload": payload,
            "expected_integrity_hash": digest,
        },
    )


@pytest.mark.parametrize("value", [0, 20, 20.5], ids=["zero", "integer", "float"])
def test_repository_accepts_finite_numeric_vehicle_speed(value: int | float) -> None:
    node = _observation_node("VEHICLE_SPEED", value)

    assert node.value == value
    assert node.quality_label == EvidenceStatus.VALID
    assert node.availability == 1
    assert "value_validation_reason" not in node.metadata


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        ("20", "INVALID_NUMBER:value"),
        ("20.5", "INVALID_NUMBER:value"),
        ("abc", "INVALID_NUMBER:value"),
        (True, "INVALID_NUMBER:value"),
        (False, "INVALID_NUMBER:value"),
        (float("nan"), "INVALID_NUMBER:value"),
        (float("inf"), "INVALID_NUMBER:value"),
        (float("-inf"), "INVALID_NUMBER:value"),
        ({"value": 20}, "INVALID_NUMBER:value"),
        ([20], "INVALID_NUMBER:value"),
        (OpaqueValue(), "INVALID_NUMBER:value"),
    ],
    ids=[
        "numeric_string",
        "decimal_string",
        "text",
        "true",
        "false",
        "nan",
        "positive_infinity",
        "negative_infinity",
        "mapping",
        "list",
        "opaque_object",
    ],
)
def test_repository_rejects_invalid_vehicle_speed_without_retaining_raw_value(
    value: object, reason: str
) -> None:
    node = _observation_node("VEHICLE_SPEED", value)

    assert node.value is None
    assert node.quality_label == EvidenceStatus.MISSING
    assert node.availability == 0
    assert node.freshness == 0
    assert node.consistency == 0
    assert node.metadata["value_validation_reason"] == reason
    assert node.metadata["received_value_type"] == type(value).__name__
    assert node.metadata["raw_value_retained"] is False
    assert node.metadata["integrity_payload"]["value"] is None


def test_repository_keeps_none_as_existing_missing_semantics() -> None:
    node = _observation_node("VEHICLE_SPEED", None)

    assert node.value is None
    assert node.quality_label == EvidenceStatus.MISSING
    assert node.availability == 0
    assert "value_validation_reason" not in node.metadata


@pytest.mark.parametrize(
    "evidence_type",
    sorted(
        evidence_type
        for evidence_type, mapping in evidence_runtime_mapping().items()
        if mapping["value_schema"]["type"] == "number"
    ),
)
def test_all_strict_numeric_safety_evidence_types_share_contract(
    evidence_type: str,
) -> None:
    assert _observation_node(evidence_type, 3).quality_label == EvidenceStatus.VALID
    rejected = _observation_node(evidence_type, "3")
    assert rejected.quality_label == EvidenceStatus.MISSING
    assert rejected.metadata["value_validation_reason"] == "INVALID_NUMBER:value"


@pytest.mark.parametrize(
    "value", [5, 5.5, "low", "DARK", "NIGHT", True]
)
def test_ambient_light_preserves_numeric_and_existing_categorical_values(
    value: int | float | str,
) -> None:
    node = _observation_node("ENVIRONMENT_CONDITIONS", {"ambient_illumination": value})
    assert node.value["ambient_illumination"] == value
    assert node.quality_label == EvidenceStatus.VALID


@pytest.mark.parametrize("value", ["5", "BRIGHT", " LOW "])
def test_ambient_light_any_schema_accepts_values_without_type_guessing(value: object) -> None:
    node = _observation_node("ENVIRONMENT_CONDITIONS", {"ambient_illumination": value})
    assert node.value == {"ambient_illumination": value}
    assert node.quality_label == EvidenceStatus.VALID


def test_finite_number_predicate_explicitly_excludes_bool_and_non_finite() -> None:
    assert is_finite_number(0)
    assert is_finite_number(20.5)
    assert not is_finite_number(True)
    assert not is_finite_number(False)
    assert not is_finite_number(float("nan"))
    assert not is_finite_number(float("inf"))
    assert is_finite_number(10**1000)


@pytest.mark.parametrize("model", [VehicleState, VehicleStatePatch])
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("vehicle_speed", "20"),
        ("vehicle_speed", True),
        ("front_obstacle_distance", "3"),
        ("rear_obstacle_distance", False),
        ("speed_limit", float("inf")),
        ("ambient_light", "5"),
    ],
)
def test_vehicle_models_reject_wide_numeric_values_before_pydantic_coercion(
    model, field: str, value: object
) -> None:
    with pytest.raises(ValidationError):
        model(**{field: value})


@pytest.mark.parametrize("model", [VehicleState, VehicleStatePatch])
def test_vehicle_models_preserve_legal_numeric_and_ambient_light_values(model) -> None:
    instance = model(vehicle_speed=20, ambient_light="low")
    assert instance.vehicle_speed == 20
    assert instance.ambient_light == "low"


def test_quality_rejects_valid_label_that_bypassed_repository_contract() -> None:
    node = _bypass_node("VEHICLE_SPEED", "20")
    quality = EvidenceQualityService(load_yaml("evidence_quality.yaml"))

    evaluated, metrics, conflicts = quality.evaluate(
        [node],
        ["VEHICLE_SPEED"],
        frozenset({node.node_id}),
        now=node.timestamp,
    )

    assert evaluated[0].quality_label == EvidenceStatus.MISSING
    assert evaluated[0].value is None
    assert evaluated[0].availability == 0
    assert evaluated[0].metadata["value_validation_reason"] == "INVALID_NUMBER:value"
    assert metrics.ecr == 0
    assert conflicts == []


def test_quality_safely_rejects_non_serializable_object_bypassing_repository() -> None:
    timestamp = utc_now()
    raw_value = OpaqueValue()
    node = EvidenceNode(
        evidence_type="VEHICLE_SPEED",
        layer="L2_DRIVING",
        source="opaque_bypass_sensor",
        value=raw_value,
        timestamp=timestamp,
        expires_at=timestamp + timedelta(seconds=30),
        freshness=1,
        consistency=1,
        availability=1,
        quality_label=EvidenceStatus.VALID,
        integrity_hash="0" * 64,
        metadata={
            "integrity_payload": {
                "evidence_type": "VEHICLE_SPEED",
                "source": "opaque_bypass_sensor",
                "value": raw_value,
                "timestamp": timestamp.isoformat(),
            }
        },
    )
    quality = EvidenceQualityService(load_yaml("evidence_quality.yaml"))

    evaluated, metrics, _ = quality.evaluate(
        [node],
        ["VEHICLE_SPEED"],
        frozenset({node.node_id}),
        now=timestamp,
    )

    assert evaluated[0].quality_label == EvidenceStatus.MISSING
    assert evaluated[0].value is None
    assert evaluated[0].metadata["integrity_payload"]["value"] is None
    assert evaluated[0].metadata["received_value_type"] == "OpaqueValue"
    assert metrics.ecr == 0


def test_gate_fails_closed_on_upstream_contract_violation_without_mutating_node() -> None:
    node = _bypass_node("VEHICLE_SPEED", "20")
    frame = SemanticFrame(
        turn_id="TURN_GATE_CONTRACT",
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
    demand = EvidenceDemand(
        turn_id=frame.turn_id,
        intent_demands=[
            IntentEvidenceDemand(
                intent_id="DOOR_OPEN",
                clause_index=0,
                action="打开",
                target="车门",
                risk_level="R3",
                query_text="DOOR_OPEN 打开 车门",
                required_types=["VEHICLE_SPEED"],
            )
        ],
    )
    gate = SafetyGateService(load_yaml("safety_rules.yaml")).evaluate(
        frame,
        demand,
        [node],
        [
            IntentEvidenceResolution(
                clause_index=0,
                intent_id="DOOR_OPEN",
                candidate_node_ids=[node.node_id],
                bindings=[
                    IntentEvidenceBinding(
                        clause_index=0,
                        intent_id="DOOR_OPEN",
                        evidence_type="VEHICLE_SPEED",
                        requirement_level="REQUIRED",
                        node_id=node.node_id,
                        resolution_status="RETRIEVED",
                        retrieval_origin=RetrievalOrigin.HNSW,
                    )
                ],
            )
        ],
        runtime_safety_context=RuntimeSafetyContext(),
    )

    missing = next(
        check for check in gate.checks if check.rule_id == "MANDATORY_EVIDENCE_AVAILABLE"
    )
    moving = next(
        check for check in gate.checks if check.rule_id == "MOVING_DOOR_OPEN_PROHIBITED"
    )
    assert gate.blocked is True
    assert missing.hit is True
    assert missing.observed["missing_types"] == ["VEHICLE_SPEED"]
    assert missing.observed["upstream_value_contract_violations"] == [
        validate_evidence_value("VEHICLE_SPEED", "20").violation_summary()
    ]
    assert moving.hit is False
    assert node.quality_label == EvidenceStatus.VALID
    assert node.value == "20"
