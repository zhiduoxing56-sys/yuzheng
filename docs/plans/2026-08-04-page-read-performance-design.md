# 页面切换与只读接口性能专项设计

## 背景与目标

当前页面首屏主要受后端只读接口阻塞，而不是前端代码块下载。实测审计列表、轮次展示、工作流状态、时间线和审计详情分别需要约 3–7 秒。目标是在不改变裁决结论和冻结接口默认行为的前提下，引入数据库定向查询、compact 兼容接口、后端有界单飞缓存和前端应用级 SWR 缓存。

## 现状与约束

- `records_for_root` 调用 `all_records` 后再由 Python 筛选，工作流状态读取会解析全部命令审计 JSON。
- presentation 组装隐式执行全局审计链校验，并重复计算工作流状态。
- 默认审计列表每条包含完整 `DecisionResult`，二十条响应约 10.89 MiB。
- 默认时间线包含完整 audits 和 workflow_events，单次响应约 1.61 MiB。
- 裁决页会在 presentation 返回后再次请求 workflow、timeline 和 vehicle。
- 复核页按顺序请求四个读取接口。
- 默认冻结接口响应保持不变；compact 能力通过显式查询参数增加。

## 方案对比

### 方案一：只改前端请求顺序

改动小，但无法消除 3–7 秒的后端计算与 10 MiB 响应，返回页面仍然慢。

### 方案二：只做后端缓存

第二次访问快，但冷读取仍会解析全部审计，缓存失效后的体验和并发压力无法达标。

### 方案三：定向查询 + compact 接口 + 双层缓存（采用）

先消除全库解析和大响应，再用后端单飞缓存吸收同键并发，用前端 SWR 缓存提供立即回显。改动较多，但能同时改善冷读、热读、切页返回和并发行为。

## 详细设计

### 后端查询

`records_for_root` 通过 `audit_list_summaries.root_turn_id` 与 `audit_records.audit_id` 联接，按 `created_at, turn_id` 读取当前工作流记录。补充 root、turn、created 索引。工作流状态复用该定向查询，不读取其他根轮次载荷。

### 兼容接口

- `/api/audits?view=compact` 返回 `CompactAuditListResponse`，只含列表展示字段和轻量完整性摘要；不解析完整 DecisionResult。
- `/api/turns/{turn_id}/timeline?view=compact` 返回 `CompactTimelineResponse`，只含事件摘要，不携带完整 audits、原始 workflow payload、证据或裁决对象。
- 未传 `view` 时继续走现有模型和默认行为。

### 后端缓存

路由级 `BoundedSingleFlightCache` 保存 presentation、workflow、timeline-summary 和 audit-detail。采用线程安全 LRU、最大容量、同键 Condition 单飞与命中/未命中/等待/失效计数。异常不缓存。缓存对象不得包含授权令牌；presentation 仅包含既有公开授权状态。

命令、复核和执行写完成后，按受影响 turnId、root turnId、auditId 失效；审计 compact 列表不做后端结果缓存，始终读取轻量摘要表。单进程缓存不跨 worker，共享部署需改用 Redis 或版本化分布式缓存。

### 前端缓存

应用模块级 `readCache` 使用有界 LRU 条目保存数据、时间、错误、请求 Promise 和订阅者。钩子采用 stale-while-revalidate：有缓存立即显示，过期时后台更新；同键请求复用 Promise；请求序号防止迟到覆盖。写操作通过明确键和 turn/audit 前缀失效，禁止写入令牌、音频或执行私密结果。

### 请求编排

裁决页 presentation、workflow、timeline compact、vehicle 并行，移除 `presentationKey` 对后三者的隐式二次触发。复核页三类核心读取并行；链校验独立，不阻塞 presentation。页面区域分别显示缓存、加载和局部错误。

导航预取调用同一 readCache，不创建额外状态。预取失败被缓存层吞掉且不阻止导航。

## 异常与边界

- 后端计算异常会唤醒所有同键等待者且不写入缓存。
- 前端重新验证失败保留旧数据，只更新局部错误。
- compact 参数非法返回现有契约错误格式。
- 写操作失效只清除相关前缀，不清空所有缓存。
- 授权令牌只在既有私有 ref 中交接，不进入任一缓存。

## 测试策略

- 比较 compact 与默认接口的排序、分页、筛选、裁决和状态。
- 通过查询计数/猴子补丁证明 `records_for_root` 不调用 `all_records`。
- 并发请求验证相同键只计算一次，写后验证重新计算。
- HTTP 测量冷读、热读、并发、响应体积。
- 浏览器验证首次摘要、切页返回、独立区域加载、复核/执行失效和控制台错误。
