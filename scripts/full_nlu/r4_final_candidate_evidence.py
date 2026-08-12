"""Evidence helpers for the approved R4 final semantic-consistency patch.

Only the eight explicitly approved intents are classified here.  The module
also reconstructs family-level AREA evidence and cleans MEDIA/CAMERA mode
evidence from the original MAC frames.  It never reads or mutates mappings.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable

from r4_known_unsupported_evidence import SourceFrame


APPROVED_NEW_INTENT_IDS = [
    "AIR_PURIFIER_SET_FAN_SPEED",
    "DISPLAY_SET_MODE",
    "READING_LIGHT_SET_MODE",
    "REFRIGERATOR_SET_MODE",
    "FRAGRANCE_SET_SCENT",
    "INTERIOR_LIGHT_SET_BRIGHTNESS",
    "INTERIOR_LIGHT_SET_COLOR",
    "INTERIOR_LIGHT_SET_MODE",
]

AREA_FAMILIES = [
    "HVAC",
    "READING_LIGHT",
    "INTERIOR_LIGHT",
    "AMBIENT_LIGHT",
    "DISPLAY",
    "SEAT_HEATING",
    "SEAT_VENTILATION",
    "SEAT_MASSAGE",
    "SHADE",
]

DISPLAY_OBJECTS = {
    "屏幕", "屏", "显示屏", "娱乐屏", "娱乐屏幕", "中控屏", "中控屏幕", "副驾屏", "副驾屏幕",
    "大屏", "大屏幕", "HUD", "抬头显示", "仪表屏", "主屏幕", "副屏", "吸顶屏", "娱乐主机显示屏",
}
PURIFIER_OBJECTS = {"空气净化器", "净化器", "空气净化", "空气净化功能"}
REFRIGERATOR_OBJECTS = {"冰箱", "冷藏箱", "车载冰箱"}
FRAGRANCE_OBJECTS = {"香氛", "香薰", "芳香"}
SHADE_OBJECTS = {"遮阳帘", "遮阳板", "遮阳屏", "遮光板", "幕布"}

READING_LIGHT_TYPES = {"阅读灯"}
AMBIENT_LIGHT_TYPES = {"氛围灯", "面发光氛围灯"}
INTERIOR_LIGHT_TYPES = {
    "车内灯", "室内灯", "表面灯", "礼貌灯", "交互灯", "线条灯", "星空顶", "星空穹顶",
    "轮廓灯", "装饰灯", "顶灯", "头顶灯光", "面发光灯", "护眼灯",
}

# Only explicit catalog normalizations are allowed.  Anything else is pending.
AREA_ALIASES = {
    "主驾": "LEFT_FRONT", "主驾驶": "LEFT_FRONT", "主驾驶位": "LEFT_FRONT", "驾驶位": "LEFT_FRONT", "驾驶位置": "LEFT_FRONT",
    "主驾驶座": "LEFT_FRONT", "主驾位置": "LEFT_FRONT", "驾驶座": "LEFT_FRONT", "驾驶员": "LEFT_FRONT", "驾驶席": "LEFT_FRONT",
    "正驾驶": "LEFT_FRONT", "司机": "LEFT_FRONT", "左前": "LEFT_FRONT",
    "副驾": "RIGHT_FRONT", "副驾驶": "RIGHT_FRONT", "副驾驶位": "RIGHT_FRONT", "副驾区域": "RIGHT_FRONT", "右前": "RIGHT_FRONT",
    "左后": "LEFT_REAR", "左后排": "LEFT_REAR", "后左": "LEFT_REAR", "左侧后排": "LEFT_REAR", "二排左": "LEFT_REAR",
    "右后": "RIGHT_REAR", "右后排": "RIGHT_REAR", "右后侧": "RIGHT_REAR", "右后方": "RIGHT_REAR", "右侧后部": "RIGHT_REAR",
    "后排右": "RIGHT_REAR", "二排右边": "RIGHT_REAR", "第二排右边": "RIGHT_REAR",
    "前排中间": "MIDDLE_FRONT", "前排中座": "MIDDLE_FRONT",
    "后排中间": "MIDDLE_REAR", "后排中座": "MIDDLE_REAR",
    "前排": "FRONT_ROW", "一排": "FRONT_ROW", "第一排": "FRONT_ROW", "主副驾": "FRONT_ROW", "主副驾驶": "FRONT_ROW",
    "主驾副驾": "FRONT_ROW", "主驾和副驾": "FRONT_ROW", "主驾驶副驾驶": "FRONT_ROW", "主副驾侧": "FRONT_ROW",
    "后排": "REAR_ROW", "后座": "REAR_ROW", "第二排": "REAR_ROW", "二排": "REAR_ROW", "后排座": "REAR_ROW", "后排后排": "REAR_ROW",
    "左侧": "LEFT_SIDE", "左边": "LEFT_SIDE", "右侧": "RIGHT_SIDE", "右边": "RIGHT_SIDE",
    "全部": "ALL", "所有": "ALL", "全车": "ALL", "整车": "ALL", "all": "ALL",
    "前": "FRONT", "前面": "FRONT", "前部": "FRONT",
    "后": "REAR", "后面": "REAR", "后部": "REAR", "后舱": "REAR",
}

MEDIA_FORBIDDEN_TERMS = {
    "车外行人警示", "行人警示", "交通标志", "盲区", "车道偏离", "ADAS", "摄像头", "快门",
    "礼让", "让行", "让路", "借过提醒", "蜂鸣", "发动机声", "发动机启动声", "拖拉机", "跑车发动机",
}
MEDIA_FORBIDDEN_VALUES = {
    "一", "二", "三", "斑马线礼让", "让行感谢", "让路感谢", "拍摄快门声", "蜂鸣", "蜂鸣模式",
}
MEDIA_PROOF_TERMS = {"媒体音效", "音效模式", "音效", "声场", "声音均衡器", "均衡器", "音响", "音乐"}

CAMERA_SELECTION_TERMS = {"切换", "模式", "导航至"}
CAMERA_DIRECT_ACTION_VALUES = {
    "拍个照片", "拍张照", "拍摄视频", "录制", "录像", "拍照", "照片", "照相", "视频录制",
    "录音", "录音功能", "录像录音功能", "张照片", "拍摄视频", "短视频拍摄",
}


def _light_family(frame: SourceFrame) -> str | None:
    raw_type = frame.first("车内灯类型")
    obj = frame.first("对象")
    # Explicit object wins when the type slot itself is malformed (for example
    # the real frame whose type value is "稍微" but object is "表面灯").
    candidates = [raw_type, obj]
    if any(value in READING_LIGHT_TYPES for value in candidates):
        return "READING_LIGHT"
    if any(value in AMBIENT_LIGHT_TYPES for value in candidates):
        return "AMBIENT_LIGHT"
    if any(value in INTERIOR_LIGHT_TYPES for value in candidates):
        return "INTERIOR_LIGHT"
    return None


def _is_display_mode(frame: SourceFrame) -> bool:
    if frame.first("对象") not in DISPLAY_OBJECTS:
        return False
    if frame.first("调节内容") != "模式" and not frame.first("模式"):
        return False
    # These three raw frames are audio commands mislabeled with a display object.
    text = frame.split_sentence
    return "声音" not in text and "静音" not in text


def classify_approved_new(frame: SourceFrame) -> str | None:
    obj = frame.first("对象")
    adjust = frame.first("调节内容")
    value = frame.first("value")
    mode = frame.first("模式")
    light_family = _light_family(frame)

    if obj in PURIFIER_OBJECTS and value and adjust not in {"温度", "模式"} and not mode and "度" not in value:
        return "AIR_PURIFIER_SET_FAN_SPEED"
    if _is_display_mode(frame):
        return "DISPLAY_SET_MODE"
    if light_family == "READING_LIGHT" and (adjust == "模式" or mode):
        return "READING_LIGHT_SET_MODE"
    if obj in REFRIGERATOR_OBJECTS and (adjust == "模式" or mode):
        return "REFRIGERATOR_SET_MODE"
    if obj in FRAGRANCE_OBJECTS and adjust in {"香味", "味道"}:
        return "FRAGRANCE_SET_SCENT"
    if light_family == "INTERIOR_LIGHT" and adjust == "亮度":
        return "INTERIOR_LIGHT_SET_BRIGHTNESS"
    if light_family == "INTERIOR_LIGHT" and adjust == "颜色":
        return "INTERIOR_LIGHT_SET_COLOR"
    if light_family == "INTERIOR_LIGHT" and (adjust == "模式" or mode):
        return "INTERIOR_LIGHT_SET_MODE"
    return None


def _mode_value(frame: SourceFrame) -> str:
    return frame.first("模式") or frame.first("摄像头模式") or frame.first("音效") or frame.first("value")


def _report_group(intent_id: str, frames: list[SourceFrame]) -> dict[str, Any]:
    unique = sorted({frame.evidence_key(): frame for frame in frames}.values(), key=lambda frame: frame.evidence_key())
    return {
        "intent_id": intent_id,
        "unique_sample_count": len(unique),
        "source_file_counts": dict(sorted(Counter(frame.source_file for frame in unique).items())),
        "source_mode_values": sorted({value for frame in unique if (value := _mode_value(frame))}),
        "source_value_values": sorted({frame.first("value") for frame in unique if frame.first("value")}),
        "evidence_keys": [list(frame.evidence_key()) for frame in unique],
        "examples": [frame.to_report() for frame in unique[:5]],
    }


def build_approved_new_evidence(frames: Iterable[SourceFrame]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[SourceFrame]] = defaultdict(list)
    for frame in frames:
        intent_id = classify_approved_new(frame)
        if intent_id:
            grouped[intent_id].append(frame)
    return {intent_id: _report_group(intent_id, grouped[intent_id]) for intent_id in APPROVED_NEW_INTENT_IDS}


def area_family(frame: SourceFrame) -> str | None:
    obj = frame.first("对象")
    feature = frame.first("对象功能")
    light_family = _light_family(frame)
    if obj == "空调":
        return "HVAC"
    if light_family:
        return light_family
    if obj in DISPLAY_OBJECTS:
        return "DISPLAY"
    if obj == "座椅" and feature in {"加热", "通风", "按摩"}:
        return {"加热": "SEAT_HEATING", "通风": "SEAT_VENTILATION", "按摩": "SEAT_MASSAGE"}[feature]
    if obj in SHADE_OBJECTS:
        return "SHADE"
    return None


def build_area_evidence(frames: Iterable[SourceFrame], area_catalog: dict[str, Any]) -> dict[str, Any]:
    aliases = dict(AREA_ALIASES)
    for area_id, item in area_catalog.items():
        aliases[str(item.get("semantic_frame_value", ""))] = area_id
        for example in item.get("examples", []):
            aliases[str(example)] = area_id
    order = list(area_catalog)
    mapped: dict[str, set[str]] = defaultdict(set)
    pending: dict[str, dict[str, list[SourceFrame]]] = defaultdict(lambda: defaultdict(list))
    raw_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for frame in frames:
        family = area_family(frame)
        if family not in AREA_FAMILIES:
            continue
        for raw in frame.values("位置"):
            normalized = raw.strip().rstrip("的")
            raw_counts[family][normalized] += 1
            area_id = aliases.get(normalized)
            if area_id in area_catalog:
                mapped[family].add(area_id)
            else:
                pending[family][normalized].append(frame)
    result: dict[str, Any] = {}
    for family in AREA_FAMILIES:
        pending_items = []
        for raw, evidence in sorted(pending[family].items()):
            unique = sorted({frame.evidence_key(): frame for frame in evidence}.values(), key=lambda frame: frame.evidence_key())
            pending_items.append({
                "raw_area": raw,
                "unique_sample_count": len(unique),
                "status": "AREA_PENDING_REPORT",
                "reason": "NO_APPROVED_AREA_CATALOG_MAPPING",
                "examples": [frame.to_report() for frame in unique[:3]],
            })
        result[family] = {
            "allowed_areas": [area_id for area_id in order if area_id in mapped[family]],
            "raw_area_counts": dict(sorted(raw_counts[family].items())),
            "pending": pending_items,
        }
    return result


def build_media_mode_evidence(frames: Iterable[SourceFrame]) -> dict[str, Any]:
    accepted: list[SourceFrame] = []
    pending: list[tuple[SourceFrame, str]] = []
    for frame in frames:
        if frame.first("调节内容") not in {"音效", "音效模式"} and not frame.first("音效"):
            continue
        value = frame.first("音效") or frame.first("模式") or frame.first("value")
        text = frame.split_sentence
        if not value:
            pending.append((frame, "MISSING_MODE_VALUE"))
        elif value in MEDIA_FORBIDDEN_VALUES or any(term in text or term in value for term in MEDIA_FORBIDDEN_TERMS):
            pending.append((frame, "NON_MEDIA_SOURCE_OBJECT"))
        elif not any(term in text for term in MEDIA_PROOF_TERMS):
            pending.append((frame, "MEDIA_SOURCE_NOT_UNIQUELY_PROVEN"))
        else:
            accepted.append(frame)
    unique_accepted = sorted({frame.evidence_key(): frame for frame in accepted}.values(), key=lambda frame: frame.evidence_key())
    pending_groups: dict[tuple[str, str], list[SourceFrame]] = defaultdict(list)
    for frame, reason in pending:
        pending_groups[(frame.first("音效") or frame.first("模式") or frame.first("value"), reason)].append(frame)
    return {
        "mode_values": sorted({frame.first("音效") or frame.first("模式") or frame.first("value") for frame in unique_accepted}),
        "accepted_unique_sample_count": len(unique_accepted),
        "accepted_examples": [frame.to_report() for frame in unique_accepted[:5]],
        "pending": [
            {
                "raw_value": value,
                "reason": reason,
                "status": "PENDING_SOURCE_OBJECT_AMBIGUITY",
                "unique_sample_count": len({frame.evidence_key() for frame in evidence}),
                "examples": [frame.to_report() for frame in evidence[:3]],
            }
            for (value, reason), evidence in sorted(pending_groups.items())
        ],
    }


def build_camera_mode_evidence(frames: Iterable[SourceFrame]) -> dict[str, Any]:
    accepted: list[SourceFrame] = []
    pending: list[SourceFrame] = []
    for frame in frames:
        if frame.first("调节内容") != "摄像头模式" and not frame.first("摄像头模式"):
            continue
        value = frame.first("摄像头模式")
        text = frame.split_sentence
        explicit_selection = any(term in text for term in CAMERA_SELECTION_TERMS)
        if value and explicit_selection and value not in CAMERA_DIRECT_ACTION_VALUES:
            accepted.append(frame)
        else:
            pending.append(frame)
    unique_accepted = sorted({frame.evidence_key(): frame for frame in accepted}.values(), key=lambda frame: frame.evidence_key())
    unique_pending = sorted({frame.evidence_key(): frame for frame in pending}.values(), key=lambda frame: frame.evidence_key())
    return {
        "mode_values": sorted({frame.first("摄像头模式") for frame in unique_accepted if frame.first("摄像头模式")}),
        "accepted_unique_sample_count": len(unique_accepted),
        "accepted_examples": [frame.to_report() for frame in unique_accepted[:5]],
        "camera_action_pending": {
            "status": "PENDING_NO_AUTO_INTENT_CREATION",
            "unique_sample_count": len(unique_pending),
            "raw_values": sorted({frame.first("摄像头模式") for frame in unique_pending if frame.first("摄像头模式")}),
            "examples": [frame.to_report() for frame in unique_pending[:10]],
        },
    }


def build_final_patch_evidence(frames: list[SourceFrame], area_catalog: dict[str, Any]) -> dict[str, Any]:
    return {
        "approved_new_intents": build_approved_new_evidence(frames),
        "family_area_evidence": build_area_evidence(frames, area_catalog),
        "media_mode_evidence": build_media_mode_evidence(frames),
        "camera_mode_evidence": build_camera_mode_evidence(frames),
    }
