from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
FULL_NLU = SCRIPTS / "full_nlu"
for path in (SCRIPTS, FULL_NLU):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from build_sys014_r4_final_candidate import (  # noqa: E402
    FINAL_PATH,
    FULL_PATH,
    VALUE_REQUIRED_INTENTS,
    build_final_registry,
    load_yaml,
)
from r4_final_candidate_evidence import (  # noqa: E402
    APPROVED_NEW_INTENT_IDS,
    AREA_FAMILIES,
    CAMERA_DIRECT_ACTION_VALUES,
    MEDIA_FORBIDDEN_VALUES,
    build_final_patch_evidence,
)
from r4_known_unsupported_evidence import extract_frames  # noqa: E402
from validate_sys014_r4_final_candidate import (  # noqa: E402
    EXPECTED_EVIDENCE_COUNTS,
    MAC_PATHS,
    SOURCE_SCREEN_PATH,
    validate,
)


def _documents():
    return load_yaml(FULL_PATH), load_yaml(FINAL_PATH)


def _evidence(full):
    frames = extract_frames(MAC_PATHS, SOURCE_SCREEN_PATH)
    return build_final_patch_evidence(frames, full["area_catalog"])


def test_r4_final_validator_passes():
    result = validate()
    assert result["status"] == "PASS", result["errors"]


def test_final_builder_is_deterministic():
    full, actual = _documents()
    rebuilt = build_final_registry(full, _evidence(full))
    assert rebuilt == actual


def test_formal_catalog_is_exactly_frozen():
    full, final = _documents()
    full_formal = [item for item in full["intents"] if item["user_voice_scope_status"] == "FORMAL_EXECUTABLE"]
    final_formal = [item for item in final["intents"] if item["user_voice_scope_status"] == "FORMAL_EXECUTABLE"]
    assert len(final_formal) == 71
    assert final_formal == full_formal


def test_only_eight_approved_intents_are_added_with_real_evidence():
    full, final = _documents()
    full_ids = [item["intent_id"] for item in full["intents"]]
    final_ids = [item["intent_id"] for item in final["intents"]]
    assert final_ids == full_ids + APPROVED_NEW_INTENT_IDS
    evidence = _evidence(full)
    assert {
        intent_id: evidence["approved_new_intents"][intent_id]["unique_sample_count"]
        for intent_id in APPROVED_NEW_INTENT_IDS
    } == EXPECTED_EVIDENCE_COUNTS


def test_value_contract_repairs_require_value_without_overlap():
    _, final = _documents()
    by_id = {item["intent_id"]: item for item in final["intents"]}
    for intent_id, contract in VALUE_REQUIRED_INTENTS.items():
        item = by_id[intent_id]
        assert item["value_contract"] == contract
        assert "VALUE" in item["required_slots"]
        assert "VALUE" not in item["optional_slots"]
    assert by_id["GLASS_ROOF_SET_TRANSPARENCY"]["value_contract"] == "SOURCE_TRANSPARENCY_REQUIRED"


def test_family_area_union_and_steering_wheel_singleton():
    full, final = _documents()
    evidence = _evidence(full)
    families = {item["family_id"]: item for item in final["capability_families"]}
    by_id = {item["intent_id"]: item for item in final["intents"]}
    for family_key in AREA_FAMILIES:
        allowed = evidence["family_area_evidence"][family_key]["allowed_areas"]
        for intent_id in families[f"PROJECT_{family_key}_KNOWN_CONTROL"]["intents"]:
            assert by_id[intent_id]["allowed_areas"] == allowed
            assert ("AREA" in by_id[intent_id]["optional_slots"]) == bool(allowed)
    for intent_id in ("STEERING_WHEEL_HEATING_ON", "STEERING_WHEEL_HEATING_OFF"):
        assert by_id[intent_id]["allowed_areas"] == []
        assert "AREA" not in by_id[intent_id]["optional_slots"]


def test_media_camera_and_frunk_boundaries():
    _, final = _documents()
    media = set(final["mode_contracts"]["KNOWN_MEDIA_SOURCE_MODE"])
    camera = set(final["mode_contracts"]["KNOWN_CAMERA_SOURCE_MODE"])
    assert not media & MEDIA_FORBIDDEN_VALUES
    assert not camera & CAMERA_DIRECT_ACTION_VALUES
    guidance = final["annotation_guidance"]["trunk_frunk_hood_routing"]
    assert guidance["FRUNK"]["proven_operations"] == ["OPEN"]
    assert guidance["FRUNK"]["pending_operations"] == ["CLOSE"]
    assert "FRUNK_CLOSE" not in {item["intent_id"] for item in final["intents"]}
    assert "FOLLOWING_GAP_REQUIRED" not in final["value_contracts"]


def test_required_outputs_exist():
    assert FINAL_PATH.is_file()
    assert (ROOT / "data/nlu/spec/audits/r4_full_to_final_diff.md").is_file()
    assert (ROOT / "data/nlu/spec/audits/r4_final_validator_result.json").is_file()
