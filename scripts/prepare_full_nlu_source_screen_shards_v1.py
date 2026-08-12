from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PATH = (
    ROOT / "data" / "nlu" / "full" / "baseline_v2" / "full_nlu_canonical_raw_pool_v2.jsonl"
)
MAC_PATHS = {
    "train_set.jsonl": ROOT / "train_set.jsonl",
    "dev_set.jsonl": ROOT / "dev_set.jsonl",
    "test_set.jsonl": ROOT / "test_set.jsonl",
}
EXPECTED_MAC_COUNTS = {
    "train_set.jsonl": 18_000,
    "dev_set.jsonl": 1_391,
    "test_set.jsonl": 1_151,
}
EXPECTED_SOURCE_COUNTS = {
    "MAC-SLU": 20_540,
    "人工弱覆盖种子": 162,
    "人工安全边界种子": 197,
}
OUTPUT_DIR = ROOT / "data" / "nlu" / "full" / "source_screen_shards_v1"
MANIFEST_PATH = OUTPUT_DIR / "source_screen_shards_manifest_v1.json"
EXPECTED_TOTAL = 20_899
SHARD_BOUNDS = [
    (1, 2_000),
    (2_001, 4_000),
    (4_001, 6_000),
    (6_001, 8_000),
    (8_001, 10_000),
    (10_001, 12_000),
    (12_001, 14_000),
    (14_001, 16_000),
    (16_001, 18_000),
    (18_001, 20_000),
    (20_001, 20_899),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                raise ValueError(f"Blank line in {path} at line {line_number}")
            value = json.loads(line)
            if not isinstance(value, dict):
                raise TypeError(f"Non-object JSON in {path} at line {line_number}")
            rows.append(value)
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            stream.write("\n")


def main() -> None:
    input_paths = [CANONICAL_PATH, *MAC_PATHS.values()]
    missing_paths = [str(path) for path in input_paths if not path.is_file()]
    if missing_paths:
        raise FileNotFoundError(f"Required input paths missing: {missing_paths}")
    if OUTPUT_DIR.exists():
        raise FileExistsError(f"Refusing to overwrite existing output directory: {OUTPUT_DIR}")

    input_hashes_before = {str(path): sha256(path) for path in input_paths}
    canonical_rows = load_jsonl(CANONICAL_PATH)
    if len(canonical_rows) != EXPECTED_TOTAL:
        raise ValueError(
            f"Canonical count mismatch: expected {EXPECTED_TOTAL}, got {len(canonical_rows)}"
        )

    sample_ids = [row.get("样本编号") for row in canonical_rows]
    if any(value is None or value == "" for value in sample_ids):
        raise ValueError("Canonical input contains missing 样本编号")
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Canonical input contains duplicate 样本编号")

    mac_lookup: dict[str, dict[str, dict]] = {}
    for file_name, path in MAC_PATHS.items():
        rows = load_jsonl(path)
        expected_count = EXPECTED_MAC_COUNTS[file_name]
        if len(rows) != expected_count:
            raise ValueError(
                f"MAC count mismatch for {file_name}: expected {expected_count}, got {len(rows)}"
            )
        lookup: dict[str, dict] = {}
        for line_number, row in enumerate(rows, start=1):
            missing_fields = [key for key in ("id", "query", "split_sens", "semantics") if key not in row]
            if missing_fields:
                raise ValueError(
                    f"MAC row missing fields in {file_name} at line {line_number}: {missing_fields}"
                )
            original_id = str(row["id"])
            if original_id in lookup:
                raise ValueError(f"Duplicate MAC id in {file_name}: {original_id}")
            lookup[original_id] = row
        mac_lookup[file_name] = lookup

    source_counts: dict[str, int] = {}
    output_rows: list[dict] = []
    seen_mac_refs: set[tuple[str, str]] = set()
    for screen_index, source_row in enumerate(canonical_rows, start=1):
        source = source_row.get("来源")
        source_counts[source] = source_counts.get(source, 0) + 1
        row = copy.deepcopy(source_row)
        row["screen_index"] = screen_index

        if source == "MAC-SLU":
            original_file = row.get("原始文件")
            original_id = str(row.get("原始编号"))
            if original_file not in mac_lookup:
                raise ValueError(
                    f"Unknown MAC original file at screen_index {screen_index}: {original_file!r}"
                )
            ref = (original_file, original_id)
            if ref in seen_mac_refs:
                raise ValueError(f"Duplicate MAC reference at screen_index {screen_index}: {ref}")
            seen_mac_refs.add(ref)
            try:
                mac_row = mac_lookup[original_file][original_id]
            except KeyError as exc:
                raise ValueError(
                    f"MAC reference not found at screen_index {screen_index}: {ref}"
                ) from exc
            row["mac_query"] = copy.deepcopy(mac_row["query"])
            row["mac_split_sens"] = copy.deepcopy(mac_row["split_sens"])
            row["mac_semantics"] = copy.deepcopy(mac_row["semantics"])
        elif source in {"人工弱覆盖种子", "人工安全边界种子"}:
            row["mac_query"] = None
            row["mac_split_sens"] = None
            row["mac_semantics"] = None
        else:
            raise ValueError(f"Unexpected source at screen_index {screen_index}: {source!r}")

        output_rows.append(row)

    if source_counts != EXPECTED_SOURCE_COUNTS:
        raise ValueError(
            f"Source counts mismatch: expected {EXPECTED_SOURCE_COUNTS}, got {source_counts}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=False)
    shard_entries: list[dict] = []
    for shard_number, (start, end) in enumerate(SHARD_BOUNDS, start=1):
        shard_rows = output_rows[start - 1 : end]
        expected_count = end - start + 1
        if len(shard_rows) != expected_count:
            raise ValueError(
                f"Shard {shard_number:02d} count mismatch: expected {expected_count}, got {len(shard_rows)}"
            )
        shard_name = f"source_screen_input_shard_{shard_number:02d}.jsonl"
        shard_path = OUTPUT_DIR / shard_name
        write_jsonl(shard_path, shard_rows)
        shard_entries.append(
            {
                "file": shard_name,
                "start_screen_index": start,
                "end_screen_index": end,
                "sample_count": expected_count,
                "sha256": sha256(shard_path),
            }
        )

    manifest = {
        "source_file": str(CANONICAL_PATH),
        "source_sha256": input_hashes_before[str(CANONICAL_PATH)],
        "total_samples": EXPECTED_TOTAL,
        "shards": shard_entries,
    }
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

    reloaded_rows: list[dict] = []
    for shard_entry in shard_entries:
        shard_path = OUTPUT_DIR / shard_entry["file"]
        if sha256(shard_path) != shard_entry["sha256"]:
            raise ValueError(f"Shard SHA256 mismatch after write: {shard_path}")
        reloaded_rows.extend(load_jsonl(shard_path))

    if len(reloaded_rows) != EXPECTED_TOTAL:
        raise ValueError(f"Final total mismatch: {len(reloaded_rows)}")
    if [row.get("screen_index") for row in reloaded_rows] != list(
        range(1, EXPECTED_TOTAL + 1)
    ):
        raise ValueError("Final screen_index sequence is not continuous from 1 to 20899")
    final_sample_ids = [row.get("样本编号") for row in reloaded_rows]
    missing_sample_ids = sum(value is None or value == "" for value in final_sample_ids)
    duplicate_sample_ids = len(final_sample_ids) - len(set(final_sample_ids))
    if missing_sample_ids or duplicate_sample_ids:
        raise ValueError(
            f"Final sample id validation failed: missing={missing_sample_ids}, duplicates={duplicate_sample_ids}"
        )
    if sum(entry["sample_count"] for entry in shard_entries) != EXPECTED_TOTAL:
        raise ValueError("Manifest shard sample counts do not sum to 20899")

    input_hashes_after = {str(path): sha256(path) for path in input_paths}
    if input_hashes_after != input_hashes_before:
        changed = [
            path
            for path in input_hashes_before
            if input_hashes_before[path] != input_hashes_after[path]
        ]
        raise ValueError(f"Input files changed during processing: {changed}")

    report = {
        "total": len(reloaded_rows),
        "screen_index_continuous": True,
        "sample_id_duplicates": duplicate_sample_ids,
        "sample_id_missing": missing_sample_ids,
        "shard_count": len(shard_entries),
        "shard_total": sum(entry["sample_count"] for entry in shard_entries),
        "source_counts": source_counts,
        "mac_reference_count": len(seen_mac_refs),
        "canonical_sha256_before": input_hashes_before[str(CANONICAL_PATH)],
        "canonical_sha256_after": input_hashes_after[str(CANONICAL_PATH)],
        "mac_sha256_unchanged": all(
            input_hashes_before[str(path)] == input_hashes_after[str(path)]
            for path in MAC_PATHS.values()
        ),
        "manifest": str(MANIFEST_PATH),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
