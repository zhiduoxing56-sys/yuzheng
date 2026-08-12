"""Strict masked multi-task loss implementation."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import torch
import torch.nn.functional as functional

from .labels import IGNORE_INDEX


TASKS = ("scope", "structure", "intent", "slot", "negation")


def class_weights_from_counts(
    counts: Mapping[str, int],
    ordered_labels: Sequence[str],
    *,
    policy: str,
    cap: float = 3.0,
) -> list[float] | None:
    if policy == "NONE":
        return None
    if policy not in {"INVERSE_FREQ", "SQRT_INVERSE_FREQ"}:
        raise ValueError(f"Unknown class weight policy: {policy}")
    if any(counts.get(label, 0) <= 0 for label in ordered_labels):
        raise ValueError("Class weighting requires every configured class in TRAIN")
    total = float(sum(counts[label] for label in ordered_labels))
    raw = []
    for label in ordered_labels:
        inverse = total / float(counts[label])
        raw.append(inverse if policy == "INVERSE_FREQ" else math.sqrt(inverse))
    mean = sum(raw) / len(raw)
    return [round(min(value / mean, cap), 8) for value in raw]


def _masked_cross_entropy(
    logits: torch.Tensor,
    labels: torch.Tensor,
    *,
    class_weight: torch.Tensor | None = None,
) -> tuple[torch.Tensor, int]:
    supervised = labels.ne(IGNORE_INDEX)
    count = int(supervised.sum().item())
    if count == 0:
        return logits.sum() * 0.0, 0
    return (
        functional.cross_entropy(
            logits,
            labels,
            weight=class_weight,
            ignore_index=IGNORE_INDEX,
        ),
        count,
    )


def compute_masked_multitask_loss(
    outputs: Mapping[str, torch.Tensor],
    batch: Mapping[str, Any],
    *,
    loss_weights: Mapping[str, float],
    class_weights: Mapping[str, torch.Tensor | None] | None = None,
) -> dict[str, Any]:
    weights = class_weights or {}
    scope_loss, scope_count = _masked_cross_entropy(
        outputs["scope_logits"], batch["scope_labels"], class_weight=weights.get("scope")
    )
    structure_loss, structure_count = _masked_cross_entropy(
        outputs["structure_logits"],
        batch["structure_labels"],
        class_weight=weights.get("structure"),
    )
    intent_loss, intent_count = _masked_cross_entropy(
        outputs["intent_logits"], batch["intent_labels"], class_weight=weights.get("intent")
    )
    slot_loss, slot_count = _masked_cross_entropy(
        outputs["slot_logits"].reshape(-1, outputs["slot_logits"].shape[-1]),
        batch["slot_labels"].reshape(-1),
        class_weight=weights.get("slot"),
    )
    negation_loss, negation_count = _masked_cross_entropy(
        outputs["negation_logits"],
        batch["negation_labels"],
        class_weight=weights.get("negation"),
    )
    task_losses = {
        "scope": scope_loss,
        "structure": structure_loss,
        "intent": intent_loss,
        "slot": slot_loss,
        "negation": negation_loss,
    }
    total = sum(task_losses[name] * float(loss_weights[name]) for name in TASKS)
    return {
        **{f"{name}_loss": value for name, value in task_losses.items()},
        "total_loss": total,
        "supervised_counts": {
            "scope": scope_count,
            "structure": structure_count,
            "intent": intent_count,
            "slot_tokens": slot_count,
            "negation": negation_count,
        },
    }
