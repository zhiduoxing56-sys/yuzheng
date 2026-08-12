# SYS-014 Stage 3C.1 PoC v2 切分设计

## 背景与目标

`sys014-poc7-v1` 已满足不可变、可复现和零泄漏，但其 DSU 分组把原始 `paraphrase_family_id` 当作无条件连边。部分 Stage 3B.1 合成 family 同时包含多种真实表述；其中任一表述与 `TEST_ASSET` 匹配后，传递闭包会把整个 family 锁入 TEST。最明显的连通分量含 46 条 `WINDOW_OPEN` positive，仅 1 条是 `TEST_ASSET`。

本阶段创建全新的 `sys014-poc7-v2`，在不改变文本、sample_id 和语义标注的前提下修正分组粒度与 split assignment。v1 目录保持逐字节不变，Safety Gold 不参与优化。

## 方案比较

### 方案一：只更换随机种子

- 优点：实现简单。
- 缺点：无法拆开由过粗 family 形成的 46 条强制 TEST 连通分量，不能解决根因。

### 方案二：按单样本分层随机切分

- 优点：类别比例容易接近目标。
- 缺点：会把 AREA、VALUE、NEGATION 替换形成的同模板样本拆到不同 split，产生机械泄漏，不可接受。

### 方案三：细化合成 family，再做 group-aware 确定性优化（采用）

- 仅对 `SYNTHETIC_TEMPLATE` 且内部存在多个机械模板的 family 进行细分。
- 细分键为 slot-aware mechanical signature：AREA、VALUE、NEGATION 先替换成占位符，再统一连接词和礼貌词。
- `TEST_ASSET` family 完全不改。
- 细分后仍用 family、template signature、mechanical signature 三类边构造 DSU 连通分量，因此真正近重复仍被绑定。
- 先强制 TEST_ASSET group 入 TEST，再用固定 seed 的约束贪心和确定性局部移动优化 70/15/15、7 Intent positive/negated/MULTI、结构、scope 和 slot 覆盖。

该方案直接修复过度绑定，同时把零泄漏置于平衡目标之前。

## 数据流

1. 读取当前 849 条 candidate、60 条 Safety Gold 和不可变 v1。
2. 计算并保存 v1 所有文件 SHA256；生成 v1 group 失衡诊断。
3. 为符合条件的合成样本生成确定性 `PF_V2_SYN_<HASH>` family；其他字段不变。
4. 构造合法 split group，并锁定含 TEST_ASSET 的 group 到 TEST。
5. 完成带最低覆盖约束的分层分配和局部改进。
6. 在 staging 目录生成数据、manifest、诊断、差异和审计报告。
7. 独立 validator 检查 schema、span、registry、源数据等价性、Safety Gold、覆盖、SHA256、零泄漏及 v1 完整性。
8. validator 全部为零后，原子重命名为 `sys014-poc7-v2`。

## 边界与异常处理

- family 细分只能发生在 `source_type=SYNTHETIC_TEMPLATE`；`TEST_ASSET` family 改动立即失败。
- 冻结记录与源 candidate 相比，除 `split` 和允许的 `paraphrase_family_id` 外必须逐字段一致。
- 若最低覆盖与合法 group 冲突，不拆 group；报告 `BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT`，并不得标记冻结成功。
- v2 已存在时拒绝覆盖。
- v1 任一文件 SHA256 与执行前基线不一致时拒绝冻结。

## 验证策略

- source validator：span、registry、structure、family leakage 全部为 0。
- frozen validator：exact、normalized、template、mechanical、family、split_group 跨 split 泄漏全部为 0。
- `TEST_ASSET_IN_TRAIN=0`；Safety Gold 与源文件、v1 完全一致。
- 每个 Intent positive 满足 TRAIN/VAL/TEST 的 30/5/5；negated 尽量满足 8/2/2；VAL/TEST 的 `WINDOW_SET_POSITION` 均有 VALUE；`WINDOW_OPEN` VALUE 为 0。
- 使用同 seed 重新 prepare，sample→split 和 refined family 映射必须一致。

## 非目标

不训练模型、不进行模型选择、不切分 Safety Gold、不修改 backend/runtime，也不把 v2 宣称为可立即训练。
