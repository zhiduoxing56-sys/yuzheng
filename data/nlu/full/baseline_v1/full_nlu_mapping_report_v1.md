# Full NLU R3 数据基线审计报告

- 构建版本：`full_nlu_baseline_v1`
- 映射规则：`nlu_mapping_v2`
- Schema：`full_nlu_sample_schema_v1`
- R3 SHA256：`c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06`

## 硬门槛

- train_set.jsonl: expected=18000, actual=18000, PASS=True
- dev_set.jsonl: expected=1391, actual=1391, PASS=True
- test_set.jsonl: expected=1151, actual=1151, PASS=True
- weak: expected=162, actual=162, PASS=True
- safety: expected=197, actual=197, PASS=True

## MAC-SLU 审计

- 原始行：20542
- 精确文本去重后 canonical：20540
- 重复组：2；跨划分重复组：2

## 统一监督统计

- 总样本：20899
- 控制范围：{"未知": 9285, "正式可执行": 2731, "已知但不开放": 2149, "非控制": 6734}
- 结构状态：{"歧义": 10965, "单意图": 8086, "多意图": 1270, "缺槽": 578}
- 语气状态：{"肯定": 20555, "否定": 245, "取消": 99}
- needs_review：11044
- 正式完整正样本：619

## 71 项正式意图完整正样本覆盖

| canonical_intent_id | 数量 | 缺口等级 |
|---|---:|---|
| MIRROR_HEATING_ON | 5 | WEAK(<10) |
| MIRROR_HEATING_OFF | 0 | ZERO |
| SEAT_LONGITUDINAL_SET_POSITION | 10 | ADEQUATE |
| SEAT_TILT_SET_ANGLE | 0 | ZERO |
| SEAT_BACKREST_SET_ANGLE | 35 | ADEQUATE |
| SEAT_HEIGHT_SET_POSITION | 10 | ADEQUATE |
| SEAT_LUMBAR_SET_HEIGHT | 15 | ADEQUATE |
| SEAT_LUMBAR_SET_SUPPORT | 16 | ADEQUATE |
| STEERING_WHEEL_SET_EXTENSION | 7 | WEAK(<10) |
| STEERING_WHEEL_SET_TILT | 5 | WEAK(<10) |
| DEFROST_ON | 28 | ADEQUATE |
| DEFROST_OFF | 24 | ADEQUATE |
| WINDSHIELD_HEATING_ON | 2 | WEAK(<10) |
| WINDSHIELD_HEATING_OFF | 2 | WEAK(<10) |
| ESC_ENABLE | 9 | WEAK(<10) |
| ESC_DISABLE | 11 | ADEQUATE |
| TRUNK_OPEN | 8 | WEAK(<10) |
| TRUNK_CLOSE | 1 | WEAK(<10) |
| TRUNK_SET_POSITION | 1 | WEAK(<10) |
| TRUNK_LOCK | 1 | WEAK(<10) |
| TRUNK_UNLOCK | 1 | WEAK(<10) |
| HOOD_OPEN | 12 | ADEQUATE |
| HOOD_CLOSE | 12 | ADEQUATE |
| GEAR_SET | 28 | ADEQUATE |
| GEAR_CHANGE_MODE_SET | 6 | WEAK(<10) |
| HORN_ACTIVATE | 12 | ADEQUATE |
| MIRROR_FOLD | 7 | WEAK(<10) |
| MIRROR_UNFOLD | 2 | WEAK(<10) |
| MIRROR_SET_ANGLE | 0 | ZERO |
| SUNROOF_OPEN | 9 | WEAK(<10) |
| SUNROOF_CLOSE | 18 | ADEQUATE |
| SUNROOF_SET_TILT | 0 | ZERO |
| CRUISE_ENABLE | 1 | WEAK(<10) |
| CRUISE_DISABLE | 1 | WEAK(<10) |
| CRUISE_SET_SPEED | 0 | ZERO |
| CRUISE_SET_GAP | 0 | ZERO |
| HEADLIGHT_SET_MODE | 14 | ADEQUATE |
| HAZARD_LIGHT_ON | 2 | WEAK(<10) |
| HAZARD_LIGHT_OFF | 1 | WEAK(<10) |
| TURN_INDICATOR_ON | 0 | ZERO |
| TURN_INDICATOR_OFF | 4 | WEAK(<10) |
| LOW_BEAM_ON | 2 | WEAK(<10) |
| LOW_BEAM_OFF | 2 | WEAK(<10) |
| HIGH_BEAM_ON | 3 | WEAK(<10) |
| HIGH_BEAM_OFF | 2 | WEAK(<10) |
| FOG_LIGHT_ON | 3 | WEAK(<10) |
| FOG_LIGHT_OFF | 2 | WEAK(<10) |
| PARKING_LIGHT_ON | 10 | ADEQUATE |
| PARKING_LIGHT_OFF | 8 | WEAK(<10) |
| WINDOW_OPEN | 45 | ADEQUATE |
| WINDOW_CLOSE | 41 | ADEQUATE |
| WINDOW_SET_POSITION | 24 | ADEQUATE |
| DOOR_OPEN | 10 | ADEQUATE |
| DOOR_CLOSE | 19 | ADEQUATE |
| DOOR_SET_POSITION | 6 | WEAK(<10) |
| DOOR_LOCK | 3 | WEAK(<10) |
| DOOR_UNLOCK | 3 | WEAK(<10) |
| WIPER_SET_MODE | 2 | WEAK(<10) |
| WIPER_SET_SENSITIVITY | 0 | ZERO |
| PARKING_BRAKE_APPLY | 4 | WEAK(<10) |
| PARKING_BRAKE_RELEASE | 13 | ADEQUATE |
| PARKING_BRAKE_AUTO_APPLY_ENABLE | 0 | ZERO |
| PARKING_BRAKE_AUTO_APPLY_DISABLE | 0 | ZERO |
| ACCELERATE | 12 | ADEQUATE |
| DECELERATE | 9 | WEAK(<10) |
| BRAKE | 36 | ADEQUATE |
| EMERGENCY_BRAKE | 11 | ADEQUATE |
| LANE_CHANGE | 10 | ADEQUATE |
| LANE_KEEP | 9 | WEAK(<10) |
| EVASIVE_STEER | 6 | WEAK(<10) |
| AUTO_PARK_ENABLE | 4 | WEAK(<10) |

## Schema 结论

- 全部派生数据是否100%符合冻结统一样本结构：**是**
- `SCHEMA_COMPLIANCE_RATE=100.000000%`

## 已知但不开放与人工复核

- 已知但不开放对象/能力计数：{"HVAC": 1358, "SEAT_VENTILATION": 405, "SEAT_MASSAGE": 370, "DISPLAY": 274, "SEAT_HEATING": 167, "SUNSHADE": 52, "FRAGRANCE": 49, "STEERING_WHEEL_HEATING": 35, "LANE": 6, "TCS": 5, "AMBIENT_LIGHT": 3, "VEHICLE": 1, "HIGH_BEAM": 1}
- needs_review 原因：{"UNRESOLVED_MAC_VEHICLE_SEMANTICS": 4627, "NO_USABLE_MAC_SEMANTIC_FRAME": 3957, "EMPTY_MAC_ANNOTATION": 1793, "BROAD_LIGHT_OBJECT": 516, "MIXED_CONTROL_NONCONTROL": 430, "KNOWN_CABIN_ACTION_UNRESOLVED": 211, "UNRESOLVED_SAFETY_SEMANTICS": 57, "STEERING_DIMENSION_UNRESOLVED": 29, "EMPTY_SOURCE_QUERY": 1}
- 复合情况：{"MULTI_WITH_INCOMPLETE_OR_AMBIGUOUS": 1710, "FORMAL_AND_KNOWN_UNSUPPORTED_MIXED": 613, "MULTI_WITH_否定": 19, "MULTI_WITH_取消": 3}

## 自然用户语音可说性存疑（本轮未删除）

- SEAT_LONGITUDINAL_SET_POSITION
- SEAT_TILT_SET_ANGLE
- SEAT_BACKREST_SET_ANGLE
- SEAT_HEIGHT_SET_POSITION
- STEERING_WHEEL_SET_EXTENSION
- STEERING_WHEEL_SET_TILT

## 派生产物与 SHA256

- `data\nlu\full\baseline_v1\mac_slu_canonical_pool_v1.jsonl` — `1ec0ceae6e9d5461b925fe9502e8418ff4d313a472864f04f9746e3957b1f968`
- `data\nlu\full\baseline_v1\weak_seed_pool_v1.jsonl` — `9778bc82e859d12ab13bff1bca2992ec4f9709d392d67e6989c79472423ec992`
- `data\nlu\full\baseline_v1\safety_boundary_pool_v1.jsonl` — `dcfcf79e26bb4551e0834ce17c295e9b335d210ec5fa713f31c72385c811ab52`
- `data\nlu\full\baseline_v1\full_nlu_canonical_raw_pool_v1.jsonl` — `939e8172c2b4cd82dff1ce1aa7251fc79a597e312c4d8a8081c0de0e062845a2`
- `data\nlu\full\baseline_v1\source_provenance_v1.jsonl` — `aa7625c82e6cb733f903da844ab1b954b566fa35cfb484096498cda3e9a39139`
- `data\nlu\full\baseline_v1\sample_mapping_metadata_v1.jsonl` — `7fe5e962accf6fe9779560b1700f64da3299a6f62acc882db6d04c9022325de6`
- `data\nlu\full\baseline_v1\mac_exact_duplicates_v1.json` — `961f506104b233ec199f48a110af146a63b7d56db3bfd71a79fe15eeff68c897`
- `data\nlu\full\baseline_v1\mac_raw_label_slot_statistics_v1.json` — `2ca10ee2d52aa42a28d5ae0cc20920ff688500f7914b7d3f2fb58ae8a2885ad7`

## 阶段边界

- `ACTIVE_FULL_NLU_DEPENDENCY_COUNT=0`
本轮未生成最终 train/dev/test，未扩写，未训练，未加载历史 7-Intent checkpoint。
