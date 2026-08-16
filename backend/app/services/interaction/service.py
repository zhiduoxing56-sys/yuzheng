from __future__ import annotations

"""The only producer and resolver of user interactions.

Semantic, safety and authorization services provide facts only.  This module
turns those facts into one of the six user tasks, or deliberately returns
``None`` for terminal results that must not open a modal.
"""

from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from app.models.schemas import (
    DecisionLabel, InteractionAction, InteractionCandidate, InteractionRequest,
    InteractionState, InteractionType, TextCommandRequest, UserReason, utc_now,
)
from app.services.semantic.area import allowed_areas_for_intent

if TYPE_CHECKING:
    from app.core.pipeline import CommandPipeline
    from app.models.schemas import AuditRecord, TextCommandResponse


class InteractionWorkflowError(ValueError):
    pass


_FIELD_LABELS = {
    "MODE": "模式", "VALUE": "目标数值", "AREA": "区域", "POSITION": "位置",
    "ANGLE": "角度", "GEAR": "档位", "DIRECTION": "方向",
}

# 区域歧义候选：内部 area 转可读区域词（与 clarification._AREA_LABELS 对齐）。
_AREA_LABELS = {
    "LEFT_FRONT": "左前", "RIGHT_FRONT": "右前", "LEFT_REAR": "左后", "RIGHT_REAR": "右后",
    "FRONT_ROW": "前排", "REAR_ROW": "后排", "LEFT_SIDE": "左侧", "RIGHT_SIDE": "右侧",
    "ALL": "全部", "FRONT": "前部", "REAR": "后部",
}
_SPECIFIC_AREA_LABELS = ("LEFT_FRONT", "RIGHT_FRONT", "LEFT_REAR", "RIGHT_REAR")


class InteractionService:
    def __init__(self, pipeline: "CommandPipeline", config: dict) -> None:
        self.pipeline = pipeline
        self.config = config
        root = Path(__file__).resolve().parents[4]
        registry = yaml.safe_load((root / "data/nlu/spec/intent_registry_unified_v1.yaml").read_text(encoding="utf-8"))
        self._definitions = {str(item["intent_id"]): item for item in registry.get("intents", [])}
        self._value_contracts = dict(registry.get("value_contracts", {}))
        self._mode_contracts = dict(registry.get("mode_contracts", {}))

    def _reason(self, code: str, title: str, description: str, details: list[dict[str, Any]] | None = None) -> UserReason:
        return UserReason(code=code, title=title, description=description, details=details or [])

    def _save(self, request: InteractionRequest, record: "AuditRecord") -> InteractionRequest:
        return self.pipeline.workflow_repository.save_interaction_request(request, root_turn_id=record.root_turn_id or record.turn_id)

    def _operation(self, intent: Any) -> str:
        return str(intent.clause_text or f"{intent.action}{intent.target}")

    def _missing_slot(self, intent: Any) -> str | None:
        definition = self._definitions.get(str(intent.intent_id), {})
        for slot in definition.get("required_slots", []):
            value = getattr(intent, str(slot).lower(), None)
            if value is None or value == "unknown":
                return str(slot)
        return None

    def _parameter_payload(self, intent: Any, slot: str) -> dict[str, Any]:
        definition = self._definitions.get(str(intent.intent_id), {})
        payload: dict[str, Any] = {
            "original_instruction": intent.clause_text,
            "confirmed_operation": self._operation(intent),
            "missing_field": slot,
            "field_label": _FIELD_LABELS.get(slot, slot),
            "parameter_type": slot,
            "known_fields": {key: value for key, value in {
                "area": getattr(intent, "area", None), "value": getattr(intent, "value", None),
                "mode": getattr(intent, "mode", None), "direction": getattr(intent, "direction", None),
            }.items() if value is not None and value != "unknown"},
        }
        if slot == "AREA":
            payload["enum_values"] = list(definition.get("allowed_areas", []))
        elif slot == "VALUE":
            contract = self._value_contracts.get(definition.get("value_contract"), {})
            payload.update({"enum_values": list(contract.get("enum_values", [])), "minimum": (contract.get("valid_range") or {}).get("min"), "maximum": (contract.get("valid_range") or {}).get("max"), "unit": contract.get("canonical_unit")})
        elif slot == "MODE":
            payload["enum_values"] = list(self._mode_contracts.get(definition.get("mode_contract"), []))
        return payload

    def project(self, record: "AuditRecord", *, execution_allowed: bool = False) -> InteractionRequest | None:
        frame, decision = record.semantic_frame, record.final_decision.final_decision
        # Priority 1: terminal routes never receive an interaction.
        routing = record.request_routing
        if decision == DecisionLabel.BLOCK or (routing is not None and not routing.contains_vehicle_control):
            return None
        if frame.intents and all(item.runtime_identity == "KNOWN_NON_EXECUTABLE" for item in frame.intents):
            return None

        expiry = utc_now() + timedelta(seconds=int(self.config.get("review_ttl_seconds", 300)))
        formal = [item for item in frame.intents if item.runtime_identity == "FORMAL"]
        incomplete = next(((item, self._missing_slot(item)) for item in formal if self._missing_slot(item)), None)
        # Priority 2: semantic work always precedes safety and authorization.
        if incomplete is not None:
            intent, slot = incomplete
            payload = self._parameter_payload(intent, str(slot))
            return self._save(InteractionRequest(
                turn_id=record.turn_id, unit_index=intent.clause_index, intent_id=intent.intent_id,
                state=InteractionState.NEEDS_CLARIFICATION, interaction_type=InteractionType.PARAMETER_COMPLETION,
                canonical_operation=self._operation(intent), reason_codes=list(frame.review_reasons),
                user_reason=self._reason(str(slot), "需要补充参数", f"请补充{payload['field_label']}后继续处理。", [{"missing_field": slot}]),
                payload=payload, allowed_actions=[InteractionAction.SUBMIT_PARAMETERS, InteractionAction.CANCEL], expires_at=expiry,
            ), record)
        candidates = self._valid_candidates(record)
        area_candidates = self._area_candidates(record)
        if area_candidates:
            return self._save(InteractionRequest(
                turn_id=record.turn_id, unit_index=(formal[0].clause_index if formal else None), intent_id=(formal[0].intent_id if formal else None),
                state=InteractionState.NEEDS_CLARIFICATION, interaction_type=InteractionType.SEMANTIC_DISAMBIGUATION,
                canonical_operation=frame.raw_text, reason_codes=list(record.final_decision.reason_codes),
                candidates=area_candidates,
                user_reason=self._reason("AREA_AMBIGUOUS", "请选择具体位置", "您未指定具体车门/车窗，请选择要操作的位置。"),
                payload={"original_instruction": frame.raw_text, "interpretations": [item.display_text for item in area_candidates]},
                allowed_actions=[InteractionAction.SELECT_CANDIDATE, InteractionAction.REPHRASE, InteractionAction.CANCEL], expires_at=expiry,
            ), record)
        if frame.semantic_status != "OK" or frame.unresolved_clauses:
            if len(candidates) >= 2:
                return self._save(InteractionRequest(
                    turn_id=record.turn_id, state=InteractionState.NEEDS_CLARIFICATION,
                    interaction_type=InteractionType.SEMANTIC_DISAMBIGUATION, canonical_operation=frame.raw_text,
                    reason_codes=list(frame.review_reasons), candidates=candidates[:4],
                    user_reason=self._reason("SEMANTIC_AMBIGUITY", "需要确认具体操作", "存在多个合法解释，请选择您要执行的操作。"),
                    payload={"original_instruction": frame.raw_text, "interpretations": [item.display_text for item in candidates[:4]]},
                    allowed_actions=[InteractionAction.SELECT_CANDIDATE, InteractionAction.REPHRASE, InteractionAction.CANCEL], expires_at=expiry,
                ), record)
            return self._save(InteractionRequest(
                turn_id=record.turn_id, state=InteractionState.NEEDS_CLARIFICATION,
                interaction_type=InteractionType.UNRESOLVED_VEHICLE_CONTROL, canonical_operation=frame.raw_text,
                reason_codes=list(frame.review_reasons), user_reason=self._reason("UNRESOLVED_VEHICLE_CONTROL", "无法可靠确定具体操作", "系统判断这是一条车辆控制请求，但当前无法可靠确定具体操作。"),
                payload={"original_instruction": frame.raw_text}, allowed_actions=[InteractionAction.REPHRASE, InteractionAction.CANCEL], expires_at=expiry,
            ), record)
        if len(formal) >= 2:
            options = [InteractionCandidate(candidate_id=f"UNIT_{item.clause_index}", display_text=self._operation(item), canonical_text=self._operation(item), canonical_intent_id=item.intent_id, canonical_slots={"clause_index": item.clause_index}, source="RELIABLE_SUB_INTENT") for item in formal]
            return self._save(InteractionRequest(
                turn_id=record.turn_id, state=InteractionState.NEEDS_CLARIFICATION,
                interaction_type=InteractionType.MULTI_INTENT_SELECTION, canonical_operation=frame.raw_text, candidates=options,
                user_reason=self._reason("MULTI_INTENT", "检测到多个车辆控制操作", "请选择本次需要继续处理的操作。"),
                payload={"original_instruction": frame.raw_text, "sub_intents": [{"clause_index": item.clause_index, "display_text": self._operation(item)} for item in formal]},
                allowed_actions=[InteractionAction.SELECT_CANDIDATE, InteractionAction.CANCEL], expires_at=expiry,
            ), record)
        if decision == DecisionLabel.REVIEW:
            facts = [check.observed for check in record.safety_gate_result.checks if check.hit]
            return self._save(InteractionRequest(
                turn_id=record.turn_id, unit_index=(formal[0].clause_index if formal else None), intent_id=(formal[0].intent_id if formal else None),
                state=InteractionState.NEEDS_REVIEW, interaction_type=InteractionType.SAFETY_REVIEW,
                canonical_operation=self._operation(formal[0]) if formal else frame.raw_text, reason_codes=list(record.final_decision.reason_codes),
                user_reason=self._reason("SAFETY_REVIEW", "需要安全复核", record.final_decision.review_question or "当前安全信息需要您确认后才能继续。", [{"vehicle_facts": facts}, {"safety_signals": frame.security_signals}]),
                payload={"operation": self._operation(formal[0]) if formal else frame.raw_text, "safety_facts": facts, "evidence_anomalies": record.conflict_records, "security_signals": frame.security_signals},
                allowed_actions=[InteractionAction.CONFIRM, InteractionAction.CANCEL], expires_at=expiry,
            ), record)
        if execution_allowed and len(formal) == 1:
            intent = formal[0]
            return self._save(InteractionRequest(
                turn_id=record.turn_id, unit_index=intent.clause_index, intent_id=intent.intent_id,
                state=InteractionState.PASS, interaction_type=InteractionType.EXECUTION_CONFIRMATION, canonical_operation=self._operation(intent),
                user_reason=self._reason("EXECUTION_CONFIRMATION", "确认执行车辆操作", "安全检查已通过，确认后将执行该车辆操作。"),
                payload={"operation": self._operation(intent), "safety_passed": True},
                allowed_actions=[InteractionAction.EXECUTE, InteractionAction.CANCEL], expires_at=expiry,
            ), record)
        return None

    @staticmethod
    def _area_candidates(record: "AuditRecord") -> list[InteractionCandidate]:
        """区域歧义候选：单意图 + 区域未指定 + 意图支持具体区域 → 生成「打开左前车门」等。"""
        frame = record.semantic_frame
        if len(frame.intents) != 1:
            return []
        intent = frame.intents[0]
        if intent.area not in (None, "unknown"):
            return []
        allowed = allowed_areas_for_intent(intent.intent_id)
        specific = [area for area in _SPECIFIC_AREA_LABELS if area in allowed]
        if not specific:
            return []
        action = intent.action or ""
        target = intent.target or ""
        return [
            InteractionCandidate(
                candidate_id=f"AREA_{area}",
                display_text=f"{action}{_AREA_LABELS.get(area, area)}{target}",
                canonical_text=f"{action}{_AREA_LABELS.get(area, area)}{target}",
                canonical_intent_id=intent.intent_id,
                canonical_slots={"area": area},
                source="SLOT_COMPLETION",
            )
            for area in specific
        ]

    @staticmethod
    def _valid_candidates(record: "AuditRecord") -> list[InteractionCandidate]:
        return [InteractionCandidate(candidate_id=item.candidate_id, display_text=item.canonical_text, canonical_text=item.canonical_text, canonical_intent_id=getattr(item, "intent_id", None), canonical_slots=dict(item.parameters), source="REGISTERED_INTERPRETATION") for item in record.candidate_interpretations if item.validation_status == "VALID" and item.canonical_text.strip()][:4]

    def active_for_turn(self, turn_id: str) -> InteractionRequest | None:
        request = self.pipeline.workflow_repository.interaction_for_turn(turn_id)
        return request if request is not None and not request.consumed else None

    def resolve(self, *, turn_id: str, interaction_id: str, action: InteractionAction, candidate_id: str | None = None, text: str | None = None, parameters: dict[str, Any] | None = None) -> "TextCommandResponse | None":
        request = self.pipeline.workflow_repository.get_interaction_request(interaction_id)
        if request is None or request.turn_id != turn_id: raise InteractionWorkflowError("interaction not found for turn")
        if request.consumed or (request.expires_at is not None and utc_now() >= request.expires_at): raise InteractionWorkflowError("interaction is unavailable")
        if action not in request.allowed_actions: raise InteractionWorkflowError("interaction action not allowed")
        if not self.pipeline.workflow_repository.consume_interaction(interaction_id): raise InteractionWorkflowError("interaction already consumed")
        source = self.pipeline.get_turn(turn_id)
        if action == InteractionAction.CANCEL:
            self.pipeline.workflow_repository.append_event(root_turn_id=(source.root_turn_id if source else turn_id), related_turn_id=turn_id, event_type=__import__('app.models.schemas', fromlist=['WorkflowEventType']).WorkflowEventType.REVIEW_CANCELLED, payload={"reason": "用户已取消本次指令", "interaction_id": interaction_id, "interaction_type": request.interaction_type.value})
            return None
        if action == InteractionAction.EXECUTE:
            self.pipeline.workflow_repository.append_event(
                root_turn_id=source.root_turn_id if source else turn_id, related_turn_id=turn_id,
                event_type=__import__('app.models.schemas', fromlist=['WorkflowEventType']).WorkflowEventType.INTERACTION_CONFIRMED,
                payload={"interaction_id": interaction_id, "interaction_type": request.interaction_type.value, "reason": "用户已确认执行车辆操作"},
            )
            return None
        if source is None: raise InteractionWorkflowError("source turn not found")
        if action == InteractionAction.SELECT_CANDIDATE:
            selected = next((item for item in request.candidates if item.candidate_id == candidate_id), None)
            if selected is None: raise InteractionWorkflowError("candidate does not belong to interaction")
            next_text = selected.canonical_text
        elif action == InteractionAction.REPHRASE: next_text = (text or "").strip()
        elif action == InteractionAction.SUBMIT_PARAMETERS:
            next_text = " ".join([request.canonical_operation or "", *[str(value) for value in (parameters or {}).values()]]).strip()
        elif action == InteractionAction.CONFIRM: next_text = request.canonical_operation or ""
        else: raise InteractionWorkflowError("unsupported interaction action")
        if not next_text: raise InteractionWorkflowError("interaction has no resumable operation")
        return self.pipeline.process_text(TextCommandRequest(text=next_text, speaker_zone=source.input_trust_result.speaker_zone, speaker_role=source.input_trust_result.speaker_role), root_turn_id=source.root_turn_id or source.turn_id, parent_turn_id=source.turn_id, attempt_no=source.attempt_no + 1, workflow_type="UNIFIED_INTERACTION", confirmed=action == InteractionAction.CONFIRM, trusted_context=self.pipeline.trusted_context_from_audit(getattr(source, "audit", source)))
