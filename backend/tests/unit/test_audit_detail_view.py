from __future__ import annotations

from app.models.schemas import (
    TextCommandRequest,
    VehicleExecutionResult,
    VehicleState,
    VehicleStatePatch,
    WorkflowEventType,
)
from app.services.presentation.assembler import PresentationAssembler


def _fact(snapshot, key: str):
    assert snapshot is not None
    return next(
        item
        for item in [*snapshot.vehicle_state, *snapshot.environment_state]
        if item.key == key
    )


def test_detail_projects_only_human_readable_contract_and_freezes_snapshot(pipeline) -> None:
    pipeline.update_vehicle_state(
        VehicleStatePatch(
            vehicle_speed=62,
            gear_position="D",
            headlight_state="ON",
            ambient_light=8,
        )
    )
    result = pipeline.process_text(TextCommandRequest(text="关闭前照灯"))
    record = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert record is not None

    detail = PresentationAssembler(pipeline).audit_detail(record)
    assert detail.command_summary.raw_command == "关闭前照灯"
    assert _fact(detail.decision_snapshot, "vehicle_speed").value == 62
    assert _fact(detail.decision_snapshot, "ambient_illumination").value == 8
    assert "semantic_frame" not in detail.model_dump()
    assert "record_hash" not in detail.model_dump()
    assert "turn_id" not in detail.model_dump()
    snapshot_events = [
        event
        for event in pipeline.workflow_repository.events(result.root_turn_id or result.turn_id)
        if event.event_type == WorkflowEventType.DECISION_SNAPSHOT_CAPTURED
    ]
    assert len(snapshot_events) == 1
    assert snapshot_events[0].payload["audit_id"] == record.audit_id

    pipeline.update_vehicle_state(VehicleStatePatch(vehicle_speed=3, ambient_light=90))
    historical = PresentationAssembler(pipeline).audit_detail(record)
    assert _fact(historical.decision_snapshot, "vehicle_speed").value == 62
    assert _fact(historical.decision_snapshot, "ambient_illumination").value == 8


def test_execution_snapshots_are_separate_and_changes_only_include_differences(pipeline) -> None:
    result = pipeline.process_text(TextCommandRequest(text="加速"))
    record = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert record is not None
    before = VehicleState(vehicle_speed=21.3, gear_position="D")
    after = before.model_copy(update={"vehicle_speed": 28.6})
    pipeline.workflow_repository.save_execution(
        root_turn_id=record.root_turn_id or record.turn_id,
        turn_id=record.turn_id,
        token_id="TOKEN_AUDIT_TEST",
        result=VehicleExecutionResult(
            adapter="simulator",
            simulated=True,
            status="SUCCESS",
            action="加速",
            target="车辆",
            area="vehicle",
            before_state=before,
            after_state=after,
            feedback="verified",
            duration_ms=3,
        ),
    )

    detail = PresentationAssembler(pipeline).audit_detail(record)
    assert _fact(detail.execution_before_snapshot, "vehicle_speed").value == 21.3
    assert _fact(detail.execution_after_snapshot, "vehicle_speed").value == 28.6
    assert [(item.key, item.delta) for item in detail.execution_changes] == [
        ("vehicle_speed", 7.3)
    ]


class _ExplanationProvider:
    name = "TEST"
    model = "audit-test-model"

    def __init__(self, pipeline) -> None:
        self.pipeline = pipeline
        self.calls = 0

    def generate(self, _system_prompt, payload):
        self.calls += 1
        assert self.pipeline.audit_repository.count() >= 1
        return {
            "llm_explanation": f"结构化事实已给出 {payload['final_decision']} 裁决。"
        }


def test_llm_explanation_runs_once_after_audit_persistence_and_is_append_only(pipeline) -> None:
    provider = _ExplanationProvider(pipeline)
    pipeline.audit_explanation_service.provider = provider
    result = pipeline.process_text(TextCommandRequest(text="打开车窗"))
    assert provider.calls == 1
    events = pipeline.workflow_repository.events(result.root_turn_id or result.turn_id)
    explanation_events = [
        event
        for event in events
        if event.event_type == WorkflowEventType.LLM_EXPLANATION_GENERATED
    ]
    assert len(explanation_events) == 1
    assert explanation_events[0].payload["llm_explanation_status"] == "AVAILABLE"
    stored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert stored is not None
    assert stored.current_hash == result.audit.current_hash


def test_llm_failure_does_not_remove_audit_or_change_decision(pipeline) -> None:
    class FailingProvider:
        name = "FAIL"
        model = "fail-model"

        @staticmethod
        def generate(_system_prompt, _payload):
            raise TimeoutError("timeout")

    pipeline.audit_explanation_service.provider = FailingProvider()
    result = pipeline.process_text(TextCommandRequest(text="打开车窗"))
    stored = pipeline.audit_repository.get_by_turn(result.turn_id)
    assert stored is not None
    assert stored.final_decision.final_decision == result.decision.final_decision
    detail = PresentationAssembler(pipeline).audit_detail(stored)
    assert detail.llm_explanation.status == "FAILED"
    assert detail.llm_explanation.text is None
