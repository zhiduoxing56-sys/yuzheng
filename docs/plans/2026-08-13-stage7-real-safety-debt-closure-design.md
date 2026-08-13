# 第⑦阶段：剩余安全债真实行为收口设计

## 背景与目标

在已冻结的 149 意图语义空间与第⑤+⑥阶段 canonical command 架构上，关闭当前真实存在的执行事实源、后向状态、自动泊车、区域一致性及多意图复核安全债。最终验收以真实自然语言进入 `CommandPipeline.process_text()` 后的整链结果为准。

## 现状与约束

- Formal / Known / Total 固定为 71 / 78 / 149；Registry、Anchors、Token canonical 字段集合不变。
- `CANONICAL_EXECUTABLE_CANDIDATES` 与 capability contracts 形成第二事实源。
- DECELERATE 的 `SURROUNDING_OBJECT_STATE` 仅 recommended，rear rule 对不可用字段 fail open。
- `FREE_SPACE_STATE` 当前明确为 `UNAVAILABLE`，AUTO_PARK 专用规则却读取证据图外的 RuntimeSafetyContext camera/ultrasonic。
- 区域 helper 存在 Registry 外 compact 表；区域表达丢失可能降为 unknown 并匹配全局物理能力。
- 多 Formal occurrence 因单命令协议进入 REVIEW 时，公共 ClarificationCandidate 必须保持冻结结构；候选选择不得成为授权。
- 第⑤+⑥核心新文件当前存在于工作树但尚未被 Git 跟踪。本阶段保留并在最终状态中明确报告，不擅自提交整个脏工作树。

## 方案对比

### 方案一：局部安全债收口（采用）

- 优点：只触及任务明确允许的边界，保留既有架构和公共合同。
- 缺点：FREE_SPACE 无 producer 时 AUTO_PARK 保持不可执行。

### 方案二：新建统一安全策略层

- 优点：规则可集中描述。
- 缺点：形成新的事实层并扩大第⑤+⑥架构，拒绝采用。

### 方案三：仅通过测试或场景补丁规避

- 优点：改动小。
- 缺点：无法关闭生产 fail-open 与第二事实源，拒绝采用。

## 详细设计

### Capability 单一事实源

删除生产 8-ID 常量和集合相等校验。Registry 启动时逐合同校验 Formal identity、唯一性、slot 合法性、adapter、physical action、物理实现和版本。当前恰好 8 个 ID 只由测试与审计冻结。

### Rear-state fail closed

DECELERATE 将 `SURROUNDING_OBJECT_STATE` 从 recommended 移到 mandatory；BRAKE 保持不变。普通 rear rule 仅覆盖 DECELERATE/BRAKE：证据类型缺失由通用 mandatory gate 阻断；节点存在但字段缺失、null、布尔、非法类型、NaN/Inf 时专用 rule HIT；有效距离低于阈值或 validation rear conflict 时 HIT；有效安全距离且无冲突时 MISS。observed 记录 available/value/usable/threshold/conflict/failure_reason。

### AUTO_PARK 单一事实源

退休 `AUTOPARK_CRITICAL_EVIDENCE_REQUIRED` 和 `_autopark_critical`。SafetyGate 不再读取 RuntimeSafetyContext camera/ultrasonic。AUTO_PARK 四项 mandatory 保持不变；当前 FREE_SPACE 无 canonical producer，因此由通用 mandatory gate BLOCK。capability contract 继续只表达物理能力。

### Registry-driven area consistency

区域表达只从 Registry `area_catalog.semantic_frame_value/examples` 派生。删除 compact keyword 表。仅 AREA-bearing Intent 执行 guard：若命中已知区域表达但结果为 unknown，或解析区域不属于该 Intent allowed_areas，则语义进入 `REVIEW / AREA_MENTION_UNRESOLVED`，并在 EvidenceDemand 前终止。不推断、不降级、不将 unknown 视为 ALL。

### Multi-intent clarification

父轮次有多个稳定 Formal occurrences且因单命令协议 REVIEW 时，从不可变 `AuditRecord.semantic_frame.intents` 生成最多 4 个公共 ClarificationCandidate：冻结字段不变，`display_text=clause_text`，`candidate_source=SEMANTIC_REVIEW_CANDIDATE`。candidate ID 使用父 turn/audit identity、clause_index、intent_id、clause_text 的稳定摘要。

处理选择时读取持久化 ClarificationRequest 与父 Audit，使用同一算法重算所有 occurrence ID；必须唯一匹配，否则 fail closed。选中后只取原 clause_text，创建新 child turn并调用完整 `process_text()`；`confirmed=False`。父 intent_id 仅用于候选审计，child intent 必须由真实 SemanticOrchestrator 重新产生。

### TRUNK 边界

仅运行五条真实自然语言并记录 Top8、三路召回、3B、Guard 与最终 intent。若失败且需要 Anchor 变更，停止该子项并报告。

## 数据流与失败边界

自然语言 → SemanticOrchestrator → area consistency → semantic terminal 或 EvidenceDemand → HNSW/Recall/Resolution → SafetyGate → Decision → capability → Authorization/Token → PRE_EXECUTION_CHECK → translator → Adapter。

任何缺失、不可用、歧义、候选不唯一、canonical identity 或 capability 不匹配均 fail closed。no-execution 场景核对 VehicleState 前后完全一致；执行场景核对具体字段变化。

## 测试策略

1. 修改前用隔离数据库、真实 `process_text()` 建立机器可读基线。
2. 单元层验证 capability、rear predicate、area helper。
3. 集成层验证 Demand/Recall/Gate/Token/Execution。
4. E2E 黄金矩阵全部从自然语言开始；允许执行时继续真实消费 Token并检查状态。
5. 输出前后 JSON、workflow chain、active rule reachability、Stage4/Stage5 回归、compileall、diff check、git status。

## 停止条件

严格采用任务中列出的六项停止条件。尤其不修改冻结 Anchors、不发明 FREE_SPACE schema、不改变前端公共候选合同。
