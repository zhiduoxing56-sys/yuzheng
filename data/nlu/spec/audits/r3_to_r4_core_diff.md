# R3 → R4 Core Diff

- R3: `data/nlu/spec/intent_registry_r3.yaml`
- R3 SHA256: `c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06`
- R4: `data/nlu/spec/intent_registry_r4_core_draft.yaml`
- R4 SHA256: `8726c6f782f2a57ddfd4c3b1557497349d912d3d06acd97c73983650fd9fc827`
- R4 状态: `DRAFT_PENDING_KNOWN_UNSUPPORTED_EXPANSION`
- Validator: **PASS**
- 批准外差异路径: **0**

## P0-01 WINDOW endpoint uniqueness

- 涉及字段: `value_contracts.PERCENT_PARTIAL_1_99_REQUIRED, intents.WINDOW_SET_POSITION.value_contract, annotation_guidance.window_endpoint_routing, over_atomization_audit`
- Validator 结果: **PASS**

修改前：

```json
{
  "value_contract": "PERCENT_0_100_REQUIRED",
  "audit_examples": [
    "20%",
    "50%",
    "一半"
  ]
}
```

修改后：

```json
{
  "value_contract": "PERCENT_PARTIAL_1_99_REQUIRED",
  "contract": {
    "allowed": true,
    "required": true,
    "type": "PERCENT",
    "canonical_unit": "%",
    "valid_range": {
      "min": 1,
      "max": 99
    },
    "enum_values": [],
    "endpoint_routes": {
      "0": "WINDOW_CLOSE",
      "100": "WINDOW_OPEN"
    },
    "endpoint_values_prohibited_for_contract": true
  },
  "audit_examples": [
    "1%",
    "20%",
    "50%",
    "99%",
    "一半"
  ]
}
```

## P0-02 ACCELERATE/DECELERATE relative VALUE

- 涉及字段: `value_contracts.SPEED_DELTA_OPTIONAL, intents.ACCELERATE.value_contract, intents.DECELERATE.value_contract, annotation_guidance.speed_delta_routing`
- Validator 结果: **PASS**

修改前：

```json
{
  "ACCELERATE": "SPEED_OPTIONAL",
  "DECELERATE": "SPEED_OPTIONAL"
}
```

修改后：

```json
{
  "ACCELERATE": "SPEED_DELTA_OPTIONAL",
  "DECELERATE": "SPEED_DELTA_OPTIONAL"
}
```

## P0-03 CRUISE_GAP_LEVEL expansion

- 涉及字段: `mode_contracts.CRUISE_GAP_LEVEL, over_atomization_audit.CRUISE_SET_GAP.examples`
- Validator 结果: **PASS**

修改前：

```json
[
  "LEVEL_N"
]
```

修改后：

```json
[
  "LEVEL_1",
  "LEVEL_2",
  "LEVEL_3",
  "LEVEL_4"
]
```

## P0-04 OFF YAML string typing

- 涉及字段: `mode_contracts, over_atomization_audit.*.examples`
- Validator 结果: **PASS**

修改前：

```json
{
  "HEADLIGHT_SET_MODE": [
    false,
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO",
    "BEAM"
  ],
  "WIPER_SET_MODE": [
    false,
    "SLOW",
    "MEDIUM",
    "FAST",
    "INTERVAL",
    "RAIN_SENSOR"
  ]
}
```

修改后：

```json
{
  "HEADLIGHT_SET_MODE": [
    "OFF",
    "ON",
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO"
  ],
  "WIPER_SET_MODE": [
    "OFF",
    "SLOW",
    "MEDIUM",
    "FAST",
    "INTERVAL",
    "RAIN_SENSOR"
  ]
}
```

## P0-05 Seat semantic boundaries

- 涉及字段: `annotation_guidance.seat_semantic_boundaries`
- Validator 结果: **PASS**

修改前：

```json
null
```

修改后：

```json
{
  "intents": [
    "SEAT_LONGITUDINAL_SET_POSITION",
    "SEAT_TILT_SET_ANGLE",
    "SEAT_BACKREST_SET_ANGLE"
  ],
  "lexical_anchors": {
    "LONGITUDINAL": [
      "前移",
      "后移",
      "往前挪",
      "往后挪",
      "前后移动",
      "滑轨",
      "座椅前后位置"
    ],
    "BACKREST": [
      "靠背",
      "椅背",
      "躺",
      "后仰",
      "放倒",
      "直立",
      "靠背角度"
    ],
    "TILT": [
      "坐垫",
      "座盆",
      "整体倾角",
      "座椅整体倾斜",
      "坐垫前端抬高或降低",
      "坐垫后端抬高或降低"
    ]
  },
  "unqualified_forward_backward_examples": [
    "座椅往前调",
    "座椅往后调"
  ],
  "unqualified_forward_backward_priority": "SEAT_LONGITUDINAL_SET_POSITION",
  "extra_anchor_absence_required": [
    "BACKREST",
    "SEAT_CUSHION",
    "OVERALL_TILT"
  ],
  "ambiguity_policy": "ONLY_WHEN_SOURCE_TEXT_HAS_TWO_REASONABLE_INTERPRETATIONS"
}
```

## P0-06 HEADLIGHT main-light mode

- 涉及字段: `mode_contracts.HEADLIGHT, mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH, over_atomization_audit.HEADLIGHT_SET_MODE, annotation_guidance.headlight_main_switch_routing`
- Validator 结果: **PASS**

修改前：

```json
{
  "modes": [
    "OFF",
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO",
    "BEAM"
  ],
  "mapping": {
    "canonical_modes": [
      "OFF",
      "POSITION",
      "DAYTIME_RUNNING_LIGHTS",
      "AUTO",
      "BEAM"
    ],
    "lexical_aliases": {
      "ON": {
        "canonical_mode": "BEAM",
        "condition": "EXPLICIT_MAIN_LIGHT_SWITCH_REFERENCE"
      }
    }
  }
}
```

修改后：

```json
{
  "modes": [
    "OFF",
    "ON",
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO"
  ],
  "mapping": {
    "canonical_modes": [
      "OFF",
      "ON",
      "POSITION",
      "DAYTIME_RUNNING_LIGHTS",
      "AUTO"
    ],
    "lexical_aliases": {
      "ON": {
        "canonical_mode": "ON",
        "condition": "EXPLICIT_MAIN_LIGHT_SWITCH_REFERENCE"
      }
    },
    "restricted_aliases": {
      "ON": {
        "allowed_intent_id": "HEADLIGHT_SET_MODE",
        "prohibited_intent_ids": [
          "LOW_BEAM_ON",
          "HIGH_BEAM_ON"
        ],
        "prohibited_canonical_mode": "BEAM"
      }
    }
  }
}
```

## P0-07 TRUNK/FRUNK/HOOD isolation

- 涉及字段: `intents.TRUNK_*.allowed_areas, annotation_guidance.trunk_frunk_hood_routing`
- Validator 结果: **PASS**

修改前：

```json
{
  "TRUNK_OPEN": [
    "FRONT",
    "REAR"
  ],
  "TRUNK_CLOSE": [
    "FRONT",
    "REAR"
  ],
  "TRUNK_SET_POSITION": [
    "FRONT",
    "REAR"
  ],
  "TRUNK_LOCK": [
    "FRONT",
    "REAR"
  ],
  "TRUNK_UNLOCK": [
    "FRONT",
    "REAR"
  ]
}
```

修改后：

```json
{
  "TRUNK_OPEN": [
    "REAR"
  ],
  "TRUNK_CLOSE": [
    "REAR"
  ],
  "TRUNK_SET_POSITION": [
    "REAR"
  ],
  "TRUNK_LOCK": [
    "REAR"
  ],
  "TRUNK_UNLOCK": [
    "REAR"
  ]
}
```

## 语义差异路径

- `annotation_guidance`
- `document_status`
- `intents.ACCELERATE.value_contract`
- `intents.DECELERATE.value_contract`
- `intents.TRUNK_CLOSE.allowed_areas`
- `intents.TRUNK_LOCK.allowed_areas`
- `intents.TRUNK_OPEN.allowed_areas`
- `intents.TRUNK_SET_POSITION.allowed_areas`
- `intents.TRUNK_UNLOCK.allowed_areas`
- `intents.WINDOW_SET_POSITION.value_contract`
- `mode_contracts.CRUISE_GAP_LEVEL`
- `mode_contracts.HEADLIGHT`
- `mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH.canonical_modes`
- `mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH.lexical_aliases.ON.canonical_mode`
- `mode_mapping_contracts.HEADLIGHT_MAIN_SWITCH.restricted_aliases`
- `modified_date`
- `over_atomization_audit.parameterized_instead_of_split.CRUISE_SET_GAP.examples`
- `over_atomization_audit.parameterized_instead_of_split.HEADLIGHT_SET_MODE.examples`
- `over_atomization_audit.parameterized_instead_of_split.HEADLIGHT_SET_MODE.restricted_alias`
- `over_atomization_audit.parameterized_instead_of_split.WINDOW_SET_POSITION.examples`
- `over_atomization_audit.parameterized_instead_of_split.WIPER_SET_MODE.examples`
- `parent_registry.inheritance_rule`
- `parent_registry.path`
- `parent_registry.registry_version`
- `parent_registry.sha256`
- `registry_version`
- `semantic_freeze_status`
- `value_contracts.PERCENT_PARTIAL_1_99_REQUIRED`
- `value_contracts.SPEED_DELTA_OPTIONAL`
- `value_language_semantics.continuous_numeric_contracts`
