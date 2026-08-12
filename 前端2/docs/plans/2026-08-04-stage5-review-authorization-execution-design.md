# 第五阶段：复核、授权、执行与工作流完整性闭环设计说明

## 背景与目标

第五阶段在既有实时裁决与证据图谱之上，完成真实的复核、重新裁决、授权、执行和工作流链展示。页面只消费后端真实字段，不生成候选、裁决、授权令牌或执行结果。实施范围限定在 `frontend`，不进入审计、演示和系统维护阶段。

## 现状与契约约束

- 复核公开请求仅允许 `action`、`selected_candidate_id`、`corrected_text`；额外字段被拒绝。
- `CONFIRM` 只接受当前最新轮次中持久化且 `VALID` 的候选，必须提交 `selected_candidate_id`。
- `CORRECT` 只提交去除首尾空白后的 `corrected_text`，最大 2048 字符，并创建完整重裁决子轮次。
- `CANCEL` 只提交 `action`，追加终态审计，不签发令牌且禁止继续操作。
- 复核响应通过 `related_turn_id/review_turn_id` 返回实际轮次；原始授权令牌只可能出现在首次响应的 `decision.authorization_token` 中，查询接口不会恢复。
- 执行令牌绑定轮次、动作、目标和车辆状态，后端执行前会完整复查，并以原子事务消费；消费后即使适配器失败也不可重用。
- `workflow-status`、`timeline`、`verify-workflow-chain`、`execute` 是扩展接口；链校验不是后端定义的执行门，不由前端擅自升级为业务阻断。

## 方案对比

### 方案一：页面控制器编排与专用钩子（采用）

- 优点：页面轻量；查询、写入、令牌、刷新和路由职责清晰；便于取消请求和局部测试。
- 缺点：需要明确刷新协议和回调边界。

### 方案二：页面直接协调独立钩子

- 优点：少一个控制器文件。
- 缺点：页面会持有过多副作用、刷新顺序和令牌交接逻辑。

### 方案三：单一 reducer 管理完整工作流

- 优点：状态转换集中。
- 缺点：查询与写入高度耦合，令牌更容易进入共享状态，职责边界过重。

## 推荐方案

采用方案一。`ReviewPage` 只组合组件，`useReviewPageController` 通过回调和刷新版本协调专用钩子。专用钩子互不导入，依赖方向保持为 URL → 控制器 → 钩子 → API/映射器。

## 详细设计

### 架构与状态归属

- URL 中的 `turnId` 是唯一权威轮次来源。
- `sessionStore` 只同步 `currentTurnId` 和最近轮次，不保存令牌、表单、错误或请求控制器。
- `useReviewTurn` 管理 presentation 与 workflow-status 的读取状态。
- `useReviewTimeline` 管理时间线读取、取消和手动刷新。
- `useWorkflowChainVerification` 管理链校验读取、取消和手动刷新。
- `useReviewSubmission` 管理三种操作、表单校验和 `idle/validating/confirming/submitting/refreshing/completed/failed` 状态机。
- `useTurnExecution` 通过私有 `ref` 保存当前轮次的一次性令牌，管理确认、提交、结果不确定和清除逻辑。
- `useReviewPageController` 只组合钩子、维护刷新版本并协调路由，不持有令牌。

### 令牌生命周期

1. 复核响应到达后，复核钩子只读取 `decision.authorization_token`。
2. 通过一次性回调把 `{ turnId, token }` 直接交给 `useTurnExecution` 的私有 `ref`。
3. 交接后复核钩子立即释放局部响应/令牌引用，不把含令牌响应放入 React 状态。
4. 令牌不经过控制器状态、组件 props、sessionStore、URL、浏览器存储、控制台、错误消息或测试快照。
5. 执行成功、令牌明确过期/撤销/消费/拒绝、轮次不匹配或页面卸载时清除 `ref`。
6. 网络超时或结果不确定时保留引用但锁定自动重发，先按固定顺序查询后端状态，再依据真实状态决定是否仍可手动重试。
7. 页面刷新或离开页面后令牌不可恢复；即使后端仍显示 `ISSUED`，也明确提示缺少本次内存令牌。

### 数据流与刷新顺序

初始和手动刷新严格串行执行：

1. presentation
2. workflow-status
3. timeline
4. workflow-chain

任一读取失败只记录到对应区域，后续读取继续执行。切换轮次时增加读取世代并终止父轮次的全部读取请求。

复核成功流程：令牌交接 → 清除表单 → `setCurrentTurn(newTurnId)` → `navigate('/review/newTurnId', { replace: true })` → 父轮次读取取消 → 新轮次统一刷新。若后端继续使用原轮次，则只递增刷新版本。

执行完成或结果不确定时，执行钩子通知控制器触发统一刷新。写请求不自动重试，也不因 Strict Mode、卸载或路由变化重复发送。

### 执行资格

执行入口只在所有后端事实同时满足时开放：

- URL 轮次等于 `workflow.current_turn_id`；
- workflow 非终态、状态为 `AUTHORIZED`、令牌状态为 `ISSUED`；
- presentation 授权已签发、状态为 `ISSUED`、`execution_allowed=true`、`consumed=false`；
- presentation 的执行状态为 `NOT_EXECUTED`；
- 私有 `ref` 中存在同一轮次的真实令牌；
- 当前没有复核或执行写请求。

这些条件只组合后端状态，不重新计算裁决。工作流链失败显示醒目告警，但不额外改变执行资格。执行确认使用健康接口的真实 `vehicle_adapter` 映射仿真、台架、车辆或未知模式；执行后以 `ExecuteResult.execution.simulated` 和刷新后的状态为准。

### 组件

- `ReviewTurnHeader`：轮次、来源、当前裁决及返回/证据链接。
- `RecognitionResultPanel`、`ReviewReasonPanel`：输入、转写、语义和真实复核原因。
- `CandidateCommandList`、`CorrectionEditor`、`ReviewActionPanel`：候选选择、修正文案、三种互斥动作与确认弹窗。
- `ReviewResultPanel`：后端刷新后的裁决与最近复核摘要。
- `AuthorizationPanel`、`ExecutionPanel`：非敏感授权元数据、执行资格、高风险确认和真实结果。
- `WorkflowStatusPanel`、`WorkflowChainPanel`、`ReviewTimelinePanel`：状态、完整性和持久化事件。

组件只接收非敏感展示状态与动作回调；授权令牌不作为 props。

### 异常与边界处理

- 无效或缺失 turnId 停留当前页面，显示不可复核，不重定向。
- 父轮次和终态轮次可查看但不提供写操作。
- 表单错误、复核错误、执行错误、时间线错误和链校验错误分别展示。
- CONFIRM/CORRECT/CANCEL 请求体由判别联合构造，互斥字段不会同时发送。
- 执行 HTTP 超时或网络中断标记为“结果待确认”，禁止直接显示成功或失败，并立即重新读取四类状态。
- 409、令牌过期、消费、撤销或无效等后端错误按真实消息展示，但不包含请求令牌。
- 复核和执行请求使用同步锁防双击；读取请求支持取消，写请求不自动重试。

### 测试策略

- 纯函数测试：三种请求体、字段互斥、空修正、2048 字符边界、状态中文映射、执行资格和路由目标。
- 安全测试：令牌拆分后不进入公开响应、存储、日志和快照；页面/控制器类型不包含令牌。
- 钩子/控制器测试：新子轮次先同步 store 再 replace、父请求取消、统一刷新顺序、Strict Mode 不重复写入、超时后重查。
- 真实验证：使用运行中的真实接口覆盖待复核、CONFIRM、CORRECT、CANCEL、授权、执行、重复执行、刷新恢复和链校验；无法安全构造的异常场景如实记录。
- 最终运行 `npm.cmd run test`、`npm.cmd run lint`、`npm.cmd run build`，并确认后端业务文件没有本阶段新增修改。

## 风险与已确认事项

- 原始令牌只返回一次，刷新后无法恢复是后端安全设计，不通过前端缓存绕过。
- 新子轮次使用 `replace`；父轮次仅作为来源和时间线信息只读保留。
- 统一刷新必须按固定顺序执行，可能比并行读取稍慢，但状态关系更可解释。
- 当前 `writing-plans` 技能不可用，实施步骤由项目工作计划承接。
