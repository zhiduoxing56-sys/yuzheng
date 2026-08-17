from __future__ import annotations

from typing import Any


_STATE_FIELDS: tuple[tuple[str, str, str | None], ...] = (
    ("vehicle_speed", "车速", "km/h"),
    ("gear_position", "挡位", None),
    ("weather", "天气", None),
    ("ambient_light", "环境照度", "lux"),
    ("headlight_state", "前照灯", None),
    ("occupant_role", "身份", None),
    ("speaker_zone", "声源位置", None),
    ("vehicle_mode", "车辆模式", None),
    ("authentication_state", "身份认证", None),
    ("reverse_camera_active", "倒车影像", None),
    ("display_state", "中控屏", None),
    ("road_condition", "道路", None),
    ("brake_state", "制动", None),
    ("emergency_flag", "紧急标志", None),
)

_VALUE_LABELS: dict[str, str] = {
    "P": "P（驻车）",
    "D": "D（前进）",
    "R": "R（倒车）",
    "N": "N（空挡）",
    "CLEAR": "晴朗",
    "CLOUDY": "多云",
    "RAIN": "下雨",
    "FOG": "大雾",
    "DAY": "白天",
    "NIGHT": "夜间",
    "SUNSET": "黄昏",
    "ON": "开启",
    "OFF": "关闭",
    "driver": "驾驶员",
    "passenger": "乘客",
    "front_passenger": "前排乘客",
    "rear_left": "左后座",
    "rear_right": "右后座",
    "REAL_DRIVING": "真实驾驶",
    "SIMULATION": "模拟",
    "MAINTENANCE": "维护",
    "AUTHENTICATED": "已认证",
    "UNAUTHENTICATED": "未认证",
    "DRY": "干燥",
    "WET": "湿滑",
    "NONE": "无",
    "RELEASED": "已释放",
    "REQUIRED": "需要制动",
    "ENABLED": "开启",
    "DISABLED": "关闭",
    "BICYCLE": "自行车",
    "PEDESTRIAN": "行人",
    "VEHICLE": "车辆",
    "FRONT": "前方",
    "REAR": "后方",
    "FRONT_LEFT": "左前方",
    "FRONT_RIGHT": "右前方",
    "REAR_LEFT": "左后方",
    "REAR_RIGHT": "右后方",
    "STATIONARY": "静止",
    "APPROACHING": "接近",
    "RECEDING": "远离",
    "LOW": "低风险",
    "MEDIUM": "中风险",
    "HIGH": "高风险",
    "CRITICAL": "严重风险",
}

_FIELD_VALUE_LABELS: dict[str, dict[str, str]] = {
    "speaker_zone": {
        "driver": "驾驶位",
        "front_passenger": "副驾驶位",
        "rear_left": "左后座",
        "rear_right": "右后座",
    },
    "authentication_state": {
        "True": "已认证",
        "False": "未认证",
    },
    "reverse_camera_active": {"True": "开启", "False": "关闭"},
    "emergency_flag": {"True": "是", "False": "否"},
}


def _display_value(value: Any) -> str:
    if value is None:
        return "未提供"
    if isinstance(value, bool):
        return "是" if value else "否"
    return _VALUE_LABELS.get(str(value), str(value))


def _state_conditions(state: dict[str, Any]) -> list[str]:
    conditions: list[str] = []
    for key, label, unit in _STATE_FIELDS:
        if key not in state:
            continue
        rendered = _FIELD_VALUE_LABELS.get(key, {}).get(
            str(state[key]), _display_value(state[key])
        )
        suffix = f" {unit}" if unit and state[key] is not None else ""
        conditions.append(f"{label}：{rendered}{suffix}")
    return conditions


def _environment_condition(value: dict[str, Any]) -> str:
    parts: list[str] = []
    fields = (
        ("time_of_day", "时段", None),
        ("ambient_illumination", "照度", "lux"),
        ("visibility", "能见度", "m"),
        ("weather", "天气", None),
        ("precipitation", "降水", None),
        ("fog", "雾", None),
    )
    for key, label, unit in fields:
        if key not in value:
            continue
        rendered = _display_value(value[key])
        suffix = f" {unit}" if unit and value[key] is not None else ""
        parts.append(f"{label}{rendered}{suffix}")
    return "环境：" + "、".join(parts)


def _road_condition(value: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, label in (
        ("road_condition", "路面"),
        ("wetness", "湿度"),
        ("friction_scale_factor", "摩擦系数"),
        ("most_probable", "最可能摩擦系数"),
    ):
        if key in value:
            parts.append(f"{label}{_display_value(value[key])}")
    return "道路：" + "、".join(parts)


def _surrounding_condition(value: dict[str, Any]) -> str:
    objects = value.get("objects")
    if not isinstance(objects, list) or not objects:
        return "周边目标：无"
    summaries: list[str] = []
    for item in objects:
        if not isinstance(item, dict):
            summaries.append(_display_value(item))
            continue
        parts = [
            _display_value(item[key])
            for key in ("region", "entity_kind")
            if key in item
        ]
        if "distance" in item:
            parts.append(f"距离{_display_value(item['distance'])} m")
        for key in ("motion_state", "risk_level"):
            if key in item:
                parts.append(_display_value(item[key]))
        summaries.append("".join(parts))
    return "周边目标：" + "；".join(summaries)


def _system_condition(value: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, label in (
        ("vehicle_mode", "模式"),
        ("safety_constraint", "安全约束"),
        ("simulation", "仿真标志"),
    ):
        if key in value:
            parts.append(f"{label}{_display_value(value[key])}")
    return "系统：" + "、".join(parts)


def _evidence_condition(observation: dict[str, Any]) -> str:
    evidence_type = str(observation.get("evidence_type", "补充证据"))
    value = observation.get("value")
    source = str(observation.get("source", ""))
    if isinstance(value, dict):
        if evidence_type == "ENVIRONMENT_CONDITIONS":
            return _environment_condition(value)
        if evidence_type == "ROAD_FRICTION_STATE":
            return _road_condition(value)
        if evidence_type == "SURROUNDING_OBJECT_STATE":
            return _surrounding_condition(value)
        if evidence_type == "SYSTEM_MODE":
            return _system_condition(value)
        if evidence_type == "GEAR_STATE" and "current_gear" in value:
            return f"补充挡位（{source}）：{_display_value(value['current_gear'])}"
    evidence_labels = {
        "VEHICLE_SPEED": "补充车速",
        "GEAR_STATE": "补充挡位",
        "AUTHORIZATION_STATE": "补充授权",
    }
    label = evidence_labels.get(evidence_type, evidence_type)
    source_label = f"（{source}）" if source else ""
    return f"{label}{source_label}：{_display_value(value)}"


def scenario_conditions(scenario: dict[str, Any]) -> list[str]:
    """Return stable, presentation-only conditions for a demo scenario."""

    state = scenario.get("state", {})
    observations = scenario.get("evidence_overrides", [])
    conditions = _state_conditions(state if isinstance(state, dict) else {})
    if isinstance(observations, list):
        conditions.extend(
            _evidence_condition(item)
            for item in observations
            if isinstance(item, dict)
        )
    return conditions
