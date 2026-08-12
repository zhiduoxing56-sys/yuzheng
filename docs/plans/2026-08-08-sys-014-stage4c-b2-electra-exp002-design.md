# SYS-014 Stage 4C-B.2 ELECTRA exp002 设计

## 背景与目标

ELECTRA exp001 已通过冻结 safety gates，但 Slot overall F1 仅 0.246753，VALUE F1 为 0。Stage 4C-B.1 已排除实现、投影和标签映射 Bug，并将问题诊断为 VALUE 类塌缩与明显 O 偏置。本实验只验证 Slot 内部 class weighting 能否改善 token task，同时保持 exp001 的安全性与其他任务质量。

## 冻结边界

- 从 Stage 4A 固定的原始 `hfl/chinese-electra-180g-small-discriminator@826a243f...e924` 全新初始化 backbone 与五个 heads。
- 数据保持 `sys014-poc7-v2`，manifest SHA256 保持不变。
- seed、单 optimizer group、LR、scheduler、batch、max length、task loss weights、checkpoint score 和 safety gates 全部与 ELECTRA exp001 相同。
- 唯一有意变量：Slot class-weight policy 从 `NONE` 改为 `SQRT_INVERSE_FREQ_CAP_3`，以及该策略对应的 7 类向量。
- Test、Safety Gold、runtime、frozen data 均不可触碰。

## 方案选择

采用独立 `stage4c_electra_exp002.py`。不重构或动态覆盖 exp001 runner，避免改变已验收实验行为。中立的数据、loss、trainer 和评估函数可复用；exp002 自己负责 config diff、Slot token artifact、验收阈值和 checkpoint 语义。

## Preflight

正式 backward 前必须完成：

1. exp002 目录不存在，数据与模型 provenance 正确。
2. 从 B.1 结构化资产读取 7 类权重，并与 Train distribution 的确定性重算结果一致；全部权重在 `(0, 3]`。
3. `exp001_vs_exp002_config_diff.json` 仅包含 `slot_class_weight_policy` 与 `slot_class_weight_vector`。
4. 单 optimizer group 完整覆盖全部 trainable parameters，LR 为 `2e-5`。
5. 使用混合 O/VALUE synthetic batch，证明 multitask Slot CE 实际等于 weighted CE、且不同于 unweighted CE。
6. 一次真实 Validation forward+loss 验证 shape/schema；参数不变、无梯度、训练步骤为 0。

## 训练与 artifact

最多训练 10 epochs。每 epoch 保存完整 Validation predictions，包括各句级 head 概率/margin、gold/pred spans、原始 token-level Slot gold/pred labels、raw executable/abstain。同步记录四类 Slot span 指标、VALUE token 数、O rate、19 条 VALUE 状态、Scope/0731/negation 专项及全部 safety counts。

Eligible checkpoint 仍只由冻结 safety gates 决定；eligible 内仍按冻结 PRIMARY_QUALITY_SCORE 选择 best。closest 不得绕过 gates，所有 checkpoint 均为 `DEPLOYABLE=false`。

## exp002 验收

相对 ELECTRA exp001 的 selected eligible best：

- safety gates 全部通过；
- Overall Slot F1 > 0.246753 且 VALUE F1 > 0；VALUE F1 >= 0.50 仅为 diagnostic target；
- Intent、Scope、Negation F1 下降均不超过 0.03；Structure F1 下降不超过 0.02；IN_SCOPE_CONTROL recall 下降不超过 0.03。

这些阈值只适用于本次单变量消融，不推广为永久模型门槛。

## 输出与停止

输出完整实验目录、best/closest/last、`electra_exp001_vs_exp002.md` 及最终验收字段。完成后停止，不启动 exp003、RBT3、MacBERT、Test 或 Safety Gold。
