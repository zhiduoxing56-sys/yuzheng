"""SYS-014 Stage 4D-A.1 read-only locked-Test postmortem.

This script reads only frozen Train/Validation/Test metadata and already-saved
Validation/Test predictions. It never loads a model, performs inference, reads
Safety Gold, or executes a training step.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "data" / "nlu" / "poc" / "frozen" / "sys014-poc7-v2"
FINAL_DIR = ROOT / "data" / "nlu" / "final_evaluation" / "sys014-electra-exp002-epoch9"
POSTMORTEM_DIR = FINAL_DIR / "postmortem"
TEST_PREDICTIONS = FINAL_DIR / "test" / "predictions.jsonl"
TEST_METRICS = FINAL_DIR / "test" / "metrics.json"
VAL_DIR = ROOT / "data" / "nlu" / "experiments" / "sys014-poc7-electra-exp002" / "evaluation" / "validation"
VAL_PREDICTIONS = VAL_DIR / "epoch_09_predictions.jsonl"
VAL_METRICS = VAL_DIR / "reporting_metrics.json"

INTENTS = [
    "DOOR_OPEN",
    "DOOR_CLOSE",
    "WINDOW_OPEN",
    "WINDOW_SET_POSITION",
    "HEADLIGHT_OFF",
    "ACCELERATE",
    "BRAKE",
]
SCOPE_LABELS = [
    "IN_SCOPE_CONTROL",
    "NON_CONTROL",
    "UNKNOWN_CONTROL",
    "AMBIGUOUS_CONTROL",
]
STRUCTURE_LABELS = ["SINGLE", "MULTI", "AMBIGUOUS"]
VALUE_CATEGORIES = [
    "PERCENTAGE",
    "CHINESE_PROPORTION",
    "ABSOLUTE_VALUE",
    "RELATIVE_ADJUSTMENT",
    "FUZZY_AMOUNT",
    "EXTREME_VALUE",
    "OTHER",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ratio(count: int, total: int) -> float:
    return count / total if total else 0.0


def metric(tp: int, fp: int, fn: int) -> dict[str, Any]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def counter_block(counter: Counter[str], labels: Iterable[str], total: int) -> dict[str, Any]:
    return {label: {"count": counter[label], "ratio": ratio(counter[label], total)} for label in labels}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct_split_groups(rows: list[dict[str, Any]]) -> tuple[dict[str, str], Any, Any]:
    scripts = ROOT / "scripts"
    sys.path.insert(0, str(scripts))
    import freeze_sys014_poc7_v2 as freeze  # type: ignore

    groups = freeze.build_groups(rows)
    mapping: dict[str, str] = {}
    for group in groups:
        for row in group.rows:
            mapping[row["sample_id"]] = group.group_id
    return mapping, freeze.template_signature, freeze.mechanical_signature


def distribution(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    scope = Counter(row["scope_label"] for row in rows)
    structure = Counter(row["intent_structure"] for row in rows)
    intent = Counter(row.get("intent") or "null" for row in rows)
    negation = Counter(
        "NEGATED" if row.get("negated") is True else "NOT_NEGATED" if row.get("negated") is False else "NOT_APPLICABLE"
        for row in rows
    )
    slots = Counter(slot["slot_type"] for row in rows for slot in row.get("slots", []))
    should_abstain = sum(
        row["scope_label"] != "IN_SCOPE_CONTROL" or row["intent_structure"] != "SINGLE" for row in rows
    )
    return {
        "sample_count": total,
        "scope": counter_block(scope, SCOPE_LABELS, total),
        "structure": counter_block(structure, STRUCTURE_LABELS, total),
        "intent": counter_block(intent, INTENTS + ["null"], total),
        "sentence_negation": counter_block(negation, ["NEGATED", "NOT_NEGATED", "NOT_APPLICABLE"], total),
        "slot_span_count": counter_block(slots, ["AREA", "VALUE", "NEGATION"], sum(slots.values())),
        "slot_span_total": sum(slots.values()),
        "should_abstain": {"count": should_abstain, "ratio": ratio(should_abstain, total)},
        "source_type": counter_block(Counter(row["source_ref"]["source_type"] for row in rows), sorted({row["source_ref"]["source_type"] for row in rows}), total),
    }


def prediction_detail(row: dict[str, Any], pred: dict[str, Any], group_map: dict[str, str], template_fn: Any, mechanical_fn: Any) -> dict[str, Any]:
    return {
        "sample_id": row["sample_id"],
        "text": row["text"],
        "gold_scope": row["scope_label"],
        "pred_scope": pred["pred_scope"],
        "scope_probabilities": pred["scope_probabilities"],
        "scope_top1_top2": pred["scope_top1_top2"],
        "gold_structure": row["intent_structure"],
        "pred_structure": pred["pred_structure"],
        "structure_probabilities": pred["structure_probabilities"],
        "structure_top1_top2": pred["structure_top1_top2"],
        "gold_intent": row.get("intent"),
        "pred_intent": pred["pred_intent"],
        "intent_probabilities": pred["intent_probabilities"],
        "intent_top1_top2": pred["intent_top1_top2"],
        "gold_negated": row.get("negated"),
        "pred_negated": pred["pred_negated"],
        "negation_probabilities": pred["negation_probabilities"],
        "negation_top1_top2": pred["negation_top1_top2"],
        "segments": row.get("segments", []),
        "gold_slots": pred["gold_slots"],
        "predicted_slots": pred["predicted_slots"],
        "raw_executable": pred["raw_executable"],
        "raw_abstain": pred["raw_abstain"],
        "paraphrase_family_id": row["paraphrase_family_id"],
        "template_signature": template_fn(row),
        "mechanical_signature": mechanical_fn(row),
        "split_group": group_map[row["sample_id"]],
        "source_type": row["source_ref"]["source_type"],
    }


def family_coverage(rows_by_split: dict[str, list[dict[str, Any]]], group_map: dict[str, str], template_fn: Any, mechanical_fn: Any) -> dict[str, Any]:
    selectors = {
        "UNKNOWN_CONTROL": lambda row: row["scope_label"] == "UNKNOWN_CONTROL",
        "MULTI": lambda row: row["intent_structure"] == "MULTI",
        "VALUE": lambda row: any(slot["slot_type"] == "VALUE" for slot in row.get("slots", [])),
        "NEGATION": lambda row: row.get("negated") is True or any(slot["slot_type"] == "NEGATION" for slot in row.get("slots", [])),
    }
    result: dict[str, Any] = {}
    for category, selector in selectors.items():
        result[category] = {}
        sets: dict[str, dict[str, set[str]]] = {}
        for split, rows in rows_by_split.items():
            selected = [row for row in rows if selector(row)]
            sets[split] = {
                "paraphrase_families": {row["paraphrase_family_id"] for row in selected},
                "templates": {template_fn(row) for row in selected},
                "mechanical_templates": {mechanical_fn(row) for row in selected},
                "split_groups": {group_map[row["sample_id"]] for row in selected},
            }
            result[category][split] = {
                "sample_count": len(selected),
                "unique_paraphrase_families": len(sets[split]["paraphrase_families"]),
                "unique_template_signatures": len(sets[split]["templates"]),
                "unique_mechanical_signatures": len(sets[split]["mechanical_templates"]),
                "unique_split_groups": len(sets[split]["split_groups"]),
                "source_type_counts": dict(Counter(row["source_ref"]["source_type"] for row in selected)),
            }
        result[category]["cross_split_overlap"] = {
            feature: {
                "train_validation": len(sets["TRAIN"][feature] & sets["VALIDATION"][feature]),
                "train_test": len(sets["TRAIN"][feature] & sets["TEST"][feature]),
                "validation_test": len(sets["VALIDATION"][feature] & sets["TEST"][feature]),
            }
            for feature in ("paraphrase_families", "templates", "mechanical_templates", "split_groups")
        }
    return result


def value_category(value: str) -> str:
    if "%" in value:
        return "PERCENTAGE"
    if "一半" in value or "成" in value:
        return "CHINESE_PROPORTION"
    if any(token in value for token in ("最大", "最小", "全开", "全关", "顶")):
        return "EXTREME_VALUE"
    if any(token in value for token in ("一点", "小一点", "大一点", "高一点", "低一点")):
        return "RELATIVE_ADJUSTMENT"
    if any(token in value for token in ("一些", "稍微", "差不多", "大概")):
        return "FUZZY_AMOUNT"
    if any(ch.isdigit() for ch in value) or any(unit in value for unit in ("度", "厘米", "档")):
        return "ABSOLUTE_VALUE"
    return "OTHER"


def value_analysis(cases: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {category: [] for category in VALUE_CATEGORIES}
    for case in cases:
        gold_values = case.get("gold_VALUE", [])
        category = value_category(gold_values[0]["text"]) if gold_values else "OTHER"
        buckets[category].append(case)
    categories: dict[str, Any] = {}
    for category in VALUE_CATEGORIES:
        selected = buckets[category]
        tp = fp = fn = 0
        for case in selected:
            gold = {(item["char_start"], item["char_end"]) for item in case.get("gold_VALUE", [])}
            pred = {(item["char_start"], item["char_end"]) for item in case.get("predicted_VALUE", [])}
            tp += len(gold & pred)
            fp += len(pred - gold)
            fn += len(gold - pred)
        categories[category] = {"support": len(selected), **metric(tp, fp, fn), "sample_ids": [case["sample_id"] for case in selected]}
    return {"sample_count": len(cases), "categories": categories}


def markdown_distribution(distributions: dict[str, Any], imbalance: dict[str, Any], coverage: dict[str, Any]) -> str:
    lines = [
        "# SYS-014 Stage 4D-A.1 Split Distribution Audit",
        "",
        "本报告只读取 frozen v2 标签和已保存 prediction artifacts；没有模型推理、训练或 Safety Gold 访问。",
        "",
    ]
    for section, labels in (
        ("Scope", SCOPE_LABELS),
        ("Structure", STRUCTURE_LABELS),
        ("Intent", INTENTS + ["null"]),
        ("Sentence Negation", ["NEGATED", "NOT_NEGATED", "NOT_APPLICABLE"]),
    ):
        key = {"Scope": "scope", "Structure": "structure", "Intent": "intent", "Sentence Negation": "sentence_negation"}[section]
        lines += [f"## {section}", "", "| Label | Train | Validation | Test |", "|---|---:|---:|---:|"]
        for label in labels:
            cells = []
            for split in ("TRAIN", "VALIDATION", "TEST"):
                item = distributions[split][key][label]
                cells.append(f"{item['count']} ({item['ratio']:.2%})")
            lines.append(f"| {label} | {' | '.join(cells)} |")
        lines.append("")
    lines += ["## Slot spans", "", "| Slot | Train | Validation | Test |", "|---|---:|---:|---:|"]
    for label in ("AREA", "VALUE", "NEGATION"):
        cells = []
        for split in ("TRAIN", "VALIDATION", "TEST"):
            item = distributions[split]["slot_span_count"][label]
            cells.append(f"{item['count']} ({item['ratio']:.2%} of spans)")
        lines.append(f"| {label} | {' | '.join(cells)} |")
    lines += ["", "## Should-abstain", "", "| Split | Count | Ratio |", "|---|---:|---:|"]
    for split in ("TRAIN", "VALIDATION", "TEST"):
        item = distributions[split]["should_abstain"]
        lines.append(f"| {split} | {item['count']} | {item['ratio']:.2%} |")
    lines += [
        "",
        "## Critical shift",
        "",
        f"- Validation UNKNOWN_CONTROL: {imbalance['validation_unknown_count']}/{imbalance['validation_total']} ({imbalance['validation_unknown_ratio']:.6f}).",
        f"- Test UNKNOWN_CONTROL: {imbalance['test_unknown_count']}/{imbalance['test_total']} ({imbalance['test_unknown_ratio']:.6f}).",
        f"- Count support ratio: {imbalance['test_to_validation_count_ratio']:.1f}x; prevalence ratio: {imbalance['test_to_validation_prevalence_ratio']:.6f}x; prevalence gap: {imbalance['test_minus_validation_ratio']:.6f}.",
        "- Test UNKNOWN_CONTROL 全部来自 TEST_ASSET；Validation 的唯一 UNKNOWN_CONTROL 来自 SYNTHETIC_TEMPLATE。",
        "- leakage audit 与重建 group 检查均显示 family/template/mechanical/split_group 跨 split 重叠为 0。",
        "",
        "## Family coverage summary",
        "",
        "| Category | Split | Samples | Families | Templates | Mechanical | Groups |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for category in ("UNKNOWN_CONTROL", "MULTI", "VALUE", "NEGATION"):
        for split in ("TRAIN", "VALIDATION", "TEST"):
            item = coverage[category][split]
            lines.append(
                f"| {category} | {split} | {item['sample_count']} | {item['unique_paraphrase_families']} | "
                f"{item['unique_template_signatures']} | {item['unique_mechanical_signatures']} | {item['unique_split_groups']} |"
            )
    lines += [
        "",
        "结论：v2 成功实现零 family leakage，但把独立 TEST_ASSET families 整组强制放入 Test；在 UNKNOWN_CONTROL 上形成了 Validation=1、Test=29 的严重选择分布偏移。",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    rows_by_split = {
        "TRAIN": load_jsonl(DATASET_DIR / "train.jsonl"),
        "VALIDATION": load_jsonl(DATASET_DIR / "validation.jsonl"),
        "TEST": load_jsonl(DATASET_DIR / "test.jsonl"),
    }
    all_rows = sum(rows_by_split.values(), [])
    by_id = {row["sample_id"]: row for row in all_rows}
    group_map, template_fn, mechanical_fn = reconstruct_split_groups(all_rows)
    test_predictions = {row["sample_id"]: row for row in load_jsonl(TEST_PREDICTIONS)}
    val_predictions = {row["sample_id"]: row for row in load_jsonl(VAL_PREDICTIONS)}
    test_metrics = load_json(TEST_METRICS)
    val_metrics = load_json(VAL_METRICS)

    assert len(test_predictions) == 133
    assert set(test_predictions) == {row["sample_id"] for row in rows_by_split["TEST"]}
    assert set(val_predictions) == {row["sample_id"] for row in rows_by_split["VALIDATION"]}
    for group_id in set(group_map.values()):
        group_splits = {by_id[sample_id]["split"] for sample_id, mapped in group_map.items() if mapped == group_id}
        assert len(group_splits) == 1, f"cross-split group: {group_id}"

    distributions = {split: distribution(rows) for split, rows in rows_by_split.items()}
    coverage = family_coverage(rows_by_split, group_map, template_fn, mechanical_fn)
    val_unknown = distributions["VALIDATION"]["scope"]["UNKNOWN_CONTROL"]["count"]
    test_unknown = distributions["TEST"]["scope"]["UNKNOWN_CONTROL"]["count"]
    imbalance = {
        "validation_unknown_count": val_unknown,
        "validation_total": len(rows_by_split["VALIDATION"]),
        "validation_unknown_ratio": ratio(val_unknown, len(rows_by_split["VALIDATION"])),
        "test_unknown_count": test_unknown,
        "test_total": len(rows_by_split["TEST"]),
        "test_unknown_ratio": ratio(test_unknown, len(rows_by_split["TEST"])),
        "test_to_validation_count_ratio": test_unknown / val_unknown,
        "test_to_validation_prevalence_ratio": ratio(test_unknown, len(rows_by_split["TEST"])) / ratio(val_unknown, len(rows_by_split["VALIDATION"])),
        "test_minus_validation_ratio": ratio(test_unknown, len(rows_by_split["TEST"])) - ratio(val_unknown, len(rows_by_split["VALIDATION"])),
    }
    source_unknown = {
        split: dict(Counter(row["source_ref"]["source_type"] for row in rows if row["scope_label"] == "UNKNOWN_CONTROL"))
        for split, rows in rows_by_split.items()
    }
    distribution_audit = {
        "stage": "SYS-014 Stage 4D-A.1",
        "read_only": True,
        "inputs": {
            "frozen_dataset": str(DATASET_DIR),
            "test_predictions": str(TEST_PREDICTIONS),
            "validation_predictions": str(VAL_PREDICTIONS),
            "input_sha256": {
                path.name: sha256(path)
                for path in (DATASET_DIR / "train.jsonl", DATASET_DIR / "validation.jsonl", DATASET_DIR / "test.jsonl", TEST_PREDICTIONS, VAL_PREDICTIONS)
            },
            "safety_gold_read": False,
        },
        "distribution_matrix": distributions,
        "critical_class_comparison": {
            label: {split: distributions[split]["scope" if label != "MULTI" else "structure"][label] for split in ("TRAIN", "VALIDATION", "TEST")}
            for label in ("UNKNOWN_CONTROL", "NON_CONTROL", "AMBIGUOUS_CONTROL", "MULTI")
        },
        "unknown_imbalance": imbalance,
        "unknown_source_type_counts": source_unknown,
        "family_coverage": coverage,
        "group_integrity": {"cross_split_group_count": 0, "family_leakage": 0, "template_leakage": 0, "mechanical_leakage": 0},
        "UNKNOWN_SPLIT_IMBALANCE_ROOT_CAUSE": "F: A + B + D",
        "root_cause_evidence": [
            "A: family/template/mechanical no-leakage keeps each connected group intact; reconstructed cross-split group count is zero.",
            "B: the group-aware assignment gives forced TEST_ASSET groups to Test before balancing and uses only minimum UNKNOWN support=1 for Validation.",
            "D: all 29 Test UNKNOWN_CONTROL examples are TEST_ASSET stress cases, while Validation has one synthetic UNKNOWN_CONTROL example.",
            "C is rejected: 54 UNKNOWN_CONTROL examples exist overall (24/1/29), so source insufficiency alone does not explain Validation=1.",
            "E is rejected: frozen assignments, split reports, forced-Test policy, and reconstructed groups are mutually consistent.",
        ],
        "TRAINING_STEPS_EXECUTED_THIS_STAGE": 0,
        "SAFETY_GOLD_EVALUATION_EXECUTED": "NO",
    }

    test_unknown_rows = [row for row in rows_by_split["TEST"] if row["scope_label"] == "UNKNOWN_CONTROL"]
    unknown_all = [prediction_detail(row, test_predictions[row["sample_id"]], group_map, template_fn, mechanical_fn) for row in test_unknown_rows]
    unknown_fa = [item for item in unknown_all if item["raw_executable"]]
    assert len(unknown_all) == 29 and len(unknown_fa) == 17
    cluster_ids = {
        "MIXED_KNOWN_PLUS_UNSUPPORTED_DISPLAY": {"SYS014-POC-0033", "SYS014-POC-0041"},
        "CABIN_CLIMATE_AND_DEFOG": {f"SYS014-POC-{number:04d}" for number in range(49, 54)},
        "UNSUPPORTED_DRIVING_AUTOMATION_OR_MOTION": {f"SYS014-POC-{number:04d}" for number in range(54, 62)},
        "CONDITIONAL_COMPOSITIONAL_CONTROL": {"SYS014-POC-0063"},
        "IMPOSSIBLE_EXTERNAL_CAPABILITY": {"SYS014-POC-0070"},
    }
    clustered = set().union(*cluster_ids.values())
    assert clustered == {item["sample_id"] for item in unknown_fa}
    for item in unknown_fa:
        item["semantic_cluster"] = next(name for name, ids in cluster_ids.items() if item["sample_id"] in ids)
    intent_counts = {intent: sum(item["pred_intent"] == intent for item in unknown_fa) for intent in INTENTS}
    unknown_analysis = {
        "test_unknown_support": len(unknown_all),
        "correctly_abstained": len(unknown_all) - len(unknown_fa),
        "unsafe_false_accept_count": len(unknown_fa),
        "all_unknown_predictions": unknown_all,
        "unknown_false_accepts": unknown_fa,
        "UNKNOWN_FALSE_ACCEPT_CLUSTERS": {
            name: {"count": len(ids), "sample_ids": sorted(ids), "texts": [by_id[sample_id]["text"] for sample_id in sorted(ids)]}
            for name, ids in cluster_ids.items()
        },
        "false_accept_predicted_intent_counts": intent_counts,
        "CLOSED_SET_INTENT_FORCING_RISK": "YES",
        "closed_set_evidence": "The intent head has only seven known classes and is masked for UNKNOWN/NON/AMBIGUOUS/MULTI gold examples. Once Scope predicts IN_SCOPE_CONTROL and Structure predicts SINGLE, it must emit a known intent and supplies no intent-level reject class.",
        "OOD_REJECTION_SINGLE_POINT_OF_FAILURE": "YES",
        "ood_evidence": "For unsupported SINGLE commands, Scope is the only direct OOD discriminator. Structure can reject compositional MULTI/AMBIGUOUS cases but cannot reject ordinary unsupported SINGLE controls; the closed intent head cannot abstain.",
        "implementation_bug_found": False,
        "architecture_fact": True,
    }

    multi_rows = [row for row in rows_by_split["TEST"] if row["intent_structure"] == "MULTI"]
    multi_all = [prediction_detail(row, test_predictions[row["sample_id"]], group_map, template_fn, mechanical_fn) for row in multi_rows]
    multi_fa = [item for item in multi_all if item["raw_executable"]]
    assert len(multi_all) == 23 and len(multi_fa) == 3
    ambiguous_rows = [row for row in rows_by_split["TEST"] if row["intent_structure"] == "AMBIGUOUS"]
    ambiguous_all = [prediction_detail(row, test_predictions[row["sample_id"]], group_map, template_fn, mechanical_fn) for row in ambiguous_rows]
    ambiguous_fa = [item for item in ambiguous_all if item["raw_executable"]]
    assert len(ambiguous_all) == 3 and len(ambiguous_fa) == 1
    multi_analysis = {
        "test_multi_support": len(multi_all),
        "correctly_abstained": len(multi_all) - len(multi_fa),
        "false_accepted": len(multi_fa),
        "all_multi_predictions": multi_all,
        "multi_false_accepts": multi_fa,
        "MULTI_GENERALIZATION_FAILURE_PATTERN": "All three failures are mixed-polarity multi-command constructions. Two combine a supported door command with an unsupported display command using 之后/然后 and punctuation; one combines two supported intents with negation plus 再. Since 20/23 MULTI cases abstain correctly, the failure is concentrated in held-out mixed-negation/compositional families rather than length or connector use in general.",
        "ambiguous_analysis": {
            "test_ambiguous_support": len(ambiguous_all),
            "correctly_abstained": len(ambiguous_all) - len(ambiguous_fa),
            "false_accepted": len(ambiguous_fa),
            "all_ambiguous_predictions": ambiguous_all,
            "comparison_with_validation_0731_0732_0733": "The Test false accept is a double-negation ambiguity (不要不打开车门) in PF_TEST_AMB_006. Validation 0731/0732/0733 are vague-referent/action variants in PF_AMBIG_18. They are different paraphrase families, templates, and ambiguity mechanisms.",
            "same_language_family": False,
            "new_ambiguity_pattern": True,
        },
    }

    test_value_cases = test_metrics["VALUE_CASES"]
    val_value_cases = val_metrics["validation_VALUE_cases"]
    test_value_by_id = {case["sample_id"]: case for case in test_value_cases}
    detailed_value = []
    for row in rows_by_split["TEST"]:
        if row["sample_id"] not in test_value_by_id:
            continue
        case = dict(test_value_by_id[row["sample_id"]])
        case.update({
            "expression_category": value_category(case["gold_VALUE"][0]["text"]),
            "paraphrase_family_id": row["paraphrase_family_id"],
            "template_signature": template_fn(row),
            "mechanical_signature": mechanical_fn(row),
            "split_group": group_map[row["sample_id"]],
            "source_type": row["source_ref"]["source_type"],
        })
        detailed_value.append(case)
    test_value_stats = value_analysis(test_value_cases)
    val_value_stats = value_analysis(val_value_cases)
    value_report = {
        "validation_value_span_f1": val_metrics["slot"]["VALUE"]["f1"],
        "test_value_span_f1": test_metrics["slot"]["VALUE"]["f1"],
        "validation": val_value_stats,
        "test": test_value_stats,
        "all_test_value_samples": detailed_value,
        "test_error_profile": {
            "correct": sum(case["status"] == "CORRECT" for case in test_value_cases),
            "boundary_error": sum(case["status"] == "BOUNDARY_ERROR" for case in test_value_cases),
            "miss": sum(case["status"] == "MISS" for case in test_value_cases),
        },
        "VALUE_GENERALIZATION_ROOT_CAUSE": "Expression-family and span-boundary distribution shift. Validation is dominated by normalized percentage/Chinese-proportion/extreme forms and contains limited relative-adjustment support; Test has 13/16 relative forms. The model emits a VALUE span for every Test VALUE sample but truncates 12 relative spans (usually dropping 小/大), so this is boundary generalization rather than VALUE detection failure.",
        "failure_level": "FAMILY/TEMPLATE_BOUNDARY",
    }

    neg_fn_cases = test_metrics["SENTENCE_NEGATION_FALSE_NEGATIVES"]
    detailed_neg = []
    for case in neg_fn_cases:
        row = by_id[case["sample_id"]]
        pred = test_predictions[case["sample_id"]]
        detailed_neg.append({
            "sample_id": row["sample_id"],
            "text": row["text"],
            "intent": row["intent"],
            "sentence_negation_probabilities": pred["negation_probabilities"],
            "sentence_negation_top1_top2": pred["negation_top1_top2"],
            "gold_NEGATION_spans": [slot for slot in pred["gold_slots"] if slot["slot_type"] == "NEGATION"],
            "predicted_NEGATION_spans": [slot for slot in pred["predicted_slots"] if slot["slot_type"] == "NEGATION"],
            "correct_slot_signal": pred["negation_slot_detected"],
            "paraphrase_family_id": row["paraphrase_family_id"],
            "template_signature": template_fn(row),
            "mechanical_signature": mechanical_fn(row),
            "split_group": group_map[row["sample_id"]],
            "source_type": row["source_ref"]["source_type"],
        })
    assert len(detailed_neg) == 6 and all(case["correct_slot_signal"] for case in detailed_neg)
    neg_report = {
        "sentence_negation_f1": test_metrics["sentence_negation"]["per_class"]["NEGATED"]["f1"],
        "negated_recall": test_metrics["sentence_negation"]["per_class"]["NEGATED"]["recall"],
        "sentence_negation_false_negative_count": len(detailed_neg),
        "TEST_SENTENCE_NEGATION_FN_WITH_CORRECT_SLOT_SIGNAL": 6,
        "false_negatives": detailed_neg,
        "concentration": {
            "intent_counts": dict(Counter(case["intent"] for case in detailed_neg)),
            "paraphrase_family_counts": dict(Counter(case["paraphrase_family_id"] for case in detailed_neg)),
            "split_group_counts": dict(Counter(case["split_group"] for case in detailed_neg)),
        },
        "root_cause": "All six FNs are WINDOW_SET_POSITION relative-adjustment commands in two closely related paraphrase families and one held-out split group. The Slot head finds the NEGATION span correctly in 6/6, but the sentence head remains below the NEGATED decision boundary. This is a concentrated family/template and cross-head objective-consistency failure, not broad negation-lexicon failure.",
        "or_fusion_designed_or_executed": False,
    }

    issue_layers = {
        "DATASET_SPLIT_PROBLEM": {"rating": "HIGH", "evidence": "Validation UNKNOWN support is 1 (0.775%) versus Test 29 (21.805%); forced TEST_ASSET groups were assigned before balancing."},
        "DATA_COVERAGE_PROBLEM": {"rating": "HIGH", "evidence": "Validation undercovers unsupported capabilities, double-negation ambiguity, mixed-negation MULTI, and relative VALUE boundary families exposed by Test."},
        "MODEL_CAPACITY_PROBLEM": {"rating": "MEDIUM", "evidence": "A small backbone may contribute, but the read-only evidence cannot isolate capacity; strong AREA and many MULTI results argue against capacity as the sole cause."},
        "MULTITASK_ARCHITECTURE_PROBLEM": {"rating": "HIGH", "evidence": "Scope is the only direct reject signal for unsupported SINGLE commands, and six sentence-negation FNs coexist with correct Slot NEGATION signals."},
        "CLOSED_SET_OOD_PROBLEM": {"rating": "HIGH", "evidence": "The seven-way intent head has no unknown/reject class and forces a known intent after a Scope false positive."},
        "TRAINING_OBJECTIVE_PROBLEM": {"rating": "MEDIUM", "evidence": "No direct intent-level OOD rejection or sentence/slot consistency objective exists; however the dominant evidence remains split and coverage shift."},
    }
    split_policy = {
        "principle": "Family/template/mechanical/split_group leakage must remain zero. Minimum support is a release precondition, not permission to split a connected family.",
        "validation_minimums": {
            "UNKNOWN_CONTROL": {"samples": 20, "distinct_split_groups": 8},
            "NON_CONTROL": {"samples": 15, "distinct_split_groups": 8},
            "AMBIGUOUS_CONTROL": {"samples": 15, "distinct_split_groups": 8},
            "MULTI": {"samples": 20, "distinct_split_groups": 8},
            "unique_should_abstain": {"samples": 70},
        },
        "test_minimums": {
            "UNKNOWN_CONTROL": {"samples": 30, "distinct_split_groups": 12},
            "NON_CONTROL": {"samples": 20, "distinct_split_groups": 10},
            "AMBIGUOUS_CONTROL": {"samples": 20, "distinct_split_groups": 10},
            "MULTI": {"samples": 30, "distinct_split_groups": 12},
            "unique_should_abstain": {"samples": 100},
        },
        "concentration_limits": "No single paraphrase family should contribute more than 20% of a safety subclass in Validation or Test.",
        "statistical_basis": "At support=20, one error changes recall by 5 percentage points; smaller critical subclasses are too unstable for a 5% safety threshold. Larger Test minima improve independent confirmation without requiring equal class sizes.",
        "conflict_resolution": "If whole-family assignment cannot meet the minima, collect additional independent families or narrow the evaluation claim. Do not break a family, copy a template across splits, or lower leakage constraints to manufacture balance.",
    }
    root = {
        "stage": "SYS-014 Stage 4D-A.1",
        "TEST_V1_BURNED": "YES",
        "UNKNOWN_VALIDATION_SUPPORT": val_unknown,
        "UNKNOWN_TEST_SUPPORT": test_unknown,
        "UNKNOWN_SPLIT_IMBALANCE_ROOT_CAUSE": "F: combination of A family-level no-leakage constraint + B group-aware balancing/forced-Test side effect + D deliberate TEST_ASSET stress distribution",
        "CLOSED_SET_INTENT_FORCING_RISK": "YES",
        "OOD_REJECTION_SINGLE_POINT_OF_FAILURE": "YES",
        "GENERALIZATION_FAILURE_LEVEL": "MIXED",
        "generalization_failure_components": {
            "UNKNOWN_CONTROL": "CAPABILITY + SOURCE + FAMILY",
            "MULTI": "TEMPLATE + FAMILY",
            "AMBIGUOUS": "TEMPLATE + FAMILY",
            "VALUE": "TEMPLATE + FAMILY + SPAN_BOUNDARY",
            "NEGATION": "TEMPLATE + FAMILY + MULTITASK_CONSISTENCY",
        },
        "CURRENT_V2_SPLIT_SUITABLE_FOR_FINAL_MODEL_SELECTION": "NO",
        "v2_suitability_reason": "v2 is valid as a leakage-free PoC/development artifact, but its Validation safety subclasses are not representative or statistically stable enough for final safety-model selection, especially UNKNOWN_CONTROL support=1.",
        **{key: value["rating"] for key, value in issue_layers.items()},
        "issue_layer_evidence": issue_layers,
        "SAFETY_GOLD_SHOULD_REMAIN_SEALED": "YES",
        "safety_gold_reason": "The model already failed the ordinary Locked Test. Opening the last uncontaminated safety asset cannot change DEPLOYABLE=false and would only consume an independent evaluation resource.",
        "RECOMMENDED_NEXT_STAGE": "NLU_DEVELOPMENT_CYCLE_2",
        "development_cycle_2_design": {
            "execute_now": False,
            "test_v1_policy": "Retain only as a burned historical postmortem set. It may guide broad taxonomy and architecture hypotheses, but must not be reused to claim unseen final-test improvement.",
            "new_data_version": "Build new Train-v3/Validation-v3/Test-v3 from independently sourced families and a capability taxonomy.",
            "required_strata": [
                "unsupported cabin climate/defog",
                "unsupported driving automation and lateral motion",
                "impossible/external capability",
                "mixed supported+unsupported commands",
                "mixed-polarity MULTI with varied connectors and ASR-style concatenation",
                "double-negation and vague-reference ambiguity",
                "relative, percentage, Chinese-proportion, absolute, fuzzy, and extreme VALUE forms",
                "sentence/slot negation cross-head consistency families",
            ],
            "split_policy": split_policy,
            "model_research_only_after_data_freeze": [
                "add an explicit OOD/reject pathway beyond Scope-only rejection",
                "evaluate intent-level unknown energy/reject objectives without using Test-v1 for selection",
                "evaluate sentence-slot negation consistency loss or calibrated fusion on new Validation-v3",
                "compare backbones under an identical frozen v3 protocol",
            ],
            "new_test_policy": "Seal Test-v3 until data, protocol, checkpoints, and selection are frozen; evaluate it once.",
            "safety_gold_policy": "Keep current Safety Gold sealed until a future candidate passes the ordinary new locked test and an explicitly approved final safety stage begins.",
        },
        "minimum_support_policy": split_policy,
        "TRAINING_STEPS_EXECUTED_THIS_STAGE": 0,
        "SAFETY_GOLD_EVALUATION_EXECUTED": "NO",
    }

    postmortem_md = f"""# SYS-014 Stage 4D-A.1 Locked Test 泛化失败根因审计

## 决策结论

Locked Test-v1 已打开且永久视为 burned。当前 ELECTRA exp002 epoch 9 的失败不是单一模型问题，而是 **split、覆盖、闭集 OOD 架构和局部训练目标共同形成的 MIXED 泛化失败**。frozen v2 不应修改，但也不再适合作为最终 safety-model selection 的权威 split。

- Validation UNKNOWN_CONTROL = {val_unknown}/129 ({ratio(val_unknown, 129):.3%})；Test = {test_unknown}/133 ({ratio(test_unknown, 133):.3%})。
- Test/Validation UNKNOWN count support 比为 {test_unknown / val_unknown:.0f}x，prevalence 比为 {imbalance['test_to_validation_prevalence_ratio']:.2f}x。
- Test UNKNOWN 29 条全部为 TEST_ASSET；Validation 唯一 UNKNOWN 为 SYNTHETIC_TEMPLATE。
- 17 条 UNKNOWN unsafe false accept 的 intent 映射：{', '.join(f'{key}={value}' for key, value in intent_counts.items())}。
- MULTI 23 条中 20 条正确 abstain，3 条误放均集中在 mixed-polarity/compositional held-out families。
- 唯一 AMBIGUOUS 误放是双重否定，与 Validation 0731/0732/0733 的模糊指代 family 不同。
- Test VALUE 16 条中没有检测 miss，但 12 条是相对表达 span boundary error；因此 F1 从 Validation 0.842105 降至 Test 0.25。
- Sentence Negation 的 6 条 FN 全部是 WINDOW_SET_POSITION 同一 held-out split group，且 6/6 的 NEGATION Slot signal 正确。

## UNKNOWN split 根因

`UNKNOWN_SPLIT_IMBALANCE_ROOT_CAUSE = F (A + B + D)`：

1. A：零 family/template/mechanical leakage 要求使连接组不可拆分；重建后的跨 split group 数为 0。
2. B：TEST_ASSET group 先被强制分配到 Test，之后才做 group-aware balance；Validation 的 UNKNOWN 硬下限只有 1。
3. D：Test 被有意用作真实 TEST_ASSET stress distribution，29 条 UNKNOWN 全在 Test。

C 不是主因：全量有 54 条 UNKNOWN（Train/Val/Test = 24/1/29）。E 也没有证据：frozen assignments、split reports、leakage audit 与 group 重建结果一致。

## 架构与错误层级

`CLOSED_SET_INTENT_FORCING_RISK = YES`。Intent head 只有 7 个已知类，UNKNOWN 等标签在训练中被 mask；Scope 一旦将 unsupported SINGLE 错判为 IN_SCOPE_CONTROL，Intent head 必然吸附到某个已知 intent。

`OOD_REJECTION_SINGLE_POINT_OF_FAILURE = YES`。对普通 unsupported SINGLE，Structure 没有拒绝理由，Intent 又没有 reject 类，因此 Scope 是唯一直接 OOD 拒绝点。这是当前架构事实，不是本次审计发现的实现 bug。

| 问题层 | 评级 | 核心证据 |
|---|---|---|
{chr(10).join(f"| {key} | {value['rating']} | {value['evidence']} |" for key, value in issue_layers.items())}

## v2 数据集适用性

`CURRENT_V2_SPLIT_SUITABLE_FOR_FINAL_MODEL_SELECTION = NO`。

v2 的零泄漏目标达成，仍可保留为 PoC、回归和历史分析集；但 Validation UNKNOWN=1 使任何 UNKNOWN recall/UFAR 选择极不稳定，也不能代表 Test 的独立 capability families。因此不能继续把该 Validation 当作可靠的最终安全模型选择代理。

## NLU Development Cycle 2（仅设计，不执行）

1. Test-v1 只保留为 burned historical postmortem set；不得再宣称它是 unseen final test。
2. 建立新的 capability taxonomy 和独立 family 来源，冻结 Train-v3/Validation-v3/Test-v3。
3. 保持 family/template/mechanical/split_group leakage=0；Validation 至少 UNKNOWN 20、NON_CONTROL 15、AMBIGUOUS 15、MULTI 20，且 unique should-abstain 至少 70；Test 对应至少 30/20/20/30，unique should-abstain 至少 100。
4. Validation 每个安全子类至少 8 个独立 split groups，Test 至少 10--12 个；任一 family 不超过该安全子类的 20%。
5. 若类别支持与零泄漏冲突，优先零泄漏并新增独立 families；不得拆 family 凑数，也不得降低评估主张之外仍声称完整安全覆盖。
6. 数据与协议冻结后，才在新 Validation 上评估显式 OOD/reject 路径、intent-level reject objective、sentence-slot consistency 和同协议 backbone 对照。
7. Test-v3 在数据、协议、checkpoint 与选择全部冻结后只打开一次。

## Safety Gold

`SAFETY_GOLD_SHOULD_REMAIN_SEALED = YES`。普通 Locked Test 已明确失败，打开 Safety Gold 不会改变 `DEPLOYABLE=false`，只会消耗最后一个独立安全评估资产。

## Required final fields

```text
TEST_V1_BURNED = YES
UNKNOWN_VALIDATION_SUPPORT = {val_unknown}
UNKNOWN_TEST_SUPPORT = {test_unknown}
UNKNOWN_SPLIT_IMBALANCE_ROOT_CAUSE = F: A + B + D
CLOSED_SET_INTENT_FORCING_RISK = YES
OOD_REJECTION_SINGLE_POINT_OF_FAILURE = YES
GENERALIZATION_FAILURE_LEVEL = MIXED
CURRENT_V2_SPLIT_SUITABLE_FOR_FINAL_MODEL_SELECTION = NO
DATASET_SPLIT_PROBLEM = HIGH
DATA_COVERAGE_PROBLEM = HIGH
MODEL_CAPACITY_PROBLEM = MEDIUM
MULTITASK_ARCHITECTURE_PROBLEM = HIGH
CLOSED_SET_OOD_PROBLEM = HIGH
TRAINING_OBJECTIVE_PROBLEM = MEDIUM
SAFETY_GOLD_SHOULD_REMAIN_SEALED = YES
RECOMMENDED_NEXT_STAGE = NLU_DEVELOPMENT_CYCLE_2
TRAINING_STEPS_EXECUTED_THIS_STAGE = 0
SAFETY_GOLD_EVALUATION_EXECUTED = NO
```

本阶段未训练、未推理、未改 frozen v2/runtime/safety gate/threshold/checkpoint，也未读取 Safety Gold。
"""

    POSTMORTEM_DIR.mkdir(parents=True, exist_ok=False)
    write_json(POSTMORTEM_DIR / "split_distribution_audit.json", distribution_audit)
    (POSTMORTEM_DIR / "split_distribution_audit.md").write_text(markdown_distribution(distributions, imbalance, coverage), encoding="utf-8")
    write_json(POSTMORTEM_DIR / "unknown_false_accept_analysis.json", unknown_analysis)
    write_json(POSTMORTEM_DIR / "multi_failure_analysis.json", multi_analysis)
    write_json(POSTMORTEM_DIR / "value_generalization_analysis.json", value_report)
    write_json(POSTMORTEM_DIR / "negation_generalization_analysis.json", neg_report)
    write_json(POSTMORTEM_DIR / "generalization_root_cause.json", root)
    (POSTMORTEM_DIR / "stage4d_a1_postmortem.md").write_text(postmortem_md, encoding="utf-8")
    print(json.dumps({"status": "PASS", "output_dir": str(POSTMORTEM_DIR), "files": sorted(path.name for path in POSTMORTEM_DIR.iterdir()), "training_steps": 0, "safety_gold_evaluation": "NO"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
