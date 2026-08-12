# 71 Intent Evidence Demand Registry 唯一化设计说明

## 背景与目标

第三阶段只替换 Evidence Demand Rule Source，不修改第一阶段冻结的语义结构与编排，也不修改第二阶段冻结的 32 类 Evidence Type、运行时映射和安全分层。`证据/evidence_demand_registry_v1.yaml` 将成为 `SemanticIntent.intent_id → Evidence Requirement` 的唯一生产事实源，旧 `config/action_evidence_map.yaml` 及其 action/target 查询、fallback 和 priority 来源全部删除。

## 现状与约束

- Evidence Demand Registry 已包含 71 项，key 与正式 R4 Intent ID 集合相等，全部证据引用属于标准 32 类。
- Registry 有 7 条自由文本 `conditional_mandatory` 和 1 条自由文本全局安全规则，必须一次性迁移为白名单结构化条件。
- 每条 AREA 条件必须属于当前 Intent 自己的 R4 `allowed_areas`；缺少已解析区域时 `SemanticIntent.area` 为 `unknown`，不增加别名或翻译 fallback。
- Evidence Demand Intent 节点只保存 `mandatory`、`recommended`、`conditional_mandatory`、`rationale`，不复制 R4 中文名、能力族或风险元数据，也不保存派生 Intent 数量。
- `priority` 仅被展示层读取，不参与生产安全逻辑，可固定为 0。
- HNSW、Mandatory Recall、Quality、Graph、Safety Gate、Decision、Memory、Causal 和 Runtime Mapping 均保持不变。

## 方案对比

### 专用不可变 Registry Loader（采用）

- 优点：职责边界明确；启动时集中 fail-fast；运行时只有 intent_id 查询；便于证明单一事实源。
- 缺点：增加一个专用模块和若干不可变值对象。

### 在 EvidenceDemandService 内直接解析 YAML

- 优点：文件较少。
- 缺点：加载、验证和运行时计算耦合，不利于证明 Registry 是独立权威边界。

### 建设通用配置 Registry 框架

- 优点：未来可能复用。
- 缺点：超出第三阶段范围，增加不必要的通用解析和扩展面。

## 详细设计

### 架构与数据流

Pipeline 启动时构造唯一 `EvidenceDemandRegistry`。正式 R4 的现行合同为 `FROZEN_FORMAL_RUNTIME_REGISTRY` 且 `runtime_loading_allowed: true`，仅允许生产组件只读加载。Loader 同时读取正式 R4 Registry、Evidence Type Catalog 和 Evidence Demand Registry，完成全量验证后保存不可变规则；若 R4 禁止 runtime loading 则启动失败。`EvidenceDemandService` 逐个按 `clause_index` 排序的 `SemanticIntent` 精确调用 `rule_for_intent_id()`，依次合并 mandatory、当前子意图命中的 conditional add、全局 security rule add，并稳定去重；recommended 中已晋升为 required 的项删除。

### 条件白名单

- 子意图条件只允许 `field: area`、`op: IN`、非空字符串 `values`，且每个值必须属于当前 `intent_id` 自己的 R4 `allowed_areas`。
- 全局条件只允许 `field: security_signals`、`op: NONEMPTY`。
- 未知 field/op、畸形值、未知 Evidence Type、未知 Intent 或覆盖集合不一致均抛出配置错误。
- 不执行表达式、不扫描 raw_text、不读取 Registry 中的风险或语义元数据。
- Intent 数量从 R4 `intents` 实际集合推导；conditional/global rule 数量由 Registry 决定，不设生产固定数量门槛。
- 核心 `SECURITY_CONTEXT_CLAIM` 必须存在，并精确保持 `security_signals/NONEMPTY -> AUTHORIZATION_STATE, SYSTEM_MODE`；其他结构合法且 ID 唯一的 global rule 可扩展。

### 固定输出规则

- `priority = 0`
- `retrieval_scope = control_evidence`
- query_text、query_vector 与现有向量化机制不变。
- REVIEW 中保留的 resolved intents 仍逐项生成需求；NO_MATCH 因无 intents 生成空列表。

### 测试策略

新增 Registry 专项测试覆盖 71/71、R4 集合、32 类引用、结构化条件、未知配置 fail-fast 和关键 Intent 精确需求。更新 Evidence Demand、Pipeline、Stage4 与场景测试，使其只依赖新 Registry。最后运行冻结 99、关键全链、compileall、`git diff --check` 和旧规则残留扫描。
