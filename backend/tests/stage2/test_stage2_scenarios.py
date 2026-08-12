from __future__ import annotations

from app.models.schemas import (
    DecisionLabel,
    EvidenceObservationInput,
    EvidenceRelation,
    EvidenceStatus,
    TextCommandRequest,
    TrustedRuntimeContext,
    VehicleStatePatch,
)


OPEN_DOOR_REQUIRED = {
    "VEHICLE_SPEED",
    "GEAR_STATE",
    "SURROUNDING_OBJECT_STATE",
}


def _process(pipeline, speed: float | None, gear: str = "P", **kwargs):
    observations = kwargs.pop("evidence_overrides", [])
    return pipeline.process_text(
        TextCommandRequest(text="打开车门", speaker_zone="driver", speaker_role="driver"),
        trusted_context=TrustedRuntimeContext(
            state_overrides=VehicleStatePatch(vehicle_speed=speed, gear_position=gear),
            evidence_overrides=observations,
            subject_role="driver", subject_zone="driver",
            subject_source="stage2_test", zone_source="stage2_test",
        ),
    )


def _recall_records(result):
    return [
        record
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for record in resolution.mandatory_recall_records
    ]


def _required_node_ids(result) -> set[str]:
    return {
        binding.node_id
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for binding in resolution.bindings
        if binding.requirement_level == "REQUIRED" and binding.node_id is not None
    }


def test_parked_door_command_has_complete_retrieval_quality_and_graph(pipeline) -> None:
    result = _process(pipeline, 0)

    assert result.decision.final_decision == DecisionLabel.PASS
    intent_demand = result.evidence_demand.intent_demands[0]
    assert set(intent_demand.required_types) == OPEN_DOOR_REQUIRED
    assert len(result.query_vectors[0]) == 768
    assert intent_demand.vectorization_metadata.model_name == "BAAI/bge-base-zh-v1.5"
    assert intent_demand.vectorization_metadata.real_model_inference is True
    assert intent_demand.vectorization_metadata.degradation_reason is None
    assert result.retrieval_metadata.implementation == "hnswlib"
    assert result.retrieval_metadata.degraded is False
    assert result.retrieval_metadata.candidate_count == len(result.candidate_evidence)
    assert result.quality_metrics.ecr == 1.0
    assert result.quality_metrics.evidence_coverage_applicable is True
    assert result.evidence_subgraph.nodes
    assert all(node.evidence_type.isupper() for node in result.evidence_subgraph.nodes)
    assert not {"evidence_demand", "control_target", "evidence_stream"} & {
        node.evidence_type for node in result.evidence_subgraph.nodes
    }
    assert result.audit.query_vector_digests == [intent_demand.vectorization_metadata.vector_digest]


def test_moving_door_command_blocks_and_graph_contains_rule_and_state(pipeline) -> None:
    result = _process(pipeline, 80, "D")
    graph_types = {node.evidence_type for node in result.evidence_subgraph.nodes}
    relations = {edge.relation for edge in result.evidence_subgraph.edges}

    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert "行驶中禁止打开车门" in result.safety_gate.reasons
    assert {"VEHICLE_SPEED", "GEAR_STATE", "DOOR_LOCK_STATE"} <= graph_types
    assert EvidenceRelation.RULE_CONSTRAINED not in relations


def test_semantic_retrieval_omits_speed_then_mandatory_recall_supplements_it(pipeline) -> None:
    status = pipeline.rebuild_index(["VEHICLE_SPEED"])
    result = _process(pipeline, 0)
    speed_record = next(
        record for record in _recall_records(result) if record.evidence_type == "VEHICLE_SPEED"
    )

    assert "VEHICLE_SPEED" in status.excluded_types
    assert not any(node.evidence_type == "VEHICLE_SPEED" for node in result.candidate_evidence)
    assert speed_record.status == "RECALLED"
    assert speed_record.recalled_node_id is not None
    assert any(
        binding.evidence_type == "VEHICLE_SPEED"
        and binding.resolution_status == "MANDATORY_RECALLED"
        for resolution in result.evidence_subgraph.intent_evidence_resolutions
        for binding in resolution.bindings
    )
    assert result.quality_metrics.ecr == 1.0
    assert result.decision.final_decision == DecisionLabel.PASS


def test_missing_speed_creates_missing_node_reduces_ecr_and_blocks(pipeline) -> None:
    result = _process(pipeline, None)
    required_node_ids = _required_node_ids(result)
    mandatory_speed = next(
        node
        for node in result.evidence
        if node.evidence_type == "VEHICLE_SPEED" and node.node_id in required_node_ids
    )
    speed_record = next(
        record for record in _recall_records(result) if record.evidence_type == "VEHICLE_SPEED"
    )

    assert mandatory_speed.quality_label == EvidenceStatus.MISSING
    assert speed_record.status == "MISSING"
    assert result.quality_metrics.ecr < 1.0
    assert result.safety_gate.mandatory_evidence_missing is True
    assert result.decision.final_decision == DecisionLabel.BLOCK
    assert pipeline.audit_repository.get_by_turn(result.turn_id) is not None
    assert pipeline.audit_repository.verify_chain() is True

    recovered = _process(pipeline, 0)
    assert not any(
        node.source == "mandatory_recall" and node.evidence_type == "VEHICLE_SPEED"
        for node in recovered.evidence_subgraph.nodes
    )
    assert recovered.quality_metrics.ecr == 1.0
    assert recovered.decision.final_decision == DecisionLabel.PASS


def test_two_speed_sources_create_conflict_edge_and_non_pass_decision(pipeline) -> None:
    result = _process(
        pipeline,
            80,
            "D",
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="VEHICLE_SPEED", source="wheel_speed_sensor", value=20
                )
            ],
    )
    speed_nodes = [node for node in result.evidence_subgraph.nodes if node.evidence_type == "VEHICLE_SPEED"]

    assert len({node.source for node in speed_nodes}) >= 2
    assert any(edge.relation == EvidenceRelation.CONFLICTS for edge in result.evidence_subgraph.edges)
    assert result.quality_metrics.ecs < 1.0
    assert any(item["type"] == "VEHICLE_SPEED_SOURCE_CONFLICT" for item in result.audit.conflict_records)
    assert result.decision.final_decision in {DecisionLabel.REVIEW, DecisionLabel.BLOCK}


def test_current_missing_state_is_not_masked_by_stale_observation(pipeline) -> None:
    result = _process(
        pipeline,
            None,
            evidence_overrides=[
                EvidenceObservationInput(
                    evidence_type="VEHICLE_SPEED",
                    source="wheel_speed_sensor",
                    value=30,
                    age_seconds=10,
                )
            ],
    )
    speed_nodes = [node for node in result.evidence if node.evidence_type == "VEHICLE_SPEED"]
    speed_record = next(
        record for record in _recall_records(result) if record.evidence_type == "VEHICLE_SPEED"
    )

    assert any(node.quality_label == EvidenceStatus.STALE for node in speed_nodes)
    assert any(
        node.quality_label == EvidenceStatus.MISSING
        and node.node_id in _required_node_ids(result)
        for node in speed_nodes
    )
    assert speed_record.status == "MISSING"
    assert result.decision.final_decision == DecisionLabel.BLOCK


def test_ambiguous_command_has_null_ecr_review_and_no_executable_token(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="把那个打开"))

    assert result.evidence_demand.intent_demands == []
    assert result.quality_metrics.ecr is None
    assert result.quality_metrics.evidence_coverage_applicable is False
    assert result.decision.final_decision == DecisionLabel.REVIEW
    assert result.decision.authorization_token is None
    assert result.decision.review_question
