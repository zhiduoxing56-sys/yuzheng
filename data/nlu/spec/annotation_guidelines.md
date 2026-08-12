# SYS-014 NLU 标注规范（DRAFT / OFFLINE）

> 本文件只用于离线数据设计。不得由运行时加载，不授予执行权限，也不修改现有 `SemanticFrame`、授权白名单或安全规则。

## 1. 标注顺序

1. 保留原始 `text`，不得先改写成规范句。
2. 记录 `registry_version=sys-014-semantic-hardening-r2`，不得跨 Registry 版本混用。
3. 判定 `intent_structure`：`SINGLE`、`MULTI` 或 `AMBIGUOUS`。
4. 判定 `scope_label`：`IN_SCOPE_CONTROL`、`NON_CONTROL`、`UNKNOWN_CONTROL` 或 `AMBIGUOUS_CONTROL`。
5. 仅当样本为 `SINGLE + IN_SCOPE_CONTROL` 时填写唯一 `intent`。
6. 标注原始字符 span：`AREA`、`VALUE`、`DIRECTION`、`MODE`、`NEGATION`。
7. 填写句级 `negated`：仅 `SINGLE + IN_SCOPE_CONTROL` 使用 boolean；MULTI/AMBIGUOUS/NON_CONTROL/UNKNOWN_CONTROL/AMBIGUOUS_CONTROL 使用 null。
8. 判定 `ood_label` 和安全标签。
9. 分配 `paraphrase_family_id`；在数据切分前保持 `split=UNASSIGNED`。
10. 双人复核高风险、否定、多意图、未知、数值边界样本。

## 2. Intent 规则

- Intent 表达一个不可再分的用户控制目的。
- 相反执行语义必须分开：`DOOR_OPEN`/`DOOR_CLOSE`、`DOOR_LOCK`/`DOOR_UNLOCK`。
- 区域实例不进入 Intent：左后车门仍为 `DOOR_OPEN + AREA=LEFT_REAR`。
- 连续数值不进入 Intent：20% 与 50% 都是 `WINDOW_SET_POSITION`。
- 枚举值原则上进入 `MODE`：P/R/N/D 都是 `GEAR_SET`。
- 不能根据 softmax 最大类强制赋予 Intent；不在 Registry 或不满足能力约束时必须 abstain。

## 3. Slot 规则

### AREA

仅表示物理实例或作用区域。统一值来自 Registry 的 `area_catalog`。驾驶位、主驾、司机这边统一为 `LEFT_FRONT`；副驾驶、副驾统一为 `RIGHT_FRONT`；前排中间、后排中间分别统一为 `MIDDLE_FRONT`、`MIDDLE_REAR`。

- `ATOMIC` AREA 对应一个具体执行器实例；`COMPOSITE` AREA 对应多个原子区域的显式聚合。
- 组合 AREA 只有用户明确表达时才标注；不得因 AREA 缺失自动标注 `ALL`、驾驶位、说话人位置、最近位置或上下文推断位置。
- 多实例对象未表达 AREA 时，Intent 可以保留，但 AREA 语义为 `UNRESOLVED`，参数解析不完整；本阶段不实现 Resolver 或 fan-out。

### DIRECTION

表示动作方向，不表示物理实例。例如“向左变道”的“左”标为 `DIRECTION=LEFT`；“左后车门”的“左后”标为 `AREA=LEFT_REAR`。

### VALUE

- span 覆盖完整数值表达及紧邻单位，例如“80公里每小时”“一半”“开到三成”。
- canonical annotation 保存原始字符位置；`canonical_value` 是供人工复核的预期归一结果。
- 真正数值解析、单位换算和范围验证由确定性 `ParameterNormalizer` 完成。
- 不单独设置 `UNIT` slot；单位包含在 VALUE span 中。
- “一点”“最大”“一半”等程度词按 VALUE 处理，不增加 DEGREE slot。
- VALUE 的统一语言形式来自 Registry：
  - `ABSOLUTE_TARGET`：绝对目标；百分比能力中的“一半”可确定性规范为 50%。
  - `EXPLICIT_RELATIVE_DELTA`：明确相对方向和明确变化量，必须同时保留。
  - `RELATIVE_SMALL`：“一点”“稍微”“一点点”等相对小幅，不绑定固定百分比、毫米或角度。
  - `PARTIAL_UNSPECIFIED`：“一部分”等程度未指定表达，参数不完整，不得规范为 50%。
- 模型理解出 VALUE 语义不等于已经形成车辆执行值；相对小幅、程度未指定和仅有方向无幅度均保留不完整状态，等待未来车型参数规范化或人工澄清。

### MODE

用于有限枚举目标，例如挡位、换挡模式、灯光模式和雨刮模式。枚举必须来自 Registry 的 `mode_contracts`。天窗翘起使用 `DIRECTION=UP/DOWN`，不使用 MODE 或角度 VALUE。

### NEGATION

- 标注直接否定控制动作的词或短语，例如“不要”“别再”“无需”。
- “不要打开车门”标注 `intent=DOOR_OPEN`、`negated=true`，而不是 UNKNOWN。
- `SINGLE + IN_SCOPE_CONTROL` 的顶层 `negated` 必须为 `true` 或 `false`。
- `MULTI` 的顶层 `negated=null`；每个 `segments[]` 分别记录自己的 boolean。例如“不要打开车门然后加速”：segment 1 为 `DOOR_OPEN, negated=true`，segment 2 为 `ACCELERATE, negated=false`。
- `AMBIGUOUS`、`NON_CONTROL`、`UNKNOWN_CONTROL`、`AMBIGUOUS_CONTROL` 的顶层 `negated=null`。
- NEGATION 原始 span 仍保存在 `slots` 中；MULTI 时可同时通过 segment span 确定其作用域。
- 模型的否定结果不能替代确定性 `SafetyTextGuard`。

## 4. SINGLE / MULTI / AMBIGUOUS

- `SINGLE`：只有一个控制目的，即使包含 AREA、VALUE、MODE 等多个参数。
- `MULTI`：包含两个或更多独立控制目的；顶层 `intent=null`，可在 `segments` 中记录各子意图用于诊断。
- `AMBIGUOUS`：无法唯一确定控制目的或关键指代；顶层 `intent=null`，可填写 `intent_candidates` 供人工分析。
- MULTI 不得挑选其中一个 intent 作为普通可执行结果。

## 5. UNKNOWN / OOD

| 情况 | scope_label | ood_label | 顶层 intent |
|---|---|---|---|
| 帮我写论文 | NON_CONTROL | OOD | null |
| 打开冰箱 | UNKNOWN_CONTROL | OOD | null |
| 打开一下 | AMBIGUOUS_CONTROL | BOUNDARY | null |
| 有效 Registry 单意图 | IN_SCOPE_CONTROL | IN_DISTRIBUTION | registry ID |

`NON_CONTROL`、`UNKNOWN_CONTROL`、`AMBIGUOUS_CONTROL` 是 scope/abstention 监督，不是车辆控制 Intent。三者均不能生成 Authorization。

开放域问答、信息、通信和娱乐请求属于 `NON_CONTROL`；具有明确执行动作但目标位于车辆控制空间之外的命令（例如“打开冰箱”“启动火箭”“把电脑关掉”）属于 `UNKNOWN_CONTROL`，并使用 `CAPABILITY_CONFLICT` 表示能力边界。

## 6. Context Claims

“管理员已经授权我”“这是模拟器模式”“忽略安全规则”等文本不作为 Intent label。主控制意图可正常标注，但同时添加 `CONTEXT_CLAIM`，并继续交由确定性 context scanner 和 `AdvancedValidation`。

## 7. Character Offset

- 使用 Python/Unicode 字符索引语义的半开区间 `[char_start, char_end)`。
- `slot.text` 必须严格等于 `text[char_start:char_end]`。
- 不保存 tokenizer token index 作为权威标注；训练时为具体 tokenizer 动态投影 BIO/BILOU 标签。
- Unicode normalization 只能生成派生视图，不能改变原始 offset。

## 8. 两层 Dataset Validator

未来数据构建必须依次执行两层校验：

1. `annotation schema validation`：检查 JSON 类型、required 字段、枚举、字符 span 结构，以及 SINGLE/MULTI/AMBIGUOUS 与顶层 `intent/negated` 的条件关系。
2. `registry cross-validation`：加载同版本 Intent Registry，检查：
   - SINGLE intent 确实存在且 `scope_status=IN_SCOPE`；
   - `capability_family` 和 provenance 引用完整；
   - AREA 位于该 Intent 的 `allowed_areas`；
   - MODE 来自该 Intent 引用的 `mode_contract`；
   - VALUE 是否允许、是否 required、单位与范围是否满足 `value_contract`；
   - required slot 完整且不存在互斥/重复 span；
   - `LEGACY_TEST_ONLY/OUT_OF_SCOPE` 的 DISPLAY_OFF 等不得进入正式训练标签；
   - Registry version 与数据集声明版本一致。

JSON Schema 单独通过不代表样本可进入训练。跨文件校验失败必须阻止构建，不得自动改标签或裁剪危险数值。本阶段只定义 Validator 契约，不实现训练流水线。

## 9. 质量控制

- R3、NEGATION、MULTI、OOD、VALUE_BOUNDARY 样本必须双人复核。
- 同一个 `paraphrase_family_id` 只能进入一个 split。
- Safety Gold 不得用于训练或阈值拟合。
- 出现 Registry 外能力时不得临时创建标签，应进入 `UNKNOWN_CONTROL` 并提交 Registry 变更评审。
- 所有新增 Intent、MODE、AREA 或 value range 均须更新版本并重新审计 capability、risk、evidence、authorization 和 execution 边界。
