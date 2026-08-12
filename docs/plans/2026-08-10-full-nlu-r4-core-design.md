# Full NLU R4 核心合同修订设计说明

## 背景与目标

以 `data/nlu/spec/intent_registry_r3.yaml` 为只读父版本，只实施已人工批准的 P0-01～P0-07，生成可复现、可审计的 R4 核心草案、结构化差异和校验结果。R3、baseline_v2、训练数据、映射数据及模型均不得修改。

## 现状与约束

- R3 SHA256 为 `c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06`，与冻结清单一致。
- R3 包含 93 个语义 Intent、71 个正式用户语音 Intent、22 个 known-unsupported Intent。
- `scripts/validate_intent_registry.py` 固定面向 R2；`scripts/validate_sys014_r3_voice_registry.py` 强制 R3 与 R2 的语义定义完全相同，均不能直接校验 R4。
- 工作区存在大量与本任务无关的改动；本任务只新增或修改 R4 直接相关文件。

## 方案对比

### 方案一：确定性 R4 构建器与专用校验器

- 优点：从 R3 深复制后按白名单修改，复制完整性、差异范围和报告可复现；不影响冻结的 R3 验证链路。
- 缺点：新增少量脚本与测试。

### 方案二：手工复制 R4 YAML 后单独校验

- 优点：脚本数量较少。
- 缺点：难以证明没有字段遗漏，差异报告也不易稳定复现。

### 方案三：重构现有 R3 校验器兼容 R4

- 优点：减少部分重复校验代码。
- 缺点：扩大对冻结链路的影响，不符合本轮最小改动原则。

## 推荐方案

采用方案一。新增确定性构建器、R4 专用校验器和离线测试；生成 R4 YAML、Markdown/JSON 差异及 JSON 校验结果。P0-07 本轮不新增 `FRUNK_OPEN/CLOSE`，只完成 TRUNK/HOOD 隔离并在版本化标注指导中记录 FRUNK 的后续 known-unsupported 扩展状态。

## 详细设计

### 架构与关键组件

- R4 构建器读取并校验 R3 固定 SHA256，深复制全部顶层区块和 Intent。
- 构建器仅通过 P0 白名单变换元数据、合同、审核示例、版本化标注指导及指定 Intent 字段。
- R4 校验器同时读取 R3 与 R4，验证 YAML 类型、合同引用、槽位冲突、语义键唯一性、71 项正式 ID、93 项原始 ID、PROJECT_NATIVE 保留、R3 SHA256 及 P0 路径白名单。
- 离线测试调用构建与校验逻辑，覆盖七项合同断言和确定性输出。

### 数据流

`intent_registry_r3.yaml` → 深复制与七类白名单变换 → `intent_registry_r4_core_draft.yaml` → R4 校验器 → Markdown/JSON diff 与 validator JSON。

### P0 变换

- P0-01：新增 1～99 的部分开度合同并用于 `WINDOW_SET_POSITION`；冻结窗口端点路由及模糊幅度禁转规则。
- P0-02：新增可选相对速度增量合同，替换 `ACCELERATE`/`DECELERATE` 的 `SPEED_OPTIONAL` 引用。
- P0-03：将 `CRUISE_GAP_LEVEL` 展开为 `LEVEL_1`～`LEVEL_4`，保持 `VALUE_XOR_MODE`。
- P0-04：将审核示例中的布尔 `false` 改为字符串 `OFF`，增加 MODE 类型检查。
- P0-05：新增版本化 `annotation_guidance`，集中表达三类座椅词法锚点、默认优先级与歧义门槛。
- P0-06：主灯 MODE 使用 `OFF/ON/POSITION/DAYTIME_RUNNING_LIGHTS/AUTO`，同步映射合同、审核示例及受限别名规则。
- P0-07：五个 TRUNK Intent 的 `allowed_areas` 仅保留 `REAR`；标注指导区分 TRUNK、HOOD、FRUNK，并记录 FRUNK 开/关扩展待后续处理。

### 异常与边界处理

- R3 SHA256 不匹配时停止构建。
- 任何白名单外差异、合同缺失、布尔 MODE、ID 增删、PROJECT_NATIVE 丢失或正式 ID 数量变化均判定失败。
- 不读取或写入 baseline、训练集、映射数据，也不运行训练。

### 测试策略

- 严格 YAML 解析和输出确定性测试。
- P0-01～P0-07 逐项断言。
- 通用结构、不变量、R3 哈希和差异白名单断言。
- 最终重新计算 R3 SHA256，并输出完整校验结果。

## 风险与待确认项

- `writing-plans` 技能当前不可用，因此由任务内计划承接实施。
- R4 为草案状态，不创建冻结清单，不允许运行时加载。
