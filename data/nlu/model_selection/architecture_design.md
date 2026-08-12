# SYS-014 LocalJointNLUModel 架构与 Stage 4B 训练设计

## 联合模型

输入 raw ASR/text，经单个轻量 Transformer encoder 产生 sentence/token 表示：

- Scope Head：`IN_SCOPE_CONTROL / NON_CONTROL / UNKNOWN_CONTROL / AMBIGUOUS_CONTROL`。
- Structure Head：`SINGLE / MULTI / AMBIGUOUS`。
- Intent Head：仅 eligible 的 `SINGLE + IN_SCOPE_CONTROL` 预测冻结 7 Intent；其余样本 loss masked。
- Slot Head：BIO `AREA / VALUE / NEGATION`；训练时从权威 raw character span 动态投影。
- Sentence Negation Head：仅 eligible 样本监督 boolean，作为冗余信号；不得替代 token span 或 SafetyTextGuard。

禁止 action/target 独立分类器，禁止 UNKNOWN/OTHER Intent 软最大值类别。Context attack 继续由 deterministic context scanner + AdvancedValidation 处理。

## 推理门控

只有 `scope=IN_SCOPE_CONTROL && structure=SINGLE` 才允许考虑 Intent 输出。NON_CONTROL、UNKNOWN_CONTROL、AMBIGUOUS_CONTROL、MULTI、AMBIGUOUS 一律 abstain/fail closed。后续仍须经过 Deterministic Normalizer、SafetyTextGuard、VehicleCapabilityValidator 和既有安全链路。

## MULTI / AMBIGUOUS / OOD

MULTI 只监督 Structure=MULTI，Intent masked；slot 可继续学习。segments 仅作离线诊断，不实现 token-level sub-intent segmentation。AMBIGUOUS 监督 Structure，三类 scope abstention 监督 Scope；均不得被硬塞入 7 Intent。

## Loss 设计

Stage 4B 可采用共享 encoder 上的 masked multi-task objective：scope CE + structure CE + eligible intent CE + 有效 token slot CE + eligible sentence-negation CE。各项权重只能通过 validation 与安全约束设计；Safety Gold 不参与训练或权重/阈值选择。

## Confidence / Abstention

保留 scope confidence、structure confidence、intent top1、top1-top2 margin、slot span/min confidence 与 negation confidence。训练完成后只用 validation 做 calibration/阈值设计，不采用任意 `top1 < 0.5` 规则。Safety Gold 仅作独立安全回归。

## Stage 4B 指标

- Intent：eligible 样本 accuracy、macro precision/recall/F1、per-class F1。
- Scope：macro F1、per-class recall，重点 UNKNOWN_CONTROL recall。
- Structure：macro F1，重点 MULTI/AMBIGUOUS recall。
- Slot：AREA/VALUE/NEGATION span-level precision/recall/F1，不以 token accuracy 代替。
- Negation：eligible SINGLE accuracy/F1；无 negated 样本的 split × intent 标记 `NOT_ESTIMABLE`。
- Safety：`UNSAFE_FALSE_ACCEPT_RATE = unsafe abstention cases incorrectly released as executable 7-Intent / all unsafe abstention cases`。

## Legacy baseline

在完全相同 test set 比较 Legacy SemanticFrameParser 与 Future Local NLU 的 Intent/action-target correctness、negation、MULTI fail-close、UNKNOWN/OOD fail-close 和 latency。本阶段不修改 Legacy Parser。

## 安全边界

`TRAINING_STEPS_EXECUTED = 0`。本报告只定义未来训练；Stage 4A 不执行 backward、optimizer、scheduler、epoch 或 checkpoint。
