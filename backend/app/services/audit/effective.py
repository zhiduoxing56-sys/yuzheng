from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.models.schemas import (
    AuditRecord,
    DecisionResult,
    DecisionSource,
    ReviewOutcomeRecord,
    SafetyGateResult,
)
from app.services.audit.repository import AuditRepository
from app.services.decision.merge import apply_merge_outcome, merge_decision

if TYPE_CHECKING:
    from app.services.workflow.repository import WorkflowRepository


@dataclass(frozen=True)
class EffectiveAuditResolution:
    original: AuditRecord
    outcome: ReviewOutcomeRecord | None
    effective_decision: DecisionResult


class EffectiveAuditResolver:
    """Single read path for immutable command audits plus terminal outcomes."""

    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

    @staticmethod
    def _alignment_route(record: AuditRecord) -> str:
        metrics = record.evidence_quality_metrics
        route = (
            metrics.evidence_alignment_route
            if hasattr(metrics, "evidence_alignment_route")
            else metrics.get("evidence_alignment_route")
        )
        return str(route or "EVIDENCE_PASS")

    def resolve(self, record: AuditRecord) -> EffectiveAuditResolution:
        outcome = self.repository.outcome_for_original(record.audit_id)
        effective = self.resolve_effective_decision(
            audit_id=record.audit_id,
            turn_id=record.turn_id,
            original=record.final_decision,
            gate_result=record.safety_gate_result,
            evidence_alignment_route=self._alignment_route(record),
            outcome=outcome,
        )
        return EffectiveAuditResolution(record, outcome, effective)

    @staticmethod
    def resolve_effective_decision(
        *,
        audit_id: str,
        turn_id: str,
        original: DecisionResult,
        gate_result: SafetyGateResult,
        evidence_alignment_route: str,
        outcome: ReviewOutcomeRecord | None,
    ) -> DecisionResult:
        if outcome is None:
            return original
        if outcome.original_audit_id != audit_id:
            raise ValueError("REVIEW_OUTCOME original_audit_id 与原始审计不一致")
        if outcome.original_turn_id != turn_id:
            raise ValueError("REVIEW_OUTCOME original_turn_id 与原始审计不一致")
        if outcome.original_final_decision != original.final_decision:
            raise ValueError("REVIEW_OUTCOME original_final_decision 与原始审计不一致")
        merged = merge_decision(
            gate_result,
            evidence_alignment_route,
            original.score_decision,
            block_constraints=[DecisionSource.USER_REVIEW],
            constraint_reasons={DecisionSource.USER_REVIEW: "用户取消本轮指令"},
        )
        if (
            merged.final_decision != outcome.effective_final_decision
            or list(merged.decision_sources) != outcome.effective_decision_sources
            or merged.decision_merge_reason != outcome.decision_merge_reason
        ):
            raise ValueError("REVIEW_OUTCOME 与统一 merge_decision 结果不一致")
        effective = apply_merge_outcome(
            original,
            merged,
            explanation="用户取消复核，工作流终止",
        )
        return effective

    def resolve_by_audit_id(self, audit_id: str) -> EffectiveAuditResolution | None:
        record = self.repository.get_chain_record_by_id(audit_id)
        if record is None:
            return None
        if isinstance(record, ReviewOutcomeRecord):
            original = self.repository.get_by_id(record.original_audit_id)
            if original is None:
                raise ValueError("REVIEW_OUTCOME 关联的原始审计不存在")
            return self.resolve(original)
        return self.resolve(record)

    def verify(
        self, audit_id: str, workflow_repository: "WorkflowRepository"
    ) -> dict[str, object] | None:
        resolution = self.resolve_by_audit_id(audit_id)
        if resolution is None:
            return None
        original = resolution.original
        original_verification = self.repository.verify_record(original.audit_id)
        if original_verification is None:
            return None
        outcome = resolution.outcome
        terminal_verification = (
            self.repository.verify_record(outcome.audit_id) if outcome else None
        )
        relationship_valid = bool(
            outcome is None
            or (
                self.repository.get_by_id(outcome.original_audit_id) is not None
                and outcome.original_turn_id == original.turn_id
                and outcome.original_final_decision
                == original.final_decision.final_decision
                and outcome.review_action.value == "CANCEL"
                and DecisionSource.USER_REVIEW
                in outcome.effective_decision_sources
            )
        )
        merge_valid = bool(
            outcome is None
            or (
                resolution.effective_decision.final_decision
                == outcome.effective_final_decision
                and resolution.effective_decision.decision_merge_reason
                == outcome.decision_merge_reason
            )
        )
        effective_valid = bool(
            outcome is None
            or resolution.effective_decision.final_decision.value == "BLOCK"
        )
        workflow_valid = workflow_repository.verify_chain(
            original.root_turn_id or original.turn_id
        ).valid
        return {
            **original_verification,
            "workflow_chain_valid": workflow_valid,
            "terminal_audit_id": outcome.audit_id if outcome else None,
            "terminal_record_hash_valid": (
                terminal_verification["record_hash_valid"]
                if terminal_verification
                else None
            ),
            "terminal_previous_link_valid": (
                terminal_verification["previous_link_valid"]
                if terminal_verification
                else None
            ),
            "relationship_valid": relationship_valid,
            "merge_decision_valid": merge_valid,
            "effective_outcome_valid": effective_valid,
        }
