# 语证最终语义编排 V2 设计说明

## 背景与目标

Stage1 v1.3 的 1466 条锚点及三路召回已经冻结。本实验只在现有单句混合门控链之外增加确定性编排层，解决多意图绑定、动作反向、信息不足自动接受及安全声明漏检/误报。目标是降低错误 `OK`，不追求以规则替代候选召回或3B选择。

## 冻结边界

- 锚点：`挂靠/intent_anchor_set_v1_3.yaml`，SHA256 `B88B4D9DCC9CDFDB27EC6D25038AF6E7E5D3F01FE6937BA4777815987FB65BFF`。
- 门控配置 SHA256：`F46C2DADE8CA23F585BC14D8DCD09F65FCC8EBA494D5EBCF9D799C1ADF8F5155`。
- 3B配置 SHA256：`FC1C6BD7DCAC10A358790B38DF277480215536CEAAE84866225FB4ADCE8A0CAC`。
- 不修改 Stage1、BGE、literal、pinyin、RRF、3B模型/提示词、门控阈值或正式后端。

## 方案对比

### 方案一：整句结果后处理

- 优点：改动少。
- 缺点：无法可靠解决多子句动作和对象绑定，也无法判断静默漏意图。

### 方案二：重新提示或扩大3B任务

- 优点：实现表面简单。
- 缺点：违反冻结提示词与“3B只做候选选择”的边界，延迟与不确定性增加。

### 方案三：冻结单句链外加确定性编排（采用）

- 优点：每个子句仍通过冻结 Stage1 和冻结3B；新增层只能降级、拆句、审计和补充正交安全声明，不能创造正式意图。
- 缺点：连接结构和动作方向需要轻量词法规则，必须限制为通用类别而非测试句特判。

## 详细设计

### 架构

`SemanticOrchestratorV2` 包装现有 `HybridConfidenceGate`。运行时只把门控内部第一阶段召回器替换为冻结 v1.3 实例，随后：

1. `OrderedClauseResolver` 从明确并列/顺序结构中产生有序控制子句。
2. 每个子句独立调用原 `HybridConfidenceGate.run()`。
3. `EllipsisGuard`、`ActionDirectionGuard`、`CandidateConsistencyGuard` 检查每个子句结果。
4. `MultiIntentCompletenessGuard` 只在全部子句可靠且数量/顺序完整时允许整体 `OK`。
5. `SecurityClaimGuard` 对整句识别权限、验证绕过、安全限制和特殊环境声明，与车控意图正交。

### OrderedClauseResolver

优先识别 `并且/同时/然后/接着/以及/并/再`、`先…再…`、`…后再/后重新…`。`和`仅在两侧都含潜在车控动作且含明确对象或独立完整车辆动作时拆分。对于无连接词但存在两个各自带对象的明确动作片段，允许通用隐式边界拆分。否定的动作词不作为新子句起点。

### 动作方向

从 `intent_cards_v1.yaml` 读取规范动作。词法方向只映射到动作族：正向开启、负向关闭、锁/解锁、折叠/展开、施加/释放、加速/减速。带 `不要/别/不准` 的动作视为被否定，不与主请求方向冲突。若所选意图与原文明确方向相反，只能 `REVIEW/ACTION_DIRECTION_CONFLICT`；候选来自该子句 Stage1 Top8。

### 信息不足与候选一致性

仅有通用动作、未知代词或无对象比较词时触发 `INSUFFICIENT_SEMANTIC_INFORMATION`。`刹车/制动/加速/减速/鸣笛`以及包含门、窗等明确目标的短指令不受影响。候选一致性只复用已有 Top8、融合Top1、通道排名与现有门控强通道配置，不增加浮点阈值。

### 多意图完整性

拆为 N 个有效控制子句后，每个子句必须得到恰好一个可靠 `OK`，且通过方向和候选一致性检查。任一子句 `REVIEW/NO_MATCH`、结果缺失或数量不一致，整体降为 `REVIEW/MULTI_INTENT_INCOMPLETE`。可靠部分写入 `resolved_sub_intents`，未完成部分写入 `unresolved_clauses`；正式 `sub_intents` 为空。

### 安全声明

确定性识别权限伪造、跳过验证、安全限制绕过和调试/测试/模拟环境声明。明确命中时强制最终 `安全注入`；Stage1单独命中而声明规则未命中时记录 `SECURITY_SIGNAL_WEAK`，不把该弱信号提交为最终安全信号。普通否定车控和残缺动作不匹配安全声明。

### 输出与评估

输出 `status`、正式 `sub_intents`、`reason/reasons`、`review_candidates`、`resolved_sub_intents`、`unresolved_clauses`、`security_signals`、建议文本及逐子句调试证据。使用冻结的60条、39条外测共99条唯一输入，四个演示额外重跑但不进入99分母。首次全量运行后只报告，不根据结果继续改规则。

## 验证策略

- 静态核验所有冻结文件 SHA256。
- 组件级验证通用拆句、否定方向、信息不足与安全声明族。
- 实际运行99+4次完整链，检查无Ollama/Schema失败。
- 统计全部指定指标及六类Guard触发次数。

## 风险

- 规则只能覆盖明显连接和动作方向，隐含语义仍可能进入复核。
- 安全声明弱信号会被降为审计标记，最终安全链将来需决定如何消费；本实验不接正式系统。
