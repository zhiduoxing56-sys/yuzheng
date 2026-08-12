"""Deterministic raw-character-span to token BIO projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .labels import IGNORE_INDEX, SLOT_TO_ID, SUPPORTED_SLOT_TYPES


@dataclass(frozen=True)
class ProjectionFailure:
    sample_id: str
    reason: str
    detail: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "reason": self.reason,
            "detail": self.detail,
        }


def project_character_spans_to_bio(
    *,
    sample_id: str,
    text: str,
    slots: Iterable[dict[str, Any]],
    offset_mapping: Iterable[tuple[int, int] | list[int]],
    special_tokens_mask: Iterable[int],
) -> tuple[list[int], list[ProjectionFailure]]:
    offsets = [tuple(int(value) for value in item) for item in offset_mapping]
    special = [int(value) for value in special_tokens_mask]
    if len(offsets) != len(special):
        raise ValueError("offset_mapping and special_tokens_mask lengths differ")
    labels = [
        IGNORE_INDEX if marker or end <= start else SLOT_TO_ID["O"]
        for (start, end), marker in zip(offsets, special, strict=True)
    ]
    failures: list[ProjectionFailure] = []

    for slot in slots:
        slot_type = str(slot.get("slot_type"))
        if slot_type not in SUPPORTED_SLOT_TYPES:
            failures.append(
                ProjectionFailure(
                    sample_id,
                    "UNSUPPORTED_SLOT_TYPE",
                    {"slot": slot, "supported": list(SUPPORTED_SLOT_TYPES)},
                )
            )
            continue
        start = int(slot["char_start"])
        end = int(slot["char_end"])
        annotated_text = str(slot["text"])
        if start < 0 or end <= start or end > len(text):
            failures.append(
                ProjectionFailure(
                    sample_id,
                    "INVALID_RAW_SPAN_RANGE",
                    {"slot": slot, "text_length": len(text)},
                )
            )
            continue
        actual_text = text[start:end]
        if actual_text != annotated_text:
            failures.append(
                ProjectionFailure(
                    sample_id,
                    "RAW_SPAN_TEXT_MISMATCH",
                    {"slot": slot, "actual_text": actual_text},
                )
            )
            continue
        token_indices = [
            index
            for index, (token_start, token_end) in enumerate(offsets)
            if not special[index]
            and token_end > token_start
            and token_start < end
            and start < token_end
        ]
        if not token_indices:
            failures.append(
                ProjectionFailure(
                    sample_id,
                    "NO_OVERLAPPING_TOKEN",
                    {"slot": slot, "offset_mapping": offsets},
                )
            )
            continue
        covered: set[int] = set()
        for token_index in token_indices:
            token_start, token_end = offsets[token_index]
            covered.update(range(max(start, token_start), min(end, token_end)))
        required = {position for position in range(start, end) if not text[position].isspace()}
        if not required.issubset(covered):
            failures.append(
                ProjectionFailure(
                    sample_id,
                    "INCOMPLETE_CHARACTER_COVERAGE",
                    {
                        "slot": slot,
                        "token_offsets": [offsets[index] for index in token_indices],
                        "uncovered": sorted(required - covered),
                    },
                )
            )
            continue
        for position, token_index in enumerate(token_indices):
            bio_name = ("B-" if position == 0 else "I-") + slot_type
            if labels[token_index] != SLOT_TO_ID["O"]:
                failures.append(
                    ProjectionFailure(
                        sample_id,
                        "TOKEN_LABEL_COLLISION",
                        {
                            "slot": slot,
                            "token_index": token_index,
                            "existing_label_id": labels[token_index],
                            "new_label": bio_name,
                        },
                    )
                )
                continue
            labels[token_index] = SLOT_TO_ID[bio_name]
    return labels, failures
