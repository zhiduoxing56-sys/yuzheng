# 149 个统一语义空间第一阶段运行时迁移报告

## 结论

第一阶段运行时迁移已完成并停在语义路由边界。唯一生产语义注册表包含 149 个稳定意图：71 个 `FORMAL`、78 个 `KNOWN_NON_EXECUTABLE`。本轮未迁移或修改 SafetyGate 规则、Decision canonical identity、Authorization、Token、Execution、VehicleAdapter、Evidence 类型合同、Mandatory Recall 合同、CARLA 或前端。

最高优先级纠偏已落实：新生产资产中不存在 `FORMAL_EXECUTABLE`；`FORMAL` 只表示该 occurrence 进入现有 Evidence/Safety 链，不表达车辆支持执行，也不自动产生执行资格。

## 生产资产

- 唯一注册表：`data/nlu/spec/intent_registry_unified_v1.yaml`
- 派生卡片：`挂靠/intent_cards_unified_v1.yaml`，149 张
- 派生锚点：`挂靠/intent_anchor_set_unified_v1.yaml`，3734 条语义锚点（Formal 1426、Known 2308）及 20 条安全锚点
- 生产加载与一致性校验：`backend/semantic_registry_v1/registry.py`
- 运行时冻结完整性清单：`backend/intent_hybrid_gate/runtime_semantic_freeze_v1.json`
- 生成器：`scripts/build_unified_semantic_runtime_v1.py`
- 验收器：`scripts/validate_unified_semantic_runtime_v1.py`
- 机器验收：`data/nlu/spec/audits/unified_semantic_runtime_migration_audit_v1.json`

R4 冻结文件未覆盖、未改写，继续作为 Formal 的历史来源与审计资产。生产语义入口、召回器、卡片及锚点已经停止把 R4 或旧 Known bypass 资产作为运行时语义事实源。EvidenceDemandRegistry 也改为从统一注册表筛选 71 个 `FORMAL`，原有 71 项 Evidence 需求内容未改变。

## 运行时链路

- Top8 候选现在统一携带具体 `intent_id`、Registry 派生的 `runtime_identity` 与分数。
- 3B 判定器仍只能从 Top8 中选择具体 ID，身份由 Registry 回填，不能由模型创造。
- Guard 使用统一卡片的 `canonical_action`、`canonical_target`、`control_attribute` 以及 slot 合同。
- 公共 `SemanticIntent` 新增 `runtime_identity`、`mode`、`direction`、`control_attribute`；保留唯一的 `intents[]` occurrence 数组，没有创建第二个 SemanticFrame。
- `KNOWN_NON_EXECUTABLE` 明确认知后返回语义 `PASS`，不创建 EvidenceDemand、不构建 HNSW 查询、不调用 SafetyGate、不进入授权、令牌或执行服务。
- mixed occurrence 在同一 SemanticFrame 中保序；只有 `FORMAL` occurrence 下行。当前 mixed 结果不会签发 token。
- Unknown 或缺少必填 slot 保持 `REVIEW`，并保留 review reasons/candidates/unresolved clauses。

## 关键语义样例

- `关闭前照灯` → `HEADLIGHT_SET_MODE` / `FORMAL` / `mode=OFF`
- `挂D挡` → `GEAR_SET` / `FORMAL` / `mode=D`
- `切换自动换挡模式` → `GEAR_CHANGE_MODE_SET` / `FORMAL` / `mode=AUTOMATIC`
- `打开运动模式` → `DRIVING_MODE_SET` / `KNOWN_NON_EXECUTABLE` / `mode=SPORT`
- `前舱盖开到30%` → `HOOD_SET_POSITION` / `KNOWN_NON_EXECUTABLE` / `value=30`
- `锁定外后视镜调节` → `MIRROR_ADJUSTMENT_LOCK` / `KNOWN_NON_EXECUTABLE` / semantic PASS / 0 EvidenceDemand / no token

`DRIVING_MODE_SET` 与 `GEAR_CHANGE_MODE_SET` 保持独立，未因“模式”词面合并。

## 自动验收

- Registry：149；Formal：71；Known：78；ID 唯一且非空；Formal/Known 交集 0。
- Cards：149；Anchor intent group：149；语义锚点：3734；安全锚点：20。
- 产品删除的 13 个意图活跃数量：0。
- 隔离的 89 条历史表达未恢复到活跃空间。
- 1402 个未批准哈希候选使用数量：0。
- 生产 `KNOWN_CONTROL_BYPASS` runtime output：0。
- 新生产资产 `FORMAL_EXECUTABLE`：0。
- 新增 `execution_eligible/execution_supported/executable` 并行事实：0。
- 71 个 Formal 的 EvidenceDemandRegistry 覆盖：71/71。
- 149 个批准代表锚点 Top8：149/149（Formal 71/71；Known 78/78）。
- 冻结 REVIEW 用例：24/24。
- pytest collection：624 项，CARLA 导入未阻塞收集。
- 相关语义/证据/路由专项：66/66 通过；Evidence Registry 与新增迁移测试复跑：45/45 通过。
- 全仓 `pytest -q` 在约 7 分钟仍无失败输出但未完成，已人工终止；不将其报告为通过。
- `git diff --check`：无空白错误（仅现有 Windows LF/CRLF 提示）。

## 执行支持事实纠偏

仓库当前实际表达“是否进入令牌签发候选”的唯一既有事实是 `config/authorization.yaml` 的 `executable_actions`，由 `backend/app/services/authorization/service.py::AuthorizationTokenService.is_executable` 按 `action|target` 使用。另有 `RuntimeCapabilityStatus.semantic_control_mode` 表达全局语义模型运行能力，但它不是逐意图车辆执行支持字段。

本轮没有修改上述事实或其原值，没有新增 `execution_supported`、`executable`、`execution_eligible` 等并行字段，也没有通过 `runtime_identity=FORMAL` 推导执行资格。实际车辆适配器是否支持及执行结果仍由现有 Authorization/Execution/VehicleAdapter 链处理，留待后续批准阶段。

## 旧引用分类

- 生产语义链：不再输出或加载 `KNOWN_CONTROL_BYPASS`；不再使用 `FORMAL_EXECUTABLE` 作为 runtime identity。
- 历史审计/冻结数据：R1-R4、历史审计报告和旧 scope 测试仍保留旧术语，未改写。
- 离线评估：`backend/intent_hybrid_gate/evaluate_v1_3.py` 仍固定引用旧 v1.3 锚点，仅作为历史离线评估脚本，不是生产加载路径。
- 新锚点资产中的 `legacy_known_control_bypass_active: false` 只是明确的排除审计标记，不是可路由身份。

## 本阶段停止点

迁移已停在统一语义识别、slot 完整化和 Formal/Known/Review occurrence 路由处。没有开始 SafetyGate、Decision、Authorization、Token、Execution 或 VehicleAdapter 的下一阶段 canonical identity 迁移。
