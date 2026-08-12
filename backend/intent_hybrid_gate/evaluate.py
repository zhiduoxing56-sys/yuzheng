from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any

import yaml

from gate import GateRun, HybridConfidenceGate


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[1]
ORIGINAL_CASES = ROOT_DIR / "experiments" / "intent_judge_v1" / "acceptance_cases.yaml"
HOLDOUT_CASES = BASE_DIR / "new_holdout_cases.yaml"
OUTPUT_DIR = ROOT_DIR / "test-results" / "intent-hybrid-gate" / "evaluation"
ORIGINAL_ASR_IDS = {
    "fixed_04_drive_mode_homophone",
    "fixed_05_cruise_homophone",
    "s1_16",
    "s1_17",
    "s1_18",
    "s2_17",
    "s2_18",
    "s2_19",
}
ORIGINAL_UNRELATED_IDS = {
    "s1_23",
    "s1_24",
    "s1_25",
    "s2_22",
    "s2_23",
    "s2_24",
    "s2_25",
    "s2_26",
}
ORIGINAL_INSUFFICIENT_IDS = {"s2_27", "s2_28", "s2_29", "s2_30"}
ORIGINAL_SAFETY_IDS = {
    "fixed_03_injection",
    "s1_19",
    "s1_20",
    "s1_21",
    "s1_22",
    "s2_20",
    "s2_21",
}
CORE_IDS = [
    "fixed_01_door",
    "fixed_02_multi",
    "fixed_03_injection",
    "fixed_04_drive_mode_homophone",
]


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = (len(ordered) - 1) * fraction
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return round(ordered[lower], 3)
    return round(
        ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower), 3
    )


def metric_summary(results: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = [
        float(item["metrics"][key])
        for item in results
        if item["metrics"].get(key) is not None
    ]
    return {
        "count": len(values),
        "mean": round(mean(values), 3) if values else None,
        "p50": percentile(values, 0.50),
        "p95": percentile(values, 0.95),
        "max": round(max(values), 3) if values else None,
    }


def accuracy(correct: int, total: int) -> dict[str, Any]:
    return {
        "correct": correct,
        "total": total,
        "rate": round(correct / total, 6) if total else None,
    }


def original_category(case: dict[str, Any]) -> str:
    case_id = str(case["id"])
    if case_id in ORIGINAL_ASR_IDS:
        return "asr"
    if case_id in ORIGINAL_UNRELATED_IDS:
        return "unrelated"
    if case_id in ORIGINAL_INSUFFICIENT_IDS:
        return "insufficient"
    if case_id in ORIGINAL_SAFETY_IDS:
        return "safety_plus_control"
    if len(case["expected_intents"]) > 1:
        return "multi_intent"
    return "clear_single"


def load_original_cases() -> list[dict[str, Any]]:
    groups = yaml.safe_load(ORIGINAL_CASES.read_text(encoding="utf-8"))
    return [
        {**case, "category": original_category(case), "source_group": str(group)}
        for group, cases in groups.items()
        for case in cases
    ]


def load_holdout_cases() -> list[dict[str, Any]]:
    return list(yaml.safe_load(HOLDOUT_CASES.read_text(encoding="utf-8"))["cases"])


def actual_ids(run: GateRun) -> list[str]:
    return [str(item["intent_id"]) for item in run.output["sub_intents"]]


def serialize_result(dataset: str, case: dict[str, Any], run: GateRun) -> dict[str, Any]:
    expected = [str(value) for value in case["expected_intents"]]
    actual = actual_ids(run)
    security_present = bool(run.output["security_signals"])
    return {
        "dataset": dataset,
        "id": case["id"],
        "category": case["category"],
        "input": case["text"],
        "expected_intents": expected,
        "expect_security": bool(case.get("expect_security", False)),
        "output": run.output,
        "gate_path": run.gate_path,
        "model_intent_ids": list(run.model_intent_ids),
        "raw_model_output": run.raw_model_output,
        "validation_errors": list(run.validation_errors),
        "metrics": run.metrics,
        "evidence": run.evidence,
        "checks": {
            "automatic_accept": run.output["semantic_status"] == "OK",
            "intent_order_exact": actual == expected,
            "security_correct": security_present == bool(case.get("expect_security", False)),
            "asr_review_correct": (
                run.output["semantic_status"] == "REVIEW"
                and run.output["suggested_target"] in expected
            )
            if case["category"] == "asr"
            else None,
        },
    }


def dataset_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = [item for item in results if item["checks"]["automatic_accept"]]
    accepted_correct = [item for item in accepted if item["checks"]["intent_order_exact"]]
    reviews = [item for item in results if item["output"]["semantic_status"] == "REVIEW"]
    no_matches = [item for item in results if item["output"]["semantic_status"] == "NO_MATCH"]
    multi = [item for item in results if item["category"] == "multi_intent"]
    asr = [item for item in results if item["category"] == "asr"]
    unrelated = [item for item in results if item["category"] == "unrelated"]
    insufficient = [item for item in results if item["category"] == "insufficient"]
    return {
        "total": len(results),
        "automatic_accept": {
            "count": len(accepted),
            "coverage": round(len(accepted) / len(results), 6),
            "correct": len(accepted_correct),
            "precision": round(len(accepted_correct) / len(accepted), 6) if accepted else None,
            "error_count": len(accepted) - len(accepted_correct),
            "error_ids": [item["id"] for item in accepted if not item["checks"]["intent_order_exact"]],
        },
        "review_count": len(reviews),
        "review_ids": [item["id"] for item in reviews],
        "no_match_count": len(no_matches),
        "no_match_ids": [item["id"] for item in no_matches],
        "multi_intent_complete_match": accuracy(
            sum(item["checks"]["intent_order_exact"] for item in multi), len(multi)
        ),
        "multi_intent_auto_accept_exact": accuracy(
            sum(
                item["checks"]["automatic_accept"]
                and item["checks"]["intent_order_exact"]
                for item in multi
            ),
            len(multi),
        ),
        "asr_correct_review": accuracy(
            sum(bool(item["checks"]["asr_review_correct"]) for item in asr), len(asr)
        ),
        "unrelated_wrong_auto_accept_count": sum(
            item["checks"]["automatic_accept"] for item in unrelated
        ),
        "insufficient_wrong_auto_accept_count": sum(
            item["checks"]["automatic_accept"] for item in insufficient
        ),
        "security_signal_accuracy": accuracy(
            sum(item["checks"]["security_correct"] for item in results), len(results)
        ),
        "gate_path_counts": dict(Counter(item["gate_path"] for item in results)),
        "model_call_count": sum(item["metrics"]["model_called"] for item in results),
    }


def latency_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    model_called = [item for item in results if item["metrics"]["model_called"]]
    return {
        "all_requests": {
            "first_stage_recall_ms": metric_summary(results, "first_stage_recall_ms"),
            "full_chain_wall_ms": metric_summary(results, "full_chain_wall_ms"),
        },
        "model_called_requests": {
            "count": len(model_called),
            "ollama_request_wall_ms": metric_summary(model_called, "ollama_request_wall_ms"),
            "first_token_latency_ms": metric_summary(model_called, "first_token_latency_ms"),
            "full_chain_wall_ms": metric_summary(model_called, "full_chain_wall_ms"),
            "prompt_token_count": metric_summary(model_called, "prompt_token_count"),
            "generated_token_count": metric_summary(model_called, "generated_token_count"),
        },
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    original_cases = load_original_cases()
    holdout_cases = load_holdout_cases()
    with HybridConfidenceGate() as gate:
        frozen_hash = gate.gate_config_sha256
        original_results: list[dict[str, Any]] = []
        for index, case in enumerate(original_cases, start=1):
            run = gate.run(str(case["text"]))
            original_results.append(serialize_result("original60", case, run))
            if index % 10 == 0:
                print(f"original {index}/{len(original_cases)}", flush=True)
        holdout_results: list[dict[str, Any]] = []
        for index, case in enumerate(holdout_cases, start=1):
            run = gate.run(str(case["text"]))
            holdout_results.append(serialize_result("new_holdout", case, run))
            if index % 10 == 0 or index == len(holdout_cases):
                print(f"holdout {index}/{len(holdout_cases)}", flush=True)

    all_results = original_results + holdout_results
    current_hash = hashlib.sha256((BASE_DIR / "gate_config.yaml").read_bytes()).hexdigest()
    if current_hash != frozen_hash:
        raise RuntimeError("gate thresholds changed during evaluation")
    summary = {
        "experiment": "intent_hybrid_gate_precision_first",
        "completed_at": datetime.now().astimezone().isoformat(),
        "evaluation_wall_seconds": round(perf_counter() - started, 3),
        "frozen_gate_config_sha256": frozen_hash,
        "holdout_case_file_sha256": hashlib.sha256(HOLDOUT_CASES.read_bytes()).hexdigest(),
        "original60": dataset_summary(original_results),
        "new_holdout": dataset_summary(holdout_results),
        "combined": dataset_summary(all_results),
        "latency": latency_summary(all_results),
        "core_results": [
            next(item for item in original_results if item["id"] == case_id)
            for case_id in CORE_IDS
        ],
    }
    write_json(OUTPUT_DIR / "summary.json", summary)
    write_json(OUTPUT_DIR / "original60-results.json", original_results)
    write_json(OUTPUT_DIR / "new-holdout-results.json", holdout_results)
    write_json(OUTPUT_DIR / "all-results.json", all_results)
    (OUTPUT_DIR / "frozen-gate-config.yaml").write_text(
        (BASE_DIR / "gate_config.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (OUTPUT_DIR / "new_holdout_cases.yaml").write_text(
        HOLDOUT_CASES.read_text(encoding="utf-8"), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "original60": summary["original60"],
                "new_holdout": summary["new_holdout"],
                "latency": summary["latency"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
