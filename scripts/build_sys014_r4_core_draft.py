"""Deterministically derive the approved SYS-014 Full NLU R4 core draft from R3."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import (
    R3_PATH,
    R3_SHA256,
    R3_VERSION,
    R4_PATH,
    R4_STATUS,
    R4_VERSION,
    StrictSafeLoader,
    sha256_file,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "data/nlu/spec/audits"
DIFF_MD_PATH = AUDIT_DIR / "r3_to_r4_core_diff.md"
DIFF_JSON_PATH = AUDIT_DIR / "r3_to_r4_core_diff.json"
VALIDATOR_RESULT_PATH = AUDIT_DIR / "r4_core_validator_result.json"
BUILD_VERSION = "sys014_r4_core_builder_v1"


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def _insert_after(mapping: dict[str, Any], after_key: str, key: str, value: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    inserted = False
    for current_key, current_value in mapping.items():
        result[current_key] = current_value
        if current_key == after_key:
            result[key] = value
            inserted = True
    if not inserted:
        raise KeyError(f"cannot insert {key}: anchor {after_key} does not exist")
    return result


def _insert_list_after(values: list[str], after_value: str, value: str) -> list[str]:
    if value in values:
        raise ValueError(f"{value} already exists")
    index = values.index(after_value)
    return values[: index + 1] + [value] + values[index + 1 :]


def _by_intent(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["intent_id"]: item for item in registry["intents"]}


def _audit_by_intent(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["intent_id"]: item
        for item in registry["over_atomization_audit"]["parameterized_instead_of_split"]
    }


def build_registry(r3: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-copied R4 registry with only the seven approved P0 changes."""
    r4 = copy.deepcopy(r3)
    r4["document_status"] = "DRAFT_OFFLINE_NOT_RUNTIME"
    r4["registry_version"] = R4_VERSION
    r4["modified_date"] = "2026-08-10"
    r4["semantic_freeze_status"] = R4_STATUS
    r4["parent_registry"] = {
        "path": "data/nlu/spec/intent_registry_r3.yaml",
        "registry_version": R3_VERSION,
        "sha256": R3_SHA256,
        "inheritance_rule": "PRESERVE_ALL_R3_FIELDS_EXCEPT_APPROVED_P0_01_TO_P0_07",
    }

    partial_percent_contract = {
        "allowed": True,
        "required": True,
        "type": "PERCENT",
        "canonical_unit": "%",
        "valid_range": {"min": 1, "max": 99},
        "enum_values": [],
        "endpoint_routes": {0: "WINDOW_CLOSE", 100: "WINDOW_OPEN"},
        "endpoint_values_prohibited_for_contract": True,
    }
    speed_delta_contract = {
        "allowed": True,
        "required": False,
        "type": "SPEED_DELTA",
        "canonical_unit": "km/h",
        "valid_range": {
            "min": 0,
            "max_ref": "vehicle_capability_limits.max_speed_delta_kmh",
        },
        "enum_values": [],
        "absolute_target_prohibited": True,
        "action_provides_direction": True,
    }
    r4["value_contracts"] = _insert_after(
        r4["value_contracts"],
        "PERCENT_0_100_OPTIONAL",
        "PERCENT_PARTIAL_1_99_REQUIRED",
        partial_percent_contract,
    )
    r4["value_contracts"] = _insert_after(
        r4["value_contracts"],
        "SPEED_OPTIONAL",
        "SPEED_DELTA_OPTIONAL",
        speed_delta_contract,
    )
    continuous_contracts = r4["value_language_semantics"]["continuous_numeric_contracts"]
    continuous_contracts = _insert_list_after(
        continuous_contracts,
        "PERCENT_0_100_OPTIONAL",
        "PERCENT_PARTIAL_1_99_REQUIRED",
    )
    continuous_contracts = _insert_list_after(
        continuous_contracts,
        "SPEED_OPTIONAL",
        "SPEED_DELTA_OPTIONAL",
    )
    r4["value_language_semantics"]["continuous_numeric_contracts"] = continuous_contracts

    r4["mode_contracts"]["CRUISE_GAP_LEVEL"] = ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"]
    headlight_modes = ["OFF", "ON", "POSITION", "DAYTIME_RUNNING_LIGHTS", "AUTO"]
    r4["mode_contracts"]["HEADLIGHT"] = headlight_modes
    r4["mode_mapping_contracts"]["HEADLIGHT_MAIN_SWITCH"] = {
        "canonical_modes": headlight_modes,
        "lexical_aliases": {
            "ON": {
                "canonical_mode": "ON",
                "condition": "EXPLICIT_MAIN_LIGHT_SWITCH_REFERENCE",
            }
        },
        "restricted_aliases": {
            "ON": {
                "allowed_intent_id": "HEADLIGHT_SET_MODE",
                "prohibited_intent_ids": ["LOW_BEAM_ON", "HIGH_BEAM_ON"],
                "prohibited_canonical_mode": "BEAM",
            }
        },
    }

    intents = _by_intent(r4)
    intents["WINDOW_SET_POSITION"]["value_contract"] = "PERCENT_PARTIAL_1_99_REQUIRED"
    intents["ACCELERATE"]["value_contract"] = "SPEED_DELTA_OPTIONAL"
    intents["DECELERATE"]["value_contract"] = "SPEED_DELTA_OPTIONAL"
    for intent_id in ("TRUNK_OPEN", "TRUNK_CLOSE", "TRUNK_SET_POSITION", "TRUNK_LOCK", "TRUNK_UNLOCK"):
        intents[intent_id]["allowed_areas"] = ["REAR"]

    audit = _audit_by_intent(r4)
    audit["WINDOW_SET_POSITION"]["examples"] = ["1%", "20%", "50%", "99%", "一半"]
    audit["HEADLIGHT_SET_MODE"]["examples"] = [
        "OFF",
        "ON",
        "POSITION",
        "DAYTIME_RUNNING_LIGHTS",
        "AUTO",
    ]
    audit["HEADLIGHT_SET_MODE"]["restricted_alias"] = (
        "ON -> ON only for explicit main-light switch reference; "
        "MUST NOT map to LOW_BEAM_ON or HIGH_BEAM_ON"
    )
    audit["WIPER_SET_MODE"]["examples"] = [
        "OFF",
        "SLOW",
        "MEDIUM",
        "FAST",
        "INTERVAL",
        "RAIN_SENSOR",
    ]
    audit["CRUISE_SET_GAP"]["examples"] = [
        "30m",
        "RELATIVE_FARTHER",
        "RELATIVE_CLOSER",
        "LEVEL_1",
        "LEVEL_2",
        "LEVEL_3",
        "LEVEL_4",
    ]

    r4["annotation_guidance"] = {
        "version": "sys-014-r4-core-annotation-guidance-v1",
        "registry_version": R4_VERSION,
        "window_endpoint_routing": {
            "full_open_expressions": ["全开", "完全打开", "全部打开", "降到底", "降到最低"],
            "full_open_intent_id": "WINDOW_OPEN",
            "full_close_expressions": ["全关", "完全关闭", "全部关闭", "升到底", "升到顶", "升到最高"],
            "full_close_intent_id": "WINDOW_CLOSE",
            "partial_percent_range": "1%..99%",
            "partial_percent_intent_id": "WINDOW_SET_POSITION",
            "half_normalization": "50%",
            "prohibited_value_inference": ["一点", "稍微", "一点点", "留条缝"],
            "endpoint_dual_routing_prohibited": True,
        },
        "speed_delta_routing": {
            "intent_ids": ["ACCELERATE", "DECELERATE"],
            "value_semantics": "RELATIVE_SPEED_DELTA_ONLY",
            "allowed_examples": ["加速", "再快一点", "加速10公里每小时", "减速", "慢10公里每小时"],
            "non_cruise_absolute_target_examples": ["加速到80", "减速到40"],
            "non_cruise_absolute_target_status": "CONTRACT_CHECK_NOT_GOLD",
            "automatic_cruise_mapping_prohibited": True,
            "cruise_required_examples": ["巡航速度设为80", "把巡航设到80"],
            "cruise_intent_id": "CRUISE_SET_SPEED",
        },
        "cruise_gap_routing": {
            "value_expressions": ["具体距离", "RELATIVE_FARTHER", "RELATIVE_CLOSER"],
            "mode_expressions": {
                "一档": "LEVEL_1",
                "二档": "LEVEL_2",
                "三档": "LEVEL_3",
                "四档": "LEVEL_4",
            },
            "conditional_slot_contract": "VALUE_XOR_MODE",
        },
        "seat_semantic_boundaries": {
            "intents": [
                "SEAT_LONGITUDINAL_SET_POSITION",
                "SEAT_TILT_SET_ANGLE",
                "SEAT_BACKREST_SET_ANGLE",
            ],
            "lexical_anchors": {
                "LONGITUDINAL": ["前移", "后移", "往前挪", "往后挪", "前后移动", "滑轨", "座椅前后位置"],
                "BACKREST": ["靠背", "椅背", "躺", "后仰", "放倒", "直立", "靠背角度"],
                "TILT": [
                    "坐垫",
                    "座盆",
                    "整体倾角",
                    "座椅整体倾斜",
                    "坐垫前端抬高或降低",
                    "坐垫后端抬高或降低",
                ],
            },
            "unqualified_forward_backward_examples": ["座椅往前调", "座椅往后调"],
            "unqualified_forward_backward_priority": "SEAT_LONGITUDINAL_SET_POSITION",
            "extra_anchor_absence_required": ["BACKREST", "SEAT_CUSHION", "OVERALL_TILT"],
            "ambiguity_policy": "ONLY_WHEN_SOURCE_TEXT_HAS_TWO_REASONABLE_INTERPRETATIONS",
        },
        "headlight_main_switch_routing": {
            "on_expressions": ["打开大灯", "打开前照灯", "开启主灯"],
            "on_intent_id": "HEADLIGHT_SET_MODE",
            "on_mode": "ON",
            "off_expressions": ["关闭大灯", "关闭前照灯"],
            "off_intent_id": "HEADLIGHT_SET_MODE",
            "off_mode": "OFF",
            "explicit_low_beam_intent_ids": ["LOW_BEAM_ON", "LOW_BEAM_OFF"],
            "explicit_high_beam_intent_ids": ["HIGH_BEAM_ON", "HIGH_BEAM_OFF"],
            "on_mode_prohibited_intent_ids": ["LOW_BEAM_ON", "HIGH_BEAM_ON"],
        },
        "trunk_frunk_hood_routing": {
            "TRUNK": {
                "lexical_anchors": ["后备箱", "后备厢", "尾门", "未带前限定的行李厢"],
                "canonical_area": "REAR",
            },
            "HOOD": {
                "lexical_anchors": ["前舱盖", "引擎盖", "发动机舱盖"],
                "intent_ids": ["HOOD_OPEN", "HOOD_CLOSE"],
            },
            "FRUNK": {
                "lexical_anchors": ["前备箱", "前备厢"],
                "mapping_to_hood_prohibited": True,
                "mapping_to_trunk_rear_prohibited": True,
                "proven_operations": ["OPEN", "CLOSE"],
            },
            "frunk_expansion_status": "BLOCKED_BY_KNOWN_UNSUPPORTED_EXPANSION",
            "deferred_candidate_intent_ids": ["FRUNK_OPEN", "FRUNK_CLOSE"],
            "formal_user_voice_projection_prohibited": True,
            "prohibited_symmetric_expansion": ["FRUNK_SET_POSITION", "FRUNK_LOCK", "FRUNK_UNLOCK"],
        },
    }
    return r4


def _markdown_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def build_diff_report(validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "report_version": "r3_to_r4_core_diff_v1",
        "build_version": BUILD_VERSION,
        "source": {
            "path": validation["r3_registry_path"],
            "registry_version": R3_VERSION,
            "sha256": validation["r3_sha256"],
        },
        "target": {
            "path": validation["r4_registry_path"],
            "registry_version": R4_VERSION,
            "semantic_freeze_status": R4_STATUS,
            "sha256": validation["r4_sha256"],
        },
        "summary": {
            "approved_change_groups": 7,
            "p0_pass_count": validation["metrics"]["P0_PASS_COUNT"],
            "changed_path_count": validation["metrics"]["CHANGED_PATH_COUNT"],
            "unapproved_changed_path_count": validation["metrics"]["UNAPPROVED_CHANGED_PATH_COUNT"],
            "validator_status": validation["status"],
        },
        "p0_changes": validation["p0_results"],
        "changed_paths": validation["changed_paths"],
        "unauthorized_changed_paths": validation["unauthorized_changed_paths"],
        "validator_checks": validation["checks"],
    }


def render_diff_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# R3 → R4 Core Diff",
        "",
        f"- R3: `{report['source']['path']}`",
        f"- R3 SHA256: `{report['source']['sha256']}`",
        f"- R4: `{report['target']['path']}`",
        f"- R4 SHA256: `{report['target']['sha256']}`",
        f"- R4 状态: `{report['target']['semantic_freeze_status']}`",
        f"- Validator: **{report['summary']['validator_status']}**",
        f"- 批准外差异路径: **{report['summary']['unapproved_changed_path_count']}**",
        "",
    ]
    for item in report["p0_changes"]:
        lines.extend([
            f"## {item['p0_id']} {item['title']}",
            "",
            f"- 涉及字段: `{', '.join(item['involved_fields'])}`",
            f"- Validator 结果: **{item['validator_result']}**",
            "",
            "修改前：",
            "",
            "```json",
            _markdown_json(item["before"]),
            "```",
            "",
            "修改后：",
            "",
            "```json",
            _markdown_json(item["after"]),
            "```",
            "",
        ])
        if item["errors"]:
            lines.extend(["Validator 错误：", ""] + [f"- {message}" for message in item["errors"]] + [""])
    lines.extend(["## 语义差异路径", ""] + [f"- `{path}`" for path in report["changed_paths"]] + [""])
    return "\n".join(lines)


def build_artifacts(
    *,
    r3_path: Path = R3_PATH,
    r4_path: Path = R4_PATH,
    diff_md_path: Path = DIFF_MD_PATH,
    diff_json_path: Path = DIFF_JSON_PATH,
    validator_result_path: Path = VALIDATOR_RESULT_PATH,
) -> dict[str, Any]:
    if sha256_file(r3_path) != R3_SHA256:
        raise RuntimeError(f"R3 SHA256 mismatch: expected {R3_SHA256}, got {sha256_file(r3_path)}")
    r3 = load_yaml(r3_path)
    r4 = build_registry(r3)
    write_yaml(r4_path, r4)
    validation = validate(r4_path, r3_path=r3_path)
    report = build_diff_report(validation)
    write_json(diff_json_path, report)
    diff_md_path.parent.mkdir(parents=True, exist_ok=True)
    diff_md_path.write_text(render_diff_markdown(report), encoding="utf-8")
    write_json(validator_result_path, validation)
    return {
        "status": validation["status"],
        "build_version": BUILD_VERSION,
        "r3_sha256": sha256_file(r3_path),
        "r4_sha256": sha256_file(r4_path),
        "outputs": [
            r4_path.relative_to(ROOT).as_posix(),
            diff_md_path.relative_to(ROOT).as_posix(),
            diff_json_path.relative_to(ROOT).as_posix(),
            validator_result_path.relative_to(ROOT).as_posix(),
        ],
        "validator_errors": validation["errors"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        result = build_artifacts()
    except (OSError, ValueError, KeyError, RuntimeError, yaml.YAMLError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
