"""Offline quality and safety metrics for Stage 4B/4C."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

from .labels import IGNORE_INDEX, INTENT_LABELS, SCOPE_TO_ID, SLOT_LABELS, STRUCTURE_TO_ID


def classification_metrics(
    y_true: Sequence[int], y_pred: Sequence[int], *, label_names: Sequence[str]
) -> dict[str, Any]:
    labels = list(range(len(label_names)))
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)) if y_true else None,
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "per_class": {
            name: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index, name in enumerate(label_names)
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
    }


def extract_bio_spans(label_ids: Sequence[int]) -> set[tuple[str, int, int]]:
    spans: set[tuple[str, int, int]] = set()
    active_type: str | None = None
    active_start = -1
    filtered = [label if label != IGNORE_INDEX else 0 for label in label_ids]
    for index, label_id in enumerate(filtered + [0]):
        label = SLOT_LABELS[label_id]
        if label == "O":
            if active_type is not None:
                spans.add((active_type, active_start, index))
                active_type = None
            continue
        prefix, entity_type = label.split("-", 1)
        if prefix == "B" or entity_type != active_type:
            if active_type is not None:
                spans.add((active_type, active_start, index))
            active_type, active_start = entity_type, index
    return spans


def slot_span_metrics(
    true_sequences: Sequence[Sequence[int]], pred_sequences: Sequence[Sequence[int]]
) -> dict[str, Any]:
    counts: dict[str, Counter[str]] = {
        entity: Counter(tp=0, fp=0, fn=0) for entity in ("AREA", "VALUE", "NEGATION", "OVERALL")
    }
    for true, predicted in zip(true_sequences, pred_sequences, strict=True):
        if len(true) != len(predicted):
            raise ValueError("Slot sequence lengths differ")
        masked_predicted = [
            IGNORE_INDEX if truth == IGNORE_INDEX else prediction
            for truth, prediction in zip(true, predicted, strict=True)
        ]
        truth_spans = extract_bio_spans(true)
        pred_spans = extract_bio_spans(masked_predicted)
        for entity in ("AREA", "VALUE", "NEGATION"):
            truth_entity = {span for span in truth_spans if span[0] == entity}
            pred_entity = {span for span in pred_spans if span[0] == entity}
            counts[entity]["tp"] += len(truth_entity & pred_entity)
            counts[entity]["fp"] += len(pred_entity - truth_entity)
            counts[entity]["fn"] += len(truth_entity - pred_entity)
        counts["OVERALL"]["tp"] += len(truth_spans & pred_spans)
        counts["OVERALL"]["fp"] += len(pred_spans - truth_spans)
        counts["OVERALL"]["fn"] += len(truth_spans - pred_spans)

    def summarize(counter: Counter[str]) -> dict[str, float | int]:
        tp, fp, fn = counter["tp"], counter["fp"], counter["fn"]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}

    return {name: summarize(counter) for name, counter in counts.items()}


def unsafe_false_accept_metrics(
    *,
    true_scope: Sequence[int],
    true_structure: Sequence[int],
    pred_scope: Sequence[int],
    pred_structure: Sequence[int],
    pred_intent: Sequence[int],
) -> dict[str, Any]:
    lengths = {len(item) for item in (true_scope, true_structure, pred_scope, pred_structure, pred_intent)}
    if len(lengths) != 1:
        raise ValueError("UFAR inputs must have equal lengths")
    categories = {
        "NON_CONTROL": lambda scope, structure: scope == SCOPE_TO_ID["NON_CONTROL"],
        "UNKNOWN_CONTROL": lambda scope, structure: scope == SCOPE_TO_ID["UNKNOWN_CONTROL"],
        "AMBIGUOUS_CONTROL": lambda scope, structure: scope == SCOPE_TO_ID["AMBIGUOUS_CONTROL"],
        "MULTI": lambda scope, structure: structure == STRUCTURE_TO_ID["MULTI"],
        "AMBIGUOUS": lambda scope, structure: structure == STRUCTURE_TO_ID["AMBIGUOUS"],
    }
    overall_total = 0
    overall_false_accept = 0
    per_category: dict[str, Any] = {}
    for category, predicate in categories.items():
        total = 0
        false_accepts = 0
        for values in zip(
            true_scope, true_structure, pred_scope, pred_structure, pred_intent, strict=True
        ):
            scope, structure, predicted_scope, predicted_structure, predicted_intent = values
            if not predicate(scope, structure):
                continue
            total += 1
            executable = (
                predicted_scope == SCOPE_TO_ID["IN_SCOPE_CONTROL"]
                and predicted_structure == STRUCTURE_TO_ID["SINGLE"]
                and 0 <= predicted_intent < len(INTENT_LABELS)
            )
            false_accepts += int(executable)
        per_category[category] = {
            "total_should_abstain": total,
            "unsafe_false_accepts": false_accepts,
            "false_accept_rate": false_accepts / total if total else None,
        }
    for index in range(next(iter(lengths), 0)):
        should_abstain = (
            true_scope[index] != SCOPE_TO_ID["IN_SCOPE_CONTROL"]
            or true_structure[index] != STRUCTURE_TO_ID["SINGLE"]
        )
        if not should_abstain:
            continue
        overall_total += 1
        executable = (
            pred_scope[index] == SCOPE_TO_ID["IN_SCOPE_CONTROL"]
            and pred_structure[index] == STRUCTURE_TO_ID["SINGLE"]
            and 0 <= pred_intent[index] < len(INTENT_LABELS)
        )
        overall_false_accept += int(executable)
    return {
        "UNSAFE_FALSE_ACCEPT_RATE": (
            overall_false_accept / overall_total if overall_total else None
        ),
        "unsafe_false_accepts": overall_false_accept,
        "total_should_abstain": overall_total,
        "per_category": per_category,
    }


def primary_quality_score(metrics: Mapping[str, float]) -> float:
    weights = {
        "intent_macro_f1": 0.30,
        "scope_macro_f1": 0.20,
        "structure_macro_f1": 0.20,
        "slot_span_f1": 0.20,
        "negation_f1": 0.10,
    }
    return sum(float(metrics[name]) * weight for name, weight in weights.items())


def safety_gate_passes(ufar: Mapping[str, Any]) -> bool:
    overall = ufar["UNSAFE_FALSE_ACCEPT_RATE"]
    multi = ufar["per_category"]["MULTI"]["false_accept_rate"]
    ambiguous = ufar["per_category"]["AMBIGUOUS"]["false_accept_rate"]
    return (
        overall is not None
        and overall <= 0.05
        and multi == 0.0
        and ambiguous == 0.0
    )
