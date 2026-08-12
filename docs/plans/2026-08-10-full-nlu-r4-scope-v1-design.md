# Full NLU R4 高精度 Scope 映射器设计说明

## 背景与目标

本阶段仅为 Full NLU 金数据构建生成可审计候选，不承担在线 NLU 泛化任务。以冻结的 `intent_registry_r4_final.yaml` 为唯一最终语义权威，对 20,899 条初筛样本执行正确率优先的确定性试运行，并把 test 原始编号 226、251 作为额外隔离审计记录纳入 20,901 审计口径。本轮不得训练、不得自动修复复核项、不得宣布最终 Gold。

## 输入与硬边界

唯一允许读取并作为本轮标签证据的输入为当前 SHA256 已核验的五个文件：冻结 R4 Registry、初筛 JSONL、train/dev/test 三个 MAC JSONL。旧 mapping、旧 Registry、旧 PoC、旧 checkpoint、其他历史语义文件均不得读取为标签依据。旧 baseline 仅作为初筛记录中的审计字段保留，不参与 Scope 或 Intent 判断。

所有 Python 命令固定使用 `D:\software\anaconda\envs\yuzheng311\python.exe`。

## 方案对比

### 方案一：确定性证据规则编译器（采用）

- 优点：每个自动候选均可解释、可复现；可严格执行 R4 合同和边界；不依赖相似度猜测。
- 缺点：覆盖率保守，部分 Intent 会明确处于“仅复核”或“暂无自动规则”。

### 方案二：完整文本模板白名单

- 优点：误判风险最低。
- 缺点：只能识别几乎完全一致的句式，复核量过大，无法有效利用已有结构化 MAC 证据。

### 方案三：统计或语义相似度映射

- 优点：覆盖率高。
- 缺点：违反“禁止猜测和最近匹配”，不适用于安全链金数据构建。

## 推荐架构

新增两个独立脚本：

- `scripts/full_nlu/build_r4_scope_dryrun_v1.py`：输入硬校验、规则编译、关联、映射、路由、统计及产物写入。
- `scripts/full_nlu/validate_r4_scope_dryrun_v1.py`：从产物外部重读并验证数量守恒、Schema、证据、合同、规则和哈希。

所有产物写入 `outputs/full_nlu_r4_scope_v1/`，不修改冻结 Registry，也不触碰工作区既有改动。

## 数据流

1. SHA256 硬门：任一输入不符立即停止，且不写部分正式产物。
2. Registry 校验：顶层版本、71 Intent、四种 Scope、合同引用和特殊边界完整。
3. MAC 关联：严格使用“原始文件 + 原始编号”，并要求 screen 原始文本与 raw query 完全一致。
4. Source route：冲突默认隔离，损坏排除，边界候选默认复核。
5. 子句恢复：保持顺序；split 只能在可定位且顺序一致时作为辅助边界。无法可靠对齐且可能含 Formal 时进入复核。
6. Formal 判定：动作、对象、排除条件、语气、槽位与合同均必须有原文证据；高风险动作采用更严格门槛。
7. Scope 判定：Formal 失败后只在车辆本地控制证据明确时进入 Bypass；NON_CONTROL 仅接受明确非控制；UNKNOWN_OOD 仅接受明确域外或未知，不作为模糊样本兜底。
8. 输出路由：AUTO_CORE_CANDIDATE、BOUNDARY_REVIEW、SEMANTIC_REVIEW、SOURCE_QUARANTINE、MALFORMED_EXCLUDED。
9. 统计与 manifest：20,899 是映射流水线口径，20,901 是含两条 UNSCREENED_SOURCE_ROW 的审计口径；额外两条不参与任何覆盖率、Scope、Formal 或自动接受率统计。

## 自动规则原则

71 个 Formal Intent 都必须有规则条目，但规则状态允许为 `AUTO_ENABLED`、`REVIEW_ONLY` 或 `NO_RELIABLE_SOURCE_SAMPLE`。不得为填满覆盖率而创造同义词、扩展普通车控语义或使用最近匹配。

自动 Formal 候选必须保存：规则编号、动作证据、对象证据、每个槽位的原文值与字符区间、语气证据、辅助 MAC 证据、排除条件检查结果和合同检查结果。缺少任一必要解释字段即不得自动接受。

## 异常与边界处理

- `SOURCE_CONFLICT_REVIEW` → `SOURCE_QUARANTINE`。
- `DROP_MALFORMED` → `MALFORMED_EXCLUDED`。
- `TRUE_BOUNDARY_CANDIDATE` → 默认 `BOUNDARY_REVIEW`，即使生成候选标签也不进入自动核心。
- test 226、251 → `UNSCREENED_SOURCE_ROW`，仅进入隔离审计。
- 模糊、证据不足、Scope 不唯一 → `SEMANTIC_REVIEW`，不得自动写成 UNKNOWN_OOD。
- 明确域外或未知且文本完整 → 才可自动标记 UNKNOWN_OOD。

## 统计分类

覆盖不足与映射失败必须分开：

- `NO_RELIABLE_SOURCE_SAMPLE`：当前授权语料没有可靠源样本。
- `SEMANTIC_MAPPING_FAILED`：存在相关语料，但规则无法唯一裁决。
- `CONTRACT_CHECK_FAILED`：映射明确，但槽位或合同异常。

统计还须覆盖四类 Scope、Formal 自动/复核/隔离、71 Intent 明细、合同完整性、单/多意图、语气、槽位、混合 Scope、失败原因、source conflict、unscreened rows 和每条 rule_id 命中数。

## 测试与验收

验证器必须断言：

- 五个输入哈希与 manifest 完全一致；
- 20,899 个 screen 样本恰好出现一次，三个主输出互斥且数量守恒；
- quarantine 另含且只含两条 UNSCREENED_SOURCE_ROW，审计总数为 20,901；
- 额外两条不进入映射统计分母；
- Formal Intent 仅来自当前 71 个 ID；
- 每个自动 Formal 子意图都有 rule_id、实际触发证据、原文定位和合同通过记录；
- Bypass 不含 Formal 专属字段；
- UNKNOWN_OOD 没有被用作模糊样本兜底；
- 规则文件恰有 71 条 Formal 规则，且允许零自动规则；
- 统计把无可靠源样本、语义映射失败、合同检查失败分开；
- 产物 SHA256 可复现并写入 manifest。

## 已知风险

仅依靠冻结 Registry 与当前 MAC 语料构建确定性规则，自动覆盖率可能显著低于旧流程。这是本阶段允许且预期的结果；质量判断以可解释性和误接受防护为先。
