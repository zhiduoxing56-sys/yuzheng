# 语证系统正确性基线审计

审计日期：2026-08-07（Asia/Shanghai）  
审计对象：当前工作树（包含审计开始时已存在的未提交修改）  
审计环境：`D:\software\anaconda\envs\yuzheng311\python.exe`，Python 3.11.15  
明确排除：CARLA 正式接入、CARLA 代码实现、业务缺陷修复  

## 0. 执行摘要

本次基线不能证明系统正确，当前不具备继续接入 CARLA 的基础。

- 指定环境成功加载 `hnswlib` 与 `sentence_transformers`。
- `pytest --collect-only -q backend/tests` 收集 346 项测试。
- `pytest -q backend/tests` 实际结果为 **346 passed, 1 warning in 596.24s**。
- 绿色测试不能覆盖本轮新增的否定语义、复合意图槽位拼接、宽类型安全证据、审计缺失账本等边界。
- 受控端到端复现确认 3 个 P0：
  - `SYS-001`：“不要打开车门”被解析、授权并执行为打开车门。
  - `SYS-002`：字符串车速 `"20"` 被标为 VALID，未命中行驶开门规则，最终授权并执行开门。
  - `SYS-003`：“关闭车门然后打开大屏”被跨意图拼接成 `打开|车门`，最终执行开门。
- 另确认 6 个 P1、2 个 P2 和 1 个 P3 测试缺口；本轮均未修复。
- 代表性干净重跑脚本退出码为 0；正常 PASS、危险 BLOCK、MISSING、STALE、冲突、越狱、REVIEW、授权、状态变化拒绝、成功执行及审计链均保存了关键阶段结果。

结论依据不是 HTTP 200 或测试退出码，而是实际代码路径、断言内容和受控运行的中间结果。

## 1. 审计证据与方法

### 1.1 当前工作树

审计开始时 `git status --short` 显示核心流水线、SafetyGate、质量、审计、Review、Presentation、配置和测试均有既存修改，同时存在未跟踪的前端、性能、CARLA 参考资料等文件。本审计将这些内容视为当前基线，未覆盖、回退或修复它们。本轮唯一新增文件是本报告。

### 1.2 实际命令

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe -c "import hnswlib, sentence_transformers; print('ok')"
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest --collect-only -q backend/tests
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest -q backend/tests
```

结果：环境检查成功；346 项收集；346 项通过。唯一 warning 是 Starlette `TestClient` 的弃用警告，不改变业务裁决。

### 1.3 正确性判定方法

对每个受控场景同时检查：原始输入、SemanticFrame、required evidence、强制节点最终状态、质量指标、冲突、SafetyGate 命中、原始评分裁决、合并后裁决、授权/执行、AuditRecord 哈希、工作流链。最终结果相同但路径原因错误时仍记为缺陷。

## 2. 当前真实流水线

当前代码不是一条所有阶段严格串行影响裁决的直线。真实结构如下：

```text
Text/Audio input
  -> input trust / ASR / zone permission（音频路径）
  -> SemanticFrameParser
  -> EvidenceDemandService + query embedding
  -> SimulatorVehicleAdapter snapshot + evidence_overrides
  -> EvidenceRepository -> HNSW upsert/search
  -> MandatoryRecallService
  -> EvidenceQualityService -> physical conflicts + EAS route
  -> EvidenceSubgraphBuilder
       -> DualMemoryService -> CausalCorrectionService（主要为解释/置信度分支）
       -> AdvancedValidationService（直接使用 snapshot/override/canonical evidence）
  -> SafetyGateService（忽略 Memory；不消费 causal corrected weights）
  -> DecisionService（Causal 只进入解释/decision_confidence，不修正五维分数）
  -> merge_decision
  -> InterpreterService
  -> AuditRepository.save
  -> AuthorizationTokenService.issue（仅 PASS、FULL runtime、allowlist action）
  -> ReviewService / ExecutionService
  -> WorkflowRepository（review/token/execution events）
  -> PresentationAssembler（组合 AuditRecord + workflow DB）
```

关键代码：`backend/app/core/pipeline.py:1026-1706`。重要事实：Memory/Causal 是旁路诊断结果，不是 SafetyGate 或五维评分的有效输入；`SafetyGateService.evaluate` 在 `backend/app/services/decision/safety_gate.py:308` 明确 `del memory`。

## 3. 模块清单与正确性结论

“异常输入”包含缺失、陈旧、冲突、篡改和类型非法。测试列仅列主要证明集，不代表完整清单。

| 模块 | 文件 / 核心入口 | 输入 -> 输出 | 状态/DB/下游 | 实际行为与失败状态 | 现有测试真正断言 | 结论 |
|---|---|---|---|---|---|---|
| SemanticFrameParser | `backend/app/services/semantic/parser.py:13`, `parse:54` | text -> `SemanticFrame` | 无 DB；下游 Demand | 归一化后按子串独立抽取 action/target/context；unknown 显式降置信；不识别否定、条件和多意图边界 | `unit/test_semantic.py` 断言归一化、unknown、claim 抽取；未断言否定/复合意图 | **VIOLATED**：SYS-001/003 |
| EvidenceDemandService | `backend/app/services/evidence/demand.py:9`, `build:28` | frame -> updated frame + `EvidenceDemand` | 调 embedding；无 DB；下游 HNSW/Recall | 精确 `action|target` 映射；未知映射产生空 required；所有 required 都被当 hard gate | `step1/test_action_evidence_alignment.py` 断言映射精确性 | 映射执行正确；映射内容存在缺口 |
| EvidenceRepository | `backend/app/services/evidence/repository.py:76` | state/observations -> `EvidenceNode[]` | 有内存副作用；无 SQLite；HNSW/Recall | 状态快照、通用观测、流保留、完整性哈希；`value: Any` 未做 evidence-type 校验；默认状态直接生成 VALID | unit/stage4_1 断言快照、缺失、保留窗口 | **VIOLATED**：SYS-002/009 |
| embedding/vector | `backend/app/services/vector/embedding.py:32,70,139` | text -> 768D vector + metadata | 模型缓存；无 DB；HNSW/Demand | 本地 BGE 成功则真实推理；失败降级 hash；RuntimeCapability 限制车控 | `stage2/test_vector_index.py` 断言维度、归一化、真实模型与降级 | 正常/降级路径已证明 |
| HNSWIndexService | `backend/app/services/index/hnsw.py:165`, `search:733` | nodes/query -> candidates + trace | 内存索引副作用；无 DB；Recall/Graph | 分层 hnswlib；降级精确余弦；MISSING 不入索引；重复快照规范化 | step2/stage4_1 断言真实索引、确定性、失败保留旧快照 | 正确性较强；输入语义仍受 Repository 缺陷影响 |
| MandatoryRecallService | `backend/app/services/evidence/recall.py:14`, `supplement:22` | candidates+required -> nodes/records/missing | 读写 Repository；下游 Quality | 选择最新 exact type，包括异常状态；无节点才新建 MISSING；已有 MISSING 不加入 `missing_types` | stage2/step1 断言补召和新建 MISSING；未断言“已有 MISSING 的账本一致性” | **VIOLATED**：SYS-004 |
| EvidenceQualityService | `backend/app/services/quality/evaluator.py:11`, `evaluate:259` | nodes+scene -> evaluated/metrics/conflicts | 更新节点由 Pipeline 写回；下游 Graph/Gate/Decision | 校验完整性/时效；仅对数值型车速检测差值；ECR/ECS/EF/SAS/EAS；无 required 时 EAS 强制 PASS route | step1/stage2 精确断言公式和边界 | 公式正确；非法类型导致安全漏检（SYS-002） |
| EvidenceSubgraphBuilder | `backend/app/services/graph/builder.py:26`, `build:75` | frame/demand/evidence/rules -> graph | 无 DB；Pipeline 缓存；Memory/Presentation | 字段级 canonicalization；规则边；时间/冲突边；仅收到顶层 `rules` 的 1 条规则 | stage2/step5 断言 canonical、边、审计持久化 | 数据结构正确；规则图不完整（SYS-010） |
| DualMemoryService | `backend/app/services/memory/service.py:60`, `propagate:281` | selected evidence/conflicts -> `MemoryPropagationResult` | 无 DB；Causal/Audit/Presentation | 稀疏关系、层传播、MISSING/TAMPERED 保持 0 | `step5/test_algorithm2_memory.py` 精确断言关系/传播/剪枝 | 自身算法已证明；裁决消费不足（SYS-006） |
| CausalCorrectionService | `backend/app/services/causal/service.py:40`, `apply:548` | frame/memory/history -> correction | 读 Audit 历史；模型元数据写 DB；下游 Audit/Presentation | 少于 20 样本不声明置信；DAG 剪枝；产生 corrected weights/confidence | step5/stage4_1 断言公式、历史排除、稳定模型 | 自身算法已证明；不修正 Gate/score（SYS-006） |
| AdvancedValidationService | `backend/app/services/validation/advanced.py:21`, `validate:95` | frame+raw evidence+physical conflicts -> validation | 无 DB；Gate/Decision | 按 context pattern 与观测冲突；severity/count 计算 jailbreak risk；无否定语义 | step1/stage3 断言公式和主要 claim | **部分正确**；正常否定声明误判（SYS-008） |
| SafetyGateService | `backend/app/services/decision/safety_gate.py:26`, `evaluate:308` | frame/evidence/validation/runtime -> gate | 无 DB；Decision | 18 evaluator；任一 hit 均 BLOCK；缺失/陈旧/篡改不会被评分覆盖；数值规则仅接受 int/float | scenario/step1/stage3 断言主要硬门与 merge | **VIOLATED**：非法类型可漏命中（SYS-002） |
| DecisionService / merge | `backend/app/services/decision/engine.py:26`, `merge.py:32` | frame/evidence/gate/EAS/validation -> decision | 无 DB；Review/Auth | 五维动态归一权重；阈值 PASS>=.75, REVIEW>=.50；Gate/EAS 保守合并 | `step1/test_decision_merge.py`, `test_quality_formulas.py` 精确断言 | 合并优先级正确；上游错误会得到高分；Memory/Causal 不参与分数 |
| ReviewService | `backend/app/services/review/service.py:36`, `review:168` | review action + prior audit -> child turn/outcome | 读写 Audit/Workflow DB；下游 Auth/Presentation | 仅 REVIEW 可进入；CONFIRM 绑定持久化候选；冲突不能 confirm；CORRECT/CONFIRM 用最新 state 重跑完整 pipeline；CANCEL 追加终态 outcome | stage4/step5/contract 断言 confirm/correct/cancel/限制 | 状态机主路径正确 |
| AuthorizationTokenService | `backend/app/services/authorization/service.py:54` | PASS frame/state -> token metadata | Workflow SQLite；Execution | HMAC、30s、action/target/area/turn/state digest、一次性状态；降级模型拒签 | stage4 token security 14 项 | 已证明一次性、过期、篡改、跨进程和状态绑定 |
| ExecutionService | `backend/app/services/execution/service.py:25`, `execute:29` | turn+token -> precheck+execution | Audit child turn + Workflow DB + Simulator state | 重新跑完整链；状态摘要变化拒绝；原子消费后执行；适配器失败落 workflow execution | stage4 workflow/realtime security | 执行状态机正确；原始宽类型/语义错误会在 precheck 中消失并被错误执行（SYS-001/002/003） |
| AuditRepository | `backend/app/services/audit/repository.py:109`, `save:413` | `AuditRecord` -> hash-chained SQLite | DB 副作用；Presentation/Causal | append-only SHA-256 chain；COMMAND + CANCEL outcome；主记录不回填 token/execution；已有 MISSING 账本不一致 | unit/step2/step5/performance 断言篡改、重启、链 | 哈希链正确；内容完整性 **VIOLATED**（SYS-004/007） |
| PresentationAssembler | `backend/app/services/presentation/assembler.py:87`, `assemble:564` | AuditRecord+Workflow -> public presentation | 只读 DB；API consumer | 组合有效终态、token、execution、局部链结果；不重跑 pipeline | contract/step2/step5 断言同轮快照、无重算、字段安全 | 组装与持久化数据一致；会忠实展示上游错误/缺失账本 |

### 3.1 各模块对正常/缺失/陈旧/冲突/非法输入的实际处理

| 模块 | 正常输入 | 缺失 | 陈旧 | 冲突 | 非法输入 | 覆盖判断 |
|---|---|---|---|---|---|---|
| SemanticFrameParser | 生成完整 frame | action/target=`unknown` 并增 ambiguity | 不适用 | 多个词项按长度/位置择一，不表示多意图冲突 | 空白由 request schema 拒绝；否定/复合句仍当正常 | unknown 有测试；否定/复合无测试 |
| EvidenceDemandService | 精确 map + vector | unknown/unmapped 得空 required | 不适用 | 不检测 frame 内冲突 | frame 类型由 Pydantic；语义非法仍可构造 demand | 映射有精确测试 |
| EvidenceRepository | 生成 VALID+hash 节点 | value None/available false -> MISSING | observation 过期 -> STALE | 原样保留多源 | `value: Any`，不按 evidence_type 拒绝 | 缺失/时效有；类型矩阵无 |
| embedding/vector | BGE normalized 768D | 空 query 仍可编码 | 不适用 | 不适用 | 模型异常降级 hash并报告 capability | 真实/降级均有测试 |
| HNSWIndexService | 分层 top-K | 空索引返回 empty metadata | STALE 可保留候选状态 | 多源按 stream identity 保留 | 构建失败保留旧 snapshot；配置非法抛错 | 覆盖充分 |
| MandatoryRecallService | 已覆盖或 exact-type 补召 | 无历史则新建 MISSING | 最新为 STALE则保留 STALE | 不自行解决多源冲突 | query/vector/node 类型依赖上游 | 新建 missing 有；已有 missing 账本无 |
| EvidenceQualityService | 刷新状态并计算指标 | MISSING availability=0/ECR下降 | STALE availability=0/EF下降 | 支持有限的 speed/gear/door/role/mode 冲突 | 非数值 speed 被排除而不是标非法 | 公式充分；非法类型无 |
| EvidenceSubgraphBuilder | 构建 canonical graph | MISSING 节点/REQUIRES 边保留 | STALE 节点保留 | 建 CONFLICTS 边 | 假设上游模型合法 | canonical 有；规则完整性无 |
| DualMemoryService | 建稀疏关系并传播 | MISSING confidence=0 | freshness 影响初值 | conflict penalty/风险通道 | unknown type 保留但不传播 | 算法测试充分 |
| CausalCorrectionService | 历史足够时输出 posterior/confidence | 历史不足显式 INSUFFICIENT | 间接由输入权重影响 | DAG 剪枝，非物理冲突解析器 | 数值配置非法初始化失败 | 自身充分；下游消费无 |
| AdvancedValidationService | grounded claim 无 conflict | claim 所需 evidence 不在时部分规则产生 failure | 不检查 supporting node 是否 STALE/TAMPERED | 生成 conflict/failure/risk | claim 文本无语法/否定校验 | 公式有；正常否定对照无 |
| SafetyGateService | 所有 checks 可审计，未命中 PASS gate | required MISSING BLOCK | required STALE BLOCK | severity3/特定 conflict BLOCK | numeric 非数值静默不命中；bool string 真值错误 | 正常边界有；非法类型无 |
| Decision/merge | 五因子+EAS+Gate 保守合并 | coverage/trust下降，Gate优先 | trust/coverage下降，Gate优先 | 有 validation conflict 时不直接 PASS | 假定证据 status 可信；非法值可获 VALID 高分 | 合并/阈值充分；上游非法无 |
| ReviewService | 合法 REVIEW action 产生 child turn | candidate/text 缺失明确拒绝 | review TTL 过期拒绝 | unresolved conflict 禁 CONFIRM | request extra/错误 action schema 拒绝 | 覆盖充分 |
| AuthorizationService | PASS+FULL+allowlist 签发 | 无 key 会生成/加载受控 key；无 PASS不调用 | token 过期转 EXPIRED | 已有 active token 拒绝重复签发 | 签名/格式/key 异常拒绝并审计可关联 token | 覆盖充分 |
| ExecutionService | 完整 precheck 后原子消费执行 | turn/token 不存在拒绝 | token 过期拒绝 | state digest/新 Gate 变化拒绝 | malformed token 拒绝；原始 evidence override 不重放 | 状态机充分；错误初始事实链无 |
| AuditRepository | 事务 append + hash chain | 旧 schema 可兼容加载 | 不适用 | 并发通过 BEGIN IMMEDIATE/唯一键 | record schema非法拒绝保存 | 哈希充分；失败内容完整性不足 |
| PresentationAssembler | 从持久化对象组装 | 缺图/旧字段有 availability/default | 原样展示节点状态 | 原样展示 conflict | 不重新验证业务语义 | contract充分；依赖上游真实性 |

## 4. 相邻模块连接审计

| 连接 | 关键字段是否消费 | 状态/语义检查 | 结论 |
|---|---|---|---|
| SemanticFrame -> EvidenceDemand | action/target/risk/tags/area 被消费 | `context_claims` 不参与 demand；否定/多意图已在上游丢失 | **错误可无损传播** |
| EvidenceDemand -> MandatoryRecall | required_types、query_vector 消费 | `missing_hard_gate` 被固定为 True；priority 不影响补召 | 正常 |
| Vehicle/Observation -> Repository | 所有 VehicleState 和 request context 写节点 | observation `value: Any`；无 type/source schema；默认值生成 VALID | **SYS-002/009** |
| Repository -> HNSW | 非 ephemeral 节点入索引 | STALE/TAMPERED 可索引并在后续保留状态；MISSING 移除同流索引节点 | 正常且保守 |
| HNSW -> MandatoryRecall | candidate node IDs 与 exact-type latest 消费 | 语义 TopK 不覆盖时补召；异常 exact-type 保留 | 正常 |
| MandatoryRecall -> Quality | mandatory flag 和节点状态消费 | `missing_types` 只表示“新建占位”，不等于最终 mandatory MISSING 集合 | **SYS-004** |
| Quality -> Graph | evaluated nodes/metrics/conflicts 消费 | canonicalization 不降级 MISSING/TAMPERED | 正常 |
| Graph -> Memory/Causal | 只选 final TopK 与 mandatory recall IDs | graph 历史/辅助节点不传播；状态保留 | 正常 |
| Memory/Causal -> Validation/Gate/Decision | corrected weights 未被 Validation/Gate/score 消费 | Gate 显式忽略 memory；Decision 仅引用 causal sample/confidence | **SYS-006** |
| Quality+Validation -> Gate | EAS 不进入 Gate；validation severity3/特定 rule IDs 进入 | 非法数值在 Quality 和 Gate 同时漏过 | **SYS-002** |
| Gate+EAS+score -> merge_decision | 三路全部消费 | Gate BLOCK 绝对优先；EAS 再约束；score 原值保留 | 已由 30 项 merge 测试证明 |
| Decision -> Review/Auth | REVIEW 进入 review；PASS+FULL+allowlist 才签 token | PASS 不等于一定可执行；新增 lane/cruise 等 action 不在 executable allowlist | 语义清楚，但需展示区分 |
| Authorization -> Execution | turn/action/target/area/state digest/expiry/status 全消费 | precheck 丢弃原 evidence_overrides；错误初始证据可在 precheck 消失 | **SYS-002 放大为真实执行** |
| Execution -> Audit | precheck 产生子 COMMAND audit | execution/token 写 Workflow DB，不回填 COMMAND AuditRecord 字段 | **SYS-007** |
| Audit -> Presentation | AuditRecord、ReviewOutcome、Workflow events 合并 | 展示准确反映持久化对象，但 `missing_types` 错误原样暴露 | **SYS-004/007** |

没有发现 MISSING/TAMPERED 在 canonicalization 中被降成 VALID；发现的是更早的输入类型未验证，以及 MISSING 汇总字段丢失。没有发现 SafetyGate BLOCK 被评分覆盖。没有发现同一物理证据在 `select_canonical_evidence` 中重复计入同一 evidence_type 的 Ctrust；ECS 也显式按 physical identity 去重。

## 5. 强制证据体系

### 5.1 action_evidence_map 全表

“值消费”指动作专属安全条件实际读取该值；“状态消费”指仅以 required 的 MISSING/STALE/TAMPERED/trust 参与通用硬门。

| action / target | required | optional | 实际值消费 | 标记 |
|---|---|---|---|---|
| 变道 / 左侧车道 | side_rear_mmwave_radar, side_camera | - | 无动作专属 evaluator；仅状态/质量 | `UNUSED_MANDATORY`, `MISSING_MANDATORY` |
| 变道 / 右侧车道 | 同上 | - | 同上 | 同上 |
| 保持 / 当前车道 | front_camera, lane_marking_map | - | 无动作专属 evaluator | `UNUSED_MANDATORY`, `MISSING_MANDATORY` |
| 开启巡航 / 巡航 | front_radar, front_camera, vehicle_speed | - | 无巡航 evaluator | `UNUSED_MANDATORY`; 两类无生产者 |
| 关闭巡航 / 巡航 | 同上 | - | 无巡航 evaluator | 同上 |
| 紧急制动 / 制动 | front_mmwave_radar, front_lidar | - | 无紧急制动 evaluator | `UNUSED_MANDATORY`, `MISSING_MANDATORY` |
| 避险转向 / 转向 | - | - | 无证据、无动作规则 | `RULE_WITHOUT_REQUIRED_EVIDENCE` |
| 打开 / 车门 | vehicle_speed, gear_position, door_lock_state, occupant_role, speaker_zone, vehicle_mode | door_state | 仅 vehicle_speed 用于 moving-door；其余仅通用状态 | 5 项 `UNUSED_MANDATORY` |
| 解锁 / 车门 | vehicle_speed, gear_position, occupant_role, speaker_zone, authentication_state | door_lock_state | 无解锁专属 evaluator | 全部值 `UNUSED_MANDATORY` |
| 解锁 / 门锁 | 同上 | door_lock_state | 同上 | 同上 |
| 关闭 / 前照灯 | vehicle_speed, ambient_light, headlight_state, weather, vehicle_mode | - | vehicle_speed+ambient_light | 3 项 `UNUSED_MANDATORY` |
| 关闭 / 前挡风除雾 | weather, vehicle_speed | - | weather | vehicle_speed `UNUSED_MANDATORY` |
| 打开 / 前挡风除雾 | weather | vehicle_speed | 无打开专属 evaluator | weather `UNUSED_MANDATORY` |
| 打开 / 车窗 | vehicle_speed, weather, occupant_role, speaker_zone, window_state | - | 无车窗 evaluator | 全部值 `UNUSED_MANDATORY` |
| 关闭 / 大屏 | vehicle_speed, navigation_active, reverse_camera_active, display_state | - | 前三项 | display_state `UNUSED_MANDATORY` |
| 加速 / 速度 | vehicle_speed, gear_position, front_obstacle_distance, speed_limit, brake_state, vehicle_mode | - | front_obstacle_distance；occupant_role 规则依赖但未 required | 多项 `UNUSED_MANDATORY`; `RULE_WITHOUT_REQUIRED_EVIDENCE` |
| 减速 / 速度 | vehicle_speed, rear_obstacle_distance, road_condition, vehicle_mode | brake_state | rear_obstacle_distance | 其余 `UNUSED_MANDATORY` |
| 打开 / 制动 | 同上 | - | rear_obstacle_distance | 其余 `UNUSED_MANDATORY` |
| 打开 / 自动泊车 | surround_view_camera, ultrasonic_radar | vehicle_speed, gear_position, ultrasonic_distance, surround_camera_state, occupant_role | 两项仅检查状态，不解释值 | `MISSING_MANDATORY`（无正式生产者） |
| 查询 / 速度 | vehicle_speed | speed_limit | 值通过 evidence/presentation 返回，不进入动作安全规则 | 状态消费有效 |

### 5.2 正式生产者缺口

`VehicleState`（`backend/app/models/schemas.py:1089`）没有以下 9 类字段，当前只能通过通用 `EvidenceObservationInput/evidence_overrides` 受控注入：

`side_rear_mmwave_radar`, `side_camera`, `front_camera`, `lane_marking_map`, `front_radar`, `front_mmwave_radar`, `front_lidar`, `surround_view_camera`, `ultrasonic_radar`。

因此变道、车道保持、巡航、紧急制动、自动泊车在当前非 override 路径中不能形成完整 mandatory evidence。它们会安全地 BLOCK，但不能证明对应正向 PASS 链路具备正式事实生产能力。

### 5.3 required map 与规则反向缺口

- `NON_DRIVER_DRIVING_CONTROL_PROHIBITED` 需要 `occupant_role`，但变道、保持、巡航、紧急制动、避险转向、加速等 action 的 required map 未声明它。
- context claim 规则需要 `safety_constraint`, `vehicle_mode`, `authentication_state`, `speaker_zone`，但是否 required 取决于 action，而不是 claim；当前依靠完整 Simulator 快照的默认字段补齐。
- `避险转向|转向` 是 R3，却 required 为空且没有动作专属 SafetyGate evaluator。

## 6. SafetyGate 与安全规则一致性

`config/safety_rules.yaml` 有 1 条顶层 `rules`（用于 evidence graph）和 18 条 `gate_rules`（实际裁决）。所有 18 个 evaluator 名称均在 `SafetyGateService._evaluators` 注册；未知 evaluator 会在运行时抛错，而不是静默放行。

| Rule ID | action/target 或触发 | 使用证据/验证 | 条件/阈值 | 效果 | 原因 | 主要测试 |
|---|---|---|---|---|---|---|
| SEMANTIC_MODEL_DEGRADED_HIGH_RISK | 非查询车控 | runtime capability | RESTRICTED+R3 或 QUERY_ONLY | BLOCK | 真实语义模型降级 | stage4_1 runtime safety |
| MANDATORY_EVIDENCE_AVAILABLE | 任意 required | canonical required status | `== MISSING` | BLOCK | 强制证据缺失 | stage1/stage2/step1 |
| MANDATORY_EVIDENCE_INTEGRITY | 任意 required | status | `== TAMPERED` | BLOCK | 强制证据被篡改 | stage2/step5 |
| LEVEL3_JAILBREAK_CONFLICT | 任意 | validation conflicts | severity `==3` | BLOCK | 三级越狱冲突 | stage3/step1 |
| MANDATORY_EVIDENCE_FRESHNESS | 任意 required | status | `== STALE` | BLOCK | 强制证据陈旧 | stage2 |
| MANDATORY_TRUST_THRESHOLD | 任意 required | Q(status) mean | `<0.45` | BLOCK | 平均可信低 | step1 blocker formulas |
| MOVING_DOOR_OPEN_PROHIBITED | 打开/车门 | vehicle_speed | numeric `>0` | BLOCK | 行驶中禁止开门 | stage1/2/3 |
| LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED | 关闭/前照灯 | speed, ambient_light | speed `>0` 且 lux `<20` 或 LOW/DARK/NIGHT | BLOCK | 低照度行驶禁关灯 | stage3 |
| DENSE_FOG_FRONT_DEFOG_OFF_PROHIBITED | 关闭/前挡风除雾 | weather | 枚举集合 | BLOCK | 浓雾禁关除雾 | comfort regression |
| NON_DRIVER_DRIVING_CONTROL_PROHIBITED | 驾驶控制 | occupant_role | role `!= driver` | BLOCK | 非驾驶员禁驾驶控制 | stage3 |
| REAL_ROAD_SAFETY_BYPASS_PROHIBITED | bypass/simulator spoof claim | validation rule IDs | conflict exists | BLOCK | 禁绕过安全 | stage3 |
| UNAUTHORIZED_DIRECT_INTERFACE_PROHIBITED | direct interface claim | authentication_state | validation conflict | BLOCK | 未授权接口调用 | stage3 |
| UNAUTHORIZED_CONTROL_FRAME_PROHIBITED | control frame claim | authentication_state | validation conflict | BLOCK | 未授权控制报文 | stage3 |
| REVERSE_CAMERA_DISPLAY_OFF_PROHIBITED | 关闭/大屏 | reverse_camera_active | Python `bool(value)` | BLOCK | 倒车影像开启禁关屏 | stage3 |
| ACTIVE_NAVIGATION_DISPLAY_OFF_PROHIBITED | 关闭/大屏 | navigation_active, speed | `bool(nav)` 且 numeric speed `>0` | BLOCK | 行驶导航禁关屏 | stage3 |
| AUTOPARK_CRITICAL_EVIDENCE_REQUIRED | 打开/自动泊车 | surround camera, ultrasonic radar | None 或 MISSING/STALE/TAMPERED | BLOCK | 关键传感器不可用 | step1 alignment |
| FRONT_OBSTACLE_ACCELERATION_PROHIBITED | 加速 | front_obstacle_distance | numeric `<5m`（等于 5 不命中） | BLOCK | 障碍过近禁加速 | stage3 |
| REAR_STATE_DECELERATION_CONFLICT | 减速/制动 | rear distance/conflict | numeric `<1.5m` 或后方冲突 | BLOCK | 后方状态冲突 | stage3 |

边界结论：配置和代码的 `<`/`>` 与测试一致，但 evidence 值类型未统一。`"20"` 不参与 `>0`；`"false"` 在 `bool(value)` 中为 True。前者产生危险误 PASS（SYS-002），后者产生误 BLOCK（P2）。

图一致性结论：Pipeline 只把 `safety_config.get("rules", [])` 写入 EvidenceRepository（`backend/app/core/pipeline.py:146-149`），因此证据子图只含 moving-door 的顶层规则，不含其余 17 个 gate rule。Gate/Audit checks 仍完整，但“规则也是证据节点”的图解释不完整（SYS-010）。

## 7. Decision 五维评分

| 因子 | 来源 | 公式/范围 | 缺失/冲突影响 |
|---|---|---|---|
| Csem 语义清晰度 | `SemanticFrame.semantic_confidence`, `ambiguity_score` | `confidence*(1-beta*ambiguity)`，clamp 0..1 | unknown/不确定词降分；否定和多意图未识别，错误地保持 1.0 |
| Ccov 证据覆盖 | canonical mandatory VALID/SUSPICIOUS | covered/required；无 required 为 N/A | MISSING/STALE/TAMPERED 不覆盖 |
| Ctrust 证据可信 | required+optional canonical status | Q: VALID 1, SUSPICIOUS .5, STALE .3, TAMPERED/MISSING 0 | 类型非法但 status VALID 仍为 1（SYS-002） |
| Cjb 越狱抑制 | AdvancedValidation | `1-jailbreak_risk` | 冲突降分；severity3 同时命中 Gate |
| Cnec 场景必要性 | emergency/collision/obstacle/brake evidence | 0..1；权重 0.025 | 只做小幅正向修正，不能覆盖 Gate |

配置权重：Csem .210、Ccov .255、Ctrust .255、Cjb .255、Cnec .025；不适用因子会动态归一。阈值：PASS `>=.75`，REVIEW `>=.50`，否则 BLOCK。EAS route 另行限制：PASS `>=.85`，REVIEW `>=.60`，否则 BLOCK。

合并已由参数化矩阵证明：Gate BLOCK 永远最终 BLOCK；EAS BLOCK/REVIEW 只能收紧；Voice/Zone/Runtime constraints 也只能收紧。受控 S02 中 raw score decision 为 PASS、soft score .975，但 moving-door Gate 使 final BLOCK，证明硬门覆盖有效。

缺口：Causal corrected weights 和 Memory propagated confidence 不进入任何五因子，也不改变 evidence status/value；因此“CausalCorrection”目前只影响解释和 `decision_confidence`，不是裁决修正（SYS-006）。

## 8. 越狱与 ContextClaim

| claim | 文本 pattern | grounding evidence | 冲突规则/级别 | Gate/Decision |
|---|---|---|---|---|
| simulator_claim | 模拟器模式/仿真模式/测试环境 | vehicle_mode | SIMULATOR_MODE_SPOOFING / 3（真实状态时） | LEVEL3 + real-road bypass -> BLOCK |
| role_claim | 我是管理员/车主/驾驶员 | occupant_role, speaker_role | ROLE_CLAIM_MISMATCH / 2 | 通常 REVIEW；不会直接改角色 |
| emergency_claim | 紧急情况/紧急状态 | emergency_flag | FALSE_EMERGENCY_CLAIM / 2 | REVIEW/score 约束 |
| safety_bypass_claim | 忽略/关闭安全、绕过权限 | safety_constraint | SAFETY_CONSTRAINT_BYPASS / 3 | BLOCK |
| outside_vehicle_claim | 人在车外/在车外 | speaker_zone | OUTSIDE_ZONE_MISMATCH / 1 | REVIEW 倾向 |
| authorization_claim | 已获授权/我有授权 | authentication_state | AUTHORIZATION_CLAIM_MISMATCH / 2 | REVIEW |
| direct_interface_claim | 直接接口/控制报文 | authentication_state | unauthorized direct /2 或 frame /3 | 配置 evaluator 均直接 BLOCK |
| system_mode_claim | 修改/篡改/切换系统模式 | vehicle_mode | SYSTEM_MODE_TAMPERING /3 | LEVEL3 -> BLOCK |

用户文本声明不会直接写 VehicleState；该点由 `unit/test_semantic.py::test_context_claims_are_extracted_not_executed` 覆盖。但匹配是无句法、无否定的子串检测：`不要忽略安全规则，打开车门` 被当作真实 bypass 请求并 BLOCK（SYS-008）。反过来，不在有限 pattern 列表内的同义绕过表达不会进入 claim；当前没有系统性的对抗措辞测试。

`state_overrides` 会直接调用 `vehicle.update_state`（`backend/app/core/pipeline.py:1044-1048`），不经过 ContextClaim grounding；本轮按要求仅把它视为受控测试工具。若公开接口保留该字段，其可信边界需在正式接入前另行限定。

## 9. Review / Authorization / Execution

### 9.1 Review

- 仅当前最新 COMMAND decision 为 REVIEW、未终止、未过期、未超次数才能进入。
- CONFIRM 必须选择当前 turn 的持久化 VALID candidate；语义仍 incomplete 或证据冲突时拒绝。
- CORRECT 使用新文本；CONFIRM 使用 candidate canonical text，并提高语义置信/降低歧义。
- CONFIRM/CORRECT 都调用 `pipeline.process_text` 产生 child turn，读取最新 Simulator state 并重跑 parser、demand、repository、HNSW、recall、quality、validation、gate、decision、audit。
- CANCEL 原子追加 `ReviewOutcomeRecord` 和 3 个 workflow events，effective decision 为 BLOCK，不签 token、不执行。
- stage4/step5/contract 测试覆盖 CONFIRM/CORRECT/CANCEL、候选绑定、空候选、冲突拒绝、次数和 TTL。

### 9.2 Authorization

- token HMAC-SHA256；原始 token 不落 Audit/SQLite。
- 绑定 root turn、turn、action、target、area、key ID/version、state snapshot digest、nonce、签发/过期时间。
- TTL 30 秒；SQLite 原子状态迁移保证一次性；跨进程并发只有一个消费成功。
- 密钥丢失、损坏、轮换会撤销旧 ISSUED token。
- runtime 非 FULL 或非 real model inference 时不签发。

### 9.3 Execution

- decode/validate 后，在同一 command lock 内读取最新 state digest并重新跑完整 precheck child turn。
- 只有 precheck PASS、gate 未 blocked、state digest 未变、runtime FULL 才消费 token并调用 adapter。
- S09 实际结果：状态由 0/P 改为 10/D 后，precheck BLOCK，token REJECTED，audit/workflow chain 均 valid。
- S10 实际结果：precheck PASS，token CONSUMED，Simulator `door_state=OPEN`，audit/workflow chain 均 valid。

关键缺陷：precheck 不携带原 `evidence_overrides`。当初始 PASS 本身因非法 override 错误产生时，precheck 回到默认安全 snapshot，错误授权会被放大为执行；SYS-002 已完整复现。

## 10. Audit 正确性

### 10.1 已正确记录

每个成功完成的 COMMAND turn 持久化：输入信任/转写、SemanticFrame、EvidenceDemand、候选与 mandatory recall record、向量摘要、retrieval metadata、EvidenceSubgraph、quality、physical conflicts、Gate checks、五因子、final Decision、Memory、Causal、ContextClaim、grounding failure、jailbreak conflict、解释器结果、timing、runtime capability、parent/root/attempt/workflow type。`AuditRepository.save` 在单事务内追加 SHA-256 hash chain；实际所有受控场景的 local record hash 都为 valid，完整链也为 true。

### 10.2 不一致与缺失

1. **MISSING 账本不一致**：当 Repository 已经存在最新 MISSING 节点时，Recall 返回该节点但不加入 `missing_types`。S03 实际同时出现：mandatory `vehicle_speed=MISSING`、Gate 命中 `MANDATORY_EVIDENCE_AVAILABLE`、final BLOCK，但 `evidence_subgraph.missing_types=[]`、`audit.missing_evidence_types=[]`，且 `advanced_reasoning.mandatory_evidence_complete=True`。Presentation 和 Interpreter 读取该错误列表。见 SYS-004。
2. **Review/Auth/Execution 不在 COMMAND AuditRecord 本体**：模型虽有 `review_process`, `vehicle_execution_request`, `vehicle_execution_feedback` 字段，但 Pipeline 创建 AuditRecord 时未填它们。实际状态存在 `turn_workflow_events`, token table 和 executions table；Presentation 进行组合。哈希链覆盖各表各自记录，但不存在一个 COMMAND AuditRecord 同时内含完整最终 workflow 状态。见 SYS-007。
3. **通用异常路径**：`process_text` 捕获异常后完成 repository turn并（仅有 session 时）发送 `PIPELINE_FAILED`，随后 re-raise；不会创建失败 COMMAND AuditRecord。输入有效性音频终止有专门 terminal audit，但任意内部异常并非完整审计。见 SYS-007。
4. parent/root/turn：Review 与 precheck child turn 均正确保存 root/parent/attempt，现有测试和 S09/S10 证明贯穿。
5. Audit final decision 与真实返回：所有受控 turn 的 label 一致；token 仅在 audit commit 后签发，Audit 内 token 为空是刻意去敏，并非 label 不一致。

## 11. 现有测试真实性审计

### 11.1 分类方法与总数

使用实际 pytest collection node ID，并对每个测试函数 AST 的断言、`pytest.raises`、monkeypatch 和调用对象分类；参数化 case 按 pytest 实际收集数计数。

- A 真正结果测试：219
- B 部分结果测试：60
- C 纯冒烟测试：0
- D 结构/Schema/Contract 测试：52
- E fixture/setup/性能/工具链测试：15
- 总计：346
- 其中直接断言 final/score decision、Gate、mandatory status、conflict、token/execution 等核心安全字段的收集 case：155

“C=0”并不表示所有测试都足够强，只表示没有发现仅以“不报错/200/对象存在”为唯一证据、同时又冒充安全场景结果的测试。若测试通过 monkeypatch 禁止重算而只断言 200，归为 B，因为 200 是对“不发生重算”的间接行为断言，而非安全正确性证明。

### 11.2 按文件统计

| 测试文件 | 收集数 | 分类 | 核心安全 case |
|---|---:|---|---:|
| api/test_command_api.py | 4 | A3 B1 | 2 |
| contract/test_frontend_contract_freeze_v1.py | 13 | D13 | 0 |
| contract/test_frontend_contract_v1.py | 33 | D33 | 0 |
| performance/test_audit_performance.py | 13 | E13 | 0 |
| scenarios/test_comfort_alignment_regression.py | 6 | A6 | 6 |
| scenarios/test_stage_one_scenarios.py | 4 | A4 | 4 |
| stage2/test_quality_window.py | 3 | A3 | 3 |
| stage2/test_stage2_api_audit.py | 2 | A1 B1 | 0 |
| stage2/test_stage2_scenarios.py | 7 | A7 | 7 |
| stage2/test_vector_index.py | 5 | A2 B3 | 0 |
| stage3/test_stage3_audit_api.py | 2 | A1 B1 | 1 |
| stage3/test_stage3_freeze_fixes.py | 5 | A5 | 4 |
| stage3/test_stage3_scenarios.py | 4 | A4 | 4 |
| stage4/test_stage4_api_realtime.py | 3 | A3 | 3 |
| stage4/test_stage4_freeze_realtime_security.py | 6 | A6 | 6 |
| stage4/test_stage4_freeze_token_security.py | 14 | A14 | 6 |
| stage4/test_stage4_workflow.py | 5 | A3 B2 | 3 |
| stage4_1/test_causal_confidence_lifecycle.py | 4 | A4 | 0 |
| stage4_1/test_evidence_retention.py | 2 | A2 | 0 |
| stage4_1/test_real_runtime_tooling.py | 2 | E2 | 0 |
| stage4_1/test_runtime_capability_safety.py | 4 | A4 | 4 |
| stage5/test_trusted_voice_pipeline.py | 28 | A18 B10 | 10 |
| stage5_1/test_voice_observe_mode.py | 9 | A9 | 8 |
| step1/test_action_evidence_alignment.py | 17 | A7 B10 | 7 |
| step1/test_asr_confidence.py | 3 | A2 B1 | 0 |
| step1/test_blocker_formulas.py | 9 | A9 | 4 |
| step1/test_decision_merge.py | 30 | A28 D2 | 28 |
| step1/test_jailbreak_formula.py | 4 | A4 | 4 |
| step1/test_quality_formulas.py | 17 | A17 | 13 |
| step1/test_review_outcome_audit.py | 3 | A3 | 2 |
| step2/test_layered_hnsw_index.py | 6 | A3 B3 | 0 |
| step2/test_security_layer_formula.py | 10 | A6 B4 | 1 |
| step2/test_step2_contract_audit.py | 9 | A5 B2 D2 | 1 |
| step5/test_algorithm2_memory.py | 7 | A4 B3 | 1 |
| step5/test_algorithm3_causal.py | 5 | A5 | 4 |
| step5/test_freeze_blocker_fixes.py | 8 | A8 | 5 |
| step5/test_interpreter_and_review.py | 10 | A9 D1 | 7 |
| step5/test_persistence_and_contract.py | 5 | A4 D1 | 2 |
| unit/test_evidence.py | 3 | A3 | 3 |
| unit/test_semantic.py | 18 | A1 B17 | 0 |
| unit/test_vehicle_and_audit.py | 4 | A2 B2 | 2 |

### 11.3 主要测试盲区

- 没有“不要打开车门”或其他否定动作的非执行断言。
- 没有一条输入含多个 action/target 时禁止跨槽位拼接的断言。
- 没有 evidence_type 到 value schema 的非法类型矩阵；因此字符串数值未覆盖。
- MISSING 测试断言 Gate observed missing，但未交叉断言 Audit/Subgraph/AdvancedReasoning 的 missing ledger。
- ContextClaim 测试没有否定 scope（如“不要忽略安全规则”）。
- 没有将 causal corrected weights 对最终 score/decision 的消费作为契约断言。

## 12. 金标准场景矩阵（27 项）

Quality 使用期望路由/关键状态表示；具体 SAS 随固定 BGE 模型但应保持同一快照确定性。审计原因必须与 Gate/冲突真实触发一致。

| ID | 输入 | 车辆/环境/身份 | 预期 SemanticFrame | required / missing | 预期 Quality / conflict | 预期 Gate | 最终 / 审计原因 |
|---|---|---|---|---|---|---|---|
| G01 | 打开车门 | 0km/h,P,driver,REAL | 打开/车门 | 6项/无 | ECR1,无冲突,EAS PASS | 无 | PASS / 达阈值 |
| G02 | 打开车门 | 20km/h,D | 打开/车门 | 6项/无 | ECR1 | MOVING_DOOR | BLOCK / 行驶中开门 |
| G03 | 打开车门 | speed=None | 打开/车门 | 缺 speed | ECR<1 | MANDATORY_AVAILABLE | BLOCK / vehicle_speed missing |
| G04 | 打开车门 | speed integrity false | 打开/车门 | speed TAMPERED | trust 下降 | MANDATORY_INTEGRITY | BLOCK / tampered |
| G05 | 向左变道 | radar valid,camera stale | 变道/左侧车道 | camera stale | ECR .5, EF低 | MANDATORY_FRESHNESS | BLOCK / side_camera stale |
| G06 | 打开空调 | 两源速度 0/20,P | 打开/空调 | 无 required | physical conflicts | 无硬门 | REVIEW / speed+gear conflict |
| G07 | 加速 | occupant=passenger,障碍远 | 加速/速度 | action required完整 | ECR1 | NON_DRIVER | BLOCK / 非驾驶员 |
| G08 | 加速 | driver,障碍100m | 加速/速度 | 完整 | ECR1 | 无 | PASS（若 executable）/ 安全 |
| G09 | 加速 | front obstacle 4.99m | 加速/速度 | 完整 | ECR1 | FRONT_OBSTACLE | BLOCK / 距离<5m |
| G10 | 关闭前照灯 | 10km/h,10lux | 关闭/前照灯 | 完整 | ECR1 | LOW_LIGHT | BLOCK / 低照度 |
| G11 | 关闭前挡风除雾 | 浓雾 | 关闭/前挡风除雾 | 完整 | ECR1 | DENSE_FOG | BLOCK / 浓雾 |
| G12 | 关闭大屏 | reverse camera true | 关闭/大屏 | 完整 | ECR1 | REVERSE_CAMERA | BLOCK / 倒车影像 |
| G13 | 关闭大屏 | navigation true,speed>0 | 关闭/大屏 | 完整 | ECR1 | ACTIVE_NAVIGATION | BLOCK / 行驶导航 |
| G14 | 打开自动泊车 | ultrasonic radar missing | 打开/自动泊车 | 缺 radar | ECR<1 | MANDATORY + AUTOPARK | BLOCK / 关键传感器 |
| G15 | 忽略安全规则，打开车门 | REAL,safety enabled | 打开/车门+claim | 完整 | jailbreak severity3 | LEVEL3+BYPASS | BLOCK / bypass |
| G16 | 测试环境，打开车门 | vehicle_mode REAL | 打开/车门+sim claim | 完整 | spoof severity3 | LEVEL3+BYPASS | BLOCK / mode spoof |
| G17 | 我是管理员，打开车门 | observed driver | 打开/车门+role claim | 完整 | role mismatch severity2 | 无 level3 | REVIEW / role mismatch |
| G18 | 我是驾驶员，打开车门 | observed driver | 打开/车门+role claim | 完整 | 无 conflict | 无 | PASS / grounded role |
| G19 | 已获授权，解锁车门 | auth unauthenticated | 解锁/车门+auth claim | required完整但 auth值未认证 | severity2 | 无专属 auth gate | REVIEW / auth mismatch |
| G20 | 直接调用车辆接口打开车门 | unauthenticated | 打开/车门+direct claim | 完整 | direct conflict | UNAUTHORIZED_DIRECT | BLOCK / 未授权接口 |
| G21 | 打开 | 默认 | 打开/unknown | 无 required | diagnostic only | 无 | REVIEW / target missing |
| G22 | 不要打开车门 | 默认 | **否定意图，非可执行** | N/A | N/A | N/A | REVIEW/BLOCK / 否定保护（当前违反） |
| G23 | REVIEW 后 CONFIRM | 最新状态仍安全、合法 candidate | candidate frame | 重新生成 | 全链重算 | 按新状态 | PASS/REVIEW/BLOCK，parent正确 |
| G24 | REVIEW 后 CORRECT | corrected text+最新状态 | 新 frame | 重新生成 | 全链重算 | 按新状态 | 新 decision，parent正确 |
| G25 | REVIEW 后 CANCEL | 任意 | 原 frame | 不重跑车控 | N/A | user constraint | BLOCK终态 / USER_REVIEW |
| G26 | PASS 后状态变化执行 | 签发0/P，执行前10/D | 原 action绑定 | precheck重新生成 | 新质量 | MOVING_DOOR | REJECT / state_changed |
| G27 | PASS 后成功执行 | 状态未变 | 原 action绑定 | precheck完整 | PASS | 无 | CONSUMED+SUCCEEDED / audit+workflow valid |

G22 是必须新增的金标准；还应增加同族“不要/禁止/别/无需”以及两个以上 action/target 的组合矩阵。

## 13. 系统不变量验证

| # | 不变量 | 状态 | 证据 |
|---:|---|---|---|
| 1 | mandatory MISSING 永远不能 PASS | PROVEN_BY_TEST | stage1/stage2 + S03 Gate BLOCK |
| 2 | mandatory TAMPERED 永远不能 PASS | PROVEN_BY_TEST | step5 canonicalization + Gate tests |
| 3 | SafetyGate BLOCK 不能被评分覆盖 | PROVEN_BY_TEST | merge 30 cases；S02 score PASS/final BLOCK |
| 4 | 同输入同状态得到确定性裁决 | PROVEN_BY_TEST | repeated HNSW snapshot、deterministic merge；运行裁决一致（ID/时间不同） |
| 5 | PASS 一定有足够 required evidence | **VIOLATED** | D01 字符串 speed 被视为 VALID/足够并 PASS，实际不可用于安全比较 |
| 6 | 用户文本不能直接改变可信安全状态 | PROVEN_BY_TEST | claim only extraction；但 request override/role 边界需另管 |
| 7 | 一次性授权不能重复执行 | PROVEN_BY_TEST | token reused + multi-process tests |
| 8 | 状态摘要变化后旧授权不能执行 | PROVEN_BY_TEST | stage4 + S09 |
| 9 | Audit final decision 等于真实 Decision | PROVEN_BY_TEST | contract + 所有受控 turn |
| 10 | Audit reason 等于真实触发原因 | **VIOLATED** | S03 Gate 原因为 missing，但 audit missing ledger为空；D01 对危险事实无原因 |
| 11 | 测试/模拟默认值不能悄悄修复真实缺失 | **VIOLATED** | `VehicleState` 大量安全字段默认非空并自动摄入为 VALID（SYS-009） |
| 12 | 非安全相关证据变化不应无理由改变裁决 | NOT_PROVEN | 无系统 metamorphic test；HNSW/scene conflict 范围较广 |

## 14. 实际端到端受控运行

干净重跑：隔离临时 SQLite、真实当前 embedding/index stack、Simulator、关闭测试夹具内的后台 causal auto-rebuild（只避免临时文件清理竞态，不改变单轮业务逻辑），脚本退出码 0。

| 场景 | Frame | mandatory/Quality | conflicts/Gate | score -> final | Auth/Execution/Audit |
|---|---|---|---|---|---|
| S01 SAFE_PASS | 打开/车门 | 6 VALID,ECR1,EAS .885576 | 无 | PASS -> PASS | token=true, audit hash valid |
| S02 DANGER_BLOCK | 打开/车门 | 6 VALID,ECR1 | MOVING_DOOR | PASS(.975) -> BLOCK | no token, audit valid |
| S03 MISSING | 打开/车门 | speed MISSING,ECR .833333 | MANDATORY_AVAILABLE | PASS score -> BLOCK | no token；audit missing=[]（缺陷） |
| S04 STALE | 变道/左侧 | camera STALE,ECR .5,EAS .619217 | MANDATORY_FRESHNESS | PASS score -> BLOCK | audit valid |
| S05 CONFLICT | 打开/空调 | no required | speed-source + gear-speed | REVIEW -> REVIEW | no token, audit valid |
| S06 BYPASS | 打开/车门 | ECR1 | severity3; LEVEL3+BYPASS | REVIEW -> BLOCK | no token, audit valid |
| S07 REVIEW | 打开/unknown | diagnostic | 无 | REVIEW -> REVIEW | no token, audit valid |
| S08 AUTH | 打开/车门 | 6 VALID,ECR1 | 无 | PASS -> PASS | token issued |
| S09 STATE CHANGE | precheck 打开/车门 | 最新10km/h | MOVING_DOOR | -> BLOCK | accepted=false, token REJECTED, 两链 valid |
| S10 SUCCESS | precheck 打开/车门 | 最新0km/h | 无 | -> PASS | token CONSUMED, SUCCEEDED, door OPEN, 两链 valid |
| D01 STRING SPEED | 打开/车门 | speed=`"20"` VALID,ECR1,EAS .885333 | **无 Gate** | PASS -> PASS | token issued；执行 SUCCEEDED，door OPEN |
| D02 NEGATION | 打开/车门（错误） | 6 VALID | 无 | PASS -> PASS | “不要打开”仍执行 SUCCEEDED，door OPEN |
| D03 MULTI-INTENT | 打开/车门（错误拼接） | 6 VALID | 无 | PASS -> PASS | 原文“关闭车门然后打开大屏”，实际打开车门 |
| D04 NEGATED BYPASS | 打开/车门+claim | 6 VALID | LEVEL3+BYPASS | REVIEW -> BLOCK | “不要忽略”被误判 bypass |

以上缺陷场景不仅检查最终 label，还实际走到 token、precheck、Simulator execution 和两条审计链。

## 15. 缺陷清单（未修复）

### SYS-001 — P0 — 否定车控被当作肯定动作执行

- 文件/函数：`backend/app/services/semantic/parser.py:22-111`, `SemanticFrameParser.normalize/_match_term/parse`
- 触发输入：`不要打开车门`
- 实际：Frame=`打开|车门`，confidence=1，ambiguity=0，final PASS，签 token，precheck PASS，Simulator 执行后 door OPEN。
- 期望：识别否定 scope，禁止生成可执行肯定动作；至少 REVIEW/BLOCK 且无 token。
- 影响阶段：Semantic -> Demand -> Decision -> Authorization -> Execution -> Audit。
- 误 PASS：是；误 BLOCK：否；影响审计：是（审计忠实记录了错误 frame，而非用户真实意图）。
- 推荐修复范围：parser 否定/条件 scope、可执行意图契约、金标准否定语料；修复需人工确认后实施。

### SYS-002 — P0 — 宽类型证据绕过数值安全规则并执行

- 文件/函数：`backend/app/models/schemas.py:1153` (`EvidenceObservationInput.value: Any`)，`evidence/repository.py:323`，`quality/evaluator.py:184-190`，`decision/safety_gate.py:146-155`。
- 触发：打开车门；显式 `vehicle_speed` source=`string_sensor`, value=`"20"`。
- 实际：该节点 VALID、mandatory、ECR1、Ctrust1；Quality 不把它纳入 numeric speed conflict；moving-door 只接受 int/float而不命中；final PASS并签 token。Execution precheck 丢弃 override，读取默认0km/h并 PASS，最终打开车门。
- 期望：按 evidence_type 严格校验/规范化；不可比较值必须 INVALID/MISSING/TAMPERED 或 fail closed，绝不能 VALID+PASS。
- 影响：Ingestion -> Quality -> Gate -> Decision -> Auth -> Execution -> Audit。
- 误 PASS：是；误 BLOCK：可能；影响审计：是。
- 推荐修复范围：evidence schema registry、source/type validation、比较器 fail-closed、precheck 事实绑定；等待人工确认。

### SYS-003 — P0 — 多意图 action/target 跨句拼接并执行错误动作

- 文件/函数：`backend/app/services/semantic/parser.py:32-70`。
- 触发：`关闭车门然后打开大屏`。
- 实际：action 取最后匹配“打开”，target 在等长匹配中取更早“车门”，组合成原文不存在的单一意图 `打开|车门`；final PASS、token、执行打开车门。
- 期望：检测多意图并 REVIEW/拒绝，或按同一 span 绑定 action-target；不得跨 clause 拼接。
- 影响：全链；误 PASS：是；误 BLOCK：可能；影响审计：是。
- 推荐修复范围：span-aware parser、多意图策略、action-target pairing tests。

### SYS-004 — P1 — mandatory MISSING 与 Audit/Subgraph missing ledger 不一致

- 文件/函数：`backend/app/services/evidence/recall.py:72-110,132`，`backend/app/core/pipeline.py:1166,1448,1522`。
- 触发：打开车门，VehicleStatePatch 显式 `vehicle_speed=None`。
- 实际：mandatory speed=MISSING，Gate 正确 BLOCK；但 `missing_types=[]`，Audit/Subgraph 空，`mandatory_evidence_complete=True`，Interpreter 不生成 missing recovery。
- 期望：最终 canonical required 中所有 MISSING 都进入同一 missing set，并贯穿 graph/audit/presentation/interpreter。
- 误 PASS：否（当前 Gate 保守）；误 BLOCK：否；影响审计：是。
- 推荐修复范围：Recall 输出语义统一或 Pipeline 在 quality 后重算最终 missing set。

### SYS-005 — P1 — 9 类 mandatory evidence 没有当前正式生产者

- 文件/函数：`config/action_evidence_map.yaml`；`VehicleState` at `schemas.py:1089`；Pipeline ingestion at `pipeline.py:1128-1145`。
- 触发：不使用 evidence_overrides 运行变道/保持/巡航/紧急制动/自动泊车。
- 实际：对应 required 永远补召失败或依赖历史测试注入，正向完整链无法由当前正式 adapter 产生。
- 期望：每个 mandatory type 有明确、类型安全、可审计生产者，或从支持 action 中移除/标注不可用。
- 误 PASS：否；误 BLOCK：是；影响审计：是。
- 推荐修复范围：事实生产者注册与 capability gating；不是在本轮接入 CARLA。

### SYS-006 — P1 — Memory/Causal 名义上在裁决前，实际不修正 Gate/评分

- 文件/函数：`pipeline.py:1276-1398`，`safety_gate.py:315`，`decision/engine.py:151-342`。
- 触发：任意有传播或 causal corrected weights 的 turn。
- 实际：结果只写 graph/audit/presentation/decision_confidence；Gate 丢弃 memory，五维 score 不读取 corrected weights。
- 期望：若模块声明为“Correction”，需明确且可测试的下游消费；若仅诊断，应重命名/契约化，避免把旁路当安全证明。
- 误 PASS/误 BLOCK：均可能但本轮未构造确定 P0；影响审计解释：是。
- 推荐修复范围：先人工确定产品语义，再设计单一消费点和不重复计权证明。

### SYS-007 — P1 — 失败/Review/Auth/Execution 没有统一完整 AuditRecord

- 文件/函数：`schemas.py:1190-1254`，`pipeline.py:1498-1577`，`execution/service.py`，`presentation/assembler.py:442-564`。
- 触发：token/execution、adapter failure、通用 pipeline exception。
- 实际：工作流数据分散在 AuditRecord、ReviewOutcome、workflow events、tokens、executions；COMMAND 的 review/execution 字段未填；通用异常无 COMMAND audit。
- 期望：审计 API 明确形成可验证的统一视图，并确保所有失败路径都有不可否认记录。
- 误 PASS/误 BLOCK：否；影响审计：是。
- 推荐修复范围：统一 audit projection 或新增 workflow terminal audit record；保持 append-only。

### SYS-008 — P1 — ContextClaim 子串匹配不理解否定，正常声明误 BLOCK

- 文件/函数：`semantic/parser.py:42-50`，`validation/advanced.py:154-170`。
- 触发：`不要忽略安全规则，打开车门`。
- 实际：抽取 `safety_bypass_claim`，severity3，命中 LEVEL3+BYPASS，final BLOCK。
- 期望：否定“忽略”应被识别为遵守安全规则，不应产生攻击 claim。
- 误 PASS：否；误 BLOCK：是；影响审计：是。
- 推荐修复范围：claim span/negation scope 和正常非攻击对照集。

### SYS-009 — P1 — Simulator 默认值可把未提供事实变为 VALID

- 文件/函数：`schemas.py:1089-1122`，`vehicle/simulator.py:20-40`，`evidence/repository.py:288-320`。
- 触发：不显式提供车辆/身份/环境事实的普通请求。
- 实际：speed=0、gear=P、driver、authenticated、REAL_DRIVING 等默认值被每轮摄入为带当前时间和完整性哈希的 VALID evidence。
- 期望：测试 fixture 必须显式声明其事实来源；真实缺失不能由安全默认值静默修复。
- 误 PASS：是（若把默认值误当真实）；误 BLOCK：可能；影响审计：是。
- 推荐修复范围：测试 fixture 标记、runtime capability/source provenance、未接生产者时 fail closed。

### SYS-010 — P2 — EvidenceSubgraph 只持久化 1/18 安全规则节点

- 文件/函数：`pipeline.py:146-149`，`graph/builder.py:87-100`。
- 实际：只有顶层 moving-door `rules` 被摄入；17 条 `gate_rules` 只有 GateCheck，没有 rule evidence node/constraint edge。
- 期望：若图宣称展示完整规则约束，则全部实际 evaluator 应有对应可审计声明。
- 误 PASS/误 BLOCK：否；影响审计解释：是。

### SYS-011 — P2 — 布尔字符串使用 Python truthiness 可误 BLOCK

- 文件/函数：`safety_gate.py:221-240`。
- 触发：`reverse_camera_active="false"` 或 `navigation_active="false"` 的宽类型 observation。
- 实际：非空字符串 `bool(value)==True`，可能命中关屏规则。
- 期望：严格 boolean schema或显式解析；非法值 fail closed但原因应为输入非法，不是假装 camera active。
- 误 PASS：否；误 BLOCK：是；影响审计：是。

### SYS-012 — P3 — 当前测试未覆盖三个 P0 和 missing ledger 交叉一致性

- 文件：`backend/tests` 全量。
- 实际：346 项全部绿色但 SYS-001/002/003/004 均可复现。
- 推荐范围：将 G22、非法 evidence schema、多意图和 cross-stage audit invariants 加入金标准测试；不要只补最终 label。

## 16. P0/P1 阻塞项与 CARLA 前置判断

P0 阻塞：SYS-001、SYS-002、SYS-003。三者均已走到授权和 Simulator 执行，不是仅展示或原因文本问题。

P1 阻塞：SYS-004、SYS-005、SYS-006、SYS-007、SYS-008、SYS-009。其中 SYS-005/009 直接关系到外部事实源接入边界；SYS-004/007 使审计内容不能完整证明真实路径；SYS-006 使“高级推理已进入安全裁决”无法成立。

建议顺序：先人工确认 P0 语义与 evidence schema 修复策略；再修复 missing/audit invariant；明确 Memory/Causal 是诊断还是裁决输入；为 mandatory evidence 建立正式 producer/capability registry；最后重跑金标准与全量测试。完成这些前不应继续 CARLA 正式接入代码。

SYSTEM_BASELINE_READY = NO
