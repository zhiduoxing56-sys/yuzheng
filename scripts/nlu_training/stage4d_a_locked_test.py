"""SYS-014 Stage 4D-A: one-time locked Test evaluation.

The preflight path never parses Test records or sends Test text to the model.  The
formal path opens the frozen Test exactly once, performs one forward-only dataset
pass, and permanently records that the locked Test has been opened.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import torch
import transformers
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from .collator import JointNLUCollator
from .dataset import encode_record
from .labels import (
    IGNORE_INDEX,
    INTENT_LABELS,
    NEGATION_LABELS,
    SCOPE_LABELS,
    SLOT_LABELS,
    STRUCTURE_LABELS,
    label_mapping_report,
)
from .metrics import (
    classification_metrics,
    extract_bio_spans,
    primary_quality_score,
    safety_gate_passes,
    slot_span_metrics,
    unsafe_false_accept_metrics,
)
from .model import JointNLUModel
from .stage4c_electra_exp001 import MODEL_SNAPSHOT, candidate_provenance, model_inputs
from .stage4c_exp002 import build_prediction_row
from .train_config import repository_root
from .validation import DATASET_DIR, MANIFEST_PATH, read_split, sha256_file


ROOT = repository_root()
MODEL_ID = "hfl/chinese-electra-180g-small-discriminator"
MODEL_REVISION = "826a243f3f387450ef8d70de9c3d0706d8d8e924"
EXPERIMENT_ID = "sys014-poc7-electra-exp002"
LOCKED_EPOCH = 9
LOCKED_STATE_SHA256 = "dc2670a0351a219f71ba728f805242393769af8c1564bc4eb3f224f795444f68"
DATASET_MANIFEST_SHA256 = "122621c0ce5e7a6fbaadbbe97cb3e7e86a32812ee1c69fe5ee27c45d94ac8d42"
TEST_SHA256 = "813465b8b3667a74c99c519bab85baf1e38e09388979a77ce95d7cb7b99e9d29"
MAX_LENGTH = 32
BATCH_SIZE = 16

EXPERIMENT_DIR = ROOT / "data" / "nlu" / "experiments" / EXPERIMENT_ID
CHECKPOINT_DIR = EXPERIMENT_DIR / "checkpoints" / "best"
CHECKPOINT_STATE = CHECKPOINT_DIR / "model_state.pt"
OUTPUT_DIR = (
    ROOT / "data" / "nlu" / "final_evaluation" / "sys014-electra-exp002-epoch9"
)
TEST_OUTPUT_DIR = OUTPUT_DIR / "test"
FINAL_DECISION_PATH = (
    ROOT
    / "data"
    / "nlu"
    / "model_selection"
    / "stage4c_final"
    / "model_selection_decision.json"
)
TEST_PATH = DATASET_DIR / "test.jsonl"


def iso_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_jsonl(path: Path, values: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False) + "\n")


def state_dict_digest(model: torch.nn.Module) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        digest.update(name.encode("utf-8"))
        digest.update(value.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def tree_digest(root: Path) -> dict[str, Any]:
    suffixes = {".py", ".json", ".yaml", ".yml", ".toml"}
    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in suffixes
    )
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return {"root": str(root), "file_count": len(files), "sha256": digest.hexdigest()}


def tokenizer_hash_audit() -> dict[str, Any]:
    matrix = read_json(ROOT / "data" / "nlu" / "model_selection" / "candidate_matrix.json")
    candidate = next(row for row in matrix["candidates"] if row["model_id"] == MODEL_ID)
    assert candidate["revision"] == MODEL_REVISION
    rows: list[dict[str, Any]] = []
    for item in candidate["tokenizer_files"]:
        path = MODEL_SNAPSHOT / item["name"]
        actual = sha256_file(path)
        if actual != item["sha256"]:
            raise RuntimeError(f"TOKENIZER_HASH_MISMATCH:{item['name']}")
        rows.append(
            {
                "file": item["name"],
                "expected_sha256": item["sha256"],
                "actual_sha256": actual,
                "pass": True,
            }
        )
    return {
        "model_revision": candidate["revision"],
        "snapshot_path": str(MODEL_SNAPSHOT),
        "tokenizer_fast_expected": candidate["tokenizer_fast"],
        "verified_files": rows,
        "pass": True,
    }


def run_preflight() -> tuple[dict[str, Any], JointNLUModel, Any, torch.device, str]:
    if OUTPUT_DIR.exists():
        raise FileExistsError(
            f"LOCKED_TEST_OUTPUT_ALREADY_EXISTS; refusing any Test reopen: {OUTPUT_DIR}"
        )

    checkpoint_manifest = read_json(CHECKPOINT_DIR / "checkpoint_manifest.json")
    model_config = read_json(CHECKPOINT_DIR / "model_config.json")
    training_config = read_json(CHECKPOINT_DIR / "training_config.json")
    checkpoint_labels = read_json(CHECKPOINT_DIR / "label_mapping.json")
    experiment_config = read_json(EXPERIMENT_DIR / "experiment_config.json")
    experiment_manifest = read_json(EXPERIMENT_DIR / "manifest.json")
    training_summary = read_json(EXPERIMENT_DIR / "training_summary.json")
    final_decision = read_json(FINAL_DECISION_PATH)
    dataset_manifest = read_json(MANIFEST_PATH)

    actual_checkpoint_sha = sha256_file(CHECKPOINT_STATE)
    actual_manifest_sha = sha256_file(MANIFEST_PATH)
    actual_test_sha = sha256_file(TEST_PATH)
    if actual_checkpoint_sha != LOCKED_STATE_SHA256:
        raise RuntimeError("LOCKED_CHECKPOINT_SHA256_MISMATCH")
    if checkpoint_manifest["model_state_sha256"] != LOCKED_STATE_SHA256:
        raise RuntimeError("CHECKPOINT_MANIFEST_STATE_SHA256_MISMATCH")
    if actual_manifest_sha != DATASET_MANIFEST_SHA256:
        raise RuntimeError("FROZEN_DATASET_MANIFEST_SHA256_MISMATCH")
    if checkpoint_manifest["dataset_manifest_sha256"] != actual_manifest_sha:
        raise RuntimeError("CHECKPOINT_DATASET_MANIFEST_SHA256_MISMATCH")
    if dataset_manifest["file_sha256"]["test.jsonl"] != TEST_SHA256:
        raise RuntimeError("FROZEN_MANIFEST_TEST_SHA256_MISMATCH")
    if actual_test_sha != TEST_SHA256:
        raise RuntimeError("FROZEN_TEST_SHA256_MISMATCH")
    if dataset_manifest["immutable"] is not True:
        raise RuntimeError("FROZEN_DATASET_NOT_IMMUTABLE")

    expected_model_fields = {
        "model_id": MODEL_ID,
        "backbone_revision": MODEL_REVISION,
        "hidden_size": 256,
        "sentence_representation": "FIRST_TOKEN",
        "slot_representation": "FULL_LAST_HIDDEN_STATE",
    }
    for key, expected in expected_model_fields.items():
        if model_config[key] != expected:
            raise RuntimeError(f"LOCKED_MODEL_CONFIG_MISMATCH:{key}")
    if training_config["model_id"] != MODEL_ID:
        raise RuntimeError("LOCKED_TRAINING_CONFIG_MODEL_ID_MISMATCH")
    if training_config["model_revision"] != MODEL_REVISION:
        raise RuntimeError("LOCKED_TRAINING_CONFIG_REVISION_MISMATCH")
    if training_config["selected_max_length"] != MAX_LENGTH:
        raise RuntimeError("LOCKED_MAX_LENGTH_MISMATCH")
    if checkpoint_labels != label_mapping_report():
        raise RuntimeError("LOCKED_LABEL_MAPPING_MISMATCH")

    if checkpoint_manifest["epoch"] != LOCKED_EPOCH:
        raise RuntimeError("LOCKED_EPOCH_MISMATCH")
    if checkpoint_manifest["checkpoint_kind"] != "ELIGIBLE_BEST":
        raise RuntimeError("LOCKED_CHECKPOINT_KIND_MISMATCH")
    if checkpoint_manifest["model_id"] != MODEL_ID:
        raise RuntimeError("LOCKED_CHECKPOINT_MODEL_ID_MISMATCH")
    if checkpoint_manifest["model_revision"] != MODEL_REVISION:
        raise RuntimeError("LOCKED_CHECKPOINT_REVISION_MISMATCH")
    if final_decision["PROVISIONAL_FINAL_EXPERIMENT"] != EXPERIMENT_ID:
        raise RuntimeError("STAGE4C_FINAL_EXPERIMENT_MISMATCH")
    if final_decision["PROVISIONAL_FINAL_EPOCH"] != LOCKED_EPOCH:
        raise RuntimeError("STAGE4C_FINAL_EPOCH_MISMATCH")
    if final_decision["PROVISIONAL_FINAL_CHECKPOINT_SHA256"] != LOCKED_STATE_SHA256:
        raise RuntimeError("STAGE4C_FINAL_CHECKPOINT_SHA256_MISMATCH")

    test_provenance_checks = {
        "experiment_config_test_used_for_model_selection_false": experiment_config[
            "test_used_for_model_selection"
        ]
        is False,
        "experiment_manifest_test_evaluation_false": experiment_manifest[
            "test_evaluation_executed"
        ]
        is False,
        "experiment_preflight_test_records_loaded_zero": experiment_manifest[
            "preflight"
        ]["test_records_loaded"]
        == 0,
        "training_summary_test_evaluation_false": training_summary[
            "TEST_EVALUATION_EXECUTED"
        ]
        is False,
        "checkpoint_manifest_test_evaluation_false": checkpoint_manifest[
            "test_evaluation_executed"
        ]
        is False,
        "stage4c_decision_test_evaluation_no": final_decision[
            "TEST_EVALUATION_EXECUTED"
        ]
        == "NO",
    }
    if not all(test_provenance_checks.values()):
        raise RuntimeError(f"TEST_PROVENANCE_PREFLIGHT_FAIL:{test_provenance_checks}")

    runtime_history_checks = {
        "experiment_manifest_runtime_modified_false": experiment_manifest[
            "runtime_modified"
        ]
        is False,
        "training_summary_runtime_modified_false": training_summary["RUNTIME_MODIFIED"]
        is False,
    }
    if not all(runtime_history_checks.values()):
        raise RuntimeError(f"RUNTIME_HISTORY_PREFLIGHT_FAIL:{runtime_history_checks}")
    runtime_before = tree_digest(ROOT / "backend" / "app")

    provenance = candidate_provenance()
    tokenizer_audit = tokenizer_hash_audit()
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_SNAPSHOT, local_files_only=True, use_fast=True
    )
    if not tokenizer.is_fast:
        raise RuntimeError("FAST_TOKENIZER_REQUIRED")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = JointNLUModel(str(MODEL_SNAPSHOT)).to(device)
    state = torch.load(CHECKPOINT_STATE, map_location=device, weights_only=True)
    incompatible = model.load_state_dict(state, strict=True)
    if incompatible.missing_keys or incompatible.unexpected_keys:
        raise RuntimeError(f"LOCKED_STATE_DICT_INCOMPATIBLE:{incompatible}")
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    model.eval()

    requires_grad_count = sum(parameter.requires_grad for parameter in model.parameters())
    gradient_tensor_count = sum(parameter.grad is not None for parameter in model.parameters())
    if requires_grad_count != 0 or gradient_tensor_count != 0:
        raise RuntimeError("LOCKED_MODEL_GRADIENT_PREFLIGHT_FAIL")
    before_digest = state_dict_digest(model)

    preflight = {
        "stage": "SYS-014_STAGE_4D-A",
        "PREFLIGHT": "PASS",
        "performed_at": iso_now(),
        "output_directory": str(OUTPUT_DIR),
        "output_directory_absent_before_preflight": True,
        "LOCKED_TEST_OPENED": "NO",
        "test_records_loaded": 0,
        "test_text_sent_to_model": 0,
        "safety_gold_records_loaded": 0,
        "LOCKED_MODEL_ID": MODEL_ID,
        "LOCKED_MODEL_REVISION": MODEL_REVISION,
        "LOCKED_EXPERIMENT": EXPERIMENT_ID,
        "LOCKED_EPOCH": LOCKED_EPOCH,
        "LOCKED_CHECKPOINT_SHA256": LOCKED_STATE_SHA256,
        "checkpoint": {
            "path": str(CHECKPOINT_STATE),
            "manifest_path": str(CHECKPOINT_DIR / "checkpoint_manifest.json"),
            "expected_sha256": LOCKED_STATE_SHA256,
            "actual_sha256": actual_checkpoint_sha,
            "sha256_match": True,
            "state_dict_strict_load": True,
            "checkpoint_kind": checkpoint_manifest["checkpoint_kind"],
        },
        "model_config": {
            "path": str(CHECKPOINT_DIR / "model_config.json"),
            "expected_fields": expected_model_fields,
            "matches_locked_checkpoint": True,
        },
        "tokenizer": tokenizer_audit,
        "model_provenance": provenance,
        "dataset": {
            "manifest_path": str(MANIFEST_PATH),
            "expected_manifest_sha256": DATASET_MANIFEST_SHA256,
            "actual_manifest_sha256": actual_manifest_sha,
            "manifest_sha256_match": True,
            "test_path": str(TEST_PATH),
            "expected_test_sha256": TEST_SHA256,
            "actual_test_sha256": actual_test_sha,
            "test_sha256_match": True,
            "immutable": True,
        },
        "test_provenance_checks": test_provenance_checks,
        "test_never_used_for_training_or_checkpoint_selection": True,
        "runtime_history_checks": runtime_history_checks,
        "runtime_source_snapshot_before": runtime_before,
        "model_parameters": {
            "requires_grad_parameter_tensor_count": requires_grad_count,
            "gradient_tensor_count": gradient_tensor_count,
            "state_dict_digest_before_test": before_digest,
            "no_gradient": True,
        },
        "frozen_metric_implementation": {
            "paths": [
                "scripts/nlu_training/metrics.py",
                "scripts/nlu_training/stage4c_exp002.py",
                "scripts/nlu_training/labels.py",
                "scripts/nlu_training/projection.py",
            ],
            "sha256": {
                relative: sha256_file(ROOT / relative)
                for relative in (
                    "scripts/nlu_training/metrics.py",
                    "scripts/nlu_training/stage4c_exp002.py",
                    "scripts/nlu_training/labels.py",
                    "scripts/nlu_training/projection.py",
                )
            },
            "label_mapping_matches_checkpoint": True,
            "max_length": MAX_LENGTH,
            "raw_executable_definition": "pred_scope=IN_SCOPE_CONTROL AND pred_structure=SINGLE AND pred_intent in frozen 7 intents",
            "safety_gates": training_config["safety_gates"],
        },
        "MODEL_PARAMETERS_CHANGED": "NO",
        "TRAINING_STEPS_EXECUTED_THIS_STAGE": 0,
        "BACKWARD_EXECUTED": "NO",
        "OPTIMIZER_STEP_EXECUTED": "NO",
        "SCHEDULER_STEP_EXECUTED": "NO",
        "TEST_EVALUATION_EXECUTED": "NO",
        "SAFETY_GOLD_EVALUATION_EXECUTED": "NO",
        "python_executable": os.path.realpath(sys.executable),
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "device": device.type.upper(),
    }
    return preflight, model, tokenizer, device, before_digest


def slot_type_set(spans: Iterable[Iterable[Any]], entity: str) -> set[tuple[str, int, int]]:
    return {
        (str(span[0]), int(span[1]), int(span[2]))
        for span in spans
        if str(span[0]) == entity
    }


def evaluate_locked_test(
    model: JointNLUModel,
    loader: DataLoader[Any],
    *,
    records_by_id: dict[str, dict[str, Any]],
    tokenizer: Any,
    device: torch.device,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
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
    gold_token_counts: Counter[str] = Counter()
    predicted_token_counts: Counter[str] = Counter()
    value_cases: list[dict[str, Any]] = []
    forward_batch_count = 0

    model.eval()
    with torch.inference_mode():
        for batch in loader:
            outputs = model(**model_inputs(batch, device))
            forward_batch_count += 1
            scope_probabilities = torch.softmax(outputs["scope_logits"], dim=-1).cpu()
            structure_probabilities = torch.softmax(
                outputs["structure_logits"], dim=-1
            ).cpu()
            intent_probabilities = torch.softmax(outputs["intent_logits"], dim=-1).cpu()
            negation_probabilities = torch.softmax(
                outputs["negation_logits"], dim=-1
            ).cpu()
            batch_scope_pred = scope_probabilities.argmax(-1).tolist()
            batch_structure_pred = structure_probabilities.argmax(-1).tolist()
            batch_intent_pred = intent_probabilities.argmax(-1).tolist()
            batch_negation_pred = negation_probabilities.argmax(-1).tolist()
            batch_slot_pred = outputs["slot_logits"].argmax(-1).cpu().tolist()

            scope_true.extend(batch["scope_labels"].tolist())
            structure_true.extend(batch["structure_labels"].tolist())
            intent_true.extend(batch["intent_labels"].tolist())
            negation_true.extend(batch["negation_labels"].tolist())
            slot_true.extend(batch["slot_labels"].tolist())
            scope_pred.extend(batch_scope_pred)
            structure_pred.extend(batch_structure_pred)
            intent_pred.extend(batch_intent_pred)
            negation_pred.extend(batch_negation_pred)

            for index, sample_id in enumerate(batch["sample_ids"]):
                text = batch["texts"][index]
                gold_ids = batch["slot_labels"][index].tolist()
                predicted_ids = [
                    IGNORE_INDEX if gold == IGNORE_INDEX else int(predicted)
                    for gold, predicted in zip(
                        gold_ids, batch_slot_pred[index], strict=True
                    )
                ]
                slot_pred.append(predicted_ids)
                row = build_prediction_row(
                    sample_id=sample_id,
                    text=text,
                    record=records_by_id[sample_id],
                    scope_probabilities=scope_probabilities[index],
                    structure_probabilities=structure_probabilities[index],
                    intent_probabilities=intent_probabilities[index],
                    negation_probabilities=negation_probabilities[index],
                    gold_slot_ids=gold_ids,
                    predicted_slot_ids=predicted_ids,
                    tokenizer=tokenizer,
                )

                encoded = tokenizer(
                    text,
                    add_special_tokens=True,
                    truncation=True,
                    max_length=MAX_LENGTH,
                    return_offsets_mapping=True,
                )
                length = len(encoded["input_ids"])
                tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"])
                offsets = [
                    [int(value) for value in offset]
                    for offset in encoded["offset_mapping"]
                ]
                sample_gold_ids = gold_ids[:length]
                sample_predicted_ids = predicted_ids[:length]
                valid_positions = [
                    position
                    for position, label in enumerate(sample_gold_ids)
                    if label != IGNORE_INDEX
                ]
                token_rows = [
                    {
                        "token_index": position,
                        "token": tokens[position],
                        "offset": offsets[position],
                        "gold": SLOT_LABELS[sample_gold_ids[position]],
                        "predicted": SLOT_LABELS[sample_predicted_ids[position]],
                    }
                    for position in valid_positions
                ]
                gold_token_counts.update(
                    SLOT_LABELS[sample_gold_ids[position]]
                    for position in valid_positions
                )
                predicted_token_counts.update(
                    SLOT_LABELS[sample_predicted_ids[position]]
                    for position in valid_positions
                )
                row["gold_slot_label_ids"] = sample_gold_ids
                row["predicted_slot_label_ids"] = sample_predicted_ids
                row["slot_token_predictions"] = token_rows
                prediction_rows.append(row)

                gold_values = [
                    span for span in row["gold_slots"] if span["slot_type"] == "VALUE"
                ]
                if gold_values:
                    predicted_values = [
                        span
                        for span in row["predicted_slots"]
                        if span["slot_type"] == "VALUE"
                    ]
                    exact = all(
                        any(
                            candidate["char_start"] == gold["char_start"]
                            and candidate["char_end"] == gold["char_end"]
                            for candidate in predicted_values
                        )
                        for gold in gold_values
                    )
                    status = (
                        "CORRECT"
                        if exact
                        else "MISSED"
                        if not predicted_values
                        else "BOUNDARY_ERROR"
                    )
                    value_cases.append(
                        {
                            "sample_id": sample_id,
                            "text": text,
                            "gold_VALUE": gold_values,
                            "predicted_VALUE": predicted_values,
                            "status": status,
                        }
                    )

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
    slot_metrics = slot_span_metrics(slot_true, slot_pred)
    safety = unsafe_false_accept_metrics(
        true_scope=scope_true,
        true_structure=structure_true,
        pred_scope=scope_pred,
        pred_structure=structure_pred,
        pred_intent=intent_pred,
    )

    per_intent_negation: dict[str, Any] = {}
    for intent_id, intent_name in enumerate(INTENT_LABELS):
        indices = [
            index for index in intent_indices if intent_true[index] == intent_id
        ]
        if not any(negation_true[index] == 1 for index in indices):
            per_intent_negation[intent_name] = "NOT_ESTIMABLE"
        else:
            per_intent_negation[intent_name] = classification_metrics(
                [negation_true[index] for index in indices],
                [negation_pred[index] for index in indices],
                label_names=NEGATION_LABELS,
            )

    quality_inputs = {
        "intent_macro_f1": intent_metrics["macro_f1"],
        "scope_macro_f1": scope_metrics["macro_f1"],
        "structure_macro_f1": structure_metrics["macro_f1"],
        "slot_span_f1": slot_metrics["OVERALL"]["f1"],
        "negation_f1": negation_metrics["per_class"]["NEGATED"]["f1"],
    }
    token_total = sum(predicted_token_counts.values())
    sentence_negation_fns: list[dict[str, Any]] = []
    for row in prediction_rows:
        if row["gold_negated"] is True and row["pred_negated"] is False:
            gold_spans = [
                span for span in row["gold_slots"] if span["slot_type"] == "NEGATION"
            ]
            predicted_spans = [
                span
                for span in row["predicted_slots"]
                if span["slot_type"] == "NEGATION"
            ]
            gold_signature = {
                (span["char_start"], span["char_end"], span["text"])
                for span in gold_spans
            }
            predicted_signature = {
                (span["char_start"], span["char_end"], span["text"])
                for span in predicted_spans
            }
            sentence_negation_fns.append(
                {
                    "sample_id": row["sample_id"],
                    "text": row["text"],
                    "intent": row["gold_intent"],
                    "gold_negation": "NEGATED",
                    "pred_negation": "NOT_NEGATED",
                    "NEGATED_probability": row["negation_probabilities"]["NEGATED"],
                    "gold_NEGATION_spans": gold_spans,
                    "predicted_NEGATION_spans": predicted_spans,
                    "NEGATION_slot_detected": row["negation_slot_detected"],
                    "NEGATION_slot_correct": bool(gold_signature)
                    and gold_signature == predicted_signature,
                    "raw_executable": row["raw_executable"],
                }
            )

    error_cases: list[dict[str, Any]] = []
    for row in prediction_rows:
        error_types: list[str] = []
        if row["gold_intent"] is not None and row["gold_intent"] != row["pred_intent"]:
            error_types.append("INTENT_ERROR")
        if row["gold_scope"] != row["pred_scope"]:
            error_types.append("SCOPE_ERROR")
        if row["gold_structure"] != row["pred_structure"]:
            error_types.append("STRUCTURE_ERROR")
        for entity, error_name in (
            ("AREA", "AREA_ERROR"),
            ("VALUE", "VALUE_ERROR"),
            ("NEGATION", "NEGATION_SLOT_ERROR"),
        ):
            if slot_type_set(row["gold_slot_token_spans"], entity) != slot_type_set(
                row["predicted_slot_token_spans"], entity
            ):
                error_types.append(error_name)
        if (
            row["gold_negated"] is not None
            and row["gold_negated"] != row["pred_negated"]
        ):
            error_types.append("SENTENCE_NEGATION_ERROR")
        should_abstain = (
            row["gold_scope"] != "IN_SCOPE_CONTROL"
            or row["gold_structure"] != "SINGLE"
        )
        if should_abstain and row["raw_executable"]:
            error_types.append("UNSAFE_FALSE_ACCEPT")
        if error_types:
            error_cases.append(
                {
                    "sample_id": row["sample_id"],
                    "text": row["text"],
                    "error_types": error_types,
                    "gold": {
                        "scope": row["gold_scope"],
                        "structure": row["gold_structure"],
                        "intent": row["gold_intent"],
                        "negated": row["gold_negated"],
                        "slots": row["gold_slots"],
                    },
                    "predicted": {
                        "scope": row["pred_scope"],
                        "structure": row["pred_structure"],
                        "intent": row["pred_intent"],
                        "negated": row["pred_negated"],
                        "slots": row["predicted_slots"],
                        "raw_executable": row["raw_executable"],
                    },
                }
            )

    metrics = {
        "evaluation_split": "LOCKED_TEST",
        "sample_count": len(prediction_rows),
        "test_dataset_passes": 1,
        "forward_batch_count": forward_batch_count,
        "intent": intent_metrics,
        "scope": scope_metrics,
        "structure": structure_metrics,
        "slot": slot_metrics,
        "sentence_negation": negation_metrics,
        "per_intent_negation": per_intent_negation,
        "safety": {
            "metric_name": "RAW_TEST_UFAR",
            "deployment_calibrated": False,
            **safety,
        },
        "primary_quality_inputs": quality_inputs,
        "PRIMARY_QUALITY_SCORE": primary_quality_score(quality_inputs),
        "TEST_FROZEN_SAFETY_GATE_PASS": safety_gate_passes(safety),
        "gold_slot_token_distribution": {
            label: gold_token_counts[label] for label in SLOT_LABELS
        },
        "predicted_slot_token_distribution": {
            label: predicted_token_counts[label] for label in SLOT_LABELS
        },
        "PREDICTED_O_RATE": predicted_token_counts["O"] / token_total,
        "VALUE_GOLD_SAMPLE_COUNT": len(value_cases),
        "VALUE_CORRECT_SAMPLE_COUNT": sum(
            row["status"] == "CORRECT" for row in value_cases
        ),
        "VALUE_MISS_SAMPLE_COUNT": sum(
            row["status"] == "MISSED" for row in value_cases
        ),
        "VALUE_BOUNDARY_ERROR_COUNT": sum(
            row["status"] == "BOUNDARY_ERROR" for row in value_cases
        ),
        "VALUE_CASES": value_cases,
        "SENTENCE_NEGATION_FALSE_NEGATIVES": sentence_negation_fns,
        "SENTENCE_NEGATION_FN_COUNT": len(sentence_negation_fns),
        "SENTENCE_NEGATION_FN_WITH_CORRECT_SLOT_SIGNAL": sum(
            row["NEGATION_slot_correct"] for row in sentence_negation_fns
        ),
        "error_case_count": len(error_cases),
        "error_type_counts": dict(
            sorted(
                Counter(
                    error_type
                    for row in error_cases
                    for error_type in row["error_types"]
                ).items()
            )
        ),
    }
    return metrics, prediction_rows, error_cases


def generalization_gap(test_metrics: dict[str, Any]) -> dict[str, Any]:
    validation_metrics = read_json(
        EXPERIMENT_DIR / "evaluation" / "validation" / "reporting_metrics.json"
    )
    validation = {
        "intent_macro_f1": validation_metrics["intent"]["macro_f1"],
        "scope_macro_f1": validation_metrics["scope"]["macro_f1"],
        "structure_macro_f1": validation_metrics["structure"]["macro_f1"],
        "area_span_f1": validation_metrics["slot"]["AREA"]["f1"],
        "value_span_f1": validation_metrics["slot"]["VALUE"]["f1"],
        "negation_span_f1": validation_metrics["slot"]["NEGATION"]["f1"],
        "overall_slot_span_f1": validation_metrics["slot"]["OVERALL"]["f1"],
        "sentence_negated_f1": validation_metrics["negation"]["per_class"][
            "NEGATED"
        ]["f1"],
        "negated_recall": validation_metrics["negation"]["per_class"]["NEGATED"][
            "recall"
        ],
        "raw_ufar": validation_metrics["safety"]["UNSAFE_FALSE_ACCEPT_RATE"],
    }
    test = {
        "intent_macro_f1": test_metrics["intent"]["macro_f1"],
        "scope_macro_f1": test_metrics["scope"]["macro_f1"],
        "structure_macro_f1": test_metrics["structure"]["macro_f1"],
        "area_span_f1": test_metrics["slot"]["AREA"]["f1"],
        "value_span_f1": test_metrics["slot"]["VALUE"]["f1"],
        "negation_span_f1": test_metrics["slot"]["NEGATION"]["f1"],
        "overall_slot_span_f1": test_metrics["slot"]["OVERALL"]["f1"],
        "sentence_negated_f1": test_metrics["sentence_negation"]["per_class"][
            "NEGATED"
        ]["f1"],
        "negated_recall": test_metrics["sentence_negation"]["per_class"][
            "NEGATED"
        ]["recall"],
        "raw_ufar": test_metrics["safety"]["UNSAFE_FALSE_ACCEPT_RATE"],
    }
    gaps = {
        name: {
            "validation": validation[name],
            "test": test[name],
            "test_minus_validation": test[name] - validation[name],
            "absolute_difference": abs(test[name] - validation[name]),
        }
        for name in validation
    }
    quality_names = [name for name in validation if name != "raw_ufar"]
    warning_metrics = [
        name
        for name in quality_names
        if validation[name] - test[name] > 0.15
    ]
    return {
        "reference": "Frozen ELECTRA exp002 epoch 9 Validation reporting_metrics.json",
        "gap_definition": "signed delta is TEST - VALIDATION; absolute_difference is magnitude",
        "metrics": gaps,
        "warning_rule": "Any principal quality metric absolute decline from Validation greater than 0.15",
        "warning_metrics": warning_metrics,
        "GENERALIZATION_DEGRADATION_WARNING": "YES" if warning_metrics else "NO",
        "used_for_model_selection_or_tuning": False,
    }


def gap_markdown(gap: dict[str, Any]) -> str:
    lines = [
        "# Validation → Locked Test 泛化差距",
        "",
        "| Metric | Validation | Test | Test - Validation | Absolute difference |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, row in gap["metrics"].items():
        lines.append(
            f"| {name} | {row['validation']:.6f} | {row['test']:.6f} | "
            f"{row['test_minus_validation']:+.6f} | {row['absolute_difference']:.6f} |"
        )
    lines.extend(
        [
            "",
            f"`GENERALIZATION_DEGRADATION_WARNING={gap['GENERALIZATION_DEGRADATION_WARNING']}`",
            "",
            "该差距只用于一次性泛化报告，不用于重选模型、调参或补训练。",
        ]
    )
    return "\n".join(lines) + "\n"


def summary_markdown(summary: dict[str, Any], metrics: dict[str, Any]) -> str:
    safety = metrics["safety"]
    categories = safety["per_category"]
    fn_lines = []
    for row in metrics["SENTENCE_NEGATION_FALSE_NEGATIVES"]:
        fn_lines.append(
            f"- `{row['sample_id']}` {row['text']}；intent=`{row['intent']}`；"
            f"NEGATED probability=`{row['NEGATED_probability']:.6f}`；"
            f"Slot detected=`{'YES' if row['NEGATION_slot_detected'] else 'NO'}`；"
            f"Slot exact=`{'YES' if row['NEGATION_slot_correct'] else 'NO'}`。"
        )
    if not fn_lines:
        fn_lines.append("- 无。")
    return f"""# SYS-014 Stage 4D-A Locked Test 评估

## 结论

- Locked Test 已一次性打开并完成单次 forward-only dataset pass。
- `TEST_FROZEN_SAFETY_GATE_PASS={summary['TEST_FROZEN_SAFETY_GATE_PASS']}`
- `GENERALIZATION_DEGRADATION_WARNING={summary['GENERALIZATION_DEGRADATION_WARNING']}`
- `DEPLOYABLE=false`：Safety Gold 与 runtime integration 尚未完成。
- 无训练、无 backward、无 optimizer/scheduler step，模型参数未变化。

## 核心指标

| Metric | Result |
|---|---:|
| Test samples | {summary['TEST_SAMPLE_COUNT']} |
| Intent Macro F1 | {summary['TEST_INTENT_MACRO_F1']:.6f} |
| Scope Macro F1 | {summary['TEST_SCOPE_MACRO_F1']:.6f} |
| Structure Macro F1 | {summary['TEST_STRUCTURE_MACRO_F1']:.6f} |
| AREA Span F1 | {summary['TEST_AREA_F1']:.6f} |
| VALUE Span F1 | {summary['TEST_VALUE_F1']:.6f} |
| NEGATION Span F1 | {summary['TEST_NEGATION_SPAN_F1']:.6f} |
| Overall Slot Span F1 | {summary['TEST_SLOT_OVERALL_F1']:.6f} |
| Sentence NEGATED F1 | {summary['TEST_SENTENCE_NEGATION_F1']:.6f} |
| NEGATED Recall | {summary['TEST_NEGATED_RECALL']:.6f} |
| RAW Test UFAR | {summary['TEST_RAW_UFAR']:.6f} |

## Safety

| Category | Support | False accepts | Rate |
|---|---:|---:|---:|
| NON_CONTROL | {categories['NON_CONTROL']['total_should_abstain']} | {categories['NON_CONTROL']['unsafe_false_accepts']} | {categories['NON_CONTROL']['false_accept_rate']} |
| UNKNOWN_CONTROL | {categories['UNKNOWN_CONTROL']['total_should_abstain']} | {categories['UNKNOWN_CONTROL']['unsafe_false_accepts']} | {categories['UNKNOWN_CONTROL']['false_accept_rate']} |
| AMBIGUOUS_CONTROL | {categories['AMBIGUOUS_CONTROL']['total_should_abstain']} | {categories['AMBIGUOUS_CONTROL']['unsafe_false_accepts']} | {categories['AMBIGUOUS_CONTROL']['false_accept_rate']} |
| MULTI | {categories['MULTI']['total_should_abstain']} | {categories['MULTI']['unsafe_false_accepts']} | {categories['MULTI']['false_accept_rate']} |
| AMBIGUOUS | {categories['AMBIGUOUS']['total_should_abstain']} | {categories['AMBIGUOUS']['unsafe_false_accepts']} | {categories['AMBIGUOUS']['false_accept_rate']} |

Frozen gate 保持不变：UFAR ≤ 0.05、MULTI false accepts=0、AMBIGUOUS false accepts=0。

## Sentence Negation false negatives

{chr(10).join(fn_lines)}

## 最终字段

```text
LOCKED_MODEL_ID={summary['LOCKED_MODEL_ID']}
LOCKED_EXPERIMENT={summary['LOCKED_EXPERIMENT']}
LOCKED_EPOCH={summary['LOCKED_EPOCH']}
LOCKED_CHECKPOINT_SHA256={summary['LOCKED_CHECKPOINT_SHA256']}
LOCKED_TEST_OPENED={summary['LOCKED_TEST_OPENED']}
TEST_SAMPLE_COUNT={summary['TEST_SAMPLE_COUNT']}
TEST_INTENT_MACRO_F1={summary['TEST_INTENT_MACRO_F1']:.6f}
TEST_SCOPE_MACRO_F1={summary['TEST_SCOPE_MACRO_F1']:.6f}
TEST_STRUCTURE_MACRO_F1={summary['TEST_STRUCTURE_MACRO_F1']:.6f}
TEST_AREA_F1={summary['TEST_AREA_F1']:.6f}
TEST_VALUE_F1={summary['TEST_VALUE_F1']:.6f}
TEST_NEGATION_SPAN_F1={summary['TEST_NEGATION_SPAN_F1']:.6f}
TEST_SLOT_OVERALL_F1={summary['TEST_SLOT_OVERALL_F1']:.6f}
TEST_SENTENCE_NEGATION_F1={summary['TEST_SENTENCE_NEGATION_F1']:.6f}
TEST_NEGATED_RECALL={summary['TEST_NEGATED_RECALL']:.6f}
TEST_RAW_UFAR={summary['TEST_RAW_UFAR']:.6f}
TEST_AMBIGUOUS_FALSE_ACCEPT_COUNT={summary['TEST_AMBIGUOUS_FALSE_ACCEPT_COUNT']}
TEST_MULTI_FALSE_ACCEPT_COUNT={summary['TEST_MULTI_FALSE_ACCEPT_COUNT']}
TEST_UNKNOWN_FALSE_ACCEPT_COUNT={summary['TEST_UNKNOWN_FALSE_ACCEPT_COUNT']}
TEST_NON_CONTROL_FALSE_ACCEPT_COUNT={summary['TEST_NON_CONTROL_FALSE_ACCEPT_COUNT']}
TEST_FROZEN_SAFETY_GATE_PASS={summary['TEST_FROZEN_SAFETY_GATE_PASS']}
SENTENCE_NEGATION_FN_COUNT={summary['SENTENCE_NEGATION_FN_COUNT']}
SENTENCE_NEGATION_FN_WITH_CORRECT_SLOT_SIGNAL={summary['SENTENCE_NEGATION_FN_WITH_CORRECT_SLOT_SIGNAL']}
UNKNOWN_CONTROL_TEST_SUPPORT={summary['UNKNOWN_CONTROL_TEST_SUPPORT']}
GENERALIZATION_DEGRADATION_WARNING={summary['GENERALIZATION_DEGRADATION_WARNING']}
MODEL_PARAMETERS_CHANGED={summary['MODEL_PARAMETERS_CHANGED']}
TRAINING_STEPS_EXECUTED_THIS_STAGE={summary['TRAINING_STEPS_EXECUTED_THIS_STAGE']}
TEST_EVALUATION_EXECUTED={summary['TEST_EVALUATION_EXECUTED']}
SAFETY_GOLD_EVALUATION_EXECUTED={summary['SAFETY_GOLD_EVALUATION_EXECUTED']}
STAGE_4D_A_LOCKED_TEST_COMPLETE={summary['STAGE_4D_A_LOCKED_TEST_COMPLETE']}
READY_FOR_STAGE_4D_B_SAFETY_GOLD={summary['READY_FOR_STAGE_4D_B_SAFETY_GOLD']}
```

无论本结果如何，当前 Test 不得用于重选模型、调参、错误驱动训练或新的 threshold calibration。
"""


def run_formal_evaluation() -> dict[str, Any]:
    preflight, model, tokenizer, device, before_digest = run_preflight()
    OUTPUT_DIR.mkdir(parents=True)
    TEST_OUTPUT_DIR.mkdir()
    write_json(OUTPUT_DIR / "preflight.json", preflight)

    manifest: dict[str, Any] = {
        "stage": "SYS-014_STAGE_4D-A",
        "status": "LOCKED_TEST_RUNNING",
        "started_at": iso_now(),
        "finished_at": None,
        "LOCKED_TEST_OPENED": "YES",
        "locked_test_opened_is_irreversible": True,
        "test_dataset_passes_planned": 1,
        "test_dataset_passes_completed": 0,
        "LOCKED_MODEL_ID": MODEL_ID,
        "LOCKED_MODEL_REVISION": MODEL_REVISION,
        "LOCKED_EXPERIMENT": EXPERIMENT_ID,
        "LOCKED_EPOCH": LOCKED_EPOCH,
        "LOCKED_CHECKPOINT_SHA256": LOCKED_STATE_SHA256,
        "TEST_EVALUATION_EXECUTED": "IN_PROGRESS",
        "SAFETY_GOLD_EVALUATION_EXECUTED": "NO",
        "TRAINING_STEPS_EXECUTED_THIS_STAGE": 0,
        "BACKWARD_EXECUTED": "NO",
        "OPTIMIZER_STEP_EXECUTED": "NO",
        "SCHEDULER_STEP_EXECUTED": "NO",
        "RUNTIME_MODIFIED_THIS_STAGE": "NO",
    }
    write_json(OUTPUT_DIR / "manifest.json", manifest)

    try:
        # This is the single irreversible opening of Test records.
        test_records = read_split("test")
        features = [
            encode_record(record, tokenizer, max_length=MAX_LENGTH)
            for record in test_records
        ]
        loader = DataLoader(
            features,
            batch_size=BATCH_SIZE,
            shuffle=False,
            collate_fn=JointNLUCollator(tokenizer),
        )
        metrics, predictions, error_cases = evaluate_locked_test(
            model,
            loader,
            records_by_id={row["sample_id"]: row for row in test_records},
            tokenizer=tokenizer,
            device=device,
        )
        if metrics["sample_count"] != len(test_records):
            raise RuntimeError("LOCKED_TEST_PREDICTION_COUNT_MISMATCH")
        if metrics["test_dataset_passes"] != 1:
            raise RuntimeError("LOCKED_TEST_DATASET_PASS_COUNT_MISMATCH")

        after_digest = state_dict_digest(model)
        changed = before_digest != after_digest
        gradient_count = sum(parameter.grad is not None for parameter in model.parameters())
        if changed or gradient_count:
            raise RuntimeError("MODEL_CHANGED_OR_GRADIENT_CREATED_DURING_LOCKED_TEST")
        runtime_after = tree_digest(ROOT / "backend" / "app")
        runtime_unchanged = (
            runtime_after["sha256"]
            == preflight["runtime_source_snapshot_before"]["sha256"]
        )
        if not runtime_unchanged:
            raise RuntimeError("RUNTIME_SOURCE_CHANGED_DURING_LOCKED_TEST")

        gap = generalization_gap(metrics)
        safety = metrics["safety"]
        categories = safety["per_category"]
        frozen_pass = metrics["TEST_FROZEN_SAFETY_GATE_PASS"]
        summary = {
            "LOCKED_MODEL_ID": MODEL_ID,
            "LOCKED_MODEL_REVISION": MODEL_REVISION,
            "LOCKED_EXPERIMENT": EXPERIMENT_ID,
            "LOCKED_EPOCH": LOCKED_EPOCH,
            "LOCKED_CHECKPOINT_SHA256": LOCKED_STATE_SHA256,
            "LOCKED_TEST_OPENED": "YES",
            "TEST_SAMPLE_COUNT": metrics["sample_count"],
            "TEST_INTENT_ACCURACY": metrics["intent"]["accuracy"],
            "TEST_INTENT_MACRO_PRECISION": metrics["intent"]["macro_precision"],
            "TEST_INTENT_MACRO_RECALL": metrics["intent"]["macro_recall"],
            "TEST_INTENT_MACRO_F1": metrics["intent"]["macro_f1"],
            "TEST_SCOPE_MACRO_F1": metrics["scope"]["macro_f1"],
            "TEST_STRUCTURE_MACRO_F1": metrics["structure"]["macro_f1"],
            "TEST_MULTI_RECALL": metrics["structure"]["per_class"]["MULTI"][
                "recall"
            ],
            "TEST_AMBIGUOUS_RECALL": metrics["structure"]["per_class"][
                "AMBIGUOUS"
            ]["recall"],
            "TEST_AREA_F1": metrics["slot"]["AREA"]["f1"],
            "TEST_VALUE_F1": metrics["slot"]["VALUE"]["f1"],
            "TEST_NEGATION_SPAN_F1": metrics["slot"]["NEGATION"]["f1"],
            "TEST_SLOT_OVERALL_F1": metrics["slot"]["OVERALL"]["f1"],
            "PREDICTED_O_RATE": metrics["PREDICTED_O_RATE"],
            "VALUE_GOLD_SAMPLE_COUNT": metrics["VALUE_GOLD_SAMPLE_COUNT"],
            "VALUE_CORRECT_SAMPLE_COUNT": metrics["VALUE_CORRECT_SAMPLE_COUNT"],
            "VALUE_MISS_SAMPLE_COUNT": metrics["VALUE_MISS_SAMPLE_COUNT"],
            "VALUE_BOUNDARY_ERROR_COUNT": metrics["VALUE_BOUNDARY_ERROR_COUNT"],
            "TEST_SENTENCE_NEGATION_ACCURACY": metrics["sentence_negation"][
                "accuracy"
            ],
            "TEST_SENTENCE_NEGATION_MACRO_F1": metrics["sentence_negation"][
                "macro_f1"
            ],
            "TEST_SENTENCE_NEGATION_F1": metrics["sentence_negation"][
                "per_class"
            ]["NEGATED"]["f1"],
            "TEST_NEGATED_PRECISION": metrics["sentence_negation"]["per_class"][
                "NEGATED"
            ]["precision"],
            "TEST_NEGATED_RECALL": metrics["sentence_negation"]["per_class"][
                "NEGATED"
            ]["recall"],
            "TEST_NEGATED_SUPPORT": metrics["sentence_negation"]["per_class"][
                "NEGATED"
            ]["support"],
            "TEST_RAW_UFAR": safety["UNSAFE_FALSE_ACCEPT_RATE"],
            "TEST_UNSAFE_FALSE_ACCEPT_COUNT": safety["unsafe_false_accepts"],
            "TEST_AMBIGUOUS_FALSE_ACCEPT_COUNT": categories["AMBIGUOUS"][
                "unsafe_false_accepts"
            ],
            "TEST_MULTI_FALSE_ACCEPT_COUNT": categories["MULTI"][
                "unsafe_false_accepts"
            ],
            "TEST_UNKNOWN_FALSE_ACCEPT_COUNT": categories["UNKNOWN_CONTROL"][
                "unsafe_false_accepts"
            ],
            "TEST_NON_CONTROL_FALSE_ACCEPT_COUNT": categories["NON_CONTROL"][
                "unsafe_false_accepts"
            ],
            "TEST_FROZEN_SAFETY_GATE_PASS": "YES" if frozen_pass else "NO",
            "TEST_SAFETY_RESULT_STATISTICALLY_FRAGILE": (
                "YES"
                if any(
                    row["total_should_abstain"] <= 1
                    for row in categories.values()
                )
                else "NO"
            ),
            "SENTENCE_NEGATION_FN_COUNT": metrics["SENTENCE_NEGATION_FN_COUNT"],
            "SENTENCE_NEGATION_FN_WITH_CORRECT_SLOT_SIGNAL": metrics[
                "SENTENCE_NEGATION_FN_WITH_CORRECT_SLOT_SIGNAL"
            ],
            "UNKNOWN_CONTROL_TEST_SUPPORT": metrics["scope"]["per_class"][
                "UNKNOWN_CONTROL"
            ]["support"],
            "UNKNOWN_CONTROL_TEST_RECALL": metrics["scope"]["per_class"][
                "UNKNOWN_CONTROL"
            ]["recall"],
            "GENERALIZATION_DEGRADATION_WARNING": gap[
                "GENERALIZATION_DEGRADATION_WARNING"
            ],
            "MODEL_PARAMETERS_CHANGED": "NO",
            "MODEL_STATE_DIGEST_BEFORE_TEST": before_digest,
            "MODEL_STATE_DIGEST_AFTER_TEST": after_digest,
            "RUNTIME_MODIFIED_THIS_STAGE": "NO",
            "TRAINING_STEPS_EXECUTED_THIS_STAGE": 0,
            "BACKWARD_EXECUTED": "NO",
            "OPTIMIZER_STEP_EXECUTED": "NO",
            "SCHEDULER_STEP_EXECUTED": "NO",
            "TEST_EVALUATION_EXECUTED": "YES",
            "SAFETY_GOLD_EVALUATION_EXECUTED": "NO",
            "DEPLOYABLE": False,
            "STAGE_4D_A_LOCKED_TEST_COMPLETE": "YES",
            "READY_FOR_STAGE_4D_B_SAFETY_GOLD": "YES",
            "test_result_used_for_model_selection_or_tuning": False,
        }

        safety_metrics = {
            "metric_name": "RAW_TEST_UFAR",
            "frozen_gate_definition": {
                "ufar_max": 0.05,
                "multi_false_accepts": 0,
                "ambiguous_false_accepts": 0,
            },
            **safety,
            "TEST_FROZEN_SAFETY_GATE_PASS": summary[
                "TEST_FROZEN_SAFETY_GATE_PASS"
            ],
            "STATISTICALLY_FRAGILE": summary[
                "TEST_SAFETY_RESULT_STATISTICALLY_FRAGILE"
            ],
        }

        write_json(TEST_OUTPUT_DIR / "metrics.json", metrics)
        write_jsonl(TEST_OUTPUT_DIR / "predictions.jsonl", predictions)
        write_jsonl(TEST_OUTPUT_DIR / "error_cases.jsonl", error_cases)
        write_json(TEST_OUTPUT_DIR / "safety_metrics.json", safety_metrics)
        write_json(TEST_OUTPUT_DIR / "generalization_gap.json", gap)
        (TEST_OUTPUT_DIR / "generalization_gap.md").write_text(
            gap_markdown(gap), encoding="utf-8"
        )
        write_json(OUTPUT_DIR / "test_evaluation_summary.json", summary)
        (OUTPUT_DIR / "test_evaluation_summary.md").write_text(
            summary_markdown(summary, metrics), encoding="utf-8"
        )

        artifact_paths = [
            OUTPUT_DIR / "preflight.json",
            TEST_OUTPUT_DIR / "metrics.json",
            TEST_OUTPUT_DIR / "predictions.jsonl",
            TEST_OUTPUT_DIR / "error_cases.jsonl",
            TEST_OUTPUT_DIR / "safety_metrics.json",
            TEST_OUTPUT_DIR / "generalization_gap.json",
            TEST_OUTPUT_DIR / "generalization_gap.md",
            OUTPUT_DIR / "test_evaluation_summary.json",
            OUTPUT_DIR / "test_evaluation_summary.md",
        ]
        manifest.update(
            {
                "status": "COMPLETE",
                "finished_at": iso_now(),
                "test_dataset_passes_completed": 1,
                "test_forward_batch_count": metrics["forward_batch_count"],
                "test_sample_count": metrics["sample_count"],
                "TEST_EVALUATION_EXECUTED": "YES",
                "SAFETY_GOLD_EVALUATION_EXECUTED": "NO",
                "MODEL_PARAMETERS_CHANGED": "NO",
                "runtime_source_snapshot_before": preflight[
                    "runtime_source_snapshot_before"
                ],
                "runtime_source_snapshot_after": runtime_after,
                "runtime_source_unchanged": True,
                "TEST_FROZEN_SAFETY_GATE_PASS": summary[
                    "TEST_FROZEN_SAFETY_GATE_PASS"
                ],
                "GENERALIZATION_DEGRADATION_WARNING": summary[
                    "GENERALIZATION_DEGRADATION_WARNING"
                ],
                "STAGE_4D_A_LOCKED_TEST_COMPLETE": "YES",
                "READY_FOR_STAGE_4D_B_SAFETY_GOLD": "YES",
                "source_artifacts": {
                    "checkpoint_manifest": str(
                        CHECKPOINT_DIR / "checkpoint_manifest.json"
                    ),
                    "checkpoint_state": str(CHECKPOINT_STATE),
                    "dataset_manifest": str(MANIFEST_PATH),
                    "locked_test": str(TEST_PATH),
                    "stage4c_final_decision": str(FINAL_DECISION_PATH),
                },
                "output_artifacts": [
                    {
                        "path": str(path.relative_to(OUTPUT_DIR)),
                        "sha256": sha256_file(path),
                        "bytes": path.stat().st_size,
                    }
                    for path in artifact_paths
                ],
            }
        )
        write_json(OUTPUT_DIR / "manifest.json", manifest)
        return summary
    except Exception as error:
        manifest.update(
            {
                "status": "FAILED_AFTER_LOCKED_TEST_OPEN",
                "finished_at": iso_now(),
                "failure_type": type(error).__name__,
                "failure_message": str(error),
                "LOCKED_TEST_OPENED": "YES",
                "TEST_EVALUATION_EXECUTED": "FAILED_AFTER_OPEN",
                "SAFETY_GOLD_EVALUATION_EXECUTED": "NO",
                "STAGE_4D_A_LOCKED_TEST_COMPLETE": "NO",
                "READY_FOR_STAGE_4D_B_SAFETY_GOLD": "NO",
            }
        )
        write_json(OUTPUT_DIR / "manifest.json", manifest)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Run preflight without parsing Test records or creating output files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.preflight_only:
        preflight, _, _, _, _ = run_preflight()
        print(json.dumps(preflight, ensure_ascii=False, indent=2))
        return 0
    summary = run_formal_evaluation()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
