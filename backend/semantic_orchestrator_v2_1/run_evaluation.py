from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
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
)
from semantic_orchestrator_v2.run_evaluation import (  # noqa: E402
    actual_ids,
    dataset_summary,
    official_demo_correct,
    serialize,
    sha256,
    write_json,
)
from semantic_orchestrator_v2_1.orchestrator import SemanticOrchestratorV2_1  # noqa: E402


OUTPUT_DIR = ROOT_DIR / "test-results" / "semantic-orchestrator-v2_1"
ORIGINAL_CASES = ROOT_DIR / "experiments" / "intent_judge_v1" / "acceptance_cases.yaml"
HOLDOUT_CASES = HYBRID_DIR / "new_holdout_cases.yaml"
GUARD_NAMES = (
    "ACTION_DIRECTION_CONFLICT",
    "MULTI_INTENT_INCOMPLETE",
    "INSUFFICIENT_SEMANTIC_INFORMATION",
    "CANDIDATE_CONFLICT",
    "OBJECT_FAMILY_CORRECTION",
    "OBJECT_FAMILY_CONFLICT",
    "SECURITY_SIGNAL_FORCED",
    "SECURITY_SIGNAL_WEAK",
)


def direction_wrong_ok(item: dict[str, Any]) -> bool:
    if item["output"]["status"] != "OK":
        return False
    return any(
        row["conflict"]
        for clause in item["debug"]["clause_results"]
        for row in clause["guard_details"].get("action_direction", [])
    )


def object_family_wrong_ok(item: dict[str, Any]) -> bool:
    if item["output"]["status"] != "OK":
        return False
    return any(
        detail.get("conflict", False)
        for clause in item["debug"]["clause_results"]
        if (detail := clause["guard_details"].get("object_family"))
    )


def main() -> None:
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
        raise RuntimeError("V2.1 output directory is not empty; refusing to overwrite a frozen run")
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
    all_case_ids = [str(case["id"]) for case in [*original_cases, *holdout_cases]]
    if len(set(all_case_ids)) != 99:
        raise RuntimeError("the frozen evaluation does not contain 99 unique case IDs")
    demo_cases = [next(case for case in original_cases if case["id"] == case_id) for case_id in CORE_IDS]

    started = perf_counter()
    with SemanticOrchestratorV2_1() as orchestrator:
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
            sum(
                guard in [*clause["guard_triggers"], *clause.get("audit_triggers", [])]
                for clause in item["debug"]["clause_results"]
            )
            if guard not in {
                "MULTI_INTENT_INCOMPLETE",
                "SECURITY_SIGNAL_FORCED",
                "SECURITY_SIGNAL_WEAK",
            }
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
    direction_wrong_count = sum(direction_wrong_ok(item) for item in all99)
    object_wrong_count = sum(object_family_wrong_ok(item) for item in all99)
    demo_correct = sum(official_demo_correct(item) for item in demo_results)
    targets = {
        "automatic_ok_error_count": all99_summary["automatic_accept"]["error_count"],
        "obvious_action_direction_wrong_ok_count": direction_wrong_count,
        "obvious_object_family_wrong_ok_count": object_wrong_count,
        "insufficient_wrong_ok_count": all99_summary["insufficient_wrong_auto_accept_count"],
        "unrelated_wrong_ok_count": all99_summary["unrelated_wrong_auto_accept_count"],
        "security_signal_correct": all99_summary["security_signal_accuracy"]["correct"],
        "security_signal_total": all99_summary["security_signal_accuracy"]["total"],
        "multi_intent_complete_correct": all99_summary["multi_intent_complete_match"]["correct"],
        "multi_intent_complete_total": all99_summary["multi_intent_complete_match"]["total"],
        "official_demo_correct": demo_correct,
        "official_demo_total": 4,
    }
    freeze_candidate = (
        targets["automatic_ok_error_count"] == 0
        and targets["obvious_action_direction_wrong_ok_count"] == 0
        and targets["obvious_object_family_wrong_ok_count"] == 0
        and targets["insufficient_wrong_ok_count"] == 0
        and targets["unrelated_wrong_ok_count"] == 0
        and targets["security_signal_correct"] == 99
        and targets["multi_intent_complete_correct"] >= 17
        and targets["official_demo_correct"] == 4
    )
    summary = {
        "experiment": "semantic-orchestrator-v2_1",
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
        "target_checks": targets,
        "freeze_candidate": freeze_candidate,
        "official_demo4": {
            "correct": demo_correct,
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
        "# SemanticOrchestratorV2.1 冻结评估结果",
        "",
        f"- 唯一冻结样本：99；正式演示额外重复：4；完整链执行：103。",
        f"- v1.3 锚点 SHA256：`{hashes_before['v1_3_anchor']}`。",
        f"- 门控配置 SHA256：`{hashes_before['gate_config']}`。",
        f"- 3B 配置 SHA256：`{hashes_before['model_config']}`。",
        f"- 冻结候选：`{str(freeze_candidate).lower()}`。",
        "- 全量运行后未继续调整规则。",
        "",
        "## 目标检查",
        "",
        "```json",
        json.dumps(targets, ensure_ascii=False, indent=2),
        "```",
        "",
        "## 99 条汇总",
        "",
        "```json",
        json.dumps(all99_summary, ensure_ascii=False, indent=2),
        "```",
        "",
        "本目录仅为独立实验产物，未接正式后端。",
    ]
    (OUTPUT_DIR / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT_DIR),
                "all99": all99_summary,
                "target_checks": targets,
                "guard_trigger_sample_counts": guard_sample_counts,
                "freeze_candidate": freeze_candidate,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
