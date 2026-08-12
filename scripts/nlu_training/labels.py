"""Frozen Stage 4B label mappings."""

from __future__ import annotations

from typing import Final


IGNORE_INDEX: Final = -100

SCOPE_LABELS: Final = (
    "IN_SCOPE_CONTROL",
    "NON_CONTROL",
    "UNKNOWN_CONTROL",
    "AMBIGUOUS_CONTROL",
)
STRUCTURE_LABELS: Final = ("SINGLE", "MULTI", "AMBIGUOUS")
INTENT_LABELS: Final = (
    "DOOR_OPEN",
    "DOOR_CLOSE",
    "WINDOW_OPEN",
    "WINDOW_SET_POSITION",
    "HEADLIGHT_OFF",
    "ACCELERATE",
    "BRAKE",
)
SLOT_LABELS: Final = (
    "O",
    "B-AREA",
    "I-AREA",
    "B-VALUE",
    "I-VALUE",
    "B-NEGATION",
    "I-NEGATION",
)
NEGATION_LABELS: Final = ("NOT_NEGATED", "NEGATED")
SUPPORTED_SLOT_TYPES: Final = ("AREA", "VALUE", "NEGATION")

SCOPE_TO_ID: Final = {label: index for index, label in enumerate(SCOPE_LABELS)}
STRUCTURE_TO_ID: Final = {label: index for index, label in enumerate(STRUCTURE_LABELS)}
INTENT_TO_ID: Final = {label: index for index, label in enumerate(INTENT_LABELS)}
SLOT_TO_ID: Final = {label: index for index, label in enumerate(SLOT_LABELS)}
NEGATION_TO_ID: Final = {label: index for index, label in enumerate(NEGATION_LABELS)}


def label_mapping_report() -> dict[str, object]:
    return {
        "IGNORE_INDEX": IGNORE_INDEX,
        "scope": SCOPE_TO_ID,
        "structure": STRUCTURE_TO_ID,
        "intent": INTENT_TO_ID,
        "slot_bio": SLOT_TO_ID,
        "sentence_negation": NEGATION_TO_ID,
        "intent_eligibility": "scope=IN_SCOPE_CONTROL AND structure=SINGLE AND intent!=null",
        "negation_eligibility": "scope=IN_SCOPE_CONTROL AND structure=SINGLE AND negated is boolean",
    }
