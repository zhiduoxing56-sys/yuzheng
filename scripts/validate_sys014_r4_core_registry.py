"""Validate the SYS-014 Full NLU R4 core draft against its immutable R3 parent."""

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
R3_PATH = ROOT / "data/nlu/spec/intent_registry_r3.yaml"
R4_PATH = ROOT / "data/nlu/spec/intent_registry_r4_core_draft.yaml"
R3_VERSION = "sys-014-semantic-hardening-r3"
R4_VERSION = "sys-014-semantic-hardening-r4-core-draft"
R4_STATUS = "DRAFT_PENDING_KNOWN_UNSUPPORTED_EXPANSION"
R3_SHA256 = "c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06"
FORMAL_STATUS = "FORMAL_EXECUTABLE"
KNOWN_STATUS = "KNOWN_UNSUPPORTED_CONTROL"
MACHINE_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")

ALLOWED_CHANGED_PATHS = {
    "document_status",
    "registry_version",
    "modified_date",
    "semantic_freeze_status",
    "parent_registry",
    "annotation_guidance",
    "value_contracts.PERCENT_PARTIAL_1_99_REQUIRED",
    "value_contracts.SPEED_DELTA_OPTIONAL",
    "value_language_semantics.continuous_numeric_contracts",
    "mode_contracts.CRUISE_GAP_LEVEL",
    "mode_contracts.HEADLIGHT",
    "mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH",
    "intents.WINDOW_SET_POSITION.value_contract",
    "intents.ACCELERATE.value_contract",
    "intents.DECELERATE.value_contract",
    "intents.TRUNK_OPEN.allowed_areas",
    "intents.TRUNK_CLOSE.allowed_areas",
    "intents.TRUNK_SET_POSITION.allowed_areas",
    "intents.TRUNK_LOCK.allowed_areas",
    "intents.TRUNK_UNLOCK.allowed_areas",
    "over_atomization_audit.parameterized_instead_of_split.WINDOW_SET_POSITION.examples",
    "over_atomization_audit.parameterized_instead_of_split.HEADLIGHT_SET_MODE.examples",
    "over_atomization_audit.parameterized_instead_of_split.HEADLIGHT_SET_MODE.restricted_alias",
    "over_atomization_audit.parameterized_instead_of_split.WIPER_SET_MODE.examples",
    "over_atomization_audit.parameterized_instead_of_split.CRUISE_SET_GAP.examples",
}
ALLOWED_CHANGED_PREFIXES = (
    "parent_registry.",
    "mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH.",
)


class StrictSafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: StrictSafeLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return value


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _keyed_list(value: list[Any]) -> tuple[str, dict[str, Any]] | None:
    if not value or not all(isinstance(item, dict) for item in value):
        return None
    for key in ("intent_id", "family_id"):
        if all(isinstance(item.get(key), str) for item in value):
            return key, {item[key]: item for item in value}
    return None


def changed_paths(before: Any, after: Any, path: str = "") -> list[str]:
    if type(before) is not type(after):
        return [path or "<root>"]
    if isinstance(before, dict):
        paths: list[str] = []
        for key in sorted(set(before) | set(after), key=str):
            child = f"{path}.{key}" if path else str(key)
            if key not in before or key not in after:
                paths.append(child)
            else:
                paths.extend(changed_paths(before[key], after[key], child))
        return paths
    if isinstance(before, list):
        before_keyed = _keyed_list(before)
        after_keyed = _keyed_list(after)
        if before_keyed and after_keyed and before_keyed[0] == after_keyed[0]:
            paths = []
            before_map = before_keyed[1]
            after_map = after_keyed[1]
            for key in sorted(set(before_map) | set(after_map)):
                child = f"{path}.{key}" if path else key
                if key not in before_map or key not in after_map:
                    paths.append(child)
                else:
                    paths.extend(changed_paths(before_map[key], after_map[key], child))
            return paths
        return [] if before == after else [path or "<root>"]
    return [] if before == after else [path or "<root>"]


def _audit_by_id(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = registry.get("over_atomization_audit", {}).get("parameterized_instead_of_split", [])
    return {item.get("intent_id"): item for item in entries if isinstance(item, dict)}


def _intent_by_id(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item.get("intent_id"): item
        for item in registry.get("intents", [])
        if isinstance(item, dict) and isinstance(item.get("intent_id"), str)
    }


def _p0_result(
    p0_id: str,
    title: str,
    before: Any,
    after: Any,
    fields: list[str],
    conditions: list[tuple[bool, str]],
) -> dict[str, Any]:
    errors = [message for condition, message in conditions if not condition]
    return {
        "p0_id": p0_id,
        "title": title,
        "before": before,
        "after": after,
        "involved_fields": fields,
        "validator_result": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def validate(
    registry_path: Path = R4_PATH,
    *,
    r3_path: Path = R3_PATH,
) -> dict[str, Any]:
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(check_id: str, condition: bool, message: str) -> None:
        checks.append({"check_id": check_id, "status": "PASS" if condition else "FAIL", "message": message})
        if not condition:
            errors.append(f"{check_id}: {message}")

    r3 = load_yaml(r3_path)
    r4 = load_yaml(registry_path)
    r3_hash = sha256_file(r3_path)
    r4_hash = sha256_file(registry_path)
    r3_intents = r3.get("intents", [])
    r4_intents = r4.get("intents", [])
    r3_ids = [item.get("intent_id") for item in r3_intents if isinstance(item, dict)]
    r4_ids = [item.get("intent_id") for item in r4_intents if isinstance(item, dict)]
    r3_by_id = _intent_by_id(r3)
    r4_by_id = _intent_by_id(r4)
    r3_audit = _audit_by_id(r3)
    r4_audit = _audit_by_id(r4)
    value_contracts = r4.get("value_contracts", {})
    mode_contracts = r4.get("mode_contracts", {})
    direction_contracts = r4.get("direction_contracts", {})
    conditional_contracts = r4.get("conditional_slot_contracts", {})
    value_mapping_contracts = r4.get("value_mapping_contracts", {})
    mode_mapping_contracts = r4.get("mode_mapping_contracts", {})
    guidance = r4.get("annotation_guidance", {})

    check("YAML_STRICT_PARSE", isinstance(r4, dict), "R4 YAML must parse to a mapping")
    check("R3_SHA256_UNCHANGED", r3_hash == R3_SHA256, f"R3 SHA256 must remain {R3_SHA256}")
    check("R3_VERSION", r3.get("registry_version") == R3_VERSION, "R3 version mismatch")
    check("R4_VERSION", r4.get("registry_version") == R4_VERSION, "R4 version mismatch")
    check("R4_STATUS", r4.get("semantic_freeze_status") == R4_STATUS, "R4 draft status mismatch")
    check("R4_OFFLINE", r4.get("runtime_loading_allowed") is False, "R4 must remain offline/not runtime-loadable")
    expected_parent = {
        "path": "data/nlu/spec/intent_registry_r3.yaml",
        "registry_version": R3_VERSION,
        "sha256": R3_SHA256,
        "inheritance_rule": "PRESERVE_ALL_R3_FIELDS_EXCEPT_APPROVED_P0_01_TO_P0_07",
    }
    check("R4_PARENT", r4.get("parent_registry") == expected_parent, "R4 parent registry contract mismatch")
    check(
        "TOP_LEVEL_COPY_COMPLETENESS",
        set(r4) == set(r3) | {"annotation_guidance"},
        "R4 top-level keys must equal R3 plus annotation_guidance",
    )

    check("INTENT_ID_ORDER", r4_ids == r3_ids, "all original 93 intent IDs and order must be retained")
    check("INTENT_COUNT", len(r4_ids) == 93, f"semantic intent count must remain 93, got {len(r4_ids)}")
    check("DUPLICATE_INTENT_IDS", len(r4_ids) == len(set(r4_ids)), "intent IDs must be unique")
    formal_ids = [item["intent_id"] for item in r4_intents if item.get("user_voice_scope_status") == FORMAL_STATUS]
    known_ids = [item["intent_id"] for item in r4_intents if item.get("user_voice_scope_status") == KNOWN_STATUS]
    check("FORMAL_COUNT", len(formal_ids) == 71, f"formal user voice intent count must remain 71, got {len(formal_ids)}")
    check("FORMAL_IDS", formal_ids == r3.get("formal_user_voice_intent_ids"), "formal user voice intent IDs changed")
    check("FORMAL_PROJECTION", r4.get("formal_user_voice_intent_ids") == formal_ids, "R4 formal projection mismatch")
    check("KNOWN_IDS", known_ids == r3.get("known_unsupported_control_intent_ids"), "known unsupported IDs changed")
    check("KNOWN_PROJECTION", r4.get("known_unsupported_control_intent_ids") == known_ids, "R4 known projection mismatch")
    r3_project_native = [item["intent_id"] for item in r3_intents if item.get("capability_origin") == "PROJECT_NATIVE"]
    r4_project_native = [item["intent_id"] for item in r4_intents if item.get("capability_origin") == "PROJECT_NATIVE"]
    check("PROJECT_NATIVE_RETAINED", r4_project_native == r3_project_native and len(r4_project_native) == 8, "PROJECT_NATIVE intents changed")

    allowed_slots = set(r4.get("enums", {}).get("capability_slot_type", []))
    semantic_groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    unresolved_contracts: list[str] = []
    slot_conflicts: list[str] = []
    invalid_machine_ids: list[str] = []
    for item in r4_intents:
        intent_id = str(item.get("intent_id"))
        for field in ("intent_id", "canonical_action", "canonical_target", "control_attribute"):
            value = item.get(field)
            if not isinstance(value, str) or not MACHINE_ID_RE.fullmatch(value):
                invalid_machine_ids.append(f"{intent_id}.{field}={value!r}")
        semantic_groups[(item.get("canonical_action"), item.get("canonical_target"), item.get("control_attribute"))].append(intent_id)
        required = item.get("required_slots", [])
        optional = item.get("optional_slots", [])
        if not isinstance(required, list) or not isinstance(optional, list):
            slot_conflicts.append(f"{intent_id}: slots are not lists")
            continue
        overlap = sorted(set(required) & set(optional))
        if overlap:
            slot_conflicts.append(f"{intent_id}: required/optional overlap={overlap}")
        slots = required + optional
        unknown_slots = sorted(set(slots) - allowed_slots)
        if unknown_slots:
            unresolved_contracts.append(f"{intent_id}:unknown_slots={unknown_slots}")
        value_contract = item.get("value_contract")
        if value_contract not in (None, "NONE") and value_contract not in value_contracts:
            unresolved_contracts.append(f"{intent_id}:value_contract={value_contract}")
        mode_contract = item.get("mode_contract")
        if mode_contract is not None and mode_contract not in mode_contracts:
            unresolved_contracts.append(f"{intent_id}:mode_contract={mode_contract}")
        direction_contract = item.get("direction_contract")
        if direction_contract is not None and direction_contract not in direction_contracts:
            unresolved_contracts.append(f"{intent_id}:direction_contract={direction_contract}")
        conditional_contract = item.get("conditional_slot_contract")
        if conditional_contract is not None and conditional_contract not in conditional_contracts:
            unresolved_contracts.append(f"{intent_id}:conditional_slot_contract={conditional_contract}")
        value_mapping = item.get("value_mapping_contract")
        if value_mapping is not None and value_mapping not in value_mapping_contracts:
            unresolved_contracts.append(f"{intent_id}:value_mapping_contract={value_mapping}")
        mode_mapping = item.get("mode_mapping_contract")
        if mode_mapping is not None and mode_mapping not in mode_mapping_contracts:
            unresolved_contracts.append(f"{intent_id}:mode_mapping_contract={mode_mapping}")

    collisions = {"|".join(map(str, key)): ids for key, ids in semantic_groups.items() if len(ids) > 1}
    check("MACHINE_IDS", not invalid_machine_ids, f"invalid machine IDs: {invalid_machine_ids}")
    check("SLOT_CONFLICTS", not slot_conflicts, f"required_slots/optional_slots conflicts: {slot_conflicts}")
    check("CONTRACT_REFERENCES", not unresolved_contracts, f"unresolved contract references: {unresolved_contracts}")
    check("SEMANTIC_KEY_UNIQUENESS", not collisions, f"semantic key collisions: {collisions}")

    bool_mode_values = [
        f"mode_contracts.{name}[{index}]"
        for name, values in mode_contracts.items()
        for index, value in enumerate(values if isinstance(values, list) else [])
        if isinstance(value, bool)
    ]
    bool_mode_examples = [
        f"over_atomization_audit.{intent_id}.examples[{index}]"
        for intent_id, item in r4_audit.items()
        if "MODE" in str(item.get("parameter", ""))
        for index, value in enumerate(item.get("examples", []))
        if isinstance(value, bool)
    ]
    non_string_mode_values = [
        f"mode_contracts.{name}[{index}]"
        for name, values in mode_contracts.items()
        for index, value in enumerate(values if isinstance(values, list) else [])
        if not isinstance(value, str)
    ]
    check("MODE_BOOL_TYPES", not bool_mode_values and not bool_mode_examples, f"boolean MODE values/examples: {bool_mode_values + bool_mode_examples}")
    check("MODE_ENUM_STRING_TYPES", not non_string_mode_values, f"non-string MODE enums: {non_string_mode_values}")

    p0_results: list[dict[str, Any]] = []
    partial_contract = value_contracts.get("PERCENT_PARTIAL_1_99_REQUIRED", {})
    window = r4_by_id.get("WINDOW_SET_POSITION", {})
    window_guidance = guidance.get("window_endpoint_routing", {})
    p0_results.append(_p0_result(
        "P0-01",
        "WINDOW endpoint uniqueness",
        {"value_contract": r3_by_id.get("WINDOW_SET_POSITION", {}).get("value_contract"), "audit_examples": r3_audit.get("WINDOW_SET_POSITION", {}).get("examples")},
        {"value_contract": window.get("value_contract"), "contract": partial_contract, "audit_examples": r4_audit.get("WINDOW_SET_POSITION", {}).get("examples")},
        ["value_contracts.PERCENT_PARTIAL_1_99_REQUIRED", "intents.WINDOW_SET_POSITION.value_contract", "annotation_guidance.window_endpoint_routing", "over_atomization_audit"],
        [
            (partial_contract.get("valid_range") == {"min": 1, "max": 99}, "partial percent range must be 1..99"),
            (partial_contract.get("endpoint_routes") == {0: "WINDOW_CLOSE", 100: "WINDOW_OPEN"}, "window endpoint routes mismatch"),
            (window.get("value_contract") == "PERCENT_PARTIAL_1_99_REQUIRED", "WINDOW_SET_POSITION contract mismatch"),
            (r4_by_id.get("WINDOW_OPEN", {}).get("value_contract") == "NONE", "WINDOW_OPEN must not accept VALUE"),
            (r4_by_id.get("WINDOW_CLOSE", {}).get("value_contract") == "NONE", "WINDOW_CLOSE must not accept VALUE"),
            (window_guidance.get("partial_percent_range") == "1%..99%", "window partial range guidance missing"),
            (window_guidance.get("half_normalization") == "50%", "window half normalization missing"),
            (window_guidance.get("prohibited_value_inference") == ["一点", "稍微", "一点点", "留条缝"], "window prohibited VALUE inference list mismatch"),
        ],
    ))

    speed_delta = value_contracts.get("SPEED_DELTA_OPTIONAL", {})
    p0_results.append(_p0_result(
        "P0-02",
        "ACCELERATE/DECELERATE relative VALUE",
        {intent_id: r3_by_id.get(intent_id, {}).get("value_contract") for intent_id in ("ACCELERATE", "DECELERATE")},
        {intent_id: r4_by_id.get(intent_id, {}).get("value_contract") for intent_id in ("ACCELERATE", "DECELERATE")},
        ["value_contracts.SPEED_DELTA_OPTIONAL", "intents.ACCELERATE.value_contract", "intents.DECELERATE.value_contract", "annotation_guidance.speed_delta_routing"],
        [
            (speed_delta.get("type") == "SPEED_DELTA", "speed delta contract type mismatch"),
            (speed_delta.get("required") is False, "speed delta must remain optional"),
            (speed_delta.get("absolute_target_prohibited") is True, "absolute speed targets must be prohibited"),
            (all(r4_by_id.get(intent_id, {}).get("value_contract") == "SPEED_DELTA_OPTIONAL" for intent_id in ("ACCELERATE", "DECELERATE")), "ACCELERATE/DECELERATE contract mismatch"),
            ("VEHICLE_SET_SPEED" not in r4_ids, "VEHICLE_SET_SPEED must not be added"),
            (guidance.get("speed_delta_routing", {}).get("non_cruise_absolute_target_status") == "CONTRACT_CHECK_NOT_GOLD", "non-cruise absolute target guidance missing"),
        ],
    ))

    gap_modes = mode_contracts.get("CRUISE_GAP_LEVEL")
    gap_audit_examples = r4_audit.get("CRUISE_SET_GAP", {}).get("examples", [])
    p0_results.append(_p0_result(
        "P0-03",
        "CRUISE_GAP_LEVEL expansion",
        r3.get("mode_contracts", {}).get("CRUISE_GAP_LEVEL"),
        gap_modes,
        ["mode_contracts.CRUISE_GAP_LEVEL", "over_atomization_audit.CRUISE_SET_GAP.examples"],
        [
            (gap_modes == ["LEVEL_1", "LEVEL_2", "LEVEL_3", "LEVEL_4"], "cruise gap modes mismatch"),
            (r4_by_id.get("CRUISE_SET_GAP", {}).get("conditional_slot_contract") == "VALUE_XOR_MODE", "CRUISE_SET_GAP must retain VALUE_XOR_MODE"),
            ("LEVEL_N" not in gap_audit_examples and all("LEVEL_N" not in str(value) for value in gap_audit_examples), "LEVEL_N audit placeholder remains"),
        ],
    ))

    p0_results.append(_p0_result(
        "P0-04",
        "OFF YAML string typing",
        {intent_id: r3_audit.get(intent_id, {}).get("examples") for intent_id in ("HEADLIGHT_SET_MODE", "WIPER_SET_MODE")},
        {intent_id: r4_audit.get(intent_id, {}).get("examples") for intent_id in ("HEADLIGHT_SET_MODE", "WIPER_SET_MODE")},
        ["mode_contracts", "over_atomization_audit.*.examples"],
        [
            (not bool_mode_values, "MODE enum contains boolean"),
            (not bool_mode_examples, "MODE example contains boolean"),
            (all("OFF" in r4_audit.get(intent_id, {}).get("examples", []) for intent_id in ("HEADLIGHT_SET_MODE", "WIPER_SET_MODE")), "OFF string audit example missing"),
        ],
    ))

    seat_guidance = guidance.get("seat_semantic_boundaries", {})
    p0_results.append(_p0_result(
        "P0-05",
        "Seat semantic boundaries",
        None,
        seat_guidance,
        ["annotation_guidance.seat_semantic_boundaries"],
        [
            (set(seat_guidance.get("intents", [])) == {"SEAT_LONGITUDINAL_SET_POSITION", "SEAT_TILT_SET_ANGLE", "SEAT_BACKREST_SET_ANGLE"}, "seat guidance intent set mismatch"),
            (set(seat_guidance.get("lexical_anchors", {}).get("LONGITUDINAL", [])) >= {"前移", "后移", "往前挪", "往后挪", "前后移动", "滑轨", "座椅前后位置"}, "longitudinal anchors incomplete"),
            (set(seat_guidance.get("lexical_anchors", {}).get("BACKREST", [])) >= {"靠背", "椅背", "躺", "后仰", "放倒", "直立", "靠背角度"}, "backrest anchors incomplete"),
            (set(seat_guidance.get("lexical_anchors", {}).get("TILT", [])) >= {"坐垫", "座盆", "整体倾角", "座椅整体倾斜", "坐垫前端抬高或降低", "坐垫后端抬高或降低"}, "tilt anchors incomplete"),
            (seat_guidance.get("unqualified_forward_backward_priority") == "SEAT_LONGITUDINAL_SET_POSITION", "unqualified seat direction priority mismatch"),
            (seat_guidance.get("ambiguity_policy") == "ONLY_WHEN_SOURCE_TEXT_HAS_TWO_REASONABLE_INTERPRETATIONS", "seat ambiguity policy mismatch"),
            (all(r4_by_id.get(intent_id) == r3_by_id.get(intent_id) for intent_id in ("SEAT_LONGITUDINAL_SET_POSITION", "SEAT_TILT_SET_ANGLE", "SEAT_BACKREST_SET_ANGLE")), "seat intent core changed"),
        ],
    ))

    expected_headlight_modes = ["OFF", "ON", "POSITION", "DAYTIME_RUNNING_LIGHTS", "AUTO"]
    headlight_mapping = mode_mapping_contracts.get("HEADLIGHT_MAIN_SWITCH", {})
    p0_results.append(_p0_result(
        "P0-06",
        "HEADLIGHT main-light mode",
        {"modes": r3.get("mode_contracts", {}).get("HEADLIGHT"), "mapping": r3.get("mode_mapping_contracts", {}).get("HEADLIGHT_MAIN_SWITCH")},
        {"modes": mode_contracts.get("HEADLIGHT"), "mapping": headlight_mapping},
        ["mode_contracts.HEADLIGHT", "mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH", "over_atomization_audit.HEADLIGHT_SET_MODE", "annotation_guidance.headlight_main_switch_routing"],
        [
            (mode_contracts.get("HEADLIGHT") == expected_headlight_modes, "HEADLIGHT modes mismatch"),
            (headlight_mapping.get("canonical_modes") == expected_headlight_modes, "HEADLIGHT mapping canonical modes mismatch"),
            (headlight_mapping.get("lexical_aliases", {}).get("ON", {}).get("canonical_mode") == "ON", "ON mapping mismatch"),
            ("BEAM" not in mode_contracts.get("HEADLIGHT", []), "HEADLIGHT mode still contains BEAM"),
            ("BEAM" not in r4_audit.get("HEADLIGHT_SET_MODE", {}).get("examples", []), "HEADLIGHT audit still contains BEAM"),
            (guidance.get("headlight_main_switch_routing", {}).get("on_mode_prohibited_intent_ids") == ["LOW_BEAM_ON", "HIGH_BEAM_ON"], "ON beam prohibition guidance mismatch"),
        ],
    ))

    trunk_ids = ["TRUNK_OPEN", "TRUNK_CLOSE", "TRUNK_SET_POSITION", "TRUNK_LOCK", "TRUNK_UNLOCK"]
    trunk_guidance = guidance.get("trunk_frunk_hood_routing", {})
    p0_results.append(_p0_result(
        "P0-07",
        "TRUNK/FRUNK/HOOD isolation",
        {intent_id: r3_by_id.get(intent_id, {}).get("allowed_areas") for intent_id in trunk_ids},
        {intent_id: r4_by_id.get(intent_id, {}).get("allowed_areas") for intent_id in trunk_ids},
        ["intents.TRUNK_*.allowed_areas", "annotation_guidance.trunk_frunk_hood_routing"],
        [
            (all(r4_by_id.get(intent_id, {}).get("allowed_areas") == ["REAR"] for intent_id in trunk_ids), "TRUNK allowed_areas must be REAR only"),
            (all(r4_by_id.get(intent_id) == r3_by_id.get(intent_id) for intent_id in ("HOOD_OPEN", "HOOD_CLOSE", "HOOD_SET_POSITION")), "HOOD intent core changed"),
            (not ({"FRUNK_OPEN", "FRUNK_CLOSE", "FRUNK_SET_POSITION", "FRUNK_LOCK", "FRUNK_UNLOCK"} & set(r4_ids)), "FRUNK intents must not be added in this core draft"),
            (trunk_guidance.get("frunk_expansion_status") == "BLOCKED_BY_KNOWN_UNSUPPORTED_EXPANSION", "FRUNK deferred expansion status missing"),
            (trunk_guidance.get("formal_user_voice_projection_prohibited") is True, "FRUNK formal projection prohibition missing"),
        ],
    ))

    for result in p0_results:
        if result["validator_result"] != "PASS":
            errors.extend(f"{result['p0_id']}: {message}" for message in result["errors"])

    diff_paths = sorted(set(changed_paths(r3, r4)))
    unauthorized_paths = sorted(
        path
        for path in set(diff_paths)
        if path not in ALLOWED_CHANGED_PATHS
        and not any(path.startswith(prefix) for prefix in ALLOWED_CHANGED_PREFIXES)
    )
    missing_expected_change_groups = {
        "P0-01": not any(path.startswith("value_contracts.PERCENT_PARTIAL_1_99_REQUIRED") for path in diff_paths),
        "P0-02": not any(path.startswith("value_contracts.SPEED_DELTA_OPTIONAL") for path in diff_paths),
        "P0-03": "mode_contracts.CRUISE_GAP_LEVEL" not in diff_paths,
        "P0-04": not any(path.endswith("WIPER_SET_MODE.examples") for path in diff_paths),
        "P0-05": "annotation_guidance" not in diff_paths,
        "P0-06": "mode_contracts.HEADLIGHT" not in diff_paths,
        "P0-07": not any(path.startswith("intents.TRUNK_OPEN.allowed_areas") for path in diff_paths),
    }
    missing_groups = sorted(key for key, missing in missing_expected_change_groups.items() if missing)
    check("APPROVED_CHANGE_PATHS_ONLY", not unauthorized_paths, f"unapproved changed paths: {unauthorized_paths}")
    check("ALL_SEVEN_P0_GROUPS_PRESENT", not missing_groups, f"missing P0 change groups: {missing_groups}")

    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "registry_version": r4.get("registry_version"),
        "semantic_freeze_status": r4.get("semantic_freeze_status"),
        "r3_registry_path": display_path(r3_path),
        "r3_sha256": r3_hash,
        "r4_registry_path": display_path(registry_path),
        "r4_sha256": r4_hash,
        "metrics": {
            "SEMANTIC_INTENT_COUNT": len(r4_ids),
            "FORMAL_USER_VOICE_INTENT_COUNT": len(formal_ids),
            "KNOWN_UNSUPPORTED_CONTROL_INTENT_COUNT": len(known_ids),
            "PROJECT_NATIVE_INTENT_COUNT": len(r4_project_native),
            "SEMANTIC_KEY_UNIQUE_COUNT": len(semantic_groups),
            "SEMANTIC_KEY_COLLISION_COUNT": len(collisions),
            "UNRESOLVED_CONTRACT_COUNT": len(unresolved_contracts),
            "REQUIRED_OPTIONAL_SLOT_CONFLICT_COUNT": len(slot_conflicts),
            "BOOL_MODE_VALUE_COUNT": len(bool_mode_values) + len(bool_mode_examples),
            "CHANGED_PATH_COUNT": len(diff_paths),
            "UNAPPROVED_CHANGED_PATH_COUNT": len(unauthorized_paths),
            "P0_PASS_COUNT": sum(result["validator_result"] == "PASS" for result in p0_results),
        },
        "changed_paths": diff_paths,
        "unauthorized_changed_paths": unauthorized_paths,
        "checks": checks,
        "p0_results": p0_results,
        "formal_user_voice_intent_ids": formal_ids,
        "project_native_intent_ids": r4_project_native,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=R4_PATH)
    parser.add_argument("--r3", type=Path, default=R3_PATH)
    args = parser.parse_args()
    try:
        result = validate(args.registry, r3_path=args.r3)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
