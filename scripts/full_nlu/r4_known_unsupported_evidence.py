"""Evidence extraction for the SYS-014 R4 known-unsupported expansion.

This module reads only original MAC-SLU splits and the source-screen index. It
does not read baseline mappings and never mutates source data.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


OPEN_OPERATIONS = {
    "打开", "开启", "开", "开开", "启动", "打开一下", "开一下", "打开下", "开开下", "给打开",
}
CLOSE_OPERATIONS = {
    "关闭", "关掉", "关", "关了", "给关掉", "关闭掉", "关一下", "关闭一下", "关下", "关上", "给关闭",
}
ADJUST_OPERATIONS = {
    "调", "调节", "调整", "调到", "设置", "设置为", "设为", "调成", "调为", "切换", "切换为", "变成", "修改",
}
MOVE_OPERATIONS = {"移", "移动", "滑", "滑动", "升起", "下降", "旋转", "抬高", "降低", "伸出", "收回"}

CORE_TERMS = {
    "后视镜", "外后视镜", "座椅前后", "座椅高度", "靠背", "腰托", "车窗", "窗口", "天窗", "后备箱",
    "后备厢", "尾门", "前舱盖", "引擎盖", "发动机舱盖", "车门", "雨刮", "雨刷", "大灯", "前照灯",
    "近光灯", "远光灯", "雾灯", "示宽灯", "位置灯", "双闪", "危险警示灯", "转向灯", "除霜", "除雾",
    "挡风玻璃加热", "驻车制动", "手刹", "巡航", "档位", "挡位", "喇叭", "ABS", "TCS", "EBD", "EBA", "ESC",
}
ADAS_TERMS = {
    "车道偏离", "车道辅助", "变道辅助", "盲区", "碰撞预警", "碰撞减缓", "交通标志", "交通灯", "自动变道提醒",
    "前向辅助", "侧后辅助", "预防性制动", "紧急制动", "超速提醒", "超速报警", "限速提醒", "限速告警",
    "盲点", "交叉交通", "驾驶辅助", "领航辅助", "车道引导",
}


@dataclass(frozen=True)
class SourceFrame:
    source_file: str
    source_id: str
    intent_key: str
    query: str
    split_sentence: str
    frame: tuple[tuple[str, str], ...]
    source_screen_index: int | None

    def values(self, name: str) -> list[str]:
        return [value for key, value in self.frame if key == name]

    def first(self, name: str) -> str:
        values = self.values(name)
        return values[0] if values else ""

    def combined_text(self) -> str:
        return "|".join([self.split_sentence, *(value for _, value in self.frame)])

    def evidence_key(self) -> tuple[str, str, str]:
        return self.source_file, self.source_id, self.intent_key

    def to_report(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "source_id": self.source_id,
            "intent_key": self.intent_key,
            "source_screen_index": self.source_screen_index,
            "query": self.query,
            "split_sentence": self.split_sentence,
            "mac_frame": [{"name": name, "value": value} for name, value in self.frame],
        }


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected JSON object")
        records.append(value)
    return records


def load_source_screen_index(path: Path) -> dict[tuple[str, str], int]:
    index: dict[tuple[str, str], int] = {}
    for record in load_jsonl(path):
        source_file = str(record.get("原始文件", ""))
        source_id = str(record.get("原始编号", ""))
        screen_index = record.get("screen_index")
        if source_file and source_id and isinstance(screen_index, int):
            index[(source_file, source_id)] = screen_index
    return index


def extract_frames(paths: Iterable[Path], source_screen_path: Path) -> list[SourceFrame]:
    screen_index = load_source_screen_index(source_screen_path)
    frames: list[SourceFrame] = []
    for path in paths:
        for record in load_jsonl(path):
            query = str(record.get("query", ""))
            splits = record.get("split_sens") or []
            semantics = record.get("semantics") or {}
            if not isinstance(semantics, dict):
                continue
            for intent_key, intent_value in semantics.items():
                if not isinstance(intent_value, dict):
                    continue
                raw_frame = intent_value.get("车载控制")
                if not isinstance(raw_frame, list) or not raw_frame:
                    continue
                match = re.search(r"(\d+)", str(intent_key))
                split_index = int(match.group(1)) - 1 if match else 0
                split_sentence = str(splits[split_index]) if 0 <= split_index < len(splits) else query
                pairs = tuple(
                    (str(slot.get("name", "")), str(slot.get("value", "")))
                    for slot in raw_frame
                    if isinstance(slot, dict)
                )
                source_id = str(record.get("id", ""))
                frames.append(SourceFrame(
                    source_file=path.name,
                    source_id=source_id,
                    intent_key=str(intent_key),
                    query=query,
                    split_sentence=split_sentence,
                    frame=pairs,
                    source_screen_index=screen_index.get((path.name, source_id)),
                ))
    return frames


def operation_kind(frame: SourceFrame) -> str:
    operation = frame.first("操作")
    if operation in OPEN_OPERATIONS or any(token in operation for token in ("打开", "开启", "启动")):
        return "ON"
    if operation in CLOSE_OPERATIONS or any(token in operation for token in ("关闭", "关掉", "关上")):
        return "OFF"
    if operation in MOVE_OPERATIONS:
        return "MOVE"
    if operation in ADJUST_OPERATIONS or any(token in operation for token in ("调", "设置", "切换", "修改")):
        return "ADJUST"
    return "OTHER"


def _object(frame: SourceFrame) -> str:
    return frame.first("对象")


def _function(frame: SourceFrame) -> str:
    return frame.first("对象功能")


def _adjust(frame: SourceFrame) -> str:
    return frame.first("调节内容")


def _mode_value(frame: SourceFrame) -> str:
    return frame.first("模式") or frame.first("音效") or frame.first("摄像头模式") or frame.first("value")


def classify_approved(frame: SourceFrame) -> str | None:
    """Return an approved canonical candidate only for an unambiguous raw frame."""
    obj = _object(frame)
    feature = _function(frame)
    adjust = _adjust(frame)
    kind = operation_kind(frame)
    mode = frame.first("模式")
    value = frame.first("value")
    inside_light = frame.first("车内灯类型")
    text = frame.combined_text()

    if obj in {"前备箱", "前备厢"}:
        return "FRUNK_OPEN" if kind == "ON" else None

    if obj == "空调":
        if adjust == "温度":
            return "HVAC_SET_TEMPERATURE"
        if adjust in {"风量", "风速", "风", "风力"}:
            return "HVAC_SET_FAN_SPEED"
        if adjust in {"风向", "方向"}:
            return "HVAC_SET_AIRFLOW_DIRECTION"
        if (adjust == "模式" or mode) and kind not in {"ON", "OFF"}:
            return "HVAC_SET_MODE"
        if not adjust and not mode and kind in {"ON", "OFF"}:
            return f"HVAC_{kind}"
        return None

    if obj == "座椅" and feature in {"加热", "通风", "按摩"}:
        prefix = {"加热": "SEAT_HEATING", "通风": "SEAT_VENTILATION", "按摩": "SEAT_MASSAGE"}[feature]
        if kind in {"ON", "OFF"} and not adjust and not mode:
            return f"{prefix}_{kind}"
        if (adjust == "模式" or mode) and kind not in {"ON", "OFF"}:
            return f"{prefix}_SET_MODE"
        if kind not in {"ON", "OFF"} and (adjust or value):
            return f"{prefix}_SET_LEVEL"
        return None

    light = inside_light or obj
    light_prefix = {
        "阅读灯": "READING_LIGHT",
        "车内灯": "INTERIOR_LIGHT",
        "室内灯": "INTERIOR_LIGHT",
        "顶灯": "INTERIOR_LIGHT",
        "氛围灯": "AMBIENT_LIGHT",
    }.get(light)
    if light_prefix:
        if adjust == "亮度":
            return f"{light_prefix}_SET_BRIGHTNESS"
        if adjust == "颜色":
            return f"{light_prefix}_SET_COLOR"
        if (adjust == "模式" or mode) and kind not in {"ON", "OFF"}:
            return f"{light_prefix}_SET_MODE"
        if not adjust and not mode and kind in {"ON", "OFF"}:
            return f"{light_prefix}_{kind}"
        return None

    if obj in {"遮阳帘", "遮阳板", "遮阳幕", "遮光板", "幕布"}:
        if (adjust in {"幅度", "位置"} or value) and value:
            return "SHADE_SET_POSITION"
        if kind in {"ON", "OFF"}:
            return "SHADE_OPEN" if kind == "ON" else "SHADE_CLOSE"
        return None

    if obj in {"屏幕", "屏", "显示屏", "娱乐屏", "娱乐屏幕", "中控屏", "副驾屏", "大屏", "HUD", "抬头显示"}:
        if adjust == "亮度":
            return "DISPLAY_SET_BRIGHTNESS"
        if adjust in {"位置", "方向", "角度", "幅度"} or kind == "MOVE":
            return "DISPLAY_SET_POSITION"
        if not adjust and kind in {"ON", "OFF"}:
            return f"DISPLAY_{kind}"
        return None

    if obj in {"香氛", "香薰", "芳香"}:
        if (adjust == "模式" or mode) and kind not in {"ON", "OFF"}:
            return "FRAGRANCE_SET_MODE"
        if kind not in {"ON", "OFF"} and (adjust or value):
            return "FRAGRANCE_SET_LEVEL"
        if not adjust and not mode and kind in {"ON", "OFF"}:
            return f"FRAGRANCE_{kind}"
        return None

    if obj == "方向盘" and feature == "加热":
        return f"STEERING_WHEEL_HEATING_{kind}" if kind in {"ON", "OFF"} and not adjust else None

    if obj in {"扶手", "扶手台"}:
        if kind in {"ADJUST", "MOVE"} or adjust in {"位置", "方向", "幅度"} or value:
            return "ARMREST_SET_POSITION"
        return None

    if obj in {"冰箱", "冷藏箱"}:
        if adjust == "温度":
            return "REFRIGERATOR_SET_TEMPERATURE"
        if not adjust and kind in {"ON", "OFF"}:
            return f"REFRIGERATOR_{kind}"
        return None

    if obj in {"空气净化器", "净化器", "空气净化", "空气净化功能"} or feature in {"空气净化", "净化"}:
        if (adjust == "模式" or mode) and kind not in {"ON", "OFF"}:
            return "AIR_PURIFIER_SET_MODE"
        if kind in {"ON", "OFF"}:
            return f"AIR_PURIFIER_{kind}"
        return None

    if obj in {"天幕", "玻璃天幕", "天窗", "玻璃"} and adjust in {"透光度", "透明度"}:
        return "GLASS_ROOF_SET_TRANSPARENCY"

    if adjust == "音量":
        return "MEDIA_VOLUME_SET"
    if adjust in {"音效", "音效模式"} or frame.first("音效"):
        return "MEDIA_SOUND_EFFECT_SET"

    if feature in {"蓝牙", "热点", "WIFI"}:
        prefix = "BLUETOOTH" if feature == "蓝牙" else "HOTSPOT"
        return f"{prefix}_{kind}" if kind in {"ON", "OFF"} else None
    if feature == "儿童锁":
        return f"CHILD_LOCK_{kind}" if kind in {"ON", "OFF"} else None

    if obj == "摄像头" or adjust == "摄像头模式" or frame.first("摄像头模式"):
        if adjust == "摄像头模式" or frame.first("摄像头模式"):
            return "CAMERA_SET_MODE"
        if kind in {"ON", "OFF"}:
            return f"CAMERA_{kind}"
        return None

    if "行车记录" in text:
        if mode or adjust == "模式":
            return "DRIVING_RECORDER_SET_MODE"
        if kind in {"ON", "OFF"}:
            return f"DRIVING_RECORDER_{kind}"
        return None

    if "驾驶模式" in frame.split_sentence or (obj == "驾驶" and adjust == "模式"):
        return "DRIVING_MODE_SET" if (mode or value) and kind in {"ADJUST", "OTHER"} else None
    return None


def is_approved_family_frame(frame: SourceFrame) -> bool:
    text = frame.combined_text()
    obj = _object(frame)
    feature = _function(frame)
    return (
        obj in {
            "前备箱", "前备厢", "空调", "座椅", "阅读灯", "车内灯", "室内灯", "顶灯", "氛围灯",
            "遮阳帘", "遮阳板", "遮阳幕", "遮光板", "幕布", "屏幕", "屏", "显示屏", "娱乐屏", "娱乐屏幕",
            "中控屏", "副驾屏", "大屏", "HUD", "抬头显示", "香氛", "香薰", "芳香", "方向盘", "扶手", "扶手台",
            "冰箱", "冷藏箱", "空气净化器", "净化器", "空气净化", "空气净化功能", "天幕", "玻璃天幕", "玻璃", "摄像头",
        }
        or feature in {"加热", "通风", "按摩", "蓝牙", "热点", "WIFI", "儿童锁", "空气净化", "净化"}
        or _adjust(frame) in {"音量", "音效", "音效模式", "摄像头模式"}
        or any(term in text for term in ("行车记录", "驾驶模式"))
    )


def is_adas_frame(frame: SourceFrame) -> bool:
    function_text = "|".join(frame.values("功能") + frame.values("子功能"))
    text = f"{frame.split_sentence}|{function_text}"
    return any(term in text for term in ADAS_TERMS)


def is_core_covered(frame: SourceFrame) -> bool:
    text = frame.combined_text()
    return any(term in text for term in CORE_TERMS)


def _deduplicate(frames: Iterable[SourceFrame]) -> list[SourceFrame]:
    values: dict[tuple[str, str, str], SourceFrame] = {}
    for frame in frames:
        values[frame.evidence_key()] = frame
    return sorted(values.values(), key=lambda item: (item.source_file, item.source_id, item.intent_key))


def evidence_summary(intent_id: str, frames: Iterable[SourceFrame]) -> dict[str, Any]:
    unique = _deduplicate(frames)
    mode_values = sorted({value for frame in unique for value in [_mode_value(frame)] if value})
    return {
        "intent_id": intent_id,
        "unique_sample_count": len(unique),
        "source_files": sorted({frame.source_file for frame in unique}),
        "mac_intent_values": dict(sorted(Counter(frame.first("intent") for frame in unique).items())),
        "raw_operations": dict(sorted(Counter(frame.first("操作") for frame in unique).items())),
        "raw_objects": sorted({frame.first("对象") for frame in unique if frame.first("对象")}),
        "raw_object_functions": sorted({frame.first("对象功能") for frame in unique if frame.first("对象功能")}),
        "raw_adjustments": sorted({frame.first("调节内容") for frame in unique if frame.first("调节内容")}),
        "source_mode_values": mode_values,
        "examples": [frame.to_report() for frame in unique[:5]],
        "all_evidence_keys": [
            {"source_file": frame.source_file, "source_id": frame.source_id, "intent_key": frame.intent_key}
            for frame in unique
        ],
    }


def _candidate_action(frame: SourceFrame) -> str:
    kind = operation_kind(frame)
    return {"ON": "TURN_ON", "OFF": "TURN_OFF", "MOVE": "ADJUST", "ADJUST": "SET"}.get(kind, "REVIEW")


def _candidate_target(frame: SourceFrame, prefix: str) -> str:
    raw = frame.first("子功能") or frame.first("功能") or frame.first("对象功能") or frame.first("对象")
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10].upper()
    return f"{prefix}_CANDIDATE_{digest}"


def _candidate_groups(frames: Iterable[SourceFrame], *, adas: bool) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[SourceFrame]] = defaultdict(list)
    for frame in frames:
        key = (
            frame.first("对象"),
            frame.first("对象功能"),
            frame.first("功能"),
            frame.first("子功能"),
            operation_kind(frame),
            frame.first("调节内容"),
        )
        groups[key].append(frame)
    items: list[dict[str, Any]] = []
    for key, group in sorted(groups.items()):
        unique = _deduplicate(group)
        representative = unique[0]
        target = _candidate_target(representative, "ADAS" if adas else "KNOWN_CONTROL")
        action = _candidate_action(representative)
        conflict_ids: list[str] = []
        combined = "|".join(key)
        if any(term in combined for term in ("车道", "变道")):
            conflict_ids.extend(["LANE_CHANGE", "LANE_KEEP"])
        if any(term in combined for term in ("制动", "碰撞")):
            conflict_ids.extend(["BRAKE", "EMERGENCY_BRAKE"])
        if "泊车" in combined or "停车" in combined:
            conflict_ids.append("AUTO_PARK_ENABLE")
        if "巡航" in combined:
            conflict_ids.extend(["CRUISE_ENABLE", "CRUISE_DISABLE", "CRUISE_SET_SPEED", "CRUISE_SET_GAP"])
        items.append({
            "mac_raw_object": key[0],
            "mac_raw_object_function": key[1],
            "mac_raw_function": key[2],
            "mac_raw_subfunction": key[3],
            "mac_raw_operation": sorted({frame.first("操作") for frame in unique if frame.first("操作")}),
            "normalized_operation_kind": key[4],
            "mac_raw_adjustment": key[5],
            "unique_sample_count": len(unique),
            "examples": [frame.to_report() for frame in unique[:5]],
            "formal_neighbor_conflict": bool(conflict_ids),
            "formal_neighbor_intent_ids": sorted(set(conflict_ids)),
            "suggested_intent_id": f"{target}_{action}",
            "suggested_action": action,
            "suggested_target": target,
            "suggested_control_attribute": "STATE" if action in {"TURN_ON", "TURN_OFF"} else "SETTING",
            "suggested_slots": ["VALUE"] if key[5] else [],
            "approval_status": "PENDING",
        })
    return items


def build_evidence(frames: list[SourceFrame]) -> dict[str, Any]:
    approved: dict[str, list[SourceFrame]] = defaultdict(list)
    adas_frames: list[SourceFrame] = []
    other_frames: list[SourceFrame] = []
    approved_unresolved: list[SourceFrame] = []
    for frame in frames:
        intent_id = classify_approved(frame)
        if intent_id:
            approved[intent_id].append(frame)
            continue
        if is_adas_frame(frame):
            adas_frames.append(frame)
            continue
        if is_approved_family_frame(frame):
            approved_unresolved.append(frame)
            continue
        mac_intent = frame.first("intent")
        if mac_intent in {"车身控制", "车机控制"} and frame.first("操作") and not is_core_covered(frame):
            if frame.first("对象") or frame.first("对象功能") or frame.first("功能"):
                other_frames.append(frame)

    approved_summaries = {
        intent_id: evidence_summary(intent_id, values)
        for intent_id, values in sorted(approved.items())
    }
    other_candidates = _candidate_groups([*approved_unresolved, *other_frames], adas=False)
    other_candidates.insert(0, {
        "mac_raw_object": "前备箱/前备厢",
        "mac_raw_object_function": "",
        "mac_raw_function": "",
        "mac_raw_subfunction": "",
        "mac_raw_operation": ["关闭"],
        "normalized_operation_kind": "OFF",
        "mac_raw_adjustment": "",
        "unique_sample_count": 0,
        "examples": [],
        "formal_neighbor_conflict": False,
        "formal_neighbor_intent_ids": [],
        "suggested_intent_id": "FRUNK_CLOSE",
        "suggested_action": "CLOSE",
        "suggested_target": "FRUNK",
        "suggested_control_attribute": "OPENING_STATE",
        "suggested_slots": [],
        "approval_status": "PENDING_NO_REAL_DATA_EVIDENCE",
    })
    return {
        "approved": approved_summaries,
        "adas_candidates": _candidate_groups(adas_frames, adas=True),
        "other_candidates": other_candidates,
        "metrics": {
            "source_control_frame_count": len(frames),
            "approved_intent_count": len(approved_summaries),
            "approved_unique_evidence_count": sum(item["unique_sample_count"] for item in approved_summaries.values()),
            "adas_candidate_group_count": len(_candidate_groups(adas_frames, adas=True)),
            "other_candidate_group_count": len(other_candidates),
        },
    }
