"""Build the bounded R4 final dead-reference patch and its two sidecars."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, sha256_file
from validate_sys014_r4_final_micro_patch import (
    EXECUTION_TODOS_PATH,
    FINAL_PATH,
    FORMAL_MAPPING_PATH,
    MANDATORY_RULES_PATH,
    PRE_PATCH_SHA256,
    _yaml_sha256,
    reconstruct_pre_patch,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "data/nlu/spec/audits"
REPORT_PATH = AUDIT_DIR / "r4_final_dead_reference_patch.md"
VALIDATOR_PATH = AUDIT_DIR / "r4_final_patch_validator_result.json"


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def build_mandatory_rules() -> dict[str, Any]:
    return {
        "version": "r4_gold_mapping_mandatory_rules_v1",
        "document_role": "MANDATORY_INPUT_FOR_FUTURE_R4_SCOPE_MAPPING",
        "required_integration_target": "nlu_mapping_r4_scope_v1",
        "integration_must_not_be_omitted": True,
        "formal_mapping_created_by_this_patch": False,
        "rules": [{
            "rule_id": "NON_CRUISE_ABSOLUTE_SPEED_TARGET",
            "priority": "HIGH",
            "match_semantics": {
                "absolute_target_vehicle_speed_command": True,
                "explicit_cruise_context": False,
                "examples": ["加速到80", "速度提到80", "减速到40", "速度降到40"],
            },
            "result": "QUARANTINE_CONTRACT_GAP",
            "formal_positive_prohibited": True,
            "automatic_cruise_mapping_prohibited": True,
            "known_control_bypass_prohibited": True,
            "accelerate_delta_mapping_prohibited": True,
            "decelerate_delta_mapping_prohibited": True,
            "reason_code": "NON_CRUISE_ABSOLUTE_SPEED_TARGET_UNSUPPORTED",
            "semantic_rationale": [
                "ACCELERATE / DECELERATE currently accept relative speed changes only; an absolute target speed is not a delta.",
                "CRUISE_SET_SPEED is allowed only when raw text explicitly establishes cruise context.",
                "A real vehicle-motion control command must not bypass the Yuzheng safety chain via KNOWN_CONTROL_BYPASS.",
            ],
            "explicit_cruise_positive_examples": ["巡航速度设为80", "把定速巡航调到80"],
            "explicit_cruise_allowed_intent_id": "CRUISE_SET_SPEED",
        }],
    }


def build_execution_todos() -> dict[str, Any]:
    return {
        "version": "r4_execution_layer_todos_v1",
        "registry_semantics_modified": False,
        "todos": [
            {
                "todo_id": "HIGH_RISK_PRECONDITION_GATE",
                "applies_to_intent_ids_at_minimum": ["DOOR_OPEN", "DOOR_CLOSE", "ACCELERATE", "DECELERATE", "BRAKE", "EMERGENCY_BRAKE", "LANE_CHANGE", "LANE_KEEP", "EVASIVE_STEER"],
                "responsibility_boundary": {
                    "nlu": "RECOGNIZE_USER_INTENT",
                    "execution_safety_chain": ["VEHICLE_SPEED", "GEAR", "ROAD_STATE", "OBSTACLE", "PEDESTRIAN", "AUTHORIZATION"],
                    "execution_conditions_as_nlu_required_slots_prohibited": True,
                },
                "status": "DEFERRED_TO_EXECUTION_SAFETY_LAYER",
                "blocks_gold_build": False,
                "blocks_nlu_training": False,
            },
            {
                "todo_id": "COMPOSITE_AREA_FANOUT_GATE",
                "applies_to_families_at_minimum": ["WINDOW", "DOOR"],
                "composite_areas": ["FRONT_ROW", "REAR_ROW", "LEFT_SIDE", "RIGHT_SIDE", "ALL"],
                "nlu_outputs_remain_valid": ["AREA=ALL", "AREA=FRONT_ROW", "AREA=REAR_ROW"],
                "runtime_gate_if_fanout_unavailable": ["REVIEW", "BLOCK", "CAPABILITY_UNAVAILABLE"],
                "incorrect_direct_execution_prohibited": True,
                "removing_valid_composite_area_from_gold_prohibited": True,
                "status": "DEFERRED_TO_EXECUTION_CAPABILITY_LAYER",
                "blocks_gold_build": False,
                "blocks_nlu_training": False,
            },
        ],
    }


def build() -> dict[str, Any]:
    if FORMAL_MAPPING_PATH.exists():
        raise RuntimeError("formal nlu_mapping_r4_scope_v1.yaml appeared; case B builder must stop")
    registry = load_yaml(FINAL_PATH)
    alias = registry["mode_mapping_contracts"]["HEADLIGHT_MAIN_SWITCH"]["restricted_aliases"]["ON"]
    current_sha = sha256_file(FINAL_PATH)
    if current_sha == PRE_PATCH_SHA256:
        if alias.get("prohibited_canonical_mode") != "BEAM":
            raise RuntimeError("approved dead reference is absent or has an unexpected value")
        if list(alias).count("prohibited_canonical_mode") != 1:
            raise RuntimeError("approved dead reference is not unique")
        del alias["prohibited_canonical_mode"]
    elif "prohibited_canonical_mode" not in alias:
        if _yaml_sha256(reconstruct_pre_patch(registry)) != PRE_PATCH_SHA256:
            raise RuntimeError("current registry is not the uniquely patched R4 final parent")
    else:
        raise RuntimeError("R4 final pre-patch SHA256 mismatch")

    write_yaml(FINAL_PATH, registry)
    write_yaml(MANDATORY_RULES_PATH, build_mandatory_rules())
    write_yaml(EXECUTION_TODOS_PATH, build_execution_todos())

    result = validate()
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATOR_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(
        "\n".join([
            "# R4 Final Dead Reference Patch", "",
            f"- 修改前 SHA256: `{PRE_PATCH_SHA256}`",
            f"- 修改后 SHA256: `{result['post_patch_sha256']}`",
            f"- Validator: **{result['status']}**",
            f"- YAML 实际语义修改字段数: **{result['yaml_semantic_changed_field_count']}**", "",
            "## 唯一 YAML 语义修改", "",
            "删除 `mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH.restricted_aliases.ON.prohibited_canonical_mode: BEAM`。", "",
            "`allowed_intent_id: HEADLIGHT_SET_MODE` 与对 `LOW_BEAM_ON`、`HIGH_BEAM_ON` 的禁止映射保持不变。", "",
            "## 冻结确认", "",
            f"- 71 Formal Intent 100% 保持: **{str(result['formal_intents_100_percent_preserved']).lower()}**",
            "- Runtime scope: **4，保持不变**",
            "- KNOWN_CONTROL_BYPASS: **保持不变**",
            "- FOLLOWING_GAP_REQUIRED: **未恢复**",
            "- 旧 7-Intent active dependency: **0**", "",
            "## 边界登记", "",
            f"- Gold absolute-speed mandatory rule 落地: **{str(result['gold_absolute_speed_rule_landed']).lower()}**",
            "- 正式 `nlu_mapping_r4_scope_v1.yaml`: **未创建**",
            f"- 两个 execution todo 已登记: **{str(result['execution_todos_registered']).lower()}**", "",
            "未运行 Gold mapping dry-run，未生成 Gold 数据，未训练。", "",
        ]),
        encoding="utf-8",
    )
    if result["status"] != "PASS":
        raise RuntimeError(f"validator failed: {result['errors']}")
    return result


def main() -> int:
    try:
        result = build()
    except (OSError, ValueError, KeyError, RuntimeError, yaml.YAMLError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
