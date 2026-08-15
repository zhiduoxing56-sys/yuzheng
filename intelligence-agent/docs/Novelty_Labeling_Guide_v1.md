# Novelty Labeling Guide v1 —— 新颖性标注规范

版本：v1.0 | 日期：2026-08-15
适用范围：Incident Cluster 的新颖性人工标注（F 阶段双人标注 + Frozen Test 标注）
原则：**以风险模式为基本单元判定，不依品牌/车系/单次事件判定**

## 一、风险模式基本单元

每条事故的标注对象是**风险模式**，由五个维度构成：

```
RiskPattern = (Component, FailureMode, OperatingCondition, Consequence, EvidenceNeed)
```

| 维度 | 定义 | 示例 |
|---|---|---|
| Component | 失效部件（家族+子项） | EXTERIOR LIGHTING:HEADLIGHTS |
| FailureMode | 失效模式（枚举） | INTERMITTENT_FAILURE / LOSS_OF_FUNCTION |
| OperatingCondition | 运行条件 | NIGHT / HIGH_SPEED / CHARGING |
| Consequence | 后果（枚举） | REDUCED_VISIBILITY / LOSS_OF_CONTROL |
| EvidenceNeed | 安全裁决需要的证据 | LIGHTING_STATE / VEHICLE_SPEED |

判定时**五个维度全部**用于对比"知识库是否已覆盖该风险模式"。

## 二、四分类定义（粒度：风险模式级）

### KNOWN（已知风险）
知识库**已完整覆盖**该风险模式，且覆盖**不止意图/域级**，而是具体到 Component+FailureMode 级别。

判定标准（全部满足）：
1. Component 家族在知识库有对应意图节点（如 HEADLIGHTS→HEADLIGHT_SET_MODE）
2. 该失效模式在知识库节点的约束语义中被覆盖（如"前照灯失效→灯光状态核查"）
3. 需要的 Evidence 在知识库节点 required_evidence 中可找到
4. 无新增维度（没有新的 Component/FailureMode/Consequence）

示例：`SERVICE BRAKES HYDRAULIC 制动液泄漏→制动力下降`（知识库液压制动节点覆盖）→ **KNOWN**
反例：`SERVICE BRAKES 电子助力器漏油至ECU`（助力器失效模式知识库未覆盖）→ **PARTIAL_NOVEL**，不是 KNOWN

### PARTIAL_NOVEL（部分新颖）
知识库覆盖该风险的**部分维度**，但有至少一个维度是新增的：
- Component 家族已知，但具体子项/部件失效模式新（最常见）
- 或失效模式已知，但运行条件/后果组合新
- 或映射到现有意图，但 EvidenceNeed 有新增类型

判定要点：**家族级覆盖 ≠ 风险模式级覆盖**。
示例：
- 电子刹车助力漏油（助力器部件新）
- 前照灯间歇失效（间歇失效模式新——知识库有"前照灯功能调整"但无间歇失效语义）
- 天窗玻璃脱落（天窗部件新）

### NOVEL（全新风险）
知识库**无任何维度覆盖**：
- Component 家族不在知识库意图映射中（如 拖车制动控制器/BCM/高压电池）
- 或虽有域级覆盖，但该具体安全概念知识库不存在（如"转向助力突然丢失"——转向域有节点但"助力失效"概念无）

判定要点：**宁缺毋滥**——只有真正找不到对应安全概念才标 NOVEL。
示例：拖车制动控制器、BCM OTA 软件错误、高压电池热失控、EPS 助力突然丢失

### IRRELEVANT（范围外）
事故与该系统的**语音车控安全裁决链无关**：
- Component 属于非语音车控范畴（气囊/安全带/燃油/座椅/标签/发动机机械/传动轴/车桥）
- 无论后果多严重（气囊召回很严重但仍与语音车控无关）

判定要点：**严重性不影响 IRRELEVANT 判定**——气囊致死事故仍是 IRRELEVANT。
示例：乘员分类传感器（气囊）、安全带卷收器、燃油泵、认证标签

## 三、判定决策树

```
1. Component 属于非语音车控清单（气囊/安全带/燃油/座椅/标签/传动/车桥/轮胎/悬架/发动机机械）？
   ├─ YES → IRRELEVANT
   └─ NO ↓
2. 风险模式在知识库有明确对应概念（Component+FailureMode+Evidence 全部匹配）？
   ├─ YES → KNOWN
   └─ NO ↓
3. 至少一个维度被知识库覆盖（家族/意图/证据部分匹配）？
   ├─ YES → PARTIAL_NOVEL
   └─ NO → NOVEL
```

## 四、常见误判案例（校准共识）

| 案例 | 误判 | 正确 | 理由 |
|---|---|---|---|
| 安全带织带撕裂 | NOVEL（严重） | IRRELEVANT | 非语音车控 |
| 液压制动球阀失效 | KNOWN（制动） | PARTIAL_NOVEL | 球阀失效模式新 |
| 倒车防碰撞软件 | NOVEL（软件） | KNOWN 或 PARTIAL | AUTO_PARK_ENABLE 覆盖，软件缺陷模式部分新 |
| 转向助力突然丢失 | PARTIAL（转向域） | NOVEL | 助力失效概念知识库不存在 |
| 雨刮电机失效 | NOVEL | KNOWN 或 PARTIAL | WIPER_SET_MODE 覆盖（电机部件细节） |

## 五、标注要求

1. 每条约 5-10 分钟；先读完整原文（RawSnapshot），再读最相似 Trusted 节点（如有）
2. 标注时不得查看对方标注
3. 争议案例（两人不一致）标注理由后进入仲裁表
4. 目标分布参考：KNOWN 15-25% / PARTIAL 25-35% / NOVEL 15-25% / IRRELEVANT 25-35%
