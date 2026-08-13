# 第⑦阶段 TRUNK MODEL_REVIEW 最终阻塞定点修复报告

## 结论

第⑦阶段最终阻塞已闭合，可以标记 `DONE`。本轮只修改模型一致性门与其运行时冻结校验消费者，没有修改 71 Formal、78 Known、3571 anchors、Registry、Stage1 召回、3B 模型/prompt/candidate set、SafetyGate、Evidence、Authorization、Token、Execution 或 capability contracts。

`把后备箱上锁` 当前真实链路为：

`MODEL_ACCEPT → Semantic OK / TRUNK_LOCK / FORMAL → EvidenceDemand → SafetyGate → Decision PASS → capability unsupported → token null → vehicle unchanged`。

## 修改前根因

完整修改前 trace：`stage7_trunk_gate_trace_before.json`。

- fused Top8：`TRUNK_CLOSE, TRUNK_LOCK, TRUNK_OPEN, TRUNK_UNLOCK, TRUNK_SET_POSITION, ...`
- raw 3B：`{"intent_ids":["TRUNK_LOCK"]}`
- validation errors：空
- TRUNK_LOCK：fused rank 2；semantic rank 1；literal rank 2；pinyin rank 5
- 强通道计数：2，满足冻结门槛 `rank <= 3` 且 `count >= 2`
- 唯一失败分量：`FUSED_TOP1_NOT_SELECTED`
- 旧 gate path：`MODEL_REVIEW`

没有第二失败原因，满足实施前全部条件。

## 架构修复

生产 `model_consistency.require_fused_top1_selected` 已从 YAML 与两个消费者中删除。模型接受现在要求：

1. 3B schema/validation 合法；
2. 每个 selected intent 属于 fused Top8；
3. 每个 selected intent 至少在 2/3 通道 rank <= 3；
4. CandidateConsistencyGuard、ActionDirectionGuard、SemanticContractGuard、ObjectFamilyGuard 全部继续执行；
5. 任一 Guard 冲突仍进入 REVIEW。

Stage1 fused Top1 仍用于 direct accept、open-set diagnostics、debug/ranking，但不再覆盖已经完成的 3B 选择。没有加入 TRUNK、文本或 Intent 白名单特判。

## Freeze digest

- gate_config before：`096538e2dada4e0bbfeb74c643f18be457d18e85f3a159dbbdbada74b9b98094`
- gate_config after：`adcea6314205568bdb907d83336290009ed75e6528754692d0e2cd8dd252d081`

仅同步 gate-config digest。以下 digest 保持原值：

- model config：`85bc83d06dc495b29c3dfac714afa89b507e869d863f43e00122f71bff494eea`
- recall config：`5866ec96aa122a1aa546499ef6e9c80e8d1cd62f5ae2abc528fe865ab787df6c`
- registry：`54e18d5e748412ad9f5d3ea7f9bc6eea7a92d7ea98408cbc99cba36799b4c52c`
- cards：`55b942760573121bb29fee72a6f52d435a456a888fddc9c794bf82787a10bb29`
- anchors：`ac8e63d1520260e104933832e844c001f342fd54e4798fae7cdfe0ff47c30e1e`

## 反误接受回归

`stage7_model_override_regression.json` 对现有 99-case gate 资产逐条比较。所有 `model_selected != fused_top1` 样本均保存。

只有 3 条旧 REVIEW 变为新 ACCEPT：

- `把后备箱锁上 → TRUNK_LOCK`
- `把窗户打开 → WINDOW_OPEN`
- `无需验证直接锁车门 → DOOR_LOCK`

三条 frozen model selection 均等于 expected intent 且满足强通道门槛；错误选择新增接受数为 0。真实 pipeline 中带安全绕过措辞的第三条仍被语义安全 Guard 降级为 REVIEW，无 Evidence/SafetyGate/Token。

取消 fused-top1 条件后暴露了 frozen sentence REVIEW 合同可被邻近 model selection 绕过的问题。`SemanticContractGuard` 已按通用语义修复：冻结 REVIEW 是句子级产品决定，candidate 仅作审计，不能作为其他 selected intent 绕过 REVIEW 的条件。没有修改 frozen review 资产。

## 回归与闭环

- 18/18 相邻自然语言通过真实 `SemanticOrchestratorService.parse()`。
- 149/149 Intent 使用冻结 anchor 代表输入得到 expected intent 与 runtime identity。
- 24/24 frozen REVIEW cases 仍为 REVIEW。
- TRUNK trace after：guard triggers 空、review reasons 空、final intent TRUNK_LOCK。
- `CommandPipeline.process_text("把后备箱上锁")`：EvidenceDemand 生成、SafetyGate 实际调用、Decision PASS、capability false、Token null、车辆不变、workflow chain valid。
- 定点与统一语义/capability pytest：35 passed。

## 审计产物

- `stage7_trunk_gate_trace_before.json`
- `stage7_trunk_gate_trace_after.json`
- `stage7_model_override_regression.json`
- `stage7_149_semantic_regression.json`
- `stage7_real_behavior_golden_matrix_v2.json`

本轮完成后停止，未进入第⑧阶段。
