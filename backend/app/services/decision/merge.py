from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Mapping

from app.models.schemas import (
    DecisionLabel,
    DecisionSource,
    SafetyGateResult,
)


EvidenceAlignmentRoute = Literal[
    "EVIDENCE_PASS", "EVIDENCE_REVIEW", "EVIDENCE_BLOCK"
]

_BASE_DECISION_SOURCES = (
    DecisionSource.SAFETY_GATE,
    DecisionSource.EVIDENCE_ALIGNMENT,
    DecisionSource.SAFETY_SCORE,
)


@dataclass(frozen=True)
class DecisionMergeOutcome:
    final_decision: DecisionLabel
    decision_sources: tuple[DecisionSource, ...]
    decision_merge_reason: str


def merge_decision(
    gate_result: SafetyGateResult,
    evidence_alignment_route: EvidenceAlignmentRoute,
    score_decision: DecisionLabel,
    *,
    review_constraints: Iterable[DecisionSource] = (),
    block_constraints: Iterable[DecisionSource] = (),
    constraint_reasons: Mapping[DecisionSource, str] | None = None,
    prior_final_decision: DecisionLabel | None = None,
    prior_decision_sources: Iterable[DecisionSource] = (),
) -> DecisionMergeOutcome:
    """Merge independent decision layers once, preserving the raw score verdict."""

    review_set = set(review_constraints)
    block_set = set(block_constraints)
    prior_set = set(prior_decision_sources)
    for values in (review_set, block_set, prior_set):
        values.discard(DecisionSource.LEGACY_COMPATIBILITY)
    review_sources = tuple(source for source in DecisionSource if source in review_set)
    block_sources = tuple(source for source in DecisionSource if source in block_set)
    extra_set = review_set | block_set | prior_set
    constraint_reasons = constraint_reasons or {}
    sources = tuple(
        source
        for source in DecisionSource
        if source in set(_BASE_DECISION_SOURCES) | extra_set
    )

    def with_sources(reason: str) -> str:
        extra_names = ",".join(
            source.value for source in sources if source not in _BASE_DECISION_SOURCES
        )
        return reason + f"; applied_constraints={extra_names or 'NONE'}"
    if gate_result.blocked:
        return DecisionMergeOutcome(
            final_decision=DecisionLabel.BLOCK,
            decision_sources=sources,
            decision_merge_reason=with_sources(
                "SAFETY_GATE constrained final_decision to BLOCK; "
                f"hit_rules={','.join(gate_result.hit_rules) or 'UNSPECIFIED'}"
            ),
        )
    if block_sources:
        names = ",".join(source.value for source in block_sources)
        reasons = "；".join(
            constraint_reasons.get(source, "")
            for source in block_sources
            if constraint_reasons.get(source)
        )
        return DecisionMergeOutcome(
            final_decision=DecisionLabel.BLOCK,
            decision_sources=sources,
            decision_merge_reason=with_sources(
                f"{names} constrained final_decision to BLOCK"
                + (f"：{reasons}" if reasons else "")
                + f"; score_decision={score_decision.value} preserved"
            ),
        )
    if prior_final_decision == DecisionLabel.BLOCK:
        return DecisionMergeOutcome(
            final_decision=DecisionLabel.BLOCK,
            decision_sources=sources,
            decision_merge_reason=with_sources(
                "Previously merged constraints preserve final_decision=BLOCK; "
                f"score_decision={score_decision.value} preserved"
            ),
        )
    if evidence_alignment_route == "EVIDENCE_BLOCK":
        return DecisionMergeOutcome(
            final_decision=DecisionLabel.BLOCK,
            decision_sources=sources,
            decision_merge_reason=with_sources(
                "EVIDENCE_ALIGNMENT constrained final_decision to BLOCK "
                f"from score_decision={score_decision.value}"
            ),
        )
    if evidence_alignment_route == "EVIDENCE_REVIEW":
        final = (
            DecisionLabel.BLOCK
            if score_decision == DecisionLabel.BLOCK
            else DecisionLabel.REVIEW
        )
        return DecisionMergeOutcome(
            final_decision=final,
            decision_sources=sources,
            decision_merge_reason=with_sources(
                "EVIDENCE_ALIGNMENT required REVIEW and conservative severity merge "
                f"produced {final.value} from score_decision={score_decision.value}"
            ),
        )
    if evidence_alignment_route != "EVIDENCE_PASS":
        raise ValueError(
            f"unsupported evidence_alignment_route: {evidence_alignment_route}"
        )
    if (
        review_sources or prior_final_decision == DecisionLabel.REVIEW
    ) and score_decision != DecisionLabel.BLOCK:
        names = ",".join(source.value for source in review_sources) or "PRIOR_CONSTRAINTS"
        return DecisionMergeOutcome(
            final_decision=DecisionLabel.REVIEW,
            decision_sources=sources,
            decision_merge_reason=with_sources(
                f"{names} constrained final_decision to REVIEW "
                f"from score_decision={score_decision.value}"
            ),
        )
    return DecisionMergeOutcome(
        final_decision=score_decision,
        decision_sources=sources,
        decision_merge_reason=with_sources(
            "EVIDENCE_ALIGNMENT passed; final_decision equals "
            f"score_decision={score_decision.value}"
        ),
    )


def apply_merge_outcome(
    original: "DecisionResult",
    merged: DecisionMergeOutcome,
    *,
    explanation: str | None = None,
    field_updates: Mapping[str, object] | None = None,
) -> "DecisionResult":
    """Construct one effective DecisionResult from a merge outcome.

    This is the sole constructor used when an already-scored decision gains a
    later constraint.  The raw decision/score_decision and score factors remain
    unchanged; final_decision is never recomputed here.
    """

    from app.models.schemas import DecisionResult

    protected_fields = {
        "decision",
        "score_decision",
        "final_decision",
        "decision_sources",
        "decision_merge_reason",
    }
    field_updates = dict(field_updates or {})
    forbidden_updates = protected_fields & set(field_updates)
    if forbidden_updates:
        raise ValueError(
            "apply_merge_outcome field_updates不得覆盖统一裁决字段: "
            + ",".join(sorted(forbidden_updates))
        )

    payload = original.model_dump(mode="json")
    payload.update(field_updates)
    explanations = list(payload.get("explanations", []))
    if explanation and explanation not in explanations:
        explanations.append(explanation)
    if merged.decision_merge_reason not in explanations:
        explanations.append(merged.decision_merge_reason)
    payload.update(
        {
            "final_decision": merged.final_decision,
            "decision_sources": list(merged.decision_sources),
            "decision_merge_reason": merged.decision_merge_reason,
            "authorization_token": None,
            "review_question": field_updates.get("review_question"),
            "explanations": explanations,
        }
    )
    return DecisionResult.model_validate(payload)
