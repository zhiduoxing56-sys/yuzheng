"""Create immutable SYS-014 PoC7 v2 with refined synthetic families and balanced groups."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import freeze_sys014_poc7 as v1


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = v1.CANDIDATE_PATH
SAFETY_PATH = v1.SAFETY_PATH
REGISTRY_PATH = v1.REGISTRY_PATH
SCHEMA_PATH = v1.SCHEMA_PATH
GUIDELINES_PATH = v1.GUIDELINES_PATH
FROZEN_PARENT = v1.FROZEN_PARENT
PARENT_PATH = FROZEN_PARENT / "sys014-poc7-v1"
DATASET_NAME = v1.DATASET_NAME
DATASET_VERSION = "sys014-poc7-v2"
PARENT_DATASET_VERSION = "sys014-poc7-v1"
SOURCE_CANDIDATE_VERSION = "sys014-stage3b1-final-849"
SPLIT_SEED = 14032
POC_INTENTS = v1.POC_INTENTS
SPLITS = v1.SPLITS
TARGET_RATIOS = v1.TARGET_RATIOS
NEGATED_TRAIN_FLOORS = {intent: (4 if intent == "DOOR_OPEN" else 8) for intent in POC_INTENTS}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return v1.load_jsonl(path)


def jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return v1.jsonl_bytes(rows)


def sha256_bytes(value: bytes) -> str:
    return v1.sha256_bytes(value)


def sha256_file(path: Path) -> str:
    return v1.sha256_file(path)


def normalized_text(text: str) -> str:
    return v1.normalized_text(text)


def template_signature(row: dict[str, Any]) -> str:
    return v1.template_signature(row)


def mechanical_signature(row: dict[str, Any]) -> str:
    return v1.mechanical_signature(row)


def parent_hashes() -> dict[str, str]:
    if not PARENT_PATH.is_dir():
        raise RuntimeError(f"missing immutable parent dataset: {PARENT_PATH}")
    return {path.name: sha256_file(path) for path in sorted(PARENT_PATH.iterdir()) if path.is_file()}


def refine_synthetic_families(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Split only over-broad synthetic families by their true mechanical template."""
    refined = copy.deepcopy(rows)
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in refined:
        if row["source_ref"]["source_type"] == "SYNTHETIC_TEMPLATE":
            by_family[row["paraphrase_family_id"]].append(row)

    changes: list[dict[str, str]] = []
    for old_family, family_rows in sorted(by_family.items()):
        signatures = {mechanical_signature(row) for row in family_rows}
        if len(signatures) <= 1:
            continue
        for row in family_rows:
            signature = mechanical_signature(row)
            digest = hashlib.sha256(f"{old_family}|{signature}".encode("utf-8")).hexdigest()[:16].upper()
            new_family = f"PF_V2_SYN_{digest}"
            if new_family == old_family:
                continue
            row["paraphrase_family_id"] = new_family
            changes.append({
                "sample_id": row["sample_id"],
                "before": old_family,
                "after": new_family,
                "reason": "原 SYNTHETIC_TEMPLATE family 含多个真实机械模板；按 slot-aware mechanical signature 细分",
            })
    return refined, sorted(changes, key=lambda item: item["sample_id"])


def build_groups(rows: list[dict[str, Any]]) -> list[v1.SplitGroup]:
    return v1.build_groups(rows)


def group_vector(group: v1.SplitGroup) -> Counter[str]:
    values: Counter[str] = Counter()
    for row in group.rows:
        values["total"] += 1
        values[f"structure:{row['intent_structure']}"] += 1
        values[f"scope:{row['scope_label']}"] += 1
        values[f"source:{row['source_ref']['source_type']}"] += 1
        for slot in row.get("slots", []):
            values[f"slot:{slot['slot_type']}"] += 1
        if row["intent_structure"] == "SINGLE" and row["scope_label"] == "IN_SCOPE_CONTROL":
            mode = "neg" if row.get("negated") else "pos"
            values[f"{mode}:{row['intent']}"] += 1
            if row["intent"] == "WINDOW_SET_POSITION" and any(slot["slot_type"] == "VALUE" for slot in row.get("slots", [])):
                values["wsp_value"] += 1
            if row["intent"] == "WINDOW_OPEN" and any(slot["slot_type"] == "VALUE" for slot in row.get("slots", [])):
                values["window_open_value"] += 1
        if row["intent_structure"] == "MULTI":
            for segment in row.get("segments", []):
                if segment.get("intent") in POC_INTENTS:
                    values[f"multi:{segment['intent']}"] += 1
    return values


def minimum_requirements() -> dict[str, dict[str, int]]:
    requirements = {split: {} for split in SPLITS}
    for intent in POC_INTENTS:
        requirements["TRAIN"][f"pos:{intent}"] = 30
        requirements["VALIDATION"][f"pos:{intent}"] = 5
        requirements["TEST"][f"pos:{intent}"] = 5
        # DOOR_OPEN has only four non-TEST-ASSET negated samples; all other negated
        # examples are in true near-duplicate groups forced to TEST.
        requirements["TRAIN"][f"neg:{intent}"] = NEGATED_TRAIN_FLOORS[intent]
    for split in SPLITS:
        for structure in ("SINGLE", "MULTI", "AMBIGUOUS"):
            requirements[split][f"structure:{structure}"] = 1
        for scope in ("IN_SCOPE_CONTROL", "NON_CONTROL", "UNKNOWN_CONTROL", "AMBIGUOUS_CONTROL"):
            requirements[split][f"scope:{scope}"] = 1
        requirements[split]["slot:AREA"] = 1
        requirements[split]["slot:NEGATION"] = 1
    requirements["VALIDATION"]["wsp_value"] = 1
    requirements["TEST"]["wsp_value"] = 1
    return requirements


def desired_coverage() -> dict[str, dict[str, int]]:
    """Soft targets that must never cause a true leakage group to be broken."""
    desired = {split: {} for split in SPLITS}
    for intent in POC_INTENTS:
        desired["TRAIN"][f"neg:{intent}"] = 8
        desired["VALIDATION"][f"neg:{intent}"] = 2
        desired["TEST"][f"neg:{intent}"] = 2
        desired["TRAIN"][f"multi:{intent}"] = 1
        desired["VALIDATION"][f"multi:{intent}"] = 2
        desired["TEST"][f"multi:{intent}"] = 2
    return desired


def stable_order(group: v1.SplitGroup) -> str:
    return hashlib.sha256(f"{SPLIT_SEED}:{group.group_id}".encode("utf-8")).hexdigest()


def add_vector(target: Counter[str], vector: Counter[str], factor: int = 1) -> None:
    for key, value in vector.items():
        target[key] += factor * value
        if target[key] == 0:
            del target[key]


def assignment_state(
    groups: list[v1.SplitGroup], assignments: dict[str, str], vectors: dict[str, Counter[str]],
) -> dict[str, Counter[str]]:
    state = {split: Counter() for split in SPLITS}
    for group in groups:
        split = assignments.get(group.group_id)
        if split:
            add_vector(state[split], vectors[group.group_id])
    return state


def hard_deficits(state: dict[str, Counter[str]]) -> list[tuple[str, str, int]]:
    return [
        (split, key, minimum - state[split][key])
        for split, items in minimum_requirements().items()
        for key, minimum in items.items()
        if state[split][key] < minimum
    ]


def score_state(state: dict[str, Counter[str]], totals: Counter[str]) -> float:
    score = 0.0
    total_rows = totals["total"]
    for split in SPLITS:
        target = total_rows * TARGET_RATIOS[split]
        score += 350.0 * ((state[split]["total"] - target) / max(1.0, target)) ** 2

    weights: dict[str, float] = {}
    for intent in POC_INTENTS:
        weights[f"pos:{intent}"] = 130.0
        weights[f"neg:{intent}"] = 150.0
        weights[f"multi:{intent}"] = 55.0
    for key in totals:
        if key.startswith("structure:"):
            weights[key] = 12.0
        elif key.startswith("scope:"):
            weights[key] = 14.0
        elif key.startswith("slot:"):
            weights[key] = 8.0
    weights["wsp_value"] = 25.0
    for key, weight in weights.items():
        feature_total = totals[key]
        if not feature_total:
            continue
        for split in SPLITS:
            target = feature_total * TARGET_RATIOS[split]
            score += weight * ((state[split][key] - target) / max(1.0, feature_total)) ** 2

    for split, key, deficit in hard_deficits(state):
        minimum = minimum_requirements()[split][key]
        score += 1_000_000.0 * (deficit / max(1, minimum)) ** 2
    for split, items in desired_coverage().items():
        for key, minimum in items.items():
            if state[split][key] < minimum:
                score += 650.0 * ((minimum - state[split][key]) / max(1, minimum)) ** 2
    return score


def assign_groups(groups: list[v1.SplitGroup]) -> dict[str, str]:
    vectors = {group.group_id: group_vector(group) for group in groups}
    totals: Counter[str] = Counter()
    for vector in vectors.values():
        add_vector(totals, vector)
    assignments = {group.group_id: "TEST" for group in groups if group.forced_test}
    state = assignment_state(groups, assignments, vectors)
    unassigned = {group.group_id: group for group in groups if group.group_id not in assignments}
    requirements = minimum_requirements()

    # Reserve scarce validation/test supervision before filling the much larger train share.
    for split in ("VALIDATION", "TEST", "TRAIN"):
        while True:
            deficits = {key: minimum - state[split][key] for key, minimum in requirements[split].items() if state[split][key] < minimum}
            if not deficits:
                break
            candidates = []
            for group in unassigned.values():
                vector = vectors[group.group_id]
                gain = sum(
                    min(vector[key], deficit) / max(1, requirements[split][key])
                    for key, deficit in deficits.items()
                )
                if gain <= 0:
                    continue
                overflow = max(0.0, state[split]["total"] + group.size - totals["total"] * TARGET_RATIOS[split])
                candidates.append((gain / math.sqrt(group.size), -overflow, -group.size, stable_order(group), group))
            if not candidates:
                break
            selected = max(candidates, key=lambda item: item[:4])[-1]
            assignments[selected.group_id] = split
            add_vector(state[split], vectors[selected.group_id])
            del unassigned[selected.group_id]

    # Fill remaining groups by deterministic global stratification cost.
    for group in sorted(unassigned.values(), key=lambda item: (-item.size, stable_order(item))):
        options = []
        for split in SPLITS:
            add_vector(state[split], vectors[group.group_id])
            options.append((score_state(state, totals), split))
            add_vector(state[split], vectors[group.group_id], -1)
        selected_split = min(options, key=lambda item: (item[0], item[1]))[1]
        assignments[group.group_id] = selected_split
        add_vector(state[selected_split], vectors[group.group_id])

    if hard_deficits(state):
        raise RuntimeError(f"BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT: {hard_deficits(state)}")

    # Deterministic single-group local improvement; hard constraints are invariants.
    for _ in range(500):
        current_score = score_state(state, totals)
        best: tuple[float, str, str, str] | None = None
        for group in sorted(groups, key=stable_order):
            if group.forced_test:
                continue
            donor = assignments[group.group_id]
            vector = vectors[group.group_id]
            for recipient in SPLITS:
                if recipient == donor:
                    continue
                add_vector(state[donor], vector, -1)
                add_vector(state[recipient], vector)
                candidate_score = score_state(state, totals)
                feasible = not hard_deficits(state)
                add_vector(state[recipient], vector, -1)
                add_vector(state[donor], vector)
                if feasible and candidate_score + 1e-12 < current_score:
                    item = (candidate_score, group.group_id, donor, recipient)
                    if best is None or item < best:
                        best = item
        if best is None:
            break
        _, group_id, donor, recipient = best
        add_vector(state[donor], vectors[group_id], -1)
        add_vector(state[recipient], vectors[group_id])
        assignments[group_id] = recipient

    if len(assignments) != len(groups):
        raise RuntimeError("not every split group was assigned")
    if any(group.forced_test and assignments[group.group_id] != "TEST" for group in groups):
        raise RuntimeError("TEST_ASSET group escaped TEST")
    if hard_deficits(state):
        raise RuntimeError(f"BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT: {hard_deficits(state)}")
    return assignments


def split_rows(
    groups: list[v1.SplitGroup], assignments: dict[str, str],
) -> dict[str, list[dict[str, Any]]]:
    return v1.split_rows(groups, assignments)


def intent_coverage(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    return v1.intent_coverage(rows)


def split_statistics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return v1.split_statistics(rows)


def leakage_metrics(
    rows_by_split: dict[str, list[dict[str, Any]]],
    groups: list[v1.SplitGroup],
    assignments: dict[str, str],
) -> dict[str, int]:
    return v1.leakage_metrics(rows_by_split, groups, assignments)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    return v1.markdown_table(headers, rows)


def load_parent_rows() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    rows: dict[str, dict[str, Any]] = {}
    splits: dict[str, str] = {}
    for split, name in (("TRAIN", "train.jsonl"), ("VALIDATION", "validation.jsonl"), ("TEST", "test.jsonl")):
        for row in load_jsonl(PARENT_PATH / name):
            rows[row["sample_id"]] = row
            splits[row["sample_id"]] = split
    return rows, splits


def group_label_counts(group: v1.SplitGroup) -> tuple[str, int, int]:
    intents: Counter[str] = Counter()
    positive = 0
    negated = 0
    for row in group.rows:
        if row["intent_structure"] == "SINGLE" and row.get("intent"):
            intents[row["intent"]] += 1
            if row.get("negated"):
                negated += 1
            else:
                positive += 1
        for segment in row.get("segments", []):
            if segment.get("intent"):
                intents[segment["intent"]] += 1
    label = ", ".join(f"{key}:{value}" for key, value in intents.most_common()) or "无 PoC Intent"
    return label, positive, negated


def create_balance_diagnosis() -> str:
    parent_rows, parent_splits = load_parent_rows()
    groups = build_groups(list(parent_rows.values()))
    largest = sorted(groups, key=lambda group: (-group.size, group.group_id))[:20]
    top_rows = []
    for group in largest:
        label, positive, negated = group_label_counts(group)
        top_rows.append([
            group.group_id, parent_splits[group.rows[0]["sample_id"]], group.size,
            len({row["paraphrase_family_id"] for row in group.rows}),
            len({mechanical_signature(row) for row in group.rows}),
            sum(row["source_ref"]["source_type"] == "TEST_ASSET" for row in group.rows),
            label, positive, negated,
        ])

    window_groups = []
    for group in sorted(groups, key=lambda item: (-item.size, item.group_id)):
        count = sum(
            row.get("intent") == "WINDOW_OPEN" and row["intent_structure"] == "SINGLE" and row.get("negated") is False
            for row in group.rows
        )
        if count:
            coarse_families = sum(
                len({mechanical_signature(row) for row in group.rows if row["paraphrase_family_id"] == family}) > 1
                for family in {row["paraphrase_family_id"] for row in group.rows}
            )
            window_groups.append([
                group.group_id, parent_splits[group.rows[0]["sample_id"]], count, group.size,
                sum(row["source_ref"]["source_type"] == "TEST_ASSET" for row in group.rows),
                len({row["paraphrase_family_id"] for row in group.rows}), coarse_families,
            ])

    return "\n".join([
        "# sys014-poc7-v1 split group 失衡诊断", "",
        "## 结论", "",
        "v1 的极端失衡来自过粗 family 边的传递闭包，而不是随机种子。最大 group `SGRP-2431BE8F1C028D5E` 含 46 条 WINDOW_OPEN positive、12 个 family 和 1 条 TEST_ASSET；该 TEST_ASSET 使整个连通分量强制进入 TEST。另一个 7 条 WINDOW_OPEN positive 的 group 同样由 1 条 TEST_ASSET 锁入 TEST。加上其他小组，最终形成 WINDOW_OPEN positive 的 4/2/54 分布。", "",
        "问题根因是部分 SYNTHETIC_TEMPLATE family 同时包含多个明显不同的 mechanical signature。v1 将 family 作为无条件 DSU 边，再与 template/mechanical 边传递合并，因此本来可独立切分的不同表达被绑在一起。v2 仅细分这种合成 family；AREA/VALUE/NEGATION 替换相同、只含礼貌词差异或真实 template/mechanical 近重复的样本仍保持同组。", "",
        "## WINDOW_OPEN positive 所在 v1 groups", "",
        markdown_table(
            ["Group", "v1 split", "WINDOW_OPEN +", "样本", "TEST_ASSET", "Family", "过粗 family"],
            window_groups,
        ), "",
        "## TOP 20 largest split groups", "",
        markdown_table(
            ["Group", "v1 split", "样本", "Family", "Mechanical", "TEST_ASSET", "Intent mentions", "positive", "negated"],
            top_rows,
        ), "",
        "## v2 处理原则", "",
        "- TEST_ASSET 的 source_type、文本、标签和 family 不变。",
        "- 只细分内部包含多个 mechanical signature 的 SYNTHETIC_TEMPLATE family。",
        "- 细分后继续以 refined family、template signature、mechanical signature 构造 DSU；零泄漏优先于比例平衡。",
        "- Safety Gold 不参与诊断后的 split optimization。", "",
    ])


def create_split_report(
    stats: dict[str, dict[str, Any]], group_counts: dict[str, int], family_counts: dict[str, int],
    groups: list[v1.SplitGroup],
) -> str:
    intent_rows = []
    for intent in POC_INTENTS:
        row: list[Any] = [intent]
        for split in SPLITS:
            values = stats[split]["intent_coverage"][intent]
            row.extend([values["positive_single"], values["negated_single"], values["multi_segment_mentions"]])
        intent_rows.append(row)
    total = sum(stats[split]["count"] for split in SPLITS)
    lines = [
        f"# {DATASET_VERSION} 切分报告", "", "## 切分规模", "",
        markdown_table(
            ["Split", "样本", "Family", "Split group", "比例"],
            [[split, stats[split]["count"], family_counts[split], group_counts[split], f"{stats[split]['count'] / total:.2%}"] for split in SPLITS],
        ), "", "## 7-Intent 覆盖", "",
        markdown_table(
            ["Intent", "TRAIN +", "TRAIN -", "TRAIN MULTI", "VAL +", "VAL -", "VAL MULTI", "TEST +", "TEST -", "TEST MULTI"],
            intent_rows,
        ), "",
    ]
    for dimension, title in (("intent_structure", "Intent structure"), ("scope", "Scope"), ("slots", "Slots"), ("source_type", "Source type"), ("semantic_type", "语义安全类型"), ("unknown_control_derived", "UNKNOWN_CONTROL 派生类型")):
        keys = sorted(set().union(*(stats[split][dimension] for split in SPLITS)))
        lines.extend([f"## {title}", "", markdown_table(["类别", *SPLITS], [[key, *(stats[split][dimension].get(key, 0) for split in SPLITS)] for key in keys]), ""])
    negated_rows = []
    for intent in POC_INTENTS:
        actual = [stats[split]["intent_coverage"][intent]["negated_single"] for split in SPLITS]
        pattern = []
        for group in groups:
            count = group_vector(group)[f"neg:{intent}"]
            if count:
                pattern.append(f"{count}{'*' if group.forced_test else ''}")
        met = actual[0] >= 8 and actual[1] >= 2 and actual[2] >= 2
        reason = "PASS" if met else f"BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT；不可拆 group={'+'.join(pattern)}（* 为 TEST_ASSET forced TEST）"
        negated_rows.append([intent, *actual, reason])
    lines.extend([
        "## Negated 8/2/2 目标与合法 group 约束", "",
        markdown_table(["Intent", "TRAIN -", "VAL -", "TEST -", "结论"], negated_rows), "",
        "同一机械模板仅替换 AREA/NEGATION 的样本不得跨 split。因而只有两个不可拆 group 的 Intent 不可能同时覆盖三个 split；此处保留零泄漏，未为满足数字拆组。", "",
    ])
    lines.extend([
        "## 质量结论", "",
        "- v1 的 WINDOW_OPEN、HEADLIGHT_OFF、ACCELERATE、BRAKE 极端 split 失衡已通过合法 group 重建修正。",
        "- 每个 Intent 的 positive SINGLE 满足 TRAIN/VALIDATION/TEST 至少 30/5/5。",
        "- negated SINGLE 以 8/2/2 为软目标；不可满足项已逐 Intent 给出真实 group 约束原因。",
        "- WINDOW_SET_POSITION 在 VALIDATION 与 TEST 均有 VALUE；WINDOW_OPEN 的 VALUE slot 为 0。",
        "- TEST_ASSET_IN_TRAIN=0；Safety Gold 未参与切分优化。", "",
    ])
    return "\n".join(lines)


def create_leakage_report(metrics: dict[str, int], assignment_digest: str) -> str:
    return "\n".join([
        f"# {DATASET_VERSION} 泄漏审计", "",
        markdown_table(["检查项", "计数", "结果"], [[key, value, "PASS" if value == 0 else "FAIL"] for key, value in metrics.items()]), "",
        f"- split group assignment digest: `{assignment_digest}`",
        "- 分组边：refined synthetic family、slot-aware template signature、mechanical near-duplicate signature。",
        "- TEST_ASSET group 强制进入 TEST；Safety Gold 完全不参与切分优化。",
        "- 所有泄漏指标为 0。", "",
    ])


def create_diff(
    rows_by_split: dict[str, list[dict[str, Any]]], family_changes: list[dict[str, str]],
) -> str:
    _, before_split = load_parent_rows()
    after_split = {row["sample_id"]: split for split, rows in rows_by_split.items() for row in rows}
    directions: dict[str, list[str]] = defaultdict(list)
    for sample_id in sorted(before_split):
        before, after = before_split[sample_id], after_split[sample_id]
        if before != after:
            directions[f"{before} → {after}"].append(sample_id)
    lines = [
        "# sys014-poc7-v1 → sys014-poc7-v2 split 差异", "",
        "本报告只记录 split 与允许的 SYNTHETIC_TEMPLATE family 元数据变化；text、sample_id、语义标签和 Safety Gold 均未改变。", "",
        "## Split 变化汇总", "",
        markdown_table(["方向", "数量"], [[key, len(directions.get(key, []))] for key in (
            "TRAIN → VALIDATION", "TRAIN → TEST", "VALIDATION → TRAIN", "VALIDATION → TEST", "TEST → TRAIN", "TEST → VALIDATION"
        )]), "",
    ]
    for direction in ("TRAIN → VALIDATION", "TRAIN → TEST", "VALIDATION → TRAIN", "VALIDATION → TEST", "TEST → TRAIN", "TEST → VALIDATION"):
        lines.extend([f"### {direction}", "", ", ".join(f"`{sample_id}`" for sample_id in directions.get(direction, [])) or "无", ""])
    lines.extend([
        "## paraphrase_family_id 细分", "",
        f"共 {len(family_changes)} 条 SYNTHETIC_TEMPLATE 样本发生允许的 family 元数据细分。", "",
        markdown_table(["sample_id", "修改前", "修改后", "原因"], [[item["sample_id"], item["before"], item["after"], item["reason"]] for item in family_changes]), "",
    ])
    return "\n".join(lines)


def create_readme(counts: dict[str, int], family_change_count: int) -> str:
    return f"""# {DATASET_VERSION}

这是 SYS-014 的第二个不可变 7-Intent PoC 冻结版本，parent 为 `{PARENT_DATASET_VERSION}`。它使用同一批 {counts['candidate']} 条 candidate 和 {counts['safety']} 条独立 Safety Gold，主要修正 v1 的 split group 粗粒度与类别失衡；不是一次重新人工标注。

## 不可变与用途边界

1. v1 永久保留且未修改；v2 也禁止原地覆盖。
2. text、sample_id、intent、scope、structure、slots、segments、negated、safety_tags 均与 Stage 3B.1 source candidate 一致。
3. 仅有 {family_change_count} 条 `SYNTHETIC_TEMPLATE` 的 `paraphrase_family_id` 因过粗 family 被确定性细分；所有变化见 `v1_to_v2_split_diff.md`。
4. `TEST_ASSET` 不进入 TRAIN，其 source_type 与 family 未修改。
5. Safety Gold 未参与 split optimization，不得用于训练、early stopping、模型/阈值选择或校准。
6. split 单位为 refined family + template signature + mechanical signature 的 DSU 连通分量，固定 `split_seed={SPLIT_SEED}`。
7. 生成工具为 `scripts/freeze_sys014_poc7_v2.py`，验证工具为 `scripts/validate_sys014_frozen_v2.py`。
8. 本阶段不训练、不切分 Safety Gold、不修改 runtime；`READY_FOR_MODEL_TRAINING` 固定为 `NO`。

## 文件

- `train.jsonl`、`validation.jsonl`、`test.jsonl`
- `safety_gold.jsonl`
- `dataset_manifest.json`
- `split_report.md`
- `leakage_audit.md`
- `split_group_balance_diagnosis.md`
- `v1_to_v2_split_diff.md`
- `README.md`
"""


def prepare() -> tuple[
    list[v1.SplitGroup], dict[str, str], dict[str, list[dict[str, Any]]],
    list[dict[str, Any]], list[dict[str, str]], dict[str, Any],
]:
    source_candidate = load_jsonl(CANDIDATE_PATH)
    safety = load_jsonl(SAFETY_PATH)
    if len(source_candidate) != 849 or len(safety) != 60:
        raise RuntimeError(f"unexpected source counts: candidate={len(source_candidate)}, safety={len(safety)}")
    candidate, changes = refine_synthetic_families(source_candidate)
    groups = build_groups(candidate)
    assignments = assign_groups(groups)
    rows_by_split = split_rows(groups, assignments)
    stats = {split: split_statistics(rows_by_split[split]) for split in SPLITS}
    metrics = leakage_metrics(rows_by_split, groups, assignments)
    return groups, assignments, rows_by_split, safety, changes, {"statistics": stats, "leakage": metrics}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=FROZEN_PARENT / DATASET_VERSION)
    args = parser.parse_args()
    target = args.output.resolve()
    expected = (FROZEN_PARENT / DATASET_VERSION).resolve()
    if target != expected:
        raise RuntimeError(f"v2 must be frozen at {expected}")
    if target.exists():
        raise RuntimeError(f"immutable target already exists; refusing overwrite: {target}")

    baseline_parent_hashes = parent_hashes()
    groups, assignments, rows_by_split, safety, changes, prepared = prepare()
    metrics = prepared["leakage"]
    if any(metrics.values()):
        raise RuntimeError(f"leakage audit failed before freeze: {metrics}")
    stats = prepared["statistics"]
    group_counts = Counter(assignments.values())
    family_counts = {split: len({row["paraphrase_family_id"] for row in rows_by_split[split]}) for split in SPLITS}
    assignment_digest = sha256_bytes("\n".join(f"{key}:{assignments[key]}" for key in sorted(assignments)).encode("utf-8"))

    staging = FROZEN_PARENT / f".{DATASET_VERSION}.staging"
    if staging.exists():
        resolved = staging.resolve()
        if resolved.parent != FROZEN_PARENT.resolve() or resolved.name != f".{DATASET_VERSION}.staging":
            raise RuntimeError(f"unsafe staging path: {resolved}")
        shutil.rmtree(resolved)
    staging.mkdir(parents=True)
    try:
        data_files = {
            "train.jsonl": rows_by_split["TRAIN"],
            "validation.jsonl": rows_by_split["VALIDATION"],
            "test.jsonl": rows_by_split["TEST"],
            "safety_gold.jsonl": safety,
        }
        for name, rows in data_files.items():
            (staging / name).write_bytes(jsonl_bytes(rows))
        reports = {
            "split_report.md": create_split_report(stats, group_counts, family_counts, groups),
            "leakage_audit.md": create_leakage_report(metrics, assignment_digest),
            "split_group_balance_diagnosis.md": create_balance_diagnosis(),
            "v1_to_v2_split_diff.md": create_diff(rows_by_split, changes),
            "README.md": create_readme({"candidate": 849, "safety": 60}, len(changes)),
        }
        for name, value in reports.items():
            (staging / name).write_text(value, encoding="utf-8")

        artifact_names = [*data_files, *reports]
        file_hashes = {
            "data/nlu/spec/intent_registry_draft.yaml": sha256_file(REGISTRY_PATH),
            "data/nlu/spec/annotation_schema.json": sha256_file(SCHEMA_PATH),
            "data/nlu/spec/annotation_guidelines.md": sha256_file(GUIDELINES_PATH),
            "data/nlu/poc/candidate_pool.jsonl": sha256_file(CANDIDATE_PATH),
            "data/nlu/poc/safety_gold_candidates.jsonl": sha256_file(SAFETY_PATH),
            **{name: sha256_file(staging / name) for name in artifact_names},
        }
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        manifest = {
            "dataset_name": DATASET_NAME,
            "dataset_version": DATASET_VERSION,
            "parent_dataset_version": PARENT_DATASET_VERSION,
            "source_candidate_version": SOURCE_CANDIDATE_VERSION,
            "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
            "immutable": True,
            "poc_intents": POC_INTENTS,
            "registry_version": "sys-014-stage2.1-draft-2",
            "annotation_schema_id": schema["$id"],
            "split_seed": SPLIT_SEED,
            "split_strategy": "group-aware stratified greedy assignment plus deterministic local improvement; leakage constraints precede balance",
            "target_ratios": TARGET_RATIOS,
            "minimum_coverage": minimum_requirements(),
            "desired_coverage": desired_coverage(),
            "grouping_strategy": {
                "unit": "split_group_id",
                "algorithm": "DSU connected components after permitted SYNTHETIC_TEMPLATE family refinement",
                "edges": ["refined_paraphrase_family_id", "template_signature_v1", "mechanical_signature_v1"],
                "family_refinement_rule": "only over-broad SYNTHETIC_TEMPLATE families; bucket by slot-aware mechanical signature",
                "family_refined_sample_count": len(changes),
                "split_group_assignment_digest_sha256": assignment_digest,
            },
            "source_candidate_count": 849,
            "source_safety_gold_count": 60,
            "train_count": stats["TRAIN"]["count"],
            "validation_count": stats["VALIDATION"]["count"],
            "test_count": stats["TEST"]["count"],
            "safety_gold_count": 60,
            "train_family_count": family_counts["TRAIN"],
            "validation_family_count": family_counts["VALIDATION"],
            "test_family_count": family_counts["TEST"],
            "train_split_group_count": group_counts["TRAIN"],
            "validation_split_group_count": group_counts["VALIDATION"],
            "test_split_group_count": group_counts["TEST"],
            "statistics": stats,
            "leakage_audit": metrics,
            "parent_integrity_sha256": baseline_parent_hashes,
            "file_sha256": file_hashes,
            "safety_gold_policy": "byte-equivalent isolated final safety regression; excluded from split optimization, training, validation and model selection",
            "stage_flags": {
                "POC_DATASET_V2_FROZEN": True,
                "POC_SPLIT_BALANCE_PASS": True,
                "POC_SPLIT_REPRODUCIBLE": True,
                "POC_LEAKAGE_AUDIT_PASS": True,
                "READY_FOR_MODEL_SELECTION": True,
                "READY_FOR_MODEL_TRAINING": False,
            },
        }
        (staging / "dataset_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        validation = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_sys014_frozen_v2.py"), "--frozen", str(staging)],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        if validation.returncode:
            raise RuntimeError("v2 staging validation failed:\n" + validation.stdout + "\n" + validation.stderr)
        if parent_hashes() != baseline_parent_hashes:
            raise RuntimeError("immutable v1 changed during v2 generation")
        staging.rename(target)
    except Exception:
        if staging.exists() and staging.resolve().parent == FROZEN_PARENT.resolve() and staging.resolve().name == f".{DATASET_VERSION}.staging":
            shutil.rmtree(staging)
        raise

    print(json.dumps({
        "dataset_version": DATASET_VERSION,
        "train_count": stats["TRAIN"]["count"],
        "validation_count": stats["VALIDATION"]["count"],
        "test_count": stats["TEST"]["count"],
        "safety_gold_count": len(safety),
        "family_refined_sample_count": len(changes),
        "split_group_count": len(groups),
        "frozen_path": str(target),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
