# SYS-014 Stage 3C 数据冻结与无泄漏切分设计

## 背景与目标

将 Stage 3B.1 的 7-Intent 离线候选固化为不可原地修改的 `sys014-poc7-v1`，按 group 而非 sample 确定性切分，并完全隔离 Safety Gold 与 TEST_ASSET。

## 约束

- 只修改离线 NLU 数据及冻结工具/报告。
- 不下载或加载模型，不训练，不修改 runtime、数据库或 HTTP/WS contract。
- source candidate 保持 `UNASSIGNED`；冻结副本使用 `TRAIN`、`VALIDATION`、`TEST`。
- Safety Gold 仅复制为 `SAFETY_GOLD`，不参与切分或模型选择。

## 方案对比

### 方案一：仅按 paraphrase family

- 优点：简单。
- 缺点：无法阻止被错误拆成多个 family 的同模板 AREA/VALUE/NEGATION 变体跨 split。

### 方案二：family + 确定性模板签名并查集合并（采用）

- 优点：无需模型；可解释、可复算；能覆盖 family、slot 替换、礼貌词和连接词机械变体。
- 缺点：可能合并较大 group，使比例只能近似。

### 方案三：向量或编辑距离近邻聚类

- 优点：可能发现更多语义近邻。
- 缺点：阈值主观，复现和审计较弱；向量方案违反本阶段禁止加载 Transformer 的边界。

## 详细设计

### 冻结前修正

严格应用附件指定的 5 个 sample_id：删除 `0462`；将 `0686`～`0688` 改为 ACCELERATE 正样本；将 `0070` 改为 UNKNOWN_CONTROL。source validator 全零后才继续。

### 分组

1. 每条 candidate 计算 slot-aware `template_signature`：把 AREA、VALUE、NEGATION span 替换为 `<AREA>`、`<VALUE>`、`<NEG>`，再归一空白和标点。
2. 计算 `mechanical_signature`：在 template signature 上去除礼貌包装，归一多意图连接词。
3. 以 `paraphrase_family_id`、template signature、mechanical signature 的等价边建立并查集。
4. 每个连通分量生成确定性 `split_group_id`；该 ID 写入 manifest/审计，不写入受 annotation schema 约束的样本。

Dry-run 发现 Stage 3B.1 的 `PF_WINDOW_OPEN_POS_GENERAL_02` 将 6 条非 TEST 正样本锁为单一 group；与 TEST 强制 group 合计只有两个 positive group，无法同时覆盖 TRAIN/VALIDATION/TEST。冻结前仅将这 6 条新合成记录按表面模板细分为 3 个 family；不修改 text、Intent、slot 或 sample_id，机械相同项仍由 split group 重新绑定。

### 切分

- 固定 `split_seed=14031`。
- 含 TEST_ASSET 的 group 强制 TEST。
- 其余 group 先保证 TRAIN 全 7 Intent，再尽最大可能补足 VALIDATION/TEST 的 Intent、structure、scope、slot 与 WINDOW_SET_POSITION VALUE 覆盖。
- 在不拆 group 的前提下，用确定性贪心代价函数逼近 70/15/15。

### 泄漏审计

审计 exact/normalized text、family、split group、template signature、mechanical signature 的跨 split 重复；另外检查 Safety Gold 隔离、TEST_ASSET_IN_TRAIN、全局 sample_id、span、Registry、split 字段和 manifest SHA256。

### UNKNOWN_CONTROL 派生统计

不修改 annotation schema。根据完整 Registry 的能力词线索与外域对象清单，在 manifest/report 中分别统计 `UNKNOWN_KNOWN_REGISTRY_OUTSIDE_POC` 与 `UNKNOWN_EXTERNAL_CONTROL`；二者都表示当前 7-Intent 模型必须 abstain。

## 产物与不可变性

创建 `data/nlu/poc/frozen/sys014-poc7-v1/` 下四个 JSONL、manifest、split report、leakage audit 和 README。生成工具拒绝覆盖已存在的 v1；任何未来改动必须创建 v2。

## 测试策略

先运行 source validator；冻结后运行 frozen validator，重算所有摘要与 SHA256。仅在全部 failure 为 0 时报告冻结成功。
