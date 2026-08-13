"""最终一致性复核层：用户对车辆现状的声明 与 本次裁决已取得的证据 一致性核验。

设计（基于队友方案优化）：
- 现有安全判断流程保持不变。在其产生 PASS/REVIEW/BLOCK 后、授权执行之前，
  从原始指令中确定性提取有限的车辆当前状态声明（ContextClaim）。
- 只核验「有对应证据快照」的声明；无证据的声明标记 UNVERIFIABLE，不改变裁决。
- 结果规则：仅当 base_decision == PASS 且声明冲突时，提升为 REVIEW；
  原 REVIEW/BLOCK 保持不变（BLOCK > REVIEW > PASS 顺序永不破坏）。

相对队友方案的优化点：
1. 词典覆盖演示常用口语（下雨了/天黑了/车停着…），支持否定式（没下雨/没障碍）。
2. 判定使用本次裁决证据快照中的实际值 + 确定性阈值，不重新请求 CARLA，避免时间漂移。
3. 一次核验多条声明，任一冲突即提升；审计可展示每条声明的原文与核验结果。
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.models.schemas import EvidenceNode


class ClaimType(str, Enum):
    RAINING = "RAINING"                      # 现在下雨
    NOT_RAINING = "NOT_RAINING"              # 现在没下雨
    LOW_LIGHT = "LOW_LIGHT"                  # 现在天黑了/夜间
    DAYLIGHT = "DAYLIGHT"                    # 现在是白天
    FRONT_NO_PERSON = "FRONT_NO_PERSON"      # 前方没人
    FRONT_PERSON_PRESENT = "FRONT_PERSON_PRESENT"  # 前方有人
    FRONT_NO_OBSTACLE = "FRONT_NO_OBSTACLE"  # 前方无障碍
    FRONT_OBSTACLE_PRESENT = "FRONT_OBSTACLE_PRESENT"  # 前方有障碍
    VEHICLE_STOPPED = "VEHICLE_STOPPED"      # 车停着
    VEHICLE_MOVING = "VEHICLE_MOVING"        # 车在行驶


class ClaimConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"                # 声明与证据一致
    CONFLICT = "CONFLICT"                    # 声明与证据冲突
    UNVERIFIABLE = "UNVERIFIABLE"            # 无对应证据，无法核验


@dataclass(frozen=True)
class ClaimDefinition:
    claim_type: ClaimType
    display_name: str                        # 声明的人类可读名（用于审计展示）
    patterns: tuple[str, ...]                # 词典（按匹配到的原文 span 判定）
    evidence_type: str                       # 核验使用的证据类型


# 词典：pattern 按长度降序排列（最长匹配优先）。
CLAIM_DEFINITIONS: tuple[ClaimDefinition, ...] = (
    ClaimDefinition(
        ClaimType.RAINING, "现在下雨",
        ("现在正在下雨", "外面正在下雨", "当前正在下雨", "现在在下雨", "当前在下雨",
         "正在下雨", "外面下雨", "外面在下雨", "现在下雨", "下雨了"),
        "ENVIRONMENT_CONDITIONS",
    ),
    ClaimDefinition(
        ClaimType.NOT_RAINING, "现在没下雨",
        ("现在没有下雨", "当前没有下雨", "现在没下雨", "当前没下雨", "没下雨", "没有下雨"),
        "ENVIRONMENT_CONDITIONS",
    ),
    ClaimDefinition(
        ClaimType.LOW_LIGHT, "现在是夜间",
        ("现在是晚上", "现在是夜间", "天已经黑了", "天都黑了", "天黑了", "到晚上", "夜里", "夜晚"),
        "ENVIRONMENT_CONDITIONS",
    ),
    ClaimDefinition(
        ClaimType.DAYLIGHT, "现在是白天",
        ("现在是白天", "现在天亮了", "天还亮着", "天亮了", "大白天", "白天"),
        "ENVIRONMENT_CONDITIONS",
    ),
    ClaimDefinition(
        ClaimType.FRONT_NO_PERSON, "前方无人",
        ("前面没有人", "前方没有人", "前面没人", "前方没人", "前面无人", "前方无人"),
        "SURROUNDING_OBJECT_STATE",
    ),
    ClaimDefinition(
        ClaimType.FRONT_PERSON_PRESENT, "前方有人",
        ("前面有行人", "前方有行人", "前面有人", "前方有人"),
        "SURROUNDING_OBJECT_STATE",
    ),
    ClaimDefinition(
        ClaimType.FRONT_NO_OBSTACLE, "前方无障碍",
        ("前面没有障碍", "前方没有障碍", "前面没障碍", "前方没障碍", "前面无障碍", "前方无障碍"),
        "SURROUNDING_OBJECT_STATE",
    ),
    ClaimDefinition(
        ClaimType.FRONT_OBSTACLE_PRESENT, "前方有障碍",
        ("前面有障碍", "前方有障碍", "前面有车", "前方有车", "前面堵了", "前方拥堵"),
        "SURROUNDING_OBJECT_STATE",
    ),
    ClaimDefinition(
        ClaimType.VEHICLE_STOPPED, "车辆静止",
        ("车辆处于静止", "车辆是静止的", "车是停着的", "车停着的", "车辆静止", "车停着", "车停住", "车已停下"),
        "VEHICLE_SPEED",
    ),
    ClaimDefinition(
        ClaimType.VEHICLE_MOVING, "车辆行驶中",
        ("车辆正在行驶", "车辆在行驶", "车正在行驶", "车在行驶", "车在跑", "车在动", "车开着"),
        "VEHICLE_SPEED",
    ),
)

# 最长匹配优先：每个 ClaimType 只保留一个（pattern 已按长度排序，取最长命中）。
# 判定阈值（与证据单元一致）
LOW_LIGHT_THRESHOLD = 40            # ambient_illumination < 40 视为夜间
FRONT_NEAR_THRESHOLD = 8.0          # front_obstacle_distance <= 8m 视为有人/有障碍


def _normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).strip().lower().split())


@dataclass(frozen=True)
class ExtractedClaim:
    claim_type: ClaimType
    display_name: str
    matched_span: str                 # 原文中命中的声明片段
    evidence_type: str


def extract_claims(text: str) -> list[ExtractedClaim]:
    """从原始指令中确定性提取声明（词典 + 最长匹配，不切分句子）。"""
    normalized = _normalize(text)
    found: list[ExtractedClaim] = []
    seen: set[ClaimType] = set()
    for definition in CLAIM_DEFINITIONS:
        best_span: str | None = None
        best_len = -1
        for pattern in definition.patterns:
            key = _normalize(pattern)
            if key in normalized and len(key) > best_len:
                best_span = pattern
                best_len = len(key)
        if best_span is not None and definition.claim_type not in seen:
            seen.add(definition.claim_type)
            found.append(
                ExtractedClaim(
                    claim_type=definition.claim_type,
                    display_name=definition.display_name,
                    matched_span=best_span,
                    evidence_type=definition.evidence_type,
                )
            )
    # 保持词典声明顺序，便于审计稳定输出
    return found


def _evidence_node(nodes: list[EvidenceNode], evidence_type: str) -> EvidenceNode | None:
    for node in nodes:
        if node.evidence_type == evidence_type:
            return node
    return None


def _as_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _weather_string(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    weather = value.get("weather")
    return str(weather).upper() if weather is not None else None


def _ambient(value: Any) -> float | None:
    if not isinstance(value, dict):
        return None
    return _as_number(value.get("ambient_illumination", value.get("ambient_light")))


def _front_distance(value: Any) -> float | None:
    if not isinstance(value, dict):
        return None
    return _as_number(value.get("front_obstacle_distance"))


def _claim_consistent(claim: ExtractedClaim, value: Any) -> bool | None:
    """返回 True=一致 / False=冲突 / None=证据值缺失无法判定。"""
    claim_type = claim.claim_type
    if claim_type in (ClaimType.RAINING, ClaimType.NOT_RAINING):
        weather = _weather_string(value)
        if weather is None:
            return None
        raining = "RAIN" in weather
        return raining if claim_type == ClaimType.RAINING else not raining
    if claim_type in (ClaimType.LOW_LIGHT, ClaimType.DAYLIGHT):
        ambient = _ambient(value)
        if ambient is None:
            return None
        low = ambient < LOW_LIGHT_THRESHOLD
        return low if claim_type == ClaimType.LOW_LIGHT else not low
    if claim_type in (
        ClaimType.FRONT_NO_PERSON,
        ClaimType.FRONT_PERSON_PRESENT,
        ClaimType.FRONT_NO_OBSTACLE,
        ClaimType.FRONT_OBSTACLE_PRESENT,
    ):
        distance = _front_distance(value)
        if distance is None:
            return None
        near = distance <= FRONT_NEAR_THRESHOLD
        if claim_type in (ClaimType.FRONT_NO_PERSON, ClaimType.FRONT_NO_OBSTACLE):
            return not near
        return near
    if claim_type in (ClaimType.VEHICLE_STOPPED, ClaimType.VEHICLE_MOVING):
        speed = _as_number(value)
        if speed is None:
            return None
        stopped = speed == 0
        return stopped if claim_type == ClaimType.VEHICLE_STOPPED else not stopped
    return None


@dataclass(frozen=True)
class ClaimCheckItem:
    claim_type: ClaimType
    display_name: str
    matched_span: str
    consistency: ClaimConsistency
    evidence_type: str
    evidence_value: Any


@dataclass(frozen=True)
class ClaimCheckResult:
    items: list[ClaimCheckItem]
    has_conflict: bool

    @property
    def conflict_items(self) -> list[ClaimCheckItem]:
        return [item for item in self.items if item.consistency == ClaimConsistency.CONFLICT]


class ContextClaimService:
    """对本次裁决的原始指令做状态声明核验。"""

    def __init__(self) -> None:
        pass

    def check(self, raw_text: str, evidence_nodes: list[EvidenceNode]) -> ClaimCheckResult:
        claims = extract_claims(raw_text)
        items: list[ClaimCheckItem] = []
        for claim in claims:
            node = _evidence_node(evidence_nodes, claim.evidence_type)
            if node is None:
                consistency = ClaimConsistency.UNVERIFIABLE
                evidence_value = None
            else:
                consistent = _claim_consistent(claim, node.value)
                if consistent is None:
                    consistency = ClaimConsistency.UNVERIFIABLE
                else:
                    consistency = (
                        ClaimConsistency.CONSISTENT if consistent else ClaimConsistency.CONFLICT
                    )
                evidence_value = node.value
            items.append(
                ClaimCheckItem(
                    claim_type=claim.claim_type,
                    display_name=claim.display_name,
                    matched_span=claim.matched_span,
                    consistency=consistency,
                    evidence_type=claim.evidence_type,
                    evidence_value=evidence_value,
                )
            )
        has_conflict = any(
            item.consistency == ClaimConsistency.CONFLICT for item in items
        )
        return ClaimCheckResult(items=items, has_conflict=has_conflict)
