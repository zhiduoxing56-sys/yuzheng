"""Finalize exp001 diagnostics when no epoch passes frozen safety gates.

This command is report-only: it does not load a model or execute inference/training.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .labels import SCOPE_TO_ID, STRUCTURE_TO_ID
from .train_config import repository_root


EXPERIMENT_DIR = (
    repository_root() / "data" / "nlu" / "experiments" / "sys014-poc7-rbt3-exp001"
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    rows = [
        json.loads(line)
        for line in (EXPERIMENT_DIR / "metrics_by_epoch.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    ]
    if not rows or any(row["validation"]["SAFETY_GATES_PASS"] for row in rows):
        raise RuntimeError("This finalizer is only valid when exp001 has no eligible epoch")
    closest = min(
        rows,
        key=lambda row: (
            row["validation"]["safety"]["unsafe_false_accepts"],
            -row["validation"]["PRIMARY_QUALITY_SCORE"],
        ),
    )
    highest_quality = max(
        rows, key=lambda row: row["validation"]["PRIMARY_QUALITY_SCORE"]
    )
    validation = closest["validation"]
    blockers = [
        error
        for error in validation["error_cases"]
        if (
            (
                error["true"]["scope"] != SCOPE_TO_ID["IN_SCOPE_CONTROL"]
                or error["true"]["structure"] != STRUCTURE_TO_ID["SINGLE"]
            )
            and error["predicted"]["scope"] == SCOPE_TO_ID["IN_SCOPE_CONTROL"]
            and error["predicted"]["structure"] == STRUCTURE_TO_ID["SINGLE"]
        )
    ]
    logs = [
        json.loads(line)
        for line in (EXPERIMENT_DIR / "training_log.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line
    ]
    epochs = [entry for entry in logs if entry.get("event") == "EPOCH_COMPLETED"]
    gradient_values = [float(entry["gradient_norm_mean"]) for entry in epochs]
    last_manifest = read_json(
        EXPERIMENT_DIR / "checkpoints" / "last" / "checkpoint_manifest.json"
    )
    diagnosis = {
        "status": "NO_VALIDATION_CHECKPOINT_PASSED_FROZEN_SAFETY_GATES",
        "closest_safety_candidate_epoch": closest["epoch"],
        "closest_candidate_quality_score": validation["PRIMARY_QUALITY_SCORE"],
        "closest_candidate_raw_ufar": validation["safety"]["UNSAFE_FALSE_ACCEPT_RATE"],
        "blocking_gate": "AMBIGUOUS_FALSE_ACCEPT_RATE_MAX_0",
        "blocking_false_accept_count": validation["safety"]["per_category"]["AMBIGUOUS"][
            "unsafe_false_accepts"
        ],
        "blocking_category_total": validation["safety"]["per_category"]["AMBIGUOUS"][
            "total_should_abstain"
        ],
        "blocking_samples": [
            {"sample_id": item["sample_id"], "text": item["text"]} for item in blockers
        ],
        "pipeline_diagnosis": {
            "loss_masking": "PASS_STAGE4B_TESTS_AND_ALL_HEADS_LEARNED",
            "class_weights": "FROZEN_SQRT_INVERSE_FREQ_APPLIED; AMBIGUOUS validation support is only 9",
            "learning_rate": "HEALTHY_FINITE_DESCENT_AT_FIXED_2E-5",
            "head_initialization": "HEALTHY; intent/structure/slot/negation all rose far above random/collapse",
            "token_projection": "PASS_ZERO_FAILURES",
            "gradient": {
                "status": "FINITE",
                "epoch_mean_gradient_norm_min": min(gradient_values),
                "epoch_mean_gradient_norm_max": max(gradient_values),
            },
            "dataset_batching": "DETERMINISTIC_SHUFFLE_SEED_14031_BATCH_16",
        },
        "recommended_next_action": "STOP; human validation review before either limited RBT3 safety optimization or Stage 4C-B decision",
        "electra_training_started": False,
        "test_evaluation_executed": False,
        "safety_gold_evaluation_executed": False,
    }
    summary = read_json(EXPERIMENT_DIR / "training_summary.json")
    summary.update(
        {
            "CLOSEST_SAFETY_CANDIDATE_EPOCH": closest["epoch"],
            "HIGHEST_QUALITY_UNGATED_EPOCH": highest_quality["epoch"],
            "HIGHEST_QUALITY_UNGATED_SCORE": highest_quality["validation"][
                "PRIMARY_QUALITY_SCORE"
            ],
            "LAST_CHECKPOINT_SHA256": last_manifest["model_state_sha256"],
            "TRAINING_FAILURE_DIAGNOSIS": diagnosis,
        }
    )
    write_json(EXPERIMENT_DIR / "training_summary.json", summary)
    write_json(
        EXPERIMENT_DIR / "best_validation_metrics.json",
        {
            "status": "NO_ELIGIBLE_BEST_CHECKPOINT",
            "BEST_EPOCH": None,
            "reason": diagnosis["status"],
            "closest_safety_candidate_epoch": closest["epoch"],
            "closest_safety_candidate_metrics": {
                key: value
                for key, value in validation.items()
                if key not in {"error_cases", "confusion_matrices"}
            },
            "highest_quality_ungated_epoch": highest_quality["epoch"],
            "highest_quality_ungated_score": highest_quality["validation"][
                "PRIMARY_QUALITY_SCORE"
            ],
        },
    )
    evaluation_dir = EXPERIMENT_DIR / "evaluation" / "validation"
    write_json(
        evaluation_dir / "metrics.json",
        {
            "status": "DIAGNOSTIC_CLOSEST_TO_FROZEN_SAFETY_GATES_NOT_SELECTED",
            "epoch": closest["epoch"],
            **{
                key: value
                for key, value in validation.items()
                if key not in {"error_cases", "confusion_matrices"}
            },
        },
    )
    write_json(evaluation_dir / "confusion_matrix.json", validation["confusion_matrices"])
    error_path = evaluation_dir / "error_cases.jsonl"
    error_path.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in validation["error_cases"]),
        encoding="utf-8",
    )
    (EXPERIMENT_DIR / "checkpoints" / "best" / "NO_ELIGIBLE_CHECKPOINT.md").write_text(
        "# No eligible best checkpoint\n\n"
        "No epoch passed the frozen validation safety gates. No model state is stored in this directory. "
        "The epoch 10 state is retained only under `checkpoints/last/` for diagnosis.\n",
        encoding="utf-8",
    )
    metrics = validation
    (EXPERIMENT_DIR / "training_summary.md").write_text(
        f"""# SYS-014 RBT3 exp001 训练总结

## 训练事实

- CPU、batch=16、lr=2e-5、seed=14031；完成 10 epoch / 370 optimizer steps。
- mean epoch={summary['MEAN_EPOCH_SECONDS']:.3f}s；total training={summary['TOTAL_TRAINING_SECONDS']:.3f}s。
- train total loss：{summary['TRAIN_LOSS_INITIAL']:.6f} → {summary['TRAIN_LOSS_FINAL']:.6f}。
- 参数已更新、loss/gradient 全部 finite、无自动改数据或超参数。

## 最接近 safety gates 的 validation 候选（epoch {closest['epoch']}，未选为 best）

- quality score={metrics['PRIMARY_QUALITY_SCORE']:.6f}；validation loss={metrics['losses']['total_loss']:.6f}。
- Intent macro F1={metrics['intent']['macro_f1']:.6f}。
- Scope macro F1={metrics['scope']['macro_f1']:.6f}；UNKNOWN recall={metrics['scope']['per_class']['UNKNOWN_CONTROL']['recall']:.6f}。
- Structure macro F1={metrics['structure']['macro_f1']:.6f}；MULTI recall={metrics['structure']['per_class']['MULTI']['recall']:.6f}；AMBIGUOUS recall={metrics['structure']['per_class']['AMBIGUOUS']['recall']:.6f}。
- Slot overall F1={metrics['slot']['OVERALL']['f1']:.6f}；AREA={metrics['slot']['AREA']['f1']:.6f}；VALUE={metrics['slot']['VALUE']['f1']:.6f}；NEGATION={metrics['slot']['NEGATION']['f1']:.6f}。
- Sentence NEGATED F1={metrics['negation']['per_class']['NEGATED']['f1']:.6f}；recall={metrics['negation']['per_class']['NEGATED']['recall']:.6f}。
- RAW UFAR={metrics['safety']['UNSAFE_FALSE_ACCEPT_RATE']:.6f}；UNKNOWN/MULTI/NON_CONTROL false accept=0。

## 阻断结论

AMBIGUOUS false accept 为 1/9，阻断样本为 `SYS014-POC-0731: 速度那个再弄点`。因此严格保留：

- `BEST_EPOCH = NOT_AVAILABLE`
- `BEST_CHECKPOINT_SAVED = NO`
- `RBT3_BASELINE_TRAINING_PASS = NO`
- `READY_FOR_STAGE_4C_NEXT_DECISION = NO`
- `TEST_EVALUATION_EXECUTED = NO`
- `SAFETY_GOLD_EVALUATION_EXECUTED = NO`

完整诊断见 `training_summary.json`。没有训练 ELECTRA，也没有放宽 safety gates。
""",
        encoding="utf-8",
    )
    manifest = read_json(EXPERIMENT_DIR / "manifest.json")
    manifest.update(
        {
            "status": "COMPLETED_NO_ELIGIBLE_SAFETY_CHECKPOINT",
            "postmortem_finalized": True,
            "closest_safety_candidate_epoch": closest["epoch"],
            "best_checkpoint_saved": False,
            "last_checkpoint_sha256": last_manifest["model_state_sha256"],
            "training_failure_diagnosis": diagnosis,
        }
    )
    write_json(EXPERIMENT_DIR / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "POSTMORTEM": "FINALIZED",
                "closest_safety_candidate_epoch": closest["epoch"],
                "blocking_samples": diagnosis["blocking_samples"],
                "best_checkpoint_saved": False,
                "last_checkpoint_sha256": last_manifest["model_state_sha256"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
