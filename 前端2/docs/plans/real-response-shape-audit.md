# 真实接口响应形状审计

采集时间：2026-08-04。后端：`http://127.0.0.1:8765`，车辆适配器 `simulator`，语音信任模式 `enforce`。

本文件只记录字段路径、类型、可空性和结构差异。采集过程未输出授权令牌；名称包含 `token` 或 `secret` 的字段仅记录类型，未记录值。

## 真实场景样本

| 场景 | 真实轮次 | 结果 |
|---|---|---|
| 文本 PASS | `TURN_d4b1692775e6` | HTTP 200 |
| 文本 REVIEW | `TURN_79ba543b4c8d` | HTTP 200 |
| 文本 BLOCK | `TURN_061df662c8e8` | HTTP 200 |
| 音频输入 | `TURN_ba7b33a039f8` | HTTP 200 |
| 复核修正子轮次 | `TURN_3ab71d60392a` | HTTP 200 |
| 取消终态 | `TURN_6ced9cdcb89f` | HTTP 200 |
| 模拟器执行 | 新 PASS 轮次原位执行 | HTTP 200，执行响应已采集 |
| 麦克风缺失设备 | 无轮次 | HTTP 422，`detail: string` |

## 接口形状与前端类型差异

### `POST /api/command/text`

真实顶层核心字段：

- `turn_id: string`
- `input_type: string`
- `accepted: boolean`
- `actionable: boolean`
- `transcription_result: object`
- `semantic_frame: object`
- `decision: object`
- `audit: object`
- `evidence_subgraph: object`
- `websocket_channel: string | null`

`decision.authorization_token` 为敏感可空字段，不得进入展示模型或浏览器存储。当前 `TextCommandResponse` 的核心字段基本一致，但接口层此前直接断言类型，且提交钩子只保留 `turn_id`，丢失了真实即时语义和裁决。

### `POST /api/command/audio`

真实顶层核心字段：

- `turn_id: string`
- `input_type: "audio"`
- `accepted: boolean`
- `voice_trust: object`
- `spectrum_analysis: object`
- `asr_result: object | null`
- `zone_permission: object | null`
- `semantic_frame: object | null`
- `decision: object`
- `audit: object`
- `pipeline: object | null`
- `websocket_channel: string | null`

真实转写位于 `asr_result.transcribed_text`，同时可在 `pipeline.transcription_result.transcribed_text` 出现。音频响应不是文本响应的同构别名，必须独立适配。

### `POST /api/command/microphone`

当前真实环境指定设备不存在时返回 HTTP 422，结构为 `{ detail: string }`。成功结构由冻结契约固定为音频响应结构，但本机未伪造成功结果。前端必须把 422 显示为真实失败并解除输入禁用。

### `GET /api/turns/{turn_id}/presentation`

普通、REVIEW、BLOCK、音频终止、复核子轮次和取消轮次均采集。稳定核心字段：

- `turn_id`, `created_at`, `updated_at`, `current_stage`, `processing_status`
- `input`, `semantic_frame`, `evidence_demand`, `retrieval_summary`, `evidence`
- `gate_result`, `score_result`, `validation_result`, `decision_result`
- `review`, `authorization`, `execution`, `audit`

结构差异主要发生在可空值和数组内容：音频字段可能为空；REVIEW 可能没有有效候选；取消和子轮次的 review/effective 状态不同；`audit.audit_id` 在已归档响应中是字符串。核心对象缺失必须报结构异常，不能渲染为“暂无”。

### `GET /api/turns/{turn_id}/workflow-status`

真实响应为对象，包含根轮次、当前/最新轮次、工作流状态、终态、复核、授权和执行相关字段。状态值随 PASS、REVIEW、CANCEL、AUTHORIZED、EXECUTED 等场景变化，未知枚举应原样安全显示。

### `GET /api/turns/{turn_id}/timeline`

真实响应为对象，核心为 `turn_id` 和 `items: array`。时间线项含 `sequence`、`stage`、`timestamp`、`status`、`summary`，并可能含 `event_id`、`audit_id` 或关联轮次。空数组表示已加载但本轮没有持久事件，不等于请求失败。

### `POST /api/turns/{turn_id}/review`

真实修正和取消响应核心字段：

- `original_turn_id`, `review_turn_id`, `root_turn_id`, `related_turn_id`
- `user_action`, `action`, `new_decision`
- `accepted`, `message`, `reason`
- `workflow_status`, `decision`
- `token_issued`, `execution_status`, `audit_id`
- `review_question`, `command_result`

修正响应可能包含新的 `command_result`；取消响应的关联轮次与终态结构不同。原始授权令牌只可能存在于嵌套 `decision`，必须在一次性交接后清除。

### `GET /api/audits`

真实响应顶层为：

- `items: array`
- `total: integer`
- `page: integer`
- `page_size: integer`

普通记录项包含 `audit_id`、`turn_id`、`created_at`、`instruction_summary`、`initial_decision`、`original_decision`、`final_decision`、`execution_status`、`semantic_frame`。取消、复核终态和执行记录的深层对象可空性不同，因此列表必须先适配为扁平展示模型。

### `GET /api/audits/{audit_id}`

真实详情核心包含 `audit_id`、`turn_id`、`created_at`、输入/语义/证据/裁决、review、authorization、execution、workflow events 和链状态。普通记录、子轮次、取消及执行记录在 `effective_outcome`、`review_process`、`authorization_status`、`execution_status` 和转写字段上存在可空差异。单一区域缺失不应使整页崩溃。

### `GET /api/audits/{audit_id}/verify`

真实响应与当前类型一致：记录哈希、前序关联、审计链、工作流链、关系、裁决合并和有效终态均为布尔值；终态审计及其哈希字段允许为空；`failure_reason` 允许为空。

### `GET /api/audits/verify-chain`

当前真实响应明确为：

```text
{ valid: boolean }
```

当前后端并未返回 auditId 到布尔值字典。适配器支持测试固定的字典结构，但其他未知结构必须显示“响应结构异常”。

## 根因结论

1. 主要断裂不是冻结类型完全错误，而是 API 层直接断言、命令钩子丢弃即时响应以及组件直接读取深层字段。
2. 文本、音频和麦克风不能使用同一个响应提取路径。
3. presentation 的可空差异需要明确状态语义，不能统一显示“暂无”。
4. 审计不同记录类型的核心顶层相对稳定，深层 review/authorization/execution/effective outcome 差异必须在适配层消化。
5. 全局链当前是 `{ valid: boolean }`，页面不得在缺失 `valid` 时直接判异常，必须先经过适配器。
