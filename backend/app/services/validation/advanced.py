from __future__ import annotations

from time import perf_counter
import math

from app.models.schemas import (
    AdvancedValidationResult,
    ContextClaim,
    EvidenceNode,
    GroundingFailure,
    JailbreakConflict,
    SemanticFrame,
)

class AdvancedValidationService:
    def __init__(self, config: dict[str, Any]) -> None:
        self.conflict_decay_lambda = float(config.get("conflict_decay_lambda", 0.5))
        if self.conflict_decay_lambda <= 0:
            raise ValueError("conflict_decay_lambda must be positive")

    @staticmethod
    def _add_conflict(
        conflicts: list[JailbreakConflict],
        failures: list[GroundingFailure],
        *,
        claim_type: str,
        claimed: Any,
        observed: Any,
        nodes: list[EvidenceNode],
        severity: int,
        reason: str,
        rule_id: str,
        expected_types: list[str],
    ) -> None:
        node_ids = [node.node_id for node in nodes]
        conflicts.append(
            JailbreakConflict(
                claim_type=claim_type,
                claimed_value=claimed,
                observed_value=observed,
                evidence_node_ids=node_ids,
                severity=severity,
                reason=reason,
                rule_id=rule_id,
                recommended_action="BLOCK" if severity == 3 else "REVIEW",
            )
        )
        failures.append(
            GroundingFailure(
                claim=claim_type,
                expected_evidence=expected_types,
                observed_evidence={node.evidence_type: node.value for node in nodes},
                severity=severity,
                explanation=reason,
                supporting_node_ids=node_ids,
            )
        )

    def validate(
        self,
        frame: SemanticFrame,
        evidence: list[EvidenceNode],
        physical_conflicts: list[dict[str, Any]],
    ) -> AdvancedValidationResult:
        started = perf_counter()
        del evidence
        claims = [
            ContextClaim(
                claim_type="security_signal",
                claimed_value=security_signal,
                matched_text=[security_signal],
                source_text=frame.raw_text,
            )
            for security_signal in frame.security_signals
        ]
        conflicts: list[JailbreakConflict] = []
        failures: list[GroundingFailure] = []

        for claim in claims:
            if claim.claim_type == "security_signal":
                self._add_conflict(
                    conflicts,
                    failures,
                    claim_type=claim.claim_type,
                    claimed=claim.claimed_value,
                    observed=None,
                    nodes=[],
                    severity=3,
                    reason="冻结语义编排器检测到安全注入或绕过信号",
                    rule_id="SECURITY_SIGNAL_DETECTED",
                    expected_types=[],
                )

        for item in physical_conflicts:
            severity = max(1, min(3, int(item.get("severity", 1))))
            node_ids = list(item.get("node_ids", []))
            conflict = JailbreakConflict(
                claim_type="physical_evidence_conflict",
                claimed_value=item.get("type"),
                observed_value=item.get("evidence_types", []),
                evidence_node_ids=node_ids,
                severity=severity,
                reason=str(item.get("reason", "多源物理证据冲突")),
                rule_id=str(item.get("type", "PHYSICAL_EVIDENCE_CONFLICT")),
                recommended_action="BLOCK" if severity == 3 else "REVIEW",
            )
            conflicts.append(conflict)
            failures.append(
                GroundingFailure(
                    claim="physical_evidence_conflict",
                    expected_evidence=list(item.get("evidence_types", [])),
                    observed_evidence={"conflict_type": item.get("type")},
                    severity=severity,
                    explanation=conflict.reason,
                    supporting_node_ids=node_ids,
                )
            )

        distribution = {"1": 0, "2": 0, "3": 0}
        for conflict in conflicts:
            distribution[str(conflict.severity)] += 1
        max_severity = max((conflict.severity for conflict in conflicts), default=0)
        conflict_count = len(conflicts)
        risk_base = 1.0 - math.exp(-self.conflict_decay_lambda * conflict_count)
        severity_component = (
            0.0 if conflict_count == 0 else 0.5 + 0.5 * max_severity / 3.0
        )
        risk = max(0.0, min(1.0, max(risk_base, severity_component)))
        return AdvancedValidationResult(
            context_claims=claims,
            conflicts=conflicts,
            grounding_failures=failures,
            jailbreak_flag=bool(conflicts),
            jailbreak_risk=round(risk, 6),
            jailbreak_risk_base=round(risk_base, 6),
            jailbreak_risk_severity_component=round(severity_component, 6),
            conflict_count=conflict_count,
            max_severity=max_severity,
            severity_distribution=distribution,
            duration_ms=round((perf_counter() - started) * 1000, 4),
        )
