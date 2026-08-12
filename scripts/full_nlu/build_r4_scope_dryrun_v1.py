from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml


EXPECTED_HASHES = {
    "data/nlu/spec/intent_registry_r4_final.yaml": "d4f3d203308a5eb9a039fee31851c110b21bafc7727f23fd6f2b83edefadad4e",
    "初筛/full_nlu_source_screen_v1.jsonl": "59340fce2c394cb793a37ba2b301379f4ef9794c9301d0983c6b37680e09123c",
    "train_set.jsonl": "d1e9a63fa61ef2d5eec4ef543356fb53d653070916c5ceaf72962047f9aef681",
    "dev_set.jsonl": "02ccb2bae0fa1923fb0e3bcdd5d0c13635ac93cfd2880d8a8affd0481157efb1",
    "test_set.jsonl": "1b3e8243ea9a9bb544a18b571401c4a057f0246c07d26a3e2a638890d9300572",
}

REGISTRY_VERSION = "sys-014-semantic-hardening-r4-final"
GUIDANCE_WARNING = "GUIDANCE_VERSION_METADATA_MISMATCH"
SCOPES = ("FORMAL_EXECUTABLE", "KNOWN_CONTROL_BYPASS", "NON_CONTROL", "UNKNOWN_OOD")
BUILD_STATUSES = (
    "AUTO_CORE_CANDIDATE",
    "BOUNDARY_REVIEW",
    "SEMANTIC_REVIEW",
    "SOURCE_QUARANTINE",
    "MALFORMED_EXCLUDED",
)
POLARITIES = ("AFFIRMATIVE", "NEGATIVE", "CANCEL", "NOT_APPLICABLE")

SCREEN_CATEGORY = "初筛总分类"
SOURCE_ANNOTATION = "源annotation状态"
TEXT_STRUCTURE = "文本结构候选"
RAW_TEXT = "原始文本"
SOURCE_FILE = "原始文件"
SOURCE_ID = "原始编号"
SAMPLE_ID = "样本编号"

OPEN_ACTIONS = ("完全打开", "全部打开", "开启", "打开", "开一下", "开开", "开下", "启动", "激活")
CLOSE_ACTIONS = ("完全关闭", "全部关闭", "关闭", "关一下", "关掉", "关上", "关了", "关下", "熄灭", "停用", "禁用")
ENABLE_ACTIONS = ("启用", "开启", "打开", "启动", "激活")
DISABLE_ACTIONS = ("停用", "禁用", "关闭", "关掉", "停止")
LOCK_ACTIONS = ("锁定", "上锁", "落锁", "锁上")
UNLOCK_ACTIONS = ("解锁", "开锁")
NEGATION_PREFIXES = ("不要", "不想", "别", "禁止", "不准", "不能", "不要再")
CANCEL_PREFIXES = ("取消", "撤销", "停止")

HIGH_RISK_INTENTS = {
    "DOOR_OPEN", "DOOR_CLOSE", "DOOR_SET_POSITION", "DOOR_LOCK", "DOOR_UNLOCK",
    "HEADLIGHT_SET_MODE", "HAZARD_LIGHT_ON", "HAZARD_LIGHT_OFF", "TURN_INDICATOR_ON",
    "TURN_INDICATOR_OFF", "LOW_BEAM_ON", "LOW_BEAM_OFF", "HIGH_BEAM_ON", "HIGH_BEAM_OFF",
    "FOG_LIGHT_ON", "FOG_LIGHT_OFF", "GEAR_SET", "GEAR_CHANGE_MODE_SET", "CRUISE_ENABLE",
    "CRUISE_DISABLE", "CRUISE_SET_SPEED", "CRUISE_SET_GAP", "ACCELERATE", "DECELERATE",
    "BRAKE", "EMERGENCY_BRAKE", "LANE_CHANGE", "LANE_KEEP", "EVASIVE_STEER",
    "PARKING_BRAKE_APPLY", "PARKING_BRAKE_RELEASE", "PARKING_BRAKE_AUTO_APPLY_ENABLE",
    "PARKING_BRAKE_AUTO_APPLY_DISABLE",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=False))
            handle.write("\n")


def evidence(text: str, term: str, kind: str) -> dict[str, Any] | None:
    start = text.find(term)
    if start < 0:
        return None
    return {"kind": kind, "text": term, "span": [start, start + len(term)]}


def first_evidence(text: str, terms: Iterable[str], kind: str) -> dict[str, Any] | None:
    matches = [evidence(text, term, kind) for term in terms]
    found = [item for item in matches if item is not None]
    if not found:
        return None
    return sorted(found, key=lambda item: (item["span"][0], -len(item["text"])))[0]


def all_evidence(text: str, terms: Iterable[str], kind: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for term in terms:
        start = 0
        while True:
            index = text.find(term, start)
            if index < 0:
                break
            found.append({"kind": kind, "text": term, "span": [index, index + len(term)]})
            start = index + len(term)
    return sorted(found, key=lambda item: (item["span"][0], -len(item["text"])))


def polarity_for_action(text: str, action_ev: dict[str, Any] | None) -> tuple[str, dict[str, Any] | None]:
    if action_ev is None:
        return "NOT_APPLICABLE", None
    start = action_ev["span"][0]
    prefix = text[:start]
    for token in CANCEL_PREFIXES:
        pos = prefix.rfind(token)
        if pos >= 0:
            absolute = pos
            return "CANCEL", {"kind": "polarity", "text": token, "span": [absolute, absolute + len(token)]}
    for token in NEGATION_PREFIXES:
        pos = prefix.rfind(token)
        if pos >= 0:
            absolute = pos
            return "NEGATIVE", {"kind": "polarity", "text": token, "span": [absolute, absolute + len(token)]}
    return "AFFIRMATIVE", None


CHINESE_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def chinese_number(token: str) -> int | None:
    if token in CHINESE_DIGITS:
        return CHINESE_DIGITS[token]
    if token == "十":
        return 10
    if "十" in token and len(token) <= 3:
        left, right = token.split("十", 1)
        tens = CHINESE_DIGITS.get(left, 1) if left else 1
        ones = CHINESE_DIGITS.get(right, 0) if right else 0
        return tens * 10 + ones
    if token == "一百":
        return 100
    return None


NUMERIC_RE = re.compile(r"(?P<prefix>百分之)?(?P<num>\d+(?:\.\d+)?|[零〇一二两三四五六七八九十百]{1,3})(?P<unit>%|公里每小时|千米每小时|公里|千米|毫米|厘米|米|度)?")


def numeric_candidates(text: str) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for match in NUMERIC_RE.finditer(text):
        raw_num = match.group("num")
        try:
            number: float | int = float(raw_num) if "." in raw_num else int(raw_num)
        except ValueError:
            parsed = chinese_number(raw_num)
            if parsed is None:
                continue
            number = parsed
        prefix = match.group("prefix") or ""
        unit = match.group("unit")
        if prefix:
            unit = "%"
        values.append({"raw": match.group(0), "value": number, "unit": unit, "span": [match.start(), match.end()]})
    return values


def percent_value(text: str) -> tuple[dict[str, Any] | None, str | None]:
    if "一半" in text:
        start = text.index("一半")
        return {"原始值": "一半", "规范值": 50, "单位": "%", "span": [start, start + 2]}, None
    vague = first_evidence(text, ("一点点", "稍微", "一点", "留条缝", "一部分"), "prohibited_value_inference")
    if vague:
        return None, "CONTRACT_CHECK_FAILED_PROHIBITED_PERCENT_INFERENCE"
    candidates = [value for value in numeric_candidates(text) if value["unit"] == "%"]
    if len(candidates) != 1:
        return None, "CONTRACT_CHECK_FAILED_PERCENT_VALUE_MISSING_OR_AMBIGUOUS"
    item = candidates[0]
    return {"原始值": item["raw"], "规范值": item["value"], "单位": "%", "span": item["span"]}, None


def generic_numeric_value(text: str, expected_type: str) -> tuple[dict[str, Any] | None, str | None]:
    candidates = numeric_candidates(text)
    if expected_type == "SPEED":
        candidates = [item for item in candidates if item["unit"] in ("公里每小时", "千米每小时", "公里", "千米")]
        unit = "km/h"
    elif expected_type == "DISTANCE":
        candidates = [item for item in candidates if item["unit"] in ("米",)]
        unit = "m"
    elif expected_type == "ANGLE":
        candidates = [item for item in candidates if item["unit"] == "度"]
        unit = "deg"
    elif expected_type == "LENGTH":
        candidates = [item for item in candidates if item["unit"] in ("毫米", "厘米")]
        unit = "mm"
    else:
        unit = None
    if len(candidates) != 1:
        return None, f"CONTRACT_CHECK_FAILED_{expected_type}_VALUE_MISSING_OR_AMBIGUOUS"
    item = candidates[0]
    normalized = item["value"] * 10 if expected_type == "LENGTH" and item["unit"] == "厘米" else item["value"]
    return {"原始值": item["raw"], "规范值": normalized, "单位": unit, "span": item["span"]}, None


@dataclass
class RuleDefinition:
    intent_id: str
    object_terms: tuple[str, ...]
    action_terms: tuple[str, ...] = ()
    excludes: tuple[str, ...] = ()
    direction_terms: dict[str, tuple[str, ...]] = field(default_factory=dict)
    mode_terms: dict[str, tuple[str, ...]] = field(default_factory=dict)
    special: str | None = None
    force_review: bool = False


def make_rule_definitions() -> dict[str, RuleDefinition]:
    rules: dict[str, RuleDefinition] = {}

    def add(intent_id: str, objects: tuple[str, ...], actions: tuple[str, ...] = (), **kwargs: Any) -> None:
        rules[intent_id] = RuleDefinition(intent_id, objects, actions, **kwargs)

    add("MIRROR_HEATING_ON", ("外后视镜加热", "后视镜加热", "后视镜除霜"), ENABLE_ACTIONS)
    add("MIRROR_HEATING_OFF", ("外后视镜加热", "后视镜加热", "后视镜除霜"), DISABLE_ACTIONS)
    add("SEAT_LONGITUDINAL_SET_POSITION", ("座椅",), ("前移", "后移", "往前挪", "往后挪", "往前调", "往后调", "前后移动", "滑轨"),
        excludes=("靠背", "椅背", "坐垫", "座盆", "整体倾角", "角度", "打开"), direction_terms={"FORWARD": ("前移", "往前挪", "往前调"), "BACKWARD": ("后移", "往后挪", "往后调")}, special="SEAT_DIRECTIONAL")
    add("SEAT_TILT_SET_ANGLE", ("座椅整体倾角", "座椅整体倾斜", "座盆", "坐垫前端", "坐垫后端"), ("设置", "调节", "调整", "抬高", "降低", "倾斜"), special="SEAT_DIRECTIONAL")
    add("SEAT_BACKREST_SET_ANGLE", ("靠背", "椅背", "靠背角度"), ("设置", "调节", "调整", "前倾", "后仰", "放倒", "直立", "往前调", "往后调"),
        direction_terms={"FORWARD": ("前倾", "直立", "往前调"), "BACKWARD": ("后仰", "放倒", "往后调")}, special="SEAT_DIRECTIONAL")
    add("SEAT_HEIGHT_SET_POSITION", ("座椅高度",), ("设置", "调节", "调整", "升高", "降低", "调高", "调低"),
        direction_terms={"UP": ("升高", "调高", "向上"), "DOWN": ("降低", "调低", "向下")}, special="SEAT_DIRECTIONAL")
    add("SEAT_LUMBAR_SET_HEIGHT", ("腰托高度", "腰部支撑高度"), ("设置", "调节", "调整", "上移", "下移", "调高", "调低"),
        direction_terms={"UP": ("上移", "调高", "向上"), "DOWN": ("下移", "调低", "向下")}, special="SEAT_DIRECTIONAL")
    add("SEAT_LUMBAR_SET_SUPPORT", ("腰托", "腰部支撑"), ("调节", "调整", "加强", "减弱", "往前调", "往后调"),
        direction_terms={"MORE": ("加强", "增加", "往前调"), "LESS": ("减弱", "减少", "往后调")}, special="SEAT_DIRECTIONAL")
    add("STEERING_WHEEL_SET_EXTENSION", ("方向盘伸缩", "方向盘前后位置"), ("设置", "调节", "调整", "伸出", "缩回", "前移", "后移"),
        direction_terms={"EXTEND": ("伸出", "前移"), "RETRACT": ("缩回", "后移")}, special="DIRECTIONAL")
    add("STEERING_WHEEL_SET_TILT", ("方向盘倾斜", "方向盘高度"), ("设置", "调节", "调整", "抬高", "降低", "上移", "下移"),
        direction_terms={"UP": ("抬高", "上移", "调高"), "DOWN": ("降低", "下移", "调低")}, special="DIRECTIONAL")
    add("DEFROST_ON", ("风挡除霜", "风挡除雾", "前除霜", "前除雾", "后除霜", "后除雾"), ENABLE_ACTIONS, excludes=("后视镜",))
    add("DEFROST_OFF", ("风挡除霜", "风挡除雾", "前除霜", "前除雾", "后除霜", "后除雾"), DISABLE_ACTIONS, excludes=("后视镜",))
    add("WINDSHIELD_HEATING_ON", ("风挡加热", "风窗加热", "前挡加热", "后风窗加热"), ENABLE_ACTIONS)
    add("WINDSHIELD_HEATING_OFF", ("风挡加热", "风窗加热", "前挡加热", "后风窗加热"), DISABLE_ACTIONS)
    add("ESC_ENABLE", ("车身电子稳定系统", "电子稳定系统", "车身稳定系统", "ESC", "ESP"), ENABLE_ACTIONS)
    add("ESC_DISABLE", ("车身电子稳定系统", "电子稳定系统", "车身稳定系统", "ESC", "ESP"), DISABLE_ACTIONS)
    trunk = ("后备箱", "后备厢", "尾门", "行李厢")
    add("TRUNK_OPEN", trunk, OPEN_ACTIONS, excludes=("前备箱", "前备厢", "车窗", "天窗", "设置", "高度", "开度", "挡"), special="ENDPOINT_OPEN")
    add("TRUNK_CLOSE", trunk, CLOSE_ACTIONS, excludes=("前备箱", "前备厢"), special="ENDPOINT_CLOSE")
    add("TRUNK_SET_POSITION", trunk + ("行李厢开度", "尾门开度"), ("设置", "调节", "调整", "调高", "调低", "开到", "开启到"), excludes=("前备箱", "前备厢"), special="PERCENT_0_100")
    add("TRUNK_LOCK", trunk, LOCK_ACTIONS, excludes=("前备箱", "前备厢"))
    add("TRUNK_UNLOCK", trunk, UNLOCK_ACTIONS, excludes=("前备箱", "前备厢"))
    hood = ("前舱盖", "引擎盖", "发动机舱盖")
    add("HOOD_OPEN", hood, OPEN_ACTIONS)
    add("HOOD_CLOSE", hood, CLOSE_ACTIONS)
    add("GEAR_SET", ("挡", "档", "倒挡", "倒档", "前进挡", "空挡", "驻车挡"), ("挂", "切换", "设置", "换", "进入"),
        excludes=("解锁", "座椅", "记忆", "雨刮", "雨刷", "风量", "音效", "灵敏度", "自动挡", "手动挡", "换挡模式"), special="GEAR")
    add("GEAR_CHANGE_MODE_SET", ("换挡模式", "手动换挡", "自动换挡", "手动挡", "自动挡"), ("设置", "切换", "改为", "换成", "进入"), special="GEAR_CHANGE_MODE")
    add("HORN_ACTIVATE", ("鸣笛", "汽车喇叭", "车喇叭"), ("鸣笛", "按", "响", "启动"), excludes=("音响",), special="HORN_COMMAND")
    add("MIRROR_FOLD", ("后视镜", "外后视镜"), ("折叠", "收起", "收回"), excludes=("加热", "除霜", "自动折叠", "锁车", "模式", "系统"))
    add("MIRROR_UNFOLD", ("后视镜", "外后视镜"), ("展开", "伸开"), excludes=("加热", "除霜", "调节", "页面", "界面", "设置"))
    add("MIRROR_SET_ANGLE", ("后视镜角度", "后视镜方向", "外后视镜角度"), ("设置", "调节", "调整", "转向"),
        direction_terms={"LEFT": ("向左", "往左"), "RIGHT": ("向右", "往右"), "UP": ("向上", "往上"), "DOWN": ("向下", "往下")}, special="MIRROR_ANGLE")
    add("SUNROOF_OPEN", ("天窗",), OPEN_ACTIONS,
        excludes=("遮阳帘", "窗帘", "翘起", "下收", "电话", "音乐", "导航", "空调", "车窗", "车门", "后备箱", "一条缝", "留条缝"), special="ENDPOINT_OPEN")
    add("SUNROOF_CLOSE", ("天窗",), CLOSE_ACTIONS,
        excludes=("遮阳帘", "窗帘", "翘起", "下收", "电话", "音乐", "导航", "空调", "车窗", "车门", "后备箱"), special="ENDPOINT_CLOSE")
    add("SUNROOF_SET_TILT", ("天窗",), ("翘起", "下收", "起翘", "收平"),
        direction_terms={"UP": ("翘起", "起翘"), "DOWN": ("下收", "收平")}, special="DIRECTIONAL")
    add("CRUISE_ENABLE", ("巡航",), ENABLE_ACTIONS, excludes=("速度", "车距", "距离", "间距", "跟车"))
    add("CRUISE_DISABLE", ("巡航",), DISABLE_ACTIONS, excludes=("速度", "车距", "距离", "间距", "跟车"))
    add("CRUISE_SET_SPEED", ("巡航速度", "巡航设到", "巡航设置到"), ("设置", "设为", "设到", "调到", "设置到"), special="CRUISE_SPEED")
    add("CRUISE_SET_GAP", ("巡航跟车距离", "巡航车距", "跟车距离", "巡航间距"), ("设置", "调节", "调整", "增大", "减小", "远一点", "近一点"), special="CRUISE_GAP")
    add("HEADLIGHT_SET_MODE", ("大灯", "前照灯", "主灯"), OPEN_ACTIONS + CLOSE_ACTIONS + ("自动", "位置灯", "日间行车灯"),
        excludes=("近光灯", "远光灯", "自适应大灯"), special="HEADLIGHT_MODE")
    add("HAZARD_LIGHT_ON", ("危险警示灯", "危险报警灯", "双闪警示灯", "双闪灯", "双跳灯", "双闪"), ENABLE_ACTIONS)
    add("HAZARD_LIGHT_OFF", ("危险警示灯", "危险报警灯", "双闪警示灯", "双闪灯", "双跳灯", "双闪"), DISABLE_ACTIONS)
    add("TURN_INDICATOR_ON", ("转向灯", "左转向灯", "右转向灯"), ENABLE_ACTIONS + ("使用",),
        direction_terms={"LEFT": ("左转向灯", "左边的转向灯", "左转灯"), "RIGHT": ("右转向灯", "右边的转向灯", "右转灯")}, special="TURN_ON")
    add("TURN_INDICATOR_OFF", ("转向灯", "左转向灯", "右转向灯"), DISABLE_ACTIONS,
        direction_terms={"LEFT": ("左转向灯", "左边的转向灯", "左转灯"), "RIGHT": ("右转向灯", "右边的转向灯", "右转灯")})
    add("LOW_BEAM_ON", ("近光灯",), ENABLE_ACTIONS)
    add("LOW_BEAM_OFF", ("近光灯",), DISABLE_ACTIONS)
    add("HIGH_BEAM_ON", ("远光灯",), ENABLE_ACTIONS)
    add("HIGH_BEAM_OFF", ("远光灯",), DISABLE_ACTIONS, excludes=("增强",))
    add("FOG_LIGHT_ON", ("雾灯", "前雾灯", "后雾灯"), ENABLE_ACTIONS, excludes=("除雾",))
    add("FOG_LIGHT_OFF", ("雾灯", "前雾灯", "后雾灯"), DISABLE_ACTIONS, excludes=("除雾",))
    add("PARKING_LIGHT_ON", ("驻车灯",), ENABLE_ACTIONS)
    add("PARKING_LIGHT_OFF", ("驻车灯",), DISABLE_ACTIONS)
    add("WINDOW_OPEN", ("车窗", "窗户"), OPEN_ACTIONS + ("降下", "降到底", "降到最低", "一键降窗"),
        excludes=("页面", "界面", "设置", "电话", "音乐", "导航", "空调", "遮阳帘", "窗帘", "天窗", "车门", "后备箱", "阅读灯",
                  "模式", "加热", "除霜", "除雾", "童锁", "车窗锁", "窗户锁", "锁键", "闭锁", "短升短降", "挡", "略微", "已经"), special="WINDOW_OPEN")
    add("WINDOW_CLOSE", ("车窗", "窗户"), CLOSE_ACTIONS + ("升起", "升到底", "升到顶", "升到最高", "一键升窗"),
        excludes=("页面", "界面", "设置", "电话", "音乐", "导航", "空调", "遮阳帘", "窗帘", "天窗", "车门", "后备箱", "阅读灯",
                  "模式", "加热", "热力", "除霜", "除雾", "童锁", "车窗锁", "窗户锁", "锁键", "闭锁", "短升短降", "挡", "已经"), special="WINDOW_CLOSE")
    add("WINDOW_SET_POSITION", ("车窗", "窗户", "车窗开度"), ("设置", "调节", "调整", "开到", "降到", "升到"), special="WINDOW_PERCENT")
    add("DOOR_OPEN", ("车门", "左前门", "右前门", "左后门", "右后门"), OPEN_ACTIONS,
        excludes=("调节页面", "设置页面", "设置界面", "调节界面"), special="DOOR_OPEN")
    add("DOOR_CLOSE", ("车门", "左前门", "右前门", "左后门", "右后门"), CLOSE_ACTIONS, special="DOOR_CLOSE")
    add("DOOR_SET_POSITION", ("车门", "左前门", "右前门", "左后门", "右后门", "车门开度", "车门开启幅度"),
        ("设置", "调节", "调整", "开到", "打开到"), special="DOOR_PERCENT")
    add("DOOR_LOCK", ("车门", "中控锁"), LOCK_ACTIONS)
    add("DOOR_UNLOCK", ("车门", "中控锁"), UNLOCK_ACTIONS, excludes=("解锁模式",))
    add("WIPER_SET_MODE", ("雨刮", "雨刷"), ("设置", "切换", "打开", "关闭", "快刮", "慢刮", "间歇", "自动"),
        excludes=("灵敏度", "挡位调节", "档位调节", "挡位设置", "档位设置", "设置页面", "设置界面", "自动雨刮设置"), special="WIPER_MODE")
    add("WIPER_SET_SENSITIVITY", ("雨刮灵敏度", "雨刷灵敏度", "雨量感应灵敏度"), ("设置", "调节", "调整", "调高", "调低"), special="WIPER_SENSITIVITY")
    parking = ("驻车制动", "电子驻车", "电子手刹", "手刹")
    add("PARKING_BRAKE_APPLY", parking, ("施加", "拉起", "拉上", "开启", "打开"), excludes=("自动驻车制动",))
    add("PARKING_BRAKE_RELEASE", parking, ("释放", "松开", "解除", "关闭", "关掉"), excludes=("自动驻车制动",))
    add("PARKING_BRAKE_AUTO_APPLY_ENABLE", ("驻车制动自动施加", "自动驻车制动"), ENABLE_ACTIONS)
    add("PARKING_BRAKE_AUTO_APPLY_DISABLE", ("驻车制动自动施加", "自动驻车制动"), DISABLE_ACTIONS)
    add("ACCELERATE", ("加速", "快一点", "提速"), ("加速", "快一点", "提速"), special="SPEED_DELTA")
    add("DECELERATE", ("减速", "慢一点", "降速"), ("减速", "慢一点", "降速"), special="SPEED_DELTA")
    add("BRAKE", ("制动", "刹车"), ("制动", "刹车", "踩刹车"), excludes=("紧急", "驻车", "停车制动", "自动"), special="BRAKE")
    add("EMERGENCY_BRAKE", ("紧急制动", "紧急刹车", "急刹车"), ("紧急制动", "紧急刹车", "急刹车"), special="EMERGENCY_BRAKE")
    add("LANE_CHANGE", ("变道", "换道", "变更车道", "切换车道"), ("变道", "换道", "变更", "切换"),
        direction_terms={"LEFT": ("向左", "往左", "左侧", "左边"), "RIGHT": ("向右", "往右", "右侧", "右边")}, special="DIRECTIONAL")
    add("LANE_KEEP", ("保持当前车道", "保持车道"), ("保持",), special="LANE_KEEP_COMMAND")
    add("EVASIVE_STEER", ("避险转向", "紧急避让", "避让转向"), ("执行", "转向", "避让"),
        direction_terms={"LEFT": ("向左", "往左", "左侧", "左边"), "RIGHT": ("向右", "往右", "右侧", "右边")}, special="DIRECTIONAL")
    add("AUTO_PARK_ENABLE", ("自动泊车",), ENABLE_ACTIONS)
    return rules


def build_area_aliases(registry: dict[str, Any]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for canonical, item in registry.get("area_catalog", {}).items():
        candidates = [item.get("semantic_frame_value"), *(item.get("examples") or [])]
        for alias in candidates:
            if isinstance(alias, str) and len(alias) >= 2:
                aliases[alias] = canonical
    aliases.update({
        "左前门": "LEFT_FRONT", "右前门": "RIGHT_FRONT", "左后门": "LEFT_REAR", "右后门": "RIGHT_REAR",
        "前排车窗": "FRONT_ROW", "后排车窗": "REAR_ROW", "所有车窗": "ALL", "全部车窗": "ALL", "全车车窗": "ALL",
        "二排所有车门": "REAR_ROW", "后排所有车门": "REAR_ROW",
        "前雾灯": "FRONT", "后雾灯": "REAR", "前风挡": "FRONT", "后风挡": "REAR", "后风窗": "REAR",
    })
    return aliases


def extract_area(text: str, allowed_areas: list[str], aliases: dict[str, str]) -> tuple[dict[str, Any] | None, str | None]:
    if ("副驾后" in text or "主驾后" in text
            or ("副驾" in text and any(token in text for token in ("二排", "后排")))
            or ("主驾" in text and any(token in text for token in ("二排", "后排")))):
        return None, "AREA_EVIDENCE_AMBIGUOUS"
    matches: list[tuple[int, int, str, str]] = []
    for alias, canonical in aliases.items():
        if canonical not in allowed_areas:
            continue
        start = text.find(alias)
        if start >= 0:
            matches.append((start, start + len(alias), alias, canonical))
    if not matches:
        return None, None
    matches.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    filtered: list[tuple[int, int, str, str]] = []
    for item in matches:
        if any(item[0] >= prev[0] and item[1] <= prev[1] for prev in filtered):
            continue
        filtered.append(item)
    canonicals = {item[3] for item in filtered}
    if len(canonicals) != 1:
        return None, "AREA_EVIDENCE_AMBIGUOUS"
    start, end, raw, canonical = filtered[0]
    return {"原始值": raw, "规范值": canonical, "span": [start, end]}, None


def extract_direction(text: str, terms: dict[str, tuple[str, ...]]) -> tuple[dict[str, Any] | None, str | None]:
    matches: list[tuple[int, str, str]] = []
    for canonical, aliases in terms.items():
        for alias in aliases:
            start = text.find(alias)
            if start >= 0:
                matches.append((start, alias, canonical))
    canonicals = {item[2] for item in matches}
    if not matches:
        return None, None
    if len(canonicals) != 1:
        return None, "DIRECTION_EVIDENCE_AMBIGUOUS"
    start, raw, canonical = sorted(matches, key=lambda item: (item[0], -len(item[1])))[0]
    return {"原始值": raw, "规范值": canonical, "span": [start, start + len(raw)]}, None


def extract_mode(text: str, terms: dict[str, tuple[str, ...]]) -> tuple[dict[str, Any] | None, str | None]:
    matches: list[tuple[int, str, str]] = []
    for canonical, aliases in terms.items():
        for alias in aliases:
            start = text.find(alias)
            if start >= 0:
                matches.append((start, alias, canonical))
    if not matches:
        return None, None
    canonicals = {item[2] for item in matches}
    if len(canonicals) != 1:
        return None, "MODE_EVIDENCE_AMBIGUOUS"
    start, raw, canonical = sorted(matches, key=lambda item: (item[0], -len(item[1])))[0]
    return {"原始值": raw, "规范值": canonical, "span": [start, start + len(raw)]}, None


def special_slots(rule: RuleDefinition, text: str) -> tuple[dict[str, Any], list[str]]:
    slots: dict[str, Any] = {}
    failures: list[str] = []
    special = rule.special
    if special in ("PERCENT_0_100", "WINDOW_PERCENT", "DOOR_PERCENT"):
        value, error = percent_value(text)
        if error:
            failures.append(error)
        elif value:
            number = value["规范值"]
            if special == "WINDOW_PERCENT" and not (1 <= number <= 99):
                failures.append("CONTRACT_CHECK_FAILED_WINDOW_ENDPOINT_MUST_ROUTE_OPEN_CLOSE")
            elif special != "WINDOW_PERCENT" and not (0 <= number <= 100):
                failures.append("CONTRACT_CHECK_FAILED_PERCENT_OUT_OF_RANGE")
            else:
                slots["VALUE"] = value
    elif special == "CRUISE_SPEED":
        value, error = generic_numeric_value(text, "SPEED")
        if error:
            failures.append(error)
        else:
            slots["VALUE"] = value
    elif special == "SPEED_DELTA":
        absolute = re.search(r"(?:加速|减速|提速|降速)到\s*[零〇一二两三四五六七八九十百\d]", text)
        if absolute:
            failures.append("CONTRACT_CHECK_FAILED_ABSOLUTE_SPEED_TARGET_WITHOUT_CRUISE")
        else:
            candidates = [item for item in numeric_candidates(text) if item["unit"] in ("公里每小时", "千米每小时", "公里", "千米")]
            if len(candidates) == 1:
                item = candidates[0]
                slots["VALUE"] = {"原始值": item["raw"], "规范值": item["value"], "单位": "km/h", "span": item["span"]}
            elif len(candidates) > 1:
                failures.append("CONTRACT_CHECK_FAILED_SPEED_DELTA_AMBIGUOUS")
    elif special == "GEAR":
        modes = {
            "P": ("P挡", "P档", "驻车挡", "驻车档"), "N": ("N挡", "N档", "空挡", "空档"),
            "D": ("D挡", "D档", "前进挡", "前进档"), "R": ("R挡", "R档", "倒挡", "倒档"),
        }
        mode, error = extract_mode(text, modes)
        if error or not mode:
            failures.append(error or "CONTRACT_CHECK_FAILED_GEAR_MODE_MISSING")
        else:
            mode["physical_mapping_status"] = "VEHICLE_CAPABILITY_MAPPING_REQUIRED" if mode["规范值"] == "R" else "NOT_RESOLVED_IN_GOLD_BUILD"
            slots["MODE"] = mode
    elif special == "GEAR_CHANGE_MODE":
        mode, error = extract_mode(text, {"MANUAL": ("手动换挡", "手动挡", "手动模式"), "AUTOMATIC": ("自动换挡", "自动挡", "自动模式")})
        if error or not mode:
            failures.append(error or "CONTRACT_CHECK_FAILED_GEAR_CHANGE_MODE_MISSING")
        else:
            slots["MODE"] = mode
    elif special == "HEADLIGHT_MODE":
        close_ev = first_evidence(text, CLOSE_ACTIONS, "mode_action")
        open_ev = first_evidence(text, OPEN_ACTIONS, "mode_action")
        daytime = first_evidence(text, ("日间行车灯", "日间行车大灯"), "mode")
        position = first_evidence(text, ("位置灯",), "mode")
        if close_ev:
            mode = {"原始值": close_ev["text"], "规范值": "OFF", "span": close_ev["span"]}
            error = None
        elif daytime:
            mode = {"原始值": daytime["text"], "规范值": "DAYTIME_RUNNING_LIGHTS", "span": daytime["span"]}
            error = None
        elif position:
            mode = {"原始值": position["text"], "规范值": "POSITION", "span": position["span"]}
            error = None
        elif "自动大灯" in text or "大灯自动模式" in text:
            raw = "自动大灯" if "自动大灯" in text else "大灯自动模式"
            start = text.index(raw)
            mode = {"原始值": raw, "规范值": "AUTO", "span": [start, start + len(raw)]}
            error = None
        elif open_ev:
            mode = {"原始值": open_ev["text"], "规范值": "ON", "span": open_ev["span"]}
            error = None
        else:
            mode, error = extract_mode(text, {"POSITION": ("位置灯",), "DAYTIME_RUNNING_LIGHTS": ("日间行车灯",)})
        if error or not mode:
            failures.append(error or "CONTRACT_CHECK_FAILED_HEADLIGHT_MODE_MISSING")
        else:
            slots["MODE"] = mode
    elif special == "CRUISE_GAP":
        mode, mode_error = extract_mode(text, {"LEVEL_1": ("一档", "一挡"), "LEVEL_2": ("二档", "二挡"), "LEVEL_3": ("三档", "三挡"), "LEVEL_4": ("四档", "四挡")})
        relative, relative_error = extract_mode(text, {"RELATIVE_FARTHER": ("远一点", "增大", "拉远"), "RELATIVE_CLOSER": ("近一点", "减小", "拉近")})
        distance, _ = generic_numeric_value(text, "DISTANCE")
        present = sum(item is not None for item in (mode, relative, distance))
        if mode_error or relative_error or present != 1:
            failures.append("CONTRACT_CHECK_FAILED_CRUISE_GAP_VALUE_XOR_MODE")
        elif mode:
            slots["MODE"] = mode
        elif relative:
            relative["单位"] = "RELATIVE"
            slots["VALUE"] = relative
        elif distance:
            slots["VALUE"] = distance
    elif special == "WIPER_MODE":
        mode, error = extract_mode(text, {
            "OFF": ("关闭雨刮", "关闭雨刷", "雨刮关闭"), "SLOW": ("慢刮", "低速雨刮"),
            "MEDIUM": ("中速雨刮",), "FAST": ("快刮", "高速雨刮"), "INTERVAL": ("间歇",), "RAIN_SENSOR": ("自动雨刮", "雨量感应"),
        })
        if error or not mode:
            failures.append(error or "CONTRACT_CHECK_FAILED_WIPER_MODE_MISSING")
        else:
            slots["MODE"] = mode
    elif special == "WIPER_SENSITIVITY":
        mode, _ = extract_mode(text, {"LOW": ("低", "调低"), "MEDIUM": ("中", "适中"), "HIGH": ("高", "调高")})
        if mode:
            mode["单位"] = "policy_defined"
            slots["VALUE"] = mode
        else:
            candidates = numeric_candidates(text)
            if len(candidates) == 1:
                item = candidates[0]
                slots["VALUE"] = {"原始值": item["raw"], "规范值": item["value"], "单位": "policy_defined", "span": item["span"]}
            else:
                failures.append("CONTRACT_CHECK_FAILED_WIPER_SENSITIVITY_MISSING")
    elif special == "BRAKE":
        value, error = percent_value(text)
        if value:
            slots["VALUE"] = value
        elif error and "PROHIBITED" in error:
            failures.append(error)
    return slots, failures


def validate_contract(intent: dict[str, Any], slots: dict[str, Any]) -> tuple[str, list[str]]:
    failures: list[str] = []
    for required in intent.get("required_slots", []):
        if required not in slots:
            failures.append(f"CONTRACT_CHECK_FAILED_MISSING_{required}")
    conditional = intent.get("conditional_slot_contract")
    if conditional == "VALUE_OR_DIRECTION" and not ({"VALUE", "DIRECTION"} & slots.keys()):
        failures.append("CONTRACT_CHECK_FAILED_VALUE_OR_DIRECTION")
    if conditional == "VALUE_XOR_MODE" and (("VALUE" in slots) == ("MODE" in slots)):
        failures.append("CONTRACT_CHECK_FAILED_VALUE_XOR_MODE")
    return ("COMPLETE" if not failures else "INCOMPLETE"), failures


def match_rule(
    rule: RuleDefinition,
    intent: dict[str, Any],
    text: str,
    area_aliases: dict[str, str],
) -> dict[str, Any] | None:
    if any(term in text for term in rule.excludes):
        return None
    object_ev = first_evidence(text, rule.object_terms, "object")
    action_ev = first_evidence(text, rule.action_terms, "action") if rule.action_terms else object_ev
    if object_ev is None or action_ev is None:
        return None
    if rule.special == "HORN_COMMAND" and re.fullmatch(
        r"(?:请|帮我|给我|麻烦)?(?:按(?:一下)?(?:汽车|车)?喇叭|鸣笛(?:一次|一下)?(?:提醒一下前车)?)(?:吧|好吗|可以吗)?", text
    ) is None:
        return None
    if rule.special == "BRAKE" and re.fullmatch(
        r"(?:请|帮我|给我|立即|立刻|马上|赶紧)?(?:轻点|踩一下|踩|普通|进行|执行|车辆)?(?:刹车|制动|制动踏板)(?:一下|吧|好吗|可以吗)?", text
    ) is None:
        return None
    if rule.special == "EMERGENCY_BRAKE" and re.fullmatch(
        r"(?:请|帮我|给我|立即|立刻|马上|赶紧|执行)?(?:紧急刹车|紧急制动|急刹车)(?:一下|吧|好吗|可以吗)?", text
    ) is None:
        return None
    if rule.intent_id in ("ACCELERATE", "DECELERATE"):
        disallowed_context = ("雨刮", "雨刷", "播放", "进度", "踏板", "能力", "模式", "设置", "分钟", "秒")
        if any(token in text for token in disallowed_context):
            return None
        command_pattern = (
            r"(?:请|帮我|给我|马上|立即|再)?(?:车辆|汽车)?(?:加速|提速|增加速度|加快一点|快一点)"
            if rule.intent_id == "ACCELERATE"
            else r"(?:请|帮我|给我|马上|立即|再)?(?:车辆|汽车)?(?:减速|降速|降低速度|慢一点)"
        )
        if re.fullmatch(command_pattern + r"(?:\d+(?:\.\d+)?(?:公里每小时|千米每小时|公里|千米))?(?:吧|好吗|可以吗)?", text) is None:
            return None
    if rule.special == "LANE_KEEP_COMMAND" and re.fullmatch(
        r"(?:请|帮我|给我|继续)?(?:保持当前车道|保持车道)(?:吧|好吗|可以吗)?", text
    ) is None:
        return None
    if rule.intent_id in ("SUNROOF_OPEN", "SUNROOF_CLOSE"):
        if (numeric_candidates(text) or first_evidence(text, ("一点", "稍微", "一点点", "一部分"), "partial")
                or text.endswith("不") or text.count("天窗") > 1):
            return None
    if rule.intent_id in ("WINDOW_OPEN", "WINDOW_CLOSE"):
        action_repeat = text.count("打开") + text.count("关闭") + text.count("关上") + text.count("关掉")
        object_repeat = text.count("车窗") + text.count("窗户")
        malformed_area = any(token in text for token in ("主副主驾", "前排前排", "所有所有", "全全车", "二排中"))
        if (action_repeat > 1 or object_repeat > 1 or re.match(r"^能(?:不能|否)?", text)
                or "更多" in text or "关打开" in text or malformed_area):
            return None
    if rule.special == "WINDOW_OPEN":
        partial, partial_error = percent_value(text)
        if (partial_error == "CONTRACT_CHECK_FAILED_PROHIBITED_PERCENT_INFERENCE"
                or re.search(r"[一二三四五六七八九十]+分之[一二三四五六七八九十]+", text)
                or re.search(r"\d", text)
                or re.search(r"(?:打开|开启|开到|降到)[零一二两三四五六七八九十百](?:$|[^\u4e00-\u9fff])", text)):
            return None
        if partial and 1 <= partial["规范值"] <= 99:
            return None
        if first_evidence(text, ("全开", "完全打开", "全部打开", "降到底", "降到最低", "一键降窗"), "endpoint") is None and action_ev["text"] not in OPEN_ACTIONS:
            return None
    elif rule.special == "WINDOW_CLOSE":
        partial, partial_error = percent_value(text)
        if (partial_error == "CONTRACT_CHECK_FAILED_PROHIBITED_PERCENT_INFERENCE"
                or re.search(r"[一二三四五六七八九十]+分之[一二三四五六七八九十]+", text)
                or re.search(r"\d", text)
                or re.search(r"(?:关闭|关上|关到|升到)[零一二两三四五六七八九十百](?:$|[^\u4e00-\u9fff])", text)):
            return None
        if partial and 1 <= partial["规范值"] <= 99:
            return None
        if first_evidence(text, ("全关", "完全关闭", "全部关闭", "升到底", "升到顶", "升到最高", "一键升窗"), "endpoint") is None and action_ev["text"] not in CLOSE_ACTIONS:
            return None
    elif rule.special == "WINDOW_PERCENT":
        value, _ = percent_value(text)
        if value is None or not (1 <= value["规范值"] <= 99):
            return None
    elif rule.special in ("ENDPOINT_OPEN", "DOOR_OPEN") and action_ev["text"] not in OPEN_ACTIONS:
        return None
    elif rule.special in ("ENDPOINT_CLOSE", "DOOR_CLOSE") and action_ev["text"] not in CLOSE_ACTIONS:
        return None

    if rule.special == "DOOR_OPEN" and percent_value(text)[0] is not None:
        return None

    slots, failures = special_slots(rule, text)
    declared_slots = set(intent.get("required_slots", [])) | set(intent.get("optional_slots", []))
    if "AREA" in declared_slots:
        area, area_error = extract_area(text, intent.get("allowed_areas", []), area_aliases)
        if rule.intent_id.startswith(("WINDOW_", "DOOR_")) and any(token in text for token in ("和", "以及", "、")):
            area_error = "AREA_EVIDENCE_AMBIGUOUS"
            area = None
        if area_error:
            failures.append(area_error)
        elif area:
            slots["AREA"] = area
    if "DIRECTION" in declared_slots:
        direction, direction_error = extract_direction(text, rule.direction_terms)
        if direction_error:
            failures.append(direction_error)
        elif direction:
            slots["DIRECTION"] = direction
    mode, mode_error = extract_mode(text, rule.mode_terms)
    if mode_error:
        failures.append(mode_error)
    elif mode:
        slots["MODE"] = mode

    if rule.intent_id.startswith("DOOR_") and "AREA" not in slots:
        failures.append("SEMANTIC_MAPPING_FAILED_HIGH_RISK_AREA_AMBIGUOUS")
    if rule.intent_id.startswith("FOG_LIGHT_") and "AREA" not in slots:
        failures.append("SEMANTIC_MAPPING_FAILED_HIGH_RISK_AREA_AMBIGUOUS")
    if rule.intent_id.startswith("TURN_INDICATOR_") and "DIRECTION" not in slots:
        failures.append("SEMANTIC_MAPPING_FAILED_HIGH_RISK_DIRECTION_AMBIGUOUS")

    contract_status, contract_failures = validate_contract(intent, slots)
    failures.extend(contract_failures)
    contract_status = "COMPLETE" if not failures else "INCOMPLETE"
    polarity, polarity_ev = polarity_for_action(text, action_ev)
    evidence_items = [action_ev, object_ev]
    if polarity_ev:
        evidence_items.append(polarity_ev)
    for slot_name, slot in slots.items():
        evidence_items.append({"kind": f"slot_{slot_name}", "text": slot["原始值"], "span": slot["span"]})
    return {
        "scope": "FORMAL_EXECUTABLE",
        "intent_id": rule.intent_id,
        "polarity": polarity,
        "slots": slots,
        "contract_status": contract_status,
        "contract_failures": sorted(set(failures)),
        "triggered_evidence": evidence_items,
    }


BYPASS_OBJECTS = (
    "空调", "阅读灯", "车内灯", "氛围灯", "座椅加热", "座椅通风", "座椅按摩", "显示屏", "屏幕",
    "遮阳帘", "香氛", "方向盘加热", "冰箱", "空气净化", "蓝牙", "热点", "驾驶模式", "ADAS设置",
    "前备箱", "前备厢", "手机无线充电", "HUD", "抬头显示",
)
BYPASS_ACTIONS = OPEN_ACTIONS + CLOSE_ACTIONS + ("设置", "调节", "调整", "切换", "进入", "退出", "播放", "停止")

NON_CONTROL_PATTERNS = (
    re.compile(r"(?:播放|我要听|我想听|听一下|听些|来首|来一首|放首|放一首|播首|播一首|推荐).{0,12}(?:音乐|歌曲|歌单|电台|儿歌|电影|视频|综艺)"),
    re.compile(r"(?:天气|气温|下雨|下雪|空气质量|风力|湿度).{0,8}(?:怎么样|多少|吗|不|查询|查|看看)"),
    re.compile(r"(?:查询|查|告诉我|看看).{0,8}(?:天气|路况|温度|日期|时间|距离|位置)"),
    re.compile(r"^(?:你好|您好|谢谢|再见|早上好|晚上好)[！!。.]?$"),
)


def classify_nonformal(text: str) -> dict[str, Any] | None:
    for pattern in NON_CONTROL_PATTERNS:
        match = pattern.search(text)
        if match:
            return {
                "scope": "NON_CONTROL", "polarity": "NOT_APPLICABLE", "slots": {},
                "contract_status": "NOT_APPLICABLE",
                "triggered_evidence": [{"kind": "non_control_pattern", "text": match.group(0), "span": [match.start(), match.end()]}],
            }
    if any(token in text for token in ("客厅", "卧室", "房间", "家里", "家中", "办公室")):
        return None
    object_matches = all_evidence(text, BYPASS_OBJECTS, "bypass_object")
    filtered_objects: list[dict[str, Any]] = []
    for item in object_matches:
        if any(item["span"][0] >= prior["span"][0] and item["span"][1] <= prior["span"][1] for prior in filtered_objects):
            continue
        filtered_objects.append(item)
    if len(filtered_objects) != 1:
        return None
    object_ev = filtered_objects[0]
    action_ev = first_evidence(text, BYPASS_ACTIONS, "bypass_action")
    if object_ev and action_ev:
        return {
            "scope": "KNOWN_CONTROL_BYPASS", "polarity": polarity_for_action(text, action_ev)[0],
            "slots": {}, "contract_status": "NOT_APPLICABLE", "triggered_evidence": [action_ev, object_ev],
        }
    return None


def split_is_reliable(raw_text: str, splits: list[str]) -> bool:
    if not splits:
        return False
    cursor = 0
    for part in splits:
        if not isinstance(part, str) or not part.strip():
            return False
        index = raw_text.find(part, cursor)
        if index < 0:
            return False
        cursor = index + len(part)
    return True


def mac_auxiliary_evidence(raw_row: dict[str, Any] | None, sub_index: int) -> list[dict[str, Any]]:
    if raw_row is None:
        return []
    semantics = raw_row.get("semantics") or {}
    candidate = semantics.get(f"意图{sub_index + 1}")
    if not isinstance(candidate, dict):
        return []
    pairs: list[dict[str, Any]] = []
    for domain, items in candidate.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and "name" in item and "value" in item:
                pairs.append({"domain": domain, "name": item["name"], "value": item["value"], "role": "AUXILIARY_CONFLICT_CHECK_ONLY"})
    return pairs


def candidate_matches(
    text: str,
    rules: dict[str, RuleDefinition],
    intents: dict[str, dict[str, Any]],
    area_aliases: dict[str, str],
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for intent_id, rule in rules.items():
        match = match_rule(rule, intents[intent_id], text, area_aliases)
        if match is not None:
            matches.append(match)
    return matches


def related_rule_ids(text: str, rules: dict[str, RuleDefinition]) -> list[str]:
    return sorted({intent_id for intent_id, rule in rules.items() if any(term in text for term in rule.object_terms)})


def choose_sub_intent(
    text: str,
    sub_index: int,
    rules: dict[str, RuleDefinition],
    intents: dict[str, dict[str, Any]],
    area_aliases: dict[str, str],
    rule_ids: dict[str, str],
    rule_statuses: dict[str, str],
    raw_row: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[str], list[str]]:
    matches = candidate_matches(text, rules, intents, area_aliases)
    usable = [item for item in matches if rule_statuses[item["intent_id"]] == "AUTO_ENABLED"]
    complete = [item for item in usable if item["contract_status"] == "COMPLETE"]
    incomplete = [item for item in usable if item["contract_status"] != "COMPLETE"]
    diagnostic_ids = sorted({item["intent_id"] for item in matches})
    if len(complete) == 1 and len(usable) == 1:
        chosen = complete[0]
        chosen["rule_id"] = rule_ids[chosen["intent_id"]]
        chosen["text"] = text
        chosen["mac_auxiliary_evidence"] = mac_auxiliary_evidence(raw_row, sub_index)
        chosen["acceptance_checks"] = {
            "scope_unique": True, "intent_unique": True, "action_evidence_present": True,
            "object_evidence_present": True, "all_saved_slots_locatable": True,
            "special_boundary_clear": True, "contract_check": "PASS", "source_conflict": False,
        }
        return chosen, [], diagnostic_ids
    if len(incomplete) == 1 and len(usable) == 1:
        reasons = incomplete[0]["contract_failures"] or ["CONTRACT_CHECK_FAILED"]
        return None, sorted(set(reasons)), diagnostic_ids
    if len(usable) > 1:
        return None, ["SEMANTIC_MAPPING_FAILED_MULTIPLE_FORMAL_RULES"], diagnostic_ids
    nonformal = classify_nonformal(text)
    if nonformal is not None:
        nonformal["text"] = text
        nonformal["mac_auxiliary_evidence"] = mac_auxiliary_evidence(raw_row, sub_index)
        return nonformal, [], diagnostic_ids
    if matches:
        reasons: list[str] = []
        for item in matches:
            reasons.extend(item["contract_failures"])
        if reasons:
            return None, sorted(set(reasons)), diagnostic_ids
        return None, ["SEMANTIC_MAPPING_FAILED_RULE_NOT_AUTO_ENABLED"], diagnostic_ids
    if related_rule_ids(text, rules):
        return None, ["SEMANTIC_MAPPING_FAILED_RELATED_EXPRESSION_NOT_UNIQUE"], diagnostic_ids
    return None, ["SEMANTIC_REVIEW_INSUFFICIENT_SCOPE_EVIDENCE"], diagnostic_ids


def compile_rule_catalog(
    screen_rows: list[dict[str, Any]],
    raw_index: dict[tuple[str, str], dict[str, Any]],
    registry: dict[str, Any],
    rules: dict[str, RuleDefinition],
    area_aliases: dict[str, str],
) -> tuple[dict[str, str], dict[str, str], dict[str, Any]]:
    intents = {item["intent_id"]: item for item in registry["intents"]}
    rule_ids = {intent_id: f"R4-FORMAL-{index:03d}" for index, intent_id in enumerate(intents, 1)}
    safe_examples: dict[str, list[str]] = defaultdict(list)
    safe_match_counts: Counter[str] = Counter()
    related_counts: Counter[str] = Counter()
    contract_failure_counts: dict[str, Counter[str]] = defaultdict(Counter)
    observed_object_terms: dict[str, Counter[str]] = defaultdict(Counter)
    observed_action_terms: dict[str, Counter[str]] = defaultdict(Counter)

    for screen in screen_rows:
        text = screen[RAW_TEXT]
        if screen[SCREEN_CATEGORY] in ("SOURCE_CONFLICT_REVIEW", "DROP_MALFORMED", "TRUE_BOUNDARY_CANDIDATE"):
            eligible = False
        else:
            eligible = True
        raw = raw_index.get((screen[SOURCE_FILE], str(screen[SOURCE_ID])))
        parts = raw.get("split_sens") if raw and split_is_reliable(text, raw.get("split_sens") or []) else [text]
        for part in parts:
            for intent_id, rule in rules.items():
                if any(term in part for term in rule.object_terms):
                    related_counts[intent_id] += 1
                match = match_rule(rule, intents[intent_id], part, area_aliases)
                if match is None:
                    continue
                for term in rule.object_terms:
                    if term in part:
                        observed_object_terms[intent_id][term] += 1
                for term in rule.action_terms:
                    if term in part:
                        observed_action_terms[intent_id][term] += 1
                if match["contract_status"] == "COMPLETE" and eligible:
                    safe_match_counts[intent_id] += 1
                    if len(safe_examples[intent_id]) < 25:
                        safe_examples[intent_id].append(part)
                for failure in match["contract_failures"]:
                    contract_failure_counts[intent_id][failure] += 1

    statuses: dict[str, str] = {}
    formal_rules: list[dict[str, Any]] = []
    for intent_id, intent in intents.items():
        definition = rules[intent_id]
        examples = list(dict.fromkeys(safe_examples[intent_id]))
        if definition.force_review:
            status = "REVIEW_ONLY"
            status_reason = "RULE_EXPLICITLY_REQUIRES_REVIEW"
        elif examples:
            status = "AUTO_ENABLED"
            status_reason = "DETERMINISTIC_COMPLETE_MATCHES_OBSERVED_IN_AUTHORIZED_CORPUS"
        elif related_counts[intent_id]:
            status = "REVIEW_ONLY"
            status_reason = "RELATED_SOURCE_EXPRESSIONS_EXIST_BUT_NO_COMPLETE_UNIQUE_RULE_MATCH"
        else:
            status = "NO_RELIABLE_SOURCE_SAMPLE"
            status_reason = "NO_RELIABLE_SOURCE_SAMPLE"
        statuses[intent_id] = status
        formal_rules.append({
            "rule_id": rule_ids[intent_id],
            "intent_id": intent_id,
            "chinese_name": intent["chinese_name"],
            "rule_status": status,
            "rule_status_reason": status_reason,
            "allowed_text_evidence": {
                "object_anchors_observed": list(observed_object_terms[intent_id]),
                "action_anchors_observed": list(observed_action_terms[intent_id]),
                "deterministic_source_examples": examples,
                "evidence_origin": "FROZEN_R4_AND_AUTHORIZED_CORPUS_ONLY",
            },
            "allowed_mac_auxiliary_evidence": {
                "fields": ["split_sens", "semantics"],
                "role": "SEGMENTATION_AND_CONFLICT_CHECK_ONLY",
                "may_override_raw_text": False,
            },
            "explicit_exclusions": list(definition.excludes),
            "slot_extraction_rule": {
                "required_slots": intent.get("required_slots", []),
                "optional_slots": intent.get("optional_slots", []),
                "all_saved_slots_must_have_raw_span": True,
                "implicit_defaults_prohibited": True,
                "special_handler": definition.special,
            },
            "contract_rule": {
                "value_contract": intent.get("value_contract"),
                "direction_contract": intent.get("direction_contract"),
                "mode_contract": intent.get("mode_contract"),
                "conditional_slot_contract": intent.get("conditional_slot_contract"),
            },
            "manual_review_conditions": [
                "MULTIPLE_FORMAL_RULES_MATCH", "REQUIRED_SLOT_MISSING", "SLOT_EVIDENCE_AMBIGUOUS",
                "CONTRACT_CHECK_FAILED", "SOURCE_ANNOTATION_CONFLICT", "SPECIAL_R4_BOUNDARY_CONFLICT",
            ],
            "corpus_evidence": {
                "related_clause_count": related_counts[intent_id],
                "complete_deterministic_match_count": safe_match_counts[intent_id],
                "stored_example_count": len(examples),
                "contract_failure_counts": dict(contract_failure_counts[intent_id]),
            },
        })

    mapping = {
        "mapping_version": "nlu_mapping_r4_scope_v1",
        "purpose": "OFFLINE_GOLD_DRYRUN_ONLY",
        "online_runtime_use_allowed": False,
        "registry_version": registry["registry_version"],
        "registry_sha256": EXPECTED_HASHES["data/nlu/spec/intent_registry_r4_final.yaml"],
        "authorized_input_only": True,
        "evidence_priority": ["RAW_TEXT", "MAC_SPLIT_SENS", "MAC_SEMANTICS", "OLD_BASELINE_AUDIT_ONLY"],
        "fuzzy_matching_prohibited": True,
        "unknown_ood_is_fallback": False,
        "rule_status_enum": ["AUTO_ENABLED", "REVIEW_ONLY", "NO_RELIABLE_SOURCE_SAMPLE"],
        "warnings": [GUIDANCE_WARNING],
        "scope_rules": {
            "KNOWN_CONTROL_BYPASS": registry["known_control_bypass_definition"],
            "NON_CONTROL": registry["user_voice_scope_contract"]["NON_CONTROL"],
            "UNKNOWN_OOD": registry["user_voice_scope_contract"]["UNKNOWN_OOD"],
        },
        "special_r4_boundaries": registry["annotation_guidance"],
        "formal_rules": formal_rules,
    }
    return rule_ids, statuses, mapping


def build_record(
    screen: dict[str, Any],
    raw_row: dict[str, Any] | None,
    rules: dict[str, RuleDefinition],
    intents: dict[str, dict[str, Any]],
    area_aliases: dict[str, str],
    rule_ids: dict[str, str],
    rule_statuses: dict[str, str],
) -> dict[str, Any]:
    text = screen[RAW_TEXT]
    category = screen[SCREEN_CATEGORY]
    record: dict[str, Any] = {
        "sample_id": screen[SAMPLE_ID], "screen_index": screen.get("screen_index"), "raw_text": text,
        "provenance": {
            "source": screen.get("来源"), "source_file": screen[SOURCE_FILE], "source_id": str(screen[SOURCE_ID]),
            "source_annotation_status": screen.get(SOURCE_ANNOTATION), "screen_category": category,
            "screen_confidence": screen.get("初筛置信度"), "old_baseline_audit_status": screen.get("旧baseline映射状态"),
        },
        "excluded_from_mapping_stats": False,
        "sentence_structure": "MULTI" if screen.get(TEXT_STRUCTURE) == "CLEAR_MULTI" else "SINGLE",
        "sub_intents": [], "failure_reasons": [], "diagnostic_formal_rule_ids": [],
    }
    if category == "SOURCE_CONFLICT_REVIEW":
        record["build_status"] = "SOURCE_QUARANTINE"
        record["failure_reasons"] = ["SOURCE_CONFLICT"]
        record["diagnostic_formal_rule_ids"] = related_rule_ids(text, rules)
        return record
    if category == "DROP_MALFORMED":
        record["build_status"] = "MALFORMED_EXCLUDED"
        record["failure_reasons"] = ["DROP_MALFORMED"]
        return record

    reliable_split = raw_row is not None and split_is_reliable(text, raw_row.get("split_sens") or [])
    raw_splits = raw_row.get("split_sens") if raw_row is not None else []
    parts = raw_splits if reliable_split else [text]
    record["sentence_structure"] = "MULTI" if len(raw_splits) > 1 or screen.get(TEXT_STRUCTURE) == "CLEAR_MULTI" else "SINGLE"
    record["split_evidence_status"] = "RELIABLE_EXACT_ORDERED" if reliable_split else ("NOT_AVAILABLE" if raw_row is None else "UNRELIABLE_OR_UNALIGNED")
    if raw_row is None and screen.get(TEXT_STRUCTURE) == "CLEAR_MULTI":
        record["build_status"] = "BOUNDARY_REVIEW" if category == "TRUE_BOUNDARY_CANDIDATE" else "SEMANTIC_REVIEW"
        record["failure_reasons"] = ["MULTI_INTENT_BOUNDARY_UNAVAILABLE"]
        record["diagnostic_formal_rule_ids"] = related_rule_ids(text, rules)
        return record
    if raw_row is not None and len(raw_row.get("split_sens") or []) > 1 and not reliable_split:
        record["build_status"] = "BOUNDARY_REVIEW" if category == "TRUE_BOUNDARY_CANDIDATE" else "SEMANTIC_REVIEW"
        record["failure_reasons"] = ["MULTI_INTENT_SPLIT_ALIGNMENT_FAILED"]
        record["diagnostic_formal_rule_ids"] = related_rule_ids(text, rules)
        return record

    all_reasons: list[str] = []
    diagnostics: set[str] = set()
    for index, part in enumerate(parts):
        chosen, reasons, diagnostic_ids = choose_sub_intent(
            part, index, rules, intents, area_aliases, rule_ids, rule_statuses, raw_row,
        )
        diagnostics.update(diagnostic_ids)
        all_reasons.extend(reasons)
        if chosen is not None:
            chosen["order"] = index + 1
            record["sub_intents"].append(chosen)
    record["diagnostic_formal_rule_ids"] = sorted(diagnostics)
    if category == "TRUE_BOUNDARY_CANDIDATE":
        record["build_status"] = "BOUNDARY_REVIEW"
        all_reasons.append("TRUE_BOUNDARY_CANDIDATE_REQUIRES_REVIEW")
    elif len(record["sub_intents"]) != len(parts) or all_reasons:
        record["build_status"] = "SEMANTIC_REVIEW"
    else:
        record["build_status"] = "AUTO_CORE_CANDIDATE"
    record["failure_reasons"] = sorted(set(all_reasons))
    return record


def unscreened_records(raw_index: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source_id in ("226", "251"):
        raw = raw_index[("test_set.jsonl", source_id)]
        records.append({
            "sample_id": f"unscreened-test-{source_id}", "screen_index": None, "raw_text": raw["query"],
            "provenance": {"source": "MAC-SLU", "source_file": "test_set.jsonl", "source_id": source_id,
                           "source_annotation_status": "UNSCREENED", "screen_category": "UNSCREENED_SOURCE_ROW"},
            "excluded_from_mapping_stats": True, "build_status": "SOURCE_QUARANTINE", "sub_intents": [],
            "failure_reasons": ["UNSCREENED_SOURCE_ROW"], "diagnostic_formal_rule_ids": [],
        })
    return records


def accumulate_stats(records: list[dict[str, Any]], registry: dict[str, Any], rule_ids: dict[str, str], rule_statuses: dict[str, str]) -> dict[str, Any]:
    intents = {item["intent_id"]: item for item in registry["intents"]}
    status_counts: Counter[str] = Counter()
    scope_counts: Counter[str] = Counter()
    formal_outcomes: Counter[str] = Counter()
    structure_counts: Counter[str] = Counter()
    polarity_counts: Counter[str] = Counter()
    slot_counts: Counter[str] = Counter()
    failure_counts: Counter[str] = Counter()
    rule_hits: Counter[str] = Counter()
    mixed_scope_multi = 0
    scope_record_counts: Counter[str] = Counter()
    formal_routing_records: Counter[str] = Counter()
    per_intent: dict[str, dict[str, Any]] = {
        intent_id: {
            "rule_id": rule_ids[intent_id], "rule_status": rule_statuses[intent_id],
            "auto_candidate_count": 0, "review_count": 0, "quarantine_count": 0,
            "complete_contract_count": 0, "incomplete_contract_count": 0,
            "coverage_category": (
                "NO_RELIABLE_SOURCE_SAMPLE" if rule_statuses[intent_id] == "NO_RELIABLE_SOURCE_SAMPLE"
                else "SEMANTIC_MAPPING_FAILED" if rule_statuses[intent_id] == "REVIEW_ONLY"
                else "SOURCE_EVIDENCE_AVAILABLE"
            ),
        }
        for intent_id in intents
    }
    for record in records:
        if record.get("excluded_from_mapping_stats"):
            continue
        status = record["build_status"]
        status_counts[status] += 1
        structure_counts[record.get("sentence_structure", "SINGLE")] += 1
        failure_counts.update(record.get("failure_reasons", []))
        scopes_in_record: set[str] = set()
        reviewed_formal_ids: set[str] = set()
        for sub in record.get("sub_intents", []):
            scope = sub["scope"]
            scope_counts[scope] += 1
            scopes_in_record.add(scope)
            polarity_counts[sub["polarity"]] += 1
            slot_counts.update(sub.get("slots", {}).keys())
            if scope == "FORMAL_EXECUTABLE":
                intent_id = sub["intent_id"]
                if status == "AUTO_CORE_CANDIDATE":
                    per_intent[intent_id]["auto_candidate_count"] += 1
                    formal_outcomes["AUTO_CANDIDATE"] += 1
                    rule_hits[sub["rule_id"]] += 1
                else:
                    reviewed_formal_ids.add(intent_id)
                    formal_outcomes["REVIEW"] += 1
                key = "complete_contract_count" if sub["contract_status"] == "COMPLETE" else "incomplete_contract_count"
                per_intent[intent_id][key] += 1
        if len(scopes_in_record) > 1:
            mixed_scope_multi += 1
        scope_record_counts.update(scopes_in_record)
        if status == "AUTO_CORE_CANDIDATE" and "FORMAL_EXECUTABLE" in scopes_in_record:
            formal_routing_records["AUTO_RECORDS_WITH_FORMAL"] += 1
        if status in ("SEMANTIC_REVIEW", "BOUNDARY_REVIEW"):
            formal_outcomes["REVIEW_POSSIBLE_FORMAL"] += int(bool(record.get("diagnostic_formal_rule_ids")))
            formal_routing_records["REVIEW_RECORDS_WITH_FORMAL_OR_CANDIDATE"] += int(bool(record.get("diagnostic_formal_rule_ids")))
            reviewed_formal_ids.update(record.get("diagnostic_formal_rule_ids", []))
            for intent_id in reviewed_formal_ids:
                per_intent[intent_id]["review_count"] += 1
            if any(reason.startswith("CONTRACT_CHECK_FAILED") for reason in record.get("failure_reasons", [])):
                for intent_id in record.get("diagnostic_formal_rule_ids", []):
                    per_intent[intent_id]["incomplete_contract_count"] += 1
        elif status == "SOURCE_QUARANTINE":
            formal_outcomes["QUARANTINE_POSSIBLE_FORMAL"] += int(bool(record.get("diagnostic_formal_rule_ids")))
            formal_routing_records["QUARANTINE_RECORDS_WITH_POSSIBLE_FORMAL"] += int(bool(record.get("diagnostic_formal_rule_ids")))
            for intent_id in record.get("diagnostic_formal_rule_ids", []):
                per_intent[intent_id]["quarantine_count"] += 1

    coverage = Counter(item["coverage_category"] for item in per_intent.values())
    mapping_failures = sum(count for reason, count in failure_counts.items() if reason.startswith("SEMANTIC_MAPPING_FAILED"))
    contract_failures = sum(count for reason, count in failure_counts.items() if reason.startswith("CONTRACT_CHECK_FAILED"))
    return {
        "denominators": {"screen_pipeline_records": 20899, "unscreened_audit_records": 2, "audited_records": 20901,
                         "mapping_distribution_denominator": 20899},
        "processed_screen_count": len(records),
        "build_status_counts": {status: status_counts[status] for status in BUILD_STATUSES},
        "scope_sub_intent_counts": {scope: scope_counts[scope] for scope in SCOPES},
        "scope_record_counts": {scope: scope_record_counts[scope] for scope in SCOPES},
        "formal_outcome_counts": dict(formal_outcomes),
        "formal_routing_summary": {
            "auto_candidate_records_with_formal": formal_routing_records["AUTO_RECORDS_WITH_FORMAL"],
            "auto_candidate_formal_sub_intents": formal_outcomes["AUTO_CANDIDATE"],
            "review_records_with_formal_or_candidate": formal_routing_records["REVIEW_RECORDS_WITH_FORMAL_OR_CANDIDATE"],
            "review_labeled_formal_sub_intents": formal_outcomes["REVIEW"],
            "quarantine_records_with_possible_formal": formal_routing_records["QUARANTINE_RECORDS_WITH_POSSIBLE_FORMAL"],
        },
        "formal_intents": per_intent,
        "formal_coverage_summary": {
            "intent_count": 71, "auto_enabled_intent_count": sum(s == "AUTO_ENABLED" for s in rule_statuses.values()),
            "review_only_intent_count": sum(s == "REVIEW_ONLY" for s in rule_statuses.values()),
            "no_reliable_source_sample_intent_count": sum(s == "NO_RELIABLE_SOURCE_SAMPLE" for s in rule_statuses.values()),
            "coverage_categories": dict(coverage),
        },
        "sentence_structure_counts": dict(structure_counts),
        "polarity_counts": {polarity: polarity_counts[polarity] for polarity in POLARITIES},
        "slot_counts": dict(slot_counts),
        "mixed_scope_multi_intent_count": mixed_scope_multi,
        "failure_reason_counts": dict(failure_counts.most_common()),
        "failure_category_totals": {
            "NO_RELIABLE_SOURCE_SAMPLE": sum(s == "NO_RELIABLE_SOURCE_SAMPLE" for s in rule_statuses.values()),
            "SEMANTIC_MAPPING_FAILED": mapping_failures,
            "CONTRACT_CHECK_FAILED": contract_failures,
        },
        "source_conflict_counts": {
            "screen_category_SOURCE_CONFLICT_REVIEW": sum(
                record.get("provenance", {}).get("screen_category") == "SOURCE_CONFLICT_REVIEW" for record in records
            ),
            "source_annotation_status_SOURCE_CONFLICT": sum(
                record.get("provenance", {}).get("source_annotation_status") == "SOURCE_CONFLICT" for record in records
            ),
        },
        "unscreened_source_row_count": 2,
        "rule_hit_counts": {rule_id: rule_hits[rule_id] for rule_id in rule_ids.values()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build conservative R4 Full NLU gold dry-run artifacts.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = (args.output_dir or root / "outputs/full_nlu_r4_scope_v1").resolve()

    input_paths = {relative: root / relative for relative in EXPECTED_HASHES}
    actual_hashes: dict[str, str] = {}
    for relative, expected in EXPECTED_HASHES.items():
        path = input_paths[relative]
        if not path.is_file():
            raise SystemExit(f"HASH_GATE_FAILED: missing authorized input: {path}")
        actual = sha256_file(path)
        actual_hashes[relative] = actual
        if actual.lower() != expected:
            raise SystemExit(f"HASH_GATE_FAILED: {relative}: expected {expected}, got {actual}")

    registry = yaml.safe_load(input_paths["data/nlu/spec/intent_registry_r4_final.yaml"].read_text(encoding="utf-8"))
    if registry.get("registry_version") != REGISTRY_VERSION:
        raise SystemExit(f"REGISTRY_VERSION_FAILED: {registry.get('registry_version')}")
    if len(registry.get("intents", [])) != 71:
        raise SystemExit(f"REGISTRY_INTENT_COUNT_FAILED: {len(registry.get('intents', []))}")
    intent_ids = [item["intent_id"] for item in registry["intents"]]
    if len(set(intent_ids)) != 71 or set(intent_ids) != set(registry.get("formal_user_voice_intent_ids", [])):
        raise SystemExit("REGISTRY_FORMAL_INTENT_SET_FAILED")

    screen_rows = read_jsonl(input_paths["初筛/full_nlu_source_screen_v1.jsonl"])
    if len(screen_rows) != 20899:
        raise SystemExit(f"SCREEN_COUNT_FAILED: {len(screen_rows)}")
    raw_index: dict[tuple[str, str], dict[str, Any]] = {}
    for filename in ("train_set.jsonl", "dev_set.jsonl", "test_set.jsonl"):
        for row in read_jsonl(input_paths[filename]):
            key = (filename, str(row["id"]))
            if key in raw_index:
                raise SystemExit(f"DUPLICATE_RAW_LINK_KEY: {key}")
            raw_index[key] = row

    missing_screen_links: list[tuple[str, str]] = []
    for screen in screen_rows:
        if screen.get("来源") != "MAC-SLU":
            continue
        key = (screen[SOURCE_FILE], str(screen[SOURCE_ID]))
        raw = raw_index.get(key)
        if raw is None:
            missing_screen_links.append(key)
        elif screen[RAW_TEXT] != raw.get("query"):
            raise SystemExit(f"RAW_TEXT_LINK_MISMATCH: {key}")
    if missing_screen_links:
        raise SystemExit(f"RAW_LINK_MISSING: {missing_screen_links[:10]}")
    screened_keys = {(screen[SOURCE_FILE], str(screen[SOURCE_ID])) for screen in screen_rows if screen.get("来源") == "MAC-SLU"}
    expected_unscreened = {("test_set.jsonl", "226"), ("test_set.jsonl", "251")}
    actual_unscreened = set(raw_index) - screened_keys
    if actual_unscreened != expected_unscreened:
        raise SystemExit(f"UNSCREENED_SET_FAILED: {sorted(actual_unscreened)}")

    rules = make_rule_definitions()
    if set(rules) != set(intent_ids):
        raise SystemExit(f"RULE_SET_FAILED: missing={sorted(set(intent_ids)-set(rules))}, extra={sorted(set(rules)-set(intent_ids))}")
    intents = {item["intent_id"]: item for item in registry["intents"]}
    area_aliases = build_area_aliases(registry)
    rule_ids, rule_statuses, mapping = compile_rule_catalog(screen_rows, raw_index, registry, rules, area_aliases)

    records = [build_record(screen, raw_index.get((screen[SOURCE_FILE], str(screen[SOURCE_ID]))), rules, intents,
                            area_aliases, rule_ids, rule_statuses) for screen in screen_rows]
    extras = unscreened_records(raw_index)
    stats = accumulate_stats(records, registry, rule_ids, rule_statuses)
    if stats["processed_screen_count"] != 20899:
        raise SystemExit("INTERNAL_COUNT_FAILED")

    auto_rows = [row for row in records if row["build_status"] == "AUTO_CORE_CANDIDATE"]
    review_rows = [row for row in records if row["build_status"] in ("BOUNDARY_REVIEW", "SEMANTIC_REVIEW")]
    quarantine_rows = [row for row in records if row["build_status"] in ("SOURCE_QUARANTINE", "MALFORMED_EXCLUDED")] + extras
    if len(auto_rows) + len(review_rows) + len(quarantine_rows) - len(extras) != 20899:
        raise SystemExit("OUTPUT_PARTITION_COUNT_FAILED")

    temp_dir = Path(tempfile.mkdtemp(prefix="full_nlu_r4_scope_v1-", dir=str(output_dir.parent)))
    try:
        mapping_path = temp_dir / "nlu_mapping_r4_scope_v1.yaml"
        mapping_path.write_text(yaml.safe_dump(mapping, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8", newline="\n")
        write_jsonl(temp_dir / "full_nlu_gold_dryrun_v1.jsonl", auto_rows)
        write_jsonl(temp_dir / "full_nlu_gold_dryrun_review_v1.jsonl", review_rows)
        write_jsonl(temp_dir / "full_nlu_gold_dryrun_quarantine_v1.jsonl", quarantine_rows)
        stats_path = temp_dir / "full_nlu_gold_dryrun_stats_v1.json"
        stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8", newline="\n")
        output_hashes = {path.name: sha256_file(path) for path in sorted(temp_dir.iterdir()) if path.is_file()}
        manifest = {
            "manifest_version": "full_nlu_gold_dryrun_manifest_v1", "build_purpose": "OFFLINE_GOLD_DRYRUN_ONLY",
            "created_date": "2026-08-10", "registry_version": registry["registry_version"],
            "guidance_registry_version": registry["annotation_guidance"]["registry_version"], "warnings": [GUIDANCE_WARNING],
            "input_hashes": actual_hashes,
            "record_accounting": {"screen_pipeline_records": 20899, "unscreened_quarantine_audit_records": 2,
                                  "audited_records": 20901, "distribution_denominator": 20899,
                                  "unscreened_excluded_from_all_mapping_distributions": True},
            "output_counts": {"auto_core_candidate": len(auto_rows), "review": len(review_rows),
                              "quarantine_and_excluded_including_unscreened": len(quarantine_rows)},
            "output_hashes": output_hashes,
            "training_performed": False, "review_auto_repaired": False, "final_gold_declared": False,
            "python_executable_required": r"D:\software\anaconda\envs\yuzheng311\python.exe",
        }
        manifest_path = temp_dir / "full_nlu_gold_dryrun_manifest_v1.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8", newline="\n")
        if output_dir.exists():
            shutil.rmtree(output_dir)
        temp_dir.replace(output_dir)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

    print(json.dumps({"output_dir": str(output_dir), "auto": len(auto_rows), "review": len(review_rows),
                      "quarantine_including_unscreened": len(quarantine_rows),
                      "auto_enabled_intents": stats["formal_coverage_summary"]["auto_enabled_intent_count"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
