from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.models.frontend_contract import ClarificationSubmission
from app.models.schemas import (
    ClarificationCandidate,
    ClarificationCandidateSource,
    ClarificationRequest,
    ClarificationResolution,
    ClarificationType,
    DecisionLabel,
    SemanticFrame,
    SemanticIntent,
    TranscriptionResult,
)
from app.services.clarification.service import (
    ClarificationService,
    ClarificationWorkflowError,
)
from app.services.workflow.repository import WorkflowRepository
from app.models.schemas import ClarificationResolutionRecord, WorkflowEventType


class FakeWorkflowRepository:
    def __init__(self) -> None:
        self.requests: dict[str, ClarificationRequest] = {}
        self.resolutions = {}
        self.events = []

    def clarification_for_turn(self, turn_id):
        return next((item for item in self.requests.values() if item.turn_id == turn_id), None)

    def get_clarification_request(self, clarification_id):
        return self.requests.get(clarification_id)

    def get_clarification_resolution(self, clarification_id):
        return self.resolutions.get(clarification_id)

    def save_clarification_request(self, request, *, root_turn_id, review_reasons):
        self.requests.setdefault(request.clarification_id, request)
        return self.requests[request.clarification_id]

    def save_clarification_resolution(self, resolution):
        created = resolution.clarification_id not in self.resolutions
        self.resolutions.setdefault(resolution.clarification_id, resolution)
        return self.resolutions[resolution.clarification_id], created

    def append_event(self, **event):
        self.events.append(event)
        return event


class FakePipeline:
    def __init__(self) -> None:
        self.workflow_repository = FakeWorkflowRepository()
        self.audit_repository = SimpleNamespace(get_by_turn=lambda _turn_id: None)
        self.process_calls = []

    def process_text(self, request, **kwargs):
        self.process_calls.append((request, kwargs))
        return SimpleNamespace(turn_id="TURN_CHILD")

    def trusted_context_from_audit(self, _record):
        return None

    def get_turn(self, _turn_id):
        return None


def make_record(
    *,
    text="待确认指令",
    status="REVIEW",
    reasons=None,
    review_candidates=None,
    intents=None,
    alternatives=None,
    audio=False,
):
    frame = SemanticFrame(
        turn_id="TURN_A",
        raw_text=text,
        normalized_text=text,
        semantic_confidence=0.5,
        ambiguity_score=0.5,
        semantic_status=status,
        review_reasons=reasons or [],
        review_candidates=review_candidates or [],
        unresolved_clauses=[text] if status != "OK" else [],
        intents=intents or [],
    )
    transcription = TranscriptionResult(
        turn_id="TURN_A",
        text=text,
        adapter="test",
        model_inference_performed=audio,
    )
    return SimpleNamespace(
        turn_id="TURN_A",
        root_turn_id="TURN_A",
        parent_turn_id=None,
        attempt_no=0,
        final_decision=SimpleNamespace(final_decision=DecisionLabel.REVIEW),
        semantic_frame=frame,
        transcription_result=transcription,
        input_trust_result=SimpleNamespace(
            audio_source="microphone" if audio else "text_api",
            speaker_zone="driver",
            speaker_role="driver",
        ),
        audio_input_metadata={"asr_nbest": alternatives or []},
        interpreter_review_question=None,
        candidate_interpretations=[],
        spectrum_analysis=None,
    )


def test_voice_nbest_is_deduplicated_sorted_and_capped_at_four():
    pipeline = FakePipeline()
    service = ClarificationService(pipeline, {})
    record = make_record(
        text="运动莫斯",
        audio=True,
        alternatives=[
            {"text": "运动模式", "confidence": 0.91, "source_rank": 1},
            {"text": "运动模式", "confidence": 0.80, "source_rank": 2},
            {"text": "运动模式下", "confidence": 0.70, "source_rank": 3},
            {"text": "运动模试", "confidence": 0.60, "source_rank": 4},
            {"text": "运动摩斯", "confidence": 0.50, "source_rank": 5},
            {"text": "第五候选", "confidence": 0.40, "source_rank": 6},
        ],
    )

    request = service.build_for_audit(record)

    assert request is not None
    assert request.clarification_type == ClarificationType.VOICE_CONFIRMATION
    assert [item.display_text for item in request.candidates] == [
        "运动模式",
        "运动模式下",
        "运动模试",
        "运动摩斯",
    ]
    assert all(item.candidate_source == ClarificationCandidateSource.ASR_NBEST for item in request.candidates)


def test_right_side_completion_uses_only_registry_legal_discrete_areas():
    pipeline = FakePipeline()
    service = ClarificationService(pipeline, {})
    intent = SemanticIntent(
        clause_index=0,
        clause_text="打开右车门",
        intent_id="DOOR_OPEN",
        action="打开",
        target="车门",
        area="RIGHT_SIDE",
        control_domain="车身控制",
        risk_level="R3",
        semantic_confidence=0.9,
        ambiguity_score=0.2,
    )
    record = make_record(
        text="打开右车门",
        reasons=["AREA_INCOMPLETE"],
        intents=[intent],
    )

    request = service.build_for_audit(record)

    assert request is not None
    assert request.prompt == "您想打开哪扇车门？"
    assert [item.display_text for item in request.candidates] == [
        "打开右前车门",
        "打开右后车门",
    ]
    assert all(item.candidate_source == ClarificationCandidateSource.SLOT_COMPLETION for item in request.candidates)


def test_missing_continuous_value_does_not_create_guessed_candidates_or_ids():
    pipeline = FakePipeline()
    service = ClarificationService(pipeline, {})
    record = make_record(
        text="车窗开到",
        reasons=["VALUE_MISSING"],
        review_candidates=["WINDOW_SET_POSITION", "WINDOW_OPEN"],
    )

    request = service.build_for_audit(record)

    assert request is not None
    assert request.candidates == []


def test_safety_review_without_language_uncertainty_has_no_clarification():
    pipeline = FakePipeline()
    service = ClarificationService(pipeline, {})
    record = make_record(text="打开车门", status="OK")

    assert service.build_for_audit(record) is None


def test_selection_uses_persisted_candidate_and_creates_child_without_confidence_shortcut():
    pipeline = FakePipeline()
    service = ClarificationService(pipeline, {})
    request = ClarificationRequest(
        clarification_id="CLA_1",
        turn_id="TURN_A",
        clarification_type=ClarificationType.SEMANTIC_CONFIRMATION,
        prompt="请选择",
        original_text="打开右车门",
        candidates=[
            ClarificationCandidate(
                candidate_id="CAND_1",
                display_text="打开右前车门",
                candidate_source=ClarificationCandidateSource.SLOT_COMPLETION,
                source_rank=1,
                confidence=0.9,
            )
        ],
    )
    pipeline.workflow_repository.requests[request.clarification_id] = request
    source = make_record(text="打开右车门", reasons=["AREA_INCOMPLETE"])
    pipeline.audit_repository.get_by_turn = lambda _turn_id: source

    resolution, child = service.resolve(
        turn_id="TURN_A",
        clarification_id="CLA_1",
        candidate_id="CAND_1",
        none_of_above=False,
    )

    assert child.turn_id == "TURN_CHILD"
    assert resolution.resolution == ClarificationResolution.SELECTED
    assert resolution.child_turn_id == "TURN_CHILD"
    submitted, kwargs = pipeline.process_calls[0]
    assert submitted.text == "打开右前车门"
    assert kwargs["parent_turn_id"] == "TURN_A"
    assert kwargs["workflow_type"] == "CLARIFICATION_CONFIRMATION"
    assert kwargs["confirmed"] is False
    context = kwargs["audio_input_metadata"]["clarification_context"]
    assert context["confirmation_source"] == "USER_EXPLICIT_CONFIRMATION"
    assert context["confirmed_candidate_id"] == "CAND_1"


def test_none_of_above_is_terminal_without_child_or_pipeline_call():
    pipeline = FakePipeline()
    service = ClarificationService(pipeline, {})
    request = ClarificationRequest(
        clarification_id="CLA_2",
        turn_id="TURN_A",
        clarification_type=ClarificationType.SEMANTIC_CONFIRMATION,
        prompt="请重说",
        original_text="车窗开到",
        candidates=[],
    )
    pipeline.workflow_repository.requests[request.clarification_id] = request
    source = make_record(text="车窗开到", reasons=["VALUE_MISSING"])
    pipeline.audit_repository.get_by_turn = lambda _turn_id: source

    resolution, child = service.resolve(
        turn_id="TURN_A",
        clarification_id="CLA_2",
        candidate_id=None,
        none_of_above=True,
    )

    assert resolution.resolution == ClarificationResolution.NONE_OF_ABOVE
    assert resolution.child_turn_id is None
    assert child is None
    assert pipeline.process_calls == []
    assert pipeline.workflow_repository.events[-1]["payload"]["token_issued"] is False
    assert pipeline.workflow_repository.events[-1]["payload"]["execution_allowed"] is False


def test_public_submission_forbids_forged_semantic_payload():
    with pytest.raises(Exception):
        ClarificationSubmission.model_validate(
            {
                "clarification_id": "CLA_1",
                "candidate_id": "CAND_1",
                "intent_id": "DOOR_OPEN",
                "area": "RIGHT_FRONT",
                "decision": "PASS",
            }
        )


def test_unknown_candidate_is_rejected_without_child():
    pipeline = FakePipeline()
    service = ClarificationService(pipeline, {})
    request = ClarificationRequest(
        clarification_id="CLA_3",
        turn_id="TURN_A",
        clarification_type=ClarificationType.SEMANTIC_CONFIRMATION,
        prompt="请选择",
        original_text="打开右车门",
        candidates=[],
    )
    pipeline.workflow_repository.requests[request.clarification_id] = request
    pipeline.audit_repository.get_by_turn = lambda _turn_id: make_record(
        text="打开右车门", reasons=["AREA_INCOMPLETE"]
    )

    with pytest.raises(ClarificationWorkflowError, match="candidate_id"):
        service.resolve(
            turn_id="TURN_A",
            clarification_id="CLA_3",
            candidate_id="FORGED",
            none_of_above=False,
        )
    assert pipeline.process_calls == []


def test_clarification_snapshot_resolution_and_hash_chain_are_append_only(tmp_path):
    repository = WorkflowRepository(tmp_path / "workflow.db")
    request = ClarificationRequest(
        clarification_id="CLA_PERSIST",
        turn_id="TURN_A",
        clarification_type=ClarificationType.VOICE_CONFIRMATION,
        prompt="您是否说：",
        original_text="运动莫斯",
        candidates=[
            ClarificationCandidate(
                candidate_id="CAND_PERSIST",
                display_text="运动模式",
                candidate_source=ClarificationCandidateSource.ASR_NBEST,
                source_rank=1,
                confidence=0.91,
            )
        ],
    )
    repository.save_clarification_request(
        request, root_turn_id="TURN_A", review_reasons=["ASR_REVIEW"]
    )
    repository.append_event(
        root_turn_id="TURN_A",
        related_turn_id="TURN_A",
        event_type=WorkflowEventType.CLARIFICATION_REQUESTED,
        payload={"clarification_id": request.clarification_id},
    )
    resolution = ClarificationResolutionRecord(
        clarification_id=request.clarification_id,
        source_turn_id="TURN_A",
        resolution=ClarificationResolution.NONE_OF_ABOVE,
    )
    saved, created = repository.save_clarification_resolution(resolution)
    duplicate, duplicate_created = repository.save_clarification_resolution(resolution)
    repository.append_event(
        root_turn_id="TURN_A",
        related_turn_id="TURN_A",
        event_type=WorkflowEventType.CLARIFICATION_RESOLVED,
        payload=saved.model_dump(mode="json"),
    )

    restarted = WorkflowRepository(tmp_path / "workflow.db")
    assert created is True
    assert duplicate_created is False
    assert duplicate == saved
    assert restarted.get_clarification_request("CLA_PERSIST") == request
    assert restarted.get_clarification_resolution("CLA_PERSIST") == saved
    verification = restarted.verify_chain("TURN_A")
    assert verification.valid is True
    assert verification.event_count == 2
