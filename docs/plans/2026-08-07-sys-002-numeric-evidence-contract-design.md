# SYS-002 数值安全证据类型契约设计说明

## 背景与目标

`EvidenceObservationInput.value` 是冻结公开 Schema 中的宽类型字段。当前 Repository 会把字符串车速等非空输入标为 `VALID`，而 Quality 和 SafetyGate 的数值比较只接受 `int/float`，从而形成“覆盖与可信度有效、规则却静默跳过”的危险误 PASS。

本设计只修复 SYS-002：建立共享的内部值契约，使数值安全证据在 Repository 生产边界即被校验，Quality 再次验证，SafetyGate 对上游契约异常 fail closed。公开 Schema、数据库 Schema、审计哈希算法、Decision 公式、业务 Gate、阈值和 `action_evidence_map` 均保持不变。

## 数值安全证据范围

- `vehicle_speed`
- `front_obstacle_distance`
- `rear_obstacle_distance`
- `speed_limit`
- `ambient_light` 的数值形态；同时保留既有 `LOW`、`DARK`、`NIGHT` 分类值

`ultrasonic_distance` 当前不进入数值安全比较，本轮不扩展其业务语义。

## 方案对比

### 逐条修补 SafetyGate

- 优点：改动少。
- 缺点：Quality、coverage 和 trust 仍可接收非法值，其他比较器仍可能绕过。

### 收紧公开 Pydantic Schema

- 优点：API 边界可直接拒绝。
- 缺点：改变冻结公开契约，不允许采用。

### 共享内部值契约（采用）

- 优点：统一、最小，不改变公开契约；Repository、Quality、Gate 可复用同一判定。
- 缺点：需要在三个内部消费层增加明确的防御职责。

## 详细设计

### 合法值

严格数值证据只接受有限的 Python `int` 或 `float`，并明确排除 `bool`。不自动转换字符串。`None` 沿用现有缺失语义。`ambient_light` 另允许既有分类值 `LOW`、`DARK`、`NIGHT`，保留既有的大小写不敏感匹配，但不改变存储值。

### 非法值表达与审计

Repository 将普通非法值降为 `MISSING`，节点值写为 `None`，可用性、时效性和一致性均为 0。metadata 只记录受控摘要：验证原因、接收的 Python 类型、预期契约、原始值未保留。类型错误使用 `INVALID_VALUE_TYPE`，非有限数使用 `NON_FINITE_NUMERIC_VALUE`。不保存原始容器或完整 `repr`，也不使用 `TAMPERED` 冒充类型错误；若输入本身同时明确声明完整性失败，仍保留既有完整性状态优先级。

### 三层职责

1. Repository：在 `_make_node` 公共生产边界应用契约，阻止非法值进入索引、召回和审计事实。
2. EvidenceQuality：对节点值再次验证；绕过 Repository 的非法节点不得贡献 coverage、trust 或数值冲突计算。
3. SafetyGate：不修改传入 EvidenceNode。若 mandatory 节点状态看似可用但值违反契约，新增一个内部上游契约异常检查并 fail closed；不新增配置业务 Gate，不改变规则数或阈值。正常 Repository 路径仍由既有 `MANDATORY_EVIDENCE_AVAILABLE` 命中。

### 预期数据流

`vehicle_speed="20"` 将在 Repository 变成带原因 metadata 的 `MISSING` 节点；Quality 保持不可用；coverage 不完整且该节点 trust 为 0；既有 mandatory missing Gate 阻断；最终 BLOCK，不签 token，不执行，车门保持 CLOSED。`MOVING_DOOR_OPEN_PROHIBITED` 不应命中。

数值 `vehicle_speed=20` 保持 `VALID`，命中原移动开门规则。数值 `front_obstacle_distance=3` 保持 `VALID` 并命中原障碍规则；字符串 `"3"` 走 mandatory missing 保守阻断。

## 测试策略

- Repository/契约矩阵：`0`、`20`、`20.5`；数字字符串、普通字符串、布尔、`None`、NaN、正负 Infinity、容器。
- Quality：直接构造绕过 Repository 的非法有效节点，验证不可计入覆盖。
- SafetyGate：直接输入状态看似有效但值非法的 mandatory 节点，验证明确的上游契约异常阻断且不伪造数值业务规则。
- SYS-002 端到端：证据状态、coverage/trust、Gate、Decision、token、workflow execution、车辆最终状态和 Audit metadata。
- 合法车速、障碍距离、ambient light 分类语义及 SYS-001 回归。
- 最后运行完整 `backend/tests`，确认冻结契约测试保持通过。

## 明确不处理

不处理 SYS-003、SYS-004 missing ledger、限速业务规则、Execution precheck 事实绑定重构、CARLA、前端、Memory/Causal 或其他业务规则。
