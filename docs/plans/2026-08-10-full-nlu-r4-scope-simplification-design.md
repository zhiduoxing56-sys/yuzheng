# Full NLU R4 Scope Simplification 设计

## 背景与目标

语证只精确解析、安全裁决并授权执行 `FORMAL_EXECUTABLE`。其他明确车辆本地控制统一识别为 `KNOWN_CONTROL_BYPASS`，不学习详细 Intent、参数或合同，并逐子意图转交原生车机助手。

## 现状与约束

- 父版本 `intent_registry_r4_final_candidate.yaml` 有 162 个 Intent：71 个 FORMAL、91 个详细 KNOWN。
- 71 个 FORMAL 的 ID、顺序、三元组及 slot/value/mode/direction/conditional 合同必须完全冻结。
- 7 个 P0 annotation guidance 修复必须保留。
- 禁止数据重映射、扩写、训练或继续细化 Known taxonomy。

## 方案比较

### 方案一：Formal-only 运行投影 + 独立 scope schema（采用）

- 运行 `intents` 仅保留 71 个 FORMAL。
- `KNOWN_CONTROL_BYPASS` 是 scope，不创建伪 Intent。
- family、ontology 和合同裁剪为 FORMAL 引用闭包。
- 91 个 KNOWN 定义及其引用信息原样归档。

优点：真正收缩模型标签空间；FORMAL 合同仍自洽；bypass 不再被强迫生成无意义参数。

### 方案二：保留 162 个 Intent 但标记 KNOWN inactive

缺点：详细标签仍存在于 registry，容易继续进入 intent head，违反架构收缩目标。

### 方案三：增加 `KNOWN_CONTROL_BYPASS` 伪 Intent

缺点：scope 被误建模为具体 Intent，仍会要求 Intent ID，不符合批准语义。

## 详细设计

### Runtime registry

- `intents`：父版本 71 个 FORMAL 定义逐项原样保留。
- `capability_families`：保留包含 FORMAL 的 family，成员仅保留 FORMAL；`BODY_HOOD` 删除 KNOWN 成员 `HOOD_SET_POSITION`。
- contracts/ontology：仅保留 FORMAL 引用闭包，不对 bypass 维护 VALUE/MODE/AREA 或 completeness。
- `runtime_scope_schema.allowed_scopes` 固定为：`FORMAL_EXECUTABLE`、`KNOWN_CONTROL_BYPASS`、`NON_CONTROL`、`UNKNOWN_OOD`。

### Scope 路由

`KNOWN_CONTROL_BYPASS` 固定输出：

```yaml
decision_route: PASS_BYPASS
execution_authorized_by_yuzheng: false
route_target: NATIVE_COCKPIT_ASSISTANT
formal_contract_completeness_check: SKIP
```

只有原始文本、MAC split 和 semantics 明确证明为车辆/座舱/车机本地控制且不能映射 FORMAL 时才进入 bypass。普通聊天、信息查询、音乐内容请求进入 `NON_CONTROL`；真正未知或域外进入 `UNKNOWN_OOD`。

### 多意图

`multi_intent_schema` 使用有序 `sub_intents`。每项独立带 `scope` 并独立路由，允许 FORMAL 与 bypass 混合；句级统一 PASS/REVIEW 被明确禁止。

### Archive

`known_control_reference_archive_r4.yaml` 保存父版本 91 个 KNOWN intent mapping 的精确深拷贝，并附带其 family 与引用合同快照。archive 明确禁止作为模型标签空间、运行 registry 或 Gold 精确 Intent 映射依据。

### Gold 原则

registry 只记录未来构建合同，不修改现有数据。明确车辆控制但非 FORMAL 的建议子意图仅为 `{scope: KNOWN_CONTROL_BYPASS}`；原 MAC semantics 仅可作 provenance，不进入模型必学 target。

## 校验策略

- 冻结 R3、R4 core、R4 full、R4 final candidate 哈希。
- 71 个 FORMAL mapping 与父版本逐项相等，ID 顺序相等。
- 运行 intent head 不含任何 `KNOWN_UNSUPPORTED_CONTROL`，archive 数量恰为 91 且定义逐项相等。
- 四态 scope 齐全；bypass 路由和免 completeness 合同精确匹配。
- `NON_CONTROL` 与 `UNKNOWN_OOD` 分离。
- 混合多意图示例与 per-sub-intent routing 合同存在。
- FORMAL family/contract/ontology 引用闭合，7 个 P0 guidance 未回滚。

## 边界

不重映射、不训练、不扩写、不创建详细 Known Intent，也不修改任何正式 Intent。
