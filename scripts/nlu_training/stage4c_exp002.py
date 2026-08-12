"""SYS-014 Stage 4C-A.2: controlled RBT3 exp002 safety fine-tuning."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import torch
import transformers
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from scripts.profile_sys014_stage4a import cpu_name, current_rss_bytes

from .collator import JointNLUCollator
from .dataset import (
    FrozenJointNLUDataset,
    project_all_records,
    training_record_distribution,
)
from .dry_run import set_deterministic_seed, tensor_class_weights
from .labels import (
    IGNORE_INDEX,
    INTENT_LABELS,
    NEGATION_LABELS,
    SCOPE_LABELS,
    SLOT_LABELS,
    STRUCTURE_LABELS,
    label_mapping_report,
)
from .losses import compute_masked_multitask_loss
from .manifest import current_git_commit
from .metrics import (
    classification_metrics,
    extract_bio_spans,
    primary_quality_score,
    safety_gate_passes,
    slot_span_metrics,
    unsafe_false_accept_metrics,
)
from .model import JointNLUModel, representative_parameter_hashes, tensor_sha256
from .train_config import (
    PRIMARY_MODEL_ID,
    PRIMARY_MODEL_REVISION,
    TrainingProtocol,
    primary_snapshot_path,
    repository_root,
)
from .trainer import Stage4CTrainer
from .validation import DATASET_DIR, MANIFEST_PATH, read_split, sha256_file


EXPERIMENT_ID = "sys014-poc7-rbt3-exp002"
EXPERIMENT_DIR = repository_root() / "data" / "nlu" / "experiments" / EXPERIMENT_ID
EXP001_DIR = repository_root() / "data" / "nlu" / "experiments" / "sys014-poc7-rbt3-exp001"
STAGE4C_SEED = 14031
MAX_LENGTH = 32
ACTUAL_BATCH_SIZE = 16
MAX_EPOCHS = 10
EARLY_STOPPING_PATIENCE = 3
BACKBONE_LR = 1e-5
HEAD_LR = 5e-5
LOSS_WEIGHTS = {
    "scope": 1.5,
    "structure": 1.5,
    "intent": 1.0,
    "slot": 1.0,
    "negation": 2.0,
}
TEST_EVALUATION_EXECUTED = False
SAFETY_GOLD_EVALUATION_EXECUTED = False

TRACKED_AMBIGUOUS_IDS = (
    "SYS014-POC-0731",
    "SYS014-POC-0732",
    "SYS014-POC-0733",
)
TRACKED_NEGATION_IDS = (
    "SYS014-POC-0546",
    "SYS014-POC-0547",
    "SYS014-POC-0548",
    "SYS014-POC-0549",
    "SYS014-POC-0550",
    "SYS014-POC-0566",
    "SYS014-POC-0567",
)
ACCELERATE_BOUNDARY_PROBES = (
    "再快一点",
    "速度再快一点",
    "再提点速度",
    "把速度提上去",
    "稍微加点速",
)

REQUIRED_PREDICTION_FIELDS = {
    "sample_id",
    "text",
    "gold_scope",
    "pred_scope",
    "scope_probabilities",
    "scope_top1_top2",
    "gold_structure",
    "pred_structure",
    "structure_probabilities",
    "structure_top1_top2",
    "gold_intent",
    "pred_intent",
    "intent_probabilities",
    "intent_top1_top2",
    "gold_negated",
    "pred_negated",
    "negation_probabilities",
    "gold_slots",
    "predicted_slots",
    "negation_slot_detected",
    "sentence_slot_agreement",
    "raw_executable",
    "raw_abstain",
}


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def protocol() -> TrainingProtocol:
    return TrainingProtocol(
        seed=STAGE4C_SEED,
        training_enabled=True,
        selected_max_length=MAX_LENGTH,
        baseline_epochs=MAX_EPOCHS,
        early_stopping_patience=EARLY_STOPPING_PATIENCE,
        cpu_batch_size=ACTUAL_BATCH_SIZE,
        loss_weights=dict(LOSS_WEIGHTS),
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def append_jsonl(path: Path, value: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, values: Iterable[Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def model_state_digest(model: torch.nn.Module) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        digest.update(name.encode("utf-8"))
        digest.update(value.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def create_experiment_directories() -> None:
    if EXPERIMENT_DIR.exists():
        raise FileExistsError(f"Refusing to overwrite {EXPERIMENT_DIR}")
    EXPERIMENT_DIR.mkdir(parents=False)
    for relative in (
        "checkpoints/best",
        "checkpoints/closest_safety_diagnostic",
        "checkpoints/last",
        "evaluation/validation",
    ):
        (EXPERIMENT_DIR / relative).mkdir(parents=True)


def model_inputs(batch: dict[str, Any], device: torch.device) -> dict[str, torch.Tensor]:
    inputs = {
        "input_ids": batch["input_ids"].to(device),
        "attention_mask": batch["attention_mask"].to(device),
    }
    if "token_type_ids" in batch:
        inputs["token_type_ids"] = batch["token_type_ids"].to(device)
    return inputs


def build_train_distribution(
    tokenizer: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    train_records = read_split("train")
    validation_records = read_split("validation")
    train_slots, train_failures = project_all_records(
        train_records, tokenizer, max_length=MAX_LENGTH
    )
    _, validation_failures = project_all_records(
        validation_records, tokenizer, max_length=MAX_LENGTH
    )
    failures = [
        {"split": "train", **item.to_dict()} for item in train_failures
    ] + [{"split": "validation", **item.to_dict()} for item in validation_failures]
    distribution = training_record_distribution(train_records)
    distribution["slot_token_labels"] = dict(sorted(train_slots.items()))

    exp001_manifest = read_json(EXP001_DIR / "manifest.json")
    expected_files = {
        item["file"]: item["sha256"]
        for item in exp001_manifest["preflight"]["hash_verification"]["verified_files"]
    }
    actual_hashes = {
        "dataset_manifest.json": sha256_file(MANIFEST_PATH),
        "train.jsonl": sha256_file(DATASET_DIR / "train.jsonl"),
        "validation.jsonl": sha256_file(DATASET_DIR / "validation.jsonl"),
    }
    expected_hashes = {
        "dataset_manifest.json": exp001_manifest["dataset_manifest_sha256"],
        "train.jsonl": expected_files["train.jsonl"],
        "validation.jsonl": expected_files["validation.jsonl"],
    }
    if actual_hashes != expected_hashes:
        raise RuntimeError(
            f"FROZEN_V2_HASH_MISMATCH: actual={actual_hashes}, expected={expected_hashes}"
        )
    return {"train": distribution}, failures, actual_hashes


def probability_map(probabilities: torch.Tensor, labels: tuple[str, ...]) -> dict[str, float]:
    return {label: float(probabilities[index]) for index, label in enumerate(labels)}


def top1_top2(probabilities: torch.Tensor, labels: tuple[str, ...]) -> dict[str, Any]:
    values, indices = torch.topk(probabilities, k=2)
    return {
        "top1_class": labels[int(indices[0])],
        "top1_probability": float(values[0]),
        "top2_class": labels[int(indices[1])],
        "top2_probability": float(values[1]),
        "margin": float(values[0] - values[1]),
    }


def predicted_char_slots(
    text: str,
    predicted_label_ids: list[int],
    tokenizer: Any,
) -> list[dict[str, Any]]:
    encoded = tokenizer(
        text,
        add_special_tokens=True,
        truncation=True,
        max_length=MAX_LENGTH,
        return_offsets_mapping=True,
    )
    offsets = encoded["offset_mapping"]
    spans: list[dict[str, Any]] = []
    for slot_type, token_start, token_end in sorted(extract_bio_spans(predicted_label_ids)):
        usable = [
            (int(start), int(end))
            for start, end in offsets[token_start:min(token_end, len(offsets))]
            if int(end) > int(start)
        ]
        if not usable:
            continue
        char_start = min(start for start, _ in usable)
        char_end = max(end for _, end in usable)
        spans.append(
            {
                "slot_type": slot_type,
                "token_start": token_start,
                "token_end": token_end,
                "char_start": char_start,
                "char_end": char_end,
                "text": text[char_start:char_end],
            }
        )
    return spans


def build_prediction_row(
    *,
    sample_id: str,
    text: str,
    record: dict[str, Any],
    scope_probabilities: torch.Tensor,
    structure_probabilities: torch.Tensor,
    intent_probabilities: torch.Tensor,
    negation_probabilities: torch.Tensor,
    gold_slot_ids: list[int],
    predicted_slot_ids: list[int],
    tokenizer: Any,
) -> dict[str, Any]:
    scope_top = top1_top2(scope_probabilities, SCOPE_LABELS)
    structure_top = top1_top2(structure_probabilities, STRUCTURE_LABELS)
    intent_top = top1_top2(intent_probabilities, INTENT_LABELS)
    negation_top = top1_top2(negation_probabilities, NEGATION_LABELS)
    predicted_slots = predicted_char_slots(text, predicted_slot_ids, tokenizer)
    negation_slot_detected = any(
        item["slot_type"] == "NEGATION" for item in predicted_slots
    )
    pred_negated = negation_top["top1_class"] == "NEGATED"
    raw_executable = (
        scope_top["top1_class"] == "IN_SCOPE_CONTROL"
        and structure_top["top1_class"] == "SINGLE"
        and intent_top["top1_class"] in INTENT_LABELS
    )
    return {
        "sample_id": sample_id,
        "text": text,
        "gold_scope": record["scope_label"],
        "pred_scope": scope_top["top1_class"],
        "scope_probabilities": probability_map(scope_probabilities, SCOPE_LABELS),
        "scope_top1_top2": scope_top,
        "gold_structure": record["intent_structure"],
        "pred_structure": structure_top["top1_class"],
        "structure_probabilities": probability_map(
            structure_probabilities, STRUCTURE_LABELS
        ),
        "structure_top1_top2": structure_top,
        "gold_intent": record["intent"],
        "pred_intent": intent_top["top1_class"],
        "intent_probabilities": probability_map(intent_probabilities, INTENT_LABELS),
        "intent_top1_top2": intent_top,
        "gold_negated": record["negated"],
        "pred_negated": pred_negated,
        "negation_probabilities": probability_map(
            negation_probabilities, NEGATION_LABELS
        ),
        "negation_top1_top2": negation_top,
        "gold_slots": record.get("slots", []),
        "gold_slot_token_spans": sorted(extract_bio_spans(gold_slot_ids)),
        "predicted_slots": predicted_slots,
        "predicted_slot_token_spans": sorted(extract_bio_spans(predicted_slot_ids)),
        "negation_slot_detected": negation_slot_detected,
        "sentence_slot_agreement": pred_negated == negation_slot_detected,
        "raw_executable": raw_executable,
        "raw_abstain": not raw_executable,
        "final_raw_decision": "EXECUTABLE" if raw_executable else "ABSTAIN",
    }


def prediction_schema_ok(row: dict[str, Any]) -> bool:
    return REQUIRED_PREDICTION_FIELDS <= row.keys()


def evaluate_validation(
    model: JointNLUModel,
    batches: DataLoader[Any],
    *,
    records_by_id: dict[str, dict[str, Any]],
    tokenizer: Any,
    device: torch.device,
    class_weights: dict[str, torch.Tensor | None],
    training_protocol: TrainingProtocol,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    model.eval()
    loss_totals: Counter[str] = Counter()
    batch_count = 0
    scope_true: list[int] = []
    structure_true: list[int] = []
    intent_true: list[int] = []
    negation_true: list[int] = []
    slot_true: list[list[int]] = []
    scope_pred: list[int] = []
    structure_pred: list[int] = []
    intent_pred: list[int] = []
    negation_pred: list[int] = []
    slot_pred: list[list[int]] = []
    prediction_rows: list[dict[str, Any]] = []

    with torch.inference_mode():
        for batch in batches:
            tensors = {
                key: value.to(device) if isinstance(value, torch.Tensor) else value
                for key, value in batch.items()
            }
            outputs = model(**model_inputs(batch, device))
            losses = compute_masked_multitask_loss(
                outputs,
                tensors,
                loss_weights=training_protocol.loss_weights,
                class_weights=class_weights,
            )
            scalar_losses = {
                name: float(losses[name].detach().cpu())
                for name in (
                    "scope_loss",
                    "structure_loss",
                    "intent_loss",
                    "slot_loss",
                    "negation_loss",
                    "total_loss",
                )
            }
            if not all(math.isfinite(value) for value in scalar_losses.values()):
                raise FloatingPointError(f"NON_FINITE_VALIDATION_LOSS: {scalar_losses}")
            loss_totals.update(scalar_losses)
            batch_count += 1

            scope_probs = torch.softmax(outputs["scope_logits"], dim=-1).cpu()
            structure_probs = torch.softmax(outputs["structure_logits"], dim=-1).cpu()
            intent_probs = torch.softmax(outputs["intent_logits"], dim=-1).cpu()
            negation_probs = torch.softmax(outputs["negation_logits"], dim=-1).cpu()
            batch_scope_pred = scope_probs.argmax(-1).tolist()
            batch_structure_pred = structure_probs.argmax(-1).tolist()
            batch_intent_pred = intent_probs.argmax(-1).tolist()
            batch_negation_pred = negation_probs.argmax(-1).tolist()
            batch_slot_pred = outputs["slot_logits"].argmax(-1).cpu().tolist()

            scope_true.extend(tensors["scope_labels"].cpu().tolist())
            structure_true.extend(tensors["structure_labels"].cpu().tolist())
            intent_true.extend(tensors["intent_labels"].cpu().tolist())
            negation_true.extend(tensors["negation_labels"].cpu().tolist())
            slot_true.extend(tensors["slot_labels"].cpu().tolist())
            scope_pred.extend(batch_scope_pred)
            structure_pred.extend(batch_structure_pred)
            intent_pred.extend(batch_intent_pred)
            negation_pred.extend(batch_negation_pred)

            for index, sample_id in enumerate(batch["sample_ids"]):
                gold_slot_ids = tensors["slot_labels"][index].cpu().tolist()
                predicted_slot_ids = [
                    IGNORE_INDEX if gold == IGNORE_INDEX else int(predicted)
                    for gold, predicted in zip(
                        gold_slot_ids, batch_slot_pred[index], strict=True
                    )
                ]
                slot_pred.append(predicted_slot_ids)
                row = build_prediction_row(
                    sample_id=sample_id,
                    text=batch["texts"][index],
                    record=records_by_id[sample_id],
                    scope_probabilities=scope_probs[index],
                    structure_probabilities=structure_probs[index],
                    intent_probabilities=intent_probs[index],
                    negation_probabilities=negation_probs[index],
                    gold_slot_ids=gold_slot_ids,
                    predicted_slot_ids=predicted_slot_ids,
                    tokenizer=tokenizer,
                )
                if not prediction_schema_ok(row):
                    raise AssertionError(f"prediction schema incomplete for {sample_id}")
                prediction_rows.append(row)

    intent_indices = [
        index for index, label in enumerate(intent_true) if label != IGNORE_INDEX
    ]
    negation_indices = [
        index for index, label in enumerate(negation_true) if label != IGNORE_INDEX
    ]
    intent_metrics = classification_metrics(
        [intent_true[index] for index in intent_indices],
        [intent_pred[index] for index in intent_indices],
        label_names=INTENT_LABELS,
    )
    scope_metrics = classification_metrics(
        scope_true, scope_pred, label_names=SCOPE_LABELS
    )
    structure_metrics = classification_metrics(
        structure_true, structure_pred, label_names=STRUCTURE_LABELS
    )
    negation_metrics = classification_metrics(
        [negation_true[index] for index in negation_indices],
        [negation_pred[index] for index in negation_indices],
        label_names=NEGATION_LABELS,
    )
    slots = slot_span_metrics(slot_true, slot_pred)
    ufar = unsafe_false_accept_metrics(
        true_scope=scope_true,
        true_structure=structure_true,
        pred_scope=scope_pred,
        pred_structure=structure_pred,
        pred_intent=intent_pred,
    )
    quality_inputs = {
        "intent_macro_f1": intent_metrics["macro_f1"],
        "scope_macro_f1": scope_metrics["macro_f1"],
        "structure_macro_f1": structure_metrics["macro_f1"],
        "slot_span_f1": slots["OVERALL"]["f1"],
        "negation_f1": negation_metrics["per_class"]["NEGATED"]["f1"],
    }
    per_intent_negation: dict[str, Any] = {}
    for intent_id, intent_name in enumerate(INTENT_LABELS):
        indices = [index for index in intent_indices if intent_true[index] == intent_id]
        if not any(negation_true[index] == 1 for index in indices):
            per_intent_negation[intent_name] = "NOT_ESTIMABLE"
        else:
            per_intent_negation[intent_name] = classification_metrics(
                [negation_true[index] for index in indices],
                [negation_pred[index] for index in indices],
                label_names=NEGATION_LABELS,
            )

    tracked_ambiguous = {
        row["sample_id"]: row
        for row in prediction_rows
        if row["sample_id"] in TRACKED_AMBIGUOUS_IDS
    }
    tracked_negation = {
        row["sample_id"]: {
            "sample_id": row["sample_id"],
            "text": row["text"],
            "sentence_negation_prediction": (
                "NEGATED" if row["pred_negated"] else "NOT_NEGATED"
            ),
            "sentence_negation_probability": row["negation_top1_top2"][
                "top1_probability"
            ],
            "negation_slot_detected": row["negation_slot_detected"],
            "sentence_slot_agreement": row["sentence_slot_agreement"],
        }
        for row in prediction_rows
        if row["sample_id"] in TRACKED_NEGATION_IDS
    }
    negation_disagreements = sum(
        not row["sentence_slot_agreement"]
        for row in prediction_rows
        if row["gold_negated"] is not None
    )
    error_cases = [
        {
            "sample_id": row["sample_id"],
            "text": row["text"],
            "gold_scope": row["gold_scope"],
            "pred_scope": row["pred_scope"],
            "gold_structure": row["gold_structure"],
            "pred_structure": row["pred_structure"],
            "gold_intent": row["gold_intent"],
            "pred_intent": row["pred_intent"],
            "gold_negated": row["gold_negated"],
            "pred_negated": row["pred_negated"],
            "gold_slots": row["gold_slots"],
            "predicted_slots": row["predicted_slots"],
        }
        for row in prediction_rows
        if row["gold_scope"] != row["pred_scope"]
        or row["gold_structure"] != row["pred_structure"]
        or (row["gold_intent"] is not None and row["gold_intent"] != row["pred_intent"])
        or (
            row["gold_negated"] is not None
            and row["gold_negated"] != row["pred_negated"]
        )
        or row["gold_slot_token_spans"] != row["predicted_slot_token_spans"]
    ]
    metrics = {
        "losses": {
            name: value / max(batch_count, 1) for name, value in loss_totals.items()
        },
        "intent": intent_metrics,
        "scope": scope_metrics,
        "structure": structure_metrics,
        "slot": slots,
        "negation": negation_metrics,
        "per_intent_negation": per_intent_negation,
        "safety": {
            "metric_name": "RAW_VALIDATION_UFAR",
            "deployment_calibrated": False,
            **ufar,
        },
        "primary_quality_inputs": quality_inputs,
        "PRIMARY_QUALITY_SCORE": primary_quality_score(quality_inputs),
        "SAFETY_GATES_PASS": safety_gate_passes(ufar),
        "NEGATION_HEAD_SLOT_DISAGREEMENT_COUNT": negation_disagreements,
        "tracked_ambiguous_family": tracked_ambiguous,
        "tracked_negation_cases": tracked_negation,
        "error_cases": error_cases,
    }
    return metrics, prediction_rows


def run_boundary_probes(
    model: JointNLUModel, tokenizer: Any, device: torch.device
) -> dict[str, Any]:
    model.eval()
    encoded = tokenizer(
        list(ACCELERATE_BOUNDARY_PROBES),
        padding=True,
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors="pt",
    )
    inputs = {
        key: value.to(device)
        for key, value in encoded.items()
        if key in {"input_ids", "attention_mask", "token_type_ids"}
    }
    with torch.inference_mode():
        outputs = model(**inputs)
    scope_probabilities = torch.softmax(outputs["scope_logits"], dim=-1).cpu()
    structure_probabilities = torch.softmax(outputs["structure_logits"], dim=-1).cpu()
    intent_probabilities = torch.softmax(outputs["intent_logits"], dim=-1).cpu()
    rows: list[dict[str, Any]] = []
    for index, text in enumerate(ACCELERATE_BOUNDARY_PROBES):
        scope = top1_top2(scope_probabilities[index], SCOPE_LABELS)
        structure = top1_top2(structure_probabilities[index], STRUCTURE_LABELS)
        intent = top1_top2(intent_probabilities[index], INTENT_LABELS)
        accepted_as_accelerate = (
            scope["top1_class"] == "IN_SCOPE_CONTROL"
            and structure["top1_class"] == "SINGLE"
            and intent["top1_class"] == "ACCELERATE"
        )
        rows.append(
            {
                "text": text,
                "scope": scope,
                "structure": structure,
                "intent": intent,
                "accepted_as_clear_accelerate": accepted_as_accelerate,
                "false_reject": not accepted_as_accelerate,
                "probe_only_not_used_for_loss_or_checkpoint_selection": True,
            }
        )
    return {
        "ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT": sum(
            row["false_reject"] for row in rows
        ),
        "probe_count": len(rows),
        "rows": rows,
    }


def failed_safety_gate_count(metrics: dict[str, Any]) -> int:
    safety = metrics["safety"]
    return sum(
        (
            safety["UNSAFE_FALSE_ACCEPT_RATE"] is None
            or safety["UNSAFE_FALSE_ACCEPT_RATE"] > 0.05,
            safety["per_category"]["MULTI"]["false_accept_rate"] != 0.0,
            safety["per_category"]["AMBIGUOUS"]["false_accept_rate"] != 0.0,
        )
    )


def closest_key(metrics: dict[str, Any]) -> tuple[int, int, int, float]:
    safety = metrics["safety"]
    return (
        failed_safety_gate_count(metrics),
        safety["per_category"]["AMBIGUOUS"]["unsafe_false_accepts"]
        + safety["per_category"]["MULTI"]["unsafe_false_accepts"],
        safety["unsafe_false_accepts"],
        -float(metrics["PRIMARY_QUALITY_SCORE"]),
    )


def save_checkpoint(
    directory: Path,
    model: JointNLUModel,
    training_protocol: TrainingProtocol,
    *,
    epoch: int,
    metrics: dict[str, Any],
    checkpoint_kind: str,
    prediction_artifact: str,
    best: bool,
    deployable: bool,
    ranking_key: tuple[int, int, int, float] | None = None,
) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    model_state_path = directory / "model_state.pt"
    torch.save(model.state_dict(), model_state_path)
    write_json(directory / "label_mapping.json", label_mapping_report())
    write_json(
        directory / "model_config.json",
        {
            "backbone_path": str(primary_snapshot_path()),
            "backbone_revision": PRIMARY_MODEL_REVISION,
            "heads": {
                "scope": len(SCOPE_LABELS),
                "structure": len(STRUCTURE_LABELS),
                "intent": len(INTENT_LABELS),
                "slot": len(SLOT_LABELS),
                "negation": len(NEGATION_LABELS),
            },
            "sentence_representation": "FIRST_TOKEN",
        },
    )
    write_json(
        directory / "training_config.json",
        {
            **training_protocol.to_dict(),
            "baseline_learning_rate_used": False,
            "discriminative_learning_rate": True,
            "optimizer_parameter_groups": {
                "backbone": BACKBONE_LR,
                "joint_heads": HEAD_LR,
            },
            "effective_loss_weights": dict(LOSS_WEIGHTS),
        },
    )
    manifest = {
        "checkpoint_format": "PYTORCH_STATE_DICT",
        "checkpoint_kind": checkpoint_kind,
        "epoch": epoch,
        "BEST": best,
        "DEPLOYABLE": deployable,
        "model_id": PRIMARY_MODEL_ID,
        "model_revision": PRIMARY_MODEL_REVISION,
        "initialized_from_original_pretrained_rbt3": True,
        "continued_from_exp001_checkpoint": False,
        "baseline_learning_rate_used": False,
        "optimizer_parameter_groups": {
            "backbone": BACKBONE_LR,
            "joint_heads": HEAD_LR,
        },
        "effective_loss_weights": dict(LOSS_WEIGHTS),
        "dataset_version": training_protocol.dataset_version,
        "dataset_manifest_sha256": sha256_file(MANIFEST_PATH),
        "model_state_file": "model_state.pt",
        "model_state_sha256": sha256_file(model_state_path),
        "prediction_artifact": prediction_artifact,
        "validation_primary_quality_score": metrics["PRIMARY_QUALITY_SCORE"],
        "validation_safety_gates_pass": metrics["SAFETY_GATES_PASS"],
        "failed_safety_gate_count": failed_safety_gate_count(metrics),
        "closest_ranking_key": list(ranking_key) if ranking_key is not None else None,
        "test_evaluation_executed": False,
        "safety_gold_evaluation_executed": False,
    }
    write_json(directory / "checkpoint_manifest.json", manifest)
    return manifest


def initial_vs_exp001_audit(model: JointNLUModel) -> dict[str, Any]:
    exp001_checkpoint = EXP001_DIR / "checkpoints" / "last" / "model_state.pt"
    exp001_state = torch.load(exp001_checkpoint, map_location="cpu", weights_only=True)
    fresh_state = model.state_dict()
    shared = sorted(set(exp001_state) & set(fresh_state))
    differences = [name for name in shared if not torch.equal(exp001_state[name], fresh_state[name])]
    backbone_differences = [name for name in differences if name.startswith("backbone.")]
    head_differences = [name for name in differences if name.endswith(("weight", "bias")) and not name.startswith("backbone.")]
    if not backbone_differences or not head_differences or not differences:
        raise AssertionError(
            "fresh exp002 initialization is not sufficiently distinct from exp001 last checkpoint"
        )
    return {
        "fresh_state_matches_exp001_last": False,
        "shared_state_tensor_count": len(shared),
        "different_state_tensor_count": len(differences),
        "different_backbone_tensor_count": len(backbone_differences),
        "different_joint_head_tensor_count": len(head_differences),
        "exp001_last_checkpoint_sha256": sha256_file(exp001_checkpoint),
        "exp001_checkpoint_loaded_into_exp002_model": False,
        "exp002_initialization_source": str(primary_snapshot_path()),
        "exp002_initialization_revision": PRIMARY_MODEL_REVISION,
    }


def run_preflight(*, require_experiment_absent: bool = True) -> dict[str, Any]:
    if require_experiment_absent and EXPERIMENT_DIR.exists():
        raise FileExistsError(f"Preflight refuses existing experiment: {EXPERIMENT_DIR}")
    training_protocol = protocol()
    set_deterministic_seed(STAGE4C_SEED)
    tokenizer = AutoTokenizer.from_pretrained(
        primary_snapshot_path(), local_files_only=True, use_fast=True
    )
    distribution, projection_failures, dataset_hashes = build_train_distribution(
        tokenizer
    )
    if projection_failures:
        raise RuntimeError(f"TOKEN_PROJECTION_FAILURES={len(projection_failures)}")
    train_dataset = FrozenJointNLUDataset("train", tokenizer, max_length=MAX_LENGTH)
    validation_dataset = FrozenJointNLUDataset(
        "validation", tokenizer, max_length=MAX_LENGTH
    )
    collator = JointNLUCollator(tokenizer)
    validation_batch = collator([validation_dataset[index] for index in range(16)])
    records_by_id = {
        record["sample_id"]: record for record in validation_dataset.records
    }
    device = torch.device("cpu")
    model = JointNLUModel(str(primary_snapshot_path())).to(device)
    initial_digest = model_state_digest(model)
    exp001_audit = initial_vs_exp001_audit(model)
    total_optimizer_steps = math.ceil(len(train_dataset) / ACTUAL_BATCH_SIZE) * MAX_EPOCHS
    trainer = Stage4CTrainer(
        model,
        training_protocol,
        device=device,
        total_optimizer_steps=total_optimizer_steps,
        backbone_learning_rate=BACKBONE_LR,
        joint_head_learning_rate=HEAD_LR,
    )
    class_weights = tensor_class_weights(distribution, training_protocol, device)
    if trainer.parameter_group_audit is None:
        raise AssertionError("missing discriminative parameter group audit")
    if len(trainer.optimizer.param_groups) != 2:
        raise AssertionError("exp002 requires exactly two optimizer groups")
    if [float(value) for value in trainer.scheduler.base_lrs] != [
        BACKBONE_LR,
        HEAD_LR,
    ]:
        raise AssertionError("optimizer group base learning rates do not match exp002 protocol")

    # One Validation batch only; inference mode proves the schema without a training step.
    model.eval()
    with torch.inference_mode():
        outputs = model(**model_inputs(validation_batch, device))
    scope_probabilities = torch.softmax(outputs["scope_logits"], dim=-1).cpu()
    structure_probabilities = torch.softmax(outputs["structure_logits"], dim=-1).cpu()
    intent_probabilities = torch.softmax(outputs["intent_logits"], dim=-1).cpu()
    negation_probabilities = torch.softmax(outputs["negation_logits"], dim=-1).cpu()
    gold_slot_ids = validation_batch["slot_labels"][0].tolist()
    predicted_slot_ids = [
        IGNORE_INDEX if gold == IGNORE_INDEX else int(predicted)
        for gold, predicted in zip(
            gold_slot_ids, outputs["slot_logits"].argmax(-1).cpu()[0].tolist(), strict=True
        )
    ]
    sample_id = validation_batch["sample_ids"][0]
    schema_row = build_prediction_row(
        sample_id=sample_id,
        text=validation_batch["texts"][0],
        record=records_by_id[sample_id],
        scope_probabilities=scope_probabilities[0],
        structure_probabilities=structure_probabilities[0],
        intent_probabilities=intent_probabilities[0],
        negation_probabilities=negation_probabilities[0],
        gold_slot_ids=gold_slot_ids,
        predicted_slot_ids=predicted_slot_ids,
        tokenizer=tokenizer,
    )
    after_digest = model_state_digest(model)
    if initial_digest != after_digest or any(
        parameter.grad is not None for parameter in model.parameters()
    ):
        raise AssertionError("preflight changed model parameters or created gradients")
    if trainer.training_steps_executed != 0:
        raise AssertionError("preflight executed a training step")

    default_model = torch.nn.Linear(3, 2)
    default_trainer = Stage4CTrainer(
        default_model,
        training_protocol,
        device=device,
        total_optimizer_steps=10,
    )
    default_compatible = (
        len(default_trainer.optimizer.param_groups) == 1
        and float(default_trainer.scheduler.base_lrs[0])
        == training_protocol.baseline_learning_rate
        and not default_trainer.discriminative_learning_rates
    )
    if not default_compatible:
        raise AssertionError("exp001/default trainer compatibility failed")

    return {
        "PREFLIGHT": "PASS",
        "experiment_absent": not EXPERIMENT_DIR.exists(),
        "dataset_hashes": dataset_hashes,
        "projection_failures": 0,
        "train_count": len(train_dataset),
        "validation_count": len(validation_dataset),
        "test_records_loaded": 0,
        "safety_gold_records_loaded": 0,
        "test_used_for_model_selection": False,
        "safety_gold_used_for_model_selection": False,
        "fresh_initialization_audit": exp001_audit,
        "parameter_group_audit": trainer.parameter_group_audit,
        "optimizer_group_base_lrs": {
            "backbone": float(trainer.scheduler.base_lrs[0]),
            "joint_heads": float(trainer.scheduler.base_lrs[1]),
        },
        "optimizer_group_current_lrs_after_scheduler_initialization": {
            "backbone": float(trainer.optimizer.param_groups[0]["lr"]),
            "joint_heads": float(trainer.optimizer.param_groups[1]["lr"]),
        },
        "scheduler_optimizer_group_count": len(trainer.scheduler.optimizer.param_groups),
        "class_weight_tensor_shapes": {
            name: (list(value.shape) if value is not None else None)
            for name, value in class_weights.items()
        },
        "prediction_schema_valid": prediction_schema_ok(schema_row),
        "prediction_schema_fields": sorted(schema_row),
        "model_state_digest_before_forward": initial_digest,
        "model_state_digest_after_forward": after_digest,
        "model_parameters_unchanged": initial_digest == after_digest,
        "gradients_created": False,
        "training_steps_executed": 0,
        "backward_preflight_executed": False,
        "default_exp001_trainer_path_compatible": default_compatible,
        "python_executable": os.path.realpath(sys_executable()),
    }


def sys_executable() -> str:
    return os.sys.executable


def exp001_tracked_outcome(sample_id: str) -> dict[str, Any]:
    history = read_jsonl(EXP001_DIR / "metrics_by_epoch.jsonl")
    epoch5 = next(row for row in history if row["epoch"] == 5)["validation"]
    error = next(
        (item for item in epoch5["error_cases"] if item["sample_id"] == sample_id),
        None,
    )
    validation_records = {record["sample_id"]: record for record in read_split("validation")}
    gold = validation_records[sample_id]
    if error is None:
        pred_scope = gold["scope_label"]
        pred_structure = gold["intent_structure"]
        pred_intent = "NOT_AVAILABLE_FROM_EXP001_EPOCH5_ARTIFACTS"
    else:
        pred_scope = SCOPE_LABELS[int(error["predicted"]["scope"])]
        pred_structure = STRUCTURE_LABELS[int(error["predicted"]["structure"])]
        pred_intent = INTENT_LABELS[int(error["predicted"]["intent"])]
    final_abstain = not (
        pred_scope == "IN_SCOPE_CONTROL" and pred_structure == "SINGLE"
    )
    return {
        "scope": pred_scope,
        "structure": pred_structure,
        "intent": pred_intent,
        "final_abstain": final_abstain,
    }


def comparison_markdown(
    selected_epoch: int,
    selected_kind: str,
    selected: dict[str, Any],
    boundary: dict[str, Any],
    mean_epoch_seconds: float,
    best_epoch: int | None,
) -> str:
    exp001_summary = read_json(EXP001_DIR / "training_summary.json")
    exp001 = read_json(EXP001_DIR / "best_validation_metrics.json")[
        "closest_safety_candidate_metrics"
    ]
    rows_002 = selected["tracked_ambiguous_family"]
    tracked_lines = "\n".join(
        f"- {sample_id}: exp001={exp001_tracked_outcome(sample_id)}；"
        f"exp002={{'scope': '{rows_002[sample_id]['pred_scope']}', "
        f"'structure': '{rows_002[sample_id]['pred_structure']}', "
        f"'intent': '{rows_002[sample_id]['pred_intent']}', "
        f"'final_abstain': {rows_002[sample_id]['raw_abstain']}}}"
        for sample_id in TRACKED_AMBIGUOUS_IDS
    )
    return f"""# RBT3 exp001 vs exp002

exp001 使用统一 `2e-5` LR 和五任务等权；exp002 使用 backbone/head `1e-5/5e-5` 与 `1.5/1.5/1/1/2` safety-focused loss。两项策略同时变化，因此只能报告联合变化与结果相关，不能证明任何单项的独立因果效应。

| 指标 | exp001 closest epoch 5 | exp002 {selected_kind} epoch {selected_epoch} |
|---|---:|---:|
| Intent Macro F1 | {exp001['intent']['macro_f1']:.6f} | {selected['intent']['macro_f1']:.6f} |
| Scope Macro F1 | {exp001['scope']['macro_f1']:.6f} | {selected['scope']['macro_f1']:.6f} |
| Structure Macro F1 | {exp001['structure']['macro_f1']:.6f} | {selected['structure']['macro_f1']:.6f} |
| Slot Span F1 | {exp001['slot']['OVERALL']['f1']:.6f} | {selected['slot']['OVERALL']['f1']:.6f} |
| Negation F1 | {exp001['negation']['per_class']['NEGATED']['f1']:.6f} | {selected['negation']['per_class']['NEGATED']['f1']:.6f} |
| NEGATED Recall | {exp001['negation']['per_class']['NEGATED']['recall']:.6f} | {selected['negation']['per_class']['NEGATED']['recall']:.6f} |
| RAW UFAR | {exp001['safety']['UNSAFE_FALSE_ACCEPT_RATE']:.6f} | {selected['safety']['UNSAFE_FALSE_ACCEPT_RATE']:.6f} |
| AMBIGUOUS false accepts | {exp001['safety']['per_category']['AMBIGUOUS']['unsafe_false_accepts']} | {selected['safety']['per_category']['AMBIGUOUS']['unsafe_false_accepts']} |
| MULTI false accepts | {exp001['safety']['per_category']['MULTI']['unsafe_false_accepts']} | {selected['safety']['per_category']['MULTI']['unsafe_false_accepts']} |
| HEADLIGHT_OFF negated recall | {exp001['per_intent_negation']['HEADLIGHT_OFF']['per_class']['NEGATED']['recall']:.6f} | {selected['per_intent_negation']['HEADLIGHT_OFF']['per_class']['NEGATED']['recall']:.6f} |
| ACCELERATE negated recall | {exp001['per_intent_negation']['ACCELERATE']['per_class']['NEGATED']['recall']:.6f} | {selected['per_intent_negation']['ACCELERATE']['per_class']['NEGATED']['recall']:.6f} |
| CPU mean epoch seconds | {exp001_summary['MEAN_EPOCH_SECONDS']:.6f} | {mean_epoch_seconds:.6f} |
| Best eligible epoch | NOT_AVAILABLE | {best_epoch if best_epoch is not None else 'NOT_AVAILABLE'} |

## 0731 / 0732 / 0733

{tracked_lines}

## ACCELERATE 边界 probes

exp002 false reject count：`{boundary['ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT']}/5`。这些文本仅用于 forward probe，不进入 loss、PRIMARY_QUALITY_SCORE 或 checkpoint selection。
"""


def training_summary_markdown(summary: dict[str, Any]) -> str:
    selected = summary["SELECTED_VALIDATION_METRICS"]
    safety = selected["safety"]
    return f"""# SYS-014 RBT3 exp002 训练总结

## 训练与选择

- device：`{summary['TRAINING_DEVICE']}`；epochs：`{summary['EPOCHS_COMPLETED']}`；steps：`{summary['TRAINING_STEPS_EXECUTED']}`。
- backbone/head LR：`{summary['BACKBONE_LR']}` / `{summary['HEAD_LR']}`。
- reporting checkpoint：`{summary['REPORTING_CHECKPOINT_KIND']}` epoch `{summary['REPORTING_EPOCH']}`。
- best eligible epoch：`{summary['BEST_EPOCH']}`。

## Validation

- Intent/Scope/Structure Macro F1：`{selected['intent']['macro_f1']:.6f}` / `{selected['scope']['macro_f1']:.6f}` / `{selected['structure']['macro_f1']:.6f}`。
- Slot Span F1：`{selected['slot']['OVERALL']['f1']:.6f}`。
- Negation F1 / NEGATED Recall：`{selected['negation']['per_class']['NEGATED']['f1']:.6f}` / `{selected['negation']['per_class']['NEGATED']['recall']:.6f}`。
- RAW UFAR：`{safety['UNSAFE_FALSE_ACCEPT_RATE']:.6f}`；AMBIGUOUS/MULTI false accepts：`{safety['per_category']['AMBIGUOUS']['unsafe_false_accepts']}` / `{safety['per_category']['MULTI']['unsafe_false_accepts']}`。

## 冻结标志

```text
RBT3_EXP002_SAFETY_GATE_PASS={'YES' if summary['RBT3_EXP002_SAFETY_GATE_PASS'] else 'NO'}
RBT3_EXP002_NEGATION_IMPROVED={'YES' if summary['RBT3_EXP002_NEGATION_IMPROVED'] else 'NO'}
BEST_CHECKPOINT_SAVED={'YES' if summary['BEST_CHECKPOINT_SAVED'] else 'NO'}
TEST_EVALUATION_EXECUTED=NO
SAFETY_GOLD_EVALUATION_EXECUTED=NO
READY_FOR_STAGE_4C_NEXT_DECISION={'YES' if summary['READY_FOR_STAGE_4C_NEXT_DECISION'] else 'NO'}
```

本阶段没有修改 runtime、冻结数据或 safety gates，没有启动 ELECTRA。
"""


def run_training() -> int:
    if EXPERIMENT_DIR.exists():
        raise FileExistsError(f"Refusing to overwrite {EXPERIMENT_DIR}")
    preflight = run_preflight(require_experiment_absent=True)
    training_protocol = protocol()
    set_deterministic_seed(STAGE4C_SEED)
    tokenizer = AutoTokenizer.from_pretrained(
        primary_snapshot_path(), local_files_only=True, use_fast=True
    )
    distribution, projection_failures, dataset_hashes = build_train_distribution(
        tokenizer
    )
    if projection_failures:
        raise RuntimeError(f"TOKEN_PROJECTION_FAILURES={len(projection_failures)}")
    train_dataset = FrozenJointNLUDataset("train", tokenizer, max_length=MAX_LENGTH)
    validation_dataset = FrozenJointNLUDataset(
        "validation", tokenizer, max_length=MAX_LENGTH
    )
    records_by_id = {
        record["sample_id"]: record for record in validation_dataset.records
    }
    collator = JointNLUCollator(tokenizer)
    generator = torch.Generator().manual_seed(STAGE4C_SEED)
    train_loader = DataLoader(
        train_dataset,
        batch_size=ACTUAL_BATCH_SIZE,
        shuffle=True,
        generator=generator,
        num_workers=0,
        collate_fn=collator,
    )
    validation_loader = DataLoader(
        validation_dataset,
        batch_size=ACTUAL_BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        collate_fn=collator,
    )
    device = torch.device("cpu")
    model = JointNLUModel(str(primary_snapshot_path())).to(device)
    initialization_audit = initial_vs_exp001_audit(model)
    initial_backbone_hashes = representative_parameter_hashes(model.backbone)
    initial_joint_head_hashes = {
        name: tensor_sha256(parameter)
        for name, parameter in model.named_parameters()
        if not name.startswith("backbone.")
    }
    total_optimizer_steps = len(train_loader) * MAX_EPOCHS
    trainer = Stage4CTrainer(
        model,
        training_protocol,
        device=device,
        total_optimizer_steps=total_optimizer_steps,
        backbone_learning_rate=BACKBONE_LR,
        joint_head_learning_rate=HEAD_LR,
    )
    class_weights = tensor_class_weights(distribution, training_protocol, device)

    create_experiment_directories()
    started_at = iso_now()
    experiment_config = {
        **training_protocol.to_dict(),
        "experiment_id": EXPERIMENT_ID,
        "actual_batch_size": ACTUAL_BATCH_SIZE,
        "training_device": "CPU",
        "backbone_learning_rate": BACKBONE_LR,
        "joint_head_learning_rate": HEAD_LR,
        "discriminative_learning_rate": True,
        "baseline_learning_rate_used": False,
        "parameter_group_audit": trainer.parameter_group_audit,
        "total_optimizer_steps": total_optimizer_steps,
        "warmup_steps": trainer.warmup_steps,
        "closest_safety_diagnostic_sort": [
            "failed_safety_gate_count ASC",
            "ambiguous_plus_multi_false_accept_count ASC",
            "total_unsafe_false_accepts ASC",
            "primary_quality_score DESC",
        ],
        "initialized_from_original_pretrained_rbt3": True,
        "continued_from_exp001_checkpoint": False,
        "test_used_for_model_selection": False,
        "safety_gold_used_for_model_selection": False,
        "confidence_threshold_used_for_selection": False,
    }
    write_json(EXPERIMENT_DIR / "experiment_config.json", experiment_config)
    write_json(EXPERIMENT_DIR / "preflight.json", preflight)
    (EXPERIMENT_DIR / "training_log.jsonl").write_text("", encoding="utf-8")
    (EXPERIMENT_DIR / "metrics_by_epoch.jsonl").write_text("", encoding="utf-8")
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "status": "RUNNING",
        "dataset_version": training_protocol.dataset_version,
        "dataset_hashes": dataset_hashes,
        "model_id": PRIMARY_MODEL_ID,
        "model_revision": PRIMARY_MODEL_REVISION,
        "seed": STAGE4C_SEED,
        "device": "CPU",
        "cpu_model": cpu_name(),
        "torch_threads": torch.get_num_threads(),
        "torch_interop_threads": torch.get_num_interop_threads(),
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "python_executable": os.path.realpath(sys_executable()),
        "git_commit": current_git_commit(),
        "started_at": started_at,
        "finished_at": None,
        "test_evaluation_executed": False,
        "safety_gold_evaluation_executed": False,
        "electra_training_started": False,
        "runtime_modified": False,
        "preflight": preflight,
        "initialization_audit": initialization_audit,
    }
    write_json(EXPERIMENT_DIR / "manifest.json", manifest)
    append_jsonl(
        EXPERIMENT_DIR / "training_log.jsonl",
        {"event": "TRAINING_STARTED", "at": started_at, "config": experiment_config},
    )

    training_started = time.perf_counter()
    epoch_durations: list[float] = []
    history: list[dict[str, Any]] = []
    best_metrics: dict[str, Any] | None = None
    best_epoch: int | None = None
    best_score = -1.0
    best_manifest: dict[str, Any] | None = None
    best_prediction_artifact: str | None = None
    closest_metrics: dict[str, Any] | None = None
    closest_epoch: int | None = None
    closest_ranking: tuple[int, int, int, float] | None = None
    closest_manifest: dict[str, Any] | None = None
    closest_prediction_artifact: str | None = None
    selected_boundaries: dict[int, dict[str, Any]] = {}
    stale_epochs = 0
    non_finite = False

    try:
        for epoch in range(1, MAX_EPOCHS + 1):
            epoch_started = time.perf_counter()
            train_started = time.perf_counter()
            train_result = trainer.train_epoch(train_loader, class_weights=class_weights)
            train_seconds = time.perf_counter() - train_started
            lr_steps = train_result.pop("learning_rate_steps")
            for step_record in lr_steps:
                append_jsonl(
                    EXPERIMENT_DIR / "training_log.jsonl",
                    {"event": "OPTIMIZER_STEP_LR", "epoch": epoch, **step_record},
                )
            validation_started = time.perf_counter()
            validation, prediction_rows = evaluate_validation(
                model,
                validation_loader,
                records_by_id=records_by_id,
                tokenizer=tokenizer,
                device=device,
                class_weights=class_weights,
                training_protocol=training_protocol,
            )
            validation_seconds = time.perf_counter() - validation_started
            boundary = run_boundary_probes(model, tokenizer, device)
            selected_boundaries[epoch] = boundary
            validation["ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT"] = boundary[
                "ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT"
            ]
            validation["accelerate_boundary_probes"] = boundary
            prediction_relative = (
                f"evaluation/validation/epoch_{epoch:02d}_predictions.jsonl"
            )
            write_jsonl(EXPERIMENT_DIR / prediction_relative, prediction_rows)
            epoch_seconds = time.perf_counter() - epoch_started
            epoch_durations.append(epoch_seconds)
            record = {
                "epoch": epoch,
                "train": train_result,
                "validation": validation,
                "prediction_artifact": prediction_relative,
                "train_seconds": train_seconds,
                "validation_seconds": validation_seconds,
                "epoch_seconds": epoch_seconds,
            }
            history.append(record)
            append_jsonl(EXPERIMENT_DIR / "metrics_by_epoch.jsonl", record)

            score = float(validation["PRIMARY_QUALITY_SCORE"])
            eligible = bool(validation["SAFETY_GATES_PASS"])
            if eligible and score > best_score:
                best_score = score
                best_epoch = epoch
                best_metrics = validation
                best_prediction_artifact = prediction_relative
                stale_epochs = 0
                best_manifest = save_checkpoint(
                    EXPERIMENT_DIR / "checkpoints" / "best",
                    model,
                    training_protocol,
                    epoch=epoch,
                    metrics=validation,
                    checkpoint_kind="ELIGIBLE_BEST",
                    prediction_artifact=prediction_relative,
                    best=True,
                    deployable=False,
                )
            elif best_metrics is not None:
                stale_epochs += 1

            if not eligible:
                ranking = closest_key(validation)
                if closest_ranking is None or ranking < closest_ranking:
                    closest_ranking = ranking
                    closest_epoch = epoch
                    closest_metrics = validation
                    closest_prediction_artifact = prediction_relative
                    closest_manifest = save_checkpoint(
                        EXPERIMENT_DIR / "checkpoints" / "closest_safety_diagnostic",
                        model,
                        training_protocol,
                        epoch=epoch,
                        metrics=validation,
                        checkpoint_kind="CLOSEST_SAFETY_DIAGNOSTIC",
                        prediction_artifact=prediction_relative,
                        best=False,
                        deployable=False,
                        ranking_key=ranking,
                    )

            tracked = validation["tracked_ambiguous_family"]
            print(
                json.dumps(
                    {
                        "epoch": epoch,
                        "quality": score,
                        "eligible": eligible,
                        "ufar": validation["safety"]["UNSAFE_FALSE_ACCEPT_RATE"],
                        "ambiguous_false_accepts": validation["safety"]["per_category"]["AMBIGUOUS"]["unsafe_false_accepts"],
                        "multi_false_accepts": validation["safety"]["per_category"]["MULTI"]["unsafe_false_accepts"],
                        "negated_recall": validation["negation"]["per_class"]["NEGATED"]["recall"],
                        "0731_raw_abstain": tracked["SYS014-POC-0731"]["raw_abstain"],
                        "0732_raw_abstain": tracked["SYS014-POC-0732"]["raw_abstain"],
                        "0733_raw_abstain": tracked["SYS014-POC-0733"]["raw_abstain"],
                        "boundary_false_rejects": boundary["ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT"],
                        "epoch_seconds": epoch_seconds,
                        "training_steps": trainer.training_steps_executed,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            append_jsonl(
                EXPERIMENT_DIR / "training_log.jsonl",
                {
                    "event": "EPOCH_FINISHED",
                    "epoch": epoch,
                    "eligible": eligible,
                    "quality": score,
                    "safety": validation["safety"],
                    "tracked_ambiguous_family": tracked,
                    "tracked_negation_cases": validation["tracked_negation_cases"],
                    "accelerate_boundary": boundary,
                },
            )
            if best_metrics is not None and stale_epochs >= EARLY_STOPPING_PATIENCE:
                append_jsonl(
                    EXPERIMENT_DIR / "training_log.jsonl",
                    {
                        "event": "EARLY_STOPPING",
                        "epoch": epoch,
                        "stale_eligible_epochs": stale_epochs,
                    },
                )
                break
    except FloatingPointError as exc:
        non_finite = True
        append_jsonl(
            EXPERIMENT_DIR / "training_log.jsonl",
            {"event": "TRAINING_ABORTED_NON_FINITE", "at": iso_now(), "error": str(exc)},
        )

    total_training_seconds = time.perf_counter() - training_started
    epochs_completed = len(history)
    if not history:
        raise RuntimeError("exp002 completed no Validation epoch")
    last_metrics = history[-1]["validation"]
    last_prediction_artifact = history[-1]["prediction_artifact"]
    last_manifest = save_checkpoint(
        EXPERIMENT_DIR / "checkpoints" / "last",
        model,
        training_protocol,
        epoch=epochs_completed,
        metrics=last_metrics,
        checkpoint_kind="LAST_DIAGNOSTIC",
        prediction_artifact=last_prediction_artifact,
        best=False,
        deployable=False,
    )
    if best_metrics is None:
        (EXPERIMENT_DIR / "checkpoints" / "best" / "NO_ELIGIBLE_CHECKPOINT.md").write_text(
            "# No eligible checkpoint\n\nNo epoch passed every frozen safety gate.\n",
            encoding="utf-8",
        )
    elif closest_manifest is not None:
        (EXPERIMENT_DIR / "checkpoints" / "closest_safety_diagnostic" / "DIAGNOSTIC_ONLY.md").write_text(
            "# Diagnostic only\n\nThis non-eligible checkpoint is not best and not deployable.\n",
            encoding="utf-8",
        )
    else:
        (EXPERIMENT_DIR / "checkpoints" / "closest_safety_diagnostic" / "NO_NON_ELIGIBLE_EPOCH.md").write_text(
            "# No non-eligible epoch\n",
            encoding="utf-8",
        )

    reporting_metrics = best_metrics if best_metrics is not None else closest_metrics
    reporting_epoch = best_epoch if best_epoch is not None else closest_epoch
    reporting_kind = "ELIGIBLE_BEST" if best_metrics is not None else "CLOSEST_SAFETY_DIAGNOSTIC"
    reporting_prediction_artifact = (
        best_prediction_artifact
        if best_metrics is not None
        else closest_prediction_artifact
    )
    if reporting_metrics is None or reporting_epoch is None or reporting_prediction_artifact is None:
        raise RuntimeError("no reporting checkpoint could be selected")
    write_jsonl(
        EXPERIMENT_DIR / "evaluation" / "validation" / "error_cases.jsonl",
        [
            {"reporting_epoch": reporting_epoch, **item}
            for item in reporting_metrics["error_cases"]
        ],
    )
    write_json(
        EXPERIMENT_DIR / "evaluation" / "validation" / "reporting_metrics.json",
        {"epoch": reporting_epoch, "checkpoint_kind": reporting_kind, **reporting_metrics},
    )

    safety = reporting_metrics["safety"]
    tracked = reporting_metrics["tracked_ambiguous_family"]
    exp001_negated_recall = 0.7083333333333334
    safety_pass = best_metrics is not None
    summary = {
        "EXPERIMENT_ID": EXPERIMENT_ID,
        "TRAINING_DEVICE": "CPU",
        "BACKBONE_LR": BACKBONE_LR,
        "HEAD_LR": HEAD_LR,
        "LOSS_WEIGHT_SCOPE": LOSS_WEIGHTS["scope"],
        "LOSS_WEIGHT_STRUCTURE": LOSS_WEIGHTS["structure"],
        "LOSS_WEIGHT_INTENT": LOSS_WEIGHTS["intent"],
        "LOSS_WEIGHT_SLOT": LOSS_WEIGHTS["slot"],
        "LOSS_WEIGHT_NEGATION": LOSS_WEIGHTS["negation"],
        "EPOCHS_COMPLETED": epochs_completed,
        "BEST_EPOCH": best_epoch,
        "REPORTING_EPOCH": reporting_epoch,
        "REPORTING_CHECKPOINT_KIND": reporting_kind,
        "REPORTING_PREDICTION_ARTIFACT": reporting_prediction_artifact,
        "TRAINING_STEPS_EXECUTED": trainer.training_steps_executed,
        "TOTAL_OPTIMIZER_STEPS_PLANNED": total_optimizer_steps,
        "WARMUP_STEPS": trainer.warmup_steps,
        "CPU_EPOCH_DURATIONS_SECONDS": epoch_durations,
        "CPU_MEAN_EPOCH_SECONDS": sum(epoch_durations) / len(epoch_durations),
        "TOTAL_TRAINING_SECONDS": total_training_seconds,
        "VALIDATION_INTENT_MACRO_F1": reporting_metrics["intent"]["macro_f1"],
        "VALIDATION_SCOPE_MACRO_F1": reporting_metrics["scope"]["macro_f1"],
        "VALIDATION_STRUCTURE_MACRO_F1": reporting_metrics["structure"]["macro_f1"],
        "VALIDATION_SLOT_SPAN_F1": reporting_metrics["slot"]["OVERALL"]["f1"],
        "VALIDATION_NEGATION_F1": reporting_metrics["negation"]["per_class"]["NEGATED"]["f1"],
        "VALIDATION_NEGATED_RECALL": reporting_metrics["negation"]["per_class"]["NEGATED"]["recall"],
        "HEADLIGHT_OFF_NEGATED_RECALL": reporting_metrics["per_intent_negation"]["HEADLIGHT_OFF"]["per_class"]["NEGATED"]["recall"],
        "ACCELERATE_NEGATED_RECALL": reporting_metrics["per_intent_negation"]["ACCELERATE"]["per_class"]["NEGATED"]["recall"],
        "NEGATION_HEAD_SLOT_DISAGREEMENT_COUNT": reporting_metrics["NEGATION_HEAD_SLOT_DISAGREEMENT_COUNT"],
        "RAW_VALIDATION_UFAR": safety["UNSAFE_FALSE_ACCEPT_RATE"],
        "AMBIGUOUS_FALSE_ACCEPT_COUNT": safety["per_category"]["AMBIGUOUS"]["unsafe_false_accepts"],
        "MULTI_FALSE_ACCEPT_COUNT": safety["per_category"]["MULTI"]["unsafe_false_accepts"],
        "UNKNOWN_FALSE_ACCEPT_COUNT": safety["per_category"]["UNKNOWN_CONTROL"]["unsafe_false_accepts"],
        "NON_CONTROL_FALSE_ACCEPT_COUNT": safety["per_category"]["NON_CONTROL"]["unsafe_false_accepts"],
        "SYS014_POC_0731": {
            "scope": tracked["SYS014-POC-0731"]["pred_scope"],
            "structure": tracked["SYS014-POC-0731"]["pred_structure"],
            "intent": tracked["SYS014-POC-0731"]["pred_intent"],
            "final_abstain": tracked["SYS014-POC-0731"]["raw_abstain"],
        },
        "SYS014_POC_0732_FINAL_ABSTAIN": tracked["SYS014-POC-0732"]["raw_abstain"],
        "SYS014_POC_0733_FINAL_ABSTAIN": tracked["SYS014-POC-0733"]["raw_abstain"],
        "ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT": reporting_metrics["ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT"],
        "BEST_CHECKPOINT_SAVED": best_manifest is not None,
        "BEST_CHECKPOINT_SHA256": (
            best_manifest["model_state_sha256"] if best_manifest is not None else None
        ),
        "CLOSEST_SAFETY_DIAGNOSTIC_EPOCH": closest_epoch,
        "CLOSEST_SAFETY_DIAGNOSTIC_SHA256": (
            closest_manifest["model_state_sha256"] if closest_manifest is not None else None
        ),
        "LAST_CHECKPOINT_SHA256": last_manifest["model_state_sha256"],
        "NON_FINITE_LOSS_DETECTED": non_finite,
        "INITIAL_BACKBONE_PARAMETER_HASHES": initial_backbone_hashes,
        "INITIAL_JOINT_HEAD_PARAMETER_HASHES": initial_joint_head_hashes,
        "FINAL_BACKBONE_PARAMETER_HASHES": representative_parameter_hashes(model.backbone),
        "TEST_EVALUATION_EXECUTED": False,
        "SAFETY_GOLD_EVALUATION_EXECUTED": False,
        "ELECTRA_TRAINING_STARTED": False,
        "RUNTIME_MODIFIED": False,
        "RBT3_EXP002_SAFETY_GATE_PASS": safety_pass,
        "RBT3_EXP002_NEGATION_IMPROVED": reporting_metrics["negation"]["per_class"]["NEGATED"]["recall"] > exp001_negated_recall,
        "READY_FOR_STAGE_4C_NEXT_DECISION": not non_finite,
        "SELECTED_VALIDATION_METRICS": reporting_metrics,
    }
    write_json(EXPERIMENT_DIR / "training_summary.json", summary)
    (EXPERIMENT_DIR / "training_summary.md").write_text(
        training_summary_markdown(summary), encoding="utf-8"
    )
    (EXPERIMENT_DIR / "exp001_vs_exp002.md").write_text(
        comparison_markdown(
            reporting_epoch,
            reporting_kind,
            reporting_metrics,
            selected_boundaries[reporting_epoch],
            summary["CPU_MEAN_EPOCH_SECONDS"],
            best_epoch,
        ),
        encoding="utf-8",
    )

    finished_at = iso_now()
    append_jsonl(
        EXPERIMENT_DIR / "training_log.jsonl",
        {"event": "TRAINING_FINISHED", "at": finished_at, "summary": {key: value for key, value in summary.items() if key != "SELECTED_VALIDATION_METRICS"}},
    )
    manifest.update(
        {
            "status": (
                "FAILED_NON_FINITE"
                if non_finite
                else "COMPLETED_SAFETY_GATE_PASS"
                if safety_pass
                else "COMPLETED_NO_ELIGIBLE_SAFETY_CHECKPOINT"
            ),
            "finished_at": finished_at,
            "training_duration_seconds": total_training_seconds,
            "rss_after_training_bytes": current_rss_bytes(),
            "epochs_completed": epochs_completed,
            "training_steps_executed": trainer.training_steps_executed,
            "best_epoch": best_epoch,
            "best_checkpoint_sha256": summary["BEST_CHECKPOINT_SHA256"],
            "closest_safety_diagnostic_epoch": closest_epoch,
            "closest_safety_diagnostic_sha256": summary["CLOSEST_SAFETY_DIAGNOSTIC_SHA256"],
            "last_checkpoint_sha256": summary["LAST_CHECKPOINT_SHA256"],
            "rbt3_exp002_safety_gate_pass": safety_pass,
            "rbt3_exp002_negation_improved": summary["RBT3_EXP002_NEGATION_IMPROVED"],
        }
    )
    write_json(EXPERIMENT_DIR / "manifest.json", manifest)
    print(
        json.dumps(
            {key: value for key, value in summary.items() if key != "SELECTED_VALIDATION_METRICS"},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Run forward-only dry validation without creating exp002.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.preflight_only:
        result = run_preflight(require_experiment_absent=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    return run_training()


if __name__ == "__main__":
    raise SystemExit(main())
