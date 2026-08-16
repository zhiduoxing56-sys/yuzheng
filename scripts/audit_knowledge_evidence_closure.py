from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "证据" / "knowledge_evidence_alignment_v1.yaml"
REPORT_JSON_PATH = ROOT / "证据" / "knowledge_evidence_closure_v1.json"
REPORT_MD_PATH = ROOT / "证据" / "knowledge_evidence_closure_v1.md"
REGISTRY_PATH = ROOT / "data" / "nlu" / "spec" / "intent_registry_unified_v1.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return value


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"JSONL row must be an object: {path}:{line_number}")
        rows.append(row)
    return rows


def _migrate_aliases_and_conditions(
    path: Path,
    aliases: dict[str, str],
    expected_occurrences: dict[str, int],
    stationary_repairs: set[str],
) -> dict[str, int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    migrated = Counter({name: 0 for name in aliases})
    output = []
    for line in lines:
        if not line.strip():
            output.append(line)
            continue
        row = json.loads(line)
        for field in ("required_evidence", "optional_evidence"):
            values = []
            for value in row.get(field) or []:
                replacement = aliases.get(value, value)
                if replacement != value:
                    migrated[value] += 1
                if replacement not in values:
                    values.append(replacement)
            row[field] = values
        required = set(row.get("required_evidence") or [])
        row["optional_evidence"] = [
            value for value in row.get("optional_evidence") or [] if value not in required
        ]
        if row["node_id"] in stationary_repairs:
            conditions = list(row.get("conditions") or [])
            if "VEHICLE_STATIONARY" not in conditions:
                conditions.insert(0, "VEHICLE_STATIONARY")
            row["conditions"] = conditions
        if "VEHICLE_STATIONARY" in (row.get("conditions") or []):
            evidence = set(row.get("required_evidence") or []) | set(row.get("optional_evidence") or [])
            if "VEHICLE_SPEED" not in evidence:
                row["optional_evidence"].append("VEHICLE_SPEED")
        output.append(json.dumps(row, ensure_ascii=False))
    for name, expected in expected_occurrences.items():
        if migrated[name] not in {0, expected}:
            raise ValueError(
                f"alias occurrence drift for {name}: expected 0 or {expected}, got {migrated[name]}"
            )
    path.write_text("\n".join(output) + "\n", encoding="utf-8", newline="\n")
    return dict(migrated)


def _classify_reference(
    evidence_type: str,
    canonical_types: set[str],
    aliases: dict[str, str],
    gaps: set[str],
    non_realtime: set[str],
) -> str:
    if evidence_type in canonical_types:
        return "CANONICAL"
    if evidence_type in aliases:
        return "A_OLD_NAME"
    if evidence_type in gaps:
        return "B_EVIDENCE_SPACE_GAP"
    if evidence_type in non_realtime:
        return "C_NON_REALTIME_PHYSICAL_EVIDENCE"
    return "UNCLASSIFIED"


def audit(*, apply_aliases: bool = False) -> dict[str, Any]:
    policy = _load_yaml(POLICY_PATH)
    production_path = ROOT / str(policy["production_nodes"])
    catalog = _load_yaml(ROOT / str(policy["canonical_catalog"]))
    canonical_types = set(catalog["evidence_types"])
    aliases = {str(k): str(v) for k, v in policy["class_a_aliases"].items()}
    expected = {str(k): int(v) for k, v in policy["class_a_expected_occurrences"].items()}
    gaps = set(policy["class_b_evidence_space_gaps"])
    non_realtime = set(policy["class_c_non_realtime_physical_evidence"])
    physical_nodes = set(map(str, policy["physical_safety_nodes"]))
    nonphysical_nodes = set(map(str, policy["non_physical_nodes"]))
    stationary_repairs = set(map(str, policy["stationary_condition_repairs"]))
    stationary_predicate = policy["condition_predicates"]["VEHICLE_STATIONARY"]

    if set(aliases) != set(expected):
        raise ValueError("class A aliases and expected occurrence keys must match")
    if (set(aliases) & gaps) or (set(aliases) & non_realtime) or (gaps & non_realtime):
        raise ValueError("A/B/C evidence classifications must be disjoint")
    if any(target not in canonical_types for target in aliases.values()):
        raise ValueError("every class A target must be canonical")
    if physical_nodes & nonphysical_nodes:
        raise ValueError("physical and non-physical node classifications must be disjoint")
    if stationary_predicate != {
        "evidence_type": "VEHICLE_SPEED", "operator": "EQ", "value": 0, "unit": "km/h"
    }:
        raise ValueError("VEHICLE_STATIONARY must mean VEHICLE_SPEED == 0 km/h")

    migrated = (
        _migrate_aliases_and_conditions(production_path, aliases, expected, stationary_repairs)
        if apply_aliases
        else {name: 0 for name in aliases}
    )
    rows = _load_jsonl(production_path)
    if len(rows) != 120:
        raise ValueError(f"production knowledge node count must be 120, got {len(rows)}")
    production_ids = {str(row["node_id"]) for row in rows}
    if physical_nodes | nonphysical_nodes != production_ids:
        missing = sorted(production_ids - physical_nodes - nonphysical_nodes)
        stale = sorted((physical_nodes | nonphysical_nodes) - production_ids)
        raise ValueError(f"semantic classification must cover exactly 120 nodes; missing={missing}, stale={stale}")

    registry = _load_yaml(REGISTRY_PATH)
    action_identity = {
        str(item["intent_id"]): str(item["runtime_identity"])
        for item in registry["intents"]
    }
    nodes = []
    occurrences: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()
    physical_required_unknown = []
    physical_optional_unknown = []
    stationary_violations = []

    for row in rows:
        node_id = str(row["node_id"])
        action = str(row.get("canonical_action") or "")
        identity = action_identity.get(action)
        action_status = (
            "FORMAL_ONLINE_ACTION" if identity == "FORMAL"
            else "KNOWN_NON_EXECUTABLE" if identity == "KNOWN_NON_EXECUTABLE"
            else "OUTSIDE_REALTIME_ACTION_REGISTRY"
        )
        plane = "PHYSICAL_SAFETY" if node_id in physical_nodes else "NON_PHYSICAL"
        fields = {}
        noncanonical = []
        for field in ("required_evidence", "optional_evidence"):
            items = []
            for evidence_type in map(str, row.get(field) or []):
                classification = _classify_reference(
                    evidence_type, canonical_types, aliases, gaps, non_realtime
                )
                item = {"evidence_type": evidence_type, "classification": classification}
                items.append(item)
                occurrences[evidence_type] += 1
                classification_counts[classification] += 1
                if classification != "CANONICAL":
                    noncanonical.append({"field": field, **item})
            fields[field] = items

        overlap = set(row.get("required_evidence") or []) & set(row.get("optional_evidence") or [])
        if overlap:
            raise ValueError(f"required/optional overlap in {node_id}: {sorted(overlap)}")
        unknown = [item for item in noncanonical if item["classification"] == "UNCLASSIFIED"]
        if unknown:
            raise ValueError(f"unclassified evidence references in {node_id}: {unknown}")
        if plane == "PHYSICAL_SAFETY":
            physical_required_unknown.extend(
                {"node_id": node_id, **item} for item in noncanonical if item["field"] == "required_evidence"
            )
            physical_optional_unknown.extend(
                {"node_id": node_id, **item} for item in noncanonical if item["field"] == "optional_evidence"
            )

        conditions = set(map(str, row.get("conditions") or []))
        evidence = set(row.get("required_evidence") or []) | set(row.get("optional_evidence") or [])
        if "VEHICLE_STATIONARY" in conditions and "VEHICLE_SPEED" not in evidence:
            stationary_violations.append(node_id)
        nodes.append({
            "node_id": node_id,
            "knowledge_id": str(row.get("metadata", {}).get("knowledge_id") or ""),
            "canonical_action": action,
            "action_status": action_status,
            "knowledge_plane": plane,
            **fields,
            "noncanonical_references": noncanonical,
            "online_physical_eligible": plane == "PHYSICAL_SAFETY" and not noncanonical,
        })

    remaining_aliases = {name: occurrences[name] for name in aliases if occurrences[name]}
    if remaining_aliases:
        raise ValueError(f"class A aliases remain after migration: {remaining_aliases}")
    if physical_required_unknown or physical_optional_unknown:
        raise ValueError(
            f"physical nodes must be a subset of 38 Evidence; required={physical_required_unknown}, optional={physical_optional_unknown}"
        )
    if stationary_violations:
        raise ValueError(f"stationary condition lost VEHICLE_SPEED evidence: {stationary_violations}")
    if not stationary_repairs <= {
        str(row["node_id"]) for row in rows if "VEHICLE_STATIONARY" in (row.get("conditions") or [])
    }:
        raise ValueError("stationary condition repair did not persist")

    observed_noncanonical = {name for name in occurrences if name not in canonical_types}
    if not observed_noncanonical <= gaps | non_realtime:
        raise ValueError("post-migration noncanonical references are not fully classified")
    plane_counts = Counter(node["knowledge_plane"] for node in nodes)
    action_counts = Counter(node["action_status"] for node in nodes)
    physical_outside_registry = [
        node["node_id"] for node in nodes
        if node["knowledge_plane"] == "PHYSICAL_SAFETY"
        and node["action_status"] != "FORMAL_ONLINE_ACTION"
    ]
    return {
        "version": "knowledge-evidence-closure-v1.0.1",
        "production_node_count": len(rows),
        "canonical_evidence_type_count": len(canonical_types),
        "knowledge_plane_counts": dict(sorted(plane_counts.items())),
        "action_status_counts": dict(sorted(action_counts.items())),
        "classification_basis": "EXPLICIT_NODE_SEMANTICS_NOT_ACTION_FORMALITY",
        "physical_nodes_outside_action_registry": physical_outside_registry,
        "class_a_aliases": aliases,
        "class_a_expected_historical_occurrences": expected,
        "class_a_migrated_this_run": migrated,
        "class_b_evidence_space_gaps": sorted(gaps),
        "class_c_non_realtime_physical_evidence": sorted(non_realtime),
        "post_migration_noncanonical_ids": sorted(observed_noncanonical),
        "classification_occurrence_counts": dict(sorted(classification_counts.items())),
        "condition_predicates": {"VEHICLE_STATIONARY": stationary_predicate},
        "stationary_condition_violation_count": len(stationary_violations),
        "online_physical_eligible_count": plane_counts["PHYSICAL_SAFETY"],
        "online_physical_excluded_count": plane_counts["NON_PHYSICAL"],
        "physical_required_unknown_count": len(physical_required_unknown),
        "physical_optional_unknown_count": len(physical_optional_unknown),
        "unknown_reference_count": classification_counts["UNCLASSIFIED"],
        "online_required_evidence_silent_loss_risk_count": len(physical_required_unknown),
        "nodes": nodes,
    }


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# 120 KnowledgeNode × 38 Evidence 闭环验收（v1.0.1）", "",
        "## 结论", "",
        f"- 节点：**{result['production_node_count']}**；canonical Evidence：**{result['canonical_evidence_type_count']}**。",
        f"- 语义分类：Physical Safety **{result['knowledge_plane_counts']['PHYSICAL_SAFETY']}**；Non-Physical **{result['knowledge_plane_counts']['NON_PHYSICAL']}**。",
        "- 分类依据：逐节点语义裁决，不使用 FORMAL/非 FORMAL 作为 Physical 判据。",
        f"- Physical required unknown：**{result['physical_required_unknown_count']}**；optional unknown：**{result['physical_optional_unknown_count']}**；全局 unknown：**{result['unknown_reference_count']}**。",
        f"- VEHICLE_STATIONARY 条件违规：**{result['stationary_condition_violation_count']}**；其谓词固定为 `VEHICLE_SPEED == 0 km/h`。",
        "", "## 五个争议状态裁决", "",
        "- `AUTHENTICATION_STATE → AUTHORIZATION_STATE`（现有认证/授权运行时状态）。",
        "- `ADS_STATE → SYSTEM_MODE`（车辆自动驾驶/系统模式）。",
        "- `SYSTEM_FAILURE_STATE → SYSTEM_MODE`（degraded/failure 模式）。",
        "- `EMERGENCY_STATE → SYSTEM_MODE`（故障/安全约束模式）。",
        "- `BATTERY_STATE → EVIDENCE_SPACE_GAP`；当前只出现在 Non-Physical OTA 节点，不进入在线 Physical Trusted 需求。",
        "", "## Physical Safety LAW", "",
    ]
    lines.extend(f"- `{node_id}`" for node_id in result["physical_nodes_outside_action_registry"])
    lines.extend([
        "", "## 逐节点验收", "",
        "| node_id | knowledge_plane | canonical_action | action_status | required | optional | non-canonical |",
        "|---|---|---|---|---|---|---|",
    ])
    for node in result["nodes"]:
        required = ", ".join(item["evidence_type"] for item in node["required_evidence"]) or "—"
        optional = ", ".join(item["evidence_type"] for item in node["optional_evidence"]) or "—"
        noncanonical = ", ".join(
            f"{item['evidence_type']}={item['classification']}" for item in node["noncanonical_references"]
        ) or "—"
        lines.append(
            f"| {node['node_id']} | {node['knowledge_plane']} | {node['canonical_action']} | "
            f"{node['action_status']} | {required} | {optional} | {noncanonical} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply-aliases", action="store_true")
    args = parser.parse_args()
    result = audit(apply_aliases=args.apply_aliases)
    REPORT_JSON_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD_PATH.write_text(render_markdown(result), encoding="utf-8", newline="\n")
    print(json.dumps({
        "nodes": result["production_node_count"],
        "physical": result["knowledge_plane_counts"]["PHYSICAL_SAFETY"],
        "non_physical": result["knowledge_plane_counts"]["NON_PHYSICAL"],
        "unknown": result["unknown_reference_count"],
        "physical_required_unknown": result["physical_required_unknown_count"],
        "physical_optional_unknown": result["physical_optional_unknown_count"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
