from __future__ import annotations

from typing import TYPE_CHECKING

from app.models.schemas import (
    AuthorizationTokenStatus,
    DecisionLabel,
    ExecuteResult,
    PipelineEvent,
    SemanticControlMode,
    TextCommandRequest,
    VehicleExecutionResult,
    WorkflowEventType,
)
from app.services.authorization.service import (
    AuthorizationTokenError,
    state_snapshot_digest,
)
from app.core.redaction import SensitiveDataRedactor

if TYPE_CHECKING:
    from app.core.pipeline import CommandPipeline


class ExecutionService:
    def __init__(self, pipeline: "CommandPipeline") -> None:
        self.pipeline = pipeline

    def execute(
        self, turn_id: str, raw_token: str, *, session_id: str | None = None
    ) -> ExecuteResult:
        audit = self.pipeline.audit_repository.get_by_turn(turn_id)
        if audit is None:
            raise ValueError(f"未找到轮次: {turn_id}")
        try:
            payload, metadata = self.pipeline.authorization_service.decode_and_validate(
                raw_token,
                expected_turn_id=turn_id,
                expected_action=audit.semantic_frame.action,
                expected_target=audit.semantic_frame.target,
            )
        except AuthorizationTokenError as exc:
            rejected_metadata = (
                self.pipeline.authorization_service.metadata_from_untrusted_token(raw_token)
            )
            if rejected_metadata is not None:
                self.pipeline.workflow_repository.append_event(
                    root_turn_id=rejected_metadata.root_turn_id,
                    related_turn_id=turn_id,
                    event_type=WorkflowEventType.TOKEN_REJECTED,
                    payload={
                        "token_id": rejected_metadata.token_id,
                        "token_digest": rejected_metadata.token_digest,
                        "reason": str(exc),
                    },
                )
            raise
        root = metadata.root_turn_id
        self.pipeline.workflow_repository.append_event(
            root_turn_id=root,
            related_turn_id=turn_id,
            event_type=WorkflowEventType.EXECUTION_REQUESTED,
            payload={"token_id": metadata.token_id, "token_digest": metadata.token_digest},
        )
        with self.pipeline._command_lock:
            event_sequence = 0

            def event_sink(event: PipelineEvent) -> None:
                nonlocal event_sequence
                event_sequence = event.sequence
                self.pipeline.event_broker.publish(event)

            def emit_execution(stage: str, summary: str, payload: dict) -> None:
                nonlocal event_sequence
                if session_id is None:
                    return
                event_sequence += 1
                self.pipeline.event_broker.publish(
                    PipelineEvent(
                        session_id=session_id,
                        turn_id=precheck.turn_id,
                        sequence=event_sequence,
                        stage=stage,
                        summary=summary,
                        payload=payload,
                    )
                )

            latest_state = self.pipeline.vehicle.get_state()
            current_digest = state_snapshot_digest(latest_state)
            precheck = self.pipeline.process_text(
                TextCommandRequest(
                    text=audit.semantic_frame.raw_text,
                    speaker_zone=audit.input_trust_result.speaker_zone,
                    speaker_role=audit.input_trust_result.speaker_role,
                    session_id=session_id,
                ),
                root_turn_id=root,
                parent_turn_id=turn_id,
                attempt_no=audit.attempt_no + 1,
                workflow_type="PRE_EXECUTION_CHECK",
                suppress_authorization=True,
                event_sink=event_sink,
            )
            state_changed = current_digest != metadata.state_snapshot_digest
            capability_denied = (
                precheck.runtime_capability is None
                or not precheck.runtime_capability.real_model_inference
                or precheck.runtime_capability.semantic_control_mode
                != SemanticControlMode.FULL
            )
            safe = (
                precheck.decision.final_decision == DecisionLabel.PASS
                and not precheck.decision.gate_blocked
                and not state_changed
                and not capability_denied
            )
            if not safe:
                reasons = list(precheck.decision.gate_reasons)
                if state_changed:
                    reasons.append("签发后安全相关车辆状态发生变化")
                if capability_denied:
                    reasons.append(
                        "SEMANTIC_MODEL_DEGRADED_EXECUTION_DENIED: 执行前真实语义模型不可用"
                    )
                reason = "；".join(reasons) or "执行前完整复查未通过"
                self.pipeline.authorization_service.reject(metadata, reason)
                self.pipeline.workflow_repository.append_event(
                    root_turn_id=root,
                    related_turn_id=precheck.turn_id,
                    parent_turn_id=turn_id,
                    event_type=WorkflowEventType.PRE_EXECUTION_CHECK_FAILED,
                    payload={
                        "token_id": metadata.token_id,
                        "precheck_turn_id": precheck.turn_id,
                        "final_decision": precheck.decision.final_decision.value,
                        "hit_rules": precheck.safety_gate.hit_rules,
                        "state_changed": state_changed,
                        "semantic_execution_denied": capability_denied,
                        "reason": reason,
                    },
                )
                emit_execution(
                    "VEHICLE_PRECHECKED",
                    "车辆执行前复查失败",
                    {
                        "status": "FAILED",
                        "passed": False,
                        "hit_rules": precheck.safety_gate.hit_rules,
                        "state_changed": state_changed,
                        "semantic_execution_denied": capability_denied,
                    },
                )
                emit_execution(
                    "AUDIT_SAVED",
                    "执行前复查失败结果已持久化",
                    {"audit_id": precheck.audit.audit_id, "status": "FAILED"},
                )
                return ExecuteResult(
                    root_turn_id=root,
                    turn_id=turn_id,
                    accepted=False,
                    token_status=AuthorizationTokenStatus.REJECTED,
                    reason=reason,
                    precheck_turn_id=precheck.turn_id,
                    precheck_decision=precheck.decision.final_decision,
                )
            self.pipeline.workflow_repository.append_event(
                root_turn_id=root,
                related_turn_id=precheck.turn_id,
                parent_turn_id=turn_id,
                event_type=WorkflowEventType.PRE_EXECUTION_CHECK_PASSED,
                payload={
                    "token_id": metadata.token_id,
                    "precheck_turn_id": precheck.turn_id,
                    "state_snapshot_digest": current_digest,
                },
            )
            emit_execution(
                "VEHICLE_PRECHECKED",
                "车辆执行前复查通过",
                {
                    "status": "PASSED",
                    "passed": True,
                    "precheck_turn_id": precheck.turn_id,
                },
            )
            if not self.pipeline.authorization_service.consume(metadata):
                raise AuthorizationTokenError("授权令牌已被其他请求原子消费")
            self.pipeline.workflow_repository.append_event(
                root_turn_id=root,
                related_turn_id=turn_id,
                event_type=WorkflowEventType.TOKEN_CONSUMED,
                payload={"token_id": metadata.token_id, "token_digest": metadata.token_digest},
            )
            emit_execution(
                "TOKEN_CONSUMED",
                "一次性授权令牌已原子消费",
                {"token_id": metadata.token_id, "token_digest": metadata.token_digest},
            )
            try:
                execution = self.pipeline.vehicle.execute(
                    str(payload["action"]), str(payload["target"]), str(payload["area"])
                )
            except Exception as exc:
                failed_state = self.pipeline.vehicle.get_state()
                failed_execution = VehicleExecutionResult(
                    adapter=self.pipeline.vehicle.adapter_name,
                    simulated=self.pipeline.vehicle.adapter_name != "can",
                    status="FAILED",
                    action=str(payload["action"]),
                    target=str(payload["target"]),
                    area=str(payload["area"]),
                    before_state=failed_state,
                    after_state=failed_state,
                    feedback=SensitiveDataRedactor.redact_exception(exc),
                    duration_ms=0,
                )
                self.pipeline.workflow_repository.save_execution(
                    root_turn_id=root,
                    turn_id=turn_id,
                    token_id=metadata.token_id,
                    result=failed_execution,
                )
                self.pipeline.workflow_repository.append_event(
                    root_turn_id=root,
                    related_turn_id=turn_id,
                    event_type=WorkflowEventType.EXECUTION_FAILED,
                    payload={
                        "token_id": metadata.token_id,
                        "error_type": type(exc).__name__,
                        "reason": SensitiveDataRedactor.redact_exception(exc),
                    },
                )
                emit_execution(
                    "EXECUTION_FAILED",
                    "车辆适配器执行失败",
                    {"status": "FAILED", "error_type": type(exc).__name__},
                )
                emit_execution(
                    "AUDIT_SAVED",
                    "车辆执行失败结果已持久化",
                    {"audit_id": precheck.audit.audit_id, "status": "FAILED"},
                )
                return ExecuteResult(
                    root_turn_id=root,
                    turn_id=turn_id,
                    accepted=False,
                    token_status=AuthorizationTokenStatus.CONSUMED,
                    reason=(
                        "令牌已消费，但车辆适配器执行失败: "
                        f"{SensitiveDataRedactor.redact_exception(exc)}"
                    ),
                    precheck_turn_id=precheck.turn_id,
                    precheck_decision=precheck.decision.final_decision,
                    execution=failed_execution,
                )
            self.pipeline.workflow_repository.save_execution(
                root_turn_id=root,
                turn_id=turn_id,
                token_id=metadata.token_id,
                result=execution,
            )
            self.pipeline.workflow_repository.append_event(
                root_turn_id=root,
                related_turn_id=turn_id,
                event_type=WorkflowEventType.EXECUTION_SUCCEEDED,
                payload={
                    "token_id": metadata.token_id,
                    "execution_id": execution.execution_id,
                    "adapter": execution.adapter,
                    "status": execution.status,
                    "after_state": execution.after_state.model_dump(mode="json"),
                },
            )
            emit_execution(
                "VEHICLE_EXECUTED",
                "车辆模拟执行成功",
                {"status": execution.status, "execution_id": execution.execution_id},
            )
            emit_execution(
                "AUDIT_SAVED",
                "车辆执行成功结果已持久化",
                {"audit_id": precheck.audit.audit_id, "status": execution.status},
            )
            return ExecuteResult(
                root_turn_id=root,
                turn_id=turn_id,
                accepted=True,
                token_status=AuthorizationTokenStatus.CONSUMED,
                reason=execution.feedback,
                precheck_turn_id=precheck.turn_id,
                precheck_decision=precheck.decision.final_decision,
                execution=execution,
            )
