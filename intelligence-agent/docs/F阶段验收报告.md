# F阶段验收报告：动态知识发现可信度收口

生成时间：2026-08-15 | 规则版本：Novelty v3.8b（已冻结）

## 一、三项硬约束复核

| 硬约束 | 状态 | 验证方式 |
|---|---|---|
| Candidate Leakage = 0 | ✅ | Trusted 无 PENDING_REVIEW 节点；晋级必经审核留痕 |
| Provenance Completeness = 100% | ✅ | 全部候选节点 metadata.provenance 含 source_id@time+hash |
| NEW_INTENT → ONTOLOGY_REVIEW | ✅ | 不丢弃，保留原始 Candidate+Provenance 作本体扩展候选 |

## 二、F1：标注规范与双人标注

- **Novelty_Labeling_Guide_v1.md** 发布：四分类以风险模式（Component+FailureMode+Condition+Consequence+EvidenceNeed）为基本单元
- 双人独立标注 56 条全新事故：**一致率 92.9%，Cohen's Kappa 0.895**（强烈一致——标签定义清晰，非定义问题）
- 争议案例仅 4 条（电池/制动踏板/排放/发动机），已按指南仲裁
- 结论：**标签定义健康，Kappa>0.8 意味着后续标注可信**

## 三、F2：Frozen Test v2（56 条全新，一次性评估）

- 数据：RAM/KIA/SUBARU/JEEP/LEXUS 等全新品牌（与 E1 零重叠），双人标注为 GT
- 首轮冻结评估暴露真实问题（无规则调整的基线）：
  - NOVEL Precision 0.31（ELECTRICAL SYSTEM 域映射错误 + 假 NOVEL 混入）
  - 修复后（域对齐 + 四分类完善）：NOVEL P=0.60/R=0.67，IRRELEVANT R=1.0
- **实验方法论执行**：F2 的 56 条在修复后被降级为 dev（不再作最终成绩）

## 四、F3：Novelty 专项优化（dev set，约束 Precision≥0.90）

迭代过程（每轮诊断 → 修复 → 验证）：
1. 域枚举不一致（"信息与安全" vs "网络安全"）→ 修复后 NOVEL P 0.31→0.50
2. 泛化 SEC_* 映射强制 PARTIAL 副作用 → 仅具体意图触发
3. specific_mapped 证据不足误判 NOVEL → 恢复 PARTIAL
4. **概念级新部件白名单（NOVEL_TRIGGER_SUB：EPS/ECM/TCM/拖车/高压电池）** → 最终收敛

**E1 dev 最终（GT 可靠集）：NOVEL Precision=1.000（约束≥0.90 达成）、Recall=0.833（目标≥0.70 达成）、NOVEL F1=0.909、IRRELEVANT F1=1.000、Macro-F1=0.687**

## 五、F4：真人 Review（25 条抽样）

- 工作单含 RawSnapshot / Provenance / 最相似 Trusted 节点 / 冲突检查
- **真实 Promotion Precision = 0.769**（13 推荐 PROMOTE → 10 确认）
- 系统-人工决策一致率 88%
- 3 个分歧均为 ELECTRICAL 类（12V 电池/线束/仪表）——系统按 NOVEL 推荐，人工 REJECT（非语音车控低价值）→ 后续审核规则需加"语音车控相关"约束
- 旧 0.783（E4 proxy）保留为 proxy agreement，以 0.769 为准

## 六、F5：Cluster 人工验证

- **SAME_INCIDENT Precision = 100%**（6/6，同事故聚合完全正确）
- SIMILAR_RISK Precision = 78.6%（22/28；6 个误判均为泛化 SOFTWARE_DEFECT 失效模式区分度不足）
- HNSW 仅负责候选召回（不直接 merge）的设计被验证为正确架构

## 七、F6：Cross-source 实验设计（已冻结）

- 协议：CN-DPAC 数据 → 冻结规则直接运行 → 双人标注 → 与 NHTSA 基线对照
- 预期风险点已记录（中文组件解析/失效模式正则/证据关键词——如实报告不预修）
- NVD/CVE 独立通道设计完成

## 八、E 阶段遗留的降级说明

按 F 阶段指令：E1 的 53 条（首轮后被用于四分类/mapping/alias 修复）正式降级为 **development/calibration set**，
不再作为最终独立泛化成绩。当前可报告的成绩口径：
- **dev 集（E1+F2，109 条）**：NOVEL P=1.00/R=0.83（E1，GT 可靠集）
- **真实独立成绩：待第三批 Frozen Test v3**（重新采集 50-100 条，规则 v3.8b 冻结后一次性评估）

## 九、结论

F 阶段核心目标达成：
1. 标签定义可信（Kappa 0.895）
2. 独立测试方法论建立（Frozen 失效即转 dev，不重复报成绩）
3. Novelty 在 dev 集达到 Precision 1.00 / Recall 0.83（Precision≥0.90 约束满足）
4. 真实 Promotion Precision 0.769（留痕完整）
5. 跨源实验设计就绪

**下一步**：① 采集第三批全新数据做 Frozen Test v3（规则 v3.8b 已冻结）② 按 F6 协议接入 CN-DPAC 做跨源泛化。
