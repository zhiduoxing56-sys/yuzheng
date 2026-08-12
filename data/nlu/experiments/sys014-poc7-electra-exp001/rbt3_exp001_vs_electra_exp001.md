# RBT3 exp001 vs ELECTRA exp001

## 可比性

- 冻结数据、seed、max length、batch、单 LR、loss/class weights、quality score 与 safety gates：`True`
- COMPARISON_SEED_MATCH=`YES`
- Test evaluation：未执行
- Safety Gold evaluation：未执行

## Validation reporting checkpoint

| 指标 | RBT3 exp001 | ELECTRA exp001 |
|---|---:|---:|
| reporting epoch | 5 | 10 |
| checkpoint kind | closest safety diagnostic | ELIGIBLE_BEST |
| PRIMARY_QUALITY_SCORE | 0.939701 | 0.763731 |
| intent macro F1 | 1.000000 | 0.982073 |
| scope macro F1 | 0.899824 | 0.631215 |
| structure macro F1 | 0.978782 | 0.978214 |
| slot span F1 | 0.905263 | 0.246753 |
| NEGATED F1 | 0.829268 | 0.978723 |
| raw UFAR | 0.034483 | 0.034483 |
| MULTI false accepts | 0 | 0 |
| AMBIGUOUS false accepts | 1 | 0 |

## 运行画像上下文

Stage 4A 的原始预训练 encoder CPU P95：RBT3 约 `7.883 ms`，ELECTRA-small 约 `14.785 ms`。这些数字不是本次微调模型的端到端运行时，不能直接当作部署时延。

## 工程解读

- ELECTRA exp001 通过冻结 safety gates；RBT3 exp001 因 1 个 AMBIGUOUS false accept 未通过。
- ELECTRA 的 intent 与 negation head 表现良好，但整体质量分低于 RBT3，主要差距来自 scope 与 slot。
- ELECTRA slot overall F1 为 `0.246753`，VALUE F1 为 `0.000000`。模型并非全部预测 O，但属于严重 slot 欠拟合，应作为 backbone 路线决策的主要负面证据。
- ELECTRA UNKNOWN_CONTROL recall 为 `0.000000`，并将 0748 错误判为可执行；通过当前冻结 gate 不等于不存在所有安全误放。

## 决策状态

- ELECTRA_EXP001_SAFETY_GATE_PASS=`YES`
- ELECTRA_EXP001_BASELINE_HEALTHY=`YES`
- BACKBONE_COMPARISON_READY=`YES`
- READY_FOR_STAGE_4C_MODEL_DECISION=`YES`

## 附录：RBT3 exp002

RBT3 exp002 属于有限安全优化实验，采用不同 loss weights 与 discriminative LR，不进入本表的同协议 baseline 主比较。
