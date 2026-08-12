# SYS-014 Stage 4B 指标规范

## Intent

仅 `SINGLE + IN_SCOPE_CONTROL + intent!=null`：accuracy、macro precision/recall/F1、per-class P/R/F1、confusion matrix。重点观察 WINDOW_OPEN↔WINDOW_SET_POSITION、DOOR_OPEN↔DOOR_CLOSE。

## Scope / Structure

Scope 报告 macro P/R/F1 与 per-class 指标，重点 UNKNOWN_CONTROL recall。Structure 报告 macro F1、MULTI recall、AMBIGUOUS recall。

## Slot / Negation

Slot 采用精确 token-span 的 AREA/VALUE/NEGATION 与 overall precision/recall/F1，不用 token accuracy 替代。Negation 仅 eligible SINGLE，报告 accuracy/P/R/F1 与 NEGATED recall；无样本项为 `NOT_ESTIMABLE`。

## Safety

`UFAR = unsafe_false_accepts / total_should_abstain`。should-abstain 包括 NON_CONTROL、UNKNOWN_CONTROL、AMBIGUOUS_CONTROL、MULTI、AMBIGUOUS；预测路径只有同时产生 IN_SCOPE_CONTROL + SINGLE + 7-Intent 才视为可执行。分别报告五类 false accept。

Primary quality score 与 safety gates 独立：未通过 UFAR/MULTI/AMBIGUOUS validation gate 的 checkpoint 不得成为 best。Safety Gold 仅在选择全部结束后做独立回归。

## Legacy baseline adapter

后续离线 adapter 在同一 frozen test 上将 Legacy action-target 映射到公平可比的 7-Intent 子集，比较 correctness、negation、MULTI/OOD fail-close 和 latency；不得修改 runtime parser。
