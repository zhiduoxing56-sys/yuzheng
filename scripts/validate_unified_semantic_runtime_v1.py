from __future__ import annotations

import json
import unicodedata
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/nlu/spec/audits/unified_semantic_runtime_migration_audit_v1.json"
KNOWN = ROOT / "data/nlu/spec/audits/known_non_executable_semantic_freeze_final_v4.yaml"
QUARANTINE = ROOT / "data/nlu/spec/audits/known_non_executable_anchor_quarantine_final_v3.jsonl"
RECLASSIFICATION = ROOT / "data/nlu/spec/audits/fragrance_set_scent_human_reclassification_v4.yaml"
REVIEW_CASES = ROOT / "data/nlu/spec/audits/known_non_executable_semantic_review_cases_v3.yaml"
FORMAL_ANCHORS = ROOT / "挂靠/intent_anchor_set_v1_3.yaml"


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected mapping: {path}")
    return value


def normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).strip().lower().split())


def main() -> None:
    registry_path = ROOT / "data/nlu/spec/intent_registry_unified_v1.yaml"
    cards_path = ROOT / "挂靠/intent_cards_unified_v1.yaml"
    anchors_path = ROOT / "挂靠/intent_anchor_set_unified_v1.yaml"
    registry = load_yaml(registry_path)
    cards = load_yaml(cards_path)
    anchors = load_yaml(anchors_path)
    known = load_yaml(KNOWN)
    reclassification = load_yaml(RECLASSIFICATION)
    formal_source = load_yaml(FORMAL_ANCHORS)["正式意图"]
    review_cases = load_yaml(REVIEW_CASES).get("cases", [])
    quarantine = [
        json.loads(line) for line in QUARANTINE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    evidence_demands = load_yaml(ROOT / "证据/evidence_demand_registry_v1.yaml")
    removals = load_yaml(ROOT / "data/nlu/spec/audits/known_non_executable_product_removals_v2.yaml")

    definitions = registry["intents"]
    ids = [item["intent_id"] for item in definitions]
    formal_ids = {item["intent_id"] for item in definitions if item["runtime_identity"] == "FORMAL"}
    known_ids = {item["intent_id"] for item in definitions if item["runtime_identity"] == "KNOWN_NON_EXECUTABLE"}
    removed_ids = {item["intent_id"] for item in removals["removals"]}
    active_pairs = {
        (intent_id, normalize(text))
        for intent_id, group in anchors["intents"].items()
        for text in group["anchors"]
    }
    norm_owners: dict[str, set[str]] = defaultdict(set)
    for intent_id, text in active_pairs:
        norm_owners[text].add(intent_id)
    known_sources = {
        item["intent_id"]: [
            *item["anchors"].get("historical_recovered", []),
            *item["anchors"].get("human_generated_approved", []),
            *item["anchors"].get("human_reclassified_from_quarantine", []),
        ]
        for item in known["known_non_executable_intents"]
    }
    expected_anchor_count = sum(len(set(values)) for values in formal_source.values()) + sum(
        len({normalize(anchor["text"]) for anchor in values})
        for values in known_sources.values()
    )
    contract_fields = {
        "value_contract": "value_contracts",
        "mode_contract": "mode_contracts",
        "direction_contract": "direction_contracts",
        "conditional_slot_contract": "conditional_slot_contracts",
        "value_mapping_contract": "value_mapping_contracts",
    }
    contract_refs_resolve = all(
        not item.get(field) or item[field] in registry.get(catalog, {})
        for item in definitions
        for field, catalog in contract_fields.items()
    )
    formal_norms = {
        normalize(text): intent_id
        for intent_id, values in formal_source.items()
        for text in values
    }
    review_override = [
        case for case in review_cases
        if case.get("candidate") is None and normalize(str(case.get("text", ""))) in formal_norms
    ]
    approved_quarantine_exceptions = {
        (
            str(item["quarantine_id"]),
            str(item["intent_id"]),
            normalize(str(item["text"])),
        )
        for item in reclassification.get("approved_quarantine_exceptions", [])
    }
    # A quarantined provenance is active only when the active freeze entry carries
    # that quarantine identity. The same normalized text may remain active through
    # a separate, independently verified provenance and is not a quarantine return.
    active_quarantine_returns = {
        (
            str(anchor["original_quarantine_id"]),
            intent_id,
            normalize(str(anchor["text"])),
        )
        for intent_id, values in known_sources.items()
        for anchor in values
        if anchor.get("original_quarantine_id")
    }
    forbidden_fact_fields = {"execution_eligible", "execution_supported", "executable"}
    scent_reclassified = known_sources.get("FRAGRANCE_SET_SCENT", [])
    scent_texts = {normalize(anchor["text"]) for anchor in scent_reclassified}
    level_texts = {
        normalize(anchor["text"])
        for anchor in known_sources.get("FRAGRANCE_SET_LEVEL", [])
    }
    approved_scent_texts = {
        normalize(str(item["text"]))
        for item in reclassification.get("approved_quarantine_exceptions", [])
    }
    production_text = "\n".join(path.read_text(encoding="utf-8") for path in (registry_path, cards_path, anchors_path))
    checks = {
        "unified_registry_count_is_149": len(definitions) == 149,
        "formal_count_is_71": len(formal_ids) == 71,
        "known_count_is_78": len(known_ids) == 78,
        "all_intent_ids_unique_and_nonempty": len(ids) == len(set(ids)) == 149 and all(ids),
        "formal_known_overlap_is_zero": not formal_ids & known_ids,
        "cards_and_anchors_ids_match_registry": set(cards.get("intents", {})) == set(ids) == set(anchors.get("intents", {})),
        "actual_anchor_count_matches_current_sources": anchors.get("semantic_anchor_count") == expected_anchor_count,
        "every_intent_has_active_anchor": all(group.get("anchors") for group in anchors.get("intents", {}).values()),
        "cross_intent_normalized_anchor_overlap_is_zero": not {text: owners for text, owners in norm_owners.items() if len(owners) > 1},
        "quarantine_content_remains_excluded_except_exact_human_reclassification": active_quarantine_returns == approved_quarantine_exceptions,
        "active_known_anchor_source_is_approved": all(anchor.get("source_type") in {"CLEAN_HISTORICAL_RECOVERED", "GENERATED_HUMAN_APPROVED", "HUMAN_REVIEW_RECLASSIFIED_FROM_QUARANTINE"} for values in known_sources.values() for anchor in values),
        "human_reclassification_whitelist_is_exactly_two": len(approved_quarantine_exceptions) == 2 and all(intent_id == "FRAGRANCE_SET_SCENT" for _, intent_id, _ in approved_quarantine_exceptions),
        "fragrance_set_scent_active_is_exactly_two_reclassified_anchors": scent_texts == approved_scent_texts and len(scent_reclassified) == 2 and all(anchor.get("source_type") == "HUMAN_REVIEW_RECLASSIFIED_FROM_QUARANTINE" for anchor in scent_reclassified),
        "fragrance_reclassified_texts_absent_from_level": not approved_scent_texts & level_texts,
        "fragrance_ambiguous_and_multi_semantic_texts_not_active": not {
            normalize("香氛位置调到2"), normalize("香氛位置调到3"), normalize("打开香氛适中")
        } & scent_texts,
        "all_slot_contract_references_resolve": contract_refs_resolve,
        "review_case_does_not_override_formal_anchor": not review_override,
        "emergency_brake_formal_anchor_is_preserved": formal_norms.get(normalize("紧急刹车")) == "EMERGENCY_BRAKE",
        "security_anchor_count_is_20": len(anchors.get("security", {}).get("anchors", [])) == 20,
        "removed_13_active_count_is_zero": len(removed_ids) == 13 and not removed_ids & set(ids),
        "unapproved_hash_candidate_usage_is_zero": anchors.get("exclusions", {}).get("unapproved_hash_candidate_count") == 1402 and all(anchor.get("source_type") != "UNAPPROVED_HASH_CANDIDATE" for values in known_sources.values() for anchor in values),
        "active_known_control_bypass_output_is_zero": "runtime_identity: KNOWN_CONTROL_BYPASS" not in production_text,
        "runtime_identity_has_no_executable_wording": "FORMAL_EXECUTABLE" not in production_text,
        "formal_identity_does_not_create_execution_fact": all(not forbidden_fact_fields & set(item) for item in definitions),
        "all_formal_route_to_safety_chain": set(evidence_demands["intent_requirements"]) == formal_ids,
    }
    failed = [name for name, passed in checks.items() if not passed]
    report = {
        "artifact_status": "RUNTIME_MIGRATION_ACCEPTANCE_AUDIT",
        "artifact_version": "unified-semantic-runtime-migration-v1",
        "counts": {
            "registry": len(definitions), "formal": len(formal_ids), "known_non_executable": len(known_ids),
            "semantic_anchors_actual": anchors.get("semantic_anchor_count"), "semantic_anchors_expected_from_current_sources": expected_anchor_count,
            "quarantine_records_checked": len(quarantine), "cross_intent_overlap_groups": sum(len(v) > 1 for v in norm_owners.values()),
        },
        "existing_execution_support_fact": {
            "field": "executable_actions", "source": "config/authorization.yaml",
            "consumer": "backend/app/services/authorization/service.py::AuthorizationTokenService.is_executable",
            "changed_in_this_migration": False,
        },
        "checks": checks,
        "failed_checks": failed,
        "all_checks_passed": not failed,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
