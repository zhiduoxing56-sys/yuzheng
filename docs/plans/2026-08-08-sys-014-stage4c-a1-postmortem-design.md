# SYS-014 Stage 4C-A.1 安全误放诊断设计

## 背景与目标

RBT3 exp001 完成 10 个 epoch，但 epoch 5 因 `SYS014-POC-0731` 被同时预测为 `IN_SCOPE_CONTROL / SINGLE / ACCELERATE`，未通过冻结的 AMBIGUOUS 零误放门。本阶段只做根因诊断与 Validation 离线 abstention 验证，不训练、不修改 runtime、冻结数据或安全门。

## 现状与约束

- exp001 保存逐 epoch 指标和 last checkpoint，没有合格 best checkpoint。
- 现有 runtime 在 `semantic_rules.yaml` 中配置 vague pronouns，由 `SemanticFrameParser` 消费。
- 只允许 last checkpoint 在 Validation 上执行 forward-only；Test 与 Safety Gold 不得读取或推理。
- 输出必须可复现，并明确区分模型语义、模型 abstention 信号和确定性 guard。

## 方案对比

### 方案一：独立可复现诊断脚本（采用）

- 优点：证据链完整；能统一审计历史轨迹、last checkpoint 概率、guard 和 negation；可加入防训练、防越界断言。
- 缺点：需要新增少量离线脚本代码。

### 方案二：手工命令与临时分析

- 优点：文件改动少。
- 缺点：难以复现，容易遗漏边界或形成口径差异。

### 方案三：仅分析现有 JSON

- 优点：风险最低。
- 缺点：无法获得 last checkpoint 概率与置信度 tradeoff，不能完整验证 Strategy C。

## 推荐方案

新增独立 Stage 4C-A.1 脚本，只读取 exp001、冻结 Validation 和现有 runtime 规则。脚本通过 `torch.inference_mode()` 加载 last checkpoint，禁止构造 optimizer、调用 backward 或修改模型参数；所有输出仅写入 exp001 的 `postmortem/`。

## 详细设计

### 架构与关键组件

1. Artifact auditor：验证标签映射、历史指标、UFAR 公式、安全门配置及 epoch 5 错例。
2. Last-checkpoint diagnostic：生成 Validation 的 scope/structure/intent/negation 概率与 top1-top2 margin。
3. Runtime guard adapter：直接实例化现有 `SemanticFrameParser`，复用真实 YAML，模拟 fail-close，不修改 runtime。
4. Strategy evaluator：比较 raw argmax、现有 guard 和少量通用 confidence/margin 候选阈值。
5. Negation analyzer：对 Sentence Negation Head 与 NEGATION slot span 的一致性和语言模板聚类。
6. Report writer：生成要求的五份 JSON/Markdown 产物。

### 数据流

冻结 Validation + exp001 artifacts + last checkpoint + 当前只读规则
→ 完整性审计
→ forward-only 预测
→ 三策略统计与错例分析
→ postmortem 产物。

### 异常与边界处理

- epoch 5 未保存 logits 时明确标记不可恢复，不以 last checkpoint 概率代替。
- 若发现流水线、标签映射或 UFAR bug，停止策略推荐并报告。
- 若 parser 无法实例化或规则未被真实代码路径消费，Strategy B 标记不可估算。
- 所有 checkpoint 结果均标记 diagnostic-only，不生成 best/deployment checkpoint。

### 测试策略

- 静态检查脚本不包含 optimizer/backward/training 调用。
- 执行前后核对 checkpoint SHA256 与模型参数哈希不变。
- 记录且断言本阶段训练步数为 0。
- 记录实际输入文件并断言不含 Test 或 Safety Gold。
- 复算历史 UFAR 并与已保存指标交叉验证。

## 风险与待确认项

- 当前工作区有大量既有未提交修改；本阶段不提交 Git，仅新增诊断脚本、计划和 postmortem 文件。
- last checkpoint 是 epoch 10，不代表 epoch 5，不能用于恢复 epoch 5 confidence。
