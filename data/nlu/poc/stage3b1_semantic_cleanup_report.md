# SYS-014 Stage 3B.1 PoC 最终语义收尾报告

> 历史 Stage 3B.1 快照：Stage 3C 已在此基础上应用最后修正并创建不可变 `sys014-poc7-v1`。当前状态见 `coverage_report.md` 与冻结目录中的 manifest/split/leakage 报告。

## 结果

- Stage 3B 基线：candidate 780 + Safety Gold 60 = **840**。
- 删除：**10** 条；新增 WINDOW_OPEN：**80** 条。
- Stage 3B.1 最终：candidate 850 + Safety Gold 60 = **910**。
- 未执行 train/validation/test split，未训练模型，未修改 runtime。

## 仲裁清零

| sample_id | 处理 |
|---|---|
| SYS014-POC-0063 | 保持 `UNKNOWN_CONTROL / SINGLE / intent=null`，继续作为 7-Intent 外的条件 + 否定边界。 |
| SYS014-POC-0219 | 删除：“把车窗降大一点”为模板方向冲突。 |
| SYS014-POC-0235 | 删除：“把左前车窗降大一点”为模板方向冲突。 |
| SYS014-POC-0251 | 删除：“把主驾车窗降大一点”为模板方向冲突。 |
| SYS014-POC-0267 | 删除：“把司机这边的窗降大一点”为模板方向冲突。 |
| SYS014-SG-0043 | 改为 `WINDOW_SET_POSITION / IN_SCOPE_CONTROL / SINGLE / false`；VALUE span 保持“百分之一百零一”，`canonical_value=101%`、`normalization_status=INVALID`，保留 `ood_label=BOUNDARY` 与 `VALUE_BOUNDARY`。 |

REMAINING_ARBITRATION = **0**。

## 模板清理

最小自然语言修复：

| sample_id | 原 text | 最终 text |
|---|---|---|
| SYS014-POC-0438 | 快点赶紧刹住 | 赶紧把车刹住 |
| SYS014-POC-0450 | 快点马上制动 | 马上踩刹车 |
| SYS014-POC-0468 | 快点立即刹住 | 立即刹车 |
| SYS014-POC-0688 | 再快一点点？，可以吗 | 再快一点点，可以吗 |
| SYS014-POC-0736 | 刹一下那个？，可以吗 | 刹一下那个，可以吗 |

删除可能污染行车 BRAKE 的“停车制动”模板：`SYS014-POC-0477`～`0482`，共 **6** 条。

## Scope 一致性

以下“明确控制动作 + 外域对象”从 `NON_CONTROL / OPEN_DOMAIN` 修正为 `UNKNOWN_CONTROL / CAPABILITY_CONFLICT`：

- `SYS014-POC-0742` 打开冰箱
- `SYS014-POC-0743` 启动火箭
- `SYS014-POC-0744` 把电脑关掉
- `SYS014-POC-0750` 把手机调成静音
- `SYS014-POC-0754` 打开客厅的灯
- `SYS014-POC-0755` 把电视关掉
- `SYS014-POC-0756` 启动洗衣机

天气、论文、打电话、信息和娱乐请求保持 `NON_CONTROL`。

## Safety Gold

- `SYS014-SG-0033` 恢复为“把大等关掉”，保持 `HEADLIGHT_OFF / IN_SCOPE_CONTROL / SINGLE / false / ASR_CONFUSABLE`，仅用于不进入训练的鲁棒性测试。
- `SYS014-SG-0043` 的意图与越界参数分离：NLU 语义确定，确定性 CapabilityValidator 可依据 `101% / INVALID` 拒绝。

## WINDOW_OPEN 补齐

- 新增 positive SINGLE：**57**，与原 3 条合计 **60**。
- 新增 negated SINGLE：**15**，合计 **15**。
- 新增 MULTI mentions：**8**，与原 4 次合计 **12**。
- 覆盖无 AREA、`LEFT_FRONT`、`RIGHT_FRONT`、`LEFT_REAR`、`RIGHT_REAR`、`FRONT_ROW`、`REAR_ROW`、`LEFT_SIDE`、`RIGHT_SIDE`、`ALL`。
- 所有 WINDOW_OPEN 样本均无 VALUE；带“一半”“30%”等绝对开度的文本仍属于 WINDOW_SET_POSITION。
- 新增记录全部为 `SYNTHETIC_TEMPLATE`，使用多个正向、否定与 MULTI paraphrase family；未切分数据。

## 校验

```text
candidate_records = 850
safety_gold_records = 60
total_records = 910
span_validation_failures = 0
registry_validation_failures = 0
structure_failures = 0
family_leakage_failures = 0
validation_failures = 0
```

```text
REMAINING_ARBITRATION = 0
WINDOW_OPEN_DATA_SUFFICIENT = YES
POC_SEMANTIC_DATA_CLEAN = YES
READY_FOR_STAGE_3C_DATASET_FREEZE = YES
READY_FOR_MODEL_TRAINING = NO
```
