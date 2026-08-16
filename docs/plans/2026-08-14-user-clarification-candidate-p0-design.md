# User Clarification Candidate P0 收口设计

## 背景与目标

当前 `SemanticOrchestratorV2.review_candidates` 实际承载 Stage1 `fused_top8`。它经由 `SemanticFrame` 被 `ClarificationService` 直接转换为面向用户的候选，导致高召回内部候选可能改变用户已明确表达的动作、对象或槽位。

本次目标是在不改动 Stage1、Registry、anchor、模型、HNSW、Evidence、SafetyGate、Decision、Authorization、Execution 和 Audit DB/hash 的前提下，建立 ClarificationService 唯一的用户候选语义边界。

## 现状与约束

- `review_candidates` 可继续用于技术诊断，但不是用户候选事实来源。
- 用户候选仅允许来自 ASR N-best/文本纠错、已解析的语义歧义和 slot completion。
- 用户候选必须保留当前已解析 SemanticFrame/SemanticIntent 中的 resolved 信息；不得重新解析 raw text 推断约束。
- 前端仅展示后端 `ClarificationRequest.candidates`，不做候选语义判断。

## 方案对比

### 方案一：ClarificationService 唯一边界（采用）

- 切断 `frame.review_candidates` 到用户候选的直接消费。
- 在 ClarificationService 对允许来源统一执行 canonical compatibility filtering、canonical dedup、rank、truncate。
- 对候选确认后的 child turn 验证语义 identity；不一致时保持 REVIEW 并阻止后续授权/执行。

优点：完整封住本次 P0 路径，改动集中在候选出口与回归测试。

### 方案二：仅断开 review_candidates

优点：改动最小。缺点：其他候选来源未被统一约束，不能形成长期边界。

### 方案三：扩展公开候选 schema

优点：契约最显式。缺点：扩大 API、前端、审计兼容范围，不符合本次最小修复范围。

## 详细设计

### 用户候选来源

ClarificationService 仅构造以下来源：

1. `ASR_NBEST`：语音确认使用原始 N-best 文本。
2. `TEXT_SIMILARITY`：仅作为低 ASR 置信度的文本纠错来源，不取 Stage1 Top8。
3. `SEMANTIC_REVIEW_CANDIDATE`：仅使用已经在 SemanticFrame 中解析出的正式 intent occurrence 或 Interpreter 中已验证的 canonical candidate。
4. `SLOT_COMPLETION`：仅细化 unresolved/coarse area；连续 value 缺失不生成数值。

`frame.review_candidates` 不进入以上任一来源。

### 兼容性与去重

候选先映射为当前系统可表达的 canonical identity，再按当前 SemanticFrame 已解析信息检查：

- action/action direction 与已解析 action 相同或兼容；
- object family 与已解析 target 相同；
- exact area 不可变，coarse area 仅可细化为允许子区域；
- 已解析 value、mode、direction 不可变；
- runtime identity 保留。

处理顺序固定为：候选源池 → compatibility filter → canonical identity 去重 → 保持来源排序 → 最多 4 条。display text 只用于展示，不承担去重语义。

### 确认闭环

候选确认只提交 `clarification_id` 和 `candidate_id`。服务端从已保存 ClarificationRequest 取回候选文本并创建 child turn；完成后比对 child SemanticFrame 的 canonical identity 与所选候选承诺。若不一致，child 保持 REVIEW、记录 `CLARIFICATION_REPARSE_MISMATCH`，且不得产生可执行后续状态。

### 测试策略

- 构造 REVIEW 场景，证明 `WINDOW_CLOSE` 即使位于 Stage1 Top8 也不会成为“打开车窗”的用户候选。
- 覆盖 CLOSE/OPEN、LOCK/UNLOCK、前照灯开关、对象跨族、精确/粗粒度 area、OOD 和缺失连续 value。
- 执行 100 条代表表达式的用户可见候选污染统计，四项 mismatch rate 均为 0。
- 保留并执行 Stage1/冻结语义回归，证明 Top8 未被修改。
