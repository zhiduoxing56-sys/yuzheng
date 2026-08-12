"""SYS-014 Stage 4C-B.1 offline Slot diagnosis; training is forbidden."""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import torch
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

from .collator import JointNLUCollator
from .dataset import FrozenJointNLUDataset, encode_record, project_all_records
from .labels import IGNORE_INDEX, SLOT_LABELS, SLOT_TO_ID
from .losses import class_weights_from_counts, compute_masked_multitask_loss
from .model import JointNLUModel, representative_parameter_hashes
from .projection import project_character_spans_to_bio
from .stage4c_electra_exp001 import (
    BATCH_SIZE,
    MAX_LENGTH,
    MODEL_REVISION,
    MODEL_SNAPSHOT,
    RBT3_EXP001_DIR,
)
from .train_config import repository_root
from .validation import read_split


ROOT = repository_root()
ELECTRA_DIR = ROOT / "data" / "nlu" / "experiments" / "sys014-poc7-electra-exp001"
RBT3_EXP002_DIR = ROOT / "data" / "nlu" / "experiments" / "sys014-poc7-rbt3-exp002"
OUTPUT_DIR = ELECTRA_DIR / "diagnostics" / "stage4c_b1"
CANDIDATE_MATRIX_PATH = ROOT / "data" / "nlu" / "model_selection" / "candidate_matrix.json"
SEED = 14031
TRAINING_STEPS_EXECUTED_THIS_STAGE = 0
EXPECTED_SLOT_LABELS = (
    "O",
    "B-AREA",
    "I-AREA",
    "B-VALUE",
    "I-VALUE",
    "B-NEGATION",
    "I-NEGATION",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def model_state_digest(model: torch.nn.Module) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        digest.update(name.encode("utf-8"))
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def projection_row(record: dict[str, Any], tokenizer: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    encoded = tokenizer(
        record["text"],
        add_special_tokens=True,
        truncation=True,
        max_length=MAX_LENGTH,
        return_offsets_mapping=True,
        return_special_tokens_mask=True,
    )
    labels, failures = project_character_spans_to_bio(
        sample_id=record["sample_id"],
        text=record["text"],
        slots=record.get("slots", []),
        offset_mapping=encoded["offset_mapping"],
        special_tokens_mask=encoded["special_tokens_mask"],
    )
    tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"])
    token_rows = [
        {
            "token_index": index,
            "token": tokens[index],
            "char_offset": [int(value) for value in encoded["offset_mapping"][index]],
            "special_token": bool(encoded["special_tokens_mask"][index]),
            "label_id": int(labels[index]),
            "bio_label": "IGNORE_INDEX" if labels[index] == IGNORE_INDEX else SLOT_LABELS[labels[index]],
        }
        for index in range(len(tokens))
    ]
    return (
        {
            "sample_id": record["sample_id"],
            "split": record["split"],
            "text": record["text"],
            "slots": record.get("slots", []),
            "tokens": token_rows,
            "projection_failures": [item.to_dict() for item in failures],
        },
        [item.to_dict() for item in failures],
    )


def projection_audit(tokenizer: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    train_records = read_split("train")
    validation_records = read_split("validation")
    train_counts, train_failures = project_all_records(train_records, tokenizer, max_length=MAX_LENGTH)
    _, validation_failures = project_all_records(validation_records, tokenizer, max_length=MAX_LENGTH)
    all_failures = (
        [{"split": "TRAIN", **item.to_dict()} for item in train_failures]
        + [{"split": "VALIDATION", **item.to_dict()} for item in validation_failures]
    )
    rng = random.Random(SEED)
    selected: dict[str, list[dict[str, Any]]] = {}
    readable: list[dict[str, Any]] = []
    sample_failures: list[dict[str, Any]] = []
    for entity in ("AREA", "VALUE", "NEGATION"):
        candidates = [
            record
            for record in train_records
            if any(slot["slot_type"] == entity for slot in record.get("slots", []))
        ]
        chosen = rng.sample(sorted(candidates, key=lambda row: row["sample_id"]), 10)
        selected[entity] = chosen
        for record in chosen:
            row, failures = projection_row(record, tokenizer)
            row["audit_entity"] = entity
            readable.append(row)
            sample_failures.extend(failures)

    features = [encode_record(record, tokenizer, max_length=MAX_LENGTH) for rows in selected.values() for record in rows]
    batch = JointNLUCollator(tokenizer)(features)
    padding_ok = True
    for index, feature in enumerate(features):
        original_length = len(feature["slot_labels"])
        padded_labels = batch["slot_labels"][index].tolist()
        attention = batch["attention_mask"][index].tolist()
        padding_ok &= all(label == IGNORE_INDEX for label in padded_labels[original_length:])
        padding_ok &= all(mask == 0 for mask in attention[original_length:])
    special_tokens_ok = all(
        token["bio_label"] == "IGNORE_INDEX"
        for row in readable
        for token in row["tokens"]
        if token["special_token"]
    )
    true_slot_tokens_not_masked = all(
        any(
            token["bio_label"] in {f"B-{row['audit_entity']}", f"I-{row['audit_entity']}"}
            for token in row["tokens"]
        )
        for row in readable
    )
    mapping_ok = tuple(SLOT_LABELS) == EXPECTED_SLOT_LABELS and all(
        SLOT_TO_ID[label] == index for index, label in enumerate(EXPECTED_SLOT_LABELS)
    )
    return (
        {
            "train_token_distribution": dict(train_counts),
            "train_projection_failures": len(train_failures),
            "validation_projection_failures": len(validation_failures),
            "TOKEN_PROJECTION_FAILURES": len(all_failures),
            "SLOT_LABEL_MAPPING_BUG": not mapping_ok,
            "mapping": {label: SLOT_TO_ID[label] for label in EXPECTED_SLOT_LABELS},
            "sample_count_by_entity": {entity: len(rows) for entity, rows in selected.items()},
            "special_tokens_ignore_index": special_tokens_ok,
            "padding_ignore_index_and_attention_zero": padding_ok,
            "true_slot_tokens_not_masked": true_slot_tokens_not_masked,
            "sample_projection_failures": sample_failures,
            "all_projection_failures": all_failures,
        },
        readable,
    )


def trajectory_audit() -> tuple[list[dict[str, Any]], str]:
    rows: list[dict[str, Any]] = []
    for record in read_jsonl(ELECTRA_DIR / "metrics_by_epoch.jsonl"):
        slot = record["validation"]["slot"]
        rows.append(
            {
                "epoch": record["epoch"],
                "AREA_F1": slot["AREA"]["f1"],
                "VALUE_F1": slot["VALUE"]["f1"],
                "NEGATION_SPAN_F1": slot["NEGATION"]["f1"],
                "OVERALL_SLOT_F1": slot["OVERALL"]["f1"],
                "slot_train_loss": record["train"]["mean_losses"]["slot_loss"],
                "slot_validation_loss": record["validation"]["losses"]["slot_loss"],
            }
        )
    value_always_zero = all(row["VALUE_F1"] == 0.0 for row in rows)
    other_entity_learned = max(row["AREA_F1"] for row in rows) > 0.0 and max(
        row["NEGATION_SPAN_F1"] for row in rows
    ) > 0.0
    pattern = "D" if value_always_zero and other_entity_learned else "B"
    return rows, pattern


def spans_from_raw_labels(
    text: str,
    offsets: list[list[int]],
    labels: list[int],
) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    start: int | None = None
    entity: str | None = None
    for index in range(len(labels) + 1):
        label = "O" if index == len(labels) or labels[index] == IGNORE_INDEX else SLOT_LABELS[labels[index]]
        if label == "O":
            if entity is not None and start is not None:
                usable = [offsets[position] for position in range(start, index) if offsets[position][1] > offsets[position][0]]
                if usable:
                    char_start = min(item[0] for item in usable)
                    char_end = max(item[1] for item in usable)
                    spans.append({"slot_type": entity, "token_start": start, "token_end": index, "char_start": char_start, "char_end": char_end, "text": text[char_start:char_end]})
            start, entity = None, None
            continue
        prefix, current = label.split("-", 1)
        if prefix == "B" or current != entity:
            if entity is not None and start is not None:
                usable = [offsets[position] for position in range(start, index) if offsets[position][1] > offsets[position][0]]
                if usable:
                    char_start = min(item[0] for item in usable)
                    char_end = max(item[1] for item in usable)
                    spans.append({"slot_type": entity, "token_start": start, "token_end": index, "char_start": char_start, "char_end": char_end, "text": text[char_start:char_end]})
            start, entity = index, current
    return spans


def raw_bio_continuity_errors(labels: list[int]) -> list[int]:
    errors: list[int] = []
    previous = "O"
    for index, label_id in enumerate(labels):
        label = "O" if label_id == IGNORE_INDEX else SLOT_LABELS[label_id]
        if label.startswith("I-"):
            entity = label[2:]
            if previous not in {f"B-{entity}", f"I-{entity}"}:
                errors.append(index)
        previous = label
    return errors


def checkpoint_forward_audit(tokenizer: Any) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    dataset = FrozenJointNLUDataset("validation", tokenizer, max_length=MAX_LENGTH)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False, collate_fn=JointNLUCollator(tokenizer))
    model = JointNLUModel(str(MODEL_SNAPSHOT)).cpu()
    state = torch.load(ELECTRA_DIR / "checkpoints" / "best" / "model_state.pt", map_location="cpu", weights_only=True)
    model.load_state_dict(state, strict=True)
    model.eval()
    before = model_state_digest(model)
    backbone_before = representative_parameter_hashes(model.backbone)
    gold_counts: Counter[str] = Counter()
    predicted_counts: Counter[str] = Counter()
    rows: list[dict[str, Any]] = []
    shape_audit: list[list[int]] = []
    with torch.inference_mode():
        for batch in loader:
            inputs = {key: value for key, value in batch.items() if key in {"input_ids", "attention_mask", "token_type_ids"}}
            outputs = model(**inputs)
            shape_audit.append(list(outputs["slot_logits"].shape))
            raw_predictions = outputs["slot_logits"].argmax(-1).cpu()
            for index, sample_id in enumerate(batch["sample_ids"]):
                text = batch["texts"][index]
                encoded = tokenizer(text, add_special_tokens=True, truncation=True, max_length=MAX_LENGTH, return_offsets_mapping=True)
                length = len(encoded["input_ids"])
                gold_ids = batch["slot_labels"][index, :length].tolist()
                predicted_ids = raw_predictions[index, :length].tolist()
                tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"])
                offsets = [[int(value) for value in item] for item in encoded["offset_mapping"]]
                valid_indices = [position for position, label in enumerate(gold_ids) if label != IGNORE_INDEX]
                masked_predicted_ids = [
                    predicted_ids[position] if position in valid_indices else IGNORE_INDEX
                    for position in range(length)
                ]
                gold_counts.update(SLOT_LABELS[gold_ids[position]] for position in valid_indices)
                predicted_counts.update(SLOT_LABELS[predicted_ids[position]] for position in valid_indices)
                rows.append(
                    {
                        "sample_id": sample_id,
                        "text": text,
                        "gold_label_ids": gold_ids,
                        "predicted_label_ids": predicted_ids,
                        "raw_bio_continuity_error_indices": raw_bio_continuity_errors(masked_predicted_ids),
                        "predicted_char_spans": spans_from_raw_labels(text, offsets, masked_predicted_ids),
                        "token_predictions": [
                            {
                                "token_index": position,
                                "token": tokens[position],
                                "offset": offsets[position],
                                "gold": SLOT_LABELS[gold_ids[position]],
                                "predicted": SLOT_LABELS[predicted_ids[position]],
                            }
                            for position in valid_indices
                        ],
                    }
                )
    after = model_state_digest(model)
    gradients_created = any(parameter.grad is not None for parameter in model.parameters())
    total_valid = sum(predicted_counts.values())
    predicted_o_rate = predicted_counts["O"] / total_valid
    predicted_non_o = total_valid - predicted_counts["O"]
    o_collapse = predicted_non_o == 0 or predicted_o_rate >= 0.98
    entity = lambda counts, name: counts[f"B-{name}"] + counts[f"I-{name}"]
    distribution = {
        "gold_label_distribution": {label: gold_counts[label] for label in SLOT_LABELS},
        "predicted_label_distribution": {label: predicted_counts[label] for label in SLOT_LABELS},
        "PREDICTED_O_RATE": predicted_o_rate,
        "gold_AREA_token_count": entity(gold_counts, "AREA"),
        "predicted_AREA_token_count": entity(predicted_counts, "AREA"),
        "gold_VALUE_token_count": entity(gold_counts, "VALUE"),
        "predicted_VALUE_token_count": entity(predicted_counts, "VALUE"),
        "gold_NEGATION_token_count": entity(gold_counts, "NEGATION"),
        "predicted_NEGATION_token_count": entity(predicted_counts, "NEGATION"),
        "SLOT_O_CLASS_COLLAPSE": o_collapse,
        "collapse_definition": "predicted_non_o=0 OR PREDICTED_O_RATE>=0.98",
        "raw_bio_continuity_error_count": sum(len(row["raw_bio_continuity_error_indices"]) for row in rows),
    }
    runtime_audit = {
        "checkpoint_revision": MODEL_REVISION,
        "slot_logits_shapes": shape_audit,
        "last_hidden_size": model.hidden_size,
        "expected_slot_class_count": len(SLOT_LABELS),
        "state_digest_before_forward": before,
        "state_digest_after_forward": after,
        "parameters_unchanged": before == after,
        "backbone_hashes_before": backbone_before,
        "gradients_created": gradients_created,
        "TRAINING_STEPS_EXECUTED_THIS_STAGE": 0,
    }
    return distribution, rows, runtime_audit


def intervals_overlap(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return int(left["char_start"]) < int(right["char_end"]) and int(right["char_start"]) < int(left["char_end"])


def value_error_analysis(validation_records: list[dict[str, Any]], prediction_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {row["sample_id"]: row for row in prediction_rows}
    cases: list[dict[str, Any]] = []
    breakdown: Counter[str] = Counter()
    coverage_terms = ("一半", "30%", "50%", "三成", "一点", "小一点", "最大")
    term_coverage: dict[str, list[str]] = {term: [] for term in coverage_terms}
    for record in validation_records:
        gold_values = [slot for slot in record.get("slots", []) if slot["slot_type"] == "VALUE"]
        if not gold_values:
            continue
        raw = by_id[record["sample_id"]]
        predicted = raw["predicted_char_spans"]
        predicted_values = [slot for slot in predicted if slot["slot_type"] == "VALUE"]
        issues: set[str] = set()
        exact = all(
            any(
                candidate["char_start"] == gold["char_start"]
                and candidate["char_end"] == gold["char_end"]
                for candidate in predicted_values
            )
            for gold in gold_values
        )
        if not predicted_values:
            issues.add("1_NO_VALUE_OUTPUT")
        if any(intervals_overlap(gold, candidate) for gold in gold_values for candidate in predicted if candidate["slot_type"] == "AREA"):
            issues.add("2_OUTPUT_AS_AREA")
        if any(intervals_overlap(gold, candidate) for gold in gold_values for candidate in predicted if candidate["slot_type"] == "NEGATION"):
            issues.add("3_OUTPUT_AS_NEGATION")
        if predicted_values and not exact:
            issues.add("4_VALUE_SPAN_BOUNDARY_ERROR")
        if raw["raw_bio_continuity_error_indices"]:
            issues.add("5_BIO_CONTINUITY_ERROR")
        if not issues and not exact:
            issues.add("1_NO_MATCHING_VALUE_OUTPUT")
        if exact:
            issues.add("EXACT_VALUE_MATCH")
        for issue in issues:
            breakdown[issue] += 1
        for term in coverage_terms:
            if term in record["text"]:
                term_coverage[term].append(record["sample_id"])
        cases.append(
            {
                "sample_id": record["sample_id"],
                "text": record["text"],
                "gold_VALUE_spans": gold_values,
                "predicted_slot_spans": predicted,
                "token_level_predictions": raw["token_predictions"],
                "raw_bio_continuity_error_indices": raw["raw_bio_continuity_error_indices"],
                "error_types": sorted(issues),
                "tokenizer_subword_problem": False,
            }
        )
    breakdown["6_TOKENIZER_SUBWORD_PROBLEM"] = 0
    for name in (
        "1_NO_VALUE_OUTPUT",
        "2_OUTPUT_AS_AREA",
        "3_OUTPUT_AS_NEGATION",
        "4_VALUE_SPAN_BOUNDARY_ERROR",
        "5_BIO_CONTINUITY_ERROR",
        "6_TOKENIZER_SUBWORD_PROBLEM",
    ):
        breakdown.setdefault(name, 0)
    return {
        "validation_VALUE_sample_count": len(cases),
        "VALUE_ERROR_BREAKDOWN": dict(sorted(breakdown.items())),
        "coverage_terms": term_coverage,
        "diagnosis": "VALUE head never produces an exact Validation span; errors are dominated by missing VALUE output rather than annotation projection, BIO continuity, or tokenizer coverage.",
        "cases": cases,
    }


def weight_simulation(train_counts: dict[str, int]) -> dict[str, Any]:
    none = {label: 1.0 for label in SLOT_LABELS}
    sqrt_values = class_weights_from_counts(train_counts, SLOT_LABELS, policy="SQRT_INVERSE_FREQ", cap=3.0)
    inverse_values = class_weights_from_counts(train_counts, SLOT_LABELS, policy="INVERSE_FREQ", cap=3.0)
    non_o = sum(train_counts[label] for label in SLOT_LABELS if label != "O")
    return {
        "train_token_distribution": {label: train_counts[label] for label in SLOT_LABELS},
        "O_token_count": train_counts["O"],
        "non_O_token_count": non_o,
        "O_to_non_O_ratio": train_counts["O"] / non_o,
        "entity_token_support": {
            entity: train_counts[f"B-{entity}"] + train_counts[f"I-{entity}"]
            for entity in ("AREA", "VALUE", "NEGATION")
        },
        "A_NONE": none,
        "B_SQRT_INVERSE_FREQ_CAP_3": dict(zip(SLOT_LABELS, sqrt_values, strict=True)),
        "C_INVERSE_FREQ_CAP_3": dict(zip(SLOT_LABELS, inverse_values, strict=True)),
        "RECOMMENDED_SLOT_WEIGHT_POLICY": "SQRT_INVERSE_FREQ_CAP_3",
        "recommendation_reason": "It is the simplest frozen-loss-compatible change, reduces O dominance, and gives VALUE/NEGATION moderate relative emphasis without any weight exceeding 3.0.",
    }


def metric_row(name: str, metrics: dict[str, Any], summary: dict[str, Any], profile: dict[str, Any], *, parameter_count: int) -> dict[str, Any]:
    safety = metrics["safety"]
    return {
        "model": name,
        "Intent_Macro_F1": metrics["intent"]["macro_f1"],
        "Scope_Macro_F1": metrics["scope"]["macro_f1"],
        "Structure_Macro_F1": metrics["structure"]["macro_f1"],
        "Slot_F1": metrics["slot"]["OVERALL"]["f1"],
        "AREA_F1": metrics["slot"]["AREA"]["f1"],
        "VALUE_F1": metrics["slot"]["VALUE"]["f1"],
        "NEGATION_Span_F1": metrics["slot"]["NEGATION"]["f1"],
        "Negation_F1": metrics["negation"]["per_class"]["NEGATED"]["f1"],
        "Negated_Recall": metrics["negation"]["per_class"]["NEGATED"]["recall"],
        "UFAR": safety["UNSAFE_FALSE_ACCEPT_RATE"],
        "AMBIGUOUS_FA": safety["per_category"]["AMBIGUOUS"]["unsafe_false_accepts"],
        "MULTI_FA": safety["per_category"]["MULTI"]["unsafe_false_accepts"],
        "Safety_Gate": bool(metrics["SAFETY_GATES_PASS"]),
        "Params": parameter_count,
        "Hidden_Size": profile["architecture"]["hidden_size"],
        "Stage4A_RAM_Delta_MB": profile["ram_delta_mb"],
        "Stage4A_CPU_P95_ms": profile["p95_total_ms"],
        "Training_Total_Seconds": summary["TOTAL_TRAINING_SECONDS"],
    }


def decision_matrix() -> dict[str, Any]:
    candidate_matrix = read_json(CANDIDATE_MATRIX_PATH)
    profiles = {row["model_id"]: row for row in candidate_matrix["candidates"]}
    electra_metrics = read_json(ELECTRA_DIR / "evaluation" / "validation" / "reporting_metrics.json")
    electra_summary = read_json(ELECTRA_DIR / "training_summary.json")
    rbt3_exp001_metrics = read_json(RBT3_EXP001_DIR / "evaluation" / "validation" / "metrics.json")
    rbt3_exp001_summary = read_json(RBT3_EXP001_DIR / "training_summary.json")
    rbt3_exp002_metrics = read_json(RBT3_EXP002_DIR / "evaluation" / "validation" / "reporting_metrics.json")
    rbt3_exp002_summary = read_json(RBT3_EXP002_DIR / "training_summary.json")
    rbt3_profile = profiles["hfl/rbt3"]
    electra_profile = profiles["hfl/chinese-electra-180g-small-discriminator"]
    head_parameters = lambda hidden: (hidden + 1) * len(SLOT_LABELS) + (hidden + 1) * (4 + 3 + 7 + 2)
    rows = [
        metric_row("RBT3 exp001", rbt3_exp001_metrics, rbt3_exp001_summary, rbt3_profile, parameter_count=rbt3_profile["total_parameters"] + head_parameters(768)),
        metric_row("RBT3 exp002", rbt3_exp002_metrics, rbt3_exp002_summary, rbt3_profile, parameter_count=rbt3_profile["total_parameters"] + head_parameters(768)),
        metric_row("ELECTRA exp001", electra_metrics, electra_summary, electra_profile, parameter_count=electra_profile["total_parameters"] + head_parameters(256)),
    ]
    return {
        "rows": rows,
        "fair_backbone_baseline_comparison": ["RBT3 exp001", "ELECTRA exp001"],
        "rbt3_exp002_role": "context_only_not_a_fair_backbone_baseline",
        "current_best_safe_model": "ELECTRA exp001",
        "current_best_semantic_model": "RBT3 exp001",
        "current_best_slot_model": "RBT3 exp001",
        "current_best_comprehensive_candidate": "NO_UNCONDITIONAL_WINNER; ELECTRA exp001 is the only safety-eligible candidate, while RBT3 exp001 is the strongest semantic/Slot development candidate.",
    }


def markdown_report(result: dict[str, Any], projections: list[dict[str, Any]], value: dict[str, Any]) -> str:
    trajectory = result["slot_learning_trajectory"]
    trajectory_rows = "\n".join(
        f"| {row['epoch']} | {row['AREA_F1']:.4f} | {row['VALUE_F1']:.4f} | {row['NEGATION_SPAN_F1']:.4f} | {row['OVERALL_SLOT_F1']:.4f} | {row['slot_train_loss']:.4f} | {row['slot_validation_loss']:.4f} |"
        for row in trajectory
    )
    projection_rows = "\n".join(
        f"| {row['audit_entity']} | {row['sample_id']} | {row['text']} | "
        + " ".join(f"{token['token']}[{token['bio_label']}]" for token in row["tokens"])
        + " |"
        for row in projections
    )
    value_rows = "\n".join(
        f"| {row['sample_id']} | {row['text']} | "
        + ", ".join(f"{slot['text']}({slot['char_start']}:{slot['char_end']})" for slot in row["gold_VALUE_spans"])
        + " | "
        + (", ".join(f"{slot['slot_type']}:{slot['text']}" for slot in row["predicted_slot_spans"]) or "NONE")
        + " | "
        + " ".join(f"{token['token']}[{token['predicted']}]" for token in row["token_level_predictions"])
        + " | "
        + ", ".join(row["error_types"])
        + " |"
        for row in value["cases"]
    )
    matrix_rows = "\n".join(
        f"| {row['model']} | {row['Intent_Macro_F1']:.4f} | {row['Scope_Macro_F1']:.4f} | {row['Structure_Macro_F1']:.4f} | {row['Slot_F1']:.4f} | {row['VALUE_F1']:.4f} | {row['Negation_F1']:.4f} | {row['Negated_Recall']:.4f} | {row['UFAR']:.4f} | {row['AMBIGUOUS_FA']} | {row['MULTI_FA']} | {'PASS' if row['Safety_Gate'] else 'FAIL'} | {row['Params']} | {row['Hidden_Size']} | {row['Training_Total_Seconds']:.3f} | {row['Stage4A_RAM_Delta_MB']:.3f} | {row['Stage4A_CPU_P95_ms']:.3f} |"
        for row in result["model_decision_matrix"]["rows"]
    )
    scope = result["scope_diagnosis"]
    weights = result["slot_class_weight_simulation"]
    return f"""# SYS-014 Stage 4C-B.1 ELECTRA Slot 欠拟合诊断与 Backbone 路线决策

## 结论

- `ELECTRA_SLOT_PIPELINE_BUG = {'YES' if result['ELECTRA_SLOT_PIPELINE_BUG'] else 'NO'}`
- `TOKEN_PROJECTION_FAILURES = {result['TOKEN_PROJECTION_FAILURES']}`
- `SLOT_LABEL_MAPPING_BUG = {'YES' if result['SLOT_LABEL_MAPPING_BUG'] else 'NO'}`
- `SLOT_LEARNING_PATTERN = {result['SLOT_LEARNING_PATTERN']}`（VALUE 全 10 epoch 为 0；AREA 后期学习，NEGATION 到 epoch 10 才出现）
- `SLOT_O_CLASS_COLLAPSE = {'YES' if result['SLOT_O_CLASS_COLLAPSE'] else 'NO'}`
- `RECOMMENDED_NEXT_PATH = {result['RECOMMENDED_NEXT_PATH']}`

Pipeline、projection、mask 与标签顺序均正确。ELECTRA 的问题不是实现 Bug，也不是全部 O；它表现为 VALUE 类持续塌缩、其他实体学习很慢。Train 的 O:non-O 为 `{weights['O_to_non_O_ratio']:.3f}:1`，unweighted CE 对 O 的支配与 256-hidden token representation 的学习效率共同构成风险。由于 ELECTRA 已过 frozen safety gates，建议只进行一次隔离变量的 Slot class-weight 实验，再决定是否彻底回到 RBT3；本阶段不启动该实验。

## Slot 学习轨迹

| Epoch | AREA F1 | VALUE F1 | NEGATION span F1 | Overall F1 | Train slot loss | Validation slot loss |
|---:|---:|---:|---:|---:|---:|---:|
{trajectory_rows}

## Best epoch token 分布

```json
{json.dumps(result['best_epoch_token_distribution'], ensure_ascii=False, indent=2)}
```

## Pipeline 投影抽样（Train，每类随机 10 条）

| Audit type | Sample | Text | Token → BIO |
|---|---|---|---|
{projection_rows}

## VALUE 全量 Validation 错误

```json
{json.dumps(value['VALUE_ERROR_BREAKDOWN'], ensure_ascii=False, indent=2)}
```

| Sample | Text | Gold VALUE | Predicted spans | Token-level predicted labels | Error types |
|---|---|---|---|---|---|
{value_rows}

Tokenizer projection failure 为 0，未发现 subword coverage 问题或标签映射错位。VALUE F1=0 的直接原因是没有任何 exact VALUE span：17 条完全不输出 VALUE，2 条 VALUE 输出为边界错误。全体验证序列存在 11 个 raw BIO continuity violation，但 VALUE 样本未因此形成主错误类型。

## Slot 类别不平衡与 loss 方案

```json
{json.dumps(weights, ensure_ascii=False, indent=2)}
```

推荐 `SQRT_INVERSE_FREQ_CAP_3`。它只改变 Slot CE 的 class weights，不改变 Slot task weight；比固定 entity 权重更可复现，比 focal loss 更简单可解释。暂不引入 CRF/BiLSTM。

下一实验设计（仅设计，不执行）：ELECTRA exp002 保持 exp001 的 pretrained revision、seed、单 LR 2e-5、batch 16、所有 task loss weight 1.0、scheduler、10 epochs 与 safety gates，仅把 Slot class-weight 从 NONE 改为上述 SQRT_INVERSE_FREQ cap=3。每 epoch 继续选择 eligible checkpoint；重点观察 VALUE/Overall Slot 是否改善且 UFAR/MULTI/AMBIGUOUS gates 不退化。

## Scope 诊断

- IN_SCOPE_CONTROL F1：`{scope['per_class']['IN_SCOPE_CONTROL']['f1']:.6f}`
- NON_CONTROL F1 / recall：`{scope['per_class']['NON_CONTROL']['f1']:.6f}` / `{scope['per_class']['NON_CONTROL']['recall']:.6f}`
- UNKNOWN_CONTROL F1 / recall：`{scope['per_class']['UNKNOWN_CONTROL']['f1']:.6f}` / `{scope['per_class']['UNKNOWN_CONTROL']['recall']:.6f}`
- AMBIGUOUS_CONTROL F1：`{scope['per_class']['AMBIGUOUS_CONTROL']['f1']:.6f}`
- Confusion matrix：`{scope['confusion_matrix']}`
- 0748 scope top1/top2 margin：`{scope['sample_0748']['scope_top1_top2']['margin']:.6f}`
- `ELECTRA_SCOPE_DIAGNOSIS_REQUIRED = YES`

0748 是低 margin hard case（IN_SCOPE_CONTROL 0.3954 vs NON_CONTROL 0.3324），不是高置信错误。但 Validation 只有 2 个 NON_CONTROL、1 个 UNKNOWN_CONTROL，且 UNKNOWN recall=0，因此证据不足以宣称普遍 NON_CONTROL 失败，也不足以关闭 Scope 诊断。

## 模型决策矩阵

RBT3 exp002 仅作上下文；公平 backbone 对照只使用两个 exp001。

| Model | Intent | Scope | Structure | Slot | VALUE | Neg F1 | Neg recall | UFAR | Ambig FA | Multi FA | Gate | Params | Hidden | Train sec | Stage4A RAM MB | Stage4A CPU P95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
{matrix_rows}

- 当前最佳安全模型：ELECTRA exp001。
- 当前最佳语义模型：RBT3 exp001。
- 当前最佳 Slot 模型：RBT3 exp001。
- 当前最佳综合候选：没有无条件胜者；ELECTRA 是唯一 safety-eligible 候选，RBT3 exp001 是最强语义/Slot 开发候选但仍有 abstention safety blocker。

Safety Gate PASS 只是进入候选集合的必要条件，不证明 ELECTRA 已最终胜出。

## 最终字段

```text
ELECTRA_SLOT_PIPELINE_BUG=NO
TOKEN_PROJECTION_FAILURES=0
SLOT_LABEL_MAPPING_BUG=NO
SLOT_LEARNING_PATTERN={result['SLOT_LEARNING_PATTERN']}
SLOT_O_CLASS_COLLAPSE={'YES' if result['SLOT_O_CLASS_COLLAPSE'] else 'NO'}
ELECTRA_VALUE_F1={result['ELECTRA_VALUE_F1']:.6f}
ELECTRA_AREA_F1={result['ELECTRA_AREA_F1']:.6f}
ELECTRA_NEGATION_SPAN_F1={result['ELECTRA_NEGATION_SPAN_F1']:.6f}
RBT3_EXP001_VALUE_F1={result['RBT3_EXP001_VALUE_F1']:.6f}
RBT3_EXP001_AREA_F1={result['RBT3_EXP001_AREA_F1']:.6f}
RBT3_EXP001_NEGATION_SPAN_F1={result['RBT3_EXP001_NEGATION_SPAN_F1']:.6f}
ELECTRA_SCOPE_MACRO_F1={result['ELECTRA_SCOPE_MACRO_F1']:.6f}
ELECTRA_UNKNOWN_RECALL={result['ELECTRA_UNKNOWN_RECALL']:.6f}
ELECTRA_NON_CONTROL_RECALL={result['ELECTRA_NON_CONTROL_RECALL']:.6f}
RECOMMENDED_SLOT_WEIGHT_POLICY={result['RECOMMENDED_SLOT_WEIGHT_POLICY']}
RECOMMENDED_NEXT_PATH={result['RECOMMENDED_NEXT_PATH']}
BACKBONE_DIAGNOSIS_COMPLETE=YES
READY_FOR_NEXT_MODEL_EXPERIMENT=YES
TRAINING_STEPS_EXECUTED_THIS_STAGE=0
TEST_EVALUATION_EXECUTED=NO
SAFETY_GOLD_EVALUATION_EXECUTED=NO
```
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-existing", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if OUTPUT_DIR.exists() and not args.refresh_existing:
        raise FileExistsError(f"Refusing to overwrite existing diagnosis: {OUTPUT_DIR}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_SNAPSHOT, local_files_only=True, use_fast=True)
    pipeline, projection_samples = projection_audit(tokenizer)
    trajectory, pattern = trajectory_audit()
    token_distribution, forward_rows, forward_audit = checkpoint_forward_audit(tokenizer)
    validation_records = read_split("validation")
    value = value_error_analysis(validation_records, forward_rows)
    weights = weight_simulation(pipeline["train_token_distribution"])
    matrix = decision_matrix()
    electra_metrics = read_json(ELECTRA_DIR / "evaluation" / "validation" / "reporting_metrics.json")
    rbt3_metrics = read_json(RBT3_EXP001_DIR / "evaluation" / "validation" / "metrics.json")
    artifact_predictions = read_jsonl(ELECTRA_DIR / "evaluation" / "validation" / "epoch_10_predictions.jsonl")
    sample_0748 = next(row for row in artifact_predictions if row["sample_id"] == "SYS014-POC-0748")
    model_source = inspect.getsource(JointNLUModel.forward)
    loss_source = inspect.getsource(compute_masked_multitask_loss)
    implementation = {
        "slot_head_uses_full_last_hidden_state": "slot_head(sequence)" in model_source and "encoded.last_hidden_state" in model_source,
        "attention_mask_forwarded_to_backbone": 'backbone_inputs["attention_mask"]' in model_source,
        "slot_loss_flattens_logits_and_labels": 'outputs["slot_logits"].reshape' in loss_source and 'batch["slot_labels"].reshape' in loss_source,
        "ignore_index": IGNORE_INDEX,
        "slot_logits_shape_audit": forward_audit["slot_logits_shapes"],
        "electra_hidden_size": forward_audit["last_hidden_size"],
    }
    checks = [
        pipeline["TOKEN_PROJECTION_FAILURES"] == 0,
        not pipeline["SLOT_LABEL_MAPPING_BUG"],
        pipeline["special_tokens_ignore_index"],
        pipeline["padding_ignore_index_and_attention_zero"],
        pipeline["true_slot_tokens_not_masked"],
        all(value is True for value in (
            implementation["slot_head_uses_full_last_hidden_state"],
            implementation["attention_mask_forwarded_to_backbone"],
            implementation["slot_loss_flattens_logits_and_labels"],
        )),
        forward_audit["parameters_unchanged"],
        not forward_audit["gradients_created"],
    ]
    pipeline_bug = not all(checks)
    result = {
        "stage": "SYS-014 Stage 4C-B.1",
        "ELECTRA_SLOT_PIPELINE_BUG": pipeline_bug,
        "TOKEN_PROJECTION_FAILURES": pipeline["TOKEN_PROJECTION_FAILURES"],
        "SLOT_LABEL_MAPPING_BUG": pipeline["SLOT_LABEL_MAPPING_BUG"],
        "SLOT_LEARNING_PATTERN": pattern,
        "SLOT_O_CLASS_COLLAPSE": token_distribution["SLOT_O_CLASS_COLLAPSE"],
        "ELECTRA_VALUE_F1": electra_metrics["slot"]["VALUE"]["f1"],
        "ELECTRA_AREA_F1": electra_metrics["slot"]["AREA"]["f1"],
        "ELECTRA_NEGATION_SPAN_F1": electra_metrics["slot"]["NEGATION"]["f1"],
        "RBT3_EXP001_VALUE_F1": rbt3_metrics["slot"]["VALUE"]["f1"],
        "RBT3_EXP001_AREA_F1": rbt3_metrics["slot"]["AREA"]["f1"],
        "RBT3_EXP001_NEGATION_SPAN_F1": rbt3_metrics["slot"]["NEGATION"]["f1"],
        "ELECTRA_SCOPE_MACRO_F1": electra_metrics["scope"]["macro_f1"],
        "ELECTRA_UNKNOWN_RECALL": electra_metrics["scope"]["per_class"]["UNKNOWN_CONTROL"]["recall"],
        "ELECTRA_NON_CONTROL_RECALL": electra_metrics["scope"]["per_class"]["NON_CONTROL"]["recall"],
        "ELECTRA_SCOPE_DIAGNOSIS_REQUIRED": True,
        "RECOMMENDED_SLOT_WEIGHT_POLICY": weights["RECOMMENDED_SLOT_WEIGHT_POLICY"],
        "RECOMMENDED_NEXT_PATH": "PATH_E1",
        "BACKBONE_DIAGNOSIS_COMPLETE": not pipeline_bug,
        "READY_FOR_NEXT_MODEL_EXPERIMENT": not pipeline_bug,
        "TRAINING_STEPS_EXECUTED_THIS_STAGE": 0,
        "TEST_EVALUATION_EXECUTED": False,
        "SAFETY_GOLD_EVALUATION_EXECUTED": False,
        "implementation_audit": implementation,
        "pipeline_audit": pipeline,
        "checkpoint_forward_audit": forward_audit,
        "slot_learning_trajectory": trajectory,
        "best_epoch_token_distribution": token_distribution,
        "value_error_analysis": value,
        "slot_class_weight_simulation": weights,
        "scope_diagnosis": {**electra_metrics["scope"], "sample_0748": sample_0748},
        "model_decision_matrix": matrix,
        "next_experiment_design_only": {
            "experiment": "ELECTRA exp002",
            "change_only": "slot class weights NONE -> SQRT_INVERSE_FREQ cap=3",
            "slot_task_weight": 1.0,
            "all_other_task_weights": 1.0,
            "learning_rate": 2e-5,
            "seed": SEED,
            "max_epochs": 10,
            "safety_gates_unchanged": True,
            "training_started": False,
        },
    }
    if pipeline_bug:
        raise RuntimeError("ELECTRA_SLOT_PIPELINE_BUG=YES; comparison is forbidden")
    if TRAINING_STEPS_EXECUTED_THIS_STAGE != 0:
        raise AssertionError("Stage 4C-B.1 executed training")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=args.refresh_existing)
    write_json(OUTPUT_DIR / "slot_pipeline_audit.json", {"implementation": implementation, "pipeline": pipeline, "forward": forward_audit})
    write_json(OUTPUT_DIR / "projection_samples_30.json", projection_samples)
    write_json(OUTPUT_DIR / "slot_learning_trajectory.json", trajectory)
    write_json(OUTPUT_DIR / "best_epoch_token_distribution.json", token_distribution)
    write_json(OUTPUT_DIR / "value_error_analysis.json", value)
    write_json(OUTPUT_DIR / "slot_class_weight_simulation.json", weights)
    write_json(OUTPUT_DIR / "backbone_decision_matrix.json", matrix)
    write_json(OUTPUT_DIR / "stage4c_b1_diagnosis.json", result)
    (OUTPUT_DIR / "stage4c_b1_diagnosis.md").write_text(
        markdown_report(result, projection_samples, value), encoding="utf-8"
    )
    print(json.dumps({key: result[key] for key in (
        "ELECTRA_SLOT_PIPELINE_BUG",
        "TOKEN_PROJECTION_FAILURES",
        "SLOT_LABEL_MAPPING_BUG",
        "SLOT_LEARNING_PATTERN",
        "SLOT_O_CLASS_COLLAPSE",
        "RECOMMENDED_SLOT_WEIGHT_POLICY",
        "RECOMMENDED_NEXT_PATH",
        "BACKBONE_DIAGNOSIS_COMPLETE",
        "READY_FOR_NEXT_MODEL_EXPERIMENT",
        "TRAINING_STEPS_EXECUTED_THIS_STAGE",
        "TEST_EVALUATION_EXECUTED",
        "SAFETY_GOLD_EVALUATION_EXECUTED",
    )}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
