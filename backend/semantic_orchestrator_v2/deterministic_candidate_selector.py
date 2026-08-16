from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Any

from intent_hybrid_gate.gate import GateRun

from .action_direction_guard import ActionDirectionGuard
from .semantic_contract_guard import SemanticContractGuard


CHANNELS = ("semantic", "literal", "pinyin")


def _normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).strip().lower().split())


@dataclass(frozen=True, slots=True)
class DeterministicSelection:
    intent_id: str | None
    params: dict[str, Any]
    gate_path: str | None
    reason: str | None


class DeterministicCandidateSelector:
    """Accept only Registry-backed candidates justified by local recall and contracts."""

    def __init__(
        self,
        contract_guard: SemanticContractGuard,
        direction_guard: ActionDirectionGuard,
        strong_consensus: dict[str, Any],
    ) -> None:
        self.contract_guard = contract_guard
        self.direction_guard = direction_guard
        self.strong_consensus = strong_consensus

    @staticmethod
    def _exact_anchor_ids(clause: str, run: GateRun) -> set[str]:
        normalized = _normalize(clause)
        return {
            str(candidate["intent_id"])
            for candidate in run.evidence["recall_candidates"]
            if any(
                _normalize(str(anchor["text"])) == normalized
                for anchor in candidate["support_anchors"]
            )
        }

    def _viable(
        self, clause: str, intent_id: str, top8: list[str]
    ) -> tuple[bool, dict[str, Any]]:
        if self.direction_guard.has_leading_negated_action(clause):
            return False, {}
        contract = self.contract_guard.check(clause, intent_id)
        direction = self.direction_guard.check(clause, intent_id, top8)
        if contract.review_reasons or direction.conflict:
            return False, {}
        return True, dict(contract.params)

    @staticmethod
    def _dominates(left: dict[str, Any], right: dict[str, Any]) -> bool:
        """A contract consumer is unique only when every local channel prefers it."""

        return all(
            float(left["channels"][channel]["score"])
            > float(right["channels"][channel]["score"])
            for channel in CHANNELS
        )

    def _strong_consensus(self, row: dict[str, Any], evidence: dict[str, Any]) -> bool:
        channels = row["channels"]
        config = self.strong_consensus
        return (
            all(channels[channel]["rank"] == 1 for channel in CHANNELS)
            and float(channels["semantic"]["score"])
            >= float(config["min_semantic_score"])
            and float(channels["literal"]["score"])
            >= float(config["min_literal_score"])
            and float(channels["pinyin"]["score"])
            >= float(config["min_pinyin_score"])
            and float(evidence["channel_summary"]["semantic"]["first_second_gap"])
            >= float(config["min_semantic_first_second_gap"])
        )

    def select(
        self,
        clause: str,
        run: GateRun,
        *,
        eligible_candidate_ids: tuple[str, ...] | None = None,
        accept_unique_eligible_candidate: bool = False,
    ) -> DeterministicSelection:
        all_top8 = [str(intent_id) for intent_id in run.evidence["fused_top8"]]
        eligible = set(eligible_candidate_ids) if eligible_candidate_ids is not None else None
        top8 = [intent_id for intent_id in all_top8 if eligible is None or intent_id in eligible]
        rows = {str(row["intent_id"]): row for row in run.evidence["targets"]}
        exact_ids = self._exact_anchor_ids(clause, run)
        viable: dict[str, dict[str, Any]] = {}
        for intent_id in top8:
            if intent_id not in rows:
                continue
            accepted, params = self._viable(clause, intent_id, all_top8)
            if accepted:
                viable[intent_id] = params

        exact = [intent_id for intent_id in top8 if intent_id in exact_ids and intent_id in viable]
        if len(exact) == 1:
            intent_id = exact[0]
            return DeterministicSelection(
                intent_id, viable[intent_id], "EXACT_ANCHOR_ACCEPT", None
            )
        if len(exact) > 1:
            return DeterministicSelection(None, {}, None, "EXACT_ANCHOR_AMBIGUOUS")

        parameterized = [
            intent_id for intent_id in top8
            if intent_id in viable and viable[intent_id]
        ]
        if parameterized:
            winners = [
                intent_id
                for intent_id in parameterized
                if all(
                    intent_id == other or self._dominates(rows[intent_id], rows[other])
                    for other in parameterized
                )
            ]
            if len(winners) == 1:
                intent_id = winners[0]
                return DeterministicSelection(
                    intent_id, viable[intent_id], "PARAMETER_CONTRACT_ACCEPT", None
                )
            return DeterministicSelection(None, {}, None, "PARAMETER_CONTRACT_AMBIGUOUS")

        if accept_unique_eligible_candidate and len(viable) == 1:
            intent_id = next(iter(viable))
            return DeterministicSelection(
                intent_id,
                viable[intent_id],
                "OBJECT_FAMILY_CONSTRAINT_ACCEPT",
                None,
            )

        if top8:
            intent_id = top8[0]
            if intent_id in viable and self._strong_consensus(rows[intent_id], run.evidence):
                return DeterministicSelection(
                    intent_id, viable[intent_id], "DETERMINISTIC_CONSENSUS_ACCEPT", None
                )
        return DeterministicSelection(None, {}, None, "DETERMINISTIC_EVIDENCE_INSUFFICIENT")
