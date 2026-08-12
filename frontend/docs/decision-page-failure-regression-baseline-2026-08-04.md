# 实时裁决页失败回归与诊断基线

日期：2026-08-04  
范围：仅测试基础设施、测试辅助模型和诊断基线；未修改生产实现。

## 运行方式

```powershell
Set-Location 'D:\语证\frontend'
npm.cmd run test:decision-regression
```

该命令当前预期返回非零退出码，因为回归套件用于锁定尚未修复的问题。既有测试可单独运行，当前为 10 个文件、60 项全部通过。

## 测试环境

- Vitest 4.1.10
- jsdom 30.0.1
- @testing-library/react 16.3.2
- @testing-library/user-event 14.6.3
- 组件/钩子测试按文件声明 `jsdom` 环境，不改变 Vite 生产配置。

## 15 项回归结果

| 编号 | 预期行为 | 当前实际结果 | 基线 |
|---:|---|---|---|
| 1 | 后端接受后输入框保留“帮我打开空调” | `draftResetVersion=TURN_B` 后值从原文本变为空字符串 | FAIL |
| 2 | `waiting_presentation` 可继续编辑 | `busy=true`，输入控件仍被禁用 | FAIL |
| 3 | `waiting_presentation` 禁止重复提交当前任务 | `busy=true`，当前已有重复提交保护 | PASS |
| 4 | TURN_A 切到 TURN_B 时不暴露 A 快照 | TURN_B 的首个渲染观察到 `TURN_A` | FAIL |
| 5 | TURN_A 迟到 presentation 不覆盖 TURN_B | TURN_B 保持为 `TURN_B` | PASS |
| 6 | 新提交开始后所有流程阶段回到等待 | 旧事件仍令 trust、semantic、decision 为 completed | FAIL |
| 7 | TURN_A 迟到事件不参与 TURN_B | store 没有 `eventsByTurn`，事件仍只有全局数组所有权 | FAIL |
| 8 | `REVIEW_REQUIRED` 显示等待复核 | 映射结果为 `completed` | FAIL |
| 9 | `AUDIT_SAVED` 仅代表审计归档 | execution 阶段被映射为 `completed` | FAIL |
| 10 | 未执行车辆前显示尚未执行 | 仅 `VEHICLE_PRECHECKED`/`TOKEN_CONSUMED` 已令 execution 为 `completed` | FAIL |
| 11 | 新建会话取消正在进行的指令请求 | reset 后请求信号 `aborted=false` | FAIL |
| 12 | 旧请求返回不得更新新会话 activeTurnId | 新会话被旧响应更新为 `TURN_OLD` | FAIL |
| 13 | TopNav 新会话重置 viewTurnId 和摘要 | viewTurnId 仍为 `TURN_A`，旧摘要仍显示 | FAIL |
| 14 | 连续四轮各自读取事件 | store 无按轮次事件集合，四轮仍共用扁平数组 | FAIL |
| 15 | 当前轮次最终结果不退回旧轮次或空白 | 缓存钩子层在迟到旧请求完成后仍保持当前结果 | PASS |

总计：12 FAIL，3 PASS。另有 5 项测试专用状态模型/安全诊断测试全部通过。

## 确定性问题

以下结论可直接由当前生产代码和可重复的本地测试确定，不依赖后端：

1. `draftResetVersion` 会清空文本。
2. `waiting_presentation` 被合并进单一 `busy`，导致编辑与提交一起禁用。
3. 缓存键切换的 effect 生效前会渲染旧键快照。
4. session store 只有扁平 `pipelineEvents`，没有按 turn 所有权。
5. `REVIEW_REQUIRED`、`AUDIT_SAVED`、预检查/令牌消费的阶段含义映射错误。
6. `reset()` 不会 abort 当前请求，也没有 generation/session epoch 防迟到写入。
7. TopNav 只调用 store 的 `newSession()`，DecisionPage 局部状态不会随 sessionId 自动归零。
8. `useTurnPresentation` 仅进行一次缓存读取；当前没有有限次数、递增间隔的重试调度。

## 仍需真实后端事件日志确认的部分

下列内容不影响上述代码级缺陷成立，但需要安全的真实事件日志才能确认线上触发频率和后端变体：

- TURN_A 事件是否会在 TURN_B 提交开始后迟到，以及实际 sequence 是否跨轮次/连接单调递增。
- 后端 `REVIEW_REQUIRED`、`AUDIT_SAVED`、`VEHICLE_PRECHECKED`、`TOKEN_CONSUMED` 的真实 status 与安全 payload 字段组合。
- 页面实测中 presentation 的 404/未归档持续时间、轮次切换顺序和最终结果回退是否发生。
- 连续四轮输入时 WebSocket 重连、补发、乱序和重复事件的真实顺序。

诊断辅助函数仅允许输出 sessionId 前八位、submissionGeneration、turnId、sequence、stage、status、请求生命周期及枚举化丢弃原因；不会输出授权令牌、原始音频、完整证据或响应对象。该辅助函数位于测试目录，尚未接入生产运行时。
