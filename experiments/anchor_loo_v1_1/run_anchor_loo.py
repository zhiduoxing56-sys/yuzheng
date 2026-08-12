from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Iterable

import numpy as np
import yaml


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[1]
EXPERIMENTS_DIR = BASE_DIR.parent
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))

from intent_recall_v1.recaller import (  # noqa: E402
    CHANNELS,
    CandidateIntentRecaller,
    _normalized_text,
)


DEFAULT_CONFIG = ROOT_DIR / "test-results" / "intent-recall-v1_1" / "config_v1_1.yaml"
DEFAULT_OUTPUT = ROOT_DIR / "test-results" / "anchor-loo-v1_1"
FORMAL_CATEGORY = "正式意图"
BYPASS_CATEGORY = "已知车控旁路"
SECURITY_CATEGORY = "安全注入"
ALLOWED_REASONS = {
    "语义过于模糊",
    "动作区分不足",
    "对象区分不足",
    "与相邻意图表达过近",
    "疑似异常文本",
    "疑似错误挂靠",
    "表达簇覆盖不足",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def percentile(values: Iterable[float], fraction: float) -> float | None:
    ordered = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not ordered:
        return None
    rank = (len(ordered) - 1) * fraction
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return float(ordered[lower])
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower))


def rounded(value: float | None, digits: int = 6) -> float | None:
    if value is None or not math.isfinite(float(value)):
        return None
    return round(float(value), digits)


def distribution(values: Iterable[float]) -> dict[str, Any]:
    finite = [float(value) for value in values if math.isfinite(float(value))]
    return {
        "count": len(finite),
        "min": rounded(min(finite)) if finite else None,
        "p05": rounded(percentile(finite, 0.05)),
        "p10": rounded(percentile(finite, 0.10)),
        "p25": rounded(percentile(finite, 0.25)),
        "p50": rounded(percentile(finite, 0.50)),
        "p75": rounded(percentile(finite, 0.75)),
        "p90": rounded(percentile(finite, 0.90)),
        "p95": rounded(percentile(finite, 0.95)),
        "max": rounded(max(finite)) if finite else None,
        "mean": rounded(mean(finite)) if finite else None,
    }


def flatten_with_categories(anchor_path: Path) -> list[dict[str, str]]:
    data = yaml.safe_load(anchor_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("anchor YAML root must be a mapping")
    rows: list[dict[str, str]] = []
    for category, contents in data.items():
        if isinstance(contents, dict):
            for target, texts in contents.items():
                if not isinstance(texts, list):
                    raise ValueError(f"expected list at {category}/{target}")
                rows.extend(
                    {"category": str(category), "target": str(target), "text": str(text)}
                    for text in texts
                )
        elif isinstance(contents, list):
            rows.extend(
                {"category": str(category), "target": str(category), "text": str(text)}
                for text in contents
            )
        else:
            raise ValueError(f"unsupported category shape: {category}")
    return rows


def category_group(category: str) -> str:
    if category == FORMAL_CATEGORY:
        return "formal"
    if category == BYPASS_CATEGORY:
        return "bypass"
    if category == SECURITY_CATEGORY:
        return "security"
    return "other"


def load_cards(path: Path) -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    formal = data.get(FORMAL_CATEGORY, {}) if isinstance(data, dict) else {}
    if not isinstance(formal, dict):
        raise ValueError("intent cards formal section must be a mapping")
    return {str(target): dict(card) for target, card in formal.items() if isinstance(card, dict)}


def _stem(target: str) -> str:
    suffixes = (
        "_UNLOCK",
        "_UNFOLD",
        "_DISABLE",
        "_RELEASE",
        "_CLOSE",
        "_LOCK",
        "_FOLD",
        "_ENABLE",
        "_APPLY",
        "_OPEN",
        "_OFF",
        "_ON",
    )
    for suffix in suffixes:
        if target.endswith(suffix):
            return target[: -len(suffix)]
    return target


def is_opposite_pair(left: str, right: str) -> bool:
    if left == right:
        return False
    suffix_pairs = (
        ("_ON", "_OFF"),
        ("_OPEN", "_CLOSE"),
        ("_LOCK", "_UNLOCK"),
        ("_ENABLE", "_DISABLE"),
        ("_FOLD", "_UNFOLD"),
        ("_APPLY", "_RELEASE"),
    )
    for first, second in suffix_pairs:
        if _stem(left) == _stem(right) and (
            (left.endswith(first) and right.endswith(second))
            or (left.endswith(second) and right.endswith(first))
        ):
            return True
    explicit = {
        frozenset(("ACCELERATE", "DECELERATE")),
        frozenset(("BRAKE", "ACCELERATE")),
        frozenset(("EMERGENCY_BRAKE", "ACCELERATE")),
    }
    return frozenset((left, right)) in explicit


def object_family(target: str, card: dict[str, Any] | None) -> str:
    object_name = str((card or {}).get("对象", ""))
    haystack = f"{target} {object_name}"
    mappings = (
        ("DOOR", ("DOOR", "车门")),
        ("WINDOW", ("WINDOW", "车窗")),
        ("SUNROOF", ("SUNROOF", "天窗")),
        ("TRUNK", ("TRUNK", "后备箱", "后尾门")),
        ("HOOD", ("HOOD", "前舱盖", "引擎盖")),
        ("CRUISE", ("CRUISE", "巡航")),
        ("DRIVE_MODE", ("驾驶模式", "DRIVE_MODE")),
        ("LOW_BEAM", ("LOW_BEAM", "近光")),
        ("HIGH_BEAM", ("HIGH_BEAM", "远光")),
        ("FOG_LIGHT", ("FOG_LIGHT", "雾灯")),
        ("PARKING_LIGHT", ("PARKING_LIGHT", "示宽灯", "位置灯")),
    )
    for family, needles in mappings:
        if any(needle in haystack for needle in needles):
            return family
    return object_name or target.split("_", 1)[0]


def risk_types(left: str, right: str, cards: dict[str, dict[str, Any]]) -> list[str]:
    if left == right or not right:
        return []
    risks: list[str] = []
    if is_opposite_pair(left, right):
        risks.append("动作方向相反")
    left_card = cards.get(left)
    right_card = cards.get(right)
    left_object = str((left_card or {}).get("对象", ""))
    right_object = str((right_card or {}).get("对象", ""))
    left_action = str((left_card or {}).get("动作", ""))
    right_action = str((right_card or {}).get("动作", ""))
    if left_object and left_object == right_object and left_action != right_action:
        risks.append("同一对象不同控制动作")
    adjacent_sets = (
        {"DOOR", "WINDOW", "SUNROOF", "TRUNK", "HOOD"},
        {"CRUISE", "DRIVE_MODE"},
        {"LOW_BEAM", "HIGH_BEAM", "FOG_LIGHT", "PARKING_LIGHT"},
    )
    left_family = object_family(left, left_card)
    right_family = object_family(right, right_card)
    if any(left_family in group and right_family in group for group in adjacent_sets):
        risks.append("相邻目标混淆")
    return list(dict.fromkeys(risks))


class LeaveOneOutObserver:
    def __init__(self, recaller: CandidateIntentRecaller) -> None:
        self.recaller = recaller
        grouped: dict[str, list[int]] = defaultdict(list)
        for index in recaller.semantic_indices.tolist():
            grouped[str(recaller.targets[index])].append(int(index))
        self.semantic_target_indices = {
            target: np.asarray(indices, dtype=np.int64) for target, indices in grouped.items()
        }
        self.channel_target_limit = int(recaller.config["retrieval"]["channel_target_top_k"])
        self.rrf_k = int(recaller.config["retrieval"]["rrf_k"])

    def complete_channel_ranking(
        self, scores: np.ndarray
    ) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
        rows: list[dict[str, Any]] = []
        for target, indices in self.semantic_target_indices.items():
            local_scores = scores[indices]
            order = np.argsort(-local_scores, kind="stable")
            anchor_index = int(indices[int(order[0])])
            rows.append(
                {
                    "target": target,
                    "score": float(scores[anchor_index]),
                    "anchor": str(self.recaller.anchor_texts[anchor_index]),
                    "anchor_index": anchor_index,
                }
            )
        rows.sort(key=lambda row: (-row["score"], row["anchor_index"], row["target"]))
        mapping: dict[str, dict[str, Any]] = {}
        public_rows: list[dict[str, Any]] = []
        for rank, row in enumerate(rows, start=1):
            compact = {
                "rank": rank,
                "score": rounded(row["score"]),
                "anchor": row["anchor"],
                "anchor_index": row["anchor_index"],
            }
            mapping[row["target"]] = compact
            public_rows.append({"target": row["target"], **compact})
        return public_rows, mapping

    def frozen_fusion(self, scores_by_channel: dict[str, np.ndarray]) -> dict[str, Any]:
        rankings = {
            channel: self.recaller._channel_rankings(scores_by_channel[channel])
            for channel in CHANNELS
        }
        target_scores: dict[str, float] = defaultdict(float)
        target_hits: dict[str, dict[str, Any]] = defaultdict(dict)
        for channel in CHANNELS:
            for hit in rankings[channel]:
                target_scores[hit.target] += 1.0 / (self.rrf_k + hit.rank)
                target_hits[hit.target][channel] = hit
        ordered = sorted(
            target_scores,
            key=lambda target: (
                -target_scores[target],
                -len(target_hits[target]),
                min(hit.rank for hit in target_hits[target].values()),
                target,
            ),
        )
        return {
            "ordered_targets": ordered,
            "scores": target_scores,
            "hits": target_hits,
        }

    @staticmethod
    def strongest_anchor(channel_rows: dict[str, dict[str, Any]]) -> str | None:
        usable = {channel: row for channel, row in channel_rows.items() if row}
        if not usable:
            return None
        grouped: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
        for channel, row in usable.items():
            grouped[str(row["anchor"])].append((channel, row))
        return min(
            grouped,
            key=lambda anchor: (
                -len(grouped[anchor]),
                min(int(item[1]["rank"]) for item in grouped[anchor]),
                -max(float(item[1]["score"]) for item in grouped[anchor]),
                anchor,
            ),
        )

    def inspect_semantic(
        self,
        anchor_index: int,
        true_target: str,
        scores_by_channel: dict[str, np.ndarray],
    ) -> dict[str, Any]:
        complete_maps: dict[str, dict[str, dict[str, Any]]] = {}
        channel_payload: dict[str, Any] = {}
        for channel in CHANNELS:
            rows, mapping = self.complete_channel_ranking(scores_by_channel[channel])
            complete_maps[channel] = mapping
            correct = mapping[true_target]
            channel_payload[channel] = {
                "correct_target_rank": correct["rank"],
                "correct_target_highest_similarity": correct["score"],
                "top1_target": rows[0]["target"],
                "top1_similarity": rows[0]["score"],
                "second_target": rows[1]["target"],
                "second_similarity": rows[1]["score"],
                "first_second_target_gap": rounded(rows[0]["score"] - rows[1]["score"]),
                "correct_target_strongest_anchor": correct["anchor"],
                "correct_target_strongest_anchor_index": correct["anchor_index"],
                "top1_strongest_anchor": rows[0]["anchor"],
            }

        fusion = self.frozen_fusion(scores_by_channel)
        ordered = fusion["ordered_targets"]
        scores = fusion["scores"]
        hits = fusion["hits"]
        correct_rank = ordered.index(true_target) + 1 if true_target in ordered else None
        correct_channel_rows = {
            channel: complete_maps[channel][true_target] for channel in CHANNELS
        }
        top1 = ordered[0]
        top1_channel_rows = {
            channel: {
                "rank": hit.rank,
                "score": hit.best_score,
                "anchor": hit.anchors[0].text,
            }
            for channel, hit in hits[top1].items()
        }
        correct_hits = hits.get(true_target, {})
        top1_score = float(scores[top1])
        top2_score = float(scores[ordered[1]]) if len(ordered) > 1 else 0.0
        fusion_payload = {
            "top1_target": top1,
            "top3_targets": ordered[:3],
            "top8_targets": ordered[:8],
            "correct_target_rank": correct_rank,
            "correct_target_rrf_score": rounded(scores.get(true_target)) if true_target in scores else None,
            "correct_target_strongest_anchor": self.strongest_anchor(correct_channel_rows),
            "correct_target_support_channels": [
                channel for channel in CHANNELS if channel in correct_hits
            ],
            "correct_target_support_channel_count": len(correct_hits),
            "top1_rrf_score": rounded(top1_score),
            "top2_rrf_score": rounded(top2_score),
            "top1_top2_rrf_gap": rounded(top1_score - top2_score),
            "top1_strongest_anchor": self.strongest_anchor(top1_channel_rows),
            "top1_support_channel_count": len(hits[top1]),
            "candidate_count": len(ordered),
        }
        return {"channels": channel_payload, "fusion": fusion_payload}

    def inspect_security(
        self,
        query_text: str,
        scores_by_channel: dict[str, np.ndarray],
    ) -> dict[str, Any]:
        channel_payload: dict[str, Any] = {}
        support_channels: list[str] = []
        strongest_rows: dict[str, dict[str, Any]] = {}
        for channel in CHANNELS:
            scores = scores_by_channel[channel]
            indices = self.recaller.security_indices
            order = indices[np.argsort(-scores[indices], kind="stable")]
            first_index = int(order[0])
            second_index = int(order[1]) if len(order) > 1 else None
            hits = self.recaller._security_channel_hits(channel, scores, query_text)
            supported = bool(hits)
            if supported:
                support_channels.append(channel)
            strongest_rows[channel] = {
                "rank": 1,
                "score": rounded(float(scores[first_index])),
                "anchor": str(self.recaller.anchor_texts[first_index]),
            }
            channel_payload[channel] = {
                "correct_target_rank": 1 if supported else None,
                "correct_target_highest_similarity": rounded(float(scores[first_index])),
                "top1_target": self.recaller.security_target if supported else None,
                "top1_similarity": rounded(float(scores[first_index])),
                "second_target": None,
                "second_similarity": None,
                "first_second_target_gap": None,
                "first_second_anchor_gap": rounded(
                    float(scores[first_index] - scores[second_index])
                ) if second_index is not None else None,
                "correct_target_strongest_anchor": str(self.recaller.anchor_texts[first_index]),
                "correct_target_strongest_anchor_index": first_index,
                "top1_strongest_anchor": str(self.recaller.anchor_texts[first_index]),
                "passed_frozen_security_threshold": supported,
            }
        recovered = bool(support_channels)
        fusion_payload = {
            "top1_target": self.recaller.security_target if recovered else None,
            "top3_targets": [self.recaller.security_target] if recovered else [],
            "top8_targets": [self.recaller.security_target] if recovered else [],
            "correct_target_rank": 1 if recovered else None,
            "correct_target_rrf_score": None,
            "correct_target_strongest_anchor": self.strongest_anchor(strongest_rows),
            "correct_target_support_channels": support_channels,
            "correct_target_support_channel_count": len(support_channels),
            "top1_rrf_score": None,
            "top2_rrf_score": None,
            "top1_top2_rrf_gap": None,
            "top1_strongest_anchor": self.strongest_anchor(strongest_rows),
            "top1_support_channel_count": len(support_channels),
            "candidate_count": 1 if recovered else 0,
            "orthogonal_security_signal_recovered": recovered,
        }
        return {"channels": channel_payload, "fusion": fusion_payload}


def accuracy_block(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    payload: dict[str, Any] = {"anchor_count": total}
    for k in (1, 2, 3, 5, 8):
        correct = sum(
            row["correct_target_rank"] is not None and row["correct_target_rank"] <= k
            for row in rows
        )
        payload[f"top{k}"] = {
            "correct": correct,
            "total": total,
            "rate": rounded(correct / total) if total else None,
        }
    return payload


def most_common_or_none(counter: Counter[str]) -> dict[str, Any] | None:
    if not counter:
        return None
    target, count = sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0]
    return {"target": target, "count": count}


def reason_for(row: dict[str, Any]) -> str:
    risks = set(row.get("risk_types", []))
    flags = set(row.get("quality_flags", []))
    if "动作方向相反" in risks or "同一对象不同控制动作" in risks:
        return "动作区分不足"
    if "相邻目标混淆" in risks:
        return "对象区分不足"
    if "疑似错误挂靠" in flags:
        return "疑似错误挂靠"
    if "疑似异常文本" in flags:
        return "疑似异常文本"
    if "表达簇覆盖不足" in flags:
        return "表达簇覆盖不足"
    if row["fusion"]["top1_target"] != row["true_target"]:
        return "与相邻意图表达过近"
    return "语义过于模糊"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def build_readme(
    summary: dict[str, Any],
    per_intent: list[dict[str, Any]],
    confusion_pairs: list[dict[str, Any]],
    high_risk: list[dict[str, Any]],
    repair_candidates: list[dict[str, Any]],
) -> str:
    anchor_name = Path(summary["frozen_input"]["path"]).stem
    overall = summary["accuracy"]["all"]
    priorities = summary["priority_counts"]
    worst = per_intent[:10]
    opposite = [row for row in high_risk if "动作方向相反" in row["risk_types"]]
    suspected_wrong = [row for row in repair_candidates if "疑似错误挂靠" in row["quality_flags"]]
    garbage = [row for row in repair_candidates if "疑似异常文本" in row["quality_flags"]]
    lines = [
        f"# {anchor_name} 全量留一诊断",
        "",
        f"1. 总锚点数量：**{summary['counts']['all']}**",
        f"2. 正式意图锚点数量：**{summary['counts']['formal']}**",
        f"3. 留一 Top1 准确率：**{overall['top1']['rate']:.2%}**（{overall['top1']['correct']}/{overall['top1']['total']}）",
        f"4. Top3 准确率：**{overall['top3']['rate']:.2%}**（{overall['top3']['correct']}/{overall['top3']['total']}）",
        f"5. Top8 准确率：**{overall['top8']['rate']:.2%}**（{overall['top8']['correct']}/{overall['top8']['total']}）",
        f"6. P0 数量：**{priorities.get('P0', 0)}**",
        f"7. P1 数量：**{priorities.get('P1', 0)}**",
        f"8. P2 数量：**{priorities.get('P2', 0)}**",
        f"9. P3 数量：**{priorities.get('P3', 0)}**",
        "10. 最差的 10 个正式意图：见下表。",
        "11. 出现次数最多的 20 组混淆：见下表。",
        f"12. 所有动作反向错误：**{sum(row['count'] for row in opposite)} 条 / {len(opposite)} 组**，见下表。",
        f"13. 是否发现疑似错误挂靠：**{'是' if suspected_wrong else '否'}**（{len(suspected_wrong)} 条疑似样本）。",
        f"14. 是否发现明显垃圾锚点：**{'是' if garbage else '否'}**（{len(garbage)} 条疑似异常文本；仅诊断，未修改）。",
        "",
        "## 冻结性与方法",
        "",
        f"- v1.1 路径：`{summary['frozen_input']['path']}`",
        f"- 运行前 SHA256：`{summary['frozen_input']['sha256_before']}`",
        f"- 运行后 SHA256：`{summary['frozen_input']['sha256_after']}`",
        f"- 摘要未变化：`{summary['frozen_input']['unchanged']}`",
        "- 每条查询复用已缓存的归一化 BGE 锚点向量；语义、字面、拼音三路均把查询锚点自身索引屏蔽后再排名。",
        "- 正式意图与驾驶模式旁路按冻结的三路 Top40 + RRF 融合；安全注入按冻结的正交安全信号检测单独统计。",
        f"- P3 低融合间隔边界来自 Top1 正确语义候选样本间隔分布 P10：`{summary['diagnostic_thresholds']['p3_fusion_gap_p10']}`；只用于标注，未改变召回。",
        "",
        "## 分组准确率",
        "",
        markdown_table(
            ["分组", "锚点", "Top1", "Top2", "Top3", "Top5", "Top8"],
            [
                [name, block["anchor_count"]] + [f"{block[f'top{k}']['rate']:.2%}" for k in (1, 2, 3, 5, 8)]
                for name, block in summary["accuracy"].items()
            ],
        ),
        "",
        "## 最差 10 个正式意图",
        "",
        markdown_table(
            ["意图", "锚点", "Top1", "Top3", "Top8", "平均排名", "最差排名", "最常吸走目标"],
            [
                [
                    row["intent_id"], row["anchor_count"], f"{row['top1_rate']:.2%}",
                    f"{row['top3_rate']:.2%}", f"{row['top8_rate']:.2%}", row["average_correct_target_rank"],
                    row["worst_correct_target_rank"],
                    (row["most_common_absorber"] or {}).get("target", "-"),
                ]
                for row in worst
            ],
        ),
        "",
        "## 最常见 20 组混淆",
        "",
        markdown_table(
            ["真实目标", "错误 Top1", "次数", "风险类型"],
            [[row["true_target"], row["wrong_top1_target"], row["count"], "、".join(row["risk_types"]) or "-"] for row in confusion_pairs[:20]],
        ),
        "",
        "## 所有动作反向错误",
        "",
        markdown_table(
            ["真实目标", "错误 Top1", "次数", "锚点示例"],
            [[row["true_target"], row["wrong_top1_target"], row["count"], "；".join(row["anchor_examples"][:3])] for row in opposite],
        ) if opposite else "无。",
        "",
        "## 产物",
        "",
        "- `summary.json`：总体、分组、分级、分布与冻结性摘要。",
        "- `per-intent-stats.json`：71 个正式意图逐意图统计（按 Top1 从低到高）。",
        "- `all-anchor-results.json`：全部锚点逐条三通道与融合诊断。",
        "- `confusion-pairs.json`：完整错误对与等价混淆矩阵。",
        "- `high-risk-confusions.json`：动作反向、相邻目标、同对象不同动作错误。",
        "- `repair-candidates.json` / `.csv`：仅供人工修订的候选清单。",
        "",
        "本目录只包含诊断产物；没有修改、删除、新增或重新挂靠任何锚点。",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Full leave-one-out anchor diagnostics")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--diagnostic-thresholds-from",
        type=Path,
        default=None,
        help="Reuse diagnostic-only thresholds and target sets from a frozen summary.json",
    )
    args = parser.parse_args()
    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    started = perf_counter()
    recaller = CandidateIntentRecaller(args.config.resolve())
    anchor_path = recaller.anchor_path.resolve()
    hash_before = sha256_file(anchor_path)
    raw_rows = flatten_with_categories(anchor_path)
    if len(raw_rows) != len(recaller.anchors):
        raise RuntimeError("flattened anchor count differs from recaller")
    for index, row in enumerate(raw_rows):
        if row["text"] != str(recaller.anchor_texts[index]) or row["target"] != str(recaller.targets[index]):
            raise RuntimeError(f"anchor order mismatch at index {index}")
    if any(category_group(row["category"]) == "other" for row in raw_rows):
        raise RuntimeError("unexpected top-level category in frozen anchor set")

    cards = load_cards(recaller.cards_path)
    formal_targets = sorted({row["target"] for row in raw_rows if row["category"] == FORMAL_CATEGORY})
    if len(formal_targets) != 71:
        raise RuntimeError(f"expected 71 formal intents, got {len(formal_targets)}")

    observer = LeaveOneOutObserver(recaller)
    matrix_started = perf_counter()
    semantic_matrix = np.asarray(recaller.anchor_vectors @ recaller.anchor_vectors.T, dtype=np.float32)
    np.fill_diagonal(semantic_matrix, -np.inf)
    matrix_ms = (perf_counter() - matrix_started) * 1000
    print(f"loaded {len(raw_rows)} anchors; semantic matrix ready in {matrix_ms:.1f} ms", flush=True)

    results: list[dict[str, Any]] = []
    loop_started = perf_counter()
    for index, raw in enumerate(raw_rows):
        text = raw["text"]
        literal_scores = recaller._literal_scores(text)
        pinyin_scores = recaller._pinyin_scores(text)
        literal_scores[index] = -np.inf
        pinyin_scores[index] = -np.inf
        scores_by_channel = {
            "semantic": semantic_matrix[index],
            "literal": literal_scores,
            "pinyin": pinyin_scores,
        }
        group = category_group(raw["category"])
        inspected = (
            observer.inspect_security(text, scores_by_channel)
            if group == "security"
            else observer.inspect_semantic(index, raw["target"], scores_by_channel)
        )
        fusion = inspected["fusion"]
        results.append(
            {
                "anchor_index": index,
                "anchor_text": text,
                "true_target": raw["target"],
                "top_level_category": raw["category"],
                "statistics_group": group,
                "self_masked": True,
                "correct_target_rank": fusion["correct_target_rank"],
                "top1_target": fusion["top1_target"],
                "top3_targets": fusion["top3_targets"],
                "top8_targets": fusion["top8_targets"],
                "channels": inspected["channels"],
                "fusion": fusion,
            }
        )
        if (index + 1) % 50 == 0 or index + 1 == len(raw_rows):
            elapsed = perf_counter() - loop_started
            print(f"leave-one-out {index + 1}/{len(raw_rows)} ({elapsed:.1f}s)", flush=True)

    semantic_rows = [row for row in results if row["statistics_group"] != "security"]
    correct_gaps = [
        float(row["fusion"]["top1_top2_rrf_gap"])
        for row in semantic_rows
        if row["top1_target"] == row["true_target"] and row["fusion"]["top1_top2_rrf_gap"] is not None
    ]
    p3_gap = float(percentile(correct_gaps, 0.10) or 0.0)
    semantic_correct_scores = [float(row["channels"]["semantic"]["correct_target_highest_similarity"]) for row in semantic_rows]
    semantic_outlier_cutoff = float(percentile(semantic_correct_scores, 0.05) or 0.0)
    length_cutoff = float(percentile([len(_normalized_text(row["anchor_text"])) for row in results], 0.10) or 0.0)

    by_target_semantic: dict[str, list[float]] = defaultdict(list)
    by_target_texts: dict[str, list[str]] = defaultdict(list)
    for row in semantic_rows:
        by_target_semantic[row["true_target"]].append(float(row["channels"]["semantic"]["correct_target_highest_similarity"]))
        by_target_texts[row["true_target"]].append(_normalized_text(row["anchor_text"]))
    target_semantic_medians = {target: float(np.median(values)) for target, values in by_target_semantic.items()}
    cluster_coverage_cutoff = float(percentile(target_semantic_medians.values(), 0.10) or 0.0)
    target_repetition_scores: dict[str, float] = {}
    for target, texts in by_target_texts.items():
        nearest_scores = [
            max(
                SequenceMatcher(None, text, other, autojunk=False).ratio()
                for other_index, other in enumerate(texts) if other_index != text_index
            )
            for text_index, text in enumerate(texts)
        ]
        target_repetition_scores[target] = float(np.median(nearest_scores))
    repetition_target_count = max(1, math.ceil(len(target_repetition_scores) * 0.10))
    high_repetition_targets = {
        target for target, _score in sorted(
            target_repetition_scores.items(), key=lambda item: (-item[1], item[0])
        )[:repetition_target_count]
    }
    repetition_cutoff = min(target_repetition_scores[target] for target in high_repetition_targets)
    threshold_source: str | None = None
    if args.diagnostic_thresholds_from is not None:
        threshold_path = args.diagnostic_thresholds_from.resolve()
        frozen_summary = json.loads(threshold_path.read_text(encoding="utf-8"))
        frozen_thresholds = frozen_summary["diagnostic_thresholds"]
        p3_gap = float(frozen_thresholds["p3_fusion_gap_p10"])
        semantic_outlier_cutoff = float(frozen_thresholds["semantic_same_target_similarity_p05"])
        length_cutoff = float(frozen_thresholds["normalized_text_length_p10"])
        cluster_coverage_cutoff = float(frozen_thresholds["target_semantic_median_p10"])
        repetition_cutoff = float(
            frozen_thresholds["target_standard_sequence_nearest_median_top_decile_boundary"]
        )
        high_repetition_targets = set(frozen_thresholds["high_repetition_targets"])
        threshold_source = str(threshold_path)

    repeated_fragment = re.compile(r"(.{2,6})\1")
    for row in results:
        correct_rank = row["correct_target_rank"]
        top1_correct = row["top1_target"] == row["true_target"]
        risks = risk_types(row["true_target"], row["top1_target"] or "", cards) if not top1_correct else []
        if correct_rank is None or correct_rank > 8:
            priority = "P0"
        elif not top1_correct and risks:
            priority = "P1"
        elif not top1_correct:
            priority = "P2"
        elif row["statistics_group"] != "security" and float(row["fusion"]["top1_top2_rrf_gap"] or 0.0) <= p3_gap:
            priority = "P3"
        else:
            priority = "P4"
        flags: list[str] = []
        normalized = _normalized_text(row["anchor_text"])
        if row["statistics_group"] != "security":
            semantic_score = float(row["channels"]["semantic"]["correct_target_highest_similarity"])
            if semantic_score <= semantic_outlier_cutoff:
                flags.append("同意图语义离群")
            if not top1_correct:
                flags.append("容易被其他意图吸走")
            if len(normalized) <= length_cutoff and priority in {"P0", "P1", "P2", "P3"}:
                flags.append("语义或动作对象表达可能不足")
            if priority == "P0" and all((row["channels"][channel]["correct_target_rank"] or 999) > 8 for channel in CHANNELS):
                flags.append("疑似错误挂靠")
            if target_semantic_medians[row["true_target"]] <= cluster_coverage_cutoff:
                flags.append("表达簇覆盖不足")
            if row["true_target"] in high_repetition_targets:
                flags.append("意图内部表达高度重复")
        if repeated_fragment.search(normalized):
            flags.append("疑似异常文本")
        row["risk_types"] = risks
        row["priority"] = priority
        row["quality_flags"] = list(dict.fromkeys(flags))

    group_rows = {
        "all": results,
        "formal": [row for row in results if row["statistics_group"] == "formal"],
        "bypass": [row for row in results if row["statistics_group"] == "bypass"],
        "security": [row for row in results if row["statistics_group"] == "security"],
    }
    accuracy = {name: accuracy_block(rows) for name, rows in group_rows.items()}

    confusion_counter: Counter[tuple[str, str]] = Counter()
    confusion_examples: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in results:
        if row["top1_target"] != row["true_target"]:
            wrong_target = row["top1_target"] or "NO_SIGNAL"
            pair = (row["true_target"], wrong_target)
            confusion_counter[pair] += 1
            confusion_examples[pair].append(row["anchor_text"])
    confusion_pairs = [
        {
            "true_target": true_target,
            "wrong_top1_target": wrong_target,
            "count": count,
            "risk_types": risk_types(true_target, wrong_target, cards),
            "anchor_examples": confusion_examples[(true_target, wrong_target)],
        }
        for (true_target, wrong_target), count in sorted(
            confusion_counter.items(), key=lambda item: (-item[1], item[0][0], item[0][1])
        )
    ]
    matrix: dict[str, dict[str, int]] = defaultdict(dict)
    for (true_target, wrong_target), count in confusion_counter.items():
        matrix[true_target][wrong_target] = count
    high_risk = [row for row in confusion_pairs if row["risk_types"]]

    formal_rows = group_rows["formal"]
    attractors: dict[str, Counter[str]] = defaultdict(Counter)
    absorbed_by: dict[str, Counter[str]] = defaultdict(Counter)
    for row in formal_rows:
        if row["top1_target"] != row["true_target"] and row["top1_target"]:
            absorbed_by[row["true_target"]][row["top1_target"]] += 1
            attractors[row["top1_target"]][row["true_target"]] += 1

    per_intent: list[dict[str, Any]] = []
    target_count = len(observer.semantic_target_indices)
    for target in formal_targets:
        rows = [row for row in formal_rows if row["true_target"] == target]
        ranks_for_average = [
            int(row["correct_target_rank"]) if row["correct_target_rank"] is not None else target_count + 1
            for row in rows
        ]
        top1_count = sum(row["correct_target_rank"] == 1 for row in rows)
        top3_count = sum(row["correct_target_rank"] is not None and row["correct_target_rank"] <= 3 for row in rows)
        top8_count = sum(row["correct_target_rank"] is not None and row["correct_target_rank"] <= 8 for row in rows)
        per_intent.append(
            {
                "intent_id": target,
                "intent_name": str(cards.get(target, {}).get("名称", "")),
                "anchor_count": len(rows),
                "top1_correct_count": top1_count,
                "top1_rate": rounded(top1_count / len(rows)),
                "top3_correct_count": top3_count,
                "top3_rate": rounded(top3_count / len(rows)),
                "top8_correct_count": top8_count,
                "top8_rate": rounded(top8_count / len(rows)),
                "average_correct_target_rank": rounded(mean(ranks_for_average)),
                "worst_correct_target_rank": max(ranks_for_average),
                "missing_from_fusion_count": sum(row["correct_target_rank"] is None for row in rows),
                "absorbed_count": sum(absorbed_by[target].values()),
                "most_common_absorber": most_common_or_none(absorbed_by[target]),
                "most_common_other_intents_it_attracts": [
                    {"target": other, "count": count}
                    for other, count in sorted(attractors[target].items(), key=lambda item: (-item[1], item[0]))
                ],
                "priority_counts": dict(sorted(Counter(row["priority"] for row in rows).items())),
            }
        )
    per_intent.sort(
        key=lambda row: (
            row["top1_rate"], row["top3_rate"], row["top8_rate"],
            -row["average_correct_target_rank"], row["intent_id"],
        )
    )

    repair_candidates: list[dict[str, Any]] = []
    for row in results:
        if row["priority"] == "P4" and not row["quality_flags"]:
            continue
        reason = reason_for(row)
        if reason not in ALLOWED_REASONS:
            raise RuntimeError(f"unexpected repair reason: {reason}")
        repair_candidates.append(
            {
                "anchor_index": row["anchor_index"],
                "anchor_text": row["anchor_text"],
                "true_target": row["true_target"],
                "top1_wrong_target": row["top1_target"] if row["top1_target"] != row["true_target"] else None,
                "correct_target_rank": row["correct_target_rank"],
                "priority": row["priority"],
                "three_channel_performance": row["channels"],
                "strongest_wrong_support_anchor": row["fusion"]["top1_strongest_anchor"] if row["top1_target"] != row["true_target"] else None,
                "strongest_correct_support_anchor": row["fusion"]["correct_target_strongest_anchor"],
                "confusion_pair": (
                    f"{row['true_target']} -> {row['top1_target']}"
                    if row["top1_target"] and row["top1_target"] != row["true_target"] else None
                ),
                "risk_types": row["risk_types"],
                "quality_flags": row["quality_flags"],
                "suggested_human_check_reason": reason,
            }
        )
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    repair_candidates.sort(key=lambda row: (priority_order[row["priority"]], row["true_target"], row["anchor_index"]))

    hash_after = sha256_file(anchor_path)
    if hash_after != hash_before:
        raise RuntimeError("frozen anchor file changed during diagnostics")

    score_distributions = {
        group: {
            channel: {
                "correct_target_highest_similarity": distribution(
                    row["channels"][channel]["correct_target_highest_similarity"] for row in rows
                ),
                "correct_target_rank": distribution(
                    row["channels"][channel]["correct_target_rank"]
                    for row in rows if row["channels"][channel]["correct_target_rank"] is not None
                ),
                "first_second_target_gap": distribution(
                    row["channels"][channel]["first_second_target_gap"]
                    for row in rows if row["channels"][channel]["first_second_target_gap"] is not None
                ),
            }
            for channel in CHANNELS
        }
        for group, rows in group_rows.items()
    }
    priority_counts = Counter(row["priority"] for row in results)
    summary = {
        "experiment": "anchor-loo-v1_1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "frozen_input": {
            "path": str(anchor_path),
            "sha256_before": hash_before,
            "sha256_after": hash_after,
            "unchanged": hash_before == hash_after,
        },
        "counts": {
            "all": len(results),
            "formal": len(group_rows["formal"]),
            "formal_intents": len(formal_targets),
            "bypass": len(group_rows["bypass"]),
            "bypass_targets": sorted({row["true_target"] for row in group_rows["bypass"]}),
            "security": len(group_rows["security"]),
            "security_targets": sorted({row["true_target"] for row in group_rows["security"]}),
        },
        "accuracy": accuracy,
        "priority_counts": {priority: priority_counts.get(priority, 0) for priority in ("P0", "P1", "P2", "P3", "P4")},
        "diagnostic_thresholds": {
            "p3_fusion_gap_p10": rounded(p3_gap),
            "semantic_same_target_similarity_p05": rounded(semantic_outlier_cutoff),
            "normalized_text_length_p10": rounded(length_cutoff),
            "target_semantic_median_p10": rounded(cluster_coverage_cutoff),
            "target_standard_sequence_nearest_median_top_decile_boundary": rounded(repetition_cutoff),
            "high_repetition_target_count": len(high_repetition_targets),
            "high_repetition_targets": sorted(high_repetition_targets),
            "source_summary": threshold_source,
            "note": (
                "Diagnostic-only boundaries reused from the frozen source summary; no retrieval threshold or weight was changed."
                if threshold_source
                else "All are diagnostic-only distribution boundaries; no retrieval threshold or weight was changed."
            ),
        },
        "distributions": {
            "fusion_top1_top2_gap_top1_correct_semantic_container": distribution(correct_gaps),
            "by_group_and_channel": score_distributions,
        },
        "confusion": {
            "wrong_top1_anchor_count": sum(confusion_counter.values()),
            "distinct_pairs": len(confusion_pairs),
            "high_risk_anchor_count": sum(row["count"] for row in high_risk),
            "high_risk_pair_count": len(high_risk),
            "opposite_action_anchor_count": sum(row["count"] for row in high_risk if "动作方向相反" in row["risk_types"]),
            "opposite_action_pair_count": sum(1 for row in high_risk if "动作方向相反" in row["risk_types"]),
        },
        "repair_candidate_count": len(repair_candidates),
        "runtime": {
            "semantic_matrix_ms": rounded(matrix_ms, 3),
            "leave_one_out_loop_ms": rounded((perf_counter() - loop_started) * 1000, 3),
            "total_ms": rounded((perf_counter() - started) * 1000, 3),
            "recaller_startup": recaller.startup_diagnostics(),
        },
        "method": {
            "all_anchors_tested": True,
            "self_anchor_masked_in_all_three_channels": True,
            "semantic_query_reused_cached_normalized_anchor_vector": True,
            "anchor_library_reencoded_per_query": False,
            "retrieval_algorithm_or_threshold_changed": False,
            "ollama_called": False,
            "security_kept_orthogonal": True,
        },
    }

    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "per-intent-stats.json", per_intent)
    write_json(output_dir / "all-anchor-results.json", results)
    write_json(
        output_dir / "confusion-pairs.json",
        {"pairs": confusion_pairs, "matrix": {target: dict(sorted(row.items())) for target, row in sorted(matrix.items())}},
    )
    write_json(output_dir / "high-risk-confusions.json", high_risk)
    write_json(output_dir / "repair-candidates.json", repair_candidates)
    with (output_dir / "repair-candidates.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        fields = [
            "anchor_index", "anchor_text", "true_target", "top1_wrong_target", "correct_target_rank",
            "priority", "three_channel_performance", "strongest_wrong_support_anchor",
            "strongest_correct_support_anchor", "confusion_pair", "risk_types", "quality_flags",
            "suggested_human_check_reason",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in repair_candidates:
            csv_row = dict(row)
            for field in ("three_channel_performance", "risk_types", "quality_flags"):
                csv_row[field] = json.dumps(csv_row[field], ensure_ascii=False, separators=(",", ":"))
            writer.writerow(csv_row)
    (output_dir / "README.md").write_text(
        build_readme(summary, per_intent, confusion_pairs, high_risk, repair_candidates),
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(output_dir),
        "sha256": hash_after,
        "accuracy": accuracy,
        "priorities": summary["priority_counts"],
        "confusion": summary["confusion"],
        "repair_candidates": len(repair_candidates),
        "runtime_ms": summary["runtime"]["total_ms"],
    }, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
