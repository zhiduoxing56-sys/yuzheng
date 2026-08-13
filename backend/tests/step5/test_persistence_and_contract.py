from __future__ import annotations

from app.core.pipeline import CommandPipeline
from app.models.schemas import (
    CausalNodeWeight,
    DecisionLabel,
    ReviewAction,
    ReviewOutcomeRecord,
    ReviewRequest,
    TextCommandRequest,
)
from app.services.presentation.assembler import PresentationAssembler


TEST_SECRET = b"step5-persistence-test-secret-32-bytes"


def _request(*, session_id: str | None = None) -> TextCommandRequest:
    return TextCommandRequest(
        text="可能播放音乐",
        session_id=session_id,
    )


def test_audit_persists_step5_objects_and_get_assembly_has_no_recomputation(
    pipeline, monkeypatch
) -> None:
    result = pipeline.process_text(_request())
    record = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert record is not None
    assert record.memory_propagation is not None
    assert record.causal_correction is not None
    assert record.decision_explanation is not None
    assert record.generation_metadata is not None
    assert record.interpreter_result is not None

    assembler = PresentationAssembler(pipeline)
    expected = assembler.assemble(record).model_dump(mode="json")

    def forbidden(*args, **kwargs):
        del args, kwargs
        raise AssertionError("GET assembly attempted Step5 recomputation")

    monkeypatch.setattr(pipeline.memory_service, "propagate", forbidden)
    monkeypatch.setattr(pipeline.causal_service, "apply", forbidden)
    monkeypatch.setattr(pipeline.interpreter_service, "generate", forbidden)
    first = assembler.assemble(record).model_dump(mode="json")
    second = assembler.assemble(record).model_dump(mode="json")
    detail = assembler.audit_detail(record)
    timeline = pipeline.timeline(record.turn_id)

    assert first == expected == second
    assert detail.command_summary.raw_command == record.semantic_frame.raw_text
    assert detail.decision_summary.final_decision == record.final_decision.final_decision
    assert "memory" not in detail.model_dump()
    assert "causal" not in detail.model_dump()
    assert "decision_explanation" not in detail.model_dump()
    assert {item["stage"] for item in timeline.items} >= {
        "MEMORY_PROPAGATED",
        "CAUSAL_CORRECTED",
        "EXPLANATION_GENERATED",
        "AUDIT_SAVED",
    }
    stage_items = [
        item
        for item in timeline.items
        if item["stage"]
        in {"MEMORY_PROPAGATED", "CAUSAL_CORRECTED", "EXPLANATION_GENERATED"}
    ]
    assert all(item["audit_id"] == record.audit_id for item in stage_items)


def test_node_detail_keeps_all_occurrence_scoped_causal_weights(pipeline) -> None:
    result = pipeline.process_text(_request())
    record = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert record is not None
    assert record.evidence_subgraph is not None
    assert record.causal_correction is not None
    node = pipeline.evidence_repository.all_nodes()[0]
    node_id = node.node_id
    record.evidence_subgraph = record.evidence_subgraph.model_copy(
        update={"nodes": [node]}
    )
    record.causal_correction = record.causal_correction.model_copy(
        update={
            "node_weights": [
                CausalNodeWeight(
                    node_id=node_id,
                    causal_variable="EVI_SPEED_X",
                    clause_index=1,
                    intent_id="WINDOW_OPEN",
                    prior_probability=0.31,
                    causal_support=0.7,
                    corrected_weight=0.41,
                ),
                CausalNodeWeight(
                    node_id=node_id,
                    causal_variable="EVI_SPEED_X",
                    clause_index=0,
                    intent_id="DOOR_OPEN",
                    prior_probability=0.72,
                    causal_support=1.0,
                    corrected_weight=0.83,
                ),
            ]
        }
    )

    detail = PresentationAssembler(pipeline).node_detail(record, node_id)

    assert detail is not None
    assert [(item.clause_index, item.intent_id) for item in detail.causal_occurrence_weights] == [
        (0, "DOOR_OPEN"),
        (1, "WINDOW_OPEN"),
    ]
    assert not {"prior_probability", "causal_support", "corrected_weight"} & set(
        detail.model_dump()
    )


def test_evidence_detail_api_exposes_all_causal_occurrences(api_client, monkeypatch) -> None:
    client, pipeline = api_client
    result = pipeline.process_text(_request())
    record = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert record is not None
    assert record.evidence_subgraph is not None
    assert record.causal_correction is not None
    node = pipeline.evidence_repository.all_nodes()[0]
    node_id = node.node_id
    record.evidence_subgraph = record.evidence_subgraph.model_copy(
        update={"nodes": [node]}
    )
    record.causal_correction = record.causal_correction.model_copy(
        update={
            "node_weights": [
                CausalNodeWeight(
                    node_id=node_id,
                    causal_variable="EVI_SPEED_X",
                    clause_index=1,
                    intent_id="WINDOW_OPEN",
                    prior_probability=0.31,
                    causal_support=0.7,
                    corrected_weight=0.41,
                ),
                CausalNodeWeight(
                    node_id=node_id,
                    causal_variable="EVI_SPEED_X",
                    clause_index=0,
                    intent_id="DOOR_OPEN",
                    prior_probability=0.72,
                    causal_support=1.0,
                    corrected_weight=0.83,
                ),
            ]
        }
    )
    monkeypatch.setattr(
        pipeline.audit_repository,
        "get_by_turn",
        lambda turn_id: record if turn_id == result.turn_id else None,
    )

    response = client.get(f"/api/turns/{result.turn_id}/evidence/{node_id}")

    assert response.status_code == 200
    payload = response.json()
    assert [(item["clause_index"], item["intent_id"]) for item in payload["causal_occurrence_weights"]] == [
        (0, "DOOR_OPEN"),
        (1, "WINDOW_OPEN"),
    ]
    assert not {"prior_probability", "causal_support", "corrected_weight"} & set(payload)


def test_restart_restores_exact_persisted_step5_results(tmp_path) -> None:
    database = tmp_path / "step5-restart.db"
    first = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    response = first.process_text(_request())
    before = first.audit_repository.get_by_turn(response.turn_id)
    assert before is not None
    before_payload = {
        "memory": before.memory_propagation.model_dump(mode="json"),
        "causal": before.causal_correction.model_dump(mode="json"),
        "interpreter": before.interpreter_result.model_dump(mode="json"),
        "record_hash": before.current_hash,
    }

    restarted = CommandPipeline(database, token_secret=TEST_SECRET, audit_database_role="TEST")
    after = restarted.audit_repository.get_by_turn(response.turn_id)
    assert after is not None
    after_payload = {
        "memory": after.memory_propagation.model_dump(mode="json"),
        "causal": after.causal_correction.model_dump(mode="json"),
        "interpreter": after.interpreter_result.model_dump(mode="json"),
        "record_hash": after.current_hash,
    }
    assert after_payload == before_payload
    presentation = PresentationAssembler(restarted).assemble(after)
    assert presentation.evidence.memory.layered_graph == after.memory_propagation.layered_memory_graph
    assert presentation.evidence.causal.confidence_status == after.causal_correction.confidence_status
    assert presentation.decision_result.decision_explanation == after.decision_explanation
    verification = restarted.effective_audit_resolver.verify(
        after.audit_id, restarted.workflow_repository
    )
    assert verification is not None
    assert verification["record_hash_valid"] is True
    assert verification["previous_link_valid"] is True
    assert verification["workflow_chain_valid"] is True


def test_websocket_stage_payloads_are_bounded_summaries(pipeline, monkeypatch) -> None:
    events = []
    monkeypatch.setattr(pipeline.event_broker, "publish", events.append)
    result = pipeline.process_text(_request(session_id="SESSION_STEP5"))
    by_stage = {event.stage: event for event in events}
    assert {
        "MEMORY_PROPAGATED",
        "CAUSAL_CORRECTED",
        "EXPLANATION_GENERATED",
    } <= set(by_stage)

    memory = by_stage["MEMORY_PROPAGATED"].payload
    assert set(memory) == {
        "layer_counts",
        "relation_edge_counts",
        "average_degree",
        "propagation_count",
    }
    causal = by_stage["CAUSAL_CORRECTED"].payload
    assert set(causal) == {
        "model_build_id",
        "history_count",
        "causal_edge_count",
        "confidence_status",
        "decision_confidence",
        "top_corrected_nodes",
    }
    assert len(causal["top_corrected_nodes"]) <= 5
    explanation = by_stage["EXPLANATION_GENERATED"].payload
    assert set(explanation) == {
        "generation_mode",
        "candidate_count",
        "validation_status",
    }
    serialized = str([event.model_dump(mode="json") for event in events]).lower()
    assert "query_vector" not in serialized
    assert "authorization_token" not in serialized
    assert "api_key" not in serialized
    assert result.audit.current_hash


def test_review_outcome_schema_cannot_duplicate_large_step5_or_evidence_objects() -> None:
    fields = set(ReviewOutcomeRecord.model_fields)
    assert fields == {
        "audit_id",
        "record_type",
        "original_audit_id",
        "original_turn_id",
        "root_turn_id",
        "review_action",
        "original_final_decision",
        "effective_final_decision",
        "effective_decision_sources",
        "decision_merge_reason",
        "token_issued",
        "execution_allowed",
        "idempotency_key",
        "previous_hash",
        "current_hash",
        "created_at",
    }
    assert not fields & {
        "transcription_result",
        "semantic_frame",
        "evidence_subgraph",
        "memory_propagation",
        "causal_correction",
        "interpreter_result",
    }


def test_cancel_aggregates_effective_explanation_without_mutating_original_audit(
    pipeline,
) -> None:
    result = pipeline.process_text(TextCommandRequest(text="把那个打开"))
    original = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert original is not None
    before = original.model_dump(mode="json")
    assert original.decision_explanation.decision_label == DecisionLabel.REVIEW

    cancelled = pipeline.review_service.review(
        result.turn_id, ReviewRequest(action=ReviewAction.CANCEL)
    )
    assert cancelled.decision.final_decision == DecisionLabel.BLOCK
    unchanged = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert unchanged is not None
    assert unchanged.model_dump(mode="json") == before

    assembler = PresentationAssembler(pipeline)
    presentation = assembler.assemble(unchanged)
    detail = assembler.audit_detail(unchanged)
    effective = presentation.decision_result.decision_explanation
    assert effective is not None
    assert effective.decision_label == DecisionLabel.BLOCK
    assert effective.validation_status == "EFFECTIVE_OUTCOME_AGGREGATED"
    assert detail.decision_summary.final_decision == DecisionLabel.BLOCK
    assert unchanged.decision_explanation.decision_label == DecisionLabel.REVIEW
