from __future__ import annotations

from pydantic import ValidationError
import pytest

from app.core.config import load_yaml
from app.models.schemas import (
    EvidenceDemand,
    EvidenceObservationInput,
    IntentEvidenceBinding,
    IntentEvidenceDemand,
    IntentEvidenceResolution,
    RetrievalOrigin,
    SemanticFrame,
    SemanticIntent,
    RuntimeSafetyContext,
    VehicleState,
)
from app.services.decision.engine import DecisionService
from app.services.decision.safety_gate import SafetyGateService
from app.services.evidence.catalog import (
    CANONICAL_EVIDENCE_TYPES,
    evidence_runtime_mapping,
)
from app.services.evidence.demand import EvidenceDemandService
from app.services.evidence.demand_registry import EvidenceDemandRegistry
from app.services.evidence.recall import MandatoryRecallService
from app.services.evidence.repository import EvidenceRepository
from app.services.graph.builder import EvidenceSubgraphBuilder
from app.services.index.hnsw import HNSWIndexService, evidence_key
from app.services.quality.evaluator import EvidenceQualityService
from app.services.validation.advanced import AdvancedValidationService
from app.services.vector.embedding import DeterministicHashEmbeddingService
from semantic_registry_v1 import UnifiedSemanticRegistry


AGGREGATE_TYPES = {
    "ENVIRONMENT_CONDITIONS",
    "SURROUNDING_OBJECT_STATE",
    "SYSTEM_MODE",
}


def _frame(
    intent_id: str,
    action: str,
    target: str,
    *,
    mode: str | None = None,
) -> SemanticFrame:
    definition = UnifiedSemanticRegistry().definition(intent_id)
    intent = SemanticIntent(
        clause_index=0,
        clause_text=f"{action}{target}",
        intent_id=intent_id,
        runtime_identity=definition["runtime_identity"],
        action=action,
        target=target,
        mode=mode,
        control_attribute=definition["control_attribute"],
        control_domain=definition["control_domain"],
        semantic_confidence=1,
        ambiguity_score=0,
        risk_level=definition["risk_level"],
    )
    return SemanticFrame(
        turn_id="TURN_PHASE2_GATE",
        raw_text=intent.clause_text,
        normalized_text=intent.clause_text,
        semantic_confidence=1,
        ambiguity_score=0,
        semantic_status="OK",
        intents=[intent],
    )


def _demand(frame: SemanticFrame, required: list[str]) -> EvidenceDemand:
    intent = frame.intents[0]
    return EvidenceDemand(
        turn_id=frame.turn_id,
        intent_demands=[
            IntentEvidenceDemand(
                intent_id=intent.intent_id,
                clause_index=0,
                action=intent.action,
                target=intent.target,
                risk_level=intent.risk_level,
                query_text=intent.clause_text,
                required_types=required,
            )
        ],
    )


def _resolution(
    frame: SemanticFrame, required: list[str], nodes: list
) -> list[IntentEvidenceResolution]:
    intent = frame.intents[0]
    by_type = {node.evidence_type: node for node in nodes}
    return [
        IntentEvidenceResolution(
            clause_index=intent.clause_index,
            intent_id=intent.intent_id,
            candidate_node_ids=[node.node_id for node in nodes],
            bindings=[
                IntentEvidenceBinding(
                    clause_index=intent.clause_index,
                    intent_id=intent.intent_id,
                    evidence_type=evidence_type,
                    requirement_level="REQUIRED",
                    node_id=by_type[evidence_type].node_id,
                    resolution_status="RETRIEVED",
                    retrieval_origin=RetrievalOrigin.HNSW,
                )
                for evidence_type in required
            ],
        )
    ]


def _nodes(state: VehicleState) -> list:
    return EvidenceRepository(load_yaml("evidence_quality.yaml")).ingest_vehicle_state(
        state,
        None,
        "TURN_PHASE2_GATE",
    )


def test_catalog_and_runtime_mapping_cover_evidence_space_v1_without_compatibility_fields() -> None:
    mapping = evidence_runtime_mapping()
    assert len(CANONICAL_EVIDENCE_TYPES) == 38
    assert set(mapping) == CANONICAL_EVIDENCE_TYPES
    forbidden = {"legacy_type", "old_name", "aliases", "fallback_names", "compatibility"}
    assert not any(forbidden & set(entry) for entry in mapping.values())
    assert {entry["runtime_mode"] for entry in mapping.values()} <= {
        "DIRECT", "DERIVED", "STATIC", "SIMULATED", "UNAVAILABLE"
    }
    assert sum(entry["runtime_mode"] == "SIMULATED" for entry in mapping.values()) == 13
    assert sum(entry["runtime_mode"] == "UNAVAILABLE" for entry in mapping.values()) == 25
    assert all("usability" in entry for entry in mapping.values())


def test_repository_emits_one_node_per_available_canonical_fact_and_aggregate() -> None:
    nodes = _nodes(VehicleState())
    types = [node.evidence_type for node in nodes]
    assert len(nodes) == 16
    assert len(set(types)) == 13
    assert set(types) <= CANONICAL_EVIDENCE_TYPES
    by_type = {node.evidence_type: node for node in nodes}
    door_nodes = [node for node in nodes if node.evidence_type == "DOOR_STATE"]
    assert {node.metadata.get("area") for node in door_nodes} == {
        "LEFT_FRONT",
        "RIGHT_FRONT",
        "LEFT_REAR",
        "RIGHT_REAR",
    }
    assert len(door_nodes) == 4
    assert all(node.value == {"state": "CLOSED", "position": None} for node in door_nodes)
    assert all(isinstance(by_type[evidence_type].value, dict) for evidence_type in AGGREGATE_TYPES)
    assert by_type["ENVIRONMENT_CONDITIONS"].value["ambient_illumination"] == 100
    assert by_type["SURROUNDING_OBJECT_STATE"].value["front_obstacle_distance"] == 100
    assert "FREE_SPACE_STATE" not in by_type
    assert "OCCUPANT_STATE" not in by_type
    assert set(by_type["SYSTEM_MODE"].value) == {"vehicle_mode", "safety_constraint"}
    assert by_type["AUTHORIZATION_STATE"].quality_label.value == "MISSING"
    assert all(node.metadata["source_fields"] for node in nodes)
    assert all("source_field_availability" in node.metadata for node in nodes)


def test_four_door_nodes_keep_distinct_existing_stream_and_hnsw_identity() -> None:
    nodes = _nodes(VehicleState())
    doors = [node for node in nodes if node.evidence_type == "DOOR_STATE"]

    assert len({EvidenceRepository.stream_key(node) for node in doors}) == 4
    assert len({evidence_key(node) for node in doors}) == 4

    index = HNSWIndexService(
        load_yaml("index.yaml"), DeterministicHashEmbeddingService(768)
    )
    status = index.build(doors)
    assert status.node_count == 4


def test_observation_contract_rejects_old_type_and_accepts_canonical_type() -> None:
    with pytest.raises(ValidationError):
        EvidenceObservationInput(
            evidence_type="vehicle_speed", source="old_type", value=1
        )
    accepted = EvidenceObservationInput(
        evidence_type="VEHICLE_SPEED", source="canonical", value=1
    )
    assert accepted.evidence_type == "VEHICLE_SPEED"


def test_intent_demand_and_hnsw_namespaces_are_exact_catalog_subsets() -> None:
    registry = EvidenceDemandRegistry()
    for intent_id in registry.formal_intent_ids:
        rule = registry.rule_for_intent_id(intent_id)
        assert set(rule.mandatory) <= CANONICAL_EVIDENCE_TYPES
        assert set(rule.recommended) <= CANONICAL_EVIDENCE_TYPES
        for conditional in rule.conditional_mandatory:
            assert set(conditional.add) <= CANONICAL_EVIDENCE_TYPES
    index = HNSWIndexService(
        load_yaml("index.yaml"), DeterministicHashEmbeddingService(768)
    )
    assert set(index.security_classification.evidence_type_mapping) == CANONICAL_EVIDENCE_TYPES
    classified = index.classify_nodes(_nodes(VehicleState()))
    assert all(node.security_rank is not None for node in classified)


def test_mandatory_recall_creates_only_canonical_missing_node() -> None:
    repository = EvidenceRepository(load_yaml("evidence_quality.yaml"))
    embedder = DeterministicHashEmbeddingService(768)
    query, _ = embedder.encode("lane")
    intent_demand = _demand(_frame("DOOR_OPEN", "打开", "车门"), ["LANE_STATE"]).intent_demands[0]
    intent_demand = intent_demand.model_copy(update={"query_vector": query})
    nodes, resolution = MandatoryRecallService(repository, embedder).resolve(
        [], intent_demand, "TURN_PHASE2_MISSING"
    )
    assert resolution.missing_required_types == ["LANE_STATE"]
    assert [node.evidence_type for node in nodes] == ["LANE_STATE"]
    assert resolution.mandatory_recall_records[0].evidence_type == "LANE_STATE"


@pytest.mark.parametrize(
    ("rule_id", "frame", "state", "required"),
    [
        ("MOVING_DOOR_OPEN_PROHIBITED", _frame("DOOR_OPEN", "打开", "车门"), VehicleState(vehicle_speed=1), ["VEHICLE_SPEED"]),
        ("LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED", _frame("HEADLIGHT_SET_MODE", "设置", "前照灯", mode="OFF"), VehicleState(vehicle_speed=1, ambient_light=5), ["VEHICLE_SPEED", "ENVIRONMENT_CONDITIONS"]),
        ("LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED", _frame("LOW_BEAM_OFF", "关闭", "近光灯"), VehicleState(vehicle_speed=1, ambient_light=5), ["VEHICLE_SPEED", "ENVIRONMENT_CONDITIONS"]),
        ("LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED", _frame("HIGH_BEAM_OFF", "关闭", "远光灯"), VehicleState(vehicle_speed=1, ambient_light=5), ["VEHICLE_SPEED", "ENVIRONMENT_CONDITIONS"]),
        ("DENSE_FOG_FRONT_DEFOG_OFF_PROHIBITED", _frame("DEFROST_OFF", "关闭", "前挡风除雾"), VehicleState(weather="DENSE_FOG"), ["ENVIRONMENT_CONDITIONS"]),
        ("NON_DRIVER_DRIVING_CONTROL_PROHIBITED", _frame("ACCELERATE", "加速", "速度"), VehicleState(occupant_role="passenger"), ["AUTHORIZATION_STATE"]),
        ("FRONT_OBSTACLE_ACCELERATION_PROHIBITED", _frame("ACCELERATE", "加速", "速度"), VehicleState(front_obstacle_distance=2), ["SURROUNDING_OBJECT_STATE"]),
        ("REAR_STATE_DECELERATION_CONFLICT", _frame("DECELERATE", "减速", "速度"), VehicleState(rear_obstacle_distance=1), ["SURROUNDING_OBJECT_STATE"]),
    ],
)
def test_safety_gate_reads_canonical_scalar_and_aggregate_values(
    rule_id, frame, state, required
) -> None:
    nodes = _nodes(state)
    result = SafetyGateService(load_yaml("safety_rules.yaml")).evaluate(
        frame,
        _demand(frame, required),
        nodes,
        _resolution(frame, required, nodes),
        runtime_safety_context=RuntimeSafetyContext.from_vehicle_state(state),
    )
    assert rule_id in result.hit_rules


@pytest.mark.parametrize(
    "rear_value",
    [None, "1.0", True, float("nan"), float("inf"), float("-inf")],
)
@pytest.mark.parametrize("intent_id", ["DECELERATE", "BRAKE"])
def test_rear_state_rule_fails_closed_for_unusable_values(
    rear_value, intent_id
) -> None:
    frame = _frame(intent_id, "减速" if intent_id == "DECELERATE" else "打开", "速度")
    nodes = _nodes(VehicleState(rear_obstacle_distance=100))
    nodes = [
        node.model_copy(
            update={
                "value": {
                    **node.value,
                    "rear_obstacle_distance": rear_value,
                }
            }
        )
        if node.evidence_type == "SURROUNDING_OBJECT_STATE"
        else node
        for node in nodes
    ]
    result = SafetyGateService(load_yaml("safety_rules.yaml")).evaluate(
        frame,
        _demand(frame, ["SURROUNDING_OBJECT_STATE"]),
        nodes,
        _resolution(frame, ["SURROUNDING_OBJECT_STATE"], nodes),
        runtime_safety_context=RuntimeSafetyContext(),
    )
    check = next(
        item
        for item in result.checks
        if item.rule_id == "REAR_STATE_DECELERATION_CONFLICT"
    )
    assert check.hit is True
    assert check.observed["rear_state_usable"] is False
    assert check.observed["failure_reason"] == "REAR_OBSTACLE_DISTANCE_UNUSABLE"


def test_emergency_brake_is_not_subject_to_ordinary_rear_rule() -> None:
    frame = _frame("EMERGENCY_BRAKE", "紧急", "制动")
    nodes = _nodes(VehicleState(rear_obstacle_distance=0.1))
    result = SafetyGateService(load_yaml("safety_rules.yaml")).evaluate(
        frame,
        _demand(frame, ["SURROUNDING_OBJECT_STATE"]),
        nodes,
        _resolution(frame, ["SURROUNDING_OBJECT_STATE"], nodes),
        runtime_safety_context=RuntimeSafetyContext(),
    )
    check = next(
        item
        for item in result.checks
        if item.rule_id == "REAR_STATE_DECELERATION_CONFLICT"
    )
    assert check.hit is False
    assert check.observed["rear_state_usable"] is True


def test_decision_necessity_reads_canonical_aggregate_values() -> None:
    frame = _frame("BRAKE", "打开", "制动")
    score, reason = DecisionService(load_yaml("decision_policy.yaml"))._necessity_score(
        frame,
        _nodes(
            VehicleState(
                emergency_flag=True,
                collision_state="COLLISION",
                front_obstacle_distance=2,
                brake_state="REQUIRED",
            )
        ),
    )
    assert score == 1
    assert "紧急" in reason


def test_advanced_validation_keeps_security_signal_and_has_no_historical_claims() -> None:
    frame = _frame("DOOR_OPEN", "打开", "车门").model_copy(
        update={"security_signals": ["PERMISSION_BYPASS"]}
    )
    result = AdvancedValidationService(load_yaml("jailbreak_policy.yaml")).validate(
        frame, _nodes(VehicleState()), []
    )
    assert {claim.claim_type for claim in result.context_claims} == {"security_signal"}
    assert {conflict.rule_id for conflict in result.conflicts} == {
        "SECURITY_SIGNAL_DETECTED"
    }


def test_graph_contains_only_canonical_evidence_nodes() -> None:
    frame = _frame("DOOR_OPEN", "打开", "车门")
    demand = _demand(frame, ["VEHICLE_SPEED"])
    nodes = _nodes(VehicleState())
    evaluated, metrics, conflicts = EvidenceQualityService(
        load_yaml("evidence_quality.yaml")
    ).evaluate(
        nodes,
        ["VEHICLE_SPEED"],
        frozenset(
            node.node_id for node in nodes if node.evidence_type == "VEHICLE_SPEED"
        ),
        scene_nodes=nodes,
    )
    index = HNSWIndexService(
        load_yaml("index.yaml"), DeterministicHashEmbeddingService(768)
    )
    index.build(nodes)
    _, retrieval = index.search(demand.intent_demands[0].query_vector or [0.0] * 768)
    graph = EvidenceSubgraphBuilder().build(
        frame,
        evaluated,
        _resolution(frame, ["VEHICLE_SPEED"], nodes),
        metrics,
        retrieval,
        conflicts,
    )
    assert graph.nodes
    assert {node.evidence_type for node in graph.nodes} <= CANONICAL_EVIDENCE_TYPES
    assert not {"semantic_frame", "evidence_demand", "control_target", "evidence_stream"} & {
        node.evidence_type for node in graph.nodes
    }
