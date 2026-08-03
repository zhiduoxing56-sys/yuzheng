# 软件修整第二步：HNSW安全分层与检索导航设计

## 背景与目标

在不改变现有 CommandPipeline、安全公式、强制召回和裁决语义的前提下，将单一真实 hnswlib 索引扩展为可审计的安全分层索引组，并补齐证据页面所需的真实导航数据。最终 Top-K 仍以真实 BGE 查询向量和 layer 0 的 `hnswlib.Index.knn_query` 为唯一 ANN 来源。

## PDF依据与工程边界

PDF 式2.8明确：`lmax(e)=min(L,randlevel(e)+floor((s(e)/3)*(L/2)))`，并给出四类安全语义和几何分布 `P(l)∝exp(-l/L)`。PDF没有规定 `L` 数值、四类到编号的完整映射、seed、离散采样实现或应用层内部 trace Schema。

本轮经用户批准采用 `L=3`，安全 rank 为 `ENTERTAINMENT=0, COCKPIT=1, DRIVING=2, EMERGENCY=3`。该编号映射来自现有 `L0_ENTERTAINMENT/L1_CABIN/L2_DRIVING/L3_EMERGENCY`，来源固定为 `EXISTING_PROJECT_MAPPING`；`CABIN` 只作为旧名输入，公开统一为 `COCKPIT`。L来源为 `ENGINEERING_CONFIG`。式2.8来源为 `REPORT_EXPLICIT`。

L=3时安全增量严格为 `0,0,1,1`，不得修改公式以人为制造四个不同增量。基础 `randlevel` 通过稳定物理身份、`index_seed` 和 `formula_version` 的 SHA-256 均匀量，再按报告几何分布作确定性工程实现；采样与seed来源标记为 `ENGINEERING_REALIZATION/ENGINEERING_CONFIG`。

## 方案对比与选择

- 单索引内部level/trace：当前 hnswlib 0.8.0 公开API不支持指定/读取节点level、entry point或visited nodes，不能安全采用。
- 三层图示复刻：图2.9只是示意，不能作为固定层数数据来源。
- 四个累积真实索引：每个节点进入0..hnsw_max_layer，每层均为独立真实 hnswlib.Index。此方案被采用，`layering_mode=CUMULATIVE_REAL_HNSWLIB_INDICES`。

## 架构与原子快照

在现有索引服务内集中加入安全分类器、式2.8层级计算器、不可变构建快照和分层查询器，继续复用唯一 embedder、证据仓库及 label/node 映射。构建先在锁外完成候选快照和全部真实索引，验证 base 覆盖、层级单调性、映射完整度与真实对象后，在锁内一次性替换；失败保留旧快照。读取先捕获快照引用，避免看到半构建状态。

build_id由公式版本、seed、索引参数、分类版本、配置摘要和节点集合摘要确定性生成。node_set_digest只包含稳定节点身份及元数据摘要，不包含向量。审计不保存向量、模型路径、私有指针或hnswlib二进制。

### 稳定索引身份与构建摘要

索引明确区分三类身份：

- `runtime_node_id`：现有 `EvidenceNode.node_id`，由UUID生成，仅用于当前turn节点引用、审计子图、API节点详情、Top-K/锚点/mandatory引用和hnswlib label映射。它不得进入randlevel、node_set_digest或build_id。
- `stable_physical_identity`：版本 `STABLE_PHYSICAL_IDENTITY_V1`，来源 `EXISTING_EVIDENCE_STREAM_KEY`。规范字段为已存在的 `evidence_type`、`source`，以及按 `entity_id/rule_id/area/global` 优先级解析的稳定来源实体。字符串做Unicode NFC和首尾空白规范化，不假定不存在的sensor_id。
- `content_identity`：版本 `INDEX_CONTENT_IDENTITY_V1`。对 `layer/value/unit/timestamp/expires_at/freshness/consistency/availability/quality_label/integrity_hash` 的规范JSON做SHA-256；不包含node_id、built_at、turn_id、临时路径或对象地址。独立内容摘要用于覆盖外部节点缺少规范integrity payload或篡改状态统一使用无效hash的情况。

`stable_index_fingerprint` 版本为 `STABLE_INDEX_FINGERPRINT_V1`。规范载荷包含稳定身份版本与值、内容身份、security_class、security_rank、hnsw_max_layer、classification_source和formula_version；enum转为字符串，JSON固定排序、UTF-8、紧凑分隔符，使用SHA-256，不使用Python `hash()`。

`node_set_digest` 是实际进入索引的逻辑节点指纹多重集合摘要：先按物理身份选择最新内容版本；若同批存在多个完全相同的最新节点，则保留重复数量。最终对按指纹排序的 `fingerprint + count` 列表做SHA-256。节点顺序和UUID变化不影响摘要，内容、物理身份、分类、最大层或重复数量变化会改变摘要。

内部索引键使用稳定身份、指纹和occurrence序号，避免UUID参与排序；每次构建的hnswlib label仍映射到该批真实运行节点ID。因此不同UUID的等价重建可拥有相同build_id和层级成员摘要，但导航node_id仍是各次构建的真实运行ID，不承诺跨构建相同。

`build_id` 的规范载荷显式覆盖 node_set_digest、formula_version、index_seed、L、security/classification mapping版本及摘要、完整index config摘要、embedding implementation/model/dimension、cosine space、M、ef_construction、ef_search、top_k和layering_mode。`built_at`仅用于展示和审计，不参与build_id。

randlevel继续绑定 `stable_physical_identity + index_seed + formula_version`。同一物理流仅value更新时randlevel保持稳定；seed或物理身份变化时允许变化。PDF式2.8的加号与安全增量不变。

## 查询与轨迹

查询从最高非空层严格下降，每层调用该层真实 `knn_query`，请求数为 `min(efSearch,node_count)`；候选按 SAS 降序、node_id稳定排序，首项作为展示锚点。layer 0独立执行真实Top-K查询并产生唯一生产候选。MandatoryRecall继续在其后运行。

应用层轨迹固定声明：`trace_kind=SECURITY_LAYER_INDEX_TRACE`、`trace_source=REAL_HNSWLIB_LAYER_QUERIES`、`is_internal_hnsw_trace=false`。内部level、entry point、visited nodes和内部navigation path保持空；`internal_hnsw_trace_reason=UNSUPPORTED_BY_PUBLIC_HNSWLIB_API`。

## Schema、审计与降级

扩充现有 `RetrievalMetadata`、`AuditRecord` 和前端契约，不创建第二套 EvidenceNode 或 RetrievalMetadata。轨迹只引用节点ID与受限候选摘要。AuditRecord保存构建ID、摘要、分层状态、导航、可视化路径、最终Top-K与内部轨迹可用性；ReviewOutcome不复制轨迹。presentation、audit detail与节点详情只从原始审计读取，不重新查询索引。

正常模式 availability 为 `AVAILABLE`；exact cosine降级为 `DEGRADED_UNAVAILABLE` 且不生成假分层路径；旧审计为 `LEGACY_NOT_RECORDED`。WebSocket仅发送构建、层计数、锚点路径和Top-K计数摘要，每层候选最多5项且不发送向量。

## 安全隔离

security_class、最大层、导航和可视化只影响真实分层检索及说明，不直接进入 Safety Gate、EAS、SafetyScore、merge_decision、令牌或执行器。第一步公式、动作证据映射、CANCEL追加式审计和裁决阈值均保持不变。

## 测试策略

覆盖式2.8边界与0/0/1/1增量、确定性seed、四类映射、未知类型base-only、四个真实索引、累积成员关系、原子构建、逐层真实候选、base Top-K、强制召回顺序、路径真实性、审计重启回放、legacy/degraded、GET无副作用、WebSocket摘要、OpenAPI契约及全部Step1安全回归。稳定身份专项测试必须使用两批重新实例化且UUID不同的节点，并覆盖顺序变化、内容变化、物理身份变化、仅UUID变化、built_at变化、seed变化、分类变化、重复数量变化，以及等价重建仍返回当前批真实node_id而不泄露旧UUID。

## 已知限制

hnswlib公开API不提供内部入口点、节点内部层级和visited path。本轮交付的是由多个真实 hnswlib 索引查询构成的安全层导航轨迹，不是原生HNSW内部遍历轨迹。候选解释和受限LLM解释留待Step5，契约保持DRAFT且不冻结。

稳定物理身份的当前限制是项目只提供 evidence type、source 和可选 entity/rule/area 标识；没有通用硬件sensor_id。缺少这些可选实体标识时使用明确的 `global`，不得推断硬件身份。完全相同的重复节点通过occurrence保留数量，但其运行期UUID与相同距离下的展示顺序不承诺跨构建一致。
