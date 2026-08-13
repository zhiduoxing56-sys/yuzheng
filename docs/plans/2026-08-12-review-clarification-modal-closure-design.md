# REVIEW 候选确认弹窗闭环设计说明

## 背景与目标

对可由用户语言确认解决的 REVIEW 返回唯一 `clarification_request`，前端立即弹出轻量确认 Modal。用户选择候选后保留原始 turn、追加澄清审计、创建 child turn，并以确认文本重新运行完整安全 Pipeline；用户选择或通过遮罩空白触发“都不是，再说一次”时结束本轮，不签发 token、不执行、不创建 child turn。

安全型 REVIEW 不生成澄清候选。前端不得通过 `decision == REVIEW` 自行推断是否弹窗。

## 现状与约束

- 现有系统已有持久化 review candidates、child turn、完整重新裁决、workflow event hash 链和人工 Review 页面。
- 现有 `confirmed=True` 会提高语义置信度并降低歧义度，不能用于本闭环；用户确认只确定输入文本，不直接改变安全或语义结论。
- 不修改 R4 Intent Registry、32 Evidence Types、Evidence Demand、HNSW、Mandatory Recall、Quality、SafetyGate、Phase5/6、Authorization、Execution、frozen99 或 registry hash。
- 当前工作区已有未提交改动，实施时保留并避让这些改动。

## 方案对比

### 方案一：扩展现有人工 `/review`

- 优点：改动文件较少。
- 缺点：语言澄清与安全人工复核语义混杂，并会继承现有确认置信度修正行为。

### 方案二：独立 ClarificationService，复用 Pipeline 与 workflow 存储（采用）

- 优点：弹窗触发条件、请求合同和安全边界明确；复用已有完整重跑及 hash 链；不侵入 Phase1～Phase6。
- 缺点：需要新增少量合同、存储和前端状态管理。

### 方案三：新建第二套澄清 Pipeline

- 优点：模块隔离最彻底。
- 缺点：重复 turn、审计和裁决能力，容易产生第二套权威数据。

## 详细设计

### 架构与合同

新增 `ClarificationRequest` 和 `ClarificationCandidate`。`ClarificationRequest` 包含 `clarification_id`、`turn_id`、`clarification_type`、`prompt`、`original_text`、最多四条 `candidates`。候选包含 `candidate_id`、`display_text`、`candidate_source`、`source_rank`、`confidence`。

`TextCommandResponse` 与 `TurnPresentationResponse` 增加可空 `clarification_request`。唯一触发条件为当前结果是 REVIEW 且该字段非空。

确认接口为 `POST /api/turns/{turn_id}/clarification`。正常选择仅提交 `clarification_id + candidate_id`；拒绝所有候选提交 `clarification_id + resolution=NONE_OF_ABOVE`。接口不接受 intent、slot、decision 或 semantic frame。

### 候选来源

- VOICE：已有 ASR N-best；若当前适配器没有 N-best，只复用已存在的文本纠错、anchor similarity 或正式候选结果。
- SEMANTIC：`SemanticFrame.review_candidates`、已持久化的正式 candidate interpretations、unresolved clause/slot，以及 Registry 已知的确定性离散槽位空间。
- SLOT_COMPLETION：第一版只做可证明的离散补全，例如 `RIGHT_SIDE -> RIGHT_FRONT / RIGHT_REAR`。
- 连续 value 缢失时不生成猜测数值。候选去重、稳定排序并截断到四条，不补位。

VOICE 与 SEMANTIC 不混合；语音优先。确认后的 child turn可因新的语义原因再次产生 SEMANTIC_CONFIRMATION，但不得再次产生相同的 VOICE_CONFIRMATION。

### 数据流与审计

澄清请求按 `turn_id + clarification_id` 持久化候选快照。选择时后端从快照读取确认文本，创建 child turn，并携带 `parent_turn_id`、`clarification_id`、`confirmed_candidate_id`、`confirmation_source=USER_EXPLICIT_CONFIRMATION`。完整 Pipeline 使用确认文本重新开始，不直接修改 Decision，也不使用语义置信度提升捷径。

workflow hash 链追加 `CLARIFICATION_REQUESTED` 和 `CLARIFICATION_RESOLVED` 事件。旧 command audit 与 hash 不修改、不重算。审计详情聚合展示原始文本、review reasons、全部候选及来源/排名/置信度、resolution、选中项、child turn 和最终结果。

### NONE_OF_ABOVE 与 Modal

Modal 居中、约 420～480px，复用当前蓝灰视觉体系。候选纵向整块可点击，底部固定低层级“都不是，再说一次”。候选为零时显示“暂未找到可靠候选，请重新说一次”。

点击“都不是”或 Modal 外遮罩空白均提交 `NONE_OF_ABOVE`；点击 Modal 内容区阻止冒泡。提交期间候选和遮罩动作禁用，避免重复提交。成功后关闭 Modal、恢复 idle 和输入入口；不生成 token、执行或 child turn。

Modal 生命周期严格绑定 `turn_id + clarification_id`。turn 改变、child turn 到达或组件卸载时，旧 Modal 立即失效并中止旧请求。

### 异常与边界

- clarification、candidate 不属于当前 turn：拒绝请求。
- 已解决 clarification：幂等返回既有结果或明确冲突，不重复创建 child turn。
- 安全型 REVIEW：`clarification_request=null`，继续现有展示。
- 可靠候选为零：允许只显示“都不是”，不制造候选。
- 后端失败：Modal 保持，显示可重试错误，不误回 idle。

### 测试策略

覆盖附件所列 A～W：候选来源、去重排序和上限、离散补全、连续值禁猜、candidate_id 防伪、child turn 完整重跑、NONE_OF_ABOVE、安全 REVIEW 不弹窗、Modal 生命周期、遮罩取消、append-only 与 hash 链。

最终运行项目指定 Python 环境下的后端测试、compileall、frozen99/Phase5/6/audit 回归，以及前端 Vitest、lint、build 和 `git diff --check`。

