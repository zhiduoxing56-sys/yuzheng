# SYS-014 R2 → R3 用户语音正式注册表审计

- status: **PASS**
- R2 SHA256: `18c4e02edec1630946be6aa8613345a6e16dc246c883068c6f017f5e28e9f251`
- R3 SHA256: `c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06`
- 正式用户语音意图: **71**
- 已知但不开放: **22**
- 保留语义目录: **93**

## R2 → R3 变更

- R2 全部93条语义定义、合同、capability family 和 VSS provenance 逐项保留。
- 22条从用户语音正式范围移至 `KNOWN_UNSUPPORTED_CONTROL`。
- 其余71条标记为 `FORMAL_EXECUTABLE`。
- `intent_runtime_support.yaml` 未修改，也不定义 Full NLU 标签空间。
- 旧 annotation schema 冲突只记录，留待下一阶段处理。

## 移出的22项

| # | canonical_intent_id | 中文语义 | action | target | attribute | VSS source |
|---:|---|---|---|---|---|---|
| 1 | `MIRROR_ADJUSTMENT_LOCK` | 锁定外后视镜调节 | `LOCK` | `MIRROR` | `ADJUSTMENT_LOCK_STATE` | `BODY_MIRROR_ADJUSTMENT_LOCK` |
| 2 | `MIRROR_ADJUSTMENT_UNLOCK` | 解锁外后视镜调节 | `UNLOCK` | `MIRROR` | `ADJUSTMENT_LOCK_STATE` | `BODY_MIRROR_ADJUSTMENT_LOCK` |
| 3 | `ABS_ENABLE` | 启用防抱死制动系统 | `ENABLE` | `ABS` | `STATE` | `ADAS_ABS_ENABLE` |
| 4 | `ABS_DISABLE` | 停用防抱死制动系统 | `DISABLE` | `ABS` | `STATE` | `ADAS_ABS_ENABLE` |
| 5 | `TCS_ENABLE` | 启用牵引力控制系统 | `ENABLE` | `TCS` | `STATE` | `ADAS_TCS_ENABLE` |
| 6 | `TCS_DISABLE` | 停用牵引力控制系统 | `DISABLE` | `TCS` | `STATE` | `ADAS_TCS_ENABLE` |
| 7 | `EBD_ENABLE` | 启用电子制动力分配系统 | `ENABLE` | `EBD` | `STATE` | `ADAS_EBD_ENABLE` |
| 8 | `EBD_DISABLE` | 停用电子制动力分配系统 | `DISABLE` | `EBD` | `STATE` | `ADAS_EBD_ENABLE` |
| 9 | `EBA_ENABLE` | 启用紧急制动辅助系统 | `ENABLE` | `EBA` | `STATE` | `ADAS_EBA_ENABLE` |
| 10 | `EBA_DISABLE` | 停用紧急制动辅助系统 | `DISABLE` | `EBA` | `STATE` | `ADAS_EBA_ENABLE` |
| 11 | `HOOD_SET_POSITION` | 设置前舱盖开度 | `ADJUST` | `HOOD` | `OPENING_POSITION` | `BODY_HOOD` |
| 12 | `LOW_RANGE_ENABLE` | 启用低速四驱或低速挡 | `ENABLE` | `TRANSMISSION` | `LOW_RANGE_STATE` | `TRANSMISSION_LOW_RANGE` |
| 13 | `LOW_RANGE_DISABLE` | 停用低速四驱或低速挡 | `DISABLE` | `TRANSMISSION` | `LOW_RANGE_STATE` | `TRANSMISSION_LOW_RANGE` |
| 14 | `TORQUE_DISTRIBUTION_SET` | 设置前后轴扭矩分配 | `SET` | `TRANSMISSION` | `TORQUE_DISTRIBUTION` | `TRANSMISSION_TORQUE_DISTRIBUTION` |
| 15 | `TRANSMISSION_PERFORMANCE_MODE_SET` | 设置变速箱性能模式 | `SWITCH_MODE` | `TRANSMISSION` | `PERFORMANCE_MODE` | `TRANSMISSION_PERFORMANCE_MODE` |
| 16 | `DIFFERENTIAL_LOCK` | 锁定差速器 | `LOCK` | `DIFFERENTIAL` | `LOCK_STATE` | `TRANSMISSION_DIFF_LOCK` |
| 17 | `DIFFERENTIAL_UNLOCK` | 解锁差速器 | `UNLOCK` | `DIFFERENTIAL` | `LOCK_STATE` | `TRANSMISSION_DIFF_LOCK` |
| 18 | `ELECTRIC_POWERTRAIN_ENGAGE` | 结合电驱动力 | `ENGAGE` | `ELECTRIC_POWERTRAIN` | `ENGAGEMENT_STATE` | `TRANSMISSION_ELECTRICAL_POWERTRAIN_ENGAGEMENT` |
| 19 | `ELECTRIC_POWERTRAIN_DISENGAGE` | 分离电驱动力 | `DISENGAGE` | `ELECTRIC_POWERTRAIN` | `ENGAGEMENT_STATE` | `TRANSMISSION_ELECTRICAL_POWERTRAIN_ENGAGEMENT` |
| 20 | `CLUTCH_SET_ENGAGEMENT` | 设置离合器结合度 | `ADJUST` | `CLUTCH` | `ENGAGEMENT_LEVEL` | `TRANSMISSION_CLUTCH` |
| 21 | `PARK_LOCK` | 结合驻车锁 | `LOCK` | `PARK_LOCK` | `ENGAGEMENT_STATE` | `TRANSMISSION_PARK_LOCK` |
| 22 | `PARK_UNLOCK` | 释放驻车锁 | `UNLOCK` | `PARK_LOCK` | `ENGAGEMENT_STATE` | `TRANSMISSION_PARK_LOCK` |

## 71项正式用户语音意图

| # | canonical_intent_id | 中文语义 | action | target | attribute |
|---:|---|---|---|---|---|
| 1 | `MIRROR_HEATING_ON` | 开启外后视镜加热 | `TURN_ON` | `MIRROR` | `HEATING_STATE` |
| 2 | `MIRROR_HEATING_OFF` | 关闭外后视镜加热 | `TURN_OFF` | `MIRROR` | `HEATING_STATE` |
| 3 | `SEAT_LONGITUDINAL_SET_POSITION` | 设置座椅前后位置 | `ADJUST` | `SEAT` | `LONGITUDINAL_POSITION` |
| 4 | `SEAT_TILT_SET_ANGLE` | 设置座椅整体倾角 | `ADJUST` | `SEAT` | `TILT_ANGLE` |
| 5 | `SEAT_BACKREST_SET_ANGLE` | 设置座椅靠背角度 | `ADJUST` | `SEAT` | `BACKREST_ANGLE` |
| 6 | `SEAT_HEIGHT_SET_POSITION` | 设置座椅高度 | `ADJUST` | `SEAT` | `HEIGHT` |
| 7 | `SEAT_LUMBAR_SET_HEIGHT` | 设置座椅腰托高度 | `ADJUST` | `SEAT` | `LUMBAR_HEIGHT` |
| 8 | `SEAT_LUMBAR_SET_SUPPORT` | 设置座椅腰托支撑程度 | `ADJUST` | `SEAT` | `LUMBAR_SUPPORT` |
| 9 | `STEERING_WHEEL_SET_EXTENSION` | 设置方向盘伸缩位置 | `ADJUST` | `STEERING_WHEEL` | `EXTENSION` |
| 10 | `STEERING_WHEEL_SET_TILT` | 设置方向盘倾斜位置 | `ADJUST` | `STEERING_WHEEL` | `TILT_POSITION` |
| 11 | `DEFROST_ON` | 开启风挡除霜除雾 | `TURN_ON` | `WINDSHIELD` | `DEFROST_STATE` |
| 12 | `DEFROST_OFF` | 关闭风挡除霜除雾 | `TURN_OFF` | `WINDSHIELD` | `DEFROST_STATE` |
| 13 | `WINDSHIELD_HEATING_ON` | 开启风挡加热 | `TURN_ON` | `WINDSHIELD` | `HEATING_STATE` |
| 14 | `WINDSHIELD_HEATING_OFF` | 关闭风挡加热 | `TURN_OFF` | `WINDSHIELD` | `HEATING_STATE` |
| 15 | `ESC_ENABLE` | 启用车身电子稳定系统 | `ENABLE` | `ESC` | `STATE` |
| 16 | `ESC_DISABLE` | 停用车身电子稳定系统 | `DISABLE` | `ESC` | `STATE` |
| 17 | `TRUNK_OPEN` | 打开行李厢 | `OPEN` | `TRUNK` | `OPENING_STATE` |
| 18 | `TRUNK_CLOSE` | 关闭行李厢 | `CLOSE` | `TRUNK` | `OPENING_STATE` |
| 19 | `TRUNK_SET_POSITION` | 设置行李厢开度 | `ADJUST` | `TRUNK` | `OPENING_POSITION` |
| 20 | `TRUNK_LOCK` | 锁定行李厢 | `LOCK` | `TRUNK` | `LOCK_STATE` |
| 21 | `TRUNK_UNLOCK` | 解锁行李厢 | `UNLOCK` | `TRUNK` | `LOCK_STATE` |
| 22 | `HOOD_OPEN` | 打开前舱盖 | `OPEN` | `HOOD` | `OPENING_STATE` |
| 23 | `HOOD_CLOSE` | 关闭前舱盖 | `CLOSE` | `HOOD` | `OPENING_STATE` |
| 24 | `GEAR_SET` | 设置目标挡位 | `SWITCH_MODE` | `TRANSMISSION` | `SELECTED_GEAR` |
| 25 | `GEAR_CHANGE_MODE_SET` | 设置自动或手动换挡模式 | `SWITCH_MODE` | `TRANSMISSION` | `GEAR_CHANGE_MODE` |
| 26 | `HORN_ACTIVATE` | 鸣笛 | `ACTIVATE` | `HORN` | `SOUND` |
| 27 | `MIRROR_FOLD` | 折叠外后视镜 | `FOLD` | `MIRROR` | `FOLDING_STATE` |
| 28 | `MIRROR_UNFOLD` | 展开外后视镜 | `UNFOLD` | `MIRROR` | `FOLDING_STATE` |
| 29 | `MIRROR_SET_ANGLE` | 设置外后视镜角度 | `ADJUST` | `MIRROR` | `ANGLE` |
| 30 | `SUNROOF_OPEN` | 打开天窗 | `OPEN` | `SUNROOF` | `OPENING_STATE` |
| 31 | `SUNROOF_CLOSE` | 关闭天窗 | `CLOSE` | `SUNROOF` | `OPENING_STATE` |
| 32 | `SUNROOF_SET_TILT` | 控制天窗翘起或下收 | `ADJUST` | `SUNROOF` | `TILT_OPERATION` |
| 33 | `CRUISE_ENABLE` | 启用巡航 | `ENABLE` | `CRUISE` | `STATE` |
| 34 | `CRUISE_DISABLE` | 停用巡航 | `DISABLE` | `CRUISE` | `STATE` |
| 35 | `CRUISE_SET_SPEED` | 设置巡航速度 | `SET` | `CRUISE` | `SPEED` |
| 36 | `CRUISE_SET_GAP` | 设置巡航跟车距离 | `SET` | `CRUISE` | `FOLLOWING_GAP` |
| 37 | `HEADLIGHT_SET_MODE` | 设置主灯模式 | `SWITCH_MODE` | `HEADLIGHT` | `MODE` |
| 38 | `HAZARD_LIGHT_ON` | 开启危险警示灯 | `TURN_ON` | `HAZARD_LIGHT` | `STATE` |
| 39 | `HAZARD_LIGHT_OFF` | 关闭危险警示灯 | `TURN_OFF` | `HAZARD_LIGHT` | `STATE` |
| 40 | `TURN_INDICATOR_ON` | 开启转向灯 | `TURN_ON` | `TURN_INDICATOR` | `STATE` |
| 41 | `TURN_INDICATOR_OFF` | 关闭转向灯 | `TURN_OFF` | `TURN_INDICATOR` | `STATE` |
| 42 | `LOW_BEAM_ON` | 开启近光灯 | `TURN_ON` | `LOW_BEAM` | `STATE` |
| 43 | `LOW_BEAM_OFF` | 关闭近光灯 | `TURN_OFF` | `LOW_BEAM` | `STATE` |
| 44 | `HIGH_BEAM_ON` | 开启远光灯 | `TURN_ON` | `HIGH_BEAM` | `STATE` |
| 45 | `HIGH_BEAM_OFF` | 关闭远光灯 | `TURN_OFF` | `HIGH_BEAM` | `STATE` |
| 46 | `FOG_LIGHT_ON` | 开启雾灯 | `TURN_ON` | `FOG_LIGHT` | `STATE` |
| 47 | `FOG_LIGHT_OFF` | 关闭雾灯 | `TURN_OFF` | `FOG_LIGHT` | `STATE` |
| 48 | `PARKING_LIGHT_ON` | 开启驻车灯 | `TURN_ON` | `PARKING_LIGHT` | `STATE` |
| 49 | `PARKING_LIGHT_OFF` | 关闭驻车灯 | `TURN_OFF` | `PARKING_LIGHT` | `STATE` |
| 50 | `WINDOW_OPEN` | 打开车窗 | `OPEN` | `WINDOW` | `OPENING_STATE` |
| 51 | `WINDOW_CLOSE` | 关闭车窗 | `CLOSE` | `WINDOW` | `OPENING_STATE` |
| 52 | `WINDOW_SET_POSITION` | 设置车窗开度 | `ADJUST` | `WINDOW` | `OPENING_POSITION` |
| 53 | `DOOR_OPEN` | 打开车门 | `OPEN` | `DOOR` | `OPENING_STATE` |
| 54 | `DOOR_CLOSE` | 关闭车门 | `CLOSE` | `DOOR` | `OPENING_STATE` |
| 55 | `DOOR_SET_POSITION` | 设置车门开度 | `ADJUST` | `DOOR` | `OPENING_POSITION` |
| 56 | `DOOR_LOCK` | 锁定车门 | `LOCK` | `DOOR` | `LOCK_STATE` |
| 57 | `DOOR_UNLOCK` | 解锁车门 | `UNLOCK` | `DOOR` | `LOCK_STATE` |
| 58 | `WIPER_SET_MODE` | 设置雨刮模式 | `SWITCH_MODE` | `WIPER` | `MODE` |
| 59 | `WIPER_SET_SENSITIVITY` | 设置雨刮灵敏度 | `ADJUST` | `WIPER` | `SENSITIVITY` |
| 60 | `PARKING_BRAKE_APPLY` | 施加驻车制动 | `APPLY` | `PARKING_BRAKE` | `APPLICATION_STATE` |
| 61 | `PARKING_BRAKE_RELEASE` | 释放驻车制动 | `RELEASE` | `PARKING_BRAKE` | `APPLICATION_STATE` |
| 62 | `PARKING_BRAKE_AUTO_APPLY_ENABLE` | 启用驻车制动自动施加 | `ENABLE` | `PARKING_BRAKE` | `AUTO_APPLY_STATE` |
| 63 | `PARKING_BRAKE_AUTO_APPLY_DISABLE` | 停用驻车制动自动施加 | `DISABLE` | `PARKING_BRAKE` | `AUTO_APPLY_STATE` |
| 64 | `ACCELERATE` | 加速 | `ACCELERATE` | `VEHICLE` | `SPEED` |
| 65 | `DECELERATE` | 减速 | `DECELERATE` | `VEHICLE` | `SPEED` |
| 66 | `BRAKE` | 执行制动 | `BRAKE` | `SERVICE_BRAKE` | `NORMAL_BRAKING` |
| 67 | `EMERGENCY_BRAKE` | 执行紧急制动 | `BRAKE` | `SERVICE_BRAKE` | `EMERGENCY_BRAKING` |
| 68 | `LANE_CHANGE` | 变更车道 | `CHANGE` | `LANE` | `POSITION` |
| 69 | `LANE_KEEP` | 保持当前车道 | `KEEP` | `LANE` | `POSITION` |
| 70 | `EVASIVE_STEER` | 执行避险转向 | `STEER` | `VEHICLE` | `TRAJECTORY` |
| 71 | `AUTO_PARK_ENABLE` | 启用自动泊车 | `ENABLE` | `AUTO_PARK` | `STATE` |

## 合同与本体统计

| 指标 | 全部93条语义 | 正式71条 | 已知不开放22条 |
|---|---:|---:|---:|
| Intent | 93 | 71 | 22 |
| canonical_action | 24 | 22 | 9 |
| canonical_target | 34 | 26 | 11 |
| control_attribute | 36 | 30 | 9 |

- VALUE contracts: `17`
- DIRECTION contracts: `11`
- MODE contracts: `8`
- conditional slot contracts: `3`

## 当前7项运行支持事实

这些项目均存在独立的后端模拟器动作配置、执行服务调用链和测试证据；保留 `execution_support=FULL`，但不参与 Full NLU 标签空间定义。

| Intent | adapter action | finding |
|---|---|---|
| `WINDOW_OPEN` | `打开|车窗` | `INDEPENDENT_BACKEND_IMPLEMENTATION_CONFIRMED` |
| `DOOR_OPEN` | `打开|车门` | `INDEPENDENT_BACKEND_IMPLEMENTATION_CONFIRMED` |
| `DOOR_UNLOCK` | `解锁|车门` | `INDEPENDENT_BACKEND_IMPLEMENTATION_CONFIRMED` |
| `ACCELERATE` | `加速|速度` | `INDEPENDENT_BACKEND_IMPLEMENTATION_CONFIRMED` |
| `DECELERATE` | `减速|速度` | `INDEPENDENT_BACKEND_IMPLEMENTATION_CONFIRMED` |
| `BRAKE` | `打开|制动` | `INDEPENDENT_BACKEND_IMPLEMENTATION_CONFIRMED` |
| `AUTO_PARK_ENABLE` | `打开|自动泊车` | `INDEPENDENT_BACKEND_IMPLEMENTATION_CONFIRMED` |

## 7-Intent PoC Active Dependency Audit

- `ACTIVE_FULL_NLU_DEPENDENCY_COUNT = 0`
- 历史脚本和测试仍保留，统一分类为历史/待复盘代码，不是 Full NLU 主路径。
- 后端运行代码及 config 中未发现 `sys014-poc7-*`、RBT3/ELECTRA 7类 checkpoint 或7类 label mapping 加载。

| 分类 | 引用行数 |
|---|---:|
| `HISTORICAL_POC_ONLY` | 53 |

完整代码引用关系见同目录 machine-readable JSON 的 `historical_poc_dependency_audit.all_code_references`。

## Validator

- status: `PASS`
- semantic key collision count: `0`
- duplicate intent ID count: `0`
- unresolved contract count: `0`
- source traceability error count: `0`

## Annotation schema

现有 `data/nlu/spec/annotation_schema.json` 与下一阶段冻结的中文统一样本结构冲突。本轮未修改；下一阶段必须以显式适配层替换，不能静默兼容。
