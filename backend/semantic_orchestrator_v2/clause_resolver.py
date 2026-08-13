from __future__ import annotations

import re
from dataclasses import dataclass


ACTION_TERMS = (
    "解除锁定",
    "打开",
    "开启",
    "关闭",
    "关掉",
    "关上",
    "合上",
    "锁定",
    "上锁",
    "解锁",
    "折叠",
    "收起",
    "展开",
    "启用",
    "停用",
    "禁用",
    "退出",
    "取消",
    "激活",
    "恢复",
    "施加",
    "释放",
    "松开",
    "拉起",
    "升起",
    "降下",
    "放倒",
    "调高",
    "调低",
    "调节",
    "调整",
    "设置",
    "切换",
    "加速",
    "减速",
    "刹车",
    "制动",
    "鸣笛",
    "按喇叭",
    "掀开",
    "开",
    "关",
    "锁",
    "调",
)

OBJECT_TERMS = (
    "外后视镜",
    "后视镜",
    "方向盘",
    "挡风玻璃",
    "风挡",
    "后挡风",
    "车身稳定控制",
    "电子稳定系统",
    "车身稳定",
    "行李厢",
    "后备厢",
    "后备箱",
    "尾门",
    "前舱盖",
    "发动机舱盖",
    "引擎盖",
    "巡航",
    "双闪警示灯",
    "双闪",
    "危险警示灯",
    "转向灯",
    "近光灯",
    "远光灯",
    "雾灯",
    "示宽灯",
    "位置灯",
    "车窗",
    "窗户",
    "天窗",
    "车门",
    "电动门",
    "雨刮",
    "雨刷",
    "驻车制动",
    "电子手刹",
    "手刹",
    "座椅",
    "靠背",
    "腰托",
    "喇叭",
    "档位",
    "挡位",
    "车速",
    "速度",
    "自动泊车",
    "车道",
    "ESC",
    "窗",
    "门",
)

SELF_CONTAINED_ACTIONS = ("刹车", "制动", "加速", "减速", "鸣笛", "按喇叭")
NEGATION_PREFIXES = ("不要", "别", "不准", "禁止")

_ACTION_PATTERN = re.compile("|".join(re.escape(term) for term in sorted(ACTION_TERMS, key=len, reverse=True)))
_OBJECT_PATTERN = re.compile("|".join(re.escape(term) for term in sorted(OBJECT_TERMS, key=len, reverse=True)), re.IGNORECASE)
_ORDERED_BOUNDARY = re.compile(
    r"后(?:再|重新)|[，,；;。]+|并且|然后|接着|同时|以及|并|再|和"
)


@dataclass(frozen=True, slots=True)
class ClauseResolution:
    clauses: tuple[str, ...]
    split: bool
    strategy: str


def has_explicit_object(text: str) -> bool:
    return bool(_OBJECT_PATTERN.search(text))


def _is_negated(text: str, start: int) -> bool:
    prefix = text[max(0, start - 4) : start]
    return any(prefix.endswith(item) for item in NEGATION_PREFIXES)


def has_positive_action(text: str) -> bool:
    return any(not _is_negated(text, match.start()) for match in _ACTION_PATTERN.finditer(text))


def is_potential_control_clause(text: str) -> bool:
    stripped = text.strip()
    if not stripped or not has_positive_action(stripped):
        return False
    return has_explicit_object(stripped) or any(term in stripped for term in SELF_CONTAINED_ACTIONS)


def _clean_clause(text: str) -> str:
    value = text.strip(" ，,；;。")
    value = re.sub(r"^(?:请)?先", "", value)
    value = re.sub(r"^(?:然后|接着|再|并且|并|同时|以及)", "", value)
    value = re.sub(r"(?:然后|接着|再|并且|并|同时|以及)$", "", value)
    value = re.sub(r"^重新", "", value)
    return value.strip(" ，,；;。")


class OrderedClauseResolver:
    """Split only when every produced fragment is a plausible vehicle-control clause."""

    def resolve(self, text: str) -> ClauseResolution:
        normalized = text.strip()
        ordered_parts = [
            cleaned
            for part in _ORDERED_BOUNDARY.split(normalized)
            if (cleaned := _clean_clause(part))
        ]
        if len(ordered_parts) > 1 and all(
            is_potential_control_clause(part) for part in ordered_parts
        ):
            return ClauseResolution(tuple(ordered_parts), True, "ORDERED_BOUNDARY")

        implicit = self._implicit_action_boundary(normalized)
        if implicit is not None:
            return ClauseResolution(tuple(implicit), True, "IMPLICIT_ACTION_BOUNDARY")
        return ClauseResolution((_clean_clause(normalized),), False, "SINGLE_CLAUSE")

    @staticmethod
    def _implicit_action_boundary(text: str) -> list[str] | None:
        matches = [
            match
            for match in _ACTION_PATTERN.finditer(text)
            if not _is_negated(text, match.start())
        ]
        if len(matches) < 2:
            return None
        boundaries = [match.start() for match in matches[1:]]
        parts = [
            _clean_clause(text[start:end])
            for start, end in zip(
                [0, *boundaries],
                [*boundaries, len(text)],
                strict=True,
            )
        ]
        if all(is_potential_control_clause(part) for part in parts):
            return parts
        return None
