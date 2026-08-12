# 第二阶段冻结记录：32 类标准 Evidence Type

## 冻结结论

第二阶段在现有 32 类标准 Evidence Type、Evidence Runtime Contract 与安全边界实现上冻结。后续阶段不得为恢复旧 Stage4 正向场景而修改 `SemanticFrame`、`SemanticIntent`、`EvidenceDemand`、`IntentEvidenceDemand`、冻结语义编排器或本阶段的 Evidence Runtime Contract；只有发现可复现的明确缺陷时才允许重新开启冻结范围。

本次收口没有进入 71 Intent Evidence Demand Registry，没有修改证据类型、Evidence Demand 规则、HNSW 算法、质量公式、Memory、Causal 或最终 Decision 公式，也没有建立临时正向场景、兼容层或回退路径。

## Stage4 过期基线登记

以下用例保留原文件和原断言，作为 Stage4 历史行为基线，不再作为第二阶段冻结门禁：

1. `backend/tests/stage4/test_stage4_api_realtime.py::test_state_scenario_audit_timeline_and_restart_apis`
   - 历史假设：`parked_open_door` 在旧需求结构下返回 `PASS` 并签发授权令牌。
   - 当前行为：最终 Evidence Demand 契约按强制证据 fail-closed，裁决为 `BLOCK`。
   - 取代原因：旧用例验证的是迁移前的正向场景结果，不再代表当前 Evidence Demand 契约。

2. `backend/tests/stage4/test_stage4_freeze_realtime_security.py::test_adapter_execution_failure`
   - 历史假设：前置开门请求必定 `PASS`，因此测试能够取得非空授权令牌后进入适配器失败分支。
   - 当前行为：前置请求被当前 Evidence Demand 契约阻断，不签发令牌；旧适配器执行断言因而不可达。
   - 取代原因：该用例的入口条件由旧证据需求决定，不能通过降低当前强制证据要求或伪造正向场景恢复。

这两个用例不增加 `skip`、`xfail` 或修改后的期望值；其失败保持可见，以免把历史基线误报为现行契约通过。第二阶段验收以第二阶段定向契约测试、API 信任边界测试、Pipeline 测试、冻结语义测试和机械检查为准。

## 不可达生产代码收口

删除 `EvidenceRepository.latest_usable()`。全仓调用扫描确认该方法只有定义、没有生产或测试调用；当前 Mandatory Recall 的唯一仓库解析入口是 `latest_resolved()`，删除不改变运行时证据选择、可用性判定或 fail-closed 行为。

## 冻结边界

第二阶段冻结后，以下内容保持不变：

- 32 类标准 Evidence Type 及其 runtime mapping、value schema、usability 与安全分类唯一来源。
- 正式命令 API 与内部 `TrustedRuntimeContext` 的信任边界。
- `RuntimeSafetyContext` 与 EvidenceNode 的隔离边界。
- 当前第三阶段前唯一 Evidence Demand 规则源。
- 第一阶段已冻结的语义和 Evidence Demand 数据契约。

