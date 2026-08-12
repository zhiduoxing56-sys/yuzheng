"""Build the traceable Full NLU R3 canonical raw baseline without training or splitting.

This program never edits raw sources. It consumes the read-only spreadsheet extraction
created by inspect_seed_workbooks.mjs and writes only derived assets below data/nlu/full.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import yaml

from validate_full_nlu_schema import validate_paths


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "data/nlu/spec/intent_registry_r3.yaml"
RULES_PATH = ROOT / "data/nlu/full/rules/full_nlu_mapping_v2.yaml"
COGNITION_PATH = ROOT / "data/nlu/full/rules/known_unsupported_cognition_v1.yaml"
OVERRIDES_PATH = ROOT / "data/nlu/full/rules/manual_overrides_v1.json"
SCHEMA_PATH = ROOT / "data/nlu/full/schema/full_nlu_sample_schema_v1.json"
EXTRACTED_WORKBOOKS_PATH = ROOT / "data/nlu/full/workbench/seed_workbooks_extracted.json"
OUT = ROOT / "data/nlu/full/baseline_v1"

REGISTRY_VERSION = "sys-014-semantic-hardening-r3"
REGISTRY_SHA256 = "c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06"
MAPPING_VERSION = "nlu_mapping_v2"
SCHEMA_VERSION = "full_nlu_sample_schema_v1"
OVERRIDE_VERSION = "manual_override_v1"
CONVERSION_VERSION = "full_nlu_baseline_v1"

MAC_EXPECTED = {"train_set.jsonl": 18000, "dev_set.jsonl": 1391, "test_set.jsonl": 1151}
SOURCE_NAME = {
    "weak": "人工弱覆盖种子",
    "safety": "人工安全边界种子",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(source: str, file_name: str, source_id: str, raw_text: str) -> str:
    key = "\x1f".join((CONVERSION_VERSION, source, file_name, source_id, raw_text))
    return f"fnlu-{hashlib.sha256(key.encode('utf-8')).hexdigest()[:24]}"


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", " ", text).strip()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def require_sha(path: Path, expected: str, label: str) -> None:
    actual = sha256_path(path)
    if actual != expected:
        raise SystemExit(f"HARD_GATE_FAIL {label} SHA256 expected={expected} actual={actual} path={path}")


def parse_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, line in enumerate(handle, start=1):
            try:
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise TypeError("row must be object")
                rows.append(value)
            except Exception as exc:
                errors.append({"line": line_number, "error": str(exc)})
    return rows, errors


def flatten_semantics(row: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    semantics = row.get("semantics")
    if not isinstance(semantics, dict):
        return result
    for intent_key, outer in semantics.items():
        if not isinstance(outer, dict):
            continue
        for domain, items in outer.items():
            if not isinstance(items, list):
                continue
            slots: dict[str, Any] = {}
            duplicate_names: list[str] = []
            for item in items:
                if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                    continue
                name = item["name"]
                if name in slots:
                    duplicate_names.append(name)
                slots[name] = item.get("value")
            result.append({"intent_key": intent_key, "domain": domain, "slots": slots, "duplicate_slot_names": duplicate_names})
    return result


CN_DIGITS = {"零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn_number(value: str) -> int | None:
    if value in CN_DIGITS:
        return CN_DIGITS[value]
    if value == "十":
        return 10
    if "十" in value and all(ch in CN_DIGITS or ch == "十" for ch in value):
        left, right = value.split("十", 1)
        return (CN_DIGITS.get(left, 1) * 10) + CN_DIGITS.get(right, 0)
    return None


def extract_value(text: str, slots: dict[str, Any] | None = None) -> str | int | float | None:
    candidates = []
    if slots:
        for key in ("value", "数值", "幅度", "程度", "速度", "温度", "角度", "开度"):
            value = slots.get(key)
            if value is not None:
                candidates.append(str(value))
    candidates.append(text)
    joined = " ".join(candidates)
    if "一半" in joined or "半开" in joined:
        return "50%"
    match = re.search(r"([一二两三四五六七八九])成", joined)
    if match:
        return f"{CN_DIGITS[match.group(1)] * 10}%"
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", joined)
    if match:
        number = float(match.group(1))
        return f"{int(number) if number.is_integer() else number}%"
    match = re.search(r"百分之([零一二两三四五六七八九十]+)", joined)
    if match and (number := cn_number(match.group(1))) is not None:
        return f"{number}%"
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:公里每小时|千米每小时|km/h)", joined, re.I)
    if match:
        return f"{match.group(1)} km/h"
    match = re.search(r"(?:到|为|成|设|调)(\d+(?:\.\d+)?)\s*(?:度|°)", joined)
    if match:
        return f"{match.group(1)}°"
    match = re.search(r"([一二两三四五六七八九十\d]+)\s*挡", joined)
    if match:
        raw = match.group(1)
        return int(raw) if raw.isdigit() else cn_number(raw)
    return None


AREA_ALIASES = [
    ("LEFT_FRONT", ("左前", "主驾", "驾驶位", "驾驶员")),
    ("RIGHT_FRONT", ("右前", "副驾", "副驾驶")),
    ("LEFT_REAR", ("左后",)),
    ("RIGHT_REAR", ("右后",)),
    ("FRONT_ROW", ("前排",)),
    ("REAR_ROW", ("后排", "后座")),
    ("LEFT_SIDE", ("左侧", "左边")),
    ("RIGHT_SIDE", ("右侧", "右边")),
    ("ALL", ("全车", "全部", "所有", "整车")),
    ("FRONT", ("前挡", "前风挡", "前面", "前部")),
    ("REAR", ("后挡", "后风挡", "后面", "后部")),
]


def extract_area(text: str, slots: dict[str, Any] | None = None) -> str | None:
    source = " ".join(str(v) for v in (slots or {}).values() if v is not None) + " " + text
    for canonical, aliases in AREA_ALIASES:
        if any(alias in source for alias in aliases):
            return canonical
    return None


def extract_lr(text: str) -> str | None:
    if any(token in text for token in ("向左", "往左", "左侧", "左边", "左车道")):
        return "LEFT"
    if any(token in text for token in ("向右", "往右", "右侧", "右边", "右车道")):
        return "RIGHT"
    return None


def polarity(text: str) -> str:
    if re.search(r"取消|撤销|算了|不用.*了|不用了", text):
        return "取消"
    if re.search(r"不要|千万别|先别|别", text):
        return "否定"
    return "肯定"


class Resolver:
    def __init__(self, registry: dict[str, Any], rules: dict[str, Any], cognition: dict[str, Any]):
        self.registry = registry
        self.rules = rules
        self.cognition = cognition
        self.by_id = {item["intent_id"]: item for item in registry["intents"]}
        self.by_name = {item["chinese_name"]: item["intent_id"] for item in registry["intents"]}
        self.formal = set(registry["formal_user_voice_intent_ids"])
        self.unsupported = set(registry["known_unsupported_control_intent_ids"])
        self.cabin = cognition["extended_cabin_capabilities"]

    def subintent(self, intent_id: str, slots: dict[str, Any] | None = None) -> dict[str, Any]:
        item = self.by_id[intent_id]
        slots = slots or {}
        return {
            "规范动作": item["canonical_action"],
            "规范对象": item["canonical_target"],
            "控制属性": item["control_attribute"],
            "位置": slots.get("AREA"),
            "数值": slots.get("VALUE"),
            "方向": slots.get("DIRECTION"),
            "模式": slots.get("MODE"),
        }

    def complete(self, intent_id: str, slots: dict[str, Any]) -> bool:
        item = self.by_id[intent_id]
        if intent_id in {"STEERING_WHEEL_SET_EXTENSION", "STEERING_WHEEL_SET_TILT"}:
            return slots.get("VALUE") is not None or slots.get("DIRECTION") is not None
        if intent_id == "CRUISE_SET_GAP":
            return slots.get("VALUE") is not None or slots.get("MODE") is not None
        return all(slots.get(slot) is not None for slot in item.get("required_slots", []))

    @staticmethod
    def state_action(text: str) -> str | None:
        if re.search(r"关闭|关掉|关上|关了|停用|禁用|停止|关", text):
            return "OFF"
        if re.search(r"打开|开启|启用|启动|开一下|开着|切换成|切成|(?:别|不要|不用|先别)?开(?=车?门|门|前舱盖|巡航|驻车灯|大灯|灯|车窗|窗|空调)", text):
            return "ON"
        return None

    def directions(self, intent_id: str, text: str) -> str | None:
        if intent_id in {"LANE_CHANGE", "EVASIVE_STEER", "TURN_INDICATOR_ON", "TURN_INDICATOR_OFF"}:
            return extract_lr(text)
        if intent_id == "STEERING_WHEEL_SET_EXTENSION":
            mapping = self.rules["steering_wheel_semantics"][intent_id]["direction_aliases"]
        elif intent_id == "STEERING_WHEEL_SET_TILT":
            mapping = self.rules["steering_wheel_semantics"][intent_id]["direction_aliases"]
        elif intent_id in {"SEAT_LONGITUDINAL_SET_POSITION", "SEAT_TILT_SET_ANGLE", "SEAT_BACKREST_SET_ANGLE"}:
            mapping = {"FORWARD": ["往前", "向前", "前移", "前倒"], "BACKWARD": ["往后", "向后", "后移", "后倒", "放倒"]}
        elif intent_id in {"SEAT_HEIGHT_SET_POSITION", "SEAT_LUMBAR_SET_HEIGHT"}:
            mapping = {"UP": ["往上", "向上", "升高", "调高"], "DOWN": ["往下", "向下", "降低", "调低"]}
        elif intent_id == "SEAT_LUMBAR_SET_SUPPORT":
            mapping = {"MORE": ["更强", "顶一点", "增加"], "LESS": ["弱一点", "少一点", "降低"]}
        elif intent_id == "SUNROOF_SET_TILT":
            mapping = {"UP": ["翘起", "上翘", "抬起"], "DOWN": ["下收", "收下", "放下"]}
        else:
            return None
        for direction, aliases in mapping.items():
            if any(alias in text for alias in aliases):
                return direction
        return None

    @staticmethod
    def gear_mode(text: str) -> str | None:
        upper = text.upper()
        for letter in ("P", "N", "D", "R"):
            if re.search(rf"(?<![A-Z]){letter}\s*挡", upper):
                return letter
        if "倒挡" in text or "倒车挡" in text:
            return "R"
        if "停车挡" in text or "驻车挡" in text:
            return "P"
        match = re.search(r"([1-9]\d*)\s*挡", text)
        if match:
            number = match.group(1)
            return f"REVERSE_GEAR_{number}" if "倒" in text else f"FORWARD_GEAR_{number}"
        return None

    def infer_registry(self, text: str, slots: dict[str, Any] | None = None, approved_name: str | None = None) -> dict[str, Any] | None:
        slots = slots or {}
        if approved_name:
            intent_id = self.by_name.get(approved_name) or self.rules.get("approved_weak_seed_intent_aliases", {}).get(approved_name)
            if not intent_id:
                return None
            parsed = self.parse_slots(intent_id, text, slots)
            return self.resolution(intent_id, parsed, "APPROVED_WEAK_SEED_INTENT_NAME")

        state = self.state_action(text)
        intent_id: str | None = None

        # Explicit light rules are evaluated before generic object rules.
        if any(alias in text for alias in self.rules["light_semantics"]["position_light_aliases"]):
            intent_id = "HEADLIGHT_SET_MODE"
        elif any(alias in text for alias in self.rules["light_semantics"]["parking_light_aliases"]):
            intent_id = "PARKING_LIGHT_OFF" if state == "OFF" else "PARKING_LIGHT_ON" if state == "ON" else None
        elif "近光灯" in text or "近光" in text:
            intent_id = "LOW_BEAM_OFF" if state == "OFF" else "LOW_BEAM_ON" if state == "ON" else None
        elif "远光灯" in text or "远光" in text:
            intent_id = "HIGH_BEAM_OFF" if state == "OFF" else "HIGH_BEAM_ON" if state == "ON" else None
        elif "雾灯" in text:
            intent_id = "FOG_LIGHT_OFF" if state == "OFF" else "FOG_LIGHT_ON" if state == "ON" else None
        elif "双闪" in text or "危险警示灯" in text:
            intent_id = "HAZARD_LIGHT_OFF" if state == "OFF" else "HAZARD_LIGHT_ON" if state == "ON" else None
        elif "转向灯" in text:
            intent_id = "TURN_INDICATOR_OFF" if state == "OFF" else "TURN_INDICATOR_ON" if state == "ON" else None
        elif "大灯" in text or "主灯" in text:
            if state == "OFF":
                intent_id = "HEADLIGHT_SET_MODE"
            elif state == "ON":
                intent_id = "HEADLIGHT_SET_MODE"
        elif any(alias in text for alias in self.rules["light_semantics"]["broad_ambiguous_objects"]):
            return {"status": "AMBIGUOUS", "reason": "BROAD_LIGHT_OBJECT", "candidate_scope": "正式可执行"}

        if intent_id is None:
            object_hint = str(slots.get("对象") or "")
            feature_hint = str(slots.get("对象功能") or "")
            adjust_hint = str(slots.get("调节内容") or "")
            combined = " ".join((text, object_hint, feature_hint, adjust_hint))
            state = state or self.state_action(combined)
            has_value = extract_value(text, slots) is not None
            if any(token in combined for token in ("车窗", "窗户", "车玻璃", "主驾玻璃", "副驾玻璃")):
                intent_id = "WINDOW_SET_POSITION" if has_value or any(x in adjust_hint for x in ("幅度", "开度")) or re.search(r"开条缝|留条缝|开度|那个程度", text) else "WINDOW_CLOSE" if state == "OFF" else "WINDOW_OPEN" if state == "ON" or re.search(r"降下|摇下", text) else None
            elif "车门" in combined or re.search(r"(?:前|后|左|右)门", text):
                intent_id = "DOOR_SET_POSITION" if has_value or any(x in adjust_hint for x in ("幅度", "开度")) or re.search(r"开度|那个程度", text) else "DOOR_UNLOCK" if "解锁" in text else "DOOR_LOCK" if "锁" in text else "DOOR_CLOSE" if state == "OFF" else "DOOR_OPEN" if state == "ON" else None
            elif any(token in combined for token in ("后备箱", "后备厢", "尾门", "行李厢", "行李箱")):
                intent_id = "TRUNK_SET_POSITION" if has_value else "TRUNK_UNLOCK" if "解锁" in text else "TRUNK_LOCK" if "锁" in text else "TRUNK_CLOSE" if state == "OFF" else "TRUNK_OPEN" if state == "ON" else None
            elif any(token in combined for token in ("前舱盖", "机盖", "引擎盖", "车头盖", "前备厢", "前备箱", "前储物箱")):
                intent_id = "HOOD_SET_POSITION" if has_value else "HOOD_CLOSE" if state == "OFF" else "HOOD_OPEN" if state == "ON" or "掀开" in text else None
            elif "天窗" in combined:
                intent_id = "SUNROOF_SET_TILT" if any(x in text for x in ("翘", "下收")) else "SUNROOF_CLOSE" if state == "OFF" else "SUNROOF_OPEN" if state == "ON" else None
            elif "后视镜" in combined or "外后视镜" in combined:
                if "加热" in combined:
                    intent_id = "MIRROR_HEATING_OFF" if state == "OFF" else "MIRROR_HEATING_ON" if state == "ON" else None
                elif "折叠" in combined or "收起" in combined:
                    intent_id = "MIRROR_FOLD"
                elif "展开" in combined:
                    intent_id = "MIRROR_UNFOLD"
                elif "锁定调节" in combined:
                    intent_id = "MIRROR_ADJUSTMENT_LOCK"
                elif "解锁调节" in combined:
                    intent_id = "MIRROR_ADJUSTMENT_UNLOCK"
                elif any(x in combined for x in ("角度", "方向", "调整", "调节")):
                    intent_id = "MIRROR_SET_ANGLE"
            elif "方向盘" in combined and "加热" not in combined:
                if any(x in text for x in ("往外", "向外", "伸缩", "伸出", "拉出来", "往里", "向里", "收回", "缩回", "缩进去", "靠近", "离我远")):
                    intent_id = "STEERING_WHEEL_SET_EXTENSION"
                elif any(x in text for x in ("抬高", "升高", "往上", "向上", "降低", "往下", "向下", "高度")):
                    intent_id = "STEERING_WHEEL_SET_TILT"
                else:
                    return {"status": "AMBIGUOUS", "reason": "STEERING_DIMENSION_UNRESOLVED", "candidate_scope": "正式可执行"}
            elif "除霜" in combined or "除雾" in combined:
                intent_id = "DEFROST_OFF" if state == "OFF" else "DEFROST_ON" if state == "ON" else None
            elif ("风挡" in combined or "挡风玻璃" in combined) and "加热" in combined:
                intent_id = "WINDSHIELD_HEATING_OFF" if state == "OFF" else "WINDSHIELD_HEATING_ON" if state == "ON" else None
            elif "雨刮" in combined or "雨刷" in combined:
                intent_id = "WIPER_SET_SENSITIVITY" if "灵敏" in combined else "WIPER_SET_MODE"
            elif "巡航" in combined:
                intent_id = "CRUISE_SET_SPEED" if "速度" in combined or re.search(r"\d+", text) else "CRUISE_SET_GAP" if any(x in combined for x in ("距离", "跟车")) else "CRUISE_DISABLE" if state == "OFF" else "CRUISE_ENABLE" if state == "ON" else None
            elif "电子手刹" in combined or "驻车制动" in combined or "手刹" in combined:
                intent_id = "PARKING_BRAKE_RELEASE" if re.search(r"松|释放|解除|放掉|放开|取消|关闭", text) else "PARKING_BRAKE_APPLY" if re.search(r"拉|施加|启用|打开", text) else None
            elif "自动泊车" in combined:
                intent_id = "AUTO_PARK_ENABLE" if state != "OFF" else None
            elif "鸣笛" in combined or "喇叭" in combined:
                intent_id = "HORN_ACTIVATE" if re.search(r"鸣|按|响|叫|发出", text) else None
            elif re.search(r"急刹|紧急制动|紧急刹|马上刹停|紧急停车", combined):
                intent_id = "EMERGENCY_BRAKE"
            elif re.search(r"刹车|制动|脚刹", combined):
                intent_id = "BRAKE"
            elif re.search(r"减速|慢下来|降低(?:行驶)?速度|车速下降", combined):
                intent_id = "DECELERATE"
            elif re.search(r"降到\s*\d+", combined):
                intent_id = "DECELERATE"
            elif re.search(r"加速|快一些|加快|提高(?:行驶)?速度|提高车速|速度提升", combined):
                intent_id = "ACCELERATE"
            elif re.search(r"避险|躲避|避开|避让|绕开障碍", combined):
                intent_id = "EVASIVE_STEER"
            elif re.search(r"变道|并线|并到|并个道|换个车道|换到.*车道|驶入.*车道|往旁边并", combined):
                intent_id = "LANE_CHANGE"
            elif re.search(r"保持(?:当前|本|原)?车道|维持(?:当前|本|原)?车道", combined):
                intent_id = "LANE_KEEP"
            elif "挡" in combined or "挡位" in combined:
                if "手动" in combined or "自动换挡" in combined or "换挡模式" in combined:
                    intent_id = "GEAR_CHANGE_MODE_SET"
                else:
                    intent_id = "GEAR_SET"
            elif "ESC" in combined.upper() or "车身稳定" in combined or "电子稳定" in combined:
                intent_id = "ESC_DISABLE" if state == "OFF" else "ESC_ENABLE" if state == "ON" else None
            elif "牵引力控制" in combined or "防滑" in combined:
                intent_id = "TCS_DISABLE" if state == "OFF" else "TCS_ENABLE" if state == "ON" else None
            elif "防抱死" in combined or "ABS" in combined.upper():
                intent_id = "ABS_DISABLE" if state == "OFF" else "ABS_ENABLE" if state == "ON" else None

            if intent_id is None and "座椅" in combined or intent_id is None and "靠背" in combined or intent_id is None and "腰托" in combined:
                if any(x in combined for x in ("通风", "按摩", "加热")):
                    return self.infer_cabin(text, slots)
                if "腰托" in combined:
                    intent_id = "SEAT_LUMBAR_SET_HEIGHT" if any(x in combined for x in ("高", "上", "下")) else "SEAT_LUMBAR_SET_SUPPORT"
                elif "靠背" in combined:
                    intent_id = "SEAT_BACKREST_SET_ANGLE"
                elif "高度" in combined or re.search(r"升高|降低|调高|调低", combined):
                    intent_id = "SEAT_HEIGHT_SET_POSITION"
                elif re.search(r"往前|向前|前移|往后|向后|后移", combined):
                    intent_id = "SEAT_LONGITUDINAL_SET_POSITION"

            if intent_id is None and re.search(r"打方向|方向打", combined) and extract_lr(text):
                return {
                    "status": "RESOLVED", "intent_id": "KNOWN::DIRECTIONAL_STEERING", "scope": "已知但不开放",
                    "slots": {}, "subintent": {"规范动作": "STEER", "规范对象": "VEHICLE", "控制属性": "TRAJECTORY",
                    "位置": None, "数值": None, "方向": extract_lr(text), "模式": None},
                    "complete": True, "evidence": "KNOWN_DIRECTIONAL_STEERING_WITHOUT_EVASIVE_SEMANTICS",
                }
            if intent_id is None and re.search(r"保持(?:这个|当前)?速度|维持(?:这个|当前)?速度", combined):
                return {
                    "status": "RESOLVED", "intent_id": "KNOWN::KEEP_SPEED", "scope": "已知但不开放",
                    "slots": {}, "subintent": {"规范动作": "KEEP", "规范对象": "VEHICLE", "控制属性": "SPEED",
                    "位置": None, "数值": extract_value(text, slots), "方向": None, "模式": None},
                    "complete": True, "evidence": "KNOWN_KEEP_SPEED_NOT_IN_R3",
                }
            if intent_id is None and re.search(r"车道保持辅助|车道保持系统", combined):
                action = "DISABLE" if state == "OFF" else "ENABLE" if state == "ON" else None
                if action:
                    return {
                        "status": "RESOLVED", "intent_id": f"KNOWN::LANE_KEEP_ASSIST::{action}", "scope": "已知但不开放",
                        "slots": {}, "subintent": {"规范动作": action, "规范对象": "LANE", "控制属性": "STATE",
                        "位置": None, "数值": None, "方向": None, "模式": None},
                        "complete": True, "evidence": "KNOWN_LANE_KEEP_ASSIST_TOGGLE_NOT_LANE_KEEP_COMMAND",
                    }
            if intent_id is None and ("远光" in combined) and re.search(r"闪一下|闪烁", combined):
                return {
                    "status": "RESOLVED", "intent_id": "KNOWN::HIGH_BEAM_FLASH", "scope": "已知但不开放",
                    "slots": {}, "subintent": {"规范动作": "ACTIVATE", "规范对象": "HIGH_BEAM", "控制属性": "STATE",
                    "位置": None, "数值": None, "方向": None, "模式": None},
                    "complete": True, "evidence": "KNOWN_HIGH_BEAM_FLASH_NOT_STEADY_ON",
                }

        if intent_id:
            parsed = self.parse_slots(intent_id, text, slots)
            return self.resolution(intent_id, parsed, "R3_REGISTRY_RULE")
        return self.infer_cabin(text, slots)

    def parse_slots(self, intent_id: str, text: str, source_slots: dict[str, Any]) -> dict[str, Any]:
        parsed: dict[str, Any] = {
            "AREA": extract_area(text, source_slots),
            "VALUE": extract_value(text, source_slots),
            "DIRECTION": self.directions(intent_id, text),
            "MODE": None,
        }
        if intent_id == "HEADLIGHT_SET_MODE":
            if any(x in text for x in self.rules["light_semantics"]["position_light_aliases"]):
                parsed["MODE"] = "OFF" if self.state_action(text) == "OFF" else "POSITION"
            elif self.state_action(text) == "OFF":
                parsed["MODE"] = "OFF"
            elif self.state_action(text) == "ON":
                parsed["MODE"] = "BEAM"
        elif intent_id == "GEAR_SET":
            parsed["MODE"] = self.gear_mode(text)
        elif intent_id == "GEAR_CHANGE_MODE_SET":
            parsed["MODE"] = "MANUAL" if "手动" in text and not re.search(r"关闭手动|切自动", text) else "AUTOMATIC" if "自动" in text or "切自动" in text else None
        elif intent_id == "WIPER_SET_MODE":
            modes = (("RAIN_SENSOR", ("感应", "雨量")), ("INTERVAL", ("间歇",)), ("FAST", ("快速", "高速", "最快")), ("SLOW", ("慢速", "低速")), ("OFF", ("关闭", "关掉")))
            for mode, aliases in modes:
                if any(alias in text for alias in aliases):
                    parsed["MODE"] = mode
                    break
        elif intent_id == "CRUISE_SET_GAP":
            match = re.search(r"(?:等级|距离)\s*([1-4一二三四])", text)
            if match:
                raw = match.group(1)
                number = int(raw) if raw.isdigit() else cn_number(raw)
                parsed["MODE"] = f"LEVEL_{number}"
            elif re.search(r"远一点|加大", text):
                parsed["VALUE"] = "RELATIVE_FARTHER"
            elif re.search(r"近一点|缩短", text):
                parsed["VALUE"] = "RELATIVE_CLOSER"
        return parsed

    def resolution(self, intent_id: str, slots: dict[str, Any], evidence: str) -> dict[str, Any]:
        return {
            "status": "RESOLVED",
            "intent_id": intent_id,
            "scope": "正式可执行" if intent_id in self.formal else "已知但不开放",
            "slots": slots,
            "subintent": self.subintent(intent_id, slots),
            "complete": self.complete(intent_id, slots),
            "evidence": evidence,
        }

    def infer_cabin(self, text: str, slots: dict[str, Any] | None = None) -> dict[str, Any] | None:
        slots = slots or {}
        combined = text + " " + " ".join(str(v) for v in slots.values() if v is not None)
        matched = None
        for item in self.cabin:
            if any(alias in combined for alias in item["aliases"]):
                matched = item
                break
        if not matched:
            return None
        target = matched["target"]
        if target == "HVAC":
            attribute = "TEMPERATURE" if "温度" in combined else "FAN_SPEED" if any(x in combined for x in ("风速", "风量", "风力")) else "AIR_DIRECTION" if "风向" in combined or "吹" in combined else "MODE" if "模式" in combined or any(x in combined for x in ("循环", "AC", "制冷", "制热")) else "STATE"
        elif target in {"DISPLAY", "AMBIENT_LIGHT"}:
            attribute = "BRIGHTNESS" if "亮度" in combined or "亮" in combined else "COLOR" if "颜色" in combined or re.search(r"红色|蓝色|绿色|紫色|白色", combined) else "POSITION" if re.search(r"移动|滑|往左|往右", combined) else "STATE"
        elif target in {"SEAT_HEATING", "SEAT_VENTILATION", "SEAT_MASSAGE", "FRAGRANCE", "STEERING_WHEEL_HEATING"}:
            attribute = "LEVEL" if re.search(r"挡|级|最大|最小|调", combined) else "STATE"
        elif target == "SUNSHADE":
            attribute = "OPENING_POSITION" if extract_value(text, slots) is not None else "OPENING_STATE"
        else:
            attribute = "STATE"
        state = self.state_action(combined)
        if attribute in {"STATE", "OPENING_STATE"}:
            action = "TURN_OFF" if state == "OFF" else "TURN_ON" if state == "ON" else None
        else:
            action = "ADJUST"
        if action is None:
            return {"status": "AMBIGUOUS", "reason": "KNOWN_CABIN_ACTION_UNRESOLVED", "candidate_scope": "已知但不开放"}
        subintent = {
            "规范动作": action,
            "规范对象": target,
            "控制属性": attribute,
            "位置": extract_area(text, slots),
            "数值": extract_value(text, slots),
            "方向": extract_lr(text) if attribute == "POSITION" else None,
            "模式": str(slots.get("模式")) if slots.get("模式") is not None else None,
        }
        return {"status": "RESOLVED", "intent_id": f"KNOWN::{target}::{action}::{attribute}", "scope": "已知但不开放", "slots": {}, "subintent": subintent, "complete": True, "evidence": "KNOWN_UNSUPPORTED_COGNITION_CATALOG"}


def make_sample(*, source: str, file_name: str, source_id: str, raw_text: str, scope: str, structure: str,
                tone: str, subintents: list[dict[str, Any]], complete: bool, review: bool,
                override_version: str | None = None) -> dict[str, Any]:
    positive = scope == "正式可执行" and structure == "单意图" and tone == "肯定" and complete and not review and len(subintents) == 1
    return {
        "样本编号": stable_id(source, file_name, source_id, raw_text),
        "原始文本": raw_text,
        "规范文本": normalize_text(raw_text),
        "来源": source,
        "原始文件": file_name,
        "原始编号": source_id,
        "控制范围": scope,
        "结构状态": structure,
        "语气状态": tone,
        "子意图列表": subintents,
        "合同是否完整": bool(complete),
        "是否允许进入正式正样本": bool(positive),
        "是否需要人工复核": bool(review),
        "映射规则版本": MAPPING_VERSION,
        "人工覆盖规则版本": override_version,
    }


def assemble_control_sample(resolutions: list[dict[str, Any]], *, source: str, file_name: str, source_id: str,
                            raw_text: str, expected_multi: bool = False, forced_structure: str | None = None,
                            extra_reasons: list[str] | None = None, tone_override: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    extra_reasons = list(extra_reasons or [])
    resolved = [item for item in resolutions if item and item.get("status") == "RESOLVED"]
    ambiguous = [item for item in resolutions if item and item.get("status") == "AMBIGUOUS"]
    ids = [item["intent_id"] for item in resolved]
    subintents = [item["subintent"] for item in resolved]
    formal_count = sum(item["scope"] == "正式可执行" for item in resolved)
    unsupported_count = sum(item["scope"] == "已知但不开放" for item in resolved)
    if formal_count:
        scope = "正式可执行"
    elif unsupported_count or any(item.get("candidate_scope") == "已知但不开放" for item in ambiguous):
        scope = "已知但不开放"
    elif ambiguous and any(item.get("candidate_scope") == "正式可执行" for item in ambiguous):
        scope = "正式可执行"
    else:
        scope = "未知"
    all_complete = bool(resolved) and all(item["complete"] for item in resolved) and not ambiguous
    if forced_structure:
        structure = forced_structure
    elif ambiguous or (expected_multi and len(resolved) < 2):
        structure = "歧义"
    elif not all_complete:
        structure = "缺槽" if resolved else "歧义"
    elif expected_multi or len(resolved) >= 2:
        structure = "多意图"
    else:
        structure = "单意图"
    if structure == "多意图" and len(subintents) < 2:
        structure = "歧义"
        extra_reasons.append("MULTI_SUBINTENT_UNDERFLOW")
    if scope in {"未知", "非控制"}:
        subintents = []
        all_complete = False
    review_reasons = extra_reasons + [item.get("reason", "UNRESOLVED") for item in ambiguous]
    review = bool(review_reasons) or structure == "歧义"
    sample = make_sample(source=source, file_name=file_name, source_id=source_id, raw_text=raw_text,
                         scope=scope, structure=structure, tone=tone_override or polarity(raw_text), subintents=subintents,
                         complete=all_complete, review=review)
    meta = {"canonical_intent_ids": ids, "review_reasons": review_reasons, "compound_flags": []}
    if expected_multi and not all_complete:
        meta["compound_flags"].append("MULTI_WITH_INCOMPLETE_OR_AMBIGUOUS")
    if sample["语气状态"] != "肯定" and expected_multi:
        meta["compound_flags"].append(f"MULTI_WITH_{sample['语气状态']}")
    if formal_count and unsupported_count:
        meta["compound_flags"].append("FORMAL_AND_KNOWN_UNSUPPORTED_MIXED")
    return sample, meta


def split_safety_clauses(text: str) -> list[str]:
    parts = [item.strip() for item in re.split(r"(?:先|再|然后|并且|并|同时|的同时|后|边)", text) if item.strip()]
    return parts if len(parts) >= 2 else [text]


def counterpart(previous_id: str, clause: str) -> str | None:
    pairs = {
        "SUNROOF_OPEN": "SUNROOF_CLOSE", "HOOD_OPEN": "HOOD_CLOSE", "DOOR_OPEN": "DOOR_CLOSE",
        "WINDOW_OPEN": "WINDOW_CLOSE", "TRUNK_OPEN": "TRUNK_CLOSE", "LOW_BEAM_ON": "LOW_BEAM_OFF",
        "HIGH_BEAM_ON": "HIGH_BEAM_OFF", "PARKING_LIGHT_ON": "PARKING_LIGHT_OFF",
    }
    if re.search(r"关|关闭|关掉|关上", clause):
        return pairs.get(previous_id)
    return None


def load_sources() -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], dict[str, str]]:
    raw_hashes: dict[str, str] = {}
    mac: dict[str, list[dict[str, Any]]] = {}
    gate: dict[str, Any] = {"status": "PASS", "checks": []}
    for file_name, expected in MAC_EXPECTED.items():
        path = ROOT / file_name
        rows, errors = parse_jsonl(path)
        raw_hashes[file_name] = sha256_path(path)
        check = {"source": file_name, "expected": expected, "actual": len(rows), "json_parse_errors": errors,
                 "pass": len(rows) == expected and not errors}
        gate["checks"].append(check)
        if not check["pass"]:
            raise SystemExit(f"HARD_GATE_FAIL {check}")
        mac[file_name] = rows
    if sum(map(len, mac.values())) != 20542:
        raise SystemExit("HARD_GATE_FAIL MAC-SLU total != 20542")

    extracted = json.loads(EXTRACTED_WORKBOOKS_PATH.read_text(encoding="utf-8"))
    workbook_by_headers: dict[str, dict[str, Any]] = {}
    for book in extracted:
        source_path = Path(book["source_path"])
        if not source_path.exists() or sha256_path(source_path) != book["source_sha256"]:
            raise SystemExit(f"HARD_GATE_FAIL workbook provenance mismatch: {source_path}")
        raw_hashes[book["source_file"]] = book["source_sha256"]
        for sheet in book["sheets"]:
            values = sheet["values"]
            headers = values[0] if values else []
            if headers == ["编号", "弱覆盖意图", "种子句"]:
                workbook_by_headers["weak"] = {"book": book, "sheet": sheet}
            elif headers[:3] == ["编号", "安全边界类别", "种子句"]:
                workbook_by_headers["safety"] = {"book": book, "sheet": sheet}
    for kind, expected in (("weak", 162), ("safety", 197)):
        if kind not in workbook_by_headers:
            raise SystemExit(f"HARD_GATE_FAIL missing workbook recognized by headers: {kind}")
        actual = len([row for row in workbook_by_headers[kind]["sheet"]["values"][1:] if any(value not in (None, "") for value in row)])
        check = {"source": kind, "expected": expected, "actual": actual, "pass": actual == expected,
                 "file": workbook_by_headers[kind]["book"]["source_file"], "sheet": workbook_by_headers[kind]["sheet"]["name"]}
        gate["checks"].append(check)
        if not check["pass"]:
            raise SystemExit(f"HARD_GATE_FAIL {check}")
    return mac, {"gate": gate, "workbooks": workbook_by_headers}, raw_hashes


def mac_audit(mac: dict[str, list[dict[str, Any]]]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    text_occurrences: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    slot_counts: Counter[str] = Counter()
    slot_value_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    domain_counts: Counter[str] = Counter()
    structure_counts: Counter[int] = Counter()
    anomaly_counts: Counter[str] = Counter()
    annotation_signatures: Counter[str] = Counter()
    empty_semantics_count = 0
    no_usable_semantic_frame_count = 0
    row_key_signatures: Counter[str] = Counter()
    empty_field_counts: Counter[str] = Counter()
    all_rows: list[dict[str, Any]] = []
    seen_source_ids: defaultdict[str, list[str]] = defaultdict(list)
    for file_name, rows in mac.items():
        source_split = file_name.removesuffix("_set.jsonl")
        for line_number, row in enumerate(rows, start=1):
            row_key_signatures["|".join(sorted(row))] += 1
            for required_field in ("id", "query", "semantics", "split_sens"):
                if required_field not in row:
                    anomaly_counts[f"MISSING_FIELD::{required_field}"] += 1
                elif row[required_field] in (None, "", [], {}):
                    empty_field_counts[required_field] += 1
            raw_text = row.get("query")
            if not isinstance(raw_text, str) or not raw_text.strip():
                anomaly_counts["EMPTY_OR_INVALID_QUERY"] += 1
                raw_text = ""
            source_id = str(row.get("id", line_number))
            seen_source_ids[source_id].append(f"{file_name}:{line_number}")
            frames = flatten_semantics(row)
            annotation_signatures[json.dumps(row.get("semantics"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))] += 1
            if not row.get("semantics"):
                empty_semantics_count += 1
            elif not frames:
                no_usable_semantic_frame_count += 1
            structure_counts[len(frames)] += 1
            if not isinstance(row.get("semantics"), dict):
                anomaly_counts["SEMANTICS_NOT_OBJECT"] += 1
            if not isinstance(row.get("split_sens"), list):
                anomaly_counts["SPLIT_SENS_NOT_LIST"] += 1
            elif frames and len(row["split_sens"]) != len(frames):
                anomaly_counts["SPLIT_SENS_FRAME_COUNT_MISMATCH"] += 1
            for frame in frames:
                domain_counts[frame["domain"]] += 1
                for name, value in frame["slots"].items():
                    slot_counts[name] += 1
                    slot_value_counts[name][str(value)] += 1
                if frame["duplicate_slot_names"]:
                    anomaly_counts["DUPLICATE_SLOT_NAME_WITHIN_FRAME"] += 1
            occurrence = {"source_file": file_name, "source_split": source_split, "source_line": line_number,
                          "source_id": source_id, "raw_text": raw_text, "row": row, "frames": frames}
            text_occurrences[raw_text].append(occurrence)
            all_rows.append(occurrence)
    duplicate_groups = []
    canonical = []
    priority = {name: index for index, name in enumerate(MAC_EXPECTED)}
    for raw_text, occurrences in text_occurrences.items():
        ordered = sorted(occurrences, key=lambda item: (priority[item["source_file"]], item["source_line"]))
        canonical.append(ordered[0])
        if len(ordered) > 1:
            duplicate_groups.append({"raw_text": raw_text, "occurrence_count": len(ordered),
                                     "cross_split": len({x["source_split"] for x in ordered}) > 1,
                                     "occurrences": [{k: x[k] for k in ("source_file", "source_split", "source_line", "source_id")} for x in ordered]})
    canonical.sort(key=lambda item: (priority[item["source_file"]], item["source_line"]))
    audit = {
        "raw_row_count": len(all_rows),
        "canonical_exact_text_count": len(canonical),
        "exact_duplicate_group_count": len(duplicate_groups),
        "exact_duplicate_excess_row_count": sum(x["occurrence_count"] - 1 for x in duplicate_groups),
        "cross_split_duplicate_group_count": sum(x["cross_split"] for x in duplicate_groups),
        "source_id_duplicate_count": sum(len(v) > 1 for v in seen_source_ids.values()),
        "empty_semantics_count": empty_semantics_count,
        "no_usable_semantic_frame_count": no_usable_semantic_frame_count,
        "duplicate_annotation_signature_count": sum(count > 1 for count in annotation_signatures.values()),
        "duplicate_annotation_excess_row_count": sum(count - 1 for count in annotation_signatures.values() if count > 1),
        "row_key_signature_counts": dict(row_key_signatures),
        "empty_field_counts": dict(empty_field_counts),
        "domain_counts": dict(domain_counts.most_common()),
        "semantic_frame_count_distribution": {str(k): v for k, v in sorted(structure_counts.items())},
        "slot_name_counts": dict(slot_counts.most_common()),
        "slot_value_counts": {name: dict(counter.most_common()) for name, counter in slot_value_counts.items()},
        "anomaly_counts": dict(anomaly_counts),
    }
    return audit, duplicate_groups, canonical


def map_mac(resolver: Resolver, occurrence: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    row = occurrence["row"]
    raw_text = occurrence["raw_text"]
    frames = occurrence["frames"]
    split_sens = row.get("split_sens") if isinstance(row.get("split_sens"), list) else []
    vehicle_frames = [frame for frame in frames if frame["domain"] == "车载控制"]
    non_vehicle_frames = [frame for frame in frames if frame["domain"] != "车载控制"]
    if not raw_text.strip():
        sample = make_sample(source="MAC-SLU", file_name=occurrence["source_file"], source_id=occurrence["source_id"],
                             raw_text=raw_text, scope="未知", structure="歧义", tone="肯定",
                             subintents=[], complete=False, review=True)
        meta = {"canonical_intent_ids": [], "review_reasons": ["EMPTY_SOURCE_QUERY"], "compound_flags": []}
    elif not frames:
        reason = "EMPTY_MAC_ANNOTATION" if not row.get("semantics") else "NO_USABLE_MAC_SEMANTIC_FRAME"
        sample = make_sample(source="MAC-SLU", file_name=occurrence["source_file"], source_id=occurrence["source_id"],
                             raw_text=raw_text, scope="未知", structure="歧义", tone=polarity(raw_text),
                             subintents=[], complete=False, review=True)
        meta = {"canonical_intent_ids": [], "review_reasons": [reason], "compound_flags": []}
    elif not vehicle_frames:
        sample = make_sample(source="MAC-SLU", file_name=occurrence["source_file"], source_id=occurrence["source_id"],
                             raw_text=raw_text, scope="非控制", structure="单意图", tone=polarity(raw_text),
                             subintents=[], complete=False, review=False)
        meta = {"canonical_intent_ids": [], "review_reasons": [], "compound_flags": []}
    else:
        resolutions = []
        for index, frame in enumerate(vehicle_frames):
            clause = split_sens[index] if len(split_sens) == len(frames) else raw_text
            resolution = resolver.infer_registry(clause, frame["slots"])
            if resolution is None:
                resolution = {"status": "AMBIGUOUS", "reason": "UNRESOLVED_MAC_VEHICLE_SEMANTICS", "candidate_scope": "未知"}
            resolutions.append(resolution)
        expected_multi = len(frames) >= 2
        reasons = ["MIXED_CONTROL_NONCONTROL"] if vehicle_frames and non_vehicle_frames else []
        sample, meta = assemble_control_sample(resolutions, source="MAC-SLU", file_name=occurrence["source_file"],
                                               source_id=occurrence["source_id"], raw_text=raw_text,
                                               expected_multi=expected_multi, extra_reasons=reasons)
    provenance = {
        "样本编号": sample["样本编号"], "source_dataset": "MAC-SLU", "source_file": occurrence["source_file"],
        "source_split": occurrence["source_split"], "source_row": occurrence["source_line"],
        "source_id": occurrence["source_id"], "raw_text": raw_text, "original_annotation": row.get("semantics"),
        "split_sens": row.get("split_sens"), "conversion_version": CONVERSION_VERSION,
    }
    mapping = {"样本编号": sample["样本编号"], **meta}
    return sample, provenance, mapping


def map_weak(resolver: Resolver, book: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    samples, provenance, mappings = [], [], []
    file_name = book["book"]["source_file"]
    for row_number, row in enumerate(book["sheet"]["values"][1:], start=2):
        if not any(value not in (None, "") for value in row):
            continue
        source_id, approved_name, raw_text = str(row[0]), str(row[1]), str(row[2])
        resolution = resolver.infer_registry(raw_text, approved_name=approved_name)
        if resolution is None:
            sample, meta = assemble_control_sample([{"status": "AMBIGUOUS", "reason": "WEAK_LABEL_NOT_IN_R3", "candidate_scope": "未知"}],
                                                   source=SOURCE_NAME["weak"], file_name=file_name, source_id=source_id, raw_text=raw_text)
        else:
            tone_override = None
            exceptions = resolver.rules.get("polarity_lexicalized_action_exceptions", {}).get(resolution["intent_id"], [])
            if raw_text in exceptions:
                tone_override = "肯定"
            sample, meta = assemble_control_sample([resolution], source=SOURCE_NAME["weak"], file_name=file_name,
                                                   source_id=source_id, raw_text=raw_text, tone_override=tone_override)
        samples.append(sample)
        provenance.append({"样本编号": sample["样本编号"], "source_dataset": SOURCE_NAME["weak"], "source_file": file_name,
                           "source_split": None, "source_row": row_number, "source_id": source_id, "raw_text": raw_text,
                           "original_annotation": {"弱覆盖意图": approved_name}, "conversion_version": CONVERSION_VERSION})
        mappings.append({"样本编号": sample["样本编号"], **meta})
    return samples, provenance, mappings


def map_safety(resolver: Resolver, book: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    samples, provenance, mappings = [], [], []
    file_name = book["book"]["source_file"]
    for row_number, row in enumerate(book["sheet"]["values"][1:], start=2):
        if not any(value not in (None, "") for value in row):
            continue
        source_id, category, raw_text = str(row[0]), str(row[1]), str(row[2])
        clauses = split_safety_clauses(raw_text) if category == "多意图" else [raw_text]
        resolutions: list[dict[str, Any]] = []
        for clause in clauses:
            resolution = resolver.infer_registry(clause)
            if resolution is None and resolutions and resolutions[-1].get("status") == "RESOLVED":
                if (pair := counterpart(resolutions[-1]["intent_id"], clause)) is not None:
                    parsed = resolver.parse_slots(pair, clause, {})
                    resolution = resolver.resolution(pair, parsed, "SAFETY_COREFERENCE_COUNTERPART_RULE")
            if resolution is None:
                resolution = {"status": "AMBIGUOUS", "reason": "UNRESOLVED_SAFETY_SEMANTICS", "candidate_scope": "未知"}
            resolutions.append(resolution)
        expected_multi = category == "多意图"
        forced = None
        if category == "危险模糊边界":
            forced = "歧义"
        sample, meta = assemble_control_sample(resolutions, source=SOURCE_NAME["safety"], file_name=file_name,
                                               source_id=source_id, raw_text=raw_text, expected_multi=expected_multi,
                                               forced_structure=forced)
        # Boundary category is authoritative evidence; machine labels are rebuilt from current rules.
        if category == "缺槽" and sample["结构状态"] == "单意图":
            sample["结构状态"] = "缺槽"
            sample["合同是否完整"] = False
            sample["是否允许进入正式正样本"] = False
        if category in {"相似对象混淆", "危险模糊边界"} and sample["结构状态"] == "歧义":
            sample["是否需要人工复核"] = True
            sample["是否允许进入正式正样本"] = False
        samples.append(sample)
        provenance.append({"样本编号": sample["样本编号"], "source_dataset": SOURCE_NAME["safety"], "source_file": file_name,
                           "source_split": None, "source_row": row_number, "source_id": source_id, "raw_text": raw_text,
                           "original_annotation": {"安全边界类别": category},
                           "ignored_as_machine_supervision": {"关联/干扰意图": row[3] if len(row) > 3 else None,
                                                               "预期处理路径": row[4] if len(row) > 4 else None},
                           "conversion_version": CONVERSION_VERSION})
        mappings.append({"样本编号": sample["样本编号"], "source_boundary_category": category, **meta})
    return samples, provenance, mappings


def stats_for(samples: list[dict[str, Any]], mappings: list[dict[str, Any]], formal_ids: list[str]) -> dict[str, Any]:
    by_id = {item["样本编号"]: item for item in mappings}
    coverage = Counter()
    for sample in samples:
        if sample["是否允许进入正式正样本"]:
            ids = by_id[sample["样本编号"]]["canonical_intent_ids"]
            if len(ids) == 1 and ids[0] in formal_ids:
                coverage[ids[0]] += 1
    return {
        "sample_count": len(samples),
        "control_scope": dict(Counter(x["控制范围"] for x in samples)),
        "structure_status": dict(Counter(x["结构状态"] for x in samples)),
        "polarity": dict(Counter(x["语气状态"] for x in samples)),
        "contract_complete": dict(Counter(str(x["合同是否完整"]).lower() for x in samples)),
        "formal_positive_allowed": sum(x["是否允许进入正式正样本"] for x in samples),
        "needs_review": sum(x["是否需要人工复核"] for x in samples),
        "formal_intent_positive_coverage": {intent_id: coverage[intent_id] for intent_id in formal_ids},
    }


def markdown_report(report: dict[str, Any]) -> str:
    s = report["combined_statistics"]
    coverage = s["formal_intent_positive_coverage"]
    lines = [
        "# Full NLU R3 数据基线审计报告", "",
        f"- 构建版本：`{CONVERSION_VERSION}`", f"- 映射规则：`{MAPPING_VERSION}`",
        f"- Schema：`{SCHEMA_VERSION}`", f"- R3 SHA256：`{REGISTRY_SHA256}`", "",
        "## 硬门槛", "",
    ]
    for check in report["input_gate"]["checks"]:
        lines.append(f"- {check['source']}: expected={check['expected']}, actual={check['actual']}, PASS={check['pass']}")
    lines += ["", "## MAC-SLU 审计", "",
              f"- 原始行：{report['mac_audit']['raw_row_count']}",
              f"- 精确文本去重后 canonical：{report['mac_audit']['canonical_exact_text_count']}",
              f"- 重复组：{report['mac_audit']['exact_duplicate_group_count']}；跨划分重复组：{report['mac_audit']['cross_split_duplicate_group_count']}",
              "", "## 统一监督统计", "",
              f"- 总样本：{s['sample_count']}", f"- 控制范围：{json.dumps(s['control_scope'], ensure_ascii=False)}",
              f"- 结构状态：{json.dumps(s['structure_status'], ensure_ascii=False)}",
              f"- 语气状态：{json.dumps(s['polarity'], ensure_ascii=False)}",
              f"- needs_review：{s['needs_review']}",
              f"- 正式完整正样本：{s['formal_positive_allowed']}", "",
              "## 71 项正式意图完整正样本覆盖", "", "| canonical_intent_id | 数量 | 缺口等级 |", "|---|---:|---|" ]
    for intent_id, count in coverage.items():
        level = "ZERO" if count == 0 else "WEAK(<10)" if count < 10 else "ADEQUATE"
        lines.append(f"| {intent_id} | {count} | {level} |")
    lines += ["", "## Schema 结论", "",
              f"- 全部派生数据是否100%符合冻结统一样本结构：**{'是' if report['schema_validation']['all_pass'] else '否'}**",
              f"- `SCHEMA_COMPLIANCE_RATE={report['schema_validation']['compliance_rate']}`", "",
              "## 已知但不开放与人工复核", "",
              f"- 已知但不开放对象/能力计数：{json.dumps(report['known_unsupported_object_counts'], ensure_ascii=False)}",
              f"- needs_review 原因：{json.dumps(report['needs_review_reason_distribution'], ensure_ascii=False)}",
              f"- 复合情况：{json.dumps(report['compound_case_distribution'], ensure_ascii=False)}", "",
              "## 自然用户语音可说性存疑（本轮未删除）", ""]
    lines.extend(f"- {intent_id}" for intent_id in report["natural_user_sayability_questionable"])
    lines += ["", "## 派生产物与 SHA256", ""]
    lines.extend(f"- `{item['path']}` — `{item['sha256']}`" for item in report["derived_artifacts"])
    lines += ["", "## 阶段边界", "",
              "- `ACTIVE_FULL_NLU_DEPENDENCY_COUNT=0`",
              "本轮未生成最终 train/dev/test，未扩写，未训练，未加载历史 7-Intent checkpoint。", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()

    require_sha(REGISTRY_PATH, REGISTRY_SHA256, "R3 registry")
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    rules = yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))
    cognition = yaml.safe_load(COGNITION_PATH.read_text(encoding="utf-8"))
    overrides = json.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    if registry.get("registry_version") != REGISTRY_VERSION or registry.get("semantic_freeze_status") != "FROZEN_FOR_FULL_NLU_DATASET_BUILD":
        raise SystemExit("HARD_GATE_FAIL R3 registry is not the frozen authority")
    if len(registry["formal_user_voice_intent_ids"]) != 71 or len(registry["known_unsupported_control_intent_ids"]) != 22:
        raise SystemExit("HARD_GATE_FAIL R3 scope counts are not 71/22")
    if rules.get("mapping_rule_version") != MAPPING_VERSION:
        raise SystemExit("HARD_GATE_FAIL mapping rule version")
    if overrides["覆盖记录"]:
        raise SystemExit("This baseline builder requires explicit override application implementation before non-empty overrides are allowed")

    mac, source_info, raw_hashes_before = load_sources()
    audit, duplicate_groups, canonical_occurrences = mac_audit(mac)
    resolver = Resolver(registry, rules, cognition)

    mac_samples, mac_provenance, mac_mappings = [], [], []
    for occurrence in canonical_occurrences:
        sample, provenance, mapping = map_mac(resolver, occurrence)
        mac_samples.append(sample); mac_provenance.append(provenance); mac_mappings.append(mapping)
    weak_samples, weak_provenance, weak_mappings = map_weak(resolver, source_info["workbooks"]["weak"])
    safety_samples, safety_provenance, safety_mappings = map_safety(resolver, source_info["workbooks"]["safety"])
    if len(weak_samples) != 162 or len(safety_samples) != 197:
        raise SystemExit("HARD_GATE_FAIL derived seed counts changed")
    combined = mac_samples + weak_samples + safety_samples
    provenance = mac_provenance + weak_provenance + safety_provenance
    mappings = mac_mappings + weak_mappings + safety_mappings

    pool_paths = {
        "mac_canonical_pool": output_dir / "mac_slu_canonical_pool_v1.jsonl",
        "weak_seed_pool": output_dir / "weak_seed_pool_v1.jsonl",
        "safety_boundary_pool": output_dir / "safety_boundary_pool_v1.jsonl",
        "combined_canonical_raw_pool": output_dir / "full_nlu_canonical_raw_pool_v1.jsonl",
    }
    for key, values in (("mac_canonical_pool", mac_samples), ("weak_seed_pool", weak_samples),
                        ("safety_boundary_pool", safety_samples), ("combined_canonical_raw_pool", combined)):
        write_jsonl(pool_paths[key], values)
    write_jsonl(output_dir / "source_provenance_v1.jsonl", provenance)
    write_jsonl(output_dir / "sample_mapping_metadata_v1.jsonl", mappings)
    write_json(output_dir / "mac_exact_duplicates_v1.json", duplicate_groups)
    write_json(output_dir / "mac_raw_label_slot_statistics_v1.json", {
        "domain_counts": audit["domain_counts"], "slot_name_counts": audit["slot_name_counts"],
        "slot_value_counts": audit["slot_value_counts"], "semantic_frame_count_distribution": audit["semantic_frame_count_distribution"]})

    validations = {key: validate_paths([path]) for key, path in pool_paths.items()}
    all_pass = all(item["status"] == "PASS" for item in validations.values())
    total_validation_samples = sum(item["sample_count"] for item in validations.values())
    total_validation_valid = sum(item["valid_sample_count"] for item in validations.values())
    compliance = f"{(100 * total_validation_valid / total_validation_samples):.6f}%" if total_validation_samples else "0.000000%"
    if not all_pass or compliance != "100.000000%":
        write_json(output_dir / "schema_validation_failure_v1.json", validations)
        raise SystemExit("SCHEMA_HARD_GATE_FAIL derived data is not 100% compliant")

    combined_stats = stats_for(combined, mappings, registry["formal_user_voice_intent_ids"])
    mapping_by_id = {item["样本编号"]: item for item in mappings}
    review_reasons = Counter(reason for item in mappings for reason in item.get("review_reasons", []))
    compound_flags = Counter(flag for item in mappings for flag in item.get("compound_flags", []))
    unsupported_objects = Counter()
    for sample in combined:
        if sample["控制范围"] == "已知但不开放":
            for sub in sample["子意图列表"]:
                unsupported_objects[sub["规范对象"]] += 1
    formal_registry_items = [resolver.by_id[intent_id] for intent_id in registry["formal_user_voice_intent_ids"]]
    derived_artifact_paths = [
        *pool_paths.values(), output_dir / "source_provenance_v1.jsonl", output_dir / "sample_mapping_metadata_v1.jsonl",
        output_dir / "mac_exact_duplicates_v1.json", output_dir / "mac_raw_label_slot_statistics_v1.json",
    ]
    derived_artifacts = [{"path": str(path.relative_to(ROOT)), "sha256": sha256_path(path), "bytes": path.stat().st_size}
                         for path in derived_artifact_paths]
    coverage = combined_stats["formal_intent_positive_coverage"]
    report = {
        "report_version": "full_nlu_mapping_report_v1",
        "build_date": str(date.today()),
        "conversion_version": CONVERSION_VERSION,
        "registry": {"version": REGISTRY_VERSION, "path": str(REGISTRY_PATH.relative_to(ROOT)), "sha256": REGISTRY_SHA256,
                     "formal_intent_count": 71, "known_unsupported_registry_intent_count": 22},
        "registry_contract_statistics": {
            "canonical_action_count": len({x["canonical_action"] for x in formal_registry_items}),
            "canonical_target_count": len({x["canonical_target"] for x in formal_registry_items}),
            "control_attribute_count": len({x["control_attribute"] for x in formal_registry_items}),
            "required_slot_occurrences": dict(Counter(slot for x in formal_registry_items for slot in x.get("required_slots", []))),
            "value_contracts": dict(Counter(x.get("value_contract", "NONE") for x in formal_registry_items)),
            "direction_contracts": dict(Counter(x.get("direction_contract") or "NONE" for x in formal_registry_items)),
            "mode_contracts": dict(Counter(x.get("mode_contract") or "NONE" for x in formal_registry_items)),
        },
        "schema": {"version": SCHEMA_VERSION, "path": str(SCHEMA_PATH.relative_to(ROOT)), "sha256": sha256_path(SCHEMA_PATH)},
        "mapping_rules": {"version": MAPPING_VERSION, "path": str(RULES_PATH.relative_to(ROOT)), "sha256": sha256_path(RULES_PATH)},
        "cognition_catalog": {"version": cognition["catalog_version"], "path": str(COGNITION_PATH.relative_to(ROOT)), "sha256": sha256_path(COGNITION_PATH)},
        "manual_overrides": {"version": OVERRIDE_VERSION, "path": str(OVERRIDES_PATH.relative_to(ROOT)), "sha256": sha256_path(OVERRIDES_PATH), "applied_count": 0},
        "input_gate": source_info["gate"],
        "raw_source_sha256": raw_hashes_before,
        "mac_audit": {k: v for k, v in audit.items() if k != "slot_value_counts"},
        "pool_statistics": {
            "mac": stats_for(mac_samples, mac_mappings, registry["formal_user_voice_intent_ids"]),
            "weak_seed": stats_for(weak_samples, weak_mappings, registry["formal_user_voice_intent_ids"]),
            "safety_boundary": stats_for(safety_samples, safety_mappings, registry["formal_user_voice_intent_ids"]),
        },
        "combined_statistics": combined_stats,
        "formal_intent_gaps": {
            "zero": [key for key, value in coverage.items() if value == 0],
            "weak_lt_10": [key for key, value in coverage.items() if 0 < value < 10],
            "adequate_ge_10": [key for key, value in coverage.items() if value >= 10],
        },
        "known_unsupported_object_counts": dict(unsupported_objects.most_common()),
        "needs_review_reason_distribution": dict(review_reasons.most_common()),
        "compound_case_distribution": dict(compound_flags.most_common()),
        "natural_user_sayability_questionable": registry.get("risk_review_required_intents", []),
        "derived_artifacts": derived_artifacts,
        "schema_validation": {"all_pass": all_pass, "compliance_rate": compliance, "per_pool": validations},
        "historical_poc": {"active_full_nlu_dependency_count": 0, "used_for_build": False, "checkpoint_loaded": False},
        "prohibited_outputs_confirmed_absent": ["FINAL_TRAIN_SPLIT", "FINAL_DEV_SPLIT", "FINAL_TEST_SPLIT", "AUGMENTATION", "MODEL_TRAINING"],
    }
    machine_report_path = output_dir / "full_nlu_mapping_report_v1.json"
    markdown_path = output_dir / "full_nlu_mapping_report_v1.md"
    write_json(machine_report_path, report)
    markdown_path.write_text(markdown_report(report), encoding="utf-8")

    raw_hashes_after = {name: sha256_path(ROOT / name) for name in MAC_EXPECTED}
    for book in source_info["workbooks"].values():
        raw_hashes_after[book["book"]["source_file"]] = sha256_path(Path(book["book"]["source_path"]))
    if raw_hashes_after != raw_hashes_before:
        raise SystemExit("IMMUTABILITY_HARD_GATE_FAIL raw source changed during build")

    manifest_path = output_dir / "full_nlu_baseline_manifest_v1.json"
    changeset_path = output_dir / "full_nlu_changeset_v1.json"
    generated = sorted(path for path in output_dir.rglob("*") if path.is_file() and path not in {manifest_path, changeset_path})
    manifest = {
        "manifest_version": "full_nlu_baseline_manifest_v1",
        "status": "FROZEN_CANONICAL_RAW_BASELINE_NO_SPLIT_NO_TRAINING",
        "registry_version": REGISTRY_VERSION,
        "registry_sha256": REGISTRY_SHA256,
        "schema_version": SCHEMA_VERSION,
        "mapping_rule_version": MAPPING_VERSION,
        "manual_override_rule_version": OVERRIDE_VERSION,
        "conversion_version": CONVERSION_VERSION,
        "raw_sources_immutable_verified": True,
        "SCHEMA_COMPLIANCE_RATE": compliance,
        "sample_counts": {"mac_raw": 20542, "mac_canonical": len(mac_samples), "weak_seed": len(weak_samples),
                          "safety_boundary": len(safety_samples), "combined": len(combined)},
        "generated_files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256_path(path), "bytes": path.stat().st_size} for path in generated],
    }
    write_json(manifest_path, manifest)
    implementation_paths = [
        ROOT / "docs/plans/2026-08-09-full-nlu-r3-data-baseline-design.md",
        SCHEMA_PATH,
        ROOT / "data/nlu/full/schema/full_nlu_schema_smoke_v1.jsonl",
        RULES_PATH,
        COGNITION_PATH,
        OVERRIDES_PATH,
        EXTRACTED_WORKBOOKS_PATH,
        ROOT / "scripts/full_nlu/inspect_seed_workbooks.mjs",
        ROOT / "scripts/full_nlu/validate_full_nlu_schema.py",
        ROOT / "scripts/full_nlu/build_full_nlu_baseline.py",
        ROOT / "backend/tests/offline_nlu/test_full_nlu_schema_v1.py",
    ]
    changeset_files = implementation_paths + generated + [manifest_path]
    write_json(changeset_path, {
        "changeset_version": "full_nlu_changeset_v1",
        "note": "Lists every file created or modified by this Full NLU baseline stage except this self-describing changeset file.",
        "files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256_path(path), "bytes": path.stat().st_size}
                  for path in changeset_files],
    })
    print(json.dumps({"status": "PASS", "output_dir": str(output_dir), "combined_count": len(combined),
                      "SCHEMA_COMPLIANCE_RATE": compliance, "manifest": str(manifest_path),
                      "manifest_sha256": sha256_path(manifest_path), "changeset": str(changeset_path),
                      "changeset_sha256": sha256_path(changeset_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
