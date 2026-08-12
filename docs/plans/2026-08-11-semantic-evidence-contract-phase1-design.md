# 语证证据链第一阶段统一契约设计

## 背景与目标

本阶段将冻结的 `SemanticOrchestratorV2.1` 提升为后端唯一正式语义实现，建立唯一 `SemanticFrame`、有序子意图及最终多意图 `EvidenceDemand` 契约。迁移不提供兼容接入，不改变冻结语义算法、证据类型体系、HNSW、质量公式、因果或最终裁决算法。

成功标准是生产链只有一个语义入口；正式意图编号和安全信号均来自同一次冻结语义运行；多意图及 REVIEW 中已解析子句保持原序；证据需求只由 `EvidenceDemand.intent_demands` 拥有；冻结 99 条语义结果保持一致。

## 现状与约束

- 生产 `CommandPipeline` 当前仍调用旧 `SemanticFrameParser`。
- 冻结 V2.1 当前位于 `experiments/semantic_orchestrator_v2_1`，尚未进入生产。
- V2.1 正常结果从 `output.sub_intents` 输出正式意图编号；REVIEW 已解析结果保留在 `resolved_sub_intents` 和子句结果中。
- 安全信号权威来源是同一次运行的 `output.security_signals` 集合。
- 当前 `EvidenceDemandService` 会把 required/optional 类型复制回 `SemanticFrame`，形成双事实源。
- 工作树已有大量未提交修改，迁移必须逐处融合。

## 方案对比

### 方案甲：提升冻结实现为正式后端实现（采用）

- 移动并整理现有 V2/V2.1 实现及其正式运行依赖，由后端生产包持有唯一实现。
- 冻结测试改为直接导入生产实现。
- 删除旧 parser 的生产调用和无合法用途代码。

优点是生产、冻结测试共享同一实现，实验目录退出生产依赖。代价是需要系统调整导入路径和直接消费者。

### 方案乙：生产直接导入 experiments

改动较少，但实验目录会成为生产依赖，部署边界和唯一实现边界不成立，因此不采用。

### 方案丙：V2.1 与旧 parser 并行

可借旧 parser 补齐字段，但会形成双语义源、二次解析和失败回退，违反正式迁移原则，因此禁止。

## 详细设计

### 架构

冻结语义编排器在后端语义服务中成为唯一入口。服务一次运行直接生成正式 `SemanticFrame`；投影只读取同次运行的输出、子句结果、候选度量和冻结意图元数据，不重新解析原始文本，不按 action/target 反推 intent_id。

### 数据契约

`SemanticFrame` 只保存轮次信息：标识、原始/规范化文本、整体置信度、整体歧义度、语义状态、复核原因、复核候选、未解析子句、安全信号集合和有序 `intents`。

每个 `SemanticIntent` 保存 `clause_index`、`clause_text`、`intent_id`、`action`、`target`、`area`、`value`、`control_domain`、`risk_level`、`risk_tags`、`semantic_confidence`、`ambiguity_score`。动作等子意图字段不在帧顶层重复。

`EvidenceDemand` 一轮一个，仅保存标识、轮次标识和按 `clause_index` 排序的 `intent_demands`。每项独立保存意图编号、子句字段、查询向量及元数据、required/optional 类型、优先级和检索范围。不得持久化聚合集合。

### 数据流

Pipeline 对每个子意图构建一项需求并分别执行向量检索；当前步骤需要的 required/optional 并集只作为局部变量计算。Safety Gate 接收 `SemanticFrame` 和 `EvidenceDemand`，按子意图匹配证据需求。审计、API、图和展示直接序列化或消费新结构。

安全信号保留 V2.1 输出集合的完整基数，不创建第二安全上下文。REVIEW 不清除已经成功解析的子意图；整体状态完全继承冻结编排器裁决。

### 异常与边界

- 冻结语义初始化或运行错误直接失败，不回退旧 parser。
- NO_MATCH/REVIEW 可产生空或部分 `intents`，但保持原状态和原因。
- 终止型语音响应也使用同一语义入口生成空输入帧。
- 当前 action evidence map 仍是唯一证据需求规则；不接入后续注册表。

### 测试策略

- 迁移并运行完整语义组件及 99 条冻结用例，对比迁移前冻结产物。
- 验证单意图、多意图原序、REVIEW 部分意图和安全注入信号集合。
- 运行受影响单元、流水线、审计、API 和 Safety Gate 测试。
- 全仓扫描旧字段、旧 parser 调用、action/target 反推、兼容层、回退、第二安全源及生产到 experiments 的依赖。

## 风险与控制

- 既有单意图消费者较多：通过直接改签名和显式逐意图处理迁移，不建立转换器。
- 工作树已有修改：实施前后分别保存差异清单，只用局部补丁融合。
- 冻结组件依赖链较深：移动后由冻结哈希和 99 条结果对比证明算法未变。
