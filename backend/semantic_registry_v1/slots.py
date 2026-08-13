from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


_PERCENT = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*%")
_NUMBER = re.compile(r"(?<![A-Za-z])(?P<value>\d+(?:\.\d+)?)")
_CHINESE_RATIO = {
    "一成": 10, "两成": 20, "二成": 20, "三成": 30, "四成": 40,
    "五成": 50, "六成": 60, "七成": 70, "八成": 80, "九成": 90, "一半": 50,
}


@dataclass(frozen=True, slots=True)
class SlotResolution:
    params: dict[str, Any]
    missing_required: tuple[str, ...]


def _first_surface(text: str, mapping: dict[str, list[str]]) -> str | None:
    lowered = text.lower()
    matches = [
        (lowered.find(surface.lower()), -len(surface), canonical)
        for canonical, surfaces in mapping.items()
        for surface in surfaces
        if surface and surface.lower() in lowered
    ]
    return min(matches)[2] if matches else None


def _numeric_value(text: str, contract: dict[str, Any] | None) -> int | float | str | None:
    if not contract or contract.get("allowed") is False:
        return None
    contract_type = str(contract.get("type", ""))
    if contract_type == "PERCENT":
        match = _PERCENT.search(text)
        if match:
            value = float(match.group("value"))
            return int(value) if value.is_integer() else value
        for surface, value in _CHINESE_RATIO.items():
            if surface in text:
                return value
    match = _NUMBER.search(text)
    if match and contract_type not in {"NONE", ""}:
        value = float(match.group("value"))
        return int(value) if value.is_integer() else value
    enum_values = contract.get("enum_values", [])
    if isinstance(enum_values, list):
        for value in sorted((str(item) for item in enum_values), key=len, reverse=True):
            if value and value.lower() in text.lower():
                return value
    return None


def resolve_slots(
    text: str,
    definition: dict[str, Any],
    registry_document: dict[str, Any],
) -> SlotResolution:
    """Resolve slots using only catalogs contained in the unified Registry."""

    params: dict[str, Any] = {}
    value_contract_id = definition.get("value_contract")
    value_contract = (
        registry_document.get("value_contracts", {}).get(str(value_contract_id))
        if value_contract_id
        else None
    )
    value = _numeric_value(text, value_contract)
    if value is not None:
        params["value"] = value

    mode_contract = definition.get("mode_contract")
    mode_mapping = registry_document.get("mode_surface_mappings", {}).get(
        str(mode_contract), {}
    )
    if mode_mapping:
        mode = _first_surface(text, mode_mapping)
        if mode is not None:
            params["mode"] = mode

    direction_contract = definition.get("direction_contract")
    direction_mapping = registry_document.get("direction_surface_mappings", {}).get(
        str(direction_contract), {}
    )
    if direction_mapping:
        direction = _first_surface(text, direction_mapping)
        if direction is not None:
            params["direction"] = direction

    missing = tuple(
        str(slot).upper()
        for slot in definition.get("required_slots", [])
        if str(slot).lower() not in params
    )
    return SlotResolution(params=params, missing_required=missing)
