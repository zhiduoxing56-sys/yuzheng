"""Audit deterministic MAC-SLU coverage gaps and build Full NLU baseline_v2.

No augmentation, training, final splitting, nearest-neighbor matching, or raw mutation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[2]
V1_BUILDER_PATH = ROOT / "scripts/full_nlu/build_full_nlu_baseline.py"
SPEC = importlib.util.spec_from_file_location("full_nlu_baseline_v1_builder", V1_BUILDER_PATH)
assert SPEC and SPEC.loader
V1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V1)

REGISTRY_PATH = ROOT / "data/nlu/spec/intent_registry_r3.yaml"
SCHEMA_PATH = ROOT / "data/nlu/full/schema/full_nlu_sample_schema_v1.json"
RULES_V2_PATH = ROOT / "data/nlu/full/rules/full_nlu_mapping_v2.yaml"
RULES_V3_PATH = ROOT / "data/nlu/full/rules/full_nlu_mapping_v3.yaml"
COGNITION_PATH = ROOT / "data/nlu/full/rules/known_unsupported_cognition_v1.yaml"
OVERRIDES_PATH = ROOT / "data/nlu/full/rules/manual_overrides_v1.json"
BASELINE_V1 = ROOT / "data/nlu/full/baseline_v1"
AUDIT_OUT = ROOT / "data/nlu/full/audit_v3"
BASELINE_V2 = ROOT / "data/nlu/full/baseline_v2"

REGISTRY_SHA256 = "c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06"
SCHEMA_SHA256 = "97f74d2d7f55871808fe18b432f0f6859094483444a6f16de715467acd8b6f33"
RULES_V2_SHA256 = "cf2eed72aa829083e0b666777799ab8052f674bb49b10637340d54882a142aa4"
MAPPING_VERSION = "nlu_mapping_v3"
CONVERSION_VERSION = "full_nlu_baseline_v2"
SCHEMA_VERSION = "full_nlu_sample_schema_v1"

ZERO_V1_INTENTS = [
    "MIRROR_HEATING_OFF", "SEAT_TILT_SET_ANGLE", "MIRROR_SET_ANGLE", "SUNROOF_SET_TILT",
    "CRUISE_SET_SPEED", "CRUISE_SET_GAP", "TURN_INDICATOR_ON", "WIPER_SET_SENSITIVITY",
    "PARKING_BRAKE_AUTO_APPLY_ENABLE", "PARKING_BRAKE_AUTO_APPLY_DISABLE",
]

TARGET_CABIN_RULES = {
    "阅读灯": {"V3-CABIN-001"}, "普通车内灯": {"V3-CABIN-002"}, "空调启停": {"V3-CABIN-003"},
    "空调温度": {"V3-CABIN-004"}, "空调风量": {"V3-CABIN-005"}, "空调风向": {"V3-CABIN-006"},
    "空调模式": {"V3-CABIN-007"}, "座椅加热": {"V3-CABIN-008"}, "座椅通风": {"V3-CABIN-009"},
    "座椅按摩": {"V3-CABIN-010"}, "氛围灯": {"V3-CABIN-011"}, "遮阳帘": {"V3-CABIN-012"},
    "屏幕亮度/显示": {"V3-CABIN-013", "V3-CABIN-017"}, "香氛": {"V3-CABIN-014"}, "方向盘加热": {"V3-CABIN-015"},
    "其他-天幕透光": {"V3-CABIN-016"}, "其他-扶手位置": {"V3-CABIN-018"},
    "其他-连接开关": {"V3-CABIN-019"}, "其他-无线充电": {"V3-CABIN-020"},
    "其他-车辆模式": {"V3-CABIN-021"}, "其他-低速提示音": {"V3-CABIN-022"},
}


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, values: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")


def source_key(sample: dict[str, Any]) -> tuple[str, str, str, str]:
    return sample["来源"], sample["原始文件"], sample["原始编号"], sample["原始文本"]


def value_type(value: Any) -> str:
    if value in (None, ""):
        return "NONE"
    text = str(value)
    if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", text):
        return "NUMBER"
    if re.search(r"\d|百分之|一半|[一二两三四五六七八九十]成|最大|最小|最高|最低|挡|档", text):
        return "QUANTIFIED_OR_LEVEL"
    if re.search(r"增|减|高|低|大|小|前|后|左|右|上|下|里|外", text):
        return "RELATIVE_OR_DIRECTIONAL"
    return "TEXT_ENUM_OR_OTHER"


def semantic_fields(slots: dict[str, Any]) -> dict[str, Any]:
    return {
        "原始操作": slots.get("操作"),
        "原始对象": slots.get("对象"),
        "原始功能": {
            key: slots.get(key) for key in ("功能", "对象功能", "调节内容", "车内灯类型", "车外灯类型", "子功能")
            if slots.get(key) not in (None, "")
        },
        "原始位置类型": value_type(slots.get("位置")),
        "原始数值类型": value_type(slots.get("value")),
        "原始模式类型": value_type(slots.get("模式")),
    }


class StructuredResolver:
    def __init__(self, registry: dict[str, Any], rules_v2: dict[str, Any], rules_v3: dict[str, Any], cognition: dict[str, Any]):
        self.registry = registry
        self.rules_v3 = rules_v3
        self.base = V1.Resolver(registry, rules_v2, cognition)
        self.by_id = self.base.by_id
        self.formal = self.base.formal
        self.op_classes = rules_v3["operation_classes"]

    def op_class(self, raw: Any) -> str | None:
        if raw is None:
            return None
        text = str(raw)
        for name, aliases in self.op_classes.items():
            if text in aliases:
                return name
        if re.search(r"打开|开启|启用|启动", text):
            return "ON"
        if re.search(r"关闭|停用|禁用", text):
            return "OFF"
        return None

    @staticmethod
    def combined(slots: dict[str, Any]) -> str:
        return " ".join(str(value) for key, value in slots.items() if key != "intent" and value not in (None, ""))

    @staticmethod
    def cabin_candidate_categories(slots: dict[str, Any]) -> set[str]:
        """Identify a cabin semantic family without requiring a resolvable action.

        This is reporting-only: it makes the denominator include structurally
        evident cabin controls whose action is still unclear.  It never changes
        a sample label or invokes text similarity.
        """
        obj = str(slots.get("对象") or "")
        obj_fun = str(slots.get("对象功能") or "")
        feature = str(slots.get("功能") or "")
        adjust = str(slots.get("调节内容") or "")
        mode = str(slots.get("模式") or "")
        inside_light = str(slots.get("车内灯类型") or "")
        evidence = " ".join((obj, obj_fun, feature, adjust, mode, inside_light))
        categories: set[str] = set()
        if obj == "阅读灯" or inside_light == "阅读灯":
            categories.add("阅读灯")
        if obj in {"车内灯", "舱内灯", "顶灯"} or inside_light in {"车内灯", "舱内灯", "顶灯"}:
            categories.add("普通车内灯")
        if obj == "空调" or adjust in {"温度", "风量", "风速", "风力", "风向"}:
            if adjust == "温度" and not (obj == "座椅" or obj_fun == "加热"):
                categories.add("空调温度")
            elif adjust in {"风量", "风速", "风力", "风"} and not (obj == "座椅" or obj_fun == "通风"):
                categories.add("空调风量")
            elif adjust == "风向" and obj not in {"座椅", "屏", "屏幕", "扶手", "扶手台"}:
                categories.add("空调风向")
            elif adjust == "模式" or mode:
                categories.add("空调模式")
            else:
                categories.add("空调启停")
        if obj == "座椅" and obj_fun == "加热":
            categories.add("座椅加热")
        if obj == "座椅" and obj_fun == "通风":
            categories.add("座椅通风")
        if obj_fun == "按摩":
            categories.add("座椅按摩")
        if obj == "氛围灯" or inside_light == "氛围灯":
            categories.add("氛围灯")
        if obj in {"遮阳帘", "遮阳幕", "遮光板", "幕布"}:
            categories.add("遮阳帘")
        if obj in {"屏", "屏幕", "显示屏", "中控屏", "娱乐屏", "娱乐屏幕", "HUD"}:
            categories.add("屏幕亮度/显示")
        if obj in {"香氛", "香薰", "芳香"}:
            categories.add("香氛")
        if obj == "方向盘" and obj_fun == "加热":
            categories.add("方向盘加热")
        if obj in {"天窗", "天幕"} and adjust in {"透光度", "透明度", "透光值"}:
            categories.add("其他-天幕透光")
        if obj in {"扶手", "扶手台"} and adjust == "方向":
            categories.add("其他-扶手位置")
        if any(token in evidence for token in ("蓝牙", "热点", "WIFI", "WiFi", "wifi")):
            categories.add("其他-连接开关")
        if "无线充电" in evidence:
            categories.add("其他-无线充电")
        vehicle_modes = {"舒享", "舒享模式", "驻车舒享", "驻车舒享模式", "停车舒享", "停车舒享模式", "经济", "经济模式", "运动", "运动模式", "标准", "标准模式", "雪地", "雪地模式", "山地", "山地模式", "纯电", "纯电模式", "混动", "混动模式", "四驱", "四驱模式", "单踏板", "单踏板模式", "能量回收"}
        if adjust == "模式" and mode in vehicle_modes:
            categories.add("其他-车辆模式")
        if any(token in evidence for token in ("低速提示音", "低速报警")):
            categories.add("其他-低速提示音")
        return categories

    @staticmethod
    def raw_value(slots: dict[str, Any]) -> Any:
        for key in ("value", "方向偏移量", "幅度", "程度", "温度", "速度", "角度", "开度"):
            if slots.get(key) not in (None, ""):
                return slots[key]
        return None

    def normalize_numeric(self, raw: Any, intent_id: str, text: str) -> Any:
        if raw in (None, ""):
            return V1.extract_value(text, {})
        value = str(raw).strip()
        parsed = V1.extract_value(value, {"value": value})
        if parsed is not None:
            return parsed
        if re.fullmatch(r"\d+(?:\.\d+)?", value):
            number = float(value)
            return int(number) if number.is_integer() else number
        if (number := V1.cn_number(value)) is not None:
            return number
        if intent_id == "WIPER_SET_SENSITIVITY":
            if value in {"最大", "最高", "高"}:
                return "HIGH"
            if value in {"最小", "最低", "低"}:
                return "LOW"
        return None

    def slots_for(self, intent_id: str, slots: dict[str, Any], evidence_text: str) -> dict[str, Any]:
        parsed = self.base.parse_slots(intent_id, evidence_text, slots)
        raw = self.raw_value(slots)
        parsed["VALUE"] = self.normalize_numeric(raw, intent_id, evidence_text)
        if intent_id == "MIRROR_SET_ANGLE":
            area = V1.extract_area(evidence_text, slots)
            parsed["AREA"] = "LEFT_SIDE" if area in {"LEFT_FRONT", "LEFT_REAR", "LEFT_SIDE"} else "RIGHT_SIDE" if area in {"RIGHT_FRONT", "RIGHT_REAR", "RIGHT_SIDE"} else None
            direction_source = " ".join((str(slots.get("value") or ""), str(slots.get("方向偏移量") or ""), evidence_text))
            parsed["DIRECTION"] = "LEFT" if re.search(r"往左|向左|左调", direction_source) else "RIGHT" if re.search(r"往右|向右|右调", direction_source) else "UP" if re.search(r"往上|向上|上调", direction_source) else "DOWN" if re.search(r"往下|向下|下调", direction_source) else None
        elif intent_id == "SUNROOF_SET_TILT":
            operation = str(slots.get("操作") or "")
            parsed["DIRECTION"] = "UP" if operation in {"翘起", "后翘", "上翘"} else "DOWN" if operation in {"下收", "收下"} else None
            parsed["VALUE"] = None
        elif intent_id == "TURN_INDICATOR_ON" or intent_id == "TURN_INDICATOR_OFF":
            direction_source = " ".join((str(slots.get("位置") or ""), str(slots.get("对象") or ""), str(slots.get("车外灯类型") or ""), evidence_text))
            parsed["DIRECTION"] = "LEFT" if "左" in direction_source else "RIGHT" if "右" in direction_source else None
        elif intent_id == "CRUISE_SET_SPEED":
            parsed["VALUE"] = self.normalize_numeric(raw, intent_id, evidence_text)
        elif intent_id == "CRUISE_SET_GAP":
            value = str(raw or "")
            parsed["VALUE"] = None
            parsed["MODE"] = None
            match = re.search(r"([1-4一二三四])\s*[挡档]", value)
            if match:
                token = match.group(1)
                number = int(token) if token.isdigit() else V1.cn_number(token)
                parsed["MODE"] = f"LEVEL_{number}"
            elif value in {"最小", "最低", "最近"}:
                parsed["MODE"] = "LEVEL_1"
            elif value in {"最大", "最高", "最远"}:
                parsed["MODE"] = "LEVEL_4"
            elif re.search(r"太大|太长|近一点|缩短", value + evidence_text):
                parsed["VALUE"] = "RELATIVE_CLOSER"
            elif re.search(r"太小|太短|远一点|加大", value + evidence_text):
                parsed["VALUE"] = "RELATIVE_FARTHER"
        elif intent_id == "WIPER_SET_SENSITIVITY":
            mode = str(slots.get("模式") or "")
            parsed["MODE"] = "RAIN_SENSOR" if mode in {"自动", "感应", "雨量感应"} else parsed.get("MODE")
        return parsed

    def formal_result(self, intent_id: str, slots: dict[str, Any], evidence_text: str, rule_id: str) -> dict[str, Any]:
        parsed = self.slots_for(intent_id, slots, evidence_text)
        result = self.base.resolution(intent_id, parsed, rule_id)
        result.update({
            "rule_ids": [rule_id], "candidate_intent_ids": [intent_id],
            "missing_slots": self.missing_slots(intent_id, parsed),
        })
        return result

    def missing_slots(self, intent_id: str, slots: dict[str, Any]) -> list[str]:
        if intent_id in {"STEERING_WHEEL_SET_EXTENSION", "STEERING_WHEEL_SET_TILT"}:
            return [] if slots.get("VALUE") is not None or slots.get("DIRECTION") is not None else ["VALUE_OR_DIRECTION"]
        if intent_id == "CRUISE_SET_GAP":
            return [] if slots.get("VALUE") is not None or slots.get("MODE") is not None else ["VALUE_OR_MODE"]
        return [slot for slot in self.by_id[intent_id].get("required_slots", []) if slots.get(slot) is None]

    def known_result(self, *, target: str, attribute: str, action: str, slots: dict[str, Any], evidence_text: str,
                     rule_id: str, value: Any = None, direction: str | None = None, mode: str | None = None) -> dict[str, Any]:
        subintent = {
            "规范动作": action, "规范对象": target, "控制属性": attribute,
            "位置": V1.extract_area(evidence_text, slots), "数值": value,
            "方向": direction, "模式": mode,
        }
        intent_id = f"KNOWN::{target}::{action}::{attribute}"
        return {
            "status": "RESOLVED", "intent_id": intent_id, "scope": "已知但不开放", "slots": {},
            "subintent": subintent, "complete": True, "evidence": rule_id, "rule_ids": [rule_id],
            "candidate_intent_ids": [], "missing_slots": [],
        }

    def resolve_frame(self, frame: dict[str, Any], clause: str | None = None) -> dict[str, Any]:
        slots = frame["slots"]
        op = str(slots.get("操作") or "")
        op_class = self.op_class(op)
        obj = str(slots.get("对象") or "")
        obj_fun = str(slots.get("对象功能") or "")
        feature = str(slots.get("功能") or "")
        adjust = str(slots.get("调节内容") or "")
        mode = str(slots.get("模式") or "")
        inside_light = str(slots.get("车内灯类型") or "")
        outside_light = str(slots.get("车外灯类型") or "")
        subfeature = str(slots.get("子功能") or "")
        evidence = self.combined(slots)

        # Formal zero-coverage candidates and their exact structural evidence.
        if obj in {"后视镜", "外后视镜"} and obj_fun == "加热" and op_class in {"ON", "OFF"}:
            return self.formal_result("MIRROR_HEATING_ON" if op_class == "ON" else "MIRROR_HEATING_OFF", slots, evidence, "V3-FORMAL-001")
        if (obj in {"座椅", "座椅坐垫", "坐垫"}) and ("倾斜" in evidence or adjust in {"倾角", "整体倾角"}):
            return self.formal_result("SEAT_TILT_SET_ANGLE", slots, evidence, "V3-FORMAL-002")
        if obj in {"后视镜", "外后视镜"} and adjust in {"方向", "角度"} and not obj_fun:
            return self.formal_result("MIRROR_SET_ANGLE", slots, evidence, "V3-FORMAL-003")
        if obj == "天窗" and op in {"翘起", "后翘", "上翘", "下收", "收下"}:
            return self.formal_result("SUNROOF_SET_TILT", slots, evidence, "V3-FORMAL-004")
        cruise_feature = any(token in feature for token in ("巡航",)) and not any(token in subfeature + feature for token in ("LIMITER", "限速"))
        if cruise_feature and adjust in {"速度", "车速"}:
            return self.formal_result("CRUISE_SET_SPEED", slots, evidence, "V3-FORMAL-005")
        if cruise_feature and adjust in {"距离", "跟车距离"}:
            return self.formal_result("CRUISE_SET_GAP", slots, evidence, "V3-FORMAL-006")
        if (obj in {"转向灯", "左转向灯", "右转向灯"} or "转向灯" in outside_light) and op_class in {"ON", "OFF"} and "预览" not in obj_fun:
            return self.formal_result("TURN_INDICATOR_ON" if op_class == "ON" else "TURN_INDICATOR_OFF", slots, evidence, "V3-FORMAL-007")
        if obj in {"雨刮", "雨刮器", "雨刷"} and adjust == "灵敏度" and not re.search(r"速挡|速档", str(slots.get("value") or "")):
            return self.formal_result("WIPER_SET_SENSITIVITY", slots, evidence, "V3-FORMAL-008")
        if mode in {"自动驻车", "自动驻车制动"} and op_class in {"ON", "OFF"}:
            intent_id = "PARKING_BRAKE_AUTO_APPLY_ENABLE" if op_class == "ON" else "PARKING_BRAKE_AUTO_APPLY_DISABLE"
            return self.formal_result(intent_id, slots, evidence, "V3-FORMAL-009")

        # Explicit ordinary cabin cognition. Every rule requires structured object/function + action evidence.
        if (obj == "阅读灯" or inside_light == "阅读灯") and op_class in {"ON", "OFF"}:
            return self.known_result(target="READING_LIGHT", attribute="STATE", action="TURN_ON" if op_class == "ON" else "TURN_OFF", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-001")
        if (obj in {"车内灯", "舱内灯", "顶灯"} or inside_light in {"车内灯", "舱内灯", "顶灯"}) and op_class in {"ON", "OFF"}:
            return self.known_result(target="CABIN_LIGHT", attribute="STATE", action="TURN_ON" if op_class == "ON" else "TURN_OFF", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-002")
        if obj == "空调" and op_class in {"ON", "OFF"} and adjust not in {"温度", "风量", "风速", "风力", "风向", "模式"}:
            return self.known_result(target="HVAC", attribute="STATE", action="TURN_ON" if op_class == "ON" else "TURN_OFF", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-003")
        if adjust == "温度" and op_class == "ADJUST" and not (obj == "座椅" or obj_fun == "加热"):
            return self.known_result(target="HVAC", attribute="TEMPERATURE", action="ADJUST", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-004", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence))
        if adjust in {"风量", "风速", "风力", "风"} and op_class == "ADJUST" and not (obj == "座椅" or obj_fun == "通风"):
            return self.known_result(target="HVAC", attribute="FAN_SPEED", action="ADJUST", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-005", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence))
        if adjust == "风向" and op_class in {"ADJUST", "ON", "OFF"} and obj not in {"座椅", "屏", "屏幕", "扶手", "扶手台"}:
            action = "ADJUST" if op_class == "ADJUST" else "TURN_ON" if op_class == "ON" else "TURN_OFF"
            return self.known_result(target="HVAC", attribute="AIR_DIRECTION", action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-006", mode=str(self.raw_value(slots)) if self.raw_value(slots) is not None else None)
        hvac_modes = {"AC", "内循环", "外循环", "制冷", "制热", "自然风", "极速制冷", "除湿", "自动空调"}
        if (adjust == "模式" or obj == "空调") and mode in hvac_modes and op_class in {"ON", "OFF", "ADJUST"}:
            action = "TURN_OFF" if op_class == "OFF" else "TURN_ON" if op_class == "ON" else "ADJUST"
            return self.known_result(target="HVAC", attribute="MODE", action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-007", mode=mode)
        if obj == "座椅" and obj_fun == "加热" and op_class in {"ON", "OFF", "ADJUST"}:
            action = "TURN_ON" if op_class == "ON" else "TURN_OFF" if op_class == "OFF" else "ADJUST"
            return self.known_result(target="SEAT_HEATING", attribute="STATE" if op_class in {"ON", "OFF"} else "LEVEL", action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-008", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence))
        if obj == "座椅" and obj_fun == "通风" and op_class in {"ON", "OFF", "ADJUST"}:
            action = "TURN_ON" if op_class == "ON" else "TURN_OFF" if op_class == "OFF" else "ADJUST"
            return self.known_result(target="SEAT_VENTILATION", attribute="STATE" if op_class in {"ON", "OFF"} else "LEVEL", action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-009", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence))
        if (obj == "座椅" and obj_fun == "按摩" or obj_fun == "按摩") and op_class in {"ON", "OFF", "ADJUST"}:
            action = "TURN_ON" if op_class == "ON" else "TURN_OFF" if op_class == "OFF" else "ADJUST"
            return self.known_result(target="SEAT_MASSAGE", attribute="STATE" if op_class in {"ON", "OFF"} else "LEVEL", action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-010", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence), mode=mode or None)
        if (obj == "氛围灯" or inside_light == "氛围灯") and op_class in {"ON", "OFF", "ADJUST"}:
            attribute = "BRIGHTNESS" if adjust == "亮度" else "COLOR" if adjust == "颜色" else "MODE" if adjust == "模式" else "STATE"
            action = "TURN_ON" if op_class == "ON" else "TURN_OFF" if op_class == "OFF" else "ADJUST"
            return self.known_result(target="AMBIENT_LIGHT", attribute=attribute, action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-011", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence), mode=mode or None)
        if obj in {"遮阳帘", "遮阳幕", "遮光板", "幕布"} and op_class in {"ON", "OFF", "OPEN", "CLOSE", "ADJUST"}:
            action = "OPEN" if op_class in {"ON", "OPEN"} else "CLOSE" if op_class in {"OFF", "CLOSE"} else "ADJUST"
            return self.known_result(target="SUNSHADE", attribute="OPENING_POSITION" if op_class == "ADJUST" else "OPENING_STATE", action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-012", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence))
        if obj in {"屏", "屏幕", "显示屏", "中控屏", "娱乐屏", "娱乐屏幕", "HUD"} and (op_class in {"ON", "OFF"} or adjust == "亮度"):
            attribute = "BRIGHTNESS" if adjust == "亮度" else "STATE"
            action = "ADJUST" if attribute == "BRIGHTNESS" else "TURN_ON" if op_class == "ON" else "TURN_OFF"
            return self.known_result(target="DISPLAY", attribute=attribute, action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-013", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence))
        if obj in {"香氛", "香薰", "芳香"} and op_class in {"ON", "OFF", "ADJUST"}:
            action = "TURN_ON" if op_class == "ON" else "TURN_OFF" if op_class == "OFF" else "ADJUST"
            return self.known_result(target="FRAGRANCE", attribute="STATE" if op_class in {"ON", "OFF"} else "LEVEL", action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-014", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence), mode=mode or None)
        if obj == "方向盘" and obj_fun == "加热" and op_class in {"ON", "OFF", "ADJUST"}:
            action = "TURN_ON" if op_class == "ON" else "TURN_OFF" if op_class == "OFF" else "ADJUST"
            return self.known_result(target="STEERING_WHEEL_HEATING", attribute="STATE" if op_class in {"ON", "OFF"} else "LEVEL", action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-015", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence))
        if obj in {"天窗", "天幕"} and adjust in {"透光度", "透明度", "透光值"} and op_class == "ADJUST":
            return self.known_result(target="ROOF_GLASS", attribute="TRANSPARENCY", action="ADJUST", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-016", value=self.normalize_numeric(self.raw_value(slots), "KNOWN", evidence))
        if obj in {"屏", "屏幕", "显示屏", "娱乐屏", "娱乐屏幕"} and adjust == "方向" and op_class == "ADJUST":
            direction = "LEFT" if re.search(r"左|主驾|驾驶员", evidence) else "RIGHT" if re.search(r"右|副驾", evidence) else None
            if direction:
                return self.known_result(target="DISPLAY", attribute="POSITION", action="ADJUST", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-017", direction=direction)
        if obj in {"扶手", "扶手台"} and adjust == "方向" and op_class == "ADJUST":
            direction = "FORWARD" if re.search(r"前|主驾|驾驶员", evidence) else "BACKWARD" if re.search(r"后|后座", evidence) else None
            if direction:
                return self.known_result(target="ARMREST", attribute="POSITION", action="ADJUST", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-018", direction=direction)
        connectivity = " ".join((obj, obj_fun, feature, adjust))
        if any(token in connectivity for token in ("蓝牙", "热点", "WIFI", "WiFi", "wifi")) and op_class in {"ON", "OFF"} and "播放" not in connectivity:
            return self.known_result(target="CONNECTIVITY", attribute="STATE", action="TURN_ON" if op_class == "ON" else "TURN_OFF", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-019")
        if "无线充电" in connectivity and op_class in {"ON", "OFF"}:
            return self.known_result(target="WIRELESS_CHARGING", attribute="STATE", action="TURN_ON" if op_class == "ON" else "TURN_OFF", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-020")
        vehicle_modes = {"舒享", "舒享模式", "驻车舒享", "驻车舒享模式", "停车舒享", "停车舒享模式", "经济", "经济模式", "运动", "运动模式", "标准", "标准模式", "雪地", "雪地模式", "山地", "山地模式", "纯电", "纯电模式", "混动", "混动模式", "四驱", "四驱模式", "单踏板", "单踏板模式", "能量回收"}
        if adjust == "模式" and mode in vehicle_modes and op_class in {"ON", "OFF", "ADJUST"}:
            action = "TURN_OFF" if op_class == "OFF" else "TURN_ON" if op_class == "ON" else "SWITCH_MODE"
            return self.known_result(target="VEHICLE_MODE", attribute="MODE", action=action, slots=slots, evidence_text=evidence, rule_id="V3-CABIN-021", mode=mode)
        alert_feature = " ".join((obj, obj_fun, feature))
        if any(token in alert_feature for token in ("低速提示音", "低速报警")) and op_class in {"ON", "OFF"}:
            return self.known_result(target="EXTERIOR_ALERT_SOUND", attribute="STATE", action="TURN_ON" if op_class == "ON" else "TURN_OFF", slots=slots, evidence_text=evidence, rule_id="V3-CABIN-022")

        # Explicit non-control frames mislabeled under the broad MAC vehicle domain.
        if adjust in {"音量", "声音", "音", "声", "音效"} or feature in {"查询当前音量", "查询剩余电量", "查询续航里程", "胎压监测"} or str(slots.get("intent")) == "提供信息" and str(slots.get("功能") or "").startswith("查询"):
            return {"status": "NON_CONTROL", "rule_ids": ["V3-NONCONTROL-001"], "candidate_intent_ids": [], "reason": "STRUCTURED_INFORMATION_OR_MEDIA_CONTROL"}

        # Existing v2 deterministic rules, isolated to this frame to prevent cross-intent contamination.
        # Preserve the v2 resolver's text evidence for already-supported formal
        # semantics.  Structured slots remain authoritative, but some canonical
        # actions/values are expressed only in the aligned MAC clause.
        base_result = self.base.infer_registry(clause or evidence, slots)
        if base_result and base_result.get("status") == "RESOLVED":
            base_result.update({"rule_ids": ["V3-FRAME-001"], "candidate_intent_ids": [base_result["intent_id"]] if base_result["intent_id"] in self.formal else [],
                                "missing_slots": self.missing_slots(base_result["intent_id"], base_result["slots"]) if base_result["intent_id"] in self.by_id else []})
            return base_result
        if base_result and base_result.get("status") == "AMBIGUOUS":
            # An ambiguous semantic frame does not establish executable scope.
            # Keeping the base resolver's formal candidate scope here caused
            # broad/non-vehicle "light" utterances to be promoted from UNKNOWN
            # without a v3 rule or a uniquely resolved canonical intent.
            base_result.update({"candidate_scope": "未知", "rule_ids": [], "candidate_intent_ids": [], "missing_slots": []})
            return base_result
        return {"status": "AMBIGUOUS", "reason": "UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3", "candidate_scope": "未知", "rule_ids": [], "candidate_intent_ids": [], "missing_slots": []}

    def classify_no_frame(self, raw_text: str) -> dict[str, Any]:
        text = V1.normalize_text(raw_text)
        if not text or len(text) <= 2 or text in {"帮我弄一下", "你看着办", "差不多就行", "打开那个", "调一下", "设置一下", "别管了"}:
            return {"category": "明显残缺/垃圾输入", "reason": "EMPTY_SHORT_OR_DEICTIC", "rule_ids": ["V3-NOFRAME-004"], "resolution": None}
        action_present = bool(re.search(r"打开|开启|关闭|关掉|调(?:节|整|到|高|低)?|设置|升起|降下|锁定|解锁|加热|通风|按摩|鸣笛|刹车|加速|减速|变道|挂[PNDR]\s*挡", text, re.I))
        specific_targets = (
            "阅读灯", "车内灯", "空调", "座椅加热", "座椅通风", "座椅按摩", "氛围灯", "遮阳帘", "屏幕", "显示屏", "香氛", "方向盘加热",
            "后视镜加热", "近光灯", "远光灯", "雾灯", "驻车灯", "停车灯", "示宽灯", "示廓灯", "位置灯", "车窗", "车门", "天窗", "后备箱", "前舱盖", "雨刮", "巡航", "电子手刹", "驻车制动", "转向灯",
        )
        target_present = any(target in text for target in specific_targets)
        broad_light_only = bool(re.search(r"(?:车灯|灯光|把灯|开灯|关灯)", text)) and not any(target in text for target in specific_targets if target not in {"车内灯"})
        if action_present and target_present and not broad_light_only:
            synthetic_slots: dict[str, Any] = {"操作": "关闭" if re.search(r"关闭|关掉|关上", text) else "打开" if re.search(r"打开|开启", text) else "调节"}
            if "阅读灯" in text:
                synthetic_slots.update({"对象": "阅读灯", "车内灯类型": "阅读灯"})
            elif "车内灯" in text:
                synthetic_slots.update({"对象": "车内灯", "车内灯类型": "车内灯"})
            elif "方向盘加热" in text:
                synthetic_slots.update({"对象": "方向盘", "对象功能": "加热"})
            elif "座椅加热" in text:
                synthetic_slots.update({"对象": "座椅", "对象功能": "加热"})
            elif "座椅通风" in text:
                synthetic_slots.update({"对象": "座椅", "对象功能": "通风"})
            elif "座椅按摩" in text:
                synthetic_slots.update({"对象": "座椅", "对象功能": "按摩"})
            elif "氛围灯" in text:
                synthetic_slots.update({"对象": "氛围灯", "车内灯类型": "氛围灯"})
            elif "遮阳帘" in text:
                synthetic_slots.update({"对象": "遮阳帘"})
            elif "香氛" in text:
                synthetic_slots.update({"对象": "香氛"})
            elif "空调" in text:
                synthetic_slots.update({"对象": "空调"})
                if "温度" in text:
                    synthetic_slots["调节内容"] = "温度"
                elif re.search(r"风量|风速|风力", text):
                    synthetic_slots["调节内容"] = "风量"
            elif "屏幕" in text or "显示屏" in text:
                synthetic_slots.update({"对象": "屏幕"})
                if "亮度" in text:
                    synthetic_slots["调节内容"] = "亮度"
            structured = self.resolve_frame({"slots": synthetic_slots, "domain": "车载控制", "intent_key": "NO_FRAME_SYNTHETIC", "duplicate_slot_names": []})
            result = structured if structured.get("status") == "RESOLVED" else self.base.infer_registry(text, {})
            if result and result.get("status") == "RESOLVED":
                rule_id = "V3-NOFRAME-001" if result["scope"] == "正式可执行" else "V3-NOFRAME-002"
                result.update({"rule_ids": sorted(set(result.get("rule_ids", []) + [rule_id])), "candidate_intent_ids": [result["intent_id"]] if result["intent_id"] in self.formal else [],
                               "missing_slots": self.missing_slots(result["intent_id"], result["slots"]) if result["intent_id"] in self.by_id else []})
                return {"category": "明显车辆/座舱控制", "reason": "EXPLICIT_ACTION_SPECIFIC_TARGET", "rule_ids": result["rule_ids"], "resolution": result}
            return {"category": "明显车辆/座舱控制", "reason": "EXPLICIT_CONTROL_BUT_CONTRACT_UNRESOLVED", "rule_ids": [], "resolution": result}
        noncontrol = bool(re.search(r"播放|歌曲|音乐|歌手|导航|路线|地图|天气|气温|打电话|拨打|联系人|电影|电视剧|视频|收音机|电台|新闻|查询|多少|是什么|为什么|怎么样|知识|讲个|笑话", text))
        if noncontrol and not (action_present and target_present):
            return {"category": "明显非控制", "reason": "EXPLICIT_NON_CONTROL_DOMAIN_WITHOUT_CONTROL_PAIR", "rule_ids": ["V3-NOFRAME-003"], "resolution": None}
        if broad_light_only:
            return {"category": "明显车辆/座舱控制", "reason": "BROAD_LIGHT_MUST_REMAIN_AMBIGUOUS", "rule_ids": [], "resolution": {"status": "AMBIGUOUS", "reason": "BROAD_LIGHT_OBJECT", "candidate_scope": "未知", "rule_ids": [], "candidate_intent_ids": [], "missing_slots": []}}
        return {"category": "无法判断", "reason": "NO_HIGH_PRECISION_DOMAIN_EVIDENCE", "rule_ids": [], "resolution": None}


def old_unresolved_frame_occurrences(canonical: list[dict[str, Any]], old_resolver: V1.Resolver) -> list[dict[str, Any]]:
    result = []
    for occurrence in canonical:
        frames = occurrence["frames"]
        split_sens = occurrence["row"].get("split_sens") if isinstance(occurrence["row"].get("split_sens"), list) else []
        vehicle_frames = [frame for frame in frames if frame["domain"] == "车载控制"]
        # Reproduce baseline_v1 exactly, including its vehicle-frame index behavior in mixed-domain samples.
        for index, frame in enumerate(vehicle_frames):
            clause = split_sens[index] if len(split_sens) == len(frames) else occurrence["raw_text"]
            old = old_resolver.infer_registry(clause, frame["slots"])
            if old is None:
                result.append({"occurrence": occurrence, "frame_index": index, "frame": frame, "clause": clause})
    return result


def map_mac_v3(resolver: StructuredResolver, occurrence: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    row = occurrence["row"]
    raw_text = occurrence["raw_text"]
    frames = occurrence["frames"]
    split_sens = row.get("split_sens") if isinstance(row.get("split_sens"), list) else []
    applied_rules: list[str] = []
    candidate_details: list[dict[str, Any]] = []

    if not raw_text.strip():
        sample = V1.make_sample(source="MAC-SLU", file_name=occurrence["source_file"], source_id=occurrence["source_id"], raw_text=raw_text,
                                scope="未知", structure="歧义", tone="肯定", subintents=[], complete=False, review=True)
        meta = {"canonical_intent_ids": [], "review_reasons": ["EMPTY_SOURCE_QUERY"], "compound_flags": [], "applied_rule_ids": [], "candidate_intent_ids": [], "candidate_details": []}
    elif not frames:
        classification = resolver.classify_no_frame(raw_text)
        applied_rules.extend(classification["rule_ids"])
        resolution = classification["resolution"]
        if classification["category"] == "明显非控制":
            sample = V1.make_sample(source="MAC-SLU", file_name=occurrence["source_file"], source_id=occurrence["source_id"], raw_text=raw_text,
                                    scope="非控制", structure="单意图", tone=V1.polarity(raw_text), subintents=[], complete=False, review=False)
            meta = {"canonical_intent_ids": [], "review_reasons": [], "compound_flags": [], "applied_rule_ids": applied_rules, "candidate_intent_ids": [], "candidate_details": [], "no_frame_category": classification["category"]}
        elif resolution and resolution.get("status") == "RESOLVED":
            sample, base_meta = V1.assemble_control_sample([resolution], source="MAC-SLU", file_name=occurrence["source_file"], source_id=occurrence["source_id"], raw_text=raw_text)
            candidate_details = [{"intent_id": intent_id, "resolved": True, "complete": resolution["complete"], "missing_slots": resolution.get("missing_slots", []), "rule_ids": resolution.get("rule_ids", [])} for intent_id in resolution.get("candidate_intent_ids", [])]
            meta = {**base_meta, "applied_rule_ids": applied_rules, "candidate_intent_ids": resolution.get("candidate_intent_ids", []), "candidate_details": candidate_details, "no_frame_category": classification["category"]}
        else:
            reason = classification["reason"]
            scope = "正式可执行" if resolution and resolution.get("candidate_scope") == "正式可执行" else "未知"
            sample = V1.make_sample(source="MAC-SLU", file_name=occurrence["source_file"], source_id=occurrence["source_id"], raw_text=raw_text,
                                    scope=scope, structure="歧义", tone=V1.polarity(raw_text), subintents=[], complete=False, review=True)
            meta = {"canonical_intent_ids": [], "review_reasons": [reason], "compound_flags": [], "applied_rule_ids": applied_rules, "candidate_intent_ids": [], "candidate_details": [], "no_frame_category": classification["category"]}
    else:
        vehicle_results = []
        non_vehicle_count = 0
        non_control_vehicle_frames = 0
        for index, frame in enumerate(frames):
            if frame["domain"] != "车载控制":
                non_vehicle_count += 1
                continue
            clause = split_sens[index] if len(split_sens) == len(frames) else None
            resolved = resolver.resolve_frame(frame, clause)
            applied_rules.extend(resolved.get("rule_ids", []))
            if resolved.get("status") == "NON_CONTROL":
                non_control_vehicle_frames += 1
                continue
            vehicle_results.append(resolved)
            for intent_id in resolved.get("candidate_intent_ids", []):
                candidate_details.append({"intent_id": intent_id, "resolved": resolved.get("status") == "RESOLVED" and resolved.get("intent_id") == intent_id,
                                          "complete": bool(resolved.get("complete")), "missing_slots": resolved.get("missing_slots", []), "rule_ids": resolved.get("rule_ids", [])})
        if not vehicle_results and (non_vehicle_count or non_control_vehicle_frames):
            sample = V1.make_sample(source="MAC-SLU", file_name=occurrence["source_file"], source_id=occurrence["source_id"], raw_text=raw_text,
                                    scope="非控制", structure="单意图", tone=V1.polarity(raw_text), subintents=[], complete=False, review=False)
            meta = {"canonical_intent_ids": [], "review_reasons": [], "compound_flags": [], "applied_rule_ids": sorted(set(applied_rules)), "candidate_intent_ids": [], "candidate_details": []}
        else:
            expected_multi = len(frames) >= 2
            reasons = ["MIXED_CONTROL_NONCONTROL"] if vehicle_results and (non_vehicle_count or non_control_vehicle_frames) else []
            sample, base_meta = V1.assemble_control_sample(vehicle_results, source="MAC-SLU", file_name=occurrence["source_file"], source_id=occurrence["source_id"], raw_text=raw_text,
                                                           expected_multi=expected_multi, extra_reasons=reasons)
            meta = {**base_meta, "applied_rule_ids": sorted(set(applied_rules)), "candidate_intent_ids": sorted({x["intent_id"] for x in candidate_details}), "candidate_details": candidate_details}

    provenance = {
        "样本编号": sample["样本编号"], "source_dataset": "MAC-SLU", "source_file": occurrence["source_file"], "source_split": occurrence["source_split"],
        "source_row": occurrence["source_line"], "source_id": occurrence["source_id"], "raw_text": raw_text,
        "original_annotation": row.get("semantics"), "split_sens": row.get("split_sens"), "conversion_version": CONVERSION_VERSION,
    }
    mapping = {"样本编号": sample["样本编号"], **meta}
    return sample, provenance, mapping


def carry_forward_seed(source_pool: Path, source_provenance: dict[str, dict[str, Any]], source_mapping: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    samples, provenance, mappings = [], [], []
    for old_sample in load_jsonl(source_pool):
        old_id = old_sample["样本编号"]
        sample = dict(old_sample)
        sample["样本编号"] = V1.stable_id(sample["来源"], sample["原始文件"], sample["原始编号"], sample["原始文本"])
        sample["映射规则版本"] = MAPPING_VERSION
        samples.append(sample)
        prov = dict(source_provenance[old_id]); prov["样本编号"] = sample["样本编号"]; prov["conversion_version"] = CONVERSION_VERSION
        provenance.append(prov)
        mapping = dict(source_mapping[old_id]); mapping["样本编号"] = sample["样本编号"]; mapping["applied_rule_ids"] = []; mapping.setdefault("candidate_intent_ids", mapping.get("canonical_intent_ids", [])); mapping.setdefault("candidate_details", [])
        mappings.append(mapping)
    return samples, provenance, mappings


def build_pattern_audit(unresolved: list[dict[str, Any]], resolver: StructuredResolver, v1_sample_by_key: dict[tuple[str, str, str, str], dict[str, Any]]) -> tuple[list[dict[str, Any]], Counter[str]]:
    grouped: dict[str, dict[str, Any]] = {}
    rule_counts: Counter[str] = Counter()
    for item in unresolved:
        occurrence, frame = item["occurrence"], item["frame"]
        fields = semantic_fields(frame["slots"])
        signature = json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        entry = grouped.setdefault(signature, {**fields, "样本数量": 0, "示例文本": [], "当前转换结果": "未知/需要人工复核",
                                               "建议控制范围分布": Counter(), "候选正式意图": Counter(), "新增规则": Counter(), "无法映射原因": Counter(), "可确定结果": Counter()})
        entry["样本数量"] += 1
        if occurrence["raw_text"] not in entry["示例文本"] and len(entry["示例文本"]) < 5:
            entry["示例文本"].append(occurrence["raw_text"])
        new = resolver.resolve_frame(frame, item["clause"])
        if new.get("status") == "RESOLVED":
            entry["建议控制范围分布"][new["scope"]] += 1
            if new["intent_id"] in resolver.formal:
                entry["候选正式意图"][new["intent_id"]] += 1
            entry["可确定结果"]["是"] += 1
            for rule_id in new.get("rule_ids", []):
                entry["新增规则"][rule_id] += 1; rule_counts[rule_id] += 1
        elif new.get("status") == "NON_CONTROL":
            entry["建议控制范围分布"]["非控制"] += 1; entry["可确定结果"]["是"] += 1
            for rule_id in new.get("rule_ids", []):
                entry["新增规则"][rule_id] += 1; rule_counts[rule_id] += 1
        else:
            entry["建议控制范围分布"][new.get("candidate_scope", "未知")] += 1
            entry["可确定结果"]["否"] += 1
            entry["无法映射原因"][new.get("reason", "UNRESOLVED")] += 1
    rows = []
    for entry in grouped.values():
        entry["建议控制范围"] = dict(entry.pop("建议控制范围分布"))
        entry["候选正式意图"] = dict(entry["候选正式意图"])
        entry["新增规则"] = dict(entry["新增规则"])
        entry["无法映射原因"] = dict(entry["无法映射原因"])
        deterministic = entry.pop("可确定结果")
        entry["是否可确定映射"] = "是" if deterministic.get("否", 0) == 0 else "部分" if deterministic.get("是", 0) else "否"
        rows.append(entry)
    rows.sort(key=lambda row: (-row["样本数量"], str(row["原始操作"]), str(row["原始对象"])))
    return rows, rule_counts


def pattern_markdown(rows: list[dict[str, Any]]) -> str:
    lines = ["# MAC 未解析车辆语义模式审计（v3）", "", f"未解析 frame occurrence：{sum(row['样本数量'] for row in rows)}；去重模式：{len(rows)}。", "",
             "| 操作 | 对象 | 功能 | 位置类型 | 数值类型 | 模式类型 | 数量 | 示例 | 建议范围 | 候选正式意图 | 可确定 | 原因 |", "|---|---|---|---|---|---|---:|---|---|---|---|---|"]
    for row in rows:
        values = [row["原始操作"], row["原始对象"], json.dumps(row["原始功能"], ensure_ascii=False), row["原始位置类型"], row["原始数值类型"], row["原始模式类型"], row["样本数量"],
                  "；".join(row["示例文本"]), json.dumps(row["建议控制范围"], ensure_ascii=False), json.dumps(row["候选正式意图"], ensure_ascii=False), row["是否可确定映射"], json.dumps(row["无法映射原因"], ensure_ascii=False)]
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in values) + " |")
    return "\n".join(lines) + "\n"


def no_frame_audit(canonical: list[dict[str, Any]], resolver: StructuredResolver) -> tuple[list[dict[str, Any]], dict[str, Any], Counter[str]]:
    rows = []
    counts: Counter[str] = Counter()
    rule_counts: Counter[str] = Counter()
    for occurrence in canonical:
        if occurrence["frames"] or not occurrence["row"].get("semantics"):
            continue
        classification = resolver.classify_no_frame(occurrence["raw_text"])
        counts[classification["category"]] += 1
        rule_counts.update(classification["rule_ids"])
        resolution = classification["resolution"] or {}
        rows.append({
            "source_file": occurrence["source_file"], "source_split": occurrence["source_split"], "source_row": occurrence["source_line"], "source_id": occurrence["source_id"],
            "原始文本": occurrence["raw_text"], "分类": classification["category"], "分类原因": classification["reason"],
            "建议控制范围": resolution.get("scope") or resolution.get("candidate_scope") or ("非控制" if classification["category"] == "明显非控制" else "未知"),
            "候选正式意图": resolution.get("intent_id") if resolution.get("intent_id") in resolver.formal else None,
            "是否可确定映射": bool(resolution.get("status") == "RESOLVED" or classification["category"] == "明显非控制"),
            "新增规则": classification["rule_ids"],
        })
    if len(rows) != 3957:
        raise SystemExit(f"AUDIT_GATE_FAIL no usable frame expected=3957 actual={len(rows)}")
    summary = {"sample_count": len(rows), "classification_counts": dict(counts), "deterministically_resolved_count": sum(row["是否可确定映射"] for row in rows)}
    return rows, summary, rule_counts


def safety_review_list() -> list[dict[str, Any]]:
    samples = load_jsonl(BASELINE_V1 / "safety_boundary_pool_v1.jsonl")
    mappings = {row["样本编号"]: row for row in load_jsonl(BASELINE_V1 / "sample_mapping_metadata_v1.jsonl")}
    provenance = {row["样本编号"]: row for row in load_jsonl(BASELINE_V1 / "source_provenance_v1.jsonl")}
    rows = []
    for sample in samples:
        mapping = mappings[sample["样本编号"]]
        unresolved_count = sum(reason == "UNRESOLVED_SAFETY_SEMANTICS" for reason in mapping.get("review_reasons", []))
        if not unresolved_count:
            continue
        category = provenance[sample["样本编号"]]["original_annotation"]["安全边界类别"]
        suggestion = "保持歧义并人工复核" if sample["结构状态"] == "歧义" else "依据当前结构状态人工补充审计，不修改原句"
        for occurrence_index in range(1, unresolved_count + 1):
            rows.append({"原始编号": sample["原始编号"], "未解析子语义序号": occurrence_index, "原始文本": sample["原始文本"], "人工大类": category,
                         "当前结构结果": {"控制范围": sample["控制范围"], "结构状态": sample["结构状态"], "语气状态": sample["语气状态"], "子意图列表": sample["子意图列表"]},
                         "无法解析原因": ["UNRESOLVED_SAFETY_SEMANTICS"], "建议处理": suggestion})
    if len(rows) != 57:
        raise SystemExit(f"AUDIT_GATE_FAIL safety unresolved expected=57 actual={len(rows)}")
    return rows


def safety_markdown(rows: list[dict[str, Any]]) -> str:
    lines = ["# 安全边界种子待复核清单（57 条）", "", "本清单只报告，不修改人工原句或原表。", "",
             "| 原始编号 | 原始文本 | 人工大类 | 当前控制范围 | 当前结构 | 原因 | 建议 |", "|---:|---|---|---|---|---|---|"]
    for row in rows:
        current = row["当前结构结果"]
        lines.append(f"| {row['原始编号']} | {row['原始文本']} | {row['人工大类']} | {current['控制范围']} | {current['结构状态']} | {','.join(row['无法解析原因'])} | {row['建议处理']} |")
    return "\n".join(lines) + "\n"


def build_audits(canonical: list[dict[str, Any]], old_resolver: V1.Resolver, resolver: StructuredResolver) -> tuple[dict[str, Any], Counter[str]]:
    AUDIT_OUT.mkdir(parents=True, exist_ok=True)
    unresolved = old_unresolved_frame_occurrences(canonical, old_resolver)
    if len(unresolved) != 4627:
        raise SystemExit(f"AUDIT_GATE_FAIL unresolved frame occurrences expected=4627 actual={len(unresolved)}")
    v1_samples = load_jsonl(BASELINE_V1 / "full_nlu_canonical_raw_pool_v1.jsonl")
    patterns, rule_counts = build_pattern_audit(unresolved, resolver, {source_key(row): row for row in v1_samples})
    write_json(AUDIT_OUT / "mac_unresolved_vehicle_semantic_patterns_v3.json", {"unresolved_frame_occurrence_count": len(unresolved), "unique_canonical_sample_count": len({item['occurrence']['source_file'] + ':' + str(item['occurrence']['source_line']) for item in unresolved}), "pattern_count": len(patterns), "patterns": patterns})
    (AUDIT_OUT / "mac_unresolved_vehicle_semantic_patterns_v3.md").write_text(pattern_markdown(patterns), encoding="utf-8")

    no_frame_rows, no_frame_summary, no_frame_rule_counts = no_frame_audit(canonical, resolver)
    write_jsonl(AUDIT_OUT / "mac_no_usable_frame_audit_v3.jsonl", no_frame_rows)
    write_json(AUDIT_OUT / "mac_no_usable_frame_summary_v3.json", no_frame_summary)
    no_frame_md = ["# MAC 无可用 semantic frame 审计", "", f"样本数：{no_frame_summary['sample_count']}", ""]
    no_frame_md.extend(f"- {key}: {value}" for key, value in no_frame_summary["classification_counts"].items())
    (AUDIT_OUT / "mac_no_usable_frame_audit_v3.md").write_text("\n".join(no_frame_md) + "\n", encoding="utf-8")
    rule_counts.update(no_frame_rule_counts)

    safety_rows = safety_review_list()
    write_json(AUDIT_OUT / "safety_seed_unresolved_57_v3.json", safety_rows)
    (AUDIT_OUT / "safety_seed_unresolved_57_v3.md").write_text(safety_markdown(safety_rows), encoding="utf-8")
    summary = {"unresolved_frame_occurrences": len(unresolved), "unresolved_unique_samples": len({item['occurrence']['source_file'] + ':' + str(item['occurrence']['source_line']) for item in unresolved}),
               "semantic_pattern_count": len(patterns), "no_usable_frame": no_frame_summary, "safety_unresolved_count": len(safety_rows), "audit_rule_occurrence_counts": dict(rule_counts)}
    write_json(AUDIT_OUT / "audit_v3_summary.json", summary)
    write_json(AUDIT_OUT / "rule_occurrence_counts_v3.json", dict(rule_counts))
    return summary, rule_counts


def zero_coverage_audit(mac: dict[str, list[dict[str, Any]]], canonical: list[dict[str, Any]], resolver: StructuredResolver,
                        v2_samples: list[dict[str, Any]], v2_mappings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    v2_sample_by_id = {row["样本编号"]: row for row in v2_samples}
    v2_mapping_by_id = {row["样本编号"]: row for row in v2_mappings}
    candidates_raw: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    candidates_canonical: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    def inspect_occurrence(occurrence: dict[str, Any], target: defaultdict[str, list[dict[str, Any]]]) -> None:
        for frame in occurrence["frames"]:
            if frame["domain"] != "车载控制":
                continue
            result = resolver.resolve_frame(frame)
            for intent_id in result.get("candidate_intent_ids", []):
                if intent_id in ZERO_V1_INTENTS:
                    target[intent_id].append({"occurrence": occurrence, "frame": frame, "result": result})

    for file_name, rows in mac.items():
        for line_number, row in enumerate(rows, start=1):
            inspect_occurrence({"source_file": file_name, "source_split": file_name.removesuffix("_set.jsonl"), "source_line": line_number,
                                "source_id": str(row.get("id", line_number)), "raw_text": row.get("query", ""), "row": row, "frames": V1.flatten_semantics(row)}, candidates_raw)
    for occurrence in canonical:
        inspect_occurrence(occurrence, candidates_canonical)

    v2_coverage = V1.stats_for(v2_samples, v2_mappings, resolver.registry["formal_user_voice_intent_ids"])["formal_intent_positive_coverage"]
    report = []
    for intent_id in ZERO_V1_INTENTS:
        raw_items = candidates_raw[intent_id]
        canonical_items = candidates_canonical[intent_id]
        complete = sum(item["result"].get("complete", False) for item in canonical_items)
        missing = Counter(slot for item in canonical_items for slot in item["result"].get("missing_slots", []))
        examples = [{"原始文本": item["occurrence"]["raw_text"], "source_file": item["occurrence"]["source_file"], "source_row": item["occurrence"]["source_line"],
                     "MAC原始semantics": item["occurrence"]["row"].get("semantics"), "v3合同完整": item["result"].get("complete"), "缺失槽位": item["result"].get("missing_slots", [])}
                    for item in canonical_items[:8]]
        if v2_coverage[intent_id]:
            conclusion = "已恢复可进入正式正样本的可靠完整样本"
        elif complete:
            conclusion = "已恢复合同完整候选，但因多意图/语气/复核约束仍不进入正式正样本"
        elif canonical_items:
            conclusion = "仅发现缺槽或无法唯一确定的候选，保持零覆盖"
        else:
            conclusion = "公开数据与 canonical pool 均无候选，保持零覆盖"
        report.append({"canonical_intent_id": intent_id, "公开原始候选数量": len(raw_items), "canonical候选数量": len(canonical_items), "示例": examples,
                       "v1未映射原因": "结构字段路由缺失或整句其他子意图污染；v1 正式完整正样本为 0",
                       "依据R3可唯一恢复的合同完整候选": complete, "不能恢复时缺失内容": dict(missing),
                       "baseline_v2正式完整正样本": v2_coverage[intent_id], "恢复结论": conclusion})
    return report


def funnel_report(samples: list[dict[str, Any]], mappings: list[dict[str, Any]], formal_ids: list[str]) -> list[dict[str, Any]]:
    sample_by_id = {sample["样本编号"]: sample for sample in samples}
    details_by_intent: defaultdict[str, list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for mapping in mappings:
        sample = sample_by_id[mapping["样本编号"]]
        seen = set()
        for detail in mapping.get("candidate_details", []):
            intent_id = detail.get("intent_id")
            if intent_id in formal_ids and intent_id not in seen:
                details_by_intent[intent_id].append((sample, mapping, detail)); seen.add(intent_id)
        for intent_id in mapping.get("canonical_intent_ids", []):
            if intent_id in formal_ids and intent_id not in seen:
                details_by_intent[intent_id].append((sample, mapping, {"intent_id": intent_id, "resolved": True, "complete": sample["合同是否完整"], "missing_slots": []})); seen.add(intent_id)
    rows = []
    for intent_id in formal_ids:
        items = details_by_intent[intent_id]
        a = len(items)
        b_items = [item for item in items if item[2].get("resolved")]
        c_items = [item for item in b_items if item[2].get("complete")]
        d_items = [item for item in c_items if item[0]["结构状态"] == "单意图" and item[0]["语气状态"] == "肯定"]
        e_items = [item for item in d_items if not item[0]["是否需要人工复核"]]
        f_items = [item for item in e_items if item[0]["是否允许进入正式正样本"]]
        loss_cd = Counter()
        for sample, _, _ in c_items:
            if sample["结构状态"] != "单意图": loss_cd[f"结构状态={sample['结构状态']}"] += 1
            if sample["语气状态"] != "肯定": loss_cd[f"语气状态={sample['语气状态']}"] += 1
        loss_de = Counter(reason for sample, mapping, _ in d_items if sample["是否需要人工复核"] for reason in mapping.get("review_reasons", []))
        missing = Counter(slot for _, _, detail in b_items if not detail.get("complete") for slot in detail.get("missing_slots", []))
        rows.append({"canonical_intent_id": intent_id, "A_原始候选数量": a, "B_成功确定正式意图": len(b_items), "C_合同完整": len(c_items),
                     "D_单意图且肯定": len(d_items), "E_无需人工复核": len(e_items), "F_允许进入正式正样本": len(f_items),
                     "A到B损失": a - len(b_items), "B到C损失": len(b_items) - len(c_items), "B到C缺槽原因": dict(missing),
                     "C到D损失": len(c_items) - len(d_items), "C到D原因": dict(loss_cd), "D到E损失": len(d_items) - len(e_items), "D到E原因": dict(loss_de),
                     "E到F损失": len(e_items) - len(f_items)})
    return rows


def cabin_coverage_report(candidate_sample_ids: dict[str, set[str]], samples: list[dict[str, Any]], mappings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sample_by_id = {sample["样本编号"]: sample for sample in samples}
    mapping_by_id = {mapping["样本编号"]: mapping for mapping in mappings}
    rule_to_category = {rule_id: category for category, rule_ids in TARGET_CABIN_RULES.items() for rule_id in rule_ids}
    mapped_by_category: defaultdict[str, set[str]] = defaultdict(set)
    for mapping in mappings:
        for rule_id in mapping.get("applied_rule_ids", []):
            if rule_id in rule_to_category:
                mapped_by_category[rule_to_category[rule_id]].add(mapping["样本编号"])
    rows = []
    for category in TARGET_CABIN_RULES:
        candidates = candidate_sample_ids.get(category, set())
        mapped = mapped_by_category.get(category, set())
        rows.append({"类别": category, "总样本数": len(candidates), "成功映射数": len(candidates & mapped),
                     "仍需复核数": sum(sample_by_id[sid]["是否需要人工复核"] for sid in candidates if sid in sample_by_id),
                     "未知数": sum(sample_by_id[sid]["控制范围"] == "未知" for sid in candidates if sid in sample_by_id)})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()

    for path, expected, name in ((REGISTRY_PATH, REGISTRY_SHA256, "R3"), (SCHEMA_PATH, SCHEMA_SHA256, "schema"), (RULES_V2_PATH, RULES_V2_SHA256, "mapping v2")):
        if sha256_path(path) != expected:
            raise SystemExit(f"IMMUTABLE_GATE_FAIL {name} expected={expected} actual={sha256_path(path)}")
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    rules_v2 = yaml.safe_load(RULES_V2_PATH.read_text(encoding="utf-8"))
    rules_v3 = yaml.safe_load(RULES_V3_PATH.read_text(encoding="utf-8"))
    cognition = yaml.safe_load(COGNITION_PATH.read_text(encoding="utf-8"))
    if rules_v3["mapping_rule_version"] != MAPPING_VERSION:
        raise SystemExit("RULE_VERSION_GATE_FAIL")

    mac, source_info, raw_hashes_before = V1.load_sources()
    mac_audit, duplicate_groups, canonical = V1.mac_audit(mac)
    old_resolver = V1.Resolver(registry, rules_v2, cognition)
    resolver = StructuredResolver(registry, rules_v2, rules_v3, cognition)
    audit_summary, audit_rule_counts = build_audits(canonical, old_resolver, resolver)
    if args.audit_only:
        unique_rule_samples: defaultdict[str, set[str]] = defaultdict(set)
        for occurrence in canonical:
            _, _, mapping = map_mac_v3(resolver, occurrence)
            source_identity = f"{occurrence['source_file']}:{occurrence['source_id']}:{occurrence['raw_text']}"
            for rule_id in mapping.get("applied_rule_ids", []):
                unique_rule_samples[rule_id].add(source_identity)
        unique_counts = {rule_id: len(values) for rule_id, values in sorted(unique_rule_samples.items())}
        write_json(AUDIT_OUT / "rule_unique_sample_counts_v3.json", unique_counts)
        audit_summary["rule_unique_sample_counts"] = unique_counts
        write_json(AUDIT_OUT / "audit_v3_summary.json", audit_summary)
        print(json.dumps({"status": "AUDIT_ONLY_PASS", "audit_dir": str(AUDIT_OUT), "summary": audit_summary}, ensure_ascii=False, indent=2))
        return 0

    # Full build is allowed only after counts are frozen into every v3 rule.
    configured_counts = {rule["rule_id"]: rule["corresponding_sample_count"] for rule in rules_v3["rules"]}
    if any(not isinstance(value, int) for value in configured_counts.values()) or rules_v3.get("status") != "FROZEN_FOR_BASELINE_V2_BUILD":
        raise SystemExit("RULE_AUDIT_GATE_FAIL v3 counts/status are not frozen")

    V1.MAPPING_VERSION = MAPPING_VERSION
    V1.CONVERSION_VERSION = CONVERSION_VERSION

    mac_samples, provenance, mappings = [], [], []
    cabin_candidates_by_source: defaultdict[str, set[str]] = defaultdict(set)
    for occurrence in canonical:
        sample, prov, mapping = map_mac_v3(resolver, occurrence)
        mac_samples.append(sample); provenance.append(prov); mappings.append(mapping)
        for frame in occurrence["frames"]:
            if frame["domain"] == "车载控制":
                for category in resolver.cabin_candidate_categories(frame["slots"]):
                    cabin_candidates_by_source[category].add(sample["样本编号"])
        for rule_id in mapping.get("applied_rule_ids", []):
            for category, target_rules in TARGET_CABIN_RULES.items():
                if rule_id in target_rules:
                    cabin_candidates_by_source[category].add(sample["样本编号"])

    actual_rule_sample_counts: defaultdict[str, set[str]] = defaultdict(set)
    for mapping in mappings:
        for rule_id in mapping.get("applied_rule_ids", []):
            actual_rule_sample_counts[rule_id].add(mapping["样本编号"])
    actual_counts = {rule_id: len(actual_rule_sample_counts.get(rule_id, set())) for rule_id in configured_counts}
    count_mismatches = {rule_id: {"configured": configured_counts[rule_id], "actual": actual_counts[rule_id]}
                        for rule_id in configured_counts if configured_counts[rule_id] != actual_counts[rule_id]}
    if count_mismatches:
        write_json(AUDIT_OUT / "rule_count_gate_failure.json", count_mismatches)
        raise SystemExit(f"RULE_COUNT_GATE_FAIL {count_mismatches}")

    v1_prov = {row["样本编号"]: row for row in load_jsonl(BASELINE_V1 / "source_provenance_v1.jsonl")}
    v1_map = {row["样本编号"]: row for row in load_jsonl(BASELINE_V1 / "sample_mapping_metadata_v1.jsonl")}
    weak_samples, weak_prov, weak_map = carry_forward_seed(BASELINE_V1 / "weak_seed_pool_v1.jsonl", v1_prov, v1_map)
    safety_samples, safety_prov, safety_map = carry_forward_seed(BASELINE_V1 / "safety_boundary_pool_v1.jsonl", v1_prov, v1_map)
    all_samples = mac_samples + weak_samples + safety_samples
    all_provenance = provenance + weak_prov + safety_prov
    all_mappings = mappings + weak_map + safety_map

    BASELINE_V2.mkdir(parents=True, exist_ok=True)
    pool_paths = {
        "mac_canonical_pool": BASELINE_V2 / "mac_slu_canonical_pool_v2.jsonl",
        "weak_seed_pool": BASELINE_V2 / "weak_seed_pool_v2.jsonl",
        "safety_boundary_pool": BASELINE_V2 / "safety_boundary_pool_v2.jsonl",
        "combined_canonical_raw_pool": BASELINE_V2 / "full_nlu_canonical_raw_pool_v2.jsonl",
    }
    for key, values in (("mac_canonical_pool", mac_samples), ("weak_seed_pool", weak_samples), ("safety_boundary_pool", safety_samples), ("combined_canonical_raw_pool", all_samples)):
        write_jsonl(pool_paths[key], values)
    write_jsonl(BASELINE_V2 / "source_provenance_v2.jsonl", all_provenance)
    write_jsonl(BASELINE_V2 / "sample_mapping_metadata_v2.jsonl", all_mappings)

    validations = {key: V1.validate_paths([path]) for key, path in pool_paths.items()}
    if not all(result["status"] == "PASS" for result in validations.values()):
        write_json(BASELINE_V2 / "schema_validation_failure_v2.json", validations)
        raise SystemExit("SCHEMA_GATE_FAIL baseline_v2")
    validation_total = sum(result["sample_count"] for result in validations.values())
    validation_valid = sum(result["valid_sample_count"] for result in validations.values())
    compliance = f"{100 * validation_valid / validation_total:.6f}%"
    if compliance != "100.000000%":
        raise SystemExit("SCHEMA_GATE_FAIL compliance below 100%")

    stats_v2 = V1.stats_for(all_samples, all_mappings, registry["formal_user_voice_intent_ids"])
    report_v1 = json.loads((BASELINE_V1 / "full_nlu_mapping_report_v1.json").read_text(encoding="utf-8"))
    stats_v1 = report_v1["combined_statistics"]
    coverage_v1 = stats_v1["formal_intent_positive_coverage"]
    coverage_v2 = stats_v2["formal_intent_positive_coverage"]

    v1_samples = load_jsonl(BASELINE_V1 / "full_nlu_canonical_raw_pool_v1.jsonl")
    v1_by_key = {source_key(sample): sample for sample in v1_samples}
    v2_mapping_by_id = {mapping["样本编号"]: mapping for mapping in all_mappings}
    diff_rows = []
    trace_failures = []
    transition_reasons: Counter[str] = Counter()
    scope_transitions: Counter[str] = Counter()
    positive_transitions: Counter[str] = Counter()
    positive_loss_by_rule: Counter[str] = Counter()
    positive_gain_by_rule: Counter[str] = Counter()
    for new in all_samples:
        old = v1_by_key[source_key(new)]
        scope_transitions[f"{old['控制范围']} -> {new['控制范围']}"] += 1
        positive_transitions[f"{old['是否允许进入正式正样本']} -> {new['是否允许进入正式正样本']}"] += 1
        changes = {field: {"v1": old[field], "v2": new[field]} for field in ("控制范围", "结构状态", "语气状态", "合同是否完整", "是否允许进入正式正样本", "是否需要人工复核") if old[field] != new[field]}
        if not changes:
            continue
        mapping = v2_mapping_by_id[new["样本编号"]]
        rule_ids = mapping.get("applied_rule_ids", [])
        if old["是否允许进入正式正样本"] and not new["是否允许进入正式正样本"]:
            positive_loss_by_rule.update(rule_ids or ["NO_NEW_RULE_CONSERVATIVE_REVIEW"])
        if not old["是否允许进入正式正样本"] and new["是否允许进入正式正样本"]:
            positive_gain_by_rule.update(rule_ids or ["UNTRACED"])
        if (old["控制范围"] == "未知" or old["是否需要人工复核"]) and new["控制范围"] in {"正式可执行", "已知但不开放"} and not rule_ids:
            trace_failures.append({"source_key": source_key(new), "changes": changes})
        transition_reasons.update(rule_ids or ["NO_NEW_RULE_LABEL_ONLY_CHANGE"])
        diff_rows.append({"来源": new["来源"], "原始文件": new["原始文件"], "原始编号": new["原始编号"], "原始文本": new["原始文本"], "changes": changes,
                          "applied_rule_ids": rule_ids, "canonical_intent_ids_v2": mapping.get("canonical_intent_ids", []), "review_reasons_v2": mapping.get("review_reasons", [])})
    if trace_failures:
        write_json(BASELINE_V2 / "traceability_gate_failure_v2.json", trace_failures)
        raise SystemExit(f"TRACEABILITY_GATE_FAIL count={len(trace_failures)}")
    write_jsonl(BASELINE_V2 / "baseline_v1_to_v2_changed_samples.jsonl", diff_rows)

    zero_report = zero_coverage_audit(mac, canonical, resolver, all_samples, all_mappings)
    write_json(AUDIT_OUT / "zero_coverage_10_intents_v3.json", zero_report)
    zero_md = ["# 十个 baseline_v1 零覆盖正式意图审计", "", "| Intent | 公开候选 | canonical候选 | 合同完整候选 | v2正式正样本 | 结论 |", "|---|---:|---:|---:|---:|---|"]
    zero_md.extend(f"| {row['canonical_intent_id']} | {row['公开原始候选数量']} | {row['canonical候选数量']} | {row['依据R3可唯一恢复的合同完整候选']} | {row['baseline_v2正式完整正样本']} | {row['恢复结论']} |" for row in zero_report)
    (AUDIT_OUT / "zero_coverage_10_intents_v3.md").write_text("\n".join(zero_md) + "\n", encoding="utf-8")
    funnel = funnel_report(all_samples, all_mappings, registry["formal_user_voice_intent_ids"])
    write_json(AUDIT_OUT / "formal_71_positive_funnel_v3.json", funnel)
    funnel_md = ["# 71 项正式意图正样本漏斗", "", "| Intent | A候选 | B确定 | C合同完整 | D单意图肯定 | E无需复核 | F正式正样本 |", "|---|---:|---:|---:|---:|---:|---:|"]
    funnel_md.extend(f"| {row['canonical_intent_id']} | {row['A_原始候选数量']} | {row['B_成功确定正式意图']} | {row['C_合同完整']} | {row['D_单意图且肯定']} | {row['E_无需人工复核']} | {row['F_允许进入正式正样本']} |" for row in funnel)
    (AUDIT_OUT / "formal_71_positive_funnel_v3.md").write_text("\n".join(funnel_md) + "\n", encoding="utf-8")

    cabin_report = cabin_coverage_report(cabin_candidates_by_source, all_samples, all_mappings)
    write_json(AUDIT_OUT / "known_unsupported_cabin_coverage_v3.json", cabin_report)
    cabin_md = ["# 普通座舱已知但不开放覆盖", "", "总样本数由 MAC 结构化对象/功能确定，不要求动作已解析；各统计可重叠。", "", "| 类别 | 总样本 | 成功映射 | 仍需复核 | 未知 |", "|---|---:|---:|---:|---:|"]
    cabin_md.extend(f"| {row['类别']} | {row['总样本数']} | {row['成功映射数']} | {row['仍需复核数']} | {row['未知数']} |" for row in cabin_report)
    (AUDIT_OUT / "known_unsupported_cabin_coverage_v3.md").write_text("\n".join(cabin_md) + "\n", encoding="utf-8")

    review_v2 = Counter(reason for mapping in all_mappings for reason in mapping.get("review_reasons", []))
    zero_v2 = [intent_id for intent_id, count in coverage_v2.items() if count == 0]
    weak_v2 = [intent_id for intent_id, count in coverage_v2.items() if 0 < count < 10]
    diff_report = {
        "report_version": "full_nlu_baseline_v1_v2_diff_v1", "build_date": str(date.today()),
        "headline": {
            "正式可执行": {"v1": stats_v1["control_scope"]["正式可执行"], "v2": stats_v2["control_scope"].get("正式可执行", 0)},
            "已知但不开放": {"v1": stats_v1["control_scope"]["已知但不开放"], "v2": stats_v2["control_scope"].get("已知但不开放", 0)},
            "非控制": {"v1": stats_v1["control_scope"]["非控制"], "v2": stats_v2["control_scope"].get("非控制", 0)},
            "未知": {"v1": stats_v1["control_scope"]["未知"], "v2": stats_v2["control_scope"].get("未知", 0)},
            "需要人工复核": {"v1": stats_v1["needs_review"], "v2": stats_v2["needs_review"]},
            "正式正样本": {"v1": stats_v1["formal_positive_allowed"], "v2": stats_v2["formal_positive_allowed"]},
            "71项零覆盖": {"v1": len([x for x in coverage_v1.values() if x == 0]), "v2": len(zero_v2)},
            "71项弱覆盖": {"v1": len([x for x in coverage_v1.values() if 0 < x < 10]), "v2": len(weak_v2)},
        },
        "changed_sample_count": len(diff_rows), "change_reason_by_rule": dict(transition_reasons),
        "control_scope_transition_matrix": dict(scope_transitions),
        "formal_positive_transition_matrix": dict(positive_transitions),
        "formal_positive_loss_by_rule": dict(positive_loss_by_rule),
        "formal_positive_gain_by_rule": dict(positive_gain_by_rule),
        "zero_intents_v2": zero_v2, "weak_intents_v2": weak_v2,
        "needs_review_reason_distribution_v1": report_v1["needs_review_reason_distribution"], "needs_review_reason_distribution_v2": dict(review_v2),
        "traceability_gate": {"status": "PASS", "untraced_improvement_count": 0},
    }
    write_json(BASELINE_V2 / "baseline_v1_to_v2_diff_report.json", diff_report)
    diff_md = ["# Full NLU baseline_v1 → baseline_v2 对比", "", "| 指标 | v1 | v2 | 变化 |", "|---|---:|---:|---:|"]
    for name, values in diff_report["headline"].items():
        diff_md.append(f"| {name} | {values['v1']} | {values['v2']} | {values['v2'] - values['v1']:+d} |")
    diff_md += ["", "## 控制范围迁移", "", "| 迁移 | 样本数 |", "|---|---:|"]
    diff_md.extend(f"| {transition} | {count} |" for transition, count in sorted(scope_transitions.items()))
    diff_md += ["", "正式可执行总量下降主要来自两类保守纠正：原先误入正式范围的普通座舱能力转为已知但不开放，以及无唯一灯型/对象解释的样本回到未知并保持歧义。", "",
                "## 变化规则追溯", "", "| rule_id / 原因 | 发生变化的样本数 |", "|---|---:|"]
    diff_md.extend(f"| {rule_id} | {count} |" for rule_id, count in sorted(transition_reasons.items()))
    diff_md += ["", "`NO_NEW_RULE_LABEL_ONLY_CHANGE` 仅包含保守降级或统一装配结果变化，不包含未知/复核到正式可执行或已知但不开放的提升。",
                "所有未知/复核到正式可执行或已知但不开放的变化均通过新增 rule_id 溯源，未追溯变化数为 0。", ""]
    (BASELINE_V2 / "baseline_v1_to_v2_diff_report.md").write_text("\n".join(diff_md), encoding="utf-8")

    report = {
        "report_version": "full_nlu_mapping_report_v2", "registry_version": registry["registry_version"], "registry_sha256": REGISTRY_SHA256,
        "schema_version": SCHEMA_VERSION, "schema_sha256": SCHEMA_SHA256, "mapping_rule_version": MAPPING_VERSION,
        "mapping_rule_path": str(RULES_V3_PATH.relative_to(ROOT)), "mapping_rule_sha256": sha256_path(RULES_V3_PATH),
        "manual_override_rule_version": "manual_override_v1", "manual_override_sha256": sha256_path(OVERRIDES_PATH),
        "schema_validator_sha256": sha256_path(ROOT / "scripts/full_nlu/validate_full_nlu_schema.py"),
        "build_script_sha256": sha256_path(Path(__file__)), "conversion_version": CONVERSION_VERSION,
        "input_gate": source_info["gate"], "raw_source_sha256": raw_hashes_before, "mac_audit": {key: value for key, value in mac_audit.items() if key != "slot_value_counts"},
        "combined_statistics": stats_v2, "needs_review_reason_distribution": dict(review_v2),
        "formal_intent_gaps": {"zero": zero_v2, "weak_lt_10": weak_v2, "adequate_ge_10": [intent_id for intent_id, count in coverage_v2.items() if count >= 10]},
        "schema_validation": {"all_pass": True, "compliance_rate": compliance, "per_pool": validations},
        "audit_artifacts": {
            "unresolved_vehicle_patterns": str((AUDIT_OUT / "mac_unresolved_vehicle_semantic_patterns_v3.json").relative_to(ROOT)),
            "no_frame": str((AUDIT_OUT / "mac_no_usable_frame_audit_v3.jsonl").relative_to(ROOT)),
            "zero_coverage": str((AUDIT_OUT / "zero_coverage_10_intents_v3.json").relative_to(ROOT)),
            "funnel_71": str((AUDIT_OUT / "formal_71_positive_funnel_v3.json").relative_to(ROOT)),
            "cabin": str((AUDIT_OUT / "known_unsupported_cabin_coverage_v3.json").relative_to(ROOT)),
            "safety_57": str((AUDIT_OUT / "safety_seed_unresolved_57_v3.json").relative_to(ROOT)),
        },
        "diff": diff_report, "historical_poc": {"active_full_nlu_dependency_count": 0, "used": False},
        "stage_boundaries": {"augmentation": False, "training": False, "final_split": False},
    }
    report_path = BASELINE_V2 / "full_nlu_mapping_report_v2.json"
    write_json(report_path, report)
    report_md = ["# Full NLU baseline_v2 映射覆盖审计报告", "", f"- R3: `{REGISTRY_SHA256}`", f"- mapping: `{MAPPING_VERSION}` / `{sha256_path(RULES_V3_PATH)}`",
                 f"- manual overrides: `manual_override_v1` / `{sha256_path(OVERRIDES_PATH)}`",
                 f"- schema validator: `{sha256_path(ROOT / 'scripts/full_nlu/validate_full_nlu_schema.py')}`",
                 f"- canonical raw pool: {len(all_samples)} / `{sha256_path(pool_paths['combined_canonical_raw_pool'])}`",
                 f"- `SCHEMA_COMPLIANCE_RATE={compliance}`", "", "## v1/v2 关键变化", ""]
    report_md.extend(f"- {name}: {values['v1']} → {values['v2']} ({values['v2'] - values['v1']:+d})" for name, values in diff_report["headline"].items())
    report_md += ["", "正式范围下降来自对普通座舱误标与宽泛/不唯一对象的保守纠正；安全合同未放宽。正式正样本净减少 9 = 新增 22 - 移出 31。", "",
                  "## 重点审计", "",
                  f"- 未解析车辆 semantic frame：{audit_summary['unresolved_frame_occurrences']} 个 occurrence，{audit_summary['unresolved_unique_samples']} 个 canonical 样本，{audit_summary['semantic_pattern_count']} 个去重模式。",
                  f"- 无可用 semantic frame：{audit_summary['no_usable_frame']['sample_count']} 条；确定性处理 {audit_summary['no_usable_frame']['deterministically_resolved_count']} 条。",
                  f"- 安全种子待复核：{audit_summary['safety_unresolved_count']} 个语义 occurrence（原文未修改）。",
                  f"- baseline_v2 零覆盖正式意图：{', '.join(zero_v2) if zero_v2 else '无'}。", "",
                  "## needs_review v2 原因分布", "", "| 原因 | 数量 |", "|---|---:|"]
    report_md.extend(f"| {reason} | {count} |" for reason, count in review_v2.most_common())
    report_md += ["", "## 审计资产", "",
                  "- 4627 frame 模式：`data/nlu/full/audit_v3/mac_unresolved_vehicle_semantic_patterns_v3.json` / `.md`",
                  "- 3957 无 frame：`data/nlu/full/audit_v3/mac_no_usable_frame_audit_v3.jsonl` / `.md`",
                  "- 十项零覆盖审计：`data/nlu/full/audit_v3/zero_coverage_10_intents_v3.json` / `.md`",
                  "- 71 项漏斗：`data/nlu/full/audit_v3/formal_71_positive_funnel_v3.json` / `.md`",
                  "- 普通座舱覆盖：`data/nlu/full/audit_v3/known_unsupported_cabin_coverage_v3.json` / `.md`",
                  "- 安全种子 57 occurrence：`data/nlu/full/audit_v3/safety_seed_unresolved_57_v3.json` / `.md`", "",
                  "未扩写、未训练、未生成最终 train/dev/test。", ""]
    (BASELINE_V2 / "full_nlu_mapping_report_v2.md").write_text("\n".join(report_md), encoding="utf-8")

    raw_hashes_after = {name: sha256_path(ROOT / name) for name in V1.MAC_EXPECTED}
    for book in source_info["workbooks"].values():
        raw_hashes_after[book["book"]["source_file"]] = sha256_path(Path(book["book"]["source_path"]))
    if raw_hashes_after != raw_hashes_before:
        raise SystemExit("RAW_IMMUTABILITY_GATE_FAIL")

    manifest_path = BASELINE_V2 / "full_nlu_baseline_manifest_v2.json"
    files = sorted(path for path in [*BASELINE_V2.glob("*"), *AUDIT_OUT.glob("*")] if path.is_file() and path != manifest_path)
    manifest = {
        "manifest_version": "full_nlu_baseline_manifest_v2", "status": "FROZEN_CANONICAL_RAW_BASELINE_NO_SPLIT_NO_TRAINING",
        "registry_version": registry["registry_version"], "registry_sha256": REGISTRY_SHA256,
        "schema_version": SCHEMA_VERSION, "schema_sha256": SCHEMA_SHA256, "mapping_rule_version": MAPPING_VERSION,
        "mapping_rule_sha256": sha256_path(RULES_V3_PATH), "manual_override_rule_version": "manual_override_v1",
        "manual_override_sha256": sha256_path(OVERRIDES_PATH), "schema_validator_sha256": sha256_path(ROOT / "scripts/full_nlu/validate_full_nlu_schema.py"),
        "build_script_sha256": sha256_path(Path(__file__)), "conversion_version": CONVERSION_VERSION,
        "raw_sources_immutable_verified": True, "SCHEMA_COMPLIANCE_RATE": compliance,
        "sample_counts": {"mac_raw": 20542, "mac_canonical": len(mac_samples), "weak_seed": len(weak_samples), "safety_boundary": len(safety_samples), "combined": len(all_samples)},
        "generated_files": [{"path": str(path.relative_to(ROOT)), "sha256": sha256_path(path), "bytes": path.stat().st_size} for path in files],
    }
    write_json(manifest_path, manifest)
    print(json.dumps({"status": "PASS", "baseline_v2": str(BASELINE_V2), "combined_count": len(all_samples), "SCHEMA_COMPLIANCE_RATE": compliance,
                      "manifest": str(manifest_path), "manifest_sha256": sha256_path(manifest_path), "headline_diff": diff_report["headline"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
