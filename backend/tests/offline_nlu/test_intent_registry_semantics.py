from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = ROOT / "scripts/validate_intent_registry.py"
SPEC = importlib.util.spec_from_file_location("validate_intent_registry", VALIDATOR_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def test_formal_intent_registry_semantics_are_consistent() -> None:
    result = VALIDATOR.validate()

    assert result["status"] == "PASS", result["errors"]
    assert result["metrics"] == {
        "INTENT_COUNT": 93,
        "SEMANTIC_KEY_UNIQUE_COUNT": 93,
        "SEMANTIC_KEY_COLLISION_COUNT": 0,
        "MISSING_VALUE_CONTRACT_COUNT": 0,
        "MISSING_DIRECTION_CONTRACT_COUNT": 0,
        "MISSING_MODE_CONTRACT_COUNT": 0,
        "MISSING_VALUE_MAPPING_CONTRACT_COUNT": 0,
        "UNKNOWN_AREA_REFERENCE_COUNT": 0,
        "MIDDLE_AREA_VSS_MISMATCH_COUNT": 0,
        "LIGHT_SOURCE_CHANGED_COUNT": 0,
        "TORQUE_DISTRIBUTION_SEMANTIC_BLOCKER_COUNT": 0,
        "CAPABILITY_NEGATION_SLOT_COUNT": 0,
        "RUNTIME_SUPPORT_COVERAGE_COUNT": 93,
        "UNRESOLVED_SEMANTIC_BLOCKER_COUNT": 0,
        "OLD_REGISTRY_SHA256": VALIDATOR.EXPECTED_OLD_SHA256,
        "R1_REGISTRY_SHA256": VALIDATOR.EXPECTED_R1_SHA256,
        "NEW_REGISTRY_SHA256": result["metrics"]["NEW_REGISTRY_SHA256"],
        "SEMANTIC_FREEZE_STATUS": "REOPENED_PENDING_REVIEW",
    }


def test_registry_ontologies_are_smaller_than_the_intent_set() -> None:
    result = VALIDATOR.validate()

    assert len(result["actions"]) < 93
    assert len(result["targets"]) < 93
    assert len(result["attributes"]) < 93
