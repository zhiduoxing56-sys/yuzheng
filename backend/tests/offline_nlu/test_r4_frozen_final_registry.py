from __future__ import annotations

import copy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_sys014_r4_final_freeze import (  # noqa: E402
    FINAL_PATH,
    NEXT_MAPPING_PATH,
    SIMPLIFIED_PATH,
    build_final_registry,
    load_yaml,
)
from validate_sys014_r4_frozen_final import RUNTIME_SCOPES, validate  # noqa: E402


def _documents():
    return load_yaml(SIMPLIFIED_PATH), load_yaml(FINAL_PATH)


def test_r4_frozen_final_validator_passes():
    result = validate()
    assert result["status"] == "PASS", result["errors"]
    assert result["metrics"]["FORBIDDEN_CHANGED_PATH_COUNT"] == 0
    assert result["metrics"]["ACTIVE_7_INTENT_DEPENDENCY_COUNT"] == 0


def test_final_freeze_builder_is_deterministic():
    simplified, final = _documents()
    assert build_final_registry(simplified) == final


def test_all_formal_intents_and_contracts_are_exact():
    simplified, final = _documents()
    assert final["intents"] == simplified["intents"]
    assert final["formal_user_voice_intent_ids"] == simplified["formal_user_voice_intent_ids"]
    for section in (
        "value_contracts", "mode_contracts", "direction_contracts", "conditional_slot_contracts",
        "value_mapping_contracts", "area_catalog", "area_semantics", "value_language_semantics",
    ):
        assert final[section] == simplified[section]
    expected_mode_mapping_contracts = copy.deepcopy(simplified["mode_mapping_contracts"])
    del expected_mode_mapping_contracts["HEADLIGHT_MAIN_SWITCH"]["restricted_aliases"]["ON"][
        "prohibited_canonical_mode"
    ]
    assert final["mode_mapping_contracts"] == expected_mode_mapping_contracts


def test_legacy_mapping_is_provenance_only():
    simplified, final = _documents()
    mapping = final["mapping_rule_source"]
    for field in ("path", "version", "sha256"):
        assert mapping[field] == simplified["mapping_rule_source"][field]
    assert mapping["status"] == "LEGACY_PRE_R4_MAPPING"
    assert mapping["usable_for_r4_gold"] is False
    assert mapping["usable_for_training"] is False
    assert mapping["required_next_mapping_version"] == "nlu_mapping_r4_scope_v1"
    assert NEXT_MAPPING_PATH.exists() is False


def test_known_control_evidence_uses_raw_text_priority():
    _, final = _documents()
    policy = final["gold_scope_mapping_policy"]["known_control_evidence_policy"]
    assert policy["primary_evidence"] == "RAW_TEXT"
    assert policy["auxiliary_evidence_when_available"] == ["MAC_SPLIT_SENS", "MAC_SEMANTICS"]
    assert policy["evidence_priority"] == ["RAW_TEXT", "MAC_SPLIT_SENS", "MAC_SEMANTICS"]
    assert policy["all_three_required"] is False
    assert policy["baseline_mapping_as_truth_prohibited"] is True
    assert policy["source_conflict_policy"] == {
        "annotation_must_not_override_raw_text": True,
        "route": "SOURCE_CONFLICT_REVIEW",
    }
    assert "known_control_evidence_requirement" not in final["gold_scope_mapping_policy"]


def test_scope_routing_and_multi_intent_schema_are_unchanged():
    simplified, final = _documents()
    assert final["enums"]["runtime_scope"] == RUNTIME_SCOPES
    assert final["user_voice_scope_contract"] == simplified["user_voice_scope_contract"]
    assert final["runtime_scope_routing"] == simplified["runtime_scope_routing"]
    assert final["multi_intent_schema"] == simplified["multi_intent_schema"]
    assert final["runtime_scope_routing"]["KNOWN_CONTROL_BYPASS"] == {
        "decision_route": "PASS_BYPASS",
        "execution_authorized_by_yuzheng": False,
        "route_target": "NATIVE_COCKPIT_ASSISTANT",
    }


def test_final_freeze_statistics_and_dead_contract():
    _, final = _documents()
    expected = {
        "intent_count": 71,
        "formal_user_voice_intent_count": 71,
        "runtime_intent_head_count": 71,
        "known_unsupported_control_intent_count": 0,
        "archived_known_control_reference_count": 91,
        "runtime_scope_count": 4,
    }
    assert all(final["statistics"][key] == value for key, value in expected.items())
    assert "FOLLOWING_GAP_REQUIRED" not in final["value_contracts"]


def test_required_final_freeze_outputs_exist():
    for path in (
        FINAL_PATH,
        ROOT / "data/nlu/spec/audits/r4_simplified_to_final_diff.md",
        ROOT / "data/nlu/spec/audits/r4_final_validator_result.json",
    ):
        assert path.is_file(), path
