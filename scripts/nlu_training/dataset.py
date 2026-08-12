"""Read-only Dataset and distribution helpers for frozen SYS-014 data."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Iterable

from torch.utils.data import Dataset

from .labels import (
    IGNORE_INDEX,
    INTENT_TO_ID,
    NEGATION_TO_ID,
    SCOPE_TO_ID,
    SLOT_LABELS,
    STRUCTURE_TO_ID,
)
from .projection import ProjectionFailure, project_character_spans_to_bio
from .validation import FrozenDatasetError, read_split


class FrozenJointNLUDataset(Dataset[dict[str, Any]]):
    def __init__(self, split: str, tokenizer: Any, *, max_length: int) -> None:
        self.split = split.lower()
        self.records = read_split(self.split)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return encode_record(
            self.records[index], self.tokenizer, max_length=self.max_length
        )


def encode_record(record: dict[str, Any], tokenizer: Any, *, max_length: int) -> dict[str, Any]:
    encoded = tokenizer(
        str(record["text"]),
        add_special_tokens=True,
        truncation=True,
        max_length=max_length,
        return_offsets_mapping=True,
        return_special_tokens_mask=True,
    )
    slot_labels, failures = project_character_spans_to_bio(
        sample_id=str(record["sample_id"]),
        text=str(record["text"]),
        slots=record.get("slots", []),
        offset_mapping=encoded["offset_mapping"],
        special_tokens_mask=encoded["special_tokens_mask"],
    )
    if failures:
        raise FrozenDatasetError(
            f"TOKEN_PROJECTION_FAILURES for {record['sample_id']}: "
            + str([failure.to_dict() for failure in failures])
        )
    eligible_intent = (
        record["scope_label"] == "IN_SCOPE_CONTROL"
        and record["intent_structure"] == "SINGLE"
        and record["intent"] is not None
    )
    eligible_negation = (
        record["scope_label"] == "IN_SCOPE_CONTROL"
        and record["intent_structure"] == "SINGLE"
        and isinstance(record["negated"], bool)
    )
    model_inputs = {
        key: value
        for key, value in encoded.items()
        if key not in {"offset_mapping", "special_tokens_mask"}
    }
    return {
        **model_inputs,
        "scope_labels": SCOPE_TO_ID[record["scope_label"]],
        "structure_labels": STRUCTURE_TO_ID[record["intent_structure"]],
        "intent_labels": INTENT_TO_ID[record["intent"]] if eligible_intent else IGNORE_INDEX,
        "slot_labels": slot_labels,
        "negation_labels": (
            NEGATION_TO_ID["NEGATED" if record["negated"] else "NOT_NEGATED"]
            if eligible_negation
            else IGNORE_INDEX
        ),
        "sample_id": str(record["sample_id"]),
        "text": str(record["text"]),
    }


def token_length_distribution(
    records: Iterable[dict[str, Any]], tokenizer: Any
) -> dict[str, float | int]:
    lengths = sorted(
        len(tokenizer(str(record["text"]), add_special_tokens=True)["input_ids"])
        for record in records
    )

    def percentile(value: float) -> float:
        position = (len(lengths) - 1) * value / 100.0
        low, high = math.floor(position), math.ceil(position)
        if low == high:
            return float(lengths[low])
        fraction = position - low
        return lengths[low] * (1 - fraction) + lengths[high] * fraction

    return {
        "count": len(lengths),
        "p50": round(percentile(50), 3),
        "p90": round(percentile(90), 3),
        "p95": round(percentile(95), 3),
        "p99": round(percentile(99), 3),
        "max": max(lengths),
    }


def select_max_length(max_token_length: int) -> int:
    for candidate in (32, 48, 64):
        if max_token_length <= candidate:
            return candidate
    raise FrozenDatasetError(
        f"MAX_TOKEN_LENGTH={max_token_length} exceeds frozen Stage 4B candidates"
    )


def project_all_records(
    records: Iterable[dict[str, Any]], tokenizer: Any, *, max_length: int
) -> tuple[Counter[str], list[ProjectionFailure]]:
    slot_distribution: Counter[str] = Counter()
    failures: list[ProjectionFailure] = []
    for record in records:
        encoded = tokenizer(
            str(record["text"]),
            add_special_tokens=True,
            truncation=True,
            max_length=max_length,
            return_offsets_mapping=True,
            return_special_tokens_mask=True,
        )
        labels, record_failures = project_character_spans_to_bio(
            sample_id=str(record["sample_id"]),
            text=str(record["text"]),
            slots=record.get("slots", []),
            offset_mapping=encoded["offset_mapping"],
            special_tokens_mask=encoded["special_tokens_mask"],
        )
        failures.extend(record_failures)
        slot_distribution.update(
            SLOT_LABELS[label] for label in labels if label != IGNORE_INDEX
        )
    return slot_distribution, failures


def training_record_distribution(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(records)
    intent = Counter(
        str(record["intent"]) for record in rows if record.get("intent") is not None
    )
    negation = Counter(
        "NEGATED" if record["negated"] else "NOT_NEGATED"
        for record in rows
        if isinstance(record.get("negated"), bool)
    )
    return {
        "sample_count": len(rows),
        "scope": dict(sorted(Counter(record["scope_label"] for record in rows).items())),
        "structure": dict(
            sorted(Counter(record["intent_structure"] for record in rows).items())
        ),
        "intent_eligible_only": dict(sorted(intent.items())),
        "negation_eligible_only": dict(sorted(negation.items())),
    }
