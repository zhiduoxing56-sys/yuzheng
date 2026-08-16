from __future__ import annotations

from app.models.schemas import (
    EvidenceObservationInput,
    IntentEvidenceDemand,
    SemanticIntent,
)
from app.services.evidence.catalog import CANONICAL_EVIDENCE_TYPES
from app.services.evidence.repository import EvidenceRepository
from app.services.index.trusted_knowledge import TrustedKnowledgeIndexService
from app.services.vector.embedding import DeterministicHashEmbeddingService


def _service() -> TrustedKnowledgeIndexService:
    return TrustedKnowledgeIndexService(
        {
            "enabled": False,
            "context": {"low_light_max_lux": 20, "high_speed_min_kph": 80},
        },
        DeterministicHashEmbeddingService(64),
        CANONICAL_EVIDENCE_TYPES,
    )


def _demand(
    *,
    required_types: list[str] | None = None,
    optional_types: list[str] | None = None,
) -> IntentEvidenceDemand:
    return IntentEvidenceDemand(
        intent_id="DOOR_OPEN",
        clause_index=0,
        action="打开",
        target="车门",
        area="RIGHT_REAR",
        risk_level="R3",
        query_text="",
        required_types=(
            required_types
            if required_types is not None
            else ["VEHICLE_SPEED", "GEAR_STATE", "SURROUNDING_OBJECT_STATE", "DOOR_STATE"]
        ),
        optional_types=(optional_types if optional_types is not None else ["OCCUPANT_STATE"]),
    )


def _intent() -> SemanticIntent:
    return SemanticIntent(
        clause_index=0,
        clause_text="打开右后车门",
        intent_id="DOOR_OPEN",
        runtime_identity="FORMAL",
        action="打开",
        target="车门",
        area="RIGHT_REAR",
        control_attribute="开闭状态",
        control_domain="车身控制",
        risk_level="R3",
        semantic_confidence=1.0,
        ambiguity_score=0.0,
    )


def _nodes(*observations: EvidenceObservationInput):
    return EvidenceRepository().ingest_observations(list(observations), "TURN_CONTEXT")


def _observation(evidence_type: str, value, **updates) -> EvidenceObservationInput:
    return EvidenceObservationInput(
        evidence_type=evidence_type,
        source=updates.pop("source", "SIMULATION"),
        value=value,
        **updates,
    )


def test_complete_context_projection_uses_formal_evidence_and_provenance() -> None:
    service = _service()
    nodes = _nodes(
        _observation("VEHICLE_SPEED", 42),
        _observation("GEAR_STATE", {"current_gear": "D"}),
        _observation(
            "ROAD_FRICTION_STATE",
            {
                "road_condition": "WET",
                "wetness": "WET",
                "friction_scale_factor": 0.4,
                "lower_bound": 0.3,
                "most_probable": 0.4,
                "upper_bound": 0.5,
            },
        ),
        _observation(
            "ENVIRONMENT_CONDITIONS",
            {
                "ambient_illumination": 5,
                "visibility": 60,
                "weather": "RAIN",
                "precipitation_type": "RAIN",
                "fog": "NONE",
            },
        ),
        _observation(
            "SURROUNDING_OBJECT_STATE",
            {
                "objects": [
                    {
                        "object_id": "bicycle-right-rear",
                        "entity_kind": "BICYCLE",
                        "region": "REAR_RIGHT",
                        "exists": True,
                        "distance": 3.0,
                        "relative_speed": -5.0,
                        "motion_state": "APPROACHING",
                        "risk_level": "HIGH",
                        "source_kind": "SIMULATION",
                    }
                ]
            },
        ),
        _observation(
            "SYSTEM_MODE",
            {"vehicle_mode": "REAL_DRIVING", "simulation": True},
        ),
        _observation(
            "AUTHORIZATION_STATE",
            {
                "authentication_state": "AUTHENTICATED",
                "authenticated": True,
                "subject_role": "driver",
                "subject_zone": "driver",
                "intent_authorizations": [
                    {
                        "clause_index": 0,
                        "intent_id": "DOOR_OPEN",
                        "control_domain": "车身控制",
                        "permission_label": "ALLOW",
                        "permission_score": 1.0,
                        "authorized": True,
                    }
                ],
                "authorized_for_request": True,
            },
            source="AUTHORIZATION_SERVICE",
        ),
    )
    demand = _demand(
        required_types=[
            "VEHICLE_SPEED",
            "GEAR_STATE",
            "ROAD_FRICTION_STATE",
            "ENVIRONMENT_CONDITIONS",
            "SURROUNDING_OBJECT_STATE",
            "SYSTEM_MODE",
            "AUTHORIZATION_STATE",
        ],
        optional_types=[],
    )
    intent = _intent()
    fields = service._project_context_fields(
        nodes,
        semantic_intent=intent,
        demand=demand,
    )
    query = service.build_query_text(
        demand,
        semantic_intent=intent,
        context_fields=fields,
    )

    expected_fragments = [
        "运动状态=行驶",
        "速度等级=普通速度",
        "挡位=D",
        "天气=RAIN",
        "降水=RAIN",
        "光照=低照度",
        "能见度=低",
        "道路状态=WET",
        "道路湿度=WET",
        "道路附着系数=0.4",
        "目标区域=REAR_RIGHT",
        "区域目标=存在",
        "目标类型=BICYCLE",
        "目标距离=3m",
        "目标相对速度=-5m/s",
        "目标运动=APPROACHING",
        "目标风险=HIGH",
        "系统模式=REAL_DRIVING",
        "授权状态=已授权",
    ]
    assert all(fragment in query for fragment in expected_fragments)
    assert "道路附着=低" not in query
    assert all(item["node_id"] for item in fields)
    assert all(item["evidence_type"] for item in fields)
    assert all(item["source"] for item in fields)


def test_invalid_unavailable_and_expired_evidence_is_omitted() -> None:
    service = _service()
    nodes = _nodes(
        _observation(
            "GEAR_STATE",
            {"current_gear": "D"},
            available=False,
        ),
        _observation(
            "ENVIRONMENT_CONDITIONS",
            {"visibility": 60, "weather": "RAIN"},
            age_seconds=10,
            expires_in_seconds=1,
        ),
        _observation(
            "ROAD_FRICTION_STATE",
            {"road_condition": "WET"},
            integrity_valid=False,
        ),
    )
    demand = _demand()
    intent = _intent()
    fields = service._project_context_fields(
        nodes,
        semantic_intent=intent,
        demand=demand,
    )
    query = service.build_query_text(
        demand,
        semantic_intent=intent,
        context_fields=fields,
    )
    assert "挡位=" not in query
    assert "能见度=" not in query
    assert "道路状态=" not in query

    projection = service._context_projection(
        nodes,
        semantic_intent=intent,
        demand=demand,
    )
    reasons = {item["evidence_type"]: item["reason"] for item in projection["excluded"]}
    assert reasons["GEAR_STATE"] == "UNAVAILABLE"
    assert reasons["ENVIRONMENT_CONDITIONS"] == "STALE"
    assert reasons["ROAD_FRICTION_STATE"] == "INVALID"


def test_surrounding_object_projection_is_isolated_to_operation_region() -> None:
    service = _service()
    nodes = _nodes(
        _observation(
            "SURROUNDING_OBJECT_STATE",
            {
                "objects": [
                    {
                        "object_id": "front-pedestrian",
                        "entity_kind": "PEDESTRIAN",
                        "region": "FRONT",
                        "exists": True,
                        "distance": 1.0,
                        "risk_level": "CRITICAL",
                    },
                    {
                        "object_id": "rear-right-bicycle",
                        "entity_kind": "BICYCLE",
                        "region": "REAR_RIGHT",
                        "exists": True,
                        "distance": 3.0,
                        "motion_state": "APPROACHING",
                        "risk_level": "HIGH",
                    },
                ]
            },
        )
    )
    demand = _demand()
    intent = _intent()
    fields = service._project_context_fields(
        nodes,
        semantic_intent=intent,
        demand=demand,
    )
    query = service.build_query_text(
        demand,
        semantic_intent=intent,
        context_fields=fields,
    )
    assert "目标类型=BICYCLE" in query
    assert "目标类型=PEDESTRIAN" not in query


def test_context_projection_uses_current_evidence_demand_as_the_only_filter() -> None:
    service = _service()
    nodes = _nodes(
        _observation("VEHICLE_SPEED", 0),
        _observation("GEAR_STATE", {"current_gear": "P"}),
        _observation("ROAD_FRICTION_STATE", {"road_condition": "WET"}),
        _observation("ENVIRONMENT_CONDITIONS", {"precipitation": "RAIN"}),
        _observation("SYSTEM_MODE", {"vehicle_mode": "SIMULATION"}),
    )

    projection = service._context_projection(
        nodes,
        semantic_intent=_intent(),
        demand=_demand(),
    )

    assert {item["evidence_type"] for item in projection["included"]} == {
        "VEHICLE_SPEED",
        "GEAR_STATE",
    }
    excluded = {
        item["evidence_type"]: item["reason"] for item in projection["excluded"]
    }
    assert excluded == {
        "ROAD_FRICTION_STATE": "NOT_RELEVANT_TO_CURRENT_DEMAND",
        "ENVIRONMENT_CONDITIONS": "NOT_RELEVANT_TO_CURRENT_DEMAND",
        "SYSTEM_MODE": "NOT_RELEVANT_TO_CURRENT_DEMAND",
    }


def test_no_object_in_operation_region_is_explicit_only_when_object_list_exists() -> None:
    service = _service()
    nodes = _nodes(
        _observation(
            "SURROUNDING_OBJECT_STATE",
            {"objects": [], "collision_state": "NONE"},
        )
    )
    demand = _demand()
    intent = _intent()
    fields = service._project_context_fields(
        nodes,
        semantic_intent=intent,
        demand=demand,
    )
    query = service.build_query_text(
        demand,
        semantic_intent=intent,
        context_fields=fields,
    )
    assert "目标区域=REAR_RIGHT" in query
    assert "区域目标=不存在" in query
    assert "目标类型=" not in query
