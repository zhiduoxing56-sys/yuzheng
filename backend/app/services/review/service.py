from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from app.models.schemas import (
    AuthorizationTokenStatus,
    DecisionLabel,
    DecisionSource,
    ReviewAction,
    ReviewRequest,
    ReviewResult,
    ReviewOutcomeRecord,
    TextCommandRequest,
    TurnWorkflowStatus,
    PipelineEvent,
    WorkflowEventType,
    utc_now,
)
from app.core.redaction import SensitiveDataRedactor
from app.services.decision.merge import merge_decision

if TYPE_CHECKING:
    from app.core.pipeline import CommandPipeline


REVIEW_ACTION_EVENTS = {
    WorkflowEventType.REVIEW_CONFIRM_REJECTED,
    WorkflowEventType.REVIEW_CONFIRMED,
    WorkflowEventType.REVIEW_CORRECTED,
    WorkflowEventType.REVIEW_CANCELLED,
}
TERMINAL_EVENTS = {
    WorkflowEventType.REVIEW_CANCELLED,
    WorkflowEventType.EXECUTION_SUCCEEDED,
    WorkflowEventType.EXECUTION_FAILED,
}


class ReviewWorkflowError(ValueError):
    pass


class ReviewService:
    def __init__(self, pipeline: "CommandPipeline", config: dict[str, Any]) -> None:
        self.pipeline = pipeline
        self.config = config

    @property
    def max_attempts(self) -> int:
        return int(self.config.get("max_review_attempts", 3))

    def root_for_turn(self, turn_id: str) -> str:
        root_turn_id = self.pipeline.audit_repository.root_turn_id_for_turn(turn_id)
        if root_turn_id is None:
            raise ReviewWorkflowError(f"未找到轮次: {turn_id}")
        return root_turn_id

    def _root_audits(self, root_turn_id: str):
        audits = self.pipeline.audit_repository.records_for_root(root_turn_id)
        if not audits:
            root = self.pipeline.audit_repository.get_by_turn(root_turn_id)
            if root is not None:
                audits = [root]
        return sorted(audits, key=lambda record: (record.created_at, record.turn_id))

    def status(self, turn_id: str) -> TurnWorkflowStatus:
        root_turn_id = self.root_for_turn(turn_id)
        latest = self.pipeline.audit_repository.latest_turn_summary_for_root(root_turn_id)
        if latest is None:
            raise ReviewWorkflowError(f"未找到轮次: {turn_id}")
        latest_turn_id, latest_decision_value = latest
        latest_decision = DecisionLabel(latest_decision_value)
        events = self.pipeline.workflow_repository.events(root_turn_id)
        attempts = sum(event.event_type in REVIEW_ACTION_EVENTS for event in events)
        terminal_event = next(
            (event for event in reversed(events) if event.event_type in TERMINAL_EVENTS), None
        )
        clarification_cancelled = next(
            (
                event
                for event in reversed(events)
                if event.event_type == WorkflowEventType.CLARIFICATION_RESOLVED
                and event.payload.get("resolution") == "NONE_OF_ABOVE"
            ),
            None,
        )
        token = self.pipeline.workflow_repository.latest_token_for_root(root_turn_id)
        if terminal_event is not None:
            status = {
                WorkflowEventType.REVIEW_CANCELLED: "CANCELLED",
                WorkflowEventType.EXECUTION_SUCCEEDED: "EXECUTED",
                WorkflowEventType.EXECUTION_FAILED: "TERMINATED",
            }[terminal_event.event_type]
            latest_decision = (
                DecisionLabel.BLOCK
                if terminal_event.event_type == WorkflowEventType.REVIEW_CANCELLED
                else latest_decision
            )
        elif clarification_cancelled is not None:
            status = "CANCELLED"
        elif latest_decision == DecisionLabel.REVIEW:
            status = "REVIEW_REQUIRED"
        elif token is not None and token.status == AuthorizationTokenStatus.ISSUED:
            status = "AUTHORIZED"
        else:
            status = latest_decision.value
        return TurnWorkflowStatus(
            root_turn_id=root_turn_id,
            current_turn_id=latest_turn_id,
            status=status,
            review_attempts=attempts,
            max_review_attempts=self.max_attempts,
            latest_decision=latest_decision,
            token_status=token.status if token else None,
            event_count=len(events),
            terminal=terminal_event is not None or clarification_cancelled is not None,
        )

    def _validate_entry(self, turn_id: str):
        status = self.status(turn_id)
        audits = self._root_audits(status.root_turn_id)
        latest = audits[-1]
        if status.terminal:
            raise ReviewWorkflowError(f"工作流已终止: {status.status}")
        if latest.final_decision.final_decision != DecisionLabel.REVIEW:
            raise ReviewWorkflowError(
                f"只有 REVIEW 轮次允许复核，当前为 {latest.final_decision.final_decision.value}"
            )
        if status.review_attempts >= self.max_attempts:
            raise ReviewWorkflowError("已达到最大复核次数")
        ttl = timedelta(seconds=int(self.config.get("review_ttl_seconds", 300)))
        if utc_now() >= latest.created_at + ttl:
            raise ReviewWorkflowError("复核请求已过期")
        return status, latest

    def _reject_confirm(
        self,
        *,
        root_turn_id: str,
        latest,
        next_attempt: int,
        reason: str,
        rejection_code: str,
        rejection_status_code: int,
    ) -> ReviewResult:
        idempotency_key = (
            f"{latest.audit_id}:CONFIRM_REJECTED:{rejection_code}"
        )
        already_recorded = any(
            event.event_type == WorkflowEventType.REVIEW_CONFIRM_REJECTED
            and event.payload.get("idempotency_key") == idempotency_key
            for event in self.pipeline.workflow_repository.events(root_turn_id)
        )
        if not already_recorded:
            self.pipeline.workflow_repository.append_event(
                root_turn_id=root_turn_id,
                related_turn_id=latest.turn_id,
                event_type=WorkflowEventType.REVIEW_CONFIRM_REJECTED,
                payload={
                    "reason": reason,
                    "attempt_no": next_attempt,
                    "rejection_code": rejection_code,
                    "idempotency_key": idempotency_key,
                },
            )
        return ReviewResult(
            root_turn_id=root_turn_id,
            related_turn_id=latest.turn_id,
            action=ReviewAction.CONFIRM,
            accepted=False,
            reason=reason,
            workflow_status=self.status(root_turn_id),
            decision=latest.final_decision,
            review_question=latest.interpreter_review_question,
            rejection_code=rejection_code,
            rejection_status_code=rejection_status_code,
        )

    def review(self, turn_id: str, request: ReviewRequest) -> ReviewResult:
        request = ReviewRequest.model_validate(
            SensitiveDataRedactor.redact(request.model_dump(mode="json"))
        )
        if request.action == ReviewAction.CANCEL:
            requested_record = self.pipeline.audit_repository.get_by_turn(turn_id)
            if requested_record is None:
                raise ReviewWorkflowError(f"未找到轮次: {turn_id}")
            existing = self.pipeline.audit_repository.outcome_for_original(
                requested_record.audit_id
            )
            if existing is not None:
                raise ReviewWorkflowError(
                    "工作流已终止: CANCELLED; "
                    f"terminal_audit_id={existing.audit_id}"
                )

        status, latest = self._validate_entry(turn_id)
        root = status.root_turn_id
        next_attempt = status.review_attempts + 1
        if request.action == ReviewAction.CANCEL:
            alignment_route = self.pipeline.effective_audit_resolver._alignment_route(
                latest
            )
            merged = merge_decision(
                latest.safety_gate_result,
                alignment_route,
                latest.final_decision.score_decision,
                block_constraints=[DecisionSource.USER_REVIEW],
                constraint_reasons={
                    DecisionSource.USER_REVIEW: "用户取消本轮指令"
                },
            )
            outcome = ReviewOutcomeRecord(
                original_audit_id=latest.audit_id,
                original_turn_id=latest.turn_id,
                root_turn_id=root,
                original_final_decision=latest.final_decision.final_decision,
                effective_final_decision=merged.final_decision,
                effective_decision_sources=list(merged.decision_sources),
                decision_merge_reason=merged.decision_merge_reason,
                idempotency_key=f"{latest.audit_id}:{ReviewAction.CANCEL.value}",
            )
            event_payload = {
                "original_audit_id": latest.audit_id,
                "original_turn_id": latest.turn_id,
                "original_final_decision": latest.final_decision.final_decision.value,
                "effective_final_decision": merged.final_decision.value,
                "decision_source": DecisionSource.USER_REVIEW.value,
                "terminal_audit_id": outcome.audit_id,
                "token_issued": False,
                "execution_allowed": False,
                "reason": request.cancel_reason or "用户取消本轮指令",
            }
            saved_outcome, _, created = (
                self.pipeline.audit_repository.append_review_outcome_with_events(
                    outcome,
                    [
                        (WorkflowEventType.REVIEW_CANCELLED, event_payload),
                        (WorkflowEventType.FINAL_DECISION_UPDATED, event_payload),
                        (WorkflowEventType.AUDIT_OUTCOME_APPENDED, event_payload),
                    ],
                )
            )
            if not created:
                raise ReviewWorkflowError(
                    "工作流已终止: CANCELLED; "
                    f"terminal_audit_id={saved_outcome.audit_id}"
                )
            resolved = self.pipeline.effective_audit_resolver.resolve(latest)
            updated = self.status(root)
            session_id = latest.audio_input_metadata.get("session_id")
            if session_id:
                self.pipeline.event_broker.publish(
                    PipelineEvent(
                        session_id=str(session_id),
                        turn_id=latest.turn_id,
                        sequence=updated.event_count,
                        event_type=WorkflowEventType.REVIEW_CANCELLED.value,
                        stage=WorkflowEventType.REVIEW_CANCELLED.value,
                        status="COMPLETED",
                        duration_ms=0,
                        summary="用户取消复核，终态审计已追加",
                        payload=event_payload,
                    )
                )
            return ReviewResult(
                root_turn_id=root,
                related_turn_id=latest.turn_id,
                action=request.action,
                accepted=True,
                reason="复核已取消，未签发令牌且未执行车辆动作",
                workflow_status=updated,
                decision=resolved.effective_decision,
                review_question=None,
                terminal_audit_id=saved_outcome.audit_id,
            )

        frame = latest.semantic_frame
        selected_candidate = None
        if request.action == ReviewAction.CONFIRM:
            if len(frame.intents) > 1:
                return self._reject_confirm(
                    root_turn_id=root,
                    latest=latest,
                    next_attempt=next_attempt,
                    reason=(
                        "原轮次检测到多个独立车控意图，CONFIRM 不能自动选择其中一个动作；"
                        "请使用 CORRECT 提供新的单一指令或使用 CANCEL 终止"
                    ),
                    rejection_code="NO_PERSISTED_REVIEW_CANDIDATES",
                    rejection_status_code=409,
                )
            persisted_candidates = list(latest.candidate_interpretations)
            if not persisted_candidates:
                return self._reject_confirm(
                    root_turn_id=root,
                    latest=latest,
                    next_attempt=next_attempt,
                    reason=(
                        "原轮次没有持久化的合法复核候选；"
                        "请使用CORRECT提供修正文案或使用CANCEL终止"
                    ),
                    rejection_code="NO_PERSISTED_REVIEW_CANDIDATES",
                    rejection_status_code=409,
                )
            if not (request.selected_candidate_id or "").strip():
                return self._reject_confirm(
                    root_turn_id=root,
                    latest=latest,
                    next_attempt=next_attempt,
                    reason="CONFIRM必须提供selected_candidate_id",
                    rejection_code="SELECTED_CANDIDATE_REQUIRED",
                    rejection_status_code=422,
                )
            persisted_candidate = next(
                (
                    candidate
                    for candidate in persisted_candidates
                    if candidate.candidate_id == request.selected_candidate_id
                ),
                None,
            )
            if persisted_candidate is None or persisted_candidate.turn_id != latest.turn_id:
                return self._reject_confirm(
                    root_turn_id=root,
                    latest=latest,
                    next_attempt=next_attempt,
                    reason="selected_candidate_id不存在或不属于当前轮次",
                    rejection_code="REVIEW_CANDIDATE_NOT_FOUND",
                    rejection_status_code=404,
                )
            if (
                persisted_candidate.validation_status != "VALID"
                or not persisted_candidate.canonical_text.strip()
            ):
                return self._reject_confirm(
                    root_turn_id=root,
                    latest=latest,
                    next_attempt=next_attempt,
                    reason="selected_candidate_id对应候选未通过本地校验",
                    rejection_code="REVIEW_CANDIDATE_NOT_VALID",
                    rejection_status_code=409,
                )
            selected_candidate = persisted_candidate
        has_unresolved_conflict = bool(
            latest.jailbreak_conflicts
            or latest.conflict_records
            or any(node.quality_label.value == "SUSPICIOUS" for node in (latest.evidence_subgraph.nodes if latest.evidence_subgraph else []))
        )
        if request.action == ReviewAction.CONFIRM and (
            (
                selected_candidate is None
                and (frame.semantic_status != "OK" or not frame.intents)
            )
            or has_unresolved_conflict
        ):
            reason = (
                "语义动作或目标仍不完整，CONFIRM 不能补全含义，请使用 CORRECT"
                if selected_candidate is None
                and (frame.semantic_status != "OK" or not frame.intents)
                else "证据或权限冲突仍存在，CONFIRM 不能删除冲突"
            )
            return self._reject_confirm(
                root_turn_id=root,
                latest=latest,
                next_attempt=next_attempt,
                reason=reason,
                rejection_code="REVIEW_NOT_ALLOWED",
                rejection_status_code=409,
            )

        new_text = (
            request.corrected_text.strip()
            if request.action == ReviewAction.CORRECT and request.corrected_text
            else selected_candidate.canonical_text
            if selected_candidate is not None
            else frame.raw_text
        )
        action_event = (
            WorkflowEventType.REVIEW_CONFIRMED
            if request.action == ReviewAction.CONFIRM
            else WorkflowEventType.REVIEW_CORRECTED
        )
        self.pipeline.workflow_repository.append_event(
            root_turn_id=root,
            related_turn_id=latest.turn_id,
            event_type=action_event,
            payload={
                "attempt_no": next_attempt,
                "confirmation_text": request.confirmation_text,
                "old_text": frame.raw_text,
                "corrected_text": new_text if request.action == ReviewAction.CORRECT else None,
                "selected_candidate_id": (
                    selected_candidate.candidate_id if selected_candidate is not None else None
                ),
                "selected_candidate_text": (
                    selected_candidate.canonical_text if selected_candidate is not None else None
                ),
            },
        )
        self.pipeline.workflow_repository.append_event(
            root_turn_id=root,
            related_turn_id=latest.turn_id,
            event_type=WorkflowEventType.REDECISION_STARTED,
            payload={"attempt_no": next_attempt, "text": new_text},
        )
        result = self.pipeline.process_text(
            TextCommandRequest(
                text=new_text,
                speaker_zone=latest.input_trust_result.speaker_zone,
                speaker_role=latest.input_trust_result.speaker_role,
            ),
            root_turn_id=root,
            parent_turn_id=latest.turn_id,
            attempt_no=next_attempt,
            workflow_type=(
                "REVIEW_CONFIRMATION"
                if request.action == ReviewAction.CONFIRM
                else "REVIEW_CORRECTION"
            ),
            confirmed=request.action == ReviewAction.CONFIRM,
            input_trust_override=(
                latest.input_trust_result
                if latest.input_trust_result.audio_source != "text_api"
                else None
            ),
            transcription_override=(
                latest.transcription_result
                if latest.input_trust_result.audio_source != "text_api"
                else None
            ),
            spectrum_analysis=latest.spectrum_analysis,
            audio_input_metadata=latest.audio_input_metadata,
            trusted_context=self.pipeline.trusted_context_from_audit(latest),
        )
        self.pipeline.workflow_repository.append_event(
            root_turn_id=root,
            related_turn_id=result.turn_id,
            parent_turn_id=latest.turn_id,
            event_type=WorkflowEventType.REDECISION_COMPLETED,
            payload={
                "attempt_no": next_attempt,
                "final_decision": result.decision.final_decision.value,
                "old_semantic_frame": frame.model_dump(mode="json"),
                "new_semantic_frame": result.semantic_frame.model_dump(mode="json"),
            },
        )
        return ReviewResult(
            root_turn_id=root,
            related_turn_id=result.turn_id,
            action=request.action,
            accepted=True,
            reason="已使用最新车辆状态完成完整重新裁决",
            workflow_status=self.status(root),
            decision=result.decision,
            review_question=result.decision.review_question,
            command_result=result,
        )
