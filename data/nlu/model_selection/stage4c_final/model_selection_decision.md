# SYS-014 Stage 4C-C Validation 模型决策审计

## 决策

推荐 `PATH_SELECT`：冻结 ELECTRA exp002 epoch 9 为 `PROVISIONAL_FINAL_MODEL`。它通过 Stage 4B 冻结 safety gates，并且是所有 frozen-eligible 候选中综合质量最高、Slot 修复最完整的 checkpoint。历史 `ELECTRA_EXP002_PASS=NO` 保持不变；该字段只表示本次 Slot-weighting 单变量消融没有满足额外的 Sentence Negation 退化上限，不是 Stage 4B 永久候选禁入规则。

冻结对象：

- Model: `hfl/chinese-electra-180g-small-discriminator`
- Experiment: `sys014-poc7-electra-exp002`
- Epoch: `9`
- Checkpoint SHA256: `dc2670a0351a219f71ba728f805242393769af8c1564bc4eb3f224f795444f68`（已与实际 `model_state.pt` 重新核验一致）
- `DEPLOYABLE=false`：Test、Safety Gold、runtime integration 均未完成。

## 三种“通过”的语义

- `FROZEN_SAFETY_GATE_PASS`：只检查 UFAR ≤ 0.05、MULTI FA=0、AMBIGUOUS FA=0。
- `EXPERIMENT_ABLATION_PASS`：ELECTRA exp002 单变量实验附加的相对退化与 Slot 改善验收；其历史结果为 NO。
- `FINAL_MODEL_CANDIDATE_ELIGIBLE`：按冻结 Stage 4B 协议，先过 safety gates，再进入 PRIMARY_QUALITY_SCORE 比较；不等于 deployable。

冻结设计文档和原始 checkpoint selection 实现都采用 `SAFETY_GATES_PASS + PRIMARY_QUALITY_SCORE`。未发现“后续消融失败即永久失去候选资格”的规则。因此 `FROZEN_PROTOCOL_REQUIRES_ABLATION_PASS_FOR_MODEL_CANDIDACY=NO`。

## 四实验统一矩阵

FA A/M/U/N 分别表示 AMBIGUOUS、MULTI、UNKNOWN_CONTROL、NON_CONTROL false accepts。Stage 4A CPU P95 是原始 pretrained encoder 的画像，不是微调后端到端 runtime 延迟。

| Experiment | Epoch/kind | Intent | Scope | Structure | AREA | VALUE | NEG span | Slot | Sent Neg F1 | Neg recall | Quality | UFAR | FA A/M/U/N | Frozen | Exp pass | Params | Stage4A CPU P95 ms | Train s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|---:|---:|---:|
| RBT3 exp001 | 5/CLOSEST_SAFETY_DIAGNOSTIC | 1.000000 | 0.899824 | 0.978782 | 0.917431 | 0.864865 | 0.909091 | 0.905263 | 0.829268 | 0.708333 | 0.939701 | 0.034483 | 1/0/0/0 | NO | NO | 38494487 | 7.883200 | 143.352148 |
| RBT3 exp002 | 5/CLOSEST_SAFETY_DIAGNOSTIC | 0.971939 | 0.496835 | 0.978214 | 0.666667 | 0.173913 | 0.137931 | 0.490066 | 0.956522 | 0.916667 | 0.780257 | 0.103448 | 0/0/1/2 | NO | NO | 38494487 | 7.883200 | 88.648936 |
| ELECTRA exp001 | 10/ELIGIBLE_BEST | 0.982073 | 0.631215 | 0.978214 | 0.333333 | 0.000000 | 0.129032 | 0.246753 | 0.978723 | 0.958333 | 0.763731 | 0.034483 | 0/0/0/1 | YES | YES | 12286487 | 14.784640 | 137.837766 |
| ELECTRA exp002 | 9/ELIGIBLE_BEST | 0.991063 | 0.733175 | 1.000000 | 0.890909 | 0.842105 | 1.000000 | 0.908163 | 0.933333 | 0.875000 | 0.918920 | 0.034483 | 0/0/1/0 | YES | NO | 12286487 | 14.784640 | 89.699016 |

RBT3 exp001/exp002 的展示行均为 closest safety diagnostic，不是 eligible best。RBT3 两实验使用同一 joint architecture，其 38,494,487 参数量取自 exp002 的现有参数分组 artifact；ELECTRA 两实验的 12,286,487 取自 exp001 summary。

## ELECTRA exp002 Sentence Negation 复核

Validation negated support 为 24；epoch 9 的 false negatives 共 3 条：

- `SYS014-POC-0563` — 不要再提点速度；intent=`ACCELERATE`；sentence `NEGATED → NOT_NEGATED`；NEGATED probability=`0.491741`；gold span=`不要[0:2]`；pred span=`不要[0:2]`；Slot signal exact=`YES`；raw executable=`YES`。
- `SYS014-POC-0564` — 别再提点速度；intent=`ACCELERATE`；sentence `NEGATED → NOT_NEGATED`；NEGATED probability=`0.367724`；gold span=`别[0:1]`；pred span=`别[0:1]`；Slot signal exact=`YES`；raw executable=`YES`。
- `SYS014-POC-0567` — 请勿再提点速度；intent=`ACCELERATE`；sentence `NEGATED → NOT_NEGATED`；NEGATED probability=`0.479807`；gold span=`请勿[0:2]`；pred span=`请勿[0:2]`；Slot signal exact=`YES`；raw executable=`YES`。

三条的 NEGATION Slot span 均与 gold 精确一致，所以 `SENTENCE_NEGATION_FN_WITH_CORRECT_SLOT_SIGNAL=3`。这是诊断事实，不构成本阶段修改 runtime 或加入 OR 融合的授权。对照 ELECTRA exp001 epoch 10 有 1 条 Sentence Negation FN（`SYS014-POC-0849`），且该条没有正确的 NEGATION Slot signal。

## UNKNOWN_CONTROL 风险

Validation 中 UNKNOWN_CONTROL support 仅 1。`SYS014-POC-0773`（“打开危险警示灯”）被预测为 IN_SCOPE_CONTROL，UNKNOWN_CONTROL recall=`0.000000`，raw executable=`YES`。单样本指标统计稳定性极弱，故 `UNKNOWN_CONTROL_RESULT_STATISTICALLY_FRAGILE=YES`；该风险没有被忽略，也没有在本阶段通过修改 gate 掩盖。

## ELECTRA exp002 全 epoch 审计

| Epoch | Frozen | Quality | Intent | Scope | Structure | Slot | VALUE | NEG span | Sent Neg F1 | UFAR | FA A/M/U/N |
|---:|:---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | NO | 0.187719 | 0.039752 | 0.440741 | 0.297258 | 0.007634 | 0.000000 | 0.000000 | 0.266667 | 0.862069 | 7/17/1/0 |
| 2 | NO | 0.217328 | 0.294498 | 0.237805 | 0.295977 | 0.000000 | 0.000000 | 0.000000 | 0.222222 | 1.000000 | 9/17/1/2 |
| 3 | NO | 0.552597 | 0.665150 | 0.237805 | 0.664566 | 0.590164 | 0.727273 | 0.583333 | 0.545455 | 0.689655 | 5/12/1/2 |
| 4 | NO | 0.748646 | 0.833535 | 0.365741 | 0.877934 | 0.880829 | 0.800000 | 0.916667 | 0.736842 | 0.344828 | 3/4/1/2 |
| 5 | NO | 0.817177 | 0.896961 | 0.463520 | 1.000000 | 0.943590 | 0.888889 | 1.000000 | 0.666667 | 0.103448 | 0/0/1/2 |
| 6 | NO | 0.873217 | 0.973628 | 0.631215 | 1.000000 | 0.923077 | 0.864865 | 1.000000 | 0.702703 | 0.068966 | 0/0/1/1 |
| 7 | NO | 0.873716 | 0.973628 | 0.631215 | 1.000000 | 0.892308 | 0.864865 | 1.000000 | 0.769231 | 0.068966 | 0/0/1/1 |
| 8 | YES | 0.900696 | 0.973628 | 0.715585 | 1.000000 | 0.912821 | 0.864865 | 1.000000 | 0.829268 | 0.034483 | 0/0/1/0 |
| 9 | YES | 0.918920 | 0.991063 | 0.733175 | 1.000000 | 0.908163 | 0.842105 | 1.000000 | 0.933333 | 0.034483 | 0/0/1/0 |
| 10 | YES | 0.912864 | 0.982602 | 0.715585 | 1.000000 | 0.908163 | 0.842105 | 1.000000 | 0.933333 | 0.034483 | 0/0/1/0 |

冻结 gate 合格 epoch 为 8、9、10。epoch 9 与 10 的 Sentence Negation F1 都是 0.933333、Slot F1 都是 0.908163，但 epoch 9 的 PRIMARY_QUALITY_SCORE 更高（0.918920 vs 0.912864）；epoch 8 的 Negation 更差。不存在 Sentence Negation 更好且仍 frozen-eligible 的其它 epoch。

## Validation 重复使用风险

风险评级为 `HIGH`。同一 Validation（129 条；should-abstain 29；negated 24；UNKNOWN 1）已经用于 RBT3 baseline 判断、RBT3 safety-focused 调整、backbone 对比和 ELECTRA Slot weighting 调整。若继续专门针对 0563/0564/0567 做 exp003，相当于针对已反复查看的 3 个 Validation 样本调参，产生明显 selection/overfitting 风险。当前问题集中在 3 条，且 Slot Head 均保留正确否定信号；仅为满足 0.03 消融数字再次调参的证据不足。

## 最终字段

```text
FROZEN_PROTOCOL_REQUIRES_ABLATION_PASS_FOR_MODEL_CANDIDACY=NO
ELECTRA_EXP002_EXPERIMENT_PASS=NO
ELECTRA_EXP002_FROZEN_SAFETY_ELIGIBLE=YES
ELECTRA_EXP002_MODEL_CANDIDATE_ELIGIBLE=YES
ELECTRA_EXP001_NEGATION_FALSE_NEGATIVE_COUNT=1
ELECTRA_EXP002_NEGATION_FALSE_NEGATIVE_COUNT=3
SENTENCE_NEGATION_FN_WITH_CORRECT_SLOT_SIGNAL=3
UNKNOWN_CONTROL_VALIDATION_SUPPORT=1
UNKNOWN_CONTROL_RESULT_STATISTICALLY_FRAGILE=YES
VALIDATION_REUSE_RISK=HIGH
RECOMMENDED_NEXT_PATH=PATH_SELECT
PROVISIONAL_FINAL_MODEL=hfl/chinese-electra-180g-small-discriminator
PROVISIONAL_FINAL_EXPERIMENT=sys014-poc7-electra-exp002
PROVISIONAL_FINAL_EPOCH=9
PROVISIONAL_FINAL_CHECKPOINT_SHA256=dc2670a0351a219f71ba728f805242393769af8c1564bc4eb3f224f795444f68
STAGE_4C_MODEL_DECISION_AUDIT_COMPLETE=YES
TRAINING_STEPS_EXECUTED_THIS_STAGE=0
TEST_EVALUATION_EXECUTED=NO
SAFETY_GOLD_EVALUATION_EXECUTED=NO
```

本阶段未训练、未做 forward inference、未执行 Test 或 Safety Gold，未修改 runtime、frozen dataset、safety gates 或任何历史实验状态。
