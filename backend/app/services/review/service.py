from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from app.models.schemas import (
    AuthorizationTokenStatus,
    DecisionLabel,
    ReviewAction,
    ReviewRequest,
    ReviewResult,
    TextCommandRequest,
    TurnWorkflowStatus,
    WorkflowEventType,
    utc_now,
)

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
        audit = self.pipeline.audit_repository.get_by_turn(turn_id)
        if audit is None:
            raise ReviewWorkflowError(f"未找到轮次: {turn_id}")
        return audit.root_turn_id or audit.turn_id

    def _root_audits(self, root_turn_id: str):
        audits = self.pipeline.audit_repository.records_for_root(root_turn_id)
        if not audits:
            root = self.pipeline.audit_repository.get_by_turn(root_turn_id)
            if root is not None:
                audits = [root]
        return sorted(audits, key=lambda record: (record.created_at, record.turn_id))

    def status(self, turn_id: str) -> TurnWorkflowStatus:
        root_turn_id = self.root_for_turn(turn_id)
        audits = self._root_audits(root_turn_id)
        latest = audits[-1]
        events = self.pipeline.workflow_repository.events(root_turn_id)
        attempts = sum(event.event_type in REVIEW_ACTION_EVENTS for event in events)
        terminal_event = next(
            (event for event in reversed(events) if event.event_type in TERMINAL_EVENTS), None
        )
        token = self.pipeline.workflow_repository.latest_token_for_root(root_turn_id)
        if terminal_event is not None:
            status = {
                WorkflowEventType.REVIEW_CANCELLED: "CANCELLED",
                WorkflowEventType.EXECUTION_SUCCEEDED: "EXECUTED",
                WorkflowEventType.EXECUTION_FAILED: "TERMINATED",
            }[terminal_event.event_type]
        elif latest.final_decision.final_decision == DecisionLabel.REVIEW:
            status = "REVIEW_REQUIRED"
        elif token is not None and token.status == AuthorizationTokenStatus.ISSUED:
            status = "AUTHORIZED"
        else:
            status = latest.final_decision.final_decision.value
        return TurnWorkflowStatus(
            root_turn_id=root_turn_id,
            current_turn_id=latest.turn_id,
            status=status,
            review_attempts=attempts,
            max_review_attempts=self.max_attempts,
            latest_decision=latest.final_decision.final_decision,
            token_status=token.status if token else None,
            event_count=len(events),
            terminal=terminal_event is not None,
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

    def review(self, turn_id: str, request: ReviewRequest) -> ReviewResult:
        status, latest = self._validate_entry(turn_id)
        root = status.root_turn_id
        next_attempt = status.review_attempts + 1
        if request.action == ReviewAction.CANCEL:
            self.pipeline.workflow_repository.append_event(
                root_turn_id=root,
                related_turn_id=latest.turn_id,
                parent_turn_id=latest.parent_turn_id,
                event_type=WorkflowEventType.REVIEW_CANCELLED,
                payload={"reason": request.cancel_reason or "用户取消"},
            )
            cancelled = latest.final_decision.model_copy(
                update={
                    "decision": DecisionLabel.BLOCK,
                    "final_decision": DecisionLabel.BLOCK,
                    "authorization_token": None,
                    "explanations": [
                        *latest.final_decision.explanations,
                        "用户取消复核，工作流终止",
                    ],
                }
            )
            updated = self.status(root)
            return ReviewResult(
                root_turn_id=root,
                related_turn_id=latest.turn_id,
                action=request.action,
                accepted=True,
                reason="复核已取消，未签发令牌且未执行车辆动作",
                workflow_status=updated,
                decision=cancelled,
                review_question=None,
            )

        frame = latest.semantic_frame
        has_unresolved_conflict = bool(
            latest.jailbreak_conflicts
            or latest.conflict_records
            or any(node.quality_label.value == "SUSPICIOUS" for node in (latest.evidence_subgraph.nodes if latest.evidence_subgraph else []))
        )
        if request.action == ReviewAction.CONFIRM and (
            frame.action == "unknown" or frame.target == "unknown" or has_unresolved_conflict
        ):
            reason = (
                "语义动作或目标仍不完整，CONFIRM 不能补全含义，请使用 CORRECT"
                if frame.action == "unknown" or frame.target == "unknown"
                else "证据或权限冲突仍存在，CONFIRM 不能删除冲突"
            )
            self.pipeline.workflow_repository.append_event(
                root_turn_id=root,
                related_turn_id=latest.turn_id,
                event_type=WorkflowEventType.REVIEW_CONFIRM_REJECTED,
                payload={"reason": reason, "attempt_no": next_attempt},
            )
            return ReviewResult(
                root_turn_id=root,
                related_turn_id=latest.turn_id,
                action=request.action,
                accepted=False,
                reason=reason,
                workflow_status=self.status(root),
                decision=latest.final_decision,
                review_question=latest.final_decision.review_question,
            )

        new_text = (
            request.corrected_text.strip()
            if request.action == ReviewAction.CORRECT and request.corrected_text
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
