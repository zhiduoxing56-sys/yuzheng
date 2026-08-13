# 第⑤+⑥阶段 Canonical Command Identity 一体化收口设计

## 背景与目标

统一语义空间已经冻结为 71 个 Formal、78 个 Known Non-Executable，共 149 个 Intent。本阶段不修改语义 Registry、Anchors 或 Known/Formal 定义，而是移除 SafetyGate、Decision、Authorization、Token 与 Execution 中作为安全身份存在的 `action|target`，统一使用由 `SemanticIntent` 确定性投影的 canonical command identity。

Known occurrence 继续在语义层 PASS 终止；Unknown、不完整或歧义输入继续 REVIEW 终止。两类路径都不得进入 Evidence、SafetyGate、Authorization、Token 或 Execution。

## 现状与约束

- `authorization.yaml` 的 13 个旧 `executable_actions` 同时包含重复别名、Known DISPLAY、无 Formal 对应的音乐动作及实际 Formal 能力。
- Token 仅绑定 `action/target/area`，Execution 也仅用这些展示字段复查身份。
- `vehicle_actions.yaml` 是底层物理动作库存；DISPLAY 映射可保留，但不得构成语音执行资格。
- Simulator 与 CARLA 不得各自维护 canonical slot 到默认物理行为的翻译。
- `area=unknown` 不等价于 `ALL`。是否支持省略 area 或 `ALL` 必须分别由统一语义合同和 capability contract 明确表达，未明确者 fail closed。
- capability contract 必须具有稳定版本与摘要；Token 必须绑定摘要，配置改变后旧 Token 不得对应新的物理行为。
- SQLite 只进行一次兼容增列。旧 Token 只可用于历史审计，缺少 canonical identity 的 Token 永久禁止执行，不提供 legacy fallback。

## 方案对比

### 方案一：中央 Canonical Capability Registry（采用）

- 在车辆能力配置中定义固定 8 个 canonical capability contract。
- 单一服务使用统一 Semantic Registry 校验 Intent 与 slot，再按 active adapter 判断支持并转换为物理动作。
- Authorization 与 Execution 共用该服务。

优点：唯一执行支持事实、adapter 差异可审计、DISPLAY 底层能力与语音资格解耦。

### 方案二：Authorization 独立能力白名单

会与车辆能力配置形成双重事实源，拒绝采用。

### 方案三：每个 Adapter 自行解释 canonical command

会让 Simulator 与 CARLA 分别维护语义翻译和默认值，拒绝采用。

## 推荐方案

采用中央 Canonical Capability Registry。生产数据流为：

统一 Semantic Registry → canonical identity → SafetyGate → central capability registry → Authorization → canonical Token → PRE_EXECUTION_CHECK → single translator → VehicleAdapter。

## 详细设计

### Canonical identity

从现有 `SemanticIntent` 投影固定字段：

- `intent_id`
- `area`
- `mode`
- `value`
- `direction`
- `control_attribute`

投影器依据统一 Registry 校验 runtime identity、slot 可承载性、枚举和数值合同，使用稳定 null 与 canonical JSON 规范。`action/target` 只保留为显示或底层物理描述。

### Capability contracts

候选全集固定为：

- `DOOR_OPEN`
- `DOOR_UNLOCK`
- `HEADLIGHT_SET_MODE`
- `WINDOW_OPEN`
- `ACCELERATE`
- `DECELERATE`
- `BRAKE`
- `AUTO_PARK_ENABLE`

每个合同明确 adapter、area/mode/value/direction 约束、默认物理行为、物理动作映射、合同版本。任何未列组合均 fail closed。

对于 `ACCELERATE/DECELERATE`，若当前物理实现确认空 value 对应固定 ±10 km/h，则默认值只在中央合同中定义；Adapter 不再自行赋予 canonical 默认值。

### Authorization 与 Token

删除生产 `executable_actions`。`is_executable` 和 `issue` 都必须通过 central capability registry；直接调用 `issue` 也必须拒绝 Known、非候选 Intent 和不受支持的 slot 组合。

Token payload 与 metadata 绑定完整 canonical identity、capability contract version/digest、turn/root/state/key/nonce/timestamps。稳定排序序列化保证等价命令身份一致。

### Execution

执行前要求 Token、原审计和 PRE_EXECUTION_CHECK 的 canonical identity 完全一致，并重新确认 active adapter 的 capability contract digest 未变化。通过后由单一 translator 生成底层物理动作，再调用 VehicleAdapter。

### SafetyGate 与 Decision

SafetyGate 的业务 selector 全部迁移为 `intent_id`、canonical slot 或 Registry metadata。DISPLAY 两条不可达规则在 canonical Authorization 验收完成后退休，active rule 数为 16。Decision 必要性保持旧覆盖，仅迁移到 `BRAKE` 和 `DECELERATE` Intent ID。

### SQLite migration

对现有 `authorization_tokens` 表一次性增加 canonical identity 与 capability contract 字段。历史行允许读取审计字段；任何 canonical 字段或合同摘要缺失的旧 Token 在验证阶段永久拒绝。

## 异常与边界处理

- `area=unknown` 与 `ALL` 分开匹配，绝不自动互换。
- Registry 未声明的 slot、capability 未声明的组合、未知 adapter、Known Intent、合同摘要变化均拒绝。
- Adapter 可保留 DISPLAY 等物理库存，但没有 canonical capability contract 就无法获得语音 Token。
- 历史 action/target 字段不得用于 Token 或执行身份 fallback。

## 测试策略

- 13 项旧 executable action 迁移矩阵及 8 个 capability contract 正反测试。
- 78 个 Known 的 Authorization eligibility 全部为 false。
- DISPLAY Pipeline 零下游、直接 issue 拒绝、无合法 Token。
- HEADLIGHT OFF/ON SafetyGate 与 Token 串用拒绝。
- capability digest 变化导致旧 Token 拒绝。
- DOOR/HEADLIGHT/DEFROST/驾驶控制/AUTOPARK/障碍/后方冲突专项测试。
- 16 条 active SafetyGate 规则逐条 HIT/MISS 与 reachability audit。
- 静态检查 SafetyGate、Decision、Authorization、Token、Execution 中 action/target 安全身份残留为零。
