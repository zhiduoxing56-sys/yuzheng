# 审计写路径性能回归修复结果

## 结论

在 contract 1.0.0 响应正文、`AuditRecord` 字段、规范化规则、哈希算法、哈希链语义和 SQLite 持久化安全参数不变的前提下，“变道并加速”的最终受控 1 次预热 + 5 次正式测试结果为：

| 指标 | 修复前平均 | 修复后平均 | 修复后 P50 | 修复后 P95 / 最大 |
|---|---:|---:|---:|---:|
| HTTP 端到端 | 19,092.63 ms | 502.49 ms | 502.34 ms | 527.46 ms |
| 核心裁决 | 79.33 ms | 43.74 ms | 42.79 ms | 48.22 ms |
| 核心裁决完成到令牌签发 | 15,619.05 ms | 404.18 ms | 404.21 ms | 424.39 ms |
| 审计对象构建 | 不可用 | 0.17 ms | 0.16 ms | 0.21 ms |
| 审计规范化与序列化 | 不可用 | 182.03 ms | 180.86 ms | 207.53 ms |
| 审计哈希 | 不可用 | 6.24 ms | 5.87 ms | 7.31 ms |
| SQLite 事务与 commit | 不可用 | 59.98 ms | 58.17 ms | 76.46 ms |
| 响应模型编码 | 不可用 | 26.37 ms | 23.01 ms | 39.38 ms |

修复后 HTTP 平均耗时降低 97.37%，`post_decision_ms` 平均降低 97.41%。`core_decision_ms` 没有退化。

## 请求阶段时间点

下表是从 `request_received` 起算的阶段偏移；ASGI 中间件仅在 `send` 包装器中累加 body chunk 长度，没有缓存、拼接或复制完整响应体。

| 时间点 | 平均 | P50 | P95 / 最大 |
|---|---:|---:|---:|
| `core_decision_complete` | 44.32 ms | 43.34 ms | 48.84 ms |
| `audit_object_built` | 44.50 ms | 43.50 ms | 49.03 ms |
| `audit_serialized` | 226.38 ms | 225.05 ms | 261.45 ms |
| `audit_hash_complete` | 237.34 ms | 235.42 ms | 274.41 ms |
| `audit_db_commit_complete` | 288.00 ms | 282.02 ms | 321.14 ms |
| `token_issued` | 448.50 ms | 449.57 ms | 467.73 ms |
| `service_returned` | 448.79 ms | 449.83 ms | 468.04 ms |
| `response_started` | 475.16 ms | 472.85 ms | 490.22 ms |
| `response_completed` | 476.92 ms | 474.44 ms | 491.75 ms |
| `request_completed` | 477.18 ms | 474.72 ms | 492.00 ms |

## 根因和修复

回归的主因不是核心裁决、Pydantic/FastAPI 编码、哈希还是 SQLite commit，而是令牌签发前的因果自动重建调度每次都调用 `learning_status()`，旧路径会解析所有命令审计的 `record_json`。修复前数据库约 253 MB，这次全库 JSON/Pydantic 重复处理占用了约 14–17 秒。

修复后，质量元数据检查通过 SQLite `LEFT JOIN ... WHERE quality.audit_id IS NULL` 只读取真正缺失的审计正文；已完整的常规路径只读小型质量元数据行。审计规范化、canonical JSON、紧凑摘要和持久化 JSON 在事务前尽可能预处理；事务内仍保留链尾查询、`prev_hash` 绑定、最终哈希、INSERT 和 commit。没有修改 `synchronous`、`journal_mode`、commit 或哈希定义。

## 体积与冻结契约限制

| 响应 | 平均字节数 |
|---|---:|
| `POST /api/command/text` | 7,462,822 B |
| 单条持久化完整审计 | 3,989,561 B |
| 完整审计导出 | 3,991,209 B |
| 完整 timeline | 3,995,297 B |
| timeline-summary | 699 B |

`timeline-summary` 保持字节级（远小于 1 KB）。通过浏览器运行态访问验证，裁决页和复核页都只请求 `/timeline-summary`，没有请求、回退或预取完整 `/timeline`；summary 失败时钩子保留错误状态，不回退。审计详情仍展示完整持久化时间线，完整审计可通过 export 读取。运行态浏览器验证是本次 Browser 技能直接影响的验收环节。

- `POST /api/command/text` 小于 100 KB：`BLOCKED_BY_FROZEN_CONTRACT`
- 新增精简提交契约：`BLOCKED_BY_FROZEN_CONTRACT`

阻塞字段是必填的 `audit: AuditRecord`。它单独平均约 3.99 MB，已经约是 100 KiB 限制的 38.96 倍；即使其他字段全部不存在也不可能达标。本轮没有删除、改名、改类型或将其替换为摘要/引用，该项不计为修复失败。

## 等价性与安全验证

- canonical bytes 字节级一致，持久化 JSON 与 Pydantic 输出字节级一致。
- `audit_hash` 、`prev_hash` 链接和全链校验全部通过；最新旧记录混合数据库共 167 条链记录，全链有效。
- contract v1 响应模型未修改；`POST /api/command/text` 仍返回必填完整 `audit`。
- PASS / REVIEW / BLOCK 定向回归通过；REVIEW 不提前执行，BLOCK 不签发令牌，PASS 令牌仍只能消费一次。
- 调用顺序回归明确记录为 `audit_committed` 后 `token_issued`。
- 后端定向套件 50 项通过，前端定向套件 8 项通过，TypeScript 检查通过；未运行 115 条全量测试。

## 额外压力观察

一组诊断 1+5 运行恰好跨过现有“每 20 条合格审计自动重建因果模型”阈值，后台完整重建与请求争用 CPU/SQLite，两次尖峰为 2.30–2.68 秒。阶段记录同时显示 retrieval、序列化、哈希和令牌都被系统争用放大，并非单一写路径回归。该观察被保留；本轮没有改变自动重建阈值或策略。最终正式 1+5 是在 `auto_rebuild_running=false` 后完成的受控同环境测量。
