"""阶段1.4: 安全知识抽取器

架构（用户方案）：
  MinerU条款 → 本地Qwen（枚举槽填充）→ Schema Validator
      ├─ 正常 → 审核池
      └─ 低置信/冲突 → DeepSeek复核（接口预留）

严格约束：只从枚举选值，禁止生成新 intent_id/evidence_type/condition。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

BACKEND = Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng\backend")
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from safety_knowledge.ontology.schema import (  # noqa: E402
    CONDITION_ENUM,
    CONSEQUENCE_ENUM,
    CONSTRAINT_ENUM,
    SOURCE_LEVEL_ENUM,
    validate_enum_values,
)


class SafetyRuleExtractor:
    """LLM 知识抽取器：条款 → 结构化安全知识。"""

    def __init__(self, ollama_base: str = "http://127.0.0.1:11434", model: str = "qwen2.5:3b-instruct-q4_0") -> None:
        self.client = httpx.Client(base_url=ollama_base, timeout=120)
        self.model = model

    def _build_prompt(self, clause: dict) -> str:
        return f"""你是智能网联汽车安全法规知识抽取器。从法规条款中抽取结构化安全知识。

【输入条款】
标准: {clause['standard_id']}
条款号: {clause['clause']}
条款内容:
{clause['content'][:800]}

【任务】从以下枚举中选择值填充 JSON（禁止创造新值）：

可选条件(condition，可多个): {CONDITION_ENUM}
可选约束(constraint，选1个): {CONSTRAINT_ENUM}
可选后果(consequence，可多个): {CONSEQUENCE_ENUM}
intent_id: 若条款明确涉及某车控动作则填写（如 HEADLIGHT_SET_MODE/CRUISE_ENABLE/DOOR_OPEN），否则填空字符串
required_evidence: 从证据类型枚举中选，如 VEHICLE_SPEED/ENVIRONMENT_CONDITIONS/LIGHTING_STATE/LANE_STATE/SURROUNDING_OBJECT_STATE/GEAR_STATE/SERVICE_BRAKE_STATE/FREE_SPACE_STATE/CRUISE_STATE/DOOR_STATE/AUTHORIZATION_STATE

【输出格式】严格输出 JSON（不要任何额外文字）:
{{
  "intent_id": "",
  "title": "简短标题",
  "conditions": [],
  "constraint": "",
  "required_evidence": [],
  "consequences": [],
  "confidence": 0.0,
  "description": "安全规则描述（30-100字）"
}}"""

    def extract(self, clause: dict) -> dict | None:
        """抽取单条款。返回结构化知识；解析失败返回 None。"""
        prompt = self._build_prompt(clause)
        try:
            resp = self.client.post(
                "/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {"temperature": 0.0, "num_predict": 400},
                },
            )
            resp.raise_for_status()
            content = resp.json()["message"]["content"]
            # 提取 JSON（处理可能的 ```json 包裹）
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                return None
            # 过滤空知识（没有 intent 且没有证据，说明条款与车控无关）
            if not parsed.get("intent_id") and not parsed.get("required_evidence"):
                return None
            return parsed
        except Exception as e:
            print(f"  抽取失败 {clause['standard_id']} {clause['clause']}: {e}")
            return None

    def validate(self, knowledge: dict) -> tuple[bool, list[str]]:
        """Schema + 枚举校验。"""
        errors = validate_enum_values(knowledge)
        if not knowledge.get("intent_id"):
            errors.append("缺少 intent_id（条款与车控无关或抽取失败）")
        if not knowledge.get("required_evidence"):
            errors.append("缺少 required_evidence")
        return (not errors, errors)

    def close(self) -> None:
        self.client.close()


def main() -> int:
    print("=" * 72)
    print("阶段1.4: 安全知识抽取器（Qwen 本地抽取 + Schema 校验）")
    print("=" * 72)

    clauses = json.loads(
        Path(r"C:\Users\Leo\AppData\Local\Temp\opencode\yuzheng\data\law_clauses.json").read_text(encoding="utf-8")
    )
    print(f"条款数: {len(clauses)}")

    extractor = SafetyRuleExtractor()
    try:
        # 先抽 10 条代表性条款（覆盖各标准）
        samples = clauses[:12]
        for i, clause in enumerate(samples):
            print(f"\n[{i+1}/{len(samples)}] {clause['standard_id']} {clause['clause']}")
            knowledge = extractor.extract(clause)
            if knowledge is None:
                print("  → 无相关车控知识（跳过）")
                continue
            ok, errors = extractor.validate(knowledge)
            print(f"  intent={knowledge.get('intent_id')} constraint={knowledge.get('constraint')} conf={knowledge.get('confidence')}")
            print(f"  conditions={knowledge.get('conditions')}")
            print(f"  evidence={knowledge.get('required_evidence')}")
            print(f"  校验: {'✅ PASS' if ok else '❌ ' + str(errors)}")
    finally:
        extractor.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
