from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_sys014_r4_scope_simplification import (  # noqa: E402
    ARCHIVE_PATH,
    FINAL_PARENT_PATH,
    RUNTIME_SCOPES,
    SIMPLIFIED_PATH,
    build_archive,
    build_simplified_registry,
    load_yaml,
)
from validate_sys014_r4_core_registry import sha256_file  # noqa: E402
from validate_sys014_r4_scope_simplification import validate  # noqa: E402


def _documents():
    return load_yaml(FINAL_PARENT_PATH), load_yaml(SIMPLIFIED_PATH), load_yaml(ARCHIVE_PATH)


def test_scope_simplification_validator_passes():
    result = validate()
    assert result["status"] == "PASS", result["errors"]
    assert all(result["required_outcomes"].values())


def test_scope_simplification_builder_is_deterministic():
    parent, simplified, archive = _documents()
    rebuilt_archive = build_archive(parent)
    assert rebuilt_archive == archive
    rebuilt_simplified = build_simplified_registry(parent, sha256_file(ARCHIVE_PATH), 91)
    assert rebuilt_simplified == simplified


def test_formal_intent_head_is_exact_parent_projection():
    parent, simplified, _ = _documents()
    parent_formal = [item for item in parent["intents"] if item["user_voice_scope_status"] == "FORMAL_EXECUTABLE"]
    assert len(parent_formal) == 71
    assert simplified["intents"] == parent_formal
    assert simplified["formal_user_voice_intent_ids"] == [item["intent_id"] for item in parent_formal]
    assert all(item["user_voice_scope_status"] == "FORMAL_EXECUTABLE" for item in simplified["intents"])


def test_all_detailed_known_control_definitions_are_archived_exactly():
    parent, simplified, archive = _documents()
    parent_known = [item for item in parent["intents"] if item["user_voice_scope_status"] == "KNOWN_UNSUPPORTED_CONTROL"]
    assert len(parent_known) == 91
    assert archive["archived_intents"] == parent_known
    assert archive["archived_intent_count"] == 91
    assert archive["usage_policy"]["runtime_registry"] is False
    assert archive["usage_policy"]["model_label_space"] is False
    assert "known_unsupported_control_intent_ids" not in simplified


def test_four_scopes_and_bypass_route_are_exact():
    _, simplified, _ = _documents()
    assert simplified["enums"]["runtime_scope"] == RUNTIME_SCOPES
    bypass = simplified["user_voice_scope_contract"]["KNOWN_CONTROL_BYPASS"]
    for field in (
        "requires_intent_id", "requires_canonical_action", "requires_canonical_target",
        "requires_control_attribute", "requires_value", "requires_mode", "requires_area",
    ):
        assert bypass[field] is False
    assert bypass["formal_contract_completeness_check"] == "SKIP"
    assert simplified["runtime_scope_routing"]["KNOWN_CONTROL_BYPASS"] == {
        "decision_route": "PASS_BYPASS",
        "execution_authorized_by_yuzheng": False,
        "route_target": "NATIVE_COCKPIT_ASSISTANT",
    }


def test_non_control_unknown_and_mixed_multi_intent_remain_distinct():
    _, simplified, _ = _documents()
    contracts = simplified["user_voice_scope_contract"]
    assert contracts["NON_CONTROL"] != contracts["UNKNOWN_OOD"]
    schema = simplified["multi_intent_schema"]
    assert schema["ordered_sub_intents_required"] is True
    assert schema["per_sub_intent_scope_and_routing_required"] is True
    assert schema["sentence_level_route_collapse_prohibited"] is True
    assert schema["mixed_example"]["sub_intents"] == [
        {"scope": "KNOWN_CONTROL_BYPASS"},
        {"scope": "FORMAL_EXECUTABLE", "intent_id": "LOW_BEAM_OFF"},
    ]


def test_formal_contracts_and_p0_guidance_are_closed_and_preserved():
    parent, simplified, _ = _documents()
    p0_sections = [
        "window_endpoint_routing", "speed_delta_routing", "cruise_gap_routing",
        "seat_semantic_boundaries", "headlight_main_switch_routing",
    ]
    for section in p0_sections:
        assert simplified["annotation_guidance"][section] == parent["annotation_guidance"][section]
    boundary = simplified["annotation_guidance"]["trunk_frunk_hood_routing"]
    assert boundary["FRUNK"]["runtime_scope"] == "KNOWN_CONTROL_BYPASS"
    assert boundary["FRUNK"]["detailed_intent_assignment_prohibited"] is True
    assert simplified["statistics"]["intent_count"] == 71
    assert simplified["statistics"]["known_unsupported_control_intent_count"] == 0
    assert simplified["statistics"]["archived_known_control_reference_count"] == 91


def test_required_scope_simplification_outputs_exist():
    for path in (
        SIMPLIFIED_PATH,
        ARCHIVE_PATH,
        ROOT / "data/nlu/spec/audits/r4_scope_simplification_diff.md",
        ROOT / "data/nlu/spec/audits/r4_scope_simplification_validator.json",
    ):
        assert path.is_file(), path
