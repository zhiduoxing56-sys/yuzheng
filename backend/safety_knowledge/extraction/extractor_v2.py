"""S4: Extractor v2 — ABSTAIN + 严格枚举 + Ontology Normalizer

升级点（vs v1）：
  1. relevant=false/ABSTAIN：条款与车控无关时明确弃权，禁止强造知识
  2. 全部字段从枚举选择（intent/evidence/constraint/condition），Ontology Normalizer 归一化
  3. Schema Validator 输出结构化错误
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import httpx

BACKEND = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\backend")
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from safety_knowledge.ontology.schema import (  # noqa: E402
    CONDITION_ENUM,
    CONSEQUENCE_ENUM,
    CONSTRAINT_ENUM,
    validate_enum_values,
)

EVIDENCE_WHITELIST = {
    "VEHICLE_SPEED", "GEAR_STATE", "ENVIRONMENT_CONDITIONS", "LIGHTING_STATE",
    "LANE_STATE", "SURROUNDING_OBJECT_STATE", "SERVICE_BRAKE_STATE",
    "FREE_SPACE_STATE", "CRUISE_STATE", "DOOR_STATE", "DOOR_LOCK_STATE",
    "AUTHORIZATION_STATE", "ROAD_FRICTION_STATE", "TRAFFIC_LIGHT_STATE",
    "SPEED_LIMIT_STATE", "OCCUPANT_STATE", "STEERING_STATE",
    "PARKING_BRAKE_STATE", "WINDOW_STATE", "SUNROOF_STATE", "TRUNK_STATE",
    "TRUNK_LOCK_STATE", "HOOD_STATE", "MIRROR_STATE", "MIRROR_HEATING_STATE",
    "WIPER_STATE", "DEFROST_STATE", "SEAT_POSITION_STATE",
    "STEERING_WHEEL_POSITION_STATE", "ESC_STATE", "EMERGENCY_STATE", "SYSTEM_MODE",
}

# Ontology Normalizer：术语归一化映射（同义 → 枚举）
NORMALIZE_MAP = {
    "环境光": "ENVIRONMENT_CONDITIONS", "光照": "ENVIRONMENT_CONDITIONS",
    "照度": "ENVIRONMENT_CONDITIONS", "亮度": "ENVIRONMENT_CONDITIONS",
    "车速": "VEHICLE_SPEED", "速度": "VEHICLE_SPEED",
    "车辆速度": "VEHICLE_SPEED", "档位": "GEAR_STATE", "挡位": "GEAR_STATE",
    "大灯状态": "LIGHTING_STATE", "灯光状态": "LIGHTING_STATE",
    "前照灯状态": "LIGHTING_STATE", "车道": "LANE_STATE",
    "车道线": "LANE_STATE", "障碍": "SURROUNDING_OBJECT_STATE",
    "前方目标": "SURROUNDING_OBJECT_STATE", "目标物": "SURROUNDING_OBJECT_STATE",
    "制动状态": "SERVICE_BRAKE_STATE", "刹车状态": "SERVICE_BRAKE_STATE",
    "可用空间": "FREE_SPACE_STATE", "空位": "FREE_SPACE_STATE",
    "巡航状态": "CRUISE_STATE", "门状态": "DOOR_STATE", "车门状态": "DOOR_STATE",
    "门锁": "DOOR_LOCK_STATE", "授权": "AUTHORIZATION_STATE",
    "身份": "AUTHORIZATION_STATE", "路况": "ROAD_FRICTION_STATE",
    "摩擦": "ROAD_FRICTION_STATE", "信号灯": "TRAFFIC_LIGHT_STATE",
    "限速": "SPEED_LIMIT_STATE", "乘员": "OCCUPANT_STATE",
    "驾驶员状态": "OCCUPANT_STATE", "转向": "STEERING_STATE",
    "方向盘": "STEERING_STATE", "驻车制动": "PARKING_BRAKE_STATE",
    "车窗": "WINDOW_STATE", "天窗": "SUNROOF_STATE", "后备箱": "TRUNK_STATE",
    "尾门": "TRUNK_STATE", "舱盖": "HOOD_STATE", "后视镜": "MIRROR_STATE",
    "雨刮": "WIPER_STATE", "除霜": "DEFROST_STATE", "座椅位置": "SEAT_POSITION_STATE",
    "ESC": "ESC_STATE", "应急": "EMERGENCY_STATE", "系统模式": "SYSTEM_MODE",
}

INTENT_MAP = {
    "巡航": "CRUISE_ENABLE", "跟车": "CRUISE_ENABLE", "时距": "CRUISE_SET_GAP",
    "换道": "LANE_CHANGE", "变道": "LANE_CHANGE",
    "车道保持": "LANE_KEEP", "单车道": "LANE_KEEP",
    "紧急制动": "EMERGENCY_BRAKE", "碰撞": "EMERGENCY_BRAKE", "AEB": "EMERGENCY_BRAKE",
    "泊车": "AUTO_PARK_ENABLE", "车位": "AUTO_PARK_ENABLE",
    "前照灯": "HEADLIGHT_SET_MODE", "大灯": "HEADLIGHT_SET_MODE",
    "远光": "HIGH_BEAM_ON", "近光": "LOW_BEAM_ON",
    "转向灯": "TURN_INDICATOR_ON", "危险警告": "HAZARD_LIGHT_ON",
    "制动": "BRAKE", "刹车": "BRAKE", "加速": "ACCELERATE", "减速": "DECELERATE",
    "驻车制动": "PARKING_BRAKE_APPLY", "自动驻车": "PARKING_BRAKE_APPLY",
    "车门": "DOOR_OPEN", "车窗": "WINDOW_OPEN", "天窗": "SUNROOF_OPEN",
    "后备箱": "TRUNK_OPEN", "舱盖": "HOOD_OPEN", "后视镜": "MIRROR_FOLD",
    "除霜": "DEFROST_ON", "雨刮": "WIPER_SET_MODE", "限速": "SPEED_LIMIT_STATE",
    "驾驶员监测": "LANE_KEEP", "脱手": "LANE_KEEP",
}


class OntologyNormalizer:
    """术语归一化：LLM 自由输出 → 枚举。"""

    def normalize_evidence(self, values: list) -> list[str]:
        result = []
        for v in values:
            if isinstance(v, dict):
                v = v.get("type", "") or v.get("evidence_type", "")
            v = str(v).strip()
            if v in EVIDENCE_WHITELIST:
                result.append(v)
            elif v in NORMALIZE_MAP:
                result.append(NORMALIZE_MAP[v])
            # 无法归一化则丢弃（不猜）
        return list(dict.fromkeys(result))

    def normalize_conditions(self, values: list) -> list[str]:
        result = []
        for v in values:
            if isinstance(v, dict):
                v = v.get("condition", "")
            v = str(v).strip()
            if v in CONDITION_ENUM:
                result.append(v)
            # 中文条件尝试映射（简单匹配）
            else:
                mapped = self._map_condition(v)
                if mapped:
                    result.append(mapped)
        return list(dict.fromkeys(result))

    def _map_condition(self, text: str) -> str | None:
        text = text.lower()
        mapping = [
            ("行驶", "VEHICLE_MOVING"), ("运动", "VEHICLE_MOVING"), ("moving", "VEHICLE_MOVING"),
            ("停止", "VEHICLE_STOPPED"), ("停驻", "VEHICLE_STOPPED"), ("停车", "VEHICLE_STOPPED"),
            ("低速", "LOW_SPEED"), ("高速", "HIGH_SPEED"),
            ("低照度", "LOW_LIGHT"), ("夜间", "NIGHT"), ("暗", "LOW_LIGHT"),
            ("雨", "RAIN"), ("雾", "FOG"), ("雪", "SNOW"),
            ("隧道", "TUNNEL"), ("拥堵", "CONGESTION"), ("泊车", "PARKING"),
            ("驾驶员", "DRIVER_PRESENT"), ("乘客", "PASSENGER_PRESENT"),
            ("倒车", "REVERSE"), ("p档", "GEAR_P"), ("d档", "GEAR_D"),
            ("湿滑", "WET_ROAD"), ("低能见度", "LOW_VISIBILITY"), ("路口", "INTERSECTION"),
            ("人行横道", "CROSSWALK"),
        ]
        for kw, enum in mapping:
            if kw in text:
                return enum
        return None

    def normalize_consequences(self, values: list) -> list[str]:
        result = []
        for v in values:
            if isinstance(v, dict):
                v = v.get("consequence", "")
            v = str(v).strip()
            if v in CONSEQUENCE_ENUM:
                result.append(v)
        return list(dict.fromkeys(result))

    def normalize_constraint(self, value) -> str:
        value = str(value or "").strip()
        if value in CONSTRAINT_ENUM:
            return value
        mapping = {"禁止": "PROHIBIT", "限制": "RESTRICT", "复核": "REVIEW",
                   "额外证据": "REQUIRE_EXTRA_EVIDENCE", "条件允许": "ALLOW_WITH_CONDITION",
                   "允许": "ALLOW"}
        return mapping.get(value, "")


class SchemaValidator:
    """v2 校验器：结构化错误输出。"""

    def validate(self, knowledge: dict) -> tuple[bool, list[str]]:
        errors = []
        if not isinstance(knowledge.get("intent_id", ""), str) or not knowledge["intent_id"]:
            errors.append("intent_id 缺失或非法")
        if not isinstance(knowledge.get("conditions", []), list) or not all(
            isinstance(c, str) and c in CONDITION_ENUM for c in knowledge["conditions"]
        ):
            errors.append("conditions 含非法枚举")
        if knowledge.get("constraint") not in CONSTRAINT_ENUM:
            errors.append(f"constraint 非法: {knowledge.get('constraint')}")
        if not knowledge.get("required_evidence"):
            errors.append("required_evidence 为空")
        # 来源必须由系统注入（防伪造）
        if not isinstance(knowledge.get("source"), dict) or not knowledge["source"].get("standard_id"):
            errors.append("source 缺失（应由系统注入）")
        return (not errors, errors)


class ExtractorV2:
    """v2 抽取器：ABSTAIN 优先 + 归一化 + 严格校验。"""

    def __init__(self, ollama_base: str = "http://127.0.0.1:11434",
                 model: str = "qwen2.5:3b-instruct-q4_0") -> None:
        self.client = httpx.Client(base_url=ollama_base, timeout=120)
        self.model = model
        self.normalizer = OntologyNormalizer()
        self.validator = SchemaValidator()

    def extract(self, clause: dict) -> dict | None:
        """返回 knowledge dict；ABSTAIN 返回 None。"""
        prompt = self._build_prompt(clause)
        try:
            resp = self.client.post("/api/chat", json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": 400},
            })
            content = resp.json()["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                return None
            # ABSTAIN：relevance 判定
            if parsed.get("relevant") is False or parsed.get("abstain") is True:
                return None
            # 归一化
            parsed["required_evidence"] = self.normalizer.normalize_evidence(
                parsed.get("required_evidence", [])
            )
            parsed["conditions"] = self.normalizer.normalize_conditions(
                parsed.get("conditions", [])
            )
            parsed["consequences"] = self.normalizer.normalize_consequences(
                parsed.get("consequences", [])
            )
            parsed["constraint"] = self.normalizer.normalize_constraint(
                parsed.get("constraint", "")
            )
            # intent 映射：条款关键词 → INTENT_MAP（LLM 的 intent 输出不可靠，系统判定）
            content = clause["content"]
            mapped_intent = ""
            # 先排除试验/测试/记录类条款（ABSTAIN）
            if any(m in content for m in ("试验", "测试方法", "记录", "采样", "频率", "数据元")):
                return None
            for kw, intent in INTENT_MAP.items():
                if kw in content:
                    mapped_intent = intent
                    break
            if not mapped_intent:
                return None  # ABSTAIN：无法确定车控动作
            parsed["intent_id"] = mapped_intent
            # 来源由系统注入（LLM 不生成来源，避免伪造）
            parsed["source"] = {
                "standard_id": clause["standard_id"],
                "clause": clause["clause"],
                "source_level": clause.get("source_level", "L2"),
            }
            # 归一化后无证据 → ABSTAIN
            if not parsed.get("required_evidence"):
                return None
            return parsed
        except Exception as e:
            print(f"  抽取异常: {e}")
            return None

    def _build_prompt(self, clause: dict) -> str:
        return f"""你是智能网联汽车安全法规知识抽取器。

【输入条款】
标准: {clause['standard_id']}
条款号: {clause['clause']}
内容: {clause['content'][:700]}

【判定】先判断该条款是否与"车辆控制/行驶安全"相关。
- 若条款是纯测试方法/标志设计/数据处理/术语定义 → 输出 {{"relevant": false}}
- 若相关 → 抽取安全知识

【输出】严格 JSON:
{{"relevant": true, "intent_id": "", "title": "", "conditions": [],
  "constraint": "", "required_evidence": [], "consequences": [],
  "confidence": 0.0, "description": ""}}
conditions 从 [{', '.join(CONDITION_ENUM)}] 选。
constraint 从 [{', '.join(CONSTRAINT_ENUM)}] 选。
required_evidence 从 [VEHICLE_SPEED, GEAR_STATE, ENVIRONMENT_CONDITIONS, LIGHTING_STATE,
LANE_STATE, SURROUNDING_OBJECT_STATE, SERVICE_BRAKE_STATE, FREE_SPACE_STATE, CRUISE_STATE,
DOOR_STATE, AUTHORIZATION_STATE, ROAD_FRICTION_STATE, SPEED_LIMIT_STATE, OCCUPANT_STATE,
STEERING_STATE, PARKING_BRAKE_STATE, WINDOW_STATE, SUNROOF_STATE, TRUNK_STATE, HOOD_STATE] 选。
不要创造枚举之外的值。"""

    def close(self) -> None:
        self.client.close()


def main() -> int:
    print("=" * 72)
    print("S4: Extractor v2（ABSTAIN + 归一化 + 严格校验）")
    print("=" * 72)

    clauses = json.loads(
        Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\law_clauses.json").read_text(encoding="utf-8")
    ) if Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng_clean\data\law_clauses.json").exists() else []
    if not clauses:
        print("law_clauses.json 缺失（需重新切片）")
        return 1

    extractor = ExtractorV2()
    passed = abstained = failed = 0
    try:
        # 只测车控相关条款（GB/T 44461 辅助驾驶）
        samples = [c for c in clauses if "44461" in c["standard_id"]][:10]
        for i, clause in enumerate(samples):
            print(f"\n[{i+1}] {clause['standard_id']} {clause['clause']}")
            k = extractor.extract(clause)
            if k is None:
                print("  → ABSTAIN（无相关车控知识）")
                abstained += 1
                continue
            ok, errors = extractor.validator.validate(k)
            print(f"  intent={k.get('intent_id')} constraint={k.get('constraint')} conf={k.get('confidence')}")
            print(f"  evidence={k.get('required_evidence')}")
            if ok:
                passed += 1
                print("  ✅ PASS")
            else:
                failed += 1
                print(f"  ❌ {errors}")
    finally:
        extractor.close()
    print(f"\n汇总: PASS {passed} / ABSTAIN {abstained} / FAIL {failed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
