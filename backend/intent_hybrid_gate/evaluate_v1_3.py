from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parents[1]
EXPERIMENTS_DIR = BASE_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(EXPERIMENTS_DIR))

from evaluate import (  # noqa: E402
    CORE_IDS,
    dataset_summary,
    latency_summary,
    load_holdout_cases,
    load_original_cases,
    serialize_result,
)
from gate import HybridConfidenceGate  # noqa: E402
from intent_recall_v1.recaller import CandidateIntentRecaller  # noqa: E402


V13_RECALL_CONFIG = ROOT_DIR / "test-results" / "anchor-loo-v1_3" / "config_v1_3.yaml"
V13_ANCHOR = ROOT_DIR / "挂靠" / "intent_anchor_set_v1_3.yaml"
GATE_CONFIG = BASE_DIR / "gate_config.yaml"
MODEL_CONFIG = ROOT_DIR / "experiments" / "intent_judge_3b_minimal" / "config.yaml"
ORIGINAL_CASES = ROOT_DIR / "experiments" / "intent_judge_v1" / "acceptance_cases.yaml"
HOLDOUT_CASES = BASE_DIR / "new_holdout_cases.yaml"
OUTPUT_DIR = ROOT_DIR / "test-results" / "intent-hybrid-gate-v1_3" / "evaluation"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compact_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "automatic_accept": summary["automatic_accept"],
        "review_count": summary["review_count"],
        "no_match_count": summary["no_match_count"],
        "multi_intent_complete_match": summary["multi_intent_complete_match"],
        "asr_correct_review": summary["asr_correct_review"],
        "unrelated_wrong_auto_accept_count": summary["unrelated_wrong_auto_accept_count"],
        "insufficient_wrong_auto_accept_count": summary["insufficient_wrong_auto_accept_count"],
        "security_signal_accuracy": summary["security_signal_accuracy"],
        "gate_path_counts": summary["gate_path_counts"],
        "model_call_count": summary["model_call_count"],
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    frozen_paths = {
        "v1_3_anchor": V13_ANCHOR,
        "v1_3_recall_config": V13_RECALL_CONFIG,
        "gate_config": GATE_CONFIG,
        "model_config": MODEL_CONFIG,
        "original60_cases": ORIGINAL_CASES,
        "holdout39_cases": HOLDOUT_CASES,
    }
    hashes_before = {name: sha256(path) for name, path in frozen_paths.items()}
    started = perf_counter()
    original_cases = load_original_cases()
    holdout_cases = load_holdout_cases()
    if len(original_cases) != 60 or len(holdout_cases) != 39:
        raise RuntimeError(
            f"unexpected case counts: original={len(original_cases)}, holdout={len(holdout_cases)}"
        )
    core_cases = [next(case for case in original_cases if case["id"] == case_id) for case_id in CORE_IDS]

    with HybridConfidenceGate() as gate:
        gate_hash = gate.gate_config_sha256.upper()
        model_config_hash = sha256(gate.model_judge.config_path)
        original_first_stage = str(gate.recaller.anchor_path)
        v13_recaller = CandidateIntentRecaller(V13_RECALL_CONFIG)
        if v13_recaller.anchor_path.resolve() != V13_ANCHOR.resolve():
            raise RuntimeError("v1.3 recall configuration resolved to the wrong anchor file")
        if len(v13_recaller.anchors) != 1466:
            raise RuntimeError(f"expected 1466 v1.3 anchors, got {len(v13_recaller.anchors)}")
        gate.recaller = v13_recaller
        gate.model_judge.recaller = v13_recaller

        original_results: list[dict[str, Any]] = []
        for index, case in enumerate(original_cases, start=1):
            original_results.append(
                serialize_result("original60_v1_3", case, gate.run(str(case["text"])))
            )
            if index % 10 == 0:
                print(f"original60 {index}/{len(original_cases)}", flush=True)

        holdout_results: list[dict[str, Any]] = []
        for index, case in enumerate(holdout_cases, start=1):
            holdout_results.append(
                serialize_result("holdout39_v1_3", case, gate.run(str(case["text"])))
            )
            if index % 10 == 0 or index == len(holdout_cases):
                print(f"holdout39 {index}/{len(holdout_cases)}", flush=True)

        official_demo_results: list[dict[str, Any]] = []
        for index, case in enumerate(core_cases, start=1):
            official_demo_results.append(
                serialize_result("official_demo4_v1_3", case, gate.run(str(case["text"])))
            )
            print(f"official_demo {index}/{len(core_cases)}", flush=True)

        recaller_startup = v13_recaller.startup_diagnostics()
        prompt_system = str(gate.model_judge.config["prompt"]["system"])
        model_runtime = {
            "model": gate.model_judge.model,
            "endpoint": gate.model_judge.endpoint,
            "keep_alive": gate.model_judge.keep_alive,
            "options": gate.model_judge.options,
            "prompt_system": prompt_system,
            "prompt_system_sha256": hashlib.sha256(prompt_system.encode("utf-8")).hexdigest().upper(),
        }

    hashes_after = {name: sha256(path) for name, path in frozen_paths.items()}
    if hashes_after != hashes_before:
        raise RuntimeError("a frozen input changed during evaluation")
    if gate_hash != hashes_before["gate_config"]:
        raise RuntimeError("gate configuration hash differs from the frozen gate")
    if model_config_hash != hashes_before["model_config"]:
        raise RuntimeError("model configuration hash differs from the frozen model config")

    unique99_results = original_results + holdout_results
    all103_results = unique99_results + official_demo_results
    original_summary = dataset_summary(original_results)
    holdout_summary = dataset_summary(holdout_results)
    official_summary = dataset_summary(official_demo_results)
    unique99_summary = dataset_summary(unique99_results)
    all103_summary = dataset_summary(all103_results)
    summary = {
        "experiment": "intent_hybrid_gate_v1_3_frozen_rerun",
        "completed_at": datetime.now().astimezone().isoformat(),
        "evaluation_wall_seconds": round(perf_counter() - started, 3),
        "execution_counts": {
            "original60": len(original_results),
            "holdout39": len(holdout_results),
            "official_demo4_separate_rerun": len(official_demo_results),
            "total_chain_executions": len(all103_results),
        },
        "frozen_inputs": {
            "hashes_before": hashes_before,
            "hashes_after": hashes_after,
            "unchanged": hashes_before == hashes_after,
            "original_first_stage_anchor": original_first_stage,
            "replacement_first_stage_anchor": str(V13_ANCHOR.resolve()),
            "gate_config_hash_matches_calibration_freeze": gate_hash == hashes_before["gate_config"],
            "model_config_hash_unchanged": model_config_hash == hashes_before["model_config"],
        },
        "model_runtime": model_runtime,
        "recaller_startup": recaller_startup,
        "original60": original_summary,
        "holdout39": holdout_summary,
        "official_demo4": official_summary,
        "combined_unique99": unique99_summary,
        "combined_all103_executions": all103_summary,
        "latency_all103": latency_summary(all103_results),
        "official_demo_results": official_demo_results,
    }
    write_json(OUTPUT_DIR / "summary.json", summary)
    write_json(OUTPUT_DIR / "original60-results.json", original_results)
    write_json(OUTPUT_DIR / "holdout39-results.json", holdout_results)
    write_json(OUTPUT_DIR / "official-demo4-results.json", official_demo_results)
    write_json(OUTPUT_DIR / "all103-results.json", all103_results)
    (OUTPUT_DIR / "frozen-gate-config.yaml").write_text(
        GATE_CONFIG.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (OUTPUT_DIR / "frozen-model-config.yaml").write_text(
        MODEL_CONFIG.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (OUTPUT_DIR / "frozen-v1_3-recall-config.yaml").write_text(
        V13_RECALL_CONFIG.read_text(encoding="utf-8"), encoding="utf-8"
    )
    readme = [
        "# v1.3 第一阶段锚点完整语义链重跑",
        "",
        f"- 实际执行：60 + 39 + 4 = {len(all103_results)} 次。",
        f"- v1.3 锚点 SHA256：`{hashes_before['v1_3_anchor']}`。",
        f"- 门控配置 SHA256：`{hashes_before['gate_config']}`。",
        f"- 3B 配置 SHA256：`{hashes_before['model_config']}`。",
        f"- 模型：`{model_runtime['model']}`；keep_alive：`{model_runtime['keep_alive']}`。",
        "- 只替换第一阶段锚点与版本隔离缓存；提示词、模型、门控条件未修改。",
        "",
        "## 汇总",
        "",
        "```json",
        json.dumps(
            {
                "original60": compact_summary(original_summary),
                "holdout39": compact_summary(holdout_summary),
                "official_demo4": compact_summary(official_summary),
                "combined_unique99": compact_summary(unique99_summary),
            },
            ensure_ascii=False,
            indent=2,
        ),
        "```",
        "",
        "本目录是隔离实验产物，未接入正式后端。",
    ]
    (OUTPUT_DIR / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUTPUT_DIR),
                "execution_counts": summary["execution_counts"],
                "original60": compact_summary(original_summary),
                "holdout39": compact_summary(holdout_summary),
                "official_demo4": compact_summary(official_summary),
                "latency_all103": summary["latency_all103"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
