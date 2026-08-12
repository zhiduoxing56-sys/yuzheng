from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


EXPECTED_INPUT_HASHES = {
    "data/nlu/spec/intent_registry_r4_final.yaml": "d4f3d203308a5eb9a039fee31851c110b21bafc7727f23fd6f2b83edefadad4e",
    "初筛/full_nlu_source_screen_v1.jsonl": "59340fce2c394cb793a37ba2b301379f4ef9794c9301d0983c6b37680e09123c",
    "train_set.jsonl": "d1e9a63fa61ef2d5eec4ef543356fb53d653070916c5ceaf72962047f9aef681",
    "dev_set.jsonl": "02ccb2bae0fa1923fb0e3bcdd5d0c13635ac93cfd2880d8a8affd0481157efb1",
    "test_set.jsonl": "1b3e8243ea9a9bb544a18b571401c4a057f0246c07d26a3e2a638890d9300572",
}
EXPECTED_OUTPUT_FILES = {
    "nlu_mapping_r4_scope_v1.yaml",
    "full_nlu_gold_dryrun_v1.jsonl",
    "full_nlu_gold_dryrun_review_v1.jsonl",
    "full_nlu_gold_dryrun_quarantine_v1.jsonl",
    "full_nlu_gold_dryrun_stats_v1.json",
    "full_nlu_gold_dryrun_manifest_v1.json",
}
SCOPES = {"FORMAL_EXECUTABLE", "KNOWN_CONTROL_BYPASS", "NON_CONTROL", "UNKNOWN_OOD"}
POLARITIES = {"AFFIRMATIVE", "NEGATIVE", "CANCEL", "NOT_APPLICABLE"}
RULE_STATUSES = {"AUTO_ENABLED", "REVIEW_ONLY", "NO_RELIABLE_SOURCE_SAMPLE"}
HIGH_RISK_AREA_REQUIRED = {
    "DOOR_OPEN", "DOOR_CLOSE", "DOOR_SET_POSITION", "DOOR_LOCK", "DOOR_UNLOCK",
    "FOG_LIGHT_ON", "FOG_LIGHT_OFF",
}
HIGH_RISK_DIRECTION_REQUIRED = {"TURN_INDICATOR_ON", "TURN_INDICATOR_OFF", "LANE_CHANGE", "EVASIVE_STEER"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{path.name}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def validate_span(text: str, evidence: dict[str, Any], context: str) -> None:
    span = evidence.get("span")
    require(isinstance(span, list) and len(span) == 2 and all(isinstance(value, int) for value in span), f"{context}: invalid span")
    start, end = span
    require(0 <= start < end <= len(text), f"{context}: span out of range: {span} for {text!r}")
    require(text[start:end] == str(evidence.get("text")), f"{context}: evidence text/span mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate R4 Full NLU dry-run artifacts independently.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = (args.output_dir or root / "outputs/full_nlu_r4_scope_v1").resolve()

    require(output_dir.is_dir(), f"missing output directory: {output_dir}")
    actual_output_files = {path.name for path in output_dir.iterdir() if path.is_file()}
    require(actual_output_files == EXPECTED_OUTPUT_FILES,
            f"unexpected output file set: missing={EXPECTED_OUTPUT_FILES-actual_output_files}, extra={actual_output_files-EXPECTED_OUTPUT_FILES}")

    manifest = json.loads((output_dir / "full_nlu_gold_dryrun_manifest_v1.json").read_text(encoding="utf-8"))
    stats = json.loads((output_dir / "full_nlu_gold_dryrun_stats_v1.json").read_text(encoding="utf-8"))
    mapping = yaml.safe_load((output_dir / "nlu_mapping_r4_scope_v1.yaml").read_text(encoding="utf-8"))
    registry = yaml.safe_load((root / "data/nlu/spec/intent_registry_r4_final.yaml").read_text(encoding="utf-8"))

    require(manifest["training_performed"] is False, "training must not be performed")
    require(manifest["review_auto_repaired"] is False, "review must not be auto-repaired")
    require(manifest["final_gold_declared"] is False, "dry-run must not declare final Gold")
    require(manifest["warnings"] == ["GUIDANCE_VERSION_METADATA_MISMATCH"], "guidance mismatch warning missing")
    require(mapping["warnings"] == ["GUIDANCE_VERSION_METADATA_MISMATCH"], "mapping guidance warning missing")
    require(mapping["fuzzy_matching_prohibited"] is True, "fuzzy matching must be prohibited")
    require(mapping["unknown_ood_is_fallback"] is False, "UNKNOWN_OOD must not be a fallback")

    for relative, expected in EXPECTED_INPUT_HASHES.items():
        actual = sha256_file(root / relative)
        require(actual == expected, f"input hash mismatch: {relative}")
        require(manifest["input_hashes"].get(relative) == expected, f"manifest input hash mismatch: {relative}")
    for filename, expected in manifest["output_hashes"].items():
        require(filename != "full_nlu_gold_dryrun_manifest_v1.json", "manifest must not self-hash")
        require(sha256_file(output_dir / filename) == expected, f"output hash mismatch: {filename}")
    require(set(manifest["output_hashes"]) == EXPECTED_OUTPUT_FILES - {"full_nlu_gold_dryrun_manifest_v1.json"},
            "manifest output hash set mismatch")

    accounting = manifest["record_accounting"]
    require(accounting == {
        "screen_pipeline_records": 20899,
        "unscreened_quarantine_audit_records": 2,
        "audited_records": 20901,
        "distribution_denominator": 20899,
        "unscreened_excluded_from_all_mapping_distributions": True,
    }, "20,899/20,901 accounting mismatch")

    registry_ids = [item["intent_id"] for item in registry["intents"]]
    registry_by_id = {item["intent_id"]: item for item in registry["intents"]}
    require(registry["registry_version"] == "sys-014-semantic-hardening-r4-final", "top-level registry version mismatch")
    require(len(registry_ids) == len(set(registry_ids)) == 71, "registry must contain 71 unique intents")
    require(mapping["registry_version"] == registry["registry_version"], "mapping registry version mismatch")
    formal_rules = mapping["formal_rules"]
    require(len(formal_rules) == 71, "mapping must contain exactly 71 Formal rule entries")
    require({rule["intent_id"] for rule in formal_rules} == set(registry_ids), "mapping Formal intent set mismatch")
    require(len({rule["rule_id"] for rule in formal_rules}) == 71, "rule_id values must be unique")
    rule_by_intent = {rule["intent_id"]: rule for rule in formal_rules}
    rule_by_id = {rule["rule_id"]: rule for rule in formal_rules}
    authorized_expressions: set[str] = set()
    for relative in ("train_set.jsonl", "dev_set.jsonl", "test_set.jsonl"):
        for row in read_jsonl(root / relative):
            authorized_expressions.add(row["query"])
            authorized_expressions.update(part for part in row.get("split_sens", []) if isinstance(part, str))
    screen_rows = read_jsonl(root / "初筛/full_nlu_source_screen_v1.jsonl")
    authorized_expressions.update(row["原始文本"] for row in screen_rows)
    for rule in formal_rules:
        require(rule["rule_status"] in RULE_STATUSES, f"invalid rule status: {rule['intent_id']}")
        for field in ("allowed_text_evidence", "allowed_mac_auxiliary_evidence", "explicit_exclusions",
                      "slot_extraction_rule", "contract_rule", "manual_review_conditions", "corpus_evidence"):
            require(field in rule, f"{rule['intent_id']}: missing {field}")
        examples = rule["allowed_text_evidence"]["deterministic_source_examples"]
        require(all(example in authorized_expressions for example in examples), f"{rule['intent_id']}: invented source example")
        if rule["rule_status"] == "NO_RELIABLE_SOURCE_SAMPLE":
            require(not examples, f"{rule['intent_id']}: no-source rule must not contain deterministic examples")

    auto_rows = read_jsonl(output_dir / "full_nlu_gold_dryrun_v1.jsonl")
    review_rows = read_jsonl(output_dir / "full_nlu_gold_dryrun_review_v1.jsonl")
    quarantine_rows = read_jsonl(output_dir / "full_nlu_gold_dryrun_quarantine_v1.jsonl")
    require(all(row["build_status"] == "AUTO_CORE_CANDIDATE" for row in auto_rows), "auto file contains non-auto status")
    require(all(row["build_status"] in {"BOUNDARY_REVIEW", "SEMANTIC_REVIEW"} for row in review_rows), "review file status mismatch")
    require(all(row["build_status"] in {"SOURCE_QUARANTINE", "MALFORMED_EXCLUDED"} for row in quarantine_rows), "quarantine file status mismatch")

    unscreened = [row for row in quarantine_rows if row.get("excluded_from_mapping_stats")]
    require(len(unscreened) == 2, "exactly two unscreened audit records required")
    require({(row["provenance"]["source_file"], row["provenance"]["source_id"]) for row in unscreened}
            == {("test_set.jsonl", "226"), ("test_set.jsonl", "251")}, "unscreened row identity mismatch")
    for row in unscreened:
        require(row["failure_reasons"] == ["UNSCREENED_SOURCE_ROW"], "unscreened row reason mismatch")
        require(row["sub_intents"] == [], "unscreened row must not have labels")

    mapped_rows = auto_rows + review_rows + [row for row in quarantine_rows if not row.get("excluded_from_mapping_stats")]
    require(len(mapped_rows) == 20899, f"screen partition count mismatch: {len(mapped_rows)}")
    require(len(auto_rows) + len(review_rows) + len(quarantine_rows) == 20901, "audited record count mismatch")
    screen_indexes = [row["screen_index"] for row in mapped_rows]
    require(len(set(screen_indexes)) == 20899 and set(screen_indexes) == set(range(1, 20900)), "screen indexes not bijective")
    require(len({row["sample_id"] for row in mapped_rows}) == 20899, "screen sample IDs not unique")

    status_counts: Counter[str] = Counter(row["build_status"] for row in mapped_rows)
    scope_counts: Counter[str] = Counter()
    polarity_counts: Counter[str] = Counter()
    slot_counts: Counter[str] = Counter()
    rule_hits: Counter[str] = Counter()
    scope_record_counts: Counter[str] = Counter()
    formal_routing_records: Counter[str] = Counter()
    auto_formal_count = 0
    for row in mapped_rows:
        require(row["sentence_structure"] in {"SINGLE", "MULTI"}, f"invalid sentence structure: {row['sample_id']}")
        record_scopes: set[str] = set()
        for sub in row.get("sub_intents", []):
            scope = sub.get("scope")
            require(scope in SCOPES, f"invalid scope: {row['sample_id']}")
            require(sub.get("polarity") in POLARITIES, f"invalid polarity: {row['sample_id']}")
            require(isinstance(sub.get("triggered_evidence"), list) and sub["triggered_evidence"], f"missing triggered evidence: {row['sample_id']}")
            for item in sub["triggered_evidence"]:
                validate_span(sub["text"], item, f"{row['sample_id']}:{scope}")
            scope_counts[scope] += 1
            record_scopes.add(scope)
            polarity_counts[sub["polarity"]] += 1
            slot_counts.update(sub.get("slots", {}).keys())
            if scope == "FORMAL_EXECUTABLE":
                intent_id = sub.get("intent_id")
                require(intent_id in registry_by_id, f"unknown Formal intent: {intent_id}")
                require(sub.get("rule_id") == rule_by_intent[intent_id]["rule_id"], f"rule_id mismatch: {row['sample_id']}")
                declared_slots = set(registry_by_id[intent_id].get("required_slots", [])) | set(registry_by_id[intent_id].get("optional_slots", []))
                require(set(sub.get("slots", {})) <= declared_slots, f"undeclared Formal slot: {row['sample_id']}")
                for slot_name, slot in sub.get("slots", {}).items():
                    span = slot.get("span")
                    require(isinstance(span, list) and len(span) == 2, f"slot span missing: {row['sample_id']}:{slot_name}")
                    require(sub["text"][span[0]:span[1]] == str(slot["原始值"]), f"slot not locatable: {row['sample_id']}:{slot_name}")
                if row["build_status"] == "AUTO_CORE_CANDIDATE":
                    auto_formal_count += 1
                    require(rule_by_intent[intent_id]["rule_status"] == "AUTO_ENABLED", f"auto Formal used disabled rule: {intent_id}")
                    evidence_kinds = {item["kind"] for item in sub["triggered_evidence"]}
                    require("action" in evidence_kinds and "object" in evidence_kinds, f"auto Formal lacks action/object evidence: {row['sample_id']}")
                    require(sub.get("contract_status") == "COMPLETE" and not sub.get("contract_failures"), f"auto Formal contract not complete: {row['sample_id']}")
                    checks = sub.get("acceptance_checks", {})
                    require(checks.get("contract_check") == "PASS" and checks.get("source_conflict") is False,
                            f"auto Formal contract/source checks failed: {row['sample_id']}")
                    require(all(checks.get(key) is True for key in (
                        "scope_unique", "intent_unique", "action_evidence_present", "object_evidence_present",
                        "all_saved_slots_locatable", "special_boundary_clear",
                    )), f"auto Formal acceptance checks failed: {row['sample_id']}")
                    require(intent_id not in HIGH_RISK_AREA_REQUIRED or "AREA" in sub["slots"], f"high-risk area missing: {row['sample_id']}")
                    require(intent_id not in HIGH_RISK_DIRECTION_REQUIRED or "DIRECTION" in sub["slots"], f"high-risk direction missing: {row['sample_id']}")
                    rule_hits[sub["rule_id"]] += 1
            elif scope == "KNOWN_CONTROL_BYPASS":
                for prohibited in ("intent_id", "canonical_action", "canonical_target", "VALUE", "MODE", "AREA"):
                    require(prohibited not in sub, f"Bypass contains prohibited field {prohibited}: {row['sample_id']}")
                require(sub.get("slots") == {}, f"Bypass slots must be empty: {row['sample_id']}")
            else:
                require("intent_id" not in sub, f"non-Formal scope contains intent_id: {row['sample_id']}")
                if scope == "UNKNOWN_OOD":
                    require(any(item["kind"] == "explicit_ood_pattern" for item in sub["triggered_evidence"]),
                            f"UNKNOWN_OOD used without explicit OOD evidence: {row['sample_id']}")
        scope_record_counts.update(record_scopes)
        if row["build_status"] == "AUTO_CORE_CANDIDATE" and "FORMAL_EXECUTABLE" in record_scopes:
            formal_routing_records["auto"] += 1
        if row["build_status"] in {"BOUNDARY_REVIEW", "SEMANTIC_REVIEW"} and row.get("diagnostic_formal_rule_ids"):
            formal_routing_records["review"] += 1
        if row["build_status"] == "SOURCE_QUARANTINE" and row.get("diagnostic_formal_rule_ids"):
            formal_routing_records["quarantine"] += 1

    require(dict(status_counts) == {key: value for key, value in stats["build_status_counts"].items() if value}, "build status stats mismatch")
    require(all(stats["scope_sub_intent_counts"].get(scope, 0) == scope_counts[scope] for scope in SCOPES), "scope stats mismatch")
    require(all(stats["scope_record_counts"].get(scope, 0) == scope_record_counts[scope] for scope in SCOPES), "scope record stats mismatch")
    require(all(stats["polarity_counts"].get(key, 0) == polarity_counts[key] for key in POLARITIES), "polarity stats mismatch")
    require(stats["slot_counts"] == dict(slot_counts), "slot stats mismatch")
    require(stats["formal_outcome_counts"].get("AUTO_CANDIDATE", 0) == auto_formal_count, "Formal auto count mismatch")
    require(stats["formal_routing_summary"] == {
        "auto_candidate_records_with_formal": formal_routing_records["auto"],
        "auto_candidate_formal_sub_intents": auto_formal_count,
        "review_records_with_formal_or_candidate": formal_routing_records["review"],
        "review_labeled_formal_sub_intents": stats["formal_outcome_counts"].get("REVIEW", 0),
        "quarantine_records_with_possible_formal": formal_routing_records["quarantine"],
    }, "Formal routing summary mismatch")
    require(stats["source_conflict_counts"] == {
        "screen_category_SOURCE_CONFLICT_REVIEW": 274,
        "source_annotation_status_SOURCE_CONFLICT": 266,
    }, "source conflict counts mismatch")
    require(stats["unscreened_source_row_count"] == 2, "unscreened stats mismatch")
    require(set(stats["failure_category_totals"]) == {"NO_RELIABLE_SOURCE_SAMPLE", "SEMANTIC_MAPPING_FAILED", "CONTRACT_CHECK_FAILED"},
            "coverage/mapping/contract failure categories must remain separate")
    require(stats["formal_coverage_summary"]["intent_count"] == 71, "Formal coverage denominator mismatch")
    require(stats["formal_coverage_summary"]["no_reliable_source_sample_intent_count"]
            == sum(rule["rule_status"] == "NO_RELIABLE_SOURCE_SAMPLE" for rule in formal_rules), "no-source count mismatch")
    require(all(stats["rule_hit_counts"][rule_id] == rule_hits[rule_id] for rule_id in rule_by_id), "rule hit stats mismatch")
    require(manifest["output_counts"] == {
        "auto_core_candidate": len(auto_rows),
        "review": len(review_rows),
        "quarantine_and_excluded_including_unscreened": len(quarantine_rows),
    }, "manifest output counts mismatch")

    print(json.dumps({
        "validation": "PASS",
        "screen_pipeline_records": len(mapped_rows),
        "audited_records": len(auto_rows) + len(review_rows) + len(quarantine_rows),
        "auto_core_candidates": len(auto_rows),
        "auto_formal_sub_intents": auto_formal_count,
        "auto_enabled_formal_intents": stats["formal_coverage_summary"]["auto_enabled_intent_count"],
        "unknown_ood_auto_count": scope_counts["UNKNOWN_OOD"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
