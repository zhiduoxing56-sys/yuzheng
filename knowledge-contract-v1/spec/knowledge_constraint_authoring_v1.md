# 知识约束节点填写规范（knowledge-constraint-authoring-v1）

本文档规定"语证知识库"中知识约束节点的字段含义与填写规则。所有值必须来自冻结注册表（见 `knowledge_contract_freeze_v1.json`），禁止自行创造字段、同义词、单位或阈值。

## 1. 节点结构

每个节点是一个 JSON 对象，合法字段如下：

| 字段 | 必填 | 说明 |
|---|---|---|
| node_id | 是 | 形如 `知识.灯光.夜间关闭限制.001` |
| node_type | 是 | `安全知识` / `规范安全知识` / `应急驾驶指导知识` |
| title | 是 | 节点标题 |
| source | 是 | 来源：source_file / chapter / clause |
| command | 是 | 该节点约束的车控指令（见 §2） |
| evidence | 是 | 判断条件所需证据（见 §3） |
| when | 是 | 可执行条件（见 §4） |
| effect | 是 | 条件成立/不成立的效果（见 §5） |

## 2. command 填写规则

必须与 `intent_registry_unified_v1.yaml` 完全一致，且只允许 FORMAL 意图（`runtime_identity: FORMAL`）。KNOWN_NON_EXECUTABLE 意图禁止建立可执行约束。

### 2.1 字段取值来源

| 字段 | 取值来源 |
|---|---|
| intent_id | 正式意图注册表 |
| action | 当前 intent 的 `canonical_action` |
| target | 当前 intent 的 `canonical_target` |
| area | 当前 intent 的 `allowed_areas`（或 `ANY`） |
| mode | 当前 intent 引用的 `mode_contract`（或 `ANY`） |
| value | 当前 intent 引用的 `value_contract`（或 `ANY`） |
| direction | 当前 intent 引用的 `direction_contract`（或 `ANY`） |
| control_attribute | 当前 intent 的 `control_attribute` |

### 2.2 核心校验：以 intent_id 为主键

以下合法（同属 HEADLIGHT_SET_MODE）：

```yaml
intent_id: HEADLIGHT_SET_MODE
action: SWITCH_MODE
target: HEADLIGHT
mode: OFF
```

以下必须拒绝（跨意图拼装）：

```yaml
intent_id: HEADLIGHT_SET_MODE
action: UNLOCK
target: DOOR
```

### 2.3 area

只能填 `area_catalog` 中属于该 intent `allowed_areas` 的值：

```text
LEFT_FRONT RIGHT_FRONT LEFT_REAR RIGHT_REAR MIDDLE_FRONT MIDDLE_REAR
FRONT_ROW REAR_ROW LEFT_SIDE RIGHT_SIDE FRONT REAR ALL
```

不限制区域写 `ANY`。禁止 `驾驶位`、`左边` 等自然语言。

### 2.4 mode / value / direction

由各 intent 的 `mode_contract` / `value_contract` / `direction_contract` 决定，禁止跨 intent 引用。不限制时写 `ANY`。

## 3. evidence 填写规则

上下文只能通过 `evidence.type + evidence.field` 表达，禁止自造 `context`、`weather_context` 等字段。

- `type` 必须来自 `evidence_type_catalog_v1.yaml` 的 `evidence_types`（32 个 canonical types）
- `field` 必须来自 `evidence_runtime_mapping_v1.yaml` 中该 type 的合法字段
- 字段必须与类型对应

正确：

```yaml
evidence:
  speed:
    type: VEHICLE_SPEED
    field: value
  light:
    type: ENVIRONMENT_CONDITIONS
    field: ambient_illumination
  gear:
    type: GEAR_STATE
    field: current_gear
```

错误：

```yaml
type: GEAR_STATE
field: ambient_illumination
```

标量证据统一用 `field: value`；对象型证据使用其内部字段（如 `DOOR_STATE.field: is_open`）。

## 4. when 填写规则

第一版只允许：

```yaml
when:
  all:
    - field: speed
      op: GT
      value: 0
  any:
    - field: weather
      op: IN
      value: [RAIN, HEAVY_RAIN]
```

`all` 与 `any` 至少一个存在（可同时存在，all 与 any 均须成立）。

### 4.1 运算符与数据类型对应

| 数据类型 | 允许运算符 |
|---|---|
| number | `EQ NE GT GTE LT LTE` |
| string/enum | `EQ NE IN NOT_IN` |
| boolean | `EQ NE` |

禁止自由文本（`高速行驶`）与脚本表达式（`speed > 0 and light < 20`）。

## 5. effect 填写规则

只允许 `ALLOW / BLOCK / REVIEW`：

```yaml
effect:
  then: BLOCK
  else: ALLOW
  reason_code: LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED
  reason: 夜间行驶中禁止关闭前照灯
```

含义：
- command 不匹配：节点不适用
- command 匹配且 when 成立：使用 `then`
- command 匹配且 when 不成立：使用 `else`
- 证据缺失/过期/篡改/冲突：由统一证据安全机制处理，不在节点内重复写

## 6. 阈值来源原则（最重要）

**"有值"必须有值的来源**，分两类：

1. **规范阈值**（法规/标准明确给出）→ 直接写入 when 的 value
   - 例：`VISIBILITY < 200`、`SPEED <= 60`（实施条例第81条）
2. **工程判定阈值**（为判断抽象状态而设）→ 进入 Evidence Registry / 状态解析器，**不写入知识节点**
   - 例：`VEHICLE_MOTION_STATE=MOVING` 由 `moving_speed_threshold_kmh: 0.5` 校准得出

禁止把工程校准值伪装成法规值写入节点。

## 7. 完整示例（合法）

```yaml
node_id: 知识.灯光.夜间关闭限制.001
node_type: 安全知识
title: 夜间行驶中禁止关闭前照灯
source:
  source_file: GB 7258-2017
  chapter: 第8章
  clause: 8.2.1
command:
  intent_id: HEADLIGHT_SET_MODE
  action: SWITCH_MODE
  target: HEADLIGHT
  area: ANY
  mode: OFF
evidence:
  speed:
    type: VEHICLE_SPEED
    field: value
  light:
    type: ENVIRONMENT_CONDITIONS
    field: ambient_illumination
when:
  all:
    - field: speed
      op: GT
      value: 0
    - field: light
      op: LT
      value: 20
effect:
  then: BLOCK
  else: ALLOW
  reason_code: LOW_LIGHT_HEADLIGHT_OFF_PROHIBITED
  reason: 夜间行驶中禁止关闭前照灯
```
