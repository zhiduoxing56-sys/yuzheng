# Evidence Space v1 标准映射与能力矩阵

> 本报告由 `evidence_type_catalog_v1.yaml` 与 `evidence_runtime_mapping_v1.yaml` 确定性生成；它是审计产物，不是第三个事实源。

## 结论摘要

- 最终 canonical Evidence Type：**38 类**；保留原 32 类并新增 6 类，没有 V2 或 Standard Evidence 并行 namespace。
- 原 32 类对最终母类目标空间的类型级覆盖为 **32/38（84.2%）**；缺失的是 `VEHICLE_ACCELERATION`、`HVAC_STATE`、`ROAD_STRUCTURE_STATE`、`COLLISION_ASSIST_STATE`、`LANE_ASSIST_STATE`、`DRIVER_MONITORING_STATE`。
- 对齐处理：A 直接复用 7 类；B 扩字段 17 类；C 统一并扩展 8 类；D 新增 6 类。
- 字段来源性质：DIRECT_STANDARD 136，DERIVED 57，INTERNAL_SECURITY 17。
- 八方向只作为 `SURROUNDING_OBJECT_STATE.objects[].region` 参数，且明确由 OSI 相对位置派生。CAMERA/RADAR/LIDAR/ULTRASONIC 只作为 source。

## 实际读取的本地标准材料

| 本地目录 | 标准与版本 | 实际机器可读文件 | 与 Evidence Space 相关的核心实体/字段 |
|---|---|---|---|
| `references/standards/01_covesa_vss_v6.0/vehicle_signal_specification-6.0` | COVESA VSS 6.0 | `spec/**/*.vspec`, `spec/units.yaml`, `spec/quantities.yaml` | `Vehicle.Speed`, `Vehicle.Acceleration.*`, transmission, brake, doors/windows, lights, wiper, HVAC, seats, mirrors, steering, occupant/driver signals |
| `references/standards/02_asam_osi_v3.8.0/open-simulation-interface-3.8.0` | ASAM OSI 3.8.0（`VERSION`） | `osi_*.proto` | `MovingObject`, `StationaryObject`, `BaseMoving`, classification, `SensorView` technology subviews, `EnvironmentalConditions`, `Occupant`, `Lane`, `LogicalLane`, `GroundTruth` |
| `references/standards/03_asam_openscenario_xml_v1.4.0` | ASAM OpenSCENARIO XML 1.4.0 | `OpenSCENARIO.xsd`, examples `*.xosc` | `Weather`, `Sun`, `Fog`, `Precipitation`, `RoadCondition` including visual range, illuminance, wetness and friction scale |
| `references/standards/04_asam_opendrive_v1.9.0` | ASAM OpenDRIVE 1.9.0 | `*_xsd_schema_files/*.xsd`, examples `*.xodr` | `t_road`, `t_road_type`, `t_road_lanes`, `t_junction`, `t_road_surface`, `t_road_surface_CRG` |
| `references/standards/05_android_automotive_vhal/repo/automotive/vehicle/aidl_property/android/hardware/automotive/vehicle` | Android Automotive VHAL，Android 16 本地快照 | `VehicleProperty.aidl`, feature/error enum `*.aidl`, `current.txt` | AEB, FCW, BSW, LDW, LKA, LCA, ELKA, cruise/ACC, seat occupancy, hands-on, drowsiness and distraction properties |

补充收集物：`data/standards/covesa_vss_v6.0/vss.json|csv` 和 `data/standards/android_vhal_android16/properties/*.aidl` 是上述源码的项目内机器可读镜像/裁剪，不作为独立标准或第三事实源；`carla_reference` 是模拟器能力清单，只能证明 SIMULATION 可用性。

## 标准事实能力清单

以下字段级矩阵同时承担标准事实能力清单和 A/B/C/D 对齐审计。`当前 Evidence Type=EVIDENCE_SPACE_GAP` 表示原 32 类中不存在；数据类型、单位、是否直接标准字段由 `mapping_kind` 明示。

## Evidence Capability Matrix

| 安全事实 | 标准来源 | 标准字段 | 数据类型/单位 | 当前 Evidence Type | 当前 runtime field | 是否已有 | 处理方式 | 最终 Evidence Type | 最终字段 | mapping_kind | 安全用途 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SELF_MOTION.value | COVESA VSS 6.0 | Vehicle.Speed | float / km/h | VEHICLE_SPEED | vehicle_speed | 是 | A_REUSE | VEHICLE_SPEED | value | DIRECT_STANDARD | 判断车辆是否运动、纵横向动态与动作前置条件 |
| SELF_MOTION.longitudinal | COVESA VSS 6.0 | Vehicle.Acceleration.Longitudinal | float / m/s^2 | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | VEHICLE_ACCELERATION | longitudinal | DIRECT_STANDARD | 判断车辆是否运动、纵横向动态与动作前置条件 |
| SELF_MOTION.lateral | COVESA VSS 6.0 | Vehicle.Acceleration.Lateral | float / m/s^2 | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | VEHICLE_ACCELERATION | lateral | DIRECT_STANDARD | 判断车辆是否运动、纵横向动态与动作前置条件 |
| SELF_MOTION.vertical | COVESA VSS 6.0 | Vehicle.Acceleration.Vertical | float / m/s^2 | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | VEHICLE_ACCELERATION | vertical | DIRECT_STANDARD | 判断车辆是否运动、纵横向动态与动作前置条件 |
| SELF_MOTION.current_gear | COVESA VSS 6.0 | Vehicle.Powertrain.Transmission.CurrentGear | int8 | GEAR_STATE | current_gear | 是 | A_REUSE | GEAR_STATE | current_gear | DIRECT_STANDARD | 判断车辆是否运动、纵横向动态与动作前置条件 |
| SELF_MOTION.selected_gear | COVESA VSS 6.0 | Vehicle.Powertrain.Transmission.SelectedGear | int8 | GEAR_STATE | selected_gear | 是 | A_REUSE | GEAR_STATE | selected_gear | DIRECT_STANDARD | 判断车辆是否运动、纵横向动态与动作前置条件 |
| SELF_MOTION.change_mode | COVESA VSS 6.0 | Vehicle.Powertrain.Transmission.GearChangeMode | string | GEAR_STATE | change_mode | 是 | A_REUSE | GEAR_STATE | change_mode | DIRECT_STANDARD | 判断车辆是否运动、纵横向动态与动作前置条件 |
| VEHICLE_FUNCTION_STATE.brake_state | SYSTEM DERIVATION | normalized brake actuator/provider state | enum | SERVICE_BRAKE_STATE | brake_state | 是 | A_REUSE | SERVICE_BRAKE_STATE | brake_state | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.pedal_position | COVESA VSS 6.0 | Vehicle.Chassis.Brake.PedalPosition | uint8 / percent | SERVICE_BRAKE_STATE | — | 否 | B_EXTEND | SERVICE_BRAKE_STATE | pedal_position | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.emergency_braking_detected | COVESA VSS 6.0 | Vehicle.Chassis.Brake.IsDriverEmergencyBrakingDetected | boolean | SERVICE_BRAKE_STATE | emergency_braking_detected | 是 | A_REUSE | SERVICE_BRAKE_STATE | emergency_braking_detected | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.engaged | COVESA VSS 6.0 | Vehicle.Chassis.ParkingBrake.IsEngaged | boolean | PARKING_BRAKE_STATE | engaged | 是 | A_REUSE | PARKING_BRAKE_STATE | engaged | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.auto_apply_enabled | COVESA VSS 6.0 | Vehicle.Chassis.ParkingBrake.IsAutoApplyEnabled | boolean | PARKING_BRAKE_STATE | auto_apply_enabled | 是 | A_REUSE | PARKING_BRAKE_STATE | auto_apply_enabled | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.steering_wheel_angle | COVESA VSS 6.0 | Vehicle.Chassis.SteeringWheel.Angle | int16 / degrees | STEERING_STATE | steering_wheel_angle | 是 | A_REUSE | STEERING_STATE | steering_wheel_angle | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.axle_steering_angle | COVESA VSS 6.0 | Vehicle.Chassis.Axle.Row1.SteeringAngle | float / degrees | STEERING_STATE | axle_steering_angle | 是 | A_REUSE | STEERING_STATE | axle_steering_angle | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.rear_axle_steering_angle | COVESA VSS 6.0 | Vehicle.Chassis.Axle.Row2.SteeringAngle | float / degrees | STEERING_STATE | — | 否 | B_EXTEND | STEERING_STATE | rear_axle_steering_angle | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.steering_rate | SYSTEM DERIVATION | time derivative of steering angle | float / degrees/s | STEERING_STATE | — | 否 | B_EXTEND | STEERING_STATE | steering_rate | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| ADAS.enabled | COVESA VSS 6.0 | Vehicle.ADAS.ESC.IsEnabled | boolean | ESC_STATE | enabled | 是 | A_REUSE | ESC_STATE | enabled | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.engaged | COVESA VSS 6.0 | Vehicle.ADAS.ESC.IsEngaged | boolean | ESC_STATE | engaged | 是 | A_REUSE | ESC_STATE | engaged | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.state | Android Automotive VHAL (Android 16 local snapshot) | ELECTRONIC_STABILITY_CONTROL_STATE | int32 enum | ESC_STATE | — | 否 | B_EXTEND | ESC_STATE | state | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.error | COVESA VSS 6.0 | Vehicle.ADAS.ESC.IsError | boolean | ESC_STATE | error | 是 | A_REUSE | ESC_STATE | error | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ROAD.road_condition | SYSTEM DERIVATION | normalized observed road surface condition | enum | ROAD_FRICTION_STATE | road_condition | 是 | A_REUSE | ROAD_FRICTION_STATE | road_condition | DERIVED | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.wetness | ASAM OpenSCENARIO XML 1.4.0 | RoadCondition.@wetness | Wetness / enum | ROAD_FRICTION_STATE | — | 否 | B_EXTEND | ROAD_FRICTION_STATE | wetness | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.friction_scale_factor | ASAM OpenSCENARIO XML 1.4.0 | RoadCondition.@frictionScaleFactor | Double / ratio | ROAD_FRICTION_STATE | — | 否 | B_EXTEND | ROAD_FRICTION_STATE | friction_scale_factor | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.lower_bound | COVESA VSS 6.0 | Vehicle.ADAS.ESC.RoadFriction.LowerBound | float / ratio | ROAD_FRICTION_STATE | lower_bound | 是 | A_REUSE | ROAD_FRICTION_STATE | lower_bound | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.most_probable | COVESA VSS 6.0 | Vehicle.ADAS.ESC.RoadFriction.MostProbable | float / ratio | ROAD_FRICTION_STATE | most_probable | 是 | A_REUSE | ROAD_FRICTION_STATE | most_probable | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.upper_bound | COVESA VSS 6.0 | Vehicle.ADAS.ESC.RoadFriction.UpperBound | float / ratio | ROAD_FRICTION_STATE | upper_bound | 是 | A_REUSE | ROAD_FRICTION_STATE | upper_bound | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ADAS.enabled | Android Automotive VHAL (Android 16 local snapshot) | CRUISE_CONTROL_ENABLED | boolean | CRUISE_STATE | enabled | 是 | A_REUSE | CRUISE_STATE | enabled | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.active | COVESA VSS 6.0 | Vehicle.ADAS.CruiseControl.IsActive | boolean | CRUISE_STATE | active | 是 | A_REUSE | CRUISE_STATE | active | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.cruise_type | Android Automotive VHAL (Android 16 local snapshot) | CRUISE_CONTROL_TYPE | int32 enum | CRUISE_STATE | — | 否 | B_EXTEND | CRUISE_STATE | cruise_type | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.state | Android Automotive VHAL (Android 16 local snapshot) | CRUISE_CONTROL_STATE | int32 enum | CRUISE_STATE | — | 否 | B_EXTEND | CRUISE_STATE | state | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.target_speed | Android Automotive VHAL (Android 16 local snapshot) | CRUISE_CONTROL_TARGET_SPEED | float / m/s | CRUISE_STATE | speed_set | 是 | C_UNIFY | CRUISE_STATE | target_speed | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.target_time_gap | Android Automotive VHAL (Android 16 local snapshot) | ADAPTIVE_CRUISE_CONTROL_TARGET_TIME_GAP | int32 / ms | CRUISE_STATE | — | 否 | B_EXTEND | CRUISE_STATE | target_time_gap | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.lead_vehicle_distance | Android Automotive VHAL (Android 16 local snapshot) | ADAPTIVE_CRUISE_CONTROL_LEAD_VEHICLE_MEASURED_DISTANCE | float / m | CRUISE_STATE | — | 否 | B_EXTEND | CRUISE_STATE | lead_vehicle_distance | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.error | COVESA VSS 6.0 | Vehicle.ADAS.CruiseControl.IsError | boolean | CRUISE_STATE | error | 是 | A_REUSE | CRUISE_STATE | error | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS instance path normalized to area | enum | DOOR_STATE | metadata.area | 是 | B_EXTEND | DOOR_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.is_open | COVESA VSS 6.0 | Vehicle.Cabin.Door.*.IsOpen | boolean | DOOR_STATE | — | 否 | B_EXTEND | DOOR_STATE | is_open | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.state | SYSTEM DERIVATION | normalized from IsOpen/Position or provider state | enum | DOOR_STATE | state | 是 | C_UNIFY | DOOR_STATE | state | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.position | COVESA VSS 6.0 | Vehicle.Cabin.Door.*.Position | uint8 / percent | DOOR_STATE | position | 是 | A_REUSE | DOOR_STATE | position | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS instance path normalized to area | enum | DOOR_LOCK_STATE | — | 否 | B_EXTEND | DOOR_LOCK_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.locked | COVESA VSS 6.0 | Vehicle.Cabin.Door.*.IsLocked | boolean | DOOR_LOCK_STATE | — | 否 | B_EXTEND | DOOR_LOCK_STATE | locked | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.lock_state | SYSTEM DERIVATION | normalized provider lock state | enum | DOOR_LOCK_STATE | lock_state | 是 | A_REUSE | DOOR_LOCK_STATE | lock_state | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.child_lock_active | COVESA VSS 6.0 | Vehicle.Cabin.Door.*.IsChildLockActive | boolean | DOOR_LOCK_STATE | child_lock_active | 是 | A_REUSE | DOOR_LOCK_STATE | child_lock_active | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS instance path normalized to area | enum | WINDOW_STATE | — | 否 | B_EXTEND | WINDOW_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.is_open | COVESA VSS 6.0 | Vehicle.Cabin.Door.*.Window.IsOpen | boolean | WINDOW_STATE | — | 否 | B_EXTEND | WINDOW_STATE | is_open | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.state | SYSTEM DERIVATION | normalized provider window state | enum | WINDOW_STATE | state | 是 | A_REUSE | WINDOW_STATE | state | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.position | COVESA VSS 6.0 | Vehicle.Cabin.Door.*.Window.Position | uint8 / percent | WINDOW_STATE | position | 是 | A_REUSE | WINDOW_STATE | position | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.child_lock_active | COVESA VSS 6.0 | Vehicle.Cabin.IsWindowChildLockEngaged | boolean | WINDOW_STATE | child_lock_active | 是 | A_REUSE | WINDOW_STATE | child_lock_active | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.position | COVESA VSS 6.0 | Vehicle.Cabin.Sunroof.Position | uint8 / percent | SUNROOF_STATE | position | 是 | A_REUSE | SUNROOF_STATE | position | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.tilt | SYSTEM DERIVATION | normalized sunroof tilt if provider supplies it | float / percent | SUNROOF_STATE | — | 否 | B_EXTEND | SUNROOF_STATE | tilt | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS instance path normalized to area | enum | TRUNK_STATE | — | 否 | B_EXTEND | TRUNK_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.is_open | COVESA VSS 6.0 | Vehicle.Body.Trunk.*.IsOpen | boolean | TRUNK_STATE | — | 否 | B_EXTEND | TRUNK_STATE | is_open | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.state | SYSTEM DERIVATION | normalized trunk state | enum | TRUNK_STATE | state | 是 | A_REUSE | TRUNK_STATE | state | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.position | COVESA VSS 6.0 | Vehicle.Body.Trunk.*.Position | uint8 / percent | TRUNK_STATE | position | 是 | A_REUSE | TRUNK_STATE | position | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS instance path normalized to area | enum | TRUNK_LOCK_STATE | — | 否 | B_EXTEND | TRUNK_LOCK_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.locked | COVESA VSS 6.0 | Vehicle.Body.Trunk.*.IsLocked | boolean | TRUNK_LOCK_STATE | — | 否 | B_EXTEND | TRUNK_LOCK_STATE | locked | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.lock_state | SYSTEM DERIVATION | normalized trunk lock state | enum | TRUNK_LOCK_STATE | lock_state | 是 | A_REUSE | TRUNK_LOCK_STATE | lock_state | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.is_open | COVESA VSS 6.0 | Vehicle.Body.Hood.IsOpen | boolean | HOOD_STATE | — | 否 | B_EXTEND | HOOD_STATE | is_open | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.state | SYSTEM DERIVATION | normalized hood state | enum | HOOD_STATE | state | 是 | A_REUSE | HOOD_STATE | state | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.position | COVESA VSS 6.0 | Vehicle.Body.Hood.Position | uint8 / percent | HOOD_STATE | position | 是 | A_REUSE | HOOD_STATE | position | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS mirror instance normalized to area | enum | MIRROR_STATE | — | 否 | B_EXTEND | MIRROR_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.folded | COVESA VSS 6.0 | Vehicle.Body.Mirrors.*.IsFolded | boolean | MIRROR_STATE | folded | 是 | A_REUSE | MIRROR_STATE | folded | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.locked | COVESA VSS 6.0 | Vehicle.Body.Mirrors.*.IsLocked | boolean | MIRROR_STATE | — | 否 | B_EXTEND | MIRROR_STATE | locked | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.pan | COVESA VSS 6.0 | Vehicle.Body.Mirrors.*.Pan | int8 / percent | MIRROR_STATE | pan | 是 | A_REUSE | MIRROR_STATE | pan | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.tilt | COVESA VSS 6.0 | Vehicle.Body.Mirrors.*.Tilt | int8 / percent | MIRROR_STATE | tilt | 是 | A_REUSE | MIRROR_STATE | tilt | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.yaw | COVESA VSS 6.0 | Vehicle.Body.Mirrors.*.Yaw | int8 / percent | MIRROR_STATE | — | 否 | B_EXTEND | MIRROR_STATE | yaw | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS mirror instance normalized to area | enum | MIRROR_HEATING_STATE | — | 否 | B_EXTEND | MIRROR_HEATING_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.heating_on | COVESA VSS 6.0 | Vehicle.Body.Mirrors.*.IsHeatingOn | boolean | MIRROR_HEATING_STATE | heating_on | 是 | A_REUSE | MIRROR_HEATING_STATE | heating_on | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS seat instance normalized to area | enum | SEAT_POSITION_STATE | — | 否 | B_EXTEND | SEAT_POSITION_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.position | COVESA VSS 6.0 | Vehicle.Cabin.Seat.*.Position | uint16 / mm | SEAT_POSITION_STATE | position | 是 | A_REUSE | SEAT_POSITION_STATE | position | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.height | COVESA VSS 6.0 | Vehicle.Cabin.Seat.*.Height | uint16 / mm | SEAT_POSITION_STATE | height | 是 | A_REUSE | SEAT_POSITION_STATE | height | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.tilt | COVESA VSS 6.0 | Vehicle.Cabin.Seat.*.Tilt | float / degrees | SEAT_POSITION_STATE | tilt | 是 | A_REUSE | SEAT_POSITION_STATE | tilt | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.recline | COVESA VSS 6.0 | Vehicle.Cabin.Seat.*.Backrest.Recline | float / degrees | SEAT_POSITION_STATE | recline | 是 | A_REUSE | SEAT_POSITION_STATE | recline | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.lumbar_height | COVESA VSS 6.0 | Vehicle.Cabin.Seat.*.Backrest.LumbarHeight | uint8 / mm | SEAT_POSITION_STATE | lumbar_height | 是 | A_REUSE | SEAT_POSITION_STATE | lumbar_height | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.lumbar_support | COVESA VSS 6.0 | Vehicle.Cabin.Seat.*.Backrest.LumbarSupport | float / percent | SEAT_POSITION_STATE | lumbar_support | 是 | A_REUSE | SEAT_POSITION_STATE | lumbar_support | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.extension | COVESA VSS 6.0 | Vehicle.Chassis.SteeringWheel.Extension | uint8 / percent | STEERING_WHEEL_POSITION_STATE | extension | 是 | A_REUSE | STEERING_WHEEL_POSITION_STATE | extension | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.tilt | COVESA VSS 6.0 | Vehicle.Chassis.SteeringWheel.Tilt | uint8 / percent | STEERING_WHEEL_POSITION_STATE | tilt | 是 | A_REUSE | STEERING_WHEEL_POSITION_STATE | tilt | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS HVAC station instance normalized to area | enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | HVAC_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.active | COVESA VSS 6.0 | Vehicle.Cabin.HVAC.IsAirConditioningActive | boolean | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | HVAC_STATE | active | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.recirculation_active | COVESA VSS 6.0 | Vehicle.Cabin.HVAC.IsRecirculationActive | boolean | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | HVAC_STATE | recirculation_active | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.target_temperature | COVESA VSS 6.0 | Vehicle.Cabin.HVAC.Station.*.Temperature | float / Celsius | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | HVAC_STATE | target_temperature | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.fan_speed | COVESA VSS 6.0 | Vehicle.Cabin.HVAC.Station.*.FanSpeed | uint8 / percent | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | HVAC_STATE | fan_speed | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.air_distribution | COVESA VSS 6.0 | Vehicle.Cabin.HVAC.Station.*.AirDistribution | string / enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | HVAC_STATE | air_distribution | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.front_active | COVESA VSS 6.0 | Vehicle.Cabin.HVAC.IsFrontDefrosterActive | boolean | DEFROST_STATE | front_active | 是 | A_REUSE | DEFROST_STATE | front_active | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.rear_active | COVESA VSS 6.0 | Vehicle.Cabin.HVAC.IsRearDefrosterActive | boolean | DEFROST_STATE | rear_active | 是 | A_REUSE | DEFROST_STATE | rear_active | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS windshield instance normalized to area | enum | WINDSHIELD_HEATING_STATE | — | 否 | B_EXTEND | WINDSHIELD_HEATING_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.heating_on | COVESA VSS 6.0 | Vehicle.Body.Windshield.*.IsHeatingOn | boolean | WINDSHIELD_HEATING_STATE | heating_on | 是 | A_REUSE | WINDSHIELD_HEATING_STATE | heating_on | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.headlight_state | SYSTEM DERIVATION | normalized provider headlight state | enum | LIGHTING_STATE | headlight_state | 是 | A_REUSE | LIGHTING_STATE | headlight_state | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.high_beam | SYSTEM DERIVATION | compatibility-preserving normalized high-beam state | boolean | LIGHTING_STATE | high_beam | 是 | A_REUSE | LIGHTING_STATE | high_beam | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.fog | SYSTEM DERIVATION | compatibility-preserving aggregate fog-lamp state | boolean | LIGHTING_STATE | fog | 是 | A_REUSE | LIGHTING_STATE | fog | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.parking | SYSTEM DERIVATION | compatibility-preserving parking-lamp state | boolean | LIGHTING_STATE | parking | 是 | A_REUSE | LIGHTING_STATE | parking | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.hazard | SYSTEM DERIVATION | compatibility-preserving hazard state | boolean | LIGHTING_STATE | hazard | 是 | A_REUSE | LIGHTING_STATE | hazard | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.direction_indicator | SYSTEM DERIVATION | aggregate left/right indication | enum | LIGHTING_STATE | direction_indicator | 是 | A_REUSE | LIGHTING_STATE | direction_indicator | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.light_switch | COVESA VSS 6.0 | Vehicle.Body.Lights.LightSwitch | string / enum | LIGHTING_STATE | — | 否 | B_EXTEND | LIGHTING_STATE | light_switch | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.low_beam_on | COVESA VSS 6.0 | Vehicle.Body.Lights.Beam.Low.IsOn | boolean | LIGHTING_STATE | — | 否 | B_EXTEND | LIGHTING_STATE | low_beam_on | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.high_beam_on | COVESA VSS 6.0 | Vehicle.Body.Lights.Beam.High.IsOn | boolean | LIGHTING_STATE | high_beam | 是 | C_UNIFY | LIGHTING_STATE | high_beam_on | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.high_beam_switch_on | COVESA VSS 6.0 | Vehicle.Body.Lights.IsHighBeamSwitchOn | boolean | LIGHTING_STATE | — | 否 | B_EXTEND | LIGHTING_STATE | high_beam_switch_on | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.front_fog_on | COVESA VSS 6.0 | Vehicle.Body.Lights.Fog.Front.IsOn | boolean | LIGHTING_STATE | fog | 是 | C_UNIFY | LIGHTING_STATE | front_fog_on | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.rear_fog_on | COVESA VSS 6.0 | Vehicle.Body.Lights.Fog.Rear.IsOn | boolean | LIGHTING_STATE | — | 否 | B_EXTEND | LIGHTING_STATE | rear_fog_on | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.parking_on | COVESA VSS 6.0 | Vehicle.Body.Lights.Parking.IsOn | boolean | LIGHTING_STATE | parking | 是 | C_UNIFY | LIGHTING_STATE | parking_on | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.hazard_signaling | COVESA VSS 6.0 | Vehicle.Body.Lights.Hazard.IsSignaling | boolean | LIGHTING_STATE | hazard | 是 | C_UNIFY | LIGHTING_STATE | hazard_signaling | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.left_indicator_signaling | COVESA VSS 6.0 | Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling | boolean | LIGHTING_STATE | direction_indicator | 是 | C_UNIFY | LIGHTING_STATE | left_indicator_signaling | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.right_indicator_signaling | COVESA VSS 6.0 | Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling | boolean | LIGHTING_STATE | direction_indicator | 是 | C_UNIFY | LIGHTING_STATE | right_indicator_signaling | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.area | SYSTEM DERIVATION | VSS windshield instance normalized to area | enum | WIPER_STATE | — | 否 | B_EXTEND | WIPER_STATE | area | DERIVED | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.mode | COVESA VSS 6.0 | Vehicle.Body.Windshield.*.Wiping.Mode | string / enum | WIPER_STATE | mode | 是 | A_REUSE | WIPER_STATE | mode | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.intensity | COVESA VSS 6.0 | Vehicle.Body.Windshield.*.Wiping.Intensity | uint8 | WIPER_STATE | intensity | 是 | A_REUSE | WIPER_STATE | intensity | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.frequency | COVESA VSS 6.0 | Vehicle.Body.Windshield.*.Wiping.System.Frequency | uint8 / cpm | WIPER_STATE | — | 否 | B_EXTEND | WIPER_STATE | frequency | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.wiping | COVESA VSS 6.0 | Vehicle.Body.Windshield.*.Wiping.System.IsWiping | boolean | WIPER_STATE | wiping | 是 | A_REUSE | WIPER_STATE | wiping | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| VEHICLE_FUNCTION_STATE.error | COVESA VSS 6.0 | Vehicle.Body.Windshield.*.Wiping.System.IsWiperError | boolean | WIPER_STATE | error | 是 | A_REUSE | WIPER_STATE | error | DIRECT_STANDARD | 确认车身/底盘执行器当前状态并防止危险切换 |
| OCCUPANT.area | SYSTEM DERIVATION | VSS instance / OSI Occupant.Classification.seat normalized to area | enum | OCCUPANT_STATE | — | 否 | B_EXTEND | OCCUPANT_STATE | area | DERIVED | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.occupied | SYSTEM DERIVATION | normalized from VSS OccupancyStatus or VHAL SEAT_OCCUPANCY | boolean | OCCUPANT_STATE | occupied | 是 | C_UNIFY | OCCUPANT_STATE | occupied | DERIVED | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.occupancy_status | COVESA VSS 6.0 | Vehicle.Cabin.Seat.*.OccupancyStatus | string / enum | OCCUPANT_STATE | — | 否 | B_EXTEND | OCCUPANT_STATE | occupancy_status | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.belted | COVESA VSS 6.0 | Vehicle.Cabin.Seat.*.IsBelted | boolean | OCCUPANT_STATE | belted | 是 | A_REUSE | OCCUPANT_STATE | belted | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.is_driver | ASAM OSI 3.8.0 | Occupant.Classification.is_driver | bool | OCCUPANT_STATE | — | 否 | B_EXTEND | OCCUPANT_STATE | is_driver | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.steering_control | ASAM OSI 3.8.0 | Occupant.Classification.steering_control | enum | OCCUPANT_STATE | hands_on_wheel | 是 | C_UNIFY | OCCUPANT_STATE | steering_control | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.hands_on_wheel | COVESA VSS 6.0 | Vehicle.Driver.IsHandsOnWheel | boolean | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | DRIVER_MONITORING_STATE | hands_on_wheel | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.hands_on_state | Android Automotive VHAL (Android 16 local snapshot) | HANDS_ON_DETECTION_DRIVER_STATE | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | DRIVER_MONITORING_STATE | hands_on_state | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.hands_on_warning | Android Automotive VHAL (Android 16 local snapshot) | HANDS_ON_DETECTION_WARNING | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | DRIVER_MONITORING_STATE | hands_on_warning | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.drowsiness_state | Android Automotive VHAL (Android 16 local snapshot) | DRIVER_DROWSINESS_ATTENTION_STATE | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | DRIVER_MONITORING_STATE | drowsiness_state | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.drowsiness_warning | Android Automotive VHAL (Android 16 local snapshot) | DRIVER_DROWSINESS_ATTENTION_WARNING | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | DRIVER_MONITORING_STATE | drowsiness_warning | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.distraction_state | Android Automotive VHAL (Android 16 local snapshot) | DRIVER_DISTRACTION_STATE | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | DRIVER_MONITORING_STATE | distraction_state | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| OCCUPANT.distraction_warning | Android Automotive VHAL (Android 16 local snapshot) | DRIVER_DISTRACTION_WARNING | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | DRIVER_MONITORING_STATE | distraction_warning | DIRECT_STANDARD | 判断乘员占用、安全带与驾驶员状态 |
| SURROUNDING_OBJECT.objects | ASAM OSI 3.8.0 | GroundTruth.moving_object/stationary_object normalized collection | array | SURROUNDING_OBJECT_STATE | objects | 是 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].object_id | ASAM OSI 3.8.0 | MovingObject.id / StationaryObject.id | Identifier | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].object_id | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].entity_kind | ASAM OSI 3.8.0 | MovingObject.type/vehicle_classification.type or StationaryObject.classification.type normalized | enum | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].entity_kind | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].region | SYSTEM DERIVATION | derived from relative position using eight-region policy | enum | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].region | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].exists | SYSTEM DERIVATION | derived from presence/track validity | boolean | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].exists | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].position_x | ASAM OSI 3.8.0 | BaseMoving.position.x / BaseStationary.position.x | double / m | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].position_x | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].position_y | ASAM OSI 3.8.0 | BaseMoving.position.y / BaseStationary.position.y | double / m | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].position_y | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].position_z | ASAM OSI 3.8.0 | BaseMoving.position.z / BaseStationary.position.z | double / m | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].position_z | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].velocity_x | ASAM OSI 3.8.0 | BaseMoving.velocity.x | double / m/s | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].velocity_x | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].velocity_y | ASAM OSI 3.8.0 | BaseMoving.velocity.y | double / m/s | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].velocity_y | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].velocity_z | ASAM OSI 3.8.0 | BaseMoving.velocity.z | double / m/s | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].velocity_z | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].acceleration_x | ASAM OSI 3.8.0 | BaseMoving.acceleration.x | double / m/s^2 | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].acceleration_x | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].acceleration_y | ASAM OSI 3.8.0 | BaseMoving.acceleration.y | double / m/s^2 | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].acceleration_y | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].acceleration_z | ASAM OSI 3.8.0 | BaseMoving.acceleration.z | double / m/s^2 | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].acceleration_z | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].distance | SYSTEM DERIVATION | Euclidean/planar distance derived from relative position | double / m | SURROUNDING_OBJECT_STATE | front_obstacle_distance/rear_obstacle_distance | 是 | C_UNIFY | SURROUNDING_OBJECT_STATE | objects[].distance | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].relative_speed | SYSTEM DERIVATION | projected relative velocity to host | double / m/s | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].relative_speed | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].motion_state | SYSTEM DERIVATION | derived from relative/absolute velocity | enum | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].motion_state | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].risk_level | SYSTEM DERIVATION | derived from distance relative speed trajectory and policy | enum | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].risk_level | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].source_kind | ASAM OSI 3.8.0 | SensorView camera_sensor_view/radar_sensor_view/lidar_sensor_view/ultrasonic_sensor_view normalized | enum | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].source_kind | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].sensor_id | ASAM OSI 3.8.0 | SensorView.sensor_id | Identifier | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].sensor_id | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.objects[].ground_truth | ASAM OSI 3.8.0 | provenance flag for SensorView.global_ground_truth / GroundTruth | boolean | SURROUNDING_OBJECT_STATE | — | 否 | B_EXTEND | SURROUNDING_OBJECT_STATE | objects[].ground_truth | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.front_obstacle_distance | SYSTEM DERIVATION | nearest object distance where region=FRONT | double / m | SURROUNDING_OBJECT_STATE | front_obstacle_distance | 是 | C_UNIFY | SURROUNDING_OBJECT_STATE | front_obstacle_distance | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.rear_obstacle_distance | SYSTEM DERIVATION | nearest object distance where region=REAR | double / m | SURROUNDING_OBJECT_STATE | rear_obstacle_distance | 是 | C_UNIFY | SURROUNDING_OBJECT_STATE | rear_obstacle_distance | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.collision_state | SYSTEM DERIVATION | simulator/runtime collision observation | any | SURROUNDING_OBJECT_STATE | collision_state | 是 | A_REUSE | SURROUNDING_OBJECT_STATE | collision_state | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| ROAD.current_lane_id | ASAM OSI 3.8.0 | host assignment to Lane.id | Identifier | LANE_STATE | current_lane | 是 | C_UNIFY | LANE_STATE | current_lane_id | DERIVED | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.lane_type | ASAM OSI 3.8.0 | Lane.classification.type | enum | LANE_STATE | — | 否 | B_EXTEND | LANE_STATE | lane_type | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.left_adjacent_lane_ids | ASAM OSI 3.8.0 | Lane.classification.left_adjacent_lane_id | Identifier[] | LANE_STATE | left_adjacent_lane | 是 | C_UNIFY | LANE_STATE | left_adjacent_lane_ids | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.right_adjacent_lane_ids | ASAM OSI 3.8.0 | Lane.classification.right_adjacent_lane_id | Identifier[] | LANE_STATE | right_adjacent_lane | 是 | C_UNIFY | LANE_STATE | right_adjacent_lane_ids | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.boundaries | ASAM OSI 3.8.0 | LaneBoundary / Lane.classification.lane_pairing | array | LANE_STATE | boundaries | 是 | A_REUSE | LANE_STATE | boundaries | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.logical_lane_ids | ASAM OSI 3.8.0 | LogicalLane.id | Identifier[] | LANE_STATE | — | 否 | B_EXTEND | LANE_STATE | logical_lane_ids | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.lane_state | SYSTEM DERIVATION | normalized open/closed/blocked/unknown lane state | enum | LANE_STATE | — | 否 | B_EXTEND | LANE_STATE | lane_state | DERIVED | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.road_id | ASAM OpenDRIVE 1.9.0 | t_road.@id | string | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | ROAD_STRUCTURE_STATE | road_id | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.road_type | ASAM OpenDRIVE 1.9.0 | t_road_type.@type | e_roadType / enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | ROAD_STRUCTURE_STATE | road_type | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.junction_id | ASAM OpenDRIVE 1.9.0 | t_road.@junction | string | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | ROAD_STRUCTURE_STATE | junction_id | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.at_junction | SYSTEM DERIVATION | derived from t_road.@junction and host road match | boolean | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | ROAD_STRUCTURE_STATE | at_junction | DERIVED | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.traffic_rule | ASAM OpenDRIVE 1.9.0 | t_road.@rule | e_trafficRule / enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | ROAD_STRUCTURE_STATE | traffic_rule | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.lane_section_count | ASAM OpenDRIVE 1.9.0 | count(t_road_lanes.laneSection) | integer / count | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | ROAD_STRUCTURE_STATE | lane_section_count | DERIVED | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.surface_reference | ASAM OpenDRIVE 1.9.0 | t_road_surface_CRG.@file | string / URI/path | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | ROAD_STRUCTURE_STATE | surface_reference | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.surface_purpose | ASAM OpenDRIVE 1.9.0 | t_road_surface_CRG.@purpose | e_road_surface_CRG_purpose / enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | ROAD_STRUCTURE_STATE | surface_purpose | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.traffic_light_id | ASAM OSI 3.8.0 | TrafficLight.id | Identifier | TRAFFIC_LIGHT_STATE | — | 否 | B_EXTEND | TRAFFIC_LIGHT_STATE | traffic_light_id | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.state | ASAM OSI 3.8.0 | normalized TrafficLight.classification | enum | TRAFFIC_LIGHT_STATE | state | 是 | A_REUSE | TRAFFIC_LIGHT_STATE | state | DERIVED | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.color | ASAM OSI 3.8.0 | TrafficLight.classification.color | enum | TRAFFIC_LIGHT_STATE | — | 否 | B_EXTEND | TRAFFIC_LIGHT_STATE | color | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.lane_ids | ASAM OSI 3.8.0 | TrafficLight.classification.assigned_lane_id | Identifier[] | TRAFFIC_LIGHT_STATE | lane_relation | 是 | C_UNIFY | TRAFFIC_LIGHT_STATE | lane_ids | DIRECT_STANDARD | 判断车道、路口、道路类型、限速和附着条件 |
| ROAD.value | ASAM OSI 3.8.0 | TrafficSign speed-limit classification value or t_road_type_speed.@max normalized to km/h | double / km/h | SPEED_LIMIT_STATE | value | 是 | A_REUSE | SPEED_LIMIT_STATE | value | DERIVED | 判断车道、路口、道路类型、限速和附着条件 |
| SURROUNDING_OBJECT.region | SYSTEM DERIVATION | derived from free-space geometry | enum | FREE_SPACE_STATE | — | 否 | B_EXTEND | FREE_SPACE_STATE | region | DERIVED | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.free_space_probability | ASAM OSI 3.8.0 | FeatureData.free_space.free_space_probability | double / ratio | FREE_SPACE_STATE | free_space_probability | 是 | A_REUSE | FREE_SPACE_STATE | free_space_probability | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| SURROUNDING_OBJECT.geometry | ASAM OSI 3.8.0 | FeatureData.free_space geometry | object / m | FREE_SPACE_STATE | geometry | 是 | A_REUSE | FREE_SPACE_STATE | geometry | DIRECT_STANDARD | 判断开门、制动、变道和泊车周边碰撞风险 |
| ENVIRONMENT.ambient_illumination | ASAM OSI 3.8.0 | EnvironmentalConditions.ambient_illumination | enum / category | ENVIRONMENT_CONDITIONS | ambient_illumination | 是 | B_EXTEND | ENVIRONMENT_CONDITIONS | ambient_illumination | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.visibility | ASAM OpenSCENARIO XML 1.4.0 | normalized from Fog.@visualRange or trusted visibility source | double / m | ENVIRONMENT_CONDITIONS | — | 否 | B_EXTEND | ENVIRONMENT_CONDITIONS | visibility | DERIVED | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.weather | SYSTEM DERIVATION | normalized provider weather summary | enum | ENVIRONMENT_CONDITIONS | weather | 是 | A_REUSE | ENVIRONMENT_CONDITIONS | weather | DERIVED | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.precipitation | ASAM OSI 3.8.0 | compatibility-preserving precipitation observation | any | ENVIRONMENT_CONDITIONS | precipitation | 是 | A_REUSE | ENVIRONMENT_CONDITIONS | precipitation | DERIVED | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.fog | ASAM OSI 3.8.0 | compatibility-preserving fog observation | any | ENVIRONMENT_CONDITIONS | fog | 是 | A_REUSE | ENVIRONMENT_CONDITIONS | fog | DERIVED | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.precipitation_type | ASAM OpenSCENARIO XML 1.4.0 | Precipitation.@precipitationType | PrecipitationType / enum | ENVIRONMENT_CONDITIONS | precipitation | 是 | C_UNIFY | ENVIRONMENT_CONDITIONS | precipitation_type | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.precipitation_intensity | ASAM OpenSCENARIO XML 1.4.0 | Precipitation.@precipitationIntensity | Double / m/s | ENVIRONMENT_CONDITIONS | precipitation | 是 | C_UNIFY | ENVIRONMENT_CONDITIONS | precipitation_intensity | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.fog_visibility | ASAM OpenSCENARIO XML 1.4.0 | Fog.@visualRange | Double / m | ENVIRONMENT_CONDITIONS | fog | 是 | C_UNIFY | ENVIRONMENT_CONDITIONS | fog_visibility | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.time_of_day | ASAM OSI 3.8.0 | EnvironmentalConditions.time_of_day | enum / category | ENVIRONMENT_CONDITIONS | time_of_day | 是 | A_REUSE | ENVIRONMENT_CONDITIONS | time_of_day | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.ambient_temperature | ASAM OpenSCENARIO XML 1.4.0 | Weather.@temperature | Double / K | ENVIRONMENT_CONDITIONS | — | 否 | B_EXTEND | ENVIRONMENT_CONDITIONS | ambient_temperature | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.atmospheric_pressure | ASAM OSI 3.8.0 | EnvironmentalConditions.atmospheric_pressure | double / Pa | ENVIRONMENT_CONDITIONS | — | 否 | B_EXTEND | ENVIRONMENT_CONDITIONS | atmospheric_pressure | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.relative_humidity | ASAM OSI 3.8.0 | EnvironmentalConditions.relative_humidity | double / percent | ENVIRONMENT_CONDITIONS | — | 否 | B_EXTEND | ENVIRONMENT_CONDITIONS | relative_humidity | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.sun_azimuth | ASAM OpenSCENARIO XML 1.4.0 | Sun.@azimuth | Double / rad | ENVIRONMENT_CONDITIONS | — | 否 | B_EXTEND | ENVIRONMENT_CONDITIONS | sun_azimuth | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.sun_elevation | ASAM OpenSCENARIO XML 1.4.0 | Sun.@elevation | Double / rad | ENVIRONMENT_CONDITIONS | — | 否 | B_EXTEND | ENVIRONMENT_CONDITIONS | sun_elevation | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ENVIRONMENT.sun_illuminance | ASAM OpenSCENARIO XML 1.4.0 | Sun.@illuminance | Double / lx | ENVIRONMENT_CONDITIONS | — | 否 | B_EXTEND | ENVIRONMENT_CONDITIONS | sun_illuminance | DIRECT_STANDARD | 判断照明、能见度、降水、雾和天气风险 |
| ADAS.feature | Android Automotive VHAL (Android 16 local snapshot) | property identity normalized to AEB/FCW/BSW/LSAEB/LSCW/CROSS_TRAFFIC | enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | COLLISION_ASSIST_STATE | feature | DERIVED | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.area | Android Automotive VHAL (Android 16 local snapshot) | VehicleArea (for example MIRROR for BSW) normalized to area | enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | COLLISION_ASSIST_STATE | area | DERIVED | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.enabled | Android Automotive VHAL (Android 16 local snapshot) | *_ENABLED | boolean | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | COLLISION_ASSIST_STATE | enabled | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.state | Android Automotive VHAL (Android 16 local snapshot) | *_STATE | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | COLLISION_ASSIST_STATE | state | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.warning_level | Android Automotive VHAL (Android 16 local snapshot) | normalized feature-specific warning enum | enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | COLLISION_ASSIST_STATE | warning_level | DERIVED | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.error_state | Android Automotive VHAL (Android 16 local snapshot) | ErrorState | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | COLLISION_ASSIST_STATE | error_state | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.feature | Android Automotive VHAL (Android 16 local snapshot) | property identity normalized to LDW/LKA/LCA/ELKA | enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | LANE_ASSIST_STATE | feature | DERIVED | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.enabled | Android Automotive VHAL (Android 16 local snapshot) | LANE_*_ENABLED / EMERGENCY_LANE_KEEP_ASSIST_ENABLED | boolean | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | LANE_ASSIST_STATE | enabled | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.state | Android Automotive VHAL (Android 16 local snapshot) | LANE_*_STATE / EMERGENCY_LANE_KEEP_ASSIST_STATE | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | LANE_ASSIST_STATE | state | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| ADAS.error_state | Android Automotive VHAL (Android 16 local snapshot) | ErrorState | int32 enum | EVIDENCE_SPACE_GAP | — | 否 | D_NEW_TYPE | LANE_ASSIST_STATE | error_state | DIRECT_STANDARD | 判断辅助驾驶功能是否启用、介入、告警或故障 |
| AUTHORIZATION.authentication_state | PROJECT INTERNAL SECURITY | trusted authentication backend state | any | AUTHORIZATION_STATE | authentication_state | 是 | A_REUSE | AUTHORIZATION_STATE | authentication_state | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.authenticated | PROJECT INTERNAL SECURITY | trusted authentication result | boolean | AUTHORIZATION_STATE | authenticated | 是 | A_REUSE | AUTHORIZATION_STATE | authenticated | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.subject_role | PROJECT INTERNAL SECURITY | trusted backend subject role | string | AUTHORIZATION_STATE | subject_role | 是 | A_REUSE | AUTHORIZATION_STATE | subject_role | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.subject_zone | PROJECT INTERNAL SECURITY | trusted backend subject zone | string | AUTHORIZATION_STATE | subject_zone | 是 | A_REUSE | AUTHORIZATION_STATE | subject_zone | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.intent_authorizations | PROJECT INTERNAL SECURITY | per-occurrence authorization decisions | array | AUTHORIZATION_STATE | intent_authorizations | 是 | A_REUSE | AUTHORIZATION_STATE | intent_authorizations | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.intent_authorizations[].clause_index | PROJECT INTERNAL SECURITY | semantic clause occurrence index | number / index | AUTHORIZATION_STATE | clause_index | 是 | A_REUSE | AUTHORIZATION_STATE | intent_authorizations[].clause_index | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.intent_authorizations[].intent_id | PROJECT INTERNAL SECURITY | canonical intent identity | string | AUTHORIZATION_STATE | intent_id | 是 | A_REUSE | AUTHORIZATION_STATE | intent_authorizations[].intent_id | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.intent_authorizations[].control_domain | PROJECT INTERNAL SECURITY | protected control domain | string | AUTHORIZATION_STATE | control_domain | 是 | A_REUSE | AUTHORIZATION_STATE | intent_authorizations[].control_domain | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.intent_authorizations[].permission_label | PROJECT INTERNAL SECURITY | authorization policy result label | string | AUTHORIZATION_STATE | permission_label | 是 | A_REUSE | AUTHORIZATION_STATE | intent_authorizations[].permission_label | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.intent_authorizations[].permission_score | PROJECT INTERNAL SECURITY | authorization policy score | number / score | AUTHORIZATION_STATE | permission_score | 是 | A_REUSE | AUTHORIZATION_STATE | intent_authorizations[].permission_score | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.intent_authorizations[].authorized | PROJECT INTERNAL SECURITY | occurrence authorization result | boolean | AUTHORIZATION_STATE | authorized | 是 | A_REUSE | AUTHORIZATION_STATE | intent_authorizations[].authorized | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| AUTHORIZATION.authorized_for_request | PROJECT INTERNAL SECURITY | aggregate request authorization result | boolean | AUTHORIZATION_STATE | authorized_for_request | 是 | A_REUSE | AUTHORIZATION_STATE | authorized_for_request | INTERNAL_SECURITY | 阻止未授权主体或区域执行车控 |
| SYSTEM_RUNTIME.vehicle_mode | PROJECT INTERNAL SECURITY | trusted vehicle runtime mode | enum | SYSTEM_MODE | vehicle_mode | 是 | A_REUSE | SYSTEM_MODE | vehicle_mode | INTERNAL_SECURITY | 阻止用户声明伪造模拟、测试或安全约束状态 |
| SYSTEM_RUNTIME.safety_constraint | PROJECT INTERNAL SECURITY | protected safety constraint state | enum | SYSTEM_MODE | safety_constraint | 是 | A_REUSE | SYSTEM_MODE | safety_constraint | INTERNAL_SECURITY | 阻止用户声明伪造模拟、测试或安全约束状态 |
| SYSTEM_RUNTIME.simulation | PROJECT INTERNAL SECURITY | trusted adapter/runtime provenance | boolean | SYSTEM_MODE | runtime_mode | 是 | B_EXTEND | SYSTEM_MODE | simulation | INTERNAL_SECURITY | 阻止用户声明伪造模拟、测试或安全约束状态 |
| SYSTEM_RUNTIME.test_mode | PROJECT INTERNAL SECURITY | trusted runtime configuration | boolean | SYSTEM_MODE | — | 否 | B_EXTEND | SYSTEM_MODE | test_mode | INTERNAL_SECURITY | 阻止用户声明伪造模拟、测试或安全约束状态 |
| SYSTEM_RUNTIME.degraded | PROJECT INTERNAL SECURITY | runtime capability health | boolean | SYSTEM_MODE | — | 否 | B_EXTEND | SYSTEM_MODE | degraded | INTERNAL_SECURITY | 阻止用户声明伪造模拟、测试或安全约束状态 |

## 五套标准带来的直接能力

- **COVESA VSS 6.0**：贡献 75 个最终 DIRECT_STANDARD 字段。
- **ASAM OSI 3.8.0**：贡献 27 个最终 DIRECT_STANDARD 字段。
- **ASAM OpenSCENARIO XML 1.4.0**：贡献 9 个最终 DIRECT_STANDARD 字段。
- **ASAM OpenDRIVE 1.9.0**：贡献 6 个最终 DIRECT_STANDARD 字段。
- **Android Automotive VHAL (Android 16 local snapshot)**：贡献 19 个最终 DIRECT_STANDARD 字段。

- VSS：自车速度/加速度、挡位、行车与驻车制动、转向、车门/窗、灯光、雨刮、HVAC、座椅、镜面和乘员信号。
- OSI：运动/静止目标分类与空间运动、传感器视图技术来源、环境、乘员、车道/逻辑车道和 ground-truth 来源标识。
- OpenSCENARIO：动态天气、降水、雾视距、太阳照度、路面湿润和摩擦缩放。
- OpenDRIVE：静态道路类型、车道段、路口关系、交通规则和 CRG 表面引用；不把静态表面引用冒充实时附着。
- Android VHAL：AEB/FCW/BSW、LDW/LKA/LCA/ELKA、巡航/ACC、座椅占用、手握方向盘、困倦和分心状态。

## 反向场景验收

| 场景 | KnowledgeNode 只引用的母类 | runtime contract 可表达字段 | 当前接入结论 |
|---|---|---|---|
| BRAKE | `SERVICE_BRAKE_STATE`, `VEHICLE_SPEED`, `ROAD_FRICTION_STATE`; optional `PARKING_BRAKE_STATE`, `GEAR_STATE` | brake/pedal/emergency、speed、road_condition/wetness/friction、parking brake、gear | 可完整表达；驻车制动无可靠接入，摩擦仅有模拟类别，数值估计仍为空 |
| DOOR_OPEN RIGHT_REAR | `VEHICLE_SPEED`, `DOOR_STATE`, `SURROUNDING_OBJECT_STATE` | door `area=RIGHT_REAR`; object `region=REAR_RIGHT`, entity_kind, distance, relative_speed, motion_state, risk_level | contract 可完整表达；当前仅有模拟前后最近距离，无 bicycle/pedestrian/motorcycle 分类与相对速度，必须保持 PARTIAL/UNAVAILABLE |
| HEADLIGHT OFF | `ENVIRONMENT_CONDITIONS`, `VEHICLE_SPEED`, `LIGHTING_STATE` | illumination, visibility, precipitation, fog, speed, lamp states | contract 可完整表达；模拟器只有 ambient_light/weather/headlight_state，visibility 与细分天气仍为空 |
| WIPER | `WIPER_STATE`, `ENVIRONMENT_CONDITIONS`, `VEHICLE_SPEED` | wiper mode/intensity/frequency/wiping/error, precipitation, vehicle motion predicate | contract 可完整表达；WIPER_STATE 当前 UNAVAILABLE，降水细分也未真实接入 |

## KnowledgeNode 消费者审计

扫描 `data/knowledge_nodes_v4.jsonl` 与 `data/knowledge/trusted_nodes.mock.jsonl` 共 124 个节点，发现 74 个不同 Evidence 引用值。车控主链和本轮四个场景均可由 canonical 母类表达，KnowledgeNode schema 未修改。

完整知识语料还含以下非 canonical 引用，它们不能作为第二 namespace 继续在线使用：

`ACCELERATION_STATE`, `ACCESS_LOG`, `ADS_STATE`, `APP_INTEGRITY_STATE`, `ASSET_STATE`, `AUTHENTICATION_STATE`, `BATTERY_STATE`, `COMMAND_VALIDITY_STATE`, `COMMUNICATION_LOG`, `COMMUNICATION_STATE`, `CSMS_STATE`, `DATA_ACCESS_STATE`, `DATA_ANONYMIZATION_STATE`, `DATA_CATEGORY`, `DATA_CLASSIFICATION_STATE`, `DATA_COLLECTION_STATE`, `DATA_DELETE_STATE`, `DATA_ENCRYPTION_STATE`, `DATA_INTEGRITY_STATE`, `DATA_LOCATION_STATE`, `DATA_SECURITY_MANAGEMENT_STATE`, `DATA_STORAGE_STATE`, `DATA_USE_STATE`, `DATA_VALIDITY_STATE`, `EMERGENCY_PLAN_STATE`, `EMERGENCY_STATE`, `INTERFACE_STATE`, `KEY_STATE`, `LOG_RETENTION_STATE`, `NON_CANONICAL_TYPE`, `NOTIFICATION_STATE`, `PACKAGE_INTEGRITY_STATE`, `PRODUCT_COMPLIANCE_STATE`, `RISK_ASSESSMENT_STATE`, `SECURITY_EVENT_STATE`, `SECURITY_LEVEL_STATE`, `SECURITY_LOG_STATE`, `SECURITY_MANAGEMENT_STATE`, `SECURITY_STATE`, `SOFTWARE_VERSION`, `STORAGE_STATE`, `SYSTEM_FAILURE_STATE`, `THREAT_STATE`, `UPDATE_STATE`, `USER_CONSENT_STATE`, `VEHICLE_STATIONARY`, `VULNERABILITY_STATE`, `WEATHER`

其中 `WEATHER` 应统一引用 `ENVIRONMENT_CONDITIONS`，`VEHICLE_STATIONARY` 应引用 `VEHICLE_SPEED`，`ACCELERATION_STATE` 应迁移为 `VEHICLE_ACCELERATION`；`NON_CANONICAL_TYPE` 是明确错误样本。其余多数为网络安全、数据治理、OTA/合规领域，超出本轮车辆运行 Evidence Space 的标准输入范围，保留为明确 Gap，不能凭名称批量造类型。

## Evidence Space Gap

1. 真实 CAMERA/RADAR/LIDAR/ULTRASONIC 尚未接入；OSI 对象分类、八方向、相对速度和风险字段目前只能由未来真实适配器或明确 SIMULATION 产生。
2. WIPER、驻车制动、车道/道路结构、ADAS 和驾驶员监测均有正式 contract，但当前 runtime 为 UNAVAILABLE。
3. 当前环境模拟器没有真实 visibility、precipitation intensity、fog visual range、wetness 或 friction scale，不得由 `weather` 字符串伪造。
4. OpenDRIVE 的 CRG surface 是静态表面引用，不等同于实时路面湿滑或附着系数。
5. 全知识语料中的网络安全、数据治理、OTA 和合规 Evidence 引用尚未建立相应标准驱动空间；本轮保持显式非 canonical Gap。

## 十二类来源性质总结

- 系统派生重点：八方向 `region`、`entity_kind` 归一化、`exists`、`distance`、`relative_speed`、`motion_state`、`risk_level`、当前车道关联、是否位于路口、天气摘要、可用性与质量指标。
- 内部安全重点：`AUTHORIZATION_STATE` 全部字段、`SYSTEM_MODE` 全部字段，以及 common envelope 的 runtime availability。
- 其余标为 DIRECT_STANDARD 的字段均可追到本地机器可读标准文件和实际实体/字段；没有把派生值写成标准原生字段。

## 最终回答

1. 现有 32 类覆盖最终 38 个母类目标中的 32 个（84.2%），但多个母类需要字段扩展。
2. 需要扩字段或统一结构的类型可由矩阵 `B_EXTEND`/`C_UNIFY` 行逐项审计。
3. 真正缺失的新母类共 6 个：车辆加速度、HVAC、道路结构、碰撞辅助、车道辅助、驾驶员监测。
4. 最终 Evidence Space 为 38 个 canonical 类型。
5-9. 五套标准贡献见“实际读取材料”“直接能力”和完整矩阵。
10. 系统派生字段见 `mapping_kind=DERIVED` 的全部矩阵行。
11. 内部安全字段见 `mapping_kind=INTERNAL_SECURITY` 的全部矩阵行。
12. 当前车控知识库与四个验收场景在 contract 层均可表达；部分事实尚无真实 runtime 数据。
13. 剩余 Gap 见上一节，尤其是真实传感器、动态环境、道路/ADAS 接入和非车控网络安全语料。
