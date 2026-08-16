# 交互状态统一重构设计说明

## 背景与目标

当前系统将语义候选、澄清请求、传统复核候选、工作流状态和前端本地确认状态混合使用，导致同一轮次可能出现空候选澄清弹窗或多套可写确认入口。

本次重构建立唯一、持久化的 `InteractionRequest` 作为前端实时交互事实源。对外只投影四种状态：需要澄清、通过、需要复核、拒绝。前端只读取该对象并提交后端下发的允许操作。

## 约束

- 不修改 Qwen、OrderedSemanticUnit、SemanticOrchestrator、Registry、确定性候选选择、EvidenceDemand、SafetyGate、安全评分或 VehicleAdapter。
- 安全决策仍为 `PASS / REVIEW / BLOCK`，且保持 `BLOCK > REVIEW > PASS`。
- 旧候选字段如需保留，只用于历史审计；新的可写流程不得依赖它们。
- 当前白色前端目录为 `frontend/`。

## 方案

后端新增 `InteractionRequest` 及持久化仓储记录，字段包括 interaction id、turn id、unit index、intent id、四态、当前规范操作、原因、允许操作、候选快照、有效期和 consumed 标记。

状态由后端单向投影：

- 语义未完成：`NEEDS_CLARIFICATION`；不得进入安全、授权或执行。
- 语义明确且最终裁决为 `PASS`：`PASS`。
- 语义明确且最终裁决为 `REVIEW`：`NEEDS_REVIEW`。
- 最终裁决为 `BLOCK`：`BLOCK`。

`NEEDS_CLARIFICATION` 允许选择候选、重新表达和取消；无合法候选时仅允许重新表达和取消。`NEEDS_REVIEW` 仅允许确认继续和取消，且候选为空。`BLOCK` 仅允许关闭。`PASS` 仅在后端签发有效 token 时允许执行。

## 接口与恢复

澄清接口只接受 interaction id 与候选 id，或重新表达/取消；后端校验状态、有效期、归属及一次性消费。安全复核接口只接受 interaction id 与确认继续/取消；确认绑定原始 unit 和 intent，不接受语义候选或修正文案。两类确认都必须再次由后端核验；BLOCK 不可确认。

## 前端

`DecisionPage` 成为唯一实时交互入口。它仅根据 `interaction_request.state` 和 `allowed_actions` 渲染澄清弹窗、安全复核弹窗、拒绝提示或无弹窗。前端本地状态仅表示提交中、错误和可见性，不再判断风险、复核资格或执行资格。

## 验证

覆盖明确通过、有候选澄清、无候选重新表达、安全复核、BLOCK 不可确认、过期/重复确认、多动作 unit 绑定和 token 状态约束；完成 Python 编译、后端测试、前端类型/测试与 `git diff --check`。
