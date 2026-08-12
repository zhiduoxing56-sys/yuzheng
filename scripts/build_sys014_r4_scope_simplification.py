"""Build the Full NLU R4 formal-only runtime scope candidate and archive."""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, changed_paths, sha256_file
from validate_sys014_r4_full_registry import CORE_PATH, CORE_SHA256, R3_PATH, R3_SHA256


ROOT = Path(__file__).resolve().parents[1]
FINAL_PARENT_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_final_candidate.yaml"
SIMPLIFIED_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_simplified_candidate.yaml"
ARCHIVE_PATH = ROOT / "data" / "nlu" / "spec" / "known_control_reference_archive_r4.yaml"
AUDIT_DIR = ROOT / "data" / "nlu" / "spec" / "audits"
DIFF_PATH = AUDIT_DIR / "r4_scope_simplification_diff.md"
VALIDATOR_PATH = AUDIT_DIR / "r4_scope_simplification_validator.json"

FULL_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_full_draft.yaml"
FULL_SHA256 = "393de4203c2cb93b0162724b336cb29a2cc67fba1c73b1cbc1fe62bb642f4f21"
FINAL_PARENT_SHA256 = "55bbb90780a969cb249f73833d7d34d9e464d99c65e1a6352ead15aa34db4440"
SIMPLIFIED_VERSION = "sys-014-semantic-hardening-r4-simplified-candidate"
SIMPLIFIED_STATUS = "DRAFT_PENDING_FINAL_SCOPE_REVIEW"
ARCHIVE_VERSION = "known-control-reference-archive-r4"
BUILD_VERSION = "sys014_r4_scope_simplification_builder_v1"

RUNTIME_SCOPES = ["FORMAL_EXECUTABLE", "KNOWN_CONTROL_BYPASS", "NON_CONTROL", "UNKNOWN_OOD"]


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


def _referenced_values(intents: list[dict[str, Any]], field: str, excluded: set[Any] | None = None) -> list[str]:
    excluded = excluded or set()
    return sorted({str(item[field]) for item in intents if item.get(field) not in excluded and item.get(field) is not None})


def build_archive(parent: dict[str, Any]) -> dict[str, Any]:
    known = [
        copy.deepcopy(item)
        for item in parent["intents"]
        if item.get("user_voice_scope_status") == "KNOWN_UNSUPPORTED_CONTROL"
    ]
    known_ids = {item["intent_id"] for item in known}
    family_snapshots = [
        copy.deepcopy(family)
        for family in parent["capability_families"]
        if known_ids & set(family.get("intents", []))
    ]

    def referenced_contracts(field: str, section: str, excluded: set[Any] | None = None) -> dict[str, Any]:
        names = _referenced_values(known, field, excluded)
        return {name: copy.deepcopy(parent[section][name]) for name in names}

    area_ids = sorted({area for item in known for area in item.get("allowed_areas", [])})
    archive = {
        "document_status": "REFERENCE_ARCHIVE_NOT_RUNTIME",
        "archive_version": ARCHIVE_VERSION,
        "created_date": "2026-08-10",
        "source_registry": {
            "path": "data/nlu/spec/intent_registry_r4_final_candidate.yaml",
            "registry_version": parent["registry_version"],
            "sha256": FINAL_PARENT_SHA256,
        },
        "usage_policy": {
            "provenance_and_future_expansion_reference_only": True,
            "model_label_space": False,
            "runtime_registry": False,
            "gold_precise_intent_mapping_authority": False,
            "automatic_taxonomy_reactivation_prohibited": True,
        },
        "archived_scope_status": "KNOWN_UNSUPPORTED_CONTROL",
        "archived_intent_count": len(known),
        "archived_intent_ids": [item["intent_id"] for item in known],
        "archived_intents": known,
        "supporting_reference_snapshot": {
            "capability_families": family_snapshots,
            "area_catalog": {area_id: copy.deepcopy(parent["area_catalog"][area_id]) for area_id in area_ids},
            "value_contracts": referenced_contracts("value_contract", "value_contracts", {None, "NONE"}),
            "mode_contracts": referenced_contracts("mode_contract", "mode_contracts"),
            "direction_contracts": referenced_contracts("direction_contract", "direction_contracts"),
            "conditional_slot_contracts": referenced_contracts("conditional_slot_contract", "conditional_slot_contracts"),
            "mode_mapping_contracts": referenced_contracts("mode_mapping_contract", "mode_mapping_contracts"),
            "value_mapping_contracts": referenced_contracts("value_mapping_contract", "value_mapping_contracts"),
            "semantic_ontology": copy.deepcopy(parent["semantic_ontology"]),
            "annotation_guidance": copy.deepcopy(parent["annotation_guidance"]),
            "known_unsupported_expansion": copy.deepcopy(parent.get("known_unsupported_expansion")),
            "final_semantic_consistency_patch": copy.deepcopy(parent.get("final_semantic_consistency_patch")),
        },
    }
    return archive


def _runtime_scope_contract() -> dict[str, Any]:
    return {
        "FORMAL_EXECUTABLE": {
            "definition_zh": "语证正式执行范围内的车辆控制指令；必须输出具体正式 Intent 与必要 slots。",
            "requires_intent_id": True,
            "formal_contract_completeness_check": "APPLY",
        },
        "KNOWN_CONTROL_BYPASS": {
            "definition_zh": "明确属于车辆、座舱或车机本地控制，但不属于 FORMAL_EXECUTABLE 的清楚指令。",
            "requires_intent_id": False,
            "requires_canonical_action": False,
            "requires_canonical_target": False,
            "requires_control_attribute": False,
            "requires_value": False,
            "requires_mode": False,
            "requires_area": False,
            "formal_contract_completeness_check": "SKIP",
        },
        "NON_CONTROL": {
            "definition_zh": "普通聊天、信息查询、音乐内容请求或其他非车辆控制表达。",
            "vehicle_control_evidence_required": False,
        },
        "UNKNOWN_OOD": {
            "definition_zh": "真正未知、域外或无法确认是否属于车辆控制的表达。",
            "vehicle_control_evidence_status": "UNKNOWN_OR_INSUFFICIENT",
        },
    }


def _routing_contract() -> dict[str, Any]:
    return {
        "FORMAL_EXECUTABLE": {
            "decision_route": "ENTER_YUZHENG_SAFETY_CHAIN",
            "execution_authorized_by_yuzheng": "CONDITIONAL_AFTER_SAFETY_AND_AUTHORIZATION",
            "route_target": "YUZHENG_FORMAL_EXECUTION_PIPELINE",
        },
        "KNOWN_CONTROL_BYPASS": {
            "decision_route": "PASS_BYPASS",
            "execution_authorized_by_yuzheng": False,
            "route_target": "NATIVE_COCKPIT_ASSISTANT",
        },
        "NON_CONTROL": {
            "decision_route": "PASS_NON_CONTROL",
            "execution_authorized_by_yuzheng": False,
        },
        "UNKNOWN_OOD": {
            "decision_route": "UNKNOWN_OOD",
            "execution_authorized_by_yuzheng": False,
        },
    }


def _multi_intent_schema() -> dict[str, Any]:
    return {
        "ordered_sub_intents_required": True,
        "per_sub_intent_scope_and_routing_required": True,
        "mixed_scope_allowed": True,
        "sentence_level_route_collapse_prohibited": True,
        "sub_intent_schema": {
            "required_fields": ["scope"],
            "scope_enum": RUNTIME_SCOPES,
            "conditional_requirements": {
                "FORMAL_EXECUTABLE": {
                    "required_fields": ["scope", "intent_id"],
                    "slot_fields": "AS_REQUIRED_BY_FORMAL_INTENT_CONTRACT",
                },
                "KNOWN_CONTROL_BYPASS": {
                    "required_fields": ["scope"],
                    "detailed_semantic_fields_required": [],
                    "detailed_semantic_fields_prohibited_as_MODEL_REQUIRED_LABELS": [
                        "intent_id", "canonical_action", "canonical_target", "control_attribute", "VALUE", "MODE", "AREA"
                    ],
                },
                "NON_CONTROL": {"required_fields": ["scope"]},
                "UNKNOWN_OOD": {"required_fields": ["scope"]},
            },
        },
        "mixed_example": {
            "utterance": "打开空调然后关闭近光灯",
            "sub_intents": [
                {"scope": "KNOWN_CONTROL_BYPASS"},
                {"scope": "FORMAL_EXECUTABLE", "intent_id": "LOW_BEAM_OFF"},
            ],
            "per_sub_intent_routes": [
                {"decision_route": "PASS_BYPASS", "route_target": "NATIVE_COCKPIT_ASSISTANT"},
                {"decision_route": "ENTER_YUZHENG_SAFETY_CHAIN", "route_target": "YUZHENG_FORMAL_EXECUTION_PIPELINE"},
            ],
        },
    }


def _simplify_frunk_guidance(guidance: dict[str, Any]) -> None:
    routing = guidance["trunk_frunk_hood_routing"]
    frunk = routing["FRUNK"]
    for key in ("proven_operations", "pending_operations"):
        frunk.pop(key, None)
    frunk["runtime_scope"] = "KNOWN_CONTROL_BYPASS"
    frunk["detailed_intent_assignment_prohibited"] = True
    for key in (
        "frunk_expansion_status", "deferred_candidate_intent_ids", "formal_user_voice_projection_prohibited",
        "prohibited_symmetric_expansion", "included_intent_ids", "frunk_close_status",
    ):
        routing.pop(key, None)


def _prune_formal_closure(simplified: dict[str, Any], formal: list[dict[str, Any]]) -> None:
    formal_ids = {item["intent_id"] for item in formal}
    simplified["capability_families"] = [
        {**copy.deepcopy(family), "intents": [intent_id for intent_id in family["intents"] if intent_id in formal_ids]}
        for family in simplified["capability_families"]
        if formal_ids & set(family["intents"])
    ]

    contract_sections = {
        "value_contract": ("value_contracts", {None, "NONE"}),
        "mode_contract": ("mode_contracts", set()),
        "direction_contract": ("direction_contracts", set()),
        "conditional_slot_contract": ("conditional_slot_contracts", set()),
        "mode_mapping_contract": ("mode_mapping_contracts", set()),
        "value_mapping_contract": ("value_mapping_contracts", set()),
    }
    for field, (section, excluded) in contract_sections.items():
        used = set(_referenced_values(formal, field, excluded))
        if section == "value_contracts" and "NONE" in simplified[section]:
            used.add("NONE")
        simplified[section] = {name: value for name, value in simplified[section].items() if name in used}

    value_semantics = simplified.get("value_language_semantics", {})
    if "continuous_numeric_contracts" in value_semantics:
        value_semantics["continuous_numeric_contracts"] = [
            name for name in value_semantics["continuous_numeric_contracts"] if name in simplified["value_contracts"]
        ]
    used_areas = {area for item in formal for area in item.get("allowed_areas", [])}
    simplified["area_catalog"] = {
        area_id: value for area_id, value in simplified["area_catalog"].items() if area_id in used_areas
    }
    audit = simplified.get("over_atomization_audit", {})
    audit["parameterized_instead_of_split"] = [
        item for item in audit.get("parameterized_instead_of_split", []) if item.get("intent_id") in formal_ids
    ]
    audit["deliberately_split_for_safety_semantics"] = [
        group for group in audit.get("deliberately_split_for_safety_semantics", []) if set(group) <= formal_ids
    ]
    simplified["risk_review_required_intents"] = [
        intent_id for intent_id in simplified.get("risk_review_required_intents", []) if intent_id in formal_ids
    ]


def _recompute_runtime_metadata(simplified: dict[str, Any], formal: list[dict[str, Any]], archive_count: int) -> None:
    ontology = simplified["semantic_ontology"]
    ontology["canonical_actions"] = sorted({item["canonical_action"] for item in formal})
    ontology["canonical_targets"] = sorted({item["canonical_target"] for item in formal})
    ontology["control_attributes"] = sorted({item["control_attribute"] for item in formal})
    origins = Counter(item["capability_origin"] for item in formal)
    by_id = {item["intent_id"]: item for item in formal}
    project_families = sum(
        all(by_id[intent_id]["capability_origin"] == "PROJECT_NATIVE" for intent_id in family["intents"])
        for family in simplified["capability_families"]
    )
    vss_families = sum(
        all(by_id[intent_id]["capability_origin"] in {"VSS", "VSS_AND_PROJECT"} for intent_id in family["intents"])
        for family in simplified["capability_families"]
    )
    stats = simplified["statistics"]
    stats.update({
        "intent_count": len(formal),
        "semantic_intent_count": len(formal),
        "runtime_intent_head_count": len(formal),
        "formal_user_voice_intent_count": len(formal),
        "known_unsupported_control_intent_count": 0,
        "known_control_bypass_scope_count": 1,
        "runtime_scope_count": len(RUNTIME_SCOPES),
        "archived_known_control_reference_count": archive_count,
        "capability_family_count": len(simplified["capability_families"]),
        "project_native_family_count": project_families,
        "vss_family_count": vss_families,
        "project_native_intent_count": origins["PROJECT_NATIVE"],
        "vss_derived_intent_count": origins["VSS"] + origins["VSS_AND_PROJECT"],
        "legacy_test_only_intent_count": len(simplified.get("legacy_test_only", [])),
        "out_of_scope_family_count": 0,
        "pending_scope_intent_count": 0,
    })


def build_simplified_registry(parent: dict[str, Any], archive_sha256: str, archive_count: int) -> dict[str, Any]:
    formal = [
        copy.deepcopy(item)
        for item in parent["intents"]
        if item.get("user_voice_scope_status") == "FORMAL_EXECUTABLE"
    ]
    simplified = copy.deepcopy(parent)
    simplified["document_status"] = "DRAFT_OFFLINE_NOT_RUNTIME"
    simplified["registry_version"] = SIMPLIFIED_VERSION
    simplified["modified_date"] = "2026-08-10"
    simplified["semantic_freeze_status"] = SIMPLIFIED_STATUS
    simplified["public_semantic_frame_change_required"] = True
    simplified["parent_registry"] = {
        "path": "data/nlu/spec/intent_registry_r4_final_candidate.yaml",
        "registry_version": parent["registry_version"],
        "sha256": FINAL_PARENT_SHA256,
        "inheritance_rule": "FREEZE_FORMAL_AND_REMOVE_DETAILED_KNOWN_CONTROL_FROM_RUNTIME_INTENT_HEAD",
    }
    simplified["scope_simplification"] = {
        "version": BUILD_VERSION,
        "architecture": "FORMAL_INTENT_HEAD_PLUS_UNIFIED_SCOPE_CLASSIFICATION",
        "removed_detailed_known_control_intent_count": archive_count,
        "reference_archive": {
            "path": "data/nlu/spec/known_control_reference_archive_r4.yaml",
            "sha256": archive_sha256,
            "archived_intent_count": archive_count,
            "runtime_loading_prohibited": True,
        },
        "data_remapping_performed": False,
        "training_performed": False,
        "data_expansion_performed": False,
        "known_taxonomy_refinement_performed": False,
    }
    simplified["intents"] = formal
    simplified["formal_user_voice_intent_ids"] = [item["intent_id"] for item in formal]
    simplified.pop("known_unsupported_control_intent_ids", None)
    simplified.pop("known_unsupported_expansion", None)
    simplified.pop("final_semantic_consistency_patch", None)

    simplified["enums"]["user_voice_scope_status"] = ["FORMAL_EXECUTABLE"]
    simplified["enums"]["runtime_scope"] = RUNTIME_SCOPES
    simplified["user_voice_scope_contract"] = _runtime_scope_contract()
    simplified["runtime_scope_routing"] = _routing_contract()
    simplified["formal_contract_completeness"] = {
        "applicable_scopes": ["FORMAL_EXECUTABLE"],
        "excluded_scopes": ["KNOWN_CONTROL_BYPASS", "NON_CONTROL", "UNKNOWN_OOD"],
        "known_control_bypass_slot_completeness_check": "SKIP",
    }
    simplified["gold_scope_mapping_policy"] = {
        "applies_to_future_gold_construction_only": True,
        "existing_data_remapped_by_this_change": False,
        "known_vehicle_control_not_formal_target": {"scope": "KNOWN_CONTROL_BYPASS"},
        "specific_intent_id_required": False,
        "original_mac_semantics_may_be_retained_as_provenance": True,
        "mac_object_mode_value_as_required_model_labels": False,
        "known_control_evidence_requirement": "RAW_TEXT_PLUS_MAC_SPLIT_SENS_PLUS_MAC_SEMANTICS_CLEAR_VEHICLE_CONTROL_EVIDENCE",
        "non_control_and_unknown_ood_must_remain_distinct": True,
    }
    simplified["multi_intent_schema"] = _multi_intent_schema()
    simplified["annotation_schema_compatibility"] = {
        **copy.deepcopy(simplified.get("annotation_schema_compatibility", {})),
        "runtime_scope_schema_embedded_in_registry": True,
        "existing_annotation_data_modified": False,
    }
    guidance = simplified["annotation_guidance"]
    guidance["version"] = "sys-014-r4-simplified-annotation-guidance-v1"
    guidance["registry_version"] = SIMPLIFIED_VERSION
    for key in (
        "interior_lighting_lexical_boundary", "family_area_semantic_policy",
        "media_sound_effect_mode_routing", "camera_mode_routing",
    ):
        guidance.pop(key, None)
    _simplify_frunk_guidance(guidance)
    simplified["known_control_bypass_definition"] = {
        "definition_zh": "明确属于车辆、座舱或车机本地控制，但不属于 FORMAL_EXECUTABLE Intent 的清楚指令。",
        "examples_non_exhaustive": [
            "空调", "阅读灯", "车内灯", "氛围灯", "座椅加热", "座椅通风", "座椅按摩", "屏幕", "遮阳帘",
            "香氛", "方向盘加热", "冰箱", "空气净化", "蓝牙", "热点", "驾驶模式", "ADAS设置", "其他明确车辆本地设置",
        ],
        "examples_must_not_be_split_into_runtime_intents": True,
        "high_confidence_known_vehicle_control_evidence_required": True,
    }

    _prune_formal_closure(simplified, formal)
    _recompute_runtime_metadata(simplified, formal, archive_count)
    return simplified


def _render_diff(parent: dict[str, Any], simplified: dict[str, Any], archive: dict[str, Any], validation: dict[str, Any]) -> str:
    lines = [
        "# R4 Scope Simplification Diff", "",
        f"- Parent final candidate SHA256: `{FINAL_PARENT_SHA256}`",
        f"- Simplified candidate SHA256: `{sha256_file(SIMPLIFIED_PATH)}`",
        f"- Known-control archive SHA256: `{sha256_file(ARCHIVE_PATH)}`",
        f"- Validator: **{validation['status']}**", "",
        "## Required outcome report", "",
        f"1. FORMAL_EXECUTABLE 完全未变：**{validation['required_outcomes']['formal_executable_completely_unchanged']}**",
        f"2. 移出运行 Intent 空间的 Known Unsupported：**{validation['required_outcomes']['known_unsupported_removed_count']}**",
        f"3. Archive 数量：**{validation['required_outcomes']['archive_count']}**",
        f"4. 运行 Intent Head 已无 KNOWN_UNSUPPORTED_CONTROL：**{validation['required_outcomes']['all_known_unsupported_removed_from_runtime_intent_head']}**",
        f"5. 已新增统一 KNOWN_CONTROL_BYPASS scope：**{validation['required_outcomes']['known_control_bypass_scope_present']}**",
        f"6. NON_CONTROL / UNKNOWN_OOD 仍分离：**{validation['required_outcomes']['non_control_unknown_ood_distinct']}**",
        f"7. 多意图允许 FORMAL + BYPASS 混合：**{validation['required_outcomes']['mixed_formal_bypass_multi_intent_allowed']}**", "",
        "## Runtime projection", "",
        f"- Intent head: **{len(parent['intents'])} → {len(simplified['intents'])}**",
        f"- Capability families: **{len(parent['capability_families'])} → {len(simplified['capability_families'])}**",
        f"- Archived detailed KNOWN definitions: **{archive['archived_intent_count']}**", "",
        "## Scope routing", "",
        "- `FORMAL_EXECUTABLE` → precise Intent + formal safety chain",
        "- `KNOWN_CONTROL_BYPASS` → `PASS_BYPASS`, no Yuzheng authorization, target `NATIVE_COCKPIT_ASSISTANT`",
        "- `NON_CONTROL` and `UNKNOWN_OOD` remain separate scopes", "",
        "## Changed paths", "",
    ]
    lines.extend(f"- `{path}`" for path in sorted(set(changed_paths(parent, simplified))))
    lines.append("")
    return "\n".join(lines)


def build_artifacts() -> dict[str, Any]:
    if sha256_file(R3_PATH) != R3_SHA256:
        raise RuntimeError("R3 SHA256 mismatch")
    if sha256_file(CORE_PATH) != CORE_SHA256:
        raise RuntimeError("R4 core SHA256 mismatch")
    if sha256_file(FULL_PATH) != FULL_SHA256:
        raise RuntimeError("R4 full SHA256 mismatch")
    if sha256_file(FINAL_PARENT_PATH) != FINAL_PARENT_SHA256:
        raise RuntimeError("R4 final candidate parent SHA256 mismatch")

    parent = load_yaml(FINAL_PARENT_PATH)
    archive = build_archive(parent)
    write_yaml(ARCHIVE_PATH, archive)
    archive_hash = sha256_file(ARCHIVE_PATH)
    simplified = build_simplified_registry(parent, archive_hash, archive["archived_intent_count"])
    write_yaml(SIMPLIFIED_PATH, simplified)

    from validate_sys014_r4_scope_simplification import validate

    validation = validate()
    write_json(VALIDATOR_PATH, validation)
    DIFF_PATH.write_text(_render_diff(parent, simplified, archive, validation), encoding="utf-8")
    return {
        "status": validation["status"],
        "r3_sha256": sha256_file(R3_PATH),
        "core_sha256": sha256_file(CORE_PATH),
        "full_sha256": sha256_file(FULL_PATH),
        "final_parent_sha256": sha256_file(FINAL_PARENT_PATH),
        "simplified_sha256": sha256_file(SIMPLIFIED_PATH),
        "archive_sha256": archive_hash,
        "metrics": validation.get("metrics", {}),
        "required_outcomes": validation.get("required_outcomes", {}),
        "errors": validation.get("errors", []),
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
