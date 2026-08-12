from __future__ import annotations

import re
from dataclasses import dataclass

from .clause_resolver import SELF_CONTAINED_ACTIONS, has_explicit_object


_POLITENESS = re.compile(r"^(?:请|麻烦|帮我|请帮我|给我|可以|能不能|请你)+")
_GENERIC_ONLY = re.compile(r"^(?:把)?(?:打开|关闭|关|开|调|调整|设置|弄)(?:它|这个|那个)?(?:一下|下|一点)?$")
_COMPARATIVE_ONLY = re.compile(r"^(?:再)?(?:快|慢|高|低|大|小)(?:一点|一些|点)?$")
_UNKNOWN_PRONOUN = re.compile(r"(?:打开|关闭|关|开|调|调整|设置|弄)(?:它|这个|那个)$")


@dataclass(frozen=True, slots=True)
class EllipsisDecision:
    insufficient: bool
    matched_pattern: str | None


class EllipsisGuard:
    def check(self, text: str) -> EllipsisDecision:
        value = re.sub(r"[，。！？、,.!?;；\s]", "", text)
        value = _POLITENESS.sub("", value)
        if any(value == action or value == f"{action}一下" for action in SELF_CONTAINED_ACTIONS):
            return EllipsisDecision(False, None)
        if has_explicit_object(value):
            return EllipsisDecision(False, None)
        if _GENERIC_ONLY.fullmatch(value):
            return EllipsisDecision(True, "GENERIC_ACTION_WITHOUT_OBJECT")
        if _COMPARATIVE_ONLY.fullmatch(value):
            return EllipsisDecision(True, "COMPARATIVE_WITHOUT_OBJECT")
        if _UNKNOWN_PRONOUN.fullmatch(value):
            return EllipsisDecision(True, "UNKNOWN_CONTEXT_PRONOUN")
        return EllipsisDecision(False, None)
