# 审计延迟修复前基线

## 测量条件

- 分支：`backend-contract-freeze-v1`
- Commit：`ecb9701b6c20cfb9f360b3b33292ebd22e75bc78`
- 后端：`http://127.0.0.1:8765`
- 数据库：`D:\语证\data\database\yuzheng.db`
- 指令：`变道并加速`
- 运行：1 次预热，5 次正式测试
- 未执行令牌，未输出令牌或完整响应内容。

## 结果

| 指标 | 平均值 | P50 | P95 | 最大值 |
|---|---:|---:|---:|---:|
| HTTP 端到端 | 19,092.63 ms | 19,052.55 ms | 20,287.87 ms | 20,287.87 ms |
| 核心裁决 | 79.33 ms | 73.73 ms | 110.54 ms | 110.54 ms |
| 核心裁决完成到令牌签发 | 15,619.05 ms | 15,668.53 ms | 16,819.22 ms | 16,819.22 ms |
| 提交响应 | 7,811,117 B | 7,810,988 B | 7,811,350 B | 7,811,350 B |
| 单条完整审计 HTTP 响应 | 4,182,314 B | 4,182,250 B | 4,182,430 B | 4,182,430 B |
| 完整 timeline | 4,188,078 B | 4,188,014 B | 4,188,194 B | 4,188,194 B |
| timeline-summary | 714 B | 714 B | 714 B | 714 B |

完整时间线改用摘要后，当前样本响应体可缩小约 99.983%。

## 修前计时限制

修复前代码只在审计对象构建之前结束 `turn_timing.end_to_end_ms`，因此该字段实际表示核心裁决时间。修前无法可靠拆分 `audit_build_ms`、`audit_serialize_ms`、`audit_hash_ms`、`audit_db_commit_ms` 与响应编码耗时；这些字段在 JSON 基线中明确标为 `UNAVAILABLE_BEFORE_INSTRUMENTATION`，没有推测或伪造。

提交响应低于 100 KB 标记为 `BLOCKED_BY_FROZEN_CONTRACT`：contract 1.0.0 强制返回完整 `TextCommandResponse`，且 `audit: AuditRecord` 为必填。
