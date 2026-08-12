"""Validate the SYS-014 R4 full draft against the immutable R4 core parent."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, changed_paths, sha256_file

FULL_NLU_DIR = Path(__file__).resolve().parent / "full_nlu"
if str(FULL_NLU_DIR) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(FULL_NLU_DIR))
from r4_known_unsupported_evidence import build_evidence, extract_frames  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
R3_PATH = ROOT / "data/nlu/spec/intent_registry_r3.yaml"
CORE_PATH = ROOT / "data/nlu/spec/intent_registry_r4_core_draft.yaml"
FULL_PATH = ROOT / "data/nlu/spec/intent_registry_r4_full_draft.yaml"
AUDIT_DIR = ROOT / "data/nlu/spec/audits"
EXPANSION_REPORT_PATH = AUDIT_DIR / "r4_known_unsupported_expansion_report_v1.json"
ADAS_REPORT_PATH = AUDIT_DIR / "known_unsupported_adas_candidates_v1.json"
OTHER_REPORT_PATH = AUDIT_DIR / "known_unsupported_other_candidates_v1.json"
SOURCE_SCREEN_PATH = ROOT / "初筛/full_nlu_source_screen_v1.jsonl"
MAC_PATHS = [ROOT / "train_set.jsonl", ROOT / "dev_set.jsonl", ROOT / "test_set.jsonl"]

R3_SHA256 = "c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06"
CORE_SHA256 = "8726c6f782f2a57ddfd4c3b1557497349d912d3d06acd97c73983650fd9fc827"
FULL_VERSION = "sys-014-semantic-hardening-r4-full-draft"
FULL_STATUS = "DRAFT_PENDING_FINAL_REVIEW"
FORMAL_STATUS = "FORMAL_EXECUTABLE"
KNOWN_STATUS = "KNOWN_UNSUPPORTED_CONTROL"
MACHINE_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def _display(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _active_following_gap_references() -> list[str]:
    matches: list[str] = []
    roots = [ROOT / "backend/app", ROOT / "config", ROOT / "scripts/full_nlu"]
    excluded = {Path(__file__).resolve(), (FULL_NLU_DIR / "r4_known_unsupported_evidence.py").resolve()}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.resolve() not in excluded and path.suffix.lower() in {".py", ".yaml", ".yml", ".json"}:
                if "FOLLOWING_GAP_REQUIRED" in path.read_text(encoding="utf-8", errors="ignore"):
                    matches.append(path.relative_to(ROOT).as_posix())
    return sorted(matches)


def _active_poc_references() -> list[str]:
    forbidden = re.compile(r"sys014-poc7|poc7-v[12]|7-Intent|7 Intent|rbt3-exp|electra-exp", re.IGNORECASE)
    matches: list[str] = []
    for root in (ROOT / "backend/app", ROOT / "config"):
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".py", ".yaml", ".yml", ".json"}:
                if forbidden.search(path.read_text(encoding="utf-8", errors="ignore")):
                    matches.append(path.relative_to(ROOT).as_posix())
    return sorted(matches)


def validate(
    registry_path: Path = FULL_PATH,
    *,
    core_path: Path = CORE_PATH,
    r3_path: Path = R3_PATH,
    expansion_report_path: Path = EXPANSION_REPORT_PATH,
    adas_report_path: Path = ADAS_REPORT_PATH,
    other_report_path: Path = OTHER_REPORT_PATH,
) -> dict[str, Any]:
    errors: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(check_id: str, condition: bool, message: str) -> None:
        checks.append({"check_id": check_id, "status": "PASS" if condition else "FAIL", "message": message})
        if not condition:
            errors.append(f"{check_id}: {message}")

    core = load_yaml(core_path)
    full = load_yaml(registry_path)
    expansion = load_json(expansion_report_path)
    adas = load_json(adas_report_path)
    other = load_json(other_report_path)
    core_hash = sha256_file(core_path)
    r3_hash = sha256_file(r3_path)
    full_hash = sha256_file(registry_path)

    check("STRICT_YAML_PARSE", isinstance(full, dict), "full draft must parse as a unique-key YAML mapping")
    check("R3_SHA256_UNCHANGED", r3_hash == R3_SHA256, "R3 SHA256 changed")
    check("CORE_SHA256_UNCHANGED", core_hash == CORE_SHA256, "R4 core SHA256 changed")
    check("FULL_VERSION", full.get("registry_version") == FULL_VERSION, "full draft version mismatch")
    check("FULL_STATUS", full.get("semantic_freeze_status") == FULL_STATUS, "full draft status mismatch")
    check("FULL_OFFLINE", full.get("runtime_loading_allowed") is False, "full draft must remain offline")
    expected_parent = {
        "path": "data/nlu/spec/intent_registry_r4_core_draft.yaml",
        "registry_version": "sys-014-semantic-hardening-r4-core-draft",
        "sha256": CORE_SHA256,
        "inheritance_rule": "PRESERVE_CORE_AND_APPEND_EVIDENCE_BACKED_KNOWN_UNSUPPORTED_ONLY",
    }
    check("PARENT_REGISTRY", full.get("parent_registry") == expected_parent, "parent_registry mismatch")

    core_intents = core.get("intents", [])
    full_intents = full.get("intents", [])
    core_ids = [item.get("intent_id") for item in core_intents]
    full_ids = [item.get("intent_id") for item in full_intents]
    core_by_id = {item.get("intent_id"): item for item in core_intents}
    full_by_id = {item.get("intent_id"): item for item in full_intents}
    new_ids = full_ids[len(core_ids):] if full_ids[: len(core_ids)] == core_ids else []
    check("CORE_INTENT_PREFIX", full_ids[: len(core_ids)] == core_ids, "core intent IDs/order are not an exact prefix")
    check("CORE_INTENT_DEFINITIONS", all(full_by_id.get(intent_id) == item for intent_id, item in core_by_id.items()), "existing core intent changed")
    check("UNIQUE_INTENT_IDS", len(full_ids) == len(set(full_ids)), "intent IDs are not unique")

    formal_ids = [item["intent_id"] for item in full_intents if item.get("user_voice_scope_status") == FORMAL_STATUS]
    known_ids = [item["intent_id"] for item in full_intents if item.get("user_voice_scope_status") == KNOWN_STATUS]
    check("FORMAL_COUNT", len(formal_ids) == 71, f"formal intent count must be 71, got {len(formal_ids)}")
    check("FORMAL_IDS", formal_ids == core.get("formal_user_voice_intent_ids"), "formal intent IDs/order changed")
    check("FORMAL_PROJECTION", full.get("formal_user_voice_intent_ids") == formal_ids, "formal projection mismatch")
    check("KNOWN_PROJECTION", full.get("known_unsupported_control_intent_ids") == known_ids, "known projection mismatch")
    check("NEW_STATUS", all(full_by_id[item_id].get("user_voice_scope_status") == KNOWN_STATUS for item_id in new_ids), "new intent is not known unsupported")
    check("NEW_PROJECT_NATIVE", all(
        full_by_id[item_id].get("capability_origin") == "PROJECT_NATIVE"
        and full_by_id[item_id].get("vss_relation") == "NONE"
        and full_by_id[item_id].get("vss_capability_ids") == []
        for item_id in new_ids
    ), "new intent contains invalid or fabricated provenance")

    frames = extract_frames(MAC_PATHS, SOURCE_SCREEN_PATH)
    evidence = build_evidence(frames)
    evidence_ids = sorted(evidence["approved"])
    check("EVIDENCE_BACKED_NEW_IDS", sorted(new_ids) == evidence_ids, f"new/evidence ID mismatch: {sorted(set(new_ids) ^ set(evidence_ids))}")
    check("FRUNK_OPEN_ONLY", "FRUNK_OPEN" in new_ids and not ({"FRUNK_CLOSE", "FRUNK_SET_POSITION", "FRUNK_LOCK", "FRUNK_UNLOCK"} & set(full_ids)), "FRUNK boundary violated")
    check("FRUNK_CLOSE_PENDING", any(
        item.get("suggested_intent_id") == "FRUNK_CLOSE"
        and item.get("unique_sample_count") == 0
        and item.get("approval_status") == "PENDING_NO_REAL_DATA_EVIDENCE"
        for item in other.get("candidates", [])
    ), "FRUNK_CLOSE zero-evidence candidate missing")

    value_contracts = full.get("value_contracts", {})
    mode_contracts = full.get("mode_contracts", {})
    direction_contracts = full.get("direction_contracts", {})
    conditional_contracts = full.get("conditional_slot_contracts", {})
    families = full.get("capability_families", [])
    family_ids = {item.get("family_id") for item in families if isinstance(item, dict)}
    family_members = [intent_id for family in families if isinstance(family, dict) for intent_id in family.get("intents", [])]
    unresolved: list[str] = []
    slot_conflicts: list[str] = []
    invalid_machine_ids: list[str] = []
    semantic_groups: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    bool_modes: list[str] = []
    for name, values in mode_contracts.items():
        if not isinstance(values, list):
            unresolved.append(f"mode_contracts.{name}:not_list")
            continue
        for index, value in enumerate(values):
            if isinstance(value, bool) or not isinstance(value, str):
                bool_modes.append(f"{name}[{index}]={value!r}")
    for item in full_intents:
        intent_id = str(item.get("intent_id"))
        for field in ("intent_id", "canonical_action", "canonical_target", "control_attribute"):
            value = item.get(field)
            if not isinstance(value, str) or not MACHINE_ID_RE.fullmatch(value):
                invalid_machine_ids.append(f"{intent_id}.{field}={value!r}")
        semantic_groups[(item.get("canonical_action"), item.get("canonical_target"), item.get("control_attribute"))].append(intent_id)
        required = item.get("required_slots", [])
        optional = item.get("optional_slots", [])
        if not isinstance(required, list) or not isinstance(optional, list):
            slot_conflicts.append(f"{intent_id}:slots_not_lists")
            continue
        overlap = sorted(set(required) & set(optional))
        if overlap:
            slot_conflicts.append(f"{intent_id}:{overlap}")
        value_contract = item.get("value_contract")
        if value_contract not in (None, "NONE") and value_contract not in value_contracts:
            unresolved.append(f"{intent_id}:value_contract={value_contract}")
        if item.get("mode_contract") and item.get("mode_contract") not in mode_contracts:
            unresolved.append(f"{intent_id}:mode_contract={item.get('mode_contract')}")
        if item.get("direction_contract") and item.get("direction_contract") not in direction_contracts:
            unresolved.append(f"{intent_id}:direction_contract={item.get('direction_contract')}")
        if item.get("conditional_slot_contract") and item.get("conditional_slot_contract") not in conditional_contracts:
            unresolved.append(f"{intent_id}:conditional_slot_contract={item.get('conditional_slot_contract')}")
        if item.get("capability_family") not in family_ids:
            unresolved.append(f"{intent_id}:capability_family={item.get('capability_family')}")
    collisions = {"|".join(map(str, key)): ids for key, ids in semantic_groups.items() if len(ids) > 1}
    check("MACHINE_IDS", not invalid_machine_ids, f"invalid machine IDs: {invalid_machine_ids}")
    check("SEMANTIC_KEY_UNIQUE", not collisions, f"semantic collisions: {collisions}")
    check("CAPABILITY_FAMILY_COVERAGE", Counter(family_members) == Counter(full_ids), "family coverage must be exactly one-to-one")
    check("CONTRACT_REFERENCES", not unresolved, f"unresolved references: {unresolved}")
    check("SLOT_INTERSECTION", not slot_conflicts, f"slot conflicts: {slot_conflicts}")
    check("MODE_ENUM_TYPES", not bool_modes, f"invalid MODE enums: {bool_modes}")

    ontology = full.get("semantic_ontology", {})
    actions = sorted({item.get("canonical_action") for item in full_intents})
    targets = sorted({item.get("canonical_target") for item in full_intents})
    attributes = sorted({item.get("control_attribute") for item in full_intents})
    check("ONTOLOGY_ACTIONS", ontology.get("canonical_actions") == actions, "action ontology mismatch")
    check("ONTOLOGY_TARGETS", ontology.get("canonical_targets") == targets, "target ontology mismatch")
    check("ONTOLOGY_ATTRIBUTES", ontology.get("control_attributes") == attributes, "attribute ontology mismatch")

    origins = Counter(item.get("capability_origin") for item in full_intents)
    project_family_count = sum(
        bool(family.get("intents"))
        and all(full_by_id.get(intent_id, {}).get("capability_origin") == "PROJECT_NATIVE" for intent_id in family.get("intents", []))
        for family in families
    )
    stats = full.get("statistics", {})
    expected_stats = {
        "intent_count": len(full_intents),
        "semantic_intent_count": len(full_intents),
        "formal_user_voice_intent_count": len(formal_ids),
        "known_unsupported_control_intent_count": len(known_ids),
        "project_native_intent_count": origins["PROJECT_NATIVE"],
        "vss_derived_intent_count": origins["VSS"] + origins["VSS_AND_PROJECT"],
        "capability_family_count": len(families),
        "project_native_family_count": project_family_count,
    }
    check("STATISTICS", all(stats.get(key) == value for key, value in expected_stats.items()), f"statistics mismatch: expected {expected_stats}")

    check("FOLLOWING_GAP_CONTRACT_REMOVED", "FOLLOWING_GAP_REQUIRED" not in value_contracts, "dead value contract remains")
    check("FOLLOWING_GAP_CONTINUOUS_REMOVED", "FOLLOWING_GAP_REQUIRED" not in full.get("value_language_semantics", {}).get("continuous_numeric_contracts", []), "dead continuous contract reference remains")
    check("FOLLOWING_GAP_INTENT_REFS_REMOVED", all(item.get("value_contract") != "FOLLOWING_GAP_REQUIRED" for item in full_intents), "intent still references dead contract")
    active_following = _active_following_gap_references()
    active_poc = _active_poc_references()
    check("ACTIVE_FOLLOWING_GAP_REFERENCE_COUNT", not active_following, f"active references: {active_following}")
    check("ACTIVE_FULL_NLU_DEPENDENCY_COUNT", not active_poc, f"active PoC references: {active_poc}")

    expansion_ids = [item.get("intent_id") for item in expansion.get("new_intents", [])]
    check("EXPANSION_REPORT_COVERAGE", expansion_ids == new_ids, "expansion report intent order/coverage mismatch")
    check("EXPANSION_REPORT_EVIDENCE", all(item.get("unique_sample_count", 0) > 0 and 1 <= len(item.get("examples", [])) <= 5 for item in expansion.get("new_intents", [])), "new intent lacks report evidence")
    adas_ids = {item.get("suggested_intent_id") for item in adas.get("candidates", [])}
    other_ids = {item.get("suggested_intent_id") for item in other.get("candidates", [])}
    check("CANDIDATES_NOT_IN_REGISTRY", not ((adas_ids | other_ids) & set(new_ids)), "pending candidate entered registry")

    legacy_ids = {item.get("intent_id") for item in full.get("legacy_test_only", []) if isinstance(item, dict)}
    check("LEGACY_ID_DISJOINT", not (legacy_ids & set(full_ids)), "legacy ID duplicates semantic catalog")
    diff = sorted(set(changed_paths(core, full)))
    return {
        "status": "PASS" if not errors else "FAIL",
        "registry_version": full.get("registry_version"),
        "semantic_freeze_status": full.get("semantic_freeze_status"),
        "r3_path": _display(r3_path),
        "r3_sha256": r3_hash,
        "core_path": _display(core_path),
        "core_sha256": core_hash,
        "full_path": _display(registry_path),
        "full_sha256": full_hash,
        "metrics": {
            "SEMANTIC_INTENT_COUNT": len(full_ids),
            "FORMAL_USER_VOICE_INTENT_COUNT": len(formal_ids),
            "KNOWN_UNSUPPORTED_CONTROL_INTENT_COUNT": len(known_ids),
            "NEW_INTENT_COUNT": len(new_ids),
            "NEW_CAPABILITY_FAMILY_COUNT": len(families) - len(core.get("capability_families", [])),
            "PROJECT_NATIVE_INTENT_COUNT": origins["PROJECT_NATIVE"],
            "VSS_DERIVED_INTENT_COUNT": origins["VSS"] + origins["VSS_AND_PROJECT"],
            "CAPABILITY_FAMILY_COUNT": len(families),
            "SEMANTIC_KEY_COLLISION_COUNT": len(collisions),
            "UNRESOLVED_REFERENCE_COUNT": len(unresolved),
            "SLOT_INTERSECTION_COUNT": len(slot_conflicts),
            "INVALID_MODE_ENUM_COUNT": len(bool_modes),
            "ACTIVE_FOLLOWING_GAP_REFERENCE_COUNT": len(active_following),
            "ACTIVE_FULL_NLU_DEPENDENCY_COUNT": len(active_poc),
            "CHANGED_PATH_COUNT": len(diff),
        },
        "new_intent_ids": new_ids,
        "changed_paths": diff,
        "active_following_gap_references": active_following,
        "active_poc_references": active_poc,
        "checks": checks,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=FULL_PATH)
    args = parser.parse_args()
    try:
        result = validate(args.registry)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
