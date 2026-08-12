# SYS-014 Stage 4C-A.2 RBT3 exp002 设计说明

## 背景与目标

exp001 的训练流水线正确，但 AMBIGUOUS abstention 和 negation 能力不足。exp002 作为从原始 RBT3 重新初始化的受控对照实验，只改变 discriminative learning rate 与 multi-task loss 权重，不修改冻结数据、runtime、模型结构、质量分数或 safety gates。

## 现状与约束

- 原始模型固定为 `hfl/rbt3@0aa0527ff4170f29e1dfd3eb6ef60dc67e1bf75c`。
- 使用冻结 `sys014-poc7-v2` 的 Train/Validation；禁止 Test 与 Safety Gold inference。
- exp001 全部只读；exp002 不得从其 checkpoint 续训。
- batch、长度、epoch、warmup、weight decay、gradient clip、seed 与 class weight policy 保持不变。

## 方案对比

### 方案一：隔离 runner + trainer 可选扩展（采用）

- 优点：复用已验证训练循环；exp001 默认参数路径不变；exp002 artifact 和选择逻辑完全隔离。
- 缺点：trainer 需要新增可选参数组分支。

### 方案二：在 exp002 中复制训练循环

- 优点：对 trainer 无改动。
- 缺点：训练实现分叉，后续验证和维护风险更高。

### 方案三：重构通用实验框架

- 优点：长期扩展性较好。
- 缺点：改动面超出有限安全优化范围。

## 推荐方案

采用方案一。`Stage4CTrainer` 仅在同时提供 backbone/head LR 时启用两个参数组；未提供时保持 exp001 原始单组 AdamW 行为和返回结构。exp002 使用独立 runner，启动前通过 dry validation 后再创建实验目录和执行训练。

## 详细设计

### 架构与关键组件

1. Trainer 扩展：互斥、无遗漏地划分 backbone 与五个 joint heads；scheduler 管理两组 LR；逐 step 返回两组 LR 日志。
2. Exp002 preflight：验证目录不存在、Train/Validation/manifest 哈希、原始模型初始化、参数组覆盖和预测 schema；只做 inference-mode forward。
3. Validation evaluator：逐 epoch 保存全部 probability、margin、slots、raw executable/abstain，并计算冻结质量和 safety 指标。
4. 专项追踪：0731/0732/0733、七条 negation 错例及五条用户提供的 ACCELERATE forward probes。
5. Checkpoint selector：先按 frozen safety gate 判 eligibility，再按 quality 选 best；non-eligible 使用批准的四级 closest 排序。
6. Reporter：生成训练总结和 exp001 对照，明确两个策略同时变化，不能宣称单因素因果。

### 数据流

原始 RBT3 + 冻结 Train → safety-focused loss 训练 → 冻结 Validation 完整预测 → frozen metrics/gates → best 或 closest diagnostic → last → exp001 对照报告。

### Closest 排序

只在 non-eligible epochs 中按以下 tuple 升序：

1. failed safety gate count；
2. AMBIGUOUS + MULTI false accept 总数；
3. total unsafe false accepts；
4. `-PRIMARY_QUALITY_SCORE`。

closest 始终 `BEST=false`、`DEPLOYABLE=false`，不得参与 eligible best 选择。

### 异常与边界处理

- exp002 已存在、哈希不符、参数组重叠/遗漏、初始化疑似来自 exp001、预测 schema 不完整时，训练前停止。
- non-finite loss/gradient 时停止训练并保留已生成诊断，不运行后续数据集。
- 若始终无 eligible，跑满 10 epochs，保存 closest 与 last；不自动 exp003/ELECTRA。
- 若有 eligible，仅连续三个 epoch 无更高 eligible quality 后 early stop。

### 测试策略

- 对 trainer 默认单组路径做兼容断言，并对 exp002 双组做互斥、覆盖、初始 LR 与 scheduler 断言。
- preflight 只允许 forward，不执行 backward 或参数更新。
- 正式训练后核对 optimizer steps、逐 epoch预测文件数量、checkpoint SHA 和选择规则。
- 核对 Test/Safety Gold 执行标志均为 NO，runtime 与冻结 Train/Validation 哈希不变。

## 风险与待确认项

- discriminative LR 与 loss weighting 同时变化，只能说明联合策略与结果相关，不能证明单一因素因果。
- 五条 ACCELERATE 文本是用户指定的离线 probes，不进入 loss 或 frozen metric。
