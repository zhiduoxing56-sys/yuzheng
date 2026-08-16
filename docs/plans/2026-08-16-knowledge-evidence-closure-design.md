# 120 KnowledgeNode × 38 Evidence 闭环验收设计

## 背景与目标

以 `data/knowledge_nodes_v4.jsonl` 的 120 个正式节点为唯一生产审计范围，逐节点验证 `canonical_action`、`required_evidence` 和 `optional_evidence`。所有非 canonical Evidence 只能归入：A 旧名迁移、B 物理安全事实缺口、C 非实时物理证据域。

成功标准是：所有 120 个节点都有确定结论；允许进入 Realtime Physical Evidence demand 的节点，其 required/optional evidence 全部属于 38 类 canonical namespace；运行时加载器不得再静默删除非法 evidence。

## 现状与约束

- 正式文件正好 120 节点；此前报告的第 121–124 个来自 mock 文件。
- 正式 120 节点当前有 47 个非 canonical Evidence ID；mock 文件另有测试占位符 `NON_CANONICAL_TYPE`，不计入生产 47 个。
- 现有加载器 `_canonical_unique` 会静默过滤未知 required/optional evidence。
- KnowledgeNode schema、38 类 Evidence Space 和安全裁决结构均不扩展。

## 方案对比

### 方案 A：显式分类清单、源数据迁移、fail-fast 门禁（采用）

- 用版本化 YAML 固化 A/B/C 结论。
- A 类在源 JSONL 中一次性迁移到 canonical ID。
- B/C 节点不进入在线 Physical Evidence demand。
- Trusted 加载遇到非法 required/optional evidence 直接失败，禁止静默删除。
- 生成逐节点 JSON/Markdown 审计结果并由测试门禁。

### 方案 B：仅报告

改动最少，但运行时仍可能静默删除 required evidence，不能满足闭环目标。

### 方案 C：扩展 KnowledgeNode schema

增加 domain/eligibility 字段更强，但会扩大本轮范围并引入消费者迁移。

## 详细设计

### 分类

- A：`WEATHER → ENVIRONMENT_CONDITIONS`、`VEHICLE_STATIONARY → VEHICLE_SPEED`、`ACCELERATION_STATE → VEHICLE_ACCELERATION`。
- B：本轮审计没有发现必须新增第 39 类才能表达的在线物理事实，列表为空。
- C：其余 44 个 ID 只出现在 `SEC_`、`OTA_`、`DSSAD_`、`LAW_`、`DATA_` action 域，保留为网络安全、OTA、数据记录/治理或合规知识，不映射到 38 类物理证据。

### 在线资格

节点必须同时满足：action 位于统一语义 Registry；A 类迁移后 required/optional 全部 canonical；不存在 B/C 引用。否则报告明确排除原因，不进入 Realtime Physical Evidence demand。

### 异常处理

`load_trusted_nodes` 对任何已标为 Trusted 的节点执行严格验证。required 或 optional 中存在非法 ID 时抛出带 node_id、字段名和非法值的错误；上层索引保持现有降级策略，但记录 `load_error`，不再返回被悄悄删字段的节点。

### 测试策略

- 120 节点计数和逐节点 action/evidence 闭包。
- A/B/C 清单互斥且覆盖迁移前全部 47 个非 canonical ID。
- 迁移后在线合格节点不存在非 canonical required/optional。
- C 类只出现在批准的非实时 action 域。
- Trusted 加载器对非法 required 和 optional 均 fail-fast。
- mock 的 `NON_CANONICAL_TYPE` 继续作为严格门禁测试样本，不混入正式统计。

