from __future__ import annotations

import operator
from typing import Any, Callable

from app.models.schemas import EvidenceNode, EvidenceStatus, GateCheck, SafetyGateResult, SemanticFrame


OPERATORS: dict[str, Callable[[Any, Any], bool]] = {
    "gt": operator.gt,
    "ge": operator.ge,
    "lt": operator.lt,
    "le": operator.le,
    "eq": operator.eq,
    "ne": operator.ne,
}


class SafetyGateService:
    def __init__(self, config: dict[str, Any]) -> None:
        self.rules = config.get("rules", [])

    def evaluate(self, frame: SemanticFrame, evidence: list[EvidenceNode]) -> SafetyGateResult:
        by_type = {node.evidence_type: node for node in evidence}
        missing = [
            node.evidence_type
            for node in evidence
            if node.mandatory and node.quality_label == EvidenceStatus.MISSING
        ]
        checks = [
            GateCheck(
                rule_id="MANDATORY_EVIDENCE_AVAILABLE",
                hit=bool(missing),
                reason="强制证据缺失" if missing else "强制证据完整",
                observed={"missing_types": missing},
            )
        ]
        for rule in self.rules:
            applicable = frame.action == rule.get("action") and frame.target == rule.get("target")
            node = by_type.get(str(rule.get("evidence_type")))
            observed_value = node.value if node is not None else None
            hit = False
            if applicable and node is not None and node.quality_label == EvidenceStatus.VALID:
                op = OPERATORS.get(str(rule.get("operator")))
                if op is None:
                    raise ValueError(f"未知安全规则运算符: {rule.get('operator')}")
                hit = bool(op(observed_value, rule.get("threshold")))
            checks.append(
                GateCheck(
                    rule_id=str(rule.get("id")),
                    hit=hit,
                    reason=str(rule.get("reason")) if hit else "规则未命中",
                    observed={
                        "applicable": applicable,
                        "evidence_type": rule.get("evidence_type"),
                        "value": observed_value,
                        "operator": rule.get("operator"),
                        "threshold": rule.get("threshold"),
                    },
                )
            )
        reasons = [check.reason for check in checks if check.hit]
        return SafetyGateResult(
            blocked=bool(reasons),
            mandatory_evidence_missing=bool(missing),
            checks=checks,
            reasons=reasons,
        )
