"""Validate the reopened SYS-014 formal intent registry semantic contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data/nlu/spec/intent_registry_draft.yaml"
DEFAULT_RUNTIME_SUPPORT = ROOT / "data/nlu/spec/intent_runtime_support.yaml"
DEFAULT_ANNOTATION_SCHEMA = ROOT / "data/nlu/spec/annotation_schema.json"
DEFAULT_VSS_AUDIT = ROOT / "data/nlu/spec/audits/approved44_intent_expansion_audit.json"
DEFAULT_VSS_ACTUATORS = ROOT / "data/standards/vss/6.0/generated/vss_actuators_normalized.json"
DEFAULT_FREEZE_MANIFEST = ROOT / "data/nlu/spec/frozen/full_registry_semantic_freeze_manifest.json"
DEFAULT_R1_SNAPSHOT = ROOT / "data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml"

EXPECTED_INTENT_COUNT = 93
EXPECTED_VSS_DERIVED_COUNT = 85
EXPECTED_PROJECT_NATIVE_COUNT = 8
EXPECTED_OLD_SHA256 = "0127af1d64b33a9e517537ccd458905fcc6af3414cc70701fc362474a4ec2739"
EXPECTED_R1_SHA256 = "b9b5e7dbe421f48e7d9c39b99e6776bb320edb15c763b26e3a4b3bbebba08764"
EXPECTED_REGISTRY_VERSION = "sys-014-semantic-hardening-r2"
MACHINE_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
RUNTIME_FIELDS = {
    "current_semantic_support",
    "current_evidence_support",
    "current_authorization_support",
    "current_execution_support",
}
SUPPORT_FIELDS = {
    "semantic_support",
    "evidence_support",
    "authorization_support",
    "execution_support",
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append_error(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def validate(
    registry_path: Path = DEFAULT_REGISTRY,
    runtime_support_path: Path = DEFAULT_RUNTIME_SUPPORT,
    annotation_schema_path: Path = DEFAULT_ANNOTATION_SCHEMA,
    vss_audit_path: Path = DEFAULT_VSS_AUDIT,
    vss_actuators_path: Path = DEFAULT_VSS_ACTUATORS,
    freeze_manifest_path: Path = DEFAULT_FREEZE_MANIFEST,
    r1_snapshot_path: Path = DEFAULT_R1_SNAPSHOT,
) -> dict[str, Any]:
    errors: list[str] = []
    registry = load_yaml(registry_path)
    runtime_support = load_yaml(runtime_support_path)
    annotation_schema = json.loads(annotation_schema_path.read_text(encoding="utf-8"))
    vss_audit = json.loads(vss_audit_path.read_text(encoding="utf-8"))
    vss_actuators = json.loads(vss_actuators_path.read_text(encoding="utf-8"))
    freeze_manifest = json.loads(freeze_manifest_path.read_text(encoding="utf-8"))
    r1_snapshot = load_yaml(r1_snapshot_path)

    intents = registry.get("intents")
    if not isinstance(intents, list):
        intents = []
        errors.append("registry.intents must be a list")
    ids = [item.get("intent_id") for item in intents if isinstance(item, dict)]
    r1_ids = [
        item.get("intent_id")
        for item in r1_snapshot.get("intents", [])
        if isinstance(item, dict)
    ]
    id_counts = Counter(ids)
    duplicate_ids = sorted(str(intent_id) for intent_id, count in id_counts.items() if count > 1)
    append_error(errors, len(intents) == EXPECTED_INTENT_COUNT, f"intent count must be {EXPECTED_INTENT_COUNT}")
    append_error(errors, len(ids) == len(set(ids)), f"duplicate intent IDs: {duplicate_ids}")
    append_error(errors, ids == r1_ids, "formal intent IDs/order differ from the protected R1 snapshot")
    append_error(errors, "HEADLIGHT_ON" not in ids, "HEADLIGHT_ON must not be a formal intent")
    append_error(errors, "HEADLIGHT_OFF" not in ids, "HEADLIGHT_OFF must not be a formal intent")
    append_error(errors, "HEADLIGHT_SET_MODE" in ids, "HEADLIGHT_SET_MODE must exist")

    value_contracts = registry.get("value_contracts", {})
    mode_contracts = registry.get("mode_contracts", {})
    direction_contracts = registry.get("direction_contracts", {})
    conditional_contracts = registry.get("conditional_slot_contracts", {})
    value_mapping_contracts = registry.get("value_mapping_contracts", {})
    area_catalog = registry.get("area_catalog", {})
    known_areas = set(area_catalog)
    value_language_semantics = registry.get("value_language_semantics", {})
    area_semantics = registry.get("area_semantics", {})
    allowed_capability_slots = set(registry.get("enums", {}).get("capability_slot_type", []))
    annotation_slots = set(registry.get("enums", {}).get("annotation_slot_type", []))
    append_error(errors, allowed_capability_slots == {"AREA", "VALUE", "DIRECTION", "MODE"}, "capability slot enum must exclude NEGATION")
    append_error(errors, "NEGATION" in annotation_slots, "annotation slot enum must retain NEGATION")

    expected_value_forms = {
        "ABSOLUTE_TARGET",
        "EXPLICIT_RELATIVE_DELTA",
        "RELATIVE_SMALL",
        "PARTIAL_UNSPECIFIED",
    }
    actual_value_forms = set(value_language_semantics.get("forms", {}))
    append_error(errors, actual_value_forms == expected_value_forms, "global VALUE language forms are incomplete")
    continuous_contracts = set(value_language_semantics.get("continuous_numeric_contracts", []))
    numeric_value_contracts = {
        name for name, contract in value_contracts.items() if contract.get("allowed") is True
    }
    append_error(
        errors,
        continuous_contracts == numeric_value_contracts,
        "global VALUE semantics must cover every numeric value contract exactly once",
    )
    append_error(
        errors,
        all("RELATIVE_STEP" not in contract.get("enum_values", []) for contract in value_contracts.values()),
        "legacy RELATIVE_STEP enum must be replaced by the global RELATIVE_SMALL form",
    )
    half_rule = value_language_semantics.get("deterministic_lexical_normalization", {}).get(
        "HALF_FOR_PERCENT_CONTRACT", {}
    )
    append_error(errors, half_rule.get("canonical_value") == 50, "percent HALF must normalize to 50")
    relative_small = value_language_semantics.get("forms", {}).get("RELATIVE_SMALL", {})
    append_error(
        errors,
        relative_small.get("resolution_status") == "INCOMPLETE_NEEDS_VEHICLE_PARAMETERIZATION",
        "RELATIVE_SMALL must remain incomplete pending vehicle parameterization",
    )
    append_error(
        errors,
        set(relative_small.get("prohibited_fixed_conversions", [])) >= {"5%", "10%", "FIXED_MILLIMETERS", "FIXED_DEGREES"},
        "RELATIVE_SMALL must prohibit fixed physical conversions",
    )
    partial_unspecified = value_language_semantics.get("forms", {}).get("PARTIAL_UNSPECIFIED", {})
    append_error(
        errors,
        partial_unspecified.get("prohibited_normalization") == "50%",
        "PARTIAL_UNSPECIFIED must not normalize to 50%",
    )
    direction_only_rule = value_language_semantics.get("parameter_completeness_rules", {}).get(
        "DIRECTION_WITHOUT_VALUE_FOR_NUMERIC_CONTROL", {}
    )
    append_error(
        errors,
        direction_only_rule.get("intent_recognition_allowed") is True
        and direction_only_rule.get("parameter_resolution_status") == "INCOMPLETE_MISSING_MAGNITUDE"
        and direction_only_rule.get("default_physical_step_prohibited") is True,
        "direction-only numeric controls must remain recognized but parameter-incomplete",
    )

    expected_atomic_areas = {
        "LEFT_FRONT",
        "RIGHT_FRONT",
        "LEFT_REAR",
        "RIGHT_REAR",
        "MIDDLE_FRONT",
        "MIDDLE_REAR",
        "FRONT",
        "REAR",
    }
    expected_composite_areas = {"FRONT_ROW", "REAR_ROW", "LEFT_SIDE", "RIGHT_SIDE", "ALL"}
    append_error(
        errors,
        {key for key, value in area_catalog.items() if value.get("area_type") == "ATOMIC"} == expected_atomic_areas,
        "atomic AREA catalog is invalid",
    )
    append_error(
        errors,
        {key for key, value in area_catalog.items() if value.get("area_type") == "COMPOSITE"} == expected_composite_areas,
        "composite AREA catalog is invalid",
    )
    missing_area = area_semantics.get("missing_area", {})
    append_error(errors, missing_area.get("representation") == "UNRESOLVED", "missing AREA must remain UNRESOLVED")
    append_error(
        errors,
        set(missing_area.get("implicit_defaults_prohibited", []))
        == {"ALL", "DRIVER_POSITION", "SPEAKER_POSITION", "NEAREST_POSITION", "CONTEXT_INFERENCE"},
        "missing AREA implicit default prohibitions are incomplete",
    )
    append_error(
        errors,
        area_semantics.get("composite_area_policy", {}).get("explicit_expression_required") is True,
        "composite AREA must require explicit user expression",
    )

    missing_value_contracts: list[str] = []
    missing_mode_contracts: list[str] = []
    missing_direction_contracts: list[str] = []
    missing_value_mapping_contracts: list[str] = []
    unknown_area_references: list[str] = []
    capability_negation_slots: list[str] = []
    semantic_groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    current_status_entries: list[str] = []
    invalid_origins: list[str] = []
    invalid_machine_ids: list[str] = []
    known_origins = set(registry.get("enums", {}).get("capability_origin", []))

    for item in intents:
        if not isinstance(item, dict):
            errors.append("every intent entry must be a mapping")
            continue
        intent_id = item.get("intent_id", "<missing>")
        for field in ("canonical_action", "canonical_target", "control_attribute"):
            value = item.get(field)
            if not isinstance(value, str) or not MACHINE_ID_RE.fullmatch(value):
                invalid_machine_ids.append(f"{intent_id}.{field}={value!r}")
        if all(isinstance(item.get(field), str) for field in ("canonical_action", "canonical_target", "control_attribute")):
            semantic_groups[(item["canonical_action"], item["canonical_target"], item["control_attribute"])].append(intent_id)

        required = item.get("required_slots", [])
        optional = item.get("optional_slots", [])
        if not isinstance(required, list) or not isinstance(optional, list):
            errors.append(f"{intent_id}: required_slots and optional_slots must be lists")
            continue
        slots = required + optional
        for area in item.get("allowed_areas", []):
            if area not in known_areas:
                unknown_area_references.append(f"{intent_id}:{area}")
        unknown_slots = sorted(set(slots) - allowed_capability_slots)
        if unknown_slots:
            errors.append(f"{intent_id}: unknown capability slots {unknown_slots}")
        if "NEGATION" in slots:
            capability_negation_slots.append(intent_id)
        if "VALUE" in slots:
            contract = item.get("value_contract")
            if contract == "NONE" or contract not in value_contracts:
                missing_value_contracts.append(intent_id)
        if "MODE" in slots:
            contract = item.get("mode_contract")
            if not contract or contract not in mode_contracts:
                missing_mode_contracts.append(intent_id)
        if "DIRECTION" in slots:
            contract = item.get("direction_contract")
            if not contract or contract not in direction_contracts:
                missing_direction_contracts.append(intent_id)
        conditional = item.get("conditional_slot_contract")
        if conditional and conditional not in conditional_contracts:
            errors.append(f"{intent_id}: unresolved conditional_slot_contract {conditional}")
        value_mapping = item.get("value_mapping_contract")
        if value_mapping and value_mapping not in value_mapping_contracts:
            missing_value_mapping_contracts.append(intent_id)
        if RUNTIME_FIELDS.intersection(item):
            current_status_entries.append(intent_id)
        if item.get("capability_origin") not in known_origins:
            invalid_origins.append(intent_id)

    append_error(errors, not invalid_machine_ids, f"invalid machine identifiers: {invalid_machine_ids}")
    append_error(errors, not missing_value_contracts, f"missing VALUE contracts: {missing_value_contracts}")
    append_error(errors, not missing_mode_contracts, f"missing MODE contracts: {missing_mode_contracts}")
    append_error(errors, not missing_direction_contracts, f"missing DIRECTION contracts: {missing_direction_contracts}")
    append_error(errors, not missing_value_mapping_contracts, f"missing value mapping contracts: {missing_value_mapping_contracts}")
    append_error(errors, not unknown_area_references, f"unknown AREA references: {unknown_area_references}")
    append_error(errors, not capability_negation_slots, f"NEGATION remains a capability slot: {capability_negation_slots}")
    append_error(errors, not current_status_entries, f"runtime support remains in semantic entries: {current_status_entries}")
    append_error(errors, not invalid_origins, f"invalid capability origins: {invalid_origins}")

    collisions = {"|".join(key): value for key, value in semantic_groups.items() if len(value) > 1}
    append_error(errors, not collisions, f"semantic key collisions: {collisions}")
    ontology = registry.get("semantic_ontology", {})
    used_actions = sorted({item.get("canonical_action") for item in intents})
    used_targets = sorted({item.get("canonical_target") for item in intents})
    used_attributes = sorted({item.get("control_attribute") for item in intents})
    append_error(errors, ontology.get("canonical_actions") == used_actions, "declared action ontology does not match used actions")
    append_error(errors, ontology.get("canonical_targets") == used_targets, "declared target ontology does not match used targets")
    append_error(errors, ontology.get("control_attributes") == used_attributes, "declared attribute ontology does not match used attributes")
    append_error(errors, ontology.get("semantic_key_fields") == ["canonical_action", "canonical_target", "control_attribute"], "semantic key fields are invalid")

    origins = Counter(item.get("capability_origin") for item in intents)
    vss_derived_count = origins["VSS"] + origins["VSS_AND_PROJECT"]
    append_error(errors, vss_derived_count == EXPECTED_VSS_DERIVED_COUNT, f"VSS-derived count must be {EXPECTED_VSS_DERIVED_COUNT}")
    append_error(errors, origins["PROJECT_NATIVE"] == EXPECTED_PROJECT_NATIVE_COUNT, f"project-native count must be {EXPECTED_PROJECT_NATIVE_COUNT}")

    families = registry.get("capability_families", [])
    family_ids = {family.get("family_id") for family in families if isinstance(family, dict)}
    family_intents = [intent_id for family in families if isinstance(family, dict) for intent_id in family.get("intents", [])]
    append_error(errors, Counter(family_intents) == Counter(ids), "capability family intent coverage must be exactly one-to-one")
    append_error(errors, all(item.get("capability_family") in family_ids for item in intents), "intent references an unknown capability family")

    by_id = {item.get("intent_id"): item for item in intents}
    r1_by_id = {
        item.get("intent_id"): item
        for item in r1_snapshot.get("intents", [])
        if isinstance(item, dict)
    }
    approved_rows = vss_audit.get("capability_rows", [])
    approved_by_id = {row.get("approved_capability_id"): row for row in approved_rows}
    generated_paths = {row.get("vss_path") for row in vss_actuators.get("records", [])}
    unresolved_capability_refs: list[str] = []
    unresolved_vss_paths: list[str] = []
    for item in intents:
        for capability_id in item.get("vss_capability_ids", []):
            if capability_id not in approved_by_id:
                unresolved_capability_refs.append(f"{item.get('intent_id')}:{capability_id}")
    for capability_id, row in approved_by_id.items():
        for path in row.get("VSS actuator paths", []):
            if path not in generated_paths:
                unresolved_vss_paths.append(f"{capability_id}:{path}")
    append_error(errors, not unresolved_capability_refs, f"unresolved capability references: {unresolved_capability_refs}")
    append_error(errors, not unresolved_vss_paths, f"unresolved VSS paths: {unresolved_vss_paths}")

    middle_area_vss_mismatches: list[str] = []
    for item in intents:
        intent_id = str(item.get("intent_id"))
        areas = set(item.get("allowed_areas", []))
        for area, marker in (("MIDDLE_FRONT", ".Row1.Middle."), ("MIDDLE_REAR", ".Row2.Middle.")):
            if area not in areas:
                continue
            capability_paths = [
                path
                for capability_id in item.get("vss_capability_ids", [])
                for path in approved_by_id.get(capability_id, {}).get("VSS actuator paths", [])
            ]
            if item.get("canonical_target") != "SEAT" or not any(marker in path for path in capability_paths):
                middle_area_vss_mismatches.append(f"{intent_id}:{area}")
    expected_middle_seat_intents = {
        "SEAT_LONGITUDINAL_SET_POSITION",
        "SEAT_TILT_SET_ANGLE",
        "SEAT_BACKREST_SET_ANGLE",
        "SEAT_HEIGHT_SET_POSITION",
        "SEAT_LUMBAR_SET_HEIGHT",
        "SEAT_LUMBAR_SET_SUPPORT",
    }
    for intent_id in expected_middle_seat_intents:
        append_error(
            errors,
            {"MIDDLE_FRONT", "MIDDLE_REAR"} <= set(by_id.get(intent_id, {}).get("allowed_areas", [])),
            f"{intent_id}: missing VSS-backed middle-seat AREA",
        )
    append_error(errors, not middle_area_vss_mismatches, f"middle-seat AREA lacks VSS actuator: {middle_area_vss_mismatches}")

    light_contracts = {
        "HEADLIGHT_SET_MODE": ("HEADLIGHT", "MODE", "BODY_MAIN_LIGHT_MODE"),
        "HAZARD_LIGHT_ON": ("HAZARD_LIGHT", "STATE", "BODY_HAZARD_LIGHT"),
        "HAZARD_LIGHT_OFF": ("HAZARD_LIGHT", "STATE", "BODY_HAZARD_LIGHT"),
        "TURN_INDICATOR_ON": ("TURN_INDICATOR", "STATE", "BODY_TURN_INDICATOR"),
        "TURN_INDICATOR_OFF": ("TURN_INDICATOR", "STATE", "BODY_TURN_INDICATOR"),
        "LOW_BEAM_ON": ("LOW_BEAM", "STATE", "BODY_LOW_BEAM"),
        "LOW_BEAM_OFF": ("LOW_BEAM", "STATE", "BODY_LOW_BEAM"),
        "HIGH_BEAM_ON": ("HIGH_BEAM", "STATE", "BODY_HIGH_BEAM"),
        "HIGH_BEAM_OFF": ("HIGH_BEAM", "STATE", "BODY_HIGH_BEAM"),
        "FOG_LIGHT_ON": ("FOG_LIGHT", "STATE", "BODY_FOG_LIGHT"),
        "FOG_LIGHT_OFF": ("FOG_LIGHT", "STATE", "BODY_FOG_LIGHT"),
        "PARKING_LIGHT_ON": ("PARKING_LIGHT", "STATE", "BODY_PARKING_LIGHT"),
        "PARKING_LIGHT_OFF": ("PARKING_LIGHT", "STATE", "BODY_PARKING_LIGHT"),
    }
    changed_light_sources: list[str] = []
    for intent_id, (target, attribute, capability_id) in light_contracts.items():
        item = by_id.get(intent_id, {})
        append_error(errors, item.get("canonical_target") == target, f"{intent_id}: light target is not split")
        append_error(errors, item.get("control_attribute") == attribute, f"{intent_id}: light attribute is invalid")
        append_error(errors, item.get("capability_family") == capability_id, f"{intent_id}: light capability family changed")
        append_error(errors, item.get("vss_capability_ids") == [capability_id], f"{intent_id}: light VSS capability mapping changed")
        old_item = r1_by_id.get(intent_id, {})
        if (
            item.get("capability_family") != old_item.get("capability_family")
            or item.get("vss_capability_ids") != old_item.get("vss_capability_ids")
        ):
            changed_light_sources.append(intent_id)
    append_error(errors, not changed_light_sources, f"light VSS sources changed: {changed_light_sources}")

    runtime_entries = runtime_support.get("intents", {})
    runtime_ids = set(runtime_entries) if isinstance(runtime_entries, dict) else set()
    append_error(errors, runtime_ids == set(ids), "runtime support IDs must exactly match formal intent IDs")
    append_error(errors, runtime_support.get("intent_count") == EXPECTED_INTENT_COUNT, "runtime support intent_count must be 93")
    allowed_statuses = set(runtime_support.get("support_status", []))
    for intent_id, statuses in runtime_entries.items() if isinstance(runtime_entries, dict) else []:
        if set(statuses) != SUPPORT_FIELDS:
            errors.append(f"{intent_id}: runtime support fields are incomplete")
        invalid_statuses = sorted(set(statuses.values()) - allowed_statuses)
        if invalid_statuses:
            errors.append(f"{intent_id}: invalid runtime support values {invalid_statuses}")

    registry_version = registry.get("registry_version")
    append_error(errors, registry_version == EXPECTED_REGISTRY_VERSION, "registry_version must be semantic hardening R2")
    append_error(errors, runtime_support.get("registry_version") == registry_version, "runtime support registry_version mismatch")
    schema_version = annotation_schema.get("properties", {}).get("registry_version", {}).get("const")
    append_error(errors, schema_version == registry_version, "annotation schema registry_version mismatch")
    append_error(errors, registry.get("semantic_freeze_status") == "REOPENED_PENDING_REVIEW", "semantic freeze status must be reopened pending review")
    append_error(errors, registry.get("public_semantic_frame_change_required") is True, "R2 target/AREA semantics require future public frame alignment")

    gear_modes = mode_contracts.get("GEAR", [])
    gear_mapping = registry.get("mode_mapping_contracts", {}).get("GEAR_VEHICLE_SPECIFIC", {})
    append_error(errors, "R" in gear_modes, "GEAR mode contract must include generic R")
    append_error(errors, "R" in gear_mapping.get("canonical_modes", []), "GEAR mapping contract must include generic R")
    append_error(errors, gear_mapping.get("vss_code_rules", {}).get("R") == "VEHICLE_CAPABILITY_MAPPING_REQUIRED", "generic R must defer physical mapping")

    brake = by_id.get("BRAKE", {})
    emergency_brake = by_id.get("EMERGENCY_BRAKE", {})
    append_error(errors, brake.get("canonical_action") == "BRAKE", "BRAKE action must be BRAKE")
    append_error(errors, emergency_brake.get("canonical_action") == "BRAKE", "EMERGENCY_BRAKE action must be BRAKE")
    append_error(errors, brake.get("control_attribute") != emergency_brake.get("control_attribute"), "normal and emergency braking must be distinguishable")
    sunroof = by_id.get("SUNROOF_SET_TILT", {})
    append_error(errors, sunroof.get("required_slots") == ["DIRECTION"], "SUNROOF_SET_TILT must require DIRECTION")
    append_error(errors, sunroof.get("direction_contract") == "SUNROOF_TILT_UP_DOWN", "SUNROOF_SET_TILT direction contract is invalid")
    append_error(errors, "mode_contract" not in sunroof, "SUNROOF_SET_TILT must not depend on MODE")
    append_error(errors, sunroof.get("value_contract") == "NONE", "SUNROOF_SET_TILT must not use VALUE")
    append_error(errors, sunroof.get("control_attribute") == "TILT_OPERATION", "SUNROOF_SET_TILT must use a discrete operation attribute")
    append_error(errors, "角" not in str(sunroof.get("chinese_name", "")), "SUNROOF_SET_TILT name must not imply an angle value")

    for intent_id in ("STEERING_WHEEL_SET_EXTENSION", "STEERING_WHEEL_SET_TILT"):
        item = by_id.get(intent_id, {})
        append_error(errors, item.get("value_contract") == "PERCENT_0_100_OPTIONAL", f"{intent_id}: VALUE must allow semantic-only relative adjustment")
        append_error(errors, item.get("required_slots") == [], f"{intent_id}: VALUE must not be unconditionally required")
        append_error(errors, set(item.get("optional_slots", [])) == {"VALUE", "DIRECTION"}, f"{intent_id}: optional VALUE/DIRECTION contract is invalid")
        append_error(errors, item.get("conditional_slot_contract") == "VALUE_OR_DIRECTION", f"{intent_id}: must recognize VALUE or DIRECTION")

    wiper_sensitivity = by_id.get("WIPER_SET_SENSITIVITY", {})
    append_error(
        errors,
        wiper_sensitivity.get("mode_contract") == "WIPER_SENSITIVITY_APPLICABLE_MODE",
        "WIPER_SET_SENSITIVITY must use the restricted mode contract",
    )
    append_error(
        errors,
        mode_contracts.get("WIPER_SENSITIVITY_APPLICABLE_MODE") == ["INTERVAL", "RAIN_SENSOR"],
        "wiper sensitivity modes must be INTERVAL/RAIN_SENSOR only",
    )
    append_error(
        errors,
        mode_contracts.get("WIPER") == ["OFF", "SLOW", "MEDIUM", "FAST", "INTERVAL", "RAIN_SENSOR"],
        "WIPER_SET_MODE must retain the full VSS mode contract",
    )

    door_position = by_id.get("DOOR_SET_POSITION", {})
    window_position = by_id.get("WINDOW_SET_POSITION", {})
    append_error(
        errors,
        set(door_position.get("allowed_areas", [])) == {"LEFT_FRONT", "RIGHT_FRONT", "LEFT_REAR", "RIGHT_REAR"},
        "DOOR_SET_POSITION must remain restricted to four atomic doors",
    )
    append_error(
        errors,
        door_position.get("composite_area_policy") == "PROHIBITED_CONSERVATIVE_SAFETY_CONTRACT",
        "DOOR_SET_POSITION conservative composite-area safety contract is missing",
    )
    append_error(
        errors,
        set(window_position.get("allowed_areas", []))
        == {"LEFT_FRONT", "RIGHT_FRONT", "LEFT_REAR", "RIGHT_REAR", "FRONT_ROW", "REAR_ROW", "LEFT_SIDE", "RIGHT_SIDE", "ALL"},
        "WINDOW_SET_POSITION approved explicit composite areas changed",
    )
    for intent_id, item in (("DOOR_SET_POSITION", door_position), ("WINDOW_SET_POSITION", window_position)):
        append_error(
            errors,
            item.get("area_resolution_policy") == "EXPLICIT_ONLY_UNRESOLVED_IF_MISSING",
            f"{intent_id}: missing AREA must remain unresolved",
        )

    for intent_id in ("SEAT_LUMBAR_SET_HEIGHT", "SEAT_LUMBAR_SET_SUPPORT"):
        areas = set(by_id.get(intent_id, {}).get("allowed_areas", []))
        append_error(errors, not ({"FRONT_ROW", "REAR_ROW"} & areas), f"{intent_id}: unapproved row composite AREA present")

    torque = by_id.get("TORQUE_DISTRIBUTION_SET", {})
    torque_mapping = value_mapping_contracts.get("TORQUE_DISTRIBUTION_SIGNED_PERCENT", {})
    append_error(errors, torque.get("value_contract") == "PERCENT_0_100_REQUIRED", "torque user VALUE must be a nonnegative magnitude")
    append_error(errors, torque.get("direction_contract") == "TORQUE_DISTRIBUTION_FRONT_REAR", "torque direction contract is missing")
    append_error(errors, torque.get("conditional_slot_contract") == "TORQUE_DIRECTION_FOR_NONZERO_VALUE", "torque nonzero direction rule is missing")
    append_error(errors, torque.get("value_mapping_contract") == "TORQUE_DISTRIBUTION_SIGNED_PERCENT", "torque signed VSS mapping is missing")
    native_torque_domain = torque_mapping.get("vehicle_native_domain", {})
    append_error(
        errors,
        native_torque_domain.get("min") == -100
        and native_torque_domain.get("max") == 100
        and native_torque_domain.get("negative_semantics") == "FRONT_BIAS"
        and native_torque_domain.get("positive_semantics") == "REAR_BIAS",
        "torque native signed-percent semantics are invalid",
    )
    for intent_id in ("DEFROST_ON", "DEFROST_OFF"):
        item = by_id.get(intent_id, {})
        append_error(errors, item.get("canonical_target") == "WINDSHIELD", f"{intent_id} target must be WINDSHIELD")
        append_error(errors, set(item.get("allowed_areas", [])) == {"FRONT", "REAR", "ALL"}, f"{intent_id} AREA contract must cover front/rear/all")
    defrost_paths = set(approved_by_id.get("CABIN_HVAC_DEFROST", {}).get("VSS actuator paths", []))
    append_error(errors, any("IsFrontDefrosterActive" in path for path in defrost_paths), "DEFROST source lacks front actuator")
    append_error(errors, any("IsRearDefrosterActive" in path for path in defrost_paths), "DEFROST source lacks rear actuator")

    old_sha = freeze_manifest.get("registry_sha256")
    r1_sha = sha256_file(r1_snapshot_path)
    new_sha = sha256_file(registry_path)
    append_error(errors, old_sha == EXPECTED_OLD_SHA256, "historical freeze manifest SHA changed")
    append_error(errors, r1_sha == EXPECTED_R1_SHA256, "protected R1 registry snapshot SHA changed")
    append_error(errors, new_sha != old_sha, "reopened registry SHA must differ from historical freeze")
    append_error(errors, new_sha != r1_sha, "R2 registry SHA must differ from protected R1")

    metrics = {
        "INTENT_COUNT": len(intents),
        "SEMANTIC_KEY_UNIQUE_COUNT": len(semantic_groups),
        "SEMANTIC_KEY_COLLISION_COUNT": len(collisions),
        "MISSING_VALUE_CONTRACT_COUNT": len(missing_value_contracts),
        "MISSING_DIRECTION_CONTRACT_COUNT": len(missing_direction_contracts),
        "MISSING_MODE_CONTRACT_COUNT": len(missing_mode_contracts),
        "MISSING_VALUE_MAPPING_CONTRACT_COUNT": len(missing_value_mapping_contracts),
        "UNKNOWN_AREA_REFERENCE_COUNT": len(unknown_area_references),
        "MIDDLE_AREA_VSS_MISMATCH_COUNT": len(middle_area_vss_mismatches),
        "LIGHT_SOURCE_CHANGED_COUNT": len(changed_light_sources),
        "TORQUE_DISTRIBUTION_SEMANTIC_BLOCKER_COUNT": 0,
        "CAPABILITY_NEGATION_SLOT_COUNT": len(capability_negation_slots),
        "RUNTIME_SUPPORT_COVERAGE_COUNT": len(runtime_ids.intersection(ids)),
        "UNRESOLVED_SEMANTIC_BLOCKER_COUNT": len(errors),
        "OLD_REGISTRY_SHA256": old_sha,
        "R1_REGISTRY_SHA256": r1_sha,
        "NEW_REGISTRY_SHA256": new_sha,
        "SEMANTIC_FREEZE_STATUS": registry.get("semantic_freeze_status"),
    }
    return {
        "status": "PASS" if not errors else "FAIL",
        "metrics": metrics,
        "collisions": collisions,
        "actions": used_actions,
        "targets": used_targets,
        "attributes": used_attributes,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--runtime-support", type=Path, default=DEFAULT_RUNTIME_SUPPORT)
    args = parser.parse_args()
    try:
        result = validate(registry_path=args.registry, runtime_support_path=args.runtime_support)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
