# VSS 6.0 第一阶段离线导入设计

## 背景与目标

本阶段固定导入 COVESA Vehicle Signal Specification 正式发布版 v6.0 的
`vss.csv`，建立版本化、可审计、可重复生成的车辆可控能力候选源数据。

本阶段只产生以下四层中的第一层到第二层之间的候选关系：

```text
VSS actuator
!= 语音可控能力
!= 当前语证支持能力
!= 安全规则
```

VSS actuator 只表示 VSS 视角下可读写的车辆信号。导入结果不注册运行时动作，
不修改语义规则、证据需求、安全规则、授权、执行、CARLA 或前端实现。

## 现状与隔离边界

当前项目的运行时车控链分别由以下位置承担：

- `config/semantic_rules.yaml`：动作、目标、控制域和风险语义。
- `config/action_evidence_map.yaml`：动作所需证据。
- `config/safety_rules.yaml`：安全硬门规则。
- `config/vehicle_actions.yaml`：模拟器可执行动作。
- `backend/app/services/semantic/parser.py`：语义解析。
- `backend/app/services/decision/safety_gate.py`：安全门。
- `backend/app/services/execution/service.py`：授权后执行。

上述文件及冻结 HTTP 契约、数据库、Memory、Causal、Bayesian 和 SafetyScore
实现均不属于本阶段修改范围。

## 数据布局

```text
data/standards/vss/6.0/
├── source/
│   ├── vss.csv
│   └── metadata.json
└── generated/
    ├── vss_actuators_raw.json
    ├── vss_actuators_normalized.json
    ├── vss_capability_candidates.json
    ├── vss_import_report.json
    └── vss_import_report.md
```

导入实现位于 `scripts/import_vss.py`，测试位于
`backend/tests/data/test_vss_import.py`。

## 官方来源

- 上游项目：COVESA/vehicle_signal_specification
- 版本：VSS 6.0
- Release tag：v6.0
- Release commit：20c609b
- Artifact：`https://github.com/COVESA/vehicle_signal_specification/releases/download/v6.0/vss.csv`
- License：MPL-2.0

导入器只接受上述版本身份。若本地不存在 source CSV，导入器尝试从固定 artifact
下载；下载失败时给出准确的人工放置路径。

## 数据流

1. 读取 CSV，检查固定列名和异常行。
2. 计算 source SHA-256 和文件大小，创建或校验 `metadata.json`。
3. 选出全部 `Type == actuator` 的行形成 raw 层；deprecated 行保留。
4. 排除明确 deprecated 的 actuator，形成 normalized 层。
5. 每个 normalized actuator 一对一产生一个 capability candidate，禁止跨节点合并。
6. 生成 JSON 统计和 Markdown 报告。

所有记录按 VSS path 稳定排序；JSON 使用固定缩进、固定键顺序策略和 UTF-8，
相同输入与 metadata 重复执行得到逐字节一致的 generated 文件。

## 原始与标准化语义

Raw 层保留 CSV 全部原始字段，并额外提供规范字段、源行号、deprecated 布尔值和
deprecation 原文。Normalized 层只做确定性解析：空值转 `null`，数值约束转数值，
Allowed 转列表，同时保留 raw 引用和 upstream metadata 引用。

## 候选生成

每个有效 actuator 独立生成候选。候选包括 domain、component、component_path、
instance、property、datatype、value_constraint、control_mode、parameters 和原始路径。
候选名称只用于辅助人工整理，不代表语音表达，也不把布尔值解释为“打开/关闭”。

控制模式确定性分类：

- boolean：BOOLEAN
- 有 Allowed 值：ENUM
- 标量整数/浮点：NUMERIC
- string：STRING
- 数组或 struct：STRUCT
- 未知类型：OTHER

## 人工复核

以下情况保留候选并标记 `manual_review_required=true`：

- MotionManagement、ADAS、Powertrain。
- 诊断、故障、健康管理、内部 request/command/set-point/control interface 语义。
- 原始 datatype 为 string。
- STRUCT 或未知 datatype。
- 同一父节点存在 IsOpen/Position/Switch，或 ActualPosition/TargetPosition 等冲突。
- boolean 描述未明确说明 true/false 语义。
- 根级、组件无法确定或明显技术目标/限制量等难以映射的节点。

`manual_review_reasons` 记录所有命中的确定性原因，不删除任何有效 actuator。

## 异常与报告

报告记录总条目、actuator、deprecated、有效 actuator、原始 datatype、控制模式、
一级域、二级域、主要车辆域、候选数、人工复核数，以及无法解析行、关键字段缺失、
未知 datatype、重复 path、Allowed 解析失败和其他异常。

## 测试策略

测试覆盖版本和 metadata、SHA-256、actuator 筛选、deprecated 排除、布尔/枚举/
数值约束、Door 实例、多个车门实例、三层追溯、一对一候选、人工复核、逐字节
可复现，以及运行时配置、数据库和冻结契约在导入前后摘要不变。

