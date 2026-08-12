from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = ROOT / "scripts/full_nlu/validate_full_nlu_schema.py"
SPEC = importlib.util.spec_from_file_location("validate_full_nlu_schema", VALIDATOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def base_sample() -> dict:
    return {
        "样本编号": "TEST-001",
        "原始文本": "向左变道",
        "规范文本": "向左变道",
        "来源": "受控扩写",
        "原始文件": "unit_test",
        "原始编号": "1",
        "控制范围": "正式可执行",
        "结构状态": "单意图",
        "语气状态": "肯定",
        "子意图列表": [{
            "规范动作": "CHANGE",
            "规范对象": "LANE",
            "控制属性": "POSITION",
            "位置": None,
            "数值": None,
            "方向": "LEFT",
            "模式": None,
        }],
        "合同是否完整": True,
        "是否允许进入正式正样本": True,
        "是否需要人工复核": False,
        "映射规则版本": "nlu_mapping_v2",
        "人工覆盖规则版本": None,
    }


def test_schema_smoke_file_passes() -> None:
    path = ROOT / "data/nlu/full/schema/full_nlu_schema_smoke_v1.jsonl"
    result = MODULE.validate_paths([path])
    assert result["status"] == "PASS", result["errors"]
    assert result["sample_count"] == 3


def test_unknown_top_level_field_fails() -> None:
    sample = base_sample()
    sample["intent"] = "LANE_CHANGE"
    errors = MODULE.validate_sample(sample)
    assert any(error.startswith("SCHEMA:") for error in errors)
    assert any(error.startswith("TOP_LEVEL_FIELDS:") for error in errors)


def test_positive_logic_is_equivalence() -> None:
    sample = base_sample()
    sample["语气状态"] = "否定"
    errors = MODULE.validate_sample(sample)
    assert any(error.startswith("FORMAL_POSITIVE_LOGIC:") for error in errors)


def test_multi_requires_two_sub_intents() -> None:
    sample = base_sample()
    sample["结构状态"] = "多意图"
    sample["是否允许进入正式正样本"] = False
    errors = MODULE.validate_sample(sample)
    assert "MULTI:min two sub-intents required" in errors


def test_null_policy_rejects_empty_slot_string() -> None:
    sample = base_sample()
    sample["子意图列表"][0]["位置"] = ""
    errors = MODULE.validate_sample(sample)
    assert any(error.startswith("NULL_POLICY:") for error in errors)


def test_empty_raw_source_text_is_preserved_for_review() -> None:
    sample = base_sample()
    sample["原始文本"] = ""
    sample["规范文本"] = ""
    sample["控制范围"] = "未知"
    sample["结构状态"] = "歧义"
    sample["子意图列表"] = []
    sample["合同是否完整"] = False
    sample["是否允许进入正式正样本"] = False
    sample["是否需要人工复核"] = True
    assert MODULE.validate_sample(sample) == []
