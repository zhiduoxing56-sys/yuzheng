# 人类可读安全审计详情一次性迁移设计

## 背景与目标

当前 `GET /api/audits/{audit_id}` 返回面向工程排障的 `AuditDetailResponse`，同时承载语义帧、证据图、质量、门控、哈希与工作流字段。目标是一次性迁移为唯一公开的 `AuditDetailView`，让比赛展示和安全追溯直接回答指令、系统理解、裁决现场、裁决依据、用户复核、授权与执行。底层 `AuditRecord`、SQLite 历史记录、审计哈希链与 occurrence identity 均保持不变。

## 现状与调用方审计

- 生产后端调用方：`backend/app/api/routes.py` 与 `backend/app/services/presentation/assembler.py`。
- active frontend 调用方：`frontend/src/hooks/useAuditDetail.ts`、详情 adapter、详情页面和详情组件。
- `audit verify` 与 export 直接读取 repository / resolver，不依赖旧详情 DTO，可保持独立。
- 当前语义帧技术入口位于审计列表弹窗，可继续读取列表记录中的 `semantic_frame`。
- REVIEW clarification 的未提交实现已通过 workflow append-only event 保存请求与结果，详情投影只做增量聚合。
- 其他调用为测试、验收/性能脚本、合同生成器和历史副本 `前端2`；迁移 active caller、当前测试与当前合同工件，不将历史副本作为兼容层。

## 方案对比

### 方案一：同响应兼容扩展

- 优点：短期调用方改动小。
- 缺点：继续暴露工程字段，产生双合同和长期兼容负担。

### 方案二：新增 v2 端点

- 优点：迁移风险较低。
- 缺点：公开存在两个审计详情入口，违背唯一合同目标。

### 方案三：原端点一次性切换

- 优点：公开模型唯一，前端不再解释机器审计，职责清晰。
- 缺点：必须同步迁移全部 active caller、测试和合同工件。

## 推荐方案

采用方案三。`GET /api/audits/{audit_id}` 的 response model 直接切换为 `AuditDetailView`，不保留旧字段 alias、wrapper 或 compatibility mapping。历史机器记录在读取时投影，缺失事实不伪造。

## 详细设计

### 架构

```text
AuditRecord + WorkflowEvent + Execution feedback
                      ↓
             PresentationAssembler
                      ↓
               AuditDetailView
                      ↓
          GET /api/audits/{audit_id}
                      ↓
            Human-readable Audit UI
```

`AuditSnapshotBuilder` 是唯一快照生产入口。当前从本轮已持久化 Evidence / Simulator 可证明事实构造；未来 CARLA 只替换 producer，不改变合同或前端。

### 公开合同

`AuditDetailView` 包含：

- `command_summary`
- `resolved_operations[]`
- `decision_snapshot`
- `decision_summary`
- `key_evidence[]`
- `intent_decisions[]`
- `llm_explanation`
- `clarification_history[]`
- `authorization_summary`
- `execution_summary`
- `execution_before_snapshot`
- `execution_after_snapshot`
- `execution_changes[]`

技术 ID、哈希、SemanticFrame、EvidenceSubgraph、原始传感器载荷不进入公开详情。

### 数据流

1. 安全流水线完成并固化 final decision。
2. 基础 AuditRecord 先持久化，哈希链不受 LLM 影响。
3. 固化 `decision_snapshot`；历史记录只能投影当时已保存且可证明的事实。
4. explanation service 使用严格的 `AuditExplanationContext` 后置调用一次。
5. 成功或失败结果以新的 workflow/audit event append-only 保存。
6. 详情读取聚合原始审计、clarification、explanation 与 execution events，不修改历史记录。

### LLM 边界

复用现有 OpenAI-compatible provider 基础设施，但 explanation 使用独立 service、prompt 和窄上下文。模型只能解释结构化事实，不得产生或修改 final decision、gate hit、evidence、snapshot、authorization 或 execution truth。超时、模型错误或输出越界只令 explanation 状态失败，不影响裁决、授权、执行或基础审计。

### 前端

主详情严格按六区顺序渲染：指令与结果、系统理解、裁决现场、裁决依据与 AI 说明、用户复核、授权/执行/CARLA 回执。空、`unknown`、`N/A` 等无意义字段整行隐藏。技术语义帧继续从审计列表独立弹窗查看。审计列表只显示时间、原始指令、最终裁决、执行结果、是否复核和详情入口。

### 异常与边界

- 历史记录缺少 snapshot、clarification 或 execution feedback 时对应区块为空或显示明确的未发生状态，不补造事实。
- raw sensor payload 永不进入 `AuditDetailView`。
- before / after / decision 三类 snapshot 独立；changes 仅由真实前后快照中的变化字段生成。
- BLOCK / REVIEW 不授权、不执行；PASS 的授权与执行状态只取既有安全链事实。

### 测试策略

覆盖单意图 PASS/BLOCK/REVIEW、多意图 occurrence、空值隐藏、历史快照不漂移、raw sensor 排除、execution changes、clarification SELECTED/NONE_OF_ABOVE/child turn、LLM 调用时序与失败隔离、append-only、现有 Simulator 投影、API/前端/合同工件以及 frozen99、Phase5/6、audit/hash 回归。

## 约束

- 不修改 SafetyGate rule、R4 Registry、32 Evidence Types、Evidence Demand、HNSW 或 Mandatory Recall。
- 不实现 CARLA Bridge。
- 不迁移、覆盖或重算历史审计数据与哈希。
- 保留并增量融合当前未提交 clarification 修改。

## 实施计划与完成状态

1. 完成旧详情合同 caller 审计并确认 verify/export 独立读取底层事实。
2. 将公开详情模型一次性切换为 `AuditDetailView`，审计列表同步简化。
3. 新增 `AuditSnapshotBuilder`；新轮次以 `DECISION_SNAPSHOT_CAPTURED` workflow event 固化现场，历史记录从已持久化 Evidence 只读投影。
4. 复用现有 OpenAI-compatible provider，使用独立 `AuditExplanationService` 和 `AuditExplanationContext`；结果以 `LLM_EXPLANATION_GENERATED` append-only event 保存。
5. active frontend 只消费新合同，六区展示；SemanticFrame 改为独立技术端点按需读取。
6. 更新 API/contract tests、验收脚本与当前 frontend contract artifacts。
7. 完成本轮专项、frozen99、Phase5/6、audit/hash、compileall、lint 和 diff-check 门禁；全量前端现存非审计失败单独报告。
