"""SYS-014 Stage 4C-B: ELECTRA-small same-protocol exp001 baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import torch
import transformers
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from scripts.profile_sys014_stage4a import cpu_name, current_rss_bytes

from .collator import JointNLUCollator
from .dataset import FrozenJointNLUDataset, project_all_records, training_record_distribution
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
from .model import JointNLUModel, representative_parameter_hashes
from .stage4c_exp002 import (
    build_prediction_row,
    closest_key,
    evaluate_validation,
    failed_safety_gate_count,
    prediction_schema_ok,
    run_boundary_probes,
)
from .train_config import TrainingProtocol, repository_root
from .trainer import Stage4CTrainer
from .validation import (
    DATASET_DIR,
    MANIFEST_PATH,
    read_split,
    sha256_file,
    verify_manifest_hashes,
)


EXPERIMENT_ID = "sys014-poc7-electra-exp001"
MODEL_ID = "hfl/chinese-electra-180g-small-discriminator"
MODEL_REVISION = "826a243f3f387450ef8d70de9c3d0706d8d8e924"
MODEL_WEIGHT_SHA256 = "45c0a4519ee767bd58ddd3573b9ceebb81a2c0fb65919a8b7513b57ee52009b3"
EXPECTED_DATASET_MANIFEST_SHA256 = (
    "122621c0ce5e7a6fbaadbbe97cb3e7e86a32812ee1c69fe5ee27c45d94ac8d42"
)
SEED = 14031
MAX_LENGTH = 32
BATCH_SIZE = 16
MAX_EPOCHS = 10
PATIENCE = 3
LEARNING_RATE = 2e-5
LOSS_WEIGHTS = {task: 1.0 for task in ("scope", "structure", "intent", "slot", "negation")}
TRACKED_ABSTENTION_IDS = (
    "SYS014-POC-0748",
    "SYS014-POC-0762",
    "SYS014-POC-0773",
)
EXPERIMENT_DIR = repository_root() / "data" / "nlu" / "experiments" / EXPERIMENT_ID
RBT3_EXP001_DIR = (
    repository_root() / "data" / "nlu" / "experiments" / "sys014-poc7-rbt3-exp001"
)
CANDIDATE_MATRIX_PATH = repository_root() / "data" / "nlu" / "model_selection" / "candidate_matrix.json"
MODEL_SNAPSHOT = (
    repository_root()
    / "data"
    / "nlu"
    / "model_selection"
    / "hf_cache"
    / "models--hfl--chinese-electra-180g-small-discriminator"
    / "snapshots"
    / MODEL_REVISION
)


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def protocol() -> TrainingProtocol:
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
    )


def model_inputs(batch: dict[str, Any], device: torch.device) -> dict[str, torch.Tensor]:
    result = {
        "input_ids": batch["input_ids"].to(device),
        "attention_mask": batch["attention_mask"].to(device),
    }
    if "token_type_ids" in batch:
        result["token_type_ids"] = batch["token_type_ids"].to(device)
    return result


def candidate_provenance() -> dict[str, Any]:
    matrix = read_json(CANDIDATE_MATRIX_PATH)
    matches = [item for item in matrix["candidates"] if item["model_id"] == MODEL_ID]
    if len(matches) != 1:
        raise RuntimeError(f"Stage 4A candidate lookup expected one match, got {len(matches)}")
    item = matches[0]
    if item["revision"] != MODEL_REVISION:
        raise RuntimeError("ELECTRA_REVISION_MISMATCH")
    recorded_path = Path(item["local_cache_path"])
    if recorded_path.resolve() != MODEL_SNAPSHOT.resolve():
        raise RuntimeError("ELECTRA_CACHE_PATH_MISMATCH")
    if not MODEL_SNAPSHOT.is_dir():
        raise FileNotFoundError(f"Fixed Stage 4A snapshot unavailable: {MODEL_SNAPSHOT}")
    weight_path = MODEL_SNAPSHOT / "pytorch_model.bin"
    actual_weight_hash = sha256_file(weight_path)
    recorded_hashes = {entry["name"]: entry["sha256"] for entry in item["weight_files"]}
    if actual_weight_hash != MODEL_WEIGHT_SHA256 or recorded_hashes.get("pytorch_model.bin") != actual_weight_hash:
        raise RuntimeError("ELECTRA_WEIGHT_HASH_MISMATCH")
    return {
        "model_id": item["model_id"],
        "revision": item["revision"],
        "local_cache_path": str(recorded_path),
        "tokenizer_fast": item["tokenizer_fast"],
        "hidden_size": item["architecture"]["hidden_size"],
        "pretrained_parameter_count": item["total_parameters"],
        "weight_sha256": actual_weight_hash,
        "loading_info": item["loading_info"],
        "stage4a_cpu_p95_total_ms": item["p95_total_ms"],
    }


def data_context(tokenizer: Any) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    hash_report = verify_manifest_hashes()
    if hash_report["dataset_manifest_sha256"] != EXPECTED_DATASET_MANIFEST_SHA256:
        raise RuntimeError("FROZEN_V2_MANIFEST_HASH_MISMATCH")
    train_records = read_split("train")
    validation_records = read_split("validation")
    train_slots, train_failures = project_all_records(train_records, tokenizer, max_length=MAX_LENGTH)
    _, validation_failures = project_all_records(validation_records, tokenizer, max_length=MAX_LENGTH)
    failures = (
        [{"split": "train", **item.to_dict()} for item in train_failures]
        + [{"split": "validation", **item.to_dict()} for item in validation_failures]
    )
    distribution = training_record_distribution(train_records)
    distribution["slot_token_labels"] = dict(sorted(train_slots.items()))
    return {"train": distribution}, failures, train_records, validation_records, hash_report


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


def run_preflight(*, require_experiment_absent: bool = True) -> dict[str, Any]:
    if require_experiment_absent and EXPERIMENT_DIR.exists():
        raise FileExistsError(f"Preflight refuses existing experiment: {EXPERIMENT_DIR}")
    provenance = candidate_provenance()
    training_protocol = protocol()
    set_deterministic_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_SNAPSHOT, local_files_only=True, use_fast=True)
    if not tokenizer.is_fast:
        raise RuntimeError("FAST_TOKENIZER_REQUIRED")
    distribution, failures, _, validation_records, hash_report = data_context(tokenizer)
    if failures:
        raise RuntimeError(f"TOKEN_PROJECTION_FAILURES={len(failures)}")
    train_dataset = FrozenJointNLUDataset("train", tokenizer, max_length=MAX_LENGTH)
    validation_dataset = FrozenJointNLUDataset("validation", tokenizer, max_length=MAX_LENGTH)
    collator = JointNLUCollator(tokenizer)
    edge_count = min(BATCH_SIZE // 2, len(validation_dataset) // 2)
    dry_indices = list(range(edge_count)) + list(
        range(len(validation_dataset) - edge_count, len(validation_dataset))
    )
    batch = collator([validation_dataset[index] for index in dry_indices])
    records_by_id = {record["sample_id"]: record for record in validation_records}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = JointNLUModel(str(MODEL_SNAPSHOT)).to(device)
    initial_digest = model_state_digest(model)
    initial_backbone_hashes = representative_parameter_hashes(model.backbone)
    initial_head_hashes = {
        name: representative_parameter_hashes(getattr(model, name))
        for name in ("scope_head", "structure_head", "intent_head", "slot_head", "negation_head")
    }
    total_steps = math.ceil(len(train_dataset) / BATCH_SIZE) * MAX_EPOCHS
    trainer = Stage4CTrainer(model, training_protocol, device=device, total_optimizer_steps=total_steps)
    if trainer.discriminative_learning_rates or len(trainer.optimizer.param_groups) != 1:
        raise AssertionError("ELECTRA exp001 requires exactly one optimizer parameter group")
    optimizer_ids = {id(parameter) for group in trainer.optimizer.param_groups for parameter in group["params"]}
    trainable_ids = {id(parameter) for parameter in model.parameters() if parameter.requires_grad}
    if optimizer_ids != trainable_ids:
        raise AssertionError("single optimizer group does not completely cover trainable parameters")
    if list(map(float, trainer.scheduler.base_lrs)) != [LEARNING_RATE]:
        raise AssertionError("baseline scheduler LR mismatch")
    class_weights = tensor_class_weights(distribution, training_protocol, device)

    model.eval()
    with torch.inference_mode():
        outputs = model(**model_inputs(batch, device))
        tensors = {key: value.to(device) if isinstance(value, torch.Tensor) else value for key, value in batch.items()}
        losses = compute_masked_multitask_loss(
            outputs,
            tensors,
            loss_weights=training_protocol.loss_weights,
            class_weights=class_weights,
        )
    batch_sequence_length = int(batch["input_ids"].shape[1])
    if batch_sequence_length > MAX_LENGTH:
        raise AssertionError("collated sequence exceeds frozen max_length")
    expected_shapes = {
        "scope_logits": (len(batch["sample_ids"]), len(SCOPE_LABELS)),
        "structure_logits": (len(batch["sample_ids"]), len(STRUCTURE_LABELS)),
        "intent_logits": (len(batch["sample_ids"]), len(INTENT_LABELS)),
        "slot_logits": (len(batch["sample_ids"]), batch_sequence_length, len(SLOT_LABELS)),
        "negation_logits": (len(batch["sample_ids"]), len(NEGATION_LABELS)),
    }
    actual_shapes = {name: tuple(value.shape) for name, value in outputs.items()}
    if actual_shapes != expected_shapes:
        raise AssertionError(f"joint head shape mismatch: {actual_shapes}")
    if not all(math.isfinite(float(losses[name])) for name in ("scope_loss", "structure_loss", "intent_loss", "slot_loss", "negation_loss", "total_loss")):
        raise FloatingPointError("NON_FINITE_PREFLIGHT_LOSS")

    scope_probs = torch.softmax(outputs["scope_logits"], dim=-1).cpu()
    structure_probs = torch.softmax(outputs["structure_logits"], dim=-1).cpu()
    intent_probs = torch.softmax(outputs["intent_logits"], dim=-1).cpu()
    negation_probs = torch.softmax(outputs["negation_logits"], dim=-1).cpu()
    gold_slot_ids = batch["slot_labels"][0].tolist()
    predicted_slot_ids = [
        IGNORE_INDEX if gold == IGNORE_INDEX else int(predicted)
        for gold, predicted in zip(gold_slot_ids, outputs["slot_logits"].argmax(-1).cpu()[0].tolist(), strict=True)
    ]
    sample_id = batch["sample_ids"][0]
    schema_row = build_prediction_row(
        sample_id=sample_id,
        text=batch["texts"][0],
        record=records_by_id[sample_id],
        scope_probabilities=scope_probs[0],
        structure_probabilities=structure_probs[0],
        intent_probabilities=intent_probs[0],
        negation_probabilities=negation_probs[0],
        gold_slot_ids=gold_slot_ids,
        predicted_slot_ids=predicted_slot_ids,
        tokenizer=tokenizer,
    )
    final_digest = model_state_digest(model)
    gradients_created = any(parameter.grad is not None for parameter in model.parameters())
    if initial_digest != final_digest or gradients_created or trainer.training_steps_executed != 0:
        raise AssertionError("preflight changed parameters, created gradients, or executed a training step")
    masked_intent = int((batch["intent_labels"] == IGNORE_INDEX).sum())
    masked_negation = int((batch["negation_labels"] == IGNORE_INDEX).sum())
    if masked_intent == 0 or masked_negation == 0:
        raise AssertionError("preflight batch did not exercise masked sentence labels")
    if model.hidden_size != int(model.backbone.config.hidden_size) or model.hidden_size != 256:
        raise AssertionError("dynamic ELECTRA hidden size audit failed")

    return {
        "PREFLIGHT": "PASS",
        "experiment_absent": not EXPERIMENT_DIR.exists(),
        "model_provenance": provenance,
        "dataset_hash_verification": hash_report,
        "projection_failures": 0,
        "max_length": MAX_LENGTH,
        "preflight_batch_sequence_length": batch_sequence_length,
        "train_count": len(train_dataset),
        "validation_count": len(validation_dataset),
        "test_records_loaded": 0,
        "safety_gold_records_loaded": 0,
        "head_shapes": {name: list(shape) for name, shape in actual_shapes.items()},
        "dynamic_hidden_size": model.hidden_size,
        "sentence_representation": "last_hidden_state[:,0,:]",
        "slot_representation": "full_last_hidden_state",
        "loss_masking": {
            "intent_ignore_index_count": masked_intent,
            "negation_ignore_index_count": masked_negation,
            "losses_finite": True,
        },
        "single_optimizer_group": True,
        "optimizer_group_complete_coverage": True,
        "optimizer_group_parameter_count": sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad),
        "scheduler_base_lrs": list(map(float, trainer.scheduler.base_lrs)),
        "class_weight_tensor_shapes": {name: list(value.shape) if value is not None else None for name, value in class_weights.items()},
        "prediction_schema_valid": prediction_schema_ok(schema_row),
        "prediction_schema_fields": sorted(schema_row),
        "initialized_from_fixed_original_electra_snapshot": True,
        "initialized_from_rbt3_checkpoint": False,
        "initialized_from_previous_experiment_checkpoint": False,
        "initial_backbone_parameter_hashes": initial_backbone_hashes,
        "initial_joint_head_parameter_hashes": initial_head_hashes,
        "model_state_digest_before_forward_loss": initial_digest,
        "model_state_digest_after_forward_loss": final_digest,
        "model_parameters_unchanged": initial_digest == final_digest,
        "gradients_created": gradients_created,
        "TRAINING_STEPS_EXECUTED": trainer.training_steps_executed,
        "BACKWARD_PREFLIGHT_EXECUTED": False,
        "TEST_EVALUATION_EXECUTED": False,
        "SAFETY_GOLD_EVALUATION_EXECUTED": False,
        "python_executable": os.path.realpath(sys.executable),
    }


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
            "single_optimizer_parameter_group": True,
            "baseline_learning_rate_used": True,
            "effective_loss_weights": dict(LOSS_WEIGHTS),
        },
    )
    manifest = {
        "checkpoint_format": "PYTORCH_STATE_DICT",
        "checkpoint_kind": checkpoint_kind,
        "epoch": epoch,
        "BEST": best,
        "DEPLOYABLE": deployable,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "initialized_from_original_pretrained_electra": True,
        "continued_from_previous_checkpoint": False,
        "single_optimizer_parameter_group": True,
        "learning_rate": LEARNING_RATE,
        "effective_loss_weights": dict(LOSS_WEIGHTS),
        "dataset_version": training_protocol.dataset_version,
        "dataset_manifest_sha256": sha256_file(MANIFEST_PATH),
        "model_state_file": "model_state.pt",
        "model_state_sha256": sha256_file(state_path),
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


def tracked_abstention(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {row["sample_id"]: row for row in predictions}
    return {
        sample_id: {
            "sample_id": sample_id,
            "text": by_id[sample_id]["text"],
            "pred_scope": by_id[sample_id]["pred_scope"],
            "pred_structure": by_id[sample_id]["pred_structure"],
            "pred_intent": by_id[sample_id]["pred_intent"],
            "raw_abstain": by_id[sample_id]["raw_abstain"],
        }
        for sample_id in TRACKED_ABSTENTION_IDS
    }


def comparison_protocol_audit(training_protocol: TrainingProtocol) -> dict[str, Any]:
    rbt3 = read_json(RBT3_EXP001_DIR / "experiment_config.json")
    keys = (
        "seed",
        "selected_max_length",
        "baseline_learning_rate",
        "weight_decay",
        "warmup_ratio",
        "gradient_clip_norm",
        "baseline_epochs",
        "early_stopping_patience",
        "loss_weights",
        "class_weight_policy",
        "class_weight_cap",
        "quality_score_weights",
        "safety_gates",
    )
    electra = training_protocol.to_dict()
    checks = {key: electra[key] == rbt3[key] for key in keys}
    checks["actual_batch_size"] = BATCH_SIZE == rbt3["actual_batch_size"]
    return {
        "checks": checks,
        "all_protocol_fields_match": all(checks.values()),
        "COMPARISON_SEED_MATCH": "YES" if checks["seed"] else "NO",
    }


def comparison_markdown(summary: dict[str, Any], reporting: dict[str, Any]) -> str:
    rbt3 = read_json(RBT3_EXP001_DIR / "evaluation" / "validation" / "metrics.json")
    return f"""# RBT3 exp001 vs ELECTRA exp001

## 可比性

- 冻结数据、seed、max length、batch、单 LR、loss/class weights、quality score 与 safety gates：`{summary['PROTOCOL_MATCH_RBT3_EXP001']}`
- COMPARISON_SEED_MATCH=`{summary['COMPARISON_SEED_MATCH']}`
- Test evaluation：未执行
- Safety Gold evaluation：未执行

## Validation reporting checkpoint

| 指标 | RBT3 exp001 | ELECTRA exp001 |
|---|---:|---:|
| reporting epoch | {rbt3['epoch']} | {summary['REPORTING_EPOCH']} |
| checkpoint kind | closest safety diagnostic | {summary['REPORTING_CHECKPOINT_KIND']} |
| PRIMARY_QUALITY_SCORE | {rbt3['PRIMARY_QUALITY_SCORE']:.6f} | {reporting['PRIMARY_QUALITY_SCORE']:.6f} |
| intent macro F1 | {rbt3['intent']['macro_f1']:.6f} | {reporting['intent']['macro_f1']:.6f} |
| scope macro F1 | {rbt3['scope']['macro_f1']:.6f} | {reporting['scope']['macro_f1']:.6f} |
| structure macro F1 | {rbt3['structure']['macro_f1']:.6f} | {reporting['structure']['macro_f1']:.6f} |
| slot span F1 | {rbt3['slot']['OVERALL']['f1']:.6f} | {reporting['slot']['OVERALL']['f1']:.6f} |
| NEGATED F1 | {rbt3['negation']['per_class']['NEGATED']['f1']:.6f} | {reporting['negation']['per_class']['NEGATED']['f1']:.6f} |
| raw UFAR | {rbt3['safety']['UNSAFE_FALSE_ACCEPT_RATE']:.6f} | {reporting['safety']['UNSAFE_FALSE_ACCEPT_RATE']:.6f} |
| MULTI false accepts | {rbt3['safety']['per_category']['MULTI']['unsafe_false_accepts']} | {reporting['safety']['per_category']['MULTI']['unsafe_false_accepts']} |
| AMBIGUOUS false accepts | {rbt3['safety']['per_category']['AMBIGUOUS']['unsafe_false_accepts']} | {reporting['safety']['per_category']['AMBIGUOUS']['unsafe_false_accepts']} |

## 运行画像上下文

Stage 4A 的原始预训练 encoder CPU P95：RBT3 约 `7.883 ms`，ELECTRA-small 约 `14.785 ms`。这些数字不是本次微调模型的端到端运行时，不能直接当作部署时延。

## 工程解读

- ELECTRA exp001 通过冻结 safety gates；RBT3 exp001 因 1 个 AMBIGUOUS false accept 未通过。
- ELECTRA 的 intent 与 negation head 表现良好，但整体质量分低于 RBT3，主要差距来自 scope 与 slot。
- ELECTRA slot overall F1 为 `{reporting['slot']['OVERALL']['f1']:.6f}`，VALUE F1 为 `{reporting['slot']['VALUE']['f1']:.6f}`。模型并非全部预测 O，但属于严重 slot 欠拟合，应作为 backbone 路线决策的主要负面证据。
- ELECTRA UNKNOWN_CONTROL recall 为 `{reporting['scope']['per_class']['UNKNOWN_CONTROL']['recall']:.6f}`，并将 0748 错误判为可执行；通过当前冻结 gate 不等于不存在所有安全误放。

## 决策状态

- ELECTRA_EXP001_SAFETY_GATE_PASS=`{'YES' if summary['ELECTRA_EXP001_SAFETY_GATE_PASS'] else 'NO'}`
- ELECTRA_EXP001_BASELINE_HEALTHY=`{'YES' if summary['ELECTRA_EXP001_BASELINE_HEALTHY'] else 'NO'}`
- BACKBONE_COMPARISON_READY=`{'YES' if summary['BACKBONE_COMPARISON_READY'] else 'NO'}`
- READY_FOR_STAGE_4C_MODEL_DECISION=`{'YES' if summary['READY_FOR_STAGE_4C_MODEL_DECISION'] else 'NO'}`

## 附录：RBT3 exp002

RBT3 exp002 属于有限安全优化实验，采用不同 loss weights 与 discriminative LR，不进入本表的同协议 baseline 主比较。
"""


def summary_markdown(summary: dict[str, Any]) -> str:
    return f"""# SYS-014 Stage 4C-B ELECTRA exp001

- experiment: `{summary['EXPERIMENT_ID']}`
- model revision: `{summary['MODEL_REVISION']}`
- device: `{summary['TRAINING_DEVICE']}`
- trainable parameters: `{summary['TRAINABLE_PARAMETER_COUNT']}`
- epochs: `{summary['EPOCHS_COMPLETED']}`
- reporting checkpoint: `{summary['REPORTING_CHECKPOINT_KIND']}` epoch `{summary['REPORTING_EPOCH']}`
- training steps: `{summary['TRAINING_STEPS_EXECUTED']}`
- PRIMARY_QUALITY_SCORE: `{summary['PRIMARY_QUALITY_SCORE']:.6f}`
- raw UFAR: `{summary['RAW_VALIDATION_UFAR']:.6f}`
- AMBIGUOUS false accepts: `{summary['AMBIGUOUS_FALSE_ACCEPT_COUNT']}`
- MULTI false accepts: `{summary['MULTI_FALSE_ACCEPT_COUNT']}`
- slot collapse: `{summary['SLOT_COLLAPSE']}`
- boundary false rejects: `{summary['ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT']}`

ELECTRA_EXP001_SAFETY_GATE_PASS={'YES' if summary['ELECTRA_EXP001_SAFETY_GATE_PASS'] else 'NO'}

ELECTRA_EXP001_BASELINE_HEALTHY={'YES' if summary['ELECTRA_EXP001_BASELINE_HEALTHY'] else 'NO'}

BACKBONE_COMPARISON_READY={'YES' if summary['BACKBONE_COMPARISON_READY'] else 'NO'}

READY_FOR_STAGE_4C_MODEL_DECISION={'YES' if summary['READY_FOR_STAGE_4C_MODEL_DECISION'] else 'NO'}

TEST_EVALUATION_EXECUTED=NO

SAFETY_GOLD_EVALUATION_EXECUTED=NO
"""


def flatten_required_summary_fields(summary: dict[str, Any]) -> dict[str, Any]:
    """Expose every Stage 4C-B required final field without changing metrics."""
    result = dict(summary)
    metrics = result["SELECTED_VALIDATION_METRICS"]
    intent_per_class = metrics["intent"]["per_class"]
    per_intent_negation = metrics["per_intent_negation"]
    ambiguous = metrics["tracked_ambiguous_family"]
    abstention = metrics["tracked_abstention_examples"]
    result.update(
        {
            "PARAMETER_COUNT": result["TRAINABLE_PARAMETER_COUNT"],
            "VALIDATION_INTENT_PER_CLASS_F1": {
                label: intent_per_class[label]["f1"] for label in INTENT_LABELS
            },
            "UNKNOWN_CONTROL_RECALL": metrics["scope"]["per_class"]["UNKNOWN_CONTROL"]["recall"],
            "MULTI_RECALL": metrics["structure"]["per_class"]["MULTI"]["recall"],
            "AMBIGUOUS_RECALL": metrics["structure"]["per_class"]["AMBIGUOUS"]["recall"],
            "VALIDATION_SLOT_SPAN_F1": metrics["slot"]["OVERALL"]["f1"],
            "AREA_F1": metrics["slot"]["AREA"]["f1"],
            "VALUE_F1": metrics["slot"]["VALUE"]["f1"],
            "NEGATION_SPAN_F1": metrics["slot"]["NEGATION"]["f1"],
            "VALIDATION_NEGATION_F1": metrics["negation"]["per_class"]["NEGATED"]["f1"],
            "VALIDATION_NEGATED_RECALL": metrics["negation"]["per_class"]["NEGATED"]["recall"],
            "HEADLIGHT_OFF_NEGATED_RECALL": per_intent_negation["HEADLIGHT_OFF"]["per_class"]["NEGATED"]["recall"],
            "ACCELERATE_NEGATED_RECALL": per_intent_negation["ACCELERATE"]["per_class"]["NEGATED"]["recall"],
            "0731_FINAL_ABSTAIN": ambiguous["SYS014-POC-0731"]["raw_abstain"],
            "0732_FINAL_ABSTAIN": ambiguous["SYS014-POC-0732"]["raw_abstain"],
            "0733_FINAL_ABSTAIN": ambiguous["SYS014-POC-0733"]["raw_abstain"],
            "0748_FINAL_ABSTAIN": abstention["SYS014-POC-0748"]["raw_abstain"],
            "0762_FINAL_ABSTAIN": abstention["SYS014-POC-0762"]["raw_abstain"],
            "0773_FINAL_ABSTAIN": abstention["SYS014-POC-0773"]["raw_abstain"],
            "MACBERT_TRAINING_STARTED": False,
            "SLOT_SEVERE_UNDERPERFORMANCE": (
                metrics["slot"]["OVERALL"]["f1"] < 0.5
                or any(
                    metrics["slot"][entity]["f1"] == 0.0
                    for entity in ("AREA", "VALUE", "NEGATION")
                )
            ),
        }
    )
    return result


def refresh_existing_reports() -> int:
    summary_path = EXPERIMENT_DIR / "training_summary.json"
    if not summary_path.is_file():
        raise FileNotFoundError(f"Missing completed summary: {summary_path}")
    summary = flatten_required_summary_fields(read_json(summary_path))
    write_json(summary_path, summary)
    (EXPERIMENT_DIR / "training_summary.md").write_text(
        summary_markdown(summary), encoding="utf-8"
    )
    (EXPERIMENT_DIR / "rbt3_exp001_vs_electra_exp001.md").write_text(
        comparison_markdown(summary, summary["SELECTED_VALIDATION_METRICS"]),
        encoding="utf-8",
    )
    return 0


def run_training() -> int:
    preflight = run_preflight(require_experiment_absent=True)
    training_protocol = protocol()
    comparison_audit = comparison_protocol_audit(training_protocol)
    if not comparison_audit["all_protocol_fields_match"]:
        raise RuntimeError(f"RBT3_EXP001_PROTOCOL_MISMATCH: {comparison_audit}")
    set_deterministic_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_SNAPSHOT, local_files_only=True, use_fast=True)
    distribution, failures, _, validation_records, hash_report = data_context(tokenizer)
    if failures:
        raise RuntimeError(f"TOKEN_PROJECTION_FAILURES={len(failures)}")
    train_dataset = FrozenJointNLUDataset("train", tokenizer, max_length=MAX_LENGTH)
    validation_dataset = FrozenJointNLUDataset("validation", tokenizer, max_length=MAX_LENGTH)
    collator = JointNLUCollator(tokenizer)
    generator = torch.Generator().manual_seed(SEED)
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        generator=generator,
        collate_fn=collator,
    )
    validation_loader = DataLoader(validation_dataset, batch_size=BATCH_SIZE, shuffle=False, collate_fn=collator)
    records_by_id = {record["sample_id"]: record for record in validation_records}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = JointNLUModel(str(MODEL_SNAPSHOT)).to(device)
    initial_backbone_hashes = representative_parameter_hashes(model.backbone)
    initial_head_hashes = {
        name: representative_parameter_hashes(getattr(model, name))
        for name in ("scope_head", "structure_head", "intent_head", "slot_head", "negation_head")
    }
    trainable_parameter_count = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    total_steps = len(train_loader) * MAX_EPOCHS
    trainer = Stage4CTrainer(model, training_protocol, device=device, total_optimizer_steps=total_steps)
    class_weights = tensor_class_weights(distribution, training_protocol, device)
    create_experiment_directories()
    started_at = iso_now()
    config = {
        **training_protocol.to_dict(),
        "experiment_id": EXPERIMENT_ID,
        "actual_batch_size": BATCH_SIZE,
        "training_device": device.type.upper(),
        "single_optimizer_parameter_group": True,
        "discriminative_learning_rate": False,
        "total_optimizer_steps": total_steps,
        "warmup_steps": trainer.warmup_steps,
        "seed_controls": ["python_random", "numpy", "torch"],
        "COMPARISON_SEED_MATCH": comparison_audit["COMPARISON_SEED_MATCH"],
        "test_used_for_model_selection": False,
        "safety_gold_used_for_model_selection": False,
    }
    write_json(EXPERIMENT_DIR / "experiment_config.json", config)
    write_json(EXPERIMENT_DIR / "preflight.json", preflight)
    (EXPERIMENT_DIR / "training_log.jsonl").write_text("", encoding="utf-8")
    (EXPERIMENT_DIR / "metrics_by_epoch.jsonl").write_text("", encoding="utf-8")
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "status": "RUNNING",
        "dataset_version": training_protocol.dataset_version,
        "dataset_manifest_sha256": hash_report["dataset_manifest_sha256"],
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "model_weight_sha256": MODEL_WEIGHT_SHA256,
        "seed": SEED,
        "device": device.type.upper(),
        "cpu_model": cpu_name(),
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "python_executable": os.path.realpath(sys.executable),
        "git_commit": current_git_commit(),
        "started_at": started_at,
        "finished_at": None,
        "test_evaluation_executed": False,
        "safety_gold_evaluation_executed": False,
        "rbt3_training_started": False,
        "electra_exp002_started": False,
        "runtime_modified": False,
        "preflight": preflight,
    }
    write_json(EXPERIMENT_DIR / "manifest.json", manifest)
    append_jsonl(EXPERIMENT_DIR / "training_log.jsonl", {"event": "TRAINING_STARTED", "at": started_at, "config": config})

    started = time.perf_counter()
    history: list[dict[str, Any]] = []
    epoch_durations: list[float] = []
    best_metrics: dict[str, Any] | None = None
    best_epoch: int | None = None
    best_score = -1.0
    best_manifest: dict[str, Any] | None = None
    best_prediction: str | None = None
    closest_metrics: dict[str, Any] | None = None
    closest_epoch: int | None = None
    closest_ranking: tuple[int, int, int, float] | None = None
    closest_manifest: dict[str, Any] | None = None
    closest_prediction: str | None = None
    stale_epochs = 0
    non_finite = False

    try:
        for epoch in range(1, MAX_EPOCHS + 1):
            epoch_started = time.perf_counter()
            train_started = time.perf_counter()
            train_result = trainer.train_epoch(train_loader, class_weights=class_weights)
            train_seconds = time.perf_counter() - train_started
            validation_started = time.perf_counter()
            validation, predictions = evaluate_validation(
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
            validation["ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT"] = boundary["ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT"]
            validation["accelerate_boundary_probes"] = boundary
            validation["tracked_abstention_examples"] = tracked_abstention(predictions)
            validation["SLOT_COLLAPSE"] = validation["slot"]["OVERALL"]["f1"] == 0.0
            prediction_relative = f"evaluation/validation/epoch_{epoch:02d}_predictions.jsonl"
            write_jsonl(EXPERIMENT_DIR / prediction_relative, predictions)
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
                best_prediction = prediction_relative
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
                    closest_prediction = prediction_relative
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
            progress = {
                "epoch": epoch,
                "quality": score,
                "eligible": eligible,
                "ufar": validation["safety"]["UNSAFE_FALSE_ACCEPT_RATE"],
                "multi_false_accepts": validation["safety"]["per_category"]["MULTI"]["unsafe_false_accepts"],
                "ambiguous_false_accepts": validation["safety"]["per_category"]["AMBIGUOUS"]["unsafe_false_accepts"],
                "0731_raw_abstain": tracked["SYS014-POC-0731"]["raw_abstain"],
                "0732_raw_abstain": tracked["SYS014-POC-0732"]["raw_abstain"],
                "0733_raw_abstain": tracked["SYS014-POC-0733"]["raw_abstain"],
                "boundary_false_rejects": boundary["ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT"],
                "epoch_seconds": epoch_seconds,
                "training_steps": trainer.training_steps_executed,
            }
            print(json.dumps(progress, ensure_ascii=False), flush=True)
            append_jsonl(EXPERIMENT_DIR / "training_log.jsonl", {"event": "EPOCH_FINISHED", **progress})
            if best_metrics is not None and stale_epochs >= PATIENCE:
                append_jsonl(EXPERIMENT_DIR / "training_log.jsonl", {"event": "EARLY_STOPPING", "epoch": epoch, "stale_epochs": stale_epochs})
                break
    except FloatingPointError as exc:
        non_finite = True
        append_jsonl(EXPERIMENT_DIR / "training_log.jsonl", {"event": "TRAINING_ABORTED_NON_FINITE", "at": iso_now(), "error": str(exc)})

    total_training_seconds = time.perf_counter() - started
    if not history:
        raise RuntimeError("ELECTRA exp001 completed no Validation epoch")
    epochs_completed = len(history)
    last_metrics = history[-1]["validation"]
    last_prediction = history[-1]["prediction_artifact"]
    last_manifest = save_checkpoint(
        EXPERIMENT_DIR / "checkpoints" / "last",
        model,
        training_protocol,
        epoch=epochs_completed,
        metrics=last_metrics,
        checkpoint_kind="LAST_DIAGNOSTIC",
        prediction_artifact=last_prediction,
        best=False,
        deployable=False,
    )
    if best_metrics is None:
        (EXPERIMENT_DIR / "checkpoints" / "best" / "NO_ELIGIBLE_CHECKPOINT.md").write_text(
            "# No eligible checkpoint\n\nNo epoch passed every frozen safety gate.\n", encoding="utf-8"
        )
    if closest_manifest is None:
        (EXPERIMENT_DIR / "checkpoints" / "closest_safety_diagnostic" / "NO_NON_ELIGIBLE_EPOCH.md").write_text(
            "# No non-eligible epoch\n", encoding="utf-8"
        )
    else:
        (EXPERIMENT_DIR / "checkpoints" / "closest_safety_diagnostic" / "DIAGNOSTIC_ONLY.md").write_text(
            "# Diagnostic only\n\nBEST=false and DEPLOYABLE=false.\n", encoding="utf-8"
        )

    reporting = best_metrics if best_metrics is not None else closest_metrics
    reporting_epoch = best_epoch if best_epoch is not None else closest_epoch
    reporting_kind = "ELIGIBLE_BEST" if best_metrics is not None else "CLOSEST_SAFETY_DIAGNOSTIC"
    reporting_prediction = best_prediction if best_metrics is not None else closest_prediction
    if reporting is None or reporting_epoch is None or reporting_prediction is None:
        raise RuntimeError("no reporting checkpoint could be selected")
    write_jsonl(
        EXPERIMENT_DIR / "evaluation" / "validation" / "error_cases.jsonl",
        [{"reporting_epoch": reporting_epoch, **item} for item in reporting["error_cases"]],
    )
    write_json(
        EXPERIMENT_DIR / "evaluation" / "validation" / "reporting_metrics.json",
        {"epoch": reporting_epoch, "checkpoint_kind": reporting_kind, **reporting},
    )
    final_backbone_hashes = representative_parameter_hashes(model.backbone)
    pretrained_changed = initial_backbone_hashes != final_backbone_hashes
    task_metrics_finite = all(
        math.isfinite(float(value))
        for value in (
            reporting["intent"]["macro_f1"],
            reporting["scope"]["macro_f1"],
            reporting["structure"]["macro_f1"],
            reporting["slot"]["OVERALL"]["f1"],
            reporting["negation"]["per_class"]["NEGATED"]["f1"],
        )
    )
    artifacts_complete = all(
        (EXPERIMENT_DIR / record["prediction_artifact"]).is_file() for record in history
    )
    slot_collapse = bool(reporting["SLOT_COLLAPSE"])
    baseline_healthy = (
        not non_finite
        and task_metrics_finite
        and not slot_collapse
        and pretrained_changed
        and trainer.training_steps_executed > 0
        and artifacts_complete
    )
    comparison_ready = baseline_healthy and comparison_audit["all_protocol_fields_match"]
    ready_for_decision = comparison_ready
    safety = reporting["safety"]
    tracked = reporting["tracked_ambiguous_family"]
    summary = {
        "EXPERIMENT_ID": EXPERIMENT_ID,
        "MODEL_ID": MODEL_ID,
        "MODEL_REVISION": MODEL_REVISION,
        "MODEL_WEIGHT_SHA256": MODEL_WEIGHT_SHA256,
        "TRAINING_DEVICE": device.type.upper(),
        "TRAINABLE_PARAMETER_COUNT": trainable_parameter_count,
        "ACTUAL_BATCH_SIZE": BATCH_SIZE,
        "LEARNING_RATE": LEARNING_RATE,
        "OPTIMIZER_PARAMETER_GROUP_COUNT": 1,
        "LOSS_WEIGHTS": dict(LOSS_WEIGHTS),
        "MAX_EPOCHS": MAX_EPOCHS,
        "EPOCHS_COMPLETED": epochs_completed,
        "BEST_EPOCH": best_epoch,
        "REPORTING_EPOCH": reporting_epoch,
        "REPORTING_CHECKPOINT_KIND": reporting_kind,
        "REPORTING_PREDICTION_ARTIFACT": reporting_prediction,
        "TRAINING_STEPS_EXECUTED": trainer.training_steps_executed,
        "TOTAL_OPTIMIZER_STEPS_PLANNED": total_steps,
        "WARMUP_STEPS": trainer.warmup_steps,
        "EPOCH_DURATIONS_SECONDS": epoch_durations,
        "MEAN_EPOCH_SECONDS": sum(epoch_durations) / len(epoch_durations),
        "TOTAL_TRAINING_SECONDS": total_training_seconds,
        "PRIMARY_QUALITY_SCORE": reporting["PRIMARY_QUALITY_SCORE"],
        "VALIDATION_INTENT_MACRO_F1": reporting["intent"]["macro_f1"],
        "VALIDATION_INTENT_PER_CLASS": reporting["intent"]["per_class"],
        "VALIDATION_SCOPE_MACRO_F1": reporting["scope"]["macro_f1"],
        "VALIDATION_UNKNOWN_CONTROL_RECALL": reporting["scope"]["per_class"]["UNKNOWN_CONTROL"]["recall"],
        "VALIDATION_STRUCTURE_MACRO_F1": reporting["structure"]["macro_f1"],
        "VALIDATION_MULTI_RECALL": reporting["structure"]["per_class"]["MULTI"]["recall"],
        "VALIDATION_AMBIGUOUS_RECALL": reporting["structure"]["per_class"]["AMBIGUOUS"]["recall"],
        "VALIDATION_SLOT_METRICS": reporting["slot"],
        "SLOT_COLLAPSE": slot_collapse,
        "VALIDATION_NEGATION_METRICS": reporting["negation"],
        "VALIDATION_PER_INTENT_NEGATION": reporting["per_intent_negation"],
        "NEGATION_HEAD_SLOT_DISAGREEMENT_COUNT": reporting["NEGATION_HEAD_SLOT_DISAGREEMENT_COUNT"],
        "RAW_VALIDATION_UFAR": safety["UNSAFE_FALSE_ACCEPT_RATE"],
        "TOTAL_UNSAFE_FALSE_ACCEPT_COUNT": safety["unsafe_false_accepts"],
        "AMBIGUOUS_FALSE_ACCEPT_COUNT": safety["per_category"]["AMBIGUOUS"]["unsafe_false_accepts"],
        "MULTI_FALSE_ACCEPT_COUNT": safety["per_category"]["MULTI"]["unsafe_false_accepts"],
        "UNKNOWN_FALSE_ACCEPT_COUNT": safety["per_category"]["UNKNOWN_CONTROL"]["unsafe_false_accepts"],
        "NON_CONTROL_FALSE_ACCEPT_COUNT": safety["per_category"]["NON_CONTROL"]["unsafe_false_accepts"],
        "TRACKED_0731_0732_0733": {
            sample_id: {
                "scope": row["pred_scope"],
                "structure": row["pred_structure"],
                "intent": row["pred_intent"],
                "final_abstain": row["raw_abstain"],
            }
            for sample_id, row in tracked.items()
        },
        "TRACKED_UNKNOWN_NON_CONTROL": reporting["tracked_abstention_examples"],
        "TRACKED_NEGATION_CASES": reporting["tracked_negation_cases"],
        "ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT": reporting["ACCELERATE_BOUNDARY_FALSE_REJECT_COUNT"],
        "ACCELERATE_BOUNDARY_PROBES": reporting["accelerate_boundary_probes"],
        "BEST_CHECKPOINT_SAVED": best_manifest is not None,
        "BEST_CHECKPOINT_SHA256": best_manifest["model_state_sha256"] if best_manifest else None,
        "CLOSEST_SAFETY_DIAGNOSTIC_EPOCH": closest_epoch,
        "CLOSEST_SAFETY_DIAGNOSTIC_SHA256": closest_manifest["model_state_sha256"] if closest_manifest else None,
        "LAST_CHECKPOINT_SHA256": last_manifest["model_state_sha256"],
        "NON_FINITE_LOSS_DETECTED": non_finite,
        "PRETRAINED_WEIGHTS_CHANGED": pretrained_changed,
        "INITIAL_BACKBONE_PARAMETER_HASHES": initial_backbone_hashes,
        "INITIAL_JOINT_HEAD_PARAMETER_HASHES": initial_head_hashes,
        "FINAL_BACKBONE_PARAMETER_HASHES": final_backbone_hashes,
        "COMPARISON_SEED_MATCH": comparison_audit["COMPARISON_SEED_MATCH"],
        "PROTOCOL_MATCH_RBT3_EXP001": comparison_audit["all_protocol_fields_match"],
        "TEST_EVALUATION_EXECUTED": False,
        "SAFETY_GOLD_EVALUATION_EXECUTED": False,
        "RUNTIME_MODIFIED": False,
        "RBT3_EXP003_STARTED": False,
        "ELECTRA_EXP002_STARTED": False,
        "MACBERT_STARTED": False,
        "ELECTRA_EXP001_SAFETY_GATE_PASS": best_metrics is not None,
        "ELECTRA_EXP001_BASELINE_HEALTHY": baseline_healthy,
        "BACKBONE_COMPARISON_READY": comparison_ready,
        "READY_FOR_STAGE_4C_MODEL_DECISION": ready_for_decision,
        "SELECTED_VALIDATION_METRICS": reporting,
    }
    summary = flatten_required_summary_fields(summary)
    write_json(EXPERIMENT_DIR / "training_summary.json", summary)
    (EXPERIMENT_DIR / "training_summary.md").write_text(summary_markdown(summary), encoding="utf-8")
    (EXPERIMENT_DIR / "rbt3_exp001_vs_electra_exp001.md").write_text(
        comparison_markdown(summary, reporting), encoding="utf-8"
    )
    finished_at = iso_now()
    append_jsonl(
        EXPERIMENT_DIR / "training_log.jsonl",
        {"event": "TRAINING_FINISHED", "at": finished_at, "summary": {key: value for key, value in summary.items() if key != "SELECTED_VALIDATION_METRICS"}},
    )
    manifest.update(
        {
            "status": "COMPLETED_SAFETY_GATE_PASS" if best_metrics is not None else "COMPLETED_NO_ELIGIBLE_SAFETY_CHECKPOINT",
            "finished_at": finished_at,
            "training_duration_seconds": total_training_seconds,
            "rss_after_training_bytes": current_rss_bytes(),
            "epochs_completed": epochs_completed,
            "training_steps_executed": trainer.training_steps_executed,
            "best_epoch": best_epoch,
            "closest_safety_diagnostic_epoch": closest_epoch,
            "electra_exp001_safety_gate_pass": best_metrics is not None,
            "electra_exp001_baseline_healthy": baseline_healthy,
            "backbone_comparison_ready": comparison_ready,
            "ready_for_stage_4c_model_decision": ready_for_decision,
        }
    )
    write_json(EXPERIMENT_DIR / "manifest.json", manifest)
    print(json.dumps({key: value for key, value in summary.items() if key != "SELECTED_VALIDATION_METRICS"}, ensure_ascii=False, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--refresh-existing-reports", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.preflight_only:
        print(json.dumps(run_preflight(require_experiment_absent=True), ensure_ascii=False, indent=2))
        return 0
    if args.refresh_existing_reports:
        return refresh_existing_reports()
    return run_training()


if __name__ == "__main__":
    raise SystemExit(main())
