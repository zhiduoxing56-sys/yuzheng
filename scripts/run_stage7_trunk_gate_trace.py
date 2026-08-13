from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from intent_hybrid_gate.calibrate_gate import target_rows  # noqa: E402
from intent_hybrid_gate.gate import HybridConfidenceGate  # noqa: E402
from semantic_orchestrator_v2_1.orchestrator import SemanticOrchestratorV2_1  # noqa: E402


TARGETS = ("TRUNK_CLOSE", "TRUNK_LOCK", "TRUNK_UNLOCK", "TRUNK_OPEN")


def _channel_projection(row: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for channel in ("semantic", "literal", "pinyin"):
        value = row["channels"][channel]
        result[channel] = {
            "rank": value["rank"],
            "score": value["score"],
            "anchor": value.get("anchor"),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=("before", "after"))
    args = parser.parse_args()
    text = "把后备箱上锁"
    with HybridConfidenceGate() as gate:
        run = gate.run(text)
        sample = {"input": text, "diagnostic": run.evidence}
        rows = target_rows(sample)
        config = gate.config["model_consistency"]
        selected = list(run.model_intent_ids)
        top1 = str(run.evidence["fused_top8"][0])
        max_rank = int(config["strong_channel_rank_max"])
        min_count = int(config["min_strong_channel_count_per_selected_target"])
        selected_checks = []
        for target in selected:
            row = rows.get(target)
            strong_count = (
                sum(
                    row["channels"][channel]["rank"] <= max_rank
                    for channel in ("semantic", "literal", "pinyin")
                )
                if row is not None
                else 0
            )
            selected_checks.append(
                {
                    "intent_id": target,
                    "in_fused_top8": row is not None,
                    "fused_top8_rank": row["fused_top8_rank"] if row else None,
                    "fused_top1_selected": target == top1,
                    "selected_target_strong_channel_count": strong_count,
                    "strong_channel_rank_max": max_rank,
                    "min_strong_channel_count_per_selected_target": min_count,
                    "strong_channel_requirement_passed": strong_count >= min_count,
                }
            )
        failures = []
        if not selected:
            failures.append("MODEL_SELECTED_EMPTY")
        if config.get("require_fused_top1_selected") and top1 not in selected:
            failures.append("FUSED_TOP1_NOT_SELECTED")
        failures.extend(
            f"SELECTED_TARGET_NOT_IN_FUSED_TOP8:{item['intent_id']}"
            for item in selected_checks
            if not item["in_fused_top8"]
        )
        failures.extend(
            f"SELECTED_TARGET_STRONG_CHANNEL_SUPPORT_INSUFFICIENT:{item['intent_id']}"
            for item in selected_checks
            if not item["strong_channel_requirement_passed"]
        )
        trace = {
            "phase": args.phase,
            "input": text,
            "gate_config_sha256": hashlib.sha256(gate.config_path.read_bytes()).hexdigest(),
            "fused_top8": run.evidence["fused_top8"],
            "channel_summary": run.evidence["channel_summary"],
            "targets": {
                target: {
                    "fused_top8_rank": rows[target]["fused_top8_rank"],
                    "channels": _channel_projection(rows[target]),
                    "channel_support_count": sum(
                        rows[target]["channels"][channel]["rank"] <= max_rank
                        for channel in ("semantic", "literal", "pinyin")
                    ),
                }
                for target in TARGETS
                if target in rows
            },
            "raw_model_output": run.raw_model_output,
            "model_intent_ids": selected,
            "validation_errors": list(run.validation_errors),
            "model_consistency_checks": {
                "require_fused_top1_selected_check": config.get(
                    "require_fused_top1_selected", "REMOVED"
                ),
                "fused_top1": top1,
                "selected_targets": selected_checks,
                "failure_reasons": failures,
                "final_model_consistent": not failures,
            },
            "gate_path": run.gate_path,
            "guard_triggers": [],
            "semantic_status": run.output["semantic_status"],
            "review_reasons": ["MODEL_REVIEW"] if run.gate_path == "MODEL_REVIEW" else [],
            "final_intent": (
                run.output["sub_intents"][0]["intent_id"]
                if run.output["sub_intents"]
                else None
            ),
        }
    if args.phase == "after":
        orchestrator = SemanticOrchestratorV2_1()
        semantic_run = orchestrator.run(text)
        trace["guard_triggers"] = semantic_run.debug.get("guard_triggers", [])
        trace["guard_details"] = semantic_run.debug.get("clause_results", [])[0].get(
            "guard_details", {}
        )
        trace["semantic_status"] = semantic_run.output["status"]
        trace["review_reasons"] = semantic_run.output.get("reasons", [])
        trace["final_intent"] = (
            semantic_run.output["sub_intents"][0]["intent_id"]
            if semantic_run.output.get("sub_intents")
            else None
        )
        trace["guard_observation_source"] = "live SemanticOrchestratorV2_1.run"
        golden_path = (
            ROOT
            / "data"
            / "nlu"
            / "spec"
            / "audits"
            / "stage7_real_behavior_golden_matrix_v2.json"
        )
        if golden_path.exists():
            golden = json.loads(golden_path.read_text(encoding="utf-8"))
            pipeline_case = next(
                item
                for item in golden["cases"]
                if item["id"] == "TRUNK_LOCK_MODEL_OVERRIDE"
            )
            for field in (
                "evidence_demand_generated",
                "evidence_required_types",
                "safety_gate_invoked",
                "safety_gate_hit_rules",
                "decision",
                "capability_supported",
                "authorization_token",
                "vehicle_state_before",
                "vehicle_state_after",
                "vehicle_state_changed",
                "workflow_chain_valid",
            ):
                trace[field] = pipeline_case[field]
    destination = (
        ROOT
        / "data"
        / "nlu"
        / "spec"
        / "audits"
        / f"stage7_trunk_gate_trace_{args.phase}.json"
    )
    destination.write_text(
        json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(trace, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
