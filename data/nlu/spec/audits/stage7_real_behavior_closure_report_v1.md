# 第⑦阶段：剩余安全债真实行为收口报告

## 结论

第⑦阶段局部安全债已经按批准边界实施，但本阶段不标记 `DONE`。原因是 TRUNK 的真实自然语言验收触发了用户指定的停止条件：`把后备箱上锁` 虽然 Top8 和 3B 都包含/选中 `TRUNK_LOCK`，最终仍进入 `REVIEW`。该子项已停止，冻结 Formal anchors、Top8、3B 和 Guard 均未为此修改。

其余已批准子项已完成：Capability 单一事实源、DECELERATE/BRAKE rear-state fail closed、AUTO_PARK 隐藏 runtime safety fact 退休、Registry-only area consistency guard，以及基于父 Audit occurrence 的 Multi-intent clarification child 全链重跑。

机器可读结果见 `stage7_real_behavior_golden_matrix_v1.json`。

## 先复现、后修改

修改前使用隔离测试数据库，以真实自然语言调用 `CommandPipeline.process_text()`：

- `减速`：`SURROUNDING_OBJECT_STATE` 仅 optional；rear 值缺失或 null 时 rear rule `MISS`。
- `正常制动一下`：rear 为 null 时 rear rule `MISS`，最终 `PASS` 并签发 Token，确认了真实 fail-open。
- `开启自动泊车`：`FREE_SPACE_STATE` 已无真实 producer，通用 mandatory gate `HIT`；旧 AUTO_PARK 专用规则仍存在但 `MISS`。
- `打开车窗然后锁车门`：父轮次 `REVIEW`、无 Token；原实现没有 occurrence clarification candidates。
- `打开左侧车窗`：旧语义可能把明确区域压成 `unknown`。
- `把后备箱上锁`：Top8/3B 正确但最终 `REVIEW`，触发 TRUNK 子项停止条件。

修改后使用相同自然语言与相同车辆场景重新运行；结果记录在黄金矩阵中。

## A. Capability 单一事实源

生产 `CANONICAL_EXECUTABLE_CANDIDATES` 已删除。唯一执行支持事实由 `config/vehicle_actions.yaml` 的 `canonical_capability_contracts` 派生，并校验每个 contract 只能引用统一 Semantic Registry 中的 Formal intent。当前恰好 8 个 executable intent 的冻结断言仅保留在测试中。

DISPLAY_OFF、音乐两项与全部 78 个 KNOWN_NON_EXECUTABLE 继续得到 capability support=false。Token 仍绑定完整 canonical identity 和 capability contract id/version/digest；旧 Token 缺失 canonical identity 时不可执行。

## B. Rear-state

DECELERATE 的 `SURROUNDING_OBJECT_STATE` 已提升为 mandatory，BRAKE 保持 mandatory。普通 rear rule 仅选择 `DECELERATE` 与 `BRAKE`；`EMERGENCY_BRAKE` 不在 selector 中。

rear node 缺失，或 `rear_obstacle_distance` 为 null、字符串、bool、NaN、正负 Inf 时均 `HIT` 并 fail closed。危险距离小于阈值时 `HIT`；合法安全距离时该 rule `MISS`。DECELERATE 的其他授权策略仍可独立阻断执行，本阶段没有绕过该策略。

## C. AUTO_PARK

已删除 active rule `AUTOPARK_CRITICAL_EVIDENCE_REQUIRED`、专用 `_autopark_critical` evaluator，以及 SafetyGate 对 `RuntimeSafetyContext.surround_camera_state / ultrasonic_distance` 的读取。没有新增 Evidence Type，没有修改 `FREE_SPACE_STATE` schema，也没有把隐藏 runtime 字段伪装成 canonical evidence。

AUTO_PARK_ENABLE mandatory 保持：`VEHICLE_SPEED + GEAR_STATE + FREE_SPACE_STATE + SURROUNDING_OBJECT_STATE`。当前 `FREE_SPACE_STATE` 无 producer，真实命令由 `MANDATORY_EVIDENCE_AVAILABLE` 阻断，无 Token、无执行、车辆状态不变。active rule 与 evaluator 均为 15。

## D. Area

区域表达只读取统一 `Semantic Registry.area_catalog` 中的 `semantic_frame_value` 与 `examples`；已删除 compact keyword list。guard 只对承载 AREA slot 的 intent 生效。

明确命中 Registry area expression 后，若最终 area 为 unknown，或该 area 不在 intent allowed_areas，则进入 `REVIEW / AREA_MENTION_UNRESOLVED` 并在 EvidenceDemand 前终止。没有猜区域，也没有把 unknown 改写成 ALL。`打开左侧车窗` 保留 `LEFT_SIDE`；由于当前 capability 不支持该具体 area，最终不签 Token。

## E. Multi-intent candidate

公共 `ClarificationCandidate` 结构保持严格五字段，不增加 parameters、clause_index 或 intent_id。稳定 candidate_id 由父 audit/turn identity、clause_index、intent_id、clause_text 的 canonical JSON SHA-256 摘要生成。

选择时重新读取持久化 ClarificationRequest 与不可变父 Audit，按相同算法复算 Formal occurrence；零匹配或多匹配均 fail closed。选中后仅把父 occurrence 的原 `clause_text` 作为 child 输入；child 使用新 turn_id、`confirmed=False`，真实重新运行 Semantic、EvidenceDemand、HNSW、Mandatory Recall、SafetyGate、Decision、Capability 与 Authorization。父 Token 不存在，也没有复用父 SemanticIntent、SafetyGate、Decision 或 Token。

## F. TRUNK 停止项

`把后备箱上锁` 的真实链路事实：

- Top8 含 `TRUNK_CLOSE / TRUNK_LOCK / TRUNK_OPEN / TRUNK_UNLOCK / TRUNK_SET_POSITION`；
- 3B 输出 `TRUNK_LOCK`；
- Guard 无 trigger；
- gate path 最终为 `MODEL_REVIEW`，公共语义为 `REVIEW`。

按批准边界，该子项立即停止并保持冻结 Formal anchors 零修改。因此整个第⑦阶段状态为 `NOT DONE`，而不是用单元测试或 mock SemanticIntent 覆盖该失败。

## 验证范围

验证包括：配置/Registry 合同、15 条 active SafetyGate、rear 非法类型矩阵、AUTO_PARK mandatory fail-closed、Multi-intent occurrence ID 与 child 全链重跑、canonical capability 8-ID 测试冻结，以及真实 Door physical execution 的 PRE_EXECUTION_CHECK、before/after state 和 workflow hash chain。

工作区在本阶段开始前已有大量未提交修改；本轮没有清理、覆盖、暂存或提交用户的既有变更。第⑤+⑥核心新文件仍保持在工作区可见。
