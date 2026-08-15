# intelligence-agent —— 动态安全情报与态势感知模块

> 语证（yuzheng）系统中的**离线知识演进链**：从全球多源真实情报中发现新风险，经受控审核回流为可信安全知识。

本目录是一个**自包含模块**，只依赖标准 Python 库与 hnswlib/sentence-transformers/httpx，与主系统其余部分解耦运行。运行入口与说明见下文。

---

## 一、本模块在语证中的位置（如何与主系统连接）

语证完整主线分两条链：

```
【在线裁决链】（主系统）
用户语音 → ASR+语义 → Intent ID → 安全知识检索需求
  → Trusted Safety KB → HNSW Top-K
  → Required Evidence ∪ Mandatory Evidence → Evidence Resolver
  → CARLA/CAN/Camera/Sensor 实时物理证据
  → HardRule + CBN → PASS/REVIEW/BLOCK → 解释 + 审计

【离线知识演进链】（本模块 intelligence-agent）
事故/召回/投诉/态势感知
  → Raw Intelligence Lake
  → Cluster / Analyzer
  → Risk Pattern / Situation Awareness
  → Candidate Risk Knowledge
  → Review / Conflict Check / Version Freeze
  → Trusted KB（回流主系统）
```

### 连接点（接口契约）

| 本模块产出 | 主系统消费 | 位置 |
|---|---|---|
| Trusted 知识节点（KnowledgeNode v2 JSONL） | 重建 `safety_trusted_hnsw` 索引 | `backend/safety_knowledge/intelligence/` 审核晋级 → 主系统 `backend/app/services/regulation/` 重建 HNSW |
| Candidate 节点（L5/PENDING） | 人工审核面板 | 候选不参与在线裁决（Leakage=0） |
| 覆盖矩阵 / Golden Cases / Frozen Test | 检索质量评测 | 主系统 HNSW 的证据需求推导正确性依据 |
| 态势预警 / 风险模式 | 知识补盲方向 | 指导法规条款补充顺序 |

### 安全边界（两侧共同保证）

- **在线 HNSW 只索引 `status=ACTIVE 且 node_type=Trusted`**——Candidate Leakage=0 由代码约束保证；
- 本模块全部产出先入 Candidate 域（L5/PENDING），人工审核 + 冲突检查 + 版本冻结后才成为 Trusted；
- 每条记录保留完整 Provenance（source / retrieved_at / content_hash / parser_version）。

---

## 二、目录结构

```
intelligence-agent/
├── README.md                    ← 本文件（连接说明）
├── requirements.txt
├── backend/safety_knowledge/intelligence/
│   ├── models.py                ← 统一数据模型 + 枚举体系（FailureMode/Consequence/…）
│   └── agent/                   ← 9 层管线实现
│       ├── source_layer.py      ← L1 原始快照（不可变 + hash）
│       ├── unified_adapter.py   ← 统一 Adapter（NHTSA 三源/NVD，fetch_since 接口）
│       ├── cn_adapter.py        ← 中国车质网
│       ├── eu_adapter.py        ← 英国 DVSA（表单交互）
│       ├── clusterer.py         ← L2 IncidentCluster 聚合
│       ├── analyzer.py          ← L3 组件/失效/条件/后果/严重度
│       ├── source_analyzer.py   ← Source-Specific（投诉口语 + 中文正则）
│       ├── mapping_v2.py        ← L4 三路融合 + ABSTAIN
│       ├── novelty_engine.py    ← L5 四分类新颖性
│       ├── prioritizer.py       ← L6 P0/P1/P2 审核优先级
│       ├── node_builder.py      ← L7 Candidate 节点（L5）
│       ├── integrator.py        ← L8 审核 + L9 冲突检查/晋级
│       ├── reporter.py          ← 整合报告
│       └── relevance.py         ← VoiceControlRelevance（DIRECT/INDIRECT/NONE）
├── scripts/                     ← 运行入口（采集/分析/态势/评测）
├── data/
│   ├── samples/                 ← 每来源 20 条样例（全量数据不入库）
│   └── manifests/               ← Raw Lake 数据清单（来源/数量/哈希）
└── docs/                        ← 各阶段报告 + 论文
```

## 三、运行入口

```bash
pip install -r requirements.txt

# 多源采集（NHTSA/DVSA/车质网/NVD）
python scripts/s80_h4_bulk_collect.py

# 全量分析（Source-Specific Analyzer，14k+ Cluster）
python scripts/s100_ssa_rerun.py

# 态势感知（Endsley L1-L3）
python scripts/s112_situational_awareness.py

# 态势 → 知识回流（Candidate 生成）
python scripts/s114_sa_to_kb.py

# Novelty 独立评测（Frozen Test v3）
python scripts/s71_g1_frozen_v3.py
```

## 四、核心实验结果（截至 2026-08-15）

| 指标 | 结果 |
|---|---|
| 多源采集吞吐 | 140,727 条（去重后 15,935 唯一；US/EU/CN/CYBER 四地域） |
| 分析规模 | 14,041 Cluster 全量分析（Coverage 100%） |
| 早期风险信号 | 1,854（投诉先行，随规模同步增长） |
| 时间线证据 | 同车型投诉先行于召回（AEB 提前 126 天，200 条聚集） |
| 检索质量（主系统对接） | Frozen Test：MMR=0、Evidence Recall 0.965 |
| Candidate Leakage | 0（硬约束） |
| Provenance | 100%（硬约束） |
| 标注一致性 | Kappa=0.895（双人独立标注） |

详细报告见 `docs/`（含论文《面向高风险智能座舱车控的可信知识驱动安全裁决系统》）。
