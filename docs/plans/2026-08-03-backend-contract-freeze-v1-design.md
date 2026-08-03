# 后端前端契约 v1 正式冻结设计

## 1. 冻结基线与目标

- 基线提交：`d894002bd7add4bc89e5513ffdee8807fc501a01`（阶段五：完成双重记忆、因果修正与受限解释）
- 冻结分支：`backend-contract-freeze-v1`
- 契约标识：`frontend_contract_v1`
- 契约版本：`1.0.0`
- 版本来源：`ENGINEERING_VERSIONING`。PDF没有规定软件契约版本号。
- 正式状态：`contract_status=FROZEN`、`frozen=true`
- 三个后端步骤均为 `COMPLETE`，`pending_steps=[]`

本次冻结不改变任何业务字段、算法、裁决、检索、复核、令牌、执行或审计语义。冻结工作的作用是把已提交且已验收的生产事实转为确定、可校验、受版本控制的前端契约。

## 2. 唯一事实来源

冻结生成链只有三个输入：

1. `backend/app/models/schemas.py` 与 `backend/app/models/frontend_contract.py` 中的生产 Pydantic Schema；
2. `create_app().openapi()` 产生的 FastAPI OpenAPI；
3. `scripts/generate_backend_contract.py` 中明确的 v1 公开操作 allowlist 和说明性语义。

枚举值不在生成器维护第二份手写列表。Enum 直接迭代生产类型；Literal 通过生产模型的 JSON Schema 提取。HTTP request、response、参数和状态码直接取公开 OpenAPI 操作。

## 3. v1 公开范围

冻结九条 HTTP 操作：

1. `POST /api/command/text`
2. `POST /api/command/audio`
3. `GET /api/turns/{turn_id}/presentation`
4. `GET /api/turns/{turn_id}/evidence/{node_id}`
5. `POST /api/turns/{turn_id}/review`
6. `GET /api/turns/{turn_id}/timeline`
7. `GET /api/audits`
8. `GET /api/audits/{audit_id}`
9. `GET /api/audits/{audit_id}/verify`

冻结一条 WebSocket：`/ws/pipeline/{session_id}`。

健康检查、状态写入、索引维护、因果维护、执行、场景、调试和内部兼容路径均不进入 v1 公开契约。OpenAPI 生成器只保留九条 path/method，并递归保留这些操作可达的 component schemas。

## 4. 四页面模型

- 可信输入：`InputPresentation` 与 `TurnPresentationResponse`。
- 证据检索：EvidenceDemand、RetrievalSummary、QualityMetrics、Evidence、Memory、Causal 和 EvidenceNodeDetail。
- 裁决复核：Gate、Score、Validation、Decision、Review、Authorization、Execution、ReviewSubmission 与 ReviewSubmissionResponse。
- 审计日志：AuditListResponse、AuditDetailResponse、TimelineItem 与 AuditVerificationResponse。

字段名、required 和 nullable 均从 Pydantic Schema 自动读取。前端只展示后端持久事实，不重算 EAS、SafetyScore、score_decision、final_decision、授权或复核恢复结果。

## 5. 枚举与同源说明

冻结 DecisionLabel、DecisionSource、EvidenceStatus、EvidenceDemandStatus、RetrievalOrigin、SecurityClass、ReviewAction、Availability、LayerNavigationAvailability、WorkflowEventType、ErrorCode、ContractStatus、ContractStepStatus，以及生产 Literal 定义的 candidate validation、generation mode、candidate availability 和 confidence status。

DecisionSource 保持八值。`LEGACY_COMPATIBILITY` 仅用于旧审计兼容读取，不进入正常新裁决。枚举说明同时记录生产符号路径；DecisionSource 使用生产说明映射。

## 6. Nullable / Availability

冻结并区分：

- `AVAILABLE`：当前记录存在持久事实；
- `NULLABLE_NOT_APPLICABLE`：字段对当前输入或场景不适用；
- `LEGACY_NOT_RECORDED`：旧审计未记录，禁止读取时重算；
- `DEGRADED_UNAVAILABLE`：运行降级导致能力不可用；
- `PROVIDER_NOT_CONFIGURED`：外部 provider 未配置，使用确定性 fallback；
- `INSUFFICIENT_HISTORY`：历史不足，decision_confidence 为 null；
- `NO_VALID_CANDIDATES`：本地复验后无候选，列表为空。

生产 Schema 中所有 nullable 字段由生成器自动列出；条件语义由契约固定，前端不通过 null 猜测原因。

## 7. Review、错误与有效终态

- CONFIRM 必须引用原轮次持久化且 VALID 的 candidate，创建 child turn 并完整重跑；
- CORRECT 必须提供 corrected_text，创建 child turn 并完整重跑；
- CANCEL 追加 ReviewOutcome，将公开有效终态解析为 BLOCK，不重跑原指令。

错误结构和 ErrorCode 来自生产模型。零候选 CONFIRM 固定为 `409 NO_PERSISTED_REVIEW_CANDIDATES`。token 消费接口未进入九条冻结路径，因此不为文档新增不存在的 token 输入错误码；前端仍可读取授权和执行状态。

## 8. WebSocket 边界

WebSocket Schema 直接来自 `PipelineEvent`。契约同时固定核心字段、同一活动 session 内 sequence 单调递增语义、断线后通过 presentation 恢复，以及 payload 脱敏边界。公开 hnswlib 不支持内部 entry point/visited-node trace，故继续固定 `internal_hnsw_trace_available=false` 和原因 `UNSUPPORTED_BY_PUBLIC_HNSWLIB_API`。

## 9. 生成物与摘要

单一正式目录：`docs/contracts/frontend-contract-v1/`。

- `frontend-contract-v1.json`：机器可读语义契约；
- `frontend-contract-v1.md`：人工可读说明；
- `openapi-public-v1.json`：九条 HTTP 操作的公开 OpenAPI 子集；
- `manifest.json`：版本、状态、生产 Schema 摘要、产物摘要、生成器版本和基线提交；
- `README.md`：前端使用入口和兼容规则。

`production_schema_digest` 对冻结元数据 Schema 和公开 OpenAPI components 的 canonical JSON 计算 SHA-256。manifest 中的 source_commit 使用已知稳定基线 `d894002bd7add4bc89e5513ffdee8807fc501a01`；包含这些产物的冻结提交将在人工核验后另行创建。

## 10. 可复现性

JSON 使用 UTF-8、稳定缩进、key 排序和末尾换行。Markdown/README 使用固定模板和稳定生产顺序。生成内容禁止包含生成时间、Git提交时间、机器绝对路径、用户名、临时目录、随机 UUID、SQLite 运行数据或秘密。

生成器支持 `--output-dir`，测试在两个独立临时目录连续生成并逐字节比较，同时与正式目录比较。Git提交时间承担冻结时间语义，不进入文件摘要。

## 11. 旧审计兼容

PRE_STEP1、Step1、Step2、Step5 和 ReviewOutcome 继续通过现有生产 resolver/assembler 读取。旧记录缺失 Memory、Causal、Interpreter 或 HNSW 导航字段时返回 `LEGACY_NOT_RECORDED`，不得重新计算、调用 fallback、修改 record_json 或改变旧哈希。

## 12. 兼容性政策

允许的非破坏性变更：新增 optional nullable 字段；升级 minor 后新增不影响旧客户端的枚举值；新增独立路径；改进文字；保持契约行为的内部修复。

破坏性变更包括删除字段、改类型、nullable 变 required、修改现有枚举语义或状态码、改路径、改 Review 动作、改 final_decision 含义、改 WebSocket 包络或审计有效终态语义。破坏性变更必须发布新版本，不得覆盖 v1 文件。

## 13. 运行边界与已知限制

- 外部 LLM provider 未配置；正式状态为确定性 fallback 已验证，不得宣称云端 provider 成功。
- PDF与正式配置均未规定因果低置信 REVIEW 阈值；因果置信度只用于审计和解释。
- hnswlib 内部访问轨迹不由公共 API 提供；四层安全导航数据是各层真实索引查询，不冒充内部 trace。

## 14. 验收原则

契约测试必须核对 metadata、精确路径/method、生产同源枚举、nullable/availability、四页面、WebSocket、错误契约、manifest、连续生成字节一致和敏感信息边界。全量回归、Step1 truth、Step2/Step5 live runtime、preflight 和 `git diff --check` 必须继续通过，且业务 Schema 变化与 breaking change 均应为 false。
