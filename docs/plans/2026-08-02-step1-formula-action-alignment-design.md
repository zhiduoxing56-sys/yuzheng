# 软件修整第一步：公式与动作—证据对齐设计

## 范围与依据

本轮仅落实《语证》报告摘要、第一章、第二章（排除 2.2.4、2.3.4）、第五章和第六章中与 ASR 工程置信度、ECS、EAS、越狱风险和动作—证据映射直接相关的要求。第三章、第四章、实验数值、硬件实现及第二步 HNSW 修整均不在范围内。

既有前端契约字段名、安全门、SafetyScore、复核、令牌、审计安全语义保持不变。本轮只向已经建立的可空字段填入可追溯的真实计算结果，不填充假值。

## ASR 工程置信度

Whisper 推理请求生成分数，并使用 `compute_transition_scores(..., normalize_logits=True)` 获取生成序列的 token 对数概率。统计时仅保留文本 token，排除 decoder prompt、语言/任务/timestamp token、padding、EOS 及全部 special token。置信度定义为文本 token 平均对数概率的指数，并限制在 `[0, 1]`。

空文本、没有有效文本 token、模型未返回分数或运行时不支持该接口时返回 `None`，不得伪造置信度。文本输入继续没有 ASR 置信度。审计只保存聚合值，不保存 token 数组或 logits。

## ECS 与 EAS

ECS 仅使用唯一、可比较、非 `MISSING` 的证据节点。有效节点少于两个时 ECS 为 1；否则分母为 `n(n-1)/2`。冲突事件展开成无序节点对并去重，只有两端均属于有效节点的冲突对才进入分子。

EAS 只由 ECR、ECS、EF、SAS 构成。默认权重保持既有 `0.35/0.25/0.20/0.20`；报告只给出定性动态规则，因此高速场景提高 EF 权重，复杂道路/交叉口场景提高 ECS 权重，这些数值属于 `ENGINEERING_PROFILE`。ECR 不可用时移除该项并归一化其余权重。证据层路由严格为：`>=0.85` PASS，`>=0.60` REVIEW，否则 BLOCK。

最终裁决通过单一保守合并入口产生，严重度为 `BLOCK > REVIEW > PASS`：硬门命中直接 BLOCK；否则 EVIDENCE_BLOCK 直接 BLOCK；EVIDENCE_REVIEW 与 SafetyScore 原始裁决取更严格结果；EVIDENCE_PASS 保留原始 SafetyScore 裁决。`decision` 是旧兼容字段且永远等于新增的 `score_decision`；`final_decision` 独立保存合并结果。模型兼容读取旧记录时以 `decision` 补齐缺失的 `score_decision`，但显式不一致输入必须拒绝。新记录同时持久化 `decision`、`score_decision`、`final_decision`、`decision_sources` 与 `decision_merge_reason`。

## 越狱风险

基础风险使用 `1-exp(-lambda*conflict_count)`。无冲突时严重度风险为 0；有冲突时为 `0.5+0.5*max_severity/3`，严重度限制在 1 到 3。最终风险为两者较大值并限制在 `[0,1]`，`Cjb=1-risk` 保持不变。`conflict_decay_lambda` 是显式工程配置。报告明确规定存在冲突时越狱标记为真，因此标记不再混入风险公式。

## 动作与精确证据类型

本轮新增变道、车道保持、巡航、紧急制动和避险转向语义。表 2.1 的精确映射如下：

- 变道：`side_rear_mmwave_radar`、`side_camera`
- 紧急制动：`front_mmwave_radar`、`front_lidar`
- 自适应巡航：`front_radar`、`front_camera`、`vehicle_speed`
- 车道保持：`front_camera`、`lane_marking_map`

自动泊车按表 2.1 使用 `surround_view_camera`、`ultrasonic_radar` 两项精确 required evidence；既有车速、档位、距离和工程状态只能作为 optional，不能满足 required 覆盖、可信度或硬门。报告只提到避险转向动作，没有给出证据集合，因此标记为 `REPORT_ACTION_WITHOUT_EXPLICIT_EVIDENCE_MAPPING`，不借用其他动作的证据集合。

报告没有给出这些新增动作的 canonical target、风险等级、风险标签或优先级数值；相应最小配置均标记为 `ENGINEERING_MAPPING`，不得表述为报告明确值。

仓库按精确 `evidence_type` 检索。未命中时创建同类型 `MISSING` 占位节点：值、传感器时间戳和可信分数均为空，来源为 `missing_placeholder`，召回来源为 `NONE`。不使用距离、盲区、通用摄像头、车道状态或车速近似替代报告类型。测试可显式注入精确类型，来源必须为 `simulated_test_source`，且不得进入生产初始化。

`MISSING` 会降低 ECR，但不进入 ECS 有效节点或分母。按照式 2.9，任一 required evidence 最终解析为 `MISSING` 或 `TAMPERED` 时必须命中 Safety Gate；这不是在 EAS 或最终裁决层增加通用 `missing=true` 覆盖，而是 PDF 明确的 required evidence 硬门。

## 阻塞问题收口设计

证据状态量化统一为式 2.11 的 `VALID=1.0`、`SUSPICIOUS=0.5`、`STALE=0.3`、`TAMPERED=0`、`MISSING=0`。required trust 对每个精确 required type 只采用强制补召最终选定的 canonical 节点；Ctrust 对当前轮实际验证并参与裁决的 canonical evidence 做同一 Q 映射的算术平均，MISSING/TAMPERED 以 0 参与，因果后验权重只作诊断。

式 2.12 的 `semantic_ambiguity_beta` 在报告中没有具体数值，因此使用保持既有行为的 `1.0`，来源固定为 `ENGINEERING_PROFILE`，不按场景调参。

CANCEL 通过 `merge_decision(USER_REVIEW=BLOCK)` 产生终态，不重跑原流水线。原始命令 `AuditRecord` 不变，另追加仅含终态关联字段的 `REVIEW_OUTCOME` 判别式记录。outcome 与 `REVIEW_CANCELLED`、`FINAL_DECISION_UPDATED`、`AUDIT_OUTCOME_APPENDED` 在同一 SQLite 事务中进入审计链和工作流链，并由 `(original_audit_id, review_action)` 唯一约束保证并发幂等。presentation、audit detail/list、timeline、verify 统一通过有效终态 resolver 聚合读取；物理 outcome 行不作为第二个业务轮次展示。

## 契约与验证

填充既有 `asr_confidence`、方法、证据对数、EAS profile/source/weights/route 和 jailbreak base/severity 等字段。HNSW 内部路径与候选解释继续为空。契约状态保持 `DRAFT`、`frozen=false`；第一步完成后 pending steps 保留 `step2_hnsw_safety_layer_and_visualization` 与 `step5_explanation_and_review_generation`。

验证包含定向单元测试、API/契约测试、全量测试、编译、差异检查、真实运行预检，以及文本和真实中文 WAV 场景。所有生成矩阵与报告位于被 Git 忽略的 `tmp/step1-alignment`。
