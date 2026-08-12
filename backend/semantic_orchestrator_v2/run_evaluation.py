from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[1]
HYBRID_DIR = ROOT_DIR / "experiments" / "intent_hybrid_gate"
if str(BASE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(BASE_DIR.parent))
if str(HYBRID_DIR) not in sys.path:
    sys.path.insert(0, str(HYBRID_DIR))

from evaluate import CORE_IDS, load_holdout_cases, load_original_cases  # noqa: E402
from semantic_orchestrator_v2.orchestrator import (  # noqa: E402
    GATE_CONFIG,
    INTENT_CARDS,
    MODEL_CONFIG,
    V13_ANCHOR,
    V13_RECALL_CONFIG,
    SemanticOrchestratorV2,
)


OUTPUT_DIR = ROOT_DIR / "test-results" / "semantic-orchestrator-v2"
ORIGINAL_CASES = ROOT_DIR / "experiments" / "intent_judge_v1" / "acceptance_cases.yaml"
HOLDOUT_CASES = HYBRID_DIR / "new_holdout_cases.yaml"
GUARD_NAMES = (
    "ACTION_DIRECTION_CONFLICT",
    "MULTI_INTENT_INCOMPLETE",
    "INSUFFICIENT_SEMANTIC_INFORMATION",
    "CANDIDATE_CONFLICT",
    "SECURITY_SIGNAL_FORCED",
    "SECURITY_SIGNAL_WEAK",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def actual_ids(output: dict[str, Any]) -> list[str]:
    return [str(item["intent_id"]) for item in output["sub_intents"]]


def serialize(dataset: str, case: dict[str, Any], run: Any) -> dict[str, Any]:
    expected = [str(value) for value in case["expected_intents"]]
    actual = actual_ids(run.output)
    status = str(run.output["status"])
    security_correct = bool(run.output["security_signals"]) == bool(case.get("expect_security", False))
    exact_order = actual == expected
    same_intent_multiset = Counter(actual) == Counter(expected) and len(actual) == len(expected)
    accepted = status == "OK"
    asr_review_correct = (
        status == "REVIEW" and run.output.get("suggested_target") in expected
        if case["category"] == "asr"
        else None
    )
    return {
        "dataset": dataset,
        "id": case["id"],
        "category": case["category"],
        "input": case["text"],
        "expected_intents": expected,
        "expect_security": bool(case.get("expect_security", False)),
        "output": run.output,
        "metrics": run.metrics,
        "debug": run.debug,
        "checks": {
            "automatic_accept": accepted,
            "automatic_accept_correct": accepted and exact_order,
            "intent_multiset_exact": same_intent_multiset,
            "intent_order_exact": exact_order,
            "security_correct": security_correct,
            "asr_review_correct": asr_review_correct,
        },
    }


def rate(correct: int, total: int) -> dict[str, Any]:
    return {"correct": correct, "total": total, "rate": round(correct / total, 6) if total else None}


def dataset_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = [item for item in results if item["checks"]["automatic_accept"]]
    accepted_correct = [item for item in accepted if item["checks"]["automatic_accept_correct"]]
    multi = [item for item in results if item["category"] == "multi_intent"]
    insufficient = [item for item in results if item["category"] == "insufficient"]
    unrelated = [item for item in results if item["category"] == "unrelated"]
    return {
        "total": len(results),
        "ok_count": sum(item["output"]["status"] == "OK" for item in results),
        "review_count": sum(item["output"]["status"] == "REVIEW" for item in results),
        "no_match_count": sum(item["output"]["status"] == "NO_MATCH" for item in results),
        "automatic_accept": {
            "count": len(accepted),
            "coverage": round(len(accepted) / len(results), 6) if results else None,
            "correct": len(accepted_correct),
            "error_count": len(accepted) - len(accepted_correct),
            "precision": round(len(accepted_correct) / len(accepted), 6) if accepted else None,
            "error_ids": [item["id"] for item in accepted if not item["checks"]["automatic_accept_correct"]],
        },
        "multi_intent_complete_match": rate(
            sum(item["output"]["status"] == "OK" and item["checks"]["intent_multiset_exact"] for item in multi),
            len(multi),
        ),
        "multi_intent_order_correct": rate(
            sum(item["output"]["status"] == "OK" and item["checks"]["intent_order_exact"] for item in multi),
            len(multi),
        ),
        "insufficient_wrong_auto_accept_count": sum(item["output"]["status"] == "OK" for item in insufficient),
        "unrelated_wrong_auto_accept_count": sum(item["output"]["status"] == "OK" for item in unrelated),
        "security_signal_accuracy": rate(sum(item["checks"]["security_correct"] for item in results), len(results)),
        "model_call_count": sum(int(item["metrics"]["model_call_count"]) for item in results),
        "mean_clause_count": round(mean(float(item["metrics"]["clause_count"]) for item in results), 3),
        "mean_wall_ms": round(mean(float(item["metrics"]["full_orchestrator_wall_ms"]) for item in results), 3),
    }


def official_demo_correct(result: dict[str, Any]) -> bool:
    if result["id"] == "fixed_04_drive_mode_homophone":
        return (
            result["output"]["status"] == "REVIEW"
            and result["output"]["suggested_target"] == "驾驶模式"
            and result["output"]["suggested_text"] == "打开运动模式"
            and result["checks"]["security_correct"]
        )
    return (
        result["output"]["status"] == "OK"
        and result["checks"]["intent_order_exact"]
        and result["checks"]["security_correct"]
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frozen_paths = {
        "v1_3_anchor": V13_ANCHOR,
        "v1_3_recall_config": V13_RECALL_CONFIG,
        "gate_config": GATE_CONFIG,
        "model_config": MODEL_CONFIG,
        "intent_cards": INTENT_CARDS,
        "original60_cases": ORIGINAL_CASES,
        "holdout39_cases": HOLDOUT_CASES,
    }
    hashes_before = {name: sha256(path) for name, path in frozen_paths.items()}
    original_cases = load_original_cases()
    holdout_cases = load_holdout_cases()
    if len(original_cases) != 60 or len(holdout_cases) != 39:
        raise RuntimeError("expected exactly 60 original and 39 holdout cases")
    demo_cases = [next(case for case in original_cases if case["id"] == case_id) for case_id in CORE_IDS]
    started = perf_counter()
    with SemanticOrchestratorV2() as orchestrator:
        original_results: list[dict[str, Any]] = []
        for index, case in enumerate(original_cases, start=1):
            original_results.append(serialize("original60", case, orchestrator.run(str(case["text"]))))
            if index % 10 == 0:
                print(f"original60 {index}/{len(original_cases)}", flush=True)
        holdout_results: list[dict[str, Any]] = []
        for index, case in enumerate(holdout_cases, start=1):
            holdout_results.append(serialize("holdout39", case, orchestrator.run(str(case["text"]))))
            if index % 10 == 0 or index == len(holdout_cases):
                print(f"holdout39 {index}/{len(holdout_cases)}", flush=True)
        demo_results: list[dict[str, Any]] = []
        for index, case in enumerate(demo_cases, start=1):
            demo_results.append(serialize("official_demo4", case, orchestrator.run(str(case["text"]))))
            print(f"official_demo4 {index}/{len(demo_cases)}", flush=True)
        component_hashes_after = orchestrator.frozen_hashes_after()
        startup = orchestrator.recaller.startup_diagnostics()

    expected_components = {
        key: value for key, value in hashes_before.items() if key in component_hashes_after
    }
    if component_hashes_after != expected_components:
        raise RuntimeError("a frozen semantic component changed during evaluation")
    hashes_after = {name: sha256(path) for name, path in frozen_paths.items()}
    if hashes_after != hashes_before:
        raise RuntimeError("a frozen input or test set changed during evaluation")
    all99 = original_results + holdout_results
    all103 = all99 + demo_results
    guard_sample_counts = {
        guard: sum(guard in item["debug"]["guard_triggers"] for item in all99)
        for guard in GUARD_NAMES
    }
    guard_event_counts = {
        guard: sum(
            sum(guard in clause["guard_triggers"] for clause in item["debug"]["clause_results"])
            if guard not in {"MULTI_INTENT_INCOMPLETE", "SECURITY_SIGNAL_FORCED", "SECURITY_SIGNAL_WEAK"}
            else int(guard in item["debug"]["guard_triggers"])
            for item in all99
        )
        for guard in GUARD_NAMES
    }
    validation_errors = [
        error
        for item in all103
        for clause in item["debug"]["clause_results"]
        for error in clause["validation_errors"]
    ]
    request_errors = [
        clause["metrics"].get("request_error")
        for item in all103
        for clause in item["debug"]["clause_results"]
        if clause["metrics"].get("request_error")
    ]
    if validation_errors or request_errors:
        raise RuntimeError(f"model or schema failures occurred: {validation_errors} {request_errors}")

    all99_summary = dataset_summary(all99)
    summary = {
        "experiment": "semantic-orchestrator-v2",
        "completed_at": datetime.now().astimezone().isoformat(),
        "evaluation_wall_seconds": round(perf_counter() - started, 3),
        "unique_sample_count": 99,
        "extra_official_demo_execution_count": 4,
        "total_chain_execution_count": 103,
        "frozen_hashes_before": hashes_before,
        "frozen_hashes_after": hashes_after,
        "frozen_unchanged": hashes_before == hashes_after,
        "recaller_startup": startup,
        "all99": all99_summary,
        "original60": dataset_summary(original_results),
        "holdout39": dataset_summary(holdout_results),
        "guard_trigger_sample_counts": guard_sample_counts,
        "guard_trigger_event_counts": guard_event_counts,
        "official_demo4": {
            "correct": sum(official_demo_correct(item) for item in demo_results),
            "total": 4,
            "results": demo_results,
        },
        "validation_error_count": len(validation_errors),
        "request_error_count": len(request_errors),
    }
    write_json(OUTPUT_DIR / "summary.json", summary)
    write_json(OUTPUT_DIR / "all99-results.json", all99)
    write_json(OUTPUT_DIR / "original60-results.json", original_results)
    write_json(OUTPUT_DIR / "holdout39-results.json", holdout_results)
    write_json(OUTPUT_DIR / "official-demo4-results.json", demo_results)
    write_json(
        OUTPUT_DIR / "guard-trigger-stats.json",
        {"sample_counts": guard_sample_counts, "event_counts": guard_event_counts},
    )
    readme = [
        "# SemanticOrchestratorV2 评估结果",
        "",
        f"- 唯一样本：99；四个正式演示额外重跑；完整链执行：103。",
        f"- v1.3锚点SHA256：`{hashes_before['v1_3_anchor']}`。",
        f"- 门控配置SHA256：`{hashes_before['gate_config']}`。",
        f"- 3B配置SHA256：`{hashes_before['model_config']}`。",
        "- 全量运行后未继续调整规则。",
        "",
        "## 99条汇总",
        "",
        "```json",
        json.dumps(all99_summary, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Guard触发",
        "",
        "```json",
        json.dumps(guard_sample_counts, ensure_ascii=False, indent=2),
        "```",
        "",
        "本目录仅为独立实验产物，未接正式后端。",
    ]
    (OUTPUT_DIR / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT_DIR),
        "all99": all99_summary,
        "guard_trigger_sample_counts": guard_sample_counts,
        "official_demo4_correct": summary["official_demo4"]["correct"],
    }, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
