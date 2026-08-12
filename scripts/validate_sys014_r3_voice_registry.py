"""Validate the frozen SYS-014 R3 Full NLU user-voice registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
R2_PATH = ROOT / "data/nlu/spec/intent_registry_draft.yaml"
R3_PATH = ROOT / "data/nlu/spec/intent_registry_r3.yaml"
MAPPING_PATH = ROOT / "data/nlu/spec/mapping_rules/full_nlu_mapping_v1.yaml"
RUNTIME_SUPPORT_PATH = ROOT / "data/nlu/spec/intent_runtime_support.yaml"
MANIFEST_PATH = ROOT / "data/nlu/spec/frozen/full_nlu_r3_freeze_manifest.json"
VSS_AUDIT_PATH = ROOT / "data/nlu/spec/audits/approved44_intent_expansion_audit.json"

R2_VERSION = "sys-014-semantic-hardening-r2"
R3_VERSION = "sys-014-semantic-hardening-r3"
R2_SHA256 = "18c4e02edec1630946be6aa8613345a6e16dc246c883068c6f017f5e28e9f251"
FORMAL_STATUS = "FORMAL_EXECUTABLE"
KNOWN_STATUS = "KNOWN_UNSUPPORTED_CONTROL"
FROZEN_STATUS = "FROZEN_FOR_FULL_NLU_DATASET_BUILD"
EXPECTED_RUNTIME_FULL = {
    "WINDOW_OPEN",
    "DOOR_OPEN",
    "DOOR_UNLOCK",
    "ACCELERATE",
    "DECELERATE",
    "BRAKE",
    "AUTO_PARK_ENABLE",
}
EXPECTED_REMOVED = {
    "MIRROR_ADJUSTMENT_LOCK",
    "MIRROR_ADJUSTMENT_UNLOCK",
    "HOOD_SET_POSITION",
    "LOW_RANGE_ENABLE",
    "LOW_RANGE_DISABLE",
    "TORQUE_DISTRIBUTION_SET",
    "TRANSMISSION_PERFORMANCE_MODE_SET",
    "ELECTRIC_POWERTRAIN_ENGAGE",
    "ELECTRIC_POWERTRAIN_DISENGAGE",
    "CLUTCH_SET_ENGAGEMENT",
    "DIFFERENTIAL_LOCK",
    "DIFFERENTIAL_UNLOCK",
    "PARK_LOCK",
    "PARK_UNLOCK",
    "ABS_ENABLE",
    "ABS_DISABLE",
    "TCS_ENABLE",
    "TCS_DISABLE",
    "EBD_ENABLE",
    "EBD_DISABLE",
    "EBA_ENABLE",
    "EBA_DISABLE",
}
REQUIRED_RETAINED = {
    "ACCELERATE",
    "DECELERATE",
    "BRAKE",
    "EMERGENCY_BRAKE",
    "LANE_CHANGE",
    "LANE_KEEP",
    "EVASIVE_STEER",
    "AUTO_PARK_ENABLE",
    "GEAR_SET",
    "GEAR_CHANGE_MODE_SET",
    "ESC_ENABLE",
    "ESC_DISABLE",
    "HORN_ACTIVATE",
}
MACHINE_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def validate(
    registry_path: Path = R3_PATH,
    *,
    require_frozen: bool = True,
    manifest_path: Path | None = MANIFEST_PATH,
) -> dict[str, Any]:
    errors: list[str] = []

    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    r2 = load_yaml(R2_PATH)
    r3 = load_yaml(registry_path)
    mapping = load_yaml(MAPPING_PATH)
    runtime = load_yaml(RUNTIME_SUPPORT_PATH)
    vss_audit = json.loads(VSS_AUDIT_PATH.read_text(encoding="utf-8"))
    r2_intents = r2.get("intents", [])
    r3_intents = r3.get("intents", [])
    r2_ids = [item.get("intent_id") for item in r2_intents]
    r3_ids = [item.get("intent_id") for item in r3_intents]
    by_id = {item.get("intent_id"): item for item in r3_intents}

    check(sha256_file(R2_PATH) == R2_SHA256, "R2 SHA256 mismatch")
    check(r2.get("registry_version") == R2_VERSION, "R2 version mismatch")
    check(r3.get("registry_version") == R3_VERSION, "R3 version mismatch")
    expected_status = FROZEN_STATUS if require_frozen else "CANDIDATE_PENDING_VALIDATION"
    check(r3.get("semantic_freeze_status") == expected_status, f"R3 status must be {expected_status}")
    check(r3.get("runtime_loading_allowed") is False, "R3 must remain offline/not runtime-loadable")
    check(len(r2_intents) == 93 and len(r3_intents) == 93, "semantic catalog must preserve all 93 intents")
    check(r3_ids == r2_ids, "R3 intent IDs/order differ from R2")
    duplicate_ids = sorted(key for key, count in Counter(r3_ids).items() if count > 1)
    check(not duplicate_ids, f"duplicate canonical_intent_id values: {duplicate_ids}")

    for r2_item, r3_item in zip(r2_intents, r3_intents, strict=True):
        comparable = dict(r3_item)
        comparable.pop("user_voice_scope_status", None)
        check(comparable == r2_item, f"semantic/VSS definition changed for {r2_item.get('intent_id')}")

    formal_ids = [item["intent_id"] for item in r3_intents if item.get("user_voice_scope_status") == FORMAL_STATUS]
    known_ids = [item["intent_id"] for item in r3_intents if item.get("user_voice_scope_status") == KNOWN_STATUS]
    invalid_scope = [item.get("intent_id") for item in r3_intents if item.get("user_voice_scope_status") not in {FORMAL_STATUS, KNOWN_STATUS}]
    check(not invalid_scope, f"invalid user voice scope status: {invalid_scope}")
    check(len(formal_ids) == 71, f"formal user-voice intent count must be 71, got {len(formal_ids)}")
    check(len(known_ids) == 22, f"known unsupported intent count must be 22, got {len(known_ids)}")
    check(set(known_ids) == EXPECTED_REMOVED, f"22-item removal set mismatch: {sorted(set(known_ids) ^ EXPECTED_REMOVED)}")
    check(set(formal_ids) == set(r3_ids) - EXPECTED_REMOVED, "formal set is not the exact R2 complement of removed 22")
    check(r3.get("formal_user_voice_intent_ids") == formal_ids, "formal projection list mismatch")
    check(r3.get("known_unsupported_control_intent_ids") == known_ids, "known unsupported projection list mismatch")
    check(REQUIRED_RETAINED <= set(formal_ids), f"required high-risk intents missing: {sorted(REQUIRED_RETAINED - set(formal_ids))}")

    enums = r3.get("enums", {})
    check(enums.get("user_voice_scope_status") == [FORMAL_STATUS, KNOWN_STATUS], "user voice scope enum mismatch")
    stats = r3.get("statistics", {})
    check(stats.get("intent_count") == 93, "semantic intent_count must remain 93")
    check(stats.get("formal_user_voice_intent_count") == 71, "formal count metadata mismatch")
    check(stats.get("known_unsupported_control_intent_count") == 22, "known unsupported count metadata mismatch")

    known_areas = set(r3.get("area_catalog", {}))
    value_contracts = r3.get("value_contracts", {})
    mode_contracts = r3.get("mode_contracts", {})
    direction_contracts = r3.get("direction_contracts", {})
    conditional_contracts = r3.get("conditional_slot_contracts", {})
    value_mapping_contracts = r3.get("value_mapping_contracts", {})
    mode_mapping_contracts = r3.get("mode_mapping_contracts", {})
    allowed_slots = set(r3.get("enums", {}).get("capability_slot_type", []))
    semantic_groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    unresolved_contracts: list[str] = []
    invalid_machine_ids: list[str] = []
    unknown_areas: list[str] = []
    for item in r3_intents:
        intent_id = str(item.get("intent_id"))
        for field in ("intent_id", "canonical_action", "canonical_target", "control_attribute"):
            value = item.get(field)
            if not isinstance(value, str) or not MACHINE_ID_RE.fullmatch(value):
                invalid_machine_ids.append(f"{intent_id}.{field}={value!r}")
        semantic_groups[(item.get("canonical_action"), item.get("canonical_target"), item.get("control_attribute"))].append(intent_id)
        slots = item.get("required_slots", []) + item.get("optional_slots", [])
        unknown_slots = sorted(set(slots) - allowed_slots)
        if unknown_slots:
            unresolved_contracts.append(f"{intent_id}:unknown_slots={unknown_slots}")
        for area in item.get("allowed_areas", []):
            if area not in known_areas:
                unknown_areas.append(f"{intent_id}:{area}")
        if "VALUE" in slots and item.get("value_contract") not in value_contracts:
            unresolved_contracts.append(f"{intent_id}:value_contract")
        if "MODE" in slots and item.get("mode_contract") not in mode_contracts:
            unresolved_contracts.append(f"{intent_id}:mode_contract")
        if "DIRECTION" in slots and item.get("direction_contract") not in direction_contracts:
            unresolved_contracts.append(f"{intent_id}:direction_contract")
        if item.get("conditional_slot_contract") and item.get("conditional_slot_contract") not in conditional_contracts:
            unresolved_contracts.append(f"{intent_id}:conditional_slot_contract")
        if item.get("value_mapping_contract") and item.get("value_mapping_contract") not in value_mapping_contracts:
            unresolved_contracts.append(f"{intent_id}:value_mapping_contract")
        if item.get("mode_mapping_contract") and item.get("mode_mapping_contract") not in mode_mapping_contracts:
            unresolved_contracts.append(f"{intent_id}:mode_mapping_contract")
    collisions = {"|".join(key): ids for key, ids in semantic_groups.items() if len(ids) > 1}
    check(not invalid_machine_ids, f"invalid canonical machine identifiers: {invalid_machine_ids}")
    check(not collisions, f"semantic key collisions: {collisions}")
    check(not unresolved_contracts, f"unresolved contracts: {unresolved_contracts}")
    check(not unknown_areas, f"unknown area references: {unknown_areas}")

    families = r3.get("capability_families", [])
    family_ids = {family.get("family_id") for family in families if isinstance(family, dict)}
    family_intents = [intent_id for family in families if isinstance(family, dict) for intent_id in family.get("intents", [])]
    check(Counter(family_intents) == Counter(r3_ids), "capability family coverage is not one-to-one")
    check(all(item.get("capability_family") in family_ids for item in r3_intents), "unknown capability family reference")
    check(all(by_id[intent_id].get("vss_capability_ids") for intent_id in EXPECTED_REMOVED), "removed semantic lost VSS source")
    approved_vss_ids = {
        row.get("approved_capability_id")
        for row in vss_audit.get("capability_rows", [])
        if isinstance(row, dict)
    }
    source_traceability_errors: list[str] = []
    for item in r3_intents:
        intent_id = str(item.get("intent_id"))
        vss_ids = item.get("vss_capability_ids", [])
        if item.get("capability_origin") in {"VSS", "VSS_AND_PROJECT"} and not vss_ids:
            source_traceability_errors.append(f"{intent_id}:missing_vss_capability_source")
        for capability_id in vss_ids:
            if capability_id not in approved_vss_ids:
                source_traceability_errors.append(f"{intent_id}:unapproved_vss_capability={capability_id}")
    check(not source_traceability_errors, f"source traceability errors: {source_traceability_errors}")

    steering_extension = by_id.get("STEERING_WHEEL_SET_EXTENSION", {})
    steering_tilt = by_id.get("STEERING_WHEEL_SET_TILT", {})
    check(steering_extension.get("conditional_slot_contract") == "VALUE_OR_DIRECTION", "steering extension conditional contract mismatch")
    check(steering_tilt.get("conditional_slot_contract") == "VALUE_OR_DIRECTION", "steering tilt conditional contract mismatch")
    check(direction_contracts.get("STEERING_WHEEL_EXTEND_RETRACT") == ["EXTEND", "RETRACT"], "steering extension directions mismatch")
    check(direction_contracts.get("STEERING_WHEEL_UP_DOWN") == ["UP", "DOWN"], "steering tilt directions mismatch")

    light = mapping.get("light_semantics", {})
    check(light.get("main_headlight_position_mode", {}).get("canonical_mode") == "POSITION", "position-light mapping missing")
    check(light.get("main_headlight_position_mode", {}).get("canonical_intent_id") == "HEADLIGHT_SET_MODE", "position-light intent mismatch")
    check(set(light.get("independent_parking_light", {}).get("allowed_intent_ids", [])) == {"PARKING_LIGHT_ON", "PARKING_LIGHT_OFF"}, "parking-light mapping mismatch")
    broad = light.get("broad_light_object_ambiguity", {})
    check(broad.get("structure_status") == "歧义", "broad-light ambiguity rule missing")
    check(set(broad.get("prohibited_automatic_intent_ids", [])) >= {"HEADLIGHT_SET_MODE", "LOW_BEAM_ON", "HIGH_BEAM_ON", "FOG_LIGHT_ON", "PARKING_LIGHT_ON"}, "broad-light prohibited mappings incomplete")

    gear = by_id.get("GEAR_SET", {})
    expected_gears = ["P", "N", "D", "R", "FORWARD_GEAR_N", "REVERSE_GEAR_N"]
    gear_mapping = mode_mapping_contracts.get("GEAR_VEHICLE_SPECIFIC", {})
    check(mode_contracts.get("GEAR") == expected_gears, "GEAR mode contract mismatch")
    check(gear.get("mode_mapping_contract") == "GEAR_VEHICLE_SPECIFIC", "GEAR mapping contract reference mismatch")
    check(gear_mapping.get("canonical_modes") == expected_gears, "GEAR mapping canonical modes mismatch")
    check(gear_mapping.get("vss_code_rules", {}).get("R") == "VEHICLE_CAPABILITY_MAPPING_REQUIRED", "R must defer to VehicleCapabilityMapping")
    check(gear_mapping.get("prohibited_generic_mapping") == "R -> -1 or REVERSE_GEAR_1", "GEAR prohibited generic mapping changed")

    runtime_full = {intent_id for intent_id, status in runtime.get("intents", {}).items() if status.get("execution_support") == "FULL"}
    check(runtime_full == EXPECTED_RUNTIME_FULL, f"runtime FULL facts changed: {sorted(runtime_full)}")
    runtime_meta = r3.get("runtime_support_independence", {})
    check(runtime_meta.get("source_sha256") == sha256_file(RUNTIME_SUPPORT_PATH), "runtime support provenance hash mismatch")
    check(runtime_meta.get("defines_full_nlu_label_space") is False, "runtime support must not define Full NLU labels")

    poc_policy = r3.get("historical_poc_policy", {})
    check(poc_policy.get("active_full_nlu_dependency_count") == 0, "historical PoC active Full NLU dependency must be zero")
    forbidden = re.compile(r"sys014-poc7|poc7-v[12]|7-Intent|7 Intent|rbt3-exp|electra-exp", re.IGNORECASE)
    active_runtime_refs: list[str] = []
    for root in (ROOT / "backend/app", ROOT / "config"):
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".py", ".yaml", ".yml", ".json"}:
                if forbidden.search(path.read_text(encoding="utf-8", errors="ignore")):
                    active_runtime_refs.append(path.relative_to(ROOT).as_posix())
    check(not active_runtime_refs, f"active runtime still references historical 7-Intent PoC: {active_runtime_refs}")

    annotation = r3.get("annotation_schema_compatibility", {})
    check(annotation.get("status") == "CONFLICT_RECORDED_DEFERRED_TO_NEXT_STAGE", "annotation schema conflict was not recorded")

    if manifest_path is not None and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        check(manifest.get("registry_file") == "data/nlu/spec/intent_registry_r3.yaml", "manifest registry path mismatch")
        check(manifest.get("registry_version") == R3_VERSION, "manifest registry version mismatch")
        check(manifest.get("registry_sha256") == sha256_file(registry_path), "manifest registry SHA mismatch")
        check(manifest.get("status") == FROZEN_STATUS, "manifest status mismatch")
        check(manifest.get("formal_user_voice_intent_count") == 71, "manifest formal count mismatch")
        check(manifest.get("known_unsupported_control_intent_count") == 22, "manifest known count mismatch")
        check(manifest.get("parent_registry_sha256") == R2_SHA256, "manifest parent SHA mismatch")
        check(manifest.get("mapping_rule_sha256") == sha256_file(MAPPING_PATH), "manifest mapping SHA mismatch")

    formal_items = [by_id[intent_id] for intent_id in formal_ids]
    result = {
        "status": "PASS" if not errors else "FAIL",
        "registry_version": r3.get("registry_version"),
        "registry_sha256": sha256_file(registry_path),
        "metrics": {
            "SEMANTIC_INTENT_COUNT": len(r3_intents),
            "FORMAL_USER_VOICE_INTENT_COUNT": len(formal_ids),
            "KNOWN_UNSUPPORTED_CONTROL_INTENT_COUNT": len(known_ids),
            "DUPLICATE_INTENT_ID_COUNT": len(duplicate_ids),
            "SEMANTIC_KEY_COLLISION_COUNT": len(collisions),
            "UNRESOLVED_CONTRACT_COUNT": len(unresolved_contracts),
            "UNKNOWN_AREA_REFERENCE_COUNT": len(unknown_areas),
            "SOURCE_TRACEABILITY_ERROR_COUNT": len(source_traceability_errors),
            "CANONICAL_ACTION_COUNT_FORMAL": len({item.get('canonical_action') for item in formal_items}),
            "CANONICAL_TARGET_COUNT_FORMAL": len({item.get('canonical_target') for item in formal_items}),
            "CONTROL_ATTRIBUTE_COUNT_FORMAL": len({item.get('control_attribute') for item in formal_items}),
            "VALUE_CONTRACT_COUNT": len(value_contracts),
            "DIRECTION_CONTRACT_COUNT": len(direction_contracts),
            "MODE_CONTRACT_COUNT": len(mode_contracts),
            "CONDITIONAL_SLOT_CONTRACT_COUNT": len(conditional_contracts),
            "RUNTIME_EXECUTION_FULL_COUNT": len(runtime_full),
            "ACTIVE_FULL_NLU_DEPENDENCY_COUNT": len(active_runtime_refs),
        },
        "formal_user_voice_intent_ids": formal_ids,
        "known_unsupported_control_intent_ids": known_ids,
        "errors": errors,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=R3_PATH)
    parser.add_argument("--candidate", action="store_true")
    parser.add_argument("--no-manifest", action="store_true")
    args = parser.parse_args()
    result = validate(
        args.registry,
        require_frozen=not args.candidate,
        manifest_path=None if args.no_manifest else MANIFEST_PATH,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
