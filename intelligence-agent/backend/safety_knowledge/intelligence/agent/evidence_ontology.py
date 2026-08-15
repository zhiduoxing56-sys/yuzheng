"""情报智能体 v3 —— 证据本体（Evidence Ontology）

Physical Evidence 枚举 → 事故文本关键词（供 Novelty 证据重叠判定）
与 KnowledgeNode Schema 的 required_evidence 枚举空间一致。
"""
from __future__ import annotations

# 证据枚举 → 事故文本匹配关键词
EVIDENCE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "VEHICLE_SPEED": ("speed", "mph", "km/h", "车速", "velocity"),
    "GEAR_STATE": ("gear", "档位", "transmission", "park", "drive"),
    "SERVICE_BRAKE_STATE": ("brake", "制动", "刹车", "stopping"),
    "PARKING_BRAKE_STATE": ("parking brake", "驻车制动", "手刹", "e-brake"),
    "SURROUNDING_OBJECT_STATE": ("collision", "crash", "impact", "障碍", "碰撞", "object", "pedestrian"),
    "LANE_STATE": ("lane", "车道", "steering", "偏离"),
    "STEERING_STATE": ("steering", "转向", "wheel", "方向盘"),
    "LIGHTING_STATE": ("light", "headlight", "taillight", "灯", "照明", "illuminat"),
    "ENVIRONMENT_CONDITIONS": ("night", "dark", "rain", "fog", "夜间", "雨天", "雾"),
    "DOOR_STATE": ("door", "车门", "latch", "锁闩"),
    "WINDOW_STATE": ("window", "车窗"),
    "TRUNK_STATE": ("trunk", "行李箱", "后备箱", "boot"),
    "MIRROR_STATE": ("mirror", "后视镜"),
    "WIPER_STATE": ("wiper", "雨刮", "刮水器"),
    "DEFROST_STATE": ("defrost", "除霜", "除雾"),
    "CRUISE_STATE": ("cruise", "巡航", "adaptive"),
    "FREE_SPACE_STATE": ("park", "泊车", "space", "车位"),
    "AUTHORIZATION_STATE": ("key", "fob", "钥匙", "remote", "access", "授权"),
    "AUTHENTICATION_STATE": ("auth", "认证", "identity", "身份"),
    "SECURITY_STATE": ("security", "secure", "安全", "cyber"),
    "SOFTWARE_VERSION": ("software", "software version", "firmware", "软件", "固件", "update"),
    "SECURITY_LOG_STATE": ("log", "日志", "record", "记录"),
    "DATA_INTEGRITY_STATE": ("data", "corrupt", "数据", "integrity"),
    "BATTERY_STATE": ("battery", "电量", "电池"),
    "COMMUNICATION_STATE": ("communication", "通信", "connect", "连接", "network"),
    "KEY_STATE": ("key", "密钥"),
    "OCCUPANT_STATE": ("occupant", "passenger", "乘员", "乘客", "injury"),
    "ROAD_FRICTION_STATE": ("friction", "湿滑", "slippery", "路面"),
    "SPEED_LIMIT_STATE": ("speed limit", "限速"),
    "TRAFFIC_LIGHT_STATE": ("traffic light", "信号灯"),
    "ADS_STATE": ("autonomous", "self-driving", "自动驾驶", "fsd", "adas", "driverless"),
    "SYSTEM_FAILURE_STATE": ("failure", "fail", "失效", "故障", "malfunction"),
}
