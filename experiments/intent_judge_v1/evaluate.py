from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any

import yaml

from judge import CandidateIntentJudge, JudgeRun


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CASES = BASE_DIR / "acceptance_cases.yaml"
DEFAULT_OUTPUT = BASE_DIR.parents[1] / "test-results" / "intent-judge-v1"


def percentile(values: list[float], percentile_value: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile_value
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return round(ordered[lower], 3)
    value = ordered[lower] + (ordered[upper] - ordered[lower]) * (rank - lower)
    return round(value, 3)


def metric_summary(runs: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = [float(run[key]) for run in runs if run.get(key) is not None]
    return {
        "count": len(values),
        "mean": round(mean(values), 3) if values else None,
        "p50": percentile(values, 0.50),
        "p95": percentile(values, 0.95),
        "max": round(max(values), 3) if values else None,
    }


def load_cases(path: Path) -> dict[str, list[dict[str, Any]]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("case file root must be a mapping")
    return {str(key): list(value) for key, value in payload.items()}


def actual_ids(run: JudgeRun) -> list[str]:
    return [str(item["intent_id"]) for item in run.output["sub_intents"]]


def assess_case(group: str, case: dict[str, Any], run: JudgeRun) -> dict[str, Any]:
    expected_ids = [str(value) for value in case["expected_intents"]]
    observed_ids = actual_ids(run)
    allowed_statuses = [str(value) for value in case["allowed_statuses"]]
    security_present = bool(run.output["security_signals"])
    expect_security = bool(case.get("expect_security", False))
    expected_confirmation = case.get("expected_confirmation")
    observed_confirmation = (
        run.output["confirmation"].get("suggested_text")
        if isinstance(run.output.get("confirmation"), dict)
        else None
    )
    intents_correct = observed_ids == expected_ids
    status_correct = run.output["status"] in allowed_statuses
    security_correct = security_present == expect_security
    confirmation_correct = (
        observed_confirmation == expected_confirmation
        if expected_confirmation is not None
        else True
    )
    return {
        "group": group,
        "id": case["id"],
        "input": case["text"],
        "expected": {
            "statuses": allowed_statuses,
            "intent_ids": expected_ids,
            "security_present": expect_security,
            "confirmation": expected_confirmation,
        },
        "output": run.output,
        "raw_model_output": run.raw_model_output,
        "validation_errors": list(run.validation_errors),
        "metrics": run.metrics,
        "semantic_candidates": [
            {
                "target": item["target"],
                "channels": item["channels"],
                "support_anchors": item["support_anchors"][:2],
            }
            for item in run.recall_result["semantic_candidates"]
        ],
        "checks": {
            "intents_correct": intents_correct,
            "status_correct": status_correct,
            "security_correct": security_correct,
            "confirmation_correct": confirmation_correct,
            "complete_correct": (
                intents_correct
                and status_correct
                and security_correct
                and confirmation_correct
            ),
        },
    }


def accuracy(numerator: int, denominator: int) -> dict[str, Any]:
    return {
        "correct": numerator,
        "total": denominator,
        "rate": round(numerator / denominator, 4) if denominator else None,
    }


def suite_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    complete = sum(item["checks"]["complete_correct"] for item in results)
    single = [item for item in results if len(item["expected"]["intent_ids"]) == 1]
    multi = [item for item in results if len(item["expected"]["intent_ids"]) > 1]
    no_match = [item for item in results if not item["expected"]["intent_ids"]]
    review_outputs = [item for item in results if item["output"]["status"] == "REVIEW"]
    review_expected = [
        item for item in results if "REVIEW" in item["expected"]["statuses"]
    ]
    forced = [
        item
        for item in no_match
        if item["output"]["sub_intents"]
    ]
    return {
        "complete_accuracy": accuracy(complete, len(results)),
        "single_intent_accuracy": accuracy(
            sum(item["checks"]["intents_correct"] for item in single), len(single)
        ),
        "multi_intent_exact_match": accuracy(
            sum(item["checks"]["intents_correct"] for item in multi), len(multi)
        ),
        "no_match_correct_rejection": accuracy(
            sum(
                item["output"]["status"] == "NO_MATCH"
                and not item["output"]["sub_intents"]
                for item in no_match
            ),
            len(no_match),
        ),
        "wrong_forced_classification_count": len(forced),
        "wrong_forced_classification_ids": [item["id"] for item in forced],
        "review_usage": {
            "output_count": len(review_outputs),
            "expected_or_allowed_count": len(review_expected),
            "output_ids": [item["id"] for item in review_outputs],
        },
        "sub_intent_order_accuracy": accuracy(
            sum(item["checks"]["intents_correct"] for item in multi), len(multi)
        ),
        "security_signal_accuracy": accuracy(
            sum(item["checks"]["security_correct"] for item in results), len(results)
        ),
        "status_counts": dict(Counter(item["output"]["status"] for item in results)),
        "failed_case_ids": [
            item["id"] for item in results if not item["checks"]["complete_correct"]
        ],
    }


def serializable_run(run: JudgeRun) -> dict[str, Any]:
    return {
        "output": run.output,
        "metrics": run.metrics,
        "raw_model_output": run.raw_model_output,
        "validation_errors": list(run.validation_errors),
        "prompt": run.prompt,
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="候选裁决器离线验收与热态延迟测试")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--hot-runs", type=int, default=50)
    args = parser.parse_args()
    if args.hot_runs < 50:
        raise ValueError("hot-runs must be at least 50 for formal evaluation")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    groups = load_cases(args.cases.resolve())
    all_cases = [
        (group, case) for group, cases in groups.items() for case in cases
    ]
    started_at = datetime.now().astimezone().isoformat()

    with CandidateIntentJudge() as judge:
        judge.unload_model()
        before_cold = judge.resident_models()
        cold_started = perf_counter()
        cold_run = judge.judge(groups["fixed"][0]["text"])
        cold_wall = round((perf_counter() - cold_started) * 1000, 3)
        after_cold = judge.resident_models()
        warmup_run = judge.judge(groups["fixed"][0]["text"])

        results: list[dict[str, Any]] = []
        for index, (group, case) in enumerate(all_cases, start=1):
            run = judge.judge(str(case["text"]))
            results.append(assess_case(group, case, run))
            print(f"suite {index}/{len(all_cases)} {case['id']} {run.output['status']}", flush=True)

        latency_cases = [case for _, case in all_cases]
        hot_metrics: list[dict[str, Any]] = []
        hot_outputs: list[dict[str, Any]] = []
        for index in range(args.hot_runs):
            case = latency_cases[index % len(latency_cases)]
            run = judge.judge(str(case["text"]))
            hot_metrics.append(run.metrics)
            hot_outputs.append(
                {
                    "run": index + 1,
                    "case_id": case["id"],
                    "input": case["text"],
                    "status": run.output["status"],
                    "intent_ids": actual_ids(run),
                    "metrics": run.metrics,
                }
            )
            if (index + 1) % 10 == 0:
                print(f"latency {index + 1}/{args.hot_runs}", flush=True)

        model_resident_after = judge.resident_models()

    latency_keys = [
        "first_stage_recall_ms",
        "ollama_request_wall_ms",
        "first_token_latency_ms",
        "model_output_duration_ms",
        "full_chain_wall_ms",
        "prompt_token_count",
        "generated_token_count",
    ]
    summary = suite_summary(results)
    latency_summary = {key: metric_summary(hot_metrics, key) for key in latency_keys}
    death_gate = {
        "hot_ollama_p95_le_2000ms": (
            latency_summary["ollama_request_wall_ms"]["p95"] is not None
            and latency_summary["ollama_request_wall_ms"]["p95"] <= 2000
        ),
        "multi_intent_usable": summary["multi_intent_exact_match"]["rate"] >= 0.8,
        "no_match_usable": summary["no_match_correct_rejection"]["rate"] >= 0.8,
    }
    death_gate["passed"] = all(death_gate.values())
    report = {
        "experiment": "intent_judge_v1",
        "started_at": started_at,
        "completed_at": datetime.now().astimezone().isoformat(),
        "model": "qwen2.5:1.5b",
        "case_counts": {key: len(value) for key, value in groups.items()},
        "suite": summary,
        "cold_request": {
            "resident_before": before_cold,
            "resident_after": after_cold,
            "outer_wall_ms": cold_wall,
            **serializable_run(cold_run),
        },
        "warmup_request": serializable_run(warmup_run),
        "hot_latency_runs": args.hot_runs,
        "hot_latency": latency_summary,
        "model_resident_after": model_resident_after,
        "death_gate": death_gate,
    }
    write_json(output_dir / "summary.json", report)
    write_json(output_dir / "case-results.json", results)
    write_json(output_dir / "hot-latency-runs.json", hot_outputs)
    write_json(output_dir / "actual-prompt-and-schema.json", cold_run.prompt)
    (output_dir / "acceptance_cases.yaml").write_text(
        args.cases.resolve().read_text(encoding="utf-8"), encoding="utf-8"
    )
    print(json.dumps({"summary": summary, "latency": latency_summary, "death_gate": death_gate}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
