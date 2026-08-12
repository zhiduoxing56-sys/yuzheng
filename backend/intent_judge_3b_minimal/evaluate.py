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

from judge import JudgeRun, MinimalCandidateJudge


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = BASE_DIR.parents[1] / "test-results" / "intent-judge-3b-minimal"
FOCUS_IDS = [
    "fixed_01_door",
    "fixed_02_multi",
    "fixed_03_injection",
    "fixed_04_drive_mode_homophone",
    "fixed_05_cruise_homophone",
    "s2_27",
    "s2_22",
    "s2_23",
]


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


def accuracy(correct: int, total: int) -> dict[str, Any]:
    return {
        "correct": correct,
        "total": total,
        "rate": round(correct / total, 4) if total else None,
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def actual_ids(run: JudgeRun) -> list[str]:
    return list(run.model_selection["intent_ids"])


def same_set_without_duplicates(left: list[str], right: list[str]) -> bool:
    return len(left) == len(right) and len(left) == len(set(left)) and set(left) == set(right)


def assess_case(group: str, case: dict[str, Any], run: JudgeRun) -> dict[str, Any]:
    expected = [str(value) for value in case["expected_intents"]]
    observed = actual_ids(run)
    expected_confirmation = case.get("expected_confirmation")
    observed_confirmation = (
        run.output["confirmation"].get("suggested_text")
        if isinstance(run.output.get("confirmation"), dict)
        else None
    )
    expect_security = bool(case.get("expect_security", False))
    security_present = bool(run.output["security_signals"])
    return {
        "group": group,
        "id": case["id"],
        "input": case["text"],
        "expected": {
            "intent_ids": expected,
            "security_present": expect_security,
            "confirmation": expected_confirmation,
        },
        "model_selection": run.model_selection,
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
            "intent_set_exact": same_set_without_duplicates(observed, expected),
            "intent_order_exact": observed == expected,
            "empty_array_correct": not expected and not observed,
            "security_correct": security_present == expect_security,
            "confirmation_correct": (
                observed_confirmation == expected_confirmation
                if expected_confirmation is not None
                else True
            ),
        },
    }


def capability_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    single = [item for item in results if len(item["expected"]["intent_ids"]) == 1]
    multi = [item for item in results if len(item["expected"]["intent_ids"]) > 1]
    empty = [item for item in results if not item["expected"]["intent_ids"]]
    forced = [item for item in empty if item["model_selection"]["intent_ids"]]
    return {
        "strict_intent_set_accuracy": accuracy(
            sum(item["checks"]["intent_set_exact"] for item in results), len(results)
        ),
        "strict_ordered_intent_accuracy": accuracy(
            sum(item["checks"]["intent_order_exact"] for item in results), len(results)
        ),
        "single_intent_accuracy": accuracy(
            sum(item["checks"]["intent_order_exact"] for item in single), len(single)
        ),
        "multi_intent_set_exact": accuracy(
            sum(item["checks"]["intent_set_exact"] for item in multi), len(multi)
        ),
        "multi_intent_order_exact": accuracy(
            sum(item["checks"]["intent_order_exact"] for item in multi), len(multi)
        ),
        "empty_array_rejection": accuracy(
            sum(item["checks"]["empty_array_correct"] for item in empty), len(empty)
        ),
        "wrong_forced_classification_count": len(forced),
        "wrong_forced_classification_ids": [item["id"] for item in forced],
        "security_signal_accuracy": accuracy(
            sum(item["checks"]["security_correct"] for item in results), len(results)
        ),
        "validation_status_counts": dict(
            Counter(item["metrics"]["validation_status"] for item in results)
        ),
        "request_error_count": sum(
            item["metrics"]["request_error"] is not None for item in results
        ),
        "model_output_status_counts": dict(
            Counter(item["output"]["status"] for item in results)
        ),
        "failed_ordered_case_ids": [
            item["id"] for item in results if not item["checks"]["intent_order_exact"]
        ],
    }


def group_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    groups = sorted({str(item["group"]) for item in results})
    return {
        group: capability_summary([item for item in results if item["group"] == group])
        for group in groups
    }


def baseline_selection_summary(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    normalized: list[dict[str, Any]] = []
    for item in case_results:
        expected = list(item["expected"]["intent_ids"])
        observed = [value["intent_id"] for value in item["output"]["sub_intents"]]
        normalized.append(
            {
                "id": item["id"],
                "expected": {"intent_ids": expected},
                "model_selection": {"intent_ids": observed},
                "checks": {
                    "intent_set_exact": same_set_without_duplicates(observed, expected),
                    "intent_order_exact": observed == expected,
                    "empty_array_correct": not expected and not observed,
                    "security_correct": item["checks"]["security_correct"],
                },
                "metrics": item["metrics"],
                "output": item["output"],
            }
        )
    return capability_summary(normalized)


def serializable_run(run: JudgeRun) -> dict[str, Any]:
    return {
        "output": run.output,
        "model_selection": run.model_selection,
        "metrics": run.metrics,
        "raw_model_output": run.raw_model_output,
        "validation_errors": list(run.validation_errors),
        "prompt": run.prompt,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="3B 极简候选多选能力与延迟对照")
    parser.add_argument("--config", type=Path, default=BASE_DIR / "config.yaml")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--hot-runs", type=int, default=50)
    args = parser.parse_args()
    if args.hot_runs < 50:
        raise ValueError("hot-runs must be at least 50")
    experiment_started = perf_counter()
    started_at = datetime.now().astimezone().isoformat()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with MinimalCandidateJudge(args.config.resolve()) as judge:
        cases_path = judge._resolve_path(str(judge.config["paths"]["acceptance_cases"]))
        case_groups = yaml.safe_load(cases_path.read_text(encoding="utf-8"))
        all_cases = [
            (str(group), case)
            for group, cases in case_groups.items()
            for case in cases
        ]
        baseline_summary_path = judge._resolve_path(
            str(judge.config["paths"]["baseline_summary"])
        )
        baseline_cases_path = judge._resolve_path(
            str(judge.config["paths"]["baseline_case_results"])
        )
        baseline_report = load_json(baseline_summary_path)
        baseline_cases = load_json(baseline_cases_path)

        judge.unload_model()
        resident_before = judge.resident_models()
        cold_outer_started = perf_counter()
        cold_run = judge.judge(str(case_groups["fixed"][0]["text"]))
        cold_outer_wall_ms = round((perf_counter() - cold_outer_started) * 1000, 3)
        resident_after_cold = judge.resident_models()
        warmup_run = judge.judge(str(case_groups["fixed"][0]["text"]))

        results: list[dict[str, Any]] = []
        for index, (group, case) in enumerate(all_cases, start=1):
            run = judge.judge(str(case["text"]))
            results.append(assess_case(group, case, run))
            print(
                f"suite {index}/{len(all_cases)} {case['id']} {run.model_selection['intent_ids']}",
                flush=True,
            )

        hot_metrics: list[dict[str, Any]] = []
        hot_outputs: list[dict[str, Any]] = []
        latency_cases = [case for _, case in all_cases]
        for index in range(args.hot_runs):
            case = latency_cases[index % len(latency_cases)]
            run = judge.judge(str(case["text"]))
            hot_metrics.append(run.metrics)
            hot_outputs.append(
                {
                    "run": index + 1,
                    "case_id": case["id"],
                    "input": case["text"],
                    "intent_ids": actual_ids(run),
                    "metrics": run.metrics,
                }
            )
            if (index + 1) % 10 == 0:
                print(f"latency {index + 1}/{args.hot_runs}", flush=True)
        resident_after = judge.resident_models()

    capability = capability_summary(results)
    latency_keys = [
        "first_stage_recall_ms",
        "ollama_request_wall_ms",
        "first_token_latency_ms",
        "model_output_duration_ms",
        "full_chain_wall_ms",
        "prompt_token_count",
        "generated_token_count",
    ]
    hot_latency = {key: metric_summary(hot_metrics, key) for key in latency_keys}
    baseline_normalized = baseline_selection_summary(baseline_cases)
    baseline_multi = float(
        baseline_report["suite"]["multi_intent_exact_match"]["rate"]
    )
    semantic_gate = {
        "single_intent_at_least_70pct": capability["single_intent_accuracy"]["rate"] >= 0.70,
        "multi_order_at_least_50pct": capability["multi_intent_order_exact"]["rate"] >= 0.50,
        "multi_order_improves_at_least_20_points": (
            capability["multi_intent_order_exact"]["rate"] - baseline_multi >= 0.20
        ),
        "empty_rejection_at_least_80pct": capability["empty_array_rejection"]["rate"] >= 0.80,
        "wrong_forced_classifications_at_most_1": (
            capability["wrong_forced_classification_count"] <= 1
        ),
    }
    semantic_gate["passed"] = all(semantic_gate.values())
    latency_gate = {
        "ollama_p95_le_2000ms": hot_latency["ollama_request_wall_ms"]["p95"] <= 2000,
        "full_chain_p95_le_2500ms": hot_latency["full_chain_wall_ms"]["p95"] <= 2500,
    }
    latency_gate["passed"] = all(latency_gate.values())
    death_gate = {
        "semantic": semantic_gate,
        "latency": latency_gate,
        "passed": semantic_gate["passed"] and latency_gate["passed"],
    }
    focus_results = [
        next(item for item in results if item["id"] == focus_id)
        for focus_id in FOCUS_IDS
    ]
    comparison = {
        "qwen2.5_1.5b_original": {
            "strict_complete_accuracy": baseline_report["suite"]["complete_accuracy"],
            "single_intent_accuracy": baseline_report["suite"]["single_intent_accuracy"],
            "multi_intent_exact_match": baseline_report["suite"]["multi_intent_exact_match"],
            "no_match_correct_rejection": baseline_report["suite"]["no_match_correct_rejection"],
            "wrong_forced_classification_count": baseline_report["suite"]["wrong_forced_classification_count"],
            "hot_latency": baseline_report["hot_latency"],
        },
        "qwen2.5_1.5b_selection_only_normalized": baseline_normalized,
        "qwen2.5_3b_minimal": {
            "capability": capability,
            "hot_latency": hot_latency,
        },
    }
    report = {
        "experiment": "intent_judge_3b_minimal",
        "started_at": started_at,
        "completed_at": datetime.now().astimezone().isoformat(),
        "experiment_wall_seconds": round(perf_counter() - experiment_started, 3),
        "model": "qwen2.5:3b-instruct-q4_0",
        "case_counts": {str(key): len(value) for key, value in case_groups.items()},
        "capability": capability,
        "group_capability": group_summary(results),
        "focus_results": focus_results,
        "cold_request": {
            "resident_before": resident_before,
            "resident_after": resident_after_cold,
            "outer_wall_ms": cold_outer_wall_ms,
            **serializable_run(cold_run),
        },
        "warmup_request": serializable_run(warmup_run),
        "hot_latency_runs": args.hot_runs,
        "hot_latency": hot_latency,
        "model_resident_after": resident_after,
        "comparison": comparison,
        "death_gate": death_gate,
    }
    write_json(output_dir / "summary.json", report)
    write_json(output_dir / "case-results.json", results)
    write_json(output_dir / "focus-results.json", focus_results)
    write_json(output_dir / "hot-latency-runs.json", hot_outputs)
    write_json(output_dir / "actual-prompt-and-schema.json", cold_run.prompt)
    (output_dir / "acceptance_cases.yaml").write_text(
        cases_path.read_text(encoding="utf-8"), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "capability": capability,
                "hot_latency": hot_latency,
                "death_gate": death_gate,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
