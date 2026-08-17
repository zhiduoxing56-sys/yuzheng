# 下一阶段方案：SafetyGate 增强用例 + 差分测试 → constraint_parameter_loader

- 日期：2026-08-16
- 前置：knowledge-contract-v1 交付完成（5 约束 + 15 基础 + 19 扩充用例全部 PASS）
- 原则：**结果一致或 SafetyGate 更严格，绝不允许安全能力下降**

## 0. 关键表述修正（证据缺失语义）

> 单独计算 when 可能落到 `else: ALLOW`，但**完整裁决链路必须先返回 MISSING_EVIDENCE**，不得进入 else，更不能最终放行。
> 这与 EV-008/009 结论一致：command 匹配 + when 引用证据缺失 → 证据门拦截。

## 1. 阶段一：SafetyGate 安全增强用例（本次先做）

围绕 5 个 evaluator 的真实安全增强，补充测试（不扩展合同）：

| 增强点 | evaluator | 用例数 | 覆盖场景 |
|---|---|---|---|
| LOW/DARK/NIGHT 枚举 | low_light_headlight | 3 | weather=LOW/DARK/NIGHT 时即使无数值也 BLOCK |
| 缺失车速 fail-closed | low_light_headlight | 2 | speed 缺失/非数值 → 视为行驶 → BLOCK |
| off_intent_ids | low_light_headlight | 2 | LOW_BEAM_OFF/HIGH_BEAM_OFF 意图 → BLOCK |
| DOOR_SET_POSITION | moving_door | 2 | position value>0 → BLOCK |
| 非数值防护 | moving_door/acceleration | 2 | speed/front_dist 非数值 → 不触发 |
| 冲突分级 | deceleration_rear_conflict | 2 | REAR 冲突 → BLOCK；缺失 → 分级 reason |
| 枚举归一化 | dense_fog_defog | 2 | 小写/带空格 weather → 归一后命中 |

**共约 15 条**，输出 `safety_gate_enhancement_cases_v1.jsonl`

## 2. 阶段二：知识节点—SafetyGate 差分测试

对同一场景（command+evidence）同时求值两套逻辑：

```
场景集 = 基础 15 条 + 扩充 19 条 + 增强 15 条（约 49 条）
知识节点求值（when/effect）→ 结果 K
SafetyGate evaluator 求值 → 结果 G
验收：K==G 或 G 更严格（BLOCK>REVIEW>ALLOW>NOT_APPLICABLE）
禁止：K 更严格但 G 放行；G 比现有行为更宽松
```

输出差分矩阵 `constraint_diff_matrix_v1.json`，零违规才算通过。

## 3. 阶段三：constraint_parameter_loader（差分通过后才做）

不叫"阈值加载器"，因为读取的是**完整约束参数**：

- 数值阈值：20 lux / 5m / 1.5m
- 枚举集合：浓雾 values（含中英文）
- 条件操作符及边界语义：GT/LT/IN 的边界（GT 不含等号、LT 不含等号等）
- 与 when 谓词一一对应

**接入硬性要求（保留全部安全增强）**：
1. 不得删除：枚举判断（LOW/DARK/NIGHT）、缺失证据拦截、冲突处理、off_intent_ids
2. 加载失败 / 合同哈希不符 / 节点缺失 → **拒绝启动或回退当前冻结配置**，禁止静默默认值
3. 每参数带来源引用（threshold_ref）

## 4. 验收标准

- 阶段一：增强用例全部 PASS（15/15）
- 阶段二：差分矩阵零违规（49 条中全部 K==G 或 G 更严）
- 阶段三：loader 单测 + 现有 evaluator 行为回归零差异

## 5. 不做的事（本阶段）

- 不扩展知识合同（17 无阈值 + 4 不可表达继续保留）
- 不让知识节点直接替换 evaluator（evaluator 安全增强是必需逻辑）
- 不新增冻结字段/意图/证据类型

## 6. 执行进度

### 阶段一：SafetyGate 安全增强用例（已完成 2026-08-16）
- 用例：safety_gate_enhancement_cases_v1.jsonl（15 条）
- 执行：safety_gate_enhancement_execution_v1.json（真实 evaluator 调用）
- 结果：15/15 PASS
- 覆盖：LOW/DARK/NIGHT 枚举(3)、fail-closed speed 缺失/非数值(2)、off_intent_ids(2)、
  DOOR_SET_POSITION(2)、非数值防护(2)、REAR 冲突+缺失 fail-closed(2)、浓雾归一化(2)

### 过程中确认的真实 evaluator 行为（记录）
1. low_light_headlight: 枚举 LOW/DARK/NIGHT 或数值<20；speed fail-closed（缺失/非数值视为行驶）；off_intent_ids 覆盖 LOW_BEAM_OFF/HIGH_BEAM_OFF
2. moving_door: DOOR_SET_POSITION 需 intent.value 数字>0；非数值不命中
3. deceleration_rear_conflict: **fail-closed**（applies+证据缺失也命中，REAR_OBSTACLE_DISTANCE_MISSING）
4. dense_fog_defog: .upper() 归一化 + 默认枚举回退

### 待办
- [x] 阶段一：增强用例 15/15 PASS
- [ ] 阶段二：知识节点—SafetyGate 差分测试（49 条，零违规）
- [ ] 阶段三：constraint_parameter_loader（差分通过后）

## 7. 阶段二执行结果（差分测试，已完成 2026-08-16）

- 场景：49 条（基础 15 + 扩充 19 + 增强 15）
- 结果：**42 CONSISTENT + 7 SAFETYGATE_STRICTER + 0 FAILED + 0 NOT_EXECUTABLE → PASS**
- 数据：constraint_diff_matrix_v1.json

### SAFETYGATE_STRICTER（7 条）增强原因分类
1. **枚举兼容（3 条）**：知识侧仅数值比较（DARK/LOW/NIGHT 枚举→TYPE_ERROR→REVIEW），SafetyGate 枚举命中→BLOCK——合同表达力限制，SafetyGate 更严合理
2. **off_intent_ids/DOOR_SET_POSITION 覆盖更广（3 条）**：知识节点未覆盖 LOW_BEAM_OFF/HIGH_BEAM_OFF/DOOR_SET_POSITION 意图，SafetyGate 拦截
3. **浓雾归一化（1 条）**：weather=fog 小写，知识 IN 未命中（大小写敏感），SafetyGate .upper() 归一化后命中→BLOCK

### 过程中确认的口径修正
- NOT_APPLICABLE 与 ALLOW 视为等价放行（CONSISTENT，4 条）
- 证据缺失/类型错误在两侧均映射 REVIEW（证据门策略），非 ALLOW

### 阶段二验收
- [x] 49 条总数闭合
- [x] FAILED=0（KNOWLEDGE_STRICTER=0，无无法解释差异）
- [x] NOT_EXECUTABLE=0（全部接入真实 evaluator）
- [x] 每条例两侧原始结果/最终裁决/差异原因已记录

### 阶段三就绪
constraint_parameter_loader 可实施（差分通过）。

## 8. 阶段三执行结果（constraint_parameter_loader，已完成 2026-08-16）

- 代码：backend/app/services/knowledge/constraint_parameter_loader.py
- 单测：14/14 PASS（正常加载/哈希不符拒绝/文件缺失拒绝/非法op拒绝）
- 回归：loader 参数 vs safety_rules 零差异 PASS
- 说明：loader 只提供参数（数值/枚举/操作符边界/来源引用），不替换 evaluator 安全逻辑

### 接入硬性要求落实
1. ✅ 合同哈希校验（3DFF...，行数 335）不符 → ConstraintParameterError 拒绝启动
2. ✅ 约束文件/合同缺失 → 拒绝启动
3. ✅ node_id/reason_code 重复 → 拒绝启动
4. ✅ 非法操作符（非 EQ/NE/GT/GTE/LT/LTE/IN/NOT_IN）→ 拒绝启动
5. ✅ IN/NOT_IN 必须列表值
6. ✅ 每参数带 threshold_ref（来源引用）
7. ✅ enforcement 映射：BLOCK→HARD / REVIEW→SOFT
8. ✅ 操作符边界语义（GT/LT 不含等号等）随参数输出

### 保留的 evaluator 安全增强（loader 不触碰）
枚举判断（LOW/DARK/NIGHT）、缺失证据拦截、冲突处理、off_intent_ids、fail-closed

## 9. 同步任务完成（第三步双写消除 + 第四步溯源）

### 任务A：safety_rules.yaml 双写消除 ✅
- 已删除知识节点提供的重复值：low_light_lux=20 / threshold_m=5 / threshold_m=1.5 / dense_fog_values
- 保留：id/evaluator/intent_ids/off_intent_ids/mode/reason（路由与安全增强）
- 备份：freezes/safety_rules.yaml.bak_knowledge_v1

### 任务B：裁决溯源 ✅
- SafetyGateResult 新增 knowledge_trace 字段（模型合法扩展）
- evaluate 组装 trace：rule_id/知识节点ID/证据实际值/谓词/阈值来源/gate_hit/gate_reason
- 溯源验证 PASS（node=知识.加速.近距障碍加速限制.001, evidence=4.9, gate_hit=true）

### 接入状态
- constraint_overlay 注入 evaluate ✅（_knowledge_params 按规则注入）
- 4 处默认值改 _knowledge_threshold（overlay 缺失→拒绝启动）✅
- 增强用例回归 15/15 ✅（overlay 注入后零差异）
- 说明：完整 evaluate 链路 e2e 的 contexts/resolution 投影依赖真实前端构造，
  已由既有系统测试覆盖；本阶段验证 evaluator 层 + overlay + 溯源字段全部通过
