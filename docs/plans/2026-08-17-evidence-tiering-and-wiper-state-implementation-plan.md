# 证据分级与雨刮状态闭环实施计划

## 实施原则

- 先建立数据契约，再修改裁决行为，最后接入雨刮状态与前端解释。
- 每个阶段均保持可测试、可审计；不得以雨刮特例绕过通用裁决链。
- 硬前置证据的现有安全强度不得下降。
- 本计划不实现真实雨刮执行器。

## 阶段一：冻结当前缺陷与目标行为

### 修改位置

- `backend/tests/integration/test_knowledge_augmented_demand.py`
- `backend/tests/integration/test_trusted_knowledge_online_main_chain.py`
- 新增雨刮裁决回归测试文件

### 工作项

1. 增加当前缺陷复现：雨天、`WIPER_SET_MODE / RAIN_SENSOR`、缺少 `WIPER_STATE` 时，记录旧行为为错误的 `BLOCK`。
2. 将目标断言写为 `REVIEW`，并断言：
   - `MANDATORY_EVIDENCE_AVAILABLE` 不得命中；
   - 原因是 `KNOWLEDGE_EVIDENCE_MISSING`；
   - 安全评分原值被保留。
3. 增加硬门保护测试：`DOOR_OPEN` 缺少 `VEHICLE_SPEED` 仍为 `BLOCK`。

### 验收

- 新雨刮目标测试在修改前失败。
- 硬门保护测试在修改前后均通过。

## 阶段二：扩展证据需求契约

### 修改位置

- `backend/app/models/schemas.py`
- `backend/app/services/evidence/demand.py`
- `backend/app/services/evidence/demand_registry.py`
- `frontend/src/types/contract.ts`
- 对应契约冻结测试

### 工作项

1. 为 `IntentEvidenceDemand` 增加：
   - `assessment_types`；
   - `knowledge_required_types`；
   - 分级来源元数据。
2. 保留 `required_types` 作为硬前置的唯一权威字段。
3. 暂时令 `optional_types` 镜像 `assessment_types`，保证旧前端与旧审计兼容。
4. 建立统一等级去重函数，优先级固定为：
   `HARD_REQUIRED > KNOWLEDGE_REQUIRED > ASSESSMENT`。
5. 更新模型序列化、前端类型和契约快照。

### 验收

- Registry 的 `mandatory` 只进入 `required_types`。
- Registry 的 `recommended` 进入 `assessment_types`。
- 同一证据不会在多个等级被重复计算。
- 旧审计记录可正常反序列化。

## 阶段三：修正知识增强边界

### 修改位置

- `backend/app/services/index/trusted_knowledge.py`
- `backend/tests/integration/test_knowledge_augmented_demand.py`
- `backend/tests/unit/test_trusted_knowledge.py`

### 工作项

1. 停止把知识节点 `required_evidence` 追加进 `required_types`。
2. 将其追加到 `knowledge_required_types`。
3. 将知识节点 `optional_evidence` 追加到 `assessment_types`。
4. 保留节点 ID、相似度、需求等级和证据类型之间的来源映射。
5. 增加防升级测试：任何知识节点都不能隐式创建硬前置证据。

### 验收

- `WIPER_STATE`、`ENVIRONMENT_CONDITIONS` 的知识需求可见，但不进入硬门输入。
- 原有知识命中和检索诊断信息不丢失。

## 阶段四：拆分召回、解析与缺失路由

### 修改位置

- `backend/app/services/evidence/recall.py`
- `backend/app/services/evidence/resolution.py`
- `backend/app/core/pipeline.py`
- 证据召回与解析测试

### 工作项

1. 三个等级都参与召回，但分别记录覆盖、缺失、无效、陈旧与冲突结果。
2. `mandatory_recall_records` 仅保留硬前置召回；新增知识需求召回审计集合。
3. 质量指标读取评估层和已解析的知识层，但避免同一节点重复计分。
4. 在管线中生成明确的知识证据缺失投影，供证据对齐和审计使用。

### 验收

- 缺失集合能区分 `missing_required_types` 与 `missing_knowledge_required_types`。
- 知识证据缺失不再设置 `mandatory_evidence_missing=true`。

## 阶段五：调整安全门和裁决合并

### 修改位置

- `backend/app/services/decision/safety_gate.py`
- `backend/app/services/decision/merge.py`
- `backend/app/services/decision/engine.py`
- `config/safety_rules.yaml`
- 安全门、合并与场景测试

### 工作项

1. 强制证据可用性、完整性、新鲜度和可信度规则只读取 `required_types`。
2. 知识必需证据缺失生成 `EVIDENCE_REVIEW` 和原因码 `KNOWLEDGE_EVIDENCE_MISSING`。
3. 合并规则固定为：
   - 独立硬门或评分 `BLOCK`：最终 `BLOCK`；
   - 否则知识证据缺失：最终至少 `REVIEW`；
   - 否则采用评分结果。
4. 补齐中文解释和 review question，列出缺失证据及来源知识节点。

### 验收

- 雨刮缺状态：安全门未阻断、证据对齐为 `EVIDENCE_REVIEW`、最终为 `REVIEW`。
- 开门缺车速：安全门阻断、最终为 `BLOCK`。
- 评分本身为 `BLOCK` 时，知识层不得降级为 `REVIEW`。

## 阶段六：补齐雨刮状态模型与证据提供者

### 修改位置

- `backend/app/models/schemas.py`
- `backend/app/services/vehicle/simulator.py`
- `backend/app/services/vehicle/carla.py`
- `backend/app/services/evidence/repository.py`
- `证据/evidence_runtime_mapping_v1.yaml`
- 车辆状态和证据仓库测试

### 工作项

1. 在 `VehicleState`、`VehicleStatePatch` 增加雨刮模式、强度、频率、运动和故障字段及枚举校验。
2. Simulator 持久化这些字段，并在手动更新时刷新状态版本。
3. CARLA 没有可靠原生接口时保存为影子状态，provider 明确标记为 `carla_shadow_state`。
4. `EvidenceRepository.ingest_vehicle_state()` 生成结构符合目录约束的 `WIPER_STATE`。
5. 更新 runtime mapping，区分 Simulator/CARLA shadow 与未来真实 Vehicle Bus，不得继续整体标记为无条件 `UNAVAILABLE`。

### 验收

- 有任一非空可用雨刮字段时生成有效 `WIPER_STATE`。
- 无可用字段时仍生成可追踪的缺失节点，不伪造默认事实。
- provider 和 source metadata 能证明证据来自场景、模拟器或影子状态。

## 阶段七：更新场景和全局上下文一致性

### 修改位置

- `config/demo_scenarios.yaml`
- `backend/app/core/pipeline.py` 的场景字段到证据类型映射
- `backend/app/services/vehicle/scenario_summary.py`
- 场景持久化测试

### 工作项

1. 晴天和雨天雨刮场景加入完整 `WIPER_STATE` 覆盖。
2. 场景加载时同步物理雨刮字段与激活场景证据。
3. 手动修改雨刮字段时，仅使对应 `WIPER_STATE` 场景覆盖失效。
4. CARLA 页面往返、裁决页面提交和无关指令不得清空雨刮上下文。
5. 当前激活场景摘要增加雨刮模式与状态来源。

### 验收

- 雨天场景选择后，在裁决页输入“开启自动雨刮”，审计使用同一场景版本和雨刮状态。
- 页面往返后结果一致。

## 阶段八：前端解释与审计展示

### 修改位置

- `frontend/src/components/DecisionResultPanel.tsx`
- `frontend/src/components/EvidenceDemandPanel.tsx`
- `frontend/src/components/DecisionVisuals.tsx`
- `frontend/src/utils/decisionExplanation.ts`
- 相应前端测试

### 工作项

1. 分开展示硬前置、评估佐证和知识检索证据。
2. 知识证据缺失显示“需要复核”，不显示“硬性安全门已阻断”。
3. 具体原因显示缺失类型、命中知识和对最终裁决的影响。
4. 安全允许但执行器未接入时，单独显示运行能力状态，避免与安全拒绝混淆。

### 验收

- 不再出现“硬门阻断、评分允许、具体原因空白”的组合。
- 截图对应案例显示：硬门未阻断、证据对齐需要复核、评分允许、最终需要复核。

## 阶段九：全量验证与交付

### 验证命令

所有 Python 命令使用项目指定解释器：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest backend\tests\unit backend\tests\integration backend\tests\scenarios -v
```

前端执行类型检查、单测和构建；同时执行 Python 编译检查与 `git diff --check`。

### 最终验收矩阵

| 场景 | 缺失类型 | 预期结果 |
| --- | --- | --- |
| 开门且缺车速 | 硬前置 | `BLOCK` |
| 自动雨刮且缺 `WIPER_STATE` | 知识必需 | `REVIEW` |
| 自动雨刮且雨天状态完整 | 无 | 不因证据缺失而拒绝 |
| 评估佐证缺失 | 评估层 | 由评分决定 |
| 任意独立禁止规则命中 | 非证据硬门 | `BLOCK` |
| 评分直接判定高风险 | 评分层 | `BLOCK` |

### 交付要求

- 提供变更文件清单与兼容性说明。
- 提供上述验收矩阵的实际测试结果。
- 明确说明真实雨刮执行器仍未接入，不把“安全允许”描述成“已执行”。
