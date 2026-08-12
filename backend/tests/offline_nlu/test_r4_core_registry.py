from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = _load_module(
    "validate_sys014_r4_core_registry",
    SCRIPTS / "validate_sys014_r4_core_registry.py",
)
BUILDER = _load_module(
    "build_sys014_r4_core_draft",
    SCRIPTS / "build_sys014_r4_core_draft.py",
)


def test_r4_core_draft_passes_all_contract_checks() -> None:
    result = VALIDATOR.validate()

    assert result["status"] == "PASS", result["errors"]
    assert result["metrics"]["SEMANTIC_INTENT_COUNT"] == 93
    assert result["metrics"]["FORMAL_USER_VOICE_INTENT_COUNT"] == 71
    assert result["metrics"]["PROJECT_NATIVE_INTENT_COUNT"] == 8
    assert result["metrics"]["SEMANTIC_KEY_COLLISION_COUNT"] == 0
    assert result["metrics"]["UNRESOLVED_CONTRACT_COUNT"] == 0
    assert result["metrics"]["REQUIRED_OPTIONAL_SLOT_CONFLICT_COUNT"] == 0
    assert result["metrics"]["BOOL_MODE_VALUE_COUNT"] == 0
    assert result["metrics"]["UNAPPROVED_CHANGED_PATH_COUNT"] == 0
    assert result["metrics"]["P0_PASS_COUNT"] == 7
    assert all(item["validator_result"] == "PASS" for item in result["p0_results"])


def test_builder_preserves_complete_r3_copy_and_is_deterministic(tmp_path: Path) -> None:
    r3 = BUILDER.load_yaml(BUILDER.R3_PATH)
    expected = BUILDER.build_registry(r3)
    actual = BUILDER.load_yaml(BUILDER.R4_PATH)

    assert actual == expected
    assert set(actual) == set(r3) | {"annotation_guidance"}
    assert [item["intent_id"] for item in actual["intents"]] == [
        item["intent_id"] for item in r3["intents"]
    ]

    first = tmp_path / "first.yaml"
    second = tmp_path / "second.yaml"
    BUILDER.write_yaml(first, BUILDER.build_registry(r3))
    BUILDER.write_yaml(second, BUILDER.build_registry(r3))
    assert first.read_bytes() == second.read_bytes() == BUILDER.R4_PATH.read_bytes()


def test_validator_rejects_an_eighth_semantic_change(tmp_path: Path) -> None:
    r4 = BUILDER.load_yaml(BUILDER.R4_PATH)
    unauthorized = copy.deepcopy(r4)
    mirror = next(item for item in unauthorized["intents"] if item["intent_id"] == "MIRROR_SET_ANGLE")
    mirror["chinese_name"] = "未经批准的变更"
    candidate = tmp_path / "unauthorized_r4.yaml"
    BUILDER.write_yaml(candidate, unauthorized)

    result = VALIDATOR.validate(candidate)

    assert result["status"] == "FAIL"
    assert "intents.MIRROR_SET_ANGLE.chinese_name" in result["unauthorized_changed_paths"]


def test_strict_yaml_loader_rejects_duplicate_keys(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.yaml"
    duplicate.write_text("registry_version: one\nregistry_version: two\n", encoding="utf-8")

    try:
        VALIDATOR.load_yaml(duplicate)
    except Exception as exc:  # PyYAML exposes ConstructorError from the strict loader.
        assert "duplicate key" in str(exc)
    else:
        raise AssertionError("duplicate YAML keys must be rejected")
