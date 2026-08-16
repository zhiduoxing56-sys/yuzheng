# 安全知识场景上下文完整接入设计说明

## 背景与目标

在已冻结的 38 类 Evidence Space、Trusted Knowledge filtered HNSW 和 Evidence Demand 合并链上，将当前轮可信 Evidence 投影为确定性知识查询上下文，提高同一动作下的场景敏感性。

成功标准：挡位、道路、环境、区域目标、系统模式和授权状态只在当前轮证据有效时进入唯一 Knowledge Query Builder；每个查询字段可追溯 EvidenceNode；演示状态经现有 EvidenceRepository 入库；不改变 KnowledgeNode、HNSW、阈值、安全规则或前端。

## 现状与约束

- `TrustedKnowledgeIndexService.build_query_text()` 当前直接读取 `VehicleState`，没有 EvidenceNode 来源关系。
- 当前轮 VehicleState 和 evidence overrides 在知识增强之后才进入 EvidenceRepository。
- `demo_scenarios.yaml` 是唯一演示场景预置，`EvidenceObservationInput` 和 EvidenceRepository 已负责 timestamp、expires、availability、freshness、validity 与 integrity。
- 正式事实源为 `证据/evidence_type_catalog_v1.yaml` 与 `证据/evidence_runtime_mapping_v1.yaml`。
- 不新增 Evidence Type、Context/Scene 模型或 Query Builder。

## 方案对比

### 方案一：Evidence-first 临时投影（采用）

- 当前轮正式 EvidenceNode 在知识增强前入库。
- Query Builder 从有效节点确定性投影字段，并把 evidence_type、node_id、source 写入检索审计。
- 优点：满足来源追溯和质量门槛，不产生第二模型或第二事实源。
- 代价：需要调整主链中“当前轮证据入库”和“知识增强”的先后顺序，但不改变安全决策规则。

### 方案二：继续直接读取 VehicleState

- 优点：改动少。
- 缺点：无法证明字段来自有效 Evidence，不能消费 evidence overrides，不满足目标。

### 方案三：扩展 RuntimeSafetyContext

- 优点：有显式类型。
- 缺点：混淆安全互锁上下文与 Evidence，形成并行事实表达，不采用。

## 详细设计

### 架构与数据流

```text
VehicleState / demo scenario evidence_overrides
→ EvidenceRepository 当前轮 EvidenceNode
→ 有效性过滤与区域相关上下文投影
→ 唯一 TrustedKnowledgeIndexService.build_query_text()
→ 现有 canonical_action filtered HNSW
→ Knowledge Hits / dynamic Evidence Demand
→ 原安全主链
```

### 查询上下文

- `VEHICLE_SPEED`：速度值、运动状态、现有配置定义的速度等级。
- `GEAR_STATE`：current_gear。
- `ROAD_FRICTION_STATE`：road_condition、wetness，以及存在的 friction_scale_factor/lower_bound/most_probable/upper_bound 原值。本轮不生成高低附着标签。
- `ENVIRONMENT_CONDITIONS`：weather、precipitation、precipitation_type/intensity、fog/fog_visibility、ambient_illumination、visibility。visibility 复用已有离散规则；缺失则省略。
- `SURROUNDING_OBJECT_STATE`：只摘要与意图 area 对应八方向的目标；优先显式 risk_level，其次距离更近的目标；使用 entity_kind、distance、relative_speed、motion_state、risk_level。没有正式距离分级时保留米值。
- `SYSTEM_MODE`：vehicle_mode 等有效内部安全事实。
- `AUTHORIZATION_STATE`：只使用当前轮正式授权 Evidence 中可用字段。

字段顺序固定；UNKNOWN、UNAVAILABLE、INVALID、MISSING、STALE、过期或 availability=0 的节点不进入查询。每个投影字段在 `knowledge_retrieval_metadata` 中保留 Evidence 来源。

### 演示场景

扩展现有 `config/demo_scenarios.yaml`。VehicleState 继续承载安全主链需要的基础状态；细粒度环境、道路和目标信息通过 `evidence_overrides` 使用 canonical Evidence object 写入，`source: SIMULATION`，不得标记为 CAMERA/RADAR/LIDAR。

### 异常与边界

- 无有效 Evidence 时省略字段，知识检索继续执行。
- 同一类型多来源按现有 Evidence 质量/最新有效观测规则选择，不由 Query Builder 自创来源优先级。
- 不从用户声明生成车辆事实。
- 不根据 relative_speed 或距离临时推导 motion_state/risk_level；只消费正式派生层已经提供的值。
- 道路附着没有正式等级阈值，只输出正式枚举或数值。

### 测试策略

- 字段到 Evidence 来源、无效/过期省略、固定顺序、区域目标隔离、多目标选择、SIMULATION 来源真实性测试。
- 主链验证 current-turn Evidence 在知识增强前可用，且 Evidence Demand 与安全规则不变。
- 重跑 HEADLIGHT、DOOR、WIPER、BRAKE、WINDOW 五组场景敏感性测试，记录 query、全候选排名、阈值命中、动态需求来源。
- 执行 targeted pytest、compileall、`git diff --check`。

## 风险与已确认项

- 已确认采用严格证据方案：没有正式阈值时禁止输出“低附着/高附着”。
- 当前真实适配器仅部分提供细粒度场景值；缺失字段由明确 `SIMULATION` 演示证据覆盖，不冒充传感器。
- 不要求排名强制翻转，只验收分数和命中变化是否符合节点语义。
