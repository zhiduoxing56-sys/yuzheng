# Phase6-Lite：确定性 occurrence-scoped 因果修正

## 背景与目标

Phase6-Lite 仅为比赛演示提供可审计、可展示的因果修正解释。它不参与任何安全裁决、授权或执行，也不学习历史因果关系。

## 冻结边界

- 不读取 audit history、`causal_model_metadata` 或 `learning_records()` 来生成当前结果。
- 不进行 command-class、rho、在线训练、历史 DAG 或 per-intent graph 学习。
- 不修改 v3 数据库、`record_json` 或 hash chain。
- 不改变 Phase1--Phase5 的安全公式、`IntentSafetyAssessment`、aggregate/final decision、Authorization 或 Execution。

## 推荐方案

保留共享物理 Memory graph，并以 Phase4 的 `(clause_index, intent_id, node_id)` binding 为因果解释归属。每个有效 binding 独立生成一条既有 `CausalPriorComponents` 和 `CausalNodeWeight`；不新增顶级 Schema。

```text
raw_prior = 0.30*binding_similarity + 0.25*memory_final
          + 0.15*freshness + 0.10*availability
          + 0.20*requirement_component
prior = softmax(raw_prior within occurrence)
causal_support = role_support * evidence_trust_value(status)
unnormalized = prior * causal_support
corrected_weight = unnormalized / sum(unnormalized within occurrence)
```

其中 REQUIRED/OPTIONAL 的 `role_support` 来自 `causal_policy.yaml`，默认分别为 1.0/0.7。`CausalNodeWeight.corrected_weight` 是 canonical truth；`corrected_weights[node_id]` 仅保留为同一物理节点所有 occurrence weight 的 `max` 展示投影。

## 固定模型身份

模型固定为 `DETERMINISTIC_CAUSAL_PROXY_V1`。`model_build_id` 只由公式版本、确定性 support 配置和代码定义权重 profile 的 canonical hash 生成；history/source audit count 恒为 0，training IDs 恒为空，DAG 列表为空。

## 验证策略

覆盖 shared node 的双 occurrence、REQUIRED/OPTIONAL、不可用证据、全零权重、重启稳定性、v3/metadata 不影响结果、Phase5 隔离和 presentation occurrence 展示。并运行 Phase5、Memory/Causal、Presentation/Audit/Pipeline、compileall、diff-check 与前端 TypeScript 检查。
