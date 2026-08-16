from __future__ import annotations

from pathlib import Path

from app.core.config import PROJECT_ROOT
from app.services.evidence.catalog import (
    CANONICAL_EVIDENCE_TYPES,
    evidence_runtime_mapping,
    evidence_type_catalog,
)


NEW_MOTHER_TYPES = {
    "VEHICLE_ACCELERATION",
    "HVAC_STATE",
    "ROAD_STRUCTURE_STATE",
    "COLLISION_ASSIST_STATE",
    "LANE_ASSIST_STATE",
    "DRIVER_MONITORING_STATE",
}
MAPPING_KINDS = {"DIRECT_STANDARD", "DERIVED", "INTERNAL_SECURITY"}
EIGHT_REGIONS = {
    "FRONT",
    "FRONT_LEFT",
    "FRONT_RIGHT",
    "LEFT",
    "RIGHT",
    "REAR_LEFT",
    "REAR_RIGHT",
    "REAR",
}


def _fields(mapping: dict, evidence_type: str) -> set[str]:
    return set(mapping[evidence_type]["value_schema"].get("fields", {}))


def test_evidence_space_v1_is_one_38_type_canonical_namespace() -> None:
    catalog = evidence_type_catalog()
    mapping = evidence_runtime_mapping()

    assert len(catalog) == len(mapping) == len(CANONICAL_EVIDENCE_TYPES) == 38
    assert set(catalog) == set(mapping) == CANONICAL_EVIDENCE_TYPES
    assert NEW_MOTHER_TYPES <= CANONICAL_EVIDENCE_TYPES
    assert not any(name.startswith("STANDARD_") or name.endswith("_V2") for name in catalog)


def test_every_final_runtime_field_has_explicit_source_nature() -> None:
    mapping = evidence_runtime_mapping()
    observed_kinds = {
        provenance["mapping_kind"]
        for entry in mapping.values()
        for provenance in entry["field_provenance"].values()
    }

    assert observed_kinds == MAPPING_KINDS
    for evidence_type, entry in mapping.items():
        for field_name, provenance in entry["field_provenance"].items():
            if provenance["mapping_kind"] != "DIRECT_STANDARD":
                continue
            source = provenance.get("local_source_file")
            assert source, f"{evidence_type}.{field_name} has no local standard source"
            assert (PROJECT_ROOT / source).is_file(), source


def test_surrounding_direction_and_risk_are_derived_parameters() -> None:
    mapping = evidence_runtime_mapping()
    surrounding = mapping["SURROUNDING_OBJECT_STATE"]
    provenance = surrounding["field_provenance"]

    assert provenance["objects[].region"]["mapping_kind"] == "DERIVED"
    assert set(provenance["objects[].region"]["allowed_values"]) == EIGHT_REGIONS
    assert provenance["objects[].risk_level"]["mapping_kind"] == "DERIVED"
    assert not any(region in CANONICAL_EVIDENCE_TYPES for region in EIGHT_REGIONS)
    assert {"CAMERA", "RADAR", "LIDAR", "ULTRASONIC"}.isdisjoint(
        CANONICAL_EVIDENCE_TYPES
    )


def test_required_vehicle_safety_scenarios_are_expressible() -> None:
    mapping = evidence_runtime_mapping()

    # BRAKE: service brake, motion, adhesion, parking brake and gear.
    assert {
        "SERVICE_BRAKE_STATE",
        "VEHICLE_SPEED",
        "ROAD_FRICTION_STATE",
        "PARKING_BRAKE_STATE",
        "GEAR_STATE",
    } <= set(mapping)
    assert {"engaged"} <= _fields(mapping, "PARKING_BRAKE_STATE")
    assert {"current_gear"} <= _fields(mapping, "GEAR_STATE")
    assert {"friction_scale_factor", "wetness"} <= _fields(
        mapping, "ROAD_FRICTION_STATE"
    )

    # DOOR_OPEN RIGHT_REAR: parameterized door and object facts.
    assert {"area", "is_open", "state", "position"} <= _fields(mapping, "DOOR_STATE")
    object_fields = set(
        mapping["SURROUNDING_OBJECT_STATE"]["value_schema"]["fields"]["objects"][
            "items"
        ]["fields"]
    )
    assert {
        "entity_kind",
        "region",
        "distance",
        "relative_speed",
        "motion_state",
    } <= object_fields

    # HEADLIGHT OFF and WIPER retain KnowledgeNode mother-type references.
    assert {"headlight_state", "low_beam_on", "high_beam_on"} <= _fields(
        mapping, "LIGHTING_STATE"
    )
    assert {"ambient_illumination", "visibility", "precipitation"} <= _fields(
        mapping, "ENVIRONMENT_CONDITIONS"
    )
    assert {"mode", "intensity", "frequency", "wiping"} <= _fields(
        mapping, "WIPER_STATE"
    )


def test_common_evidence_quality_is_an_envelope_not_parallel_types() -> None:
    import yaml

    runtime_path = PROJECT_ROOT / "证据" / "evidence_runtime_mapping_v1.yaml"
    raw = yaml.safe_load(runtime_path.read_text(encoding="utf-8"))
    envelope = raw["common_evidence_envelope"]

    assert set(envelope["value_schema"]) == {
        "timestamp",
        "freshness",
        "validity",
        "confidence",
        "conflict_status",
        "availability",
    }
    assert set(envelope["field_provenance"]) == set(envelope["value_schema"])
    assert "EVIDENCE_QUALITY" not in CANONICAL_EVIDENCE_TYPES


def test_generated_capability_matrix_exists_and_contains_all_sources() -> None:
    report = (PROJECT_ROOT / "证据" / "evidence_standard_mapping.md").read_text(
        encoding="utf-8"
    )
    for standard in (
        "COVESA VSS 6.0",
        "ASAM OSI 3.8.0",
        "ASAM OpenSCENARIO XML 1.4.0",
        "ASAM OpenDRIVE 1.9.0",
        "Android Automotive VHAL",
    ):
        assert standard in report
    assert "Evidence Capability Matrix" in report
    assert "32/38" in report
