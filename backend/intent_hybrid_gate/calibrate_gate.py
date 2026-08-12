from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import yaml


BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from intent_recall_v1.recaller import CandidateIntentRecaller  # noqa: E402


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(base: Path, configured: str) -> Path:
    path = Path(configured)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def target_rows(sample: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item["target"]): item for item in sample["diagnostic"]["targets"]
    }


def unanimous_top1(sample: dict[str, Any], target: str) -> bool:
    row = target_rows(sample)[target]
    return all(row["channels"][channel]["rank"] == 1 for channel in ("semantic", "literal", "pinyin"))


def asr_review(
    sample: dict[str, Any],
    recaller: CandidateIntentRecaller,
    config: dict[str, Any],
) -> tuple[bool, dict[str, Any] | None]:
    target = str(sample["diagnostic"]["fused_top8"][0])
    if config["require_fused_top1_rank_one_in_all_channels"] and not unanimous_top1(sample, target):
        return False, None
    literal_scores = recaller._literal_scores(str(sample["input"]))
    pinyin_scores = recaller._pinyin_scores(str(sample["input"]))
    indices = np.where(recaller.targets == target)[0]
    best_index = int(indices[np.argsort(-pinyin_scores[indices], kind="stable")[0]])
    best = config["best_pinyin_anchor"]
    best_matches = (
        float(pinyin_scores[best_index]) >= float(best["min_pinyin_score"])
        and float(literal_scores[best_index]) <= float(best["max_literal_score"])
        and float(pinyin_scores[best_index] - literal_scores[best_index])
        >= float(best["min_pinyin_literal_gain"])
    )
    high = config["high_similarity_target_anchor"]
    high_indices = [
        int(index)
        for index in indices
        if float(pinyin_scores[index]) >= float(high["min_pinyin_score"])
        and float(literal_scores[index]) <= float(high["max_literal_score"])
        and float(pinyin_scores[index] - literal_scores[index])
        >= float(high["min_pinyin_literal_gain"])
    ]
    if not best_matches and not high_indices:
        return False, None
    selected_index = (
        best_index
        if best_matches
        else max(
            high_indices,
            key=lambda index: (
                float(pinyin_scores[index]),
                float(pinyin_scores[index] - literal_scores[index]),
                -float(literal_scores[index]),
                -index,
            ),
        )
    )
    return True, {
        "target": target,
        "suggested_text": str(recaller.anchor_texts[selected_index]),
        "pinyin_score": round(float(pinyin_scores[selected_index]), 6),
        "literal_score": round(float(literal_scores[selected_index]), 6),
        "gain": round(
            float(pinyin_scores[selected_index] - literal_scores[selected_index]), 6
        ),
    }


def direct_accept(sample: dict[str, Any], config: dict[str, Any]) -> bool:
    target = str(sample["diagnostic"]["fused_top8"][0])
    if config["require_fused_top1_rank_one_in_all_channels"] and not unanimous_top1(sample, target):
        return False
    row = target_rows(sample)[target]
    channels = row["channels"]
    gaps = sample["diagnostic"]["channel_summary"]
    strong = config["strong_consensus"]
    strong_match = (
        channels["semantic"]["score"] >= strong["min_semantic_score"]
        and channels["literal"]["score"] >= strong["min_literal_score"]
        and channels["pinyin"]["score"] >= strong["min_pinyin_score"]
        and gaps["semantic"]["first_second_gap"]
        >= strong["min_semantic_first_second_gap"]
        and gaps["literal"]["first_second_gap"]
        >= strong["min_literal_first_second_gap"]
        and gaps["pinyin"]["first_second_gap"]
        >= strong["min_pinyin_first_second_gap"]
    )
    exact = config["exact_lexical_consensus"]
    exact_match = (
        channels["semantic"]["score"] >= exact["min_semantic_score"]
        and channels["literal"]["score"] >= exact["min_literal_score"]
        and channels["pinyin"]["score"] >= exact["min_pinyin_score"]
        and gaps["literal"]["first_second_gap"]
        >= exact["min_literal_first_second_gap"]
        and gaps["pinyin"]["first_second_gap"]
        >= exact["min_pinyin_first_second_gap"]
    )
    return strong_match or exact_match


def open_set_no_match(sample: dict[str, Any], config: dict[str, Any]) -> bool:
    summary = sample["diagnostic"]["channel_summary"]
    return (
        summary["semantic"]["first_score"]
        <= config["max_semantic_channel_winner_score"]
        and summary["literal"]["first_score"]
        <= config["max_literal_channel_winner_score"]
        and summary["semantic"]["first_second_gap"]
        <= config["max_semantic_first_second_gap"]
    )


def model_consistent(
    sample: dict[str, Any], selected: list[str], config: dict[str, Any]
) -> bool:
    if not selected:
        return False
    top1 = str(sample["diagnostic"]["fused_top8"][0])
    if config["require_fused_top1_selected"] and top1 not in selected:
        return False
    rows = target_rows(sample)
    max_rank = int(config["strong_channel_rank_max"])
    min_count = int(config["min_strong_channel_count_per_selected_target"])
    for target in selected:
        if target not in rows:
            return False
        count = sum(
            rows[target]["channels"][channel]["rank"] <= max_rank
            for channel in ("semantic", "literal", "pinyin")
        )
        if count < min_count:
            return False
    return True


def main() -> None:
    config_path = BASE_DIR / "gate_config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    paths = config["paths"]
    samples = load_json(resolve(BASE_DIR, paths["diagnostic_samples"]))
    diagnostic_summary = load_json(resolve(BASE_DIR, paths["diagnostic_summary"]))
    model_results = {
        str(item["id"]): [
            str(intent["intent_id"]) for intent in item["output"]["sub_intents"]
        ]
        for item in load_json(resolve(BASE_DIR, paths["frozen_3b_case_results"]))
    }
    recall_config = resolve(BASE_DIR, config["frozen_components"]["recall_config"])
    recaller = CandidateIntentRecaller(recall_config)
    results: list[dict[str, Any]] = []
    for sample in samples:
        top1 = str(sample["diagnostic"]["fused_top8"][0])
        asr, asr_evidence = asr_review(sample, recaller, config["asr_review"])
        if asr:
            path = "ASR_REVIEW"
            automatic_ids: list[str] = []
        elif direct_accept(sample, config["direct_accept"]):
            path = "DIRECT_ACCEPT"
            automatic_ids = [top1]
        elif open_set_no_match(sample, config["open_set_no_match"]):
            path = "OPEN_SET_NO_MATCH"
            automatic_ids = []
        else:
            selected = model_results[str(sample["id"])]
            if model_consistent(sample, selected, config["model_consistency"]):
                path = "MODEL_ACCEPT"
                automatic_ids = selected
            else:
                path = "MODEL_REVIEW"
                automatic_ids = []
        expected = list(sample["expected_intents"])
        results.append(
            {
                "id": sample["id"],
                "input": sample["input"],
                "expected_intents": expected,
                "path": path,
                "automatic_intent_ids": automatic_ids,
                "automatic_correct": automatic_ids == expected,
                "asr_evidence": asr_evidence,
                "frozen_model_intent_ids": model_results[str(sample["id"])],
            }
        )

    accepted = [item for item in results if item["path"] in {"DIRECT_ACCEPT", "MODEL_ACCEPT"}]
    no_match = [item for item in results if item["path"] == "OPEN_SET_NO_MATCH"]
    review = [item for item in results if item["path"] in {"ASR_REVIEW", "MODEL_REVIEW"}]
    output_dir = resolve(BASE_DIR, paths["calibration_output"])
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "frozen": True,
        "gate_config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "recall_config_sha256": hashlib.sha256(recall_config.read_bytes()).hexdigest(),
        "anchor_sha256": hashlib.sha256(recaller.anchor_path.read_bytes()).hexdigest(),
        "threshold_provenance": {
            "direct_strong_consensus": "正样本分数约P10/P25及通道间隔约P25向保守方向取整；校准集零错误",
            "direct_exact_lexical": "安全注入+明确车控的语义分最低0.642503，无关样本语义通道最高0.548508，分界向保守方向取0.60；多意图字面/拼音间隔常为0",
            "open_set": "8条明显无关样本语义最高分最大0.548508、字面最高分最大0.50、语义间隔最大0.022649，分别向外取0.55/0.50/0.025",
            "asr": "校准ASR样本的同目标拼音锚点最低约0.70；为覆盖低分长句采用0.69/0.51分支，高相似错字采用0.95/0.81分支；均要求三通道目标排名一致",
            "model_consistency": "11条3B正确多意图中每个所选目标至少两个通道进入Top3；两个错误多意图均含不满足该条件的目标或遗漏融合Top1",
        },
        "diagnostic_topk": diagnostic_summary["single_intent_fused_accuracy"],
        "path_counts": dict(Counter(item["path"] for item in results)),
        "automatic_accept": {
            "count": len(accepted),
            "coverage": round(len(accepted) / len(results), 6),
            "correct": sum(item["automatic_correct"] for item in accepted),
            "precision": round(
                sum(item["automatic_correct"] for item in accepted) / len(accepted), 6
            ),
            "errors": [item for item in accepted if not item["automatic_correct"]],
        },
        "review_count": len(review),
        "no_match_count": len(no_match),
        "no_match_correct": sum(not item["expected_intents"] for item in no_match),
        "results": results,
    }
    (output_dir / "frozen-gate-config.yaml").write_text(
        config_path.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (output_dir / "calibration-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: report[key] for key in ("gate_config_sha256", "path_counts", "automatic_accept", "review_count", "no_match_count", "no_match_correct")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
