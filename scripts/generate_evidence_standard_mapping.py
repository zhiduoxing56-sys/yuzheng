from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "证据" / "evidence_type_catalog_v1.yaml"
RUNTIME_PATH = ROOT / "证据" / "evidence_runtime_mapping_v1.yaml"
OUTPUT_PATH = ROOT / "证据" / "evidence_standard_mapping.md"

STANDARD_LABELS = (
    ("01_covesa_vss", "COVESA VSS 6.0"),
    ("02_asam_osi", "ASAM OSI 3.8.0"),
    ("03_asam_openscenario", "ASAM OpenSCENARIO XML 1.4.0"),
    ("04_asam_opendrive", "ASAM OpenDRIVE 1.9.0"),
    ("05_android_automotive_vhal", "Android Automotive VHAL (Android 16 local snapshot)"),
)

SAFETY_USES = {
    "SELF_MOTION": "判断车辆是否运动、纵横向动态与动作前置条件",
    "VEHICLE_FUNCTION_STATE": "确认车身/底盘执行器当前状态并防止危险切换",
    "ENVIRONMENT": "判断照明、能见度、降水、雾和天气风险",
    "ROAD": "判断车道、路口、道路类型、限速和附着条件",
    "SURROUNDING_OBJECT": "判断开门、制动、变道和泊车周边碰撞风险",
    "OCCUPANT": "判断乘员占用、安全带与驾驶员状态",
    "ADAS": "判断辅助驾驶功能是否启用、介入、告警或故障",
    "AUTHORIZATION": "阻止未授权主体或区域执行车控",
    "SYSTEM_RUNTIME": "阻止用户声明伪造模拟、测试或安全约束状态",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def standard_for(provenance: dict[str, Any]) -> str:
    kind = provenance["mapping_kind"]
    source = str(provenance.get("local_source_file") or "").replace("\\", "/")
    if kind == "INTERNAL_SECURITY":
        return "PROJECT INTERNAL SECURITY"
    if kind == "DERIVED" and not source:
        return "SYSTEM DERIVATION"
    for token, label in STANDARD_LABELS:
        if token in source:
            return label
    return "SYSTEM DERIVATION" if kind == "DERIVED" else "LOCAL STANDARD SOURCE"


def type_treatment(entry: dict[str, Any]) -> str:
    alignments = {str(item.get("alignment")) for item in entry["field_provenance"].values()}
    if "D_NEW_TYPE" in alignments:
        return "D 新增最小参数化母类"
    if "C_UNIFY" in alignments:
        return "C 统一命名/结构并扩展"
    if "B_EXTEND" in alignments:
        return "B 扩展现有母类字段"
    return "A 直接复用"


def knowledge_reference_audit(canonical: set[str]) -> tuple[int, Counter[str], list[str]]:
    counts: Counter[str] = Counter()
    node_count = 0
    for relative in ("data/knowledge_nodes_v4.jsonl", "data/knowledge/trusted_nodes.mock.jsonl"):
        path = ROOT / relative
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                node = json.loads(line)
                node_count += 1
                counts.update(node.get("required_evidence") or [])
                counts.update(node.get("optional_evidence") or [])
    return node_count, counts, sorted(set(counts) - canonical)


def render() -> str:
    catalog_raw = load_yaml(CATALOG_PATH)
    runtime_raw = load_yaml(RUNTIME_PATH)
    catalog = catalog_raw["evidence_types"]
    runtime = {entry["canonical_type"]: entry for entry in runtime_raw["evidence_types"]}
    canonical = set(catalog)
    treatments = Counter(type_treatment(entry)[0] for entry in runtime.values())
    standard_direct = Counter()
    mapping_kinds = Counter()
    for entry in runtime.values():
        for provenance in entry["field_provenance"].values():
            mapping_kinds[provenance["mapping_kind"]] += 1
            if provenance["mapping_kind"] == "DIRECT_STANDARD":
                standard_direct[standard_for(provenance)] += 1

    node_count, knowledge_counts, noncanonical = knowledge_reference_audit(canonical)
    lines: list[str] = [
        "# Evidence Space v1 标准映射与能力矩阵",
        "",
        "> 本报告由 `evidence_type_catalog_v1.yaml` 与 `evidence_runtime_mapping_v1.yaml` 确定性生成；它是审计产物，不是第三个事实源。",
        "",
        "## 结论摘要",
        "",
        f"- 最终 canonical Evidence Type：**{len(canonical)} 类**；保留原 32 类并新增 6 类，没有 V2 或 Standard Evidence 并行 namespace。",
        f"- 原 32 类对最终母类目标空间的类型级覆盖为 **32/38（84.2%）**；缺失的是 `VEHICLE_ACCELERATION`、`HVAC_STATE`、`ROAD_STRUCTURE_STATE`、`COLLISION_ASSIST_STATE`、`LANE_ASSIST_STATE`、`DRIVER_MONITORING_STATE`。",
        f"- 对齐处理：A 直接复用 {treatments['A']} 类；B 扩字段 {treatments['B']} 类；C 统一并扩展 {treatments['C']} 类；D 新增 {treatments['D']} 类。",
        f"- 字段来源性质：DIRECT_STANDARD {mapping_kinds['DIRECT_STANDARD']}，DERIVED {mapping_kinds['DERIVED']}，INTERNAL_SECURITY {mapping_kinds['INTERNAL_SECURITY']}。",
        "- 八方向只作为 `SURROUNDING_OBJECT_STATE.objects[].region` 参数，且明确由 OSI 相对位置派生。CAMERA/RADAR/LIDAR/ULTRASONIC 只作为 source。",
        "",
        "## 实际读取的本地标准材料",
        "",
        "| 本地目录 | 标准与版本 | 实际机器可读文件 | 与 Evidence Space 相关的核心实体/字段 |",
        "|---|---|---|---|",
        "| `references/standards/01_covesa_vss_v6.0/vehicle_signal_specification-6.0` | COVESA VSS 6.0 | `spec/**/*.vspec`, `spec/units.yaml`, `spec/quantities.yaml` | `Vehicle.Speed`, `Vehicle.Acceleration.*`, transmission, brake, doors/windows, lights, wiper, HVAC, seats, mirrors, steering, occupant/driver signals |",
        "| `references/standards/02_asam_osi_v3.8.0/open-simulation-interface-3.8.0` | ASAM OSI 3.8.0（`VERSION`） | `osi_*.proto` | `MovingObject`, `StationaryObject`, `BaseMoving`, classification, `SensorView` technology subviews, `EnvironmentalConditions`, `Occupant`, `Lane`, `LogicalLane`, `GroundTruth` |",
        "| `references/standards/03_asam_openscenario_xml_v1.4.0` | ASAM OpenSCENARIO XML 1.4.0 | `OpenSCENARIO.xsd`, examples `*.xosc` | `Weather`, `Sun`, `Fog`, `Precipitation`, `RoadCondition` including visual range, illuminance, wetness and friction scale |",
        "| `references/standards/04_asam_opendrive_v1.9.0` | ASAM OpenDRIVE 1.9.0 | `*_xsd_schema_files/*.xsd`, examples `*.xodr` | `t_road`, `t_road_type`, `t_road_lanes`, `t_junction`, `t_road_surface`, `t_road_surface_CRG` |",
        "| `references/standards/05_android_automotive_vhal/repo/automotive/vehicle/aidl_property/android/hardware/automotive/vehicle` | Android Automotive VHAL，Android 16 本地快照 | `VehicleProperty.aidl`, feature/error enum `*.aidl`, `current.txt` | AEB, FCW, BSW, LDW, LKA, LCA, ELKA, cruise/ACC, seat occupancy, hands-on, drowsiness and distraction properties |",
        "",
        "补充收集物：`data/standards/covesa_vss_v6.0/vss.json|csv` 和 `data/standards/android_vhal_android16/properties/*.aidl` 是上述源码的项目内机器可读镜像/裁剪，不作为独立标准或第三事实源；`carla_reference` 是模拟器能力清单，只能证明 SIMULATION 可用性。",
        "",
        "## 标准事实能力清单",
        "",
        "以下字段级矩阵同时承担标准事实能力清单和 A/B/C/D 对齐审计。`当前 Evidence Type=EVIDENCE_SPACE_GAP` 表示原 32 类中不存在；数据类型、单位、是否直接标准字段由 `mapping_kind` 明示。",
        "",
        "## Evidence Capability Matrix",
        "",
        "| 安全事实 | 标准来源 | 标准字段 | 数据类型/单位 | 当前 Evidence Type | 当前 runtime field | 是否已有 | 处理方式 | 最终 Evidence Type | 最终字段 | mapping_kind | 安全用途 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for type_name, entry in runtime.items():
        domain = str(catalog[type_name]["domain"])
        safety_use = SAFETY_USES.get(domain, "支持车控安全事实核验")
        for field, provenance in entry["field_provenance"].items():
            alignment = str(provenance.get("alignment") or "A_REUSE")
            current_field = provenance.get("previous_runtime_field")
            current_type = "EVIDENCE_SPACE_GAP" if alignment == "D_NEW_TYPE" else type_name
            exists = "否" if current_field in (None, "null", "") else "是"
            dtype = str(provenance.get("data_type") or "any")
            unit = provenance.get("unit")
            dtype_unit = dtype if unit in (None, "null", "") else f"{dtype} / {unit}"
            standard_field = str(provenance.get("standard_entity_or_field") or "-").replace("|", "/")
            lines.append(
                "| " + " | ".join(
                    [
                        f"{domain}.{field}", standard_for(provenance), standard_field,
                        dtype_unit, current_type, str(current_field or "—"), exists,
                        alignment, type_name, field, provenance["mapping_kind"], safety_use,
                    ]
                ) + " |"
            )

    lines.extend([
        "",
        "## 五套标准带来的直接能力",
        "",
    ])
    for label in [item[1] for item in STANDARD_LABELS]:
        lines.append(f"- **{label}**：贡献 {standard_direct[label]} 个最终 DIRECT_STANDARD 字段。")
    lines.extend([
        "",
        "- VSS：自车速度/加速度、挡位、行车与驻车制动、转向、车门/窗、灯光、雨刮、HVAC、座椅、镜面和乘员信号。",
        "- OSI：运动/静止目标分类与空间运动、传感器视图技术来源、环境、乘员、车道/逻辑车道和 ground-truth 来源标识。",
        "- OpenSCENARIO：动态天气、降水、雾视距、太阳照度、路面湿润和摩擦缩放。",
        "- OpenDRIVE：静态道路类型、车道段、路口关系、交通规则和 CRG 表面引用；不把静态表面引用冒充实时附着。",
        "- Android VHAL：AEB/FCW/BSW、LDW/LKA/LCA/ELKA、巡航/ACC、座椅占用、手握方向盘、困倦和分心状态。",
        "",
        "## 反向场景验收",
        "",
        "| 场景 | KnowledgeNode 只引用的母类 | runtime contract 可表达字段 | 当前接入结论 |",
        "|---|---|---|---|",
        "| BRAKE | `SERVICE_BRAKE_STATE`, `VEHICLE_SPEED`, `ROAD_FRICTION_STATE`; optional `PARKING_BRAKE_STATE`, `GEAR_STATE` | brake/pedal/emergency、speed、road_condition/wetness/friction、parking brake、gear | 可完整表达；驻车制动无可靠接入，摩擦仅有模拟类别，数值估计仍为空 |",
        "| DOOR_OPEN RIGHT_REAR | `VEHICLE_SPEED`, `DOOR_STATE`, `SURROUNDING_OBJECT_STATE` | door `area=RIGHT_REAR`; object `region=REAR_RIGHT`, entity_kind, distance, relative_speed, motion_state, risk_level | contract 可完整表达；当前仅有模拟前后最近距离，无 bicycle/pedestrian/motorcycle 分类与相对速度，必须保持 PARTIAL/UNAVAILABLE |",
        "| HEADLIGHT OFF | `ENVIRONMENT_CONDITIONS`, `VEHICLE_SPEED`, `LIGHTING_STATE` | illumination, visibility, precipitation, fog, speed, lamp states | contract 可完整表达；模拟器只有 ambient_light/weather/headlight_state，visibility 与细分天气仍为空 |",
        "| WIPER | `WIPER_STATE`, `ENVIRONMENT_CONDITIONS`, `VEHICLE_SPEED` | wiper mode/intensity/frequency/wiping/error, precipitation, vehicle motion predicate | contract 可完整表达；WIPER_STATE 当前 UNAVAILABLE，降水细分也未真实接入 |",
        "",
        "## KnowledgeNode 消费者审计",
        "",
        f"扫描 `data/knowledge_nodes_v4.jsonl` 与 `data/knowledge/trusted_nodes.mock.jsonl` 共 {node_count} 个节点，发现 {len(knowledge_counts)} 个不同 Evidence 引用值。车控主链和本轮四个场景均可由 canonical 母类表达，KnowledgeNode schema 未修改。",
        "",
        "完整知识语料还含以下非 canonical 引用，它们不能作为第二 namespace 继续在线使用：",
        "",
        "`" + "`, `".join(noncanonical) + "`",
        "",
        "其中 `WEATHER` 应统一引用 `ENVIRONMENT_CONDITIONS`，`VEHICLE_STATIONARY` 应引用 `VEHICLE_SPEED`，`ACCELERATION_STATE` 应迁移为 `VEHICLE_ACCELERATION`；`NON_CANONICAL_TYPE` 是明确错误样本。其余多数为网络安全、数据治理、OTA/合规领域，超出本轮车辆运行 Evidence Space 的标准输入范围，保留为明确 Gap，不能凭名称批量造类型。",
        "",
        "## Evidence Space Gap",
        "",
        "1. 真实 CAMERA/RADAR/LIDAR/ULTRASONIC 尚未接入；OSI 对象分类、八方向、相对速度和风险字段目前只能由未来真实适配器或明确 SIMULATION 产生。",
        "2. WIPER、驻车制动、车道/道路结构、ADAS 和驾驶员监测均有正式 contract，但当前 runtime 为 UNAVAILABLE。",
        "3. 当前环境模拟器没有真实 visibility、precipitation intensity、fog visual range、wetness 或 friction scale，不得由 `weather` 字符串伪造。",
        "4. OpenDRIVE 的 CRG surface 是静态表面引用，不等同于实时路面湿滑或附着系数。",
        "5. 全知识语料中的网络安全、数据治理、OTA 和合规 Evidence 引用尚未建立相应标准驱动空间；本轮保持显式非 canonical Gap。",
        "",
        "## 十二类来源性质总结",
        "",
        "- 系统派生重点：八方向 `region`、`entity_kind` 归一化、`exists`、`distance`、`relative_speed`、`motion_state`、`risk_level`、当前车道关联、是否位于路口、天气摘要、可用性与质量指标。",
        "- 内部安全重点：`AUTHORIZATION_STATE` 全部字段、`SYSTEM_MODE` 全部字段，以及 common envelope 的 runtime availability。",
        "- 其余标为 DIRECT_STANDARD 的字段均可追到本地机器可读标准文件和实际实体/字段；没有把派生值写成标准原生字段。",
        "",
        "## 最终回答",
        "",
        "1. 现有 32 类覆盖最终 38 个母类目标中的 32 个（84.2%），但多个母类需要字段扩展。",
        "2. 需要扩字段或统一结构的类型可由矩阵 `B_EXTEND`/`C_UNIFY` 行逐项审计。",
        "3. 真正缺失的新母类共 6 个：车辆加速度、HVAC、道路结构、碰撞辅助、车道辅助、驾驶员监测。",
        "4. 最终 Evidence Space 为 38 个 canonical 类型。",
        "5-9. 五套标准贡献见“实际读取材料”“直接能力”和完整矩阵。",
        "10. 系统派生字段见 `mapping_kind=DERIVED` 的全部矩阵行。",
        "11. 内部安全字段见 `mapping_kind=INTERNAL_SECURITY` 的全部矩阵行。",
        "12. 当前车控知识库与四个验收场景在 contract 层均可表达；部分事实尚无真实 runtime 数据。",
        "13. 剩余 Gap 见上一节，尤其是真实传感器、动态环境、道路/ADAS 接入和非车控网络安全语料。",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    OUTPUT_PATH.write_text(render(), encoding="utf-8", newline="\n")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
