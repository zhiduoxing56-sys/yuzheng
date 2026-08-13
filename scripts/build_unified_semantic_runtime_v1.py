from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
FORMAL_PATH = ROOT / "data/nlu/spec/intent_registry_r4_final.yaml"
KNOWN_PATH = ROOT / "data/nlu/spec/audits/known_non_executable_semantic_freeze_final_v4.yaml"
REMOVALS_PATH = ROOT / "data/nlu/spec/audits/known_non_executable_product_removals_v2.yaml"
QUARANTINE_PATH = ROOT / "data/nlu/spec/audits/known_non_executable_anchor_quarantine_final_v3.jsonl"
CONTRACT_SOURCE_PATH = ROOT / "data/nlu/spec/intent_registry_r4_final_candidate.yaml"
FORMAL_ANCHOR_PATH = ROOT / "挂靠/intent_anchor_set_v1_3.yaml"

REGISTRY_PATH = ROOT / "data/nlu/spec/intent_registry_unified_v1.yaml"
CARDS_PATH = ROOT / "挂靠/intent_cards_unified_v1.yaml"
ANCHOR_PATH = ROOT / "挂靠/intent_anchor_set_unified_v1.yaml"
RUNTIME_FREEZE_PATH = ROOT / "backend/intent_hybrid_gate/runtime_semantic_freeze_v1.json"


def load_yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def formal_definition(source: dict) -> dict:
    item = dict(source)
    # This frozen R4 label described legacy voice scope, not vehicle execution
    # support. It must not leak into the new neutral runtime identity contract.
    item.pop("user_voice_scope_status", None)
    item["runtime_identity"] = "FORMAL"
    item["boundary_contract"] = {}
    return item


def known_definition(source: dict) -> dict:
    slots = source["slots"]
    execution = source["execution_contract"]
    return {
        "intent_id": source["intent_id"],
        "chinese_name": source["display_name"],
        "capability_family": source["capability_family"],
        "canonical_action": source["canonical_action"],
        "canonical_target": source["canonical_target"],
        "control_attribute": source["control_attribute"],
        "control_domain": source["control_domain"],
        "risk_level": "R0_NON_EXECUTABLE",
        "risk_tags": ["KNOWN_NON_EXECUTABLE"],
        "required_slots": list(slots["required"]),
        "optional_slots": list(slots["optional"]),
        "allowed_areas": list(slots["allowed_areas"]),
        "value_contract": slots.get("value_contract"),
        "mode_contract": slots.get("mode_contract"),
        "direction_contract": slots.get("direction_contract"),
        "conditional_slot_contract": slots.get("conditional_slot_contract"),
        "value_mapping_contract": slots.get("value_mapping_contract"),
        "runtime_identity": execution["runtime_identity"],
        "boundary_contract": source["semantic_contract"]["formal_boundary"],
    }


def main() -> None:
    formal = load_yaml(FORMAL_PATH)
    known = load_yaml(KNOWN_PATH)
    removals = load_yaml(REMOVALS_PATH)
    formal_anchors = load_yaml(FORMAL_ANCHOR_PATH)
    contract_source = load_yaml(CONTRACT_SOURCE_PATH)

    formal_items = [formal_definition(item) for item in formal["intents"]]
    known_sources = known["known_non_executable_intents"]
    blocked_anchor_sources = [
        item["intent_id"]
        for item in known_sources
        if item.get("freeze_readiness") == "BLOCKED_ANCHOR_SOURCE"
    ]
    if blocked_anchor_sources:
        raise ValueError(
            "current Known freeze contains BLOCKED_ANCHOR_SOURCE intents; "
            f"production integration refused: {blocked_anchor_sources}"
        )
    known_items = [known_definition(item) for item in known_sources]
    intents = [*formal_items, *known_items]
    ids = [item["intent_id"] for item in intents]
    removed_ids = {item["intent_id"] for item in removals["removals"]}
    if (len(formal_items), len(known_items), len(intents)) != (71, 78, 149):
        raise ValueError("unified intent counts must be 71/78/149")
    if len(ids) != len(set(ids)) or set(ids) & removed_ids:
        raise ValueError("unified IDs are duplicate or contain product removals")

    referenced_contracts = {
        "value_contracts": {
            str(item.get("value_contract"))
            for item in intents
            if item.get("value_contract")
        },
        "mode_contracts": {
            str(item.get("mode_contract"))
            for item in intents
            if item.get("mode_contract")
        },
        "direction_contracts": {
            str(item.get("direction_contract"))
            for item in intents
            if item.get("direction_contract")
        },
        "conditional_slot_contracts": {
            str(item.get("conditional_slot_contract"))
            for item in intents
            if item.get("conditional_slot_contract")
        },
        "value_mapping_contracts": {
            str(item.get("value_mapping_contract"))
            for item in intents
            if item.get("value_mapping_contract")
        },
    }
    contract_catalogs = {}
    for catalog_name, references in referenced_contracts.items():
        source_catalog = contract_source.get(catalog_name, {})
        source_only_references = set(references)
        if catalog_name == "mode_contracts":
            source_only_references.discard("DRIVING_MODE_FINAL_APPROVED_V2")
        missing = source_only_references - set(source_catalog)
        if missing:
            raise ValueError(f"unresolved source contracts {catalog_name}: {sorted(missing)}")
        contract_catalogs[catalog_name] = {
            contract_id: source_catalog[contract_id]
            for contract_id in sorted(source_only_references)
        }
    driving_contract = next(
        item for item in known_sources if item["intent_id"] == "DRIVING_MODE_SET"
    )["semantic_contract"]["approved_mode_contract"]
    contract_catalogs["mode_contracts"]["DRIVING_MODE_FINAL_APPROVED_V2"] = [
        value["canonical"] for value in driving_contract["allowed_values"]
    ]

    mode_surface_mappings = {
        "HEADLIGHT": {
            "OFF": ["关闭前照灯", "关掉前照灯", "前照灯关闭", "主灯关闭"],
            "ON": ["打开前照灯", "开启前照灯", "前照灯打开", "主灯打开"],
            "POSITION": ["示宽灯", "位置灯"],
            "DAYTIME_RUNNING_LIGHTS": ["日间行车灯"],
            "AUTO": ["自动大灯", "自动前照灯"],
        },
        "GEAR": {"P": ["P挡", "P档", "驻车挡"], "N": ["N挡", "N档", "空挡"], "D": ["D挡", "D档", "前进挡"], "R": ["R挡", "R档", "倒挡"]},
        "GEAR_CHANGE": {"MANUAL": ["手动换挡", "手动模式"], "AUTOMATIC": ["自动换挡", "自动模式"]},
        "WIPER": {
            "OFF": ["关闭雨刮", "雨刮关闭"], "SLOW": ["雨刮慢速", "低速雨刮", "雨刮低速"],
            "MEDIUM": ["雨刮中速", "中速雨刮"], "FAST": ["雨刮快速", "高速雨刮", "雨刮高速"],
            "INTERVAL": ["间歇雨刮", "雨刮间歇"], "RAIN_SENSOR": ["自动雨刮", "感应雨刮"],
        },
        "CRUISE_GAP_LEVEL": {
            "LEVEL_1": ["一级", "1级", "一档"], "LEVEL_2": ["二级", "2级", "二档"],
            "LEVEL_3": ["三级", "3级", "三档"], "LEVEL_4": ["四级", "4级", "四档"],
        },
        "DRIVING_MODE_FINAL_APPROVED_V2": {
            value["canonical"]: list(value["surface_values"])
            for value in driving_contract["allowed_values"]
        },
    }
    for contract_id, values in contract_catalogs["mode_contracts"].items():
        mode_surface_mappings.setdefault(
            contract_id,
            {str(value): [str(value)] for value in values},
        )
    direction_surface_mappings = {
        "SEAT_FORWARD_BACKWARD": {"FORWARD": ["往前", "向前", "前移"], "BACKWARD": ["往后", "向后", "后移"]},
        "SEAT_UP_DOWN": {"UP": ["往上", "向上", "升高", "调高"], "DOWN": ["往下", "向下", "降低", "调低"]},
        "LUMBAR_SUPPORT_MORE_LESS": {"MORE": ["增加", "加强", "多顶"], "LESS": ["减小", "减弱", "少顶"]},
        "STEERING_WHEEL_EXTEND_RETRACT": {"EXTEND": ["往前", "向外", "推远"], "RETRACT": ["往后", "向内", "拉近"]},
        "STEERING_WHEEL_UP_DOWN": {"UP": ["往上", "抬高", "调高"], "DOWN": ["往下", "压低", "调低"]},
        "MIRROR_LEFT_RIGHT_UP_DOWN": {"LEFT": ["向左", "往左"], "RIGHT": ["向右", "往右"], "UP": ["向上", "往上"], "DOWN": ["向下", "往下"]},
        "TURN_INDICATOR_LEFT_RIGHT": {"LEFT": ["左转", "左侧"], "RIGHT": ["右转", "右侧"]},
        "LANE_CHANGE_LEFT_RIGHT": {"LEFT": ["向左", "左侧"], "RIGHT": ["向右", "右侧"]},
        "EVASIVE_STEER_LEFT_RIGHT": {"LEFT": ["向左", "左侧"], "RIGHT": ["向右", "右侧"]},
        "SUNROOF_TILT_UP_DOWN": {"UP": ["翘起", "上翘"], "DOWN": ["下收", "向下"]},
    }

    registry = {
        "document_status": "PRODUCTION_UNIFIED_SEMANTIC_REGISTRY",
        "registry_version": "unified-semantic-runtime-v1",
        "runtime_loading_allowed": True,
        "single_semantic_source_of_truth": True,
        "statistics": {
            "intent_count": 149,
            "formal_count": 71,
            "known_non_executable_count": 78,
        },
        "source_freezes": {
            "formal": {"path": FORMAL_PATH.relative_to(ROOT).as_posix(), "sha256": digest(FORMAL_PATH)},
            "known": {"path": KNOWN_PATH.relative_to(ROOT).as_posix(), "sha256": digest(KNOWN_PATH)},
            "product_removals": {"path": REMOVALS_PATH.relative_to(ROOT).as_posix(), "sha256": digest(REMOVALS_PATH)},
            "contract_catalog": {"path": CONTRACT_SOURCE_PATH.relative_to(ROOT).as_posix(), "sha256": digest(CONTRACT_SOURCE_PATH)},
        },
        "enums": {
            key: value
            for key, value in formal.get("enums", {}).items()
            if key not in {"user_voice_scope_status", "runtime_scope"}
        },
        "area_catalog": formal.get("area_catalog", []),
        "area_semantics": formal.get("area_semantics", {}),
        "value_contracts": contract_catalogs["value_contracts"],
        "mode_contracts": contract_catalogs["mode_contracts"],
        "direction_contracts": contract_catalogs["direction_contracts"],
        "conditional_slot_contracts": contract_catalogs["conditional_slot_contracts"],
        "mode_mapping_contracts": formal.get("mode_mapping_contracts", {}),
        "value_mapping_contracts": contract_catalogs["value_mapping_contracts"],
        "mode_surface_mappings": mode_surface_mappings,
        "direction_surface_mappings": direction_surface_mappings,
        "contract_catalog_provenance": {
            "source": CONTRACT_SOURCE_PATH.relative_to(ROOT).as_posix(),
            "policy": "COPY_ONLY_REFERENCED_EXISTING_CONTRACTS_NO_GUESSED_RANGE_OR_ENUM",
        },
        "intents": intents,
    }

    cards = {
        "artifact_status": "DERIVED_RUNTIME_INDEX",
        "artifact_version": "unified-intent-cards-v1",
        "source_registry": REGISTRY_PATH.relative_to(ROOT).as_posix(),
        "source_registry_version": registry["registry_version"],
        "intent_count": len(intents),
        "intents": {
            item["intent_id"]: {
                "name": item["chinese_name"],
                "runtime_identity": item["runtime_identity"],
                "canonical_action": item["canonical_action"],
                "canonical_target": item["canonical_target"],
                "control_attribute": item["control_attribute"],
            }
            for item in intents
        },
    }

    anchor_groups = {}
    formal_anchor_map = formal_anchors["正式意图"]
    for item in formal_items:
        intent_id = item["intent_id"]
        anchor_groups[intent_id] = {
            "runtime_identity": "FORMAL",
            "anchors": list(dict.fromkeys(formal_anchor_map[intent_id])),
        }
    for source in known_sources:
        intent_id = source["intent_id"]
        active = [
            anchor["text"]
            for anchor in source["anchors"].get("historical_recovered", [])
        ] + [
            anchor["text"]
            for anchor in source["anchors"].get("human_generated_approved", [])
        ] + [
            anchor["text"]
            for anchor in source["anchors"].get("human_reclassified_from_quarantine", [])
        ]
        anchor_groups[intent_id] = {
            "runtime_identity": "KNOWN_NON_EXECUTABLE",
            "anchors": list(dict.fromkeys(active)),
        }
    if set(anchor_groups) != set(ids) or any(not group["anchors"] for group in anchor_groups.values()):
        raise ValueError("every unified intent must have a non-empty anchor group")

    anchor_index = {
        "artifact_status": "DERIVED_RUNTIME_INDEX",
        "artifact_version": "unified-intent-anchors-v1",
        "source_registry": REGISTRY_PATH.relative_to(ROOT).as_posix(),
        "source_registry_version": registry["registry_version"],
        "intent_count": len(anchor_groups),
        "semantic_anchor_count": sum(len(group["anchors"]) for group in anchor_groups.values()),
        "intents": anchor_groups,
        "security": {
            "target": "安全注入",
            "anchors": list(formal_anchors["安全注入"]),
        },
        "exclusions": {
            "product_removed_intent_count": len(removed_ids),
            "quarantine_record_count": len(QUARANTINE_PATH.read_text(encoding="utf-8").splitlines()),
            "unapproved_hash_candidate_count": 1402,
            "legacy_known_control_bypass_active": False,
        },
    }

    REGISTRY_PATH.write_text(yaml.safe_dump(registry, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    registry_hash = digest(REGISTRY_PATH)
    cards["source_registry_sha256"] = registry_hash
    anchor_index["source_registry_sha256"] = registry_hash
    CARDS_PATH.write_text(yaml.safe_dump(cards, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    ANCHOR_PATH.write_text(yaml.safe_dump(anchor_index, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    runtime_freeze = json.loads(RUNTIME_FREEZE_PATH.read_text(encoding="utf-8"))
    runtime_freeze.update(
        {
            "registry_sha256": digest(REGISTRY_PATH),
            "cards_sha256": digest(CARDS_PATH),
            "anchors_sha256": digest(ANCHOR_PATH),
        }
    )
    RUNTIME_FREEZE_PATH.write_text(
        json.dumps(runtime_freeze, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        {
            "registry": str(REGISTRY_PATH),
            "cards": len(cards["intents"]),
            "semantic_anchors": anchor_index["semantic_anchor_count"],
            "security_anchors": len(anchor_index["security"]["anchors"]),
        }
    )


if __name__ == "__main__":
    main()
