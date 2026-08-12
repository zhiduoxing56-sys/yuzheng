# Full NLU 映射覆盖第二轮审计与 baseline_v2 设计

## 背景与目标

在保持 R3、中文统一 schema、五个 raw source、人工种子和 baseline_v1 不变的前提下，审计 baseline_v1 中确定性转换器遗漏的语义模式。只有能够由 MAC-SLU 结构化字段与 R3 contract 唯一证明的模式才进入 `nlu_mapping_v3`，随后重建 `baseline_v2`。

## 不可变边界

- R3 固定为 `sys-014-semantic-hardening-r3`，SHA256 固定为 `c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06`。
- `full_nlu_sample_schema_v1`、`nlu_mapping_v2`、baseline_v1、MAC-SLU JSONL 和两份 Excel 均只读。
- 不使用文本相似度、最近邻、旧 7-Intent 标签、checkpoint 或 fallback。
- 不放宽灯光、变道、避险、方向盘或其他 R3 合同。

## 方案比较

### 方案一：逐句 override

- 优点：局部准确。
- 缺点：无法解释 4,627 个 frame occurrence 的系统性缺口，不可推广，不符合“不要逐句人工处理”。

### 方案二：继续扩充自然语言关键词 if/else

- 优点：实现快。
- 缺点：规则来源分散，容易受同一句其他子意图干扰，并可能把宽泛对象猜成正式能力。

### 方案三：结构化语义模式规则表 + 通用解释器

- 优点：以操作、对象、功能、位置、数值、模式形成稳定模式；每次状态变化都可追溯到规则编号；可显式声明排除条件。
- 缺点：需先生成审计表并维护规范化字典。

## 采用方案

采用方案三。用户给定的任务清单已明确批准“先审计、再规则、后重建”的实施顺序和安全门。

## 数据流

1. 从 baseline_v1 sidecar 定位 review reason，并回连 immutable provenance。
2. 重新按每个 MAC semantic frame 执行 v2 解释器，区分“样本数”和“未解析 frame occurrence 数”。
3. 生成去重模式表及示例，不在审计阶段改变标签。
4. 根据结构字段组合建立带规则编号的 v3 表；文本只能用于方向、数值、模式等确定性规范化，不能选择最近 Intent。
5. 对无 frame 样本使用四分类高精度审核：明显非控制、明显控制、残缺垃圾、无法判断。明显控制必须同时出现动作和具体对象/功能。
6. 以同一 R3/schema/raw source 重建 baseline_v2，并在 mapping metadata 中记录每条新增规则编号。
7. 逐样本比较 v1/v2；任何 UNKNOWN/review 的改善必须存在 v3 rule id。

## 输出与验收

- `nlu_mapping_v3` 规则源及 SHA256。
- 4,627 frame occurrence 模式审计、无 frame 四分类审计、10 个零覆盖审计、71 意图 A-F 漏斗、座舱覆盖报告、安全 57 条清单。
- baseline_v2 四个 pool、provenance、mapping metadata、报告、manifest 和 v1/v2 diff。
- 全部派生样本继续通过冻结 validator，`SCHEMA_COMPLIANCE_RATE=100%`。

## 停止条件

任一输入/R3/schema 哈希变化、规则无法唯一指向合同、或 schema 合规率低于 100% 时停止，不生成扩写、划分或训练资产。
