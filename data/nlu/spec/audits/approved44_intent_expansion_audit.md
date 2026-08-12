# SYS-014 Approved-44 → User-Level Intent Expansion Completeness Audit

> 审计性质：只读设计审计。未修改 Registry、runtime，未生成训练数据，未训练模型，未打开 Safety Gold。

## 结论

- `APPROVED_44_EXPANSION_COMPLETE = NO`
- `CURRENT_87_VSS_INTENTS_CORRECT = NO`
- 数量审计后仍为 87，但组成与参数合同不正确：应新增 2、合并 2，并修复 8 个参数/Slot 合同问题。

## 核心数量

| 指标 | 值 |
|---|---:|
| `APPROVED_CAPABILITY_COUNT` | 44 |
| `DISTINCT_USER_CONTROL_OBJECT_COUNT` | 35 |
| `CURRENT_REGISTRY_VSS_INTENT_COUNT` | 87 |
| `AUDITED_REQUIRED_VSS_INTENT_COUNT` | 87 |
| `PROJECT_NATIVE_INTENT_COUNT` | 8 |
| `AUDITED_FINAL_INTENT_COUNT` | 95 |
| `MISSING_VSS_USER_OPERATION_COUNT` | 2 |
| `OVER_EXPANDED_INTENT_COUNT` | 2 |
| `SEMANTIC_MISMATCH_COUNT` | 8 |
| `POSSIBLE_DUPLICATE_INTENT_COUNT` | 0 |
| `UNSUPPORTED_VSS_DERIVED_INTENT_COUNT` | 0 |
| `REVIEW_REQUIRED_CAPABILITY_COUNT` | 0 |

## 权威输入与交叉校验

- 最终人工工作簿：`新语证_VSS6.0_113能力筛选表_v0.2.xlsx` / `113能力筛选` / `A1:I45`，数据行 44。
- Stage 2.1 文档明确：这 44 项全部为 `HUMAN_APPROVED`；未出现的 69 项为 `HUMAN_REJECTED`。本审计未用‘有效（建议）’字段推定批准状态。
- VSS 原始 actuator：643；normalized actuator：641；candidate：641。
- 44 项重建映射包含 220 个 actuator occurrence / 220 个唯一 VSS path；每项均与工作簿 `VSS actuator数` 相等。
- 来源缺口：仓库未发现独立的‘257 semantics / 113 atomic clusters’或 standalone capability merge mapping 文件；113→44 人工范围由最终工作簿与 Stage 2.1 文档交叉确认，能力→VSS path 映射按工作簿 actuator count 从 normalized VSS 资产重建并逐项 assert。

## 44 能力 → 对象 → 操作 → Intent 主表

| 序号 | approved_capability_id | 功能族 | 中文能力 | user_target_object | VSS actuator paths | user_operations | required_slots | optional_slots | expected_intents | current_registry_intents | status |
|---:|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BODY_MIRROR_HEATING | 外后视镜 | 外后视镜加热 | 外后视镜 | ["Vehicle.Body.Mirrors.DriverSide.IsHeatingOn","Vehicle.Body.Mirrors.PassengerSide.IsHeatingOn"] | ["ON","OFF"] | {"MIRROR_HEATING_ON":[],"MIRROR_HEATING_OFF":[]} | {"MIRROR_HEATING_ON":["AREA","NEGATION"],"MIRROR_HEATING_OFF":["AREA","NEGATION"]} | ["MIRROR_HEATING_ON","MIRROR_HEATING_OFF"] | ["MIRROR_HEATING_ON","MIRROR_HEATING_OFF"] | COMPLETE |
| 2 | BODY_MIRROR_ADJUSTMENT_LOCK | 外后视镜 | 外后视镜调节锁定 | 外后视镜 | ["Vehicle.Body.Mirrors.DriverSide.IsLocked","Vehicle.Body.Mirrors.PassengerSide.IsLocked"] | ["LOCK","UNLOCK"] | {"MIRROR_ADJUSTMENT_LOCK":[],"MIRROR_ADJUSTMENT_UNLOCK":[]} | {"MIRROR_ADJUSTMENT_LOCK":["AREA","NEGATION"],"MIRROR_ADJUSTMENT_UNLOCK":["AREA","NEGATION"]} | ["MIRROR_ADJUSTMENT_LOCK","MIRROR_ADJUSTMENT_UNLOCK"] | ["MIRROR_ADJUSTMENT_LOCK","MIRROR_ADJUSTMENT_UNLOCK"] | COMPLETE |
| 3 | SEAT_LONGITUDINAL_POSITION | 座椅 | 座椅前后位置调节 | 座椅 | ["Vehicle.Cabin.Seat.Row1.DriverSide.IsBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.IsForwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.Position","Vehicle.Cabin.Seat.Row1.Middle.IsBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.IsForwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.Position","Vehicle.Cabin.Seat.Row1.PassengerSide.IsBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.IsForwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.Position","Vehicle.Cabin.Seat.Row2.DriverSide.IsBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.IsForwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.Position","Vehicle.Cabin.Seat.Row2.Middle.IsBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.IsForwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.Position","Vehicle.Cabin.Seat.Row2.PassengerSide.IsBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.IsForwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.Position"] | ["SET_POSITION"] | {"SEAT_LONGITUDINAL_SET_POSITION":["AREA","ONE_OF(VALUE,DIRECTION)"]} | {"SEAT_LONGITUDINAL_SET_POSITION":["NEGATION"]} | ["SEAT_LONGITUDINAL_SET_POSITION"] | ["SEAT_LONGITUDINAL_SET_POSITION"] | SEMANTIC_MISMATCH |
| 4 | SEAT_TILT | 座椅 | 座椅整体倾角调节 | 座椅 | ["Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltForwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.Tilt","Vehicle.Cabin.Seat.Row1.Middle.IsTiltBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.IsTiltForwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.Tilt","Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltForwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.Tilt","Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltForwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.Tilt","Vehicle.Cabin.Seat.Row2.Middle.IsTiltBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.IsTiltForwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.Tilt","Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltForwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.Tilt"] | ["SET_ANGLE"] | {"SEAT_TILT_SET_ANGLE":["AREA","ONE_OF(VALUE,DIRECTION)"]} | {"SEAT_TILT_SET_ANGLE":["NEGATION"]} | ["SEAT_TILT_SET_ANGLE"] | ["SEAT_TILT_SET_ANGLE"] | SEMANTIC_MISMATCH |
| 5 | SEAT_BACKREST_RECLINE | 座椅 | 座椅靠背角度调节 | 座椅 | ["Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineForwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.Recline","Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineForwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.Backrest.Recline","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineForwardSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.Recline","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineForwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.Recline","Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineForwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.Backrest.Recline","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineForwardSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.Recline"] | ["SET_ANGLE"] | {"SEAT_BACKREST_SET_ANGLE":["AREA","ONE_OF(VALUE,DIRECTION)"]} | {"SEAT_BACKREST_SET_ANGLE":["NEGATION"]} | ["SEAT_BACKREST_SET_ANGLE"] | ["SEAT_BACKREST_SET_ANGLE"] | SEMANTIC_MISMATCH |
| 6 | SEAT_HEIGHT | 座椅 | 座椅高度调节 | 座椅 | ["Vehicle.Cabin.Seat.Row1.DriverSide.Height","Vehicle.Cabin.Seat.Row1.DriverSide.IsDownSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.IsUpSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.Height","Vehicle.Cabin.Seat.Row1.Middle.IsDownSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.IsUpSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.Height","Vehicle.Cabin.Seat.Row1.PassengerSide.IsDownSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.IsUpSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.Height","Vehicle.Cabin.Seat.Row2.DriverSide.IsDownSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.IsUpSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.Height","Vehicle.Cabin.Seat.Row2.Middle.IsDownSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.IsUpSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.Height","Vehicle.Cabin.Seat.Row2.PassengerSide.IsDownSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.IsUpSwitchEngaged"] | ["SET_POSITION"] | {"SEAT_HEIGHT_SET_POSITION":["AREA","ONE_OF(VALUE,DIRECTION)"]} | {"SEAT_HEIGHT_SET_POSITION":["NEGATION"]} | ["SEAT_HEIGHT_SET_POSITION"] | ["SEAT_HEIGHT_SET_POSITION"] | SEMANTIC_MISMATCH |
| 7 | SEAT_LUMBAR_SUPPORT | 座椅 | 腰托调节 | 座椅 | ["Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.BottomLumbarSupport","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarDownSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarUpSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarHeight","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarSupport","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.MidLumbarSupport","Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.TopLumbarSupport","Vehicle.Cabin.Seat.Row1.Middle.Backrest.BottomLumbarSupport","Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLessLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarDownSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarUpSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarHeight","Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarSupport","Vehicle.Cabin.Seat.Row1.Middle.Backrest.MidLumbarSupport","Vehicle.Cabin.Seat.Row1.Middle.Backrest.TopLumbarSupport","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.BottomLumbarSupport","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarDownSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarUpSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarHeight","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarSupport","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.MidLumbarSupport","Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.TopLumbarSupport","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.BottomLumbarSupport","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarDownSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarUpSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarHeight","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarSupport","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.MidLumbarSupport","Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.TopLumbarSupport","Vehicle.Cabin.Seat.Row2.Middle.Backrest.BottomLumbarSupport","Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLessLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarDownSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarUpSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarHeight","Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarSupport","Vehicle.Cabin.Seat.Row2.Middle.Backrest.MidLumbarSupport","Vehicle.Cabin.Seat.Row2.Middle.Backrest.TopLumbarSupport","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.BottomLumbarSupport","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarDownSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarUpSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarHeight","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarSupport","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.MidLumbarSupport","Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.TopLumbarSupport"] | ["SET_HEIGHT","SET_SUPPORT"] | {"SEAT_LUMBAR_SET_HEIGHT":["AREA","ONE_OF(VALUE,DIRECTION)"],"SEAT_LUMBAR_SET_SUPPORT":["AREA","ONE_OF(VALUE,DIRECTION)"]} | {"SEAT_LUMBAR_SET_HEIGHT":["NEGATION"],"SEAT_LUMBAR_SET_SUPPORT":["MODE","NEGATION"]} | ["SEAT_LUMBAR_SET_HEIGHT","SEAT_LUMBAR_SET_SUPPORT"] | ["SEAT_LUMBAR_SET_HEIGHT","SEAT_LUMBAR_SET_SUPPORT"] | SEMANTIC_MISMATCH |
| 8 | CHASSIS_STEERING_WHEEL_POSITION | 方向盘舒适/位置 | 方向盘位置调节 | 方向盘 | ["Vehicle.Chassis.SteeringWheel.Extension","Vehicle.Chassis.SteeringWheel.Tilt"] | ["SET_EXTENSION","SET_TILT"] | {"STEERING_WHEEL_SET_EXTENSION":["VALUE"],"STEERING_WHEEL_SET_TILT":["VALUE"]} | {"STEERING_WHEEL_SET_EXTENSION":["DIRECTION","NEGATION"],"STEERING_WHEEL_SET_TILT":["DIRECTION","NEGATION"]} | ["STEERING_WHEEL_SET_EXTENSION","STEERING_WHEEL_SET_TILT"] | ["STEERING_WHEEL_SET_EXTENSION","STEERING_WHEEL_SET_TILT"] | COMPLETE |
| 9 | CABIN_HVAC_DEFROST | 空调与热管理 | 前/后除霜除雾控制 | 除霜除雾系统 | ["Vehicle.Cabin.HVAC.IsFrontDefrosterActive","Vehicle.Cabin.HVAC.IsRearDefrosterActive"] | ["ON","OFF"] | {"DEFROST_ON":[],"DEFROST_OFF":[]} | {"DEFROST_ON":["AREA","NEGATION"],"DEFROST_OFF":["AREA","NEGATION"]} | ["DEFROST_ON","DEFROST_OFF"] | ["DEFROST_ON","DEFROST_OFF"] | COMPLETE |
| 10 | BODY_WINDSHIELD_HEATING | 风挡与雨刮 | 前/后风挡加热 | 风挡玻璃 | ["Vehicle.Body.Windshield.Front.IsHeatingOn","Vehicle.Body.Windshield.Rear.IsHeatingOn"] | ["ON","OFF"] | {"WINDSHIELD_HEATING_ON":[],"WINDSHIELD_HEATING_OFF":[]} | {"WINDSHIELD_HEATING_ON":["AREA","NEGATION"],"WINDSHIELD_HEATING_OFF":["AREA","NEGATION"]} | ["WINDSHIELD_HEATING_ON","WINDSHIELD_HEATING_OFF"] | ["WINDSHIELD_HEATING_ON","WINDSHIELD_HEATING_OFF"] | COMPLETE |
| 11 | ADAS_ABS_ENABLE | ADAS安全/辅助功能开关 | ABS启用状态控制 | ABS | ["Vehicle.ADAS.ABS.IsEnabled"] | ["ENABLE","DISABLE"] | {"ABS_ENABLE":[],"ABS_DISABLE":[]} | {"ABS_ENABLE":["NEGATION"],"ABS_DISABLE":["NEGATION"]} | ["ABS_ENABLE","ABS_DISABLE"] | ["ABS_ENABLE","ABS_DISABLE"] | COMPLETE |
| 12 | ADAS_TCS_ENABLE | ADAS安全/辅助功能开关 | 牵引力控制系统启用控制 | TCS | ["Vehicle.ADAS.TCS.IsEnabled"] | ["ENABLE","DISABLE"] | {"TCS_ENABLE":[],"TCS_DISABLE":[]} | {"TCS_ENABLE":["NEGATION"],"TCS_DISABLE":["NEGATION"]} | ["TCS_ENABLE","TCS_DISABLE"] | ["TCS_ENABLE","TCS_DISABLE"] | COMPLETE |
| 13 | ADAS_EBD_ENABLE | ADAS安全/辅助功能开关 | 电子制动力分配系统启用控制 | EBD | ["Vehicle.ADAS.EBD.IsEnabled"] | ["ENABLE","DISABLE"] | {"EBD_ENABLE":[],"EBD_DISABLE":[]} | {"EBD_ENABLE":["NEGATION"],"EBD_DISABLE":["NEGATION"]} | ["EBD_ENABLE","EBD_DISABLE"] | ["EBD_ENABLE","EBD_DISABLE"] | COMPLETE |
| 14 | ADAS_EBA_ENABLE | ADAS安全/辅助功能开关 | 紧急制动辅助系统启用控制 | EBA | ["Vehicle.ADAS.EBA.IsEnabled"] | ["ENABLE","DISABLE"] | {"EBA_ENABLE":[],"EBA_DISABLE":[]} | {"EBA_ENABLE":["NEGATION"],"EBA_DISABLE":["NEGATION"]} | ["EBA_ENABLE","EBA_DISABLE"] | ["EBA_ENABLE","EBA_DISABLE"] | COMPLETE |
| 15 | ADAS_ESC_ENABLE | ADAS安全/辅助功能开关 | 车身电子稳定系统启用控制 | ESC | ["Vehicle.ADAS.ESC.IsEnabled"] | ["ENABLE","DISABLE"] | {"ESC_ENABLE":[],"ESC_DISABLE":[]} | {"ESC_ENABLE":["NEGATION"],"ESC_DISABLE":["NEGATION"]} | ["ESC_ENABLE","ESC_DISABLE"] | ["ESC_ENABLE","ESC_DISABLE"] | COMPLETE |
| 16 | BODY_TRUNK_OPENING | 前/后行李厢 | 行李厢开合控制 | 行李厢 | ["Vehicle.Body.Trunk.Front.IsOpen","Vehicle.Body.Trunk.Front.Position","Vehicle.Body.Trunk.Front.Switch","Vehicle.Body.Trunk.Rear.IsOpen","Vehicle.Body.Trunk.Rear.Position","Vehicle.Body.Trunk.Rear.Switch"] | ["OPEN","CLOSE","SET_POSITION"] | {"TRUNK_OPEN":[],"TRUNK_CLOSE":[],"TRUNK_SET_POSITION":["VALUE"]} | {"TRUNK_OPEN":["AREA","NEGATION"],"TRUNK_CLOSE":["AREA","NEGATION"],"TRUNK_SET_POSITION":["AREA","NEGATION"]} | ["TRUNK_OPEN","TRUNK_CLOSE","TRUNK_SET_POSITION"] | ["TRUNK_OPEN","TRUNK_CLOSE","TRUNK_SET_POSITION"] | COMPLETE |
| 17 | BODY_TRUNK_LOCK | 前/后行李厢 | 行李厢锁控制 | 行李厢 | ["Vehicle.Body.Trunk.Front.IsLocked","Vehicle.Body.Trunk.Rear.IsLocked"] | ["LOCK","UNLOCK"] | {"TRUNK_LOCK":[],"TRUNK_UNLOCK":[]} | {"TRUNK_LOCK":["AREA","NEGATION"],"TRUNK_UNLOCK":["AREA","NEGATION"]} | ["TRUNK_LOCK","TRUNK_UNLOCK"] | ["TRUNK_LOCK","TRUNK_UNLOCK"] | COMPLETE |
| 18 | BODY_HOOD | 前舱盖 | 前舱盖开合控制 | 前舱盖 | ["Vehicle.Body.Hood.IsOpen","Vehicle.Body.Hood.Position","Vehicle.Body.Hood.Switch"] | ["OPEN","CLOSE","SET_POSITION"] | {"HOOD_OPEN":[],"HOOD_CLOSE":[],"HOOD_SET_POSITION":["VALUE"]} | {"HOOD_OPEN":["NEGATION"],"HOOD_CLOSE":["NEGATION"],"HOOD_SET_POSITION":["NEGATION"]} | ["HOOD_OPEN","HOOD_CLOSE","HOOD_SET_POSITION"] | ["HOOD_OPEN","HOOD_CLOSE","HOOD_SET_POSITION"] | COMPLETE |
| 19 | TRANSMISSION_LOW_RANGE | 变速箱与传动 | 低速四驱/低速挡控制 | 低速挡 | ["Vehicle.Powertrain.Transmission.IsLowRangeEngaged"] | ["ENABLE","DISABLE"] | {"LOW_RANGE_ENABLE":[],"LOW_RANGE_DISABLE":[]} | {"LOW_RANGE_ENABLE":["NEGATION"],"LOW_RANGE_DISABLE":["NEGATION"]} | ["LOW_RANGE_ENABLE","LOW_RANGE_DISABLE"] | ["LOW_RANGE_ENABLE","LOW_RANGE_DISABLE"] | COMPLETE |
| 20 | TRANSMISSION_TORQUE_DISTRIBUTION | 变速箱与传动 | 前后轴扭矩分配控制 | 前后轴扭矩分配 | ["Vehicle.Powertrain.Transmission.TorqueDistribution"] | ["SET_DISTRIBUTION"] | {"TORQUE_DISTRIBUTION_SET":["VALUE"]} | {"TORQUE_DISTRIBUTION_SET":["DIRECTION","NEGATION"]} | ["TORQUE_DISTRIBUTION_SET"] | ["TORQUE_DISTRIBUTION_SET"] | COMPLETE |
| 21 | TRANSMISSION_PERFORMANCE_MODE | 变速箱与传动 | 变速箱性能模式选择 | 变速箱性能模式 | ["Vehicle.Powertrain.Transmission.PerformanceMode"] | ["SET_MODE"] | {"TRANSMISSION_PERFORMANCE_MODE_SET":["MODE"]} | {"TRANSMISSION_PERFORMANCE_MODE_SET":["NEGATION"]} | ["TRANSMISSION_PERFORMANCE_MODE_SET"] | ["TRANSMISSION_PERFORMANCE_MODE_SET"] | COMPLETE |
| 22 | TRANSMISSION_DIFF_LOCK | 变速箱与传动 | 差速锁控制 | 差速锁 | ["Vehicle.Powertrain.Transmission.DiffLockFrontEngagement","Vehicle.Powertrain.Transmission.DiffLockRearEngagement"] | ["LOCK","UNLOCK","SET_ENGAGEMENT"] | {"DIFFERENTIAL_LOCK":[],"DIFFERENTIAL_UNLOCK":[],"DIFFERENTIAL_SET_ENGAGEMENT":["VALUE"]} | {"DIFFERENTIAL_LOCK":["AREA","NEGATION"],"DIFFERENTIAL_UNLOCK":["AREA","NEGATION"],"DIFFERENTIAL_SET_ENGAGEMENT":["AREA","NEGATION"]} | ["DIFFERENTIAL_LOCK","DIFFERENTIAL_UNLOCK","DIFFERENTIAL_SET_ENGAGEMENT"] | ["DIFFERENTIAL_LOCK","DIFFERENTIAL_UNLOCK"] | MISSING |
| 23 | TRANSMISSION_GEAR_SELECTION | 变速箱与传动 | 挡位选择 | 挡位 | ["Vehicle.Powertrain.Transmission.SelectedGear"] | ["SET_GEAR"] | {"GEAR_SET":["ONE_OF(MODE,VALUE)"]} | {"GEAR_SET":["NEGATION"]} | ["GEAR_SET"] | ["GEAR_SET"] | SEMANTIC_MISMATCH |
| 24 | TRANSMISSION_ELECTRICAL_POWERTRAIN_ENGAGEMENT | 变速箱与传动 | 电驱动力结合控制 | 电驱动力结合机构 | ["Vehicle.Powertrain.Transmission.IsElectricalPowertrainEngaged"] | ["ENGAGE","DISENGAGE"] | {"ELECTRIC_POWERTRAIN_ENGAGE":[],"ELECTRIC_POWERTRAIN_DISENGAGE":[]} | {"ELECTRIC_POWERTRAIN_ENGAGE":["NEGATION"],"ELECTRIC_POWERTRAIN_DISENGAGE":["NEGATION"]} | ["ELECTRIC_POWERTRAIN_ENGAGE","ELECTRIC_POWERTRAIN_DISENGAGE"] | ["ELECTRIC_POWERTRAIN_ENGAGE","ELECTRIC_POWERTRAIN_DISENGAGE"] | COMPLETE |
| 25 | TRANSMISSION_CLUTCH | 变速箱与传动 | 离合器结合度控制 | 离合器 | ["Vehicle.Powertrain.Transmission.ClutchEngagement"] | ["SET_ENGAGEMENT"] | {"CLUTCH_SET_ENGAGEMENT":["VALUE"]} | {"CLUTCH_SET_ENGAGEMENT":["NEGATION"]} | ["CLUTCH_SET_ENGAGEMENT"] | ["CLUTCH_SET_ENGAGEMENT"] | COMPLETE |
| 26 | TRANSMISSION_GEAR_CHANGE_MODE | 变速箱与传动 | 自动/手动换挡模式 | 换挡模式 | ["Vehicle.Powertrain.Transmission.GearChangeMode"] | ["SET_MODE"] | {"GEAR_CHANGE_MODE_SET":["MODE"]} | {"GEAR_CHANGE_MODE_SET":["NEGATION"]} | ["GEAR_CHANGE_MODE_SET"] | ["GEAR_CHANGE_MODE_SET"] | COMPLETE |
| 27 | TRANSMISSION_PARK_LOCK | 变速箱与传动 | 驻车锁控制 | 驻车锁 | ["Vehicle.Powertrain.Transmission.IsParkLockEngaged"] | ["LOCK","UNLOCK"] | {"PARK_LOCK":[],"PARK_UNLOCK":[]} | {"PARK_LOCK":["NEGATION"],"PARK_UNLOCK":["NEGATION"]} | ["PARK_LOCK","PARK_UNLOCK"] | ["PARK_LOCK","PARK_UNLOCK"] | COMPLETE |
| 28 | BODY_HORN | 喇叭 | 喇叭控制 | 喇叭 | ["Vehicle.Body.Horn.IsActive"] | ["ACTIVATE","DEACTIVATE"] | {"HORN_ACTIVATE":[],"HORN_DEACTIVATE":[]} | {"HORN_ACTIVATE":["NEGATION"],"HORN_DEACTIVATE":["NEGATION"]} | ["HORN_ACTIVATE","HORN_DEACTIVATE"] | ["HORN_ACTIVATE"] | MISSING |
| 29 | BODY_MIRROR_FOLD | 外后视镜 | 外后视镜折叠 | 外后视镜 | ["Vehicle.Body.Mirrors.DriverSide.IsFolded","Vehicle.Body.Mirrors.PassengerSide.IsFolded"] | ["FOLD","UNFOLD"] | {"MIRROR_FOLD":[],"MIRROR_UNFOLD":[]} | {"MIRROR_FOLD":["AREA","NEGATION"],"MIRROR_UNFOLD":["AREA","NEGATION"]} | ["MIRROR_FOLD","MIRROR_UNFOLD"] | ["MIRROR_FOLD","MIRROR_UNFOLD"] | COMPLETE |
| 30 | BODY_MIRROR_ADJUSTMENT | 外后视镜 | 外后视镜角度调节 | 外后视镜 | ["Vehicle.Body.Mirrors.DriverSide.Tilt","Vehicle.Body.Mirrors.DriverSide.Yaw","Vehicle.Body.Mirrors.PassengerSide.Tilt","Vehicle.Body.Mirrors.PassengerSide.Yaw"] | ["SET_ANGLE"] | {"MIRROR_SET_ANGLE":["AREA","DIRECTION"]} | {"MIRROR_SET_ANGLE":["VALUE","NEGATION"]} | ["MIRROR_SET_ANGLE"] | ["MIRROR_SET_ANGLE"] | COMPLETE |
| 31 | CABIN_SUNROOF | 天窗与天窗遮阳帘 | 天窗开合控制 | 天窗 | ["Vehicle.Cabin.Sunroof.Switch"] | ["OPEN","CLOSE","SET_TILT"] | {"SUNROOF_OPEN":[],"SUNROOF_CLOSE":[],"SUNROOF_SET_TILT":["MODE"]} | {"SUNROOF_OPEN":["NEGATION"],"SUNROOF_CLOSE":["NEGATION"],"SUNROOF_SET_TILT":["NEGATION"]} | ["SUNROOF_OPEN","SUNROOF_CLOSE","SUNROOF_SET_TILT"] | ["SUNROOF_OPEN","SUNROOF_CLOSE","SUNROOF_SET_TILT"] | COMPLETE |
| 32 | ADAS_CRUISE_CONTROL | 巡航与跟车 | 巡航控制 | 巡航系统 | ["Vehicle.ADAS.CruiseControl.AdaptiveDistanceSet","Vehicle.ADAS.CruiseControl.AdaptiveIntervalSet","Vehicle.ADAS.CruiseControl.IsActive","Vehicle.ADAS.CruiseControl.IsAdaptive","Vehicle.ADAS.CruiseControl.IsEnabled","Vehicle.ADAS.CruiseControl.SpeedSet"] | ["ENABLE","DISABLE","SET_SPEED","SET_GAP"] | {"CRUISE_ENABLE":[],"CRUISE_DISABLE":[],"CRUISE_SET_SPEED":["VALUE"],"CRUISE_SET_GAP":["ONE_OF(VALUE,MODE)"]} | {"CRUISE_ENABLE":["NEGATION"],"CRUISE_DISABLE":["NEGATION"],"CRUISE_SET_SPEED":["NEGATION"],"CRUISE_SET_GAP":["NEGATION"]} | ["CRUISE_ENABLE","CRUISE_DISABLE","CRUISE_SET_SPEED","CRUISE_SET_GAP"] | ["CRUISE_ENABLE","CRUISE_DISABLE","CRUISE_SET_SPEED","CRUISE_SET_GAP"] | SEMANTIC_MISMATCH |
| 33 | BODY_MAIN_LIGHT_MODE | 车外灯光 | 主灯光模式控制 | 主灯开关 | ["Vehicle.Body.Lights.LightSwitch"] | ["SET_MODE"] | {"HEADLIGHT_SET_MODE":["MODE"]} | {"HEADLIGHT_SET_MODE":["NEGATION"]} | ["HEADLIGHT_SET_MODE"] | ["HEADLIGHT_ON","HEADLIGHT_OFF","HEADLIGHT_SET_MODE"] | OVER_EXPANDED |
| 34 | BODY_HAZARD_LIGHT | 车外灯光 | 危险警示灯控制 | 危险警示灯 | ["Vehicle.Body.Lights.Hazard.IsSignaling"] | ["ON","OFF"] | {"HAZARD_LIGHT_ON":[],"HAZARD_LIGHT_OFF":[]} | {"HAZARD_LIGHT_ON":["NEGATION"],"HAZARD_LIGHT_OFF":["NEGATION"]} | ["HAZARD_LIGHT_ON","HAZARD_LIGHT_OFF"] | ["HAZARD_LIGHT_ON","HAZARD_LIGHT_OFF"] | COMPLETE |
| 35 | BODY_TURN_INDICATOR | 车外灯光 | 转向灯控制 | 转向灯 | ["Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling","Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling"] | ["ON","OFF"] | {"TURN_INDICATOR_ON":["DIRECTION"],"TURN_INDICATOR_OFF":[]} | {"TURN_INDICATOR_ON":["NEGATION"],"TURN_INDICATOR_OFF":["DIRECTION","NEGATION"]} | ["TURN_INDICATOR_ON","TURN_INDICATOR_OFF"] | ["TURN_INDICATOR_ON","TURN_INDICATOR_OFF"] | COMPLETE |
| 36 | BODY_LOW_BEAM | 车外灯光 | 近光灯控制 | 近光灯 | ["Vehicle.Body.Lights.Beam.Low.IsOn"] | ["ON","OFF"] | {"LOW_BEAM_ON":[],"LOW_BEAM_OFF":[]} | {"LOW_BEAM_ON":["NEGATION"],"LOW_BEAM_OFF":["NEGATION"]} | ["LOW_BEAM_ON","LOW_BEAM_OFF"] | ["LOW_BEAM_ON","LOW_BEAM_OFF"] | COMPLETE |
| 37 | BODY_HIGH_BEAM | 车外灯光 | 远光灯控制 | 远光灯 | ["Vehicle.Body.Lights.Beam.High.IsOn","Vehicle.Body.Lights.IsHighBeamSwitchOn"] | ["ON","OFF"] | {"HIGH_BEAM_ON":[],"HIGH_BEAM_OFF":[]} | {"HIGH_BEAM_ON":["NEGATION"],"HIGH_BEAM_OFF":["NEGATION"]} | ["HIGH_BEAM_ON","HIGH_BEAM_OFF"] | ["HIGH_BEAM_ON","HIGH_BEAM_OFF"] | COMPLETE |
| 38 | BODY_FOG_LIGHT | 车外灯光 | 雾灯控制 | 雾灯 | ["Vehicle.Body.Lights.Fog.Front.IsOn","Vehicle.Body.Lights.Fog.Rear.IsOn"] | ["ON","OFF"] | {"FOG_LIGHT_ON":[],"FOG_LIGHT_OFF":[]} | {"FOG_LIGHT_ON":["AREA","NEGATION"],"FOG_LIGHT_OFF":["AREA","NEGATION"]} | ["FOG_LIGHT_ON","FOG_LIGHT_OFF"] | ["FOG_LIGHT_ON","FOG_LIGHT_OFF"] | COMPLETE |
| 39 | BODY_PARKING_LIGHT | 车外灯光 | 驻车灯控制 | 驻车灯 | ["Vehicle.Body.Lights.Parking.IsOn"] | ["ON","OFF"] | {"PARKING_LIGHT_ON":[],"PARKING_LIGHT_OFF":[]} | {"PARKING_LIGHT_ON":["NEGATION"],"PARKING_LIGHT_OFF":["NEGATION"]} | ["PARKING_LIGHT_ON","PARKING_LIGHT_OFF"] | ["PARKING_LIGHT_ON","PARKING_LIGHT_OFF"] | COMPLETE |
| 40 | CABIN_WINDOW | 车窗 | 车窗开合与开度控制 | 车窗 | ["Vehicle.Cabin.Door.Row1.DriverSide.Window.IsOpen","Vehicle.Cabin.Door.Row1.DriverSide.Window.Position","Vehicle.Cabin.Door.Row1.DriverSide.Window.Switch","Vehicle.Cabin.Door.Row1.PassengerSide.Window.IsOpen","Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position","Vehicle.Cabin.Door.Row1.PassengerSide.Window.Switch","Vehicle.Cabin.Door.Row2.DriverSide.Window.IsOpen","Vehicle.Cabin.Door.Row2.DriverSide.Window.Position","Vehicle.Cabin.Door.Row2.DriverSide.Window.Switch","Vehicle.Cabin.Door.Row2.PassengerSide.Window.IsOpen","Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position","Vehicle.Cabin.Door.Row2.PassengerSide.Window.Switch"] | ["OPEN","CLOSE","SET_POSITION"] | {"WINDOW_OPEN":[],"WINDOW_CLOSE":[],"WINDOW_SET_POSITION":["VALUE"]} | {"WINDOW_OPEN":["AREA","NEGATION"],"WINDOW_CLOSE":["AREA","NEGATION"],"WINDOW_SET_POSITION":["AREA","NEGATION"]} | ["WINDOW_OPEN","WINDOW_CLOSE","WINDOW_SET_POSITION"] | ["WINDOW_OPEN","WINDOW_CLOSE","WINDOW_SET_POSITION"] | COMPLETE |
| 41 | CABIN_DOOR_OPENING | 车门 | 车门开合控制 | 车门 | ["Vehicle.Cabin.Door.Row1.DriverSide.IsOpen","Vehicle.Cabin.Door.Row1.DriverSide.Position","Vehicle.Cabin.Door.Row1.DriverSide.Switch","Vehicle.Cabin.Door.Row1.PassengerSide.IsOpen","Vehicle.Cabin.Door.Row1.PassengerSide.Position","Vehicle.Cabin.Door.Row1.PassengerSide.Switch","Vehicle.Cabin.Door.Row2.DriverSide.IsOpen","Vehicle.Cabin.Door.Row2.DriverSide.Position","Vehicle.Cabin.Door.Row2.DriverSide.Switch","Vehicle.Cabin.Door.Row2.PassengerSide.IsOpen","Vehicle.Cabin.Door.Row2.PassengerSide.Position","Vehicle.Cabin.Door.Row2.PassengerSide.Switch"] | ["OPEN","CLOSE","SET_POSITION"] | {"DOOR_OPEN":[],"DOOR_CLOSE":[],"DOOR_SET_POSITION":["AREA","VALUE"]} | {"DOOR_OPEN":["AREA","NEGATION"],"DOOR_CLOSE":["AREA","NEGATION"],"DOOR_SET_POSITION":["NEGATION"]} | ["DOOR_OPEN","DOOR_CLOSE","DOOR_SET_POSITION"] | ["DOOR_OPEN","DOOR_CLOSE","DOOR_SET_POSITION"] | COMPLETE |
| 42 | CABIN_DOOR_LOCK | 车门 | 车门锁控制 | 车门 | ["Vehicle.Cabin.Door.Row1.DriverSide.IsLocked","Vehicle.Cabin.Door.Row1.PassengerSide.IsLocked","Vehicle.Cabin.Door.Row2.DriverSide.IsLocked","Vehicle.Cabin.Door.Row2.PassengerSide.IsLocked"] | ["LOCK","UNLOCK"] | {"DOOR_LOCK":[],"DOOR_UNLOCK":[]} | {"DOOR_LOCK":["AREA","NEGATION"],"DOOR_UNLOCK":["AREA","NEGATION"]} | ["DOOR_LOCK","DOOR_UNLOCK"] | ["DOOR_LOCK","DOOR_UNLOCK"] | COMPLETE |
| 43 | BODY_WIPER_USER_CONTROL | 风挡与雨刮 | 雨刮模式与灵敏度控制 | 雨刮 | ["Vehicle.Body.Windshield.Front.Wiping.Intensity","Vehicle.Body.Windshield.Front.Wiping.Mode","Vehicle.Body.Windshield.Rear.Wiping.Intensity","Vehicle.Body.Windshield.Rear.Wiping.Mode"] | ["SET_MODE","SET_SENSITIVITY"] | {"WIPER_SET_MODE":["MODE"],"WIPER_SET_SENSITIVITY":["VALUE"]} | {"WIPER_SET_MODE":["AREA","NEGATION"],"WIPER_SET_SENSITIVITY":["AREA","MODE","NEGATION"]} | ["WIPER_SET_MODE","WIPER_SET_SENSITIVITY"] | ["WIPER_SET_MODE","WIPER_SET_SENSITIVITY"] | COMPLETE |
| 44 | CHASSIS_PARKING_BRAKE | 驻车制动 | 驻车制动控制 | 驻车制动 | ["Vehicle.Chassis.ParkingBrake.IsAutoApplyEnabled","Vehicle.Chassis.ParkingBrake.IsEngaged"] | ["APPLY","RELEASE","AUTO_APPLY_ENABLE","AUTO_APPLY_DISABLE"] | {"PARKING_BRAKE_APPLY":[],"PARKING_BRAKE_RELEASE":[],"PARKING_BRAKE_AUTO_APPLY_ENABLE":[],"PARKING_BRAKE_AUTO_APPLY_DISABLE":[]} | {"PARKING_BRAKE_APPLY":["NEGATION"],"PARKING_BRAKE_RELEASE":["NEGATION"],"PARKING_BRAKE_AUTO_APPLY_ENABLE":["NEGATION"],"PARKING_BRAKE_AUTO_APPLY_DISABLE":["NEGATION"]} | ["PARKING_BRAKE_APPLY","PARKING_BRAKE_RELEASE","PARKING_BRAKE_AUTO_APPLY_ENABLE","PARKING_BRAKE_AUTO_APPLY_DISABLE"] | ["PARKING_BRAKE_APPLY","PARKING_BRAKE_RELEASE","PARKING_BRAKE_AUTO_APPLY_ENABLE","PARKING_BRAKE_AUTO_APPLY_DISABLE"] | COMPLETE |

## 需要新增的 VSS 用户操作

| capability_id | VSS path | operation | recommended intent | required slots | reason |
|---|---|---|---|---|---|
| TRANSMISSION_DIFF_LOCK | ["Vehicle.Powertrain.Transmission.DiffLockFrontEngagement","Vehicle.Powertrain.Transmission.DiffLockRearEngagement"] | SET_ENGAGEMENT | DIFFERENTIAL_SET_ENGAGEMENT | ["VALUE"] | 连续 Engagement actuator 支持 0..100 设置，LOCK/UNLOCK 仅覆盖端点。 |
| BODY_HORN | ["Vehicle.Body.Horn.IsActive"] | DEACTIVATE | HORN_DEACTIVATE | [] | Horn.IsActive 明示 True=Active、False=Inactive；停止持续鸣笛是可写用户级反向操作，不是反馈代理。 |

## 错误扩成独立 Intent 的操作

| capability_id | current intent | 应合并到 | Slot | reason |
|---|---|---|---|---|
| BODY_MAIN_LIGHT_MODE | HEADLIGHT_ON | HEADLIGHT_SET_MODE | MODE | 唯一来源 LightSwitch 是枚举 actuator；OFF 是枚举值，且 VSS 没有通用 ON 值，应由 SET_MODE + MODE 表达。 |
| BODY_MAIN_LIGHT_MODE | HEADLIGHT_OFF | HEADLIGHT_SET_MODE | MODE | 唯一来源 LightSwitch 是枚举 actuator；OFF 是枚举值，且 VSS 没有通用 ON 值，应由 SET_MODE + MODE 表达。 |

`OPERATIONS_WRONGLY_COLLAPSED_INTO_SLOTS = []`。未发现应独立成 Intent 却仅作为 Slot 的现有操作；差速锁结合度和喇叭停止属于完全缺失。

## 参数与 Slot 合同语义不匹配

| capability_id | current intents | 问题 | 推荐合同 |
|---|---|---|---|
| SEAT_LONGITUDINAL_POSITION | ["SEAT_LONGITUDINAL_SET_POSITION"] | VSS 同时提供 Position 与 Forward/Backward switch；当前 Registry 强制 VALUE、仅可选 DIRECTION，无法覆盖仅含“向前/向后”的方向型命令。 | {"SEAT_LONGITUDINAL_SET_POSITION":{"required_slots":["AREA","ONE_OF(VALUE,DIRECTION)"],"optional_slots":["NEGATION"],"mode_values":[],"value_semantics":"mm target or relative directional step"}} |
| SEAT_TILT | ["SEAT_TILT_SET_ANGLE"] | VSS 同时提供 Tilt 与 TiltForward/TiltBackward switch；当前强制 VALUE，方向型相对调节合同不完整。 | {"SEAT_TILT_SET_ANGLE":{"required_slots":["AREA","ONE_OF(VALUE,DIRECTION)"],"optional_slots":["NEGATION"],"mode_values":[],"value_semantics":"degree target or relative directional step"}} |
| SEAT_BACKREST_RECLINE | ["SEAT_BACKREST_SET_ANGLE"] | VSS 同时提供 Recline 与 ReclineForward/ReclineBackward switch；当前强制 VALUE，方向型相对调节合同不完整。 | {"SEAT_BACKREST_SET_ANGLE":{"required_slots":["AREA","ONE_OF(VALUE,DIRECTION)"],"optional_slots":["NEGATION"],"mode_values":[],"value_semantics":"degree target or relative directional step"}} |
| SEAT_HEIGHT | ["SEAT_HEIGHT_SET_POSITION"] | VSS 同时提供 Height 与 Up/Down switch；当前强制 VALUE，方向型相对调节合同不完整。 | {"SEAT_HEIGHT_SET_POSITION":{"required_slots":["AREA","ONE_OF(VALUE,DIRECTION)"],"optional_slots":["NEGATION"],"mode_values":[],"value_semantics":"mm target or relative up/down step"}} |
| SEAT_LUMBAR_SUPPORT | ["SEAT_LUMBAR_SET_HEIGHT","SEAT_LUMBAR_SET_SUPPORT"] | VSS 同时提供腰托高度/支撑连续量与 Up/Down/More/Less switch；当前两个 Intent 均强制 VALUE，方向型相对调节合同不完整。 | {"SEAT_LUMBAR_SET_HEIGHT":{"required_slots":["AREA","ONE_OF(VALUE,DIRECTION)"],"optional_slots":["NEGATION"],"mode_values":[],"value_semantics":"mm target or relative up/down step"},"SEAT_LUMBAR_SET_SUPPORT":{"required_slots":["AREA","ONE_OF(VALUE,DIRECTION)"],"optional_slots":["MODE","NEGATION"],"mode_values":["GENERIC","TOP","MID","BOTTOM"],"value_semantics":"percent target or relative more/less step"}} |
| TRANSMISSION_GEAR_SELECTION | ["GEAR_SET"] | VSS SelectedGear 支持 0、正/负整数挡、126(P)、127(D)；当前 MODE 仅允许 P/R/N/D，不能覆盖明确的 1/2/... 前进挡或 -1/-2/... 倒挡。 | {"GEAR_SET":{"required_slots":["ONE_OF(MODE,VALUE)"],"optional_slots":["NEGATION"],"mode_values":["P","R","N","D","FORWARD_GEAR_N","REVERSE_GEAR_N"],"value_semantics":"VSS int8 gear code"}} |
| ADAS_CRUISE_CONTROL | ["CRUISE_ENABLE","CRUISE_DISABLE","CRUISE_SET_SPEED","CRUISE_SET_GAP"] | AdaptiveDistanceSet 是米制连续量，AdaptiveIntervalSet 是车辆相关等级；当前 required VALUE + optional MODE 与设计文档的 VALUE_OR_MODE 不一致，且硬编码 LEVEL_1..4 未由 VSS allowed/min/max 支持。 | {"CRUISE_ENABLE":{"required_slots":[],"optional_slots":["NEGATION"],"mode_values":[],"value_semantics":null},"CRUISE_DISABLE":{"required_slots":[],"optional_slots":["NEGATION"],"mode_values":[],"value_semantics":null},"CRUISE_SET_SPEED":{"required_slots":["VALUE"],"optional_slots":["NEGATION"],"mode_values":[],"value_semantics":"km/h"},"CRUISE_SET_GAP":{"required_slots":["ONE_OF(VALUE,MODE)"],"optional_slots":["NEGATION"],"mode_values":["VEHICLE_SPECIFIC_GAP_LEVEL"],"value_semantics":"distance in m or vehicle-specific interval level"}} |
| BODY_MAIN_LIGHT_MODE | ["HEADLIGHT_ON","HEADLIGHT_OFF","HEADLIGHT_SET_MODE"] | 当前 HEADLIGHT mode_contract 遗漏 VSS 明示的 OFF；OFF 应作为同一 MODE contract，而不是独立 HEADLIGHT_OFF。VSS 不存在通用 ON 枚举。 | {"HEADLIGHT_SET_MODE":{"required_slots":["MODE"],"optional_slots":["NEGATION"],"mode_values":["OFF","POSITION","DAYTIME_RUNNING_LIGHTS","AUTO","BEAM"],"value_semantics":null}} |

## 连续量 actuator 审计

- 已正确参数化且未按数值拆 Intent：座椅位置/高度/倾角/靠背、腰托高度与支撑、方向盘伸缩/倾斜、行李厢/前舱盖/车窗/车门位置、外后视镜 Tilt/Yaw、巡航速度/距离、扭矩分配、离合器结合度、雨刮灵敏度。
- 缺失：`DiffLockFrontEngagement` / `DiffLockRearEngagement` 的 0–100% 连续结合度没有 `DIFFERENTIAL_SET_ENGAGEMENT + VALUE`。
- Slot 合同问题：5 个座椅 capability 含方向 switch actuator，但 Registry 强制 VALUE；应接受同一 Intent 下 `ONE_OF(VALUE,DIRECTION)`。

## 枚举 actuator 审计

- 正确使用 `SET_* + MODE`：变速箱性能模式、换挡模式、挡位、雨刮模式、天窗倾斜方向。
- 主灯 `LightSwitch` 应只有 `HEADLIGHT_SET_MODE + MODE`；`OFF` 必须进入 mode contract。
- `SelectedGear` 的 VSS int8 语义包含具体正/负整数挡；现有 P/R/N/D mode contract 不完整，但不应因此拆出每个挡位 Intent。

## Boolean / IsEnabled / Switch 审计

- 直接用户可控 Boolean：ABS/TCS/EBD/EBA/ESC、镜加热/折叠/调节锁、除霜、风挡加热、灯光、锁止、驻车制动等按真实反向语义展开。
- 状态/代理，不新增 Intent：Door/Window/Trunk/Hood `IsOpen`（已有 Switch/Position 主控制）；巡航 `IsActive`/`IsAdaptive`；座椅各类 `*SwitchEngaged`；`IsHighBeamSwitchOn`。
- 喇叭 `IsActive` 是唯一主 actuator，False 明示 Inactive；因此 `HORN_DEACTIVATE` 不是机械凑对称，而是缺失的直接用户操作。

## 重复与来源追踪

- `POSSIBLE_DUPLICATE_INTENTS = []`：未发现相同 action + target + parameter contract + VSS source 的重复 Intent。
- `UNSUPPORTED_VSS_DERIVED_INTENTS = []`：87 个当前 VSS-derived Intent 均可追溯到 44 项 HUMAN_APPROVED capability；没有 HUMAN_REJECTED 来源。
- `DEFROST_*` 与 `WINDSHIELD_HEATING_*` 来源分别是 HVAC defroster 与 windshield heater，不能仅因中文效果相近而合并。

## Project-native 8（不参与 VSS 计数）

`ACCELERATE`, `DECELERATE`, `BRAKE`, `EMERGENCY_BRAKE`, `LANE_CHANGE`, `LANE_KEEP`, `EVASIVE_STEER`, `AUTO_PARK_ENABLE`。

## 87 数量的人工复核差异式

```text
当前 87
+ 应增加 2：DIFFERENTIAL_SET_ENGAGEMENT, HORN_DEACTIVATE
- 应删除 0
- 应合并 2：HEADLIGHT_ON → HEADLIGHT_SET_MODE；HEADLIGHT_OFF → HEADLIGHT_SET_MODE
= 审计后 87
```

数量相等不代表正确：两个缺失与两个过度展开恰好抵消；另有 8 个不改变 Intent 数量的 Slot/参数合同错误。

## 逐 capability actuator 证据

### 1. `BODY_MIRROR_HEATING` — 外后视镜加热

- 对象：外后视镜；期望操作：ON, OFF；状态：`COMPLETE`。
- 当前 Intent：MIRROR_HEATING_ON, MIRROR_HEATING_OFF。
- 期望 Intent：MIRROR_HEATING_ON, MIRROR_HEATING_OFF。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Mirrors.DriverSide.IsHeatingOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Mirror Heater on or off. True = Heater On. False = Heater Off. |
| Vehicle.Body.Mirrors.PassengerSide.IsHeatingOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Mirror Heater on or off. True = Heater On. False = Heater Off. |

### 2. `BODY_MIRROR_ADJUSTMENT_LOCK` — 外后视镜调节锁定

- 对象：外后视镜；期望操作：LOCK, UNLOCK；状态：`COMPLETE`。
- 当前 Intent：MIRROR_ADJUSTMENT_LOCK, MIRROR_ADJUSTMENT_UNLOCK。
- 期望 Intent：MIRROR_ADJUSTMENT_LOCK, MIRROR_ADJUSTMENT_UNLOCK。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Mirrors.DriverSide.IsLocked | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is mirror movement locked? True = Locked, mirror will not react to Tilt/Pan change. False = Unlocked. |
| Vehicle.Body.Mirrors.PassengerSide.IsLocked | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is mirror movement locked? True = Locked, mirror will not react to Tilt/Pan change. False = Unlocked. |

### 3. `SEAT_LONGITUDINAL_POSITION` — 座椅前后位置调节

- 对象：座椅；期望操作：SET_POSITION；状态：`SEMANTIC_MISMATCH`。
- 当前 Intent：SEAT_LONGITUDINAL_SET_POSITION。
- 期望 Intent：SEAT_LONGITUDINAL_SET_POSITION。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.Seat.Row1.DriverSide.IsBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat backward switch engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.IsForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat forward switch engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Position | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle x-axis. Position is relative to the frontmost position supported by the seat. 0 = Frontmost position supported. |
| Vehicle.Cabin.Seat.Row1.Middle.IsBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat backward switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.IsForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat forward switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.Position | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle x-axis. Position is relative to the frontmost position supported by the seat. 0 = Frontmost position supported. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.IsBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat backward switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.IsForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat forward switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Position | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle x-axis. Position is relative to the frontmost position supported by the seat. 0 = Frontmost position supported. |
| Vehicle.Cabin.Seat.Row2.DriverSide.IsBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat backward switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.IsForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat forward switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Position | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle x-axis. Position is relative to the frontmost position supported by the seat. 0 = Frontmost position supported. |
| Vehicle.Cabin.Seat.Row2.Middle.IsBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat backward switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.IsForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat forward switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.Position | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle x-axis. Position is relative to the frontmost position supported by the seat. 0 = Frontmost position supported. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.IsBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat backward switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.IsForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat forward switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Position | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle x-axis. Position is relative to the frontmost position supported by the seat. 0 = Frontmost position supported. |

### 4. `SEAT_TILT` — 座椅整体倾角调节

- 对象：座椅；期望操作：SET_ANGLE；状态：`SEMANTIC_MISMATCH`。
- 当前 Intent：SEAT_TILT_SET_ANGLE。
- 期望 Intent：SEAT_TILT_SET_ANGLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt backward switch engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt forward switch engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Tilt | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Tilting of seat (seating and backrest) relative to vehicle x-axis. 0 = seat bottom is flat, seat bottom and vehicle x-axis are parallel. Positive degrees = seat tilted backwards, seat x-axis tilted upward, seat z-axis is tilted backward. |
| Vehicle.Cabin.Seat.Row1.Middle.IsTiltBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt backward switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.IsTiltForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt forward switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.Tilt | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Tilting of seat (seating and backrest) relative to vehicle x-axis. 0 = seat bottom is flat, seat bottom and vehicle x-axis are parallel. Positive degrees = seat tilted backwards, seat x-axis tilted upward, seat z-axis is tilted backward. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt backward switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt forward switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Tilt | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Tilting of seat (seating and backrest) relative to vehicle x-axis. 0 = seat bottom is flat, seat bottom and vehicle x-axis are parallel. Positive degrees = seat tilted backwards, seat x-axis tilted upward, seat z-axis is tilted backward. |
| Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt backward switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt forward switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Tilt | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Tilting of seat (seating and backrest) relative to vehicle x-axis. 0 = seat bottom is flat, seat bottom and vehicle x-axis are parallel. Positive degrees = seat tilted backwards, seat x-axis tilted upward, seat z-axis is tilted backward. |
| Vehicle.Cabin.Seat.Row2.Middle.IsTiltBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt backward switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.IsTiltForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt forward switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.Tilt | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Tilting of seat (seating and backrest) relative to vehicle x-axis. 0 = seat bottom is flat, seat bottom and vehicle x-axis are parallel. Positive degrees = seat tilted backwards, seat x-axis tilted upward, seat z-axis is tilted backward. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt backward switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Tilt forward switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Tilt | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Tilting of seat (seating and backrest) relative to vehicle x-axis. 0 = seat bottom is flat, seat bottom and vehicle x-axis are parallel. Positive degrees = seat tilted backwards, seat x-axis tilted upward, seat z-axis is tilted backward. |

### 5. `SEAT_BACKREST_RECLINE` — 座椅靠背角度调节

- 对象：座椅；期望操作：SET_ANGLE；状态：`SEMANTIC_MISMATCH`。
- 当前 Intent：SEAT_BACKREST_SET_ANGLE。
- 期望 Intent：SEAT_BACKREST_SET_ANGLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline backward switch engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline forward switch engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.Recline | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Backrest recline compared to seat z-axis (seat vertical axis). 0 degrees = Upright/Vertical backrest. Negative degrees for forward recline. Positive degrees for backward recline. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline backward switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline forward switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.Recline | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Backrest recline compared to seat z-axis (seat vertical axis). 0 degrees = Upright/Vertical backrest. Negative degrees for forward recline. Positive degrees for backward recline. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline backward switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline forward switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.Recline | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Backrest recline compared to seat z-axis (seat vertical axis). 0 degrees = Upright/Vertical backrest. Negative degrees for forward recline. Positive degrees for backward recline. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline backward switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline forward switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.Recline | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Backrest recline compared to seat z-axis (seat vertical axis). 0 degrees = Upright/Vertical backrest. Negative degrees for forward recline. Positive degrees for backward recline. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline backward switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline forward switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.Recline | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Backrest recline compared to seat z-axis (seat vertical axis). 0 degrees = Upright/Vertical backrest. Negative degrees for forward recline. Positive degrees for backward recline. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline backward switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineForwardSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Backrest recline forward switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.Recline | float | {"unit":"degrees","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Backrest recline compared to seat z-axis (seat vertical axis). 0 degrees = Upright/Vertical backrest. Negative degrees for forward recline. Positive degrees for backward recline. |

### 6. `SEAT_HEIGHT` — 座椅高度调节

- 对象：座椅；期望操作：SET_POSITION；状态：`SEMANTIC_MISMATCH`。
- 当前 Intent：SEAT_HEIGHT_SET_POSITION。
- 期望 Intent：SEAT_HEIGHT_SET_POSITION。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.Seat.Row1.DriverSide.Height | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle z-axis. Position is relative within available movable range of the seating. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row1.DriverSide.IsDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat down switch engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.IsUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat up switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.Height | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle z-axis. Position is relative within available movable range of the seating. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row1.Middle.IsDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat down switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.IsUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat up switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Height | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle z-axis. Position is relative within available movable range of the seating. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.IsDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat down switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.IsUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat up switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Height | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle z-axis. Position is relative within available movable range of the seating. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row2.DriverSide.IsDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat down switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.IsUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat up switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.Height | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle z-axis. Position is relative within available movable range of the seating. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row2.Middle.IsDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat down switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.IsUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat up switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Height | uint16 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Seat position on vehicle z-axis. Position is relative within available movable range of the seating. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.IsDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat down switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.IsUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Seat up switch engaged. |

### 7. `SEAT_LUMBAR_SUPPORT` — 腰托调节

- 对象：座椅；期望操作：SET_HEIGHT, SET_SUPPORT；状态：`SEMANTIC_MISMATCH`。
- 当前 Intent：SEAT_LUMBAR_SET_HEIGHT, SEAT_LUMBAR_SET_SUPPORT。
- 期望 Intent：SEAT_LUMBAR_SET_HEIGHT, SEAT_LUMBAR_SET_SUPPORT。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.BottomLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Bottom lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for less lumbar support engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar down switch engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar up switch engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for more lumbar support engaged. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarHeight | uint8 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Height of lumbar support. Position is relative within available movable range of the lumbar support. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.MidLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Mid lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.TopLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Top lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.BottomLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Bottom lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLessLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for less lumbar support engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar down switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar up switch engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for more lumbar support engaged. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarHeight | uint8 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Height of lumbar support. Position is relative within available movable range of the lumbar support. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.MidLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Mid lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.Middle.Backrest.TopLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Top lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.BottomLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Bottom lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for less lumbar support engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar down switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar up switch engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for more lumbar support engaged. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarHeight | uint8 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Height of lumbar support. Position is relative within available movable range of the lumbar support. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.MidLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Mid lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.TopLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Top lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.BottomLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Bottom lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for less lumbar support engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar down switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar up switch engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for more lumbar support engaged. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarHeight | uint8 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Height of lumbar support. Position is relative within available movable range of the lumbar support. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.MidLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Mid lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.TopLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Top lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.BottomLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Bottom lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLessLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for less lumbar support engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar down switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar up switch engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for more lumbar support engaged. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarHeight | uint8 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Height of lumbar support. Position is relative within available movable range of the lumbar support. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.MidLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Mid lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.Middle.Backrest.TopLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Top lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.BottomLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Bottom lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for less lumbar support engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarDownSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar down switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarUpSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Lumbar up switch engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Is switch for more lumbar support engaged. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarHeight | uint8 | {"unit":"mm","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Height of lumbar support. Position is relative within available movable range of the lumbar support. 0 = Lowermost position supported. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.MidLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Mid lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |
| Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.TopLumbarSupport | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Top lumbar support (in/out position). 0 = Innermost position. 100 = Outermost position. |

### 8. `CHASSIS_STEERING_WHEEL_POSITION` — 方向盘位置调节

- 对象：方向盘；期望操作：SET_EXTENSION, SET_TILT；状态：`COMPLETE`。
- 当前 Intent：STEERING_WHEEL_SET_EXTENSION, STEERING_WHEEL_SET_TILT。
- 期望 Intent：STEERING_WHEEL_SET_EXTENSION, STEERING_WHEEL_SET_TILT。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Chassis.SteeringWheel.Extension | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Steering wheel column extension from dashboard. 0 = Closest to dashboard. 100 = Furthest from dashboard. |
| Vehicle.Chassis.SteeringWheel.Tilt | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Steering wheel column tilt. 0 = Lowest position. 100 = Highest position. |

### 9. `CABIN_HVAC_DEFROST` — 前/后除霜除雾控制

- 对象：除霜除雾系统；期望操作：ON, OFF；状态：`COMPLETE`。
- 当前 Intent：DEFROST_ON, DEFROST_OFF。
- 期望 Intent：DEFROST_ON, DEFROST_OFF。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.HVAC.IsFrontDefrosterActive | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is front defroster active. |
| Vehicle.Cabin.HVAC.IsRearDefrosterActive | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is rear defroster active. |

### 10. `BODY_WINDSHIELD_HEATING` — 前/后风挡加热

- 对象：风挡玻璃；期望操作：ON, OFF；状态：`COMPLETE`。
- 当前 Intent：WINDSHIELD_HEATING_ON, WINDSHIELD_HEATING_OFF。
- 期望 Intent：WINDSHIELD_HEATING_ON, WINDSHIELD_HEATING_OFF。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Windshield.Front.IsHeatingOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Windshield heater status. False - off, True - on. |
| Vehicle.Body.Windshield.Rear.IsHeatingOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Windshield heater status. False - off, True - on. |

### 11. `ADAS_ABS_ENABLE` — ABS启用状态控制

- 对象：ABS；期望操作：ENABLE, DISABLE；状态：`COMPLETE`。
- 当前 Intent：ABS_ENABLE, ABS_DISABLE。
- 期望 Intent：ABS_ENABLE, ABS_DISABLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.ADAS.ABS.IsEnabled | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if ABS is enabled. True = Enabled. False = Disabled. |

### 12. `ADAS_TCS_ENABLE` — 牵引力控制系统启用控制

- 对象：TCS；期望操作：ENABLE, DISABLE；状态：`COMPLETE`。
- 当前 Intent：TCS_ENABLE, TCS_DISABLE。
- 期望 Intent：TCS_ENABLE, TCS_DISABLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.ADAS.TCS.IsEnabled | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if TCS is enabled. True = Enabled. False = Disabled. |

### 13. `ADAS_EBD_ENABLE` — 电子制动力分配系统启用控制

- 对象：EBD；期望操作：ENABLE, DISABLE；状态：`COMPLETE`。
- 当前 Intent：EBD_ENABLE, EBD_DISABLE。
- 期望 Intent：EBD_ENABLE, EBD_DISABLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.ADAS.EBD.IsEnabled | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if EBD is enabled. True = Enabled. False = Disabled. |

### 14. `ADAS_EBA_ENABLE` — 紧急制动辅助系统启用控制

- 对象：EBA；期望操作：ENABLE, DISABLE；状态：`COMPLETE`。
- 当前 Intent：EBA_ENABLE, EBA_DISABLE。
- 期望 Intent：EBA_ENABLE, EBA_DISABLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.ADAS.EBA.IsEnabled | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if EBA is enabled. True = Enabled. False = Disabled. |

### 15. `ADAS_ESC_ENABLE` — 车身电子稳定系统启用控制

- 对象：ESC；期望操作：ENABLE, DISABLE；状态：`COMPLETE`。
- 当前 Intent：ESC_ENABLE, ESC_DISABLE。
- 期望 Intent：ESC_ENABLE, ESC_DISABLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.ADAS.ESC.IsEnabled | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if ESC is enabled. True = Enabled. False = Disabled. |

### 16. `BODY_TRUNK_OPENING` — 行李厢开合控制

- 对象：行李厢；期望操作：OPEN, CLOSE, SET_POSITION；状态：`COMPLETE`。
- 当前 Intent：TRUNK_OPEN, TRUNK_CLOSE, TRUNK_SET_POSITION。
- 期望 Intent：TRUNK_OPEN, TRUNK_CLOSE, TRUNK_SET_POSITION。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Trunk.Front.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Body.Trunk.Front.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Body.Trunk.Front.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |
| Vehicle.Body.Trunk.Rear.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Body.Trunk.Rear.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Body.Trunk.Rear.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |

### 17. `BODY_TRUNK_LOCK` — 行李厢锁控制

- 对象：行李厢；期望操作：LOCK, UNLOCK；状态：`COMPLETE`。
- 当前 Intent：TRUNK_LOCK, TRUNK_UNLOCK。
- 期望 Intent：TRUNK_LOCK, TRUNK_UNLOCK。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Trunk.Front.IsLocked | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is item locked or unlocked. True = Locked. False = Unlocked. |
| Vehicle.Body.Trunk.Rear.IsLocked | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is item locked or unlocked. True = Locked. False = Unlocked. |

### 18. `BODY_HOOD` — 前舱盖开合控制

- 对象：前舱盖；期望操作：OPEN, CLOSE, SET_POSITION；状态：`COMPLETE`。
- 当前 Intent：HOOD_OPEN, HOOD_CLOSE, HOOD_SET_POSITION。
- 期望 Intent：HOOD_OPEN, HOOD_CLOSE, HOOD_SET_POSITION。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Hood.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Body.Hood.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Body.Hood.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |

### 19. `TRANSMISSION_LOW_RANGE` — 低速四驱/低速挡控制

- 对象：低速挡；期望操作：ENABLE, DISABLE；状态：`COMPLETE`。
- 当前 Intent：LOW_RANGE_ENABLE, LOW_RANGE_DISABLE。
- 期望 Intent：LOW_RANGE_ENABLE, LOW_RANGE_DISABLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Powertrain.Transmission.IsLowRangeEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is gearbox in low range mode or not. False = Normal/High range engaged. True = Low range engaged. |

### 20. `TRANSMISSION_TORQUE_DISTRIBUTION` — 前后轴扭矩分配控制

- 对象：前后轴扭矩分配；期望操作：SET_DISTRIBUTION；状态：`COMPLETE`。
- 当前 Intent：TORQUE_DISTRIBUTION_SET。
- 期望 Intent：TORQUE_DISTRIBUTION_SET。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Powertrain.Transmission.TorqueDistribution | float | {"unit":"percent","min":-100,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Torque distribution between front and rear axle in percent. -100% = Full torque to front axle, 0% = 50:50 Front/Rear, 100% = Full torque to rear axle. |

### 21. `TRANSMISSION_PERFORMANCE_MODE` — 变速箱性能模式选择

- 对象：变速箱性能模式；期望操作：SET_MODE；状态：`COMPLETE`。
- 当前 Intent：TRANSMISSION_PERFORMANCE_MODE_SET。
- 期望 Intent：TRANSMISSION_PERFORMANCE_MODE_SET。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Powertrain.Transmission.PerformanceMode | string | {"unit":null,"min":null,"max":null,"allowed":["NORMAL","SPORT","ECONOMY","SNOW","RAIN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Current gearbox performance mode. |

### 22. `TRANSMISSION_DIFF_LOCK` — 差速锁控制

- 对象：差速锁；期望操作：LOCK, UNLOCK, SET_ENGAGEMENT；状态：`MISSING`。
- 当前 Intent：DIFFERENTIAL_LOCK, DIFFERENTIAL_UNLOCK。
- 期望 Intent：DIFFERENTIAL_LOCK, DIFFERENTIAL_UNLOCK, DIFFERENTIAL_SET_ENGAGEMENT。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Powertrain.Transmission.DiffLockFrontEngagement | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Front Diff Lock engagement. 0% = Diff lock fully disengaged. 100% = Diff lock fully engaged. |
| Vehicle.Powertrain.Transmission.DiffLockRearEngagement | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Rear Diff Lock engagement. 0% = Diff lock fully disengaged. 100% = Diff lock fully engaged. |

### 23. `TRANSMISSION_GEAR_SELECTION` — 挡位选择

- 对象：挡位；期望操作：SET_GEAR；状态：`SEMANTIC_MISMATCH`。
- 当前 Intent：GEAR_SET。
- 期望 Intent：GEAR_SET。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Powertrain.Transmission.SelectedGear | int8 | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | The selected gear. 0=Neutral, 1/2/..=Forward, -1/-2/..=Reverse, 126=Park, 127=Drive. |

### 24. `TRANSMISSION_ELECTRICAL_POWERTRAIN_ENGAGEMENT` — 电驱动力结合控制

- 对象：电驱动力结合机构；期望操作：ENGAGE, DISENGAGE；状态：`COMPLETE`。
- 当前 Intent：ELECTRIC_POWERTRAIN_ENGAGE, ELECTRIC_POWERTRAIN_DISENGAGE。
- 期望 Intent：ELECTRIC_POWERTRAIN_ENGAGE, ELECTRIC_POWERTRAIN_DISENGAGE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Powertrain.Transmission.IsElectricalPowertrainEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is electrical powertrain mechanically connected/engaged to the drivetrain or not. False = Disconnected/Disengaged. True = Connected/Engaged. |

### 25. `TRANSMISSION_CLUTCH` — 离合器结合度控制

- 对象：离合器；期望操作：SET_ENGAGEMENT；状态：`COMPLETE`。
- 当前 Intent：CLUTCH_SET_ENGAGEMENT。
- 期望 Intent：CLUTCH_SET_ENGAGEMENT。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Powertrain.Transmission.ClutchEngagement | float | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Clutch engagement. 0% = Clutch fully disengaged. 100% = Clutch fully engaged. |

### 26. `TRANSMISSION_GEAR_CHANGE_MODE` — 自动/手动换挡模式

- 对象：换挡模式；期望操作：SET_MODE；状态：`COMPLETE`。
- 当前 Intent：GEAR_CHANGE_MODE_SET。
- 期望 Intent：GEAR_CHANGE_MODE_SET。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Powertrain.Transmission.GearChangeMode | string | {"unit":null,"min":null,"max":null,"allowed":["MANUAL","AUTOMATIC"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Is the gearbox in automatic or manual (paddle) mode. |

### 27. `TRANSMISSION_PARK_LOCK` — 驻车锁控制

- 对象：驻车锁；期望操作：LOCK, UNLOCK；状态：`COMPLETE`。
- 当前 Intent：PARK_LOCK, PARK_UNLOCK。
- 期望 Intent：PARK_LOCK, PARK_UNLOCK。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Powertrain.Transmission.IsParkLockEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is the transmission park lock engaged or not. False = Disengaged. True = Engaged. |

### 28. `BODY_HORN` — 喇叭控制

- 对象：喇叭；期望操作：ACTIVATE, DEACTIVATE；状态：`MISSING`。
- 当前 Intent：HORN_ACTIVATE。
- 期望 Intent：HORN_ACTIVATE, HORN_DEACTIVATE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Horn.IsActive | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Horn active or inactive. True = Active. False = Inactive. |

### 29. `BODY_MIRROR_FOLD` — 外后视镜折叠

- 对象：外后视镜；期望操作：FOLD, UNFOLD；状态：`COMPLETE`。
- 当前 Intent：MIRROR_FOLD, MIRROR_UNFOLD。
- 期望 Intent：MIRROR_FOLD, MIRROR_UNFOLD。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Mirrors.DriverSide.IsFolded | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is mirror folded? True = Fully or partially folded. False = Fully unfolded. |
| Vehicle.Body.Mirrors.PassengerSide.IsFolded | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is mirror folded? True = Fully or partially folded. False = Fully unfolded. |

### 30. `BODY_MIRROR_ADJUSTMENT` — 外后视镜角度调节

- 对象：外后视镜；期望操作：SET_ANGLE；状态：`COMPLETE`。
- 当前 Intent：MIRROR_SET_ANGLE。
- 期望 Intent：MIRROR_SET_ANGLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Mirrors.DriverSide.Tilt | int8 | {"unit":"percent","min":-100,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Mirror tilt as a percent. 0 = Center Position. 100 = Fully Upward Position. -100 = Fully Downward Position. |
| Vehicle.Body.Mirrors.DriverSide.Yaw | int8 | {"unit":"percent","min":-100,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Relative mirror yaw angle, measured from the vehicle sprung mass X-axis as defined by ISO 23150:2023 to the mirror X-axis, around the vehicle Z-axis (right-hand rule). 0 = Mirror in default position. Exact position (yaw relative to vehicle X-axis) is vehicle dependent. 100 = Maximum yaw. Mirror rotated clockwise as much as possible around Z-axis. -100 = Minimum yaw. Mirror rotated counter-clockwise as much as possible around Z-axis. |
| Vehicle.Body.Mirrors.PassengerSide.Tilt | int8 | {"unit":"percent","min":-100,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Mirror tilt as a percent. 0 = Center Position. 100 = Fully Upward Position. -100 = Fully Downward Position. |
| Vehicle.Body.Mirrors.PassengerSide.Yaw | int8 | {"unit":"percent","min":-100,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Relative mirror yaw angle, measured from the vehicle sprung mass X-axis as defined by ISO 23150:2023 to the mirror X-axis, around the vehicle Z-axis (right-hand rule). 0 = Mirror in default position. Exact position (yaw relative to vehicle X-axis) is vehicle dependent. 100 = Maximum yaw. Mirror rotated clockwise as much as possible around Z-axis. -100 = Minimum yaw. Mirror rotated counter-clockwise as much as possible around Z-axis. |

### 31. `CABIN_SUNROOF` — 天窗开合控制

- 对象：天窗；期望操作：OPEN, CLOSE, SET_TILT；状态：`COMPLETE`。
- 当前 Intent：SUNROOF_OPEN, SUNROOF_CLOSE, SUNROOF_SET_TILT。
- 期望 Intent：SUNROOF_OPEN, SUNROOF_CLOSE, SUNROOF_SET_TILT。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.Sunroof.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN","TILT_UP","TILT_DOWN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or shade. |

### 32. `ADAS_CRUISE_CONTROL` — 巡航控制

- 对象：巡航系统；期望操作：ENABLE, DISABLE, SET_SPEED, SET_GAP；状态：`SEMANTIC_MISMATCH`。
- 当前 Intent：CRUISE_ENABLE, CRUISE_DISABLE, CRUISE_SET_SPEED, CRUISE_SET_GAP。
- 期望 Intent：CRUISE_ENABLE, CRUISE_DISABLE, CRUISE_SET_SPEED, CRUISE_SET_GAP。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.ADAS.CruiseControl.AdaptiveDistanceSet | float | {"unit":"m","min":0,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Distance in meters to keep from lead vehicle |
| Vehicle.ADAS.CruiseControl.AdaptiveIntervalSet | uint8 | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Follow distance setting, commonly 1-5 with 1 being closest. |
| Vehicle.ADAS.CruiseControl.IsActive | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Indicates if cruise control system is active (i.e. actively controls speed). True = Active. False = Inactive. |
| Vehicle.ADAS.CruiseControl.IsAdaptive | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Indicates if cruise control system is adaptive (i.e. actively controls speed). |
| Vehicle.ADAS.CruiseControl.IsEnabled | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if cruise control system is enabled (e.g. ready to receive configurations and settings) True = Enabled. False = Disabled. |
| Vehicle.ADAS.CruiseControl.SpeedSet | float | {"unit":"km/h","min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Set cruise control speed in kilometers per hour. |

### 33. `BODY_MAIN_LIGHT_MODE` — 主灯光模式控制

- 对象：主灯开关；期望操作：SET_MODE；状态：`OVER_EXPANDED`。
- 当前 Intent：HEADLIGHT_ON, HEADLIGHT_OFF, HEADLIGHT_SET_MODE。
- 期望 Intent：HEADLIGHT_SET_MODE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Lights.LightSwitch | string | {"unit":null,"min":null,"max":null,"allowed":["OFF","POSITION","DAYTIME_RUNNING_LIGHTS","AUTO","BEAM"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Status of the vehicle main light switch. |

### 34. `BODY_HAZARD_LIGHT` — 危险警示灯控制

- 对象：危险警示灯；期望操作：ON, OFF；状态：`COMPLETE`。
- 当前 Intent：HAZARD_LIGHT_ON, HAZARD_LIGHT_OFF。
- 期望 Intent：HAZARD_LIGHT_ON, HAZARD_LIGHT_OFF。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Lights.Hazard.IsSignaling | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if light is signaling or off. True = signaling. False = Off. |

### 35. `BODY_TURN_INDICATOR` — 转向灯控制

- 对象：转向灯；期望操作：ON, OFF；状态：`COMPLETE`。
- 当前 Intent：TURN_INDICATOR_ON, TURN_INDICATOR_OFF。
- 期望 Intent：TURN_INDICATOR_ON, TURN_INDICATOR_OFF。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if light is signaling or off. True = signaling. False = Off. |
| Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if light is signaling or off. True = signaling. False = Off. |

### 36. `BODY_LOW_BEAM` — 近光灯控制

- 对象：近光灯；期望操作：ON, OFF；状态：`COMPLETE`。
- 当前 Intent：LOW_BEAM_ON, LOW_BEAM_OFF。
- 期望 Intent：LOW_BEAM_ON, LOW_BEAM_OFF。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Lights.Beam.Low.IsOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if light is on or off. True = On. False = Off. |

### 37. `BODY_HIGH_BEAM` — 远光灯控制

- 对象：远光灯；期望操作：ON, OFF；状态：`COMPLETE`。
- 当前 Intent：HIGH_BEAM_ON, HIGH_BEAM_OFF。
- 期望 Intent：HIGH_BEAM_ON, HIGH_BEAM_OFF。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Lights.Beam.High.IsOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if light is on or off. True = On. False = Off. |
| Vehicle.Body.Lights.IsHighBeamSwitchOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["LOW_LEVEL_INTERNAL","STATUS_LIKE"] | Status of the high beam switch. True = high beam enabled. False = high beam not enabled. |

### 38. `BODY_FOG_LIGHT` — 雾灯控制

- 对象：雾灯；期望操作：ON, OFF；状态：`COMPLETE`。
- 当前 Intent：FOG_LIGHT_ON, FOG_LIGHT_OFF。
- 期望 Intent：FOG_LIGHT_ON, FOG_LIGHT_OFF。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Lights.Fog.Front.IsOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if light is on or off. True = On. False = Off. |
| Vehicle.Body.Lights.Fog.Rear.IsOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if light is on or off. True = On. False = Off. |

### 39. `BODY_PARKING_LIGHT` — 驻车灯控制

- 对象：驻车灯；期望操作：ON, OFF；状态：`COMPLETE`。
- 当前 Intent：PARKING_LIGHT_ON, PARKING_LIGHT_OFF。
- 期望 Intent：PARKING_LIGHT_ON, PARKING_LIGHT_OFF。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Lights.Parking.IsOn | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if light is on or off. True = On. False = Off. |

### 40. `CABIN_WINDOW` — 车窗开合与开度控制

- 对象：车窗；期望操作：OPEN, CLOSE, SET_POSITION；状态：`COMPLETE`。
- 当前 Intent：WINDOW_OPEN, WINDOW_CLOSE, WINDOW_SET_POSITION。
- 期望 Intent：WINDOW_OPEN, WINDOW_CLOSE, WINDOW_SET_POSITION。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.Door.Row1.DriverSide.Window.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Cabin.Door.Row1.DriverSide.Window.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Cabin.Door.Row1.DriverSide.Window.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |
| Vehicle.Cabin.Door.Row1.PassengerSide.Window.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Cabin.Door.Row1.PassengerSide.Window.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Cabin.Door.Row1.PassengerSide.Window.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |
| Vehicle.Cabin.Door.Row2.DriverSide.Window.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Cabin.Door.Row2.DriverSide.Window.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Cabin.Door.Row2.DriverSide.Window.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |
| Vehicle.Cabin.Door.Row2.PassengerSide.Window.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Cabin.Door.Row2.PassengerSide.Window.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Cabin.Door.Row2.PassengerSide.Window.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |

### 41. `CABIN_DOOR_OPENING` — 车门开合控制

- 对象：车门；期望操作：OPEN, CLOSE, SET_POSITION；状态：`COMPLETE`。
- 当前 Intent：DOOR_OPEN, DOOR_CLOSE, DOOR_SET_POSITION。
- 期望 Intent：DOOR_OPEN, DOOR_CLOSE, DOOR_SET_POSITION。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.Door.Row1.DriverSide.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Cabin.Door.Row1.DriverSide.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Cabin.Door.Row1.DriverSide.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |
| Vehicle.Cabin.Door.Row1.PassengerSide.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Cabin.Door.Row1.PassengerSide.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Cabin.Door.Row1.PassengerSide.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |
| Vehicle.Cabin.Door.Row2.DriverSide.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Cabin.Door.Row2.DriverSide.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Cabin.Door.Row2.DriverSide.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |
| Vehicle.Cabin.Door.Row2.PassengerSide.IsOpen | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["STATUS_LIKE"] | Is item open or closed? True = Fully or partially open. False = Fully closed. |
| Vehicle.Cabin.Door.Row2.PassengerSide.Position | uint8 | {"unit":"percent","min":0,"max":100,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Item position. 0 = Start position 100 = End position. |
| Vehicle.Cabin.Door.Row2.PassengerSide.Switch | string | {"unit":null,"min":null,"max":null,"allowed":["INACTIVE","CLOSE","OPEN","ONE_SHOT_CLOSE","ONE_SHOT_OPEN"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Switch controlling sliding action such as window, sunroof, or blind. |

### 42. `CABIN_DOOR_LOCK` — 车门锁控制

- 对象：车门；期望操作：LOCK, UNLOCK；状态：`COMPLETE`。
- 当前 Intent：DOOR_LOCK, DOOR_UNLOCK。
- 期望 Intent：DOOR_LOCK, DOOR_UNLOCK。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Cabin.Door.Row1.DriverSide.IsLocked | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is item locked or unlocked. True = Locked. False = Unlocked. |
| Vehicle.Cabin.Door.Row1.PassengerSide.IsLocked | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is item locked or unlocked. True = Locked. False = Unlocked. |
| Vehicle.Cabin.Door.Row2.DriverSide.IsLocked | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is item locked or unlocked. True = Locked. False = Unlocked. |
| Vehicle.Cabin.Door.Row2.PassengerSide.IsLocked | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Is item locked or unlocked. True = Locked. False = Unlocked. |

### 43. `BODY_WIPER_USER_CONTROL` — 雨刮模式与灵敏度控制

- 对象：雨刮；期望操作：SET_MODE, SET_SENSITIVITY；状态：`COMPLETE`。
- 当前 Intent：WIPER_SET_MODE, WIPER_SET_SENSITIVITY。
- 期望 Intent：WIPER_SET_MODE, WIPER_SET_SENSITIVITY。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Body.Windshield.Front.Wiping.Intensity | uint8 | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Relative intensity/sensitivity for interval and rain sensor mode as requested by user/driver. Has no significance if Windshield.Wiping.Mode is OFF/SLOW/MEDIUM/FAST 0 - wipers inactive. 1 - minimum intensity (lowest frequency/sensitivity, longest interval). 2/3/4/... - higher intensity (higher frequency/sensitivity, shorter interval). Maximum value supported is vehicle specific. |
| Vehicle.Body.Windshield.Front.Wiping.Mode | string | {"unit":null,"min":null,"max":null,"allowed":["OFF","SLOW","MEDIUM","FAST","INTERVAL","RAIN_SENSOR"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Wiper mode requested by user/driver. INTERVAL indicates intermittent wiping, with fixed time interval between each wipe. RAIN_SENSOR indicates intermittent wiping based on rain intensity. |
| Vehicle.Body.Windshield.Rear.Wiping.Intensity | uint8 | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL","PARAMETER_CONTROL"] | Relative intensity/sensitivity for interval and rain sensor mode as requested by user/driver. Has no significance if Windshield.Wiping.Mode is OFF/SLOW/MEDIUM/FAST 0 - wipers inactive. 1 - minimum intensity (lowest frequency/sensitivity, longest interval). 2/3/4/... - higher intensity (higher frequency/sensitivity, shorter interval). Maximum value supported is vehicle specific. |
| Vehicle.Body.Windshield.Rear.Wiping.Mode | string | {"unit":null,"min":null,"max":null,"allowed":["OFF","SLOW","MEDIUM","FAST","INTERVAL","RAIN_SENSOR"],"default":null} | ["USER_LEVEL_CONTROL","MODE_CONTROL"] | Wiper mode requested by user/driver. INTERVAL indicates intermittent wiping, with fixed time interval between each wipe. RAIN_SENSOR indicates intermittent wiping based on rain intensity. |

### 44. `CHASSIS_PARKING_BRAKE` — 驻车制动控制

- 对象：驻车制动；期望操作：APPLY, RELEASE, AUTO_APPLY_ENABLE, AUTO_APPLY_DISABLE；状态：`COMPLETE`。
- 当前 Intent：PARKING_BRAKE_APPLY, PARKING_BRAKE_RELEASE, PARKING_BRAKE_AUTO_APPLY_ENABLE, PARKING_BRAKE_AUTO_APPLY_DISABLE。
- 期望 Intent：PARKING_BRAKE_APPLY, PARKING_BRAKE_RELEASE, PARKING_BRAKE_AUTO_APPLY_ENABLE, PARKING_BRAKE_AUTO_APPLY_DISABLE。

| VSS path | datatype | constraints | classification | semantics |
|---|---|---|---|---|
| Vehicle.Chassis.ParkingBrake.IsAutoApplyEnabled | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Indicates if parking brake will be automatically engaged when the vehicle engine is turned off. |
| Vehicle.Chassis.ParkingBrake.IsEngaged | boolean | {"unit":null,"min":null,"max":null,"allowed":[],"default":null} | ["USER_LEVEL_CONTROL"] | Parking brake status. True = Parking Brake is Engaged. False = Parking Brake is not Engaged. |

## 停止条件

- `MODEL_TRAINING_EXECUTED = NO`
- `DATASET_GENERATION_EXECUTED = NO`
- `REGISTRY_MODIFIED = NO`
- `RUNTIME_MODIFIED = NO`
- `SAFETY_GOLD_OPENED = NO`
- `READY_FOR_HUMAN_REVIEW_OF_FULL_INTENT_REGISTRY = YES`
