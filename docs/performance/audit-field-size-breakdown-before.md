# 审计字段体积分析（修复前）

样本为 `AUD_6b83f66790ee`（`TURN_71954c01dadd`），指令为“变道并加速”。报告只保存字段名、路径、大小和重复次数，不保存字段内容。

## SQLite 状态

| 项目 | 数值 |
|---|---:|
| 数据库文件 | 252,956,672 B |
| 全部审计链记录 | 148 |
| 命令审计 | 147 |
| 复核终态审计 | 1 |
| 单条平均 | 1,167,641.89 B |
| 单条中位数 | 450,746 B |
| 单条 P95 | 3,841,970 B |
| 单条最大 | 3,922,180 B |
| 当前样本持久化 UTF-8 大小 | 3,978,080 B |

`audit_records` 将完整 `record_json` 与摘要列保存在同一表；另有 `audit_list_summaries` 摘要表。`timeline-summary` 直接读取摘要表与紧凑工作流列，不解析完整 `record_json`。现有查询索引覆盖创建时间、摘要裁决、动作、目标、根轮次和轮次编号，未发现需要以降低持久化安全性解决的索引问题。

## 顶层字段前 10 名

| 排名 | 字段 | UTF-8 字节数 |
|---:|---|---:|
| 1 | `final_decision` | 1,555,554 |
| 2 | `advanced_reasoning` | 777,198 |
| 3 | `causal_correction` | 565,459 |
| 4 | `causal_candidate_edges` | 246,824 |
| 5 | `causal_removed_edges` | 234,243 |
| 6 | `memory_propagation` | 209,549 |
| 7 | `evidence_subgraph` | 157,220 |
| 8 | `candidate_recall_results` | 51,274 |
| 9 | `horizontal_memory` | 45,989 |
| 10 | `retrieval_metadata` | 30,098 |

## 重复嵌套结论

- `advanced_reasoning` 在顶层和 `final_decision.advanced_reasoning` 中完整重复。
- `causal_correction` 出现 4 份；其候选边、移除边分别出现 5 份。
- `memory_propagation` 出现 4 份；横向、纵向传播数据分别出现 5 份。
- `causal_pruned_edges` 的同值结构最多出现 9 份。
- `retrieval_metadata` 同时存在于顶层与 `evidence_subgraph`。
- 没有发现 presentation 与 audit 互相嵌套、memory 保存完整历史 audit、review 子轮次复制父审计或递归历史审计嵌套。
- 完整 `/timeline` 直接包含完整 audit；`timeline-summary` 不包含 evidence graph、memory、advanced reasoning 或 audit blob。
- `TextCommandResponse` 根据冻结契约同时携带顶层大型产物和必填完整 audit，导致提交响应约 7.81 MB。该项不能通过删除字段修复。

本轮不删减上述法证字段；字段重复只作为体积与响应编码瓶颈证据，任何结构性拆分留待新 schema 与人工批准。
