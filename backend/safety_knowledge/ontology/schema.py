"""阶段1.1: 安全知识 Schema 定义

安全知识 = 约束对象 + 适用条件 + 危险行为 + 必要证据 + 风险后果 + 权威来源

核心原则（防 Ontology 膨胀）：
  - intent_id / evidence_type / condition / constraint 全部枚举约束
  - LLM 只做"选值 + 填槽"，禁止自由生成新枚举
"""
from __future__ import annotations

from typing import Any, Literal

# ---------- 枚举约束（对齐 yuzheng 现有语义） ----------

CONDITION_ENUM = [
    "VEHICLE_MOVING",      # 车辆行驶中
    "VEHICLE_STOPPED",     # 车辆停止
    "LOW_SPEED",           # 低速 (<30km/h)
    "HIGH_SPEED",          # 高速 (>=90km/h)
    "LOW_LIGHT",           # 低照度
    "BRIGHT_LIGHT",        # 高照度
    "RAIN",                # 雨天
    "FOG",                 # 雾天
    "SNOW",                # 雪天
    "NIGHT",               # 夜间
    "TUNNEL",              # 隧道
    "CONGESTION",          # 拥堵
    "PARKING",             # 泊车
    "DRIVER_PRESENT",      # 驾驶员在位
    "PASSENGER_PRESENT",   # 乘客在位
    "REVERSE",             # 倒车
    "GEAR_P",              # P 档
    "GEAR_D",              # D 档
    "WET_ROAD",            # 湿滑路面
    "LOW_VISIBILITY",      # 低能见度
    "INTERSECTION",        # 路口
    "CROSSWALK",           # 人行横道
]

CONSTRAINT_ENUM = [
    "PROHIBIT",            # 禁止执行
    "RESTRICT",            # 限制执行（需满足条件）
    "REVIEW",              # 需人工复核
    "REQUIRE_EXTRA_EVIDENCE",  # 需额外证据
    "ALLOW_WITH_CONDITION",    # 条件允许
    "ALLOW",               # 允许
]

CONSEQUENCE_ENUM = [
    "LIGHTING_LOSS",       # 照明能力下降
    "COLLISION_RISK",      # 碰撞风险
    "BLIND_SPOT",          # 视野盲区
    "OCCUPANT_FALL_RISK",  # 乘员跌落风险
    "VEHICLE_DRIFT",       # 车辆偏移/失稳
    "UNINTENDED_ACCEL",    # 非预期加速
    "UNINTENDED_BRAKE",    # 非预期制动
    "DOOR_CONTACT",        # 车门碰撞风险
    "PINCH_RISK",          # 夹伤风险
    "LOSS_OF_CONTROL",     # 失控
    "BATTERY_DRAIN",       # 电池耗尽
    "DATA_LEAK",           # 数据泄露
    "UNAUTHORIZED_ACCESS", # 未授权访问
]

SOURCE_LEVEL_ENUM = [
    "L1",  # 法律法规 / 强制国标 / 政府文件
    "L2",  # 推荐性标准 / 行业标准 / 政府技术指南
    "L3",  # OEM 技术文档 / 权威工程资料
    "L4",  # 学术论文 / 专业数据库
    "L5",  # 媒体报道 / 事故新闻
]

REVIEW_STATUS_ENUM = [
    "DRAFT",           # 抽取完成待审核
    "PENDING_REVIEW",  # 待人工审核
    "APPROVED",        # 已审核通过
    "REJECTED",        # 已拒绝
    "SUPERSEDED",      # 已被新版本替代
]


# ---------- Schema ----------

SAFETY_KNOWLEDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": [
        "knowledge_id",
        "intent_id",
        "title",
        "conditions",
        "constraint",
        "required_evidence",
        "consequences",
        "source",
    ],
    "properties": {
        "knowledge_id": {
            "type": "string",
            "pattern": r"^SAFETY-[A-Z0-9_]+-\d{5}$",
        },
        "intent_id": {
            "type": "string",
            "description": "必须来自 unified registry 的 intent_id 枚举",
        },
        "title": {"type": "string", "maxLength": 120},
        "conditions": {
            "type": "array",
            "items": {"enum": CONDITION_ENUM},
            "minItems": 1,
        },
        "constraint": {"enum": CONSTRAINT_ENUM},
        "required_evidence": {
            "type": "array",
            "items": {"type": "string"},  # 必须来自 evidence_type 枚举
            "minItems": 1,
        },
        "optional_evidence": {
            "type": "array",
            "items": {"type": "string"},
        },
        "consequences": {
            "type": "array",
            "items": {"enum": CONSEQUENCE_ENUM},
            "minItems": 1,
        },
        "description": {"type": "string", "maxLength": 500},
        "source": {
            "type": "object",
            "required": ["standard_id", "clause", "source_level"],
            "properties": {
                "standard_id": {"type": "string"},
                "clause": {"type": "string"},
                "source_level": {"enum": SOURCE_LEVEL_ENUM},
                "url": {"type": "string"},
            },
        },
        "review_status": {"enum": REVIEW_STATUS_ENUM},
        "version": {"type": "string"},
        "created_at": {"type": "string"},
        "reviewed_at": {"type": "string"},
    },
}


def validate_enum_values(payload: dict[str, Any]) -> list[str]:
    """校验抽取结果是否违反枚举约束（Ontology 防膨胀）。"""
    errors: list[str] = []
    for cond in payload.get("conditions", []):
        if cond not in CONDITION_ENUM:
            errors.append(f"未知条件枚举: {cond}")
    if payload.get("constraint") not in CONSTRAINT_ENUM:
        errors.append(f"未知约束枚举: {payload.get('constraint')}")
    for cons in payload.get("consequences", []):
        if cons not in CONSEQUENCE_ENUM:
            errors.append(f"未知后果枚举: {cons}")
    level = payload.get("source", {}).get("source_level")
    if level not in SOURCE_LEVEL_ENUM:
        errors.append(f"未知来源等级: {level}")
    return errors


if __name__ == "__main__":
    import json
    print("Schema 定义:")
    print(json.dumps(SAFETY_KNOWLEDGE_SCHEMA, ensure_ascii=False, indent=2)[:2000])
    print(f"\n条件枚举: {len(CONDITION_ENUM)} 个")
    print(f"约束枚举: {len(CONSTRAINT_ENUM)} 个")
    print(f"后果枚举: {len(CONSEQUENCE_ENUM)} 个")
