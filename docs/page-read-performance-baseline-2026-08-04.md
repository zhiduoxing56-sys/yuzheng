# 页面切换与只读接口性能基线（2026-08-04）

环境：Windows，本地单进程 Uvicorn，SQLite 约 111 条审计。通过完整 HTTP 响应测量，不记录令牌或响应载荷。

| 接口 | 第一轮 | 第二轮 | 响应字节 |
|---|---:|---:|---:|
| `/api/health` | 334.9 ms | 14.8 ms | 1,069 |
| `/api/state` | 14.5 ms | 12.1 ms | 862 |
| `/api/audits?page=1&page_size=20` | 6,837.1 ms | 7,116.9 ms | 10,885,490 |
| `/api/evidence/turn/TURN_5b9748fa0c7a` | 165.4 ms | 144.8 ms | 139,930 |
| `/api/turns/TURN_5b9748fa0c7a/presentation` | 5,963.0 ms | 5,927.0 ms | 328,859 |
| `/api/turns/TURN_5b9748fa0c7a/workflow-status` | 2,952.3 ms | 3,009.3 ms | 212 |
| `/api/turns/TURN_5b9748fa0c7a/timeline` | 3,525.1 ms | 3,795.8 ms | 1,607,226 |
| `/api/turns/TURN_5b9748fa0c7a/verify-workflow-chain` | 83.9 ms | 94.1 ms | 89 |
| `/api/audits/AUD_655f181c18d2` | 5,846.9 ms | 5,881.8 ms | 192,155 |
| `/api/audits/AUD_655f181c18d2/verify` | 1,352.0 ms | 1,436.9 ms | 338 |

基线业务样例：`TURN_5b9748fa0c7a` 的最终裁决为 PASS；`TURN_3b0b6721d76b` 为 BLOCK；`TURN_0d608191104f` 为 REVIEW。优化后以同一数据库记录复测裁决、列表顺序和时间线顺序。
