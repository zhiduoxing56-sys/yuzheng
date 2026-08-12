# 阶段三实时安全裁决闭环设计

## 目标与边界

本阶段只修改 `frontend`，把实时安全裁决页接入健康检查、车辆状态、文本/音频/后端麦克风指令、WebSocket、轮次展示、时间线和工作流状态。最终裁决、评分、安全门、授权和执行状态均只展示后端返回值。

不实现证据图谱、审计详情、系统维护、复核提交或执行按钮，也不修改后端业务代码和冻结契约。

## 方案

采用“页面编排 + 专用 Hooks”：

- `DecisionPage` 只组合组件、传递数据并汇总区域状态。
- 健康、车辆、实时连接、轮次展示、时间线、工作流各由独立 Hook 管理。
- 指令校验、三种提交方式和统一提交状态机由 `useCommandSubmission` 管理。
- `sessionStore` 只保存跨页面状态：会话、当前/最近轮次、实时事件和连接状态。
- 文件、表单、局部错误、局部加载状态和请求控制器保持局部。

## 依赖方向

```text
types / constants / config
  -> api / utils
    -> hooks / sessionStore
      -> components
        -> DecisionPage
```

组件不反向引用 Hooks；API 不引用 Store；Store 只引用契约类型，因此不存在循环依赖。

## 数据流

1. `sessionId` 创建或恢复后，`usePipelineSocket` 建立唯一实时连接。
2. 输入面板把局部表单数据交给 `useCommandSubmission`。
3. Hook 校验健康状态、输入和高级 JSON，然后调用真实命令接口。
4. HTTP 响应中的 `turn_id` 写入 Store，并保留最近轮次。
5. 轮次变化触发 presentation、timeline、workflow-status 和车辆状态请求。
6. presentation 是最终裁决的唯一事实源；实时事件只驱动阶段进度和事件详情。
7. 刷新后从 localStorage 恢复 `sessionId`、`currentTurnId` 和最近轮次，再重新拉取持久结果。

## 异步和错误

- 所有轮次请求使用 `AbortController`，轮次变化和卸载时取消。
- presentation 使用有限递增退避，不无限轮询。
- 健康检查每 10 秒刷新，失败只显示在健康区域。
- 时间线、车辆和工作流错误保持局部，不使整个页面失效。
- WebSocket 按 `event_id` 去重、按 `sequence` 排序，非法事件被忽略并在开发模式记录。
- 音频文件采用集中定义的 20 MiB 硬限制，不保存原始字节。

## 实施计划

1. 修正端口、代理、运行时地址、真实 TypeScript 契约和 API 返回类型。
2. 收紧 Session Store 的长期状态边界并实现刷新恢复。
3. 实现六个数据 Hook、实时连接 Hook 和指令提交 Hook。
4. 实现输入、八阶段进度、裁决、车辆、评分、安全门、时间线和事件抽屉组件。
5. 重构 `DecisionPage`、补充响应式样式和 README。
6. 执行 lint、build，并使用真实后端验证 PASS、REVIEW、BLOCK 以及音频/麦克风错误路径。

## 风险

- 后端麦克风依赖运行后端的主机设备与权限，前端只能准确展示真实结果或错误。
- WebSocket 不回放历史；刷新后恢复持久结果并明确提示实时过程不可回放。
- `workflow-status` 属扩展接口，前端必须继续与冻结公开接口区分。
