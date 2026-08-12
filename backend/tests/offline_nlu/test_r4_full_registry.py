from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
FULL_NLU = SCRIPTS / "full_nlu"
for path in (SCRIPTS, FULL_NLU):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_module("validate_sys014_r4_full_registry", SCRIPTS / "validate_sys014_r4_full_registry.py")
BUILDER = _load_module("build_sys014_r4_full_draft", SCRIPTS / "build_sys014_r4_full_draft.py")


def test_r4_full_draft_passes_all_contract_gates() -> None:
    result = VALIDATOR.validate()

    assert result["status"] == "PASS", result["errors"]
    assert result["metrics"] == {
        "SEMANTIC_INTENT_COUNT": 154,
        "FORMAL_USER_VOICE_INTENT_COUNT": 71,
        "KNOWN_UNSUPPORTED_CONTROL_INTENT_COUNT": 83,
        "NEW_INTENT_COUNT": 61,
        "NEW_CAPABILITY_FAMILY_COUNT": 23,
        "PROJECT_NATIVE_INTENT_COUNT": 69,
        "VSS_DERIVED_INTENT_COUNT": 85,
        "CAPABILITY_FAMILY_COUNT": 72,
        "SEMANTIC_KEY_COLLISION_COUNT": 0,
        "UNRESOLVED_REFERENCE_COUNT": 0,
        "SLOT_INTERSECTION_COUNT": 0,
        "INVALID_MODE_ENUM_COUNT": 0,
        "ACTIVE_FOLLOWING_GAP_REFERENCE_COUNT": 0,
        "ACTIVE_FULL_NLU_DEPENDENCY_COUNT": 0,
        "CHANGED_PATH_COUNT": result["metrics"]["CHANGED_PATH_COUNT"],
    }


def test_full_builder_is_complete_and_deterministic(tmp_path: Path) -> None:
    core = BUILDER.load_yaml(BUILDER.CORE_PATH)
    frames = BUILDER.extract_frames(BUILDER.MAC_PATHS, BUILDER.SOURCE_SCREEN_PATH)
    evidence = BUILDER.build_evidence(frames)
    expected, reports = BUILDER.build_registry(core, evidence, BUILDER._source_hashes())
    actual = BUILDER.load_yaml(BUILDER.FULL_PATH)

    assert actual == expected
    assert len(reports) == 61
    assert [item["intent_id"] for item in actual["intents"][:93]] == [
        item["intent_id"] for item in core["intents"]
    ]
    output = tmp_path / "full.yaml"
    BUILDER.write_yaml(output, expected)
    assert output.read_bytes() == BUILDER.FULL_PATH.read_bytes()


def test_formal_projection_and_new_provenance_are_frozen() -> None:
    core = BUILDER.load_yaml(BUILDER.CORE_PATH)
    full = BUILDER.load_yaml(BUILDER.FULL_PATH)
    core_ids = {item["intent_id"] for item in core["intents"]}
    new_items = [item for item in full["intents"] if item["intent_id"] not in core_ids]

    assert full["formal_user_voice_intent_ids"] == core["formal_user_voice_intent_ids"]
    assert len(full["formal_user_voice_intent_ids"]) == 71
    assert all(item["user_voice_scope_status"] == "KNOWN_UNSUPPORTED_CONTROL" for item in new_items)
    assert all(item["capability_origin"] == "PROJECT_NATIVE" for item in new_items)
    assert all(item["vss_relation"] == "NONE" and item["vss_capability_ids"] == [] for item in new_items)


def test_frunk_boundary_and_zero_evidence_close_candidate() -> None:
    full = BUILDER.load_yaml(BUILDER.FULL_PATH)
    ids = {item["intent_id"] for item in full["intents"]}
    other = json.loads(BUILDER.OTHER_REPORT_PATH.read_text(encoding="utf-8"))

    assert "FRUNK_OPEN" in ids
    assert not ({"FRUNK_CLOSE", "FRUNK_SET_POSITION", "FRUNK_LOCK", "FRUNK_UNLOCK"} & ids)
    candidate = next(item for item in other["candidates"] if item["suggested_intent_id"] == "FRUNK_CLOSE")
    assert candidate["unique_sample_count"] == 0
    assert candidate["approval_status"] == "PENDING_NO_REAL_DATA_EVIDENCE"


def test_dead_contract_and_parent_hashes_remain_safe() -> None:
    full = BUILDER.load_yaml(BUILDER.FULL_PATH)

    assert "FOLLOWING_GAP_REQUIRED" not in full["value_contracts"]
    assert "FOLLOWING_GAP_REQUIRED" not in full["value_language_semantics"]["continuous_numeric_contracts"]
    assert BUILDER.sha256_file(BUILDER.R3_PATH) == BUILDER.R3_SHA256
    assert BUILDER.sha256_file(BUILDER.CORE_PATH) == BUILDER.CORE_SHA256


def test_validator_rejects_formal_space_expansion(tmp_path: Path) -> None:
    full = BUILDER.load_yaml(BUILDER.FULL_PATH)
    invalid = copy.deepcopy(full)
    frunk = next(item for item in invalid["intents"] if item["intent_id"] == "FRUNK_OPEN")
    frunk["user_voice_scope_status"] = "FORMAL_EXECUTABLE"
    invalid["formal_user_voice_intent_ids"].append("FRUNK_OPEN")
    candidate = tmp_path / "invalid_formal.yaml"
    BUILDER.write_yaml(candidate, invalid)

    result = VALIDATOR.validate(candidate)

    assert result["status"] == "FAIL"
    assert any(error.startswith("FORMAL_COUNT:") for error in result["errors"])


def test_candidate_reports_never_auto_enter_registry() -> None:
    full = BUILDER.load_yaml(BUILDER.FULL_PATH)
    ids = {item["intent_id"] for item in full["intents"]}
    adas = json.loads(BUILDER.ADAS_REPORT_PATH.read_text(encoding="utf-8"))
    other = json.loads(BUILDER.OTHER_REPORT_PATH.read_text(encoding="utf-8"))

    assert adas["candidate_count"] > 0
    assert other["candidate_count"] > 0
    assert all(item["approval_status"] == "PENDING" for item in adas["candidates"])
    assert not ({item["suggested_intent_id"] for item in adas["candidates"]} & ids)
    assert not ({item["suggested_intent_id"] for item in other["candidates"]} & set(VALIDATOR.validate()["new_intent_ids"]))
