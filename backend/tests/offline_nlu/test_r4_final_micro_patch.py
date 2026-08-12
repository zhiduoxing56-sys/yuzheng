from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from validate_sys014_r4_final_micro_patch import validate  # noqa: E402


def test_r4_final_micro_patch_validator_passes():
    result = validate()
    assert result["status"] == "PASS", result["errors"]


def test_r4_final_micro_patch_has_exactly_one_semantic_change():
    result = validate()
    assert result["yaml_semantic_changed_field_count"] == 1
    assert result["yaml_semantic_changed_paths"] == [
        "mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH.restricted_aliases.ON.prohibited_canonical_mode"
    ]


def test_r4_final_micro_patch_sidecars_are_complete():
    result = validate()
    assert result["gold_absolute_speed_rule_landed"] is True
    assert result["execution_todos_registered"] is True
    assert result["metrics"]["MANDATORY_MAPPING_RULE_COUNT"] == 1
    assert result["metrics"]["EXECUTION_TODO_COUNT"] == 2
