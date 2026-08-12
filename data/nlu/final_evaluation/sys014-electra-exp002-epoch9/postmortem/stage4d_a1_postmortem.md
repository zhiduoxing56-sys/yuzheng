# SYS-014 Stage 4D-A.1 Locked Test 泛化失败根因审计

## 决策结论

Locked Test-v1 已打开且永久视为 burned。当前 ELECTRA exp002 epoch 9 的失败不是单一模型问题，而是 **split、覆盖、闭集 OOD 架构和局部训练目标共同形成的 MIXED 泛化失败**。frozen v2 不应修改，但也不再适合作为最终 safety-model selection 的权威 split。

- Validation UNKNOWN_CONTROL = 1/129 (0.775%)；Test = 29/133 (21.805%)。
- Test/Validation UNKNOWN count support 比为 29x，prevalence 比为 28.13x。
- Test UNKNOWN 29 条全部为 TEST_ASSET；Validation 唯一 UNKNOWN 为 SYNTHETIC_TEMPLATE。
- 17 条 UNKNOWN unsafe false accept 的 intent 映射：DOOR_OPEN=0, DOOR_CLOSE=0, WINDOW_OPEN=5, WINDOW_SET_POSITION=0, HEADLIGHT_OFF=7, ACCELERATE=2, BRAKE=3。
- MULTI 23 条中 20 条正确 abstain，3 条误放均集中在 mixed-polarity/compositional held-out families。
- 唯一 AMBIGUOUS 误放是双重否定，与 Validation 0731/0732/0733 的模糊指代 family 不同。
- Test VALUE 16 条中没有检测 miss，但 12 条是相对表达 span boundary error；因此 F1 从 Validation 0.842105 降至 Test 0.25。
- Sentence Negation 的 6 条 FN 全部是 WINDOW_SET_POSITION 同一 held-out split group，且 6/6 的 NEGATION Slot signal 正确。

## UNKNOWN split 根因

`UNKNOWN_SPLIT_IMBALANCE_ROOT_CAUSE = F (A + B + D)`：

1. A：零 family/template/mechanical leakage 要求使连接组不可拆分；重建后的跨 split group 数为 0。
2. B：TEST_ASSET group 先被强制分配到 Test，之后才做 group-aware balance；Validation 的 UNKNOWN 硬下限只有 1。
3. D：Test 被有意用作真实 TEST_ASSET stress distribution，29 条 UNKNOWN 全在 Test。

C 不是主因：全量有 54 条 UNKNOWN（Train/Val/Test = 24/1/29）。E 也没有证据：frozen assignments、split reports、leakage audit 与 group 重建结果一致。

## 架构与错误层级

`CLOSED_SET_INTENT_FORCING_RISK = YES`。Intent head 只有 7 个已知类，UNKNOWN 等标签在训练中被 mask；Scope 一旦将 unsupported SINGLE 错判为 IN_SCOPE_CONTROL，Intent head 必然吸附到某个已知 intent。

`OOD_REJECTION_SINGLE_POINT_OF_FAILURE = YES`。对普通 unsupported SINGLE，Structure 没有拒绝理由，Intent 又没有 reject 类，因此 Scope 是唯一直接 OOD 拒绝点。这是当前架构事实，不是本次审计发现的实现 bug。

| 问题层 | 评级 | 核心证据 |
|---|---|---|
| DATASET_SPLIT_PROBLEM | HIGH | Validation UNKNOWN support is 1 (0.775%) versus Test 29 (21.805%); forced TEST_ASSET groups were assigned before balancing. |
| DATA_COVERAGE_PROBLEM | HIGH | Validation undercovers unsupported capabilities, double-negation ambiguity, mixed-negation MULTI, and relative VALUE boundary families exposed by Test. |
| MODEL_CAPACITY_PROBLEM | MEDIUM | A small backbone may contribute, but the read-only evidence cannot isolate capacity; strong AREA and many MULTI results argue against capacity as the sole cause. |
| MULTITASK_ARCHITECTURE_PROBLEM | HIGH | Scope is the only direct reject signal for unsupported SINGLE commands, and six sentence-negation FNs coexist with correct Slot NEGATION signals. |
| CLOSED_SET_OOD_PROBLEM | HIGH | The seven-way intent head has no unknown/reject class and forces a known intent after a Scope false positive. |
| TRAINING_OBJECTIVE_PROBLEM | MEDIUM | No direct intent-level OOD rejection or sentence/slot consistency objective exists; however the dominant evidence remains split and coverage shift. |

## v2 数据集适用性

`CURRENT_V2_SPLIT_SUITABLE_FOR_FINAL_MODEL_SELECTION = NO`。

v2 的零泄漏目标达成，仍可保留为 PoC、回归和历史分析集；但 Validation UNKNOWN=1 使任何 UNKNOWN recall/UFAR 选择极不稳定，也不能代表 Test 的独立 capability families。因此不能继续把该 Validation 当作可靠的最终安全模型选择代理。

## NLU Development Cycle 2（仅设计，不执行）

1. Test-v1 只保留为 burned historical postmortem set；不得再宣称它是 unseen final test。
2. 建立新的 capability taxonomy 和独立 family 来源，冻结 Train-v3/Validation-v3/Test-v3。
3. 保持 family/template/mechanical/split_group leakage=0；Validation 至少 UNKNOWN 20、NON_CONTROL 15、AMBIGUOUS 15、MULTI 20，且 unique should-abstain 至少 70；Test 对应至少 30/20/20/30，unique should-abstain 至少 100。
4. Validation 每个安全子类至少 8 个独立 split groups，Test 至少 10--12 个；任一 family 不超过该安全子类的 20%。
5. 若类别支持与零泄漏冲突，优先零泄漏并新增独立 families；不得拆 family 凑数，也不得降低评估主张之外仍声称完整安全覆盖。
6. 数据与协议冻结后，才在新 Validation 上评估显式 OOD/reject 路径、intent-level reject objective、sentence-slot consistency 和同协议 backbone 对照。
7. Test-v3 在数据、协议、checkpoint 与选择全部冻结后只打开一次。

## Safety Gold

`SAFETY_GOLD_SHOULD_REMAIN_SEALED = YES`。普通 Locked Test 已明确失败，打开 Safety Gold 不会改变 `DEPLOYABLE=false`，只会消耗最后一个独立安全评估资产。

## Required final fields

```text
TEST_V1_BURNED = YES
UNKNOWN_VALIDATION_SUPPORT = 1
UNKNOWN_TEST_SUPPORT = 29
UNKNOWN_SPLIT_IMBALANCE_ROOT_CAUSE = F: A + B + D
CLOSED_SET_INTENT_FORCING_RISK = YES
OOD_REJECTION_SINGLE_POINT_OF_FAILURE = YES
GENERALIZATION_FAILURE_LEVEL = MIXED
CURRENT_V2_SPLIT_SUITABLE_FOR_FINAL_MODEL_SELECTION = NO
DATASET_SPLIT_PROBLEM = HIGH
DATA_COVERAGE_PROBLEM = HIGH
MODEL_CAPACITY_PROBLEM = MEDIUM
MULTITASK_ARCHITECTURE_PROBLEM = HIGH
CLOSED_SET_OOD_PROBLEM = HIGH
TRAINING_OBJECTIVE_PROBLEM = MEDIUM
SAFETY_GOLD_SHOULD_REMAIN_SEALED = YES
RECOMMENDED_NEXT_STAGE = NLU_DEVELOPMENT_CYCLE_2
TRAINING_STEPS_EXECUTED_THIS_STAGE = 0
SAFETY_GOLD_EVALUATION_EXECUTED = NO
```

本阶段未训练、未推理、未改 frozen v2/runtime/safety gate/threshold/checkpoint，也未读取 Safety Gold。
