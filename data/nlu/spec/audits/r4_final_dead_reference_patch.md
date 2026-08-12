# R4 Final Dead Reference Patch

- 修改前 SHA256: `b6453ff4c264464bb74ceb2aaa78cfc7fea7b55eef9a1d61bb2a7c54df47edae`
- 修改后 SHA256: `d4f3d203308a5eb9a039fee31851c110b21bafc7727f23fd6f2b83edefadad4e`
- Validator: **PASS**
- YAML 实际语义修改字段数: **1**

## 唯一 YAML 语义修改

删除 `mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH.restricted_aliases.ON.prohibited_canonical_mode: BEAM`。

`allowed_intent_id: HEADLIGHT_SET_MODE` 与对 `LOW_BEAM_ON`、`HIGH_BEAM_ON` 的禁止映射保持不变。

## 冻结确认

- 71 Formal Intent 100% 保持: **true**
- Runtime scope: **4，保持不变**
- KNOWN_CONTROL_BYPASS: **保持不变**
- FOLLOWING_GAP_REQUIRED: **未恢复**
- 旧 7-Intent active dependency: **0**

## 边界登记

- Gold absolute-speed mandatory rule 落地: **true**
- 正式 `nlu_mapping_r4_scope_v1.yaml`: **未创建**
- 两个 execution todo 已登记: **true**

未运行 Gold mapping dry-run，未生成 Gold 数据，未训练。
