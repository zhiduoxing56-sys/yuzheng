"""Validate immutable SYS-014 PoC7 v2, including balance, provenance and parent integrity."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

import freeze_sys014_poc7_v2 as freeze
import validate_nlu_dataset as source_validator


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FROZEN = ROOT / "data/nlu/poc/frozen/sys014-poc7-v2"


def load(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def cross_count(rows_by_split: dict[str, list[dict[str, Any]]], key_fn) -> int:
    seen: dict[str, set[str]] = defaultdict(set)
    for split, rows in rows_by_split.items():
        for row in rows:
            seen[key_fn(row)].add(split)
    return sum(len(splits) > 1 for splits in seen.values())


def semantic_signature(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("intent_structure"), row.get("scope_label"), row.get("intent"), row.get("negated"),
        tuple((segment.get("intent"), segment.get("negated")) for segment in row.get("segments", [])),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, default=DEFAULT_FROZEN)
    args = parser.parse_args()
    frozen = args.frozen.resolve()
    file_paths = {
        "TRAIN": frozen / "train.jsonl",
        "VALIDATION": frozen / "validation.jsonl",
        "TEST": frozen / "test.jsonl",
        "SAFETY_GOLD": frozen / "safety_gold.jsonl",
    }
    report_names = (
        "dataset_manifest.json", "split_report.md", "leakage_audit.md",
        "split_group_balance_diagnosis.md", "v1_to_v2_split_diff.md", "README.md",
    )
    missing = [str(path) for path in [*file_paths.values(), *(frozen / name for name in report_names)] if not path.is_file() or path.stat().st_size == 0]
    if missing:
        print(json.dumps({"missing_artifacts": missing}, ensure_ascii=False, indent=2))
        return 1

    manifest = json.loads((frozen / "dataset_manifest.json").read_text(encoding="utf-8"))
    rows_by_split = {split: load(path) for split, path in file_paths.items()}
    candidate_splits = {split: rows_by_split[split] for split in freeze.SPLITS}
    candidate = [row for split in freeze.SPLITS for row in candidate_splits[split]]
    safety = rows_by_split["SAFETY_GOLD"]
    all_rows = candidate + safety

    registry = yaml.safe_load(freeze.REGISTRY_PATH.read_text(encoding="utf-8"))
    schema = json.loads(freeze.SCHEMA_PATH.read_text(encoding="utf-8"))
    intent_map = {item["intent_id"]: item for item in registry["intents"]}
    area_values = set(registry["area_catalog"])
    row_errors: list[str] = []
    span_failures = 0
    registry_failures = 0
    for split, rows in rows_by_split.items():
        for row in rows:
            errors, span_count, registry_count = source_validator.validate_row(
                row, registry_version=registry["registry_version"], intent_map=intent_map,
                area_values=area_values, mode_contracts=registry.get("mode_contracts", {}),
                schema=schema, expected_split=split,
            )
            row_errors.extend(errors)
            span_failures += span_count
            registry_failures += registry_count
    structure_markers = (
        "schema ", "invalid intent_structure", "invalid scope_label", "MULTI requires",
        "segment.negated must be boolean", "non-MULTI record must have no segments",
        "in-scope SINGLE negated must be boolean", "boundary/ambiguous record requires",
        "negated SINGLE requires", "negated segment lacks",
    )
    structure_failures = sum(any(marker in error for marker in structure_markers) for error in row_errors)
    other_row_failures = max(0, len(row_errors) - span_failures - registry_failures - structure_failures)

    ids = [row["sample_id"] for row in all_rows]
    texts = [row["text"] for row in all_rows]
    duplicate_id_failures = len(ids) - len(set(ids))
    duplicate_text_failures = len(texts) - len(set(texts))
    unassigned_count = sum(row.get("split") == "UNASSIGNED" for row in all_rows)

    exact_cross = cross_count(candidate_splits, lambda row: row["text"])
    normalized_cross = cross_count(candidate_splits, lambda row: freeze.normalized_text(row["text"]))
    template_cross = cross_count(candidate_splits, freeze.template_signature)
    mechanical_cross = cross_count(candidate_splits, freeze.mechanical_signature)
    family_cross = cross_count(candidate_splits, lambda row: row["paraphrase_family_id"])

    groups = freeze.build_groups(candidate)
    sample_split = {row["sample_id"]: row["split"] for row in candidate}
    group_split_sets = {
        group.group_id: {sample_split[row["sample_id"]] for row in group.rows} for group in groups
    }
    split_group_leakage = sum(len(splits) > 1 for splits in group_split_sets.values())
    assignments = {group_id: next(iter(splits)) for group_id, splits in group_split_sets.items() if len(splits) == 1}
    assignment_digest = freeze.sha256_bytes(
        "\n".join(f"{key}:{assignments[key]}" for key in sorted(assignments)).encode("utf-8")
    )
    test_asset_in_train = sum(row["source_ref"]["source_type"] == "TEST_ASSET" for row in candidate_splits["TRAIN"])

    source_candidate = freeze.load_jsonl(freeze.CANDIDATE_PATH)
    expected_candidate, expected_changes = freeze.refine_synthetic_families(source_candidate)
    expected_map = {row["sample_id"]: {**row, "split": "UNASSIGNED"} for row in expected_candidate}
    frozen_map = {row["sample_id"]: {**row, "split": "UNASSIGNED"} for row in candidate}
    source_copy_failures = int(expected_map != frozen_map)
    changed_ids = {item["sample_id"] for item in expected_changes}
    forbidden_family_change_failures = sum(
        expected_map[row["sample_id"]]["paraphrase_family_id"] != row["paraphrase_family_id"]
        or (
            row["sample_id"] in changed_ids
            and next(item for item in source_candidate if item["sample_id"] == row["sample_id"])["source_ref"]["source_type"] != "SYNTHETIC_TEMPLATE"
        )
        for row in candidate
    )
    source_safety = freeze.load_jsonl(freeze.SAFETY_PATH)
    safety_copy_failures = int(source_safety != safety)
    parent_safety = freeze.load_jsonl(freeze.PARENT_PATH / "safety_gold.jsonl")
    safety_copy_failures += int(parent_safety != safety)

    safety_ids = {row["sample_id"] for row in safety}
    safety_texts = {freeze.normalized_text(row["text"]) for row in safety}
    safety_families = {row["paraphrase_family_id"] for row in safety}
    safety_isolation_failures = (
        len(safety_ids & {row["sample_id"] for row in candidate})
        + len(safety_texts & {freeze.normalized_text(row["text"]) for row in candidate})
        + len(safety_families & {row["paraphrase_family_id"] for row in candidate})
    )

    family_signatures: dict[str, set[tuple[Any, ...]]] = defaultdict(set)
    for row in all_rows:
        family_signatures[row["paraphrase_family_id"]].add(semantic_signature(row))
    family_semantic_failures = sum(len(signatures) > 1 for signatures in family_signatures.values())

    split_counts = {split: len(rows_by_split[split]) for split in file_paths}
    family_counts = {split: len({row["paraphrase_family_id"] for row in candidate_splits[split]}) for split in freeze.SPLITS}
    group_counts = Counter(assignments.values())
    manifest_count_failures = sum([
        split_counts["TRAIN"] != manifest.get("train_count"),
        split_counts["VALIDATION"] != manifest.get("validation_count"),
        split_counts["TEST"] != manifest.get("test_count"),
        split_counts["SAFETY_GOLD"] != manifest.get("safety_gold_count"),
        family_counts["TRAIN"] != manifest.get("train_family_count"),
        family_counts["VALIDATION"] != manifest.get("validation_family_count"),
        family_counts["TEST"] != manifest.get("test_family_count"),
        group_counts["TRAIN"] != manifest.get("train_split_group_count"),
        group_counts["VALIDATION"] != manifest.get("validation_split_group_count"),
        group_counts["TEST"] != manifest.get("test_split_group_count"),
        len(expected_changes) != manifest.get("grouping_strategy", {}).get("family_refined_sample_count"),
        manifest.get("dataset_version") != freeze.DATASET_VERSION,
        manifest.get("parent_dataset_version") != freeze.PARENT_DATASET_VERSION,
    ])
    manifest_digest_failures = int(assignment_digest != manifest.get("grouping_strategy", {}).get("split_group_assignment_digest_sha256"))
    current_stats = {split: freeze.split_statistics(candidate_splits[split]) for split in freeze.SPLITS}
    manifest_statistics_failures = int(current_stats != manifest.get("statistics"))

    manifest_hash_failures = 0
    for relative, expected in manifest.get("file_sha256", {}).items():
        path = ROOT / relative if "/" in relative else frozen / relative
        if not path.is_file() or freeze.sha256_file(path) != expected:
            manifest_hash_failures += 1
    parent_integrity_failures = int(freeze.parent_hashes() != manifest.get("parent_integrity_sha256"))

    state = freeze.assignment_state(groups, assignments, {group.group_id: freeze.group_vector(group) for group in groups})
    hard_balance_failures = len(freeze.hard_deficits(state))
    ratio_balance_failures = 0
    for intent in freeze.POC_INTENTS:
        total_positive = sum(current_stats[split]["intent_coverage"][intent]["positive_single"] for split in freeze.SPLITS)
        shares = {split: current_stats[split]["intent_coverage"][intent]["positive_single"] / total_positive for split in freeze.SPLITS}
        ratio_balance_failures += int(not 0.60 <= shares["TRAIN"] <= 0.75)
        ratio_balance_failures += int(not 0.10 <= shares["VALIDATION"] <= 0.20)
        ratio_balance_failures += int(not 0.10 <= shares["TEST"] <= 0.20)
    total_candidate = len(candidate)
    overall_ratio_failures = sum(abs(split_counts[split] / total_candidate - freeze.TARGET_RATIOS[split]) > 0.025 for split in freeze.SPLITS)
    multi_coverage_failures = sum(
        current_stats[split]["intent_coverage"][intent]["multi_segment_mentions"] < minimum
        for split, minimum in (("TRAIN", 1), ("VALIDATION", 2), ("TEST", 2))
        for intent in freeze.POC_INTENTS
    )
    wsp_value_failures = sum(
        not any(row.get("intent") == "WINDOW_SET_POSITION" and any(slot["slot_type"] == "VALUE" for slot in row.get("slots", [])) for row in candidate_splits[split])
        for split in ("VALIDATION", "TEST")
    )
    window_open_value_failures = sum(
        row.get("intent") == "WINDOW_OPEN" and any(slot["slot_type"] == "VALUE" for slot in row.get("slots", []))
        for row in candidate
    )
    balance_failures = hard_balance_failures + ratio_balance_failures + overall_ratio_failures + multi_coverage_failures + wsp_value_failures + window_open_value_failures
    negated_soft_target_blocked_count = sum(
        not (
            current_stats["TRAIN"]["intent_coverage"][intent]["negated_single"] >= 8
            and current_stats["VALIDATION"]["intent_coverage"][intent]["negated_single"] >= 2
            and current_stats["TEST"]["intent_coverage"][intent]["negated_single"] >= 2
        )
        for intent in freeze.POC_INTENTS
    )

    regenerated_groups, regenerated_assignments, regenerated_rows, regenerated_safety, regenerated_changes, _ = freeze.prepare()
    regenerated_map = {row["sample_id"]: row for split in freeze.SPLITS for row in regenerated_rows[split]}
    reproducibility_failures = sum([
        regenerated_map != {row["sample_id"]: row for row in candidate},
        regenerated_safety != safety,
        regenerated_changes != expected_changes,
        len(regenerated_groups) != len(groups),
        regenerated_assignments != assignments,
    ])

    report_failures = sum([
        "TOP 20 largest split groups" not in (frozen / "split_group_balance_diagnosis.md").read_text(encoding="utf-8"),
        "BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT" not in (frozen / "split_report.md").read_text(encoding="utf-8"),
        "TRAIN → VALIDATION" not in (frozen / "v1_to_v2_split_diff.md").read_text(encoding="utf-8"),
        "所有泄漏指标为 0" not in (frozen / "leakage_audit.md").read_text(encoding="utf-8"),
    ])
    total_failures = sum([
        span_failures, registry_failures, structure_failures, other_row_failures,
        duplicate_id_failures, duplicate_text_failures, unassigned_count,
        exact_cross, normalized_cross, template_cross, mechanical_cross, family_cross, split_group_leakage,
        test_asset_in_train, source_copy_failures, forbidden_family_change_failures,
        safety_copy_failures, safety_isolation_failures, family_semantic_failures,
        manifest_count_failures, manifest_digest_failures, manifest_statistics_failures,
        manifest_hash_failures, parent_integrity_failures, balance_failures,
        reproducibility_failures, report_failures,
    ])
    summary = {
        "dataset_version": manifest.get("dataset_version"),
        "train_count": split_counts["TRAIN"],
        "validation_count": split_counts["VALIDATION"],
        "test_count": split_counts["TEST"],
        "safety_gold_count": split_counts["SAFETY_GOLD"],
        "test_asset_in_train": test_asset_in_train,
        "exact_cross_split_duplicates": exact_cross,
        "normalized_cross_split_duplicates": normalized_cross,
        "template_signature_cross_split_duplicates": template_cross,
        "mechanical_near_duplicate_cross_split_failures": mechanical_cross,
        "family_leakage_failures": family_cross + family_semantic_failures,
        "split_group_leakage_failures": split_group_leakage,
        "span_validation_failures": span_failures,
        "registry_validation_failures": registry_failures,
        "structure_failures": structure_failures,
        "source_copy_failures": source_copy_failures,
        "forbidden_family_change_failures": forbidden_family_change_failures,
        "safety_gold_copy_failures": safety_copy_failures,
        "safety_gold_isolation_failures": safety_isolation_failures,
        "manifest_count_failures": manifest_count_failures,
        "manifest_digest_failures": manifest_digest_failures,
        "manifest_statistics_failures": manifest_statistics_failures,
        "manifest_hash_failures": manifest_hash_failures,
        "parent_v1_integrity_failures": parent_integrity_failures,
        "balance_failures": balance_failures,
        "negated_soft_target_blocked_count": negated_soft_target_blocked_count,
        "reproducibility_failures": reproducibility_failures,
        "report_failures": report_failures,
        "validation_failures": total_failures,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for error in row_errors[:100]:
        print(error, file=sys.stderr)
    return 1 if total_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
