# SYS-014 Full Registry Human Approval Record

- package_status: `HUMAN_APPROVAL_APPLIED`
- reviewed_at: `2026-08-09T09:17:53+08:00`
- reviewer: `USER_APPROVED`
- Registry runtime loading: **DISALLOWED**

## Final decision summary

| Metric | Value |
|---|---:|
| TOTAL_CHANGE_ITEMS | `12` |
| FRR_APPROVE_COUNT | `9` |
| FRR_REJECT_COUNT | `2` |
| FRR_MODIFY_COUNT | `1` |
| FINAL_APPROVED_VSS_CAPABILITY_COUNT | `44` |
| FINAL_VSS_INTENT_COUNT | `85` |
| FINAL_PROJECT_NATIVE_INTENT_COUNT | `8` |
| FINAL_INTENT_COUNT | `93` |
| HEADLIGHT_ON_PRESENT | `NO` |
| HEADLIGHT_OFF_PRESENT | `NO` |
| HEADLIGHT_SET_MODE_CONTRACT_VALID | `YES` |
| GEAR_R_HARDCODED_TO_REVERSE_GEAR_1 | `NO` |
| RUNTIME_LOADING_ALLOWED | `NO` |
| DATASET_GENERATED | `NO` |
| MODEL_TRAINING_EXECUTED | `NO` |
| RUNTIME_MODIFIED | `NO` |
| SAFETY_GOLD_OPENED | `NO` |

## Decision table

| CHANGE_ID | change_type | approved_capability_id | human_decision | reviewer | reviewed_at |
|---|---|---|---|---|---|
| FRR-001 | ADD_INTENT | TRANSMISSION_DIFF_LOCK | **REJECT** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-002 | ADD_INTENT | BODY_HORN | **REJECT** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-003 | MERGE_INTENT | BODY_MAIN_LIGHT_MODE | **APPROVE** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-004 | MERGE_INTENT | BODY_MAIN_LIGHT_MODE | **APPROVE** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-005 | SLOT_CONTRACT_CHANGE | SEAT_LONGITUDINAL_POSITION | **APPROVE** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-006 | SLOT_CONTRACT_CHANGE | SEAT_TILT | **APPROVE** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-007 | SLOT_CONTRACT_CHANGE | SEAT_BACKREST_RECLINE | **APPROVE** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-008 | SLOT_CONTRACT_CHANGE | SEAT_HEIGHT | **APPROVE** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-009 | SLOT_CONTRACT_CHANGE | SEAT_LUMBAR_SUPPORT | **APPROVE** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-010 | MODE_CONTRACT_CHANGE | TRANSMISSION_GEAR_SELECTION | **MODIFY** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-011 | VALUE_CONTRACT_CHANGE | ADAS_CRUISE_CONTROL | **APPROVE** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |
| FRR-012 | MODE_CONTRACT_CHANGE | BODY_MAIN_LIGHT_MODE | **APPROVE** | USER_APPROVED | 2026-08-09T09:17:53+08:00 |

## Count reconciliation

```json
{
  "old_vss_intents": 87,
  "approved_additions": [],
  "rejected_addition_candidates": [
    "DIFFERENTIAL_SET_ENGAGEMENT",
    "HORN_DEACTIVATE"
  ],
  "approved_merges": [
    "HEADLIGHT_ON -> HEADLIGHT_SET_MODE",
    "HEADLIGHT_OFF -> HEADLIGHT_SET_MODE"
  ],
  "approved_contract_changes": 8,
  "formula": "87 + 0 - 2 = 85; 85 + 8 project-native = 93",
  "final_count_pending_human_review": false
}
```

## Item-level approval record

### FRR-001 — ADD_INTENT

- **human_decision:** `REJECT`
- **human_comment:** 不新增 DIFFERENTIAL_SET_ENGAGEMENT：项目不把差速锁 0~100% 中间结合度作为普通用户级语音控制能力；保留 DIFFERENTIAL_LOCK / DIFFERENTIAL_UNLOCK。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "candidate_intent": "ABSENT",
  "existing_sibling_intents": {
    "DIFFERENTIAL_LOCK": {
      "intent_id": "DIFFERENTIAL_LOCK",
      "chinese_name": "锁定差速器",
      "capability_family": "TRANSMISSION_DIFF_LOCK",
      "canonical_action": "锁定",
      "canonical_target": "差速锁",
      "control_domain": "驾驶控制",
      "risk_level": "R3",
      "risk_tags": [
        "动力传递",
        "车辆稳定"
      ],
      "allowed_areas": [
        "FRONT",
        "REAR",
        "ALL"
      ],
      "value_contract": "NONE",
      "required_slots": [],
      "optional_slots": [
        "AREA",
        "NEGATION"
      ],
      "scope_status": "IN_SCOPE",
      "capability_origin": "VSS",
      "vss_capability_ids": [
        "TRANSMISSION_DIFF_LOCK"
      ],
      "vss_relation": "DIRECT",
      "scope_authority": "HUMAN_APPROVED_VSS",
      "current_semantic_support": "NONE",
      "current_evidence_support": "NONE",
      "current_authorization_support": "NONE",
      "current_execution_support": "NONE"
    },
    "DIFFERENTIAL_UNLOCK": {
      "intent_id": "DIFFERENTIAL_UNLOCK",
      "chinese_name": "解锁差速器",
      "capability_family": "TRANSMISSION_DIFF_LOCK",
      "canonical_action": "解锁",
      "canonical_target": "差速锁",
      "control_domain": "驾驶控制",
      "risk_level": "R3",
      "risk_tags": [
        "动力传递",
        "车辆稳定"
      ],
      "allowed_areas": [
        "FRONT",
        "REAR",
        "ALL"
      ],
      "value_contract": "NONE",
      "required_slots": [],
      "optional_slots": [
        "AREA",
        "NEGATION"
      ],
      "scope_status": "IN_SCOPE",
      "capability_origin": "VSS",
      "vss_capability_ids": [
        "TRANSMISSION_DIFF_LOCK"
      ],
      "vss_relation": "DIRECT",
      "scope_authority": "HUMAN_APPROVED_VSS",
      "current_semantic_support": "NONE",
      "current_evidence_support": "NONE",
      "current_authorization_support": "NONE",
      "current_execution_support": "NONE"
    }
  },
  "coverage": "Only 0% and 100% semantic endpoints are represented as lock/unlock; intermediate engagement has no Intent."
}
```

#### proposed_definition

```json
{
  "intent_id": "DIFFERENTIAL_SET_ENGAGEMENT",
  "chinese_name": "设置差速锁结合度",
  "capability_family": "TRANSMISSION_DIFF_LOCK",
  "canonical_action": "调节",
  "canonical_target": "差速锁结合度",
  "required_slots": [
    "VALUE"
  ],
  "optional_slots": [
    "AREA",
    "NEGATION"
  ],
  "value_contract": {
    "type": "PERCENT",
    "unit": "%",
    "min": 0,
    "max": 100
  },
  "mode_contract": null,
  "direction_usage": "NOT_USED",
  "area_semantics": "FRONT / REAR / ALL; optional only if policy permits ALL as default",
  "scope_status": "IN_SCOPE_CANDIDATE_PENDING_HUMAN_APPROVAL"
}
```

#### approved_capability_id

```json
"TRANSMISSION_DIFF_LOCK"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Powertrain.Transmission.DiffLockFrontEngagement",
  "Vehicle.Powertrain.Transmission.DiffLockRearEngagement"
]
```

#### VSS datatype

```json
[
  "float"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Powertrain.Transmission.DiffLockFrontEngagement": [],
  "Vehicle.Powertrain.Transmission.DiffLockRearEngagement": []
}
```

#### unit / min / max

```json
{
  "Vehicle.Powertrain.Transmission.DiffLockFrontEngagement": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Powertrain.Transmission.DiffLockRearEngagement": {
    "unit": "percent",
    "min": 0,
    "max": 100
  }
}
```

#### 为什么当前 Registry 错

```json
"两个 VSS actuator 都是 0..100% 的连续 Engagement 写入量；现有 LOCK/UNLOCK 只能表达全结合与全分离端点。"
```

#### 为什么建议修改

```json
"新增 SET_ENGAGEMENT 能覆盖用户明确请求的中间结合度，同时保留 LOCK/UNLOCK 的离散安全语义；但量产车辆是否允许语音设置中间结合度必须由人审确认。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "把前差速锁结合度设到50%",
    "representation": {
      "intent": "DIFFERENTIAL_SET_ENGAGEMENT",
      "slots": {
        "AREA": "FRONT",
        "VALUE": "50%"
      }
    }
  },
  {
    "text": "前差速锁锁死",
    "representation": {
      "intent": "DIFFERENTIAL_LOCK",
      "slots": {
        "AREA": "FRONT"
      }
    }
  },
  {
    "text": "解除后差速锁",
    "representation": {
      "intent": "DIFFERENTIAL_UNLOCK",
      "slots": {
        "AREA": "REAR"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "intent": "DIFFERENTIAL_SET_ENGAGEMENT",
  "required_slots": [
    "VALUE"
  ],
  "optional_slots": [
    "AREA",
    "NEGATION"
  ]
}
```

#### 是否影响其它 Intent

```json
{
  "preserve": [
    "DIFFERENTIAL_LOCK",
    "DIFFERENTIAL_UNLOCK"
  ],
  "boundary": "0/100 endpoints remain distinct commands; intermediate percentage uses SET_ENGAGEMENT."
}
```

#### confidence

```json
"MEDIUM"
```

### FRR-002 — ADD_INTENT

- **human_decision:** `REJECT`
- **human_comment:** 不新增 HORN_DEACTIVATE：HORN_ACTIVATE 按瞬时/有界动作处理，停止由执行生命周期释放或超时完成；不得按 Boolean 对称强行扩展。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "candidate_intent": "ABSENT",
  "existing_sibling_intents": {
    "HORN_ACTIVATE": {
      "intent_id": "HORN_ACTIVATE",
      "chinese_name": "鸣笛",
      "capability_family": "BODY_HORN",
      "canonical_action": "执行",
      "canonical_target": "喇叭",
      "control_domain": "车身控制",
      "risk_level": "R2",
      "risk_tags": [
        "对外信号"
      ],
      "allowed_areas": [],
      "value_contract": "NONE",
      "required_slots": [],
      "optional_slots": [
        "NEGATION"
      ],
      "scope_status": "IN_SCOPE",
      "capability_origin": "VSS",
      "vss_capability_ids": [
        "BODY_HORN"
      ],
      "vss_relation": "DIRECT",
      "scope_authority": "HUMAN_APPROVED_VSS",
      "current_semantic_support": "NONE",
      "current_evidence_support": "NONE",
      "current_authorization_support": "NONE",
      "current_execution_support": "NONE"
    }
  },
  "unresolved_lifecycle": "Registry does not state whether HORN_ACTIVATE is momentary/pulsed or establishes a persistent active state."
}
```

#### proposed_definition

```json
{
  "intent_id": "HORN_DEACTIVATE",
  "chinese_name": "停止鸣笛",
  "capability_family": "BODY_HORN",
  "canonical_action": "停止",
  "canonical_target": "喇叭",
  "required_slots": [],
  "optional_slots": [
    "NEGATION"
  ],
  "value_contract": "NONE",
  "mode_contract": null,
  "direction_usage": "NOT_USED",
  "scope_status": "REVIEW_REQUIRED",
  "approval_condition": "Approve only if HORN_ACTIVATE can leave the actuator active beyond an instantaneous/policy-bounded pulse and False is an exposed user command.",
  "rejection_condition": "Reject if HORN_ACTIVATE is strictly momentary and release/timeout is internal execution behavior."
}
```

#### approved_capability_id

```json
"BODY_HORN"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Body.Horn.IsActive"
]
```

#### VSS datatype

```json
[
  "boolean"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Body.Horn.IsActive": []
}
```

#### unit / min / max

```json
{
  "Vehicle.Body.Horn.IsActive": {
    "unit": null,
    "min": null,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"VSS 明示 IsActive=True/False，但仅凭可写 Boolean 不能证明 False 是独立语音目的；当前 Registry 也没有定义 HORN_ACTIVATE 的持续时间和释放语义。"
```

#### 为什么建议修改

```json
"若系统允许持续鸣笛，‘停止鸣笛’是明确的 False write；若鸣笛始终是瞬时脉冲，则停止由执行生命周期完成，不应新增 Intent。该项必须人工裁决，不能按对称性自动新增。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "停止鸣笛",
    "representation_if_approved": {
      "intent": "HORN_DEACTIVATE",
      "slots": {}
    },
    "representation_if_rejected": "No standalone Intent; execution layer releases/times out HORN_ACTIVATE."
  },
  {
    "text": "把喇叭关掉",
    "representation_if_approved": {
      "intent": "HORN_DEACTIVATE",
      "slots": {}
    }
  },
  {
    "text": "不要鸣笛",
    "representation": {
      "intent": "HORN_ACTIVATE",
      "slots": {
        "NEGATION": true
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "intent": "HORN_DEACTIVATE",
  "required_slots": [],
  "optional_slots": [
    "NEGATION"
  ],
  "status": "REVIEW_REQUIRED"
}
```

#### 是否影响其它 Intent

```json
{
  "review": [
    "HORN_ACTIVATE"
  ],
  "boundary": "Do not reinterpret negated activation (‘不要鸣笛’) as deactivation; it remains HORN_ACTIVATE + NEGATION."
}
```

#### confidence

```json
"LOW"
```

### FRR-003 — MERGE_INTENT

- **human_decision:** `APPROVE`
- **human_comment:** 删除独立 HEADLIGHT_ON；明确主灯开关语义下，‘打开主灯/大灯’统一为 HEADLIGHT_SET_MODE + MODE=BEAM。ON 仅是受限词法别名。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "intent_id": "HEADLIGHT_ON",
  "chinese_name": "开启主灯",
  "capability_family": "BODY_MAIN_LIGHT_MODE",
  "canonical_action": "打开",
  "canonical_target": "前照灯",
  "control_domain": "车身控制",
  "risk_level": "R3",
  "risk_tags": [
    "驾驶视野",
    "对外灯光"
  ],
  "allowed_areas": [],
  "value_contract": "NONE",
  "required_slots": [],
  "optional_slots": [
    "NEGATION"
  ],
  "scope_status": "IN_SCOPE",
  "capability_origin": "VSS_AND_PROJECT",
  "vss_capability_ids": [
    "BODY_MAIN_LIGHT_MODE"
  ],
  "vss_relation": "DIRECT",
  "scope_authority": "BOTH",
  "current_semantic_support": "FULL",
  "current_evidence_support": "NONE",
  "current_authorization_support": "NONE",
  "current_execution_support": "NONE"
}
```

#### proposed_definition

```json
{
  "remove_standalone_intent": "HEADLIGHT_ON",
  "merge_into": "HEADLIGHT_SET_MODE",
  "canonical_mapping": {
    "generic_on_utterance": {
      "intent": "HEADLIGHT_SET_MODE",
      "MODE": "BEAM"
    }
  },
  "note": "BEAM is the VSS canonical enum. ‘ON’ may remain a lexical alias only; it must not be added as a source enum."
}
```

#### approved_capability_id

```json
"BODY_MAIN_LIGHT_MODE"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Body.Lights.LightSwitch"
]
```

#### VSS datatype

```json
[
  "string"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Body.Lights.LightSwitch": [
    "OFF",
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO",
    "BEAM"
  ]
}
```

#### unit / min / max

```json
{
  "Vehicle.Body.Lights.LightSwitch": {
    "unit": null,
    "min": null,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"唯一批准来源 LightSwitch 没有 ON 枚举，也没有独立主灯开关 Boolean；HEADLIGHT_ON 因此缺少一对一 VSS write semantic。"
```

#### 为什么建议修改

```json
"将通用‘打开主灯/大灯’规范化到 HEADLIGHT_SET_MODE + MODE=BEAM，保持一个枚举 actuator 对应一个参数化 Intent。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "打开主灯",
    "representation": {
      "intent": "HEADLIGHT_SET_MODE",
      "slots": {
        "MODE": "BEAM"
      }
    }
  },
  {
    "text": "把大灯设为自动",
    "representation": {
      "intent": "HEADLIGHT_SET_MODE",
      "slots": {
        "MODE": "AUTO"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "intent": "HEADLIGHT_SET_MODE",
  "required_slots": [
    "MODE"
  ],
  "canonical_mode_for_on_alias": "BEAM"
}
```

#### 是否影响其它 Intent

```json
{
  "must_not_merge": [
    "LOW_BEAM_ON",
    "LOW_BEAM_OFF",
    "HIGH_BEAM_ON",
    "HIGH_BEAM_OFF",
    "FOG_LIGHT_ON",
    "FOG_LIGHT_OFF"
  ],
  "reason": "These have independent VSS actuator paths."
}
```

#### confidence

```json
"HIGH"
```

### FRR-004 — MERGE_INTENT

- **human_decision:** `APPROVE`
- **human_comment:** 删除独立 HEADLIGHT_OFF；‘关闭主灯/大灯’统一为 HEADLIGHT_SET_MODE + MODE=OFF。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "intent_id": "HEADLIGHT_OFF",
  "chinese_name": "关闭主灯",
  "capability_family": "BODY_MAIN_LIGHT_MODE",
  "canonical_action": "关闭",
  "canonical_target": "前照灯",
  "control_domain": "车身控制",
  "risk_level": "R3",
  "risk_tags": [
    "驾驶视野",
    "环境风险"
  ],
  "allowed_areas": [],
  "value_contract": "NONE",
  "required_slots": [],
  "optional_slots": [
    "NEGATION"
  ],
  "scope_status": "IN_SCOPE",
  "capability_origin": "VSS_AND_PROJECT",
  "vss_capability_ids": [
    "BODY_MAIN_LIGHT_MODE"
  ],
  "vss_relation": "DIRECT",
  "scope_authority": "BOTH",
  "current_semantic_support": "FULL",
  "current_evidence_support": "FULL",
  "current_authorization_support": "FULL",
  "current_execution_support": "FULL"
}
```

#### proposed_definition

```json
{
  "remove_standalone_intent": "HEADLIGHT_OFF",
  "merge_into": "HEADLIGHT_SET_MODE",
  "canonical_mapping": {
    "off_utterance": {
      "intent": "HEADLIGHT_SET_MODE",
      "MODE": "OFF"
    }
  }
}
```

#### approved_capability_id

```json
"BODY_MAIN_LIGHT_MODE"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Body.Lights.LightSwitch"
]
```

#### VSS datatype

```json
[
  "string"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Body.Lights.LightSwitch": [
    "OFF",
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO",
    "BEAM"
  ]
}
```

#### unit / min / max

```json
{
  "Vehicle.Body.Lights.LightSwitch": {
    "unit": null,
    "min": null,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"OFF 是 LightSwitch 的明确枚举值，不是独立 actuator；HEADLIGHT_OFF 与 HEADLIGHT_SET_MODE(MODE=OFF) 表达同一 VSS write。"
```

#### 为什么建议修改

```json
"合并后避免同一 source/action/target/parameter contract 的双重标签，并保留 OFF 的明确安全语义。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "关闭主灯",
    "representation": {
      "intent": "HEADLIGHT_SET_MODE",
      "slots": {
        "MODE": "OFF"
      }
    }
  },
  {
    "text": "把大灯开关拨到关闭",
    "representation": {
      "intent": "HEADLIGHT_SET_MODE",
      "slots": {
        "MODE": "OFF"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "intent": "HEADLIGHT_SET_MODE",
  "required_slots": [
    "MODE"
  ],
  "MODE": "OFF"
}
```

#### 是否影响其它 Intent

```json
{
  "must_not_merge": [
    "LOW_BEAM_OFF",
    "HIGH_BEAM_OFF",
    "FOG_LIGHT_OFF"
  ],
  "reason": "Independent beam/fog actuator writes remain separate."
}
```

#### confidence

```json
"HIGH"
```

### FRR-005 — SLOT_CONTRACT_CHANGE

- **human_decision:** `APPROVE`
- **human_comment:** 采用 AREA 必填、VALUE/DIRECTION/NEGATION 可选、AT_LEAST_ONE_OF(VALUE,DIRECTION)，DIRECTION=FORWARD/BACKWARD；VALUE 与 DIRECTION 不共享同一文本 span。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "SEAT_LONGITUDINAL_SET_POSITION": {
    "intent_id": "SEAT_LONGITUDINAL_SET_POSITION",
    "chinese_name": "设置座椅前后位置",
    "capability_family": "SEAT_LONGITUDINAL_POSITION",
    "canonical_action": "调节",
    "canonical_target": "座椅前后位置",
    "control_domain": "座舱控制",
    "risk_level": "R1",
    "risk_review_status": "RISK_REVIEW_REQUIRED",
    "risk_tags": [
      "驾驶姿态"
    ],
    "allowed_areas": [
      "LEFT_FRONT",
      "RIGHT_FRONT",
      "LEFT_REAR",
      "RIGHT_REAR",
      "FRONT_ROW",
      "REAR_ROW"
    ],
    "value_contract": "SEAT_LONGITUDINAL_MM_REQUIRED",
    "required_slots": [
      "AREA",
      "VALUE"
    ],
    "optional_slots": [
      "DIRECTION",
      "NEGATION"
    ],
    "scope_status": "IN_SCOPE",
    "capability_origin": "VSS",
    "vss_capability_ids": [
      "SEAT_LONGITUDINAL_POSITION"
    ],
    "vss_relation": "DIRECT",
    "scope_authority": "HUMAN_APPROVED_VSS",
    "current_semantic_support": "NONE",
    "current_evidence_support": "NONE",
    "current_authorization_support": "NONE",
    "current_execution_support": "NONE"
  }
}
```

#### proposed_definition

```json
{
  "SEAT_LONGITUDINAL_SET_POSITION": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "FORWARD / BACKWARD",
    "value_semantics": "Position(mm) 与 Forward/Backward switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### approved_capability_id

```json
"SEAT_LONGITUDINAL_POSITION"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Position",
  "Vehicle.Cabin.Seat.Row1.Middle.IsBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.IsForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.Position",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Position",
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Position",
  "Vehicle.Cabin.Seat.Row2.Middle.IsBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.IsForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.Position",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Position"
]
```

#### VSS datatype

```json
[
  "boolean",
  "uint16"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Position": [],
  "Vehicle.Cabin.Seat.Row1.Middle.IsBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.IsForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Position": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Position": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Position": [],
  "Vehicle.Cabin.Seat.Row2.Middle.IsBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.IsForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Position": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Position": []
}
```

#### unit / min / max

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Position": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.IsBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.IsForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Position": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Position": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Position": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.IsBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.IsForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Position": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Position": {
    "unit": "mm",
    "min": 0,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"当前合同强制 VALUE、仅可选 DIRECTION；这会拒绝 VSS direction-switch 可表达的纯方向命令，也没有说明方向词与相对量如何避免重复标注。"
```

#### 为什么建议修改

```json
"保留一个参数化 Intent，不拆前/后、高/低、仰/俯；AREA 继续作为安全目标，VALUE 与 DIRECTION 至少出现一个，二者可在‘方向+幅度’句中以不同 span 共存。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "主驾座椅往前一点",
    "representation": {
      "intent": "SEAT_LONGITUDINAL_SET_POSITION",
      "slots": {
        "AREA": "LEFT_FRONT",
        "DIRECTION": "FORWARD",
        "VALUE": "RELATIVE_SMALL"
      }
    }
  },
  {
    "text": "主驾座椅前后位置调到120mm",
    "representation": {
      "intent": "SEAT_LONGITUDINAL_SET_POSITION",
      "slots": {
        "AREA": "LEFT_FRONT",
        "VALUE": "120 mm"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "SEAT_LONGITUDINAL_SET_POSITION": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "FORWARD / BACKWARD",
    "value_semantics": "Position(mm) 与 Forward/Backward switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### 是否影响其它 Intent

```json
{
  "intent_count_change": 0,
  "new_intents": [],
  "removed_intents": []
}
```

#### confidence

```json
"HIGH"
```

### FRR-006 — SLOT_CONTRACT_CHANGE

- **human_decision:** `APPROVE`
- **human_comment:** 采用 AREA 必填、VALUE/DIRECTION/NEGATION 可选、AT_LEAST_ONE_OF(VALUE,DIRECTION)，DIRECTION=FORWARD/BACKWARD。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "SEAT_TILT_SET_ANGLE": {
    "intent_id": "SEAT_TILT_SET_ANGLE",
    "chinese_name": "设置座椅整体倾角",
    "capability_family": "SEAT_TILT",
    "canonical_action": "调节",
    "canonical_target": "座椅倾角",
    "control_domain": "座舱控制",
    "risk_level": "R1",
    "risk_review_status": "RISK_REVIEW_REQUIRED",
    "risk_tags": [
      "驾驶姿态"
    ],
    "allowed_areas": [
      "LEFT_FRONT",
      "RIGHT_FRONT",
      "LEFT_REAR",
      "RIGHT_REAR",
      "FRONT_ROW",
      "REAR_ROW"
    ],
    "value_contract": "ANGLE_REQUIRED",
    "required_slots": [
      "AREA",
      "VALUE"
    ],
    "optional_slots": [
      "DIRECTION",
      "NEGATION"
    ],
    "scope_status": "IN_SCOPE",
    "capability_origin": "VSS",
    "vss_capability_ids": [
      "SEAT_TILT"
    ],
    "vss_relation": "DIRECT",
    "scope_authority": "HUMAN_APPROVED_VSS",
    "current_semantic_support": "NONE",
    "current_evidence_support": "NONE",
    "current_authorization_support": "NONE",
    "current_execution_support": "NONE"
  }
}
```

#### proposed_definition

```json
{
  "SEAT_TILT_SET_ANGLE": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "FORWARD / BACKWARD",
    "value_semantics": "Tilt(degrees) 与 TiltForward/TiltBackward switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### approved_capability_id

```json
"SEAT_TILT"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Tilt",
  "Vehicle.Cabin.Seat.Row1.Middle.IsTiltBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.IsTiltForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.Tilt",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Tilt",
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Tilt",
  "Vehicle.Cabin.Seat.Row2.Middle.IsTiltBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.IsTiltForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.Tilt",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Tilt"
]
```

#### VSS datatype

```json
[
  "boolean",
  "float"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Tilt": [],
  "Vehicle.Cabin.Seat.Row1.Middle.IsTiltBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.IsTiltForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Tilt": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Tilt": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Tilt": [],
  "Vehicle.Cabin.Seat.Row2.Middle.IsTiltBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.IsTiltForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Tilt": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Tilt": []
}
```

#### unit / min / max

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsTiltForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Tilt": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.IsTiltBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.IsTiltForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Tilt": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsTiltForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Tilt": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsTiltForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Tilt": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.IsTiltBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.IsTiltForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Tilt": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsTiltForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Tilt": {
    "unit": "degrees",
    "min": null,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"当前合同强制 VALUE、仅可选 DIRECTION；这会拒绝 VSS direction-switch 可表达的纯方向命令，也没有说明方向词与相对量如何避免重复标注。"
```

#### 为什么建议修改

```json
"保留一个参数化 Intent，不拆前/后、高/低、仰/俯；AREA 继续作为安全目标，VALUE 与 DIRECTION 至少出现一个，二者可在‘方向+幅度’句中以不同 span 共存。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "主驾座椅整体往后仰一点",
    "representation": {
      "intent": "SEAT_TILT_SET_ANGLE",
      "slots": {
        "AREA": "LEFT_FRONT",
        "DIRECTION": "BACKWARD",
        "VALUE": "RELATIVE_SMALL"
      }
    }
  },
  {
    "text": "主驾座椅整体倾角调到5度",
    "representation": {
      "intent": "SEAT_TILT_SET_ANGLE",
      "slots": {
        "AREA": "LEFT_FRONT",
        "VALUE": "5 deg"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "SEAT_TILT_SET_ANGLE": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "FORWARD / BACKWARD",
    "value_semantics": "Tilt(degrees) 与 TiltForward/TiltBackward switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### 是否影响其它 Intent

```json
{
  "intent_count_change": 0,
  "new_intents": [],
  "removed_intents": []
}
```

#### confidence

```json
"HIGH"
```

### FRR-007 — SLOT_CONTRACT_CHANGE

- **human_decision:** `APPROVE`
- **human_comment:** 采用 AREA 必填、VALUE/DIRECTION/NEGATION 可选、AT_LEAST_ONE_OF(VALUE,DIRECTION)，DIRECTION=FORWARD/BACKWARD。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "SEAT_BACKREST_SET_ANGLE": {
    "intent_id": "SEAT_BACKREST_SET_ANGLE",
    "chinese_name": "设置座椅靠背角度",
    "capability_family": "SEAT_BACKREST_RECLINE",
    "canonical_action": "调节",
    "canonical_target": "座椅靠背",
    "control_domain": "座舱控制",
    "risk_level": "R1",
    "risk_review_status": "RISK_REVIEW_REQUIRED",
    "risk_tags": [
      "驾驶姿态"
    ],
    "allowed_areas": [
      "LEFT_FRONT",
      "RIGHT_FRONT",
      "LEFT_REAR",
      "RIGHT_REAR",
      "FRONT_ROW",
      "REAR_ROW"
    ],
    "value_contract": "ANGLE_REQUIRED",
    "required_slots": [
      "AREA",
      "VALUE"
    ],
    "optional_slots": [
      "DIRECTION",
      "NEGATION"
    ],
    "scope_status": "IN_SCOPE",
    "capability_origin": "VSS",
    "vss_capability_ids": [
      "SEAT_BACKREST_RECLINE"
    ],
    "vss_relation": "DIRECT",
    "scope_authority": "HUMAN_APPROVED_VSS",
    "current_semantic_support": "NONE",
    "current_evidence_support": "NONE",
    "current_authorization_support": "NONE",
    "current_execution_support": "NONE"
  }
}
```

#### proposed_definition

```json
{
  "SEAT_BACKREST_SET_ANGLE": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "FORWARD / BACKWARD",
    "value_semantics": "Recline(degrees) 与 ReclineForward/ReclineBackward switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### approved_capability_id

```json
"SEAT_BACKREST_RECLINE"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.Recline",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.Recline",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.Recline",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.Recline",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.Recline",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineForwardSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.Recline"
]
```

#### VSS datatype

```json
[
  "boolean",
  "float"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.Recline": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.Recline": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.Recline": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.Recline": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.Recline": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineForwardSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.Recline": []
}
```

#### unit / min / max

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsReclineForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.Recline": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsReclineForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.Recline": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsReclineForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.Recline": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsReclineForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.Recline": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsReclineForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.Recline": {
    "unit": "degrees",
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineBackwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsReclineForwardSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.Recline": {
    "unit": "degrees",
    "min": null,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"当前合同强制 VALUE、仅可选 DIRECTION；这会拒绝 VSS direction-switch 可表达的纯方向命令，也没有说明方向词与相对量如何避免重复标注。"
```

#### 为什么建议修改

```json
"保留一个参数化 Intent，不拆前/后、高/低、仰/俯；AREA 继续作为安全目标，VALUE 与 DIRECTION 至少出现一个，二者可在‘方向+幅度’句中以不同 span 共存。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "主驾靠背往后放一点",
    "representation": {
      "intent": "SEAT_BACKREST_SET_ANGLE",
      "slots": {
        "AREA": "LEFT_FRONT",
        "DIRECTION": "BACKWARD",
        "VALUE": "RELATIVE_SMALL"
      }
    }
  },
  {
    "text": "主驾靠背调到110度",
    "representation": {
      "intent": "SEAT_BACKREST_SET_ANGLE",
      "slots": {
        "AREA": "LEFT_FRONT",
        "VALUE": "110 deg"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "SEAT_BACKREST_SET_ANGLE": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "FORWARD / BACKWARD",
    "value_semantics": "Recline(degrees) 与 ReclineForward/ReclineBackward switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### 是否影响其它 Intent

```json
{
  "intent_count_change": 0,
  "new_intents": [],
  "removed_intents": []
}
```

#### confidence

```json
"HIGH"
```

### FRR-008 — SLOT_CONTRACT_CHANGE

- **human_decision:** `APPROVE`
- **human_comment:** 采用 AREA 必填、VALUE/DIRECTION/NEGATION 可选、AT_LEAST_ONE_OF(VALUE,DIRECTION)，DIRECTION=UP/DOWN。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "SEAT_HEIGHT_SET_POSITION": {
    "intent_id": "SEAT_HEIGHT_SET_POSITION",
    "chinese_name": "设置座椅高度",
    "capability_family": "SEAT_HEIGHT",
    "canonical_action": "调节",
    "canonical_target": "座椅高度",
    "control_domain": "座舱控制",
    "risk_level": "R1",
    "risk_review_status": "RISK_REVIEW_REQUIRED",
    "risk_tags": [
      "驾驶姿态"
    ],
    "allowed_areas": [
      "LEFT_FRONT",
      "RIGHT_FRONT",
      "LEFT_REAR",
      "RIGHT_REAR",
      "FRONT_ROW",
      "REAR_ROW"
    ],
    "value_contract": "SEAT_HEIGHT_MM_REQUIRED",
    "required_slots": [
      "AREA",
      "VALUE"
    ],
    "optional_slots": [
      "DIRECTION",
      "NEGATION"
    ],
    "scope_status": "IN_SCOPE",
    "capability_origin": "VSS",
    "vss_capability_ids": [
      "SEAT_HEIGHT"
    ],
    "vss_relation": "DIRECT",
    "scope_authority": "HUMAN_APPROVED_VSS",
    "current_semantic_support": "NONE",
    "current_evidence_support": "NONE",
    "current_authorization_support": "NONE",
    "current_execution_support": "NONE"
  }
}
```

#### proposed_definition

```json
{
  "SEAT_HEIGHT_SET_POSITION": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "UP / DOWN",
    "value_semantics": "Height(mm) 与 Up/Down switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### approved_capability_id

```json
"SEAT_HEIGHT"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Cabin.Seat.Row1.DriverSide.Height",
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.Height",
  "Vehicle.Cabin.Seat.Row1.Middle.IsDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.IsUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Height",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Height",
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.Height",
  "Vehicle.Cabin.Seat.Row2.Middle.IsDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.IsUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Height",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsUpSwitchEngaged"
]
```

#### VSS datatype

```json
[
  "boolean",
  "uint16"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.Height": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Height": [],
  "Vehicle.Cabin.Seat.Row1.Middle.IsDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.IsUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Height": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Height": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Height": [],
  "Vehicle.Cabin.Seat.Row2.Middle.IsDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.IsUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Height": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsUpSwitchEngaged": []
}
```

#### unit / min / max

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.Height": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.IsUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Height": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.IsDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.IsUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Height": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.IsUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Height": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.IsUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Height": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.IsDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.IsUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Height": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.IsUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"当前合同强制 VALUE、仅可选 DIRECTION；这会拒绝 VSS direction-switch 可表达的纯方向命令，也没有说明方向词与相对量如何避免重复标注。"
```

#### 为什么建议修改

```json
"保留一个参数化 Intent，不拆前/后、高/低、仰/俯；AREA 继续作为安全目标，VALUE 与 DIRECTION 至少出现一个，二者可在‘方向+幅度’句中以不同 span 共存。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "主驾座椅升高一点",
    "representation": {
      "intent": "SEAT_HEIGHT_SET_POSITION",
      "slots": {
        "AREA": "LEFT_FRONT",
        "DIRECTION": "UP",
        "VALUE": "RELATIVE_SMALL"
      }
    }
  },
  {
    "text": "主驾座椅高度调到120mm",
    "representation": {
      "intent": "SEAT_HEIGHT_SET_POSITION",
      "slots": {
        "AREA": "LEFT_FRONT",
        "VALUE": "120 mm"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "SEAT_HEIGHT_SET_POSITION": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "UP / DOWN",
    "value_semantics": "Height(mm) 与 Up/Down switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### 是否影响其它 Intent

```json
{
  "intent_count_change": 0,
  "new_intents": [],
  "removed_intents": []
}
```

#### confidence

```json
"HIGH"
```

### FRR-009 — SLOT_CONTRACT_CHANGE

- **human_decision:** `APPROVE`
- **human_comment:** 腰托高度采用 UP/DOWN；腰托支撑采用 MORE/LESS，MODE 保留 TOP/MID/BOTTOM/GENERIC；两者均 AREA 必填并要求 VALUE/DIRECTION 至少一个，禁止同一 span 重复编码。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "SEAT_LUMBAR_SET_HEIGHT": {
    "intent_id": "SEAT_LUMBAR_SET_HEIGHT",
    "chinese_name": "设置座椅腰托高度",
    "capability_family": "SEAT_LUMBAR_SUPPORT",
    "canonical_action": "调节",
    "canonical_target": "座椅腰托高度",
    "control_domain": "座舱控制",
    "risk_level": "R1",
    "risk_tags": [
      "驾驶姿态"
    ],
    "allowed_areas": [
      "LEFT_FRONT",
      "RIGHT_FRONT",
      "LEFT_REAR",
      "RIGHT_REAR"
    ],
    "value_contract": "LUMBAR_HEIGHT_MM_REQUIRED",
    "required_slots": [
      "AREA",
      "VALUE"
    ],
    "optional_slots": [
      "DIRECTION",
      "NEGATION"
    ],
    "scope_status": "IN_SCOPE",
    "capability_origin": "VSS",
    "vss_capability_ids": [
      "SEAT_LUMBAR_SUPPORT"
    ],
    "vss_relation": "DIRECT",
    "scope_authority": "HUMAN_APPROVED_VSS",
    "current_semantic_support": "NONE",
    "current_evidence_support": "NONE",
    "current_authorization_support": "NONE",
    "current_execution_support": "NONE"
  },
  "SEAT_LUMBAR_SET_SUPPORT": {
    "intent_id": "SEAT_LUMBAR_SET_SUPPORT",
    "chinese_name": "设置座椅腰托支撑程度",
    "capability_family": "SEAT_LUMBAR_SUPPORT",
    "canonical_action": "调节",
    "canonical_target": "座椅腰托支撑",
    "control_domain": "座舱控制",
    "risk_level": "R1",
    "risk_tags": [
      "驾驶姿态"
    ],
    "allowed_areas": [
      "LEFT_FRONT",
      "RIGHT_FRONT",
      "LEFT_REAR",
      "RIGHT_REAR"
    ],
    "value_contract": "PERCENT_0_100_REQUIRED",
    "mode_contract": "LUMBAR_REGION",
    "required_slots": [
      "AREA",
      "VALUE"
    ],
    "optional_slots": [
      "MODE",
      "DIRECTION",
      "NEGATION"
    ],
    "scope_status": "IN_SCOPE",
    "capability_origin": "VSS",
    "vss_capability_ids": [
      "SEAT_LUMBAR_SUPPORT"
    ],
    "vss_relation": "DIRECT",
    "scope_authority": "HUMAN_APPROVED_VSS",
    "current_semantic_support": "NONE",
    "current_evidence_support": "NONE",
    "current_authorization_support": "NONE",
    "current_execution_support": "NONE"
  }
}
```

#### proposed_definition

```json
{
  "SEAT_LUMBAR_SET_HEIGHT": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "UP / DOWN for height; MORE / LESS for support",
    "value_semantics": "LumbarHeight(mm)、支撑(percent) 与 Up/Down/More/Less switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  },
  "SEAT_LUMBAR_SET_SUPPORT": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "MODE",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "UP / DOWN for height; MORE / LESS for support",
    "value_semantics": "LumbarHeight(mm)、支撑(percent) 与 Up/Down/More/Less switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### approved_capability_id

```json
"SEAT_LUMBAR_SUPPORT"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.BottomLumbarSupport",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarHeight",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarSupport",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.MidLumbarSupport",
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.TopLumbarSupport",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.BottomLumbarSupport",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLessLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarHeight",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarSupport",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.MidLumbarSupport",
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.TopLumbarSupport",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.BottomLumbarSupport",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarHeight",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarSupport",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.MidLumbarSupport",
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.TopLumbarSupport",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.BottomLumbarSupport",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarHeight",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarSupport",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.MidLumbarSupport",
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.TopLumbarSupport",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.BottomLumbarSupport",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLessLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarHeight",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarSupport",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.MidLumbarSupport",
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.TopLumbarSupport",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.BottomLumbarSupport",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarDownSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarUpSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarHeight",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarSupport",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.MidLumbarSupport",
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.TopLumbarSupport"
]
```

#### VSS datatype

```json
[
  "boolean",
  "float",
  "uint8"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.BottomLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarHeight": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.MidLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.TopLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.BottomLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLessLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarHeight": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.MidLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.TopLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.BottomLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarHeight": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.MidLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.TopLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.BottomLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarHeight": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.MidLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.TopLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.BottomLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLessLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarHeight": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.MidLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.TopLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.BottomLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarDownSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarUpSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarHeight": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.MidLumbarSupport": [],
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.TopLumbarSupport": []
}
```

#### unit / min / max

```json
{
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.BottomLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsLumbarUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarHeight": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.LumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.MidLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.DriverSide.Backrest.TopLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.BottomLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLessLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsLumbarUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarHeight": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.LumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.MidLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.Middle.Backrest.TopLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.BottomLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsLumbarUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarHeight": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.LumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.MidLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row1.PassengerSide.Backrest.TopLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.BottomLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLessLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsLumbarUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.IsMoreLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarHeight": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.LumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.MidLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.DriverSide.Backrest.TopLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.BottomLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLessLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsLumbarUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.IsMoreLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarHeight": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.LumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.MidLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.Middle.Backrest.TopLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.BottomLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLessLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarDownSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsLumbarUpSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.IsMoreLumbarSupportSwitchEngaged": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarHeight": {
    "unit": "mm",
    "min": 0,
    "max": null
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.LumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.MidLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  },
  "Vehicle.Cabin.Seat.Row2.PassengerSide.Backrest.TopLumbarSupport": {
    "unit": "percent",
    "min": 0,
    "max": 100
  }
}
```

#### 为什么当前 Registry 错

```json
"当前合同强制 VALUE、仅可选 DIRECTION；这会拒绝 VSS direction-switch 可表达的纯方向命令，也没有说明方向词与相对量如何避免重复标注。"
```

#### 为什么建议修改

```json
"保留一个参数化 Intent，不拆前/后、高/低、仰/俯；AREA 继续作为安全目标，VALUE 与 DIRECTION 至少出现一个，二者可在‘方向+幅度’句中以不同 span 共存。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "主驾腰托往上调一点",
    "representation": {
      "intent": "SEAT_LUMBAR_SET_HEIGHT",
      "slots": {
        "AREA": "LEFT_FRONT",
        "DIRECTION": "UP",
        "VALUE": "RELATIVE_SMALL"
      }
    }
  },
  {
    "text": "主驾腰托高度调到40mm",
    "representation": {
      "intent": "SEAT_LUMBAR_SET_HEIGHT",
      "slots": {
        "AREA": "LEFT_FRONT",
        "VALUE": "40 mm"
      }
    }
  },
  {
    "text": "主驾腰托再顶一点",
    "representation": {
      "intent": "SEAT_LUMBAR_SET_SUPPORT",
      "slots": {
        "AREA": "LEFT_FRONT",
        "MODE": "GENERIC",
        "DIRECTION": "MORE",
        "VALUE": "RELATIVE_SMALL"
      }
    }
  },
  {
    "text": "主驾上部腰托支撑设为60%",
    "representation": {
      "intent": "SEAT_LUMBAR_SET_SUPPORT",
      "slots": {
        "AREA": "LEFT_FRONT",
        "MODE": "TOP",
        "VALUE": "60%"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "SEAT_LUMBAR_SET_HEIGHT": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "UP / DOWN for height; MORE / LESS for support",
    "value_semantics": "LumbarHeight(mm)、支撑(percent) 与 Up/Down/More/Less switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  },
  "SEAT_LUMBAR_SET_SUPPORT": {
    "required_slots": [
      "AREA"
    ],
    "optional_slots": [
      "VALUE",
      "DIRECTION",
      "MODE",
      "NEGATION"
    ],
    "conditional_requirement": "AT_LEAST_ONE_OF(VALUE,DIRECTION)",
    "direction_usage": "OPTIONAL",
    "direction_values": "UP / DOWN for height; MORE / LESS for support",
    "value_semantics": "LumbarHeight(mm)、支撑(percent) 与 Up/Down/More/Less switch",
    "non_duplication_rule": "Direction words encode only DIRECTION; VALUE encodes target/magnitude/relative step. A span must not be labeled as both.",
    "unqualified_area_policy": "If AREA is absent (e.g. ‘座椅往前一点’), NLU may parse direction/value but validation must request clarification unless a separately approved deterministic driver-seat default exists."
  }
}
```

#### 是否影响其它 Intent

```json
{
  "intent_count_change": 0,
  "new_intents": [],
  "removed_intents": []
}
```

#### confidence

```json
"HIGH"
```

### FRR-010 — MODE_CONTRACT_CHANGE

- **human_decision:** `MODIFY`
- **human_comment:** GEAR_SET 保持 MODE 必填、NEGATION 可选且 VALUE 不用于目标挡位。P/N/D、FORWARD_GEAR_N、REVERSE_GEAR_N 为 canonical 类别；R挡/倒挡仅作词法识别，物理 gear code 由 VehicleCapabilityMapping 做车型级映射与校验，通用 Registry 禁止写死 R -> REVERSE_GEAR_1。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### human_modified_definition

```json
{
  "intent_id": "GEAR_SET",
  "required_slots": [
    "MODE"
  ],
  "optional_slots": [
    "NEGATION"
  ],
  "value_slot_usage": "NOT_USED_FOR_TARGET_GEAR",
  "canonical_modes": [
    "P",
    "N",
    "D",
    "FORWARD_GEAR_N",
    "REVERSE_GEAR_N"
  ],
  "lexical_aliases": {
    "R挡": "VEHICLE_SPECIFIC_REVERSE_GEAR",
    "倒挡": "VEHICLE_SPECIFIC_REVERSE_GEAR"
  },
  "physical_mapping_authority": "VehicleCapabilityMapping",
  "vehicle_specific_validation_required": true,
  "prohibited_generic_mapping": "R -> REVERSE_GEAR_1"
}
```

#### current_definition

```json
{
  "intent": {
    "intent_id": "GEAR_SET",
    "chinese_name": "设置目标挡位",
    "capability_family": "TRANSMISSION_GEAR_SELECTION",
    "canonical_action": "切换",
    "canonical_target": "挡位",
    "control_domain": "驾驶控制",
    "risk_level": "R3",
    "risk_tags": [
      "动力传递",
      "挡位安全"
    ],
    "allowed_areas": [],
    "value_contract": "NONE",
    "mode_contract": "GEAR",
    "required_slots": [
      "MODE"
    ],
    "optional_slots": [
      "NEGATION"
    ],
    "scope_status": "IN_SCOPE",
    "capability_origin": "VSS",
    "vss_capability_ids": [
      "TRANSMISSION_GEAR_SELECTION"
    ],
    "vss_relation": "DIRECT",
    "scope_authority": "HUMAN_APPROVED_VSS",
    "current_semantic_support": "NONE",
    "current_evidence_support": "NONE",
    "current_authorization_support": "NONE",
    "current_execution_support": "NONE"
  },
  "current_mode_contract": [
    "P",
    "R",
    "N",
    "D"
  ]
}
```

#### proposed_definition

```json
{
  "intent_id": "GEAR_SET",
  "required_slots": [
    "MODE"
  ],
  "optional_slots": [
    "NEGATION"
  ],
  "direction_usage": "NOT_USED",
  "value_slot_usage": "NOT_USED for target gear selection",
  "mode_contract": {
    "canonical_categories": {
      "N": {
        "vss_code": 0
      },
      "P": {
        "vss_code": 126
      },
      "D": {
        "vss_code": 127
      },
      "FORWARD_GEAR_N": {
        "vss_code_rule": "positive integer n; vehicle capability must support n"
      },
      "REVERSE_GEAR_N": {
        "vss_code_rule": "negative integer -n; vehicle capability must support n"
      },
      "R": {
        "alias_for": "REVERSE_GEAR_1 unless vehicle mapping says otherwise"
      }
    },
    "source_allowed_array": [],
    "validation_note": "VSS describes codes in text rather than an allowed enum; supported numeric gears are vehicle-specific and must be validated outside NLU."
  }
}
```

#### approved_capability_id

```json
"TRANSMISSION_GEAR_SELECTION"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Powertrain.Transmission.SelectedGear"
]
```

#### VSS datatype

```json
[
  "int8"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Powertrain.Transmission.SelectedGear": []
}
```

#### unit / min / max

```json
{
  "Vehicle.Powertrain.Transmission.SelectedGear": {
    "unit": null,
    "min": null,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"当前 MODE 仅列 P/R/N/D，遗漏 VSS 描述中的明确正整数前进挡和负整数倒挡；把‘2挡’标为普通 VALUE 又会丢失离散挡位语义。"
```

#### 为什么建议修改

```json
"GEAR_SET 保持一个 Intent，MODE 必填；P/R/N/D 与具体整数挡都是离散目标模式。VALUE 不用于挡位目标，避免把数值挡误作连续量。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "挂D挡",
    "representation": {
      "intent": "GEAR_SET",
      "slots": {
        "MODE": "D"
      }
    }
  },
  {
    "text": "切到2挡",
    "representation": {
      "intent": "GEAR_SET",
      "slots": {
        "MODE": "FORWARD_GEAR_2"
      }
    }
  },
  {
    "text": "挂倒一挡",
    "representation": {
      "intent": "GEAR_SET",
      "slots": {
        "MODE": "REVERSE_GEAR_1"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "intent": "GEAR_SET",
  "required_slots": [
    "MODE"
  ],
  "optional_slots": [
    "NEGATION"
  ]
}
```

#### 是否影响其它 Intent

```json
{
  "intent_count_change": 0,
  "must_not_create": [
    "GEAR_P",
    "GEAR_D",
    "GEAR_R",
    "GEAR_1",
    "GEAR_2"
  ]
}
```

#### confidence

```json
"MEDIUM"
```

### FRR-011 — VALUE_CONTRACT_CHANGE

- **human_decision:** `APPROVE`
- **human_comment:** CRUISE_SET_GAP 采用 VALUE XOR MODE；VALUE 表达米制或远/近相对量，MODE 表达 LEVEL_N。两者仅在确定性一致时允许共同出现。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "intent": {
    "intent_id": "CRUISE_SET_GAP",
    "chinese_name": "设置巡航跟车距离",
    "capability_family": "ADAS_CRUISE_CONTROL",
    "canonical_action": "设置",
    "canonical_target": "巡航跟车距离",
    "control_domain": "驾驶控制",
    "risk_level": "R3",
    "risk_tags": [
      "巡航控制",
      "跟车安全"
    ],
    "allowed_areas": [],
    "value_contract": "FOLLOWING_GAP_REQUIRED",
    "required_slots": [
      "VALUE"
    ],
    "optional_slots": [
      "MODE",
      "NEGATION"
    ],
    "scope_status": "IN_SCOPE",
    "capability_origin": "VSS_AND_PROJECT",
    "vss_capability_ids": [
      "ADAS_CRUISE_CONTROL"
    ],
    "vss_relation": "DIRECT",
    "scope_authority": "BOTH",
    "current_semantic_support": "NONE",
    "current_evidence_support": "NONE",
    "current_authorization_support": "NONE",
    "current_execution_support": "NONE"
  },
  "current_value_contract": {
    "allowed": true,
    "required": true,
    "type": "FOLLOWING_GAP",
    "canonical_unit": "policy_defined",
    "valid_range": {
      "min_ref": "vehicle_capability_limits.min_following_gap",
      "max_ref": "vehicle_capability_limits.max_following_gap"
    },
    "enum_values": [
      "LEVEL_1",
      "LEVEL_2",
      "LEVEL_3",
      "LEVEL_4"
    ]
  },
  "current_issue": "required VALUE + optional MODE; hard-coded LEVEL_1..4"
}
```

#### proposed_definition

```json
{
  "intent_id": "CRUISE_SET_GAP",
  "required_slots": [],
  "optional_slots": [
    "VALUE",
    "MODE",
    "NEGATION"
  ],
  "conditional_requirement": "EXACTLY_ONE_PRIMARY_REPRESENTATION_OF(VALUE,MODE); both may be accepted only when redundant values are deterministically consistent",
  "direction_usage": "NOT_USED; relative farther/closer is encoded as a relative VALUE",
  "value_contract": {
    "absolute_distance": {
      "type": "LENGTH",
      "unit": "m",
      "min": 0,
      "source": "AdaptiveDistanceSet"
    },
    "relative_adjustment": {
      "type": "RELATIVE_GAP_DELTA",
      "canonical_values": [
        "FARTHER",
        "CLOSER",
        "RELATIVE_STEP"
      ]
    }
  },
  "mode_contract": {
    "type": "VEHICLE_SPECIFIC_INTERVAL_LEVEL",
    "source": "AdaptiveIntervalSet",
    "allowed_levels": "Vehicle-specific; VSS description says commonly 1-5 but does not provide allowed/min/max."
  }
}
```

#### approved_capability_id

```json
"ADAS_CRUISE_CONTROL"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.ADAS.CruiseControl.AdaptiveDistanceSet",
  "Vehicle.ADAS.CruiseControl.AdaptiveIntervalSet",
  "Vehicle.ADAS.CruiseControl.IsActive",
  "Vehicle.ADAS.CruiseControl.IsAdaptive",
  "Vehicle.ADAS.CruiseControl.IsEnabled",
  "Vehicle.ADAS.CruiseControl.SpeedSet"
]
```

#### VSS datatype

```json
[
  "boolean",
  "float",
  "uint8"
]
```

#### allowed values / enum

```json
{
  "Vehicle.ADAS.CruiseControl.AdaptiveDistanceSet": [],
  "Vehicle.ADAS.CruiseControl.AdaptiveIntervalSet": [],
  "Vehicle.ADAS.CruiseControl.IsActive": [],
  "Vehicle.ADAS.CruiseControl.IsAdaptive": [],
  "Vehicle.ADAS.CruiseControl.IsEnabled": [],
  "Vehicle.ADAS.CruiseControl.SpeedSet": []
}
```

#### unit / min / max

```json
{
  "Vehicle.ADAS.CruiseControl.AdaptiveDistanceSet": {
    "unit": "m",
    "min": 0,
    "max": null
  },
  "Vehicle.ADAS.CruiseControl.AdaptiveIntervalSet": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.ADAS.CruiseControl.IsActive": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.ADAS.CruiseControl.IsAdaptive": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.ADAS.CruiseControl.IsEnabled": {
    "unit": null,
    "min": null,
    "max": null
  },
  "Vehicle.ADAS.CruiseControl.SpeedSet": {
    "unit": "km/h",
    "min": null,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"当前合同把 VALUE 设为必填、MODE 仅可选，却又把 LEVEL_1..4 塞入 VALUE enum；它混淆米制距离与离散间隔等级，并无 VSS 依据地固定为四级。"
```

#### 为什么建议修改

```json
"同一 CRUISE_SET_GAP Intent 保留两种互斥主表达：米制/相对变化走 VALUE，明确等级走 MODE。自然语言‘远一点’不是模式目标，应为相对 VALUE。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "跟车距离设为30米",
    "representation": {
      "intent": "CRUISE_SET_GAP",
      "slots": {
        "VALUE": "30 m"
      }
    }
  },
  {
    "text": "跟车距离调到三级",
    "representation": {
      "intent": "CRUISE_SET_GAP",
      "slots": {
        "MODE": "LEVEL_3"
      }
    }
  },
  {
    "text": "跟远一点",
    "representation": {
      "intent": "CRUISE_SET_GAP",
      "slots": {
        "VALUE": "FARTHER/RELATIVE_STEP"
      }
    }
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "intent": "CRUISE_SET_GAP",
  "required_constraint": "VALUE XOR MODE",
  "optional_slots": [
    "NEGATION"
  ]
}
```

#### 是否影响其它 Intent

```json
{
  "intent_count_change": 0,
  "preserve": [
    "CRUISE_ENABLE",
    "CRUISE_DISABLE",
    "CRUISE_SET_SPEED"
  ]
}
```

#### confidence

```json
"HIGH"
```

### FRR-012 — MODE_CONTRACT_CHANGE

- **human_decision:** `APPROVE`
- **human_comment:** HEADLIGHT_SET_MODE 的 MODE 必填，canonical 五值为 OFF/POSITION/DAYTIME_RUNNING_LIGHTS/AUTO/BEAM；ON 仅是明确主灯开关语义下 BEAM 的受限别名，LOW/HIGH/FOG intents 保持独立。
- **reviewer:** `USER_APPROVED`
- **reviewed_at:** `2026-08-09T09:17:53+08:00`
- **review_status:** `RESOLVED`

#### current_definition

```json
{
  "intent": {
    "intent_id": "HEADLIGHT_SET_MODE",
    "chinese_name": "设置主灯模式",
    "capability_family": "BODY_MAIN_LIGHT_MODE",
    "canonical_action": "切换",
    "canonical_target": "前照灯模式",
    "control_domain": "车身控制",
    "risk_level": "R3",
    "risk_tags": [
      "驾驶视野",
      "对外灯光"
    ],
    "allowed_areas": [],
    "value_contract": "NONE",
    "mode_contract": "HEADLIGHT",
    "required_slots": [
      "MODE"
    ],
    "optional_slots": [
      "NEGATION"
    ],
    "scope_status": "IN_SCOPE",
    "capability_origin": "VSS_AND_PROJECT",
    "vss_capability_ids": [
      "BODY_MAIN_LIGHT_MODE"
    ],
    "vss_relation": "DIRECT",
    "scope_authority": "BOTH",
    "current_semantic_support": "NONE",
    "current_evidence_support": "NONE",
    "current_authorization_support": "NONE",
    "current_execution_support": "NONE"
  },
  "current_mode_contract": [
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO",
    "BEAM"
  ],
  "missing_source_enum": "OFF"
}
```

#### proposed_definition

```json
{
  "intent_id": "HEADLIGHT_SET_MODE",
  "required_slots": [
    "MODE"
  ],
  "optional_slots": [
    "NEGATION"
  ],
  "mode_contract": [
    "OFF",
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO",
    "BEAM"
  ],
  "lexical_aliases": {
    "ON": "BEAM only when utterance clearly refers to the main light switch"
  },
  "excluded_from_contract": [
    "LOW_BEAM",
    "HIGH_BEAM",
    "FOG_FRONT",
    "FOG_REAR"
  ],
  "exclusion_reason": "Low/high/fog beams have separate approved capability families and separate VSS actuator paths."
}
```

#### approved_capability_id

```json
"BODY_MAIN_LIGHT_MODE"
```

#### 所有相关 VSS actuator path

```json
[
  "Vehicle.Body.Lights.LightSwitch"
]
```

#### VSS datatype

```json
[
  "string"
]
```

#### allowed values / enum

```json
{
  "Vehicle.Body.Lights.LightSwitch": [
    "OFF",
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO",
    "BEAM"
  ]
}
```

#### unit / min / max

```json
{
  "Vehicle.Body.Lights.LightSwitch": {
    "unit": null,
    "min": null,
    "max": null
  }
}
```

#### 为什么当前 Registry 错

```json
"当前 HEADLIGHT mode_contract 遗漏 LightSwitch 明示的 OFF；同时独立 HEADLIGHT_ON/OFF 造成同一枚举 source 的标签分裂。"
```

#### 为什么建议修改

```json
"采用完整、逐字来自 VSS 的五值 mode contract；ON 仅作为 BEAM 的受限词法别名，不把独立近光/远光/雾灯 actuator 吞入主灯模式。"
```

#### 修改后用户自然语言示例

```json
[
  {
    "text": "把主灯关掉",
    "representation": {
      "intent": "HEADLIGHT_SET_MODE",
      "slots": {
        "MODE": "OFF"
      }
    }
  },
  {
    "text": "主灯调成自动",
    "representation": {
      "intent": "HEADLIGHT_SET_MODE",
      "slots": {
        "MODE": "AUTO"
      }
    }
  },
  {
    "text": "打开主灯",
    "representation": {
      "intent": "HEADLIGHT_SET_MODE",
      "slots": {
        "MODE": "BEAM"
      },
      "note": "Only when main-switch reference is unambiguous."
    }
  },
  {
    "text": "打开近光灯",
    "representation": {
      "intent": "LOW_BEAM_ON",
      "slots": {}
    },
    "note": "Not HEADLIGHT_SET_MODE."
  }
]
```

#### 修改后最终 intent / slot 表达

```json
{
  "intent": "HEADLIGHT_SET_MODE",
  "required_slots": [
    "MODE"
  ],
  "MODE": [
    "OFF",
    "POSITION",
    "DAYTIME_RUNNING_LIGHTS",
    "AUTO",
    "BEAM"
  ]
}
```

#### 是否影响其它 Intent

```json
{
  "merge_in": [
    "HEADLIGHT_ON",
    "HEADLIGHT_OFF"
  ],
  "must_not_merge": [
    "LOW_BEAM_ON",
    "LOW_BEAM_OFF",
    "HIGH_BEAM_ON",
    "HIGH_BEAM_OFF",
    "FOG_LIGHT_ON",
    "FOG_LIGHT_OFF"
  ]
}
```

#### confidence

```json
"HIGH"
```

## Prohibited actions confirmation

```json
{
  "registry_modified": true,
  "training_data_generated": false,
  "split_modified": false,
  "model_trained": false,
  "validator_implemented": false,
  "runtime_modified": false,
  "http_contract_modified": false,
  "safety_gold_opened": false
}
```
