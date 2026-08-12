# Phase4 Mandatory Recall 与 Intent-Scoped SAS 收口设计

## 背景与目标

第四阶段 ownership 已迁移到 `IntentEvidenceBinding`，但仍有两个未闭合点：Mandatory Recall 可能跳过最新异常 observation；`semantic_similarity` 仍存于物理 `EvidenceNode`，导致多 Intent 共用节点时只保留最大值。

目标是忠实保留最新 exact-type 事实，并让 query 与 evidence node 的相似度只属于 occurrence binding。

## 现状与约束

- occurrence 唯一键仍为 `(clause_index, intent_id)`。
- HNSW 参数、Quality/Memory/Causal 数学公式不变。
- 物理 EvidenceNode 只按 `node_id` 去重，不按 Intent clone。
- MISSING 仍按 `(turn_id, evidence_type)` 共享。
- 不增加新的 canonical Pydantic model。

## 方案对比

### 方案一：原子删除节点 SAS，Binding 唯一化（采用）

- 从 `EvidenceNode` 删除 `semantic_similarity`。
- 给 `IntentEvidenceBinding` 增加 `semantic_similarity: float | None`。
- HNSW 运行时用 occurrence-scoped candidate similarity map 传递分数。
- turn-level 下游只使用 resolution projection 的即时聚合。

优点：没有第二事实源，可以完整恢复每个 Intent 自己的 SAS。缺点：需要一次性迁移全部消费者和测试。

### 方案二：保留节点占位字段

消费者改读 binding，但节点继续保存无权威值。改动较小，但字段容易被再次误用，不采用。

### 方案三：Binding 与节点双写

继续保留节点 max SAS。会形成双事实源，不采用。

## 详细设计

### Mandatory Recall

Repository 的 `latest_resolved()` 恢复为返回最新 exact-type observation，不过滤质量状态。

- VALID/SUSPICIOUS：绑定原节点，状态 `MANDATORY_RECALLED`。
- STALE：绑定最新 STALE 原节点，由 `mandatory_stale` 阻断。
- TAMPERED：绑定最新 TAMPERED 原节点，由 `mandatory_tampered` 阻断。
- MISSING：转换到本轮共享 MISSING placeholder。

不得越过较新的异常事实寻找旧 VALID。

### Intent-scoped semantic similarity

HNSW 每个 occurrence 产生 `node_id -> similarity` map。Binding 创建时保存当前 occurrence 的分数；Mandatory Recall 对被召回节点重新计算当前 query 的分数；MISSING 与 OPTIONAL_NOT_FOUND 使用 `None`。

Projection 即时派生：

- required binding SAS 序列，供 turn-level Quality 继续做算术平均；required MISSING 按既有语义贡献 0。
- resolved binding SAS 序列。
- 每个物理 node 的投影 SAS，用于当前 Memory/Causal 公式；为保持旧 turn-level 行为使用 binding 分数的最大值，但该值不写回物理节点。

### 消费者迁移

- Quality：SAS 只读 required/all binding 投影。
- Memory/Causal：接收 projection 的 per-node SAS，不读取 EvidenceNode。
- Presentation：Intent demand item 展示 binding SAS；node detail 不再展示节点 SAS；turn-level retrieval candidate 使用即时 per-node 投影。
- Canonicalization、Repository、Pipeline：删除节点 SAS 的构造、合并和复制逻辑。

## 测试策略

- 旧 VALID + 新 STALE/TAMPERED + HNSW miss，必须绑定最新异常节点并触发硬门。
- 新 MISSING + 旧 VALID，必须使用共享 MISSING。
- 同一物理节点被两个 Intent 绑定时保存两个不同 SAS。
- 物理节点列表仍只有一份，且 Schema 不含 `semantic_similarity`。
- Quality 使用全部 required bindings 的 SAS，不能使用物理节点 max。
- Memory/Causal 只接收 projection SAS。
- 运行 Phase4、SafetyGate、Quality、Memory、Causal、Presentation、Pipeline、Scenario、frozen99、compileall 与 diff 检查。
