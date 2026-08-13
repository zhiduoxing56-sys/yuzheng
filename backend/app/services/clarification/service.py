from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from threading import RLock
from typing import TYPE_CHECKING, Any
import re

import yaml

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


def _normalize_for_cmp(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).strip().lower().split())
_UNIFIED_INTENT_REGISTRY = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "nlu"
    / "spec"
    / "intent_registry_unified_v1.yaml"
)
_UNIFIED_ANCHOR_SET = (
    Path(__file__).resolve().parents[4]
    / "挂靠"
    / "intent_anchor_set_unified_v1.yaml"
)
_intent_chinese_names: dict[str, str] | None = None
_intent_anchors: dict[str, list[str]] | None = None

# 对 chinese_name 不完整（缺 required 槽位）且锚点首句也可能 REVIEW 的意图，
# 指定一个「确认后能闭环」的首选候选句。其余意图回退到锚点句。
_CANDIDATE_PREFERRED_EXECUTABLE = {
    "HEADLIGHT_SET_MODE": "打开前照灯",
}

# 区域歧义澄清：把内部 area 转成可读的区域词，用于生成候选指令。
_AREA_LABELS = {
    "LEFT_FRONT": "左前",
    "RIGHT_FRONT": "右前",
    "LEFT_REAR": "左后",
    "RIGHT_REAR": "右后",
    "FRONT_ROW": "前排",
    "REAR_ROW": "后排",
    "LEFT_SIDE": "左侧",
    "RIGHT_SIDE": "右侧",
    "ALL": "全部",
    "FRONT": "前部",
    "REAR": "后部",
}
_SPECIFIC_AREA_LABELS = ("LEFT_FRONT", "RIGHT_FRONT", "LEFT_REAR", "RIGHT_REAR")


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

    @classmethod
    def _readable_intent_name(cls, intent_id: str) -> str:
        """把内部 intent_id 转成一个「可重新执行」的人类可读指令。

        不能直接返回 chinese_name：对 required_slots 非空（如 HEADLIGHT_SET_MODE 需
        MODE）的意图，chinese_name（如「设置主灯模式」）是不完整指令，用户确认后
        重新处理仍会 REVIEW，造成弹窗无限循环。因此优先取该意图锚点里第一个
        「完整动作句」（跳过与 chinese_name 相同的锚点），确保确认后能闭环。
        """
        if not _INTERNAL_IDENTIFIER.fullmatch(intent_id):
            return intent_id
        global _intent_chinese_names, _intent_anchors
        if _intent_chinese_names is None or _intent_anchors is None:
            raw = yaml.safe_load(_UNIFIED_INTENT_REGISTRY.read_text(encoding="utf-8"))
            definitions = raw.get("intents", []) if isinstance(raw, dict) else []
            _intent_chinese_names = {
                str(definition.get("intent_id")): str(definition.get("chinese_name", ""))
                for definition in definitions
                if isinstance(definition, dict) and definition.get("intent_id")
            }
            try:
                anchor_root = yaml.safe_load(_UNIFIED_ANCHOR_SET.read_text(encoding="utf-8"))
                anchor_intents = anchor_root.get("intents", {}) if isinstance(anchor_root, dict) else {}
                _intent_anchors = {
                    str(key): [str(item) for item in (value.get("anchors", []) if isinstance(value, dict) else [])]
                    for key, value in anchor_intents.items()
                }
            except Exception:
                _intent_anchors = {}
        chinese_name = _intent_chinese_names.get(intent_id, intent_id)
        preferred = _CANDIDATE_PREFERRED_EXECUTABLE.get(intent_id)
        if preferred and _normalize_for_cmp(preferred) != _normalize_for_cmp(chinese_name):
            return preferred
        anchors = _intent_anchors.get(intent_id, [])
        if anchors:
            normalized_cn = _normalize_for_cmp(chinese_name)
            for anchor in anchors:
                if _normalize_for_cmp(anchor) == normalized_cn:
                    continue
                return anchor
        return chinese_name

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
        # 未指定侧的车门/车窗等区域歧义：生成具体区域候选（如 打开左前车门）。
        # 仅当意图允许具体区域（LEFT_FRONT 等）且当前 area 未解析时才生成。
        if not values and intent.area in (None, "unknown"):
            specific = [a for a in _SPECIFIC_AREA_LABELS if a in allowed]
            if specific:
                target_label = intent.target or ""
                action_label = intent.action or ""
                for area in specific:
                    area_label = _AREA_LABELS.get(area, "")
                    candidate = f"{action_label}{area_label}{target_label}".strip()
                    if not candidate:
                        continue
                    values.append(
                        (
                            candidate,
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
            area_ambiguous = "AREA_AMBIGUOUS" in record.final_decision.reason_codes
            semantic_language_review = bool(
                frame.semantic_status != "OK"
                or frame.review_reasons
                or frame.review_candidates
                or frame.unresolved_clauses
                or area_ambiguous
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
                            self._readable_intent_name(text),
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

                # 防无限循环：确认的候选若本身不完整，重新处理后又产生「原文相同」
                # 的澄清（如候选「设置主灯模式」缺 MODE，处理后仍 REVIEW 又弹同样
                # 候选），则抑制 child 的澄清弹窗，让用户重新描述，避免死循环。
                child_clarification = command_result.clarification_request
                if (
                    child_clarification is not None
                    and child_clarification.original_text == selected_text
                ):
                    command_result = command_result.model_copy(
                        update={"clarification_request": None}
                    )

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
