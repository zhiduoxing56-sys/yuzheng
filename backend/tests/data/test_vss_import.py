from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from scripts import import_vss


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_PATH = PROJECT_ROOT / "data" / "standards" / "vss" / "6.0" / "source" / "vss.csv"
METADATA_PATH = SOURCE_PATH.with_name("metadata.json")
GENERATED_DIR = SOURCE_PATH.parents[1] / "generated"

RUNTIME_PROTECTED_FILES = (
    PROJECT_ROOT / "config" / "semantic_rules.yaml",
    PROJECT_ROOT / "证据" / "evidence_demand_registry_v1.yaml",
    PROJECT_ROOT / "config" / "safety_rules.yaml",
    PROJECT_ROOT / "config" / "vehicle_actions.yaml",
    PROJECT_ROOT / "config" / "authorization.yaml",
    PROJECT_ROOT / "backend" / "app" / "services" / "semantic" / "orchestrator.py",
    PROJECT_ROOT / "backend" / "app" / "models" / "schemas.py",
    PROJECT_ROOT / "backend" / "app" / "services" / "decision" / "safety_gate.py",
    PROJECT_ROOT / "backend" / "app" / "services" / "execution" / "service.py",
)
PERSISTENCE_CONTRACT_FILES = (
    PROJECT_ROOT / "docs" / "contracts" / "frontend-contract-v1" / "manifest.json",
    PROJECT_ROOT / "docs" / "contracts" / "frontend-contract-v1" / "openapi-public-v1.json",
    PROJECT_ROOT / "data" / "database" / "yuzheng.db",
)


def _load(name: str) -> dict:
    return json.loads((GENERATED_DIR / name).read_text(encoding="utf-8"))


def _digest(path: Path) -> tuple[int, str]:
    data = path.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def test_fixed_official_version_and_source_metadata() -> None:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    assert import_vss.SOURCE_VERSION == "VSS 6.0"
    assert metadata["upstream_project"] == "COVESA/vehicle_signal_specification"
    assert metadata["source_version"] == "VSS 6.0"
    assert metadata["release_tag"] == "v6.0"
    assert metadata["release_commit"] == "20c609b"
    assert metadata["source_url"] == import_vss.SOURCE_URL
    assert metadata["license"] == "MPL-2.0"
    assert len(metadata["sha256"]) == 64
    assert metadata["sha256"] == import_vss.EXPECTED_SOURCE_SHA256
    assert metadata["sha256"] == import_vss.sha256_file(SOURCE_PATH)
    assert metadata["file_size"] == import_vss.EXPECTED_SOURCE_FILE_SIZE
    assert metadata["file_size"] == SOURCE_PATH.stat().st_size


def test_raw_contains_only_all_actuators_and_preserves_paths() -> None:
    raw = _load("vss_actuators_raw.json")
    assert raw["source_version"] == "VSS 6.0"
    assert raw["record_count"] == 643
    assert all(item["type"].lower() == "actuator" for item in raw["records"])
    assert all(item["vss_path"] for item in raw["records"])
    assert all(item["source_fields"]["Signal"] == item["vss_path"] for item in raw["records"])
    assert sum(item["deprecated"] for item in raw["records"]) == 2


def test_normalized_excludes_deprecated_and_traces_to_raw() -> None:
    raw = _load("vss_actuators_raw.json")["records"]
    normalized = _load("vss_actuators_normalized.json")["records"]
    raw_by_path = {item["vss_path"]: item for item in raw}
    assert len(normalized) == 641
    assert all(item["deprecated"] is False for item in normalized)
    assert all(item["source_version"] == "VSS 6.0" for item in normalized)
    assert all(item["vss_path"] in raw_by_path for item in normalized)
    assert all(
        item["raw_ref"]["source_row_number"] == raw_by_path[item["vss_path"]]["source_row_number"]
        for item in normalized
    )


def test_candidates_are_one_to_one_and_trace_to_normalized() -> None:
    normalized = _load("vss_actuators_normalized.json")["records"]
    candidates = _load("vss_capability_candidates.json")["records"]
    normalized_paths = {item["vss_path"] for item in normalized}
    candidate_paths = [item["vss_path"] for item in candidates]
    assert len(candidates) == len(normalized)
    assert len(candidate_paths) == len(set(candidate_paths))
    assert set(candidate_paths) == normalized_paths
    assert all(item["normalized_ref"]["vss_path"] == item["vss_path"] for item in candidates)
    assert all(item["candidate_status"] == "CANDIDATE_ONLY_NOT_REGISTERED" for item in candidates)


def test_boolean_enum_and_numeric_constraints_are_preserved() -> None:
    normalized = {
        item["vss_path"]: item
        for item in _load("vss_actuators_normalized.json")["records"]
    }
    candidates = {
        item["vss_path"]: item
        for item in _load("vss_capability_candidates.json")["records"]
    }
    door = "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen"
    switch = "Vehicle.Cabin.Door.Row1.DriverSide.Switch"
    position = "Vehicle.Cabin.Door.Row1.DriverSide.Window.Position"
    assert candidates[door]["control_mode"] == "BOOLEAN"
    assert candidates[door]["parameters"]["value"]["boolean_semantic_mapping"] == "not_inferred"
    assert candidates[switch]["control_mode"] == "ENUM"
    assert normalized[switch]["constraints"]["allowed"] == [
        "INACTIVE",
        "CLOSE",
        "OPEN",
        "ONE_SHOT_CLOSE",
        "ONE_SHOT_OPEN",
    ]
    assert candidates[position]["control_mode"] == "NUMERIC"
    assert normalized[position]["unit"] == "percent"
    assert normalized[position]["constraints"]["min"] == 0
    assert normalized[position]["constraints"]["max"] == 100


def test_door_instances_and_multiple_doors_are_not_lost() -> None:
    candidates = {
        item["vss_path"]: item
        for item in _load("vss_capability_candidates.json")["records"]
    }
    driver = candidates["Vehicle.Cabin.Door.Row1.DriverSide.IsOpen"]
    passenger = candidates["Vehicle.Cabin.Door.Row1.PassengerSide.IsOpen"]
    rear_driver = candidates["Vehicle.Cabin.Door.Row2.DriverSide.IsOpen"]
    assert driver["domain"] == "Cabin"
    assert driver["component"] == "Door"
    assert driver["instance"] == "Row1.DriverSide"
    assert driver["property"] == "IsOpen"
    assert driver["candidate_capability"] == "door.open"
    assert driver["parameters"]["row"] == 1
    assert driver["parameters"]["side"] == "driver"
    assert passenger["candidate_id"] != driver["candidate_id"]
    assert rear_driver["candidate_id"] != driver["candidate_id"]
    assert rear_driver["parameters"]["row"] == 2


def test_required_manual_review_categories_and_sibling_conflicts() -> None:
    candidates = {
        item["vss_path"]: item
        for item in _load("vss_capability_candidates.json")["records"]
    }
    paths = (
        "Vehicle.MotionManagement.Steering.SteeringWheel.AngleTarget",
        "Vehicle.ADAS.CruiseControl.IsActive",
        "Vehicle.Powertrain.TractionBattery.BatteryConditioning.RequestedMode",
        "Vehicle.Cabin.Door.Row1.DriverSide.Switch",
        "Vehicle.Cabin.Door.Row1.DriverSide.IsOpen",
    )
    for path in paths:
        assert candidates[path]["manual_review_required"] is True
        assert candidates[path]["manual_review_reasons"]
    assert any(
        "兄弟节点" in reason
        for reason in candidates["Vehicle.Cabin.Door.Row1.DriverSide.IsOpen"]["manual_review_reasons"]
    )
    report = _load("vss_import_report.json")
    assert len(report["manual_review_items"]) == report["counts"]["manual_review_required"]
    assert all(item["manual_review_reasons"] for item in report["manual_review_items"])


def test_repeat_generation_is_byte_stable(tmp_path: Path) -> None:
    source = tmp_path / "source" / "vss.csv"
    metadata = source.with_name("metadata.json")
    output = tmp_path / "generated"
    source.parent.mkdir(parents=True)
    shutil.copyfile(SOURCE_PATH, source)
    shutil.copyfile(METADATA_PATH, metadata)
    import_vss.run_import(source, metadata, output, allow_download=False)
    first = {path.name: path.read_bytes() for path in output.iterdir()}
    import_vss.run_import(source, metadata, output, allow_download=False)
    second = {path.name: path.read_bytes() for path in output.iterdir()}
    assert first == second


def test_import_does_not_modify_runtime_config_or_control_code(tmp_path: Path) -> None:
    before = {path: _digest(path) for path in RUNTIME_PROTECTED_FILES}
    output = tmp_path / "generated"
    import_vss.run_import(SOURCE_PATH, METADATA_PATH, output, allow_download=False)
    after = {path: _digest(path) for path in RUNTIME_PROTECTED_FILES}
    assert before == after
    assert not any(
        path.name
        in {
            "semantic_rules.yaml",
            "evidence_demand_registry_v1.yaml",
            "safety_rules.yaml",
            "vehicle_actions.yaml",
            "authorization.yaml",
        }
        for path in output.rglob("*")
    )


def test_import_does_not_modify_database_or_frozen_contract(tmp_path: Path) -> None:
    before = {path: _digest(path) for path in PERSISTENCE_CONTRACT_FILES}
    import_vss.run_import(
        SOURCE_PATH,
        METADATA_PATH,
        tmp_path / "generated",
        allow_download=False,
    )
    after = {path: _digest(path) for path in PERSISTENCE_CONTRACT_FILES}
    assert before == after
