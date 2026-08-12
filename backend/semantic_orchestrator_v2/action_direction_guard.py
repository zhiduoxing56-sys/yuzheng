from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


ACTION_TO_FAMILY = {
    "OPEN": "POSITIVE_ON",
    "TURN_ON": "POSITIVE_ON",
    "ENABLE": "POSITIVE_ON",
    "ACTIVATE": "POSITIVE_ON",
    "CLOSE": "NEGATIVE_OFF",
    "TURN_OFF": "NEGATIVE_OFF",
    "DISABLE": "NEGATIVE_OFF",
    "LOCK": "LOCK",
    "UNLOCK": "UNLOCK",
    "FOLD": "FOLD",
    "UNFOLD": "UNFOLD",
    "APPLY": "APPLY",
    "RELEASE": "RELEASE",
    "ACCELERATE": "ACCELERATE",
    "DECELERATE": "DECELERATE",
    "BRAKE": "BRAKE",
}

FAMILY_CUES = {
    "UNLOCK": ("解除锁定", "解除车门锁定", "解除尾门锁定", "解锁"),
    "LOCK": ("锁定", "上锁", "锁上", "锁一下"),
    "FOLD": ("折叠", "收起"),
    "UNFOLD": ("展开",),
    "APPLY": ("施加", "拉起手刹", "拉手刹"),
    "RELEASE": ("释放", "松开手刹", "松手刹", "放下电子手刹"),
    "ACCELERATE": ("加速", "提高车速", "加快车速"),
    "DECELERATE": ("减速", "降低车速", "放慢车速"),
    "BRAKE": ("刹车", "制动", "刹停"),
    "NEGATIVE_OFF": ("关闭", "关掉", "关上", "合上", "停用", "禁用", "退出", "取消"),
    "POSITIVE_ON": ("打开", "开启", "启用", "激活", "恢复", "掀开"),
}

OPPOSITES = {
    "POSITIVE_ON": "NEGATIVE_OFF",
    "NEGATIVE_OFF": "POSITIVE_ON",
    "LOCK": "UNLOCK",
    "UNLOCK": "LOCK",
    "FOLD": "UNFOLD",
    "UNFOLD": "FOLD",
    "APPLY": "RELEASE",
    "RELEASE": "APPLY",
    "ACCELERATE": "DECELERATE",
    "DECELERATE": "ACCELERATE",
}

NEGATION_PREFIXES = ("不要", "别", "不准", "禁止")


@dataclass(frozen=True, slots=True)
class DirectionDecision:
    conflict: bool
    requested_families: tuple[str, ...]
    selected_family: str | None
    compatible_candidates: tuple[str, ...]


def _negated(text: str, start: int) -> bool:
    prefix = text[max(0, start - 5) : start]
    return any(prefix.endswith(item) for item in NEGATION_PREFIXES)


def requested_families(text: str) -> tuple[str, ...]:
    found: list[tuple[int, str]] = []
    mirror_open = re.search(r"打开(?:外)?后视镜", text)
    if mirror_open:
        found.append((mirror_open.start(), "UNFOLD"))
    if re.search(r"(?:车窗|窗户|窗).{0,4}(?:升起|升上)", text) or re.search(r"(?:升起|升上).{0,4}(?:车窗|窗户|窗)", text):
        found.append((0, "NEGATIVE_OFF"))
    if re.search(r"(?:车窗|窗户|窗).{0,4}(?:降下|降下来)", text) or re.search(r"(?:降下|降下来).{0,4}(?:车窗|窗户|窗)", text):
        found.append((0, "POSITIVE_ON"))
    for match in re.finditer(r"开(?=车门|门|车窗|窗户|窗|天窗|近光灯|远光灯|雾灯|双闪|巡航)", text):
        if not _negated(text, match.start()):
            found.append((match.start(), "POSITIVE_ON"))
    for match in re.finditer(r"关(?=车门|门|车窗|窗户|窗|天窗|近光灯|远光灯|雾灯|双闪|巡航)", text):
        if not _negated(text, match.start()):
            found.append((match.start(), "NEGATIVE_OFF"))
    for match in re.finditer(r"(?<!解)锁(?=车门|门|尾门|后备箱|后备厢|行李厢)", text):
        if not _negated(text, match.start()):
            found.append((match.start(), "LOCK"))
    for family, cues in FAMILY_CUES.items():
        for cue in cues:
            for match in re.finditer(re.escape(cue), text):
                if _negated(text, match.start()):
                    continue
                if family == "POSITIVE_ON" and cue == "打开" and mirror_open and match.start() == mirror_open.start():
                    continue
                found.append((match.start(), family))
    found.sort(key=lambda item: item[0])
    return tuple(dict.fromkeys(family for _position, family in found))


class ActionDirectionGuard:
    def __init__(self, intent_cards: dict[str, dict[str, Any]]) -> None:
        self.intent_cards = intent_cards

    def family_for_intent(self, intent_id: str) -> str | None:
        card = self.intent_cards.get(intent_id)
        if not card:
            return None
        return ACTION_TO_FAMILY.get(str(card.get("动作", "")))

    def check(
        self,
        clause: str,
        selected_intent: str,
        stage1_candidates: list[str],
    ) -> DirectionDecision:
        requested = requested_families(clause)
        selected_family = self.family_for_intent(selected_intent)
        conflict = bool(
            requested
            and selected_family
            and selected_family not in requested
            and any(OPPOSITES.get(family) == selected_family for family in requested)
        )
        compatible = tuple(
            candidate
            for candidate in stage1_candidates
            if self.family_for_intent(candidate) in requested
        )
        return DirectionDecision(conflict, requested, selected_family, compatible)
