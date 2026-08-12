"""Validate the strictly bounded R4 final dead-reference micro patch."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, changed_paths, sha256_file
from validate_sys014_r4_full_registry import _active_poc_references


ROOT = Path(__file__).resolve().parents[1]
FINAL_PATH = ROOT / "data/nlu/spec/intent_registry_r4_final.yaml"
FORMAL_MAPPING_PATH = ROOT / "data/nlu/spec/mapping_rules/nlu_mapping_r4_scope_v1.yaml"
MANDATORY_RULES_PATH = ROOT / "data/nlu/spec/mapping_rules/r4_gold_mapping_mandatory_rules_v1.yaml"
EXECUTION_TODOS_PATH = ROOT / "data/nlu/spec/r4_execution_layer_todos_v1.yaml"

PRE_PATCH_SHA256 = "b6453ff4c264464bb74ceb2aaa78cfc7fea7b55eef9a1d61bb2a7c54df47edae"
DEAD_REFERENCE_PATH = (
    "mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH.restricted_aliases.ON.prohibited_canonical_mode"
)
RUNTIME_SCOPES = ["FORMAL_EXECUTABLE", "KNOWN_CONTROL_BYPASS", "NON_CONTROL", "UNKNOWN_OOD"]
BEAM_INTENT_IDS = ["LOW_BEAM_ON", "LOW_BEAM_OFF", "HIGH_BEAM_ON", "HIGH_BEAM_OFF"]


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def _yaml_sha256(value: dict[str, Any]) -> str:
    rendered = yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120)
    payload = rendered.replace("\n", os.linesep).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def reconstruct_pre_patch(final: dict[str, Any]) -> dict[str, Any]:
    parent = copy.deepcopy(final)
    aliases = parent["mode_mapping_contracts"]["HEADLIGHT_MAIN_SWITCH"]["restricted_aliases"]["ON"]
    if "prohibited_canonical_mode" in aliases:
        raise ValueError("dead BEAM reference still exists in patched registry")
    aliases["prohibited_canonical_mode"] = "BEAM"
    return parent


def validate(final_path: Path = FINAL_PATH) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    errors: list[str] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "detail": "verified" if passed else detail,
        })
        if not passed:
            errors.append(f"{name}: {detail}")

    final = load_yaml(final_path)
    parent = reconstruct_pre_patch(final)
    actual_paths = sorted(set(changed_paths(parent, final)))
    check("PRE_PATCH_SHA256_RECONSTRUCTED", _yaml_sha256(parent) == PRE_PATCH_SHA256, "reconstructed parent SHA mismatch")
    check("ONLY_APPROVED_SEMANTIC_CHANGE", actual_paths == [DEAD_REFERENCE_PATH], f"changed paths: {actual_paths}")

    parent_intents = parent["intents"]
    final_intents = final["intents"]
    parent_ids = [item["intent_id"] for item in parent_intents]
    final_ids = [item["intent_id"] for item in final_intents]
    check("RUNTIME_INTENT_COUNT_71", final["statistics"]["runtime_intent_head_count"] == 71 and len(final_intents) == 71, "runtime Intent count must be 71")
    check("FORMAL_ID_SET_EXACT", set(final_ids) == set(parent_ids), "Formal ID set changed")
    check("FORMAL_ID_ORDER_EXACT", final_ids == parent_ids == final["formal_user_voice_intent_ids"], "Formal ID order changed")
    check("FORMAL_DEFINITIONS_100_PERCENT_PRESERVED", final_intents == parent_intents, "one or more Formal Intent definitions changed")

    check("RUNTIME_SCOPES_EXACT", final["enums"]["runtime_scope"] == RUNTIME_SCOPES, "runtime scopes changed")
    check("KNOWN_CONTROL_BYPASS_EXACT", final["runtime_scope_routing"]["KNOWN_CONTROL_BYPASS"] == parent["runtime_scope_routing"]["KNOWN_CONTROL_BYPASS"] == {"decision_route": "PASS_BYPASS", "execution_authorized_by_yuzheng": False, "route_target": "NATIVE_COCKPIT_ASSISTANT"}, "KNOWN_CONTROL_BYPASS behavior changed")
    check("FOLLOWING_GAP_REQUIRED_ABSENT", "FOLLOWING_GAP_REQUIRED" not in yaml.safe_dump(final, allow_unicode=True), "FOLLOWING_GAP_REQUIRED was restored")
    active_poc = _active_poc_references()
    check("ACTIVE_7_INTENT_DEPENDENCY_ZERO", not active_poc, f"active legacy dependencies: {active_poc}")

    headlight_modes = final["mode_contracts"]["HEADLIGHT"]
    alias = final["mode_mapping_contracts"]["HEADLIGHT_MAIN_SWITCH"]["restricted_aliases"]["ON"]
    check("HEADLIGHT_CANONICAL_MODE_NO_BEAM", headlight_modes == ["OFF", "ON", "POSITION", "DAYTIME_RUNNING_LIGHTS", "AUTO"], f"HEADLIGHT modes: {headlight_modes}")
    check("DEAD_BEAM_REFERENCE_ABSENT", "prohibited_canonical_mode" not in alias, f"restricted alias: {alias}")
    check("HEADLIGHT_ON_ROUTE_PRESERVED", alias.get("allowed_intent_id") == "HEADLIGHT_SET_MODE" and alias.get("prohibited_intent_ids") == ["LOW_BEAM_ON", "HIGH_BEAM_ON"], f"restricted alias: {alias}")
    check("LOW_HIGH_BEAM_INTENTS_INDEPENDENT", all(intent_id in final_ids for intent_id in BEAM_INTENT_IDS), "one or more LOW/HIGH BEAM intents missing")

    check("FORMAL_MAPPING_NOT_CREATED", not FORMAL_MAPPING_PATH.exists(), "formal mapping must not be created in case B")
    mandatory = load_yaml(MANDATORY_RULES_PATH)
    rules = mandatory.get("rules", [])
    rule = rules[0] if len(rules) == 1 else {}
    expected_flags = {
        "result": "QUARANTINE_CONTRACT_GAP",
        "formal_positive_prohibited": True,
        "automatic_cruise_mapping_prohibited": True,
        "known_control_bypass_prohibited": True,
        "accelerate_delta_mapping_prohibited": True,
        "decelerate_delta_mapping_prohibited": True,
        "reason_code": "NON_CRUISE_ABSOLUTE_SPEED_TARGET_UNSUPPORTED",
    }
    mandatory_ok = (
        mandatory.get("version") == "r4_gold_mapping_mandatory_rules_v1"
        and len(rules) == 1
        and rule.get("rule_id") == "NON_CRUISE_ABSOLUTE_SPEED_TARGET"
        and all(rule.get(key) == value for key, value in expected_flags.items())
        and mandatory.get("required_integration_target") == "nlu_mapping_r4_scope_v1"
        and mandatory.get("integration_must_not_be_omitted") is True
    )
    check("ABSOLUTE_SPEED_MANDATORY_RULE_LANDED", mandatory_ok, "mandatory absolute-speed rule is incomplete or contains extra rules")

    todos_doc = load_yaml(EXECUTION_TODOS_PATH)
    todos = todos_doc.get("todos", [])
    todo_ids = [item.get("todo_id") for item in todos]
    todo_flags_ok = len(todos) == 2 and all(item.get("blocks_gold_build") is False and item.get("blocks_nlu_training") is False for item in todos)
    check("EXECUTION_TODOS_REGISTERED", todo_ids == ["HIGH_RISK_PRECONDITION_GATE", "COMPOSITE_AREA_FANOUT_GATE"] and todo_flags_ok, f"todo IDs/flags: {todo_ids}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "pre_patch_sha256": PRE_PATCH_SHA256,
        "post_patch_sha256": sha256_file(final_path),
        "yaml_semantic_changed_field_count": len(actual_paths),
        "yaml_semantic_changed_paths": actual_paths,
        "formal_intents_100_percent_preserved": final_intents == parent_intents,
        "gold_absolute_speed_rule_landed": mandatory_ok,
        "execution_todos_registered": todo_ids == ["HIGH_RISK_PRECONDITION_GATE", "COMPOSITE_AREA_FANOUT_GATE"] and todo_flags_ok,
        "metrics": {
            "RUNTIME_INTENT_HEAD_COUNT": final["statistics"]["runtime_intent_head_count"],
            "FORMAL_INTENT_COUNT": len(final_intents),
            "RUNTIME_SCOPE_COUNT": len(final["enums"]["runtime_scope"]),
            "ACTIVE_7_INTENT_DEPENDENCY_COUNT": len(active_poc),
            "MANDATORY_MAPPING_RULE_COUNT": len(rules),
            "EXECUTION_TODO_COUNT": len(todos),
        },
        "checks": checks,
        "errors": errors,
    }


def main() -> int:
    try:
        result = validate()
    except (OSError, ValueError, KeyError, yaml.YAMLError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
