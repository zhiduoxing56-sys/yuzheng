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
        if len(audit.semantic_frame.intents) != 1:
            raise AuthorizationTokenError("执行审计必须恰好包含一个正式子意图")
        intent = audit.semantic_frame.intents[0]
        try:
            payload, metadata = self.pipeline.authorization_service.decode_and_validate(
                raw_token,
                expected_turn_id=turn_id,
                expected_intent=intent,
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
                trusted_context=self.pipeline.trusted_context_from_audit(audit),
            )
            state_changed = current_digest != metadata.state_snapshot_digest
            capability_denied = (
                precheck.runtime_capability is None
                or not precheck.runtime_capability.real_model_inference
                or precheck.runtime_capability.semantic_control_mode
                != SemanticControlMode.FULL
            )
            identity_consistent = False
            identity_reason = "执行前语义未产生唯一 Formal canonical command"
            precheck_capability = None
            if len(precheck.semantic_frame.intents) == 1:
                try:
                    original_identity = (
                        self.pipeline.command_capability_registry.identity_projector.project(
                            intent, require_formal=True
                        )
                    )
                    precheck_intent = precheck.semantic_frame.intents[0]
                    precheck_identity = (
                        self.pipeline.command_capability_registry.identity_projector.project(
                            precheck_intent, require_formal=True
                        )
                    )
                    precheck_capability = self.pipeline.command_capability_registry.resolve(
                        precheck_intent, adapter=self.pipeline.vehicle.adapter_name
                    )
                    identity_consistent = (
                        original_identity == precheck_identity
                        and precheck_capability.contract_id
                        == payload["capability_contract_id"]
                        and precheck_capability.contract_version
                        == payload["capability_contract_version"]
                        and precheck_capability.contract_digest
                        == payload["capability_contract_digest"]
                        and precheck_capability.adapter == payload["capability_adapter"]
                    )
                    if not identity_consistent:
                        identity_reason = (
                            "Token、原审计与 PRE_EXECUTION_CHECK canonical identity "
                            "或 capability contract 不一致"
                        )
                except Exception as exc:
                    identity_reason = f"执行前 canonical identity 校验失败: {exc}"
            safe = (
                precheck.decision.final_decision == DecisionLabel.PASS
                and not precheck.decision.gate_blocked
                and not state_changed
                and not capability_denied
                and identity_consistent
            )
            if not safe:
                reasons = list(precheck.decision.gate_reasons)
                if state_changed:
                    reasons.append("签发后安全相关车辆状态发生变化")
                if capability_denied:
                    reasons.append(
                        "SEMANTIC_MODEL_DEGRADED_EXECUTION_DENIED: 执行前真实语义模型不可用"
                    )
                if not identity_consistent:
                    reasons.append(identity_reason)
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
                        "canonical_identity_consistent": identity_consistent,
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
                        "canonical_identity_consistent": identity_consistent,
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
                if precheck_capability is None:  # pragma: no cover - guarded by safe
                    raise AuthorizationTokenError("缺少已验证的 canonical capability")
                execution = self.pipeline.vehicle.execute(
                    precheck_capability.physical_command
                ).model_copy(
                    update={
                        **precheck_capability.identity.as_dict(),
                        "capability_contract_digest": precheck_capability.contract_digest,
                    }
                )
            except Exception as exc:
                failed_state = self.pipeline.vehicle.get_state()
                physical = (
                    precheck_capability.physical_command
                    if precheck_capability is not None
                    else None
                )
                failed_execution = VehicleExecutionResult(
                    adapter=self.pipeline.vehicle.adapter_name,
                    simulated=self.pipeline.vehicle.adapter_name != "can",
                    status="FAILED",
                    action=physical.action if physical is not None else "canonical",
                    target=physical.target if physical is not None else "canonical",
                    area=str(payload["area"]),
                    intent_id=str(payload["intent_id"]),
                    mode=payload["mode"],
                    value=payload["value"],
                    direction=payload["direction"],
                    control_attribute=str(payload["control_attribute"]),
                    capability_contract_digest=str(
                        payload["capability_contract_digest"]
                    ),
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
