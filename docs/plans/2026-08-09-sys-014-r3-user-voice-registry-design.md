# SYS-014 R3 用户语音正式注册表设计说明

## 背景与目标

以 SHA256 为 `18c4e02edec1630946be6aa8613345a6e16dc246c883068c6f017f5e28e9f251` 的 R2 为唯一父版本，派生 `sys-014-semantic-hardening-r3`。R3 保留 R2 全部 93 条语义定义和 VSS 来源，并将用户语音范围显式分为 71 条“正式可执行”和 22 条“已知但不开放”。后端当前运行支持继续由 `intent_runtime_support.yaml` 独立维护。

## 现状与约束

- R2 是 reopened 状态，不能继续作为 Full NLU 构建权威。
- 旧 freeze manifest 指向更早的 `0127…2739`，不得复用。
- 历史 7-Intent PoC、数据、Safety Gold、checkpoint、阈值和训练脚本仅供复盘，不得成为 Full NLU 依赖或 fallback。
- 本阶段不读取 MAC-SLU、两个人工 Excel 或历史 Safety Gold 内容，不实现最终中文样本 schema，不训练模型。

## 方案对比

### 方案一：从 `intents[]` 删除22条

- 优点：正式列表直接得到71条。
- 缺点：破坏语义认知和 VSS 来源完整性，不符合任务约束。

### 方案二：拆成两个独立注册表

- 优点：正式与不开放清单物理隔离。
- 缺点：合同容易漂移，重复维护 provenance。

### 方案三：单一93条语义目录加用户语音范围投影

- 优点：不删除任何语义或 VSS 来源；71/22 可机器校验；运行支持状态保持独立。
- 缺点：消费者必须显式读取范围字段，不能再把全部 `intents[]` 当作正式执行标签。

## 推荐方案

采用方案三。每条 intent 新增 `user_voice_scope_status`，只允许 `FORMAL_EXECUTABLE` 或 `KNOWN_UNSUPPORTED_CONTROL`。R3 同时冻结 `formal_user_voice_intent_ids` 与 `known_unsupported_control_intent_ids` 两个有序投影视图。

## 详细设计

### 架构

- `intent_registry_r3.yaml`：唯一 R3 语义目录及71/22范围投影。
- `mapping_rules/full_nlu_mapping_v1.yaml`：灯光、方向盘和挡位等版本化映射规则。
- `build_sys014_r3_voice_registry.py`：从固定 R2 SHA 确定性生成 R3、审计和 manifest。
- `validate_sys014_r3_voice_registry.py`：校验计数、合同、来源、语义键、历史 PoC 隔离和 manifest 哈希。

### 数据流

1. 校验 R2 文件真实 SHA。
2. 按中文名称和固定 ID 双重确认22项映射。
3. 保留93条 intent 和原顺序，仅增加用户语音范围字段。
4. 验证71/22、关键合同、来源和历史 PoC 依赖。
5. 全部通过后标记 `FROZEN_FOR_FULL_NLU_DATASET_BUILD` 并生成 manifest。

### 异常与边界处理

- R2 SHA、名称、ID、数量任一不符即停止。
- 不为满足71强删其他意图。
- 不改写 `intent_runtime_support.yaml`。
- 不允许 R3 Full NLU 主路径引用 `sys014-poc7-*`、7类 label mapping 或 checkpoint。

### 测试策略

- R2 原 validator 必须通过。
- R3 validator 必须检查重复 ID、语义键冲突、全部合同引用、来源追溯、关键高风险保留、方向盘/灯光/GEAR_SET 规则及 manifest SHA。
- 新增离线测试验证可重复构建和关键不变量。

## 风险与待确认项

旧 `annotation_schema.json` 与下一阶段的中文统一样本结构冲突，本轮只记录，不修改。历史 PoC 文件保留，但统一标记为 `HISTORICAL_POC_ONLY / NOT_FOR_FULL_NLU`。

