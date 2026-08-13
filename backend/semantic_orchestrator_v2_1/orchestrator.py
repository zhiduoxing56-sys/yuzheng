from __future__ import annotations

from typing import Any

import yaml

from semantic_orchestrator_v2.orchestrator import (
    INTENT_CARDS,
    OrchestratorRun,
    SemanticOrchestratorV2,
)

from .object_family_guard import ObjectFamilyGuard
from .security_claim_guard import SecurityClaimGuard


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def _decision_dict(decision: Any) -> dict[str, Any]:
    return {
        "explicit_families": list(decision.explicit_families),
        "selected_families": list(decision.selected_families),
        "requested_action_families": list(decision.requested_action_families),
        "matching_candidates": list(decision.matching_candidates),
        "final_intent_ids": list(decision.final_intent_ids),
        "corrected_from": list(decision.corrected_from),
        "corrected_to": decision.corrected_to,
        "correction": decision.correction,
        "conflict": decision.conflict,
    }


class SemanticOrchestratorV2_1(SemanticOrchestratorV2):
    """V2 plus two isolated, generic final guards."""

    def __init__(self) -> None:
        super().__init__()
        cards_root = yaml.safe_load(INTENT_CARDS.read_text(encoding="utf-8"))
        cards = cards_root.get("intents", {})
        self.object_guard = ObjectFamilyGuard(cards, self.direction_guard)
        self.security_guard = SecurityClaimGuard()

    def _run_clause(self, clause: str) -> dict[str, Any]:
        result = super()._run_clause(clause)
        result["audit_triggers"] = []
        if result["base_status"] != "OK" or not result["accepted_intent_ids"]:
            return result

        decision = self.object_guard.check(
            clause,
            list(result["accepted_intent_ids"]),
            list(result["stage1_top8"]),
        )
        if not decision.explicit_families:
            return result

        result["guard_details"]["object_family"] = _decision_dict(decision)
        if decision.correction:
            result["accepted_intent_ids"] = list(decision.final_intent_ids)
            result["resolved_params"] = {
                intent_id: dict(
                    self.semantic_contract_guard.check(clause, intent_id).params
                )
                for intent_id in decision.final_intent_ids
            }
            result["audit_triggers"].append("OBJECT_FAMILY_CORRECTION")
        elif decision.conflict:
            result["guard_triggers"] = _unique(
                [*result["guard_triggers"], "OBJECT_FAMILY_CONFLICT"]
            )
            result["reliable"] = False
        return result

    def run(self, text: str) -> OrchestratorRun:
        run = super().run(text)
        debug = dict(run.debug)
        audit_triggers = _unique(
            [
                trigger
                for clause in debug["clause_results"]
                for trigger in clause.get("audit_triggers", [])
            ]
        )
        debug["guard_triggers"] = _unique(
            [*debug["guard_triggers"], *audit_triggers]
        )
        return OrchestratorRun(output=run.output, metrics=run.metrics, debug=debug)
