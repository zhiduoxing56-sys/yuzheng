# R4 最终死引用微补丁与 Gold 边界登记设计

## 背景与目标

以 SHA256 为 `b6453ff4c264464bb74ceb2aaa78cfc7fea7b55eef9a1d61bb2a7c54df47edae` 的 `intent_registry_r4_final.yaml` 为唯一父版本，只删除 `HEADLIGHT_MAIN_SWITCH.restricted_aliases.ON.prohibited_canonical_mode: BEAM` 这一处已失效引用。R4 的 71 个 Formal Intent、4 个 runtime scope 及其他合同全部冻结不变。

## 方案与边界

正式 `nlu_mapping_r4_scope_v1.yaml` 尚不存在，因此不创建不完整的正式 mapping；仅在 `data/nlu/spec/mapping_rules/r4_gold_mapping_mandatory_rules_v1.yaml` 登记一条必须在后续 mapping 纳入的绝对目标速度隔离规则。两个执行层问题登记在独立 `r4_execution_layer_todos_v1.yaml`，不写入 NLU registry，也不改变 Gold 合法语义。

备选方案包括提前创建正式 mapping、或把规则与 TODO 写回 registry；两者都会突破本轮边界，因此不采用。

## 实施与失败策略

构建器先校验父文件 SHA、正式 mapping 不存在、死引用精确存在，再生成三个限定产物。验证器反向重建修改前 registry 并核对固定 SHA，要求语义 diff 只有一个叶子路径；任何额外 registry 语义变化、额外 mapping rule、scope/Intent/合同变化都会使任务失败。

## 验证策略

- 71 个 Formal Intent 的 ID、顺序和完整定义保持一致。
- HEADLIGHT canonical mode 不含 `BEAM`，ON 仍禁止映射 LOW/HIGH BEAM Intent。
- 4 个 runtime scope、KNOWN_CONTROL_BYPASS 路由、旧 7-Intent active dependency 与 `FOLLOWING_GAP_REQUIRED` 状态保持不变。
- mandatory sidecar 仅包含 `NON_CRUISE_ABSOLUTE_SPEED_TARGET`。
- 两个 execution TODO 均存在且不阻塞 Gold/训练。
- 不运行 Gold mapping dry-run，不生成 Gold，不训练。
