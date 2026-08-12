# R4 Final Freeze 元数据补丁设计

## 背景与目标

从 `intent_registry_r4_simplified_candidate.yaml` 只读派生最终冻结文件。仅更新版本/冻结状态、旧 mapping 禁用元数据以及 Known Control Gold 证据优先级；不修改 Intent、合同、scope 路由、多意图 schema 或数据。

## 方案比较

### 方案一：原地修改 simplified candidate

缺点：破坏候选父版本，无法证明最终补丁只改元数据。

### 方案二：派生独立 final 文件（采用）

保留 simplified candidate 哈希不变，生成 `intent_registry_r4_final.yaml`；validator 对父子结构做允许路径白名单比较。

### 方案三：同时创建下一版 mapping

缺点：属于下一阶段工作，本轮明确禁止。

## 允许变更路径

- `registry_version`
- `semantic_freeze_status`
- `document_status`
- `runtime_loading_allowed`（2026-08-10 当时保持 `false`）
- `mapping_rule_source.status`
- `mapping_rule_source.usable_for_r4_gold`
- `mapping_rule_source.usable_for_training`
- `mapping_rule_source.required_next_mapping_version`
- `r4_mapping_policy`
- `gold_scope_mapping_policy.known_control_evidence_requirement`（删除）
- `gold_scope_mapping_policy.known_control_evidence_policy`（新增）

除上述路径外，父子 YAML 必须完全一致。

## Mapping 与 Gold 证据规则

旧 `full_nlu_mapping_v1.yaml` 的 path/version/SHA 仅保留为 provenance，明确禁止用于 R4 Gold 与训练。下一阶段所需版本只记录为 `nlu_mapping_r4_scope_v1`，本轮不创建文件。

Known Control 以 `RAW_TEXT` 为主证据；MAC split/semantics 仅在可用时辅助和做冲突检查。三者不要求同时存在。annotation 与原文冲突时不得覆盖原文，进入 `SOURCE_CONFLICT_REVIEW`；baseline 不得决定 scope。

## 2026-08-10 当时的冻结语义（历史合同）

- `registry_version`: `sys-014-semantic-hardening-r4-final`
- `semantic_freeze_status`: `FROZEN_FOR_FULL_NLU_GOLD_BUILD`
- `document_status`: `FROZEN_OFFLINE_FOR_GOLD_BUILD`
- `runtime_loading_allowed`: `false`

该冻结只授权后续 Full NLU Gold 构建，不表示已接入 runtime。

## 2026-08-11 Phase3 取代合同

Evidence Demand Registry Phase3 已将正式 R4 作为生产运行时只读权威，用于校验 Intent ID 集合与各 Intent 自身的 `allowed_areas`。因此上述 offline-only 限制自 2026-08-11 起不再是现行合同。现行权威状态以 `intent_registry_r4_final.yaml` 顶部元数据为准：`document_status: FROZEN_FORMAL_RUNTIME_REGISTRY`、`runtime_loading_allowed: true`。该许可仅允许生产组件只读加载，不授权运行时修改、热更新、自动扩展或建立第二套 Registry。

## 验证策略

- 71 个 Formal mapping 与 simplified candidate 逐字段、逐顺序相等。
- value/mode/direction/conditional/mapping contracts 全部整对象相等。
- 四态 scope、bypass route、多意图 schema 全部整对象相等。
- 统计冻结为 71/71/71/0/91/4。
- 旧 7-Intent active dependency 为 0，`FOLLOWING_GAP_REQUIRED` 不存在。
- 下一版 mapping 文件未在本轮创建。

## 边界

不做 mapping、数据清洗、Gold 构建、训练或 taxonomy 修改。
