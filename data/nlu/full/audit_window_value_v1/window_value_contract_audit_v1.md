# R3 车窗开度 VALUE 与端点/比例表达审计

- 审计版本：`window_value_contract_audit_v1`
- R3：`sys-014-semantic-hardening-r3` / `c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06`
- baseline_v2 canonical pool：`6d8645adf0fd9429bb8fd6d3d75ecfdf6d65ff4c33926ea1cc27054dd5c51a51` / 20899 条
- 本轮只生成审计材料；R3、映射规则和 baseline_v2 均未修改。

## 合同结论

`WINDOW_SET_POSITION` = `ADJUST + WINDOW + OPENING_POSITION`，VALUE 使用 `PERCENT_0_100_REQUIRED`，合法范围 0–100%，且 VALUE 必需。

R3 明确了百分比范围，也明确了“一半”在百分比合同中确定性归一为 50%；但 `WINDOW_SET_POSITION` 没有专属的 `zero_semantics`、`hundred_semantics` 或端点映射。

同时，R3 另有 `WINDOW_OPEN` 与 `WINDOW_CLOSE` 两个 `OPENING_STATE` 意图，且没有冻结“全开/全关/升到底/降到底”应优先进入状态意图还是开度端点值的规则。

R3 引用的 VSS 6.0 源说明：Window 的 Start position 是 Closed，Position 的 0 是 Start、100 是 End；同一 Position 行又明确提醒 Open/Close 与 Start/End 的关系依对象而定。由此可以推出 0%=Closed 起点，但当前冻结文本没有把 100%=Fully Open 明写为 Full NLU 规范。

结论：`0/100` 双向端点合同尚未在 R3 中完整冻结。为遵守“只有唯一确定才规范化”，本轮没有把全开/降到底自动写成 100%。

## “主驾车窗降到最低”复核

- 样本编号：`fnlu-5d8cea51f8e39780f01ec46c`；来源：`train_set.jsonl:1235`。
- 当前已正确识别：正式可执行、肯定、`WINDOW_SET_POSITION`、位置 `LEFT_FRONT`。
- 当前 VALUE=null，因此结构状态=缺槽、合同不完整、不得进入正式正样本。
- 语言物理语义可确定为 fully-open endpoint；但冻结 R3 尚未显式确定该端点的 canonical 数字，因此本轮未改样本。
- 若后续正式冻结 `0%=完全关闭、100%=完全打开`，该样本应按用户指定结果改为 VALUE=`100%`、单意图、合同完整且允许进入正式正样本。

## 缺槽清单统计

- 全 canonical pool 命中指定表达：327 条；其中当前缺槽：23 条。
- 车窗相关命中：45 条；其中当前缺槽：14 条。

| 表达 | 全池命中 | 全池缺槽 | 车窗命中 | 车窗缺槽 |
|---|---:|---:|---:|---:|
| 完全打开 | 0 | 0 | 0 | 0 |
| 完全关闭 | 0 | 0 | 0 | 0 |
| 升到底 | 2 | 2 | 2 | 2 |
| 降到底 | 0 | 0 | 0 | 0 |
| 三分之一 | 15 | 4 | 4 | 4 |
| 三分之二 | 3 | 1 | 1 | 1 |
| 最低 | 161 | 11 | 7 | 3 |
| 最高 | 90 | 2 | 2 | 1 |
| 到底 | 5 | 2 | 2 | 2 |
| 全开 | 3 | 1 | 2 | 1 |
| 全关 | 9 | 1 | 5 | 1 |
| 一半 | 44 | 1 | 22 | 1 |
| 半开 | 2 | 0 | 0 | 0 |

### 车窗相关缺槽样本（完整清单）

| # | 样本编号 | 原始文本 | 命中表达 | 当前子意图数值 | 审计结论 |
|---:|---|---|---|---|---|
| 1 | `fnlu-5d8cea51f8e39780f01ec46c` | 主驾车窗降到最低 | 最低 | `[null]` | `BLOCKED_BY_UNFROZEN_WINDOW_ENDPOINT_DIRECTION` |
| 2 | `fnlu-d4460dceebf236087b8261d1` | 前排车窗打开三分之一打开空调 | 三分之一 | `[null]` | `RATIO_REQUIRES_TARGET_DELTA_AND_SERIALIZATION_AUDIT` |
| 3 | `fnlu-e4a67372762a4de3e6107ebe` | 车窗升到底 | 升到底, 到底 | `[null]` | `BLOCKED_BY_UNFROZEN_WINDOW_ENDPOINT_DIRECTION` |
| 4 | `fnlu-91125b2f1dabbffd9da2853e` | 车窗降到最低 | 最低 | `[null]` | `BLOCKED_BY_UNFROZEN_WINDOW_ENDPOINT_DIRECTION` |
| 5 | `fnlu-71a557d439fe904daea1fb49` | 把所有车窗全关闭 | 全关 | `[null]` | `BLOCKED_BY_UNFROZEN_WINDOW_ENDPOINT_DIRECTION` |
| 6 | `fnlu-e4fdd98a05f6aad79719c6c5` | 关闭空调打开全车三分之一车窗 | 三分之一 | `[null]` | `RATIO_REQUIRES_TARGET_DELTA_AND_SERIALIZATION_AUDIT` |
| 7 | `fnlu-30014b3886fbe62c968db90c` | 车窗开到最高 | 最高 | `[null]` | `BLOCKED_BY_UNFROZEN_WINDOW_ENDPOINT_DIRECTION` |
| 8 | `fnlu-e679525168d620af3c135445` | 车窗控制切换全开 | 全开 | `[null]` | `BLOCKED_BY_UNFROZEN_WINDOW_ENDPOINT_DIRECTION` |
| 9 | `fnlu-663a03a8d3f96223056aa6dc` | 打开前排窗户三分之一后排窗户二分之一 | 三分之一 | `[null, null]` | `RATIO_REQUIRES_TARGET_DELTA_AND_SERIALIZATION_AUDIT` |
| 10 | `fnlu-d108ab942e1e68b32e2c8799` | 降到最低把车窗降到最低 | 最低 | `[null]` | `BLOCKED_BY_UNFROZEN_WINDOW_ENDPOINT_DIRECTION` |
| 11 | `fnlu-600ecb65fdbcc1c7e767e73b` | 主驾车窗降到三分之一副驾车窗降到二分之一 | 三分之一 | `[null, null]` | `RATIO_REQUIRES_TARGET_DELTA_AND_SERIALIZATION_AUDIT` |
| 12 | `fnlu-1950a5ce1a59b32bc863c3e5` | 关闭空调打开主驾副驾一半车窗 | 一半 | `[null, null]` | `DETERMINISTIC_50_CONVERTER_GAP` |
| 13 | `fnlu-1512c79062fc09131e74bffb` | 后排车窗关闭三分之二前排车窗关闭二分之一 | 三分之二 | `[null, null]` | `RATIO_REQUIRES_TARGET_DELTA_AND_SERIALIZATION_AUDIT` |
| 14 | `fnlu-5eea8b5df2c183a7b82f5218` | 车窗上升到底 | 升到底, 到底 | `[null]` | `BLOCKED_BY_UNFROZEN_WINDOW_ENDPOINT_DIRECTION` |

包含非车窗对象的全部缺槽 occurrence 见 `window_value_expression_missing_slot_samples_v1.jsonl`；车窗子集见 `window_value_expression_window_missing_slot_samples_v1.jsonl`。两者都保留原始标注、映射规则编号和来源溯源。

## 模糊小幅表达安全门

共找到 16 条车窗相关“开一点/留条缝/稍微/一点点”样本；擅自写入固定数值的违规数为 0。
另发现 2 条可能被当作完整 `OPENING_STATE` 而绕过数值合同的样本，已列入 JSON 审计，但本轮未重映射。
