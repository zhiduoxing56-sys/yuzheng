from __future__ import annotations

from typing import Any

from app.models.schemas import (
    AdvancedValidationResult,
    CausalCorrectionResult,
    DecisionLabel,
    DecisionResult,
    DecisionScoreFactors,
    DecisionSource,
    EvidenceNode,
    EvidenceQualityMetrics,
    EvidenceStatus,
    IntentSafetyAssessment,
    MemoryPropagationResult,
    RuntimeCapabilityStatus,
    SafetyGateResult,
    ScoreFactor,
    SemanticControlMode,
    SemanticFrame,
)
from app.services.decision.merge import EvidenceAlignmentRoute, merge_decision
from app.services.evidence.resolution import EvidenceResolutionProjection, OccurrenceKey
from app.services.evidence.trust import (
    PDF_EVIDENCE_TRUST_VALUES,
    evidence_trust_value,
    select_canonical_evidence,
    trust_trace,
)
from app.services.evidence.value_contract import is_finite_number


class DecisionService:
    """五维动态安全评分，并通过统一入口合并硬门与 EAS 路由。"""

    def __init__(self, config: dict[str, Any]) -> None:
        self.weights = {
            key: float(value) for key, value in config["five_factor_weights"].items()
        }
        self.thresholds = config["thresholds"]
        configured_trust_mapping = {
            key: float(value) for key, value in config["evidence_trust_mapping"].items()
        }
        expected_trust_mapping = {
            status.value: value for status, value in PDF_EVIDENCE_TRUST_VALUES.items()
        }
        if configured_trust_mapping != expected_trust_mapping:
            raise ValueError("evidence_trust_mapping 必须严格匹配 PDF 公式 2.11")
        self.semantic_ambiguity_beta = float(config["semantic_ambiguity_beta"])
        self.semantic_ambiguity_beta_source = str(
            config["semantic_ambiguity_beta_source"]
        )
        self.necessity = config["necessity_evidence"]
        if abs(sum(self.weights.values()) - 1.0) > 1e-9:
            raise ValueError("五维评分权重之和必须为 1")
        if self.weights["Cnec"] > 0.025 + 1e-9:
            raise ValueError("Cnec 权重不得超过 0.025")
        if self.weights["Cnec"] > self.weights["Cjb"] * 0.1 + 1e-9:
            raise ValueError("Cnec 权重不得超过 Cjb 权重的十分之一")

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def aggregate_safety_decision(
        assessments: list[IntentSafetyAssessment],
    ) -> DecisionLabel | None:
        """Conservatively aggregate resolved occurrence safety outcomes."""
        if not assessments:
            return None
        priority = {
            DecisionLabel.PASS: 0,
            DecisionLabel.REVIEW: 1,
            DecisionLabel.BLOCK: 2,
        }
        return max(
            (assessment.final_safety_decision for assessment in assessments),
            key=lambda decision: priority[decision],
        )

    def _trust(
        self,
        validated_types: list[str],
        evidence: list[EvidenceNode],
        resolved_node_ids: frozenset[str],
    ) -> tuple[float | None, bool, str, list[dict[str, object]]]:
        nodes = select_canonical_evidence(
            validated_types, evidence, allowed_node_ids=resolved_node_ids
        )
        if not nodes:
            return None, False, "无适用 validated evidence，可信因子不适用", []
        value = sum(evidence_trust_value(node.quality_label) for node in nodes) / len(nodes)
        return (
            self._clamp(value),
            True,
            "PDF 公式 2.14：validated evidence 的 Q(status) 算术平均值",
            trust_trace(nodes),
        )

    @staticmethod
    def _truthy(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).upper() in {"TRUE", "1", "YES", "ACTIVE", "DETECTED"}

    @staticmethod
    def _field(node: EvidenceNode | None, name: str) -> Any:
        if node is None or not isinstance(node.value, dict):
            return None
        return node.value.get(name)

    def _necessity_score(
        self, frame: SemanticFrame, evidence: list[EvidenceNode]
    ) -> tuple[float, str]:
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

        emergency_node = latest.get("SERVICE_BRAKE_STATE")
        emergency_value = self._field(emergency_node, "emergency_braking_detected")
        emergency_score = (
            float(self.necessity.get("emergency_flag_score", 1.0))
            if emergency_node is not None and self._truthy(emergency_value)
            else 0.0
        )
        collision_node = latest.get("SURROUNDING_OBJECT_STATE")
        collision_value = self._field(collision_node, "collision_state")
        collision_states = {
            str(value).upper() for value in self.necessity.get("collision_states", [])
        }
        collision_supported = collision_node is not None and (
            self._truthy(collision_value)
            or str(collision_value).upper() in collision_states
        )
        if collision_supported:
            emergency_score = max(
                emergency_score,
                float(self.necessity.get("collision_state_score", 1.0)),
            )

        critical_intents = self.necessity.get("safety_critical_intent_ids", {})
        intent_cap = max(
            (
                float(critical_intents.get(intent.intent_id, 0.0))
                for intent in frame.intents
            ),
            default=0.0,
        )
        safety_evidence_score = 0.0
        evidence_reasons: list[str] = []
        if intent_cap > 0:
            obstacle = latest.get("SURROUNDING_OBJECT_STATE")
            obstacle_value = self._field(obstacle, "front_obstacle_distance")
            threshold = float(self.necessity.get("front_obstacle_threshold_m", 5.0))
            if (
                obstacle is not None
                and is_finite_number(obstacle_value)
                and obstacle_value <= threshold
            ):
                safety_evidence_score = max(
                    safety_evidence_score,
                    float(self.necessity.get("front_obstacle_score", 0.9)),
                )
                evidence_reasons.append("前方障碍距离达到制动必要性阈值")
            brake = latest.get("SERVICE_BRAKE_STATE")
            brake_value = self._field(brake, "brake_state")
            required_states = {
                str(value).upper()
                for value in self.necessity.get("brake_required_states", [])
            }
            if brake is not None and str(brake_value).upper() in required_states:
                safety_evidence_score = max(
                    safety_evidence_score,
                    float(self.necessity.get("brake_required_score", 0.9)),
                )
                evidence_reasons.append("制动状态表明存在安全必要性")
        safety_critical_score = intent_cap * safety_evidence_score
        score = self._clamp(max(emergency_score, safety_critical_score))
        reasons = []
        if emergency_score > 0:
            reasons.append("真实紧急或碰撞证据支持")
        reasons.extend(evidence_reasons)
        if not reasons:
            reasons.append("没有真实紧急、碰撞、障碍或制动必要性证据")
        return score, "；".join(reasons)

    @staticmethod
    def _gate_slice(gate: SafetyGateResult, key: OccurrenceKey) -> SafetyGateResult:
        """Project the canonical turn gate into one occurrence without re-evaluating it."""
        selected: list[Any] = []
        for check in gate.checks:
            observed = check.observed
            if observed.get("global_scene"):
                selected.append(check)
                continue
            intent_results = observed.get("intent_results")
            if isinstance(intent_results, list):
                item = next(
                    (
                        value
                        for value in intent_results
                        if value.get("clause_index") == key[0]
                        and value.get("intent_id") == key[1]
                    ),
                    None,
                )
                if item is not None and item.get("hit"):
                    item_observed = dict(item)
                    item_observed.pop("hit", None)
                    item_observed.pop("supporting_evidence_ids", None)
                    selected.append(
                        check.model_copy(
                            update={
                                "observed": item_observed,
                                "supporting_evidence_ids": list(
                                    item.get("supporting_evidence_ids", [])
                                ),
                            }
                        )
                    )
                continue
            if (
                check.hit
                and observed.get("clause_index") == key[0]
                and observed.get("intent_id") == key[1]
            ):
                selected.append(check)
        reasons: list[str] = []
        for check in selected:
            if check.reason not in reasons:
                reasons.append(check.reason)
        hit_rules = [check.rule_id for check in selected if check.hit]
        return SafetyGateResult(
            blocked=bool(hit_rules),
            gate_blocked=bool(hit_rules),
            mandatory_evidence_missing="MANDATORY_EVIDENCE_AVAILABLE" in hit_rules,
            checks=selected,
            reasons=reasons,
            hit_rules=hit_rules,
            observed_values={check.rule_id: check.observed for check in selected},
            supporting_evidence_ids=sorted(
                {
                    node_id
                    for check in selected
                    for node_id in check.supporting_evidence_ids
                }
            ),
        )

    def assess_intents(
        self,
        frame: SemanticFrame,
        evidence: list[EvidenceNode],
        gate: SafetyGateResult,
        validation: AdvancedValidationResult,
        causal: CausalCorrectionResult,
        memory: MemoryPropagationResult,
        runtime_capability: RuntimeCapabilityStatus | None,
        resolution_projection: EvidenceResolutionProjection,
        quality_metrics_by_occurrence: dict[OccurrenceKey, EvidenceQualityMetrics],
    ) -> tuple[list[IntentSafetyAssessment], DecisionLabel | None]:
        assessments: list[IntentSafetyAssessment] = []
        for intent in frame.intents:
            key = (intent.clause_index, intent.intent_id)
            metrics = quality_metrics_by_occurrence.get(key)
            if metrics is None or key not in resolution_projection.by_occurrence:
                continue
            occurrence_gate = self._gate_slice(gate, key)
            scoped_frame = frame.model_copy(
                update={
                    "intents": [intent],
                    "semantic_status": "OK",
                    "semantic_confidence": intent.semantic_confidence,
                    "ambiguity_score": intent.ambiguity_score,
                }
            )
            score_result = self.decide(
                scoped_frame,
                evidence,
                occurrence_gate,
                metrics.evidence_alignment_route or "EVIDENCE_PASS",
                validation,
                causal,
                memory,
                runtime_capability,
                required_types=resolution_projection.required_types_by_occurrence[key],
                validated_types=resolution_projection.validated_types_by_occurrence[key],
                required_node_ids=resolution_projection.required_node_ids_by_occurrence[key],
                resolved_node_ids=resolution_projection.resolved_node_ids_by_occurrence[key],
            )
            assessments.append(
                IntentSafetyAssessment(
                    clause_index=intent.clause_index,
                    intent_id=intent.intent_id,
                    quality_metrics=metrics,
                    gate_blocked=occurrence_gate.blocked,
                    gate_hit_rules=occurrence_gate.hit_rules,
                    gate_reasons=occurrence_gate.reasons,
                    gate_observed=occurrence_gate.observed_values,
                    supporting_evidence_ids=occurrence_gate.supporting_evidence_ids,
                    score_factors=score_result.score_factors,
                    safety_score=score_result.safety_score,
                    score_decision=score_result.score_decision,
                    final_safety_decision=score_result.final_decision,
                    decision_sources=score_result.decision_sources,
                    decision_merge_reason=score_result.decision_merge_reason,
                    reason_codes=score_result.reason_codes,
                    explanations=score_result.explanations,
                )
            )
        if not assessments:
            return [], None
        return assessments, self.aggregate_safety_decision(assessments)

    def decide(
        self,
        frame: SemanticFrame,
        evidence: list[EvidenceNode],
        gate: SafetyGateResult,
        evidence_alignment_route: EvidenceAlignmentRoute,
        validation: AdvancedValidationResult | None = None,
        causal: CausalCorrectionResult | None = None,
        memory: MemoryPropagationResult | None = None,
        runtime_capability: RuntimeCapabilityStatus | None = None,
        *,
        required_types: list[str],
        validated_types: list[str],
        required_node_ids: frozenset[str],
        resolved_node_ids: frozenset[str],
    ) -> DecisionResult:
        validation = validation or AdvancedValidationResult()
        causal = causal or CausalCorrectionResult()
        occurrence_evidence = [
            node for node in evidence if node.node_id in resolved_node_ids
        ]
        incomplete = frame.semantic_status != "OK"
        csem = self._clamp(
            frame.semantic_confidence
            * (1.0 - self.semantic_ambiguity_beta * frame.ambiguity_score)
        )
        required_count = len(required_types)
        covered = {
            node.evidence_type
            for node in evidence
            if node.node_id in required_node_ids
            and node.quality_label in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
        }
        ccov = len(covered) / required_count if required_count else None
        ctrust, trust_applicable, trust_reason, validated_trust_values = self._trust(
            validated_types, evidence, resolved_node_ids
        )
        cjb = self._clamp(1.0 - validation.jailbreak_risk)
        cnec, necessity_reason = self._necessity_score(frame, evidence)
        critical_intents = self.necessity.get("safety_critical_intent_ids", {})
        cnec_applicable = any(
            float(critical_intents.get(intent.intent_id, 0.0)) > 0
            for intent in frame.intents
        )

        values: dict[str, tuple[float | None, bool, str]] = {
            "Csem": (csem, True, "语义置信度经歧义惩罚"),
            "Ccov": (ccov, ccov is not None, "有效或可疑强制证据覆盖率"),
            "Ctrust": (ctrust, trust_applicable, trust_reason),
            "Cjb": (cjb, True, "1 减越狱风险"),
            "Cnec": (
                cnec if cnec_applicable else None,
                cnec_applicable,
                f"Cnec=max(emergency_score,safety_critical_score)：{necessity_reason}；紧急措辞不计入",
            ),
        }
        if incomplete:
            # 模糊指令只计算语义质量，保持 diagnostic_only 且不从无关证据获益。
            values = {
                name: (value, name == "Csem", reason)
                for name, (value, _, reason) in values.items()
            }
        active_total = sum(
            self.weights[name] for name, (_, applicable, _) in values.items() if applicable
        )
        factors: dict[str, ScoreFactor] = {}
        score = 0.0
        for name, (value, applicable, reason) in values.items():
            actual_weight = self.weights[name] / active_total if applicable and active_total else 0.0
            contribution = actual_weight * float(value or 0.0)
            score += contribution
            factors[name] = ScoreFactor(
                name=name,
                value=round(value, 6) if value is not None else None,
                applicable=applicable,
                configured_weight=self.weights[name],
                actual_weight=round(actual_weight, 6),
                contribution=round(contribution, 6),
                reason=reason,
            )
        score = round(self._clamp(score), 4)

        explanations = [
            "识别子意图="
            + ",".join(
                f"{intent.intent_id}({intent.action}|{intent.target})"
                for intent in frame.intents
            ),
            (
                f"强制证据覆盖 {len(covered)}/{required_count}"
                if required_count
                else "当前指令无强制证据需求"
            ),
            f"越狱风险={validation.jailbreak_risk:.4f}，冲突数={validation.conflict_count}",
            f"因果样本={causal.sample_count}，数据充分性={causal.data_sufficiency}",
        ]
        review_question: str | None = None
        if incomplete:
            score_decision = DecisionLabel.REVIEW
            if len(frame.intents) > 1:
                explanations.append("当前执行与授权接口仍为单动作契约，多子意图轮次仅允许复核")
            else:
                explanations.append(
                    "冻结语义状态为"
                    f"{frame.semantic_status}，仅允许诊断或复核流程"
                )
            review_question = "请根据语义复核原因确认或重新描述指令。"
        elif validation.conflicts or any(
            node.quality_label == EvidenceStatus.SUSPICIOUS
            for node in occurrence_evidence
        ):
            score_decision = DecisionLabel.REVIEW if score >= float(self.thresholds["review"]) else DecisionLabel.BLOCK
            explanations.append("存在声明或多源证据冲突，不能直接放行")
            if score_decision == DecisionLabel.REVIEW:
                review_question = "检测到声明或车辆状态不一致，请确认真实状态后再执行。"
        elif score >= float(self.thresholds["pass"]):
            score_decision = DecisionLabel.PASS
            explanations.append("五维评分达到放行阈值")
        elif score >= float(self.thresholds["review"]):
            score_decision = DecisionLabel.REVIEW
            explanations.append("五维评分处于复核区间")
            review_question = "请确认是否继续执行该指令。"
        else:
            score_decision = DecisionLabel.BLOCK
            explanations.append("五维评分低于阻断阈值")

        reason_codes = list(gate.hit_rules)
        restricted_formal = (
            runtime_capability is not None
            and runtime_capability.semantic_control_mode != SemanticControlMode.FULL
            and bool(frame.intents)
            and all(
                intent.runtime_identity == "FORMAL"
                for intent in frame.intents
            )
        )
        review_constraints: list[DecisionSource] = []
        if restricted_formal and not gate.blocked and score_decision == DecisionLabel.PASS:
            review_constraints.append(DecisionSource.RUNTIME_CAPABILITY)
            review_question = "真实语义模型当前不可用，请恢复模型后重新确认该车控指令。"
            reason_codes.append("SEMANTIC_MODEL_DEGRADED_REVIEW_REQUIRED")
            explanations.append("真实语义模型降级：R1/R2可执行车控最高只能进入复核")

        merged = merge_decision(
            gate,
            evidence_alignment_route,
            score_decision,
            review_constraints=review_constraints,
        )
        if gate.blocked:
            explanations.extend(gate.reasons)
            explanations.append("硬性安全门优先于证据路由和五维评分，其他证据不能抵消风险")
            explanations.append("五维评分仅作为硬规则阻断后的诊断评分，不参与最终裁决")
        explanations.append(merged.decision_merge_reason)
        if merged.final_decision == DecisionLabel.REVIEW and review_question is None:
            review_question = "证据对齐结果需要人工复核，请确认是否继续执行该指令。"
        elif merged.final_decision == DecisionLabel.BLOCK:
            review_question = None

        decision_confidence = causal.decision_confidence
        return DecisionResult(
            turn_id=frame.turn_id,
            decision=score_decision,
            score_decision=score_decision,
            final_decision=merged.final_decision,
            decision_sources=list(merged.decision_sources),
            decision_merge_reason=merged.decision_merge_reason,
            safety_score=score,
            soft_safety_score=score,
            gate_blocked=gate.blocked,
            gate_reasons=gate.reasons,
            score_evaluation_mode=("diagnostic_after_gate" if gate.blocked else "normal"),
            score_factors=DecisionScoreFactors(
                semantic_quality=round(csem, 4),
                evidence_coverage=round(ccov, 4) if ccov is not None else None,
                evidence_coverage_applicable=ccov is not None,
                applied_weights={
                    "semantic_quality": factors["Csem"].actual_weight,
                    "evidence_coverage": factors["Ccov"].actual_weight,
                },
                five_factors=factors,
                semantic_confidence=frame.semantic_confidence,
                ambiguity_penalty=frame.ambiguity_score,
                semantic_ambiguity_beta=self.semantic_ambiguity_beta,
                beta_source=self.semantic_ambiguity_beta_source,
                validated_evidence_count=len(validated_trust_values),
                validated_trust_values=validated_trust_values,
                trust_formula="Ctrust=mean(Q(status)) over canonical Evalidated",
                trust_value_source="REPORT_EXPLICIT:PDF_FORMULA_2_14",
            ),
            explanations=explanations,
            review_question=review_question,
            jailbreak_risk=validation.jailbreak_risk,
            decision_confidence=decision_confidence,
            reason_codes=sorted(set(reason_codes)),
            causal_correction=causal,
            memory_propagation=memory,
            grounding_failures=validation.grounding_failures,
            conflicts=validation.conflicts,
        )
