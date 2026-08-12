"""Validate the metadata-only R4 final freeze against the simplified parent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, changed_paths, sha256_file
from validate_sys014_r4_full_registry import _active_poc_references


ROOT = Path(__file__).resolve().parents[1]
SIMPLIFIED_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_simplified_candidate.yaml"
FINAL_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_final.yaml"
NEXT_MAPPING_PATH = ROOT / "data" / "nlu" / "spec" / "mapping_rules" / "nlu_mapping_r4_scope_v1.yaml"

SIMPLIFIED_SHA256 = "4eb697a9cc9daf48d1292e34b5ca37936de114028e71cfcf495e773335e6406f"
FINAL_VERSION = "sys-014-semantic-hardening-r4-final"
FINAL_FREEZE_STATUS = "FROZEN_FOR_FULL_NLU_GOLD_BUILD"
FINAL_DOCUMENT_STATUS = "FROZEN_FORMAL_RUNTIME_REGISTRY"
RUNTIME_SCOPES = ["FORMAL_EXECUTABLE", "KNOWN_CONTROL_BYPASS", "NON_CONTROL", "UNKNOWN_OOD"]
DEAD_HEADLIGHT_REFERENCE_PATH = (
    "mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH.restricted_aliases.ON.prohibited_canonical_mode"
)


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def _metadata_path_allowed(path: str) -> bool:
    exact = {
        "registry_version",
        "semantic_freeze_status",
        "document_status",
        "runtime_loading_allowed",
        DEAD_HEADLIGHT_REFERENCE_PATH,
    }
    prefixes = (
        "mapping_rule_source.",
        "r4_mapping_policy",
        "gold_scope_mapping_policy.known_control_evidence_requirement",
        "gold_scope_mapping_policy.known_control_evidence_policy",
    )
    return path in exact or any(path == prefix or path.startswith(prefix) for prefix in prefixes)


def validate(final_path: Path = FINAL_PATH) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})
        if not passed:
            errors.append(f"{name}: {detail}")

    simplified_hash = sha256_file(SIMPLIFIED_PATH)
    final_hash = sha256_file(final_path)
    check("SIMPLIFIED_PARENT_SHA256", simplified_hash == SIMPLIFIED_SHA256, f"expected {SIMPLIFIED_SHA256}, got {simplified_hash}")
    simplified = load_yaml(SIMPLIFIED_PATH)
    final = load_yaml(final_path)

    check("FINAL_VERSION", final.get("registry_version") == FINAL_VERSION, "final registry version mismatch")
    check("FINAL_FREEZE_STATUS", final.get("semantic_freeze_status") == FINAL_FREEZE_STATUS, "semantic freeze status mismatch")
    check("FINAL_DOCUMENT_STATUS", final.get("document_status") == FINAL_DOCUMENT_STATUS, "document status mismatch")
    check("RUNTIME_LOADING_ALLOWED", final.get("runtime_loading_allowed") is True, "formal frozen registry must permit read-only runtime loading")

    actual_changed_paths = sorted(set(changed_paths(simplified, final)))
    forbidden_changes = [path for path in actual_changed_paths if not _metadata_path_allowed(path)]
    check("METADATA_ONLY_CHANGED_PATHS", not forbidden_changes, f"forbidden changed paths: {forbidden_changes}")

    check("INTENT_COUNT_71", len(final["intents"]) == 71, f"intent count is {len(final['intents'])}")
    check("FORMAL_INTENTS_ALL_FIELDS_EXACT", final["intents"] == simplified["intents"], "one or more Formal Intent fields changed")
    check("FORMAL_ID_SET_AND_ORDER_EXACT", final["formal_user_voice_intent_ids"] == simplified["formal_user_voice_intent_ids"], "Formal ID set/order changed")
    check("CAPABILITY_FAMILIES_EXACT", final["capability_families"] == simplified["capability_families"], "capability families changed")
    check("SEMANTIC_ONTOLOGY_EXACT", final["semantic_ontology"] == simplified["semantic_ontology"], "semantic ontology changed")

    contract_sections = [
        "value_contracts", "mode_contracts", "direction_contracts", "conditional_slot_contracts",
        "value_mapping_contracts", "area_catalog", "area_semantics", "value_language_semantics",
    ]
    changed_contract_sections = [section for section in contract_sections if final.get(section) != simplified.get(section)]
    check("ALL_CONTRACTS_EXACT", not changed_contract_sections, f"contract sections changed: {changed_contract_sections}")
    expected_mode_mapping_contracts = json.loads(json.dumps(simplified["mode_mapping_contracts"]))
    del expected_mode_mapping_contracts["HEADLIGHT_MAIN_SWITCH"]["restricted_aliases"]["ON"][
        "prohibited_canonical_mode"
    ]
    check(
        "MODE_MAPPING_CONTRACTS_EXACT_EXCEPT_DEAD_REFERENCE",
        final["mode_mapping_contracts"] == expected_mode_mapping_contracts,
        "mode mapping contracts changed beyond the approved dead BEAM reference removal",
    )

    expected_stats = {
        "intent_count": 71,
        "formal_user_voice_intent_count": 71,
        "runtime_intent_head_count": 71,
        "known_unsupported_control_intent_count": 0,
        "archived_known_control_reference_count": 91,
        "runtime_scope_count": 4,
    }
    check("FROZEN_STATISTICS", all(final["statistics"].get(key) == value for key, value in expected_stats.items()), f"statistics mismatch: {expected_stats}")
    check("STATISTICS_OBJECT_EXACT", final["statistics"] == simplified["statistics"], "statistics changed during metadata freeze")

    check("FOUR_RUNTIME_SCOPES_EXACT", final["enums"].get("runtime_scope") == RUNTIME_SCOPES, "runtime scope order/content changed")
    check("SCOPE_CONTRACT_EXACT", final["user_voice_scope_contract"] == simplified["user_voice_scope_contract"], "scope contract changed")
    bypass = final["runtime_scope_routing"]["KNOWN_CONTROL_BYPASS"]
    check(
        "BYPASS_ROUTE_EXACT",
        bypass == {
            "decision_route": "PASS_BYPASS",
            "execution_authorized_by_yuzheng": False,
            "route_target": "NATIVE_COCKPIT_ASSISTANT",
        }
        and final["runtime_scope_routing"] == simplified["runtime_scope_routing"],
        "KNOWN_CONTROL_BYPASS route changed",
    )
    check("MULTI_INTENT_SCHEMA_EXACT", final["multi_intent_schema"] == simplified["multi_intent_schema"], "formal+bypass multi-intent schema changed")
    check("FORMAL_COMPLETENESS_POLICY_EXACT", final["formal_contract_completeness"] == simplified["formal_contract_completeness"], "formal completeness scope changed")

    parent_mapping = simplified["mapping_rule_source"]
    mapping = final["mapping_rule_source"]
    provenance_exact = all(mapping.get(field) == parent_mapping.get(field) for field in ("path", "version", "sha256"))
    check("LEGACY_MAPPING_PROVENANCE_PRESERVED", provenance_exact, "legacy mapping path/version/SHA changed")
    mapping_disabled = (
        mapping.get("status") == "LEGACY_PRE_R4_MAPPING"
        and mapping.get("usable_for_r4_gold") is False
        and mapping.get("usable_for_training") is False
        and mapping.get("required_next_mapping_version") == "nlu_mapping_r4_scope_v1"
    )
    check("LEGACY_MAPPING_DISABLED", mapping_disabled, "legacy mapping not explicitly disabled for R4 Gold/training")
    check(
        "R4_MAPPING_POLICY",
        final.get("r4_mapping_policy") == {
            "architecture": "FORMAL_INTENT_HEAD_PLUS_UNIFIED_SCOPE_CLASSIFICATION",
            "scope_mapping_required": True,
            "formal_intent_mapping_only_when_scope_formal": True,
            "old_baseline_mapping_as_truth_prohibited": True,
        },
        "R4 mapping policy mismatch",
    )
    check("NEXT_MAPPING_FILE_NOT_CREATED", not NEXT_MAPPING_PATH.exists(), "nlu_mapping_r4_scope_v1 must not be created in this stage")

    gold = final["gold_scope_mapping_policy"]
    policy = gold.get("known_control_evidence_policy", {})
    evidence_policy_ok = (
        "known_control_evidence_requirement" not in gold
        and policy.get("primary_evidence") == "RAW_TEXT"
        and policy.get("auxiliary_evidence_when_available") == ["MAC_SPLIT_SENS", "MAC_SEMANTICS"]
        and policy.get("evidence_priority") == ["RAW_TEXT", "MAC_SPLIT_SENS", "MAC_SEMANTICS"]
        and policy.get("all_three_required") is False
        and policy.get("baseline_mapping_as_truth_prohibited") is True
        and policy.get("known_control_bypass_candidate_rule") == {
            "raw_text_clearly_indicates_real_vehicle_cockpit_or_local_head_unit_control": True,
            "formal_executable_mapping_unavailable": True,
        }
        and policy.get("mac_annotation_role") == "AUXILIARY_EVIDENCE_AND_CONFLICT_CHECK_WHEN_AVAILABLE"
        and policy.get("source_conflict_policy") == {
            "annotation_must_not_override_raw_text": True,
            "route": "SOURCE_CONFLICT_REVIEW",
        }
        and policy.get("old_baseline_may_determine_final_scope") is False
    )
    check("KNOWN_CONTROL_EVIDENCE_PRIORITY_POLICY", evidence_policy_ok, "Known Control evidence priority/conflict policy mismatch")
    unchanged_gold_fields = {
        key: value for key, value in simplified["gold_scope_mapping_policy"].items()
        if key != "known_control_evidence_requirement"
    }
    final_unchanged_gold_fields = {
        key: value for key, value in gold.items()
        if key != "known_control_evidence_policy"
    }
    check("OTHER_GOLD_POLICY_FIELDS_EXACT", final_unchanged_gold_fields == unchanged_gold_fields, "unapproved Gold policy fields changed")

    active_poc = _active_poc_references()
    check("ACTIVE_7_INTENT_DEPENDENCY_ZERO", not active_poc, f"active legacy PoC dependencies: {active_poc}")
    following_absent = (
        "FOLLOWING_GAP_REQUIRED" not in final["value_contracts"]
        and "FOLLOWING_GAP_REQUIRED" not in final.get("value_language_semantics", {}).get("continuous_numeric_contracts", [])
        and all(item.get("value_contract") != "FOLLOWING_GAP_REQUIRED" for item in final["intents"])
    )
    check("FOLLOWING_GAP_REQUIRED_ABSENT", following_absent, "FOLLOWING_GAP_REQUIRED was restored")

    return {
        "status": "PASS" if not errors else "FAIL",
        "registry_version": final.get("registry_version"),
        "semantic_freeze_status": final.get("semantic_freeze_status"),
        "document_status": final.get("document_status"),
        "simplified_parent_sha256": simplified_hash,
        "final_sha256": final_hash,
        "metrics": {
            "INTENT_COUNT": final["statistics"]["intent_count"],
            "FORMAL_USER_VOICE_INTENT_COUNT": final["statistics"]["formal_user_voice_intent_count"],
            "RUNTIME_INTENT_HEAD_COUNT": final["statistics"]["runtime_intent_head_count"],
            "KNOWN_UNSUPPORTED_CONTROL_INTENT_COUNT": final["statistics"]["known_unsupported_control_intent_count"],
            "ARCHIVED_KNOWN_CONTROL_REFERENCE_COUNT": final["statistics"]["archived_known_control_reference_count"],
            "RUNTIME_SCOPE_COUNT": final["statistics"]["runtime_scope_count"],
            "ACTIVE_7_INTENT_DEPENDENCY_COUNT": len(active_poc),
            "FORBIDDEN_CHANGED_PATH_COUNT": len(forbidden_changes),
            "CHANGED_METADATA_PATH_COUNT": len(actual_changed_paths),
        },
        "mapping_rule_source": mapping,
        "r4_mapping_policy": final.get("r4_mapping_policy"),
        "known_control_evidence_policy": policy,
        "changed_paths": actual_changed_paths,
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
