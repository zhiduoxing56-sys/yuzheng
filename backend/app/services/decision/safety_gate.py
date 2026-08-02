from __future__ import annotations

from typing import Any, Callable

from app.models.schemas import (
    AdvancedValidationResult,
    EvidenceNode,
    EvidenceStatus,
    GateCheck,
    MemoryPropagationResult,
    RuntimeCapabilityStatus,
    SafetyGateResult,
    SemanticControlMode,
    SemanticFrame,
)
from app.services.evidence.trust import (
    evidence_trust_value,
    select_canonical_evidence,
    trust_trace,
)


def _authenticated(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).upper() in {"AUTHENTICATED", "AUTHORIZED", "TRUE", "1"}


class SafetyGateService:
    """配置驱动的完整硬门；评分与因果结果均不能覆盖命中项。"""

    def __init__(self, config: dict[str, Any]) -> None:
        self.rules = list(config.get("gate_rules", []))
        self._evaluators: dict[
            str,
            Callable[
                [dict[str, Any], SemanticFrame, dict[str, EvidenceNode], list[EvidenceNode], AdvancedValidationResult],
                tuple[bool, dict[str, Any], list[str]],
            ],
        ] = {
            "mandatory_missing": self._mandatory_missing,
            "mandatory_tampered": self._mandatory_tampered,
            "level3_jailbreak": self._level3_jailbreak,
            "mandatory_stale": self._mandatory_stale,
            "mandatory_trust": self._mandatory_trust,
            "moving_door": self._moving_door,
            "low_light_headlight": self._low_light_headlight,
            "non_driver_control": self._non_driver_control,
            "real_road_bypass": self._real_road_bypass,
            "unauthorized_direct_interface": self._unauthorized_direct_interface,
            "unauthorized_control_frame": self._unauthorized_control_frame,
            "reverse_camera_display": self._reverse_camera_display,
            "active_navigation_display": self._active_navigation_display,
            "autopark_critical": self._autopark_critical,
            "acceleration_obstacle": self._acceleration_obstacle,
            "deceleration_rear_conflict": self._deceleration_rear_conflict,
            "semantic_model_degraded": self._semantic_model_degraded,
        }

    @staticmethod
    def _latest_by_type(evidence: list[EvidenceNode]) -> dict[str, EvidenceNode]:
        latest: dict[str, EvidenceNode] = {}
        for node in evidence:
            current = latest.get(node.evidence_type)
            if current is None or (
                node.timestamp.isoformat() if node.timestamp else "",
                node.node_id,
            ) > (
                current.timestamp.isoformat() if current.timestamp else "",
                current.node_id,
            ):
                latest[node.evidence_type] = node
        return latest

    @staticmethod
    def _required_status(
        frame: SemanticFrame, evidence: list[EvidenceNode], status: EvidenceStatus
    ) -> tuple[bool, dict[str, Any], list[str]]:
        resolved = select_canonical_evidence(frame.required_evidence_types, evidence)
        nodes = [node for node in resolved if node.quality_label == status]
        return (
            bool(nodes),
            {f"{status.value.lower()}_types": [node.evidence_type for node in nodes]},
            [node.node_id for node in nodes],
        )

    def _mandatory_missing(self, rule, frame, by_type, evidence, validation):
        del rule, by_type, validation
        return self._required_status(frame, evidence, EvidenceStatus.MISSING)

    def _mandatory_tampered(self, rule, frame, by_type, evidence, validation):
        del rule, by_type, validation
        return self._required_status(frame, evidence, EvidenceStatus.TAMPERED)

    def _mandatory_stale(self, rule, frame, by_type, evidence, validation):
        del rule, by_type, validation
        return self._required_status(frame, evidence, EvidenceStatus.STALE)

    @staticmethod
    def _level3_jailbreak(rule, frame, by_type, evidence, validation):
        conflicts = [item for item in validation.conflicts if item.severity == 3]
        return (
            bool(conflicts),
            {"conflict_ids": [item.conflict_id for item in conflicts]},
            [node_id for item in conflicts for node_id in item.evidence_node_ids],
        )

    @staticmethod
    def _mandatory_trust(rule, frame, by_type, evidence, validation):
        del by_type, validation
        mandatory = select_canonical_evidence(frame.required_evidence_types, evidence)
        trace = trust_trace(mandatory)
        average = (
            sum(evidence_trust_value(node.quality_label) for node in mandatory)
            / len(mandatory)
            if mandatory
            else 1.0
        )
        threshold = float(rule.get("threshold", 0.45))
        return (
            bool(mandatory) and average < threshold,
            {
                "required_evidence_count": len(frame.required_evidence_types),
                "required_trust_values": trace,
                "required_trust_average": round(average, 6),
                "required_missing_types": [
                    node.evidence_type
                    for node in mandatory
                    if node.quality_label == EvidenceStatus.MISSING
                ],
                "required_tampered_types": [
                    node.evidence_type
                    for node in mandatory
                    if node.quality_label == EvidenceStatus.TAMPERED
                ],
                "threshold": threshold,
            },
            [node.node_id for node in mandatory],
        )

    @staticmethod
    def _moving_door(rule, frame, by_type, evidence, validation):
        node = by_type.get("vehicle_speed")
        value = node.value if node else None
        hit = (
            frame.action == "打开"
            and frame.target == "车门"
            and isinstance(value, (int, float))
            and value > 0
        )
        return hit, {"value": value, "vehicle_speed": value}, [node.node_id] if node else []

    @staticmethod
    def _low_light_headlight(rule, frame, by_type, evidence, validation):
        speed = by_type.get("vehicle_speed")
        light = by_type.get("ambient_light")
        speed_value = speed.value if speed else None
        light_value = light.value if light else None
        low = (
            str(light_value).upper() in {"LOW", "DARK", "NIGHT"}
            or isinstance(light_value, (int, float))
            and light_value < float(rule.get("low_light_lux", 20))
        )
        hit = (
            frame.action == "关闭"
            and frame.target == "前照灯"
            and isinstance(speed_value, (int, float))
            and speed_value > 0
            and low
        )
        nodes = [node.node_id for node in (speed, light) if node]
        return hit, {"vehicle_speed": speed_value, "ambient_light": light_value}, nodes

    @staticmethod
    def _non_driver_control(rule, frame, by_type, evidence, validation):
        role = by_type.get("occupant_role")
        role_value = str(role.value).lower() if role else "unknown"
        driving = frame.control_domain == "驾驶控制" or frame.action in {"加速", "减速"}
        return (
            driving and role_value != "driver",
            {"occupant_role": role_value, "control_domain": frame.control_domain},
            [role.node_id] if role else [],
        )

    @staticmethod
    def _conflict_rule(validation: AdvancedValidationResult, rule_ids: set[str]):
        conflicts = [item for item in validation.conflicts if item.rule_id in rule_ids]
        return (
            bool(conflicts),
            {"conflict_ids": [item.conflict_id for item in conflicts]},
            [node_id for item in conflicts for node_id in item.evidence_node_ids],
        )

    def _real_road_bypass(self, rule, frame, by_type, evidence, validation):
        return self._conflict_rule(validation, {"SAFETY_CONSTRAINT_BYPASS", "SIMULATOR_MODE_SPOOFING"})

    def _unauthorized_direct_interface(self, rule, frame, by_type, evidence, validation):
        return self._conflict_rule(validation, {"UNAUTHORIZED_DIRECT_INTERFACE"})

    def _unauthorized_control_frame(self, rule, frame, by_type, evidence, validation):
        return self._conflict_rule(validation, {"UNAUTHORIZED_CONTROL_FRAME"})

    @staticmethod
    def _reverse_camera_display(rule, frame, by_type, evidence, validation):
        reverse = by_type.get("reverse_camera_active")
        hit = frame.action == "关闭" and frame.target == "大屏" and bool(reverse and reverse.value)
        return hit, {"reverse_camera_active": reverse.value if reverse else None}, [reverse.node_id] if reverse else []

    @staticmethod
    def _active_navigation_display(rule, frame, by_type, evidence, validation):
        navigation = by_type.get("navigation_active")
        speed = by_type.get("vehicle_speed")
        speed_value = speed.value if speed else None
        hit = (
            frame.action == "关闭"
            and frame.target == "大屏"
            and bool(navigation and navigation.value)
            and isinstance(speed_value, (int, float))
            and speed_value > 0
        )
        return hit, {"navigation_active": navigation.value if navigation else None, "vehicle_speed": speed_value}, [node.node_id for node in (navigation, speed) if node]

    @staticmethod
    def _autopark_critical(rule, frame, by_type, evidence, validation):
        critical = [
            by_type.get(key)
            for key in ("surround_view_camera", "ultrasonic_radar")
        ]
        bad = [
            node
            for node in critical
            if node is None
            or node.quality_label in {EvidenceStatus.MISSING, EvidenceStatus.STALE, EvidenceStatus.TAMPERED}
        ]
        return (
            frame.action == "打开" and frame.target == "自动泊车" and bool(bad),
            {"bad_types": [node.evidence_type if node else "unknown" for node in bad]},
            [node.node_id for node in critical if node],
        )

    @staticmethod
    def _acceleration_obstacle(rule, frame, by_type, evidence, validation):
        obstacle = by_type.get("front_obstacle_distance")
        value = obstacle.value if obstacle else None
        threshold = float(rule.get("threshold_m", 5))
        hit = frame.action == "加速" and isinstance(value, (int, float)) and value < threshold
        return hit, {"front_obstacle_distance": value, "threshold_m": threshold}, [obstacle.node_id] if obstacle else []

    @staticmethod
    def _deceleration_rear_conflict(rule, frame, by_type, evidence, validation):
        rear = by_type.get("rear_obstacle_distance")
        value = rear.value if rear else None
        conflict = any(
            "REAR" in item.rule_id or "rear" in item.reason.lower()
            for item in validation.conflicts
        )
        threshold = float(rule.get("threshold_m", 1.5))
        hit = frame.action in {"减速", "打开"} and frame.target in {"速度", "制动"} and (
            conflict or isinstance(value, (int, float)) and value < threshold
        )
        return hit, {"rear_obstacle_distance": value, "conflict": conflict}, [rear.node_id] if rear else []

    @staticmethod
    def _semantic_model_degraded(rule, frame, by_type, evidence, validation):
        del by_type, evidence, validation
        capability = rule.get("_runtime_capability")
        if capability is None:
            return False, {"semantic_control_mode": "FULL"}, []
        executable = frame.action != "查询" and frame.target != "unknown"
        hit = executable and (
            capability.semantic_control_mode == SemanticControlMode.QUERY_ONLY
            or (
                capability.semantic_control_mode == SemanticControlMode.RESTRICTED
                and frame.risk_level == "R3"
            )
        )
        return (
            hit,
            {
                "reason_code": "SEMANTIC_MODEL_DEGRADED_HIGH_RISK",
                "semantic_control_mode": capability.semantic_control_mode.value,
                "embedding_implementation": capability.embedding_implementation,
                "risk_level": frame.risk_level,
            },
            [],
        )

    def evaluate(
        self,
        frame: SemanticFrame,
        evidence: list[EvidenceNode],
        validation: AdvancedValidationResult | None = None,
        memory: MemoryPropagationResult | None = None,
        runtime_capability: RuntimeCapabilityStatus | None = None,
    ) -> SafetyGateResult:
        del memory  # 传播结果只能解释风险，不能抵消硬门。
        validation = validation or AdvancedValidationResult()
        by_type = self._latest_by_type(evidence)
        checks: list[GateCheck] = []
        for rule in self.rules:
            rule = dict(rule)
            rule["_runtime_capability"] = runtime_capability
            evaluator_name = str(rule.get("evaluator"))
            evaluator = self._evaluators.get(evaluator_name)
            if evaluator is None:
                raise ValueError(f"未知安全门评估器: {evaluator_name}")
            hit, observed, node_ids = evaluator(rule, frame, by_type, evidence, validation)
            reason = str(rule.get("reason")) if hit else "规则未命中"
            affected_types = (
                observed.get("missing_types")
                or observed.get("tampered_types")
                or []
            )
            if hit and affected_types:
                reason = f"{reason}: {','.join(str(item) for item in affected_types)}"
            checks.append(
                GateCheck(
                    rule_id=str(rule.get("id")),
                    hit=hit,
                    reason=reason,
                    observed=observed,
                    supporting_evidence_ids=sorted(set(node_ids)),
                )
            )
        reasons: list[str] = []
        for check in checks:
            if not check.hit:
                continue
            base_reason = check.reason.split(":", 1)[0]
            if base_reason not in reasons:
                reasons.append(base_reason)
            if check.reason not in reasons:
                reasons.append(check.reason)
        hit_rules = [check.rule_id for check in checks if check.hit]
        supporting = sorted(
            {node_id for check in checks if check.hit for node_id in check.supporting_evidence_ids}
        )
        missing_check = next(
            (check for check in checks if check.rule_id == "MANDATORY_EVIDENCE_AVAILABLE"),
            None,
        )
        return SafetyGateResult(
            blocked=bool(hit_rules),
            gate_blocked=bool(hit_rules),
            mandatory_evidence_missing=bool(missing_check and missing_check.hit),
            checks=checks,
            reasons=reasons,
            hit_rules=hit_rules,
            observed_values={check.rule_id: check.observed for check in checks if check.hit},
            supporting_evidence_ids=supporting,
        )
