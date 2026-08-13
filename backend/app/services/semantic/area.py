from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import yaml


_UNIFIED_INTENT_REGISTRY = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "nlu"
    / "spec"
    / "intent_registry_unified_v1.yaml"
)

@lru_cache(maxsize=1)
def _registry() -> dict[str, Any]:
    value = yaml.safe_load(_UNIFIED_INTENT_REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("R4 Intent Registry root must be a mapping")
    return value


def canonical_area_values() -> frozenset[str]:
    catalog = _registry().get("area_catalog", {})
    if not isinstance(catalog, dict):
        raise RuntimeError("R4 area_catalog must be a mapping")
    return frozenset(str(value) for value in catalog)


def canonical_area(value: object) -> str | None:
    normalized = str(value).strip() if value is not None else ""
    return normalized if normalized in canonical_area_values() else None


def allowed_areas_for_intent(intent_id: str) -> frozenset[str]:
    definition = next(
        (
            value
            for value in _registry().get("intents", [])
            if isinstance(value, dict) and str(value.get("intent_id")) == intent_id
        ),
        None,
    )
    if definition is None:
        return frozenset()
    return frozenset(
        value
        for raw in definition.get("allowed_areas", [])
        if (value := canonical_area(raw)) is not None
    )


@lru_cache(maxsize=1)
def _area_expressions() -> tuple[tuple[str, str], ...]:
    catalog = _registry()["area_catalog"]
    expressions: dict[str, str] = {}
    for area, definition in catalog.items():
        raw_terms = [definition.get("semantic_frame_value"), *definition.get("examples", [])]
        for raw_term in raw_terms:
            term = str(raw_term or "").strip()
            if term:
                expressions[term] = str(area)
    return tuple(
        sorted(expressions.items(), key=lambda item: (-len(item[0]), item[0], item[1]))
    )


def explicit_area_mentions(text: str) -> tuple[tuple[str, str], ...]:
    """Return only expressions frozen in Registry.area_catalog, without inference."""

    return tuple((term, area) for term, area in _area_expressions() if term in text)


def resolve_explicit_area(text: str, allowed_areas: Iterable[str]) -> str | None:
    """Resolve only explicit R4 area expressions; never infer a default area."""

    allowed = {value for raw in allowed_areas if (value := canonical_area(raw))}
    matches = [
        (len(term), text.find(term), area)
        for term, area in _area_expressions()
        if area in allowed and term in text
    ]
    if not matches:
        return None
    longest = max(length for length, _position, _area in matches)
    best_areas = {
        area for length, _position, area in matches if length == longest
    }
    if len(best_areas) != 1:
        return None
    return next(iter(best_areas))
