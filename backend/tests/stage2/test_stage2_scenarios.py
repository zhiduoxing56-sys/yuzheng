from __future__ import annotations

from app.models.schemas import (
    DecisionLabel,
    EvidenceObservationInput,
    EvidenceRelation,
    EvidenceStatus,
    TextCommandRequest,
    VehicleStatePatch,
)


OPEN_DOOR_REQUIRED = {
    "vehicle_speed",
    "gear_position",
    "door_lock_state",
    "occupant_role",
    "speaker_zone",
    "vehicle_mode",
}


def _request(speed: float | None, gear: str = "P", **kwargs) -> TextCommandRequest:
    return TextCommandRequest(
        text="打开车门",
        speaker_zone="driver",
        speaker_role="driver",
        state_overrides=VehicleStatePatch(vehicle_speed=speed, gear_position=gear),
        **kwargs,
    )


def test_parked_door_command_has_complete_retrieval_quality_and_graph(pipeline) -> None:
    result = pipeline.process_text(_request(0))

    assert result.decision.final_decision == DecisionLabel.PASS
    assert set(result.evidence_demand.required_types) == OPEN_DOOR_REQUIRED
    assert len(result.query_vector) == 768
    assert result.retrieval_metadata.candidate_count == len(result.candidate_evidence)
    assert result.quality_metrics.ecr == 1.0
    assert result.quality_metrics.evidence_coverage_applicable is True
    assert result.evidence_subgraph.nodes
    assert result.evidence_subgraph.edges
    relations = {edge.relation for edge in result.evidence_subgraph.edges}
    assert {
        EvidenceRelation.REQUIRES,
        EvidenceRelation.SUPPORTS,
        EvidenceRelation.RULE_CONSTRAINED,
        EvidenceRelation.PERMISSION_BOUND,
        EvidenceRelation.TEMPORAL,
        EvidenceRelation.DERIVED_FROM,
    } <= relations
    assert result.audit.query_vector_digest == result.evidence_demand.vectorization_metadata.vector_digest


def test_moving_door_command_blocks_and_graph_contains_rule_and_state(pipeline) -> None:
    result = pipeline.process_text(_request(80, "D"))
    graph_types = {node.evidence_type for node in result.evidence_subgraph.nodes}
    relations = {edge.relation for edge in result.evidence_subgraph.edges}

    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert "行驶中禁止打开车门" in result.safety_gate.reasons
    assert {"vehicle_speed", "gear_position", "door_lock_state"} <= graph_types
    assert EvidenceRelation.RULE_CONSTRAINED in relations


def test_semantic_retrieval_omits_speed_then_mandatory_recall_supplements_it(pipeline) -> None:
    status = pipeline.rebuild_index(["vehicle_speed"])
    result = pipeline.process_text(_request(0))
    speed_record = next(
        record for record in result.mandatory_recall_records if record.evidence_type == "vehicle_speed"
    )

    assert "vehicle_speed" in status.excluded_types
    assert not any(node.evidence_type == "vehicle_speed" for node in result.candidate_evidence)
    assert speed_record.status == "RECALLED"
    assert speed_record.recalled_node_id is not None
    assert "vehicle_speed" in result.evidence_subgraph.mandatory_recalled_types
    assert result.quality_metrics.ecr == 1.0
    assert result.decision.final_decision == DecisionLabel.PASS


def test_missing_speed_creates_missing_node_reduces_ecr_and_blocks(pipeline) -> None:
    result = pipeline.process_text(_request(None))
    mandatory_speed = next(
        node for node in result.evidence if node.evidence_type == "vehicle_speed" and node.mandatory
    )
    speed_record = next(
        record for record in result.mandatory_recall_records if record.evidence_type == "vehicle_speed"
    )

    assert mandatory_speed.quality_label == EvidenceStatus.MISSING
    assert speed_record.status == "MISSING"
    assert result.quality_metrics.ecr < 1.0
    assert result.safety_gate.mandatory_evidence_missing is True
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert pipeline.audit_repository.get_by_turn(result.turn_id) is not None
    assert pipeline.audit_repository.verify_chain() is True

    recovered = pipeline.process_text(_request(0))
    assert not any(
        node.source == "mandatory_recall" and node.evidence_type == "vehicle_speed"
        for node in recovered.evidence_subgraph.nodes
    )
    assert recovered.quality_metrics.ecr == 1.0
    assert recovered.decision.final_decision == DecisionLabel.PASS


def test_two_speed_sources_create_conflict_edge_and_non_pass_decision(pipeline) -> None:
    result = pipeline.process_text(
        _request(
            80,
            "D",
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="vehicle_speed", source="wheel_speed_sensor", value=20
                )
            ],
        )
    )
    speed_nodes = [node for node in result.evidence_subgraph.nodes if node.evidence_type == "vehicle_speed"]

    assert len({node.source for node in speed_nodes}) >= 2
    assert any(edge.relation == EvidenceRelation.CONFLICTS for edge in result.evidence_subgraph.edges)
    assert result.quality_metrics.ecs < 1.0
    assert any(item["type"] == "VEHICLE_SPEED_SOURCE_CONFLICT" for item in result.audit.conflict_records)
    assert result.decision.final_decision in {DecisionLabel.REVIEW, DecisionLabel.BLOCK}


def test_stale_speed_attempts_supplement_then_missing_blocks(pipeline) -> None:
    result = pipeline.process_text(
        _request(
            None,
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="vehicle_speed",
                    source="wheel_speed_sensor",
                    value=30,
                    age_seconds=10,
                )
            ],
        )
    )
    speed_nodes = [node for node in result.evidence if node.evidence_type == "vehicle_speed"]
    speed_record = next(
        record for record in result.mandatory_recall_records if record.evidence_type == "vehicle_speed"
    )

    assert any(node.quality_label == EvidenceStatus.STALE for node in speed_nodes)
    assert any(node.quality_label == EvidenceStatus.MISSING and node.mandatory for node in speed_nodes)
    assert speed_record.status == "MISSING"
    assert result.decision.final_decision == DecisionLabel.BLOCK


def test_ambiguous_command_has_null_ecr_review_and_no_executable_token(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="把那个打开"))

    assert result.evidence_demand.required_types == []
    assert result.quality_metrics.ecr is None
    assert result.quality_metrics.evidence_coverage_applicable is False
    assert result.decision.final_decision == DecisionLabel.REVIEW
    assert result.decision.authorization_token is None
    assert result.decision.review_question
