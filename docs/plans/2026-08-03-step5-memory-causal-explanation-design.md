# Step5 双重记忆、因果修正与受限解释设计

## 背景与目标

基线为 `13fa1d654971f9c04dc701b550117ded23436180`。本轮补齐报告 Algorithm 2、式2.9—2.15、Algorithm 3、受限解释器与 REVIEW 候选，同时保持唯一 CommandPipeline、证据图、裁决合并和审计链。不提交、不冻结契约、不开发前端。

## 方案对比与选择

1. 在现有服务中完整化：扩展 `DualMemoryService`、`CausalCorrectionService`、现有Schema和AuditRecord。优点是复用主链和兼容旧审计；本轮采用。
2. 新建平行推理系统：会复制图、裁决与审计语义，明确排除。
3. 仅填展示字段：无法提供真实Algorithm 2/3与重启恢复，明确排除。

## Algorithm 2

`Lcand` 只取 Layer 0 Top-K、MandatoryRecall成功节点及required MISSING/TAMPERED节点，不重新运行BGE/HNSW或查询仓库。以 Step2 security_class/rank 为唯一分层来源，`memory_layer==security_rank`，CABIN公开规范为COCKPIT，UNCLASSIFIED保留但不参与纵向传播。

横向图显式区分空间共现、时间同步、语义互补、传感器拓扑。边只由真实字段和配置产生，候选过多时按关系数量、配置优先级、时间差、稳定物理身份确定性裁剪，保证 `d_bar<=16`。初始置信度严格取持久SAS；MISSING/TAMPERED固定0且不可传播。`Child(u)` 是与u有Algorithm 2关系边且位于相邻下一安全层的节点，仅按G3→G2→G1→G0累加 `alpha=0.3` 的贡献。

## Algorithm 3

因果变量使用规范化evidence_type，物理流身份另存 `STABLE_PHYSICAL_IDENTITY_V1`，不混用UUID。历史仅来自审计仓库的合格COMMAND记录，当前turn在审计保存前不进入自身模型。候选边保存条件依赖统计和时间方向，按稳定规则无环剪枝；accepted DAG真实决定 `Pa(i)` 与父状态组合。

式2.10使用用户批准的工程权重：SAS 0.30、层置信0.25、EF 0.15、历史Availability 0.10、mandatory 0.20。式2.11使用稳定Softmax；式2.12按命令类别和真实父状态组合拉普拉斯计数；式2.13—2.15严格计算后验、熵和置信度。历史不足或Availability不足时不造值。当前没有正式低置信REVIEW阈值，因此Algorithm 3不改变裁决。

## 受限解释器与复核

解释器由确定性构建器和可选OpenAI-compatible provider组成，位于merge后、Audit前。输入是脱敏结构化摘要，用户文本仅作为JSON数据；禁止原始音频、向量、logits、令牌、密钥、路径和完整历史。provider输出必须通过严格Schema、裁决一致性、node_id引用和本地动作验证；失败自动进入 `DETERMINISTIC_FALLBACK`。

确定性候选只来自解析器已经得到的完整动作—目标组合，不在槽位缺失时枚举无证据候选。LLM候选只能经SemanticFrameParser、EvidenceDemandService及semantic_rules/action evidence正式动作集合再次验证后进入审计。候选ID绑定turn且数量有界。多候选CONFIRM必须选择；选中后用canonical_text创建child turn并完整重跑。CORRECT与CANCEL保持现有语义。

## 持久化与契约

正常AuditRecord保存Algorithm 2图摘要、关系边、度统计、逐步传播；Algorithm 3模型快照、DAG、先验分量、父状态统计、后验和置信度；解释器输出及校验元数据。ReviewOutcome继续只保存终态关联。presentation、audit detail、timeline和节点详情只读取持久数据；任何GET均不得重建模型或调用provider。

WebSocket仅输出MEMORY_PROPAGATED、CAUSAL_CORRECTED、EXPLANATION_GENERATED有界摘要。契约状态在全部验证通过后将Step5标记COMPLETE、pending_steps清空，但保持DRAFT与frozen=false。

## 参数来源

- alpha=0.3：REPORT_EXPLICIT。
- average_degree_limit=16：REPORT_EXPLICIT。
- lambda_values：ENGINEERING_CONFIG（用户批准）。
- laplace_epsilon=1.0、minimum_history_samples=20：EXISTING_FORMAL_CONFIG。
- numeric_epsilon：ENGINEERING_NUMERICAL_STABILITY。
- theta_causal=0.0：EXISTING_ENGINEERING_BEHAVIOR，不作为最终裁决阈值。
- provider超时、输入/输出上限和候选上限：ENGINEERING_CONFIG，不改变安全裁决。

## 测试策略与已知限制

新增step5单元、流水线、持久化、契约和真实服务测试；继续运行全量、Step1 truth与Step2 live。真实provider未配置时只验证fallback，并明确报告 `NOT_CONFIGURED_FALLBACK_VERIFIED`。PDF未给低因果置信REVIEW阈值，本轮不新增会改变final_decision的阈值。
