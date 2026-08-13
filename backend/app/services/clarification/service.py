from __future__ import annotations

import hashlib
import json
from threading import RLock
from typing import TYPE_CHECKING, Any
import re

from app.models.schemas import (
    AuditRecord,
    ClarificationCandidate,
    ClarificationCandidateSource,
    ClarificationRequest,
    ClarificationResolution,
    ClarificationResolutionRecord,
    ClarificationType,
    DecisionLabel,
    TextCommandRequest,
    TextCommandResponse,
    WorkflowEventType,
    make_id,
)
from app.services.semantic.area import allowed_areas_for_intent

if TYPE_CHECKING:
    from app.core.pipeline import CommandPipeline


MAX_CLARIFICATION_CANDIDATES = 4
CONFIRMATION_SOURCE = "USER_EXPLICIT_CONFIRMATION"
_INTERNAL_IDENTIFIER = re.compile(r"^[A-Z][A-Z0-9_]*$")
_CONTINUOUS_VALUE_CUE = re.compile(
    r"(?:开到|调到|设置为|设为|调整到)\s*$"
)


class ClarificationWorkflowError(ValueError):
    pass


class ClarificationService:
    """Builds clarification snapshots only from already-authoritative results."""

    def __init__(self, pipeline: "CommandPipeline", config: dict[str, Any]) -> None:
        self.pipeline = pipeline
        self.config = config
        self._resolution_lock = RLock()

    def active_for_turn(self, turn_id: str) -> ClarificationRequest | None:
        request = self.pipeline.workflow_repository.clarification_for_turn(turn_id)
        if request is None:
            return None
        if self.pipeline.workflow_repository.get_clarification_resolution(
            request.clarification_id
        ) is not None:
            return None
        return request

    @staticmethod
    def _occurrence_candidate_id(record: AuditRecord, intent: Any) -> str:
        payload = {
            "audit_id": record.audit_id,
            "turn_id": record.turn_id,
            "clause_index": intent.clause_index,
            "intent_id": intent.intent_id,
            "clause_text": intent.clause_text,
        }
        canonical = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return "CLAC_OCC_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]

    @classmethod
    def _occurrence_candidates(
        cls, record: AuditRecord
    ) -> list[ClarificationCandidate]:
        frame = record.semantic_frame
        formal = [
            intent
            for intent in frame.intents
            if intent.runtime_identity == "FORMAL"
        ]
        all_resolved_are_formal = bool(formal) and len(formal) == len(frame.intents)
        multi_protocol_review = (
            "MULTI_INTENT_EXECUTION_UNSUPPORTED"
            in record.final_decision.reason_codes
            and len(formal) > 1
        )
        partial_multi_review = (
            "MULTI_INTENT_INCOMPLETE" in frame.review_reasons
            and bool(frame.unresolved_clauses)
        )
        if not all_resolved_are_formal or not (
            multi_protocol_review or partial_multi_review
        ):
            return []
        return [
            ClarificationCandidate(
                candidate_id=cls._occurrence_candidate_id(record, intent),
                display_text=intent.clause_text,
                candidate_source=(
                    ClarificationCandidateSource.SEMANTIC_REVIEW_CANDIDATE
                ),
                source_rank=rank,
                confidence=intent.semantic_confidence,
            )
            for rank, intent in enumerate(formal[:MAX_CLARIFICATION_CANDIDATES], start=1)
        ]

    @staticmethod
    def _deduplicate(
        candidates: list[tuple[str, ClarificationCandidateSource, int, float | None]],
    ) -> list[ClarificationCandidate]:
        result: list[ClarificationCandidate] = []
        seen: set[str] = set()
        for display_text, source, source_rank, confidence in candidates:
            normalized = " ".join(display_text.strip().split())
            if (
                not normalized
                or normalized in seen
                or _INTERNAL_IDENTIFIER.fullmatch(normalized)
            ):
                continue
            seen.add(normalized)
            result.append(
                ClarificationCandidate(
                    candidate_id=make_id("CLAC"),
                    display_text=normalized,
                    candidate_source=source,
                    source_rank=source_rank,
                    confidence=confidence,
                )
            )
            if len(result) == MAX_CLARIFICATION_CANDIDATES:
                break
        return result

    @staticmethod
    def _slot_candidates(record: AuditRecord) -> list[tuple[str, ClarificationCandidateSource, int, float | None]]:
        frame = record.semantic_frame
        if len(frame.intents) != 1:
            return []
        intent = frame.intents[0]
        allowed = allowed_areas_for_intent(intent.intent_id)
        raw = frame.raw_text
        replacements: list[tuple[str, str, str]] = []
        if intent.area == "RIGHT_SIDE" and {"RIGHT_FRONT", "RIGHT_REAR"} <= allowed:
            replacements = [
                ("右车门", "右前车门", "RIGHT_FRONT"),
                ("右车门", "右后车门", "RIGHT_REAR"),
                ("右侧车门", "右前车门", "RIGHT_FRONT"),
                ("右侧车门", "右后车门", "RIGHT_REAR"),
            ]
        elif intent.area == "LEFT_SIDE" and {"LEFT_FRONT", "LEFT_REAR"} <= allowed:
            replacements = [
                ("左车门", "左前车门", "LEFT_FRONT"),
                ("左车门", "左后车门", "LEFT_REAR"),
                ("左侧车门", "左前车门", "LEFT_FRONT"),
                ("左侧车门", "左后车门", "LEFT_REAR"),
            ]
        values: list[tuple[str, ClarificationCandidateSource, int, float | None]] = []
        used_areas: set[str] = set()
        for old, new, area in replacements:
            if old not in raw or area in used_areas:
                continue
            used_areas.add(area)
            values.append(
                (
                    raw.replace(old, new, 1),
                    ClarificationCandidateSource.SLOT_COMPLETION,
                    len(values) + 1,
                    intent.semantic_confidence,
                )
            )
        return values

    def build_for_audit(self, record: AuditRecord) -> ClarificationRequest | None:
        existing = self.pipeline.workflow_repository.clarification_for_turn(record.turn_id)
        if existing is not None:
            if self.pipeline.workflow_repository.get_clarification_resolution(
                existing.clarification_id
            ) is not None:
                return None
            return existing
        if record.final_decision.final_decision != DecisionLabel.REVIEW:
            return None

        frame = record.semantic_frame
        transcription = record.transcription_result
        is_audio = record.input_trust_result.audio_source != "text_api"
        raw_asr_nbest = record.audio_input_metadata.get("asr_nbest", [])
        asr_nbest = [
            (
                str(item.get("text", "")),
                int(item.get("source_rank", index)),
                (
                    float(item["confidence"])
                    if item.get("confidence") is not None
                    else None
                ),
            )
            for index, item in enumerate(raw_asr_nbest, start=1)
            if isinstance(item, dict) and str(item.get("text", "")).strip()
        ] if isinstance(raw_asr_nbest, list) else []
        confirmation_context = record.audio_input_metadata.get("clarification_context", {})
        repeated_voice_confirmation = (
            isinstance(confirmation_context, dict)
            and confirmation_context.get("confirmation_source") == CONFIRMATION_SOURCE
            and confirmation_context.get("clarification_type")
            == ClarificationType.VOICE_CONFIRMATION.value
            and confirmation_context.get("confirmed_text") == frame.raw_text
        )

        raw_candidates: list[
            tuple[str, ClarificationCandidateSource, int, float | None]
        ] = []
        occurrence_candidates = self._occurrence_candidates(record)
        clarification_type: ClarificationType | None = None
        prompt = record.interpreter_review_question or "您想执行哪个操作？"

        if occurrence_candidates:
            clarification_type = ClarificationType.SEMANTIC_CONFIRMATION
            prompt = "检测到多个动作，请选择要作为新指令重新处理的原始子句。"
        elif is_audio and asr_nbest and not repeated_voice_confirmation:
            clarification_type = ClarificationType.VOICE_CONFIRMATION
            prompt = "您是否说："
            raw_candidates.extend(
                (
                    text,
                    ClarificationCandidateSource.ASR_NBEST,
                    source_rank,
                    confidence,
                )
                for text, source_rank, confidence in sorted(
                    asr_nbest,
                    key=lambda item: item[1],
                )
            )
        else:
            semantic_language_review = bool(
                frame.semantic_status != "OK"
                or frame.review_reasons
                or frame.review_candidates
                or frame.unresolved_clauses
            )
            low_asr_confidence = (
                is_audio
                and transcription.asr_confidence is not None
                and transcription.asr_confidence
                < float(self.config.get("asr_clarification_threshold", 0.75))
                and not repeated_voice_confirmation
            )
            if low_asr_confidence and frame.review_candidates:
                clarification_type = ClarificationType.VOICE_CONFIRMATION
                prompt = "您是否说："
                raw_candidates.extend(
                    (
                        text,
                        ClarificationCandidateSource.TEXT_SIMILARITY,
                        rank,
                        None,
                    )
                    for rank, text in enumerate(frame.review_candidates, start=1)
                )
            elif semantic_language_review:
                clarification_type = ClarificationType.SEMANTIC_CONFIRMATION
                continuous_value_missing = bool(
                    _CONTINUOUS_VALUE_CUE.search(frame.raw_text)
                    and not re.search(r"\d", frame.raw_text)
                )
                if not continuous_value_missing:
                    raw_candidates.extend(
                        (
                            text,
                            ClarificationCandidateSource.SEMANTIC_REVIEW_CANDIDATE,
                            rank,
                            frame.semantic_confidence,
                        )
                        for rank, text in enumerate(frame.review_candidates, start=1)
                    )
                    start = len(raw_candidates) + 1
                    raw_candidates.extend(
                        (
                            candidate.canonical_text,
                            ClarificationCandidateSource.SEMANTIC_REVIEW_CANDIDATE,
                            start + offset,
                            None,
                        )
                        for offset, candidate in enumerate(record.candidate_interpretations)
                        if candidate.validation_status == "VALID"
                    )
                slot_candidates = self._slot_candidates(record)
                if slot_candidates:
                    prompt = (
                        "您想打开哪扇车门？"
                        if any("车门" in item[0] for item in slot_candidates)
                        else prompt
                    )
                    raw_candidates = [*slot_candidates, *raw_candidates]

        if clarification_type is None:
            return None
        request = ClarificationRequest(
            clarification_id=make_id("CLA"),
            turn_id=record.turn_id,
            clarification_type=clarification_type,
            prompt=prompt,
            original_text=frame.raw_text,
            candidates=(
                occurrence_candidates
                if occurrence_candidates
                else self._deduplicate(raw_candidates)
            ),
        )
        persisted = self.pipeline.workflow_repository.save_clarification_request(
            request,
            root_turn_id=record.root_turn_id or record.turn_id,
            review_reasons=frame.review_reasons,
        )
        self.pipeline.workflow_repository.append_event(
            root_turn_id=record.root_turn_id or record.turn_id,
            related_turn_id=record.turn_id,
            parent_turn_id=record.parent_turn_id,
            event_type=WorkflowEventType.CLARIFICATION_REQUESTED,
            payload={
                "clarification_id": persisted.clarification_id,
                "clarification_type": persisted.clarification_type.value,
                "original_text": persisted.original_text,
                "review_reasons": frame.review_reasons,
                "shown_candidates": [
                    candidate.model_dump(mode="json")
                    for candidate in persisted.candidates
                ],
            },
        )
        return persisted

    def resolve(
        self,
        *,
        turn_id: str,
        clarification_id: str,
        candidate_id: str | None,
        none_of_above: bool,
    ) -> tuple[ClarificationResolutionRecord, TextCommandResponse | None]:
        with self._resolution_lock:
            request = self.pipeline.workflow_repository.get_clarification_request(
                clarification_id
            )
            if request is None or request.turn_id != turn_id:
                raise ClarificationWorkflowError("澄清请求不存在或不属于当前轮次")
            existing = self.pipeline.workflow_repository.get_clarification_resolution(
                clarification_id
            )
            if existing is not None:
                child_record = (
                    self.pipeline.get_turn(existing.child_turn_id)
                    if existing.child_turn_id
                    else None
                )
                child = (
                    child_record
                    if isinstance(child_record, TextCommandResponse)
                    else None
                )
                return existing, child
            source = self.pipeline.audit_repository.get_by_turn(turn_id)
            if source is None:
                raise ClarificationWorkflowError("未找到原始轮次")
            if source.final_decision.final_decision != DecisionLabel.REVIEW:
                raise ClarificationWorkflowError("只有 REVIEW 轮次允许语言澄清")

            selected = None
            selected_parent_occurrence: dict[str, Any] | None = None
            if not none_of_above:
                selected = next(
                    (
                        candidate
                        for candidate in request.candidates
                        if candidate.candidate_id == candidate_id
                    ),
                    None,
                )
                if selected is None:
                    raise ClarificationWorkflowError("candidate_id 不属于当前澄清请求")
                if selected.candidate_id.startswith("CLAC_OCC_"):
                    occurrence_matches = [
                        intent
                        for intent in source.semantic_frame.intents
                        if intent.runtime_identity == "FORMAL"
                        and self._occurrence_candidate_id(source, intent)
                        == selected.candidate_id
                    ]
                    if len(occurrence_matches) != 1:
                        raise ClarificationWorkflowError(
                            "候选无法唯一绑定父轮次 semantic occurrence"
                        )
                    occurrence = occurrence_matches[0]
                    formal_occurrences = [
                        intent
                        for intent in source.semantic_frame.intents
                        if intent.runtime_identity == "FORMAL"
                    ]
                    expected = ClarificationCandidate(
                        candidate_id=self._occurrence_candidate_id(source, occurrence),
                        display_text=occurrence.clause_text,
                        candidate_source=(
                            ClarificationCandidateSource.SEMANTIC_REVIEW_CANDIDATE
                        ),
                        source_rank=formal_occurrences.index(occurrence) + 1,
                        confidence=occurrence.semantic_confidence,
                    )
                    if selected != expected:
                        raise ClarificationWorkflowError(
                            "持久化候选与不可变父轮次 occurrence 不一致"
                        )
                    selected_parent_occurrence = {
                        "clause_index": occurrence.clause_index,
                        "intent_id": occurrence.intent_id,
                        "clause_text": occurrence.clause_text,
                    }

            command_result: TextCommandResponse | None = None
            child_turn_id: str | None = None
            if selected is not None:
                selected_text = (
                    str(selected_parent_occurrence["clause_text"])
                    if selected_parent_occurrence is not None
                    else selected.display_text
                )
                confirmation_context = {
                    "clarification_id": clarification_id,
                    "confirmed_candidate_id": selected.candidate_id,
                    "confirmation_source": CONFIRMATION_SOURCE,
                    "confirmed_text": selected_text,
                    "clarification_type": request.clarification_type.value,
                    "selected_parent_occurrence": selected_parent_occurrence,
                }
                transcription_override = source.transcription_result.model_copy(
                    update={
                        "text": selected_text,
                        "transcribed_text": selected_text,
                    }
                )
                command_result = self.pipeline.process_text(
                    TextCommandRequest(
                        text=selected_text,
                        speaker_zone=source.input_trust_result.speaker_zone,
                        speaker_role=source.input_trust_result.speaker_role,
                    ),
                    root_turn_id=source.root_turn_id or source.turn_id,
                    parent_turn_id=source.turn_id,
                    attempt_no=source.attempt_no + 1,
                    workflow_type="CLARIFICATION_CONFIRMATION",
                    confirmed=False,
                    input_trust_override=(
                        source.input_trust_result
                        if source.input_trust_result.audio_source != "text_api"
                        else None
                    ),
                    transcription_override=(
                        transcription_override
                        if source.input_trust_result.audio_source != "text_api"
                        else None
                    ),
                    spectrum_analysis=source.spectrum_analysis,
                    audio_input_metadata={
                        **source.audio_input_metadata,
                        "clarification_context": confirmation_context,
                    },
                    trusted_context=self.pipeline.trusted_context_from_audit(source),
                )
                child_turn_id = command_result.turn_id

            resolution = ClarificationResolutionRecord(
                clarification_id=clarification_id,
                source_turn_id=turn_id,
                resolution=(
                    ClarificationResolution.NONE_OF_ABOVE
                    if none_of_above
                    else ClarificationResolution.SELECTED
                ),
                selected_candidate_id=(selected.candidate_id if selected else None),
                selected_candidate_text=(
                    str(selected_parent_occurrence["clause_text"])
                    if selected_parent_occurrence is not None
                    else selected.display_text
                    if selected
                    else None
                ),
                child_turn_id=child_turn_id,
            )
            persisted, created = (
                self.pipeline.workflow_repository.save_clarification_resolution(
                    resolution
                )
            )
            if not created:
                return persisted, command_result
            self.pipeline.workflow_repository.append_event(
                root_turn_id=source.root_turn_id or source.turn_id,
                related_turn_id=child_turn_id or source.turn_id,
                parent_turn_id=(source.turn_id if child_turn_id else source.parent_turn_id),
                event_type=WorkflowEventType.CLARIFICATION_RESOLVED,
                payload={
                    **persisted.model_dump(mode="json"),
                    "confirmation_source": (
                        CONFIRMATION_SOURCE if selected is not None else None
                    ),
                    "token_issued": False if none_of_above else None,
                    "execution_allowed": False if none_of_above else None,
                    "selected_parent_occurrence": selected_parent_occurrence,
                },
            )
            return persisted, command_result
