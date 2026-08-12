"""Authorized SYS-014 Stage 4C-A RBT3 exp001 formal CPU baseline."""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
import transformers
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from scripts.profile_sys014_stage4a import cpu_name, current_rss_bytes

from .collator import JointNLUCollator
from .dataset import FrozenJointNLUDataset
from .dry_run import build_distribution_report, set_deterministic_seed, tensor_class_weights
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
    primary_quality_score,
    safety_gate_passes,
    slot_span_metrics,
    unsafe_false_accept_metrics,
)
from .model import JointNLUModel, representative_parameter_hashes
from .train_config import (
    PRIMARY_MODEL_ID,
    PRIMARY_MODEL_REVISION,
    TrainingProtocol,
    primary_snapshot_path,
    repository_root,
)
from .trainer import Stage4CTrainer
from .validation import MANIFEST_PATH, full_preflight, read_split, sha256_file


EXPERIMENT_ID = "sys014-poc7-rbt3-exp001"
EXPERIMENT_DIR = repository_root() / "data" / "nlu" / "experiments" / EXPERIMENT_ID
STAGE4C_SEED = 14031
MAX_LENGTH = 32
ACTUAL_BATCH_SIZE = 16
MAX_EPOCHS = 10
EARLY_STOPPING_PATIENCE = 3
TEST_EVALUATION_EXECUTED = False
SAFETY_GOLD_EVALUATION_EXECUTED = False


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def append_jsonl(path: Path, value: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_experiment_directories() -> None:
    if EXPERIMENT_DIR.exists():
        raise FileExistsError(f"Experiment directory must not be overwritten: {EXPERIMENT_DIR}")
    EXPERIMENT_DIR.mkdir(parents=False)
    for relative in ("checkpoints/best", "checkpoints/last", "evaluation/validation"):
        (EXPERIMENT_DIR / relative).mkdir(parents=True)


def protocol() -> TrainingProtocol:
    return TrainingProtocol(
        seed=STAGE4C_SEED,
        training_enabled=True,
        selected_max_length=MAX_LENGTH,
        baseline_epochs=MAX_EPOCHS,
        early_stopping_patience=EARLY_STOPPING_PATIENCE,
        cpu_batch_size=ACTUAL_BATCH_SIZE,
    )


def model_inputs(batch: dict[str, Any], device: torch.device) -> dict[str, torch.Tensor]:
    result = {
        "input_ids": batch["input_ids"].to(device),
        "attention_mask": batch["attention_mask"].to(device),
    }
    if "token_type_ids" in batch:
        result["token_type_ids"] = batch["token_type_ids"].to(device)
    return result


def evaluate_validation(
    model: JointNLUModel,
    batches: DataLoader[Any],
    *,
    device: torch.device,
    class_weights: dict[str, torch.Tensor | None],
    training_protocol: TrainingProtocol,
) -> dict[str, Any]:
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
    sample_ids: list[str] = []
    texts: list[str] = []

    with torch.no_grad():
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
            scope_true.extend(tensors["scope_labels"].cpu().tolist())
            structure_true.extend(tensors["structure_labels"].cpu().tolist())
            intent_true.extend(tensors["intent_labels"].cpu().tolist())
            negation_true.extend(tensors["negation_labels"].cpu().tolist())
            slot_true.extend(tensors["slot_labels"].cpu().tolist())
            scope_pred.extend(outputs["scope_logits"].argmax(-1).cpu().tolist())
            structure_pred.extend(outputs["structure_logits"].argmax(-1).cpu().tolist())
            intent_pred.extend(outputs["intent_logits"].argmax(-1).cpu().tolist())
            negation_pred.extend(outputs["negation_logits"].argmax(-1).cpu().tolist())
            slot_pred.extend(outputs["slot_logits"].argmax(-1).cpu().tolist())
            sample_ids.extend(batch["sample_ids"])
            texts.extend(batch["texts"])

    intent_indices = [index for index, label in enumerate(intent_true) if label != IGNORE_INDEX]
    negation_indices = [
        index for index, label in enumerate(negation_true) if label != IGNORE_INDEX
    ]
    intent_metrics = classification_metrics(
        [intent_true[index] for index in intent_indices],
        [intent_pred[index] for index in intent_indices],
        label_names=INTENT_LABELS,
    )
    scope_metrics = classification_metrics(scope_true, scope_pred, label_names=SCOPE_LABELS)
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
    quality_score = primary_quality_score(quality_inputs)
    safety_pass = safety_gate_passes(ufar)

    per_intent_negation: dict[str, Any] = {}
    for intent_id, intent_name in enumerate(INTENT_LABELS):
        indices = [index for index in intent_indices if intent_true[index] == intent_id]
        negated_count = sum(negation_true[index] == 1 for index in indices)
        if negated_count == 0:
            per_intent_negation[intent_name] = "NOT_ESTIMABLE"
            continue
        per_intent_negation[intent_name] = classification_metrics(
            [negation_true[index] for index in indices],
            [negation_pred[index] for index in indices],
            label_names=NEGATION_LABELS,
        )

    error_cases: list[dict[str, Any]] = []
    for index, sample_id in enumerate(sample_ids):
        sentence_error = (
            scope_true[index] != scope_pred[index]
            or structure_true[index] != structure_pred[index]
            or (intent_true[index] != IGNORE_INDEX and intent_true[index] != intent_pred[index])
            or (
                negation_true[index] != IGNORE_INDEX
                and negation_true[index] != negation_pred[index]
            )
        )
        masked_slot_prediction = [
            IGNORE_INDEX if truth == IGNORE_INDEX else prediction
            for truth, prediction in zip(slot_true[index], slot_pred[index], strict=True)
        ]
        slot_error = slot_true[index] != masked_slot_prediction
        if sentence_error or slot_error:
            error_cases.append(
                {
                    "sample_id": sample_id,
                    "text": texts[index],
                    "true": {
                        "scope": scope_true[index],
                        "structure": structure_true[index],
                        "intent": intent_true[index],
                        "negation": negation_true[index],
                        "slot": slot_true[index],
                    },
                    "predicted": {
                        "scope": scope_pred[index],
                        "structure": structure_pred[index],
                        "intent": intent_pred[index],
                        "negation": negation_pred[index],
                        "slot": masked_slot_prediction,
                    },
                }
            )

    return {
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
        "PRIMARY_QUALITY_SCORE": quality_score,
        "SAFETY_GATES_PASS": safety_pass,
        "confusion_matrices": {
            "intent": intent_metrics["confusion_matrix"],
            "scope": scope_metrics["confusion_matrix"],
            "structure": structure_metrics["confusion_matrix"],
            "negation": negation_metrics["confusion_matrix"],
        },
        "error_cases": error_cases,
    }


def save_checkpoint(
    directory: Path,
    model: JointNLUModel,
    training_protocol: TrainingProtocol,
    *,
    epoch: int,
    validation_metrics: dict[str, Any],
) -> dict[str, Any]:
    model_state_path = directory / "model_state.pt"
    torch.save(model.state_dict(), model_state_path)
    write_json(
        directory / "label_mapping.json",
        label_mapping_report(),
    )
    write_json(
        directory / "model_config.json",
        {
            "backbone_config": model.backbone.config.to_dict(),
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
    write_json(directory / "training_config.json", training_protocol.to_dict())
    checkpoint_sha256 = sha256_file(model_state_path)
    checkpoint_manifest = {
        "checkpoint_format": "PYTORCH_STATE_DICT",
        "epoch": epoch,
        "model_id": PRIMARY_MODEL_ID,
        "model_revision": PRIMARY_MODEL_REVISION,
        "dataset_version": training_protocol.dataset_version,
        "dataset_manifest_sha256": sha256_file(MANIFEST_PATH),
        "registry_version": training_protocol.registry_version,
        "label_mapping_file": "label_mapping.json",
        "model_config_file": "model_config.json",
        "training_config_file": "training_config.json",
        "model_state_file": "model_state.pt",
        "model_state_sha256": checkpoint_sha256,
        "validation_primary_quality_score": validation_metrics["PRIMARY_QUALITY_SCORE"],
        "validation_safety_gates_pass": validation_metrics["SAFETY_GATES_PASS"],
    }
    write_json(directory / "checkpoint_manifest.json", checkpoint_manifest)
    return checkpoint_manifest


def save_validation_evaluation(metrics: dict[str, Any]) -> None:
    evaluation_dir = EXPERIMENT_DIR / "evaluation" / "validation"
    output_metrics = {key: value for key, value in metrics.items() if key not in {"error_cases", "confusion_matrices"}}
    write_json(evaluation_dir / "metrics.json", output_metrics)
    write_json(evaluation_dir / "confusion_matrix.json", metrics["confusion_matrices"])
    error_path = evaluation_dir / "error_cases.jsonl"
    error_path.write_text("", encoding="utf-8")
    for error in metrics["error_cases"]:
        append_jsonl(error_path, error)


def training_pass(best: dict[str, Any] | None, summary: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if best is None:
        failures.append("NO_VALIDATION_CHECKPOINT_PASSED_SAFETY_GATES")
        return False, failures
    if summary["TRAIN_LOSS_FINAL"] >= summary["TRAIN_LOSS_INITIAL"]:
        failures.append("TRAIN_TOTAL_LOSS_DID_NOT_DECREASE")
    if best["intent"]["macro_f1"] <= 0.30:
        failures.append("INTENT_MACRO_F1_NOT_CLEARLY_ABOVE_RANDOM")
    if best["scope"]["per_class"]["UNKNOWN_CONTROL"]["recall"] <= 0:
        failures.append("UNKNOWN_CONTROL_NOT_LEARNED")
    if best["structure"]["per_class"]["MULTI"]["recall"] <= 0:
        failures.append("MULTI_NOT_LEARNED")
    if best["structure"]["per_class"]["AMBIGUOUS"]["recall"] <= 0:
        failures.append("AMBIGUOUS_NOT_LEARNED")
    if best["slot"]["OVERALL"]["f1"] <= 0:
        failures.append("SLOT_SPANS_NOT_LEARNED")
    if best["negation"]["per_class"]["NEGATED"]["f1"] <= 0:
        failures.append("NEGATION_NOT_LEARNED")
    if not summary["PRETRAINED_WEIGHTS_CHANGED"]:
        failures.append("BACKBONE_WEIGHTS_UNCHANGED")
    if summary["TRAINING_STEPS_EXECUTED"] <= 0:
        failures.append("NO_TRAINING_STEPS")
    if summary["NON_FINITE_LOSS_DETECTED"]:
        failures.append("NON_FINITE_LOSS")
    return not failures, failures


def summary_markdown(summary: dict[str, Any], best: dict[str, Any] | None) -> str:
    if best is None:
        metrics_section = "没有 validation checkpoint 通过冻结 safety gates。"
    else:
        metrics_section = f"""- Intent accuracy/macro F1：{best['intent']['accuracy']:.4f} / {best['intent']['macro_f1']:.4f}
- Scope macro F1 / UNKNOWN recall：{best['scope']['macro_f1']:.4f} / {best['scope']['per_class']['UNKNOWN_CONTROL']['recall']:.4f}
- Structure macro F1 / MULTI recall / AMBIGUOUS recall：{best['structure']['macro_f1']:.4f} / {best['structure']['per_class']['MULTI']['recall']:.4f} / {best['structure']['per_class']['AMBIGUOUS']['recall']:.4f}
- Slot overall/AREA/VALUE/NEGATION F1：{best['slot']['OVERALL']['f1']:.4f} / {best['slot']['AREA']['f1']:.4f} / {best['slot']['VALUE']['f1']:.4f} / {best['slot']['NEGATION']['f1']:.4f}
- Negation F1 / NEGATED recall：{best['negation']['per_class']['NEGATED']['f1']:.4f} / {best['negation']['per_class']['NEGATED']['recall']:.4f}
- RAW validation UFAR：{best['safety']['UNSAFE_FALSE_ACCEPT_RATE']:.4f}
"""
    return f"""# SYS-014 RBT3 exp001 训练总结

## 配置与耗时

- device：CPU；batch={summary['ACTUAL_BATCH_SIZE']}；lr={summary['LEARNING_RATE']}；seed={STAGE4C_SEED}。
- epochs：{summary['EPOCHS_COMPLETED']}/{summary['MAX_EPOCHS']}；best epoch={summary['BEST_EPOCH']}。
- optimizer steps：{summary['TRAINING_STEPS_EXECUTED']}；warmup steps={summary['WARMUP_STEPS']}；计划总 steps={summary['TOTAL_OPTIMIZER_STEPS']}。
- mean epoch seconds：{summary['MEAN_EPOCH_SECONDS']:.3f}；total training seconds：{summary['TOTAL_TRAINING_SECONDS']:.3f}。

## Best validation

{metrics_section}
## 健康与边界

- `NON_FINITE_LOSS_DETECTED = {'YES' if summary['NON_FINITE_LOSS_DETECTED'] else 'NO'}`
- `OVERFIT_WARNING = {'YES' if summary['OVERFIT_WARNING'] else 'NO'}`
- `PRETRAINED_WEIGHTS_CHANGED = {'YES' if summary['PRETRAINED_WEIGHTS_CHANGED'] else 'NO'}`
- `BEST_CHECKPOINT_SAVED = {'YES' if summary['BEST_CHECKPOINT_SAVED'] else 'NO'}`
- `TEST_EVALUATION_EXECUTED = NO`
- `SAFETY_GOLD_EVALUATION_EXECUTED = NO`
- `RBT3_BASELINE_TRAINING_PASS = {'YES' if summary['RBT3_BASELINE_TRAINING_PASS'] else 'NO'}`
- `READY_FOR_STAGE_4C_NEXT_DECISION = {'YES' if summary['READY_FOR_STAGE_4C_NEXT_DECISION'] else 'NO'}`

训练失败诊断：{summary['TRAINING_FAILURE_DIAGNOSIS'] or 'NONE'}。
"""


def run_preflight_only() -> int:
    result = full_preflight()
    tokenizer = AutoTokenizer.from_pretrained(
        primary_snapshot_path(), local_files_only=True, use_fast=True
    )
    distribution, failures = build_distribution_report(
        tokenizer, selected_max_length=MAX_LENGTH
    )
    train_dataset = FrozenJointNLUDataset("train", tokenizer, max_length=MAX_LENGTH)
    validation_dataset = FrozenJointNLUDataset("validation", tokenizer, max_length=MAX_LENGTH)
    model = JointNLUModel(str(primary_snapshot_path())).eval()
    batch = JointNLUCollator(tokenizer)([train_dataset[index] for index in range(ACTUAL_BATCH_SIZE)])
    with torch.inference_mode():
        outputs = model(**model_inputs(batch, torch.device("cpu")))
    print(
        json.dumps(
            {
                "PREFLIGHT": "PASS",
                "dataset_hash_verified": result["hash_verification"]["DATASET_HASH_VERIFIED"],
                "projection_failures": len(failures),
                "train_count": len(train_dataset),
                "validation_count": len(validation_dataset),
                "max_token_length": distribution["MAX_TOKEN_LENGTH"],
                "forward_shapes": {name: list(value.shape) for name, value in outputs.items()},
                "experiment_absent": not EXPERIMENT_DIR.exists(),
                "test_model_evaluation_executed": False,
                "safety_gold_model_evaluation_executed": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def run_training() -> int:
    if EXPERIMENT_DIR.exists():
        raise FileExistsError(f"Refusing to overwrite {EXPERIMENT_DIR}")
    training_protocol = protocol()
    set_deterministic_seed(STAGE4C_SEED)
    preflight = full_preflight()
    tokenizer = AutoTokenizer.from_pretrained(
        primary_snapshot_path(), local_files_only=True, use_fast=True
    )
    distribution, projection_failures = build_distribution_report(
        tokenizer, selected_max_length=MAX_LENGTH
    )
    if projection_failures:
        raise RuntimeError(f"TOKEN_PROJECTION_FAILURES={len(projection_failures)}")
    train_dataset = FrozenJointNLUDataset("train", tokenizer, max_length=MAX_LENGTH)
    validation_dataset = FrozenJointNLUDataset("validation", tokenizer, max_length=MAX_LENGTH)
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
    pretrained_hashes_before = representative_parameter_hashes(model.backbone)
    total_optimizer_steps = len(train_loader) * MAX_EPOCHS
    trainer = Stage4CTrainer(
        model,
        training_protocol,
        device=device,
        total_optimizer_steps=total_optimizer_steps,
    )
    class_weights = tensor_class_weights(distribution, training_protocol, device)
    started_at = iso_now()
    rss_before_training = current_rss_bytes()
    create_experiment_directories()
    experiment_config = {
        **training_protocol.to_dict(),
        "experiment_id": EXPERIMENT_ID,
        "actual_batch_size": ACTUAL_BATCH_SIZE,
        "training_device": "CPU",
        "total_optimizer_steps": total_optimizer_steps,
        "warmup_steps": trainer.warmup_steps,
        "seed_controls": ["python_random", "numpy", "torch"],
        "test_used_for_model_selection": False,
        "safety_gold_used_for_model_selection": False,
    }
    write_json(EXPERIMENT_DIR / "experiment_config.json", experiment_config)
    (EXPERIMENT_DIR / "training_log.jsonl").write_text("", encoding="utf-8")
    (EXPERIMENT_DIR / "metrics_by_epoch.jsonl").write_text("", encoding="utf-8")
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "status": "RUNNING",
        "dataset_version": training_protocol.dataset_version,
        "dataset_manifest_sha256": sha256_file(MANIFEST_PATH),
        "registry_version": training_protocol.registry_version,
        "model_id": PRIMARY_MODEL_ID,
        "model_revision": PRIMARY_MODEL_REVISION,
        "seed": STAGE4C_SEED,
        "device": "CPU",
        "cpu_model": cpu_name(),
        "torch_threads": torch.get_num_threads(),
        "torch_interop_threads": torch.get_num_interop_threads(),
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "python_executable": os.path.realpath(os.sys.executable),
        "git_commit": current_git_commit(),
        "started_at": started_at,
        "finished_at": None,
        "training_duration_seconds": None,
        "rss_before_training_bytes": rss_before_training,
        "rss_after_training_bytes": None,
        "test_evaluation_executed": TEST_EVALUATION_EXECUTED,
        "safety_gold_evaluation_executed": SAFETY_GOLD_EVALUATION_EXECUTED,
        "preflight": preflight,
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
    best_checkpoint_manifest: dict[str, Any] | None = None
    stale_epochs = 0
    non_finite = False

    try:
        for epoch in range(1, MAX_EPOCHS + 1):
            epoch_started = time.perf_counter()
            epoch_parameter_before = representative_parameter_hashes(model.backbone, sample_count=3)
            train_started = time.perf_counter()
            train_result = trainer.train_epoch(train_loader, class_weights=class_weights)
            train_seconds = time.perf_counter() - train_started
            epoch_parameter_after = representative_parameter_hashes(model.backbone, sample_count=3)
            validation_started = time.perf_counter()
            validation = evaluate_validation(
                model,
                validation_loader,
                device=device,
                class_weights=class_weights,
                training_protocol=training_protocol,
            )
            validation_seconds = time.perf_counter() - validation_started
            epoch_seconds = time.perf_counter() - epoch_started
            epoch_durations.append(epoch_seconds)
            parameter_updated = epoch_parameter_before != epoch_parameter_after
            record = {
                "epoch": epoch,
                "train": train_result,
                "validation": validation,
                "train_seconds": train_seconds,
                "validation_seconds": validation_seconds,
                "epoch_seconds": epoch_seconds,
                "parameter_update_detected": parameter_updated,
                "rss_bytes": current_rss_bytes(),
            }
            history.append(record)
            append_jsonl(
                EXPERIMENT_DIR / "training_log.jsonl",
                {
                    "event": "EPOCH_COMPLETED",
                    "epoch": epoch,
                    "train_losses": train_result["mean_losses"],
                    "validation_losses": validation["losses"],
                    "gradient_norm_mean": train_result["gradient_norm_mean"],
                    "gradient_norm_max": train_result["gradient_norm_max"],
                    "learning_rate_start": train_result["learning_rate_start"],
                    "learning_rate_end": train_result["learning_rate_end"],
                    "parameter_update_detected": parameter_updated,
                    "epoch_seconds": epoch_seconds,
                },
            )
            append_jsonl(EXPERIMENT_DIR / "metrics_by_epoch.jsonl", record)
            score = float(validation["PRIMARY_QUALITY_SCORE"])
            safety_pass = bool(validation["SAFETY_GATES_PASS"])
            improved = safety_pass and score > best_score
            if improved:
                best_score = score
                best_epoch = epoch
                best_metrics = validation
                stale_epochs = 0
                best_checkpoint_manifest = save_checkpoint(
                    EXPERIMENT_DIR / "checkpoints" / "best",
                    model,
                    training_protocol,
                    epoch=epoch,
                    validation_metrics=validation,
                )
                write_json(EXPERIMENT_DIR / "best_validation_metrics.json", validation)
                save_validation_evaluation(validation)
            elif best_metrics is not None:
                stale_epochs += 1
            print(
                json.dumps(
                    {
                        "epoch": epoch,
                        "train_total_loss": train_result["mean_losses"]["total_loss"],
                        "validation_total_loss": validation["losses"]["total_loss"],
                        "quality_score": score,
                        "safety_gates_pass": safety_pass,
                        "raw_validation_ufar": validation["safety"]["UNSAFE_FALSE_ACCEPT_RATE"],
                        "intent_macro_f1": validation["intent"]["macro_f1"],
                        "scope_macro_f1": validation["scope"]["macro_f1"],
                        "structure_macro_f1": validation["structure"]["macro_f1"],
                        "slot_span_f1": validation["slot"]["OVERALL"]["f1"],
                        "negated_f1": validation["negation"]["per_class"]["NEGATED"]["f1"],
                        "epoch_seconds": epoch_seconds,
                        "training_steps_executed": trainer.training_steps_executed,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            if epoch >= 2 and best_metrics is not None and stale_epochs >= EARLY_STOPPING_PATIENCE:
                append_jsonl(
                    EXPERIMENT_DIR / "training_log.jsonl",
                    {"event": "EARLY_STOPPING", "epoch": epoch, "stale_epochs": stale_epochs},
                )
                break
    except FloatingPointError as exc:
        non_finite = True
        append_jsonl(
            EXPERIMENT_DIR / "training_log.jsonl",
            {"event": "TRAINING_ABORTED_NON_FINITE", "error": str(exc), "at": iso_now()},
        )

    total_training_seconds = time.perf_counter() - training_started
    epochs_completed = len(history)
    final_metrics = history[-1]["validation"] if history else None
    if final_metrics is not None:
        save_checkpoint(
            EXPERIMENT_DIR / "checkpoints" / "last",
            model,
            training_protocol,
            epoch=epochs_completed,
            validation_metrics=final_metrics,
        )
    pretrained_hashes_after = representative_parameter_hashes(model.backbone)
    pretrained_changed = pretrained_hashes_before != pretrained_hashes_after
    overfit_warning = False
    if len(history) >= 3:
        train_losses = [item["train"]["mean_losses"]["total_loss"] for item in history]
        validation_losses = [item["validation"]["losses"]["total_loss"] for item in history]
        overfit_warning = (
            train_losses[-1] < train_losses[-2] < train_losses[-3]
            and validation_losses[-1] > validation_losses[-2] > validation_losses[-3]
            and validation_losses[-1] > min(validation_losses) * 1.10
        )
    summary = {
        "TRAINING_DEVICE": "CPU",
        "ACTUAL_BATCH_SIZE": ACTUAL_BATCH_SIZE,
        "LEARNING_RATE": training_protocol.baseline_learning_rate,
        "MAX_EPOCHS": MAX_EPOCHS,
        "EPOCHS_COMPLETED": epochs_completed,
        "BEST_EPOCH": best_epoch,
        "TRAINING_STEPS_EXECUTED": trainer.training_steps_executed,
        "TOTAL_OPTIMIZER_STEPS": total_optimizer_steps,
        "WARMUP_STEPS": trainer.warmup_steps,
        "CPU_EPOCH_TIME_MEASURED": bool(epoch_durations),
        "EPOCH_DURATIONS_SECONDS": epoch_durations,
        "MEAN_EPOCH_SECONDS": sum(epoch_durations) / max(len(epoch_durations), 1),
        "TOTAL_TRAINING_SECONDS": total_training_seconds,
        "TRAIN_LOSS_INITIAL": history[0]["train"]["mean_losses"]["total_loss"] if history else None,
        "TRAIN_LOSS_FINAL": history[-1]["train"]["mean_losses"]["total_loss"] if history else None,
        "VALIDATION_LOSS_BEST": best_metrics["losses"]["total_loss"] if best_metrics else None,
        "NON_FINITE_LOSS_DETECTED": non_finite,
        "OVERFIT_WARNING": overfit_warning,
        "PRETRAINED_WEIGHTS_CHANGED": pretrained_changed,
        "BEST_CHECKPOINT_SAVED": best_checkpoint_manifest is not None,
        "CHECKPOINT_SHA256": (
            best_checkpoint_manifest["model_state_sha256"] if best_checkpoint_manifest else None
        ),
        "TEST_USED_FOR_MODEL_SELECTION": False,
        "SAFETY_GOLD_USED_FOR_MODEL_SELECTION": False,
        "TEST_EVALUATION_EXECUTED": TEST_EVALUATION_EXECUTED,
        "SAFETY_GOLD_EVALUATION_EXECUTED": SAFETY_GOLD_EVALUATION_EXECUTED,
    }
    passed, diagnosis = training_pass(best_metrics, summary)
    summary["RBT3_BASELINE_TRAINING_PASS"] = passed
    summary["READY_FOR_STAGE_4C_NEXT_DECISION"] = passed
    summary["TRAINING_FAILURE_DIAGNOSIS"] = diagnosis
    write_json(EXPERIMENT_DIR / "training_summary.json", summary)
    (EXPERIMENT_DIR / "training_summary.md").write_text(
        summary_markdown(summary, best_metrics), encoding="utf-8"
    )
    finished_at = iso_now()
    append_jsonl(
        EXPERIMENT_DIR / "training_log.jsonl",
        {"event": "TRAINING_FINISHED", "at": finished_at, "summary": summary},
    )
    manifest.update(
        {
            "status": "COMPLETED" if not non_finite else "FAILED_NON_FINITE",
            "finished_at": finished_at,
            "training_duration_seconds": total_training_seconds,
            "rss_after_training_bytes": current_rss_bytes(),
            "epochs_completed": epochs_completed,
            "training_steps_executed": trainer.training_steps_executed,
            "best_epoch": best_epoch,
            "best_checkpoint_sha256": summary["CHECKPOINT_SHA256"],
            "rbt3_baseline_training_pass": passed,
        }
    )
    write_json(EXPERIMENT_DIR / "manifest.json", manifest)
    print(json.dumps({"experiment": EXPERIMENT_ID, **summary}, ensure_ascii=False, indent=2))
    return 0 if passed else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    return run_preflight_only() if args.preflight_only else run_training()


if __name__ == "__main__":
    raise SystemExit(main())
