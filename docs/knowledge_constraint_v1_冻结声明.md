# knowledge-constraint-v1 冻结声明

- 日期：2026-08-16
- 状态：**正式冻结**（全量回归通过）

## 1. 冻结内容

知识约束文件（正式运行时基础约束来源）：

```text
knowledge_constraints_v1.jsonl  5 条可执行约束节点
```

| 节点 | intent | 谓词 | 效果 |
|---|---|---|---|
| 知识.灯光.夜间关闭限制.001 | HEADLIGHT_SET_MODE | speed GT 0 ∧ light LT 20 | BLOCK |
| 知识.车门.行驶开门限制.001 | DOOR_OPEN | speed GT 0 | BLOCK |
| 知识.加速.近距障碍加速限制.001 | ACCELERATE | front_dist LT 5 | BLOCK |
| 知识.制动.后方冲突复核.001 | BRAKE | rear_dist LT 1.5 | REVIEW |
| 知识.除雾.浓雾关闭限制.001 | DEFROST_OFF | weather IN [DENSE_FOG,HEAVY_FOG,FOG] | BLOCK |

## 2. 运行时接入（已冻结行为）

1. **正式模式**：`constraint_required=True`——SafetyGate 启动预检 5 节点+参数，缺 overlay/节点/参数 → 启动失败
2. **参数来源**：运行时以知识 overlay 为唯一参数来源（20lux/5m/1.5m/浓雾枚举 + speed GT 0 谓词）
3. **冻结文件未修改**：safety_rules.yaml 恢复原值（20/5/1.5/浓雾集合），仅作历史兼容与一致性校验，不再作为运行时参数来源
4. **安全增强保留**：枚举(LOW/DARK/NIGHT)、fail-closed、冲突处理、off_intent_ids、DOOR_SET_POSITION、DECELERATE、中文浓雾归一化
5. **裁决溯源**：SafetyGateResult.knowledge_trace 记录命中节点/证据值/谓词/阈值来源/gate_reason

## 3. 全量回归记录（冻结依据）

**口径说明**：本表为"知识约束专项回归"（89 条专项测试）；项目既有测试套件（test_decision_merge/test_interpreter_and_review 等引用 SafetyGateResult）本次改动仅新增可选字段，序列化兼容已验证；完整项目测试建议在 CI 单独执行（含模型加载，本地超时）。

| 套件 | 数量 | 结果 |
|---|---|---|
| loader 单测 | 14 | 14/14 PASS |
| 正式模式启动预检 | 3 | 3/3 PASS（含缺 overlay/缺节点拒绝） |
| SafetyGate 增强用例 | 15 | 15/15 PASS |
| 知识—SafetyGate 差分 | 49 | 42 CONSISTENT + 7 STRICTER，0 FAILED |
| 参数修改→行为变化 | 6 | 6/6 PASS（5 条规则逐条） |
| 真实全链路 E2E | 1 | PASS（启动→指令→证据→BLOCK→trace） |
| 接口兼容（SafetyGateResult 序列化） | 1 | PASS |
| **专项合计** | **89** | **89/89 PASS** |

### 运行时代码版本（sha256 前16位）

| 文件 | 哈希 |
|---|---|
| constraint_parameter_loader.py | 见 docs/knowledge_constraint_v1_regression_report.json |
| constraint_adapter.py | 同上 |
| safety_gate.py | 同上 |
| schemas.py (SafetyGateResult) | 同上 |
| knowledge_constraints_v1.jsonl | 同上 |
| knowledge_constraint_contract_v1.yaml | 同上 |
| safety_rules.yaml | 同上 |

完整报告：`docs/knowledge_constraint_v1_regression_report.json`

## 4. 冻结输入校验

- 合同：knowledge_constraint_contract_v1.yaml（335 行，SHA256=3DFF279543199F64BB09C674D1F646B0F7B1E74DB0BDF51937CC7B40D52845D2）✓
- safety_rules.yaml：已恢复冻结原值 ✓（备份文件已从 freezes 移除）
- MANIFEST.json：21 文件全量哈希 ✓

## 5. 冻结后职责边界

| 层 | 职责 |
|---|---|
| 知识库 | 提供有依据的基础条件/阈值/操作符/效果（5 条约束） |
| SafetyGate | 证据质量、缺失、冲突、更保守运行时策略（增强保留） |
| 证据链 | 证据检索与绑定（resolution.bindings） |

## 6. 未纳入 v1（后续立项）

148 条完整闭合：

```text
5   已转换约束（本 v1）
43  装备/技术状态（保留原知识平面，不参与车控裁决）
17  有动作语义但无合法阈值（待合法阈值来源）
4   缺字段或当前合同不可表达（坡度/会车 → 需升级 DSL 合同）
79  非 FORMAL 的 B 类知识（保留原知识平面）
--- 合计 148
```

43 条装备/技术状态知识不是丢弃，而是保留在原知识平面（NORMATIVE），仅不参与车控指令裁决。
