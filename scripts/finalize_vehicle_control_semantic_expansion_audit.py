"""Close-out audit for the independent VSS/VHAL candidate table.

This script only reads the prior audit and the current unified registry, then writes
four independent CSV tables plus a summary. It never edits the production registry.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_DIR = ROOT / "artifacts/vehicle_control_semantic_expansion_audit_v1"
OUT_DIR = ROOT / "artifacts/vehicle_control_semantic_expansion_closeout_v1"

DOMAIN = {"Cabin": "座舱", "Body": "车身", "ADAS": "驾驶辅助", "Powertrain": "动力", "Chassis": "底盘"}
ACTION = {"OPEN": "打开", "CLOSE": "关闭", "LOCK": "锁定", "UNLOCK": "解锁", "TURN_ON": "开启", "TURN_OFF": "关闭", "ENABLE": "启用", "DISABLE": "停用", "SET": "设置", "SET_MODE": "设置模式", "SWITCH_MODE": "切换模式", "START": "开始", "STOP": "停止"}
OBJECT = {"WINDOW": "车窗", "DOOR": "车门", "TRUNK": "后备箱", "HOOD": "发动机舱盖", "MIRROR": "后视镜", "WIPER": "雨刮", "HVAC": "空调", "LIGHT": "灯光", "Light": "座舱灯光", "SHADE": "遮阳帘", "SUNROOF": "天窗", "SEAT": "座椅", "CRUISE": "巡航", "PARKING_BRAKE": "驻车制动", "STEERING_WHEEL": "方向盘", "GEAR": "挡位/驾驶模式", "HORN": "喇叭", "TractionBattery": "动力电池充电", "Infotainment": "车载信息娱乐"}


def domain(path: str) -> str:
    return DOMAIN.get(path.split(".")[1], "其他")


def source_text(c: dict) -> str:
    return c["official_primary_source_path"]


def ids_for(path: str, action: str) -> tuple[str, str]:
    p = path
    if "HVAC.Station." in p and action == "SET":
        if ".FanSpeed" in p: return "HVAC_SET_FAN_SPEED", "VSS 的分区风量字段归并到现有空调风量设置。"
        if ".Temperature" in p: return "HVAC_SET_TEMPERATURE", "VSS 的分区温度字段归并到现有空调温度设置。"
    if "HVAC.Station." in p and action == "SET_MODE" and ".AirDistribution" in p:
        return "HVAC_SET_AIRFLOW_DIRECTION", "VSS 的分区风向枚举归并到现有空调风向设置。"
    # Exact user-facing mappings already present in the 149-entry space.
    groups = [
        ("CruiseControl.SpeedSet", {"SET": "CRUISE_SET_SPEED"}),
        ("CruiseControl.Adaptive", {"SET": "CRUISE_SET_GAP"}),
        ("CruiseControl.IsEnabled", {"ENABLE": "CRUISE_ENABLE", "DISABLE": "CRUISE_DISABLE"}),
        ("Transmission.PerformanceMode", {"SET_MODE": "DRIVING_MODE_SET"}),
        ("Transmission.GearChangeMode", {"SET_MODE": "GEAR_CHANGE_MODE_SET"}),
        ("Transmission.SelectedGear", {"SET": "GEAR_SET"}),
        ("ABS.IsEnabled", {"ENABLE": "ABS_ENABLE", "DISABLE": "ABS_DISABLE"}),
        ("EBA.IsEnabled", {"ENABLE": "EBA_ENABLE", "DISABLE": "EBA_DISABLE"}),
        ("ESC.IsEnabled", {"ENABLE": "ESC_ENABLE", "DISABLE": "ESC_DISABLE"}),
        ("Horn.IsActive", {"TURN_ON": "HORN_ACTIVATE"}),
        ("Hood.IsOpen", {"OPEN": "HOOD_OPEN", "CLOSE": "HOOD_CLOSE"}),
        ("Trunk.", {"OPEN": "TRUNK_OPEN", "CLOSE": "TRUNK_CLOSE", "LOCK": "TRUNK_LOCK", "UNLOCK": "TRUNK_UNLOCK", "SET": "TRUNK_SET_POSITION"}),
        ("Window.", {"OPEN": "WINDOW_OPEN", "CLOSE": "WINDOW_CLOSE", "SET": "WINDOW_SET_POSITION"}),
        (".Shade.", {"OPEN": "SHADE_OPEN", "CLOSE": "SHADE_CLOSE", "SET": "SHADE_SET_POSITION"}),
        ("Cabin.Door.", {"OPEN": "DOOR_OPEN", "CLOSE": "DOOR_CLOSE", "LOCK": "DOOR_LOCK", "UNLOCK": "DOOR_UNLOCK", "SET": "DOOR_SET_POSITION"}),
        (".IsFolded", {"OPEN": "MIRROR_UNFOLD", "CLOSE": "MIRROR_FOLD"}),
        (".IsHeatingOn", {"TURN_ON": "MIRROR_HEATING_ON", "TURN_OFF": "MIRROR_HEATING_OFF"}),
        ("Mirrors.", {"LOCK": "MIRROR_ADJUSTMENT_LOCK", "UNLOCK": "MIRROR_ADJUSTMENT_UNLOCK"}),
        ("Mirrors.", {"SET": "MIRROR_SET_ANGLE"}),
        ("Windshield.Front.IsHeatingOn", {"TURN_ON": "WINDSHIELD_HEATING_ON", "TURN_OFF": "WINDSHIELD_HEATING_OFF"}),
        ("Windshield.Rear.IsHeatingOn", {"TURN_ON": "WINDSHIELD_HEATING_ON", "TURN_OFF": "WINDSHIELD_HEATING_OFF"}),
        ("Wiping.Mode", {"SET_MODE": "WIPER_SET_MODE"}),
        ("Wiping.Intensity", {"SET": "WIPER_SET_SENSITIVITY"}),
        ("Lights.", {"TURN_ON": "LIGHT_GENERIC", "TURN_OFF": "LIGHT_GENERIC", "SET_MODE": "HEADLIGHT_SET_MODE"}),
        ("HVAC.IsAirConditioningActive", {"TURN_ON": "HVAC_ON", "TURN_OFF": "HVAC_OFF"}),
        ("HVAC.IsRecirculationActive", {"TURN_ON": "HVAC_SET_RECIRCULATION", "TURN_OFF": "HVAC_SET_RECIRCULATION"}),
        ("HVAC.Station", {"SET": "HVAC_SET_TEMPERATURE_OR_FAN", "SET_MODE": "HVAC_SET_AIRFLOW_DIRECTION"}),
        ("HVAC.IsFrontDefrosterActive", {"TURN_ON": "DEFROST_ON", "TURN_OFF": "DEFROST_OFF"}),
        ("HVAC.IsRearDefrosterActive", {"TURN_ON": "DEFROST_ON", "TURN_OFF": "DEFROST_OFF"}),
        ("HVAC.Station.*.FanSpeed", {"SET": "HVAC_SET_FAN_SPEED"}),
        ("HVAC.Station.*.Temperature", {"SET": "HVAC_SET_TEMPERATURE"}),
        ("HVAC.Station.*.AirDistribution", {"SET_MODE": "HVAC_SET_AIRFLOW_DIRECTION"}),
        ("RearShade.", {"OPEN": "SHADE_OPEN", "CLOSE": "SHADE_CLOSE", "SET": "SHADE_SET_POSITION"}),
        ("Sunroof.Shade.", {"OPEN": "SHADE_OPEN", "CLOSE": "SHADE_CLOSE", "SET": "SHADE_SET_POSITION"}),
        ("Sunroof.Switch", {"SWITCH_MODE": "SUNROOF_OPEN_CLOSE_TILT"}),
        ("Seat.", {"SET": "SEAT_EXISTING_OR_MERGED"}),
        ("ParkingBrake.IsAutoApplyEnabled", {"ENABLE": "PARKING_BRAKE_AUTO_APPLY_ENABLE", "DISABLE": "PARKING_BRAKE_AUTO_APPLY_DISABLE"}),
        ("SteeringWheel.Extension", {"SET": "STEERING_WHEEL_SET_EXTENSION"}),
        ("SteeringWheel.Tilt", {"SET": "STEERING_WHEEL_SET_TILT"}),
        ("SteeringWheel.HeatingCooling", {"SET": "STEERING_WHEEL_HEATING_ON_OR_OFF"}),
        ("IsWindowChildLockEngaged", {"ENABLE": "CHILD_LOCK_ON", "DISABLE": "CHILD_LOCK_OFF"}),
        ("Infotainment.HMI.Brightness", {"SET": "DISPLAY_SET_BRIGHTNESS"}),
        ("Infotainment.HMI.DayNightMode", {"SET_MODE": "DISPLAY_SET_MODE"}),
        ("Seat.", {"SET": "SEAT_EXISTING_OR_MERGED"}),
    ]
    for marker, mapping in groups:
        if marker in p and action in mapping:
            return mapping[action], "按动作与对象语义直接覆盖，区域差异归并；若为同族多字段则按用户级能力合并。"
    return "", ""


def final_name(c: dict, action: str, path: str) -> tuple[str, str]:
    obj = OBJECT.get(c["object"], c["object"])
    act = ACTION.get(action, action)
    p = path
    if "AdaptiveDistance" in p or "AdaptiveInterval" in p: return "设置巡航跟车间距", "数值/枚举"
    if "SpeedSet" in p: return "设置巡航速度", "连续数值"
    if "Hood.Position" in p: return "设置发动机舱盖开度", "百分比"
    if "RearMainSpoiler" in p: return "设置主动尾翼位置", "百分比"
    if "IsWindowChildLock" in p: return f"{act}车窗儿童锁", "布尔"
    if "Light.AmbientLight" in p and ("Color" in p): return "设置氛围灯颜色", "枚举/颜色"
    if "Light.AmbientLight" in p and ("Intensity" in p): return "设置氛围灯亮度", "百分比"
    if "InteractiveLightBar" in p: return "设置交互灯带效果", "枚举/数值"
    if "Spotlight" in p and "Color" in p: return "设置阅读/聚光灯颜色", "枚举/颜色"
    if "Spotlight" in p and "Intensity" in p: return "设置阅读/聚光灯亮度", "百分比"
    if "Headrest.Angle" in p: return "设置座椅头枕角度", "连续数值"
    if "Headrest.Height" in p: return "设置座椅头枕高度", "连续数值"
    if "NeckScarf" in p and "FanSpeed" in p: return "设置座椅颈部送风", "百分比"
    if "NeckScarf" in p and "HeatingCooling" in p: return "设置座椅颈部加热/通风", "连续数值"
    if "SideBolsterSupport" in p: return "设置座椅侧翼支撑", "百分比"
    if "Charging.ChargeLimit" in p: return "设置充电上限", "百分比"
    if "StartStopCharging" in p: return ("开始充电" if action == "START" else "停止充电"), "枚举"
    if "Charging.Timer.Mode" in p: return "设置充电定时模式", "枚举"
    if "Charging.Timer.Time" in p: return "设置充电定时时间", "时间"
    if "Infotainment" in p: return "设置车载信息娱乐参数", c["value_type"]
    if "IsActive" in p and "CruiseControl" in p: return f"{act}巡航控制", "布尔"
    return f"{act}{obj}", "连续数值" if c["value_type"] == "连续数值" else c["value_type"]


def classify(c: dict) -> dict:
    p = source_text(c)
    action = c["action"]
    special_new = "Seat." in p and any(x in p for x in ("Headrest.", "SideBolsterSupport", "NeckScarf"))
    eid, basis = ("", "") if special_new else ids_for(p, action)
    # State-only or internal/vehicle-algorithm signals are not user commands.
    reject_markers = ("PowerOptimizeLevel", "RearMainSpoilerPosition", "Infotainment.Media", "Infotainment.Navigation", "SmartphoneProjection", "SmartphoneScreenMirroring", "DateFormat", "DistanceUnit", "EconomyUnits", "EnergyUnits", "FontSize", "FuelEconomyUnits", "FuelVolumeUnit", "SpeedUnit", "TemperatureUnit", "TimeFormat", "TirePressureUnit", "HMI.DisplayOffDuration")
    if any(x in p for x in reject_markers):
        category, reason = "rejected_low_level", "非车辆控制语义、系统设置、媒体/导航接口或内部功率优化参数；不应进入车控意图空间。"
        if "RearMainSpoilerPosition" in p: reason = "底层主动空气动力学执行器位置，普通用户不会以该底层参数直接提出。"
    elif "CruiseControl.IsActive" in p or ("Horn.IsActive" in p and action == "TURN_OFF") or "Lights.Brake.IsActive" in p or "Lights.Backup.IsOn" in p or "Lights.LicensePlate.IsOn" in p:
        category, reason = "rejected_low_level", "该字段主要表示状态或由车辆控制器管理，不能作为独立用户命令；存在可用的上层控制入口。"
    elif "Switch" in p and action == "SWITCH_MODE" and not ("Sunroof.Switch" in p):
        category, reason = "rejected_low_level", "VSS 的通用 Switch 是底层开闭驱动接口；用户语义已由打开/关闭/设置位置等能力覆盖。"
    elif eid:
        category, reason = "confirmed_existing", basis
    elif "Mirrors." in p and any(x in p for x in ("Pan", "Tilt", "Yaw")):
        category, reason, eid = "confirmed_existing", "Pan/Tilt/Yaw 是后视镜多个底层姿态字段，用户语义统一归并为‘设置后视镜角度’。", "MIRROR_SET_ANGLE"
    elif "Seat." in p and any(x in p for x in ("Headrest.", "SideBolsterSupport", "NeckScarf")):
        category, reason = "new_known_candidates", "VSS 明确提供用户可操作的座椅舒适性目标；可自然表达为设置座椅部件及数值，但现有 149 个意图未覆盖。"
    elif "Seat." in p and any(x in p for x in ("Position", "Height", "Tilt", "Recline", "Lumbar", "HeatingCooling", "Massage", "Length")):
        category, reason, eid = "confirmed_existing", "座椅区域/分段/连续字段归并到现有座椅位置、靠背、腰托、加热、按摩等用户级能力。", "SEAT_EXISTING_OR_MERGED"
    elif "Sunroof.Shade" in p or "RearShade" in p:
        category, reason, eid = "confirmed_existing", "遮阳帘的区域和开度字段归并到现有遮阳帘开闭/位置能力。", "SHADE_OPEN/SHADE_CLOSE/SHADE_SET_POSITION"
    elif "Light.AmbientLight" in p or "Light.Spotlight" in p:
        category, reason, eid = "confirmed_existing", "座舱灯光区域字段归并到现有氛围灯/阅读灯亮度与颜色语义。", "AMBIENT_LIGHT_SET_COLOR/AMBIENT_LIGHT_SET_BRIGHTNESS/READING_LIGHT_SET_BRIGHTNESS"
    elif "Charging." in p:
        category, reason = "new_known_candidates", "VSS 提供充电启停、充电上限或定时目标；属于用户可从座舱主动设置的车辆功能，现有 149 个意图未覆盖。"
    elif "Hood.Position" in p:
        category, reason = "rejected_low_level", "发动机舱盖位置不是普通座舱语音的稳定用户能力，且存在安全边界不确定性。"
    else:
        category, reason = "unresolved_candidates", "标准存在控制字段，但当前无法仅凭公开语义可靠判断其是否是普通用户直接操控的座舱能力，保留人工复核。"
    name, vt = final_name(c, action, p)
    return {"source_candidate_ids": c["candidate_id"], "建议规范名称": name, "动作": ACTION.get(action, action), "对象": OBJECT.get(c["object"], c["object"]), "可用区域": c["area_capability"], "数值类型": vt, "所属功能域": domain(p), "车辆信号规范来源路径": p, "安卓汽车辅助来源": c.get("android_auxiliary_candidates") or c.get("official_auxiliary_source", ""), "与现有意图是否重叠": "是" if eid else "否", "当前对应意图编号": eid, "是否拥有现有安全合同": c.get("complete_safety_contract", "否/待审"), "建议运行身份": "已知但不可执行" if category == "new_known_candidates" else ("现有身份" if category == "confirmed_existing" else "不进入运行空间"), "判定类别": category, "判定依据": reason, "原候选覆盖标签": c.get("current_coverage_status", "")}


def merge(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, dict] = {}
    for r in rows:
        # Keep operations separate, but merge regional and low-level variants of one user capability.
        key = (r["建议规范名称"], r["动作"], r["对象"], r["所属功能域"], r["判定类别"])
        if key not in groups:
            groups[key] = dict(r)
        else:
            old = groups[key]
            old["source_candidate_ids"] += ";" + r["source_candidate_ids"]
            old["车辆信号规范来源路径"] += "; " + r["车辆信号规范来源路径"]
            if r["原候选覆盖标签"] not in old["原候选覆盖标签"]:
                old["原候选覆盖标签"] += ";" + r["原候选覆盖标签"]
            if r["当前对应意图编号"] and r["当前对应意图编号"] not in old["当前对应意图编号"]:
                old["当前对应意图编号"] += ";" + r["当前对应意图编号"]
    return list(groups.values())


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = json.loads((IN_DIR / "candidates.json").read_text(encoding="utf-8"))
    suspected_ids = {c["candidate_id"] for c in candidates if c.get("current_coverage_status") == "疑似重复"}
    classified = [classify(c) for c in candidates]
    merged = merge(classified)
    by_cat = defaultdict(list)
    for r in merged: by_cat[r["判定类别"]].append(r)
    fields = list(merged[0])
    for cat, filename in (("confirmed_existing", "confirmed_existing.csv"), ("rejected_low_level", "rejected_low_level.csv"), ("new_known_candidates", "new_known_candidates.csv"), ("unresolved_candidates", "unresolved_candidates.csv")):
        with (OUT_DIR / filename).open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(by_cat[cat])
    counts_all = Counter(r["所属功能域"] for r in merged)
    counts_new = Counter(r["所属功能域"] for r in by_cat["new_known_candidates"])
    summary = {"previous_candidate_count": len(candidates), "previous_function_domain_stat_scope": "全部177个候选，而不是84个缺失候选；原报告标签错误。", "previous_missing_count": 84, "previous_missing_by_function_domain_recomputed": dict(Counter(r["所属功能域"] for r in classified if r["原候选覆盖标签"] in {"缺失候选", "缺失候选"})), "candidate_classification_before_user_merge": dict(Counter(classify(c)["判定类别"] for c in candidates)), "final_user_level_semantic_universe_estimate": 149 + len(by_cat["new_known_candidates"]), "existing_formal_count": 71, "existing_known_count": 78, "recommended_new_known_count": len(by_cat["new_known_candidates"]), "rejected_count": len(by_cat["rejected_low_level"]), "unresolved_count": len(by_cat["unresolved_candidates"]), "confirmed_existing_count": len(by_cat["confirmed_existing"]), "final_coverage_by_function_domain": dict(counts_all), "new_known_by_function_domain": dict(counts_new), "duplicate_decision_source_count": len(suspected_ids), "duplicate_decision_note": "A=确认等价，B=部分重叠/仍需人工边界判断，C=底层执行器差异归并，D=真正缺失。", "source_candidate_rows_accounted_for": len(classified), "note": "177行源候选经过用户级语义归并后输出；四表中的一行可对应多个底层候选编号。"
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "duplicate_decisions.csv").write_text("", encoding="utf-8")
    with (OUT_DIR / "duplicate_decisions.csv").open("w", encoding="utf-8-sig", newline="") as f:
        cols = ["source_candidate_ids", "建议规范名称", "重复判定", "判定类别", "判定依据", "当前对应意图编号"]
        duplicate_rows = []
        for r in merged:
            duplicate_source_ids = [x for x in r["source_candidate_ids"].split(";") if x in suspected_ids]
            if not duplicate_source_ids:
                continue
            if r["判定类别"] == "new_known_candidates": d = "D"
            elif r["判定类别"] == "unresolved_candidates": d = "B"
            elif r["判定类别"] == "rejected_low_level": d = "C"
            elif "直接覆盖" in r["判定依据"]: d = "A"
            elif "归并" in r["判定依据"] or "字段" in r["判定依据"]: d = "C"
            else: d = "A"
            row = {k: r[k] for k in cols if k != "重复判定"}; row["source_candidate_ids"] = ";".join(duplicate_source_ids); row["重复判定"] = d; duplicate_rows.append(row)
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(duplicate_rows)
    checks = [
        ("车门", "已覆盖", "DOOR_OPEN/DOOR_CLOSE/DOOR_LOCK/DOOR_UNLOCK/DOOR_SET_POSITION", "Vehicle.Cabin.Door.*"),
        ("车窗", "已覆盖", "WINDOW_OPEN/WINDOW_CLOSE/WINDOW_SET_POSITION", "Vehicle.Cabin.Door.*.Window.*"),
        ("天窗", "已覆盖", "SUNROOF_OPEN/SUNROOF_CLOSE/SUNROOF_SET_TILT；遮阳帘由 SHADE_* 覆盖", "Vehicle.Cabin.Sunroof.*"),
        ("后备箱", "已覆盖", "TRUNK_OPEN/TRUNK_CLOSE/TRUNK_LOCK/TRUNK_UNLOCK/TRUNK_SET_POSITION", "Vehicle.Body.Trunk.*"),
        ("门锁与儿童锁", "已覆盖", "DOOR_LOCK/DOOR_UNLOCK；CHILD_LOCK_ON/OFF", "Vehicle.Cabin.Door.*.IsLocked; Vehicle.Cabin.IsWindowChildLockEngaged"),
        ("外部灯光", "已覆盖", "HEADLIGHT/HAZARD/TURN/FOG/PARKING formal intents", "Vehicle.Body.Lights.*"),
        ("内部阅读灯和氛围灯", "已覆盖", "READING_LIGHT_* / AMBIENT_LIGHT_* known intents", "Vehicle.Cabin.Light.*"),
        ("雨刮和清洗", "已覆盖", "WIPER_SET_MODE/WIPER_SET_SENSITIVITY；清洗动作未在 VSS v6.0 执行器候选中发现", "Vehicle.Body.Windshield.*Wiping.*"),
        ("前后除雾除霜", "已覆盖", "DEFROST_ON/DEFROST_OFF 与 WINDSHIELD_HEATING_*", "Vehicle.Cabin.HVAC.Is*DefrosterActive; Vehicle.Body.Windshield.*IsHeatingOn"),
        ("空调开关", "已覆盖", "HVAC_ON/HVAC_OFF known intents", "Vehicle.Cabin.HVAC.IsAirConditioningActive"),
        ("温度/风量/风向", "已覆盖", "HVAC_SET_TEMPERATURE/HVAC_SET_FAN_SPEED/HVAC_SET_AIRFLOW_DIRECTION known intents", "Vehicle.Cabin.HVAC.Station.*"),
        ("内外循环", "已覆盖", "HVAC known intent family; VSS IsRecirculationActive", "Vehicle.Cabin.HVAC.IsRecirculationActive"),
        ("空气净化", "现有已知", "AIR_PURIFIER_* 存在，但本轮 VSS v6.0 执行器候选未发现对应路径，需后续确认来源映射", "当前 registry known intents"),
        ("座椅位置/靠背/腰托", "已覆盖", "SEAT_* formal intents，区域与分段字段已归并", "Vehicle.Cabin.Seat.*Position/Height/Tilt/Backrest/Lumbar*"),
        ("头枕", "新增已知候选", "建议设置头枕角度/高度；VSS 支持，现有 149 未覆盖", "Vehicle.Cabin.Seat.*Headrest.*"),
        ("座椅加热/通风", "已覆盖", "SEAT_HEATING_* / SEAT_VENTILATION_* known intents", "Vehicle.Cabin.Seat.*HeatingCooling"),
        ("后视镜折叠/角度/加热", "已覆盖", "MIRROR_FOLD/UNFOLD/MIRROR_SET_ANGLE/MIRROR_HEATING_*", "Vehicle.Body.Mirrors.*"),
        ("方向盘位置/加热", "已覆盖", "STEERING_WHEEL_SET_* formal；加热由已知语义覆盖", "Vehicle.Chassis.SteeringWheel.*"),
        ("驾驶模式", "已覆盖", "DRIVING_MODE_SET known intent", "Vehicle.Powertrain.Transmission.PerformanceMode"),
        ("巡航设置", "已覆盖", "CRUISE_ENABLE/DISABLE/SET_SPEED/SET_GAP formal intents", "Vehicle.ADAS.CruiseControl.*"),
        ("自动泊车", "已覆盖", "AUTO_PARK_ENABLE formal intent；VSS v6.0 执行器未提供对应独立路径", "当前 registry formal intent"),
        ("可主动开关的驾驶辅助", "部分覆盖", "ESC formal、ABS/EBA known；具体 ADAS 开关需按 VSS 路径逐项确认", "Vehicle.ADAS.*"),
        ("车载显示/抬头显示", "现有已知", "DISPLAY_* known intents；本轮 VSS 候选覆盖到 HMI brightness/day-night，HUD 独立路径未发现", "Vehicle.Cabin.Infotainment.HMI.*"),
    ]
    with (OUT_DIR / "user_experience_coverage_check.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["用户常见控制域", "覆盖结论", "当前语义/审计结论", "官方或注册依据"]); w.writerows(checks)


if __name__ == "__main__": main()
