from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from intent_hybrid_gate.gate import GateRun


@dataclass(frozen=True, slots=True)
class CandidateConsistencyDecision:
    conflict: bool
    reasons: tuple[str, ...]


class CandidateConsistencyGuard:
    """Reuse frozen candidate membership and existing model-consistency ranks only."""

    def __init__(self, frozen_model_consistency: dict[str, Any]) -> None:
        self.config = frozen_model_consistency

    def check(self, run: GateRun, selected_ids: list[str]) -> CandidateConsistencyDecision:
        reasons: list[str] = []
        fused = [str(value) for value in run.evidence["fused_top8"]]
        rows = {str(row["target"]): row for row in run.evidence["targets"]}
        for intent_id in selected_ids:
            if intent_id not in fused or intent_id not in rows:
                reasons.append(f"NOT_IN_STAGE1_TOP8:{intent_id}")
        if run.gate_path == "MODEL_ACCEPT" and selected_ids:
            if self.config["require_fused_top1_selected"] and fused[0] not in selected_ids:
                reasons.append("FUSED_TOP1_NOT_SELECTED")
            max_rank = int(self.config["strong_channel_rank_max"])
            min_count = int(self.config["min_strong_channel_count_per_selected_target"])
            for intent_id in selected_ids:
                if intent_id not in rows:
                    continue
                count = sum(
                    int(rows[intent_id]["channels"][channel]["rank"]) <= max_rank
                    for channel in ("semantic", "literal", "pinyin")
                )
                if count < min_count:
                    reasons.append(f"INSUFFICIENT_STRONG_CHANNELS:{intent_id}")
        if run.gate_path == "DIRECT_ACCEPT" and selected_ids and selected_ids[0] != fused[0]:
            reasons.append("DIRECT_RESULT_NOT_FUSED_TOP1")
        return CandidateConsistencyDecision(bool(reasons), tuple(reasons))
