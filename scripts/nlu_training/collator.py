"""Dynamic padding collator with slot IGNORE_INDEX enforcement."""

from __future__ import annotations

from typing import Any

import torch

from .labels import IGNORE_INDEX


class JointNLUCollator:
    def __init__(self, tokenizer: Any) -> None:
        self.tokenizer = tokenizer

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        model_features = [
            {
                key: value
                for key, value in feature.items()
                if key
                not in {
                    "scope_labels",
                    "structure_labels",
                    "intent_labels",
                    "slot_labels",
                    "negation_labels",
                    "sample_id",
                    "text",
                }
            }
            for feature in features
        ]
        batch = self.tokenizer.pad(model_features, padding=True, return_tensors="pt")
        sequence_length = int(batch["input_ids"].shape[1])
        slot_rows = [
            feature["slot_labels"]
            + [IGNORE_INDEX] * (sequence_length - len(feature["slot_labels"]))
            for feature in features
        ]
        batch.update(
            {
                "scope_labels": torch.tensor(
                    [feature["scope_labels"] for feature in features], dtype=torch.long
                ),
                "structure_labels": torch.tensor(
                    [feature["structure_labels"] for feature in features], dtype=torch.long
                ),
                "intent_labels": torch.tensor(
                    [feature["intent_labels"] for feature in features], dtype=torch.long
                ),
                "slot_labels": torch.tensor(slot_rows, dtype=torch.long),
                "negation_labels": torch.tensor(
                    [feature["negation_labels"] for feature in features], dtype=torch.long
                ),
                "sample_ids": [feature["sample_id"] for feature in features],
                "texts": [feature["text"] for feature in features],
            }
        )
        return dict(batch)
