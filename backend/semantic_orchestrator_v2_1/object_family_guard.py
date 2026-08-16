from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from semantic_orchestrator_v2.action_direction_guard import (
    ActionDirectionGuard,
    requested_families,
)


OBJECT_FAMILY_TERMS: dict[str, tuple[str, ...]] = {
    "WINDOW": ("车窗", "窗户", "车玻璃", "玻璃窗"),
    "SUNROOF": ("天窗",),
    "DOOR": ("车门", "侧门", "侧滑门"),
    "TRUNK": ("后备箱", "后备厢", "行李厢", "尾门"),
    "HOOD": ("前舱盖", "发动机舱盖", "引擎盖"),
    "MIRROR": ("后视镜", "外后视镜"),
}


@dataclass(frozen=True, slots=True)
class ObjectFamilyDecision:
    explicit_families: tuple[str, ...]
    selected_families: tuple[str | None, ...]
    requested_action_families: tuple[str, ...]
    matching_candidates: tuple[str, ...]
    final_intent_ids: tuple[str, ...]
    corrected_from: tuple[str, ...]
    corrected_to: str | None
    correction: bool
    conflict: bool


@dataclass(frozen=True, slots=True)
class ObjectFamilyEligibility:
    explicit_families: tuple[str, ...]
    eligible_candidates: tuple[str, ...]
    applied: bool


def explicit_object_families(text: str) -> tuple[str, ...]:
    hits: list[tuple[int, int, str]] = []
    for family, terms in OBJECT_FAMILY_TERMS.items():
        for term in terms:
            start = text.find(term)
            while start >= 0:
                hits.append((start, -len(term), family))
                start = text.find(term, start + len(term))
    hits.sort()
    return tuple(dict.fromkeys(family for _start, _length, family in hits))


class ObjectFamilyGuard:
    def __init__(
        self,
        intent_cards: dict[str, dict[str, Any]],
        direction_guard: ActionDirectionGuard,
    ) -> None:
        self.intent_cards = intent_cards
        self.direction_guard = direction_guard

    def family_for_intent(self, intent_id: str) -> str | None:
        card = self.intent_cards.get(intent_id)
        if not card:
            return None
        value = card.get("canonical_target")
        return str(value) if value is not None else None

    def eligible_candidates(
        self, clause: str, stage1_candidates: list[str]
    ) -> ObjectFamilyEligibility:
        """Pre-filter only when one explicit object family is present.

        The terms and canonical targets are the same facts used by ``check``;
        multiple or absent object mentions deliberately retain every candidate.
        """
        explicit = explicit_object_families(clause)
        if len(explicit) != 1:
            return ObjectFamilyEligibility(explicit, tuple(stage1_candidates), False)
        family = explicit[0]
        eligible = tuple(
            intent_id
            for intent_id in stage1_candidates
            if self.family_for_intent(intent_id) == family
        )
        return ObjectFamilyEligibility(explicit, eligible, True)

    def check(
        self,
        clause: str,
        selected_intents: list[str],
        stage1_candidates: list[str],
    ) -> ObjectFamilyDecision:
        explicit = explicit_object_families(clause)
        selected_families = tuple(self.family_for_intent(value) for value in selected_intents)
        requested = requested_families(clause)
        if not explicit or not selected_intents:
            return ObjectFamilyDecision(
                explicit,
                selected_families,
                requested,
                (),
                tuple(selected_intents),
                (),
                None,
                False,
                False,
            )

        consistent = [
            intent_id
            for intent_id, family in zip(selected_intents, selected_families)
            if family in explicit
        ]
        conflicting = [
            intent_id
            for intent_id, family in zip(selected_intents, selected_families)
            if family not in explicit
        ]
        if not conflicting:
            return ObjectFamilyDecision(
                explicit,
                selected_families,
                requested,
                (),
                tuple(selected_intents),
                (),
                None,
                False,
                False,
            )

        covered_families = {
            self.family_for_intent(intent_id) for intent_id in consistent
        }
        missing_families = set(explicit) - covered_families
        matches: list[str] = []
        for candidate in stage1_candidates:
            if candidate in consistent:
                continue
            if self.family_for_intent(candidate) not in missing_families:
                continue
            if requested and self.direction_guard.family_for_intent(candidate) not in requested:
                continue
            matches.append(candidate)
        matches = list(dict.fromkeys(matches))

        if len(matches) != 1:
            return ObjectFamilyDecision(
                explicit,
                selected_families,
                requested,
                tuple(matches),
                tuple(selected_intents),
                tuple(conflicting),
                None,
                False,
                True,
            )

        replacement = matches[0]
        final: list[str] = []
        inserted = False
        conflicting_set = set(conflicting)
        for intent_id in selected_intents:
            if intent_id in conflicting_set:
                if not inserted:
                    final.append(replacement)
                    inserted = True
            else:
                final.append(intent_id)
        final = list(dict.fromkeys(final))
        return ObjectFamilyDecision(
            explicit,
            selected_families,
            requested,
            tuple(matches),
            tuple(final),
            tuple(conflicting),
            replacement,
            True,
            False,
        )
