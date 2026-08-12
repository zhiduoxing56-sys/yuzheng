# Full NLU R3 数据基线设计说明

## 背景与目标

基于唯一冻结的 `sys-014-semantic-hardening-r3`，建立可追溯、可重新生成、尚未切分的 Full NLU canonical raw pool。所有来源只输出同一套中文样本结构；MAC-SLU 原 source split、原始标注、重复关系等放入独立审计 sidecar，不向最终样本增加字段。

## 现状与约束

- R3 SHA256 固定为 `c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06`。
- `full_nlu_mapping_v1` 已被 R3 freeze manifest 引用，本阶段只创建 v2，不修改 v1。
- 三个 MAC-SLU JSONL 和两个人工 Excel 均为 immutable source。
- 历史 7-Intent PoC 不得成为数据、标签、模型、评测或 fallback 来源。
- 本阶段不扩写、不切分最终 train/validation/test、不训练模型。

## 方案对比

### 方案一：沿用旧英文 annotation schema

- 优点：兼容历史脚本。
- 缺点：违反冻结中文结构，并会恢复平行标签体系。

### 方案二：只使用 JSON Schema

- 优点：结构清晰。
- 缺点：无法检查全局唯一 ID、多文件重复和正样本逻辑等跨字段约束。

### 方案三：JSON Schema + 确定性逻辑 validator

- 优点：既冻结字段和类型，又能执行跨字段、跨文件和全局唯一性检查。
- 缺点：需要同时维护 schema 与 validator SHA。

## 推荐方案

采用方案三。JSON Schema 是结构权威，Python validator 是逻辑约束权威；二者均进入数据构建 manifest。

## 详细设计

### 架构

- `data/nlu/full/schema/`：冻结中文 schema、smoke 样本。
- `data/nlu/full/spec/`：mapping v2、已知但不开放认知表、manual overrides。
- `scripts/full_nlu/`：schema validator、输入审计和数据构建器。
- `data/nlu/full/builds/full-nlu-r3-baseline-v1/`：canonical pools、provenance、重复审计、review queue、统计、报告、manifest。

### 数据流

1. schema smoke validation。
2. 五个源文件硬计数验证；任一不符立即停止。
3. MAC-SLU 合并、精确文本去重、保留全部 provenance。
4. 使用 R3、mapping v2 和独立认知表进行确定性映射；不能证明的样本进入未知或 review。
5. 转换两份人工种子，但不得绕过 R3 contract。
6. 合并 canonical raw pool，不执行最终 split。
7. 100% schema validation 后生成 manifest。

### 异常与边界处理

- 不使用最近邻、模型或旧 PoC 标签猜测。
- 不修改原始文本；规范文本只进行 Unicode/空白/标点等保守标准化。
- exact duplicate 只保留一个 canonical 样本，全部来源写入 sidecar。
- manual override 必须来自版本化文件；无可靠依据则 review。

### 测试策略

- schema 正反例单测。
- 输入行数、JSON 可解析性和 Excel 有效行硬门槛。
- R3/mapping/manual override/schema/validator SHA 锁定。
- 全部输出逐条验证并要求 `SCHEMA_COMPLIANCE_RATE=100%`。

## 风险与待确认项

MAC-SLU 标签可能比 R3 合同粗糙或带噪；本阶段宁可保守进入 `未知/人工复核`，不以宽泛自然语言纠错规则覆盖原标注。

