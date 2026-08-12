"""SYS-014 Stage 4C-B.2: isolated ELECTRA Slot-weighting ablation."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import torch
import torch.nn.functional as functional
import transformers
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from scripts.profile_sys014_stage4a import cpu_name, current_rss_bytes

from .collator import JointNLUCollator
from .dataset import FrozenJointNLUDataset
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
from .losses import class_weights_from_counts, compute_masked_multitask_loss
from .manifest import current_git_commit
from .model import JointNLUModel, representative_parameter_hashes
from .stage4c_electra_exp001 import (
    BATCH_SIZE,
    LEARNING_RATE,
    LOSS_WEIGHTS,
    MAX_EPOCHS,
    MAX_LENGTH,
    MODEL_ID,
    MODEL_REVISION,
    MODEL_SNAPSHOT,
    PATIENCE,
    SEED,
    candidate_provenance,
    data_context,
    model_inputs,
    model_state_digest,
    tracked_abstention,
)
from .stage4c_exp002 import (
    closest_key,
    evaluate_validation,
    failed_safety_gate_count,
)
from .train_config import TrainingProtocol, repository_root
from .trainer import Stage4CTrainer
from .validation import MANIFEST_PATH, read_split, sha256_file


EXPERIMENT_ID = "sys014-poc7-electra-exp002"
EXPERIMENT_DIR = repository_root() / "data" / "nlu" / "experiments" / EXPERIMENT_ID
EXP001_DIR = repository_root() / "data" / "nlu" / "experiments" / "sys014-poc7-electra-exp001"
B1_DIAGNOSIS_PATH = EXP001_DIR / "diagnostics" / "stage4c_b1" / "stage4c_b1_diagnosis.json"
SLOT_WEIGHT_POLICY = "SQRT_INVERSE_FREQ_CAP_3"
BASELINE_SLOT_F1 = 0.24675324675324675
BASELINE_VALUE_F1 = 0.0
DEGRADATION_LIMITS = {
    "intent_macro_f1": 0.03,
    "scope_macro_f1": 0.03,
    "structure_macro_f1": 0.02,
    "negation_f1": 0.03,
    "in_scope_control_recall": 0.03,
}


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, value: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, values: Iterable[Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def protocol() -> TrainingProtocol:
    policies = {
        "scope": "SQRT_INVERSE_FREQ",
        "structure": "SQRT_INVERSE_FREQ",
        "intent": "NONE",
        "slot": "SQRT_INVERSE_FREQ",
        "negation": "SQRT_INVERSE_FREQ",
    }
    return TrainingProtocol(
        model_id=MODEL_ID,
        model_revision=MODEL_REVISION,
        seed=SEED,
        training_enabled=True,
        selected_max_length=MAX_LENGTH,
        cpu_batch_size=BATCH_SIZE,
        cuda_batch_size=BATCH_SIZE,
        baseline_epochs=MAX_EPOCHS,
        early_stopping_patience=PATIENCE,
        baseline_learning_rate=LEARNING_RATE,
        loss_weights=dict(LOSS_WEIGHTS),
        class_weight_policy=policies,
    )


def load_frozen_slot_weights() -> tuple[dict[str, float], dict[str, Any]]:
    diagnosis = read_json(B1_DIAGNOSIS_PATH)
    if diagnosis["RECOMMENDED_SLOT_WEIGHT_POLICY"] != SLOT_WEIGHT_POLICY:
        raise RuntimeError("B1_SLOT_WEIGHT_POLICY_MISMATCH")
    source = diagnosis["slot_class_weight_simulation"]
    vector = source["B_SQRT_INVERSE_FREQ_CAP_3"]
    if list(vector) != list(SLOT_LABELS):
        raise RuntimeError("SLOT_WEIGHT_LABEL_ORDER_MISMATCH")
    if not all(0.0 < float(vector[label]) <= 3.0 for label in SLOT_LABELS):
        raise RuntimeError("SLOT_WEIGHT_OUT_OF_RANGE")
    return {label: float(vector[label]) for label in SLOT_LABELS}, {
        "source_file": str(B1_DIAGNOSIS_PATH),
        "source_sha256": sha256_file(B1_DIAGNOSIS_PATH),
        "policy": SLOT_WEIGHT_POLICY,
    }


def exp2_class_weights(
    distribution: dict[str, Any],
    training_protocol: TrainingProtocol,
    device: torch.device,
    frozen_vector: dict[str, float],
) -> dict[str, torch.Tensor | None]:
    result = tensor_class_weights(distribution, training_protocol, device)
    result["slot"] = torch.tensor(
        [frozen_vector[label] for label in SLOT_LABELS],
        dtype=torch.float32,
        device=device,
    )
    return result


def normalized_core_config(
    exp001_config: dict[str, Any],
    *,
    slot_policy: str,
    slot_vector: dict[str, float] | None,
) -> dict[str, Any]:
    return {
        "model_id": exp001_config["model_id"],
        "model_revision": exp001_config["model_revision"],
        "dataset_version": exp001_config["dataset_version"],
        "registry_version": exp001_config["registry_version"],
        "seed": exp001_config["seed"],
        "selected_max_length": exp001_config["selected_max_length"],
        "actual_batch_size": exp001_config["actual_batch_size"],
        "optimizer_name": exp001_config["optimizer_name"],
        "optimizer_parameter_group_count": 1,
        "baseline_learning_rate": exp001_config["baseline_learning_rate"],
        "weight_decay": exp001_config["weight_decay"],
        "warmup_ratio": exp001_config["warmup_ratio"],
        "gradient_clip_norm": exp001_config["gradient_clip_norm"],
        "baseline_epochs": exp001_config["baseline_epochs"],
        "early_stopping_patience": exp001_config["early_stopping_patience"],
        "loss_weights": exp001_config["loss_weights"],
        "scope_class_weight_policy": exp001_config["class_weight_policy"]["scope"],
        "structure_class_weight_policy": exp001_config["class_weight_policy"]["structure"],
        "intent_class_weight_policy": exp001_config["class_weight_policy"]["intent"],
        "slot_class_weight_policy": slot_policy,
        "slot_class_weight_vector": slot_vector,
        "negation_class_weight_policy": exp001_config["class_weight_policy"]["negation"],
        "class_weight_cap": exp001_config["class_weight_cap"],
        "quality_score_weights": exp001_config["quality_score_weights"],
        "safety_gates": exp001_config["safety_gates"],
        "label_mapping": label_mapping_report(),
    }


def config_diff(slot_vector: dict[str, float]) -> dict[str, Any]:
    exp001_config = read_json(EXP001_DIR / "experiment_config.json")
    exp001 = normalized_core_config(
        exp001_config,
        slot_policy="NONE",
        slot_vector=None,
    )
    exp002 = normalized_core_config(
        exp001_config,
        slot_policy=SLOT_WEIGHT_POLICY,
        slot_vector=slot_vector,
    )
    differences = [
        {"field": key, "exp001": exp001[key], "exp002": exp002[key]}
        for key in exp001
        if exp001[key] != exp002[key]
    ]
    allowed = {"slot_class_weight_policy", "slot_class_weight_vector"}
    unexpected = [item for item in differences if item["field"] not in allowed]
    return {
        "exp001": exp001,
        "exp002": exp002,
        "differences": differences,
        "allowed_difference_fields": sorted(allowed),
        "unexpected_differences": unexpected,
        "ISOLATED_VARIABLE_CHECK_PASS": not unexpected
        and {item["field"] for item in differences} == allowed,
    }


def slot_weight_wiring_test(slot_weights: torch.Tensor) -> dict[str, Any]:
    slot_logits = torch.tensor(
        [
            [
                [3.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [1.5, 0.2, 0.1, -0.5, 0.0, 0.0, 0.0],
                [1.0, 0.1, 0.2, 0.0, -0.2, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        ],
        dtype=torch.float32,
    )
    slot_labels = torch.tensor([[0, 3, 4, IGNORE_INDEX]], dtype=torch.long)
    outputs = {
        "scope_logits": torch.zeros((1, len(SCOPE_LABELS))),
        "structure_logits": torch.zeros((1, len(STRUCTURE_LABELS))),
        "intent_logits": torch.zeros((1, len(INTENT_LABELS))),
        "slot_logits": slot_logits,
        "negation_logits": torch.zeros((1, len(NEGATION_LABELS))),
    }
    batch = {
        "scope_labels": torch.tensor([0]),
        "structure_labels": torch.tensor([0]),
        "intent_labels": torch.tensor([0]),
        "slot_labels": slot_labels,
        "negation_labels": torch.tensor([0]),
    }
    losses = compute_masked_multitask_loss(
        outputs,
        batch,
        loss_weights=dict(LOSS_WEIGHTS),
        class_weights={"slot": slot_weights},
    )
    flat_logits = slot_logits.reshape(-1, len(SLOT_LABELS))
    flat_labels = slot_labels.reshape(-1)
    expected_weighted = functional.cross_entropy(
        flat_logits,
        flat_labels,
        weight=slot_weights,
        ignore_index=IGNORE_INDEX,
    )
    unweighted = functional.cross_entropy(
        flat_logits,
        flat_labels,
        ignore_index=IGNORE_INDEX,
    )
    per_token_weighted = functional.cross_entropy(
        flat_logits,
        flat_labels,
        weight=slot_weights,
        ignore_index=IGNORE_INDEX,
        reduction="none",
    )
    wired = bool(
        torch.allclose(losses["slot_loss"], expected_weighted, atol=1e-7)
        and not torch.allclose(losses["slot_loss"], unweighted, atol=1e-5)
    )
    return {
        "SLOT_WEIGHT_WIRED_TO_LOSS": wired,
        "actual_multitask_slot_loss": float(losses["slot_loss"]),
        "expected_weighted_cross_entropy": float(expected_weighted),
        "unweighted_cross_entropy": float(unweighted),
        "per_token_weighted_loss_contributions": {
            "O": float(per_token_weighted[0]),
            "B_VALUE": float(per_token_weighted[1]),
            "I_VALUE": float(per_token_weighted[2]),
        },
        "slot_weight_tensor": slot_weights.tolist(),
    }


def create_experiment_directories() -> None:
    if EXPERIMENT_DIR.exists():
        raise FileExistsError(f"Refusing to overwrite {EXPERIMENT_DIR}")
    EXPERIMENT_DIR.mkdir(parents=False)
    for relative in (
        "checkpoints/best",
        "checkpoints/closest_safety_diagnostic",
        "checkpoints/closest_exp002_diagnostic",
        "checkpoints/last",
        "evaluation/validation",
    ):
        (EXPERIMENT_DIR / relative).mkdir(parents=True)


def run_preflight(*, require_experiment_absent: bool = True) -> dict[str, Any]:
    if require_experiment_absent and EXPERIMENT_DIR.exists():
        raise FileExistsError(f"Preflight refuses existing experiment: {EXPERIMENT_DIR}")
    provenance = candidate_provenance()
    frozen_vector, weight_source = load_frozen_slot_weights()
    diff = config_diff(frozen_vector)
    if not diff["ISOLATED_VARIABLE_CHECK_PASS"]:
        raise RuntimeError(f"ISOLATED_VARIABLE_CHECK_FAIL: {diff}")
    training_protocol = protocol()
    set_deterministic_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_SNAPSHOT, local_files_only=True, use_fast=True)
    distribution, failures, _, validation_records, hash_report = data_context(tokenizer)
    if failures:
        raise RuntimeError(f"TOKEN_PROJECTION_FAILURES={len(failures)}")
    recomputed = class_weights_from_counts(
        distribution["train"]["slot_token_labels"],
        SLOT_LABELS,
        policy="SQRT_INVERSE_FREQ",
        cap=3.0,
    )
    recomputed_map = dict(zip(SLOT_LABELS, recomputed, strict=True))
    if any(abs(recomputed_map[label] - frozen_vector[label]) > 1e-8 for label in SLOT_LABELS):
        raise RuntimeError("B1_SLOT_WEIGHT_VECTOR_RECOMPUTE_MISMATCH")
    train_dataset = FrozenJointNLUDataset("train", tokenizer, max_length=MAX_LENGTH)
    validation_dataset = FrozenJointNLUDataset("validation", tokenizer, max_length=MAX_LENGTH)
    edge = BATCH_SIZE // 2
    indices = list(range(edge)) + list(range(len(validation_dataset) - edge, len(validation_dataset)))
    batch = JointNLUCollator(tokenizer)([validation_dataset[index] for index in indices])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = JointNLUModel(str(MODEL_SNAPSHOT)).to(device)
    initial_digest = model_state_digest(model)
    initial_backbone = representative_parameter_hashes(model.backbone)
    initial_heads = {
        name: representative_parameter_hashes(getattr(model, name))
        for name in ("scope_head", "structure_head", "intent_head", "slot_head", "negation_head")
    }
    exp001_preflight = read_json(EXP001_DIR / "preflight.json")
    if initial_backbone != exp001_preflight["initial_backbone_parameter_hashes"]:
        raise RuntimeError("FRESH_BACKBONE_HASH_MISMATCH_WITH_EXP001_INITIALIZATION")
    if initial_heads != exp001_preflight["initial_joint_head_parameter_hashes"]:
        raise RuntimeError("FRESH_HEAD_HASH_MISMATCH_WITH_SAME_SEED_EXP001_INITIALIZATION")
    exp001_best_state = torch.load(
        EXP001_DIR / "checkpoints" / "best" / "model_state.pt",
        map_location="cpu",
        weights_only=True,
    )
    fresh_is_not_exp001_checkpoint = not torch.equal(
        model.state_dict()["backbone.embeddings.word_embeddings.weight"].cpu(),
        exp001_best_state["backbone.embeddings.word_embeddings.weight"],
    )
    if not fresh_is_not_exp001_checkpoint:
        raise RuntimeError("EXP002_INITIALIZED_FROM_EXP001_CHECKPOINT")
    total_steps = math.ceil(len(train_dataset) / BATCH_SIZE) * MAX_EPOCHS
    trainer = Stage4CTrainer(model, training_protocol, device=device, total_optimizer_steps=total_steps)
    if trainer.discriminative_learning_rates or len(trainer.optimizer.param_groups) != 1:
        raise RuntimeError("EXP002_REQUIRES_SINGLE_OPTIMIZER_GROUP")
    optimizer_ids = {id(parameter) for group in trainer.optimizer.param_groups for parameter in group["params"]}
    trainable_ids = {id(parameter) for parameter in model.parameters() if parameter.requires_grad}
    if optimizer_ids != trainable_ids:
        raise RuntimeError("OPTIMIZER_GROUP_COVERAGE_FAILURE")
    class_weights = exp2_class_weights(
        distribution,
        training_protocol,
        device,
        frozen_vector,
    )
    wiring = slot_weight_wiring_test(class_weights["slot"].cpu())
    if not wiring["SLOT_WEIGHT_WIRED_TO_LOSS"]:
        raise RuntimeError("SLOT_WEIGHT_NOT_WIRED_TO_LOSS")
    model.eval()
    with torch.inference_mode():
        outputs = model(**model_inputs(batch, device))
        tensors = {
            key: value.to(device) if isinstance(value, torch.Tensor) else value
            for key, value in batch.items()
        }
        losses = compute_masked_multitask_loss(
            outputs,
            tensors,
            loss_weights=training_protocol.loss_weights,
            class_weights=class_weights,
        )
    after_digest = model_state_digest(model)
    if initial_digest != after_digest or any(parameter.grad is not None for parameter in model.parameters()):
        raise RuntimeError("PREFLIGHT_MUTATED_MODEL_OR_CREATED_GRADIENTS")
    if trainer.training_steps_executed != 0:
        raise RuntimeError("PREFLIGHT_EXECUTED_TRAINING_STEP")
    if not math.isfinite(float(losses["total_loss"])):
        raise FloatingPointError("NON_FINITE_PREFLIGHT_LOSS")
    return {
        "PREFLIGHT": "PASS",
        "experiment_absent": not EXPERIMENT_DIR.exists(),
        "model_provenance": provenance,
        "dataset_hash_verification": hash_report,
        "TOKEN_PROJECTION_FAILURES": 0,
        "weight_source": weight_source,
        "SLOT_CLASS_WEIGHT_VECTOR": frozen_vector,
        "recomputed_slot_class_weight_vector": recomputed_map,
        "slot_weight_vector_matches_b1_and_train_distribution": True,
        "config_diff": diff,
        "ISOLATED_VARIABLE_CHECK_PASS": diff["ISOLATED_VARIABLE_CHECK_PASS"],
        "slot_weight_wiring_test": wiring,
        "SLOT_WEIGHT_WIRED_TO_LOSS": wiring["SLOT_WEIGHT_WIRED_TO_LOSS"],
        "fresh_initialization": {
            "from_original_pretrained_electra": True,
            "from_electra_exp001_checkpoint": False,
            "from_rbt3_checkpoint": False,
            "fresh_differs_from_exp001_trained_checkpoint": fresh_is_not_exp001_checkpoint,
            "initial_backbone_hashes": initial_backbone,
            "initial_joint_head_hashes": initial_heads,
        },
        "optimizer_group_count": len(trainer.optimizer.param_groups),
        "optimizer_group_complete_coverage": True,
        "scheduler_base_lrs": list(map(float, trainer.scheduler.base_lrs)),
        "model_parameters_unchanged_after_forward_loss": initial_digest == after_digest,
        "gradients_created": False,
        "TRAINING_STEPS_EXECUTED": 0,
        "BACKWARD_PREFLIGHT_EXECUTED": False,
        "test_records_loaded": 0,
        "safety_gold_records_loaded": 0,
        "TEST_EVALUATION_EXECUTED": False,
        "SAFETY_GOLD_EVALUATION_EXECUTED": False,
        "python_executable": os.path.realpath(sys.executable),
    }


def token_level_enrichment(
    model: JointNLUModel,
    loader: DataLoader[Any],
    predictions: list[dict[str, Any]],
    *,
    tokenizer: Any,
    device: torch.device,
) -> dict[str, Any]:
    by_id = {row["sample_id"]: row for row in predictions}
    gold_counts: Counter[str] = Counter()
    predicted_counts: Counter[str] = Counter()
    value_cases: list[dict[str, Any]] = []
    model.eval()
    with torch.inference_mode():
        for batch in loader:
            outputs = model(**model_inputs(batch, device))
            predicted_batch = outputs["slot_logits"].argmax(-1).cpu()
            for index, sample_id in enumerate(batch["sample_ids"]):
                row = by_id[sample_id]
                text = batch["texts"][index]
                encoded = tokenizer(
                    text,
                    add_special_tokens=True,
                    truncation=True,
                    max_length=MAX_LENGTH,
                    return_offsets_mapping=True,
                )
                length = len(encoded["input_ids"])
                tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"])
                offsets = [[int(value) for value in item] for item in encoded["offset_mapping"]]
                gold_ids = batch["slot_labels"][index, :length].tolist()
                raw_predicted_ids = predicted_batch[index, :length].tolist()
                predicted_ids = [
                    IGNORE_INDEX if gold_ids[position] == IGNORE_INDEX else raw_predicted_ids[position]
                    for position in range(length)
                ]
                valid = [position for position, label in enumerate(gold_ids) if label != IGNORE_INDEX]
                gold_counts.update(SLOT_LABELS[gold_ids[position]] for position in valid)
                predicted_counts.update(SLOT_LABELS[predicted_ids[position]] for position in valid)
                token_rows = [
                    {
                        "token_index": position,
                        "token": tokens[position],
                        "offset": offsets[position],
                        "gold": SLOT_LABELS[gold_ids[position]],
                        "predicted": SLOT_LABELS[predicted_ids[position]],
                    }
                    for position in valid
                ]
                row["gold_slot_label_ids"] = gold_ids
                row["predicted_slot_label_ids"] = predicted_ids
                row["slot_token_predictions"] = token_rows
                gold_values = [slot for slot in row["gold_slots"] if slot["slot_type"] == "VALUE"]
                if gold_values:
                    predicted_values = [slot for slot in row["predicted_slots"] if slot["slot_type"] == "VALUE"]
                    exact = all(
                        any(
                            candidate["char_start"] == gold["char_start"]
                            and candidate["char_end"] == gold["char_end"]
                            for candidate in predicted_values
                        )
                        for gold in gold_values
                    )
                    status = "CORRECT" if exact else "MISSED" if not predicted_values else "BOUNDARY_ERROR"
                    value_cases.append(
                        {
                            "sample_id": sample_id,
                            "text": text,
                            "gold_VALUE": gold_values,
                            "predicted_VALUE": predicted_values,
                            "status": status,
                            "token_level_predictions": token_rows,
                        }
                    )
    total = sum(predicted_counts.values())
    return {
        "gold_slot_token_distribution": {label: gold_counts[label] for label in SLOT_LABELS},
        "predicted_slot_token_distribution": {label: predicted_counts[label] for label in SLOT_LABELS},
        "VALUE_GOLD_TOKEN_COUNT": gold_counts["B-VALUE"] + gold_counts["I-VALUE"],
        "VALUE_PREDICTED_TOKEN_COUNT": predicted_counts["B-VALUE"] + predicted_counts["I-VALUE"],
        "PREDICTED_O_RATE": predicted_counts["O"] / total,
        "VALUE_NO_OUTPUT_SAMPLE_COUNT": sum(row["status"] == "MISSED" for row in value_cases),
        "VALUE_BOUNDARY_ERROR_COUNT": sum(row["status"] == "BOUNDARY_ERROR" for row in value_cases),
        "VALUE_CORRECT_SAMPLE_COUNT": sum(row["status"] == "CORRECT" for row in value_cases),
        "validation_VALUE_sample_count": len(value_cases),
        "validation_VALUE_cases": value_cases,
    }


def baseline_metrics() -> dict[str, float]:
    metrics = read_json(EXP001_DIR / "evaluation" / "validation" / "reporting_metrics.json")
    return {
        "intent_macro_f1": metrics["intent"]["macro_f1"],
        "scope_macro_f1": metrics["scope"]["macro_f1"],
        "structure_macro_f1": metrics["structure"]["macro_f1"],
        "negation_f1": metrics["negation"]["per_class"]["NEGATED"]["f1"],
        "in_scope_control_recall": metrics["scope"]["per_class"]["IN_SCOPE_CONTROL"]["recall"],
        "slot_f1": metrics["slot"]["OVERALL"]["f1"],
        "value_f1": metrics["slot"]["VALUE"]["f1"],
    }


def acceptance_audit(metrics: dict[str, Any]) -> dict[str, Any]:
    baseline = baseline_metrics()
    current = {
        "intent_macro_f1": metrics["intent"]["macro_f1"],
        "scope_macro_f1": metrics["scope"]["macro_f1"],
        "structure_macro_f1": metrics["structure"]["macro_f1"],
        "negation_f1": metrics["negation"]["per_class"]["NEGATED"]["f1"],
        "in_scope_control_recall": metrics["scope"]["per_class"]["IN_SCOPE_CONTROL"]["recall"],
    }
    degradation = {name: baseline[name] - current[name] for name in current}
    degradation_pass = {
        name: degradation[name] <= DEGRADATION_LIMITS[name] for name in current
    }
    slot_improved = (
        metrics["slot"]["OVERALL"]["f1"] > BASELINE_SLOT_F1
        and metrics["slot"]["VALUE"]["f1"] > BASELINE_VALUE_F1
    )
    result = {
        "safety_gates_pass": bool(metrics["SAFETY_GATES_PASS"]),
        "slot_improved": slot_improved,
        "value_diagnostic_target_met": metrics["slot"]["VALUE"]["f1"] >= 0.50,
        "baseline": baseline,
        "current": current,
        "degradation": degradation,
        "degradation_limits": dict(DEGRADATION_LIMITS),
        "degradation_pass": degradation_pass,
    }
    result["ELECTRA_EXP002_PASS"] = bool(
        result["safety_gates_pass"]
        and slot_improved
        and all(degradation_pass.values())
    )
    return result


def exp002_closest_key(
    metrics: dict[str, Any],
) -> tuple[int, int, int, float, float, float, float]:
    audit = acceptance_audit(metrics)
    failed_degradation = sum(not value for value in audit["degradation_pass"].values())
    normalized_degradation_excess = sum(
        max(0.0, audit["degradation"][name] - limit) / limit
        for name, limit in DEGRADATION_LIMITS.items()
    )
    return (
        0 if audit["safety_gates_pass"] else 1,
        0 if audit["slot_improved"] else 1,
        failed_degradation,
        normalized_degradation_excess,
        -float(metrics["slot"]["VALUE"]["f1"]),
        -float(metrics["slot"]["OVERALL"]["f1"]),
        -float(metrics["PRIMARY_QUALITY_SCORE"]),
    )


def save_checkpoint(
    directory: Path,
    model: JointNLUModel,
    training_protocol: TrainingProtocol,
    slot_vector: dict[str, float],
    *,
    epoch: int,
    metrics: dict[str, Any],
    checkpoint_kind: str,
    prediction_artifact: str,
    best: bool,
    ranking_key: tuple[Any, ...] | None = None,
) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    state_path = directory / "model_state.pt"
    torch.save(model.state_dict(), state_path)
    write_json(directory / "label_mapping.json", label_mapping_report())
    write_json(
        directory / "model_config.json",
        {
            "model_id": MODEL_ID,
            "backbone_path": str(MODEL_SNAPSHOT),
            "backbone_revision": MODEL_REVISION,
            "hidden_size": model.hidden_size,
            "sentence_representation": "FIRST_TOKEN",
            "slot_representation": "FULL_LAST_HIDDEN_STATE",
        },
    )
    write_json(
        directory / "training_config.json",
        {
            **training_protocol.to_dict(),
            "single_optimizer_parameter_group": True,
            "slot_class_weight_policy": SLOT_WEIGHT_POLICY,
            "slot_class_weight_vector": slot_vector,
            "effective_task_loss_weights": dict(LOSS_WEIGHTS),
        },
    )
    manifest = {
        "checkpoint_format": "PYTORCH_STATE_DICT",
        "checkpoint_kind": checkpoint_kind,
        "epoch": epoch,
        "BEST": best,
        "DEPLOYABLE": False,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "initialized_from_original_pretrained_electra": True,
        "continued_from_previous_checkpoint": False,
        "slot_class_weight_policy": SLOT_WEIGHT_POLICY,
        "slot_class_weight_vector": slot_vector,
        "learning_rate": LEARNING_RATE,
        "dataset_manifest_sha256": sha256_file(MANIFEST_PATH),
        "model_state_sha256": sha256_file(state_path),
        "prediction_artifact": prediction_artifact,
        "validation_primary_quality_score": metrics["PRIMARY_QUALITY_SCORE"],
        "validation_safety_gates_pass": metrics["SAFETY_GATES_PASS"],
        "exp002_acceptance_audit": acceptance_audit(metrics),
        "failed_safety_gate_count": failed_safety_gate_count(metrics),
        "ranking_key": list(ranking_key) if ranking_key is not None else None,
        "test_evaluation_executed": False,
        "safety_gold_evaluation_executed": False,
    }
    write_json(directory / "checkpoint_manifest.json", manifest)
    return manifest


def comparison_markdown(summary: dict[str, Any], metrics: dict[str, Any]) -> str:
    baseline = read_json(EXP001_DIR / "training_summary.json")
    rows = (
        ("Intent Macro F1", baseline["VALIDATION_INTENT_MACRO_F1"], summary["VALIDATION_INTENT_MACRO_F1"]),
        ("Scope Macro F1", baseline["VALIDATION_SCOPE_MACRO_F1"], summary["VALIDATION_SCOPE_MACRO_F1"]),
        ("Structure Macro F1", baseline["VALIDATION_STRUCTURE_MACRO_F1"], summary["VALIDATION_STRUCTURE_MACRO_F1"]),
        ("AREA F1", baseline["AREA_F1"], summary["AREA_F1"]),
        ("VALUE F1", baseline["VALUE_F1"], summary["VALUE_F1"]),
        ("NEGATION span F1", baseline["NEGATION_SPAN_F1"], summary["NEGATION_SPAN_F1"]),
        ("Overall Slot F1", baseline["VALIDATION_SLOT_SPAN_F1"], summary["VALIDATION_SLOT_SPAN_F1"]),
        ("Sentence Negation F1", baseline["VALIDATION_NEGATION_F1"], summary["VALIDATION_NEGATION_F1"]),
        ("Negated Recall", baseline["VALIDATION_NEGATED_RECALL"], summary["VALIDATION_NEGATED_RECALL"]),
        ("UFAR", baseline["RAW_VALIDATION_UFAR"], summary["RAW_VALIDATION_UFAR"]),
        ("AMBIGUOUS FA", baseline["AMBIGUOUS_FALSE_ACCEPT_COUNT"], summary["AMBIGUOUS_FALSE_ACCEPT_COUNT"]),
        ("MULTI FA", baseline["MULTI_FALSE_ACCEPT_COUNT"], summary["MULTI_FALSE_ACCEPT_COUNT"]),
        ("UNKNOWN FA", baseline["UNKNOWN_FALSE_ACCEPT_COUNT"], summary["UNKNOWN_FALSE_ACCEPT_COUNT"]),
        ("NON_CONTROL FA", baseline["NON_CONTROL_FALSE_ACCEPT_COUNT"], summary["NON_CONTROL_FALSE_ACCEPT_COUNT"]),
        ("PREDICTED_O_RATE", baseline.get("SELECTED_VALIDATION_METRICS", {}).get("PREDICTED_O_RATE", 0.9056047197640118), summary["PREDICTED_O_RATE"]),
        ("Training seconds", baseline["TOTAL_TRAINING_SECONDS"], summary["TOTAL_TRAINING_SECONDS"]),
        ("Best epoch", baseline["BEST_EPOCH"], summary["BEST_EPOCH"]),
    )
    table = "\n".join(f"| {name} | {left:.6f} | {right:.6f} |" for name, left, right in rows)
    return f"""# ELECTRA exp001 vs exp002

本轮唯一有意改变的变量是 Slot class weighting：`NONE` → `{SLOT_WEIGHT_POLICY}`。其余训练协议与 checkpoint score 均保持一致。因此 Slot 差异可作为 class-imbalance treatment 有帮助的工程证据，但不是严格因果证明。

| Metric | ELECTRA exp001 | ELECTRA exp002 |
|---|---:|---:|
{table}

## 验收

```json
{json.dumps(summary['EXP002_ACCEPTANCE_AUDIT'], ensure_ascii=False, indent=2)}
```

- ELECTRA_EXP002_SAFETY_GATE_PASS=`{'YES' if summary['ELECTRA_EXP002_SAFETY_GATE_PASS'] else 'NO'}`
- ELECTRA_EXP002_SLOT_IMPROVED=`{'YES' if summary['ELECTRA_EXP002_SLOT_IMPROVED'] else 'NO'}`
- ELECTRA_EXP002_PASS=`{'YES' if summary['ELECTRA_EXP002_PASS'] else 'NO'}`
- DEPLOYABLE=`NO`
"""


def summary_markdown(summary: dict[str, Any]) -> str:
    return f"""# SYS-014 Stage 4C-B.2 ELECTRA exp002

- reporting checkpoint: `{summary['REPORTING_CHECKPOINT_KIND']}` epoch `{summary['REPORTING_EPOCH']}`
- Slot F1: `{summary['VALIDATION_SLOT_SPAN_F1']:.6f}`
- VALUE F1: `{summary['VALUE_F1']:.6f}`
- PREDICTED_O_RATE: `{summary['PREDICTED_O_RATE']:.6f}`
- UFAR: `{summary['RAW_VALIDATION_UFAR']:.6f}`

ISOLATED_VARIABLE_CHECK_PASS={'YES' if summary['ISOLATED_VARIABLE_CHECK_PASS'] else 'NO'}

SLOT_WEIGHT_WIRED_TO_LOSS={'YES' if summary['SLOT_WEIGHT_WIRED_TO_LOSS'] else 'NO'}

ELECTRA_EXP002_SAFETY_GATE_PASS={'YES' if summary['ELECTRA_EXP002_SAFETY_GATE_PASS'] else 'NO'}

ELECTRA_EXP002_SLOT_IMPROVED={'YES' if summary['ELECTRA_EXP002_SLOT_IMPROVED'] else 'NO'}

ELECTRA_EXP002_PASS={'YES' if summary['ELECTRA_EXP002_PASS'] else 'NO'}

READY_FOR_STAGE_4C_MODEL_DECISION={'YES' if summary['READY_FOR_STAGE_4C_MODEL_DECISION'] else 'NO'}

TEST_EVALUATION_EXECUTED=NO

SAFETY_GOLD_EVALUATION_EXECUTED=NO
"""


def run_training() -> int:
    preflight = run_preflight(require_experiment_absent=True)
    if not preflight["ISOLATED_VARIABLE_CHECK_PASS"] or not preflight["SLOT_WEIGHT_WIRED_TO_LOSS"]:
        raise RuntimeError("EXP002_PREFLIGHT_GATES_FAILED")
    frozen_vector = preflight["SLOT_CLASS_WEIGHT_VECTOR"]
    training_protocol = protocol()
    set_deterministic_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_SNAPSHOT, local_files_only=True, use_fast=True)
    distribution, failures, _, validation_records, hash_report = data_context(tokenizer)
    if failures:
        raise RuntimeError(f"TOKEN_PROJECTION_FAILURES={len(failures)}")
    train_dataset = FrozenJointNLUDataset("train", tokenizer, max_length=MAX_LENGTH)
    validation_dataset = FrozenJointNLUDataset("validation", tokenizer, max_length=MAX_LENGTH)
    collator = JointNLUCollator(tokenizer)
    generator = torch.Generator().manual_seed(SEED)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, generator=generator, collate_fn=collator)
    validation_loader = DataLoader(validation_dataset, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collator)
    records_by_id = {record["sample_id"]: record for record in validation_records}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = JointNLUModel(str(MODEL_SNAPSHOT)).to(device)
    initial_backbone = representative_parameter_hashes(model.backbone)
    initial_heads = {
        name: representative_parameter_hashes(getattr(model, name))
        for name in ("scope_head", "structure_head", "intent_head", "slot_head", "negation_head")
    }
    total_steps = len(train_loader) * MAX_EPOCHS
    trainer = Stage4CTrainer(model, training_protocol, device=device, total_optimizer_steps=total_steps)
    class_weights = exp2_class_weights(distribution, training_protocol, device, frozen_vector)
    create_experiment_directories()
    write_json(EXPERIMENT_DIR / "preflight.json", preflight)
    write_json(EXPERIMENT_DIR / "exp001_vs_exp002_config_diff.json", preflight["config_diff"])
    config = {
        **training_protocol.to_dict(),
        "experiment_id": EXPERIMENT_ID,
        "actual_batch_size": BATCH_SIZE,
        "training_device": device.type.upper(),
        "single_optimizer_parameter_group": True,
        "discriminative_learning_rate": False,
        "slot_class_weight_policy": SLOT_WEIGHT_POLICY,
        "slot_class_weight_vector": frozen_vector,
        "effective_task_loss_weights": dict(LOSS_WEIGHTS),
        "total_optimizer_steps": total_steps,
        "warmup_steps": trainer.warmup_steps,
        "isolated_acceptance_thresholds": dict(DEGRADATION_LIMITS),
        "test_used_for_model_selection": False,
        "safety_gold_used_for_model_selection": False,
    }
    write_json(EXPERIMENT_DIR / "experiment_config.json", config)
    (EXPERIMENT_DIR / "training_log.jsonl").write_text("", encoding="utf-8")
    (EXPERIMENT_DIR / "metrics_by_epoch.jsonl").write_text("", encoding="utf-8")
    started_at = iso_now()
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "status": "RUNNING",
        "dataset_version": training_protocol.dataset_version,
        "dataset_manifest_sha256": hash_report["dataset_manifest_sha256"],
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "seed": SEED,
        "device": device.type.upper(),
        "cpu_model": cpu_name(),
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "python_executable": os.path.realpath(sys.executable),
        "git_commit": current_git_commit(),
        "started_at": started_at,
        "finished_at": None,
        "initialized_from_original_pretrained_electra": True,
        "continued_from_electra_exp001": False,
        "test_evaluation_executed": False,
        "safety_gold_evaluation_executed": False,
        "runtime_modified": False,
        "electra_exp003_started": False,
        "rbt3_training_started": False,
        "macbert_training_started": False,
        "preflight": preflight,
    }
    write_json(EXPERIMENT_DIR / "manifest.json", manifest)
    append_jsonl(EXPERIMENT_DIR / "training_log.jsonl", {"event": "TRAINING_STARTED", "at": started_at, "config": config})

    started = time.perf_counter()
    history: list[dict[str, Any]] = []
    durations: list[float] = []
    best_metrics: dict[str, Any] | None = None
    best_epoch: int | None = None
    best_score = -1.0
    best_prediction: str | None = None
    best_manifest: dict[str, Any] | None = None
    closest_safety_metrics: dict[str, Any] | None = None
    closest_safety_epoch: int | None = None
    closest_safety_rank: tuple[int, int, int, float] | None = None
    closest_exp_rank: tuple[int, int, int, float, float, float, float] | None = None
    closest_exp_metrics: dict[str, Any] | None = None
    closest_exp_epoch: int | None = None
    closest_exp_manifest: dict[str, Any] | None = None
    stale = 0
    non_finite = False
    try:
        for epoch in range(1, MAX_EPOCHS + 1):
            epoch_started = time.perf_counter()
            train_started = time.perf_counter()
            train_result = trainer.train_epoch(train_loader, class_weights=class_weights)
            train_seconds = time.perf_counter() - train_started
            validation_started = time.perf_counter()
            metrics, predictions = evaluate_validation(
                model,
                validation_loader,
                records_by_id=records_by_id,
                tokenizer=tokenizer,
                device=device,
                class_weights=class_weights,
                training_protocol=training_protocol,
            )
            token_metrics = token_level_enrichment(
                model,
                validation_loader,
                predictions,
                tokenizer=tokenizer,
                device=device,
            )
            metrics.update(token_metrics)
            metrics["tracked_abstention_examples"] = tracked_abstention(predictions)
            metrics["EXP002_ACCEPTANCE_AUDIT"] = acceptance_audit(metrics)
            validation_seconds = time.perf_counter() - validation_started
            prediction_relative = f"evaluation/validation/epoch_{epoch:02d}_predictions.jsonl"
            write_jsonl(EXPERIMENT_DIR / prediction_relative, predictions)
            epoch_seconds = time.perf_counter() - epoch_started
            durations.append(epoch_seconds)
            record = {
                "epoch": epoch,
                "train": train_result,
                "validation": metrics,
                "prediction_artifact": prediction_relative,
                "train_seconds": train_seconds,
                "validation_seconds": validation_seconds,
                "epoch_seconds": epoch_seconds,
            }
            history.append(record)
            append_jsonl(EXPERIMENT_DIR / "metrics_by_epoch.jsonl", record)
            eligible = bool(metrics["SAFETY_GATES_PASS"])
            score = float(metrics["PRIMARY_QUALITY_SCORE"])
            if eligible and score > best_score:
                best_score = score
                best_epoch = epoch
                best_metrics = metrics
                best_prediction = prediction_relative
                stale = 0
                best_manifest = save_checkpoint(
                    EXPERIMENT_DIR / "checkpoints" / "best",
                    model,
                    training_protocol,
                    frozen_vector,
                    epoch=epoch,
                    metrics=metrics,
                    checkpoint_kind="ELIGIBLE_BEST",
                    prediction_artifact=prediction_relative,
                    best=True,
                )
            elif best_metrics is not None:
                stale += 1
            if not eligible:
                safety_rank = closest_key(metrics)
                if closest_safety_rank is None or safety_rank < closest_safety_rank:
                    closest_safety_rank = safety_rank
                    closest_safety_epoch = epoch
                    closest_safety_metrics = metrics
                    save_checkpoint(
                        EXPERIMENT_DIR / "checkpoints" / "closest_safety_diagnostic",
                        model,
                        training_protocol,
                        frozen_vector,
                        epoch=epoch,
                        metrics=metrics,
                        checkpoint_kind="CLOSEST_SAFETY_DIAGNOSTIC",
                        prediction_artifact=prediction_relative,
                        best=False,
                        ranking_key=safety_rank,
                    )
            exp_rank = exp002_closest_key(metrics)
            if closest_exp_rank is None or exp_rank < closest_exp_rank:
                closest_exp_rank = exp_rank
                closest_exp_epoch = epoch
                closest_exp_metrics = metrics
                closest_exp_manifest = save_checkpoint(
                    EXPERIMENT_DIR / "checkpoints" / "closest_exp002_diagnostic",
                    model,
                    training_protocol,
                    frozen_vector,
                    epoch=epoch,
                    metrics=metrics,
                    checkpoint_kind="CLOSEST_EXP002_DIAGNOSTIC",
                    prediction_artifact=prediction_relative,
                    best=False,
                    ranking_key=exp_rank,
                )
            tracked = metrics["tracked_ambiguous_family"]
            progress = {
                "epoch": epoch,
                "quality": score,
                "eligible": eligible,
                "slot_f1": metrics["slot"]["OVERALL"]["f1"],
                "value_f1": metrics["slot"]["VALUE"]["f1"],
                "predicted_o_rate": metrics["PREDICTED_O_RATE"],
                "value_predicted_tokens": metrics["VALUE_PREDICTED_TOKEN_COUNT"],
                "value_no_output_samples": metrics["VALUE_NO_OUTPUT_SAMPLE_COUNT"],
                "ufar": metrics["safety"]["UNSAFE_FALSE_ACCEPT_RATE"],
                "ambiguous_false_accepts": metrics["safety"]["per_category"]["AMBIGUOUS"]["unsafe_false_accepts"],
                "multi_false_accepts": metrics["safety"]["per_category"]["MULTI"]["unsafe_false_accepts"],
                "0731_abstain": tracked["SYS014-POC-0731"]["raw_abstain"],
                "0732_abstain": tracked["SYS014-POC-0732"]["raw_abstain"],
                "0733_abstain": tracked["SYS014-POC-0733"]["raw_abstain"],
                "exp002_pass_at_epoch": metrics["EXP002_ACCEPTANCE_AUDIT"]["ELECTRA_EXP002_PASS"],
                "training_steps": trainer.training_steps_executed,
                "epoch_seconds": epoch_seconds,
            }
            print(json.dumps(progress, ensure_ascii=False), flush=True)
            append_jsonl(EXPERIMENT_DIR / "training_log.jsonl", {"event": "EPOCH_FINISHED", **progress})
            if best_metrics is not None and stale >= PATIENCE:
                append_jsonl(EXPERIMENT_DIR / "training_log.jsonl", {"event": "EARLY_STOPPING", "epoch": epoch, "stale_eligible_epochs": stale})
                break
    except FloatingPointError as exc:
        non_finite = True
        append_jsonl(EXPERIMENT_DIR / "training_log.jsonl", {"event": "TRAINING_ABORTED_NON_FINITE", "at": iso_now(), "error": str(exc)})

    total_seconds = time.perf_counter() - started
    if not history:
        raise RuntimeError("ELECTRA exp002 completed no Validation epoch")
    epochs_completed = len(history)
    last_metrics = history[-1]["validation"]
    last_prediction = history[-1]["prediction_artifact"]
    last_manifest = save_checkpoint(
        EXPERIMENT_DIR / "checkpoints" / "last",
        model,
        training_protocol,
        frozen_vector,
        epoch=epochs_completed,
        metrics=last_metrics,
        checkpoint_kind="LAST_DIAGNOSTIC",
        prediction_artifact=last_prediction,
        best=False,
    )
    if best_metrics is None:
        (EXPERIMENT_DIR / "checkpoints" / "best" / "NO_ELIGIBLE_CHECKPOINT.md").write_text(
            "# No eligible checkpoint\n\nNo epoch passed every frozen safety gate.\n",
            encoding="utf-8",
        )
    if closest_safety_metrics is None:
        (EXPERIMENT_DIR / "checkpoints" / "closest_safety_diagnostic" / "NO_NON_ELIGIBLE_EPOCH.md").write_text(
            "# No non-eligible epoch\n",
            encoding="utf-8",
        )
    reporting = best_metrics if best_metrics is not None else closest_safety_metrics
    reporting_epoch = best_epoch if best_epoch is not None else closest_safety_epoch
    reporting_kind = "ELIGIBLE_BEST" if best_metrics is not None else "CLOSEST_SAFETY_DIAGNOSTIC"
    reporting_prediction = best_prediction if best_metrics is not None else history[reporting_epoch - 1]["prediction_artifact"] if reporting_epoch else None
    if reporting is None or reporting_epoch is None or reporting_prediction is None:
        raise RuntimeError("no reporting checkpoint")
    write_jsonl(
        EXPERIMENT_DIR / "evaluation" / "validation" / "error_cases.jsonl",
        [{"reporting_epoch": reporting_epoch, **item} for item in reporting["error_cases"]],
    )
    write_json(
        EXPERIMENT_DIR / "evaluation" / "validation" / "reporting_metrics.json",
        {"epoch": reporting_epoch, "checkpoint_kind": reporting_kind, **reporting},
    )
    acceptance = acceptance_audit(reporting)
    safety = reporting["safety"]
    tracked = reporting["tracked_ambiguous_family"]
    abstention = reporting["tracked_abstention_examples"]
    summary = {
        "EXPERIMENT_ID": EXPERIMENT_ID,
        "ISOLATED_VARIABLE_CHECK_PASS": preflight["ISOLATED_VARIABLE_CHECK_PASS"],
        "SLOT_WEIGHT_WIRED_TO_LOSS": preflight["SLOT_WEIGHT_WIRED_TO_LOSS"],
        "SLOT_CLASS_WEIGHT_VECTOR": frozen_vector,
        "EPOCHS_COMPLETED": epochs_completed,
        "BEST_EPOCH": best_epoch,
        "REPORTING_EPOCH": reporting_epoch,
        "REPORTING_CHECKPOINT_KIND": reporting_kind,
        "TRAINING_STEPS_EXECUTED": trainer.training_steps_executed,
        "MEAN_EPOCH_SECONDS": sum(durations) / len(durations),
        "TOTAL_TRAINING_SECONDS": total_seconds,
        "VALIDATION_INTENT_MACRO_F1": reporting["intent"]["macro_f1"],
        "VALIDATION_SCOPE_MACRO_F1": reporting["scope"]["macro_f1"],
        "IN_SCOPE_CONTROL_RECALL": reporting["scope"]["per_class"]["IN_SCOPE_CONTROL"]["recall"],
        "NON_CONTROL_RECALL": reporting["scope"]["per_class"]["NON_CONTROL"]["recall"],
        "UNKNOWN_CONTROL_RECALL": reporting["scope"]["per_class"]["UNKNOWN_CONTROL"]["recall"],
        "AMBIGUOUS_CONTROL_RECALL": reporting["scope"]["per_class"]["AMBIGUOUS_CONTROL"]["recall"],
        "VALIDATION_STRUCTURE_MACRO_F1": reporting["structure"]["macro_f1"],
        "VALIDATION_SLOT_SPAN_F1": reporting["slot"]["OVERALL"]["f1"],
        "AREA_F1": reporting["slot"]["AREA"]["f1"],
        "VALUE_F1": reporting["slot"]["VALUE"]["f1"],
        "NEGATION_SPAN_F1": reporting["slot"]["NEGATION"]["f1"],
        "VALUE_GOLD_TOKEN_COUNT": reporting["VALUE_GOLD_TOKEN_COUNT"],
        "VALUE_PREDICTED_TOKEN_COUNT": reporting["VALUE_PREDICTED_TOKEN_COUNT"],
        "VALUE_NO_OUTPUT_SAMPLE_COUNT": reporting["VALUE_NO_OUTPUT_SAMPLE_COUNT"],
        "VALUE_BOUNDARY_ERROR_COUNT": reporting["VALUE_BOUNDARY_ERROR_COUNT"],
        "PREDICTED_O_RATE": reporting["PREDICTED_O_RATE"],
        "VALIDATION_NEGATION_F1": reporting["negation"]["per_class"]["NEGATED"]["f1"],
        "VALIDATION_NEGATED_RECALL": reporting["negation"]["per_class"]["NEGATED"]["recall"],
        "HEADLIGHT_OFF_NEGATED_RECALL": reporting["per_intent_negation"]["HEADLIGHT_OFF"]["per_class"]["NEGATED"]["recall"],
        "ACCELERATE_NEGATED_RECALL": reporting["per_intent_negation"]["ACCELERATE"]["per_class"]["NEGATED"]["recall"],
        "NEGATION_HEAD_SLOT_DISAGREEMENT_COUNT": reporting["NEGATION_HEAD_SLOT_DISAGREEMENT_COUNT"],
        "RAW_VALIDATION_UFAR": safety["UNSAFE_FALSE_ACCEPT_RATE"],
        "AMBIGUOUS_FALSE_ACCEPT_COUNT": safety["per_category"]["AMBIGUOUS"]["unsafe_false_accepts"],
        "MULTI_FALSE_ACCEPT_COUNT": safety["per_category"]["MULTI"]["unsafe_false_accepts"],
        "UNKNOWN_FALSE_ACCEPT_COUNT": safety["per_category"]["UNKNOWN_CONTROL"]["unsafe_false_accepts"],
        "NON_CONTROL_FALSE_ACCEPT_COUNT": safety["per_category"]["NON_CONTROL"]["unsafe_false_accepts"],
        "0731_FINAL_ABSTAIN": tracked["SYS014-POC-0731"]["raw_abstain"],
        "0732_FINAL_ABSTAIN": tracked["SYS014-POC-0732"]["raw_abstain"],
        "0733_FINAL_ABSTAIN": tracked["SYS014-POC-0733"]["raw_abstain"],
        "0748_FINAL_ABSTAIN": abstention["SYS014-POC-0748"]["raw_abstain"],
        "0762_FINAL_ABSTAIN": abstention["SYS014-POC-0762"]["raw_abstain"],
        "0773_FINAL_ABSTAIN": abstention["SYS014-POC-0773"]["raw_abstain"],
        "BEST_CHECKPOINT_SAVED": best_manifest is not None,
        "BEST_CHECKPOINT_SHA256": best_manifest["model_state_sha256"] if best_manifest else None,
        "CLOSEST_EXP002_DIAGNOSTIC_EPOCH": closest_exp_epoch,
        "CLOSEST_EXP002_DIAGNOSTIC_SHA256": closest_exp_manifest["model_state_sha256"] if closest_exp_manifest else None,
        "LAST_CHECKPOINT_SHA256": last_manifest["model_state_sha256"],
        "EXP002_ACCEPTANCE_AUDIT": acceptance,
        "VALUE_F1_DIAGNOSTIC_TARGET_MET": acceptance["value_diagnostic_target_met"],
        "NON_FINITE_LOSS_DETECTED": non_finite,
        "INITIAL_BACKBONE_PARAMETER_HASHES": initial_backbone,
        "INITIAL_JOINT_HEAD_PARAMETER_HASHES": initial_heads,
        "FINAL_BACKBONE_PARAMETER_HASHES": representative_parameter_hashes(model.backbone),
        "TEST_EVALUATION_EXECUTED": False,
        "SAFETY_GOLD_EVALUATION_EXECUTED": False,
        "RUNTIME_MODIFIED": False,
        "ELECTRA_EXP003_STARTED": False,
        "RBT3_TRAINING_STARTED": False,
        "MACBERT_TRAINING_STARTED": False,
        "ELECTRA_EXP002_SAFETY_GATE_PASS": best_metrics is not None,
        "ELECTRA_EXP002_SLOT_IMPROVED": acceptance["slot_improved"],
        "ELECTRA_EXP002_PASS": acceptance["ELECTRA_EXP002_PASS"],
        "READY_FOR_STAGE_4C_MODEL_DECISION": acceptance["ELECTRA_EXP002_PASS"],
        "SELECTED_VALIDATION_METRICS": reporting,
    }
    write_json(EXPERIMENT_DIR / "training_summary.json", summary)
    (EXPERIMENT_DIR / "training_summary.md").write_text(summary_markdown(summary), encoding="utf-8")
    (EXPERIMENT_DIR / "electra_exp001_vs_exp002.md").write_text(comparison_markdown(summary, reporting), encoding="utf-8")
    finished_at = iso_now()
    append_jsonl(EXPERIMENT_DIR / "training_log.jsonl", {"event": "TRAINING_FINISHED", "at": finished_at, "summary": {key: value for key, value in summary.items() if key != "SELECTED_VALIDATION_METRICS"}})
    manifest.update(
        {
            "status": "COMPLETED_PASS" if summary["ELECTRA_EXP002_PASS"] else "COMPLETED_FAIL",
            "finished_at": finished_at,
            "training_duration_seconds": total_seconds,
            "rss_after_training_bytes": current_rss_bytes(),
            "epochs_completed": epochs_completed,
            "training_steps_executed": trainer.training_steps_executed,
            "best_epoch": best_epoch,
            "electra_exp002_safety_gate_pass": summary["ELECTRA_EXP002_SAFETY_GATE_PASS"],
            "electra_exp002_slot_improved": summary["ELECTRA_EXP002_SLOT_IMPROVED"],
            "electra_exp002_pass": summary["ELECTRA_EXP002_PASS"],
            "ready_for_stage_4c_model_decision": summary["READY_FOR_STAGE_4C_MODEL_DECISION"],
        }
    )
    write_json(EXPERIMENT_DIR / "manifest.json", manifest)
    print(json.dumps({key: value for key, value in summary.items() if key != "SELECTED_VALIDATION_METRICS"}, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--refresh-existing-selection", action="store_true")
    return parser.parse_args()


def refresh_existing_selection() -> int:
    if not EXPERIMENT_DIR.is_dir():
        raise FileNotFoundError(EXPERIMENT_DIR)
    history = read_jsonl(EXPERIMENT_DIR / "metrics_by_epoch.jsonl")
    selected = min(history, key=lambda row: exp002_closest_key(row["validation"]))
    epoch = int(selected["epoch"])
    metrics = selected["validation"]
    ranking = exp002_closest_key(metrics)
    best_dir = EXPERIMENT_DIR / "checkpoints" / "best"
    best_manifest = read_json(best_dir / "checkpoint_manifest.json")
    if int(best_manifest["epoch"]) != epoch:
        raise RuntimeError(
            "refresh requires selected closest epoch to equal preserved best checkpoint epoch"
        )
    target = EXPERIMENT_DIR / "checkpoints" / "closest_exp002_diagnostic"
    for name in (
        "model_state.pt",
        "label_mapping.json",
        "model_config.json",
        "training_config.json",
    ):
        shutil.copy2(best_dir / name, target / name)
    diagnostic_manifest = dict(best_manifest)
    diagnostic_manifest.update(
        {
            "checkpoint_kind": "CLOSEST_EXP002_DIAGNOSTIC",
            "BEST": False,
            "DEPLOYABLE": False,
            "ranking_key": list(ranking),
        }
    )
    write_json(target / "checkpoint_manifest.json", diagnostic_manifest)
    summary_path = EXPERIMENT_DIR / "training_summary.json"
    summary = read_json(summary_path)
    summary["CLOSEST_EXP002_DIAGNOSTIC_EPOCH"] = epoch
    summary["CLOSEST_EXP002_DIAGNOSTIC_SHA256"] = diagnostic_manifest[
        "model_state_sha256"
    ]
    write_json(summary_path, summary)
    (EXPERIMENT_DIR / "training_summary.md").write_text(
        summary_markdown(summary), encoding="utf-8"
    )
    (EXPERIMENT_DIR / "electra_exp001_vs_exp002.md").write_text(
        comparison_markdown(summary, summary["SELECTED_VALIDATION_METRICS"]),
        encoding="utf-8",
    )
    append_jsonl(
        EXPERIMENT_DIR / "training_log.jsonl",
        {
            "event": "CLOSEST_EXP002_SELECTION_REFRESHED",
            "at": iso_now(),
            "epoch": epoch,
            "ranking_key": list(ranking),
            "training_steps_added": 0,
        },
    )
    return 0


def main() -> int:
    args = parse_args()
    if args.preflight_only:
        print(json.dumps(run_preflight(require_experiment_absent=True), ensure_ascii=False, indent=2))
        return 0
    if args.refresh_existing_selection:
        return refresh_existing_selection()
    return run_training()


if __name__ == "__main__":
    raise SystemExit(main())
