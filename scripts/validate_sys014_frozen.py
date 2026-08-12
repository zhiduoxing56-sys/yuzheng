"""Validate the immutable SYS-014 PoC7 frozen dataset and its manifest."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

import freeze_sys014_poc7 as freeze
import validate_nlu_dataset as source_validator


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FROZEN = ROOT / "data/nlu/poc/frozen/sys014-poc7-v1"


def load_plain(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        value["__file"] = str(path)
        value["__line"] = line_number
        rows.append(value)
    return rows


def clean(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if not key.startswith("__")}


def cross_count(rows_by_split: dict[str, list[dict[str, Any]]], key_fn) -> int:
    seen: dict[str, set[str]] = defaultdict(set)
    for split, rows in rows_by_split.items():
        for row in rows:
            seen[key_fn(clean(row))].add(split)
    return sum(len(splits) > 1 for splits in seen.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen", type=Path, default=DEFAULT_FROZEN)
    args = parser.parse_args()
    frozen = args.frozen.resolve()
    files = {
        "TRAIN": frozen / "train.jsonl",
        "VALIDATION": frozen / "validation.jsonl",
        "TEST": frozen / "test.jsonl",
        "SAFETY_GOLD": frozen / "safety_gold.jsonl",
    }
    required_artifacts = [
        *files.values(), frozen / "dataset_manifest.json", frozen / "split_report.md",
        frozen / "leakage_audit.md", frozen / "README.md",
    ]
    missing = [str(path) for path in required_artifacts if not path.is_file() or path.stat().st_size == 0]
    if missing:
        print(json.dumps({"missing_artifacts": missing}, ensure_ascii=False, indent=2))
        return 1

    manifest = json.loads((frozen / "dataset_manifest.json").read_text(encoding="utf-8"))
    rows_by_split = {split: load_plain(path) for split, path in files.items()}
    candidate_splits = {split: rows_by_split[split] for split in ("TRAIN", "VALIDATION", "TEST")}
    candidate = [row for rows in candidate_splits.values() for row in rows]
    safety = rows_by_split["SAFETY_GOLD"]
    all_rows = candidate + safety

    registry = yaml.safe_load(freeze.REGISTRY_PATH.read_text(encoding="utf-8"))
    schema = json.loads(freeze.SCHEMA_PATH.read_text(encoding="utf-8"))
    intent_map = {item["intent_id"]: item for item in registry["intents"]}
    area_values = set(registry["area_catalog"])
    errors: list[str] = []
    span_failures = 0
    registry_failures = 0
    for split, rows in rows_by_split.items():
        for row in rows:
            row_errors, span_count, registry_count = source_validator.validate_row(
                row,
                registry_version=registry["registry_version"],
                intent_map=intent_map,
                area_values=area_values,
                mode_contracts=registry.get("mode_contracts", {}),
                schema=schema,
                expected_split=split,
            )
            errors.extend(row_errors)
            span_failures += span_count
            registry_failures += registry_count

    ids = [row["sample_id"] for row in all_rows]
    texts = [row["text"] for row in all_rows]
    global_duplicate_id_failures = len(ids) - len(set(ids))
    global_duplicate_text_failures = len(texts) - len(set(texts))
    unassigned_count = sum(row.get("split") == "UNASSIGNED" for row in all_rows)

    exact_cross = cross_count(candidate_splits, lambda row: row["text"])
    normalized_cross = cross_count(candidate_splits, lambda row: freeze.normalized_text(row["text"]))
    template_cross = cross_count(candidate_splits, freeze.template_signature)
    mechanical_cross = cross_count(candidate_splits, freeze.mechanical_signature)
    family_cross = cross_count(candidate_splits, lambda row: row["paraphrase_family_id"])

    clean_candidate = [clean(row) for row in candidate]
    groups = freeze.build_groups(clean_candidate)
    sample_split = {row["sample_id"]: row["split"] for row in clean_candidate}
    group_split_sets = {
        group.group_id: {sample_split[row["sample_id"]] for row in group.rows} for group in groups
    }
    split_group_leakage = sum(len(splits) > 1 for splits in group_split_sets.values())
    assignments = {group_id: next(iter(splits)) for group_id, splits in group_split_sets.items() if len(splits) == 1}
    assignment_digest = freeze.sha256_bytes(
        "\n".join(f"{key}:{assignments[key]}" for key in sorted(assignments)).encode("utf-8")
    )

    test_asset_in_train = sum(row["source_ref"]["source_type"] == "TEST_ASSET" for row in candidate_splits["TRAIN"])
    safety_ids = {row["sample_id"] for row in safety}
    safety_texts = {freeze.normalized_text(row["text"]) for row in safety}
    safety_families = {row["paraphrase_family_id"] for row in safety}
    candidate_ids = {row["sample_id"] for row in candidate}
    candidate_texts = {freeze.normalized_text(row["text"]) for row in candidate}
    candidate_families = {row["paraphrase_family_id"] for row in candidate}
    safety_gold_isolation_failures = (
        len(safety_ids & candidate_ids) + len(safety_texts & candidate_texts) + len(safety_families & candidate_families)
    )

    source_candidate = freeze.load_jsonl(freeze.CANDIDATE_PATH)
    source_safety = freeze.load_jsonl(freeze.SAFETY_PATH)
    source_candidate_map = {row["sample_id"]: row for row in source_candidate}
    frozen_candidate_map = {row["sample_id"]: {**clean(row), "split": "UNASSIGNED"} for row in candidate}
    source_copy_failures = int(source_candidate_map != frozen_candidate_map)
    source_safety_map = {row["sample_id"]: row for row in source_safety}
    frozen_safety_map = {row["sample_id"]: clean(row) for row in safety}
    source_copy_failures += int(source_safety_map != frozen_safety_map)

    split_counts = {split: len(rows_by_split[split]) for split in files}
    family_counts = {
        split: len({row["paraphrase_family_id"] for row in rows_by_split[split]})
        for split in ("TRAIN", "VALIDATION", "TEST")
    }
    group_counts = Counter(assignments.values())
    count_failures = sum([
        split_counts["TRAIN"] != manifest["train_count"],
        split_counts["VALIDATION"] != manifest["validation_count"],
        split_counts["TEST"] != manifest["test_count"],
        split_counts["SAFETY_GOLD"] != manifest["safety_gold_count"],
        family_counts["TRAIN"] != manifest["train_family_count"],
        family_counts["VALIDATION"] != manifest["validation_family_count"],
        family_counts["TEST"] != manifest["test_family_count"],
        group_counts["TRAIN"] != manifest["train_split_group_count"],
        group_counts["VALIDATION"] != manifest["validation_split_group_count"],
        group_counts["TEST"] != manifest["test_split_group_count"],
        assignment_digest != manifest["grouping_strategy"]["split_group_assignment_digest_sha256"],
    ])

    current_stats = {split: freeze.split_statistics([clean(row) for row in candidate_splits[split]]) for split in candidate_splits}
    statistics_failures = int(current_stats != manifest["statistics"])
    unknown_total = freeze.unknown_counts([clean(row) for row in candidate])
    statistics_failures += int(unknown_total != manifest["unknown_control_derived_total"])

    hash_failures = 0
    for relative, expected in manifest["file_sha256"].items():
        path = ROOT / relative if "/" in relative else frozen / relative
        if not path.is_file() or freeze.sha256_file(path) != expected:
            hash_failures += 1

    train_intents = {
        intent for intent, values in freeze.intent_coverage([clean(row) for row in candidate_splits["TRAIN"]]).items()
        if sum(values.values()) > 0
    }
    train_intent_coverage_failures = len(set(freeze.POC_INTENTS) - train_intents)
    window_value_eval_failures = sum(
        not any(
            row.get("intent") == "WINDOW_SET_POSITION"
            and any(slot["slot_type"] == "VALUE" for slot in row.get("slots", []))
            for row in candidate_splits[split]
        )
        for split in ("VALIDATION", "TEST")
    )
    report_failures = int("7-Intent 覆盖" not in (frozen / "split_report.md").read_text(encoding="utf-8"))

    structure_markers = (
        "schema ", "invalid intent_structure", "invalid scope_label", "MULTI requires",
        "segment.negated must be boolean", "non-MULTI record must have no segments",
        "in-scope SINGLE negated must be boolean", "boundary/ambiguous record requires",
        "negated SINGLE requires", "negated segment lacks",
    )
    structure_failures = sum(any(marker in error for marker in structure_markers) for error in errors)
    other_row_failures = max(0, len(errors) - span_failures - registry_failures)
    total_failures = sum([
        span_failures, registry_failures, structure_failures, other_row_failures,
        global_duplicate_id_failures, global_duplicate_text_failures, unassigned_count,
        exact_cross, normalized_cross, template_cross, mechanical_cross, family_cross,
        split_group_leakage, test_asset_in_train, safety_gold_isolation_failures,
        source_copy_failures, count_failures, statistics_failures, hash_failures,
        train_intent_coverage_failures, window_value_eval_failures, report_failures,
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
        "family_leakage_failures": family_cross,
        "split_group_leakage_failures": split_group_leakage,
        "span_validation_failures": span_failures,
        "registry_validation_failures": registry_failures,
        "structure_failures": structure_failures,
        "global_duplicate_id_failures": global_duplicate_id_failures,
        "global_duplicate_text_failures": global_duplicate_text_failures,
        "safety_gold_isolation_failures": safety_gold_isolation_failures,
        "unassigned_count": unassigned_count,
        "source_copy_failures": source_copy_failures,
        "manifest_count_failures": count_failures,
        "manifest_statistics_failures": statistics_failures,
        "manifest_hash_failures": hash_failures,
        "train_intent_coverage_failures": train_intent_coverage_failures,
        "window_value_eval_failures": window_value_eval_failures,
        "validation_failures": total_failures,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        for error in errors[:100]:
            print(error, file=sys.stderr)
    return 1 if total_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
