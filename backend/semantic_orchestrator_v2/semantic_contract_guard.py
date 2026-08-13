from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from pathlib import Path

import yaml

from semantic_registry_v1.registry import ROOT_DIR, UnifiedSemanticRegistry
from semantic_registry_v1.slots import resolve_slots


REVIEW_CASES_PATH = ROOT_DIR / "data/nlu/spec/audits/known_non_executable_semantic_review_cases_v3.yaml"


def _normalize(text: str) -> str:
    return "".join(unicodedata.normalize("NFKC", text).strip().lower().split())


@dataclass(frozen=True, slots=True)
class SemanticContractDecision:
    params: dict
    review_reasons: tuple[str, ...]


class SemanticContractGuard:
    """Registry-driven slot completeness plus frozen product-review cases."""

    def __init__(self, registry: UnifiedSemanticRegistry) -> None:
        self.registry = registry
        document = yaml.safe_load(REVIEW_CASES_PATH.read_text(encoding="utf-8"))
        self.review_cases = {
            _normalize(str(case["text"])): dict(case)
            for case in document.get("cases", [])
        }

    def check(self, clause: str, intent_id: str) -> SemanticContractDecision:
        definition = self.registry.definition(intent_id)
        slots = resolve_slots(clause, definition, self.registry.document)
        reasons: list[str] = []
        frozen = self.review_cases.get(_normalize(clause))
        if frozen is not None:
            # A frozen REVIEW case is a sentence-level product decision.  The
            # candidate is audit context, not a condition a different model
            # selection may use to bypass the review contract.
            reasons.append(str(frozen["reason"]))
        boundary = definition.get("boundary_contract") or {}
        required_object_terms = boundary.get("required_object_terms") or []
        if required_object_terms and not any(
            _normalize(str(term)) in _normalize(clause)
            for term in required_object_terms
        ):
            reasons.append(
                str(boundary.get("insufficient_object_reason", "OBJECT_INSUFFICIENT"))
            )
        reasons.extend(f"MISSING_REQUIRED_{slot}" for slot in slots.missing_required)
        return SemanticContractDecision(slots.params, tuple(dict.fromkeys(reasons)))

    def global_review_reason(self, text: str) -> str | None:
        """Return only explicitly candidate-null product review decisions."""

        frozen = self.review_cases.get(_normalize(text))
        if frozen is None or frozen.get("candidate") is not None:
            return None
        return str(frozen["reason"])
