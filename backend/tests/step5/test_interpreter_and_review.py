from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config import load_yaml
from app.models.frontend_contract import ReviewSubmission
from app.models.schemas import (
    CausalCorrectionResult,
    DecisionLabel,
    DecisionResult,
    DecisionScoreFactors,
    DecisionSource,
    EvidenceNode,
    EvidenceStatus,
    ReviewAction,
    ReviewRequest,
    SafetyGateResult,
    SecurityClass,
    TextCommandRequest,
    VehicleStatePatch,
    utc_now,
)
from app.services.evidence.demand import EvidenceDemandService
from app.services.interpreter.service import InterpreterService
from app.services.semantic.parser import SemanticFrameParser


class StaticProvider:
    name = "TEST_PROVIDER"
    model = "test-model"

    def __init__(self, output: dict[str, Any] | Exception) -> None:
        self.output = output
        self.payload: dict[str, Any] | None = None
        self.system_prompt: str | None = None

    def generate(self, system_prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.system_prompt = system_prompt
        self.payload = payload
        if isinstance(self.output, Exception):
            raise self.output
        return self.output


def _components(provider=None):
    parser = SemanticFrameParser(load_yaml("semantic_rules.yaml"))
    demand = EvidenceDemandService(load_yaml("action_evidence_map.yaml"))
    service = InterpreterService(
        load_yaml("interpreter.yaml"), parser, demand, provider=provider
    )
    return parser, service


def _decision(turn_id: str, label: DecisionLabel = DecisionLabel.REVIEW) -> DecisionResult:
    return DecisionResult(
        turn_id=turn_id,
        decision=label,
        score_decision=label,
        final_decision=label,
        decision_sources=[DecisionSource.SAFETY_SCORE],
        decision_merge_reason="controlled deterministic decision",
        safety_score=0.7,
        soft_safety_score=0.7,
        gate_blocked=False,
        score_factors=DecisionScoreFactors(
            semantic_quality=0.8,
            evidence_coverage=0.8,
            evidence_coverage_applicable=True,
        ),
    )


def _evidence(node_id: str = "NODE_VALID") -> EvidenceNode:
    timestamp = utc_now()
    return EvidenceNode(
        node_id=node_id,
        evidence_type="music_state",
        layer="L0_ENTERTAINMENT",
        source="vehicle_state",
        value="STOPPED",
        timestamp=timestamp,
        expires_at=timestamp + timedelta(minutes=1),
        freshness=1,
        consistency=1,
        availability=1,
        semantic_similarity=0.9,
        mandatory=False,
        quality_label=EvidenceStatus.VALID,
        integrity_hash="hash-music",
        security_class=SecurityClass.ENTERTAINMENT,
        security_rank=0,
        security_classification_source="EXISTING_PROJECT_MAPPING",
    )


def _generate(service: InterpreterService, parser: SemanticFrameParser, text: str = "可能播放音乐"):
    frame = parser.parse("TURN_INTERPRETER", text)
    decision = _decision(frame.turn_id)
    return decision, service.generate(
        frame=frame,
        evidence=[_evidence()],
        missing_types=[],
        gate=SafetyGateResult(blocked=False, checks=[], reasons=[]),
        decision=decision,
        causal=CausalCorrectionResult(
            confidence_status="INSUFFICIENT_HISTORY",
            sample_count=0,
        ),
        decision_sources=[source.value for source in decision.decision_sources],
        decision_merge_reason=decision.decision_merge_reason,
    )


def test_unconfigured_provider_uses_structured_deterministic_fallback() -> None:
    parser, service = _components(provider=None)
    decision, result = _generate(service, parser)
    assert result.generation_metadata.generation_mode == "DETERMINISTIC_FALLBACK"
    assert result.generation_metadata.provider_status == "NOT_CONFIGURED"
    assert result.generation_metadata.fallback_reason == "PROVIDER_NOT_CONFIGURED"
    assert result.decision_explanation.decision_label == decision.final_decision
    assert result.decision_explanation.evidence_citations[0].node_id == "NODE_VALID"
    assert result.review_question
    assert result.validation_result["decision_unchanged"] is True


@pytest.mark.parametrize(
    "provider_output, expected_reason",
    [
        (TimeoutError("timeout"), "TimeoutError"),
        ({"not": "valid json schema"}, "ValueError"),
        (
            {
                "summary": "attempt control",
                "decision_label": "REVIEW",
                "final_decision": "PASS",
            },
            "ValueError",
        ),
        (
            {
                "summary": "bad citation",
                "decision_label": "REVIEW",
                "evidence_citations": [{"node_id": "OTHER_TURN", "reason": "fake"}],
            },
            "ValueError",
        ),
    ],
)
def test_provider_failure_or_control_attempt_falls_back_without_changing_decision(
    provider_output, expected_reason: str
) -> None:
    provider = StaticProvider(provider_output)
    parser, service = _components(provider=provider)
    frame = parser.parse("TURN_INTERPRETER", "可能播放音乐")
    decision = _decision(frame.turn_id)
    before = decision.model_dump(mode="json")
    result = service.generate(
        frame=frame,
        evidence=[_evidence()],
        missing_types=[],
        gate=SafetyGateResult(blocked=False, checks=[], reasons=[]),
        decision=decision,
        causal=CausalCorrectionResult(confidence_status="INSUFFICIENT_HISTORY"),
        decision_sources=[source.value for source in decision.decision_sources],
        decision_merge_reason=decision.decision_merge_reason,
    )
    assert decision.model_dump(mode="json") == before
    assert result.generation_metadata.generation_mode == "DETERMINISTIC_FALLBACK"
    assert result.generation_metadata.provider_status == "FAILED_FALLBACK"
    assert result.generation_metadata.fallback_reason == expected_reason
    assert result.decision_explanation.decision_label == DecisionLabel.REVIEW


def test_provider_receives_bounded_structured_context_without_audio_vectors_or_tokens() -> None:
    provider = StaticProvider(
        {
            "summary": "review explanation",
            "decision_label": "REVIEW",
            "decision_basis": ["deterministic decision"],
            "evidence_citations": [{"node_id": "NODE_VALID", "reason": "current evidence"}],
            "candidate_texts": ["播放音乐"],
        }
    )
    parser, service = _components(provider=provider)
    decision, result = _generate(service, parser)
    assert decision.final_decision == DecisionLabel.REVIEW
    assert result.generation_metadata.generation_mode == "LLM_INTERPRETER"
    assert result.generation_metadata.provider_status == "VERIFIED"
    assert provider.payload is not None
    serialized = str(provider.payload).lower()
    assert "query_vector" not in serialized
    assert "raw_audio" not in serialized
    assert "authorization" not in serialized
    assert "api_key" not in serialized
    assert "database_path" not in serialized
    assert "current evidence" not in serialized
    assert len(str(provider.payload)) <= service.maximum_input_characters


def test_unknown_provider_candidate_is_rejected_by_local_parser_and_demand_rules() -> None:
    provider = StaticProvider(
        {
            "summary": "unknown candidate",
            "decision_label": "REVIEW",
            "candidate_texts": ["发射导弹"],
        }
    )
    parser, service = _components(provider=provider)
    frame = parser.parse("TURN_UNKNOWN", "请帮我处理一下")
    decision = _decision(frame.turn_id)
    result = service.generate(
        frame=frame,
        evidence=[],
        missing_types=[],
        gate=SafetyGateResult(blocked=False, checks=[], reasons=[]),
        decision=decision,
        causal=CausalCorrectionResult(confidence_status="INSUFFICIENT_HISTORY"),
        decision_sources=[DecisionSource.SAFETY_SCORE.value],
        decision_merge_reason=decision.decision_merge_reason,
    )
    assert result.generation_metadata.generation_mode == "LLM_INTERPRETER"
    assert result.candidate_interpretations == []
    assert result.candidate_availability == "NO_VALID_CANDIDATES"
    assert result.recommended_recovery is not None
    assert result.recommended_recovery.recovery_code == "SUPPLY_ACTION_TARGET"


def test_candidate_ids_are_bound_to_turn_and_confirm_creates_full_child_turn(pipeline) -> None:
    first = pipeline.process_text(
        TextCommandRequest(
            text="可能播放音乐",
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
        )
    )
    assert first.decision.final_decision == DecisionLabel.REVIEW
    assert first.interpreter_result is not None
    assert len(first.interpreter_result.candidate_interpretations) == 1
    candidate = first.interpreter_result.candidate_interpretations[0]
    assert candidate.turn_id == first.turn_id

    second = pipeline.process_text(
        TextCommandRequest(
            text="可能播放音乐",
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
        )
    )
    other_candidate = second.interpreter_result.candidate_interpretations[0]
    rejected = pipeline.review_service.review(
        first.turn_id,
        ReviewRequest(
            action=ReviewAction.CONFIRM,
            selected_candidate_id=other_candidate.candidate_id,
        ),
    )
    assert rejected.accepted is False
    assert rejected.related_turn_id == first.turn_id

    confirmed = pipeline.review_service.review(
        first.turn_id,
        ReviewRequest(
            action=ReviewAction.CONFIRM,
            selected_candidate_id=candidate.candidate_id,
        ),
    )
    assert confirmed.accepted is True
    assert confirmed.command_result is not None
    assert confirmed.related_turn_id != first.turn_id
    assert confirmed.command_result.parent_turn_id == first.turn_id
    assert confirmed.command_result.root_turn_id == first.turn_id
    assert confirmed.command_result.semantic_frame.action == candidate.action
    assert confirmed.command_result.semantic_frame.target == candidate.target


def test_multiple_valid_provider_candidates_require_explicit_selection(pipeline) -> None:
    pipeline.interpreter_service.provider = StaticProvider(
        {
            "summary": "two locally valid interpretations",
            "decision_label": "REVIEW",
            "candidate_texts": ["打开车门", "打开自动泊车"],
        }
    )
    result = pipeline.process_text(
        TextCommandRequest(
            text="把那个打开",
            state_overrides=VehicleStatePatch(vehicle_speed=0, gear_position="P"),
        )
    )
    candidates = result.interpreter_result.candidate_interpretations
    assert [(item.action, item.target) for item in candidates] == [
        ("打开", "车门"),
        ("打开", "自动泊车"),
    ]
    rejected = pipeline.review_service.review(
        result.turn_id, ReviewRequest(action=ReviewAction.CONFIRM)
    )
    assert rejected.accepted is False
    assert "selected_candidate_id" in rejected.reason

    selected = candidates[0]
    confirmed = pipeline.review_service.review(
        result.turn_id,
        ReviewRequest(
            action=ReviewAction.CONFIRM,
            selected_candidate_id=selected.candidate_id,
        ),
    )
    assert confirmed.accepted is True
    assert confirmed.command_result is not None
    assert confirmed.command_result.parent_turn_id == result.turn_id
    assert confirmed.command_result.semantic_frame.action == selected.action
    assert confirmed.command_result.semantic_frame.target == selected.target


def test_public_review_contract_keeps_action_specific_strictness() -> None:
    assert ReviewSubmission(action=ReviewAction.CONFIRM, selected_candidate_id="CAND_1")
    with pytest.raises(ValidationError):
        ReviewSubmission(action=ReviewAction.CONFIRM)
    with pytest.raises(ValidationError):
        ReviewSubmission(
            action=ReviewAction.CONFIRM,
            corrected_text="播放音乐",
        )
    with pytest.raises(ValidationError):
        ReviewSubmission(action=ReviewAction.CORRECT)
    with pytest.raises(ValidationError):
        ReviewSubmission(
            action=ReviewAction.CORRECT,
            corrected_text="播放音乐",
            selected_candidate_id="CAND_1",
        )
    with pytest.raises(ValidationError):
        ReviewSubmission(action=ReviewAction.CANCEL, selected_candidate_id="CAND_1")
