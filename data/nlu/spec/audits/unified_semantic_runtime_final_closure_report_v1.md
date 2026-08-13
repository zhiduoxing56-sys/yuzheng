# 149 统一语义空间第④阶段最终冻结报告

日期：2026-08-12

## 最终结论

`FRAGRANCE_SET_SCENT` 阻断已经按照人工产品裁决解除。第④阶段统一语义空间正式冻结完成，可进入第⑤阶段 SafetyGate canonical identity 迁移。

## 人工重分类

当前唯一 Known freeze 为 `known_non_executable_semantic_freeze_final_v4.yaml`。v2/v3 仅保留历史审计，不再由 production builder 读取。

`FRAGRANCE_SET_SCENT` 精确恢复：

- `Q3-00030`：给我换个其它口味的香氛试试
- `Q3-00032`：香氛给我更换一个味道

两条均标记为 `HUMAN_REVIEW_RECLASSIFIED_FROM_QUARANTINE`，保留原 quarantine ID、原 provenance、原隔离原因和人工裁决原因。其 active anchor count 为 2，`freeze_readiness=READY`，`anchor_sufficiency=SUFFICIENT_HUMAN_RECLASSIFIED`。

两条表达不在 `FRAGRANCE_SET_LEVEL` active anchors 中。`香氛位置调到2`、`香氛位置调到3` 继续 REVIEW，原因是 `FRAGRANCE_LEVEL_OR_SCENT_AMBIGUOUS`；`打开香氛适中` 继续隔离。

## 最终资产统计

- Formal：71
- Known Non-Executable：78
- Total：149
- Formal anchors：1426
- Known anchors：2145
- 统一生产 anchors：3571
- Security anchors：20
- Product removed intents active：0/13
- 未批准哈希候选使用：0/1402
- 跨 Intent 标准化 active overlap：0
- 未批准 quarantine provenance 回流：0
- 精确人工重分类例外：2

## Registry 与启动校验

生产 Registry、Cards、Anchors 已由 v4 freeze 重新派生，运行时 freeze manifest 哈希已同步。所有 value/mode/direction/conditional/value-mapping contract 引用均可解析；149 个 Intent 均至少有一个 active anchor；Registry/Cards/Anchors ID 集及 canonical identity 一致。

自动验收报告 `unified_semantic_runtime_migration_audit_v1.json` 的全部检查通过。

## 真实端到端结果

- `紧急刹车` → `EMERGENCY_BRAKE / FORMAL`，进入正式 Evidence/Safety 下游。
- `打开运动模式` → `DRIVING_MODE_SET / SPORT / KNOWN_NON_EXECUTABLE / PASS`，无 EvidenceDemand 下行。
- `切换驾驶模式` → `REVIEW / MISSING_REQUIRED_MODE`，语义层终止。
- 两条人工重分类香氛表达 → `FRAGRANCE_SET_SCENT` candidate，因 `MISSING_REQUIRED_VALUE` 为 REVIEW，未归入 `FRAGRANCE_SET_LEVEL`。
- `香氛位置调到2/3` → `REVIEW / FRAGRANCE_LEVEL_OR_SCENT_AMBIGUOUS`。
- `香氛浓度调到2级` → `FRAGRANCE_SET_LEVEL`，value=2。

## 下游零调用与生命周期

spy 测试确认纯 Known、Semantic REVIEW 和 NO_MATCH 路径均在 EvidenceDemand embedding 前终止：embedding、HNSW、Mandatory Recall、graph、memory、causal、validation、SafetyGate、Decision 和 Authorization 调用数均为 0；Known/Review turn 的 begin/complete 均为 1:1。

## 工程边界确认

本轮没有重新清洗其他 Known anchors，没有修改其他 Intent 语义合同，也没有修改 SafetyGate、Decision、Authorization、Token 或 Execution。车辆执行支持唯一事实仍为 `config/authorization.yaml::executable_actions`，没有从 `runtime_identity=FORMAL` 推导执行资格。
