from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Protocol

from pydantic import Field

from app.models.schemas import AuditRecord, StrictModel, utc_now


SYSTEM_PROMPT = """你只负责解释已经完成的安全裁决。
只能使用提供的结构化审计事实。
禁止补充审计数据中不存在的车辆状态、环境、传感器结果或安全规则。
禁止修改、质疑或重新裁决给定的 PASS / REVIEW / BLOCK。
如果现有事实不足以解释某一细节，应明确说明现有审计事实不足。
输出 2 至 5 句简洁、专业、面向安全审计人员的中文说明。
只返回 JSON 对象，唯一字段为 llm_explanation。"""


class ExplanationProvider(Protocol):
    name: str
    model: str | None

    def generate(self, system_prompt: str, payload: dict[str, Any]) -> dict[str, Any]: ...


class AuditExplanationContext(StrictModel):
    raw_command: str
    input_type: str
    resolved_intents: list[dict[str, Any]] = Field(default_factory=list)
    final_decision: str
    aggregate_safety_decision: str | None = None
    decision_snapshot: dict[str, Any] | None = None
    key_evidence: list[dict[str, Any]] = Field(default_factory=list)
    gate_hit_rules: list[str] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)
    intent_safety_assessments: list[dict[str, Any]] = Field(default_factory=list)
    clarification_history: list[dict[str, Any]] = Field(default_factory=list)
    authorization_status: str | None = None
    execution_status: str | None = None


class AuditExplanationResult(StrictModel):
    status: str
    explanation: str | None = None
    model: str | None = None
    generated_at: datetime = Field(default_factory=utc_now)
    failure_reason: str | None = None


class AuditExplanationService:
    def __init__(self, provider: ExplanationProvider | None) -> None:
        self.provider = provider

    @staticmethod
    def context(record: AuditRecord, *, decision_snapshot: dict[str, Any] | None) -> AuditExplanationContext:
        nodes = record.evidence_subgraph.nodes if record.evidence_subgraph else []
        by_id = {node.node_id: node for node in nodes}
        cited_ids = set(record.safety_gate_result.supporting_evidence_ids)
        for assessment in record.final_decision.intent_safety_assessments:
            cited_ids.update(assessment.supporting_evidence_ids)
        key_evidence = [
            {
                "evidence_type": node.evidence_type,
                "value": node.value,
                "unit": node.unit,
                "source": node.source,
            }
            for node_id in sorted(cited_ids)
            if (node := by_id.get(node_id)) is not None
        ]
        clarification_context = record.audio_input_metadata.get("clarification_context")
        clarification_history = (
            [
                {
                    "selected_candidate": clarification_context.get("confirmed_text"),
                    "resolution": "SELECTED",
                    "confirmed_text": clarification_context.get("confirmed_text"),
                }
            ]
            if isinstance(clarification_context, dict)
            else []
        )
        return AuditExplanationContext(
            raw_command=record.semantic_frame.raw_text,
            input_type=(
                "text"
                if record.input_trust_result.audio_source == "text_api"
                else "audio"
            ),
            resolved_intents=[
                {
                    "operation": intent.clause_text,
                    "action": intent.action,
                    "target": intent.target,
                    "area": None if intent.area == "unknown" else intent.area,
                    "value": intent.value,
                }
                for intent in record.semantic_frame.intents
            ],
            final_decision=record.final_decision.final_decision.value,
            aggregate_safety_decision=(
                record.final_decision.aggregate_safety_decision.value
                if record.final_decision.aggregate_safety_decision
                else None
            ),
            decision_snapshot=decision_snapshot,
            key_evidence=key_evidence,
            gate_hit_rules=record.safety_gate_result.hit_rules,
            reason_codes=record.final_decision.reason_codes,
            intent_safety_assessments=[
                {
                    "operation": next(
                        (
                            intent.clause_text
                            for intent in record.semantic_frame.intents
                            if intent.clause_index == assessment.clause_index
                            and intent.intent_id == assessment.intent_id
                        ),
                        "",
                    ),
                    "decision": assessment.final_safety_decision.value,
                    "hit_rules": assessment.gate_hit_rules,
                    "reason_codes": assessment.reason_codes,
                    "reasons": assessment.gate_reasons,
                }
                for assessment in record.final_decision.intent_safety_assessments
            ],
            clarification_history=clarification_history,
        )

    @staticmethod
    def _validate(text: Any, final_decision: str) -> str:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("llm_explanation must be non-empty text")
        cleaned = text.strip()
        if len(cleaned) > 1000:
            raise ValueError("llm_explanation is too long")
        sentences = [part for part in re.split(r"[。！？!?]+", cleaned) if part.strip()]
        if not 1 <= len(sentences) <= 5:
            raise ValueError("llm_explanation must contain at most five sentences")
        other_decisions = {"PASS", "REVIEW", "BLOCK"} - {final_decision}
        if any(value in cleaned for value in other_decisions):
            raise ValueError("llm_explanation conflicts with final_decision")
        return cleaned

    def generate(self, context: AuditExplanationContext) -> AuditExplanationResult:
        generated_at = utc_now()
        if self.provider is None:
            return AuditExplanationResult(
                status="FAILED",
                generated_at=generated_at,
                failure_reason="PROVIDER_NOT_CONFIGURED",
            )
        try:
            output = self.provider.generate(
                SYSTEM_PROMPT, context.model_dump(mode="json", exclude_none=True)
            )
            if set(output) != {"llm_explanation"}:
                raise ValueError("provider returned fields outside AuditExplanationContext boundary")
            explanation = self._validate(
                output.get("llm_explanation"), context.final_decision
            )
            return AuditExplanationResult(
                status="AVAILABLE",
                explanation=explanation,
                model=self.provider.model,
                generated_at=generated_at,
            )
        except Exception as exc:
            return AuditExplanationResult(
                status="FAILED",
                model=self.provider.model,
                generated_at=generated_at,
                failure_reason=type(exc).__name__,
            )
