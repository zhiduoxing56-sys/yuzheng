"""Create the immutable SYS-014 seven-intent PoC v1 split without model dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = ROOT / "data/nlu/poc/candidate_pool.jsonl"
SAFETY_PATH = ROOT / "data/nlu/poc/safety_gold_candidates.jsonl"
REGISTRY_PATH = ROOT / "data/nlu/spec/intent_registry_draft.yaml"
SCHEMA_PATH = ROOT / "data/nlu/spec/annotation_schema.json"
GUIDELINES_PATH = ROOT / "data/nlu/spec/annotation_guidelines.md"
FROZEN_PARENT = ROOT / "data/nlu/poc/frozen"
DATASET_NAME = "SYS-014 7-Intent PoC"
DATASET_VERSION = "sys014-poc7-v1"
SPLIT_SEED = 14031
POC_INTENTS = [
    "DOOR_OPEN", "DOOR_CLOSE", "WINDOW_OPEN", "WINDOW_SET_POSITION",
    "HEADLIGHT_OFF", "ACCELERATE", "BRAKE",
]
SPLITS = ("TRAIN", "VALIDATION", "TEST")
TARGET_RATIOS = {"TRAIN": 0.70, "VALIDATION": 0.15, "TEST": 0.15}
UNKNOWN_EXTERNAL_IDS = {
    "SYS014-POC-0070", "SYS014-POC-0742", "SYS014-POC-0743", "SYS014-POC-0744",
    "SYS014-POC-0750", "SYS014-POC-0754", "SYS014-POC-0755", "SYS014-POC-0756",
}
PUNCT_TRANSLATION = str.maketrans({
    "，": ",", "。": ".", "！": "!", "？": "?", "；": ";", "：": ":",
    "、": ",", "（": "(", "）": ")", "“": '"', "”": '"', "‘": "'", "’": "'",
})
POLITE_OR_CONTEXT = ["请帮我", "帮我", "麻烦", "能不能", "能否", "可以吗", "好吗", "请"]
CONNECTORS = ["然后", "之后", "以后", "接着", "随后", "并且", "同时", "再"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_text(text: str) -> str:
    value = unicodedata.normalize("NFKC", text).translate(PUNCT_TRANSLATION).lower()
    value = re.sub(r"\s+", "", value)
    value = re.sub(r"([,.!?;:])\1+", r"\1", value)
    return value.strip()


def template_signature(row: dict[str, Any]) -> str:
    text = row["text"]
    replacements = []
    markers = {"AREA": "<AREA>", "VALUE": "<VALUE>", "NEGATION": "<NEG>"}
    for item in row.get("slots", []):
        marker = markers.get(item.get("slot_type"))
        if marker is None:
            continue
        replacements.append((item["char_start"], item["char_end"], marker))
    for start, end, marker in sorted(replacements, reverse=True):
        text = text[:start] + marker + text[end:]
    return normalized_text(text)


def mechanical_signature(row: dict[str, Any]) -> str:
    value = template_signature(row)
    for connector in sorted(CONNECTORS, key=len, reverse=True):
        value = value.replace(connector, "<THEN>")
    for phrase in sorted(POLITE_OR_CONTEXT, key=len, reverse=True):
        value = value.replace(phrase, "")
    value = re.sub(r"[, .!?;:'\"()]+", "", value)
    value = re.sub(r"(?:<THEN>)+", "<THEN>", value).strip("<THEN>")
    return value if len(value) >= 3 else f"SHORT:{template_signature(row)}"


class DSU:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root == right_root:
            return
        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1


@dataclass
class SplitGroup:
    group_id: str
    rows: list[dict[str, Any]]
    features: set[str]
    forced_test: bool

    @property
    def size(self) -> int:
        return len(self.rows)


def row_features(row: dict[str, Any]) -> set[str]:
    result = {
        f"structure:{row['intent_structure']}",
        f"scope:{row['scope_label']}",
        f"source:{row['source_ref']['source_type']}",
    }
    for item in row.get("slots", []):
        result.add(f"slot:{item['slot_type']}")
    if row["intent_structure"] == "SINGLE" and row["scope_label"] == "IN_SCOPE_CONTROL":
        intent = row["intent"]
        mode = "negated" if row["negated"] else "positive"
        result.update({f"intent_any:{intent}", f"intent_mode:{intent}:{mode}", f"semantic:{mode}"})
        if intent == "WINDOW_SET_POSITION" and any(item["slot_type"] == "VALUE" for item in row["slots"]):
            result.add("window_set_position:value")
    if row["intent_structure"] == "MULTI":
        segment_polarities = {segment["negated"] for segment in row.get("segments", [])}
        if segment_polarities == {False, True}:
            result.add("semantic:mixed_negation_multi")
        for segment_item in row.get("segments", []):
            intent = segment_item.get("intent")
            if intent in POC_INTENTS:
                result.update({f"intent_any:{intent}", f"intent_mode:{intent}:multi"})
    return result


def build_groups(rows: list[dict[str, Any]]) -> list[SplitGroup]:
    dsu = DSU(len(rows))
    for key_fn in (
        lambda row: f"family:{row['paraphrase_family_id']}",
        lambda row: f"template:{template_signature(row)}",
        lambda row: f"mechanical:{mechanical_signature(row)}",
    ):
        first: dict[str, int] = {}
        for index, row in enumerate(rows):
            key = key_fn(row)
            if key in first:
                dsu.union(index, first[key])
            else:
                first[key] = index
    components: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for index, row in enumerate(rows):
        components[dsu.find(index)].append(row)
    groups = []
    for component_rows in components.values():
        ids = sorted(row["sample_id"] for row in component_rows)
        group_id = "SGRP-" + hashlib.sha256("|".join(ids).encode("utf-8")).hexdigest()[:16].upper()
        groups.append(SplitGroup(
            group_id=group_id,
            rows=component_rows,
            features=set().union(*(row_features(row) for row in component_rows)),
            forced_test=any(row["source_ref"]["source_type"] == "TEST_ASSET" for row in component_rows),
        ))
    return sorted(groups, key=lambda group: group.group_id)


def stable_order(group: SplitGroup) -> str:
    return hashlib.sha256(f"{SPLIT_SEED}:{group.group_id}".encode("utf-8")).hexdigest()


def coverage_requirements(groups: list[SplitGroup]) -> dict[str, set[str]]:
    desired = {
        *(f"intent_any:{intent}" for intent in POC_INTENTS),
        "structure:SINGLE", "structure:MULTI", "structure:AMBIGUOUS",
        "scope:IN_SCOPE_CONTROL", "scope:NON_CONTROL", "scope:UNKNOWN_CONTROL", "scope:AMBIGUOUS_CONTROL",
        "semantic:positive", "semantic:negated", "semantic:mixed_negation_multi",
        "slot:AREA", "slot:VALUE", "slot:NEGATION", "window_set_position:value",
    }
    for intent in POC_INTENTS:
        for mode in ("positive", "negated", "multi"):
            feature = f"intent_mode:{intent}:{mode}"
            if any(feature in group.features for group in groups):
                desired.add(feature)
    requirements = {split: set() for split in SPLITS}
    for feature in desired:
        forced = sum(group.forced_test and feature in group.features for group in groups)
        nonforced = sum(not group.forced_test and feature in group.features for group in groups)
        if nonforced >= 1:
            requirements["TRAIN"].add(feature)
        if nonforced >= 2:
            requirements["VALIDATION"].add(feature)
        if forced >= 1 or nonforced >= 3:
            requirements["TEST"].add(feature)
    return requirements


def assign_groups(groups: list[SplitGroup]) -> dict[str, str]:
    assignments = {group.group_id: "TEST" for group in groups if group.forced_test}
    by_id = {group.group_id: group for group in groups}
    total = sum(group.size for group in groups)
    targets = {split: total * TARGET_RATIOS[split] for split in SPLITS}
    counts = Counter({"TEST": sum(group.size for group in groups if group.forced_test)})
    covered = {split: set() for split in SPLITS}
    for group in groups:
        if group.forced_test:
            covered["TEST"].update(group.features)
    requirements = coverage_requirements(groups)
    frequency = Counter(feature for group in groups for feature in group.features)

    def seed_split(split: str) -> None:
        while True:
            missing = requirements[split] - covered[split]
            if not missing:
                return
            candidates = [group for group in groups if group.group_id not in assignments and group.features & missing]
            if not candidates:
                return
            def key(group: SplitGroup) -> tuple[float, float, str]:
                gain = sum(1.0 / max(1, frequency[feature]) for feature in group.features & missing)
                overflow = max(0.0, counts[split] + group.size - targets[split]) / max(1.0, targets[split])
                return (gain / math.sqrt(group.size) - overflow, -group.size, stable_order(group))
            selected = max(candidates, key=key)
            assignments[selected.group_id] = split
            counts[split] += selected.size
            covered[split].update(selected.features)

    # Forced TEST groups are enriched first; scarce remaining coverage is then reserved for validation and train.
    seed_split("TEST")
    seed_split("VALIDATION")
    seed_split("TRAIN")

    remaining = sorted((group for group in groups if group.group_id not in assignments), key=stable_order)
    for group in remaining:
        def ratio_cost(split: str) -> tuple[float, float, str]:
            prospective = dict(counts)
            prospective[split] = prospective.get(split, 0) + group.size
            cost = sum(
                ((prospective.get(name, 0) - targets[name]) / max(1.0, targets[name])) ** 2
                for name in SPLITS
            )
            deficit = (targets[split] - counts.get(split, 0)) / max(1.0, targets[split])
            return (cost, -deficit, split)
        selected_split = min(SPLITS, key=ratio_cost)
        assignments[group.group_id] = selected_split
        counts[selected_split] += group.size
        covered[selected_split].update(group.features)

    # Repair feasible supervision coverage after ratio filling. Moves never release a forced
    # TEST group and never remove the donor's last group for another required feature.
    for _ in range(sum(len(items) for items in requirements.values()) * 2):
        feature_counts = {
            split: Counter(
                feature
                for group in groups if assignments[group.group_id] == split
                for feature in group.features
            )
            for split in SPLITS
        }
        missing_pairs = [
            (feature, split)
            for split in SPLITS
            for feature in sorted(requirements[split], key=lambda item: (frequency[item], item))
            if feature_counts[split][feature] == 0
        ]
        if not missing_pairs:
            break
        moved = False
        for feature, recipient in missing_pairs:
            candidates = []
            for group in groups:
                donor = assignments[group.group_id]
                if donor == recipient or group.forced_test or feature not in group.features:
                    continue
                if feature_counts[donor][feature] <= 1:
                    continue
                if any(
                    donor_feature in requirements[donor] and feature_counts[donor][donor_feature] <= 1
                    for donor_feature in group.features
                ):
                    continue
                before = abs(counts[donor] - targets[donor]) + abs(counts[recipient] - targets[recipient])
                after = abs(counts[donor] - group.size - targets[donor]) + abs(counts[recipient] + group.size - targets[recipient])
                candidates.append((after - before, group.size, stable_order(group), group, donor))
            if not candidates:
                continue
            _, _, _, selected, donor = min(candidates, key=lambda item: item[:3])
            assignments[selected.group_id] = recipient
            counts[donor] -= selected.size
            counts[recipient] += selected.size
            moved = True
            break
        if not moved:
            break

    covered = {split: set() for split in SPLITS}
    for group in groups:
        covered[assignments[group.group_id]].update(group.features)

    if len(assignments) != len(groups):
        raise RuntimeError("not every split group was assigned")
    if any(group.forced_test and assignments[group.group_id] != "TEST" for group in groups):
        raise RuntimeError("TEST_ASSET group escaped TEST")
    uncovered = {split: sorted(requirements[split] - covered[split]) for split in SPLITS if requirements[split] - covered[split]}
    if uncovered:
        raise RuntimeError(f"required supervision coverage is incomplete after group assignment: {uncovered}")
    train_intents = {feature.removeprefix("intent_any:") for feature in covered["TRAIN"] if feature.startswith("intent_any:")}
    if train_intents != set(POC_INTENTS):
        raise RuntimeError(f"TRAIN intent coverage is incomplete: {sorted(set(POC_INTENTS) - train_intents)}")
    return assignments


def split_rows(groups: list[SplitGroup], assignments: dict[str, str]) -> dict[str, list[dict[str, Any]]]:
    assignment_by_id = {
        row["sample_id"]: assignments[group.group_id]
        for group in groups for row in group.rows
    }
    result = {split: [] for split in SPLITS}
    source_rows = [row for group in groups for row in group.rows]
    source_rows.sort(key=lambda row: row["sample_id"])
    for row in source_rows:
        frozen = {**row, "split": assignment_by_id[row["sample_id"]]}
        result[frozen["split"]].append(frozen)
    return result


def intent_coverage(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    return {
        intent: {
            "positive_single": sum(
                row.get("intent") == intent and row["intent_structure"] == "SINGLE" and row.get("negated") is False
                for row in rows
            ),
            "negated_single": sum(
                row.get("intent") == intent and row["intent_structure"] == "SINGLE" and row.get("negated") is True
                for row in rows
            ),
            "multi_segment_mentions": sum(
                segment_item.get("intent") == intent for row in rows for segment_item in row.get("segments", [])
            ),
        }
        for intent in POC_INTENTS
    }


def unknown_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    unknown = [row for row in rows if row["scope_label"] == "UNKNOWN_CONTROL"]
    external = sum(row["sample_id"] in UNKNOWN_EXTERNAL_IDS for row in unknown)
    return {
        "UNKNOWN_KNOWN_REGISTRY_OUTSIDE_POC": len(unknown) - external,
        "UNKNOWN_EXTERNAL_CONTROL": external,
    }


def split_statistics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    mixed_negation = sum(
        row["intent_structure"] == "MULTI"
        and {segment_item["negated"] for segment_item in row.get("segments", [])} == {False, True}
        for row in rows
    )
    return {
        "count": len(rows),
        "intent_coverage": intent_coverage(rows),
        "intent_structure": dict(sorted(Counter(row["intent_structure"] for row in rows).items())),
        "scope": dict(sorted(Counter(row["scope_label"] for row in rows).items())),
        "semantic_type": {
            "positive_single": sum(row["intent_structure"] == "SINGLE" and row.get("negated") is False for row in rows),
            "negated_single": sum(row["intent_structure"] == "SINGLE" and row.get("negated") is True for row in rows),
            "mixed_negation_multi": mixed_negation,
        },
        "slots": dict(sorted(Counter(item["slot_type"] for row in rows for item in row.get("slots", [])).items())),
        "source_type": dict(sorted(Counter(row["source_ref"]["source_type"] for row in rows).items())),
        "unknown_control_derived": unknown_counts(rows),
    }


def cross_split_count(rows_by_split: dict[str, list[dict[str, Any]]], key_fn) -> int:
    seen: dict[str, set[str]] = defaultdict(set)
    for split, rows in rows_by_split.items():
        for row in rows:
            seen[key_fn(row)].add(split)
    return sum(len(splits) > 1 for splits in seen.values())


def leakage_metrics(rows_by_split: dict[str, list[dict[str, Any]]], groups: list[SplitGroup], assignments: dict[str, str]) -> dict[str, int]:
    group_splits: dict[str, set[str]] = defaultdict(set)
    sample_split = {row["sample_id"]: split for split, rows in rows_by_split.items() for row in rows}
    for group in groups:
        for row in group.rows:
            group_splits[group.group_id].add(sample_split[row["sample_id"]])
    return {
        "exact_cross_split_duplicates": cross_split_count(rows_by_split, lambda row: row["text"]),
        "normalized_cross_split_duplicates": cross_split_count(rows_by_split, lambda row: normalized_text(row["text"])),
        "template_signature_cross_split_duplicates": cross_split_count(rows_by_split, template_signature),
        "mechanical_near_duplicate_cross_split_failures": cross_split_count(rows_by_split, mechanical_signature),
        "family_leakage_failures": cross_split_count(rows_by_split, lambda row: row["paraphrase_family_id"]),
        "split_group_leakage_failures": sum(len(splits) > 1 for splits in group_splits.values()),
        "test_asset_in_train": sum(
            row["source_ref"]["source_type"] == "TEST_ASSET" for row in rows_by_split["TRAIN"]
        ),
        "unassigned_count": sum(row["split"] == "UNASSIGNED" for rows in rows_by_split.values() for row in rows),
    }


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def create_split_report(stats: dict[str, dict[str, Any]], group_counts: dict[str, int], family_counts: dict[str, int]) -> str:
    intent_rows = []
    for intent in POC_INTENTS:
        row = [intent]
        for split in SPLITS:
            values = stats[split]["intent_coverage"][intent]
            row.extend([values["positive_single"], values["negated_single"], values["multi_segment_mentions"]])
        intent_rows.append(row)
    lines = [
        f"# {DATASET_VERSION} 切分报告", "",
        "## 切分规模", "",
        markdown_table(
            ["Split", "样本", "Family", "Split group", "比例"],
            [[split, stats[split]["count"], family_counts[split], group_counts[split], f"{stats[split]['count'] / sum(item['count'] for item in stats.values()):.2%}"] for split in SPLITS],
        ), "",
        "## 7-Intent 覆盖", "",
        markdown_table(
            ["Intent", "TRAIN +", "TRAIN -", "TRAIN MULTI", "VAL +", "VAL -", "VAL MULTI", "TEST +", "TEST -", "TEST MULTI"],
            intent_rows,
        ), "",
    ]
    for dimension, title in (("intent_structure", "Intent structure"), ("scope", "Scope"), ("slots", "Slots"), ("source_type", "Source type"), ("semantic_type", "语义安全类型"), ("unknown_control_derived", "UNKNOWN_CONTROL 派生类型")):
        keys = sorted(set().union(*(stats[split][dimension] for split in SPLITS)))
        lines.extend([
            f"## {title}", "",
            markdown_table(["类别", *SPLITS], [[key, *(stats[split][dimension].get(key, 0) for split in SPLITS)] for key in keys]), "",
        ])
    lines.extend([
        "## 说明", "",
        "- TEST_ASSET 所在 split group 全部进入 TEST。",
        "- WINDOW_SET_POSITION 在 VALIDATION 与 TEST 均包含 VALUE 样本。",
        "- MODE 为 0，未人工制造 MODE 样本。",
        "- UNKNOWN_CONTROL 表示当前 7-Intent PoC 必须 abstain；不等价于完整 95-Intent Registry 永远未知。",
    ])
    return "\n".join(lines) + "\n"


def create_leakage_report(metrics: dict[str, int], assignment_digest: str) -> str:
    rows = [[key, value, "PASS" if value == 0 else "FAIL"] for key, value in metrics.items()]
    return "\n".join([
        f"# {DATASET_VERSION} 泄漏审计", "",
        markdown_table(["检查项", "计数", "结果"], rows), "",
        f"- split group assignment digest: `{assignment_digest}`",
        "- 分组边：paraphrase family、template signature、mechanical signature。",
        "- Safety Gold 未参与 group 切分，且与 TRAIN/VALIDATION/TEST 全局去重。",
        "- 所有指标必须为 0 才能冻结。", "",
    ])


def create_readme(counts: dict[str, int]) -> str:
    return f"""# {DATASET_VERSION}

这是 SYS-014 的 7-Intent PoC 冻结数据集，包含 {counts['candidate']} 条 candidate 切分记录和 {counts['safety']} 条独立 Safety Gold。

## 重要边界

1. 本数据集仅覆盖 `DOOR_OPEN`、`DOOR_CLOSE`、`WINDOW_OPEN`、`WINDOW_SET_POSITION`、`HEADLIGHT_OFF`、`ACCELERATE`、`BRAKE`，不是完整 95 类最终模型数据集。
2. 来源包含 `TEST_ASSET` 与 `SYNTHETIC_TEMPLATE`；不得宣称为真实驾驶员大规模实采语料。
3. Safety Gold 完全独立于训练、验证和测试，不得用于训练、early stopping、超参数/阈值选择、confidence calibration 或模型选择；只用于方案基本确定后的最终安全回归。
4. PoC 中 `UNKNOWN_CONTROL` 表示“当前 7-Intent 模型必须 abstain 的控制请求”。它既可能是完整 Registry 已知但 PoC 未覆盖的车辆能力，也可能是 Registry 外的外域控制；不表示完整 95-Intent Registry 永远不知道该能力。
5. TRAIN/VALIDATION/TEST 按确定性 split group 切分，不按单条样本随机切分。group 由 paraphrase family、slot-aware template signature 与机械近重复 signature 合并得到。
6. 所有 TEST_ASSET 及其整个 group 均固定在 TEST。
7. `split_seed={SPLIT_SEED}`；生成与审计工具位于 `scripts/freeze_sys014_poc7.py` 和 `scripts/validate_sys014_frozen.py`。
8. 本目录是不可变 v1，禁止原地修改；未来数据变化必须创建 `sys014-poc7-v2`。

## 文件

- `train.jsonl`、`validation.jsonl`、`test.jsonl`：冻结后的 candidate split。
- `safety_gold.jsonl`：完全隔离的安全回归集。
- `dataset_manifest.json`：版本、策略、覆盖、计数和 SHA256。
- `split_report.md`：按 split 的覆盖统计。
- `leakage_audit.md`：泄漏与隔离审计。
"""


def prepare() -> tuple[list[SplitGroup], dict[str, str], dict[str, list[dict[str, Any]]], list[dict[str, Any]], dict[str, Any]]:
    candidate = load_jsonl(CANDIDATE_PATH)
    safety = load_jsonl(SAFETY_PATH)
    if len(candidate) != 849 or len(safety) != 60:
        raise RuntimeError(f"expected Stage 3C source counts 849 + 60, got {len(candidate)} + {len(safety)}")
    if any(row["split"] != "UNASSIGNED" for row in candidate):
        raise RuntimeError("source candidate split must remain UNASSIGNED")
    if any(row["split"] != "SAFETY_GOLD" for row in safety):
        raise RuntimeError("source Safety Gold split must remain SAFETY_GOLD")
    all_ids = [row["sample_id"] for row in candidate + safety]
    all_texts = [row["text"] for row in candidate + safety]
    if len(all_ids) != len(set(all_ids)) or len(all_texts) != len(set(all_texts)):
        raise RuntimeError("source contains duplicate sample_id or text")
    groups = build_groups(candidate)
    assignments = assign_groups(groups)
    rows_by_split = split_rows(groups, assignments)
    metrics = leakage_metrics(rows_by_split, groups, assignments)
    if any(metrics.values()):
        raise RuntimeError(f"pre-freeze leakage metrics are not zero: {metrics}")
    frozen_ids = {row["sample_id"] for rows in rows_by_split.values() for row in rows}
    if frozen_ids & {row["sample_id"] for row in safety}:
        raise RuntimeError("Safety Gold sample_id overlaps candidate split")
    if {row["text"] for rows in rows_by_split.values() for row in rows} & {row["text"] for row in safety}:
        raise RuntimeError("Safety Gold text overlaps candidate split")
    return groups, assignments, rows_by_split, safety, metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    target = FROZEN_PARENT / DATASET_VERSION
    if target.exists():
        raise RuntimeError(f"immutable frozen version already exists; refusing overwrite: {target}")
    groups, assignments, rows_by_split, safety, metrics = prepare()
    group_counts = Counter(assignments.values())
    family_counts = {
        split: len({row["paraphrase_family_id"] for row in rows}) for split, rows in rows_by_split.items()
    }
    stats = {split: split_statistics(rows) for split, rows in rows_by_split.items()}
    assignment_digest = sha256_bytes("\n".join(f"{key}:{assignments[key]}" for key in sorted(assignments)).encode("utf-8"))
    summary = {
        "dataset_version": DATASET_VERSION,
        "split_seed": SPLIT_SEED,
        "train_count": len(rows_by_split["TRAIN"]),
        "validation_count": len(rows_by_split["VALIDATION"]),
        "test_count": len(rows_by_split["TEST"]),
        "safety_gold_count": len(safety),
        "train_family_count": family_counts["TRAIN"],
        "validation_family_count": family_counts["VALIDATION"],
        "test_family_count": family_counts["TEST"],
        "train_split_group_count": group_counts["TRAIN"],
        "validation_split_group_count": group_counts["VALIDATION"],
        "test_split_group_count": group_counts["TEST"],
        **metrics,
    }
    if args.dry_run:
        print(json.dumps({**summary, "coverage": stats}, ensure_ascii=False, indent=2))
        return 0

    FROZEN_PARENT.mkdir(parents=True, exist_ok=True)
    staging = FROZEN_PARENT / f".{DATASET_VERSION}.staging"
    if staging.exists():
        raise RuntimeError(f"staging directory already exists: {staging}")
    staging.mkdir()
    try:
        file_rows = {
            "train.jsonl": rows_by_split["TRAIN"],
            "validation.jsonl": rows_by_split["VALIDATION"],
            "test.jsonl": rows_by_split["TEST"],
            "safety_gold.jsonl": safety,
        }
        for name, rows in file_rows.items():
            (staging / name).write_bytes(jsonl_bytes(rows))
        (staging / "split_report.md").write_text(create_split_report(stats, dict(group_counts), family_counts), encoding="utf-8")
        (staging / "leakage_audit.md").write_text(create_leakage_report(metrics, assignment_digest), encoding="utf-8")
        (staging / "README.md").write_text(create_readme({"candidate": 849, "safety": 60}), encoding="utf-8")

        file_hashes = {
            "data/nlu/spec/intent_registry_draft.yaml": sha256_file(REGISTRY_PATH),
            "data/nlu/spec/annotation_schema.json": sha256_file(SCHEMA_PATH),
            "data/nlu/spec/annotation_guidelines.md": sha256_file(GUIDELINES_PATH),
            "data/nlu/poc/candidate_pool.jsonl": sha256_file(CANDIDATE_PATH),
            "data/nlu/poc/safety_gold_candidates.jsonl": sha256_file(SAFETY_PATH),
            **{name: sha256_file(staging / name) for name in file_rows},
        }
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        manifest = {
            "dataset_name": DATASET_NAME,
            "dataset_version": DATASET_VERSION,
            "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
            "immutable": True,
            "registry_version": "sys-014-stage2.1-draft-2",
            "annotation_schema_id": schema["$id"],
            "poc_intents": POC_INTENTS,
            "split_seed": SPLIT_SEED,
            "split_strategy": "deterministic constrained group split; TEST_ASSET groups forced to TEST; target ratios 70/15/15",
            "grouping_strategy": {
                "unit": "split_group_id",
                "algorithm": "DSU connected components",
                "edges": ["paraphrase_family_id", "template_signature_v1", "mechanical_signature_v1"],
                "template_signature": "replace AREA/VALUE/NEGATION spans with <AREA>/<VALUE>/<NEG>, then NFKC whitespace/punctuation normalization",
                "mechanical_signature": "template signature plus polite/context removal and connector normalization",
                "split_group_assignment_digest_sha256": assignment_digest,
            },
            "source_candidate_count": 849,
            "source_safety_gold_count": 60,
            "train_count": summary["train_count"],
            "validation_count": summary["validation_count"],
            "test_count": summary["test_count"],
            "safety_gold_count": 60,
            "train_family_count": family_counts["TRAIN"],
            "validation_family_count": family_counts["VALIDATION"],
            "test_family_count": family_counts["TEST"],
            "train_split_group_count": group_counts["TRAIN"],
            "validation_split_group_count": group_counts["VALIDATION"],
            "test_split_group_count": group_counts["TEST"],
            "statistics": stats,
            "unknown_control_derived_total": unknown_counts([row for rows in rows_by_split.values() for row in rows]),
            "leakage_audit": metrics,
            "pre_freeze_fixes": {
                "deleted": ["SYS014-POC-0462"],
                "label_fixed": ["SYS014-POC-0070", "SYS014-POC-0686", "SYS014-POC-0687", "SYS014-POC-0688"],
                "paraphrase_family_refined_for_group_coverage": [
                    "SYS014-POC-0787", "SYS014-POC-0788", "SYS014-POC-0789",
                    "SYS014-POC-0790", "SYS014-POC-0791", "SYS014-POC-0792",
                ],
            },
            "file_sha256": file_hashes,
            "safety_gold_policy": "isolated final safety regression only; prohibited for training, early stopping, hyperparameter/threshold selection, confidence calibration, and model selection",
        }
        (staging / "dataset_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        for required in ("train.jsonl", "validation.jsonl", "test.jsonl", "safety_gold.jsonl", "dataset_manifest.json", "split_report.md", "leakage_audit.md", "README.md"):
            if not (staging / required).is_file() or (staging / required).stat().st_size == 0:
                raise RuntimeError(f"missing or empty frozen artifact: {required}")
        validation = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_sys014_frozen.py"), "--frozen", str(staging)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if validation.returncode != 0:
            raise RuntimeError(
                "staging frozen validation failed before immutable rename:\n"
                + validation.stdout + "\n" + validation.stderr
            )
        staging.rename(target)
    except Exception:
        resolved = staging.resolve()
        if resolved.parent == FROZEN_PARENT.resolve() and resolved.name == f".{DATASET_VERSION}.staging" and resolved.exists():
            shutil.rmtree(resolved)
        raise

    print(json.dumps({**summary, "frozen_path": str(target)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
