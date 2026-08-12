# COVESA VSS 6.0 第一阶段离线导入报告

## 语义边界

```text
VSS actuator
!= 语音可控能力
!= 当前语证支持能力
!= 安全规则
```

本报告中的每个 capability 都只是单个 VSS actuator 对应的候选；未进行跨节点合并，
未注册为正式可执行动作，也未修改任何语义、证据、安全、授权或车辆执行配置。
这些信号定义来源于 COVESA Vehicle Signal Specification，并非本项目原创定义。

## 官方来源

- 上游项目：`COVESA/vehicle_signal_specification`
- 版本：`VSS 6.0`
- Release tag：`v6.0`
- Release commit：`20c609b`
- Source artifact：[vss.csv](https://github.com/COVESA/vehicle_signal_specification/releases/download/v6.0/vss.csv)
- 获取时间：`2026-08-07T14:44:23Z`
- SHA-256：`6E8947C75E7FF794C75382343B69083ABBDA87D32D6D1842B06E86ADC9CC95DB`
- 文件大小：`303193` bytes
- License：`MPL-2.0`

## 总体统计

| 指标 | 数量 |
|---|---:|
| VSS 总数据项 | 1607 |
| actuator 总数 | 643 |
| deprecated actuator | 2 |
| 有效 actuator | 641 |
| capability candidate | 641 |
| manual review | 404 |

## 有效 actuator 原始 datatype

| datatype | 数量 |
|---|---:|
| `boolean` | 255 |
| `double` | 2 |
| `float` | 100 |
| `int16` | 38 |
| `int8` | 30 |
| `string` | 81 |
| `uint16` | 41 |
| `uint32` | 1 |
| `uint8` | 93 |

## 候选控制模式

| control_mode | 数量 |
|---|---:|
| BOOLEAN | 255 |
| ENUM | 57 |
| NUMERIC | 305 |
| OTHER | 0 |
| STRING | 24 |
| STRUCT | 0 |

## 主要车辆域（有效 actuator）

| 域 | 数量 |
|---|---:|
| ADAS | 21 |
| Body | 55 |
| Cabin | 455 |
| MotionManagement | 67 |
| Other | 8 |
| Powertrain | 35 |

## 人工复核原因统计

| 原因 | 候选数 |
|---|---:|
| boolean 描述未同时明确 true/false 的用户语义 | 171 |
| 内部 request/command/control 语义: request | 35 |
| 内部 request/command/control 语义: request, internal, actuator internal | 1 |
| 内部 request/command/control 语义: request, internal, set-point, steer-by-wire, actuator internal | 2 |
| 内部 request/command/control 语义: request, requested | 10 |
| 内部 request/command/control 语义: request, set-point | 3 |
| 内部 request/command/control 语义: request, set-point, steer-by-wire | 2 |
| 同一对象同时存在 ActualPosition 与 TargetPosition | 8 |
| 同一对象存在 Actual/Target 语义对: Position | 8 |
| 同一对象存在不同语义兄弟节点: IsOpen, Position, Switch | 59 |
| 同一对象存在不同语义兄弟节点: Position, Switch | 1 |
| 字符串型 actuator 需要人工确认枚举或自由文本语义 | 81 |
| 技术目标/限制量语义需人工判断: Distribution | 8 |
| 技术目标/限制量语义需人工判断: Distribution, Torque | 1 |
| 技术目标/限制量语义需人工判断: Force | 1 |
| 技术目标/限制量语义需人工判断: Limit | 1 |
| 技术目标/限制量语义需人工判断: Maximum, Distribution, Force | 1 |
| 技术目标/限制量语义需人工判断: Maximum, Distribution, Torque | 3 |
| 技术目标/限制量语义需人工判断: Maximum, Force | 1 |
| 技术目标/限制量语义需人工判断: Maximum, Limit | 2 |
| 技术目标/限制量语义需人工判断: Maximum, Limit, Torque | 2 |
| 技术目标/限制量语义需人工判断: Maximum, Torque | 6 |
| 技术目标/限制量语义需人工判断: Minimum, Distribution, Force | 1 |
| 技术目标/限制量语义需人工判断: Minimum, Distribution, Torque | 3 |
| 技术目标/限制量语义需人工判断: Minimum, Limit | 2 |
| 技术目标/限制量语义需人工判断: Minimum, Limit, Torque | 2 |
| 技术目标/限制量语义需人工判断: Minimum, Torque | 6 |
| 技术目标/限制量语义需人工判断: Omega | 8 |
| 技术目标/限制量语义需人工判断: Target | 19 |
| 技术目标/限制量语义需人工判断: Target, Force | 4 |
| 技术目标/限制量语义需人工判断: Target, Offset | 3 |
| 技术目标/限制量语义需人工判断: Target, Offset, Torque | 2 |
| 技术目标/限制量语义需人工判断: Target, Torque | 5 |
| 根级或组件不明确，无法判断用户可理解能力 | 3 |
| 诊断/健康/维护语义: fault | 9 |
| 高风险或底层控制域: ADAS | 21 |
| 高风险或底层控制域: MotionManagement | 67 |
| 高风险或底层控制域: Powertrain | 35 |

完整人工复核清单位于 `vss_import_report.json` 的 `manual_review_items`，
并可在 `vss_capability_candidates.json` 中按 `manual_review_required=true` 追溯全部字段。

## 一级域 actuator（含 deprecated）

| 一级域 | 数量 |
|---|---:|
| ADAS | 21 |
| Body | 57 |
| Cabin | 455 |
| Chassis | 5 |
| IsAutoPowerOptimize | 1 |
| MotionManagement | 67 |
| PowerOptimizeLevel | 1 |
| Powertrain | 35 |
| TripMeterReading | 1 |

## 二级域 actuator（含 deprecated）

| 二级域 | 数量 |
|---|---:|
| ADAS.ABS | 1 |
| ADAS.CruiseControl | 6 |
| ADAS.DMS | 1 |
| ADAS.EBA | 1 |
| ADAS.EBD | 1 |
| ADAS.ESC | 1 |
| ADAS.IsAutoPowerOptimize | 1 |
| ADAS.LaneDepartureDetection | 1 |
| ADAS.ObstacleDetection | 6 |
| ADAS.PowerOptimizeLevel | 1 |
| ADAS.TCS | 1 |
| Body.Hood | 3 |
| Body.Horn | 1 |
| Body.IsAutoPowerOptimize | 1 |
| Body.Lights | 14 |
| Body.Mirrors | 12 |
| Body.PowerOptimizeLevel | 1 |
| Body.RearMainSpoilerPosition | 1 |
| Body.Trunk | 10 |
| Body.Windshield | 14 |
| Cabin.Door | 40 |
| Cabin.HVAC | 30 |
| Cabin.Infotainment | 32 |
| Cabin.IsAutoPowerOptimize | 1 |
| Cabin.IsWindowChildLockEngaged | 1 |
| Cabin.Light | 42 |
| Cabin.PowerOptimizeLevel | 1 |
| Cabin.RearShade | 3 |
| Cabin.RearviewMirror | 1 |
| Cabin.Seat | 300 |
| Cabin.Sunroof | 4 |
| Chassis.ParkingBrake | 2 |
| Chassis.SteeringWheel | 3 |
| IsAutoPowerOptimize | 1 |
| MotionManagement.Brake | 28 |
| MotionManagement.ElectricAxle | 12 |
| MotionManagement.Steering | 14 |
| MotionManagement.Suspension | 13 |
| PowerOptimizeLevel | 1 |
| Powertrain.FuelSystem | 1 |
| Powertrain.IsAutoPowerOptimize | 1 |
| Powertrain.PowerOptimizeLevel | 1 |
| Powertrain.TractionBattery | 22 |
| Powertrain.Transmission | 10 |
| TripMeterReading | 1 |

## 典型候选样例

### `Vehicle.Cabin.Door.Row1.DriverSide.IsOpen`

- candidate：`door.open`
- control mode：`BOOLEAN`
- instance：`Row1.DriverSide`
- manual review：`true`
- reasons：同一对象存在不同语义兄弟节点: IsOpen, Position, Switch

### `Vehicle.Cabin.Door.Row1.DriverSide.Window.Position`

- candidate：`window.position`
- control mode：`NUMERIC`
- instance：`Row1.DriverSide`
- manual review：`true`
- reasons：同一对象存在不同语义兄弟节点: IsOpen, Position, Switch

### `Vehicle.Body.Horn.IsActive`

- candidate：`horn.active`
- control mode：`BOOLEAN`
- instance：`None`
- manual review：`false`
- reasons：无确定性复核命中；仍只是候选

### `Vehicle.ADAS.CruiseControl.IsActive`

- candidate：`cruise_control.active`
- control mode：`BOOLEAN`
- instance：`None`
- manual review：`true`
- reasons：高风险或底层控制域: ADAS

### `Vehicle.MotionManagement.Steering.SteeringWheel.AngleTarget`

- candidate：`steering_wheel.angle_target`
- control mode：`NUMERIC`
- instance：`None`
- manual review：`true`
- reasons：高风险或底层控制域: MotionManagement; 内部 request/command/control 语义: request, set-point, steer-by-wire; 技术目标/限制量语义需人工判断: Target

## 异常与无法解析项目

### 无法解析的行（0）

无。

### 缺失关键字段的行（0）

无。

### 未知 datatype（0）

无。

### 重复 path（0）

无。

### Allowed 解析失败（0）

无。

### 其他异常（0）

无。

## 隔离声明

本次导入没有写入 `semantic_rules.yaml`、`action_evidence_map.yaml`、
`safety_rules.yaml`、`vehicle_actions.yaml`、`authorization.yaml`，没有修改
Parser、Schemas 公共模型、SafetyGate、ExecutionService、CARLA、前端、数据库、
冻结契约、Memory、Causal、Bayesian 或 SafetyScore。
