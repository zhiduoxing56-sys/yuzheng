# 语证前端

React + TypeScript + Vite 前端。阶段三已经完成“实时安全裁决”，阶段四已经完成“证据检索与图谱导航”，阶段五已经完成“复核、授权、执行与工作流完整性”闭环，阶段六已经完成“审计列表、详情、完整性校验与安全导出”。所有业务展示均来自真实后端接口。

前端不重新计算安全评分、硬门、最终裁决、证据质量、可信度或因果结论。

## 安装与启动

```powershell
npm install
npm run dev
npm run test
npm run lint
npm run build
```

开发地址严格固定为 `http://127.0.0.1:5173`；端口占用时 Vite 会直接报错，不会漂移。开发环境使用相对 `/api` 和 `/ws`，由 Vite 代理到 `VITE_API_BASE_URL`，默认 `http://127.0.0.1:8765`。发布构建可通过 `/runtime-config.json` 配置完整 API 与 WebSocket 地址。

## 实时裁决闭环

`/decision` 支持文本、最大 20 MiB 原始音频和后端麦克风输入，展示八阶段实时事件、最终裁决、车辆状态、五维评分、安全门、时间线和工作流状态。每个 `sessionId` 最多一个 WebSocket；最终展示以 presentation 为唯一事实源。

获得真实 `turn_id` 后，所有轮次请求均支持取消。切换轮次或卸载页面会终止旧请求。localStorage 只保存 `sessionId`、当前 `turnId` 和最近轮次，不保存令牌、文件、表单、音频、错误或请求控制器。

## 证据检索与图谱导航

`/evidence` 优先使用 `sessionStore` 的当前轮次，其次使用最近轮次；`/evidence/{turnId}` 可直接加载并在刷新后恢复指定轮次。无效轮次留在证据页显示错误，不自动跳回实时裁决页。

页面并行加载文字摘要与真实证据子图，图谱依赖不会阻塞摘要。点击节点后才请求冻结节点详情接口；高级推理仅在用户展开对应区域时请求扩展接口。

四层展示以后端 `security_rank` 为唯一层级依据，并保留后端 `layer` 原始标签：

- 0：第零层，后端安全类 `ENTERTAINMENT`
- 1：第一层，后端安全类 `COCKPIT`
- 2：第二层，后端安全类 `DRIVING`
- 3：第三层，后端安全类 `EMERGENCY`

未分类节点进入独立区域，不伪装成四层之一。

节点状态映射：

- `VALID`：绿色可信
- `SUSPICIOUS`：橙色可疑
- `STALE`：橙褐色陈旧
- `TAMPERED`：暗红色篡改
- `MISSING`：灰色缺失

后端没有节点级 `CONFLICT` 状态。页面只根据真实 `CONFLICTS` 边和冲突记录显示红色冲突证据。

图谱支持当前子图内搜索、层级和状态组合筛选、强制/缺失/冲突/关键证据筛选、隐藏非关键边、节点点击、拖动、缩放、三维旋转、恢复视角、重新布局和全屏。筛选只改变显示，不修改原始数据或裁决。

“关键裁决证据”只合并后端明确返回的裁决引用、门控引用、推理支持/冲突编号、强制证据和真实规则/冲突关系，不声称是后端未定义的完整因果路径。

## 二维、三维与性能

证据路由、图谱面板、三维渲染器和二维渲染器分别懒加载。默认异步加载三维；依赖、WebGL 初始化或运行失败时，单次页面生命周期最多自动降级一次到二维，禁止循环降级。用户手动选择的模式保存在 sessionStorage，切换轮次时继续保留。

两个渲染器共享 `evidenceGraphAdapter` 的同一适配结果。各渲染器自行管理图形实例、动画循环、尺寸监听器和资源释放；切换轮次或离开页面会卸载旧渲染器。实时裁决主包不静态引用图谱代码。

## 复核、授权与执行闭环

`/review/{turnId}` 以地址中的 `turnId` 为唯一权威来源。缺失或无效轮次停留当前页面显示错误；页面刷新后重新读取真实 presentation、workflow-status、timeline 和工作流链，不依赖 WebSocket 历史。复核产生子轮次时，先同步 `sessionStore.currentTurnId`，再以 `replace` 更新为最新子轮次地址并取消父轮次读取。父轮次只在来源信息和时间线中保留，不能继续写入。

复核公开请求遵守冻结契约的字段互斥规则：

- `CONFIRM`：只发送 `action` 与当前轮次真实 `selected_candidate_id`；没有后端 `VALID` 候选时禁用。
- `CORRECT`：只发送 `action` 与去除首尾空白的 `corrected_text`，长度不超过后端限制 2048 字符；结果必须等待后端完整重新裁决。
- `CANCEL`：只发送 `action`，经危险操作确认后终止工作流，不签发授权也不执行动作。

复核写请求使用 `idle → validating → confirming/submitting → refreshing → completed/failed` 状态机，禁止双击和自动重试。成功后固定按 presentation → workflow-status → timeline → workflow-chain 的顺序刷新；读取请求支持取消和手动刷新。

授权区域只展示后端返回的非敏感元数据。原始授权令牌只可能由首次裁决或复核响应返回一次，通过一次性回调直接进入执行钩子的私有 `ref`：

- 不完整展示，也不允许复制或手工输入；
- 不进入控制器状态、组件 props、sessionStore、localStorage、sessionStorage、URL、控制台、错误日志或测试快照；
- 执行成功或后端明确表明令牌已使用、过期、撤销、拒绝时立即清除；
- 页面刷新或离开后无法恢复，前端不会伪造新令牌。

`POST /api/turns/{turn_id}/execute` 是高风险扩展接口。执行入口同时依赖后端最新轮次、`AUTHORIZED` 工作流、`ISSUED` 授权、`authorization.execution_allowed`、未消费、未执行、非终态及当前内存令牌。前端不把 PASS 裁决自行等同于可执行。确认窗口显示健康接口提供的真实适配器模式；执行结果再使用 `execution.simulated` 区分仿真和非仿真结果。当前已识别 `simulator`、bench 类适配器和 CAN/vehicle 类适配器；未知值明确标为未知模式。

执行请求不自动重试。超时或网络中断时页面标记“结果待确认”，重新按固定顺序查询后端状态，禁止直接判定成功或失败。一次性令牌由后端原子消费，即使车辆适配器随后失败也不能重用。

工作流链校验展示后端真实的 `root_turn_id/valid/event_count/failure_event_id`。链异常会醒目告警；由于当前后端未把链校验字段定义为执行门，前端不会擅自修改执行资格。

## 审计列表与详情

`/audits` 使用后端服务端分页，地址栏是筛选和分页状态的唯一来源。公开参数为 `page`、`page_size`、`decision`、`start_time` 和 `end_time`；非法参数回退默认值，时间范围无效时在本地阻止请求。筛选、翻页、刷新及浏览器前进后退均从地址恢复，不向 `sessionStore` 增加审计状态。请求更新期间保留最近成功列表，快速切换会取消旧请求并阻止迟到响应覆盖。

`/audits/{auditId}` 以地址中的 `auditId` 为唯一详情来源，按“指令理解 → 证据核对 → 决策依据 → 安全告警 → 复核 → 授权 → 执行 → 关联轮次 → 时间线 → 完整性 → 导出”展示真实审计解释链。列表进入详情时会保留经过校验的列表参数；这些参数只构造返回地址，不参与详情、校验或导出请求。直接访问详情不会强制附加列表参数。

详情只展示后端已有证据需求、召回、缺失、强制召回、冲突、质量与裁决引用，不重新渲染三维图谱，也不生成节点级冲突状态。证据编号和关联轮次可进入对应轮次的证据、复核或实时裁决页面。原始工作流载荷与哈希默认折叠，缺失字段明确显示空状态。

单条完整性面板调用后端校验接口，展示记录哈希、前序链接、审计链、工作流链和终态关系结果；进入详情后校验一次，也支持手动重新校验，不轮询、不在前端重算哈希。列表页的全局链摘要只展示后端当前提供的 `{ valid }`，并明确标记前端收到本次结果的时间；接口没有提供校验记录数和异常数，页面不伪造统计。

审计导出只在用户主动点击后请求。当前后端返回 JSON 且已脱敏，前端仍在生成 Blob 前递归删除字段名包含 `token`、`authorization_token` 或 `secret` 的内容。原始对象和脱敏对象均不写入控制台或错误日志，授权令牌不展示、不复制、不进入浏览器存储。

## 接口边界

阶段三使用的冻结公开接口：

- `POST /api/command/text`
- `POST /api/command/audio`
- `GET /api/turns/{turn_id}/presentation`
- `GET /api/turns/{turn_id}/timeline`
- `/ws/pipeline/{session_id}`

阶段四使用的冻结公开接口：

- `GET /api/turns/{turn_id}/presentation`
- `GET /api/turns/{turn_id}/evidence/{node_id}`

阶段五使用的冻结公开接口：

- `GET /api/turns/{turn_id}/presentation`
- `POST /api/turns/{turn_id}/review`

阶段六使用的冻结公开接口：

- `GET /api/audits`
- `GET /api/audits/{audit_id}`
- `GET /api/audits/{audit_id}/verify`

阶段三使用的扩展接口：

- `GET /api/health`
- `GET /api/state`
- `POST /api/command/microphone`
- `GET /api/turns/{turn_id}/workflow-status`

阶段四使用的扩展接口：

- `GET /api/evidence/turn/{turn_id}`
- `GET /api/turns/{turn_id}/reasoning`（按需加载）

阶段五使用的扩展接口：

- `GET /api/turns/{turn_id}/workflow-status`
- `GET /api/turns/{turn_id}/timeline`
- `GET /api/turns/{turn_id}/verify-workflow-chain`
- `POST /api/turns/{turn_id}/execute`（高风险）

阶段六使用的扩展接口：

- `GET /api/audits/{audit_id}/export`
- `GET /api/audits/verify-chain`

扩展接口没有被标记为冻结 v1 公共契约。

## 已完成与未完成

已完成阶段三实时裁决、阶段四证据图谱、阶段五复核授权执行和阶段六审计追踪闭环。当前没有实现：

- 场景控制台
- 系统维护操作

下一阶段建议实现独立场景演示控制台；本阶段按约束停止，不提前进入该范围，也不实现系统维护操作。

设计记录：

- `docs/plans/2026-08-04-stage3-realtime-decision-design.md`
- `docs/plans/2026-08-04-stage4-evidence-graph-design.md`
- `docs/plans/2026-08-04-stage5-review-authorization-execution-design.md`
- `docs/plans/2026-08-04-stage6-audit-tracking-design.md`

旧静态入口位于 `legacy/`，不参与 Vite 构建。
