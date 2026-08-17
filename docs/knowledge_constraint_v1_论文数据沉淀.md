# knowledge-constraint-v1 论文数据沉淀

- 日期：2026-08-16 | 状态：v1 技术闭环完成，本文件为论文/复现数据

## 1. 三层能力对比（论文核心表）

| 阶段 | 知识库能力 | 运行时行为 |
|---|---|---|
| 原始知识库（v10 前） | 只提供证据需求（required_evidence） | 不参与裁决，阈值由 SafetyGate 硬编码 |
| **v1 知识约束** | 提供可执行条件（command/evidence/when/effect） | 阈值/谓词来自知识节点（5m→6m 行为同步变化） |
| **v1 + SafetyGate 增强** | 知识定义基础约束 | 处理缺失/冲突/枚举/off_intent_ids/中文归一化（更严格） |

## 2. 148 条知识分类统计

| 分类 | 数量 | 占比 |
|---|---|---|
| 已转换约束 | 5 | 3.4% |
| 装备/技术状态 | 43 | 29.1% |
| 有动作语义但无合法阈值 | 17 | 11.5% |
| 缺字段或合同不可表达 | 4 | 2.7% |
| 非 FORMAL（B 类） | 79 | 53.4% |
| **合计** | **148** | 100% |

- **可执行转换率**：5/69 A 类 = 7.2%（严格阈值来源约束下的真实比例）
- 可执行约束分布：BLOCK 4 + REVIEW 1

## 3. 评测结果统计

### 知识约束评测（34 条）
- 基础验收 15 条：5 BLOCK + 5 ALLOW + 5 NOT_APPLICABLE（对应节点闭合）
- 扩充评测 19 条：7 边界 + 3 缺失 + 2 类型 + 2 冲突 + 2 多节点 + 3 正常（19/19 PASS）
- 边界值验证：20lux/19.9lux、5m/4.99m、1.5m 临界两侧全部正确

### SafetyGate 增强（15 条，真实 evaluator）
- 枚举 LOW/DARK/NIGHT（3）、fail-closed speed 缺失/非数值（2）、off_intent_ids（2）、
  DOOR_SET_POSITION（2）、非数值防护（2）、REAR 冲突+缺失（2）、浓雾归一化（2）
- **15/15 PASS**

### 差分测试（49 条）
- **42 CONSISTENT + 7 SAFETYGATE_STRICTER + 0 FAILED + 0 NOT_EXECUTABLE**
- 一致率 85.7%；SafetyGate 更严格 14.3%（枚举/意图覆盖/归一化增强）
- **KNOWLEDGE_STRICTER = 0**（知识约束未削弱现有安全能力）

### 参数修改→行为变化（6 条）
| 规则 | 参数修改 | 边界行为 |
|---|---|---|
| 夜间关灯 | 20→25lux | 22lux 从不命中→命中 |
| 行驶开门 | speed GT 0 知识谓词 | 30 命中 / 0 不命中 |
| 近距加速 | 5→6m | 5.5m 从不命中→命中 |
| 制动后方 | 1.5→2.0m | 1.8m 从不命中→命中 |
| 浓雾除雾 | 枚举去 FOG | FOG 从命中→不命中 |
| 正式模式 | 缺 overlay | 启动失败 |

### 全链路 E2E（1 条）
启动预检 → 指令(关闭前照灯) → 证据绑定(speed=60, lux=5) → SafetyGate 正式模式 →
**BLOCK** → knowledge_trace（节点/证据值/谓词/runtime_parameter_source/basis_reference/gate_reason）

## 4. 关键论文结论（可直接引用）

1. **知识库从"证据需求"到"可执行约束"**：节点规定指令对象+动作+上下文条件+证据字段+具体值+裁决效果
2. **运行时以知识为唯一参数来源**：修改知识阈值 → SafetyGate 边界行为同步变化（5m→6m 实证）
3. **知识约束不削弱安全**：差分 85.7% 一致 + 14.3% SafetyGate 更严，KNOWLEDGE_STRICTER=0
4. **正式模式防绕过**：constraint_required 启动预检，缺 overlay/节点/参数 → 启动失败（非运行时回退）
5. **可追溯裁决**：knowledge_trace 区分 runtime_parameter_source（知识节点）与 basis_reference（冻结依据）
6. **严格转换率 7.2%**：69 条 A 类仅 5 条有合法阈值来源——不猜值原则的量化体现

## 5. 复现数据清单

| 数据 | 路径 |
|---|---|
| 5 条约束 | knowledge-contract-v1/acceptance/knowledge_constraints_v1.jsonl |
| 34 条评测 | knowledge_constraint_acceptance + eval_extended |
| 15 条增强 | safety_gate_enhancement_cases_v1.jsonl |
| 49 条差分 | constraint_diff_matrix_v1.json |
| E2E | scripts/kc_r5_e2e.py |
| 版本报告 | docs/knowledge_constraint_v1_regression_report.json |
| 冻结声明 | docs/knowledge_constraint_v1_冻结声明.md |
| 148 分类 | data/a_class_final_partition.json |
