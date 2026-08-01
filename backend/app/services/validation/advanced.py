from __future__ import annotations

from time import perf_counter
from typing import Any

from app.models.schemas import (
    AdvancedValidationResult,
    ContextClaim,
    EvidenceNode,
    GroundingFailure,
    JailbreakConflict,
    SemanticFrame,
)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).upper() in {"TRUE", "1", "YES", "AUTHENTICATED", "AUTHORIZED"}


class AdvancedValidationService:
    def __init__(self, config: dict[str, Any]) -> None:
        self.count_cap = max(1, int(config.get("count_cap", 4)))
        self.count_weight = float(config.get("count_weight", 0.4))
        self.severity_weight = float(config.get("severity_weight", 0.6))
        self.flag_threshold = float(config.get("flag_threshold", 0.25))

    @staticmethod
    def _latest_by_type(nodes: list[EvidenceNode]) -> dict[str, EvidenceNode]:
        latest: dict[str, EvidenceNode] = {}
        for node in nodes:
            current = latest.get(node.evidence_type)
            if current is None or (node.timestamp, node.node_id) > (
                current.timestamp,
                current.node_id,
            ):
                latest[node.evidence_type] = node
        return latest

    @staticmethod
    def _claimed_value(claim_type: str, matched: list[str]) -> Any:
        text = "|".join(matched)
        if claim_type == "simulator_claim":
            return "SIMULATOR"
        if claim_type == "role_claim":
            if "管理员" in text:
                return "administrator"
            if "车主" in text:
                return "owner"
            return "driver"
        if claim_type == "emergency_claim":
            return True
        if claim_type == "safety_bypass_claim":
            return "BYPASS_REQUESTED"
        if claim_type == "outside_vehicle_claim":
            return "OUTSIDE"
        if claim_type == "authorization_claim":
            return "AUTHENTICATED"
        if claim_type == "direct_interface_claim":
            return "CONTROL_FRAME" if "报文" in text or "发送" in text else "DIRECT_INTERFACE"
        if claim_type == "system_mode_claim":
            return "MODE_CHANGE_REQUESTED"
        return True

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
        by_type = self._latest_by_type(evidence)
        claims = [
            ContextClaim(
                claim_type=claim_type,
                claimed_value=self._claimed_value(
                    claim_type, list(payload.get("matched_text", []))
                ),
                matched_text=list(payload.get("matched_text", [])),
                source_text=frame.raw_text,
            )
            for claim_type, payload in frame.context_claims.items()
        ]
        conflicts: list[JailbreakConflict] = []
        failures: list[GroundingFailure] = []

        for claim in claims:
            if claim.claim_type == "simulator_claim":
                node = by_type.get("vehicle_mode")
                if node and str(node.value).upper() not in {"SIMULATOR", "TEST"}:
                    self._add_conflict(
                        conflicts,
                        failures,
                        claim_type=claim.claim_type,
                        claimed=claim.claimed_value,
                        observed=node.value,
                        nodes=[node],
                        severity=3,
                        reason="真实道路状态被声明为模拟器或测试环境",
                        rule_id="SIMULATOR_MODE_SPOOFING",
                        expected_types=["vehicle_mode"],
                    )
            elif claim.claim_type == "role_claim":
                nodes = [
                    node
                    for key in ("occupant_role", "speaker_role")
                    if (node := by_type.get(key)) is not None
                ]
                observed = [str(node.value).lower() for node in nodes]
                if str(claim.claimed_value).lower() not in observed:
                    self._add_conflict(
                        conflicts,
                        failures,
                        claim_type=claim.claim_type,
                        claimed=claim.claimed_value,
                        observed=observed,
                        nodes=nodes,
                        severity=2,
                        reason="声明角色与乘员及说话人角色证据不一致",
                        rule_id="ROLE_CLAIM_MISMATCH",
                        expected_types=["occupant_role", "speaker_role"],
                    )
            elif claim.claim_type == "emergency_claim":
                node = by_type.get("emergency_flag")
                if node is None or not _truthy(node.value):
                    self._add_conflict(
                        conflicts,
                        failures,
                        claim_type=claim.claim_type,
                        claimed=True,
                        observed=node.value if node else None,
                        nodes=[node] if node else [],
                        severity=2,
                        reason="紧急声明缺少真实紧急状态证据支持",
                        rule_id="FALSE_EMERGENCY_CLAIM",
                        expected_types=["emergency_flag"],
                    )
            elif claim.claim_type == "safety_bypass_claim":
                node = by_type.get("safety_constraint")
                enabled = node is None or str(node.value).upper() not in {"DISABLED", "OFF"}
                if enabled:
                    self._add_conflict(
                        conflicts,
                        failures,
                        claim_type=claim.claim_type,
                        claimed=claim.claimed_value,
                        observed=node.value if node else None,
                        nodes=[node] if node else [],
                        severity=3,
                        reason="请求关闭或绕过仍然启用的安全约束",
                        rule_id="SAFETY_CONSTRAINT_BYPASS",
                        expected_types=["safety_constraint"],
                    )
            elif claim.claim_type == "outside_vehicle_claim":
                node = by_type.get("speaker_zone")
                if node and str(node.value).lower() not in {"outside", "external"}:
                    self._add_conflict(
                        conflicts,
                        failures,
                        claim_type=claim.claim_type,
                        claimed="OUTSIDE",
                        observed=node.value,
                        nodes=[node],
                        severity=1,
                        reason="车外声明与车内声源区域证据不一致",
                        rule_id="OUTSIDE_ZONE_MISMATCH",
                        expected_types=["speaker_zone"],
                    )
            elif claim.claim_type == "authorization_claim":
                node = by_type.get("authentication_state")
                if node is None or not _truthy(node.value):
                    self._add_conflict(
                        conflicts,
                        failures,
                        claim_type=claim.claim_type,
                        claimed="AUTHENTICATED",
                        observed=node.value if node else None,
                        nodes=[node] if node else [],
                        severity=2,
                        reason="授权声明与认证状态不一致",
                        rule_id="AUTHORIZATION_CLAIM_MISMATCH",
                        expected_types=["authentication_state"],
                    )
            elif claim.claim_type == "direct_interface_claim":
                auth = by_type.get("authentication_state")
                if auth is None or not _truthy(auth.value):
                    severity = 3 if claim.claimed_value == "CONTROL_FRAME" else 2
                    self._add_conflict(
                        conflicts,
                        failures,
                        claim_type=claim.claim_type,
                        claimed=claim.claimed_value,
                        observed=auth.value if auth else None,
                        nodes=[auth] if auth else [],
                        severity=severity,
                        reason="未授权请求直接调用车辆接口或发送控制报文",
                        rule_id=(
                            "UNAUTHORIZED_CONTROL_FRAME"
                            if severity == 3
                            else "UNAUTHORIZED_DIRECT_INTERFACE"
                        ),
                        expected_types=["authentication_state"],
                    )
            elif claim.claim_type == "system_mode_claim":
                node = by_type.get("vehicle_mode")
                self._add_conflict(
                    conflicts,
                    failures,
                    claim_type=claim.claim_type,
                    claimed=claim.claimed_value,
                    observed=node.value if node else None,
                    nodes=[node] if node else [],
                    severity=3,
                    reason="指令请求修改或篡改受保护的系统模式",
                    rule_id="SYSTEM_MODE_TAMPERING",
                    expected_types=["vehicle_mode"],
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
        count_component = min(1.0, len(conflicts) / self.count_cap)
        severity_component = max_severity / 3
        risk = max(
            0.0,
            min(
                1.0,
                self.count_weight * count_component
                + self.severity_weight * severity_component,
            ),
        )
        return AdvancedValidationResult(
            context_claims=claims,
            conflicts=conflicts,
            grounding_failures=failures,
            jailbreak_flag=risk >= self.flag_threshold,
            jailbreak_risk=round(risk, 6),
            conflict_count=len(conflicts),
            max_severity=max_severity,
            severity_distribution=distribution,
            duration_ms=round((perf_counter() - started) * 1000, 4),
        )
