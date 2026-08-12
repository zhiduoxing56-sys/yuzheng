# SYS-014 Stage 4A 模型候选选择与运行画像计划

> 状态：APPROVED / OFFLINE MODEL SELECTION / NO TRAINING  
> 日期：2026-08-08

## 目标与不可变边界

本阶段仅审计本机环境、比较三个已批准候选、验证 tokenizer/span 与联合任务头兼容性、测量 CPU 单条 forward 资源画像，并设计 Stage 4B 的训练和评价协议。

权威输入为 `data/nlu/poc/frozen/sys014-poc7-v2/`。不得修改 v1/v2、重新切分或生成训练样本；不得执行 backward、optimizer、scheduler、参数更新或 checkpoint；不得修改 runtime、Legacy Parser、SemanticFrame、安全门、授权、执行或审计链路。

## 候选方案

### 方案一：ELECTRA 轻量主选（采用）

- `hfl/chinese-electra-180g-small-discriminator` 作为默认轻量主候选。
- `hfl/rbt3` 作为浅层备用；若本机延迟或兼容性显著占优，可反转选择。
- `hfl/chinese-macbert-base` 只作 representation/resource upper-bound。
- 优点：遵循车载轻量部署目标，同时保留不同轻量架构对照。
- 缺点：Stage 4A 无训练准确率，选择只能基于架构、资源与兼容性。

### 方案二：RBT3 纯延迟优先

- 默认选择层数更少的 RBT3。
- 优点：可能获得更低 CPU 延迟。
- 缺点：未实测前不能证明整体部署收益，也不能推断准确率。

### 方案三：无句级否定头的极简联合模型

- 只使用 token NEGATION span 与确定性 SafetyTextGuard。
- 优点：参数与逻辑最少。
- 缺点：失去成本很低的句级冗余监督信号。

## 联合架构

`LocalJointNLUModel` 接收原始 ASR/text，使用单个 Transformer encoder。`[CLS]`/pooler 表示进入 Scope(4)、Structure(3)、Intent(7) 与可选 Sentence Negation(2) 线性头；序列表示进入 BIO Slot(7：O、B/I-AREA、B/I-VALUE、B/I-NEGATION) 头。

Intent loss 仅对 `SINGLE + IN_SCOPE_CONTROL` 有效。MULTI、AMBIGUOUS、NON_CONTROL、UNKNOWN_CONTROL、AMBIGUOUS_CONTROL 全部 mask。MULTI 的 segments 只用于离线诊断，运行时必须 fail closed。句级否定头仅作辅助信号，不能替代 NEGATION span 或 SafetyTextGuard。

## 数据与对齐

- latency 仅从 frozen validation/test 读取 `text`，不利用标签调模型或阈值。
- tokenizer 对齐从冻结标注读取 raw character span，动态投影为 BIO；raw offset 始终为权威来源。
- 至少检查 100 条并覆盖 AREA、VALUE、NEGATION、MULTI；记录所有不可映射、文本不一致、截断和特殊 token 冲突。
- 固定长度桶：short `<=8` 字符、medium `9..20`、long `>20`。

## 实测协议

- 使用 `D:\software\anaconda\envs\yuzheng311\python.exe`。
- 模型使用独立 cache，逐个加载到 CPU，`eval()` + `torch.inference_mode()`。
- batch size 1；每模型至少 20 次 warmup、至少 200 次正式 forward。
- 分离统计 tokenization、encoder forward、端到端；加载时间不进入延迟。
- 记录线程、CPU、RAM、CUDA、token length、参数、权重/分词器磁盘大小、RSS 增量及 mean/P50/P90/P95/P99/max。
- 随机初始化 profile-only joint heads，只验证张量形状、附加参数与 forward 开销，不训练。

## 版本与安全

缺失候选只允许下载到独立 Stage 4A cache。每个候选记录 Hugging Face revision/commit、license、config、vocab、weight 文件、SHA256 和本地路径。Evidence/HNSW encoder 不复用、不覆盖、不原地微调。

所有脚本必须不包含 optimizer、scheduler、backward 或训练循环。最终复核 `TRAINING_STEPS_EXECUTED = 0`，并重新验证 frozen v2 manifest/hash。

## Stage 4B 评价设计

- Intent：仅 eligible 样本的 accuracy、macro precision/recall/F1、per-class F1。
- Scope：macro F1、per-class recall，重点 UNKNOWN_CONTROL recall。
- Structure：macro F1，重点 MULTI/AMBIGUOUS recall。
- Slot：AREA/VALUE/NEGATION 的 span-level precision/recall/F1。
- Negation：eligible SINGLE accuracy/F1；无样本的 split × intent 标记 `NOT_ESTIMABLE`。
- Safety：`UNSAFE_FALSE_ACCEPT_RATE`；Safety Gold 只作独立回归，不选阈值。
- 阈值只在 Stage 4B 训练完成后使用 validation 设计，保留 scope/structure confidence、intent top1、margin、slot confidence；不得使用任意固定 0.5 规则。
- Legacy Parser 与 Future Local NLU 在完全相同 test set 上比较正确性、否定、MULTI/OOD fail-close 与 latency，但 Stage 4A 不修改 baseline。

## 产物与完成条件

输出 `data/nlu/model_selection/` 下的 environment、candidate matrix、latency、token alignment、architecture 和 selection 六项报告。只有三个候选均有可复核实测、联合架构兼容、对齐结论明确且冻结/零训练复核通过时，`MODEL_SELECTION_READY` 才可为 `YES`；`READY_FOR_MODEL_TRAINING` 本阶段始终为 `NO`。
