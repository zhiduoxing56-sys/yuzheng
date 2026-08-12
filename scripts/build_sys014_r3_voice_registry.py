"""Deterministically derive and freeze the SYS-014 R3 user-voice registry."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r3_voice_registry import (
    FROZEN_STATUS,
    FORMAL_STATUS,
    KNOWN_STATUS,
    MANIFEST_PATH,
    MAPPING_PATH,
    R2_PATH,
    R2_SHA256,
    R3_PATH,
    R3_VERSION,
    RUNTIME_SUPPORT_PATH,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_JSON_PATH = ROOT / "data/nlu/spec/audits/r2_to_r3_user_voice_registry_audit.json"
AUDIT_MD_PATH = ROOT / "data/nlu/spec/audits/r2_to_r3_user_voice_registry_audit.md"
VALIDATOR_RESULT_PATH = ROOT / "data/nlu/spec/audits/r3_voice_registry_validator_result.json"
BUILD_VERSION = "sys014_r3_registry_builder_v1"

REMOVAL_DECISIONS = [
    ("锁定外后视镜调节", "MIRROR_ADJUSTMENT_LOCK"),
    ("解锁外后视镜调节", "MIRROR_ADJUSTMENT_UNLOCK"),
    ("设置前舱盖开度", "HOOD_SET_POSITION"),
    ("启用低速四驱或低速挡", "LOW_RANGE_ENABLE"),
    ("停用低速四驱或低速挡", "LOW_RANGE_DISABLE"),
    ("设置前后轴扭矩分配", "TORQUE_DISTRIBUTION_SET"),
    ("设置变速箱性能模式", "TRANSMISSION_PERFORMANCE_MODE_SET"),
    ("结合电驱动力", "ELECTRIC_POWERTRAIN_ENGAGE"),
    ("分离电驱动力", "ELECTRIC_POWERTRAIN_DISENGAGE"),
    ("设置离合器结合度", "CLUTCH_SET_ENGAGEMENT"),
    ("锁定差速器", "DIFFERENTIAL_LOCK"),
    ("解锁差速器", "DIFFERENTIAL_UNLOCK"),
    ("结合驻车锁", "PARK_LOCK"),
    ("释放驻车锁", "PARK_UNLOCK"),
    ("启用防抱死制动系统", "ABS_ENABLE"),
    ("停用防抱死制动系统", "ABS_DISABLE"),
    ("启用牵引力控制系统", "TCS_ENABLE"),
    ("停用牵引力控制系统", "TCS_DISABLE"),
    ("启用电子制动力分配系统", "EBD_ENABLE"),
    ("停用电子制动力分配系统", "EBD_DISABLE"),
    ("启用紧急制动辅助系统", "EBA_ENABLE"),
    ("停用紧急制动辅助系统", "EBA_DISABLE"),
]

RUNTIME_EXECUTION_EVIDENCE = {
    "WINDOW_OPEN": {"adapter_action_key": "打开|车窗", "tests": ["backend/tests/stage4/test_stage4_workflow.py", "backend/tests/unit/test_semantic.py"]},
    "DOOR_OPEN": {"adapter_action_key": "打开|车门", "tests": ["backend/tests/stage4/test_stage4_workflow.py", "backend/tests/api/test_command_api.py"]},
    "DOOR_UNLOCK": {"adapter_action_key": "解锁|车门", "tests": ["backend/tests/stage4/test_stage4_workflow.py"]},
    "ACCELERATE": {"adapter_action_key": "加速|速度", "tests": ["backend/tests/stage4/test_stage4_workflow.py", "backend/tests/unit/test_semantic.py"]},
    "DECELERATE": {"adapter_action_key": "减速|速度", "tests": ["backend/tests/stage4/test_stage4_workflow.py", "backend/tests/stage3/test_stage3_scenarios.py"]},
    "BRAKE": {"adapter_action_key": "打开|制动", "tests": ["backend/tests/stage4/test_stage4_workflow.py"]},
    "AUTO_PARK_ENABLE": {"adapter_action_key": "打开|自动泊车", "tests": ["backend/tests/stage3/test_stage3_scenarios.py", "backend/tests/step1/test_action_evidence_alignment.py"]},
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def scan_historical_poc_code_references() -> dict[str, Any]:
    pattern = re.compile(r"sys014-poc7|poc7-v[12]|7-Intent|7 Intent|label_mapping\.json|rbt3-exp|electra-exp", re.IGNORECASE)
    matches: list[dict[str, Any]] = []
    excluded_auditors = {
        "scripts/build_sys014_r3_voice_registry.py",
        "scripts/validate_sys014_r3_voice_registry.py",
    }
    roots = [ROOT / "backend/app", ROOT / "backend/tests/offline_nlu", ROOT / "config", ROOT / "scripts"]
    for scan_root in roots:
        for path in scan_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".py", ".yaml", ".yml", ".json"}:
                continue
            relative = path.relative_to(ROOT).as_posix()
            if relative in excluded_auditors:
                continue
            for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                if not pattern.search(line):
                    continue
                if relative.startswith(("backend/app/", "config/")):
                    classification = "ACTIVE_RUNTIME_CODE"
                elif relative.startswith("backend/tests/offline_nlu/"):
                    classification = "HISTORICAL_POC_TEST_ONLY"
                elif relative.startswith("scripts/nlu_training/") or relative.startswith("scripts/freeze_sys014_poc7") or relative.startswith("scripts/validate_sys014_frozen") or relative == "scripts/profile_sys014_stage4a.py":
                    classification = "HISTORICAL_POC_ONLY"
                else:
                    classification = "LEGACY_CODE_REFERENCE_REVIEW"
                matches.append({
                    "path": relative,
                    "line": line_number,
                    "classification": classification,
                    "text": line.strip()[:500],
                })
    by_class = Counter(item["classification"] for item in matches)
    active = [item for item in matches if item["classification"] == "ACTIVE_RUNTIME_CODE"]
    return {
        "audit_name": "7-Intent PoC Active Dependency Audit",
        "scan_roots": [path.relative_to(ROOT).as_posix() for path in roots],
        "scan_exclusions": sorted(excluded_auditors),
        "classification_counts": dict(sorted(by_class.items())),
        "ACTIVE_FULL_NLU_DEPENDENCY_COUNT": len(active),
        "active_references": active,
        "all_code_references": matches,
        "required_status": "HISTORICAL_POC_ONLY / NOT_FOR_FULL_NLU",
    }


def runtime_support_audit() -> dict[str, Any]:
    runtime = load_yaml(RUNTIME_SUPPORT_PATH)
    action_config = load_yaml(ROOT / "config/vehicle_actions.yaml")
    action_keys = set(action_config.get("actions", {}))
    rows: list[dict[str, Any]] = []
    for intent_id, evidence in RUNTIME_EXECUTION_EVIDENCE.items():
        support = runtime.get("intents", {}).get(intent_id, {})
        adapter_key = evidence["adapter_action_key"]
        tests = evidence["tests"]
        if support.get("execution_support") != "FULL":
            raise RuntimeError(f"{intent_id}: execution_support is no longer FULL")
        if adapter_key not in action_keys:
            raise RuntimeError(f"{intent_id}: missing simulator action {adapter_key}")
        if not all((ROOT / path).exists() for path in tests):
            raise RuntimeError(f"{intent_id}: declared execution test evidence missing")
        rows.append({
            "canonical_intent_id": intent_id,
            "execution_support": "FULL",
            "adapter_action_key": adapter_key,
            "adapter_config": "config/vehicle_actions.yaml",
            "adapter_implementation": "backend/app/services/vehicle/simulator.py",
            "execution_service": "backend/app/services/execution/service.py",
            "test_evidence": tests,
            "finding": "INDEPENDENT_BACKEND_IMPLEMENTATION_CONFIRMED",
            "defines_full_nlu_label_space": False,
        })
    return {
        "source": "data/nlu/spec/intent_runtime_support.yaml",
        "source_sha256": sha256_file(RUNTIME_SUPPORT_PATH),
        "execution_full_count": len(rows),
        "items": rows,
        "conclusion": "KEEP_AS_CURRENT_BACKEND_ENGINEERING_FACT_ONLY",
    }


def registry_counts(intents: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "intent_count": len(intents),
        "canonical_action_count": len({item["canonical_action"] for item in intents}),
        "canonical_target_count": len({item["canonical_target"] for item in intents}),
        "control_attribute_count": len({item["control_attribute"] for item in intents}),
    }


def render_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SYS-014 R2 → R3 用户语音正式注册表审计",
        "",
        f"- status: **{audit['status']}**",
        f"- R2 SHA256: `{audit['parent_registry']['sha256']}`",
        f"- R3 SHA256: `{audit['r3_registry']['sha256']}`",
        f"- 正式用户语音意图: **{audit['counts']['formal_user_voice']['intent_count']}**",
        f"- 已知但不开放: **{audit['counts']['known_unsupported']['intent_count']}**",
        f"- 保留语义目录: **{audit['counts']['semantic_catalog']['intent_count']}**",
        "",
        "## R2 → R3 变更",
        "",
        "- R2 全部93条语义定义、合同、capability family 和 VSS provenance 逐项保留。",
        "- 22条从用户语音正式范围移至 `KNOWN_UNSUPPORTED_CONTROL`。",
        "- 其余71条标记为 `FORMAL_EXECUTABLE`。",
        "- `intent_runtime_support.yaml` 未修改，也不定义 Full NLU 标签空间。",
        "- 旧 annotation schema 冲突只记录，留待下一阶段处理。",
        "",
        "## 移出的22项",
        "",
        "| # | canonical_intent_id | 中文语义 | action | target | attribute | VSS source |",
        "|---:|---|---|---|---|---|---|",
    ]
    for index, item in enumerate(audit["known_unsupported_control_intents"], start=1):
        lines.append(
            f"| {index} | `{item['intent_id']}` | {item['chinese_name']} | `{item['canonical_action']}` | `{item['canonical_target']}` | `{item['control_attribute']}` | `{', '.join(item['vss_capability_ids'])}` |"
        )
    lines.extend([
        "",
        "## 71项正式用户语音意图",
        "",
        "| # | canonical_intent_id | 中文语义 | action | target | attribute |",
        "|---:|---|---|---|---|---|",
    ])
    for index, item in enumerate(audit["formal_user_voice_intents"], start=1):
        lines.append(
            f"| {index} | `{item['intent_id']}` | {item['chinese_name']} | `{item['canonical_action']}` | `{item['canonical_target']}` | `{item['control_attribute']}` |"
        )
    lines.extend([
        "",
        "## 合同与本体统计",
        "",
        "| 指标 | 全部93条语义 | 正式71条 | 已知不开放22条 |",
        "|---|---:|---:|---:|",
    ])
    for key, label in (
        ("intent_count", "Intent"),
        ("canonical_action_count", "canonical_action"),
        ("canonical_target_count", "canonical_target"),
        ("control_attribute_count", "control_attribute"),
    ):
        lines.append(f"| {label} | {audit['counts']['semantic_catalog'][key]} | {audit['counts']['formal_user_voice'][key]} | {audit['counts']['known_unsupported'][key]} |")
    contracts = audit["contract_counts"]
    lines.extend([
        "",
        f"- VALUE contracts: `{contracts['value_contracts']}`",
        f"- DIRECTION contracts: `{contracts['direction_contracts']}`",
        f"- MODE contracts: `{contracts['mode_contracts']}`",
        f"- conditional slot contracts: `{contracts['conditional_slot_contracts']}`",
        "",
        "## 当前7项运行支持事实",
        "",
        "这些项目均存在独立的后端模拟器动作配置、执行服务调用链和测试证据；保留 `execution_support=FULL`，但不参与 Full NLU 标签空间定义。",
        "",
        "| Intent | adapter action | finding |",
        "|---|---|---|",
    ])
    for item in audit["runtime_support_audit"]["items"]:
        lines.append(f"| `{item['canonical_intent_id']}` | `{item['adapter_action_key']}` | `{item['finding']}` |")
    dep = audit["historical_poc_dependency_audit"]
    lines.extend([
        "",
        "## 7-Intent PoC Active Dependency Audit",
        "",
        f"- `ACTIVE_FULL_NLU_DEPENDENCY_COUNT = {dep['ACTIVE_FULL_NLU_DEPENDENCY_COUNT']}`",
        "- 历史脚本和测试仍保留，统一分类为历史/待复盘代码，不是 Full NLU 主路径。",
        "- 后端运行代码及 config 中未发现 `sys014-poc7-*`、RBT3/ELECTRA 7类 checkpoint 或7类 label mapping 加载。",
        "",
        "| 分类 | 引用行数 |",
        "|---|---:|",
    ])
    for key, value in dep["classification_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend([
        "",
        "完整代码引用关系见同目录 machine-readable JSON 的 `historical_poc_dependency_audit.all_code_references`。",
        "",
        "## Validator",
        "",
        f"- status: `{audit['validator']['status']}`",
        f"- semantic key collision count: `{audit['validator']['metrics']['SEMANTIC_KEY_COLLISION_COUNT']}`",
        f"- duplicate intent ID count: `{audit['validator']['metrics']['DUPLICATE_INTENT_ID_COUNT']}`",
        f"- unresolved contract count: `{audit['validator']['metrics']['UNRESOLVED_CONTRACT_COUNT']}`",
        f"- source traceability error count: `{audit['validator']['metrics']['SOURCE_TRACEABILITY_ERROR_COUNT']}`",
        "",
        "## Annotation schema",
        "",
        "现有 `data/nlu/spec/annotation_schema.json` 与下一阶段冻结的中文统一样本结构冲突。本轮未修改；下一阶段必须以显式适配层替换，不能静默兼容。",
        "",
    ])
    return "\n".join(lines)


def build() -> dict[str, Any]:
    if sha256_file(R2_PATH) != R2_SHA256:
        raise RuntimeError("R2 SHA256 differs from the approved parent")
    r2 = load_yaml(R2_PATH)
    if len(r2.get("intents", [])) != 93:
        raise RuntimeError("R2 semantic intent count is not 93")
    by_id = {item["intent_id"]: item for item in r2["intents"]}
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in r2["intents"]:
        by_name[item["chinese_name"]].append(item)
    for expected_name, expected_id in REMOVAL_DECISIONS:
        matches = by_name.get(expected_name, [])
        if len(matches) != 1 or matches[0].get("intent_id") != expected_id:
            raise RuntimeError(f"removal mapping is not unique: {expected_name} -> {expected_id}; matches={matches}")

    removed_ids = {intent_id for _, intent_id in REMOVAL_DECISIONS}
    r3 = copy.deepcopy(r2)
    r3["document_status"] = "R3_CANDIDATE_OFFLINE_NOT_RUNTIME"
    r3["registry_version"] = R3_VERSION
    r3["modified_date"] = "2026-08-09"
    r3["semantic_freeze_status"] = "CANDIDATE_PENDING_VALIDATION"
    r3["enums"]["user_voice_scope_status"] = [FORMAL_STATUS, KNOWN_STATUS]
    r3["statistics"]["semantic_intent_count"] = 93
    r3["statistics"]["formal_user_voice_intent_count"] = 71
    r3["statistics"]["known_unsupported_control_intent_count"] = 22
    for item in r3["intents"]:
        item["user_voice_scope_status"] = KNOWN_STATUS if item["intent_id"] in removed_ids else FORMAL_STATUS
    formal_ids = [item["intent_id"] for item in r3["intents"] if item["user_voice_scope_status"] == FORMAL_STATUS]
    known_ids = [item["intent_id"] for item in r3["intents"] if item["user_voice_scope_status"] == KNOWN_STATUS]
    if len(formal_ids) != 71 or len(known_ids) != 22:
        raise RuntimeError(f"R3 projection count mismatch: formal={len(formal_ids)}, known={len(known_ids)}")
    r3["formal_user_voice_intent_ids"] = formal_ids
    r3["known_unsupported_control_intent_ids"] = known_ids
    r3["parent_registry"] = {
        "path": "data/nlu/spec/intent_registry_draft.yaml",
        "registry_version": "sys-014-semantic-hardening-r2",
        "sha256": R2_SHA256,
        "inheritance_rule": "PRESERVE_ALL_93_SEMANTIC_AND_VSS_DEFINITIONS",
    }
    r3["user_voice_scope_contract"] = {
        FORMAL_STATUS: "Full NLU 控制范围=正式可执行；不表示当前后端已经实现执行适配器。",
        KNOWN_STATUS: "Full NLU 控制范围=已知但不开放；保留语义、合同、capability family 与 VSS provenance。",
    }
    r3["mapping_rule_source"] = {
        "path": "data/nlu/spec/mapping_rules/full_nlu_mapping_v1.yaml",
        "version": "nlu_mapping_v1",
        "sha256": sha256_file(MAPPING_PATH),
    }
    r3["runtime_support_independence"] = {
        "path": "data/nlu/spec/intent_runtime_support.yaml",
        "source_sha256": sha256_file(RUNTIME_SUPPORT_PATH),
        "defines_full_nlu_label_space": False,
        "execution_full_count_at_freeze": 7,
    }
    r3["historical_poc_policy"] = {
        "status": ["HISTORICAL_POC_ONLY", "NOT_FOR_FULL_NLU"],
        "active_full_nlu_dependency_count": 0,
        "prohibited_uses": ["DATA_BUILD", "TRAINING", "VALIDATION", "TEST", "SAFETY_GOLD", "FALLBACK", "CHECKPOINT_INITIALIZATION", "LABEL_SPACE_SOURCE"],
    }
    r3["annotation_schema_compatibility"] = {
        "path": "data/nlu/spec/annotation_schema.json",
        "status": "CONFLICT_RECORDED_DEFERRED_TO_NEXT_STAGE",
        "required_next_stage": "IMPLEMENT_ONLY_THE_FROZEN_CHINESE_UNIFIED_SAMPLE_SCHEMA_AND_EXPLICIT_LEGACY_ADAPTER",
    }

    write_yaml(R3_PATH, r3)
    candidate_result = validate(R3_PATH, require_frozen=False, manifest_path=None)
    if candidate_result["status"] != "PASS":
        raise RuntimeError(json.dumps(candidate_result, ensure_ascii=False, indent=2))

    r3["document_status"] = "FROZEN_OFFLINE_NOT_RUNTIME"
    r3["semantic_freeze_status"] = FROZEN_STATUS
    write_yaml(R3_PATH, r3)
    preliminary_result = validate(R3_PATH, require_frozen=True, manifest_path=None)
    if preliminary_result["status"] != "PASS":
        raise RuntimeError(json.dumps(preliminary_result, ensure_ascii=False, indent=2))

    formal_items = [by_id[intent_id] for intent_id in formal_ids]
    known_items = [by_id[intent_id] for intent_id in known_ids]
    dep_audit = scan_historical_poc_code_references()
    if dep_audit["ACTIVE_FULL_NLU_DEPENDENCY_COUNT"] != 0:
        raise RuntimeError(json.dumps(dep_audit["active_references"], ensure_ascii=False, indent=2))
    runtime_audit = runtime_support_audit()
    audit = {
        "audit_id": "SYS-014-R2-TO-R3-USER-VOICE-REGISTRY-AUDIT-1",
        "status": "PASS",
        "build_version": BUILD_VERSION,
        "parent_registry": {"path": "data/nlu/spec/intent_registry_draft.yaml", "version": r2["registry_version"], "sha256": R2_SHA256},
        "r3_registry": {"path": "data/nlu/spec/intent_registry_r3.yaml", "version": R3_VERSION, "sha256": sha256_file(R3_PATH)},
        "diff": {
            "semantic_intents_added": [],
            "semantic_intents_deleted": [],
            "semantic_or_vss_definitions_changed": [],
            "moved_from_formal_to_known_unsupported": known_ids,
            "new_user_voice_scope_field": "user_voice_scope_status",
        },
        "counts": {
            "semantic_catalog": registry_counts(r2["intents"]),
            "formal_user_voice": registry_counts(formal_items),
            "known_unsupported": registry_counts(known_items),
        },
        "contract_counts": {
            "value_contracts": len(r3["value_contracts"]),
            "direction_contracts": len(r3["direction_contracts"]),
            "mode_contracts": len(r3["mode_contracts"]),
            "conditional_slot_contracts": len(r3["conditional_slot_contracts"]),
            "value_mapping_contracts": len(r3["value_mapping_contracts"]),
            "mode_mapping_contracts": len(r3["mode_mapping_contracts"]),
        },
        "formal_user_voice_intents": [
            {key: item.get(key) for key in ("intent_id", "chinese_name", "canonical_action", "canonical_target", "control_attribute", "capability_family", "capability_origin", "vss_capability_ids")}
            for item in formal_items
        ],
        "known_unsupported_control_intents": [
            {key: item.get(key) for key in ("intent_id", "chinese_name", "canonical_action", "canonical_target", "control_attribute", "capability_family", "capability_origin", "vss_capability_ids")}
            for item in known_items
        ],
        "removal_decision_mapping": [{"requested_semantics": name, "canonical_intent_id": intent_id, "unique_match": True} for name, intent_id in REMOVAL_DECISIONS],
        "runtime_support_audit": runtime_audit,
        "historical_poc_dependency_audit": dep_audit,
        "mapping_rule_source": {"path": "data/nlu/spec/mapping_rules/full_nlu_mapping_v1.yaml", "version": "nlu_mapping_v1", "sha256": sha256_file(MAPPING_PATH)},
        "annotation_schema_conflict": {"path": "data/nlu/spec/annotation_schema.json", "status": "RECORDED_NOT_MODIFIED", "next_stage": "CHINESE_UNIFIED_SAMPLE_SCHEMA"},
        "validator": preliminary_result,
    }
    AUDIT_JSON_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    AUDIT_MD_PATH.write_text(render_markdown(audit), encoding="utf-8")

    manifest = {
        "manifest_id": "SYS-014-R3-FULL-NLU-REGISTRY-FREEZE-1",
        "registry_file": "data/nlu/spec/intent_registry_r3.yaml",
        "registry_version": R3_VERSION,
        "registry_sha256": sha256_file(R3_PATH),
        "status": FROZEN_STATUS,
        "unique_full_nlu_registry_authority": True,
        "semantic_intent_count": 93,
        "formal_user_voice_intent_count": 71,
        "known_unsupported_control_intent_count": 22,
        "parent_registry_file": "data/nlu/spec/intent_registry_draft.yaml",
        "parent_registry_version": r2["registry_version"],
        "parent_registry_sha256": R2_SHA256,
        "mapping_rule_file": "data/nlu/spec/mapping_rules/full_nlu_mapping_v1.yaml",
        "mapping_rule_version": "nlu_mapping_v1",
        "mapping_rule_sha256": sha256_file(MAPPING_PATH),
        "runtime_support_file": "data/nlu/spec/intent_runtime_support.yaml",
        "runtime_support_sha256": sha256_file(RUNTIME_SUPPORT_PATH),
        "runtime_support_defines_full_nlu_label_space": False,
        "active_full_nlu_historical_poc_dependency_count": 0,
        "audit_json": "data/nlu/spec/audits/r2_to_r3_user_voice_registry_audit.json",
        "audit_json_sha256": sha256_file(AUDIT_JSON_PATH),
        "audit_markdown": "data/nlu/spec/audits/r2_to_r3_user_voice_registry_audit.md",
        "audit_markdown_sha256": sha256_file(AUDIT_MD_PATH),
        "deprecated_full_nlu_authorities": [
            "0127af1d64b33a9e517537ccd458905fcc6af3414cc70701fc362474a4ec2739",
            R2_SHA256,
        ],
        "dataset_build_started": False,
        "model_training_started": False,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    final_result = validate(R3_PATH, require_frozen=True, manifest_path=MANIFEST_PATH)
    VALIDATOR_RESULT_PATH.write_text(json.dumps(final_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if final_result["status"] != "PASS":
        raise RuntimeError(json.dumps(final_result, ensure_ascii=False, indent=2))
    return {
        "status": "PASS",
        "registry_path": str(R3_PATH.relative_to(ROOT)).replace("\\", "/"),
        "registry_sha256": sha256_file(R3_PATH),
        "manifest_path": str(MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/"),
        "manifest_sha256": sha256_file(MANIFEST_PATH),
        "formal_user_voice_intent_count": 71,
        "known_unsupported_control_intent_count": 22,
        "active_full_nlu_historical_poc_dependency_count": 0,
        "validator_result": str(VALIDATOR_RESULT_PATH.relative_to(ROOT)).replace("\\", "/"),
    }


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
