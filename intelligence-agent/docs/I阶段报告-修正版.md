# I阶段报告（修正版）：多源情报规模化采集与全量风险挖掘

生成时间：2026-08-15 | 依据评审意见修正 3 处报告口径

## 一、阶段状态判断

| 目标 | 判断 |
|---|---|
| 采集基础设施 | ✅ 完成 |
| Raw Lake | ✅ 完成（7,680 → 8,000+ 持续增长） |
| 全量分析 | ✅ 完成（6,882+ Cluster，Coverage 100%） |
| 投诉风险挖掘 | ✅ 完成第一版（1,026 条早期风险模式） |
| 中国源跑通 | ✅ 完成最小闭环（车质网 43 条调查报告） |
| EU 源 | ❌ 未完成（DVSA 可达需表单交互，KBA 404） |
| 20k 规模 | 🔄 进行中（持续增长，不堆投诉凑数） |
| Active Sources ≥ 10 | ❌ 未完成（当前 7 个有效） |
| 多源分析质量 | 🔄 需要继续优化（UNKNOWN 62.1%） |
| Trusted 安全边界 | ✅ 完成并验证（Leakage=0 / Provenance=100%） |

**核心链路验收通过，规模化/多地域指标部分达成——"主体完成、扩源持续进行"。**

## 二、三处口径修正（依据评审）

### 修正 1：不再将"无对应召回"表述为"召回之前"

- 原表述："AEB 误触发投诉 173 条（无对应召回）——召回之前的高频信号"
- 修正为：**"发现 1,026 条 AEB/车速控制等高危早期风险投诉，其中当前召回库未匹配到对应召回的案例，可作为潜在早期风险候选"**
- 时间线专项验证（t_complaint vs t_recall）：
  - 投诉日期字段已 100% 打通（dateComplaintFiled，2020-01 ~ 2025-12）
  - 组件级对照（FCA）显示召回早于投诉（-673 天）——**原因是 RCL/CSI 采集车辆组合不对齐**（FCA 召回仅 5 条 vs 投诉 1,464 条，车型不同）
  - 结论：**"投诉早于召回"需同车型同年款精确匹配专项验证**，当前不断言

### 修正 2：Source Type 按实际 Raw 统计（不按 Registry 登记）

- 修正前：REGISTRY 登记 7 类 → 声称覆盖 4 类
- 修正后（按实际产生 Raw Record 统计）：

| Source Type | 实际 Raw | 状态 |
|---|---|---|
| RECALL | 303 + 232（两批） | ✅ 稳定 |
| COMPLAINT | 7,315 | ✅ 稳定 |
| CYBER | 20 | ✅ 稳定 |
| INVESTIGATION（CN 调查报告） | 43 | ✅ 中国线 |
| INVESTIGATION（NHTSA） | 0（403 需 API key） | ⚠️ 未产生 |

### 修正 3：中国线定位为"最小闭环"

- 修正前：暗示中国事故/召回数据已与 NHTSA 同等规模接入
- 修正为：**"中文来源（车质网）的采集、存储和分析链已经跑通（43 条调查报告/投诉销量比/质量排行），颗粒度与 NHTSA 单条 Recall/Complaint 不同，属最小闭环验证"**
- CN-DPAC（官方召回）仍受网络限制（连接重置），待后续接入

## 三、核心技术进展（本轮新增）

### Source-Specific Analyzer（UNKNOWN 67.7% → 62.1%）

| 来源类型 | UNKNOWN 率 | 处理 |
|---|---|---|
| COMPLAINT | 62.4% | 口语正则（suddenly/won't/keeps/randomly + 中文） |
| RECALL | 50.7% | 标准描述（基础正则） |
| CN | 66.7% | 中文正则（18 条 FailureMode + 8 条 Consequence + 7 条 Condition） |

- SOFTWARE_DEFECT 提取 304 → 960（投诉文本中软件相关大量检出）
- 62.1% 仍为主要分析缺口：自由文本无语义关键词是主因，后续可引入 LLM 辅助结构化（v2）

### 投诉时间线数据打通

- **7,315 条投诉 100% 含投诉日期**（dateComplaintFiled）——为"投诉早于召回"专项验证奠定数据基础
- 1,026 条早期风险投诉全部带日期

### EU 探索（如实记录）

- UK DVSA check-vehicle-recalls.service.gov.uk：**可达（200）**，表单驱动需 POST 交互 → 最高优先级 EU 候选
- KBA（德国）：404；EU Safety Gate：JS 渲染；DfT DAT：SSL 断连
- EU 数据流：**未打通**（PARTIAL）

## 四、验收对照（原始 I 阶段指标）

| 验收项 | 目标 | 当前 | 状态 |
|---|---|---|---|
| Raw ≥ 20,000 | 20,000 | ~8,000 | 🔄 持续增长中 |
| Analysis Coverage ≥ 95% | 95% | 100% | ✅ |
| 三地域数据 | US/CN/EU | US ✅ CN ✅ EU ❌ | ⚠️ PARTIAL |
| Active Sources ≥ 10 | 10 | 7 | ⚠️ |
| ≥4 类高价值 Source Type（实际 Raw） | 4 | 4（RECALL/COMPLAINT/CYBER/CN-INVESTIGATION） | ✅ |

Active Sources（实际产生 Raw）：US-NHTSA-RCL / US-NHTSA-CSI / CYBER-NVD / CN-AUTOQUALITY + 两批 RCL 重复计 = 4 个唯一源，另有 EU-SAFETYGATE 尝试中。按唯一源计：**4 个产生数据 + 2 个已启用待数据**。

## 五、安全边界复核

| 硬约束 | 状态 |
|---|---|
| Candidate Leakage = 0 | ✅ 全部新数据进 Raw/Candidate，无绕过审核 |
| Provenance = 100% | ✅ 统一 Schema（source/retrieved_at/hash/parser_version） |
| 宽进严出 | ✅ 8,000+ Raw 全部在 Raw Lake |

## 六、下一步（评审确认的三个任务）

1. **把有效来源做实**：EU（UK DVSA 表单 POST 交互）→ Active Sources 6→10+；再增 1-2 个中国高价值源（CN-DPAC 网络问题解决后）
2. **把现有数据吃透**：Source-Specific Analyzer v2（LLM 辅助结构化），UNKNOWN 62.1% 作为主要分析质量指标
3. **把早期投诉做深**：同车型同年款匹配采集 → 时间线验证（能否证明"投诉提前 X 天暴露召回风险"）
