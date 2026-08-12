from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class MultiIntentDecision:
    incomplete: bool
    resolved_sub_intents: tuple[str, ...]
    unresolved_clauses: tuple[str, ...]


class MultiIntentCompletenessGuard:
    def check(self, clause_results: list[dict[str, Any]]) -> MultiIntentDecision:
        resolved: list[str] = []
        unresolved: list[str] = []
        for result in clause_results:
            selected = list(result["accepted_intent_ids"])
            if result["reliable"] and len(selected) == 1:
                resolved.append(str(selected[0]))
            else:
                unresolved.append(str(result["clause"]))
        return MultiIntentDecision(
            incomplete=bool(unresolved) or len(resolved) != len(clause_results),
            resolved_sub_intents=tuple(resolved),
            unresolved_clauses=tuple(unresolved),
        )
