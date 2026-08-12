"""Immutable input verification for SYS-014 Stage 4B."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .labels import INTENT_TO_ID, SCOPE_TO_ID, STRUCTURE_TO_ID
from .train_config import repository_root


DATASET_DIR = repository_root() / "data" / "nlu" / "poc" / "frozen" / "sys014-poc7-v2"
MANIFEST_PATH = DATASET_DIR / "dataset_manifest.json"
ALLOWED_SPLITS = {"train": "TRAIN", "validation": "VALIDATION", "test": "TEST"}


class FrozenDatasetError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def resolve_manifest_file(name: str) -> Path:
    return repository_root() / name if name.startswith("data/") else DATASET_DIR / name


def verify_manifest_hashes() -> dict[str, Any]:
    manifest = load_manifest()
    failures: list[dict[str, str]] = []
    verified: list[dict[str, str]] = []
    for name, expected in manifest["file_sha256"].items():
        path = resolve_manifest_file(name)
        if not path.is_file():
            failures.append({"file": name, "reason": "MISSING"})
            continue
        actual = sha256_file(path)
        if actual != expected:
            failures.append(
                {"file": name, "reason": "SHA256_MISMATCH", "expected": expected, "actual": actual}
            )
        else:
            verified.append({"file": name, "sha256": actual})
    stage_flags = manifest.get("stage_flags", {})
    required_flags = (
        "POC_DATASET_V2_FROZEN",
        "POC_LEAKAGE_AUDIT_PASS",
        "POC_SPLIT_BALANCE_PASS",
        "POC_SPLIT_REPRODUCIBLE",
    )
    for flag in required_flags:
        if stage_flags.get(flag) is not True:
            failures.append({"file": "dataset_manifest.json", "reason": f"FLAG_NOT_TRUE:{flag}"})
    result = {
        "dataset_manifest_sha256": sha256_file(MANIFEST_PATH),
        "verified_file_count": len(verified),
        "verified_files": verified,
        "failures": failures,
        "DATASET_HASH_VERIFIED": not failures,
    }
    if failures:
        raise FrozenDatasetError(json.dumps(result, ensure_ascii=False))
    return result


def read_split(split: str) -> list[dict[str, Any]]:
    split_key = split.lower()
    if split_key not in ALLOWED_SPLITS:
        raise ValueError(f"Only train/validation/test are training pipeline inputs: {split}")
    path = DATASET_DIR / f"{split_key}.jsonl"
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    expected_split = ALLOWED_SPLITS[split_key]
    for record in records:
        validate_record(record, expected_split=expected_split)
    return records


def validate_record(record: dict[str, Any], *, expected_split: str) -> None:
    required = {
        "sample_id",
        "text",
        "registry_version",
        "intent_structure",
        "scope_label",
        "intent",
        "slots",
        "negated",
        "split",
    }
    missing = sorted(required - record.keys())
    if missing:
        raise FrozenDatasetError(f"{record.get('sample_id')}: missing {missing}")
    if record["split"] != expected_split:
        raise FrozenDatasetError(f"{record['sample_id']}: split mismatch")
    if record["registry_version"] != "sys-014-stage2.1-draft-2":
        raise FrozenDatasetError(f"{record['sample_id']}: registry mismatch")
    if record["scope_label"] not in SCOPE_TO_ID:
        raise FrozenDatasetError(f"{record['sample_id']}: invalid scope")
    if record["intent_structure"] not in STRUCTURE_TO_ID:
        raise FrozenDatasetError(f"{record['sample_id']}: invalid structure")
    eligible = (
        record["scope_label"] == "IN_SCOPE_CONTROL"
        and record["intent_structure"] == "SINGLE"
    )
    if eligible:
        if record["intent"] not in INTENT_TO_ID or not isinstance(record["negated"], bool):
            raise FrozenDatasetError(f"{record['sample_id']}: invalid eligible intent/negation")
    elif record["intent"] is not None or record["negated"] is not None:
        raise FrozenDatasetError(f"{record['sample_id']}: masked labels must be null")
    text = str(record["text"])
    for slot in record["slots"]:
        start, end = int(slot["char_start"]), int(slot["char_end"])
        if text[start:end] != slot["text"]:
            raise FrozenDatasetError(f"{record['sample_id']}: authoritative span mismatch")


def run_official_validator() -> dict[str, Any]:
    script = repository_root() / "scripts" / "validate_sys014_frozen_v2.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=repository_root(),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise FrozenDatasetError(
            f"official validator failed: {completed.stdout}\n{completed.stderr}"
        )
    result = json.loads(completed.stdout)
    if result.get("validation_failures") != 0:
        raise FrozenDatasetError(json.dumps(result, ensure_ascii=False))
    return result


def full_preflight() -> dict[str, Any]:
    hashes = verify_manifest_hashes()
    official = run_official_validator()
    split_counts = {split: len(read_split(split)) for split in ALLOWED_SPLITS}
    return {
        "hash_verification": hashes,
        "official_validator": official,
        "split_counts": split_counts,
        "safety_gold_policy": "INTEGRITY_ONLY_NOT_LOADED_FOR_LOSS_OR_SELECTION",
    }
