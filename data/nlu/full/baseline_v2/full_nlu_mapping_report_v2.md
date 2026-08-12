# Full NLU baseline_v2 映射覆盖审计报告

- R3: `c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06`
- mapping: `nlu_mapping_v3` / `a497cd887c44a15acfe9d49f9dea3bc9f718ad0f3da38e797140e85dac8da80b`
- manual overrides: `manual_override_v1` / `88b018c2d7367b1b2a3e380a8b4d5d693faa1c862ad530d2f37074ab0819b9a2`
- schema validator: `1e36653e863dd8079ba7e090f7854f873585d54692d4c3a18c6c4eb0ba082ffe`
- canonical raw pool: 20899 / `6d8645adf0fd9429bb8fd6d3d75ecfdf6d65ff4c33926ea1cc27054dd5c51a51`
- `SCHEMA_COMPLIANCE_RATE=100.000000%`

## v1/v2 关键变化

- 正式可执行: 2731 → 2071 (-660)
- 已知但不开放: 2149 → 3231 (+1082)
- 非控制: 6734 → 8682 (+1948)
- 未知: 9285 → 6915 (-2370)
- 需要人工复核: 11044 → 7817 (-3227)
- 正式正样本: 619 → 610 (-9)
- 71项零覆盖: 10 → 4 (-6)
- 71项弱覆盖: 36 → 42 (+6)

正式范围下降来自对普通座舱误标与宽泛/不唯一对象的保守纠正；安全合同未放宽。正式正样本净减少 9 = 新增 22 - 移出 31。

## 重点审计

- 未解析车辆 semantic frame：4627 个 occurrence，4311 个 canonical 样本，2246 个去重模式。
- 无可用 semantic frame：3957 条；确定性处理 929 条。
- 安全种子待复核：57 个语义 occurrence（原文未修改）。
- baseline_v2 零覆盖正式意图：MIRROR_HEATING_OFF, SEAT_TILT_SET_ANGLE, MIRROR_SET_ANGLE, TURN_INDICATOR_ON。

## needs_review v2 原因分布

| 原因 | 数量 |
|---|---:|
| NO_HIGH_PRECISION_DOMAIN_EVIDENCE | 4195 |
| UNRESOLVED_MAC_VEHICLE_SEMANTICS_V3 | 2790 |
| MIXED_CONTROL_NONCONTROL | 431 |
| BROAD_LIGHT_OBJECT | 308 |
| KNOWN_CABIN_ACTION_UNRESOLVED | 147 |
| UNRESOLVED_SAFETY_SEMANTICS | 57 |
| EXPLICIT_CONTROL_BUT_CONTRACT_UNRESOLVED | 32 |
| EMPTY_SHORT_OR_DEICTIC | 28 |
| STEERING_DIMENSION_UNRESOLVED | 27 |
| BROAD_LIGHT_MUST_REMAIN_AMBIGUOUS | 12 |
| EMPTY_SOURCE_QUERY | 1 |

## 审计资产

- 4627 frame 模式：`data/nlu/full/audit_v3/mac_unresolved_vehicle_semantic_patterns_v3.json` / `.md`
- 3957 无 frame：`data/nlu/full/audit_v3/mac_no_usable_frame_audit_v3.jsonl` / `.md`
- 十项零覆盖审计：`data/nlu/full/audit_v3/zero_coverage_10_intents_v3.json` / `.md`
- 71 项漏斗：`data/nlu/full/audit_v3/formal_71_positive_funnel_v3.json` / `.md`
- 普通座舱覆盖：`data/nlu/full/audit_v3/known_unsupported_cabin_coverage_v3.json` / `.md`
- 安全种子 57 occurrence：`data/nlu/full/audit_v3/safety_seed_unresolved_57_v3.json` / `.md`

未扩写、未训练、未生成最终 train/dev/test。
