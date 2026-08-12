# SYS-014 RBT3 exp002 训练总结

## 训练与选择

- device：`CPU`；epochs：`10`；steps：`370`。
- backbone/head LR：`1e-05` / `5e-05`。
- reporting checkpoint：`CLOSEST_SAFETY_DIAGNOSTIC` epoch `5`。
- best eligible epoch：`None`。

## Validation

- Intent/Scope/Structure Macro F1：`0.971939` / `0.496835` / `0.978214`。
- Slot Span F1：`0.490066`。
- Negation F1 / NEGATED Recall：`0.956522` / `0.916667`。
- RAW UFAR：`0.103448`；AMBIGUOUS/MULTI false accepts：`0` / `0`。

## 冻结标志

```text
RBT3_EXP002_SAFETY_GATE_PASS=NO
RBT3_EXP002_NEGATION_IMPROVED=YES
BEST_CHECKPOINT_SAVED=NO
TEST_EVALUATION_EXECUTED=NO
SAFETY_GOLD_EVALUATION_EXECUTED=NO
READY_FOR_STAGE_4C_NEXT_DECISION=YES
```

本阶段没有修改 runtime、冻结数据或 safety gates，没有启动 ELECTRA。
