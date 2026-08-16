from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ResolvedIntentOccurrence:
    clause_index: int
    intent_id: str


@dataclass(frozen=True, slots=True)
class MultiIntentDecision:
    incomplete: bool
    resolved_occurrences: tuple[ResolvedIntentOccurrence, ...]
    unresolved_clauses: tuple[str, ...]


class MultiIntentCompletenessGuard:
    def check(self, clause_results: list[dict[str, Any]]) -> MultiIntentDecision:
        resolved: list[ResolvedIntentOccurrence] = []
        unresolved: list[str] = []
        for ordinal, result in enumerate(clause_results):
            clause_index = int(result.get("clause_index", ordinal))
            selected = list(result["accepted_intent_ids"])
            if result["reliable"] and len(selected) == 1:
                resolved.append(
                    ResolvedIntentOccurrence(
                        clause_index=clause_index,
                        intent_id=str(selected[0]),
                    )
                )
            else:
                unresolved.append(str(result["clause"]))
        return MultiIntentDecision(
            incomplete=bool(unresolved) or len(resolved) != len(clause_results),
            resolved_occurrences=tuple(resolved),
            unresolved_clauses=tuple(unresolved),
        )
