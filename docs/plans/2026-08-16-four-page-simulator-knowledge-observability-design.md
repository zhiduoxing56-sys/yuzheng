# 四页面模拟器与知识检索可观测性设计说明

## 背景与目标

当前正式前端只有四个主页面：裁决、证据检索、审计记录、模拟器。代码中的 `/demo` 与 `/system` 是隐藏占位路由，不属于正式信息架构。

本设计完成以下收口：

1. 保持四页面，不新增第五、第六个页面；删除两个隐藏占位路由及页面。
2. 在现有 CARLA 模拟器页内同时提供“CARLA 物理控制”和“CARLA 暂不支持的仿真上下文设置”。
3. 两类设置都通过正式状态/Evidence 链成为下一条指令的车辆上下文，并保留真实来源。
4. 将证据检索页的主视图从 Evidence HNSW 参数和强制召回，重构为 Knowledge Query、K0-K3 知识检索分层、阈值和上下文来源追踪。
5. 保持正式 Knowledge HNSW、Top-K、相似度阈值和裁决行为不变；全 eligible 排名仅作为无副作用诊断数据。
6. 裁决页突出最终裁决、安全门和证据对齐；五维评分保留但降级为诊断信息。
7. 审计页本轮不修改。

## 现状与约束

- 正式主导航为 `/decision`、`/evidence`、`/audits`、`/carla`。
- `/demo`、`/system` 仅为占位组件，正式导航不可见。
- CARLA 页已有实时画面、车辆状态轮询、天气、车速、挡位、灯光、障碍物、交通灯和 reset 控制。
- 当前 Knowledge 检索元数据包含正式 Top-K 原始结果、阈值、eligible 数量和 included context source，但前端展示合同丢失了部分字段。
- 当前未记录完整 excluded context；需要增加只读可观测元数据，但不得改变 Query 投影结果。
- `top_k=5`，部分动作的 eligible 节点超过 5 个（例如 BRAKE 为 11 个），因此正式 Top-K 不能直接冒充全 eligible 排名。
- 不新增第二套 Context/Scene/Evidence 模型；复用当前 adapter、VehicleState、EvidenceRepository 和正式 Knowledge 查询链。

## 方案对比

### 方案一：仅补前端

- 优点：修改小。
- 缺点：CARLA 细粒度上下文无法持久化；全 eligible 排名和 excluded context 没有真实数据，不能满足验收。

### 方案二：前端重构 + 只读诊断合同（采用）

- 优点：正式检索和裁决不变；页面能够完整解释真实在线结果；支持全 eligible 诊断排名。
- 缺点：需要小范围扩展后端 presentation/diagnostic contract，并严格证明诊断查询无裁决副作用。

### 方案三：正式 Top-K 改为全部 eligible

- 优点：实现表面简单。
- 缺点：改变正式检索、动态 EvidenceDemand 和安全行为，违反冻结边界，不采用。

## 信息架构

| 页面 | 正式职责 |
|---|---|
| 裁决 | 命令输入、SemanticFrame、SafetyGate、证据对齐、最终裁决、确认与执行 |
| 证据检索 | Knowledge Query、K0-K3、全 eligible 诊断排名、阈值、Context 投影、最终 EvidenceDemand |
| 审计记录 | 事后审计、授权、执行、证据链；本轮不修改 |
| 模拟器 | CARLA 实时画面、车辆/传感器状态、物理控制、仿真上下文和场景预设 |

删除 `/demo`、`/system`、对应占位页面和辅助菜单入口。

## 模拟器页设计

### 布局

桌面宽屏采用 `1/2 + 1/4 + 1/4`：

- 左侧 1/2：CARLA 实时画面、当前车辆状态、当前传感器状态。
- 中间 1/4：CARLA 支持的物理控制。
- 右侧 1/4：CARLA 暂不支持、但可作为正式车辆上下文的仿真设置。

窄屏按现有响应式风格依次折叠为单列，物理控制始终排在仿真补充之前。

### CARLA 支持区

保留并整理现有能力：天气、车速、挡位、前照灯、障碍物、交通灯、复位。设置后必须经过 CARLA API/adapter 回读，再生成正式 Evidence；不得仅在前端乐观显示成功。

### 仿真上下文区

覆盖 Evidence Space 已支持、但 CARLA 当前无法精确物理构造或观测的字段，例如：

- 周边目标：region、entity_kind、distance、relative_speed、motion_state、risk_level。
- 环境：visibility、precipitation、fog。
- 道路：road_condition、wetness、正式摩擦参数。
- SYSTEM_MODE、AUTHORIZATION_STATE。

这些值：

- 进入当前 adapter 的持久化 Simulation observation；
- 下一条独立 `/api/command/text` 重新生成新 EvidenceNode；
- `source=SIMULATION`，界面显示“仿真补充，不改变 CARLA 物理画面”；
- 不允许冒充 CAMERA/RADAR/LIDAR/CARLA sensor。

### 合并与冲突

- CARLA 能真实提供的字段由 CARLA 当前值负责，不在仿真区重复开放。
- 同一正式字段不得同时被 CARLA 和 SIMULATION 手工覆盖。
- CARLA 后续支持某字段后，该字段从仿真区迁入物理控制区。
- 场景切换、reset、相关状态更新清理或替换旧仿真上下文。
- 缺失、无效、过期、不可用值不进入 Knowledge Query。

### 场景预设

场景预设在两个右侧控制列顶部共用。一次应用拆分展示：

- 已应用到 CARLA 的物理字段；
- 已写入 SIMULATION context 的补充字段；
- 未支持、无效或冲突字段及原因；
- 当前场景、激活时间、状态刷新结果；
- 前往裁决页入口。

## 裁决页设计

五维评分仍产生 `score_decision`，但最终裁决采用保守合并：SafetyGate 硬阻断优先，其次为 Evidence Alignment 和其他约束，最后才可能保持五维评分结果。因此主视觉顺序调整为：

1. final_decision；
2. SafetyGate 状态、命中规则、证据和原因；
3. Evidence Alignment、必需证据缺失/无效/过期情况；
4. score_decision、final_decision、decision_sources 和合并原因；
5. 授权与执行状态。

五维评分保留为折叠的“诊断评分（不覆盖安全门）”，显示五项值、权重、贡献、总分、score decision 和 evaluation mode。SafetyGate 阻断时明确提示其不参与最终放行。

## 证据检索页设计

### 删除

- M、ef_construction、ef_search、layer_count 四项页面手工修改。
- 参数应用操作。
- 强制证据召回区域。
- 强制召回 AI 审计区域。
- Evidence HNSW 物理层作为页面主视图。

后端索引参数和原有能力不删除，只是不再由该正式页面修改。

### 页面布局

- 左半：Knowledge K0-K3 分层。
- 右上：完整 Knowledge Query 面板。
- 右下：查询上下文投影，包含“已进入查询”和“未进入查询”两个中文标签。

### K0：第一层·动作匹配知识

显示当前 intent occurrence 的全部 eligible KnowledgeNode、节点总数、动作完全匹配状态和动作泄漏数。

### K1：第二层·语义相似度排序

显示全部 eligible 节点的诊断排名，并区分：

- `ONLINE_TOP_K`：正式检索实际返回；
- `DIAGNOSTIC_ONLY`：无副作用全量诊断查询结果，不进入裁决。

字段包括排名、similarity、HNSW label、正式 Top-K、ef_search、编码模型和向量维数。

### K2：第三层·相似度阈值筛选

显示 similarity、正式 threshold、差值和中文状态：已命中、低于阈值、未进入正式 Top-K。

### K3：第四层·动态证据需求

显示正式命中节点、固定 EvidenceDemand、知识追加 required/optional evidence、合并后的最终需求，以及每个动态需求对应的知识节点来源。

### 分层节点详情

点击某层后展示该层看到的全部节点。每个节点可展开查看：node_id、标题、类型、canonical action、semantic description、conditions、required evidence、optional evidence、trust、source、chapter、clause、HNSW label、排名、similarity、Top-K 状态、阈值状态和动态证据贡献。

## Query 面板

多意图按 `clause_index + intent_id` 独立切换，显示中文标签：

- 原始用户指令、意图编号、规范动作、规范对象、区域、模式、数值、方向；
- 完整知识检索查询句 `knowledge_query_text`；
- 知识增强后的证据检索查询句 `query_text`；
- 编码模型、向量维数、eligible 数量、正式 Top-K、阈值、状态、耗时和降级状态。

## Context 投影面板

### 已进入查询

显示查询字段、查询值、evidence_type、node_id、source、source_field、timestamp、validity/quality、availability 和 freshness。

### 未进入查询

显示字段、当前值、evidence_type、node_id、source、source_field 和排除原因。中文映射至少包含：

- `NOT_RELEVANT_TO_CURRENT_DEMAND`：与当前证据需求无关；
- `UNAVAILABLE`：当前不可用；
- `INVALID`：证据无效；
- `STALE`：证据已过期；
- `DUPLICATE_OR_LOWER_PRIORITY`：重复或来源优先级较低。

原始枚举保留在数据合同中，中文只属于展示层。

## 后端只读诊断合同

扩展现有 turn presentation，不建立第二套业务查询：

- 完整透传 `knowledge_query_text`、`knowledge_retrieval_metadata`、`knowledge_demand_sources`。
- 增加 K0-K3 的稳定 presentation DTO。
- 增加 excluded context 的可观测记录，禁止改变实际 Query 选择结果。
- 增加全 eligible 诊断 HNSW 查询；必须与在线 Top-K 分开标记，结果不写入 `knowledge_hits`、EvidenceDemand、SafetyGate、Decision 或 Authorization。
- 每个展示项绑定 turn_id、clause_index 和 intent_id，禁止跨意图合并。

## 视觉设计硬约束

四个页面继续使用当前 `VisualPageShell` 和 `visual-pages.css` 的白底蓝色视觉体系，不混用旧 `AppShell/global.css` 的深色体系。

必须复用：

- 色彩变量：`--visual-blue`、`--visual-deep-blue`、`--visual-line`、`--visual-pale`、`--visual-pale-strong`、`--visual-ink`；
- 正文字体：`Microsoft YaHei`、`PingFang SC`；
- 标题字体：`STZhongsong`、`SimSun`；
- 当前页面边框、圆角、阴影、渐变标题、section tab、按钮、表格、弹层和状态色；
- 当前 PASS/REVIEW/BLOCK 成功、警告、危险语义。

禁止：

- 浏览器默认控件直接裸露；
- 通用 AI Dashboard 模板风格；
- 新增无来源的紫色渐变、霓虹、玻璃拟态、过度发光；
- 使用 emoji 代替现有图形语言；
- 同页混入深色旧主题；
- 为追求视觉效果降低表格密度、字段完整性或可审计性。

新增组件先从现有 class 和组件抽取可复用模式；确需新增样式时延续现有尺寸、线宽、圆角和响应式断点。

## 异常与边界处理

- 没有当前 turn：显示现有空状态，引导先提交指令。
- Knowledge 未就绪或诊断失败：保留正式在线结果，单独显示诊断不可用原因。
- 场景部分应用：逐字段显示成功/失败，禁止整体伪报成功。
- CARLA 断连：物理控制禁用，已有 SIMULATION context 不冒充 CARLA 状态。
- 多意图：每个 occurrence 独立切换，排名和来源不串联。
- 超长 Query、条件和节点详情：可换行、可复制、表格横向滚动，不截断审计信息。

## 测试策略

### 后端

- CARLA 支持字段回读并进入当前轮 Evidence。
- CARLA 不支持字段以 SIMULATION 持久化并在独立命令轮生成新 node_id/turn_id。
- reset、场景切换和状态更新清理规则。
- 全 eligible 诊断查询不改变正式 knowledge_hits、EvidenceDemand、SafetyGate 和 Decision。
- K0-K3、included/excluded context DTO 完整且多意图隔离。

### 前端

- 保持四个导航入口，两个隐藏路由不可访问或重定向。
- 模拟器三列布局和响应式折叠。
- 物理控制/仿真补充来源标识、部分成功和错误状态。
- K0-K3 层切换及全部节点详情。
- Query、中英文枚举映射、included/excluded context。
- 删除参数修改和强制召回 UI 后无残留调用。
- 裁决页五维评分降级但数据不丢失。
- 视觉回归截图覆盖四页关键状态。

## 验收标准

1. 正式导航始终只有四页。
2. CARLA 支持与不支持设置分别占右侧两个 1/4 区域。
3. 两类设置都能成为下一条独立指令的正式、可追溯上下文。
4. 证据检索页完整显示 K0-K3、Query、全 eligible 排名、阈值和 Context included/excluded。
5. 全量诊断不改变正式 Top-K 或任何安全结果。
6. 五维评分不再主导视觉层级，但诊断数据完整保留。
7. 审计页无行为变更。
8. 新界面与当前白底蓝色前端在配色、字体、间距、圆角、阴影和交互上保持一致，不出现默认 AI 风格。

