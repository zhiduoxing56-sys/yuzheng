"""Validate the Full NLU R4 scope simplification artifacts."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, sha256_file
from validate_sys014_r4_full_registry import CORE_PATH, CORE_SHA256, R3_PATH, R3_SHA256


ROOT = Path(__file__).resolve().parents[1]
FULL_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_full_draft.yaml"
FINAL_PARENT_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_final_candidate.yaml"
SIMPLIFIED_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_simplified_candidate.yaml"
ARCHIVE_PATH = ROOT / "data" / "nlu" / "spec" / "known_control_reference_archive_r4.yaml"

FULL_SHA256 = "393de4203c2cb93b0162724b336cb29a2cc67fba1c73b1cbc1fe62bb642f4f21"
FINAL_PARENT_SHA256 = "55bbb90780a969cb249f73833d7d34d9e464d99c65e1a6352ead15aa34db4440"
SIMPLIFIED_VERSION = "sys-014-semantic-hardening-r4-simplified-candidate"
SIMPLIFIED_STATUS = "DRAFT_PENDING_FINAL_SCOPE_REVIEW"
RUNTIME_SCOPES = ["FORMAL_EXECUTABLE", "KNOWN_CONTROL_BYPASS", "NON_CONTROL", "UNKNOWN_OOD"]


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def _all_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _all_strings(key)
            yield from _all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _all_strings(item)


def validate(
    simplified_path: Path = SIMPLIFIED_PATH,
    archive_path: Path = ARCHIVE_PATH,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})
        if not passed:
            errors.append(f"{name}: {detail}")

    hashes = {
        "r3": sha256_file(R3_PATH),
        "core": sha256_file(CORE_PATH),
        "full": sha256_file(FULL_PATH),
        "final_parent": sha256_file(FINAL_PARENT_PATH),
        "simplified": sha256_file(simplified_path),
        "archive": sha256_file(archive_path),
    }
    check("R3_SHA256_FROZEN", hashes["r3"] == R3_SHA256, f"expected {R3_SHA256}, got {hashes['r3']}")
    check("CORE_SHA256_FROZEN", hashes["core"] == CORE_SHA256, f"expected {CORE_SHA256}, got {hashes['core']}")
    check("FULL_SHA256_FROZEN", hashes["full"] == FULL_SHA256, f"expected {FULL_SHA256}, got {hashes['full']}")
    check("FINAL_PARENT_SHA256_FROZEN", hashes["final_parent"] == FINAL_PARENT_SHA256, f"expected {FINAL_PARENT_SHA256}, got {hashes['final_parent']}")

    parent = load_yaml(FINAL_PARENT_PATH)
    simplified = load_yaml(simplified_path)
    archive = load_yaml(archive_path)
    parent_formal = [item for item in parent["intents"] if item.get("user_voice_scope_status") == "FORMAL_EXECUTABLE"]
    parent_known = [item for item in parent["intents"] if item.get("user_voice_scope_status") == "KNOWN_UNSUPPORTED_CONTROL"]
    runtime_intents = simplified["intents"]
    runtime_ids = [item["intent_id"] for item in runtime_intents]
    known_ids = [item["intent_id"] for item in parent_known]
    known_id_set = set(known_ids)

    formal_unchanged = runtime_intents == parent_formal
    check("SIMPLIFIED_VERSION", simplified.get("registry_version") == SIMPLIFIED_VERSION, "registry version mismatch")
    check("SIMPLIFIED_STATUS", simplified.get("semantic_freeze_status") == SIMPLIFIED_STATUS, "registry status mismatch")
    check("FORMAL_COUNT_71", len(runtime_intents) == 71, f"runtime Intent head has {len(runtime_intents)} items")
    check("FORMAL_DEFINITIONS_EXACT", formal_unchanged, "FORMAL definitions or order changed")
    check("FORMAL_PROJECTION_EXACT", simplified.get("formal_user_voice_intent_ids") == [item["intent_id"] for item in parent_formal], "formal projection changed")
    check("RUNTIME_INTENT_IDS_UNIQUE", len(runtime_ids) == len(set(runtime_ids)), "duplicate runtime Intent IDs")
    all_known_removed = all(item.get("user_voice_scope_status") != "KNOWN_UNSUPPORTED_CONTROL" for item in runtime_intents)
    check("NO_KNOWN_STATUS_IN_INTENT_HEAD", all_known_removed, "detailed KNOWN status remains in runtime Intent head")
    check("OLD_KNOWN_PROJECTION_REMOVED", "known_unsupported_control_intent_ids" not in simplified, "old detailed KNOWN projection remains")
    leaked_known_ids = sorted(known_id_set & set(_all_strings(simplified)))
    check("NO_DETAILED_KNOWN_IDS_IN_RUNTIME_REGISTRY", not leaked_known_ids, f"detailed KNOWN IDs leaked: {leaked_known_ids[:20]}")

    archive_exact = archive.get("archived_intents") == parent_known
    check("ARCHIVE_COUNT_91", archive.get("archived_intent_count") == len(parent_known) == 91, "archive count mismatch")
    check("ARCHIVE_IDS_ORDER", archive.get("archived_intent_ids") == known_ids, "archive ID order mismatch")
    check("ARCHIVE_DEFINITIONS_EXACT", archive_exact, "archived definitions are not exact source copies")
    usage = archive.get("usage_policy", {})
    check(
        "ARCHIVE_NOT_RUNTIME_OR_LABEL_SPACE",
        usage.get("model_label_space") is False
        and usage.get("runtime_registry") is False
        and usage.get("gold_precise_intent_mapping_authority") is False
        and usage.get("provenance_and_future_expansion_reference_only") is True,
        "archive usage policy is unsafe",
    )
    reference = simplified.get("scope_simplification", {}).get("reference_archive", {})
    check(
        "ARCHIVE_LINK_AND_HASH",
        reference.get("path") == "data/nlu/spec/known_control_reference_archive_r4.yaml"
        and reference.get("sha256") == hashes["archive"]
        and reference.get("archived_intent_count") == 91
        and reference.get("runtime_loading_prohibited") is True,
        "archive link/hash/count mismatch",
    )

    enums = simplified.get("enums", {})
    bypass_scope_present = enums.get("runtime_scope") == RUNTIME_SCOPES
    check("FOUR_RUNTIME_SCOPES", bypass_scope_present, f"runtime scopes must be {RUNTIME_SCOPES}")
    scope_contract = simplified.get("user_voice_scope_contract", {})
    check("SCOPE_CONTRACT_KEYS", list(scope_contract) == RUNTIME_SCOPES, "scope contract keys/order mismatch")
    bypass = scope_contract.get("KNOWN_CONTROL_BYPASS", {})
    check(
        "BYPASS_NO_DETAILED_SEMANTICS_REQUIRED",
        bypass.get("requires_intent_id") is False
        and bypass.get("requires_canonical_action") is False
        and bypass.get("requires_canonical_target") is False
        and bypass.get("requires_control_attribute") is False
        and bypass.get("requires_value") is False
        and bypass.get("requires_mode") is False
        and bypass.get("requires_area") is False
        and bypass.get("formal_contract_completeness_check") == "SKIP",
        "bypass still requires detailed semantic fields/completeness",
    )
    bypass_route = simplified.get("runtime_scope_routing", {}).get("KNOWN_CONTROL_BYPASS", {})
    check(
        "BYPASS_ROUTE",
        bypass_route == {
            "decision_route": "PASS_BYPASS",
            "execution_authorized_by_yuzheng": False,
            "route_target": "NATIVE_COCKPIT_ASSISTANT",
        },
        "bypass route mismatch",
    )
    completeness = simplified.get("formal_contract_completeness", {})
    check(
        "FORMAL_ONLY_COMPLETENESS",
        completeness.get("applicable_scopes") == ["FORMAL_EXECUTABLE"]
        and set(completeness.get("excluded_scopes", [])) == {"KNOWN_CONTROL_BYPASS", "NON_CONTROL", "UNKNOWN_OOD"}
        and completeness.get("known_control_bypass_slot_completeness_check") == "SKIP",
        "formal completeness applies outside FORMAL",
    )
    non_control_unknown_distinct = (
        "NON_CONTROL" in scope_contract
        and "UNKNOWN_OOD" in scope_contract
        and scope_contract["NON_CONTROL"] != scope_contract["UNKNOWN_OOD"]
        and simplified["runtime_scope_routing"]["NON_CONTROL"] != simplified["runtime_scope_routing"]["UNKNOWN_OOD"]
    )
    check("NON_CONTROL_UNKNOWN_OOD_DISTINCT", non_control_unknown_distinct, "NON_CONTROL and UNKNOWN_OOD collapsed")

    multi = simplified.get("multi_intent_schema", {})
    example = multi.get("mixed_example", {})
    expected_sub_intents = [
        {"scope": "KNOWN_CONTROL_BYPASS"},
        {"scope": "FORMAL_EXECUTABLE", "intent_id": "LOW_BEAM_OFF"},
    ]
    mixed_allowed = (
        multi.get("ordered_sub_intents_required") is True
        and multi.get("per_sub_intent_scope_and_routing_required") is True
        and multi.get("mixed_scope_allowed") is True
        and multi.get("sentence_level_route_collapse_prohibited") is True
        and example.get("sub_intents") == expected_sub_intents
        and len(example.get("per_sub_intent_routes", [])) == 2
    )
    check("MIXED_MULTI_INTENT_SCHEMA", mixed_allowed, "formal+bypass ordered multi-intent schema missing")

    gold = simplified.get("gold_scope_mapping_policy", {})
    check(
        "GOLD_POLICY_NO_REMAP_OR_DETAILED_LABEL",
        gold.get("existing_data_remapped_by_this_change") is False
        and gold.get("known_vehicle_control_not_formal_target") == {"scope": "KNOWN_CONTROL_BYPASS"}
        and gold.get("specific_intent_id_required") is False
        and gold.get("mac_object_mode_value_as_required_model_labels") is False
        and gold.get("non_control_and_unknown_ood_must_remain_distinct") is True,
        "Gold policy violates scope simplification",
    )
    build_policy = simplified.get("scope_simplification", {})
    check(
        "NO_DATA_OR_TRAINING_MUTATION",
        build_policy.get("data_remapping_performed") is False
        and build_policy.get("training_performed") is False
        and build_policy.get("data_expansion_performed") is False
        and build_policy.get("known_taxonomy_refinement_performed") is False,
        "forbidden data/training/taxonomy operation recorded",
    )

    # Preserve the six exact P0 guidance sections and the lexical substance of
    # the trunk/hood/frunk boundary while converting FRUNK to bypass scope.
    p0_sections = [
        "window_endpoint_routing", "speed_delta_routing", "cruise_gap_routing",
        "seat_semantic_boundaries", "headlight_main_switch_routing",
    ]
    p0_changed = [
        name for name in p0_sections
        if simplified["annotation_guidance"].get(name) != parent["annotation_guidance"].get(name)
    ]
    check("P0_GUIDANCE_SECTIONS_FROZEN", not p0_changed, f"P0 guidance changed: {p0_changed}")
    parent_boundary = parent["annotation_guidance"]["trunk_frunk_hood_routing"]
    runtime_boundary = simplified["annotation_guidance"]["trunk_frunk_hood_routing"]
    boundary_ok = (
        runtime_boundary.get("TRUNK") == parent_boundary.get("TRUNK")
        and runtime_boundary.get("HOOD") == parent_boundary.get("HOOD")
        and runtime_boundary.get("lexical_boundary") == parent_boundary.get("lexical_boundary")
        and runtime_boundary.get("FRUNK", {}).get("lexical_anchors") == parent_boundary.get("FRUNK", {}).get("lexical_anchors")
        and runtime_boundary.get("FRUNK", {}).get("runtime_scope") == "KNOWN_CONTROL_BYPASS"
        and runtime_boundary.get("FRUNK", {}).get("detailed_intent_assignment_prohibited") is True
    )
    check("TRUNK_HOOD_FRUNK_BOUNDARY_PRESERVED", boundary_ok, "trunk/hood/frunk lexical boundary changed or FRUNK not bypassed")
    check(
        "ANNOTATION_GUIDANCE_VERSION_SYNC",
        simplified["annotation_guidance"].get("registry_version") == SIMPLIFIED_VERSION,
        "annotation guidance version mismatch",
    )

    value_contracts = simplified["value_contracts"]
    mode_contracts = simplified["mode_contracts"]
    direction_contracts = simplified["direction_contracts"]
    conditional_contracts = simplified["conditional_slot_contracts"]
    mode_mapping_contracts = simplified["mode_mapping_contracts"]
    value_mapping_contracts = simplified["value_mapping_contracts"]
    family_ids = {family["family_id"] for family in simplified["capability_families"]}
    family_members = [intent_id for family in simplified["capability_families"] for intent_id in family["intents"]]
    unresolved: list[str] = []
    overlaps: list[str] = []
    invalid_modes: list[str] = []
    semantic_groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for name, values in mode_contracts.items():
        if not isinstance(values, list):
            invalid_modes.append(f"{name}:not_list")
        else:
            invalid_modes.extend(f"{name}[{index}]" for index, value in enumerate(values) if isinstance(value, bool) or not isinstance(value, str))
    for item in runtime_intents:
        intent_id = item["intent_id"]
        semantic_groups[(item["canonical_action"], item["canonical_target"], item["control_attribute"])].append(intent_id)
        overlap = set(item.get("required_slots", [])) & set(item.get("optional_slots", []))
        if overlap:
            overlaps.append(f"{intent_id}:{sorted(overlap)}")
        references = [
            ("value_contract", value_contracts, {None, "NONE"}),
            ("mode_contract", mode_contracts, {None}),
            ("direction_contract", direction_contracts, {None}),
            ("conditional_slot_contract", conditional_contracts, {None}),
            ("mode_mapping_contract", mode_mapping_contracts, {None}),
            ("value_mapping_contract", value_mapping_contracts, {None}),
        ]
        for field, section, excluded in references:
            value = item.get(field)
            if value not in excluded and value not in section:
                unresolved.append(f"{intent_id}.{field}={value}")
        if item.get("capability_family") not in family_ids:
            unresolved.append(f"{intent_id}.capability_family")
        for area in item.get("allowed_areas", []):
            if area not in simplified["area_catalog"]:
                unresolved.append(f"{intent_id}.area={area}")
    collisions = {"|".join(key): ids for key, ids in semantic_groups.items() if len(ids) > 1}
    check("FORMAL_FAMILY_COVERAGE", Counter(family_members) == Counter(runtime_ids), "formal family coverage is not one-to-one")
    check("FORMAL_CONTRACT_REFERENCES", not unresolved, f"unresolved formal references: {unresolved}")
    check("FORMAL_SLOT_DISJOINT", not overlaps, f"required/optional overlap: {overlaps}")
    check("FORMAL_SEMANTIC_KEYS_UNIQUE", not collisions, f"formal semantic collisions: {collisions}")
    check("MODE_VALUES_ALL_STRINGS", not invalid_modes, f"invalid MODE values: {invalid_modes}")
    continuous = simplified.get("value_language_semantics", {}).get("continuous_numeric_contracts", [])
    check("CONTINUOUS_CONTRACT_REFS", set(continuous) <= set(value_contracts), "continuous contract list references pruned contracts")

    ontology = simplified["semantic_ontology"]
    check("FORMAL_ONTOLOGY_ACTIONS", ontology.get("canonical_actions") == sorted({item["canonical_action"] for item in runtime_intents}), "action ontology not formal-only")
    check("FORMAL_ONTOLOGY_TARGETS", ontology.get("canonical_targets") == sorted({item["canonical_target"] for item in runtime_intents}), "target ontology not formal-only")
    check("FORMAL_ONTOLOGY_ATTRIBUTES", ontology.get("control_attributes") == sorted({item["control_attribute"] for item in runtime_intents}), "attribute ontology not formal-only")

    origins = Counter(item["capability_origin"] for item in runtime_intents)
    by_id = {item["intent_id"]: item for item in runtime_intents}
    project_families = sum(
        all(by_id[intent_id]["capability_origin"] == "PROJECT_NATIVE" for intent_id in family["intents"])
        for family in simplified["capability_families"]
    )
    vss_families = sum(
        all(by_id[intent_id]["capability_origin"] in {"VSS", "VSS_AND_PROJECT"} for intent_id in family["intents"])
        for family in simplified["capability_families"]
    )
    expected_stats = {
        "intent_count": 71,
        "semantic_intent_count": 71,
        "runtime_intent_head_count": 71,
        "formal_user_voice_intent_count": 71,
        "known_unsupported_control_intent_count": 0,
        "known_control_bypass_scope_count": 1,
        "runtime_scope_count": 4,
        "archived_known_control_reference_count": 91,
        "capability_family_count": len(simplified["capability_families"]),
        "project_native_family_count": project_families,
        "vss_family_count": vss_families,
        "project_native_intent_count": origins["PROJECT_NATIVE"],
        "vss_derived_intent_count": origins["VSS"] + origins["VSS_AND_PROJECT"],
        "legacy_test_only_intent_count": len(simplified.get("legacy_test_only", [])),
        "out_of_scope_family_count": 0,
        "pending_scope_intent_count": 0,
    }
    check("SIMPLIFIED_STATISTICS", all(simplified["statistics"].get(key) == value for key, value in expected_stats.items()), f"statistics mismatch: {expected_stats}")

    required_outcomes = {
        "formal_executable_completely_unchanged": formal_unchanged,
        "known_unsupported_removed_count": len(parent_known),
        "archive_count": archive.get("archived_intent_count"),
        "all_known_unsupported_removed_from_runtime_intent_head": all_known_removed and not leaked_known_ids,
        "known_control_bypass_scope_present": bypass_scope_present and "KNOWN_CONTROL_BYPASS" in scope_contract,
        "non_control_unknown_ood_distinct": non_control_unknown_distinct,
        "mixed_formal_bypass_multi_intent_allowed": mixed_allowed,
    }
    return {
        "status": "PASS" if not errors else "FAIL",
        "registry_version": simplified.get("registry_version"),
        "semantic_freeze_status": simplified.get("semantic_freeze_status"),
        "hashes": hashes,
        "metrics": {
            "FORMAL_EXECUTABLE_INTENT_COUNT": len(runtime_intents),
            "REMOVED_KNOWN_UNSUPPORTED_INTENT_COUNT": len(parent_known),
            "ARCHIVED_KNOWN_CONTROL_REFERENCE_COUNT": archive.get("archived_intent_count"),
            "RUNTIME_INTENT_HEAD_COUNT": len(runtime_intents),
            "RUNTIME_SCOPE_COUNT": len(RUNTIME_SCOPES),
            "RUNTIME_CAPABILITY_FAMILY_COUNT": len(simplified["capability_families"]),
            "UNRESOLVED_FORMAL_REFERENCE_COUNT": len(unresolved),
            "FORMAL_SEMANTIC_COLLISION_COUNT": len(collisions),
            "FORMAL_SLOT_INTERSECTION_COUNT": len(overlaps),
            "INVALID_MODE_ENUM_COUNT": len(invalid_modes),
            "DETAILED_KNOWN_ID_LEAK_COUNT": len(leaked_known_ids),
        },
        "required_outcomes": required_outcomes,
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
