# 第⑦阶段 ActionDirectionGuard 最终漏网收口报告

## 结论

`解除行李厢锁定` 的动作方向误判已通过通用中文复合动作解析修复。TRUNK_LOCK MODEL_REVIEW 修复保持不退化。第⑦阶段满足最终 DONE 条件，本补丁后停止，不进入第⑧阶段。

## 修改前事实

真实 `SemanticOrchestratorService.parse("解除行李厢锁定")` 与 V2.1 guard debug：

- selected intent：`TRUNK_UNLOCK`
- selected family：`UNLOCK`
- requested families：`LOCK`
- compatible candidates：`TRUNK_LOCK, DOOR_LOCK`
- semantic status：`REVIEW`
- review reason：`ACTION_DIRECTION_CONFLICT`

详见 `stage7_action_direction_trace_before.json`。

## 通用修复

ActionDirectionGuard 现在把同一子句内、短距离的 `解除 + 任意非边界文本 + 锁定` 整体识别为 `UNLOCK`。中间文本不依赖对象词表；逗号、句号、分号、问号、叹号及 ASCII 对应字符均阻止跨子句匹配。复合 span 内的 `锁定` 不再二次生成独立 `LOCK` cue。

同时删除了 UNLOCK cues 中已有的车门/尾门对象专用表达，仅保留通用 `解除锁定` 与 `解锁`。未增加 TRUNK、车门、尾门或后备箱白名单。

## 修改后真实结果

- requested families：`UNLOCK`
- selected intent/family：`TRUNK_UNLOCK / UNLOCK`
- compatible candidates：`TRUNK_UNLOCK, DOOR_UNLOCK`
- semantic status：`OK`
- review reasons / guard triggers：空
- EvidenceDemand：已生成，required `AUTHORIZATION_STATE`
- SafetyGate：实际调用，无 hit
- Decision：`PASS`
- capability：unsupported
- Token：null
- VehicleState：unchanged
- workflow chain：valid

详见 `stage7_action_direction_trace_after.json` 与 `stage7_real_behavior_golden_matrix_v2.json`。

## 回归

- 指定 TRUNK/DOOR family：13/13 真实 parse 通过。
- 原相邻自然语言：18/18 通过。
- 99-case model override 审计：错误模型新增 ACCEPT=0。
- 149 representative：expected intent/runtime identity 149/149；`unexpected_action_direction_conflicts=0`。
- frozen REVIEW：24/24 仍为 REVIEW。
- TRUNK_LOCK：`把后备箱上锁 → TRUNK_LOCK / FORMAL / OK`，仍 capability unsupported、Token null。

未修改任何 Registry、anchor、Recall、3B、Hybrid Gate、CandidateConsistencyGuard、ObjectFamilyGuard 或安全/执行链组件。
