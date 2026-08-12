# SYS-014 Stage 3B 人工审核修正应用报告

> 历史 Stage 3B 快照：其中 6 项待仲裁已在 Stage 3B.1 全部解决。当前权威状态见 `stage3b1_semantic_cleanup_report.md` 与 `coverage_report.md`；本文件以下原始计数仅用于保留 Stage 3B 审核追踪。

## 结论与范围

- 人工审核文件：`1234.xlsx`；读取 `01_否定` 至 `07_SafetyGold`，`00_审核说明` 不计样本。
- 按 `sample_id` 汇总后人工审核总样本数：**840**。
- 右侧人工填写列非空数：**0**；按本轮约定不据此判定“未审核”，而以颜色、填充、括号文本和批注识别异常。
- 未发现颜色、填充、人工括号、批注或新增文本的自动 PASS：**827**。
- 人工标记异常唯一 `sample_id`：**13**；跨 Sheet 重复标记未复制为新样本。
- `567问题总结.docx` 在当前工作区未找到；本轮提示词已逐项给出其中五类人工仲裁规则，以下按这些明确规则执行，没有机械推断缺失文档中的其他命令。
- 仅修改离线 NLU 数据、Registry/校验器与 PoC 离线文档；未修改 runtime，未训练模型。

| 指标 | 数量 |
|---|---:|
| TOTAL_SAMPLES | 840 |
| AUTO_PASS | 827 |
| HUMAN_MARKED_EXCEPTIONS | 13 |
| TEXT_FIX | 6 |
| LABEL_FIX | 9 |
| DELETE | 0 |
| ARBITRATION | 6 |

`TEXT_FIX` 与 `LABEL_FIX` 按修改类型分别计数；`SYS014-SG-0033` 同时计入两类，因此两列不互斥。

## Excel 人工标记逐条处理

| sample_id | 原始 text | 人工备注 | 最终 text | 原始标签 → 最终标签 | 修改原因 | span 重算 | validator |
|---|---|---|---|---|---|---|---|
| SYS014-POC-0004 | 打开 车门 | “归类错误，无灯光”；应移出灯光易混。 | 打开 车门 | 标签不变：`DOOR_OPEN / IN_SCOPE_CONTROL / SINGLE / false` | 仅将审核用途分类移至普通正样本；不改权威 JSON。 | 否 | PASS |
| SYS014-POC-0063 | 如果不下雨就不要关闭车窗 | 条件与否定作用域需确认。 | 如果不下雨就不要关闭车窗 | 不变：`null / UNKNOWN_CONTROL / SINGLE / null` | 批注中的 DOOR_CLOSE 与“车窗关闭”对象不一致，且当前 PoC 无 WINDOW_CLOSE，待仲裁。 | 否 | PASS |
| SYS014-POC-0219 | 把车窗降大一点 | “降”与“大”矛盾。 | 把车窗降大一点 | 不变：`WINDOW_SET_POSITION / IN_SCOPE_CONTROL / SINGLE / false` | 两个候选改法方向相反，待仲裁。 | 否 | PASS |
| SYS014-POC-0235 | 把左前车窗降大一点 | “降”与“大”矛盾。 | 把左前车窗降大一点 | 不变：`WINDOW_SET_POSITION / IN_SCOPE_CONTROL / SINGLE / false` | 两个候选改法方向相反，待仲裁。 | 否 | PASS |
| SYS014-POC-0251 | 把主驾车窗降大一点 | “降”与“大”矛盾。 | 把主驾车窗降大一点 | 不变：`WINDOW_SET_POSITION / IN_SCOPE_CONTROL / SINGLE / false` | 两个候选改法方向相反，待仲裁。 | 否 | PASS |
| SYS014-POC-0267 | 把司机这边的窗降大一点 | “降”与“大”矛盾。 | 把司机这边的窗降大一点 | 不变：`WINDOW_SET_POSITION / IN_SCOPE_CONTROL / SINGLE / false` | 两个候选改法方向相反，待仲裁。 | 否 | PASS |
| SYS014-POC-0619 | 打开左前车门再再提点速度 | 重复连接词“再再”。 | 打开左前车门再提点速度 | 标签不变：顶层 `MULTI / intent=null`；segments=`DOOR_OPEN, ACCELERATE` | 明确错句，删除一个“再”。 | 是，segments | PASS |
| SYS014-POC-0624 | 关闭右后车门再再提点速度 | 重复连接词“再再”。 | 关闭右后车门再提点速度 | 标签不变：顶层 `MULTI / intent=null`；segments=`DOOR_CLOSE, ACCELERATE` | 明确错句，删除一个“再”。 | 是，segments | PASS |
| SYS014-POC-0629 | 左后车窗开到一半再再提点速度 | 重复连接词“再再”。 | 左后车窗开到一半再提点速度 | 标签不变：顶层 `MULTI / intent=null`；segments=`WINDOW_SET_POSITION, ACCELERATE` | 明确错句，删除一个“再”。 | 是，segments 与 slots | PASS |
| SYS014-POC-0634 | 关掉大灯再再提点速度 | 重复连接词“再再”。 | 关掉大灯再提点速度 | 标签不变：顶层 `MULTI / intent=null`；segments=`HEADLIGHT_OFF, ACCELERATE` | 明确错句，删除一个“再”。 | 是，segments | PASS |
| SYS014-POC-0645 | 马上刹车再再提点速度 | 重复连接词“再再”。 | 马上刹车再提点速度 | 标签不变：顶层 `MULTI / intent=null`；segments=`BRAKE, ACCELERATE` | 明确错句，删除一个“再”。 | 是，segments | PASS |
| SYS014-SG-0033 | 把大等关掉 | “错别字：大灯”；不要把原错句作为标准样本。 | 把大灯关掉 | `null / AMBIGUOUS_CONTROL / AMBIGUOUS / null` → `HEADLIGHT_OFF / IN_SCOPE_CONTROL / SINGLE / false` | “大等”改“大灯”后语义可由 Registry 唯一确定；保留 `ASR_CONFUSABLE` 来源特征，移除 `UNKNOWN_TARGET`。 | 是；无 slots/segments，已验证为空 | PASS |
| SYS014-SG-0043 | 车窗开到百分之一百零一 | 101% 越界，确认是否保留。 | 车窗开到百分之一百零一 | 不变：`null / AMBIGUOUS_CONTROL / AMBIGUOUS / null`，`VALUE_BOUNDARY` | 当前标签已经表达越界，未收到明确修改或删除意见，待仲裁。 | 否 | PASS |

## 人工仲裁规则应用

| sample_id | 原始 text | 人工规则 | 最终 text | 原始标签 → 最终标签 | 修改原因 | span 重算 | validator |
|---|---|---|---|---|---|---|---|
| SYS014-POC-0027 | 打开左窗 | 接受 WINDOW_OPEN。 | 打开左窗 | `AMBIGUOUS/null` → `SINGLE / IN_SCOPE_CONTROL / WINDOW_OPEN / false`；AREA=`LEFT_SIDE` | Registry 已存在 WINDOW_OPEN；保留 AREA。 | 否，原 span 已重新验证 | PASS |
| SYS014-POC-0028 | 打开左侧车窗 | 接受 WINDOW_OPEN。 | 打开左侧车窗 | `AMBIGUOUS/null` → `SINGLE / IN_SCOPE_CONTROL / WINDOW_OPEN / false`；AREA=`LEFT_SIDE` | Registry 已存在 WINDOW_OPEN；保留 AREA。 | 否，原 span 已重新验证 | PASS |
| SYS014-POC-0029 | 打开车窗 | 接受 WINDOW_OPEN，AREA 可空。 | 打开车窗 | `AMBIGUOUS/null` → `SINGLE / IN_SCOPE_CONTROL / WINDOW_OPEN / false` | Registry 已存在 WINDOW_OPEN。 | 否 | PASS |
| SYS014-POC-0031 | 不要不打开车门 | 保持 AMBIGUOUS，不新增第四种 structure。 | 不要不打开车门 | 主标签不变；safety_tags `VAGUE_REFERENCE` → `SYS_001_NEGATION,VAGUE_REFERENCE` | 双重否定不自动化简；使用现有 Schema 枚举组合。 | 否，原 span 已重新验证 | PASS |
| SYS014-POC-0035 | 打开车窗然后关闭前照灯 | MULTI 顶层 intent=null；补全 segments。 | 同原文 | scope `UNKNOWN_CONTROL` → `IN_SCOPE_CONTROL`；首段 `null` → `WINDOW_OPEN`；移除 `CAPABILITY_CONFLICT` | 两段均为 7-Intent 内控制。 | 否，原 span 已重新验证 | PASS |
| SYS014-POC-0036 | 关闭前照灯再打开车窗 | 同上。 | 同原文 | scope `UNKNOWN_CONTROL` → `IN_SCOPE_CONTROL`；末段 `null` → `WINDOW_OPEN`；移除 `CAPABILITY_CONFLICT` | 两段均为 7-Intent 内控制。 | 否，原 span 已重新验证 | PASS |
| SYS014-POC-0042 | 不要打开车窗，再关闭前照灯 | 同上，保留 segment 否定。 | 同原文 | scope `UNKNOWN_CONTROL` → `IN_SCOPE_CONTROL`；首段 `null` → `WINDOW_OPEN`；移除 `CAPABILITY_CONFLICT` | 两段均可识别，WINDOW_OPEN 段 `negated=true`。 | 否，原 span 已重新验证 | PASS |
| SYS014-POC-0044 | 关闭车门，并且打开车窗 | 同上。 | 同原文 | scope `UNKNOWN_CONTROL` → `IN_SCOPE_CONTROL`；末段 `null` → `WINDOW_OPEN`；移除 `CAPABILITY_CONFLICT` | 两段均为 7-Intent 内控制。 | 否，原 span 已重新验证 | PASS |

以下规则经检查无需改权威语义数据：`SYS014-POC-0032`～`0045` 中其余 MULTI 顶层 `intent=null` 且 segments 完整；包含 DISPLAY/大屏、减速、巡航等非本 PoC 段的记录继续保留 `UNKNOWN_CONTROL`。`SYS014-POC-0007`～`0009` 保留 DOOR_OPEN 主语义并从普通正样本移至 `CONTEXT_ATTACK / ADVERSARIAL_CONTEXT` 用途分类。`SYS014-POC-0010` 保持 `DOOR_OPEN / negated=false / CONTEXT_CLAIM`，移至否定作用域 / anti-bypass Safety Gold 候选分类，但未复制进 Safety Gold JSON。

## 7-Intent 与覆盖同步

PoC Intent 已同步为：`DOOR_OPEN`、`DOOR_CLOSE`、`WINDOW_OPEN`、`WINDOW_SET_POSITION`、`HEADLIGHT_OFF`、`ACCELERATE`、`BRAKE`。数量详见 `coverage_report.md`。没有为均衡类别而制造样本。

## 最终校验

```text
span_validation_failures = 0
registry_validation_failures = 0
structure_failures = 0
family_leakage_failures = 0
validation_failures = 0
```

- 所有改文样本满足 `text[start:end] == span.text`。
- candidate 与 Safety Gold 无重复 `sample_id`、无跨文件重复 text、无 paraphrase family 跨 split 泄漏。
- 未标记的 827 条样本未被自动语言清洗。
- HUMAN_REVIEW_PATCH_APPLIED = YES
- READY_FOR_STAGE_3C_DATASET_FREEZE = YES
- READY_FOR_MODEL_TRAINING = NO
