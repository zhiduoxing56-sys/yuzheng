# 四页面模拟器与知识检索可观测性实施计划

> 本计划以 `2026-08-16-four-page-simulator-knowledge-observability-design.md` 为唯一设计依据。先补只读合同与测试，再重构页面；不得改变正式 Knowledge Top-K、阈值或裁决行为。

## 阶段 0：基线与合同冻结

1. 记录四个正式页面的桌面/窄屏截图和现有前端测试基线。
2. 固定三条代表轮次：前照灯 PASS、右后自行车开门 BLOCK、夜间关灯 BLOCK。
3. 保存三条轮次的正式 Knowledge hits、EvidenceDemand、SafetyGate 和 final decision，作为无回归基线。
4. 为新的 presentation DTO 编写字段级合同测试，先失败后实现。

## 阶段 1：知识检索只读诊断合同

1. 定义按 intent occurrence 隔离的 Knowledge observability DTO：Query、K0-K3、included/excluded context。
2. 从现有 `IntentEvidenceDemand` 完整投影 `knowledge_query_text`、在线 raw results、阈值、context sources 和 demand sources。
3. 在正式 Knowledge service 内增加只读全 eligible 诊断方法，复用当前 query vector 和同一 HNSW index。
4. 诊断结果标记 `DIAGNOSTIC_ONLY`；在线结果标记 `ONLINE_TOP_K`。
5. 增加不变量测试，证明调用诊断前后正式 hits、动态需求、Gate、Decision 和 token 完全一致。
6. 记录 context projection 的排除项及原因，只增加审计元数据，不改变 included 字段。
7. 通过现有 turn presentation/API 返回稳定中文展示所需原始字段。

## 阶段 2：CARLA 当前上下文扩展

1. 盘点 CARLA adapter 可物理支持字段，形成唯一能力判断，不在前端复制硬编码事实。
2. 扩展当前 CARLA adapter/current state provider，使其可保存 CARLA 不支持字段的 SIMULATION observations。
3. 场景激活时拆分物理字段与仿真补充字段：前者调用 CARLA，后者进入同一 adapter 的当前仿真 Evidence。
4. 下一条独立 `/api/command/text` 从两类当前状态生成新 EvidenceNode。
5. 实现字段冲突拒绝、部分应用响应、reset/切换/更新清理语义。
6. 增加右后自行车、低能见度、道路摩擦等端到端测试。

## 阶段 3：模拟器页重构

1. 将 `CarlaPage` 改为 1/2 + 1/4 + 1/4 三列。
2. 左列保留直播画面、车辆状态和传感器状态。
3. 中列整理现有 CARLA 物理控制，不改变现有操作语义。
4. 右列新增仿真上下文表单，字段从后端能力/合同驱动，显示中文标签、单位和来源。
5. 增加场景选择、配置预览、应用明细、当前场景和跳转裁决。
6. 所有写操作采用逐字段反馈，显示物理成功、仿真补充、失败和冲突。
7. 增加响应式布局、键盘操作和 loading/error/empty 状态测试。

## 阶段 4：证据检索页重构

1. 删除页面上的四项索引参数修改和相关状态/API 调用。
2. 删除强制召回列表、AI 审计区域和相关页面状态/API 调用。
3. 左半实现 K0-K3 层列表、统计和层详情弹层。
4. 节点详情展示所有正式知识字段、排名、分数、阈值和动态贡献。
5. 右上实现按 occurrence 切换的完整 Query 面板。
6. 右下实现 Context 投影面板及“已进入查询/未进入查询”标签。
7. 建立统一中文枚举映射，同时保留原始值供复制与审计。
8. 处理无 turn、多意图、知识未就绪、诊断不可用和超长字段。

## 阶段 5：裁决页视觉层级调整

1. 将 final decision、SafetyGate、Evidence Alignment 和 merge reason放在主展示层。
2. 保留授权、确认和执行现有流程。
3. 将五维评分移动到默认折叠的诊断区域。
4. SafetyGate 阻断时展示“五维评分仅供诊断，不参与最终放行”。
5. 验证 score/final decision 字段没有因前端映射被混淆。

## 阶段 6：删除占位路由

1. 删除 `/demo`、`/system` 路由。
2. 删除 `DemoPage`、`SystemPage`。
3. 删除辅助菜单中的两个入口；保留四页面正式导航。
4. 增加路由回归，确认旧路径重定向到对应正式页面或 404，按产品选择固定一种。

## 阶段 7：视觉统一与验收

1. 只使用 `VisualPageShell` 与 `visual-pages.css` 白底蓝色体系。
2. 复用现有视觉变量、字体栈、section tab、按钮、表格、弹层和状态色。
3. 禁止引入旧深色 `AppShell/global.css` 组件样式或通用 AI Dashboard 风格。
4. 对四页执行桌面、常见笔记本和窄屏截图比对。
5. 检查中文标签、密度、换行、滚动、焦点、禁用态和错误态。

## 阶段 8：最终验证

1. 前端类型检查、单元测试和生产构建。
2. 后端 targeted tests、compileall、`git diff --check`。
3. 重跑三条正式 E2E，比较改造前后 hits、EvidenceDemand、Gate 和 Decision。
4. 验证动作泄漏为 0、诊断查询副作用为 0。
5. 人工验收模拟器场景设置、Query、K0-K3、Context 来源、PASS 执行和两个 BLOCK 场景。

## 建议提交拆分

1. `feat(api): expose read-only knowledge retrieval observability`
2. `feat(carla): persist unsupported scenario fields as simulation evidence`
3. `feat(ui): integrate scenario controls into carla page`
4. `feat(ui): replace evidence index controls with knowledge retrieval layers`
5. `refactor(ui): demote five-dimension score to diagnostics`
6. `chore(ui): remove hidden demo and system placeholders`
7. `test(e2e): verify four-page scenario and knowledge observability flow`

