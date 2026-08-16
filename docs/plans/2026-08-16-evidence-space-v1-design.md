# Evidence Space v1 设计说明

## 背景与目标

Evidence Space v1 必须由本地标准源码、现有 32 类正式 Evidence 和在线车控安全知识共同决定。正式事实源仍只有 `证据/evidence_type_catalog_v1.yaml` 与 `证据/evidence_runtime_mapping_v1.yaml`，不建立 V2、别名或并行 Standard Evidence namespace。

## 方案对比

1. 原位扩展 canonical 两文件：可保持单一 namespace，并让标准字段、派生字段和内部安全字段在同一 runtime contract 中可审计。
2. 只生成标准报告：不会改善运行时表达能力，无法通过四个场景的字段级验收。
3. 新建标准专用 registry：会形成并行事实源，违反约束。

采用方案 1。

## 详细设计

### 标准输入

- COVESA VSS 6.0：直接读取 `.vspec`、`units.yaml`、`quantities.yaml`。
- ASAM OSI 3.8.0：直接读取 `.proto` 与 `VERSION`。
- ASAM OpenSCENARIO XML 1.4.0：直接读取 `OpenSCENARIO.xsd`。
- ASAM OpenDRIVE 1.9.0：直接读取多文件 XSD。
- Android Automotive VHAL（本地 Android 16 快照）：直接读取 `VehicleProperty.aidl` 及枚举 AIDL。

### Canonical 类型决策

保留原 32 类，新增六个标准和安全需求共同证明的最小母类：

- `VEHICLE_ACCELERATION`：VSS/OSI 的自车加速度事实。
- `HVAC_STATE`：VSS 分区 HVAC 事实。
- `ROAD_STRUCTURE_STATE`：OpenDRIVE 道路类型、路口、结构与静态表面引用。
- `COLLISION_ASSIST_STATE`：以 `feature` 参数表达 AEB、FCW、BSW、低速碰撞和横穿交通能力。
- `LANE_ASSIST_STATE`：以 `feature` 参数表达 LDW、LKA、LCA、ELKA。
- `DRIVER_MONITORING_STATE`：驾驶员困倦、分心、手握方向盘和告警事实。

不新增八方向类型；`region` 由 OSI 相对位置派生。不为 CAMERA/RADAR/LIDAR/ULTRASONIC 建类型；它们属于 source。OSI `SensorView`、`GroundTruth` 进入来源上下文，Evidence 质量进入统一 envelope。

### 字段来源性质

每个 runtime leaf field 都具有 `field_provenance`，且 `mapping_kind` 只能为 `DIRECT_STANDARD`、`DERIVED`、`INTERNAL_SECURITY`。直接标准字段保留本地源文件、标准实体/字段、数据类型和单位；八方向、距离、相对速度、运动状态和风险级别明确为派生字段。

### 兼容与边界

KnowledgeNode 的 `conditions`、`required_evidence`、`optional_evidence` 结构不变。新类型默认 `UNAVAILABLE`，未接入真实数据时不伪造传感器来源。现有模拟器字段继续如实标记 `SIMULATION`。

### 验收

- catalog 与 runtime mapping 类型集合完全一致且为 38 类。
- 所有 runtime leaf field 均有合法 provenance。
- 四个反向场景可由母类及字段 contract 表达。
- 生成 `证据/evidence_standard_mapping.md`，但该文件只是由两份正式 YAML 确定性生成的报告。
- KnowledgeNode schema、EvidenceDemand 算法、SafetyGate、CBN、Decision、Authorization、Execution 和前端均不改动。
