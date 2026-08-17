from __future__ import annotations

from typing import Any, Callable

from app.models.schemas import (
    AdvancedValidationResult,
    EvidenceDemand,
    EvidenceNode,
    EvidenceStatus,
    GateCheck,
    IntentEvidenceDemand,
    IntentEvidenceResolution,
    MemoryPropagationResult,
    RuntimeCapabilityStatus,
    RuntimeSafetyContext,
    SafetyGateResult,
    SemanticControlMode,
    SemanticFrame,
    SemanticIntent,
)
from app.services.evidence.resolution import project_evidence_resolutions
from app.services.evidence.trust import (
    evidence_trust_value,
    select_canonical_evidence,
    trust_trace,
)
from app.services.evidence.value_contract import (
    is_finite_number,
    validate_evidence_value,
)
from semantic_registry_v1 import UnifiedSemanticRegistry


class SafetyGateService:
    """配置驱动的完整硬门；评分与因果结果均不能覆盖命中项。"""

    def __init__(self, config: dict[str, Any]) -> None:
        self.rules = list(config.get("gate_rules", []))
        self._evaluators: dict[
            str,
            Callable[
                [
                    dict[str, Any],
                    SemanticIntent | None,
                    IntentEvidenceDemand | None,
                    dict[str, EvidenceNode],
                    list[EvidenceNode],
                    AdvancedValidationResult,
                ],
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
            "dense_fog_defog": self._dense_fog_defog,
            "non_driver_control": self._non_driver_control,
            "real_road_bypass": self._real_road_bypass,
            "unauthorized_direct_interface": self._unauthorized_direct_interface,
            "unauthorized_control_frame": self._unauthorized_control_frame,
            "acceleration_obstacle": self._acceleration_obstacle,
            "deceleration_rear_conflict": self._deceleration_rear_conflict,
            "reverse_camera_display_off": self._reverse_camera_display_off,
            "semantic_model_degraded": self._semantic_model_degraded,
        }
        self._semantic_registry = UnifiedSemanticRegistry()
        self._validate_canonical_selectors()

    def _validate_canonical_selectors(self) -> None:
        for rule in self.rules:
            intent_ids = rule.get("intent_ids", [])
            if not isinstance(intent_ids, list):
                raise ValueError(f"{rule.get('id')} intent_ids 必须是列表")
            for intent_id in intent_ids:
                definition = self._semantic_registry.definition(str(intent_id))
                if definition["runtime_identity"] != "FORMAL":
                    raise ValueError(
                        f"SafetyGate selector 不得引用 Known Intent: {intent_id}"
                    )
                if "mode" in rule:
                    if "MODE" not in {
                        *definition.get("required_slots", []),
                        *definition.get("optional_slots", []),
                    }:
                        raise ValueError(f"{intent_id} SafetyGate selector 不承载 MODE")
                    reference = definition.get("mode_contract")
                    allowed = self._semantic_registry.document.get(
                        "mode_contracts", {}
                    ).get(reference, [])
                    if rule["mode"] not in allowed:
                        raise ValueError(
                            f"{intent_id} SafetyGate mode selector 不合法: {rule['mode']}"
                        )

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
    def _field(node: EvidenceNode | None, name: str) -> Any:
        if node is None or not isinstance(node.value, dict):
            return None
        return node.value.get(name)

    @staticmethod
    def _required_status(
        demand: IntentEvidenceDemand,
        evidence: list[EvidenceNode],
        status: EvidenceStatus,
    ) -> tuple[bool, dict[str, Any], list[str]]:
        resolved = select_canonical_evidence(demand.required_types, evidence)
        nodes = [node for node in resolved if node.quality_label == status]
        return (
            bool(nodes),
            {f"{status.value.lower()}_types": [node.evidence_type for node in nodes]},
            [node.node_id for node in nodes],
        )

    def _mandatory_missing(self, rule, intent, demand, by_type, evidence, validation):
        del rule, intent, by_type, validation
        resolved = select_canonical_evidence(demand.required_types, evidence)
        missing = [
            node for node in resolved if node.quality_label == EvidenceStatus.MISSING
        ]
        upstream_violations = []
        for node in resolved:
            value_validation = validate_evidence_value(node.evidence_type, node.value)
            if (
                node.quality_label in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
                and value_validation.applicable
                and not value_validation.usable
            ):
                upstream_violations.append((node, value_validation))
        unavailable = [*missing, *(node for node, _ in upstream_violations)]
        return (
            bool(unavailable),
            {
                "missing_types": list(
                    dict.fromkeys(node.evidence_type for node in unavailable)
                ),
                "upstream_value_contract_violations": [
                    value_validation.violation_summary()
                    for _, value_validation in upstream_violations
                ],
            },
            list(dict.fromkeys(node.node_id for node in unavailable)),
        )

    def _mandatory_tampered(self, rule, intent, demand, by_type, evidence, validation):
        del rule, intent, by_type, validation
        return self._required_status(demand, evidence, EvidenceStatus.TAMPERED)

    def _mandatory_stale(self, rule, intent, demand, by_type, evidence, validation):
        del rule, intent, by_type, validation
        return self._required_status(demand, evidence, EvidenceStatus.STALE)

    @staticmethod
    def _level3_jailbreak(rule, intent, demand, by_type, evidence, validation):
        del rule, intent, demand, by_type, evidence
        conflicts = [item for item in validation.conflicts if item.severity == 3]
        return (
            bool(conflicts),
            {"conflict_ids": [item.conflict_id for item in conflicts]},
            [node_id for item in conflicts for node_id in item.evidence_node_ids],
        )

    @staticmethod
    def _mandatory_trust(rule, intent, demand, by_type, evidence, validation):
        del intent, by_type, validation
        required_nodes = select_canonical_evidence(demand.required_types, evidence)
        trace = trust_trace(required_nodes)
        average = (
            sum(evidence_trust_value(node.quality_label) for node in required_nodes)
            / len(required_nodes)
            if required_nodes
            else 1.0
        )
        threshold = float(rule.get("threshold", 0.45))
        return (
            bool(required_nodes) and average < threshold,
            {
                "required_evidence_count": len(demand.required_types),
                "required_trust_values": trace,
                "required_trust_average": round(average, 6),
                "required_missing_types": [
                    node.evidence_type
                    for node in required_nodes
                    if node.quality_label == EvidenceStatus.MISSING
                ],
                "required_tampered_types": [
                    node.evidence_type
                    for node in required_nodes
                    if node.quality_label == EvidenceStatus.TAMPERED
                ],
                "threshold": threshold,
            },
            [node.node_id for node in required_nodes],
        )

    @staticmethod
    def _moving_door(rule, intent, demand, by_type, evidence, validation):
        del demand, evidence, validation
        node = by_type.get("VEHICLE_SPEED")
        value = node.value if node else None
        intent_ids = {str(item) for item in rule.get("intent_ids", [])}
        opening = intent.intent_id == "DOOR_OPEN" or (
            intent.intent_id == "DOOR_SET_POSITION"
            and is_finite_number(intent.value)
            and intent.value > 0
        )
        hit = intent.intent_id in intent_ids and opening and is_finite_number(value) and value > 0
        return hit, {
            "value": intent.value if intent.intent_id == "DOOR_SET_POSITION" else value,
            "vehicle_speed": value,
            "area": intent.area,
            "control_attribute": intent.control_attribute,
        }, [node.node_id] if node else []

    @staticmethod
    def _low_light_headlight(rule, intent, demand, by_type, evidence, validation):
        del demand, evidence, validation
        speed = by_type.get("VEHICLE_SPEED")
        light = by_type.get("ENVIRONMENT_CONDITIONS")
        speed_value = speed.value if speed else None
        light_value = SafetyGateService._field(light, "ambient_illumination")
        low = (
            str(light_value).upper() in {"LOW", "DARK", "NIGHT"}
            or is_finite_number(light_value)
            and light_value < float(rule.get("low_light_lux", 20))
        )
        # off_intent_ids 覆盖 LOW_BEAM_OFF/HIGH_BEAM_OFF 这类"本身就是关闭"的意图
        off_intent_ids = {str(item) for item in rule.get("off_intent_ids", [])}
        intent_match = (
            (
                intent.intent_id in {str(item) for item in rule.get("intent_ids", [])}
                and intent.mode == rule.get("mode")
            )
            or intent.intent_id in off_intent_ids
        )
        # 行驶判定：speed 未知/不可用时按 fail-closed 拦截(无法证明已驻车)，
        # 避免某些 intent 的 VEHICLE_SPEED 证据缺失导致夜间关灯被放行
        moving = not (is_finite_number(speed_value) and speed_value == 0)
        hit = (
            intent_match
            and moving
            and low
        )
        nodes = [node.node_id for node in (speed, light) if node]
        return hit, {
            "vehicle_speed": speed_value,
            "ambient_light": light_value,
            "mode": intent.mode,
            "control_attribute": intent.control_attribute,
        }, nodes

    @staticmethod
    def _dense_fog_defog(rule, intent, demand, by_type, evidence, validation):
        del demand, evidence, validation
        weather = by_type.get("ENVIRONMENT_CONDITIONS")
        raw_weather = SafetyGateService._field(weather, "weather")
        value = str(raw_weather).strip().upper() if raw_weather is not None else None
        dense_fog_values = {
            str(item).strip().upper()
            for item in rule.get(
                "dense_fog_values",
                ["DENSE_FOG", "HEAVY_FOG", "FOG", "浓雾", "大雾"],
            )
        }
        hit = (
            intent.intent_id in {str(item) for item in rule.get("intent_ids", [])}
            and value in dense_fog_values
        )
        return (
            hit,
            {
                "weather": value,
                "dense_fog_values": sorted(dense_fog_values),
                "area": intent.area,
                "control_attribute": intent.control_attribute,
            },
            [weather.node_id] if weather else [],
        )

    @staticmethod
    def _non_driver_control(rule, intent, demand, by_type, evidence, validation):
        del rule, demand, evidence, validation
        authorization = by_type.get("AUTHORIZATION_STATE")
        value = authorization.value if authorization and isinstance(authorization.value, dict) else {}
        role_value = value.get("subject_role")
        occurrences = value.get("intent_authorizations", [])
        occurrence = next(
            (
                item
                for item in occurrences
                if isinstance(item, dict)
                and item.get("clause_index") == intent.clause_index
                and item.get("intent_id") == intent.intent_id
            ),
            None,
        )
        driving = intent.control_domain == "驾驶控制"
        return (
            driving
            and (
                str(role_value).lower() != "driver"
                or occurrence is None
                or occurrence.get("authorized") is not True
            ),
            {
                "subject_role": role_value,
                "control_domain": intent.control_domain,
                "authorization_found": occurrence is not None,
                "authorized": occurrence.get("authorized") if occurrence else None,
            },
            [authorization.node_id] if authorization else [],
        )

    @staticmethod
    def _conflict_rule(validation: AdvancedValidationResult, rule_ids: set[str]):
        conflicts = [item for item in validation.conflicts if item.rule_id in rule_ids]
        return (
            bool(conflicts),
            {"conflict_ids": [item.conflict_id for item in conflicts]},
            [node_id for item in conflicts for node_id in item.evidence_node_ids],
        )

    def _real_road_bypass(self, rule, intent, demand, by_type, evidence, validation):
        del rule, intent, demand, by_type, evidence
        return self._conflict_rule(validation, {"SAFETY_CONSTRAINT_BYPASS", "SIMULATOR_MODE_SPOOFING"})

    def _unauthorized_direct_interface(self, rule, intent, demand, by_type, evidence, validation):
        del rule, intent, demand, by_type, evidence
        return self._conflict_rule(validation, {"UNAUTHORIZED_DIRECT_INTERFACE"})

    def _unauthorized_control_frame(self, rule, intent, demand, by_type, evidence, validation):
        del rule, intent, demand, by_type, evidence
        return self._conflict_rule(validation, {"UNAUTHORIZED_CONTROL_FRAME"})

    @staticmethod
    def _acceleration_obstacle(rule, intent, demand, by_type, evidence, validation):
        del demand, evidence, validation
        obstacle = by_type.get("SURROUNDING_OBJECT_STATE")
        value = SafetyGateService._field(obstacle, "front_obstacle_distance")
        threshold = float(rule.get("threshold_m", 5))
        hit = (
            intent.intent_id in {str(item) for item in rule.get("intent_ids", [])}
            and is_finite_number(value)
            and value < threshold
        )
        return hit, {"front_obstacle_distance": value, "threshold_m": threshold}, [obstacle.node_id] if obstacle else []

    @staticmethod
    def _deceleration_rear_conflict(rule, intent, demand, by_type, evidence, validation):
        del demand, evidence
        rear = by_type.get("SURROUNDING_OBJECT_STATE")
        value = SafetyGateService._field(rear, "rear_obstacle_distance")
        conflict = any(
            "REAR" in item.rule_id or "rear" in item.reason.lower()
            for item in validation.conflicts
        )
        threshold = float(rule.get("threshold_m", 1.5))
        applies = intent.intent_id in {
            str(item) for item in rule.get("intent_ids", [])
        }
        available = rear is not None
        usable = available and is_finite_number(value)
        failure_reason = None
        if applies and not available:
            failure_reason = "SURROUNDING_OBJECT_STATE_MISSING"
        elif applies and not usable:
            failure_reason = "REAR_OBSTACLE_DISTANCE_UNUSABLE"
        elif applies and conflict:
            failure_reason = "REAR_VALIDATION_CONFLICT"
        elif applies and value < threshold:
            failure_reason = "REAR_DISTANCE_BELOW_THRESHOLD"
        hit = applies and (not available or not usable or conflict or value < threshold)
        return (
            hit,
            {
                "rear_state_available": available,
                "rear_obstacle_distance": value,
                "rear_state_usable": usable,
                "threshold": threshold,
                "conflict": conflict,
                "failure_reason": failure_reason,
            },
            [rear.node_id] if rear is not None else [],
        )

    @staticmethod
    def _semantic_model_degraded(rule, intent, demand, by_type, evidence, validation):
        del demand, by_type, evidence, validation
        capability = rule.get("_runtime_capability")
        if capability is None:
            return False, {"semantic_control_mode": "FULL"}, []
        formal = intent.runtime_identity == "FORMAL"
        hit = formal and (
            capability.semantic_control_mode == SemanticControlMode.QUERY_ONLY
            or (
                capability.semantic_control_mode == SemanticControlMode.RESTRICTED
                and intent.risk_level == "R3"
            )
        )
        return (
            hit,
            {
                "reason_code": "SEMANTIC_MODEL_DEGRADED_HIGH_RISK",
                "semantic_control_mode": capability.semantic_control_mode.value,
                "embedding_implementation": capability.embedding_implementation,
                "risk_level": intent.risk_level,
            },
            [],
        )

    def _reverse_camera_display_off(self, rule, intent, demand, by_type, evidence, validation):
        del intent, demand, by_type, evidence, validation
        context = rule.get("_runtime_safety_context")
        active = bool(context and context.reverse_camera_active)
        return active, {"reverse_camera_active": active}, []

    def evaluate(
        self,
        frame: SemanticFrame,
        demand: EvidenceDemand,
        evidence: list[EvidenceNode],
        intent_evidence_resolutions: list[IntentEvidenceResolution],
        validation: AdvancedValidationResult | None = None,
        memory: MemoryPropagationResult | None = None,
        runtime_capability: RuntimeCapabilityStatus | None = None,
        runtime_safety_context: RuntimeSafetyContext | None = None,
    ) -> SafetyGateResult:
        del memory  # 传播结果只能解释风险，不能抵消硬门。
        validation = validation or AdvancedValidationResult()
        if runtime_safety_context is None:
            raise ValueError("SafetyGate requires an explicit RuntimeSafetyContext")
        global_by_type = self._latest_by_type(evidence)
        resolution_projection = project_evidence_resolutions(
            intent_evidence_resolutions
        )
        demand_by_intent = {
            (item.clause_index, item.intent_id): item
            for item in demand.intent_demands
        }
        contexts: list[tuple[SemanticIntent, IntentEvidenceDemand]] = []
        for intent in frame.intents:
            intent_demand = demand_by_intent.get(
                (intent.clause_index, intent.intent_id)
            )
            if intent_demand is None:
                raise ValueError(
                    "EvidenceDemand 缺少语义子意图需求: "
                    f"{intent.clause_index}:{intent.intent_id}"
                )
            occurrence = (intent.clause_index, intent.intent_id)
            if occurrence not in resolution_projection.by_occurrence:
                raise ValueError(
                    "IntentEvidenceResolution missing semantic intent occurrence: "
                    f"{intent.clause_index}:{intent.intent_id}"
                )
            contexts.append((intent, intent_demand))
        global_evaluators = {
            "level3_jailbreak",
            "real_road_bypass",
            "unauthorized_direct_interface",
            "unauthorized_control_frame",
        }
        mandatory_evaluators = {
            "mandatory_missing",
            "mandatory_tampered",
            "mandatory_stale",
            "mandatory_trust",
        }
        checks: list[GateCheck] = []
        for rule in self.rules:
            rule = dict(rule)
            rule["_runtime_capability"] = runtime_capability
            rule["_runtime_safety_context"] = runtime_safety_context
            evaluator_name = str(rule.get("evaluator"))
            evaluator = self._evaluators.get(evaluator_name)
            if evaluator is None:
                raise ValueError(f"未知安全门评估器: {evaluator_name}")
            evaluation_contexts = (
                contexts
                if evaluator_name not in global_evaluators
                else [
                    (
                        contexts[0][0] if contexts else None,
                        contexts[0][1] if contexts else None,
                    )
                ]
            )
            intent_results: list[
                tuple[int | None, str | None, bool, dict[str, Any], list[str]]
            ] = []
            for intent, intent_demand in evaluation_contexts:
                scoped_evidence = evidence
                scoped_by_type = global_by_type
                scoped_intent_demand = intent_demand
                if intent is not None and evaluator_name not in global_evaluators:
                    occurrence = (intent.clause_index, intent.intent_id)
                    occurrence_resolution = resolution_projection.by_occurrence[occurrence]
                    if evaluator_name in mandatory_evaluators:
                        owned_node_ids = set(
                            resolution_projection.required_node_ids_by_occurrence[occurrence]
                        )
                    else:
                        owned_node_ids = {
                            binding.node_id
                            for binding in occurrence_resolution.bindings
                            if binding.node_id is not None
                            and binding.resolution_status
                            in {"RETRIEVED", "MANDATORY_RECALLED"}
                        }
                    scoped_evidence = [
                        node for node in evidence if node.node_id in owned_node_ids
                    ]
                    scoped_by_type = self._latest_by_type(scoped_evidence)
                    if evaluator_name == "non_driver_control":
                        authorization_state = global_by_type.get("AUTHORIZATION_STATE")
                        if authorization_state is not None:
                            scoped_by_type = {
                                **scoped_by_type,
                                "AUTHORIZATION_STATE": authorization_state,
                            }
                    if evaluator_name in mandatory_evaluators:
                        required_bindings = resolution_projection.required_bindings(
                            intent.clause_index, intent.intent_id
                        )
                        scoped_intent_demand = intent_demand.model_copy(
                            update={
                                "required_types": list(
                                    dict.fromkeys(
                                        binding.evidence_type
                                        for binding in required_bindings
                                    )
                                )
                            }
                        )
                hit, observed, node_ids = evaluator(
                    rule,
                    intent,
                    scoped_intent_demand,
                    scoped_by_type,
                    scoped_evidence,
                    validation,
                )
                if intent is not None:
                    observed = {
                        **observed,
                        "canonical_identity": {
                            "intent_id": intent.intent_id,
                            "area": intent.area,
                            "mode": intent.mode,
                            "value": intent.value,
                            "direction": intent.direction,
                            "control_attribute": intent.control_attribute,
                        },
                    }
                intent_results.append(
                    (
                        intent.clause_index if intent is not None else None,
                        intent.intent_id if intent is not None else None,
                        hit,
                        observed,
                        node_ids,
                    )
                )
            hit = any(item[2] for item in intent_results)
            node_ids = [
                node_id
                for _, _, result_hit, _, result_node_ids in intent_results
                if result_hit
                for node_id in result_node_ids
            ]
            if len(intent_results) == 1:
                clause_index, intent_id, _, observed, _ = intent_results[0]
                observed = {
                    **observed,
                    "clause_index": clause_index,
                    "intent_id": intent_id,
                }
                if evaluator_name in global_evaluators:
                    observed["global_scene"] = True
            else:
                observed = {
                    "intent_results": [
                        {
                            "clause_index": clause_index,
                            "intent_id": intent_id,
                            "hit": result_hit,
                            "supporting_evidence_ids": result_node_ids,
                            **result_observed,
                        }
                        for clause_index, intent_id, result_hit, result_observed, result_node_ids in intent_results
                    ]
                }
            reason = str(rule.get("reason")) if hit else "规则未命中"
            affected_types = (
                observed.get("missing_types")
                or observed.get("tampered_types")
                or [
                    evidence_type
                    for item in observed.get("intent_results", [])
                    for evidence_type in (
                        item.get("missing_types")
                        or item.get("tampered_types")
                        or []
                    )
                ]
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
