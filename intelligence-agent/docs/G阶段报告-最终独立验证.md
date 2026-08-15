# G阶段报告：最终独立泛化验证结果（如实保存）

生成时间：2026-08-15 | 规则版本：v3.8b（冻结，未被 G1 结果修改）

## 一、G1 Frozen Test v3 —— 最终独立成绩（一次性评估，未修改重报）

样本：77 条 ground truth（69 真实召回：13 个全新品牌 + 8 条难例），63 个 Cluster
标注一致率：92.2%（Kappa 口径与 F1 一致）

| 类别 | Precision (95% CI) | Recall (95% CI) | F1 |
|---|---|---|---|
| KNOWN | 0.000 | 0.000 | 0.000 |
| PARTIAL_NOVEL | 0.545 (0.35-0.73) | 0.571 (0.37-0.76) | 0.558 |
| **NOVEL** | **0.500 (0.24-0.76)** | **0.556 (0.27-0.81)** | **0.526** |
| IRRELEVANT | 0.871 (0.71-0.95) | 0.964 (0.82-0.99) | 0.915 |
| Macro-F1 | | | 0.500 |

Triage：P=0.849 / R=0.800 / F1=0.824 | ABSTAIN Precision：0.867（26/30）

**验收门槛判定：NOVEL Precision≥0.90 FAIL / NOVEL Recall≥0.70 FAIL / Triage F1≥0.95 FAIL**

### 难例专项（用户预言的验证点，全部命中）

| 难例 | GT | 系统判定 | 结论 |
|---|---|---|---|
| 转向线控执行器（ACTUATOR，白名单外新部件） | NOVEL | PARTIAL | **暴露白名单局限：系统记住的是"EPS/ECM/拖车/高压电池叫新风险"，不是"知识盲区"概念** |
| 刹车线控/坡道保持执行器 | NOVEL | NOVEL(部分) | 部分命中 |
| 气囊爆炸（严重但非车控） | IRRELEVANT | PARTIAL×1 | 1 例误判 |
| 前照灯/雨刮（伪 KNOWN） | KNOWN | PARTIAL | KNOWN 全漏（5/5）——KNOWN 判定双条件过严 |

## 二、按纪律执行

1. G1 成绩照实保存：`data/intelligence_agent_v3/g1_frozen/g1_final_results.json`
2. **v3 降级为分析集**（不再作为独立成绩）
3. 根因已记录，供 v3.9 开发：
   - R1：NOVEL_TRIGGER_SUB 白名单机制 = 记住了部件名而非"盲区"概念 → 需改为**结构性盲区判定**（如：组件家族在知识库无节点 且 涉及执行能力 → NOVEL，而非子项白名单）
   - R2：KNOWN 判定需放宽（specific_mapped + 家族已知 → 至少 KNOWN 候选）
   - R3：NOVEL→PARTIAL 的 4 个漏检（线控执行器等）与白名单外新部件直接相关
4. 下一步：v3.9 修改 → 再采 Frozen v4（第四批）

## 三、G2 VoiceControlRelevance（已实现，dev 验证）

| 级别 | 定义 | dev 分布 |
|---|---|---|
| DIRECT | 直接语音车控执行 | 19 |
| INDIRECT | 影响车控依赖链（电子/软件/控制单元） | 11 |
| NONE | 与语音车控无关 | 10 |

- F4 的 3 个误推（12V 电池/线束/仪表）现在全部正确归入 INDIRECT → 不再强 PROMOTE
- STRONG_PROMOTE 仅限 NOVEL+DIRECT；NONE → ARCHIVE
- 预期 Promotion Precision 提升（待 F4 重测）

## 四、G3 FailureMode 层次化（已实现，验证）

- SOFTWARE_DEFECT 拆分 9 个 Subtype（LOGIC/TIMING/STATE_MACHINE/UPDATE/SENSOR/ACTUATOR/COMMUNICATION/MEMORY/UI）
- **SIMILAR_RISK Precision：78.6% → 96.4%**（修复 5 个"都叫软件缺陷"的误聚）

## 五、G5 最终统计表（截至 G 阶段）

### 静态知识库（Trusted KB）

| 指标 | 值 |
|---|---|
| 知识节点 | 120（11 域 / 19 来源） |
| 覆盖矩阵 | COVERED 116 / PARTIAL 0 / GAP 2 |
| Mandatory Evidence Coverage | 97.3% |
| MMR（dev 80 条） | 0 |
| Frozen Retrieval FER（42 条） | 0.965 |
| HNSW vs Exact（ef=50） | Recall 1.0000 |

### 动态情报智能体

| 指标 | 值 | 状态 |
|---|---|---|
| Candidate Leakage | **0** | ✅ 硬约束 |
| Provenance Completeness | **100%** | ✅ 硬约束 |
| 标注一致率（F1，Kappa） | 0.895 | ✅ |
| 标注一致率（G1） | 92.2% | ✅ |
| dev Novel Precision（E1） | 1.000（v3.8b） | dev 口径 |
| dev Novel Recall（E1） | 0.833 | dev 口径 |
| **Frozen v3 Novel P/R（独立）** | **0.500 / 0.556** | ❌ 未达标，v3 降级 |
| Triage F1（Frozen v3） | 0.824 | ❌ 未达标 |
| Promotion Precision（F4 真人） | 0.769 | 待 G2 重测 |
| SIMILAR_RISK Precision | 96.4%（G3 后） | ✅ |
| ABSTAIN Precision | 0.867 | — |

## 六、关键技术二叙事（当前可写内容）

**静态可信知识 + 动态风险发现 + 受控知识更新**：
- 法规/标准 → 可追溯 Trusted KB（120 节点，19 来源，覆盖 97.3%）
- 事故/召回 → 情报智能体（9 层，IncidentCluster→Candidate Risk Node）
- 硬约束：Candidate Leakage=0、Provenance=100%、NEW_INTENT→ONTOLOGY_REVIEW
- **Novelty 泛化：开发集 Precision 1.00/Recall 0.83；独立冻结测试进行中（v3 未达标，v4 待采）**

答辩口径（诚实版）：
"开发集上 Novel Precision 达到 100%、Recall 83.3%；首次独立冻结测试（77 条全新数据）暴露了白名单机制的泛化局限（NOVEL P=0.50/R=0.56），正在通过结构性盲区判定改进。动态知识发现机制的工程闭环与安全边界已验证（Leakage=0、Provenance=100%）。"
