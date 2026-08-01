from __future__ import annotations

from typing import Any

from app.models.schemas import (
    AdvancedValidationResult,
    CausalCorrectionResult,
    DecisionLabel,
    DecisionResult,
    DecisionScoreFactors,
    EvidenceNode,
    EvidenceStatus,
    MemoryPropagationResult,
    SafetyGateResult,
    ScoreFactor,
    SemanticFrame,
)


class DecisionService:
    """五维动态安全评分；硬性安全门在评分之后独立覆盖最终裁决。"""

    def __init__(self, config: dict[str, Any]) -> None:
        self.weights = {
            key: float(value) for key, value in config["five_factor_weights"].items()
        }
        self.thresholds = config["thresholds"]
        self.trust_mapping = {
            key: float(value) for key, value in config["evidence_trust_mapping"].items()
        }
        self.necessity = {
            key: float(value) for key, value in config["safety_necessity_by_risk"].items()
        }
        if abs(sum(self.weights.values()) - 1.0) > 1e-9:
            raise ValueError("五维评分权重之和必须为 1")
        if self.weights["Cnec"] > self.weights["Cjb"] / 5 + 1e-9:
            raise ValueError("Cnec 权重不得超过 Cjb 权重的五分之一")

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))

    def _trust(
        self,
        evidence: list[EvidenceNode],
        causal: CausalCorrectionResult,
    ) -> tuple[float | None, bool, str]:
        latest: dict[str, EvidenceNode] = {}
        for node in evidence:
            if node.mandatory:
                latest[node.evidence_type] = node
        nodes = [latest[key] for key in sorted(latest)]
        if not nodes:
            return None, False, "无强制证据，可信因子不适用"
        causal_weights = {
            node.node_id: causal.corrected_weights.get(node.node_id, 0.0) for node in nodes
        }
        causal_total = sum(causal_weights.values())
        if causal_total > 0:
            value = sum(
                self.trust_mapping[node.quality_label.value]
                * causal_weights[node.node_id]
                / causal_total
                for node in nodes
            )
            reason = "校验状态可信度按因果后验权重加权"
        else:
            value = sum(
                self.trust_mapping[node.quality_label.value] for node in nodes
            ) / len(nodes)
            reason = "历史不足，使用校验状态可信度均值"
        return self._clamp(value), True, reason

    def decide(
        self,
        frame: SemanticFrame,
        evidence: list[EvidenceNode],
        gate: SafetyGateResult,
        validation: AdvancedValidationResult | None = None,
        causal: CausalCorrectionResult | None = None,
        memory: MemoryPropagationResult | None = None,
    ) -> DecisionResult:
        validation = validation or AdvancedValidationResult()
        causal = causal or CausalCorrectionResult()
        incomplete = frame.action == "unknown" or frame.target == "unknown"
        csem = self._clamp(frame.semantic_confidence * (1.0 - frame.ambiguity_score))
        required_count = len(frame.required_evidence_types)
        covered = {
            node.evidence_type
            for node in evidence
            if node.mandatory
            and node.quality_label in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
        }
        ccov = len(covered) / required_count if required_count else None
        ctrust, trust_applicable, trust_reason = self._trust(evidence, causal)
        cjb = self._clamp(1.0 - validation.jailbreak_risk)
        emergency_supported = any(
            node.evidence_type == "emergency_flag" and bool(node.value)
            for node in evidence
        )
        safety_necessity = self.necessity.get(frame.risk_level, 0.2)
        emergency_necessity = 1.0 if emergency_supported else 0.0
        cnec = max(safety_necessity, emergency_necessity)

        values: dict[str, tuple[float | None, bool, str]] = {
            "Csem": (csem, True, "语义置信度经歧义惩罚"),
            "Ccov": (ccov, ccov is not None, "有效或可疑强制证据覆盖率"),
            "Ctrust": (ctrust, trust_applicable, trust_reason),
            "Cjb": (cjb, True, "1 减越狱风险"),
            "Cnec": (
                cnec,
                True,
                "取真实紧急证据与动作安全必要性的较大值；紧急措辞不计入",
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
            f"识别动作={frame.action}，对象={frame.target}",
            (
                f"强制证据覆盖 {len(covered)}/{required_count}"
                if required_count
                else "当前指令无强制证据需求"
            ),
            f"越狱风险={validation.jailbreak_risk:.4f}，冲突数={validation.conflict_count}",
            f"因果样本={causal.sample_count}，数据充分性={causal.data_sufficiency}",
        ]
        review_question: str | None = None
        if gate.blocked:
            decision = DecisionLabel.BLOCK
            explanations.extend(gate.reasons)
            explanations.append("硬性安全门优先于五维软评分，其他证据不能抵消风险")
        elif incomplete:
            decision = DecisionLabel.REVIEW
            missing_slot = (
                "动作和对象"
                if frame.action == frame.target == "unknown"
                else "动作"
                if frame.action == "unknown"
                else "目标对象"
            )
            explanations.append(f"语义帧缺少{missing_slot}，仅允许诊断检索")
            review_question = (
                "您想打开哪个设备？请明确说出车门、车窗、灯光或其他目标。"
                if frame.action == "打开" and frame.target == "unknown"
                else f"请明确指令的{missing_slot}。"
            )
        elif validation.conflicts or any(
            node.quality_label == EvidenceStatus.SUSPICIOUS for node in evidence
        ):
            decision = DecisionLabel.REVIEW if score >= float(self.thresholds["review"]) else DecisionLabel.BLOCK
            explanations.append("存在声明或多源证据冲突，不能直接放行")
            if decision == DecisionLabel.REVIEW:
                review_question = "检测到声明或车辆状态不一致，请确认真实状态后再执行。"
        elif score >= float(self.thresholds["pass"]):
            decision = DecisionLabel.PASS
            explanations.append("五维评分达到放行阈值且未命中硬门")
        elif score >= float(self.thresholds["review"]):
            decision = DecisionLabel.REVIEW
            explanations.append("五维评分处于复核区间")
            review_question = "请确认是否继续执行该指令。"
        else:
            decision = DecisionLabel.BLOCK
            explanations.append("五维评分低于阻断阈值")

        decision_confidence = causal.decision_confidence
        return DecisionResult(
            turn_id=frame.turn_id,
            decision=decision,
            final_decision=decision,
            safety_score=score,
            soft_safety_score=score,
            gate_blocked=gate.blocked,
            gate_reasons=gate.reasons,
            score_factors=DecisionScoreFactors(
                semantic_quality=round(csem, 4),
                evidence_coverage=round(ccov, 4) if ccov is not None else None,
                evidence_coverage_applicable=ccov is not None,
                applied_weights={
                    "semantic_quality": factors["Csem"].actual_weight,
                    "evidence_coverage": factors["Ccov"].actual_weight,
                },
                five_factors=factors,
            ),
            explanations=explanations,
            review_question=review_question,
            jailbreak_risk=validation.jailbreak_risk,
            decision_confidence=decision_confidence,
            causal_correction=causal,
            memory_propagation=memory,
            grounding_failures=validation.grounding_failures,
            conflicts=validation.conflicts,
        )
