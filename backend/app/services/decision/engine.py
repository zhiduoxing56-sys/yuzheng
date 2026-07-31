from __future__ import annotations

from typing import Any

from app.models.schemas import (
    DecisionLabel,
    DecisionResult,
    EvidenceNode,
    EvidenceStatus,
    SafetyGateResult,
    SemanticFrame,
)


class DecisionService:
    """阶段一简化评分：只使用语义质量与强制证据覆盖率；硬门始终优先。"""

    def __init__(self, config: dict[str, Any]) -> None:
        self.weights = config["stage_one_score_weights"]
        self.thresholds = config["thresholds"]
        if abs(sum(float(value) for value in self.weights.values()) - 1.0) > 1e-9:
            raise ValueError("阶段一评分权重之和必须为 1")

    def decide(
        self,
        frame: SemanticFrame,
        evidence: list[EvidenceNode],
        gate: SafetyGateResult,
    ) -> DecisionResult:
        semantic_quality = frame.semantic_confidence * (1.0 - frame.ambiguity_score)
        mandatory = [node for node in evidence if node.mandatory]
        usable = [
            node
            for node in mandatory
            if node.quality_label in {EvidenceStatus.VALID, EvidenceStatus.SUSPICIOUS}
        ]
        evidence_coverage = len(usable) / len(mandatory) if mandatory else 1.0
        score = (
            float(self.weights["semantic_quality"]) * semantic_quality
            + float(self.weights["evidence_coverage"]) * evidence_coverage
        )
        score = round(max(0.0, min(1.0, score)), 4)

        incomplete = frame.action == "unknown" or frame.target == "unknown"
        review_question: str | None = None
        explanations: list[str] = []
        if gate.blocked:
            decision = DecisionLabel.BLOCK
            explanations.extend(gate.reasons)
            explanations.append("硬性安全门优先于评分，其他证据不能抵消风险")
        elif incomplete:
            decision = DecisionLabel.REVIEW
            missing_slot = "动作和对象" if frame.action == frame.target == "unknown" else (
                "动作" if frame.action == "unknown" else "目标对象"
            )
            explanations.append(f"语义帧缺少{missing_slot}，不能生成可执行车控指令")
            review_question = (
                "您想打开哪个设备？请明确说出车门、车窗、灯光或其他目标。"
                if frame.action == "打开" and frame.target == "unknown"
                else f"请明确指令的{missing_slot}。"
            )
        elif score >= float(self.thresholds["pass"]):
            decision = DecisionLabel.PASS
            explanations.append("语义明确、强制证据完整且未命中阶段一硬性安全规则")
        elif score >= float(self.thresholds["review"]):
            decision = DecisionLabel.REVIEW
            explanations.append("安全分数处于复核区间")
            review_question = "请确认是否继续执行该指令。"
        else:
            decision = DecisionLabel.BLOCK
            explanations.append("安全分数低于阶段一阻断阈值")

        return DecisionResult(
            turn_id=frame.turn_id,
            decision=decision,
            safety_score=score,
            gate_blocked=gate.blocked,
            gate_reasons=gate.reasons,
            score_factors={
                "semantic_quality": round(semantic_quality, 4),
                "evidence_coverage": round(evidence_coverage, 4),
            },
            explanations=explanations,
            review_question=review_question,
        )
