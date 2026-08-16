"""Read-only audit: derive a conservative user-facing vehicle-control candidate set.

Writes only independent audit artifacts under artifacts/. It does not import or mutate
the runtime registry and does not change any production asset.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
VSS_CSV = ROOT / "data/standards/covesa_vss_v6.0/vss.csv"
REGISTRY = ROOT / "data/nlu/spec/intent_registry_unified_v1.yaml"
VHAL = ROOT / "data/standards/android_vhal_android16/properties/VehicleProperty.aidl"
OUT = ROOT / "artifacts/vehicle_control_semantic_expansion_audit_v1"

USER_DOMAINS = ("Vehicle.Body.", "Vehicle.Cabin.", "Vehicle.Chassis.", "Vehicle.ADAS.CruiseControl.", "Vehicle.ADAS.ESC.", "Vehicle.ADAS.ABS.", "Vehicle.ADAS.EBA.", "Vehicle.Powertrain.Transmission.", "Vehicle.Powertrain.TractionBattery.Charging.")
EXCLUDE = re.compile(r"(?:\.System\.|\.ActualPosition$|\.Frequency$|\.Torque|\.Omega|\.Damping|\.Roll|\.RackPosition|\.TargetMode$|\.OffsetTarget|\.Maximum|\.Minimum|\.Distribution|\.Clutch|\.DiffLock|\.IsError$|\.IsStatus$|\.IsAvailable$|\.IsSupported$|\.IsEngaged$)", re.I)
ALLOW_IS = re.compile(r"(?:\.Is(?:Open|Locked|Folded|HeatingOn|Active|On|Signaling|Enabled|AutoApplyEnabled|RecirculationActive|FrontDefrosterActive|RearDefrosterActive|AirConditioningActive|WindowChildLockEngaged)$)", re.I)
AREA_WORDS = {"Front", "Rear", "Left", "Right", "DriverSide", "PassengerSide", "Row1", "Row2", "Row3", "Row4", "Middle", "AnyPosition", "FrontLeft", "FrontMiddle", "FrontRight", "RearLeft", "RearMiddle", "RearRight"}


def norm_path(path: str) -> str:
    parts = [p for p in path.split(".") if p not in AREA_WORDS]
    return ".".join(parts)


def operation(row: dict[str, str]) -> tuple[str, str, str, str]:
    p, dt, allowed, desc = row["Signal"], row["DataType"], row["Allowed"], row["Desc"]
    leaf = p.rsplit(".", 1)[-1]
    target = p.split(".")[2] if len(p.split(".")) > 2 else p
    for token, label in (("Window", "WINDOW"), ("Door", "DOOR"), ("Trunk", "TRUNK"), ("Hood", "HOOD"), ("Mirror", "MIRROR"), ("Seat", "SEAT"), ("Sunroof", "SUNROOF"), ("Shade", "SHADE"), ("SteeringWheel", "STEERING_WHEEL"), ("Windshield", "WIPER"), ("Lights", "LIGHT"), ("HVAC", "HVAC"), ("CruiseControl", "CRUISE"), ("ParkingBrake", "PARKING_BRAKE"), ("Transmission", "GEAR"), ("Horn", "HORN")):
        if token in p:
            target = label
            break
    if leaf in {"IsLocked", "IsChargingCableLocked"}: return "LOCK", target, "锁止状态", "布尔"
    if leaf in {"IsOpen", "IsFolded", "IsFlapOpen"}: return "OPEN_CLOSE", target, "开闭状态", "布尔"
    if leaf in {"IsHeatingOn", "IsAirConditioningActive", "IsRecirculationActive", "IsFrontDefrosterActive", "IsRearDefrosterActive", "IsOn", "IsActive", "IsSignaling"}: return "TOGGLE", target, leaf, "布尔"
    if leaf in {"IsEnabled", "IsAutoApplyEnabled", "IsWindowChildLockEngaged"}: return "ENABLE", target, leaf, "布尔"
    if leaf in {"Switch", "StartStopCharging"}:
        return "SWITCH_MODE", target, leaf, "枚举"
    if dt == "string" or allowed:
        return "SET_MODE", target, leaf, "枚举"
    return "SET", target, leaf, "连续数值"


def surface_rows() -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    raw = list(csv.DictReader(VSS_CSV.open(encoding="utf-8-sig", newline="")))
    actuators = [r for r in raw if r["Type"] == "actuator"]
    selected: list[dict[str, str]] = []
    for r in actuators:
        p = r["Signal"]
        if not p.startswith(USER_DOMAINS) or EXCLUDE.search(p):
            continue
        leaf = p.rsplit(".", 1)[-1]
        if leaf.startswith("Is") and not ALLOW_IS.search(p):
            continue
        if "SwitchEngaged" in p or "SeatBeltHeight" in p:
            continue
        selected.append(r)
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in selected:
        groups[norm_path(r["Signal"])].append(r)
    candidates: list[dict[str, Any]] = []
    for i, (key, rows) in enumerate(sorted(groups.items()), 1):
        base = rows[0]
        act, target, attr, value_type = operation(base)
        paths = [r["Signal"] for r in rows]
        allowed_values = []
        for r in rows:
            value = r["Allowed"].strip("[]").replace("'", "")
            if value:
                allowed_values.extend(value.split(", "))
        allowed = sorted(set(allowed_values))
        mins = [r["Min"] for r in rows if r["Min"]]
        maxs = [r["Max"] for r in rows if r["Max"]]
        expanded = [(act, attr, value_type)]
        if act == "OPEN_CLOSE": expanded = [("OPEN", "开", "布尔"), ("CLOSE", "关", "布尔")]
        elif act == "LOCK": expanded = [("LOCK", "锁定", "布尔"), ("UNLOCK", "解锁", "布尔")]
        elif act == "TOGGLE": expanded = [("TURN_ON", "开启", "布尔"), ("TURN_OFF", "关闭", "布尔")]
        elif act == "ENABLE": expanded = [("ENABLE", "启用", "布尔"), ("DISABLE", "停用", "布尔")]
        elif act == "SWITCH_MODE" and "StartStopCharging" in key: expanded = [("START", "开始充电", "枚举"), ("STOP", "停止充电", "枚举")]
        for op, op_attr, op_type in expanded:
            candidates.append({
                "candidate_id": f"VCC-{len(candidates)+1:03d}",
                "recommended_semantic": f"{op} {target} {op_attr}",
                "action": op, "object": target, "area_capability": "按官方路径区域归并",
                "value_type": op_type, "allowed_or_range": "; ".join(allowed) or f"{min(mins) if mins else ''}..{max(maxs) if maxs else ''}".strip("."),
                "official_primary_source_path": "; ".join(paths),
                "official_primary_type": "actuator", "official_primary_datatype": base["DataType"],
                "official_primary_unit": base["Unit"], "official_primary_description": base["Desc"],
                "official_auxiliary_source": "Android VHAL Android 16 VehicleProperty.aidl (按功能名交叉核验)",
                "source_group_key": key, "raw_actuator_nodes": len(rows),
            })
    return actuators, candidates


def android_names() -> list[str]:
    text = VHAL.read_text(encoding="utf-8")
    return re.findall(r"^\s*([A-Z][A-Z0-9_]+)\s*=", text, re.M)


def android_matches(c: dict[str, Any], names: list[str]) -> str:
    p = c["official_primary_source_path"].upper()
    aliases = {"WINDOW": "WINDOW", "DOOR": "DOOR", "MIRROR": "MIRROR", "SEAT": "SEAT", "STEERING_WHEEL": "STEERING_WHEEL", "WIPER": "WIPER", "LIGHT": "LIGHT", "HVAC": "HVAC", "CRUISE": "CRUISE", "PARKING_BRAKE": "PARKING_BRAKE", "GEAR": "GEAR", "HORN": "HORN", "SUNROOF": "SUNROOF", "CHARGING": "CHARGE", "DEFROST": "DEFROST"}
    keys = {v for k, v in aliases.items() if k in p}
    return "; ".join(n for n in names if any(k in n for k in keys))[:1000]


def match_registry(c: dict[str, Any], intents: list[dict[str, Any]]) -> tuple[str, str, str, bool]:
    s = (c["recommended_semantic"] + " " + c["official_primary_source_path"]).lower()
    matches = []
    for x in intents:
        a, t, attr = str(x.get("canonical_action", "")), str(x.get("canonical_target", "")), str(x.get("control_attribute", ""))
        score = 0
        if c["action"] == a: score += 2
        if t.lower() in s or str(x.get("capability_family", "")).lower().split("_")[0] in s: score += 1
        if attr.lower() in s or attr.lower().replace("_", "") in s.replace("_", ""): score += 1
        if score >= 3: matches.append(x)
    if not matches:
        return "缺失候选", "", "否", False
    formal = [x for x in matches if x.get("runtime_identity") == "FORMAL"]
    known = [x for x in matches if x.get("runtime_identity") == "KNOWN_NON_EXECUTABLE"]
    pool = formal or known
    status = "已覆盖-正式" if formal else "已覆盖-已知"
    duplicate = len(pool) > 1 or any(str(x.get("canonical_action")) != c["action"] for x in pool)
    if duplicate: status = "疑似重复"
    return status, "; ".join(x["intent_id"] for x in pool), "是", duplicate


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    actuators, candidates = surface_rows()
    registry_doc = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    intents = registry_doc["intents"]
    names = android_names()
    for c in candidates:
        c["android_auxiliary_candidates"] = android_matches(c, names)
        status, ids, user, duplicate = match_registry(c, intents)
        c.update({"current_coverage_status": status, "current_intent_ids": ids, "user_controllable": user, "suspected_duplicate": "是" if duplicate else "否", "recommend_add_to_understandable_space": "是" if status in {"缺失候选", "疑似重复"} else "保持现有映射", "complete_safety_contract": "是" if ids and status == "已覆盖-正式" and all(x.get("boundary_contract") is not None for x in intents if x["intent_id"] in ids.split("; ")) else "否/待审"})
    counts = Counter(c["current_coverage_status"] for c in candidates)
    domains = Counter(c["official_primary_source_path"].split(".")[1] if "." in c["official_primary_source_path"] else "其他" for c in candidates)
    summary = {"vss_actuator_raw_count": len(actuators), "filtered_user_controllable_source_group_count": len({c["source_group_key"] for c in candidates}), "merged_user_level_capability_count": len(candidates), "formal_intent_count": sum(x.get("runtime_identity") == "FORMAL" for x in intents), "known_non_executable_count": sum(x.get("runtime_identity") == "KNOWN_NON_EXECUTABLE" for x in intents), "candidate_coverage_counts": dict(counts), "suspected_duplicate_count": counts["疑似重复"], "missing_count": counts["缺失候选"], "missing_by_function_domain": dict(domains), "current_registry_path": str(REGISTRY.relative_to(ROOT)).replace("\\", "/"), "vss_path": str(VSS_CSV.relative_to(ROOT)).replace("\\", "/"), "android_vhal_path": str(VHAL.relative_to(ROOT)).replace("\\", "/"), "method_note": "保守用户可控筛选；排除只读/诊断/维护/内部算法及 MotionManagement 低层目标；区域变体归并为用户级能力。"}
    formal = [x for x in intents if x.get("runtime_identity") == "FORMAL"]
    known = [x for x in intents if x.get("runtime_identity") == "KNOWN_NON_EXECUTABLE"]
    asset_audit = {
        "single_semantic_source": registry_doc.get("single_semantic_source_of_truth"),
        "registry_path": str(REGISTRY.relative_to(ROOT)).replace("\\", "/"),
        "registry_version": registry_doc.get("registry_version"),
        "formal_count": len(formal), "known_non_executable_count": len(known),
        "identity_field": "runtime_identity",
        "formal_identity_value": "FORMAL", "known_identity_value": "KNOWN_NON_EXECUTABLE",
        "saved_vss_mapping": "vss_capability_ids on registry entries",
        "saved_exact_vss_source_path_on_current_entries": False,
        "source_freezes": registry_doc.get("source_freezes"),
        "formal_intents": formal, "known_non_executable_intents": known,
        "action_values": sorted({str(x.get("canonical_action")) for x in intents}),
        "object_values": sorted({str(x.get("canonical_target")) for x in intents}),
        "control_attributes": sorted({str(x.get("control_attribute")) for x in intents}),
        "area_values": sorted({a for x in intents for a in (x.get("allowed_areas") or [])}),
        "value_contracts": sorted({str(x.get("value_contract")) for x in intents}),
        "mode_contracts": sorted({str(x.get("mode_contract")) for x in intents if x.get("mode_contract")}),
    }
    (OUT / "current_asset_audit.json").write_text(json.dumps(asset_audit, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "candidates.json").write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = list(candidates[0])
    with (OUT / "candidates.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(candidates)
    lines = ["# 可理解车控语义空间扩展：第一阶段只读审计", "", "独立审计产物；未修改正式意图、已知意图、能力卡或运行时。", "", "## 汇总", "", "| 指标 | 数值 |", "|---|---:|"]
    for k, v in summary.items():
        if isinstance(v, (int, str)): lines.append(f"| {k} | {v} |")
    lines += ["", "## 候选表", "", "详表见 `candidates.csv` / `candidates.json`；以下为完整字段的机器可读审计表。", ""]
    lines.append("| 编号 | 建议规范语义 | 动作 | 对象 | 数值类型 | 主来源路径 | 当前覆盖 | 意图编号 | 用户可控 | 建议加入 | 完整安全合同 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in candidates:
        lines.append("| {candidate_id} | {recommended_semantic} | {action} | {object} | {value_type} | `{official_primary_source_path}` | {current_coverage_status} | `{current_intent_ids}` | {user_controllable} | {recommend_add_to_understandable_space} | {complete_safety_contract} |".format(**c))
    (OUT / "audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
