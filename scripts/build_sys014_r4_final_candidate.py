"""Build the approved SYS-014 R4 final semantic-consistency candidate."""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, changed_paths, sha256_file
from validate_sys014_r4_full_registry import CORE_PATH, CORE_SHA256, MAC_PATHS, R3_PATH, R3_SHA256, SOURCE_SCREEN_PATH

FULL_NLU_DIR = Path(__file__).resolve().parent / "full_nlu"
if str(FULL_NLU_DIR) not in sys.path:
    sys.path.insert(0, str(FULL_NLU_DIR))
from r4_final_candidate_evidence import (  # noqa: E402
    APPROVED_NEW_INTENT_IDS,
    AREA_FAMILIES,
    build_final_patch_evidence,
)
from r4_known_unsupported_evidence import extract_frames  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
FULL_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_full_draft.yaml"
FINAL_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_final_candidate.yaml"
AUDIT_DIR = ROOT / "data" / "nlu" / "spec" / "audits"
DIFF_PATH = AUDIT_DIR / "r4_full_to_final_diff.md"
VALIDATOR_RESULT_PATH = AUDIT_DIR / "r4_final_validator_result.json"

FULL_SHA256 = "393de4203c2cb93b0162724b336cb29a2cc67fba1c73b1cbc1fe62bb642f4f21"
FINAL_VERSION = "sys-014-semantic-hardening-r4-final-candidate"
FINAL_STATUS = "FINAL_CANDIDATE_PENDING_APPROVAL"
BUILD_VERSION = "sys014_r4_final_semantic_consistency_builder_v1"

VALUE_REQUIRED_INTENTS = {
    "AMBIENT_LIGHT_SET_BRIGHTNESS": "SOURCE_LEVEL_REQUIRED",
    "AMBIENT_LIGHT_SET_COLOR": "SOURCE_COLOR_REQUIRED",
    "ARMREST_SET_POSITION": "SOURCE_POSITION_REQUIRED",
    "DISPLAY_SET_BRIGHTNESS": "SOURCE_LEVEL_REQUIRED",
    "DISPLAY_SET_POSITION": "SOURCE_POSITION_REQUIRED",
    "FRAGRANCE_SET_LEVEL": "SOURCE_LEVEL_REQUIRED",
    "GLASS_ROOF_SET_TRANSPARENCY": "SOURCE_TRANSPARENCY_REQUIRED",
    "HVAC_SET_AIRFLOW_DIRECTION": "SOURCE_AIRFLOW_DIRECTION_REQUIRED",
    "HVAC_SET_FAN_SPEED": "SOURCE_LEVEL_REQUIRED",
    "HVAC_SET_TEMPERATURE": "SOURCE_TEMPERATURE_REQUIRED",
    "MEDIA_VOLUME_SET": "SOURCE_LEVEL_REQUIRED",
    "READING_LIGHT_SET_BRIGHTNESS": "SOURCE_LEVEL_REQUIRED",
    "REFRIGERATOR_SET_TEMPERATURE": "SOURCE_TEMPERATURE_REQUIRED",
    "SEAT_HEATING_SET_LEVEL": "SOURCE_LEVEL_REQUIRED",
    "SEAT_MASSAGE_SET_LEVEL": "SOURCE_LEVEL_REQUIRED",
    "SEAT_VENTILATION_SET_LEVEL": "SOURCE_LEVEL_REQUIRED",
}

NEW_INTENT_SEMANTICS = {
    "AIR_PURIFIER_SET_FAN_SPEED": {
        "chinese_name": "设置空气净化器风速", "family": "AIR_PURIFIER", "action": "SET", "target": "AIR_PURIFIER",
        "attribute": "FAN_SPEED", "value_contract": "SOURCE_LEVEL_REQUIRED", "required": ["VALUE"],
    },
    "DISPLAY_SET_MODE": {
        "chinese_name": "设置显示屏模式", "family": "DISPLAY", "action": "SWITCH_MODE", "target": "DISPLAY",
        "attribute": "MODE", "value_contract": "NONE", "required": ["MODE"], "mode_contract": "KNOWN_DISPLAY_SOURCE_MODE",
    },
    "READING_LIGHT_SET_MODE": {
        "chinese_name": "设置阅读灯模式", "family": "READING_LIGHT", "action": "SWITCH_MODE", "target": "READING_LIGHT",
        "attribute": "MODE", "value_contract": "NONE", "required": ["MODE"], "mode_contract": "KNOWN_READING_LIGHT_SOURCE_MODE",
    },
    "REFRIGERATOR_SET_MODE": {
        "chinese_name": "设置车载冰箱模式", "family": "REFRIGERATOR", "action": "SWITCH_MODE", "target": "REFRIGERATOR",
        "attribute": "MODE", "value_contract": "NONE", "required": ["MODE"], "mode_contract": "KNOWN_REFRIGERATOR_SOURCE_MODE",
    },
    "FRAGRANCE_SET_SCENT": {
        "chinese_name": "设置香氛香型", "family": "FRAGRANCE", "action": "SET", "target": "FRAGRANCE",
        "attribute": "SCENT", "value_contract": "SOURCE_SCENT_REQUIRED", "required": ["VALUE"],
    },
    "INTERIOR_LIGHT_SET_BRIGHTNESS": {
        "chinese_name": "设置车内灯亮度", "family": "INTERIOR_LIGHT", "action": "SET", "target": "INTERIOR_LIGHT",
        "attribute": "BRIGHTNESS", "value_contract": "SOURCE_LEVEL_REQUIRED", "required": ["VALUE"],
    },
    "INTERIOR_LIGHT_SET_COLOR": {
        "chinese_name": "设置车内灯颜色", "family": "INTERIOR_LIGHT", "action": "SET", "target": "INTERIOR_LIGHT",
        "attribute": "COLOR", "value_contract": "SOURCE_COLOR_REQUIRED", "required": ["VALUE"],
    },
    "INTERIOR_LIGHT_SET_MODE": {
        "chinese_name": "设置车内灯模式", "family": "INTERIOR_LIGHT", "action": "SWITCH_MODE", "target": "INTERIOR_LIGHT",
        "attribute": "MODE", "value_contract": "NONE", "required": ["MODE"], "mode_contract": "KNOWN_INTERIOR_LIGHT_SOURCE_MODE",
    },
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictSafeLoader)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def _required_contract(source: dict[str, Any], value_type: str | None = None) -> dict[str, Any]:
    contract = copy.deepcopy(source)
    contract["allowed"] = True
    contract["required"] = True
    if value_type:
        contract["type"] = value_type
    contract["valid_range"] = None
    contract["range_policy"] = "SOURCE_EXPLICIT_NO_GLOBAL_RANGE"
    contract["relative_value_policy"] = "RECOGNIZE_BUT_KEEP_UNRESOLVED_WITHOUT_PHYSICAL_MAGNITUDE"
    return contract


def _add_required_contracts(final: dict[str, Any]) -> None:
    contracts = final["value_contracts"]
    contracts["SOURCE_TEMPERATURE_REQUIRED"] = _required_contract(contracts["SOURCE_TEMPERATURE_OPTIONAL"])
    contracts["SOURCE_LEVEL_REQUIRED"] = _required_contract(contracts["SOURCE_LEVEL_OPTIONAL"])
    contracts["SOURCE_AIRFLOW_DIRECTION_REQUIRED"] = _required_contract(contracts["SOURCE_AIRFLOW_DIRECTION_OPTIONAL"])
    contracts["SOURCE_POSITION_REQUIRED"] = _required_contract(contracts["SOURCE_POSITION_OPTIONAL"])
    contracts["SOURCE_COLOR_REQUIRED"] = _required_contract(contracts["SOURCE_COLOR_OPTIONAL"])
    contracts["SOURCE_TRANSPARENCY_REQUIRED"] = _required_contract(
        contracts["SOURCE_LEVEL_OPTIONAL"], "TRANSPARENCY_OR_RELATIVE"
    )
    contracts["SOURCE_SCENT_REQUIRED"] = _required_contract(contracts["SOURCE_COLOR_OPTIONAL"], "SCENT_SOURCE_TEXT")


def _set_value_required(intent: dict[str, Any], contract: str) -> None:
    intent["value_contract"] = contract
    intent["required_slots"] = list(dict.fromkeys([*intent.get("required_slots", []), "VALUE"]))
    intent["optional_slots"] = [slot for slot in intent.get("optional_slots", []) if slot != "VALUE"]


def _new_intent(final: dict[str, Any], intent_id: str, evidence_index: int) -> dict[str, Any]:
    semantic = NEW_INTENT_SEMANTICS[intent_id]
    family_id = f"PROJECT_{semantic['family']}_KNOWN_CONTROL"
    family = next(item for item in final["capability_families"] if item["family_id"] == family_id)
    sibling = next(item for item in final["intents"] if item["intent_id"] == family["intents"][0])
    intent = {
        "intent_id": intent_id,
        "chinese_name": semantic["chinese_name"],
        "capability_family": family_id,
        "canonical_action": semantic["action"],
        "canonical_target": semantic["target"],
        "control_domain": sibling["control_domain"],
        "risk_level": sibling["risk_level"],
        "risk_tags": copy.deepcopy(sibling["risk_tags"]),
        "allowed_areas": [],
        "value_contract": semantic["value_contract"],
        "required_slots": list(semantic["required"]),
        "optional_slots": [],
        "scope_status": "IN_SCOPE",
        "capability_origin": "PROJECT_NATIVE",
        "vss_capability_ids": [],
        "vss_relation": "NONE",
        "scope_authority": "EXISTING_PROJECT_DESIGN",
        "control_attribute": semantic["attribute"],
        "user_voice_scope_status": "KNOWN_UNSUPPORTED_CONTROL",
        "source_evidence_ref": f"final_semantic_consistency_patch.approved_new_intents.{intent_id}",
    }
    if semantic.get("mode_contract"):
        intent["mode_contract"] = semantic["mode_contract"]
    family["intents"].append(intent_id)
    return intent


def _apply_family_areas(final: dict[str, Any], area_evidence: dict[str, Any]) -> None:
    by_id = {item["intent_id"]: item for item in final["intents"]}
    for family_key in AREA_FAMILIES:
        family_id = f"PROJECT_{family_key}_KNOWN_CONTROL"
        family = next(item for item in final["capability_families"] if item["family_id"] == family_id)
        allowed = list(area_evidence[family_key]["allowed_areas"])
        for intent_id in family["intents"]:
            intent = by_id[intent_id]
            intent["allowed_areas"] = allowed
            optional = [slot for slot in intent.get("optional_slots", []) if slot != "AREA"]
            if allowed:
                optional.append("AREA")
            intent["optional_slots"] = optional
    for intent_id in ("STEERING_WHEEL_HEATING_ON", "STEERING_WHEEL_HEATING_OFF"):
        intent = by_id[intent_id]
        intent["allowed_areas"] = []
        intent["optional_slots"] = [slot for slot in intent.get("optional_slots", []) if slot != "AREA"]


def _apply_guidance(final: dict[str, Any], evidence: dict[str, Any]) -> None:
    guidance = final["annotation_guidance"]
    guidance["version"] = "sys-014-r4-final-annotation-guidance-v1"
    guidance["registry_version"] = FINAL_VERSION
    frunk = guidance["trunk_frunk_hood_routing"]
    frunk["FRUNK"]["proven_operations"] = ["OPEN"]
    frunk["FRUNK"]["pending_operations"] = ["CLOSE"]
    frunk["frunk_close_status"] = "PENDING_NO_REAL_DATA_EVIDENCE"
    guidance["interior_lighting_lexical_boundary"] = {
        "READING_LIGHT": ["明确阅读灯"],
        "AMBIENT_LIGHT": ["明确氛围灯"],
        "INTERIOR_LIGHT": ["普通车内灯", "表面灯", "礼貌灯", "交互灯", "线条灯", "星空顶", "轮廓灯", "装饰灯", "顶灯"],
        "external_lighting_mapping_prohibited": ["HEADLIGHT", "LOW_BEAM", "HIGH_BEAM", "FOG_LIGHT", "PARKING_LIGHT"],
    }
    guidance["family_area_semantic_policy"] = {
        "policy": "RAW_MAC_FAMILY_LEVEL_UNION_AFTER_AREA_CATALOG_NORMALIZATION",
        "families": {family: evidence["family_area_evidence"][family]["allowed_areas"] for family in AREA_FAMILIES},
        "AREA_PENDING_REPORT": {
            family: evidence["family_area_evidence"][family]["pending"]
            for family in AREA_FAMILIES
            if evidence["family_area_evidence"][family]["pending"]
        },
        "unmapped_area_inference_prohibited": True,
    }
    guidance["media_sound_effect_mode_routing"] = {
        "accepted_modes": evidence["media_mode_evidence"]["mode_values"],
        "pending": evidence["media_mode_evidence"]["pending"],
        "non_media_source_inclusion_prohibited": True,
    }
    guidance["camera_mode_routing"] = {
        "accepted_modes": evidence["camera_mode_evidence"]["mode_values"],
        "camera_action_pending": evidence["camera_mode_evidence"]["camera_action_pending"],
        "automatic_camera_capture_intent_creation_prohibited": True,
    }


def _recompute(final: dict[str, Any]) -> None:
    intents = final["intents"]
    formal = [item["intent_id"] for item in intents if item.get("user_voice_scope_status") == "FORMAL_EXECUTABLE"]
    known = [item["intent_id"] for item in intents if item.get("user_voice_scope_status") == "KNOWN_UNSUPPORTED_CONTROL"]
    final["formal_user_voice_intent_ids"] = formal
    final["known_unsupported_control_intent_ids"] = known
    ontology = final["semantic_ontology"]
    ontology["canonical_actions"] = sorted({item["canonical_action"] for item in intents})
    ontology["canonical_targets"] = sorted({item["canonical_target"] for item in intents})
    ontology["control_attributes"] = sorted({item["control_attribute"] for item in intents})
    origins = Counter(item["capability_origin"] for item in intents)
    by_id = {item["intent_id"]: item for item in intents}
    project_families = sum(
        bool(family["intents"])
        and all(by_id[intent_id]["capability_origin"] == "PROJECT_NATIVE" for intent_id in family["intents"])
        for family in final["capability_families"]
    )
    final["statistics"].update({
        "intent_count": len(intents),
        "semantic_intent_count": len(intents),
        "formal_user_voice_intent_count": len(formal),
        "known_unsupported_control_intent_count": len(known),
        "project_native_intent_count": origins["PROJECT_NATIVE"],
        "vss_derived_intent_count": origins["VSS"] + origins["VSS_AND_PROJECT"],
        "capability_family_count": len(final["capability_families"]),
        "project_native_family_count": project_families,
        "legacy_test_only_intent_count": len(final.get("legacy_test_only", [])),
    })


def build_final_registry(full: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    final = copy.deepcopy(full)
    final["registry_version"] = FINAL_VERSION
    final["modified_date"] = "2026-08-10"
    final["semantic_freeze_status"] = FINAL_STATUS
    final["parent_registry"] = {
        "path": "data/nlu/spec/intent_registry_r4_full_draft.yaml",
        "registry_version": "sys-014-semantic-hardening-r4-full-draft",
        "sha256": FULL_SHA256,
        "inheritance_rule": "ONLY_APPLY_APPROVED_FINAL_SEMANTIC_CONSISTENCY_PATCH",
    }
    final["final_semantic_consistency_patch"] = {
        "version": BUILD_VERSION,
        "approved_new_intent_ids": APPROVED_NEW_INTENT_IDS,
        "approved_new_intents": evidence["approved_new_intents"],
        "source_policy": "ORIGINAL_MAC_FRAMES_ONLY",
        "formal_projection_frozen": True,
        "free_intent_discovery_prohibited": True,
        "data_remapping_expansion_training_performed": False,
    }

    _add_required_contracts(final)
    by_id = {item["intent_id"]: item for item in final["intents"]}
    for intent_id, contract in VALUE_REQUIRED_INTENTS.items():
        _set_value_required(by_id[intent_id], contract)

    for index, intent_id in enumerate(APPROVED_NEW_INTENT_IDS):
        item = _new_intent(final, intent_id, index)
        final["intents"].append(item)
        by_id[intent_id] = item

    for intent_id in APPROVED_NEW_INTENT_IDS:
        mode_contract = NEW_INTENT_SEMANTICS[intent_id].get("mode_contract")
        if mode_contract:
            modes = evidence["approved_new_intents"][intent_id]["source_mode_values"]
            if not modes:
                raise RuntimeError(f"{intent_id}: no real MODE evidence")
            final["mode_contracts"][mode_contract] = modes

    final["mode_contracts"]["KNOWN_MEDIA_SOURCE_MODE"] = evidence["media_mode_evidence"]["mode_values"]
    final["mode_contracts"]["KNOWN_CAMERA_SOURCE_MODE"] = evidence["camera_mode_evidence"]["mode_values"]
    by_id["DRIVING_MODE_SET"]["chinese_name"] = "设置驾驶模式"
    _apply_family_areas(final, evidence["family_area_evidence"])
    _apply_guidance(final, evidence)
    _recompute(final)
    return final


def _render_diff(full: dict[str, Any], final: dict[str, Any], validation: dict[str, Any], evidence: dict[str, Any]) -> str:
    paths = sorted(set(changed_paths(full, final)))
    lines = [
        "# R4 Full → Final Candidate Diff", "",
        f"- Full SHA256: `{FULL_SHA256}`",
        f"- Final SHA256: `{sha256_file(FINAL_PATH)}`",
        f"- Validator: **{validation['status']}**",
        f"- Intent count: **{full['statistics']['intent_count']} → {final['statistics']['intent_count']}**",
        f"- Known unsupported: **{full['statistics']['known_unsupported_control_intent_count']} → {final['statistics']['known_unsupported_control_intent_count']}**",
        f"- Formal intents: **{final['statistics']['formal_user_voice_intent_count']}（ID 与顺序冻结）**", "",
        "## Approved new intent IDs", "",
    ]
    for intent_id in APPROVED_NEW_INTENT_IDS:
        count = evidence["approved_new_intents"][intent_id]["unique_sample_count"]
        lines.append(f"- `{intent_id}` — raw MAC evidence: **{count}**")
    lines.extend(["", "## VALUE contract repairs", ""])
    lines.extend(f"- `{intent_id}` → `{contract}`; `VALUE` required" for intent_id, contract in VALUE_REQUIRED_INTENTS.items())
    lines.extend(["", "## Family AREA union", ""])
    for family in AREA_FAMILIES:
        item = evidence["family_area_evidence"][family]
        lines.append(f"- `{family}`: `{item['allowed_areas']}`; pending raw areas: **{len(item['pending'])}**")
    lines.extend([
        "", "## MODE cleanup", "",
        f"- MEDIA accepted modes: `{evidence['media_mode_evidence']['mode_values']}`",
        f"- MEDIA pending groups: **{len(evidence['media_mode_evidence']['pending'])}**",
        f"- CAMERA accepted modes: `{evidence['camera_mode_evidence']['mode_values']}`",
        f"- camera_action_pending samples: **{evidence['camera_mode_evidence']['camera_action_pending']['unique_sample_count']}**",
        "", "## Changed semantic paths", "",
    ])
    lines.extend(f"- `{path}`" for path in paths)
    lines.append("")
    return "\n".join(lines)


def build_artifacts() -> dict[str, Any]:
    if sha256_file(R3_PATH) != R3_SHA256:
        raise RuntimeError("R3 SHA256 mismatch")
    if sha256_file(CORE_PATH) != CORE_SHA256:
        raise RuntimeError("R4 core SHA256 mismatch")
    if sha256_file(FULL_PATH) != FULL_SHA256:
        raise RuntimeError("R4 full parent SHA256 mismatch")
    full = load_yaml(FULL_PATH)
    frames = extract_frames(MAC_PATHS, SOURCE_SCREEN_PATH)
    evidence = build_final_patch_evidence(frames, full["area_catalog"])
    final = build_final_registry(full, evidence)
    write_yaml(FINAL_PATH, final)

    from validate_sys014_r4_final_candidate import validate  # local import avoids build/validate cycle

    validation = validate(evidence=evidence)
    write_json(VALIDATOR_RESULT_PATH, validation)
    DIFF_PATH.write_text(_render_diff(full, final, validation, evidence), encoding="utf-8")
    return {
        "status": validation["status"],
        "r3_sha256": sha256_file(R3_PATH),
        "core_sha256": sha256_file(CORE_PATH),
        "full_sha256": sha256_file(FULL_PATH),
        "final_sha256": sha256_file(FINAL_PATH),
        "metrics": validation["metrics"],
        "errors": validation["errors"],
    }


def main() -> int:
    try:
        result = build_artifacts()
    except (OSError, ValueError, KeyError, RuntimeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
