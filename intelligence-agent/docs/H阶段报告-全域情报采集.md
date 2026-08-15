# H阶段报告：全域汽车安全情报持续采集与知识扩充

生成时间：2026-08-15

## 一、核心成果

### H1 Source Registry v3（35 个来源登记）

| 维度 | 覆盖 |
|---|---|
| 地域 | US 12 / CN 12 / EU 7 / GLOBAL 4 |
| 类型 | RECALL 8 / COMPLAINT 2 / INVESTIGATION 1 / INCIDENT 7 / MANUFACTURER_NOTICE 8 / REGULATION 5 / CYBER 4 |
| 权威层级 | L1 政府监管 21 / L2 OEM 8 / L3 权威机构 4 / L4 媒体 2 |
| 已启用 | NHTSA-RCL / NHTSA-CSI / NHTSA-INV / CN-DPAC / EU-SafetyGate / CYBER-NVD |

### H2 Raw Intelligence Lake（建立）

```
data/safety_intelligence/raw/{us,cn,eu,cyber}/
  US-NHTSA-RCL_*.jsonl   303 条
  US-NHTSA-CSI_*.jsonl   7314 条
  CYBER-NVD_*.jsonl      20 条
digests/digest_2026-08-15.md
```
**Raw 永久保留原则执行**：Novelty/Mapping 全部为派生层（analysis_version=v3.8b 可重跑），算法判断不删除原始数据。

### H3 Unified Adapter（统一接口）

- `RawIntelligenceRecord` 统一 Schema（事实层 25 字段，不含 intent/novelty 推断）
- 所有 Adapter 实现 `fetch_since()` → 同一 Schema
- NHTSAAdapter（RCL/CSI/INV 三源）+ CNDpacAdapter + EUSafetyGateAdapter + CyberNvdAdapter

### H4 规模采集（第一轮：7,637 条 Raw，超 1000+ 目标 7 倍）

| 源 | 条数 | 状态 |
|---|---|---|
| US-NHTSA-RCL 召回 | 303 | ✅ 52 组车辆 |
| US-NHTSA-CSI 投诉 | 7,314 | ✅ 36 组（去重后） |
| CYBER-NVD CVE | 20 | ✅ automotive 关键词（独立通道） |
| CN-DPAC | 0 | ⚠️ SSL 断连（已记录，待重试/代理） |
| EU-SafetyGate | 0 | ⚠️ JS 渲染页面（已记录） |
| US-NHTSA-INV | 0 | ⚠️ 需 API key（403） |

### H5 跨源去重/聚类

- 跨源去重率 0.9%（投诉高度唯一，符合预期）
- **IncidentCluster：6,882**（规模效应显现，incident_hnsw 进入真实工作规模）
- 投诉数据价值验证：**UNINTENDED_ACTIVATION 38 条 + INTERMITTENT_FAILURE 27 条**——投诉确实比召回更早暴露未成形风险模式

### H6 风险模式抽取（analysis_version=v3.8b，抽样 800 cluster）

- FM Top：UNKNOWN 622（投诉文本噪音，后续分析器改进点）/ SOFTWARE_DEFECT 45 / UNINTENDED_ACTIVATION 38
- CONS Top：COLLISION 214 / OCCUPANT_INJURY 169 / FIRE 155
- **高风险候选 140**（SEV<=2 且车控相关）

### H7 Trusted 边界复核

| 硬约束 | 状态 |
|---|---|
| Candidate Leakage = 0 | ✅ 采集层全部进 Raw Lake，无任何数据绕过审核进入 Trusted |
| Provenance Completeness = 100% | ✅ 统一 Schema 含 source/retrieved_at/hash/parser_version |
| 宽进严出 | ✅ 7,637 Raw → 候选审核 → Trusted（未经验证不进入） |

### H8 Safety Intelligence Digest（首期已生成）

```
Raw Lake：7,637 条 | Cluster：6,882 | 高风险候选：140
FM Top：SOFTWARE_DEFECT 45 / UNINTENDED_ACTIVATION 38
知识覆盖缺口线索：新组件家族列表（30+）
```

## 二、关键工程问题与解决

1. **complaints API 字段差异**（`components`/`summary` 小写 vs Recall 的 `Component`/`Summary`）→ 统一 _parse 适配
2. **投诉结构化信号**：crash/fire/injuries/deaths 字段已提取到 extra.signal，作为严重度线索
3. **CN/EU 受限源**：SSL 断连 + JS 渲染——如实记录，后续用代理/官方 API 通道接入
4. **Raw Lake 损坏行容错**：load 层跳过损坏行，源文件永久保留

## 三、数据漏斗（当前状态）

```
7,637 Raw Records（第一轮）
  → 7,566 Normalized
  → 6,882 Clusters
  → 800 抽样分析（140 高风险候选）
  → Candidate Risk Nodes（待跑批）
  → Trusted（审核后，未新增）
```

## 四、下一步

1. **CSI 全量分析跑批**（7,314 条投诉 → 全量 Cluster → Candidate，找召回之前的新风险）
2. **CN-DPAC 接入**（代理/API 通道，中文源跨源测试）
3. **持续采集调度**（watch 模式 + 增量 fetch_since）
4. **v3.9 Novelty 结构性盲区判定**（Raw Lake 7,637 条可作为重跑数据源——算法与采集已解耦）

## 五、与关键技术二的关系

H 阶段建立了"知识安全"线的**数据基础**：
- Trusted KB（120 节点，静态，可追溯）→ 法规/标准
- Raw Intelligence Lake（7,637 条，动态，不可变）→ 真实召回/投诉/CVE
- 数据漏斗（Raw → Cluster → Candidate → 审核 → Trusted）→ 受控知识更新
- 两个硬约束数字保持：**Leakage=0、Provenance=100%**
