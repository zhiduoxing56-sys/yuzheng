# 第⑤+⑥阶段 Canonical Command Identity 迁移审计

## 冻结边界

- Formal：71
- Known Non-Executable：78
- Unified semantic：149
- 本阶段未修改统一 Registry、Cards、Anchors 或 Intent 定义。

## 旧 executable_actions 全量迁移矩阵

| legacy action\|target | 当前具体 intent_id | identity | 唯一 | 当前物理库存 | canonical slot 对执行支持的影响 | 迁移结论 |
|---|---|---:|---:|---:|---|---|
| 打开\|车门 | DOOR_OPEN | FORMAL | 是 | 是 | AREA 仅允许省略或 ALL；不把 unknown 转换为 ALL | 纳入合同 |
| 解锁\|车门 | DOOR_UNLOCK | FORMAL | 是 | 是 | AREA 仅允许省略或 ALL | 纳入合同 |
| 解锁\|门锁 | DOOR_UNLOCK | FORMAL | 是（旧显示别名） | 是 | 同 DOOR_UNLOCK | 合并，不保留别名白名单 |
| 关闭\|前照灯 | HEADLIGHT_SET_MODE | FORMAL | 是（mode=OFF） | 是 | MODE=OFF；Simulator/MockBench/CARLA 支持 | 纳入合同 variant |
| 设置\|前照灯 | HEADLIGHT_SET_MODE | FORMAL | 是 | 部分 | Simulator/MockBench 仅 OFF；CARLA 为 OFF/ON；其他 Registry mode 均拒绝 | 纳入受限合同 |
| 打开\|车窗 | WINDOW_OPEN | FORMAL | 是 | 是 | AREA 仅允许省略或 ALL | 纳入合同 |
| 关闭\|大屏 | DISPLAY_OFF | KNOWN_NON_EXECUTABLE | 是 | 是 | Known 永远不得签发 Token | 从语音执行支持移除；保留物理库存 |
| 打开\|音乐 | 无 Formal 对应；当前命中 Known/REVIEW 边界 | 非 Formal | 否 | 是 | 无合法 canonical command | 移除 |
| 播放\|音乐 | 无 Formal 对应 | 非 Formal | 否 | 是 | 无合法 canonical command | 移除 |
| 加速\|速度 | ACCELERATE | FORMAL | 是 | 是 | VALUE 省略时固定 +10；Simulator 可显式 10，其他值拒绝；CARLA 仅省略值 | 纳入合同 |
| 减速\|速度 | DECELERATE | FORMAL | 是 | 是 | VALUE 省略时固定 -10；Simulator 可显式 10，其他值拒绝；CARLA 仅省略值 | 纳入合同 |
| 打开\|制动 | BRAKE | FORMAL | 是 | 是 | 仅 VALUE 省略；百分比值未实现并拒绝 | 纳入合同 |
| 打开\|自动泊车 | AUTO_PARK_ENABLE | FORMAL | 是 | 是 | 不承载命令 slot | 纳入合同 |

最终 canonical executable 候选全集精确为：

`DOOR_OPEN`、`DOOR_UNLOCK`、`HEADLIGHT_SET_MODE`、`WINDOW_OPEN`、`ACCELERATE`、`DECELERATE`、`BRAKE`、`AUTO_PARK_ENABLE`。

生产执行支持事实不是无条件 ID 白名单，而是 `intent_id + adapter + canonical slot constraints + physical_action`。所选物理库存项、adapter 实现、合同版本共同进入稳定 SHA-256 摘要。

## DISPLAY_OFF 退休审计

1. `DISPLAY_OFF` 在统一 Registry 中为 `KNOWN_NON_EXECUTABLE`。
2. Pipeline 在 EvidenceDemand 与 SafetyGate 之前以语义 PASS 终止纯 Known occurrence。
3. Canonical capability registry 精确包含 8 个 Formal Intent，不包含 DISPLAY。
4. `AuthorizationTokenService.is_executable` 对 DISPLAY_OFF 返回 false。
5. 直接调用 `issue` 会因非 Formal/capability unsupported 而拒绝。
6. 新 Token 必须包含完整 canonical identity 与 capability contract 摘要；无法签发 DISPLAY_OFF Token。
7. Execution 永久拒绝缺少 canonical identity 的旧 Token，并要求 Token、原审计、PRE_EXECUTION_CHECK 三方 identity 一致。

因此 DISPLAY_OFF 不存在语音可信执行路径，以下两条规则与 evaluator 已安全退休：

- `REVERSE_CAMERA_DISPLAY_OFF_PROHIBITED`
- `ACTIVE_NAVIGATION_DISPLAY_OFF_PROHIBITED`

`vehicle_actions.yaml` 中 `关闭|大屏 → display_state=OFF` 保留。该 `actions` 节是底层物理能力库存；语音资格只由 canonical capability contracts 决定。合同只引用库存键，单一 translator 选择当前 adapter 实现，Adapter 不再解释 canonical 语义。

## SafetyGate rule reachability audit

| rule_id | evaluator | rule_type | canonical selector | positive test | negative test | reachable |
|---|---|---|---|---|---|---:|
| SEMANTIC_MODEL_DEGRADED_HIGH_RISK | semantic_model_degraded | canonical semantic | FORMAL + risk_level + RuntimeCapabilityStatus | `test_bge_failure_blocks_r3_and_is_audited_and_streamed` | 同文件 R1/R2/full-mode cases | true |
| MANDATORY_EVIDENCE_AVAILABLE | mandatory_missing | evidence/occurrence | EvidenceDemand required binding | `test_safety_gate_missing_is_not_masked_by_other_occurrence_same_type` | `test_stationary_numeric_speed_zero_keeps_formal_pass_behavior` | true |
| MANDATORY_EVIDENCE_INTEGRITY | mandatory_tampered | evidence/occurrence | canonical required evidence status | `test_hnsw_miss_recalls_newest_abnormal_instead_of_older_valid[TAMPERED]` | valid required evidence cases | true |
| LEVEL3_JAILBREAK_CONFLICT | level3_jailbreak | global validation | severity=3 validation conflict | security injection pipeline tests | ordinary command baseline | true |
| MANDATORY_EVIDENCE_FRESHNESS | mandatory_stale | evidence/occurrence | canonical required evidence status | `test_hnsw_miss_recalls_newest_abnormal_instead_of_older_valid[STALE]` | valid required evidence cases | true |
| MANDATORY_TRUST_THRESHOLD | mandatory_trust | evidence/occurrence | selected required evidence trust | `test_blocker_formulas` trust-threshold cases | valid evidence baseline | true |
| MOVING_DOOR_OPEN_PROHIBITED | moving_door | canonical semantic | DOOR_OPEN or DOOR_SET_POSITION/value>0 | phase56 real semantic cases | DOOR_CLOSE case | true |
| LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED | low_light_headlight | canonical semantic | HEADLIGHT_SET_MODE/mode=OFF | phase56 real OFF case | real ON case | true |
| DENSE_FOG_FRONT_DEFOG_OFF_PROHIBITED | dense_fog_defog | canonical semantic | DEFROST_OFF | phase56 real fog OFF case | real DEFROST_ON case | true |
| NON_DRIVER_DRIVING_CONTROL_PROHIBITED | non_driver_control | canonical metadata | Registry control_domain=驾驶控制 + occurrence authorization | phase56 passenger ACCELERATE | trusted driver tests | true |
| REAL_ROAD_SAFETY_BYPASS_PROHIBITED | real_road_bypass | global validation | SAFETY_CONSTRAINT_BYPASS/SIMULATOR_MODE_SPOOFING | `test_global_validation_rules_are_production_reachable` | no-security-signal baseline | true |
| UNAUTHORIZED_DIRECT_INTERFACE_PROHIBITED | unauthorized_direct_interface | global validation | UNAUTHORIZED_DIRECT_INTERFACE | 同上参数化 case | no-security-signal baseline | true |
| UNAUTHORIZED_CONTROL_FRAME_PROHIBITED | unauthorized_control_frame | global validation | UNAUTHORIZED_CONTROL_FRAME | 同上参数化 case | no-security-signal baseline | true |
| AUTOPARK_CRITICAL_EVIDENCE_REQUIRED | autopark_critical | canonical semantic | AUTO_PARK_ENABLE | phase56 unavailable sensor case | available sensor baseline | true |
| FRONT_OBSTACLE_ACCELERATION_PROHIBITED | acceleration_obstacle | canonical semantic | ACCELERATE | phase56 front-distance case | DECELERATE/BRAKE/EMERGENCY cases | true |
| REAR_STATE_DECELERATION_CONFLICT | deceleration_rear_conflict | canonical semantic | DECELERATE or BRAKE | phase56 DECELERATE/BRAKE cases | EMERGENCY_BRAKE case | true |

Active SafetyGate rule count：16。配置 rule 与 evaluator 集合一一对应，所有 active rules `reachable=true`。

## Token 与 Execution

Token canonical payload 绑定：

- `intent_id`, `area`, `mode`, `value`, `direction`, `control_attribute`
- `capability_contract_id`, `capability_contract_version`, `capability_contract_digest`, `capability_adapter`
- `token_id`, `turn_id`, `root_turn_id`, `state_snapshot_digest`
- `issued_at`, `expires_at`, `key_id`, `key_version`, `nonce`

`display_action/display_target` 仅是签名内 display metadata，不参与 eligibility、验证或 adapter 选择。

SQLite 通过带稳定 migration ID 的一次性 schema migration 增加 canonical columns，成功后写入 `schema_migrations`，生产启动不会重复执行增列。历史 Token 可读取用于审计；缺少 `intent_id/control_attribute` 或 capability binding 的 Token 永久拒绝执行，无 legacy fallback。

Token 验证还逐项核对持久化的 `nonce_digest`、`key_version`、`issued_at` 与 `expires_at`。这些字段缺失或与签名 payload 不一致时 fail closed；能力合同版本或摘要变化同样使旧 Token 永久失效。

Execution 校验：合法签名与持久化记录 → Token canonical identity 与原审计一致 → PRE_EXECUTION_CHECK identity 一致 → 当前 adapter capability digest 一致 → single translator 读取物理库存 → VehicleAdapter。

语音区域权限也不再读取展示 `action/target` 或 Registry 的 `canonical_action/canonical_target` 作为第二安全身份。旧风险集合机械展开为经统一 Registry 校验的具体 `intent_id` selector；结果中的 action/target 仅供展示。

## 实施文件与验证

生产实现与配置：

- `backend/app/services/command_identity.py`
- `backend/app/services/vehicle/capabilities.py`
- `backend/app/services/authorization/service.py`
- `backend/app/services/workflow/repository.py`
- `backend/app/services/execution/service.py`
- `backend/app/services/decision/safety_gate.py`
- `backend/app/services/decision/engine.py`
- `backend/app/services/voice/zone.py`
- `backend/app/services/validation/advanced.py`
- `backend/app/services/vehicle/{base,simulator,mock_bench,carla,can}.py`
- `backend/app/core/pipeline.py`
- `backend/app/models/schemas.py`
- `config/{authorization,decision_policy,safety_rules,vehicle_actions,voice}.yaml`

专项测试与审计：

- `backend/tests/integration/test_canonical_command_identity_phase56.py`
- `backend/tests/integration/test_unified_semantic_runtime_v1.py`
- `backend/tests/integration/test_evidence_type_phase2.py`
- `backend/tests/stage3/test_stage3_scenarios.py`
- `backend/tests/stage4/{test_stage4_workflow,test_stage4_freeze_token_security,_token_process_worker}.py`
- `backend/tests/stage5/test_trusted_voice_pipeline.py`
- `docs/plans/2026-08-13-canonical-command-identity-design.md`
- 本报告

核心专项结果：`20 passed`；模块 `compileall` 通过。Stage4 Token 安全回归已确认 expired、tampered、reused、cross-restart 四项通过；完整旧 Stage4 组合另有 Review 候选为空的既有语义/Review 回归，与 Token 签发前即失败，未作为本阶段通过证据。Stage5 的冻结语义断言已同步迁移，完整结果为 `28 passed`。

## 保留安全债

`AUTOPARK_CRITICAL_EVIDENCE_REQUIRED` 仍读取 `RuntimeSafetyContext` 的 surround camera/ultrasonic 状态，而非本轮重构 Evidence truth source。该问题保持为第⑦阶段剩余安全债。

## 阶段状态

- 第⑤阶段 SafetyGate canonical identity：DONE
- 第⑥阶段 Decision/Authorization/Token/Execution canonical identity：DONE
- 下一阶段：第⑦阶段剩余安全债收口
