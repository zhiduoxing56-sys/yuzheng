from __future__ import annotations

import unicodedata
from statistics import mean
from typing import Any

import yaml

from app.models.schemas import SemanticFrame, SemanticIntent
from app.services.semantic.area import (
    allowed_areas_for_intent,
    canonical_area,
    explicit_area_mentions,
    resolve_explicit_area,
)
from semantic_orchestrator_v2.orchestrator import INTENT_CARDS, OrchestratorRun
from semantic_orchestrator_v2_1.orchestrator import SemanticOrchestratorV2_1
from semantic_registry_v1 import UnifiedSemanticRegistry


_ACTION_DISPLAY_LABELS = {
    "ACCELERATE": "加速",
    "ACTIVATE": "打开",
    "ADJUST": "设置",
    "APPLY": "施加",
    "BRAKE": "制动",
    "CHANGE": "变道",
    "CLOSE": "关闭",
    "DECELERATE": "减速",
    "DISABLE": "停用",
    "ENABLE": "启用",
    "FOLD": "折叠",
    "KEEP": "保持",
    "LOCK": "锁定",
    "OPEN": "打开",
    "RELEASE": "释放",
    "SET": "设置",
    "STEER": "避险转向",
    "SWITCH_MODE": "设置",
    "TURN_OFF": "关闭",
    "TURN_ON": "打开",
    "UNFOLD": "展开",
    "UNLOCK": "解锁",
}

_TARGET_DISPLAY_LABELS = {
    "AUTO_PARK": "自动泊车",
    "CRUISE": "巡航",
    "DOOR": "车门",
    "ESC": "车身稳定",
    "FOG_LIGHT": "雾灯",
    "HAZARD_LIGHT": "危险警示灯",
    "HEADLIGHT": "前照灯",
    "HIGH_BEAM": "远光灯",
    "HOOD": "前舱盖",
    "HORN": "喇叭",
    "LANE": "车道",
    "LOW_BEAM": "近光灯",
    "MIRROR": "后视镜",
    "PARKING_BRAKE": "驻车制动",
    "PARKING_LIGHT": "驻车灯",
    "SEAT": "座椅",
    "SERVICE_BRAKE": "制动",
    "STEERING_WHEEL": "方向盘",
    "SUNROOF": "天窗",
    "TRANSMISSION": "挡位",
    "TRUNK": "后备箱",
    "TURN_INDICATOR": "转向灯",
    "VEHICLE": "车辆",
    "WINDOW": "车窗",
    "WINDSHIELD": "前挡风除雾",
    "WIPER": "雨刮",
}

_ACTION_DISPLAY_OVERRIDES = {
    ("ENABLE", "AUTO_PARK", "STATE"): "打开",
    ("BRAKE", "SERVICE_BRAKE", "NORMAL_BRAKING"): "打开",
    ("ENABLE", "CRUISE", "STATE"): "开启巡航",
    ("DISABLE", "CRUISE", "STATE"): "关闭巡航",
    ("BRAKE", "SERVICE_BRAKE", "EMERGENCY_BRAKING"): "紧急制动",
    ("ACTIVATE", "HORN", "SOUND"): "鸣笛",
}

_TARGET_DISPLAY_OVERRIDES = {
    ("ACCELERATE", "VEHICLE", "SPEED"): "速度",
    ("BRAKE", "SERVICE_BRAKE", "NORMAL_BRAKING"): "制动",
    ("DECELERATE", "VEHICLE", "SPEED"): "速度",
    ("BRAKE", "SERVICE_BRAKE", "EMERGENCY_BRAKING"): "制动",
    ("STEER", "VEHICLE", "TRAJECTORY"): "转向",
    ("KEEP", "LANE", "POSITION"): "当前车道",
}

def _normalized_text(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).strip().lower().split())


class SemanticOrchestratorService:
    """唯一正式语义入口：运行冻结 V2.1 并直接产出公共语义契约。"""

    def __init__(self) -> None:
        self._registry = UnifiedSemanticRegistry()
        registry = self._registry.document
        if not isinstance(registry, dict):
            raise RuntimeError("正式 R4 Intent Registry 根节点必须是映射")
        definitions = registry.get("intents", [])
        if not isinstance(definitions, list):
            raise RuntimeError("正式 R4 Intent Registry 的 intents 必须是列表")
        self._intent_definitions: dict[str, dict[str, Any]] = {}
        for definition in definitions:
            if not isinstance(definition, dict):
                raise RuntimeError("正式 R4 Intent Registry 的 intent 定义必须是映射")
            required_fields = {
                "intent_id",
                "canonical_action",
                "canonical_target",
                "control_attribute",
                "control_domain",
                "risk_level",
                "risk_tags",
            }
            missing_fields = required_fields - set(definition)
            if missing_fields:
                raise RuntimeError(
                    "正式 R4 Intent Registry 的 intent 定义缺少字段: "
                    f"{sorted(missing_fields)}"
                )
            intent_id = str(definition.get("intent_id", ""))
            if not intent_id or intent_id in self._intent_definitions:
                raise RuntimeError(f"正式 R4 Intent Registry 存在无效或重复 intent_id: {intent_id}")
            self._intent_definitions[intent_id] = dict(definition)
        expected_count = int(registry.get("statistics", {}).get("intent_count", 0))
        if len(self._intent_definitions) != expected_count:
            raise RuntimeError(
                "正式 R4 Intent Registry 的 intent_count 与实际定义数量不一致"
            )

        cards_root = yaml.safe_load(INTENT_CARDS.read_text(encoding="utf-8"))
        cards = cards_root.get("intents", {}) if isinstance(cards_root, dict) else {}
        if set(cards) != set(self._intent_definitions):
            raise RuntimeError("冻结 Intent Cards 与正式 R4 Intent Registry 的意图集合不一致")
        for intent_id, definition in self._intent_definitions.items():
            card = cards[intent_id]
            if (
                str(card.get("canonical_action")) != str(definition["canonical_action"])
                or str(card.get("canonical_target")) != str(definition["canonical_target"])
            ):
                raise RuntimeError(
                    "冻结 Intent Cards 与正式 R4 Intent Registry 的规范动作/对象不一致: "
                    f"{intent_id}"
                )
        self._orchestrator = SemanticOrchestratorV2_1()

    def close(self) -> None:
        self._orchestrator.close()

    @staticmethod
    def _confidence(clause: dict[str, Any], intent_id: str) -> tuple[float, float]:
        target = next(
            (
                item
                for item in clause.get("evidence", {}).get("targets", [])
                if str(item.get("target")) == intent_id
            ),
            None,
        )
        if target is None:
            return 0.5, 0.0
        scores = [
            float(channel["score"])
            for channel in target.get("channels", {}).values()
            if channel.get("score") is not None
        ]
        confidence = max(0.0, min(1.0, mean(scores))) if scores else 0.5
        return round(confidence, 6), 0.0

    def _intent_metadata(
        self, intent_id: str
    ) -> tuple[str, str, str, str, str, str, list[str]]:
        definition = self._intent_definitions.get(intent_id)
        if definition is None:
            raise RuntimeError(
                f"冻结语义输出了正式 R4 Intent Registry 中不存在的 intent_id: {intent_id}"
            )
        canonical_action = str(definition.get("canonical_action", ""))
        canonical_target = str(definition.get("canonical_target", ""))
        control_attribute = str(definition.get("control_attribute", ""))
        semantic_key = (canonical_action, canonical_target, control_attribute)
        action = _ACTION_DISPLAY_OVERRIDES.get(
            semantic_key, _ACTION_DISPLAY_LABELS.get(canonical_action)
        )
        target = _TARGET_DISPLAY_OVERRIDES.get(
            semantic_key, _TARGET_DISPLAY_LABELS.get(canonical_target)
        )
        action = action or canonical_action
        target = target or canonical_target
        return (
            action,
            target,
            str(definition["runtime_identity"]),
            control_attribute,
            str(definition["control_domain"]),
            str(definition["risk_level"]),
            [str(item) for item in definition["risk_tags"]],
        )

    @staticmethod
    def _authoritative_occurrences(run: OrchestratorRun) -> list[dict[str, Any]]:
        status = str(run.output.get("status", "NO_MATCH"))
        if status == "OK":
            raw_occurrences = run.output.get("sub_intents", [])
        elif status == "REVIEW":
            raw_occurrences = run.output.get("resolved_sub_intents", [])
        else:
            raw_occurrences = []

        occurrences: list[dict[str, Any]] = []
        for item in raw_occurrences:
            if isinstance(item, dict):
                occurrences.append(
                    {
                        "intent_id": str(item["intent_id"]),
                        "params": dict(item.get("params", {})),
                    }
                )
            else:
                occurrences.append({"intent_id": str(item), "params": {}})
        return occurrences

    def parse(self, turn_id: str, text: str) -> SemanticFrame:
        run = self._orchestrator.run(text)
        authoritative_occurrences = self._authoritative_occurrences(run)
        intents: list[SemanticIntent] = []
        status = str(run.output.get("status", "NO_MATCH"))
        reliable_clause_results = [
            (original_index, clause)
            for original_index, clause in enumerate(
                run.debug.get("clause_results", [])
            )
            if clause.get("reliable")
            and len(clause.get("accepted_intent_ids", [])) == 1
        ]
        if len(reliable_clause_results) != len(authoritative_occurrences):
            raise RuntimeError(
                "冻结语义可靠 clause occurrence 与权威子意图数量不一致"
            )
        for occurrence, (original_index, clause) in zip(
            authoritative_occurrences,
            reliable_clause_results,
            strict=True,
        ):
            intent_id = str(occurrence["intent_id"])
            accepted_intent_id = str(clause["accepted_intent_ids"][0])
            if intent_id != accepted_intent_id:
                raise RuntimeError(
                    "冻结语义 occurrence 顺序不一致: "
                    f"clause={accepted_intent_id}, authoritative={intent_id}"
                )
            (
                action,
                target,
                runtime_identity,
                control_attribute,
                domain,
                risk_level,
                risk_tags,
            ) = self._intent_metadata(intent_id)
            confidence, ambiguity = self._confidence(clause, intent_id)
            params = dict(occurrence.get("params", {}))
            allowed_areas = allowed_areas_for_intent(intent_id)
            supplied_area = canonical_area(params.get("area"))
            if supplied_area not in allowed_areas:
                supplied_area = None
            resolved_area = supplied_area or resolve_explicit_area(
                str(clause.get("clause", "")),
                allowed_areas,
            )
            intents.append(
                SemanticIntent(
                    clause_index=int(clause.get("clause_index", original_index)),
                    clause_text=str(clause.get("clause", "")),
                    intent_id=intent_id,
                    runtime_identity=runtime_identity,
                    action=action,
                    target=target,
                    area=resolved_area or "unknown",
                    value=params.get("value"),
                    mode=params.get("mode"),
                    direction=params.get("direction"),
                    control_attribute=control_attribute,
                    control_domain=domain,
                    risk_level=risk_level,
                    risk_tags=risk_tags,
                    semantic_confidence=confidence,
                    ambiguity_score=ambiguity,
                )
            )

        semantic_confidence = min(
            (intent.semantic_confidence for intent in intents), default=0.0
        )
        ambiguity_score = max((intent.ambiguity_score for intent in intents), default=1.0)
        review_reasons = [str(item) for item in run.output.get("reasons", [])]
        unresolved_clauses = [
            str(item) for item in run.output.get("unresolved_clauses", [])
        ]
        # The frozen orchestrator can report MISSING_REQUIRED_AREA before this
        # public wrapper applies the same Registry's explicit-area resolver.  Do
        # not preserve that stale REVIEW when every AREA-required occurrence now
        # carries an explicit allowed value.  This reconciles runtime state only;
        # it does not infer a default area or alter the frozen semantic contract.
        area_reconciled = bool(intents) and review_reasons == ["MISSING_REQUIRED_AREA"]
        if area_reconciled:
            for intent in intents:
                definition = self._intent_definitions[intent.intent_id]
                if "AREA" in definition.get("required_slots", []) and intent.area == "unknown":
                    area_reconciled = False
                    break
        semantic_status = "OK" if area_reconciled else str(
            run.output.get("status", "NO_MATCH")
        )
        final_review_reasons = [] if area_reconciled else review_reasons
        final_unresolved_clauses = [] if area_reconciled else unresolved_clauses
        area_failures: list[str] = []
        for intent in intents:
            definition = self._intent_definitions[intent.intent_id]
            carried_slots = {
                *definition.get("required_slots", []),
                *definition.get("optional_slots", []),
            }
            if "AREA" not in carried_slots:
                continue
            mentions = explicit_area_mentions(intent.clause_text)
            allowed_areas = allowed_areas_for_intent(intent.intent_id)
            mentioned_areas = {area for _term, area in mentions}
            if mentions and (
                intent.area == "unknown"
                or not mentioned_areas.issubset(allowed_areas)
                or intent.area not in allowed_areas
            ):
                area_failures.append(intent.clause_text)
        if area_failures:
            semantic_status = "REVIEW"
            final_review_reasons = list(
                dict.fromkeys([*final_review_reasons, "AREA_MENTION_UNRESOLVED"])
            )
            final_unresolved_clauses = list(
                dict.fromkeys([*final_unresolved_clauses, *area_failures])
            )
        return SemanticFrame(
            turn_id=turn_id,
            raw_text=text,
            normalized_text=_normalized_text(text),
            semantic_confidence=semantic_confidence,
            ambiguity_score=ambiguity_score,
            semantic_status=semantic_status,
            review_reasons=final_review_reasons,
            review_candidates=[
                str(item) for item in run.output.get("review_candidates", [])
            ],
            unresolved_clauses=final_unresolved_clauses,
            security_signals=[
                str(item) for item in run.output.get("security_signals", [])
            ],
            intents=intents,
        )
