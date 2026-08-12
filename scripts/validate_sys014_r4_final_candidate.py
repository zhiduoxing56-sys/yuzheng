"""Validate the approved SYS-014 R4 final semantic-consistency candidate."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, sha256_file
from validate_sys014_r4_full_registry import (
    CORE_PATH,
    CORE_SHA256,
    MAC_PATHS,
    R3_PATH,
    R3_SHA256,
    SOURCE_SCREEN_PATH,
    validate as validate_full,
)

FULL_NLU_DIR = Path(__file__).resolve().parent / "full_nlu"
if str(FULL_NLU_DIR) not in sys.path:
    sys.path.insert(0, str(FULL_NLU_DIR))
from r4_final_candidate_evidence import (  # noqa: E402
    APPROVED_NEW_INTENT_IDS,
    AREA_FAMILIES,
    CAMERA_DIRECT_ACTION_VALUES,
    MEDIA_FORBIDDEN_VALUES,
    build_final_patch_evidence,
)
from r4_known_unsupported_evidence import extract_frames  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
FULL_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_full_draft.yaml"
FINAL_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_final_candidate.yaml"
FULL_SHA256 = "393de4203c2cb93b0162724b336cb29a2cc67fba1c73b1cbc1fe62bb642f4f21"
FINAL_VERSION = "sys-014-semantic-hardening-r4-final-candidate"
FINAL_STATUS = "FINAL_CANDIDATE_PENDING_APPROVAL"
MACHINE_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")

VALUE_REQUIRED_INTENTS = {
    "AMBIENT_LIGHT_SET_BRIGHTNESS": "SOURCE_LEVEL_REQUIRED",
    "AMBIENT_LIGHT_SET_COLOR": "SOURCE_COLOR_REQUIRED",
    "ARMREST_SET_POSITION": "SOURCE_POSITION_REQUIRED",
    "DISPLAY_SET_BRIGHTNESS": "SOURCE_LEVEL_REQUIRED",
    "DISPLAY_SET_POSITION": "SOURCE_POSITION_REQUIRED",
    "FRAGRANCE_SET_LEVEL": "SOURCE_LEVEL_REQUIRED",
    "GLASS_ROOF_SET_TRANSPARENCY": "SOURCE_TRANSPARENCY_REQUIRED",
    "HVAC_SET_AIRFLOW_DIRECTION": "SOURCE_AIRFLOW_DIRECTION_REQUIRED",
    "HVAC_SET_FAN_SPEED": "SOURCE_LEVEL_REQUIRED",
    "HVAC_SET_TEMPERATURE": "SOURCE_TEMPERATURE_REQUIRED",
    "MEDIA_VOLUME_SET": "SOURCE_LEVEL_REQUIRED",
    "READING_LIGHT_SET_BRIGHTNESS": "SOURCE_LEVEL_REQUIRED",
    "REFRIGERATOR_SET_TEMPERATURE": "SOURCE_TEMPERATURE_REQUIRED",
    "SEAT_HEATING_SET_LEVEL": "SOURCE_LEVEL_REQUIRED",
    "SEAT_MASSAGE_SET_LEVEL": "SOURCE_LEVEL_REQUIRED",
    "SEAT_VENTILATION_SET_LEVEL": "SOURCE_LEVEL_REQUIRED",
    "AIR_PURIFIER_SET_FAN_SPEED": "SOURCE_LEVEL_REQUIRED",
    "FRAGRANCE_SET_SCENT": "SOURCE_SCENT_REQUIRED",
    "INTERIOR_LIGHT_SET_BRIGHTNESS": "SOURCE_LEVEL_REQUIRED",
    "INTERIOR_LIGHT_SET_COLOR": "SOURCE_COLOR_REQUIRED",
}

EXPECTED_EVIDENCE_COUNTS = {
    "AIR_PURIFIER_SET_FAN_SPEED": 8,
    "DISPLAY_SET_MODE": 32,
    "READING_LIGHT_SET_MODE": 2,
    "REFRIGERATOR_SET_MODE": 10,
    "FRAGRANCE_SET_SCENT": 5,
    "INTERIOR_LIGHT_SET_BRIGHTNESS": 26,
    "INTERIOR_LIGHT_SET_COLOR": 2,
    "INTERIOR_LIGHT_SET_MODE": 8,
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def _field_changes(before: dict[str, Any], after: dict[str, Any]) -> set[str]:
    return {key for key in set(before) | set(after) if before.get(key) != after.get(key)}


def validate(
    registry_path: Path = FINAL_PATH,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})
        if not passed:
            errors.append(f"{name}: {detail}")

    r3_hash = sha256_file(R3_PATH)
    core_hash = sha256_file(CORE_PATH)
    full_hash = sha256_file(FULL_PATH)
    check("R3_SHA256_FROZEN", r3_hash == R3_SHA256, f"expected {R3_SHA256}, got {r3_hash}")
    check("CORE_SHA256_FROZEN", core_hash == CORE_SHA256, f"expected {CORE_SHA256}, got {core_hash}")
    check("FULL_SHA256_FROZEN", full_hash == FULL_SHA256, f"expected {FULL_SHA256}, got {full_hash}")
    full_validation = validate_full()
    check("FULL_PARENT_VALID", full_validation["status"] == "PASS", f"full validator errors: {full_validation['errors']}")

    full = load_yaml(FULL_PATH)
    final = load_yaml(registry_path)
    final_hash = sha256_file(registry_path)
    if evidence is None:
        frames = extract_frames(MAC_PATHS, SOURCE_SCREEN_PATH)
        evidence = build_final_patch_evidence(frames, full["area_catalog"])

    check("FINAL_VERSION", final.get("registry_version") == FINAL_VERSION, "final registry version mismatch")
    check("FINAL_STATUS", final.get("semantic_freeze_status") == FINAL_STATUS, "final status mismatch")
    check(
        "FULL_PARENT_LINK",
        final.get("parent_registry") == {
            "path": "data/nlu/spec/intent_registry_r4_full_draft.yaml",
            "registry_version": "sys-014-semantic-hardening-r4-full-draft",
            "sha256": FULL_SHA256,
            "inheritance_rule": "ONLY_APPLY_APPROVED_FINAL_SEMANTIC_CONSISTENCY_PATCH",
        },
        "full parent path/version/hash mismatch",
    )

    full_intents = full["intents"]
    final_intents = final["intents"]
    full_ids = [item["intent_id"] for item in full_intents]
    final_ids = [item["intent_id"] for item in final_intents]
    full_by_id = {item["intent_id"]: item for item in full_intents}
    final_by_id = {item["intent_id"]: item for item in final_intents}
    check("ONLY_APPROVED_NEW_IDS", final_ids == full_ids + APPROVED_NEW_INTENT_IDS, "final adds IDs outside approved eight or changes order")
    check("UNIQUE_INTENT_IDS", len(final_ids) == len(set(final_ids)), "Intent IDs are not unique")

    formal_full = [item for item in full_intents if item.get("user_voice_scope_status") == "FORMAL_EXECUTABLE"]
    formal_final = [item for item in final_intents if item.get("user_voice_scope_status") == "FORMAL_EXECUTABLE"]
    check("FORMAL_COUNT_71", len(formal_final) == 71, f"formal count is {len(formal_final)}")
    check("FORMAL_ID_ORDER_FROZEN", [item["intent_id"] for item in formal_final] == [item["intent_id"] for item in formal_full], "formal ID set/order changed")
    check("FORMAL_DEFINITIONS_FROZEN", formal_final == formal_full, "one or more FORMAL definitions changed")

    area_existing_ids: set[str] = set()
    for family in full["capability_families"]:
        if family["family_id"] in {f"PROJECT_{key}_KNOWN_CONTROL" for key in AREA_FAMILIES}:
            area_existing_ids.update(family["intents"])
    allowed_existing_fields: dict[str, set[str]] = defaultdict(set)
    for intent_id in VALUE_REQUIRED_INTENTS:
        if intent_id in full_by_id:
            allowed_existing_fields[intent_id].update({"value_contract", "required_slots", "optional_slots"})
    for intent_id in area_existing_ids | {"STEERING_WHEEL_HEATING_ON", "STEERING_WHEEL_HEATING_OFF"}:
        allowed_existing_fields[intent_id].update({"allowed_areas", "optional_slots"})
    allowed_existing_fields["DRIVING_MODE_SET"].add("chinese_name")
    unexpected_existing_changes = {}
    for intent_id in full_ids:
        changed = _field_changes(full_by_id[intent_id], final_by_id[intent_id])
        unexpected = changed - allowed_existing_fields[intent_id]
        if unexpected:
            unexpected_existing_changes[intent_id] = sorted(unexpected)
    check("EXISTING_INTENT_CHANGE_SCOPE", not unexpected_existing_changes, f"unapproved fields changed: {unexpected_existing_changes}")

    for intent_id in APPROVED_NEW_INTENT_IDS:
        item = final_by_id[intent_id]
        check(
            f"NEW_INTENT_SCOPE_{intent_id}",
            item.get("user_voice_scope_status") == "KNOWN_UNSUPPORTED_CONTROL"
            and item.get("capability_origin") == "PROJECT_NATIVE"
            and item.get("vss_relation") == "NONE"
            and item.get("vss_capability_ids") == [],
            "new intent scope/provenance invalid",
        )
    check("NEW_INTENTS_NOT_FORMAL", not (set(APPROVED_NEW_INTENT_IDS) & set(final["formal_user_voice_intent_ids"])), "new intent entered FORMAL projection")

    required_contract_names = {
        "SOURCE_TEMPERATURE_REQUIRED", "SOURCE_LEVEL_REQUIRED", "SOURCE_AIRFLOW_DIRECTION_REQUIRED",
        "SOURCE_POSITION_REQUIRED", "SOURCE_COLOR_REQUIRED", "SOURCE_TRANSPARENCY_REQUIRED", "SOURCE_SCENT_REQUIRED",
    }
    contracts = final["value_contracts"]
    check("REQUIRED_CONTRACTS_PRESENT", required_contract_names <= set(contracts), "required SOURCE contracts missing")
    check(
        "REQUIRED_CONTRACT_SEMANTICS",
        all(
            contracts[name].get("required") is True
            and contracts[name].get("valid_range") is None
            and contracts[name].get("relative_value_policy") == "RECOGNIZE_BUT_KEEP_UNRESOLVED_WITHOUT_PHYSICAL_MAGNITUDE"
            for name in required_contract_names
        ),
        "required contract inferred a fixed range/step or lacks unresolved-relative policy",
    )
    value_repairs = []
    for intent_id, contract in VALUE_REQUIRED_INTENTS.items():
        item = final_by_id[intent_id]
        if item.get("value_contract") != contract or "VALUE" not in item.get("required_slots", []) or "VALUE" in item.get("optional_slots", []):
            value_repairs.append(intent_id)
    check("VALUE_REQUIRED_INTENTS", not value_repairs, f"VALUE repair incomplete: {value_repairs}")
    check(
        "TRANSPARENCY_SOURCE_CONTRACT",
        final_by_id["GLASS_ROOF_SET_TRANSPARENCY"]["value_contract"] == "SOURCE_TRANSPARENCY_REQUIRED",
        "glass roof still uses percent contract",
    )

    evidence_counts = {intent_id: evidence["approved_new_intents"][intent_id]["unique_sample_count"] for intent_id in APPROVED_NEW_INTENT_IDS}
    check("APPROVED_EVIDENCE_COUNTS", evidence_counts == EXPECTED_EVIDENCE_COUNTS, f"unexpected evidence counts: {evidence_counts}")

    area_errors: list[str] = []
    final_families = {item["family_id"]: item for item in final["capability_families"]}
    for family_key in AREA_FAMILIES:
        expected = evidence["family_area_evidence"][family_key]["allowed_areas"]
        members = final_families[f"PROJECT_{family_key}_KNOWN_CONTROL"]["intents"]
        for intent_id in members:
            item = final_by_id[intent_id]
            expected_optional_area = bool(expected)
            if item.get("allowed_areas") != expected or (("AREA" in item.get("optional_slots", [])) != expected_optional_area):
                area_errors.append(intent_id)
    check("FAMILY_AREA_UNION_POLICY", not area_errors, f"family AREA policy mismatch: {area_errors}")
    steering_errors = [
        intent_id for intent_id in ("STEERING_WHEEL_HEATING_ON", "STEERING_WHEEL_HEATING_OFF")
        if final_by_id[intent_id].get("allowed_areas") != [] or "AREA" in final_by_id[intent_id].get("optional_slots", [])
    ]
    check("STEERING_WHEEL_SINGLETON_AREA", not steering_errors, f"steering wheel still has AREA: {steering_errors}")
    guidance = final["annotation_guidance"]
    area_pending = guidance.get("family_area_semantic_policy", {}).get("AREA_PENDING_REPORT", {})
    expected_pending = {
        family: evidence["family_area_evidence"][family]["pending"]
        for family in AREA_FAMILIES
        if evidence["family_area_evidence"][family]["pending"]
    }
    check("AREA_PENDING_REPORT", area_pending == expected_pending, "unmapped family areas missing or inferred")

    media_modes = final["mode_contracts"]["KNOWN_MEDIA_SOURCE_MODE"]
    camera_modes = final["mode_contracts"]["KNOWN_CAMERA_SOURCE_MODE"]
    check("MEDIA_MODE_REBUILT", media_modes == evidence["media_mode_evidence"]["mode_values"], "MEDIA mode contract differs from clean evidence")
    check("MEDIA_FORBIDDEN_VALUES_REMOVED", not (set(media_modes) & MEDIA_FORBIDDEN_VALUES), "forbidden MEDIA values remain")
    check("CAMERA_MODE_REBUILT", camera_modes == evidence["camera_mode_evidence"]["mode_values"], "CAMERA mode contract differs from strict selection evidence")
    check("CAMERA_DIRECT_ACTIONS_REMOVED", not (set(camera_modes) & CAMERA_DIRECT_ACTION_VALUES), "direct camera actions remain as MODE")
    check(
        "CAMERA_ACTION_PENDING",
        guidance.get("camera_mode_routing", {}).get("camera_action_pending") == evidence["camera_mode_evidence"]["camera_action_pending"],
        "camera action pending evidence missing",
    )

    frunk_guidance = guidance["trunk_frunk_hood_routing"]
    check(
        "FRUNK_GUIDANCE",
        frunk_guidance["FRUNK"].get("proven_operations") == ["OPEN"]
        and frunk_guidance["FRUNK"].get("pending_operations") == ["CLOSE"]
        and frunk_guidance.get("frunk_close_status") == "PENDING_NO_REAL_DATA_EVIDENCE",
        "FRUNK proven/pending operation guidance mismatch",
    )
    check("FRUNK_CLOSE_ABSENT", "FRUNK_CLOSE" not in final_ids, "FRUNK_CLOSE entered registry")
    check("FOLLOWING_GAP_ABSENT", "FOLLOWING_GAP_REQUIRED" not in contracts, "dead following-gap contract returned")
    check("DRIVING_MODE_NAME", final_by_id["DRIVING_MODE_SET"].get("chinese_name") == "设置驾驶模式", "driving mode Chinese name not fixed")
    check("GUIDANCE_VERSION", guidance.get("registry_version") == FINAL_VERSION, "annotation guidance version not synchronized")
    lighting = guidance.get("interior_lighting_lexical_boundary", {})
    check(
        "INTERIOR_LIGHTING_BOUNDARY",
        lighting.get("READING_LIGHT") == ["明确阅读灯"]
        and lighting.get("AMBIENT_LIGHT") == ["明确氛围灯"]
        and set(lighting.get("external_lighting_mapping_prohibited", [])) == {"HEADLIGHT", "LOW_BEAM", "HIGH_BEAM", "FOG_LIGHT", "PARKING_LIGHT"},
        "interior lighting lexical boundary incomplete",
    )

    family_ids = {item["family_id"] for item in final["capability_families"]}
    family_members = [intent_id for family in final["capability_families"] for intent_id in family["intents"]]
    semantic_groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    unresolved: list[str] = []
    slot_overlap: list[str] = []
    machine_errors: list[str] = []
    invalid_modes: list[str] = []
    for name, values in final["mode_contracts"].items():
        if not isinstance(values, list):
            invalid_modes.append(f"{name}:not_list")
        else:
            invalid_modes.extend(f"{name}[{index}]" for index, value in enumerate(values) if isinstance(value, bool) or not isinstance(value, str))
    for item in final_intents:
        intent_id = item["intent_id"]
        semantic_groups[(item["canonical_action"], item["canonical_target"], item["control_attribute"])].append(intent_id)
        for field in ("intent_id", "canonical_action", "canonical_target", "control_attribute"):
            if not isinstance(item.get(field), str) or not MACHINE_ID_RE.fullmatch(item[field]):
                machine_errors.append(f"{intent_id}.{field}")
        overlap = set(item.get("required_slots", [])) & set(item.get("optional_slots", []))
        if overlap:
            slot_overlap.append(f"{intent_id}:{sorted(overlap)}")
        if item.get("value_contract") not in (None, "NONE") and item.get("value_contract") not in contracts:
            unresolved.append(f"{intent_id}.value_contract")
        if item.get("mode_contract") and item.get("mode_contract") not in final["mode_contracts"]:
            unresolved.append(f"{intent_id}.mode_contract")
        if item.get("direction_contract") and item.get("direction_contract") not in final["direction_contracts"]:
            unresolved.append(f"{intent_id}.direction_contract")
        if item.get("conditional_slot_contract") and item.get("conditional_slot_contract") not in final["conditional_slot_contracts"]:
            unresolved.append(f"{intent_id}.conditional_slot_contract")
        if item.get("capability_family") not in family_ids:
            unresolved.append(f"{intent_id}.capability_family")
    collisions = {key: ids for key, ids in semantic_groups.items() if len(ids) > 1}
    check("MACHINE_IDS", not machine_errors, f"invalid machine IDs: {machine_errors}")
    check("SEMANTIC_KEY_UNIQUE", not collisions, f"action+target+attribute collisions: {collisions}")
    check("CONTRACT_REFERENCES", not unresolved, f"unresolved references: {unresolved}")
    check("SLOT_DISJOINT", not slot_overlap, f"required/optional overlap: {slot_overlap}")
    check("FAMILY_COVERAGE", Counter(family_members) == Counter(final_ids), "capability family coverage is not one-to-one")
    check("MODE_ENUM_STRINGS", not invalid_modes, f"invalid MODE values: {invalid_modes}")

    ontology = final["semantic_ontology"]
    check("ONTOLOGY_ACTIONS", ontology.get("canonical_actions") == sorted({item["canonical_action"] for item in final_intents}), "action ontology incomplete")
    check("ONTOLOGY_TARGETS", ontology.get("canonical_targets") == sorted({item["canonical_target"] for item in final_intents}), "target ontology incomplete")
    check("ONTOLOGY_ATTRIBUTES", ontology.get("control_attributes") == sorted({item["control_attribute"] for item in final_intents}), "attribute ontology incomplete")

    formal_ids = [item["intent_id"] for item in formal_final]
    known_ids = [item["intent_id"] for item in final_intents if item.get("user_voice_scope_status") == "KNOWN_UNSUPPORTED_CONTROL"]
    origins = Counter(item["capability_origin"] for item in final_intents)
    by_id = final_by_id
    project_family_count = sum(
        bool(family["intents"])
        and all(by_id[intent_id]["capability_origin"] == "PROJECT_NATIVE" for intent_id in family["intents"])
        for family in final["capability_families"]
    )
    expected_stats = {
        "intent_count": len(final_intents),
        "semantic_intent_count": len(final_intents),
        "formal_user_voice_intent_count": len(formal_ids),
        "known_unsupported_control_intent_count": len(known_ids),
        "project_native_intent_count": origins["PROJECT_NATIVE"],
        "vss_derived_intent_count": origins["VSS"] + origins["VSS_AND_PROJECT"],
        "capability_family_count": len(final["capability_families"]),
        "project_native_family_count": project_family_count,
        "legacy_test_only_intent_count": len(final.get("legacy_test_only", [])),
    }
    check("STATISTICS", all(final["statistics"].get(key) == value for key, value in expected_stats.items()), f"statistics mismatch: {expected_stats}")
    check("FORMAL_PROJECTION", final.get("formal_user_voice_intent_ids") == formal_ids, "formal projection mismatch")
    check("KNOWN_PROJECTION", final.get("known_unsupported_control_intent_ids") == known_ids, "known projection mismatch")

    return {
        "status": "PASS" if not errors else "FAIL",
        "registry_version": final.get("registry_version"),
        "r3_sha256": r3_hash,
        "core_sha256": core_hash,
        "full_sha256": full_hash,
        "final_sha256": final_hash,
        "metrics": {
            "INTENT_COUNT": len(final_intents),
            "FORMAL_USER_VOICE_INTENT_COUNT": len(formal_ids),
            "KNOWN_UNSUPPORTED_CONTROL_INTENT_COUNT": len(known_ids),
            "PROJECT_NATIVE_INTENT_COUNT": origins["PROJECT_NATIVE"],
            "CAPABILITY_FAMILY_COUNT": len(final["capability_families"]),
            "LEGACY_TEST_ONLY_INTENT_COUNT": len(final.get("legacy_test_only", [])),
            "APPROVED_NEW_INTENT_COUNT": len(APPROVED_NEW_INTENT_IDS),
            "SEMANTIC_COLLISION_COUNT": len(collisions),
            "UNRESOLVED_CONTRACT_REFERENCE_COUNT": len(unresolved),
            "SLOT_INTERSECTION_COUNT": len(slot_overlap),
            "INVALID_MODE_ENUM_COUNT": len(invalid_modes),
            "AREA_PENDING_FAMILY_COUNT": len(expected_pending),
            "CAMERA_ACTION_PENDING_SAMPLE_COUNT": evidence["camera_mode_evidence"]["camera_action_pending"]["unique_sample_count"],
        },
        "approved_new_intent_ids": APPROVED_NEW_INTENT_IDS,
        "approved_new_intent_evidence_counts": evidence_counts,
        "family_area_union": {family: evidence["family_area_evidence"][family]["allowed_areas"] for family in AREA_FAMILIES},
        "media_modes": media_modes,
        "camera_modes": camera_modes,
        "checks": checks,
        "errors": errors,
    }


def main() -> int:
    try:
        result = validate()
    except (OSError, ValueError, KeyError, RuntimeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
