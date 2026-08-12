"""Apply the final metadata-only freeze patch to the R4 simplified candidate."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import yaml

from validate_sys014_r4_core_registry import StrictSafeLoader, changed_paths, sha256_file


ROOT = Path(__file__).resolve().parents[1]
SIMPLIFIED_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_simplified_candidate.yaml"
FINAL_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_r4_final.yaml"
AUDIT_DIR = ROOT / "data" / "nlu" / "spec" / "audits"
DIFF_PATH = AUDIT_DIR / "r4_simplified_to_final_diff.md"
VALIDATOR_PATH = AUDIT_DIR / "r4_final_validator_result.json"
NEXT_MAPPING_PATH = ROOT / "data" / "nlu" / "spec" / "mapping_rules" / "nlu_mapping_r4_scope_v1.yaml"

SIMPLIFIED_SHA256 = "4eb697a9cc9daf48d1292e34b5ca37936de114028e71cfcf495e773335e6406f"
FINAL_VERSION = "sys-014-semantic-hardening-r4-final"
FINAL_FREEZE_STATUS = "FROZEN_FOR_FULL_NLU_GOLD_BUILD"
FINAL_DOCUMENT_STATUS = "FROZEN_FORMAL_RUNTIME_REGISTRY"


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


def build_final_registry(simplified: dict[str, Any]) -> dict[str, Any]:
    final = copy.deepcopy(simplified)
    final["registry_version"] = FINAL_VERSION
    final["semantic_freeze_status"] = FINAL_FREEZE_STATUS
    final["document_status"] = FINAL_DOCUMENT_STATUS
    final["runtime_loading_allowed"] = True

    mapping = final["mapping_rule_source"]
    mapping["status"] = "LEGACY_PRE_R4_MAPPING"
    mapping["usable_for_r4_gold"] = False
    mapping["usable_for_training"] = False
    mapping["required_next_mapping_version"] = "nlu_mapping_r4_scope_v1"
    final["r4_mapping_policy"] = {
        "architecture": "FORMAL_INTENT_HEAD_PLUS_UNIFIED_SCOPE_CLASSIFICATION",
        "scope_mapping_required": True,
        "formal_intent_mapping_only_when_scope_formal": True,
        "old_baseline_mapping_as_truth_prohibited": True,
    }

    gold = final["gold_scope_mapping_policy"]
    gold.pop("known_control_evidence_requirement", None)
    gold["known_control_evidence_policy"] = {
        "primary_evidence": "RAW_TEXT",
        "auxiliary_evidence_when_available": ["MAC_SPLIT_SENS", "MAC_SEMANTICS"],
        "evidence_priority": ["RAW_TEXT", "MAC_SPLIT_SENS", "MAC_SEMANTICS"],
        "all_three_required": False,
        "baseline_mapping_as_truth_prohibited": True,
        "known_control_bypass_candidate_rule": {
            "raw_text_clearly_indicates_real_vehicle_cockpit_or_local_head_unit_control": True,
            "formal_executable_mapping_unavailable": True,
        },
        "mac_annotation_role": "AUXILIARY_EVIDENCE_AND_CONFLICT_CHECK_WHEN_AVAILABLE",
        "source_conflict_policy": {
            "annotation_must_not_override_raw_text": True,
            "route": "SOURCE_CONFLICT_REVIEW",
        },
        "old_baseline_may_determine_final_scope": False,
    }
    del final["mode_mapping_contracts"]["HEADLIGHT_MAIN_SWITCH"]["restricted_aliases"]["ON"][
        "prohibited_canonical_mode"
    ]
    return final


def _render_diff(simplified: dict[str, Any], final: dict[str, Any], validation: dict[str, Any]) -> str:
    lines = [
        "# R4 Simplified Candidate → Final Freeze Diff", "",
        f"- Simplified candidate SHA256: `{SIMPLIFIED_SHA256}`",
        f"- Final SHA256: `{sha256_file(FINAL_PATH)}`",
        f"- Validator: **{validation['status']}**",
        "- Original freeze purpose: **FULL_NLU_GOLD_BUILD**",
        "- Current runtime contract: **FROZEN_READ_ONLY_LOADING_ALLOWED**", "",
        "## Frozen catalog", "",
        f"- Runtime Intent head: **{final['statistics']['runtime_intent_head_count']}**",
        f"- FORMAL_EXECUTABLE: **{final['statistics']['formal_user_voice_intent_count']}**",
        f"- Archived Known Control references: **{final['statistics']['archived_known_control_reference_count']}**",
        f"- Runtime scopes: **{final['statistics']['runtime_scope_count']}**", "",
        "## Mapping policy", "",
        "- `full_nlu_mapping_v1.yaml`: historical provenance only",
        "- Usable for R4 Gold: **false**",
        "- Usable for training: **false**",
        "- Required next mapping version: `nlu_mapping_r4_scope_v1`",
        "- Next mapping file created in this patch: **false**", "",
        "## Known Control evidence priority", "",
        "1. `RAW_TEXT`",
        "2. `MAC_SPLIT_SENS` when available",
        "3. `MAC_SEMANTICS` when available",
        "",
        "All three required: **false**. Annotation conflicts route to `SOURCE_CONFLICT_REVIEW` and may not override raw text.", "",
        "## Changed paths", "",
    ]
    lines.extend(f"- `{path}`" for path in sorted(set(changed_paths(simplified, final))))
    lines.append("")
    return "\n".join(lines)


def build_artifacts() -> dict[str, Any]:
    if sha256_file(SIMPLIFIED_PATH) != SIMPLIFIED_SHA256:
        raise RuntimeError("R4 simplified candidate SHA256 mismatch")
    if NEXT_MAPPING_PATH.exists():
        raise RuntimeError("nlu_mapping_r4_scope_v1 already exists; this metadata-only stage must not create or modify it")
    simplified = load_yaml(SIMPLIFIED_PATH)
    final = build_final_registry(simplified)
    write_yaml(FINAL_PATH, final)

    from validate_sys014_r4_frozen_final import validate

    validation = validate()
    write_json(VALIDATOR_PATH, validation)
    DIFF_PATH.write_text(_render_diff(simplified, final, validation), encoding="utf-8")
    return {
        "status": validation["status"],
        "simplified_sha256": sha256_file(SIMPLIFIED_PATH),
        "final_sha256": sha256_file(FINAL_PATH),
        "metrics": validation.get("metrics", {}),
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
