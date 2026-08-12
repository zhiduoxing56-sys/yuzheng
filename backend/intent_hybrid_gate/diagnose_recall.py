from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
import yaml


BASE_DIR = Path(__file__).resolve().parent
EXPERIMENTS_DIR = BASE_DIR.parent
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))

from intent_recall_v1.recaller import CHANNELS, CandidateIntentRecaller  # noqa: E402


ROOT_DIR = BASE_DIR.parents[1]
RECALL_CONFIG = ROOT_DIR / "test-results" / "intent-recall-v1_1" / "config_v1_1.yaml"
CASE_FILE = ROOT_DIR / "experiments" / "intent_judge_v1" / "acceptance_cases.yaml"
OUTPUT_DIR = ROOT_DIR / "test-results" / "intent-hybrid-gate" / "diagnostic"


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = (len(ordered) - 1) * fraction
    lower = math.floor(rank)
    upper = math.ceil(rank)
    value = (
        ordered[lower]
        if lower == upper
        else ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower)
    )
    return round(float(value), 6)


def distribution(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "min": round(min(values), 6) if values else None,
        "p10": percentile(values, 0.10),
        "p25": percentile(values, 0.25),
        "p50": percentile(values, 0.50),
        "p75": percentile(values, 0.75),
        "p90": percentile(values, 0.90),
        "max": round(max(values), 6) if values else None,
        "mean": round(mean(values), 6) if values else None,
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def parse_target(display: str) -> str:
    return display.split("（", 1)[0]


class RecallDiagnosticObserver:
    def __init__(self, recaller: CandidateIntentRecaller) -> None:
        self.recaller = recaller
        grouped: dict[str, list[int]] = defaultdict(list)
        for anchor_index in recaller.semantic_indices.tolist():
            grouped[str(recaller.targets[anchor_index])].append(int(anchor_index))
        self.target_indices = {
            target: np.asarray(indices, dtype=np.int64)
            for target, indices in grouped.items()
        }

    def _complete_channel_ranking(
        self, scores: np.ndarray
    ) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
        rows: list[dict[str, Any]] = []
        for target, indices in self.target_indices.items():
            local_scores = scores[indices]
            local_order = np.argsort(-local_scores, kind="stable")
            anchor_index = int(indices[int(local_order[0])])
            rows.append(
                {
                    "target": target,
                    "score": round(float(scores[anchor_index]), 6),
                    "anchor": str(self.recaller.anchor_texts[anchor_index]),
                    "anchor_index": anchor_index,
                }
            )
        rows.sort(key=lambda item: (-item["score"], item["anchor_index"], item["target"]))
        mapping: dict[str, dict[str, Any]] = {}
        for rank, row in enumerate(rows, start=1):
            compact = {
                "rank": rank,
                "score": row["score"],
                "anchor": row["anchor"],
            }
            mapping[str(row["target"])] = compact
            row["rank"] = rank
            row.pop("anchor_index")
        return rows, mapping

    @staticmethod
    def _strongest_anchor(channel_rows: dict[str, dict[str, Any]]) -> str:
        grouped: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
        for channel, row in channel_rows.items():
            grouped[str(row["anchor"])].append((channel, row))
        return min(
            grouped,
            key=lambda anchor: (
                -len(grouped[anchor]),
                min(item[1]["rank"] for item in grouped[anchor]),
                -max(item[1]["score"] for item in grouped[anchor]),
                anchor,
            ),
        )

    def inspect(self, text: str) -> dict[str, Any]:
        score_map = {
            "semantic": self.recaller._semantic_scores(text),
            "literal": self.recaller._literal_scores(text),
            "pinyin": self.recaller._pinyin_scores(text),
        }
        frozen_rankings = {
            channel: self.recaller._channel_rankings(scores)
            for channel, scores in score_map.items()
        }
        fused = self.recaller._fuse_semantic_candidates(frozen_rankings, 8)
        fused_ids = [parse_target(str(item["target"])) for item in fused]
        complete_rows: dict[str, list[dict[str, Any]]] = {}
        channel_maps: dict[str, dict[str, dict[str, Any]]] = {}
        channel_summary: dict[str, Any] = {}
        for channel in CHANNELS:
            rows, mapping = self._complete_channel_ranking(score_map[channel])
            complete_rows[channel] = rows
            channel_maps[channel] = mapping
            channel_summary[channel] = {
                "first_target": rows[0]["target"],
                "first_score": rows[0]["score"],
                "first_anchor": rows[0]["anchor"],
                "second_target": rows[1]["target"],
                "second_score": rows[1]["score"],
                "second_anchor": rows[1]["anchor"],
                "first_second_gap": round(rows[0]["score"] - rows[1]["score"], 6),
            }

        target_rows: list[dict[str, Any]] = []
        channel_target_limit = int(
            self.recaller.config["retrieval"]["channel_target_top_k"]
        )
        for target in sorted(self.target_indices):
            per_channel = {
                channel: channel_maps[channel][target] for channel in CHANNELS
            }
            target_rows.append(
                {
                    "target": target,
                    "fused_top8_rank": (
                        fused_ids.index(target) + 1 if target in fused_ids else None
                    ),
                    "channel_support_count": sum(
                        row["rank"] <= channel_target_limit
                        for row in per_channel.values()
                    ),
                    "strongest_support_anchor": self._strongest_anchor(per_channel),
                    "channels": per_channel,
                }
            )
        return {
            "input": text,
            "fused_top8": fused_ids,
            "fused_candidates": fused,
            "channel_summary": channel_summary,
            "targets": target_rows,
            "complete_channel_rankings": complete_rows,
        }


def target_row(sample: dict[str, Any], target: str) -> dict[str, Any]:
    return next(item for item in sample["diagnostic"]["targets"] if item["target"] == target)


def sample_feature_row(sample: dict[str, Any], target: str) -> dict[str, Any]:
    row = target_row(sample, target)
    return {
        "target": target,
        "channel_support_count": row["channel_support_count"],
        "strongest_support_anchor": row["strongest_support_anchor"],
        "channels": row["channels"],
        "channel_top_gaps": {
            channel: sample["diagnostic"]["channel_summary"][channel]["first_second_gap"]
            for channel in CHANNELS
        },
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    case_groups = yaml.safe_load(CASE_FILE.read_text(encoding="utf-8"))
    all_cases = [
        (str(group), case)
        for group, cases in case_groups.items()
        for case in cases
    ]
    recaller = CandidateIntentRecaller(RECALL_CONFIG)
    observer = RecallDiagnosticObserver(recaller)
    samples: list[dict[str, Any]] = []
    for index, (group, case) in enumerate(all_cases, start=1):
        diagnostic = observer.inspect(str(case["text"]))
        samples.append(
            {
                "group": group,
                "id": case["id"],
                "input": case["text"],
                "expected_intents": list(case["expected_intents"]),
                "expect_security": bool(case.get("expect_security", False)),
                "diagnostic": diagnostic,
            }
        )
        if index % 10 == 0:
            print(f"diagnostic {index}/{len(all_cases)}", flush=True)

    single = [item for item in samples if len(item["expected_intents"]) == 1]
    multi = [item for item in samples if len(item["expected_intents"]) > 1]
    empty = [item for item in samples if not item["expected_intents"]]
    top_k: dict[str, Any] = {}
    for k in (1, 2, 3, 8):
        correct = sum(
            item["expected_intents"][0] in item["diagnostic"]["fused_top8"][:k]
            for item in single
        )
        top_k[f"top{k}"] = {
            "correct": correct,
            "total": len(single),
            "rate": round(correct / len(single), 6),
        }
    multi_all = sum(
        set(item["expected_intents"]).issubset(item["diagnostic"]["fused_top8"])
        for item in multi
    )

    correct_target_scores = {
        channel: [
            float(target_row(item, item["expected_intents"][0])["channels"][channel]["score"])
            for item in single
        ]
        for channel in CHANNELS
    }
    correct_target_ranks = {
        channel: [
            float(target_row(item, item["expected_intents"][0])["channels"][channel]["rank"])
            for item in single
        ]
        for channel in CHANNELS
    }
    empty_channel_winner_scores = {
        channel: [
            float(item["diagnostic"]["channel_summary"][channel]["first_score"])
            for item in empty
        ]
        for channel in CHANNELS
    }
    single_channel_gaps = {
        channel: [
            float(item["diagnostic"]["channel_summary"][channel]["first_second_gap"])
            for item in single
        ]
        for channel in CHANNELS
    }
    empty_channel_gaps = {
        channel: [
            float(item["diagnostic"]["channel_summary"][channel]["first_second_gap"])
            for item in empty
        ]
        for channel in CHANNELS
    }
    single_top1_features = [
        sample_feature_row(item, item["diagnostic"]["fused_top8"][0]) for item in single
    ]
    empty_top1_features = [
        sample_feature_row(item, item["diagnostic"]["fused_top8"][0]) for item in empty
    ]
    summary = {
        "dataset": {
            "total": len(samples),
            "single_intent": len(single),
            "multi_intent": len(multi),
            "empty_or_insufficient": len(empty),
        },
        "single_intent_fused_accuracy": top_k,
        "multi_intent_all_targets_in_top8": {
            "correct": multi_all,
            "total": len(multi),
            "rate": round(multi_all / len(multi), 6),
        },
        "distributions": {
            "single_correct_target": {
                channel: {
                    "score": distribution(correct_target_scores[channel]),
                    "rank": distribution(correct_target_ranks[channel]),
                }
                for channel in CHANNELS
            },
            "single_channel_first_second_gap": {
                channel: distribution(single_channel_gaps[channel]) for channel in CHANNELS
            },
            "empty_channel_winner": {
                channel: {
                    "score": distribution(empty_channel_winner_scores[channel]),
                    "first_second_gap": distribution(empty_channel_gaps[channel]),
                }
                for channel in CHANNELS
            },
            "single_fused_top1_channel_support_count": distribution(
                [float(item["channel_support_count"]) for item in single_top1_features]
            ),
            "empty_fused_top1_channel_support_count": distribution(
                [float(item["channel_support_count"]) for item in empty_top1_features]
            ),
        },
        "single_top1_error_ids": [
            item["id"]
            for item in single
            if item["diagnostic"]["fused_top8"][0] != item["expected_intents"][0]
        ],
        "multi_top8_miss_ids": [
            item["id"]
            for item in multi
            if not set(item["expected_intents"]).issubset(item["diagnostic"]["fused_top8"])
        ],
        "startup": recaller.startup_diagnostics(),
        "v1_1_sha256": hashlib.sha256(recaller.anchor_path.read_bytes()).hexdigest(),
    }
    no_target_report = [
        {
            "id": item["id"],
            "input": item["input"],
            "fused_top8": item["diagnostic"]["fused_top8"],
            "channel_summary": item["diagnostic"]["channel_summary"],
            "fused_top1_features": empty_top1_features[index],
        }
        for index, item in enumerate(empty)
    ]
    write_json(OUTPUT_DIR / "diagnostic-summary.json", summary)
    write_json(OUTPUT_DIR / "sample-evidence.json", samples)
    write_json(OUTPUT_DIR / "no-target-distribution.json", no_target_report)
    (OUTPUT_DIR / "acceptance_cases.yaml").write_text(
        CASE_FILE.read_text(encoding="utf-8"), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
