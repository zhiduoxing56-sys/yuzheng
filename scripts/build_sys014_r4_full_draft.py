"""Build the evidence-backed SYS-014 R4 full known-unsupported draft."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, changed_paths, sha256_file
from validate_sys014_r4_full_registry import (
    ADAS_REPORT_PATH,
    AUDIT_DIR,
    CORE_PATH,
    CORE_SHA256,
    EXPANSION_REPORT_PATH,
    FULL_PATH,
    FULL_STATUS,
    FULL_VERSION,
    MAC_PATHS,
    OTHER_REPORT_PATH,
    R3_PATH,
    R3_SHA256,
    SOURCE_SCREEN_PATH,
    validate,
)

FULL_NLU_DIR = Path(__file__).resolve().parent / "full_nlu"
if str(FULL_NLU_DIR) not in sys.path:
    sys.path.insert(0, str(FULL_NLU_DIR))
from r4_known_unsupported_evidence import build_evidence, extract_frames, sha256_file as evidence_sha256  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
EXPANSION_REPORT_MD_PATH = AUDIT_DIR / "r4_known_unsupported_expansion_report_v1.md"
ADAS_REPORT_MD_PATH = AUDIT_DIR / "known_unsupported_adas_candidates_v1.md"
OTHER_REPORT_MD_PATH = AUDIT_DIR / "known_unsupported_other_candidates_v1.md"
VALIDATOR_RESULT_PATH = AUDIT_DIR / "r4_full_validator_result.json"
DIFF_MD_PATH = AUDIT_DIR / "r4_core_to_full_diff.md"
DIFF_JSON_PATH = AUDIT_DIR / "r4_core_to_full_diff.json"
BUILD_VERSION = "sys014_r4_full_known_unsupported_builder_v1"

SOURCE_HASHES = {
    "initial_screen/full_nlu_source_screen_v1.jsonl": "59340fce2c394cb793a37ba2b301379f4ef9794c9301d0983c6b37680e09123c",
    "train_set.jsonl": "d1e9a63fa61ef2d5eec4ef543356fb53d653070916c5ceaf72962047f9aef681",
    "dev_set.jsonl": "02ccb2bae0fa1923fb0e3bcdd5d0c13635ac93cfd2880d8a8affd0481157efb1",
    "test_set.jsonl": "1b3e8243ea9a9bb544a18b571401c4a057f0246c07d26a3e2a638890d9300572",
}

TARGET_LABELS = {
    "FRUNK": "前备箱", "HVAC": "空调", "SEAT_HEATING": "座椅加热", "SEAT_VENTILATION": "座椅通风",
    "SEAT_MASSAGE": "座椅按摩", "READING_LIGHT": "阅读灯", "INTERIOR_LIGHT": "车内灯",
    "AMBIENT_LIGHT": "氛围灯", "SHADE": "遮阳帘", "DISPLAY": "显示屏", "FRAGRANCE": "香氛",
    "STEERING_WHEEL": "方向盘加热", "ARMREST": "扶手", "REFRIGERATOR": "车载冰箱",
    "AIR_PURIFIER": "空气净化器", "GLASS_ROOF": "玻璃天幕", "MEDIA": "车载媒体",
    "BLUETOOTH": "蓝牙", "HOTSPOT": "热点", "CHILD_LOCK": "儿童锁", "CAMERA": "车载摄像头",
    "DRIVING_RECORDER": "行车记录仪", "DRIVING_MODE": "驾驶模式",
}

AREA_ALIASES = {
    "主驾": "LEFT_FRONT", "主驾驶": "LEFT_FRONT", "主驾驶位": "LEFT_FRONT", "驾驶位": "LEFT_FRONT", "左前": "LEFT_FRONT",
    "副驾": "RIGHT_FRONT", "副驾驶": "RIGHT_FRONT", "副驾驶位": "RIGHT_FRONT", "右前": "RIGHT_FRONT",
    "左后": "LEFT_REAR", "左后排": "LEFT_REAR", "右后": "RIGHT_REAR", "右后排": "RIGHT_REAR",
    "前排": "FRONT_ROW", "主副驾": "FRONT_ROW", "主副驾驶": "FRONT_ROW", "后排": "REAR_ROW", "后座": "REAR_ROW", "第二排": "REAR_ROW",
    "左侧": "LEFT_SIDE", "左边": "LEFT_SIDE", "右侧": "RIGHT_SIDE", "右边": "RIGHT_SIDE",
    "全部": "ALL", "所有": "ALL", "全车": "ALL", "整车": "ALL", "all": "ALL",
    "前": "FRONT", "前面": "FRONT", "前部": "FRONT", "后": "REAR", "后面": "REAR", "后部": "REAR", "后舱": "REAR",
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


def _family_key(intent_id: str) -> str:
    for prefix in (
        "STEERING_WHEEL_HEATING", "GLASS_ROOF", "DRIVING_RECORDER", "SEAT_VENTILATION", "SEAT_HEATING",
        "SEAT_MASSAGE", "AIR_PURIFIER", "READING_LIGHT", "INTERIOR_LIGHT", "AMBIENT_LIGHT",
        "DRIVING_MODE", "REFRIGERATOR", "BLUETOOTH", "CHILD_LOCK", "FRAGRANCE", "HOTSPOT",
        "CAMERA", "DISPLAY", "ARMREST", "FRUNK", "HVAC", "SHADE", "MEDIA",
    ):
        if intent_id.startswith(prefix):
            return prefix
    raise ValueError(f"unsupported approved intent ID: {intent_id}")


def _target_for_family(family_key: str) -> str:
    return "STEERING_WHEEL" if family_key == "STEERING_WHEEL_HEATING" else family_key


def _semantic_contract(intent_id: str, family_key: str) -> dict[str, Any]:
    target = _target_for_family(family_key)
    if intent_id == "FRUNK_OPEN":
        return {"action": "OPEN", "target": "FRUNK", "attribute": "OPENING_STATE", "value_contract": "NONE"}
    if intent_id == "SHADE_OPEN":
        return {"action": "OPEN", "target": "SHADE", "attribute": "OPENING_STATE", "value_contract": "NONE"}
    if intent_id == "SHADE_CLOSE":
        return {"action": "CLOSE", "target": "SHADE", "attribute": "OPENING_STATE", "value_contract": "NONE"}
    if intent_id.endswith("_ON"):
        attribute = "HEATING_STATE" if family_key == "STEERING_WHEEL_HEATING" else "STATE"
        return {"action": "TURN_ON", "target": target, "attribute": attribute, "value_contract": "NONE"}
    if intent_id.endswith("_OFF"):
        attribute = "HEATING_STATE" if family_key == "STEERING_WHEEL_HEATING" else "STATE"
        return {"action": "TURN_OFF", "target": target, "attribute": attribute, "value_contract": "NONE"}
    if intent_id.endswith("_SET_TEMPERATURE"):
        return {"action": "SET", "target": target, "attribute": "TEMPERATURE", "value_contract": "SOURCE_TEMPERATURE_OPTIONAL", "optional": ["VALUE"]}
    if intent_id.endswith("_SET_FAN_SPEED"):
        return {"action": "SET", "target": target, "attribute": "FAN_SPEED", "value_contract": "SOURCE_LEVEL_OPTIONAL", "optional": ["VALUE"]}
    if intent_id.endswith("_SET_AIRFLOW_DIRECTION"):
        return {"action": "SET", "target": target, "attribute": "AIRFLOW_DIRECTION", "value_contract": "SOURCE_AIRFLOW_DIRECTION_OPTIONAL", "optional": ["VALUE"]}
    if intent_id.endswith("_SET_LEVEL") or intent_id == "MEDIA_VOLUME_SET":
        attribute = "VOLUME" if intent_id == "MEDIA_VOLUME_SET" else "LEVEL"
        return {"action": "SET", "target": target, "attribute": attribute, "value_contract": "SOURCE_LEVEL_OPTIONAL", "optional": ["VALUE"]}
    if intent_id.endswith("_SET_BRIGHTNESS"):
        return {"action": "SET", "target": target, "attribute": "BRIGHTNESS", "value_contract": "SOURCE_LEVEL_OPTIONAL", "optional": ["VALUE"]}
    if intent_id.endswith("_SET_COLOR"):
        return {"action": "SET", "target": target, "attribute": "COLOR", "value_contract": "SOURCE_COLOR_OPTIONAL", "optional": ["VALUE"]}
    if intent_id.endswith("_SET_POSITION"):
        if intent_id == "SHADE_SET_POSITION":
            return {"action": "ADJUST", "target": target, "attribute": "POSITION", "value_contract": "PERCENT_0_100_REQUIRED", "required": ["VALUE"]}
        return {"action": "ADJUST", "target": target, "attribute": "POSITION", "value_contract": "SOURCE_POSITION_OPTIONAL", "optional": ["VALUE"]}
    if intent_id.endswith("_SET_TRANSPARENCY"):
        return {"action": "SET", "target": target, "attribute": "TRANSPARENCY", "value_contract": "PERCENT_0_100_OPTIONAL", "optional": ["VALUE"]}
    if intent_id.endswith("_SET_MODE") or intent_id in {"MEDIA_SOUND_EFFECT_SET", "DRIVING_MODE_SET"}:
        attribute = "SOUND_EFFECT" if intent_id == "MEDIA_SOUND_EFFECT_SET" else "MODE"
        return {"action": "SWITCH_MODE", "target": target, "attribute": attribute, "value_contract": "NONE", "required": ["MODE"], "mode": True}
    raise ValueError(f"missing semantic contract for {intent_id}")


def _chinese_name(contract: dict[str, Any], intent_id: str) -> str:
    target = TARGET_LABELS[contract["target"]]
    attribute_labels = {
        "STATE": "状态", "HEATING_STATE": "加热状态", "TEMPERATURE": "温度", "FAN_SPEED": "风量",
        "AIRFLOW_DIRECTION": "风向", "LEVEL": "档位", "VOLUME": "音量", "BRIGHTNESS": "亮度",
        "COLOR": "颜色", "POSITION": "位置", "TRANSPARENCY": "透光度", "MODE": "模式", "SOUND_EFFECT": "音效",
    }
    if contract["action"] in {"OPEN", "TURN_ON"}:
        return f"开启{target}"
    if contract["action"] in {"CLOSE", "TURN_OFF"}:
        return f"关闭{target}"
    return f"设置{target}{attribute_labels[contract['attribute']]}"


def _evidence_areas(evidence: dict[str, Any]) -> list[str]:
    values: set[str] = set()
    for example in evidence.get("examples", []):
        for slot in example.get("mac_frame", []):
            if slot.get("name") != "位置":
                continue
            raw = str(slot.get("value", "")).strip().rstrip("的")
            if raw in AREA_ALIASES:
                values.add(AREA_ALIASES[raw])
    order = ["LEFT_FRONT", "RIGHT_FRONT", "LEFT_REAR", "RIGHT_REAR", "FRONT_ROW", "REAR_ROW", "LEFT_SIDE", "RIGHT_SIDE", "ALL", "FRONT", "REAR"]
    return [area for area in order if area in values]


def _risk(family_key: str) -> tuple[str, list[str], str]:
    if family_key in {"FRUNK", "CHILD_LOCK", "DRIVING_MODE"}:
        return "R3", ["未开放控制", "安全边界"], "车身控制"
    if family_key in {"MEDIA", "BLUETOOTH", "HOTSPOT", "CAMERA", "DRIVING_RECORDER", "DISPLAY"}:
        return "R1", ["未开放控制", "本地设备设置"], "座舱控制"
    return "R2", ["未开放控制", "座舱舒适"], "座舱控制"


def _new_value_contracts() -> dict[str, dict[str, Any]]:
    def contract(value_type: str, unit: str) -> dict[str, Any]:
        return {
            "allowed": True,
            "required": False,
            "type": value_type,
            "canonical_unit": unit,
            "valid_range": None,
            "enum_values": [],
            "range_policy": "SOURCE_EXPLICIT_NO_GLOBAL_RANGE",
            "relative_value_policy": "RECOGNIZE_BUT_KEEP_UNRESOLVED_WITHOUT_PHYSICAL_MAGNITUDE",
        }
    return {
        "SOURCE_TEMPERATURE_OPTIONAL": contract("TEMPERATURE_OR_RELATIVE", "degC_when_explicit"),
        "SOURCE_LEVEL_OPTIONAL": contract("LEVEL_OR_RELATIVE", "source_defined"),
        "SOURCE_AIRFLOW_DIRECTION_OPTIONAL": contract("AIRFLOW_DIRECTION_SOURCE_TEXT", "source_defined"),
        "SOURCE_POSITION_OPTIONAL": contract("POSITION_OR_RELATIVE", "source_defined"),
        "SOURCE_COLOR_OPTIONAL": contract("COLOR_SOURCE_TEXT", "source_defined"),
    }


def build_registry(core: dict[str, Any], evidence: dict[str, Any], source_hashes: dict[str, str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    full = copy.deepcopy(core)
    full["document_status"] = "DRAFT_OFFLINE_NOT_RUNTIME"
    full["registry_version"] = FULL_VERSION
    full["modified_date"] = "2026-08-10"
    full["semantic_freeze_status"] = FULL_STATUS
    full["parent_registry"] = {
        "path": "data/nlu/spec/intent_registry_r4_core_draft.yaml",
        "registry_version": "sys-014-semantic-hardening-r4-core-draft",
        "sha256": CORE_SHA256,
        "inheritance_rule": "PRESERVE_CORE_AND_APPEND_EVIDENCE_BACKED_KNOWN_UNSUPPORTED_ONLY",
    }
    full["known_unsupported_expansion"] = {
        "version": "r4-known-unsupported-expansion-v1",
        "evidence_priority": ["RAW_QUERY", "MAC_SPLIT_SENS", "MAC_VEHICLE_CONTROL_FRAME", "R4_CORE", "LEGACY_BASELINE"],
        "baseline_used_as_semantic_truth": False,
        "source_sha256": source_hashes,
        "all_new_intents_scope": "KNOWN_UNSUPPORTED_CONTROL",
        "formal_projection_frozen": True,
        "no_data_remapping_or_training": True,
    }

    del full["value_contracts"]["FOLLOWING_GAP_REQUIRED"]
    full["value_language_semantics"]["continuous_numeric_contracts"].remove("FOLLOWING_GAP_REQUIRED")
    for name, contract in _new_value_contracts().items():
        full["value_contracts"][name] = contract
        full["value_language_semantics"]["continuous_numeric_contracts"].append(name)

    new_intents: list[dict[str, Any]] = []
    family_members: dict[str, list[str]] = defaultdict(list)
    intent_reports: list[dict[str, Any]] = []
    for intent_id, item_evidence in evidence["approved"].items():
        family_key = _family_key(intent_id)
        semantic = _semantic_contract(intent_id, family_key)
        family_id = f"PROJECT_{family_key}_KNOWN_CONTROL"
        risk_level, risk_tags, domain = _risk(family_key)
        allowed_areas = _evidence_areas(item_evidence)
        required = list(semantic.get("required", []))
        optional = list(semantic.get("optional", []))
        if allowed_areas:
            optional.append("AREA")
        intent = {
            "intent_id": intent_id,
            "chinese_name": _chinese_name(semantic, intent_id),
            "capability_family": family_id,
            "canonical_action": semantic["action"],
            "canonical_target": semantic["target"],
            "control_domain": domain,
            "risk_level": risk_level,
            "risk_tags": risk_tags,
            "allowed_areas": allowed_areas,
            "value_contract": semantic["value_contract"],
            "required_slots": required,
            "optional_slots": optional,
            "scope_status": "IN_SCOPE",
            "capability_origin": "PROJECT_NATIVE",
            "vss_capability_ids": [],
            "vss_relation": "NONE",
            "scope_authority": "EXISTING_PROJECT_DESIGN",
            "control_attribute": semantic["attribute"],
            "user_voice_scope_status": "KNOWN_UNSUPPORTED_CONTROL",
            "source_evidence_ref": f"r4_known_unsupported_expansion_report_v1.json#new_intents/{len(intent_reports)}",
        }
        if semantic.get("mode"):
            mode_values = item_evidence.get("source_mode_values", [])
            if not mode_values:
                raise RuntimeError(f"{intent_id}: no real source MODE values")
            mode_contract = f"KNOWN_{family_key}_SOURCE_MODE"
            existing = full["mode_contracts"].get(mode_contract)
            merged = sorted(set((existing or []) + mode_values))
            full["mode_contracts"][mode_contract] = merged
            intent["mode_contract"] = mode_contract
        new_intents.append(intent)
        family_members[family_id].append(intent_id)
        intent_reports.append({
            **item_evidence,
            "capability_family": family_id,
            "canonical_action": semantic["action"],
            "canonical_target": semantic["target"],
            "control_attribute": semantic["attribute"],
            "required_slots": required,
            "optional_slots": optional,
            "value_contract": semantic["value_contract"],
            "mode_contract": intent.get("mode_contract"),
        })

    full["intents"].extend(new_intents)
    for family_id, members in sorted(family_members.items()):
        full["capability_families"].append({"family_id": family_id, "intents": members})
    full["known_unsupported_control_intent_ids"].extend(item["intent_id"] for item in new_intents)

    full["legacy_test_only"] = [
        item for item in full.get("legacy_test_only", [])
        if item.get("intent_id") not in {intent["intent_id"] for intent in new_intents}
    ]
    guidance = full["annotation_guidance"]["trunk_frunk_hood_routing"]
    guidance["frunk_expansion_status"] = "PARTIALLY_EXPANDED_FROM_REAL_DATA"
    guidance["included_intent_ids"] = ["FRUNK_OPEN"]
    guidance["deferred_candidate_intent_ids"] = ["FRUNK_CLOSE"]
    guidance["frunk_close_status"] = "PENDING_NO_REAL_DATA_EVIDENCE"
    guidance["lexical_boundary"] = {
        "FRUNK": ["前备箱", "前备厢"],
        "TRUNK": ["后备箱", "后备厢", "尾门", "普通未带前限定的行李厢"],
        "HOOD": ["前舱盖", "引擎盖", "发动机舱盖"],
    }

    ontology = full["semantic_ontology"]
    ontology["canonical_actions"] = sorted({item["canonical_action"] for item in full["intents"]})
    ontology["canonical_targets"] = sorted({item["canonical_target"] for item in full["intents"]})
    ontology["control_attributes"] = sorted({item["control_attribute"] for item in full["intents"]})

    origins = Counter(item["capability_origin"] for item in full["intents"])
    by_id = {item["intent_id"]: item for item in full["intents"]}
    project_family_count = sum(
        bool(family["intents"])
        and all(by_id[intent_id]["capability_origin"] == "PROJECT_NATIVE" for intent_id in family["intents"])
        for family in full["capability_families"]
    )
    stats = full["statistics"]
    stats.update({
        "intent_count": len(full["intents"]),
        "semantic_intent_count": len(full["intents"]),
        "formal_user_voice_intent_count": len(full["formal_user_voice_intent_ids"]),
        "known_unsupported_control_intent_count": len(full["known_unsupported_control_intent_ids"]),
        "project_native_intent_count": origins["PROJECT_NATIVE"],
        "vss_derived_intent_count": origins["VSS"] + origins["VSS_AND_PROJECT"],
        "capability_family_count": len(full["capability_families"]),
        "project_native_family_count": project_family_count,
        "legacy_test_only_intent_count": len(full.get("legacy_test_only", [])),
    })
    return full, intent_reports


def _source_hashes() -> dict[str, str]:
    paths = {"initial_screen/full_nlu_source_screen_v1.jsonl": SOURCE_SCREEN_PATH}
    paths.update({path.name: path for path in MAC_PATHS})
    actual = {name: evidence_sha256(path) for name, path in paths.items()}
    for name, expected in SOURCE_HASHES.items():
        if actual.get(name) != expected:
            raise RuntimeError(f"source SHA256 mismatch for {name}: expected {expected}, got {actual.get(name)}")
    return actual


def _candidate_report(kind: str, source_hashes: dict[str, str], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "report_version": f"known_unsupported_{kind}_candidates_v1",
        "approval_policy": "PENDING_ONLY_NOT_AUTO_ADDED_TO_REGISTRY",
        "source_sha256": source_hashes,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def _render_candidates(title: str, report: dict[str, Any]) -> str:
    lines = [f"# {title}", "", f"- Candidate count: **{report['candidate_count']}**", "- Registry auto-inclusion: **PROHIBITED**", ""]
    for index, item in enumerate(report["candidates"], start=1):
        lines.extend([
            f"## {index}. `{item['suggested_intent_id']}`", "",
            f"- MAC 对象: `{item.get('mac_raw_object', '')}`",
            f"- MAC 对象功能: `{item.get('mac_raw_object_function', '')}`",
            f"- MAC 功能: `{item.get('mac_raw_function', '')}`",
            f"- MAC 子功能: `{item.get('mac_raw_subfunction', '')}`",
            f"- MAC 操作: `{item.get('mac_raw_operation', [])}`",
            f"- 唯一样本数: **{item.get('unique_sample_count', 0)}**",
            f"- Formal 近邻冲突: `{item.get('formal_neighbor_conflict', False)}` `{item.get('formal_neighbor_intent_ids', [])}`",
            f"- 建议三元组: `{item.get('suggested_action')} + {item.get('suggested_target')} + {item.get('suggested_control_attribute')}`",
            f"- 建议 slots: `{item.get('suggested_slots', [])}`",
            f"- 审批状态: **{item.get('approval_status')}**", "", "真实示例：", "",
        ])
        lines.extend(f"- `{example['source_file']}:{example['source_id']}:{example['intent_key']}` — {example['split_sentence']}" for example in item.get("examples", []))
        lines.append("")
    return "\n".join(lines)


def _render_expansion(report: dict[str, Any]) -> str:
    lines = [
        "# R4 Known-Unsupported Expansion Report v1", "",
        f"- Removed dead contracts: `{report['removed_dead_contracts']}`",
        f"- New intents: **{report['new_intent_count']}**",
        f"- New capability families: **{report['new_capability_family_count']}**",
        f"- Formal intents: **{report['final_counts']['formal']}**",
        f"- Known unsupported intents: **{report['final_counts']['known_unsupported']}**",
        f"- R4 full SHA256: `{report['r4_full_sha256']}`", "",
    ]
    for item in report["new_intents"]:
        lines.extend([
            f"## `{item['intent_id']}`", "",
            f"- 唯一样本数: **{item['unique_sample_count']}**",
            f"- 三元组: `{item['canonical_action']} + {item['canonical_target']} + {item['control_attribute']}`",
            f"- Capability family: `{item['capability_family']}`",
            f"- VALUE/MODE contract: `{item.get('value_contract')}` / `{item.get('mode_contract')}`", "",
        ])
        lines.extend(f"- `{example['source_file']}:{example['source_id']}:{example['intent_key']}` — {example['split_sentence']}" for example in item["examples"])
        lines.append("")
    lines.extend([
        "## Pending candidates", "",
        f"- ADAS candidates not auto-added: **{report['pending_candidates']['adas']}**",
        f"- Other known-control candidates: **{report['pending_candidates']['other']}**", "",
    ])
    return "\n".join(lines)


def _render_diff(report: dict[str, Any]) -> str:
    lines = [
        "# R4 Core → Full Diff", "",
        f"- Core SHA256: `{report['core_sha256']}`",
        f"- Full SHA256: `{report['full_sha256']}`",
        f"- Validator: **{report['validator_status']}**",
        f"- New intents: **{len(report['new_intent_ids'])}**", "",
        "## New intent IDs", "",
    ]
    lines.extend(f"- `{intent_id}`" for intent_id in report["new_intent_ids"])
    lines.extend(["", "## Changed semantic paths", ""])
    lines.extend(f"- `{path}`" for path in report["changed_paths"])
    lines.append("")
    return "\n".join(lines)


def build_artifacts() -> dict[str, Any]:
    if sha256_file(CORE_PATH) != CORE_SHA256:
        raise RuntimeError("R4 core parent SHA256 mismatch")
    if sha256_file(R3_PATH) != R3_SHA256:
        raise RuntimeError("R3 SHA256 mismatch")
    source_hashes = _source_hashes()
    frames = extract_frames(MAC_PATHS, SOURCE_SCREEN_PATH)
    evidence = build_evidence(frames)
    core = load_yaml(CORE_PATH)
    full, intent_reports = build_registry(core, evidence, source_hashes)
    write_yaml(FULL_PATH, full)

    adas_report = _candidate_report("adas", source_hashes, evidence["adas_candidates"])
    other_report = _candidate_report("other", source_hashes, evidence["other_candidates"])
    write_json(ADAS_REPORT_PATH, adas_report)
    write_json(OTHER_REPORT_PATH, other_report)
    ADAS_REPORT_MD_PATH.write_text(_render_candidates("Known-Unsupported ADAS Candidates v1", adas_report), encoding="utf-8")
    OTHER_REPORT_MD_PATH.write_text(_render_candidates("Known-Unsupported Other Candidates v1", other_report), encoding="utf-8")

    core_targets = set(core["semantic_ontology"]["canonical_targets"])
    core_attributes = set(core["semantic_ontology"]["control_attributes"])
    core_contracts = set(core["value_contracts"]) | set(core["mode_contracts"])
    expansion_report = {
        "report_version": "r4_known_unsupported_expansion_report_v1",
        "build_version": BUILD_VERSION,
        "parent": {"path": "data/nlu/spec/intent_registry_r4_core_draft.yaml", "sha256": CORE_SHA256},
        "source_sha256": source_hashes,
        "removed_dead_contracts": ["FOLLOWING_GAP_REQUIRED"],
        "new_intent_count": len(intent_reports),
        "new_capability_family_count": len(full["capability_families"]) - len(core["capability_families"]),
        "new_targets": sorted(set(full["semantic_ontology"]["canonical_targets"]) - core_targets),
        "new_control_attributes": sorted(set(full["semantic_ontology"]["control_attributes"]) - core_attributes),
        "new_contracts": sorted((set(full["value_contracts"]) | set(full["mode_contracts"])) - core_contracts),
        "new_intents": intent_reports,
        "pending_candidates": {"adas": len(adas_report["candidates"]), "other": len(other_report["candidates"])},
        "final_counts": {
            "formal": len(full["formal_user_voice_intent_ids"]),
            "known_unsupported": len(full["known_unsupported_control_intent_ids"]),
            "semantic_intents": len(full["intents"]),
        },
        "r4_full_sha256": sha256_file(FULL_PATH),
    }
    write_json(EXPANSION_REPORT_PATH, expansion_report)
    EXPANSION_REPORT_MD_PATH.write_text(_render_expansion(expansion_report), encoding="utf-8")

    validation = validate()
    write_json(VALIDATOR_RESULT_PATH, validation)
    diff_report = {
        "report_version": "r4_core_to_full_diff_v1",
        "core_path": "data/nlu/spec/intent_registry_r4_core_draft.yaml",
        "core_sha256": CORE_SHA256,
        "full_path": "data/nlu/spec/intent_registry_r4_full_draft.yaml",
        "full_sha256": sha256_file(FULL_PATH),
        "validator_status": validation["status"],
        "new_intent_ids": validation.get("new_intent_ids", []),
        "changed_paths": validation.get("changed_paths", sorted(set(changed_paths(core, full)))),
        "metrics": validation.get("metrics", {}),
    }
    write_json(DIFF_JSON_PATH, diff_report)
    DIFF_MD_PATH.write_text(_render_diff(diff_report), encoding="utf-8")
    return {
        "status": validation["status"],
        "r3_sha256": sha256_file(R3_PATH),
        "core_sha256": sha256_file(CORE_PATH),
        "full_sha256": sha256_file(FULL_PATH),
        "new_intent_count": len(intent_reports),
        "new_capability_family_count": expansion_report["new_capability_family_count"],
        "formal_count": expansion_report["final_counts"]["formal"],
        "known_unsupported_count": expansion_report["final_counts"]["known_unsupported"],
        "validator_errors": validation["errors"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        result = build_artifacts()
    except (OSError, ValueError, KeyError, RuntimeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        result = {"status": "FAIL", "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
