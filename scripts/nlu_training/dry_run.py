"""Stage 4B forward/loss-only validation; this module cannot train a model."""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch
from transformers import AutoTokenizer

from .collator import JointNLUCollator
from .dataset import (
    FrozenJointNLUDataset,
    project_all_records,
    select_max_length,
    token_length_distribution,
    training_record_distribution,
)
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
from .manifest import experiment_manifest
from .metrics import (
    classification_metrics,
    slot_span_metrics,
    unsafe_false_accept_metrics,
)
from .model import JointNLUModel, representative_parameter_hashes
from .train_config import (
    BASELINE_SEED,
    CPU_EPOCH_TIME_ESTIMATE,
    TrainingProtocol,
    primary_snapshot_path,
    repository_root,
)
from .validation import full_preflight, read_split


OUTPUT_DIR = repository_root() / "data" / "nlu" / "training_design"
TRAINING_STEPS_EXECUTED = 0
DRY_RUN_BATCH_SIZE = 16
DRY_RUN_TARGET_EXAMPLES = 32


def set_deterministic_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def weight_candidates(
    counts: dict[str, int], ordered_labels: tuple[str, ...]
) -> dict[str, Any]:
    result: dict[str, Any] = {"NONE": None}
    for policy in ("INVERSE_FREQ", "SQRT_INVERSE_FREQ"):
        try:
            result[policy] = class_weights_from_counts(
                counts, ordered_labels, policy=policy, cap=3.0
            )
        except ValueError as exc:
            result[policy] = {"status": "NOT_APPLICABLE", "reason": str(exc)}
    return result


def build_distribution_report(
    tokenizer: Any, *, selected_max_length: int
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    splits = {name: read_split(name) for name in ("train", "validation", "test")}
    all_records = [record for records in splits.values() for record in records]
    token_lengths = {
        name: token_length_distribution(records, tokenizer)
        for name, records in splits.items()
    }
    token_lengths["all"] = token_length_distribution(all_records, tokenizer)
    projection_failures: list[dict[str, Any]] = []
    slot_distributions: dict[str, dict[str, int]] = {}
    for name, records in splits.items():
        slot_counts, failures = project_all_records(
            records, tokenizer, max_length=selected_max_length
        )
        slot_distributions[name] = dict(sorted(slot_counts.items()))
        projection_failures.extend(
            [{"split": name, **failure.to_dict()} for failure in failures]
        )

    train_distribution = training_record_distribution(splits["train"])
    train_distribution["slot_token_labels"] = slot_distributions["train"]
    scope_counts = train_distribution["scope"]
    structure_counts = train_distribution["structure"]
    intent_counts = train_distribution["intent_eligible_only"]
    negation_counts = train_distribution["negation_eligible_only"]
    slot_counts = train_distribution["slot_token_labels"]
    train_distribution["class_weight_candidates"] = {
        "scope": weight_candidates(scope_counts, SCOPE_LABELS),
        "structure": weight_candidates(structure_counts, STRUCTURE_LABELS),
        "intent": weight_candidates(intent_counts, INTENT_LABELS),
        "slot": weight_candidates(slot_counts, SLOT_LABELS),
        "negation": weight_candidates(negation_counts, NEGATION_LABELS),
    }
    train_distribution["recommended_class_weight_policy"] = {
        "scope": "SQRT_INVERSE_FREQ",
        "structure": "SQRT_INVERSE_FREQ",
        "intent": "NONE",
        "slot": "NONE",
        "negation": "SQRT_INVERSE_FREQ",
        "cap": 3.0,
        "NO_INTENT_CLASS_WEIGHT_REQUIRED": True,
        "rationale": "Protect minority abstention/structure/negation classes without inverse-frequency extremes; intent is already near-balanced and slot uses span-level evaluation.",
    }
    return (
        {
            "dataset_version": "sys014-poc7-v2",
            "token_length_distribution": token_lengths,
            "MAX_TOKEN_LENGTH": token_lengths["all"]["max"],
            "SELECTED_MAX_LENGTH": selected_max_length,
            "truncation_policy": "NO_FROZEN_TEXT_TRUNCATED",
            "splits": {
                name: {"record_count": len(records), "slot_token_labels": slot_distributions[name]}
                for name, records in splits.items()
            },
            "train": train_distribution,
        },
        projection_failures,
    )


def select_dry_run_indices(records: list[dict[str, Any]]) -> list[int]:
    selected: list[int] = []
    covered_scope: set[str] = set()
    covered_structure: set[str] = set()
    covered_intent: set[str] = set()
    covered_negation: set[bool] = set()
    covered_slots: set[str] = set()
    required_slots = {"AREA", "VALUE", "NEGATION"}
    for index, record in enumerate(records):
        record_slots = {
            str(slot["slot_type"])
            for slot in record.get("slots", [])
            if slot.get("slot_type") in required_slots
        }
        contributes = (
            record["scope_label"] not in covered_scope
            or record["intent_structure"] not in covered_structure
            or (record.get("intent") is not None and record["intent"] not in covered_intent)
            or (isinstance(record.get("negated"), bool) and record["negated"] not in covered_negation)
            or bool(record_slots - covered_slots)
        )
        if not contributes:
            continue
        selected.append(index)
        covered_scope.add(record["scope_label"])
        covered_structure.add(record["intent_structure"])
        if record.get("intent") is not None:
            covered_intent.add(record["intent"])
        if isinstance(record.get("negated"), bool):
            covered_negation.add(record["negated"])
        covered_slots.update(record_slots)
    for index in range(len(records)):
        if len(selected) >= DRY_RUN_TARGET_EXAMPLES:
            break
        if index not in selected:
            selected.append(index)
    coverage = {
        "scope": covered_scope,
        "structure": covered_structure,
        "intent": covered_intent,
        "negation": covered_negation,
        "slots": covered_slots,
    }
    expected = {
        "scope": set(SCOPE_LABELS),
        "structure": set(STRUCTURE_LABELS),
        "intent": set(INTENT_LABELS),
        "negation": {False, True},
        "slots": required_slots,
    }
    if any(coverage[name] != expected[name] for name in expected):
        raise RuntimeError(f"Dry-run selection lacks label coverage: {coverage}")
    return selected


def tensor_class_weights(
    distribution: dict[str, Any], protocol: TrainingProtocol, device: torch.device
) -> dict[str, torch.Tensor | None]:
    counts = {
        "scope": distribution["train"]["scope"],
        "structure": distribution["train"]["structure"],
        "intent": distribution["train"]["intent_eligible_only"],
        "slot": distribution["train"]["slot_token_labels"],
        "negation": distribution["train"]["negation_eligible_only"],
    }
    labels = {
        "scope": SCOPE_LABELS,
        "structure": STRUCTURE_LABELS,
        "intent": INTENT_LABELS,
        "slot": SLOT_LABELS,
        "negation": NEGATION_LABELS,
    }
    result: dict[str, torch.Tensor | None] = {}
    for task, policy in protocol.class_weight_policy.items():
        values = class_weights_from_counts(
            counts[task], labels[task], policy=policy, cap=protocol.class_weight_cap
        )
        result[task] = (
            torch.tensor(values, dtype=torch.float32, device=device)
            if values is not None
            else None
        )
    return result


def chunks(values: list[int], size: int) -> Iterable[list[int]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


def run_model_dry_run(
    tokenizer: Any, distribution: dict[str, Any], *, max_length: int
) -> dict[str, Any]:
    protocol = TrainingProtocol(selected_max_length=max_length)
    device = torch.device("cpu")
    dataset = FrozenJointNLUDataset("train", tokenizer, max_length=max_length)
    selected_indices = select_dry_run_indices(dataset.records)
    collator = JointNLUCollator(tokenizer)
    set_deterministic_seed(protocol.seed)
    model = JointNLUModel(str(primary_snapshot_path())).to(device).eval()
    before_backbone = representative_parameter_hashes(model.backbone)
    before_all = representative_parameter_hashes(model)
    class_weights = tensor_class_weights(distribution, protocol, device)

    expected_shapes = {
        "scope_logits": (len(SCOPE_LABELS),),
        "structure_logits": (len(STRUCTURE_LABELS),),
        "intent_logits": (len(INTENT_LABELS),),
        "slot_logits": (len(SLOT_LABELS),),
        "negation_logits": (len(NEGATION_LABELS),),
    }
    batch_reports: list[dict[str, Any]] = []
    aggregate_losses: Counter[str] = Counter()
    aggregate_counts: Counter[str] = Counter()
    all_scope_true: list[int] = []
    all_structure_true: list[int] = []
    all_intent_true: list[int] = []
    all_negation_true: list[int] = []
    all_slot_true: list[list[int]] = []
    all_scope_pred: list[int] = []
    all_structure_pred: list[int] = []
    all_intent_pred: list[int] = []
    all_negation_pred: list[int] = []
    all_slot_pred: list[list[int]] = []
    shapes_valid = True

    with torch.inference_mode():
        for batch_number, indices in enumerate(chunks(selected_indices, DRY_RUN_BATCH_SIZE), start=1):
            batch = collator([dataset[index] for index in indices])
            tensor_batch = {
                key: value.to(device) if isinstance(value, torch.Tensor) else value
                for key, value in batch.items()
            }
            outputs = model(
                input_ids=tensor_batch["input_ids"],
                attention_mask=tensor_batch.get("attention_mask"),
                token_type_ids=tensor_batch.get("token_type_ids"),
            )
            losses = compute_masked_multitask_loss(
                outputs,
                tensor_batch,
                loss_weights=protocol.loss_weights,
                class_weights=class_weights,
            )
            shape_report = {name: list(value.shape) for name, value in outputs.items()}
            batch_size = len(indices)
            for name, suffix in expected_shapes.items():
                actual = tuple(outputs[name].shape)
                expected = (
                    (batch_size, int(tensor_batch["input_ids"].shape[1]), suffix[0])
                    if name == "slot_logits"
                    else (batch_size, suffix[0])
                )
                shapes_valid = shapes_valid and actual == expected
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
                raise RuntimeError(f"Non-finite dry-run loss: {scalar_losses}")
            aggregate_losses.update(scalar_losses)
            aggregate_counts.update(losses["supervised_counts"])
            batch_reports.append(
                {
                    "batch": batch_number,
                    "sample_ids": batch["sample_ids"],
                    "logit_shapes": shape_report,
                    "losses": scalar_losses,
                    "supervised_counts": losses["supervised_counts"],
                }
            )
            all_scope_true.extend(tensor_batch["scope_labels"].cpu().tolist())
            all_structure_true.extend(tensor_batch["structure_labels"].cpu().tolist())
            all_intent_true.extend(tensor_batch["intent_labels"].cpu().tolist())
            all_negation_true.extend(tensor_batch["negation_labels"].cpu().tolist())
            all_slot_true.extend(tensor_batch["slot_labels"].cpu().tolist())
            all_scope_pred.extend(outputs["scope_logits"].argmax(-1).cpu().tolist())
            all_structure_pred.extend(outputs["structure_logits"].argmax(-1).cpu().tolist())
            all_intent_pred.extend(outputs["intent_logits"].argmax(-1).cpu().tolist())
            all_negation_pred.extend(outputs["negation_logits"].argmax(-1).cpu().tolist())
            all_slot_pred.extend(outputs["slot_logits"].argmax(-1).cpu().tolist())

    after_backbone = representative_parameter_hashes(model.backbone)
    after_all = representative_parameter_hashes(model)
    unchanged = before_backbone == after_backbone and before_all == after_all
    eligible_intent = [index for index, label in enumerate(all_intent_true) if label != IGNORE_INDEX]
    eligible_negation = [
        index for index, label in enumerate(all_negation_true) if label != IGNORE_INDEX
    ]
    diagnostic_metrics = {
        "warning": "RANDOM_HEAD_DRY_RUN_DIAGNOSTIC_ONLY_NOT_MODEL_QUALITY",
        "scope": classification_metrics(
            all_scope_true, all_scope_pred, label_names=SCOPE_LABELS
        ),
        "structure": classification_metrics(
            all_structure_true, all_structure_pred, label_names=STRUCTURE_LABELS
        ),
        "intent": classification_metrics(
            [all_intent_true[index] for index in eligible_intent],
            [all_intent_pred[index] for index in eligible_intent],
            label_names=INTENT_LABELS,
        ),
        "negation": classification_metrics(
            [all_negation_true[index] for index in eligible_negation],
            [all_negation_pred[index] for index in eligible_negation],
            label_names=NEGATION_LABELS,
        ),
        "slot": slot_span_metrics(all_slot_true, all_slot_pred),
        "ufar": unsafe_false_accept_metrics(
            true_scope=all_scope_true,
            true_structure=all_structure_true,
            pred_scope=all_scope_pred,
            pred_structure=all_structure_pred,
            pred_intent=all_intent_pred,
        ),
    }
    batch_count = len(batch_reports)
    mean_losses = {
        name: round(total / batch_count, 8) for name, total in aggregate_losses.items()
    }
    expected_intent_count = sum(
        record["scope_label"] == "IN_SCOPE_CONTROL"
        and record["intent_structure"] == "SINGLE"
        and record["intent"] is not None
        for record in (dataset.records[index] for index in selected_indices)
    )
    expected_negation_count = sum(
        record["scope_label"] == "IN_SCOPE_CONTROL"
        and record["intent_structure"] == "SINGLE"
        and isinstance(record["negated"], bool)
        for record in (dataset.records[index] for index in selected_indices)
    )
    masks_valid = (
        aggregate_counts["scope"] == len(selected_indices)
        and aggregate_counts["structure"] == len(selected_indices)
        and aggregate_counts["intent"] == expected_intent_count
        and aggregate_counts["negation"] == expected_negation_count
    )
    return {
        "mode": "FORWARD_LOSS_ONLY",
        "device": str(device),
        "model_id": protocol.model_id,
        "model_revision": protocol.model_revision,
        "local_backbone_path": str(primary_snapshot_path()),
        "joint_head_parameters": model.joint_head_parameter_count(),
        "DRY_RUN_BATCHES": batch_count,
        "dry_run_examples": len(selected_indices),
        "batch_size": DRY_RUN_BATCH_SIZE,
        "logit_shapes_valid": shapes_valid,
        "loss_masks_valid": masks_valid,
        "losses_mean_across_batches": mean_losses,
        "all_losses_finite": all(math.isfinite(value) for value in mean_losses.values()),
        "supervised_counts": {
            "SCOPE_SUPERVISED": aggregate_counts["scope"],
            "STRUCTURE_SUPERVISED": aggregate_counts["structure"],
            "INTENT_SUPERVISED": aggregate_counts["intent"],
            "NEGATION_SUPERVISED": aggregate_counts["negation"],
            "SLOT_SUPERVISED_TOKENS": aggregate_counts["slot_tokens"],
        },
        "batch_reports": batch_reports,
        "metric_input_preparation": diagnostic_metrics,
        "parameter_hashes_before": {"backbone": before_backbone, "all": before_all},
        "parameter_hashes_after": {"backbone": after_backbone, "all": after_all},
        "PRETRAINED_WEIGHTS_UNCHANGED": unchanged,
        "TRAINING_STEPS_EXECUTED": TRAINING_STEPS_EXECUTED,
        "CPU_EPOCH_TIME_ESTIMATE": CPU_EPOCH_TIME_ESTIMATE,
        "experiment_manifest_preview": experiment_manifest(protocol, device=str(device)),
    }


def training_protocol_markdown(protocol: TrainingProtocol, distribution: dict[str, Any]) -> str:
    return f"""# SYS-014 Stage 4B 冻结训练协议

## 输入与模型

- dataset：`sys014-poc7-v2`，仅 train/validation/test；Safety Gold 只校验完整性。
- primary backbone：`{protocol.model_id}` @ `{protocol.model_revision}`。
- device：device-agnostic、CPU-capable、GPU-preferred。
- max_length：`{distribution['SELECTED_MAX_LENGTH']}`；全量最大 token length=`{distribution['MAX_TOKEN_LENGTH']}`，无截断。
- baseline seed：`{protocol.seed}`；最终主结果建议至少 3 seeds。

## Loss 与类别不平衡

`L_total = L_scope + L_structure + L_intent(masked) + L_slot(masked) + L_negation(masked)`。五项 baseline 权重均为 1.0，这是 mean-reduced CE 的工程初值，不宣称最优。

Scope/Structure/Negation 使用均值归一、cap=3 的 `SQRT_INVERSE_FREQ`；Intent/Slot 使用 `NONE`。`NO_INTENT_CLASS_WEIGHT_REQUIRED = YES`。Stage 4C 只允许比较 NONE/INVERSE_FREQ/SQRT_INVERSE_FREQ，禁止 Safety Gold 调权。

## Stage 4C 候选

- AdamW；baseline LR=2e-5；候选仅 1e-5/2e-5/3e-5/5e-5。
- CPU batch=16；CUDA batch=32，可因内存下调。
- baseline epoch=10；候选 5–15；validation early stopping patience=3。
- `CPU_EPOCH_TIME_ESTIMATE = NOT_MEASURED`：未执行 backward 或 parameter update，不从 forward 延迟伪推训练时间。

## Best checkpoint 协议

`PRIMARY_QUALITY_SCORE = 0.30 Intent Macro F1 + 0.20 Scope Macro F1 + 0.20 Structure Macro F1 + 0.20 Slot Span F1 + 0.10 Negation F1`。

候选 checkpoint 还必须满足 validation：UFAR<=5%、MULTI false accept=0、AMBIGUOUS false accept=0。Safety Gold 不参与训练、early stopping、阈值、loss、超参数或 checkpoint 选择。

## 实验目录

每个 Stage 4C experiment 必须含 experiment_config、metrics、training_log、checkpoints、evaluation、manifest，并记录 dataset/manifest hash、registry、model revision、seed、hyperparameters、Git commit、device 和 Torch version。
"""


def metric_spec_markdown() -> str:
    return """# SYS-014 Stage 4B 指标规范

## Intent

仅 `SINGLE + IN_SCOPE_CONTROL + intent!=null`：accuracy、macro precision/recall/F1、per-class P/R/F1、confusion matrix。重点观察 WINDOW_OPEN↔WINDOW_SET_POSITION、DOOR_OPEN↔DOOR_CLOSE。

## Scope / Structure

Scope 报告 macro P/R/F1 与 per-class 指标，重点 UNKNOWN_CONTROL recall。Structure 报告 macro F1、MULTI recall、AMBIGUOUS recall。

## Slot / Negation

Slot 采用精确 token-span 的 AREA/VALUE/NEGATION 与 overall precision/recall/F1，不用 token accuracy 替代。Negation 仅 eligible SINGLE，报告 accuracy/P/R/F1 与 NEGATED recall；无样本项为 `NOT_ESTIMABLE`。

## Safety

`UFAR = unsafe_false_accepts / total_should_abstain`。should-abstain 包括 NON_CONTROL、UNKNOWN_CONTROL、AMBIGUOUS_CONTROL、MULTI、AMBIGUOUS；预测路径只有同时产生 IN_SCOPE_CONTROL + SINGLE + 7-Intent 才视为可执行。分别报告五类 false accept。

Primary quality score 与 safety gates 独立：未通过 UFAR/MULTI/AMBIGUOUS validation gate 的 checkpoint 不得成为 best。Safety Gold 仅在选择全部结束后做独立回归。

## Legacy baseline adapter

后续离线 adapter 在同一 frozen test 上将 Legacy action-target 映射到公平可比的 7-Intent 子集，比较 correctness、negation、MULTI/OOD fail-close 和 latency；不得修改 runtime parser。
"""


def readiness_markdown(
    preflight: dict[str, Any],
    distribution: dict[str, Any],
    projection_failures: list[dict[str, Any]],
    dry_run: dict[str, Any],
) -> str:
    ready = (
        preflight["hash_verification"]["DATASET_HASH_VERIFIED"]
        and preflight["official_validator"]["validation_failures"] == 0
        and not projection_failures
        and dry_run["logit_shapes_valid"]
        and dry_run["loss_masks_valid"]
        and dry_run["all_losses_finite"]
        and dry_run["PRETRAINED_WEIGHTS_UNCHANGED"]
        and dry_run["TRAINING_STEPS_EXECUTED"] == 0
    )
    losses = dry_run["losses_mean_across_batches"]
    counts = dry_run["supervised_counts"]
    return f"""# SYS-014 Stage 4B Readiness Report

- `DATASET_HASH_VERIFIED = {'YES' if preflight['hash_verification']['DATASET_HASH_VERIFIED'] else 'NO'}`
- `TOKEN_PROJECTION_FAILURES = {len(projection_failures)}`
- `MAX_TOKEN_LENGTH = {distribution['MAX_TOKEN_LENGTH']}`
- `SELECTED_MAX_LENGTH = {distribution['SELECTED_MAX_LENGTH']}`
- `PRIMARY_BACKBONE = hfl/rbt3`
- `JOINT_HEAD_PARAMETERS = {dry_run['joint_head_parameters']}`
- `DRY_RUN_BATCHES = {dry_run['DRY_RUN_BATCHES']}`
- `SCOPE_SUPERVISED = {counts['SCOPE_SUPERVISED']}`
- `STRUCTURE_SUPERVISED = {counts['STRUCTURE_SUPERVISED']}`
- `INTENT_SUPERVISED = {counts['INTENT_SUPERVISED']}`
- `NEGATION_SUPERVISED = {counts['NEGATION_SUPERVISED']}`
- `SLOT_SUPERVISED_TOKENS = {counts['SLOT_SUPERVISED_TOKENS']}`

Dry-run mean losses：scope={losses['scope_loss']:.6f}、structure={losses['structure_loss']:.6f}、intent={losses['intent_loss']:.6f}、slot={losses['slot_loss']:.6f}、negation={losses['negation_loss']:.6f}、total={losses['total_loss']:.6f}；全部 finite。

- `CPU_EPOCH_TIME_ESTIMATE = NOT_MEASURED`
- `TRAINING_STEPS_EXECUTED = 0`
- `PRETRAINED_WEIGHTS_UNCHANGED = {'YES' if dry_run['PRETRAINED_WEIGHTS_UNCHANGED'] else 'NO'}`
- `TRAINING_PROTOCOL_FROZEN = {'YES' if ready else 'NO'}`
- `TRAINING_PIPELINE_READY = {'YES' if ready else 'NO'}`
- `METRICS_READY = {'YES' if ready else 'NO'}`
- `READY_FOR_STAGE_4C_RBT3_TRAINING = {'YES' if ready else 'NO'}`
- `READY_FOR_MODEL_TRAINING = {'YES' if ready else 'NO'}`

Stage 4B 自身未训练、未生成正式 checkpoint、未修改 runtime/Legacy Parser/frozen v2。`READY_FOR_MODEL_TRAINING=YES` 只授权后续 Stage 4C 按冻结协议启动。
"""


def main() -> int:
    set_deterministic_seed(BASELINE_SEED)
    preflight = full_preflight()
    snapshot = primary_snapshot_path()
    if not snapshot.is_dir():
        raise FileNotFoundError(f"Pinned RBT3 snapshot missing: {snapshot}")
    tokenizer = AutoTokenizer.from_pretrained(snapshot, local_files_only=True, use_fast=True)
    all_records = [
        record
        for split in ("train", "validation", "test")
        for record in read_split(split)
    ]
    length_report = token_length_distribution(all_records, tokenizer)
    selected_max_length = select_max_length(int(length_report["max"]))
    distribution, projection_failures = build_distribution_report(
        tokenizer, selected_max_length=selected_max_length
    )
    dry_run = run_model_dry_run(
        tokenizer, distribution, max_length=selected_max_length
    )
    protocol = TrainingProtocol(selected_max_length=selected_max_length)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "label_mapping.json").write_text(
        json.dumps(label_mapping_report(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "train_distribution.json").write_text(
        json.dumps(distribution, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    dry_run["preflight"] = preflight
    dry_run["TOKEN_PROJECTION_FAILURES"] = len(projection_failures)
    dry_run["projection_failures"] = projection_failures
    (OUTPUT_DIR / "dry_run_report.json").write_text(
        json.dumps(dry_run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "training_protocol.md").write_text(
        training_protocol_markdown(protocol, distribution), encoding="utf-8"
    )
    (OUTPUT_DIR / "metric_spec.md").write_text(metric_spec_markdown(), encoding="utf-8")
    readiness = readiness_markdown(preflight, distribution, projection_failures, dry_run)
    (OUTPUT_DIR / "stage4b_readiness_report.md").write_text(readiness, encoding="utf-8")
    print(
        json.dumps(
            {
                "DATASET_HASH_VERIFIED": preflight["hash_verification"]["DATASET_HASH_VERIFIED"],
                "TOKEN_PROJECTION_FAILURES": len(projection_failures),
                "MAX_TOKEN_LENGTH": distribution["MAX_TOKEN_LENGTH"],
                "SELECTED_MAX_LENGTH": selected_max_length,
                "DRY_RUN_BATCHES": dry_run["DRY_RUN_BATCHES"],
                "TRAINING_STEPS_EXECUTED": TRAINING_STEPS_EXECUTED,
                "PRETRAINED_WEIGHTS_UNCHANGED": dry_run["PRETRAINED_WEIGHTS_UNCHANGED"],
                "CPU_EPOCH_TIME_ESTIMATE": CPU_EPOCH_TIME_ESTIMATE,
                "output_dir": str(OUTPUT_DIR),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
