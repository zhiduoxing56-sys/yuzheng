from __future__ import annotations

from app.core.pipeline import CommandPipeline
from app.models.schemas import AuditDatabaseRole


def _pipeline(tmp_path) -> CommandPipeline:
    return CommandPipeline(
        database_path=tmp_path / "audit.db",
        token_secret=b"knowledge-context-main-chain-secret",
        audit_database_role=AuditDatabaseRole.TEST,
    )


def _demand(pipeline: CommandPipeline, scenario_id: str):
    return pipeline.run_scenario(scenario_id).evidence_demand.intent_demands[0]


def test_demo_context_enters_formal_evidence_repository_before_knowledge_query(
    tmp_path,
) -> None:
    pipeline = _pipeline(tmp_path)

    door = _demand(pipeline, "knowledge_door_right_rear_bicycle_risk")
    assert door.intent_id == "DOOR_OPEN"
    for fragment in (
        "区域=RIGHT_REAR",
        "运动状态=行驶",
        "挡位=D",
        "目标区域=REAR_RIGHT",
        "区域目标=存在",
        "目标类型=BICYCLE",
        "目标距离=3m",
        "目标相对速度=-5m/s",
        "目标运动=APPROACHING",
        "目标风险=HIGH",
    ):
        assert fragment in door.knowledge_query_text
    assert door.knowledge_hits
    assert "DOOR_STATE" in door.knowledge_augmented_types

    brake = _demand(pipeline, "knowledge_brake_wet")
    for fragment in (
        "道路状态=WET",
        "道路湿度=WET",
        "道路附着系数=0.4",
        "道路附着下界=0.3",
        "道路附着最可能值=0.4",
        "道路附着上界=0.5",
    ):
        assert fragment in brake.knowledge_query_text
    assert "道路附着=低" not in brake.knowledge_query_text

    headlight = _demand(pipeline, "knowledge_headlight_night_low_visibility")
    assert "光照=低照度" in headlight.knowledge_query_text
    assert "能见度=低" in headlight.knowledge_query_text

    context_sources = [
        *door.knowledge_retrieval_metadata["context_sources"],
        *brake.knowledge_retrieval_metadata["context_sources"],
        *headlight.knowledge_retrieval_metadata["context_sources"],
    ]
    simulation_types = {
        "VEHICLE_SPEED",
        "GEAR_STATE",
        "ROAD_FRICTION_STATE",
        "ENVIRONMENT_CONDITIONS",
        "SURROUNDING_OBJECT_STATE",
        "SYSTEM_MODE",
    }
    assert all(
        item["source"] == "SIMULATION"
        for item in context_sources
        if item["evidence_type"] in simulation_types
    )
    assert not {
        "CAMERA",
        "RADAR",
        "LIDAR",
        "ULTRASONIC",
    }.intersection(item["source"] for item in context_sources)
    assert all(item["quality_label"] == "VALID" for item in context_sources)
    assert all(item["availability"] > 0 for item in context_sources)
    assert all(item["freshness"] > 0 for item in context_sources)
