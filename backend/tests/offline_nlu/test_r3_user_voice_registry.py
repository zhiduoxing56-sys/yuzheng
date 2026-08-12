from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = ROOT / "scripts/validate_sys014_r3_voice_registry.py"
SPEC = importlib.util.spec_from_file_location("validate_sys014_r3_voice_registry", VALIDATOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_frozen_r3_user_voice_registry_is_valid() -> None:
    result = MODULE.validate()
    assert result["status"] == "PASS", result["errors"]
    assert result["metrics"]["FORMAL_USER_VOICE_INTENT_COUNT"] == 71
    assert result["metrics"]["KNOWN_UNSUPPORTED_CONTROL_INTENT_COUNT"] == 22
    assert result["metrics"]["ACTIVE_FULL_NLU_DEPENDENCY_COUNT"] == 0


def test_r3_has_no_7_intent_inheritance() -> None:
    result = MODULE.validate()
    assert len(result["formal_user_voice_intent_ids"]) == 71
    assert result["metrics"]["RUNTIME_EXECUTION_FULL_COUNT"] == 7
    assert set(result["formal_user_voice_intent_ids"]) != MODULE.EXPECTED_RUNTIME_FULL
