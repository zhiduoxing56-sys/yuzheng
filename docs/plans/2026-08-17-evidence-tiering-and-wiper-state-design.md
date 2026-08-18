# 证据分级与雨刮状态闭环设计说明

## 背景与目标

“雨天开启自动雨刮”已经被正确解析为 `WIPER_SET_MODE / RAIN_SENSOR`，安全评分也允许执行，但最终被硬性安全门拒绝。直接原因是运行时缺少 `WIPER_STATE`；系统性原因是知识节点的 `required_evidence` 被无条件追加到硬前置 `required_types`，导致“知识评估需要的信息”被错误解释为“缺失即拒绝的执行条件”。

本设计同时完成两项修正：

1. 将证据需求分为硬前置、评估佐证、知识检索三层，并为每层定义唯一、可审计的裁决语义。
2. 补齐模拟器、场景和证据仓库的 `WIPER_STATE`，消除当前雨刮状态的数据缺口。

成功标准：

- 硬前置证据缺失仍然稳定输出 `BLOCK`。
- 评估佐证证据缺失只影响评分，不直接触发硬门。
- 知识检索所需证据缺失稳定输出 `REVIEW`，不能输出 `BLOCK`。
- 雨天场景提供有效 `WIPER_STATE` 后，“开启自动雨刮”不再因证据缺失而拒绝。
- 所有证据等级、来源、缺失类型和裁决影响均进入 API 与审计记录。

## 现状与约束

- `IntentEvidenceDemand.required_types` 同时承担需求表达、强制召回和硬门输入，语义过载。
- Evidence Demand Registry 中 `WIPER_SET_MODE` 的 `WIPER_STATE`、`ENVIRONMENT_CONDITIONS` 原本是 `recommended`。
- Trusted Knowledge 命中后会把知识节点 `required_evidence` 直接加入 `required_types`。
- `EvidenceDemandService.missing_is_hard_gate()` 对所有 `required_types` 固定返回硬门语义。
- `WIPER_STATE` 已存在于证据类型目录，但运行时映射为 `UNAVAILABLE`，`VehicleState` 与场景均没有完整雨刮状态字段。
- 本次只修正裁决和状态观测，不新增真实雨刮执行器；`PASS` 仍须受现有运行能力规则约束。
- 现有 API 字段和历史审计需要兼容读取，不能通过重命名破坏前端。

## 方案对比

### 方案一：仅在雨刮规则中移除 `WIPER_STATE`

- 优点：改动最小，能消除当前拒绝。
- 缺点：掩盖运行时状态缺口；其他知识节点仍会发生同类误拒绝；无法表达证据等级。

### 方案二：知识证据全部改为推荐证据

- 优点：知识命中不再触发硬拒绝。
- 缺点：知识所需证据缺失只会轻微影响评分，无法稳定进入用户已确认的 `REVIEW`。

### 方案三：三级证据需求并补齐雨刮状态（采用）

- 优点：硬门、评分和知识复核职责清晰；能修复当前问题并防止同类问题；审计可解释。
- 缺点：需要调整需求模型、知识增强、证据解析、裁决合并、前端契约和测试。

## 推荐方案

采用方案三。证据等级由证据来源和显式规则决定，知识检索不得隐式提升硬门等级。硬门只读取硬前置证据；评估层读取佐证证据并影响评分；知识层缺失时通过证据对齐路由产生 `REVIEW`。

## 详细设计

### 架构与等级语义

每个意图的证据需求拆分为：

| 等级 | 模型字段 | 来源 | 缺失影响 |
| --- | --- | --- | --- |
| 硬前置 | `required_types` | Demand Registry 的 `mandatory`、条件强制项和全局安全规则 | `BLOCK` |
| 评估佐证 | `assessment_types` | Demand Registry 的 `recommended` | 进入质量指标与安全评分，不直接硬拒绝 |
| 知识检索 | `knowledge_required_types` | 已接受知识节点的 `required_evidence` | `REVIEW` |

`optional_types` 暂时保留为兼容字段，输出 `assessment_types` 的镜像；待所有前后端消费者迁移后再单独弃用。知识节点的 `optional_evidence` 进入评估佐证层，但必须保留知识来源信息。

### 需求构建与知识增强

`EvidenceDemandService.build()` 仅允许正式 Registry 产生 `required_types`。Trusted Knowledge 的 `augment()` 不再修改 `required_types`：

- `required_evidence` 合并到 `knowledge_required_types`；
- `optional_evidence` 合并到 `assessment_types`；
- `knowledge_augmented_types` 保留为兼容摘要，但新增每种证据的 `requirement_level` 和知识节点来源；
- 同一证据被多个等级要求时采用 `HARD_REQUIRED > KNOWLEDGE_REQUIRED > ASSESSMENT`，每种类型只参与一次裁决，但保留全部来源。

知识库不能自行制造硬前置条件。未来若确需把某知识条件升级为硬门，必须在正式 Demand Registry 或 Safety Rules 中用结构化规则显式声明，并通过契约测试。

### 召回、解析和裁决

证据召回覆盖三个等级，但分别生成解析结果：

- 硬前置缺失、不可用、陈旧或被篡改：沿用硬门判定。
- 知识必需证据缺失或不可用：证据对齐路由至少为 `EVIDENCE_REVIEW`；如果其他独立硬门已命中，最终仍为 `BLOCK`。
- 评估佐证证据缺失：计入覆盖率、质量与安全评分，不单独制造 `REVIEW` 或 `BLOCK`。
- 已存在的证据冲突、规则禁止项和真实危险条件仍按各自规则处理，不因分级修正而放宽。

裁决合并顺序保持保守性：独立硬门 `BLOCK` 优先；否则知识证据缺失约束为 `REVIEW`；否则使用评分结果。

### 雨刮状态闭环

在 `VehicleState` 与 `VehicleStatePatch` 中新增雨刮状态：

- `wiper_mode`：`OFF / SLOW / MEDIUM / FAST / INTERVAL / RAIN_SENSOR`；
- `wiper_intensity`、`wiper_frequency`；
- `wiper_wiping`、`wiper_error`。

模拟器适配器保存和更新这些字段。CARLA 若没有稳定的原生雨刮读取接口，则使用明确标记为模拟/影子状态的适配器字段，不伪装成真实车辆总线来源。证据仓库从车辆状态生成 `WIPER_STATE`，并在节点元数据中记录实际 provider。

两个雨刮演示场景都显式提供 `WIPER_STATE`：晴天场景默认 `OFF` 且无故障；雨天场景默认 `OFF` 且无故障。加载场景后，该状态与其他激活场景证据一样跨页面持续，并受场景版本审计。

本次不新增 `WIPER_SET_MODE` 的真实执行契约。因此即使安全裁决为 `PASS`，实际执行仍遵循现有能力检查；界面必须区分“安全上允许”与“执行器未接入”。

### API、审计与界面解释

API 和审计增加：

- `assessment_types`、`knowledge_required_types`；
- 各等级的缺失类型；
- 知识需求来源节点；
- 证据对齐进入 `REVIEW` 的明确原因码，例如 `KNOWLEDGE_EVIDENCE_MISSING`。

裁决页面显示真实的层级原因：

- 硬门卡片只显示真正的硬门；
- 知识证据缺失时显示“需要复核”，列出缺失证据和知识规则；
- 不再出现“评分允许、硬门阻断、具体原因空白”的矛盾展示。

### 异常与边界处理

- 若知识索引不可用且没有命中节点，不虚构知识需求，沿用 Registry 需求。
- 若知识证据存在但值结构不可用，按知识证据缺失处理并进入 `REVIEW`。
- 若同一类型同时属于硬前置与知识证据，按硬前置处理，缺失为 `BLOCK`。
- 若雨刮状态来源为场景模拟，必须标识 `SIMULATION`，不能作为真实车辆总线证据展示。
- 旧审计缺少新增字段时按空列表读取，保持历史记录可查看。

### 测试策略

- 单元测试：三级需求构建、等级去重与优先级、各等级缺失的裁决语义。
- 知识增强测试：知识 `required_evidence` 不再进入硬前置，只进入知识层。
- 硬门回归：开门缺车速仍为 `BLOCK`，不受本次修改影响。
- 雨刮场景测试：缺少 `WIPER_STATE` 时为 `REVIEW`；提供有效状态后不因证据缺失而拒绝。
- 场景一致性测试：CARLA/裁决页往返后雨刮状态与激活场景版本保持一致。
- API/审计测试：等级、缺失原因和知识来源完整返回。
- 前端测试：`BLOCK`、`REVIEW`、`PASS` 三种视觉与解释一致。

## 风险与待确认项

- 历史测试中可能把知识增强类型直接断言为 `required_types`，需要按新语义更新，而不是机械维持旧行为。
- 评分服务当前主要围绕 required/optional 计算，需要确保新增评估层不会重复计数。
- CARLA 对雨刮的原生可观测能力有限时，只能提供诚实标注的影子状态；接入真实车辆总线应作为后续独立任务。
