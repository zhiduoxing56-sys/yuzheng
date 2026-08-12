# Phase5 最终收口修复设计

## 目标与冻结边界

只修复人工验收确认的四项问题：`non_driver_control` 的可信授权事实来源、后置约束污染 aggregate、assessment 正常路径的 union 决策复算、active frontend Phase4/5 contract 残留。Phase1–Phase4、公式、阈值、配置、Memory/Causal、授权/执行协议、数据库和 hash 全部冻结。

## 设计

- `non_driver_control` 继续按 occurrence 精确匹配 `intent_authorizations`，但仅为该 evaluator 注入 canonical turn-level `AUTHORIZATION_STATE`；其他 mixed evaluator 仍只使用 occurrence-owned evidence。
- `aggregate_safety_decision` 只来自 `IntentSafetyAssessment` 的固定保守聚合。Voice、Zone、Semantic REVIEW 和 multi-intent execution constraint 只影响 `final_decision`。
- 有 assessment 时，Pipeline 直接从 assessments 投影顶层 `DecisionResult`；无 assessment 才构造诊断性 turn-level decision。score 字段取最低分 occurrence，sources 合并 aggregate-worst occurrences，gate 保持现有 turn-level gate。
- active frontend contract 删除已废弃的 node/subgraph 字段，添加 Phase4 binding/resolution、demand-item similarity 与 direct response 的 Phase5 决策字段；消费方只读取绑定或 demand 级 similarity，不从物理 node 反推。

## 测试

覆盖 trusted-driver / per-occurrence authorization、PASS+BLOCK、Voice/Zone aggregate 分离、Ccov/Ctrust 隔离、顶层 provenance、单意图 parity 与 active frontend contract。
