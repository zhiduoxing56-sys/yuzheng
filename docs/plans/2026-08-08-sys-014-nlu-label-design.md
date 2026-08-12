# SYS-014 轻量本地 NLU 标签空间与标注规范设计

> 状态：Stage 3C POC7 V1 FROZEN / OFFLINE / NOT RUNTIME LOADED  
> 日期：2026-08-08  
> 阶段：第二阶段，仅设计；禁止训练、下载模型或修改现有运行时契约。

## 设计依据与不可覆盖边界

- 人工权威输入：`新语证_VSS6.0_113能力筛选表_v0.2.xlsx`，sheet `113能力筛选`，范围 `A1:I45`。
- 工作簿实际包含 44 个 VSS capability family；全部标记 `HUMAN_APPROVED`。
- 原 113 个 family 中未出现在最新工作簿的 69 个标记 `HUMAN_REJECTED`，本设计不恢复它们。
- `当前对齐` 只描述实现状态，不用于否决能力范围。
- 最终候选来源：`HUMAN_APPROVED_VSS_CAPABILITIES UNION PROJECT_NATIVE_CAPABILITIES`。
- 公开 `SemanticFrame`、HTTP/WS、数据库、Audit hash、Review、Interpreter、Authorization、Execution、Bayesian/Causal 和 HNSW 均不修改。
- 作品报告 DOCX 已做结构化文本核对；本机缺少 LibreOffice/soffice，未进行文档页面渲染核验。

## A. 标签设计原则

1. 主分类标签是 `ATOMIC_CONTROL_INTENT`，禁止独立 action classifier 与 target classifier 拼接。
2. 不同控制目的或不同安全/证据/授权/执行语义必须拆分，例如 OPEN/CLOSE、LOCK/UNLOCK、ENABLE/DISABLE。
3. AREA、连续数值、单位、模式和等级是参数，不进入 Intent ID。
4. 每个 Intent 归属稳定 `capability_family`，用于 VSS 追溯、统计、规则审计和数据集分组。
5. NLU 只负责理解；risk、canonical mapping、value range、runtime support 和 authorization 均由确定性组件决定。
6. 模型必须允许 abstention，不能用 softmax 最大类强制分类。
7. 运行时只允许独立本地轻量 encoder；禁止外部 LLM。
8. 完整 Registry 与训练阶段分离：Stage 2.1 加固后全量设计 95 类；Stage 3B.1 完成语义收尾后，PoC 构建 7 个代表 Intent 的离线候选数据。

## B. 完整 Intent Registry 草案

完整字段级 Registry 位于 `data/nlu/spec/intent_registry_draft.yaml`。实际结果：

- Intent：95。
- capability family：49，其中 44 个 VSS family、5 个项目原生聚合 family。
- VSS-derived Intent：87；其中 VSS-only 68、VSS_AND_PROJECT 19。
- PROJECT_NATIVE Intent：8。
- IN_SCOPE Intent：95。
- PENDING_SCOPE Intent：0。
- LEGACY_TEST_ONLY / OUT_OF_SCOPE Intent：1（DISPLAY_OFF，不计入上述正式 Registry）。
- HUMAN_REJECTED VSS family：69，不进入 Registry。

Stage 2.1 相对上一版的标签变更：新增 `SEAT_LUMBAR_SET_HEIGHT`、`SEAT_LUMBAR_SET_SUPPORT`、`STEERING_WHEEL_SET_EXTENSION`、`STEERING_WHEEL_SET_TILT`；移除两个含混标签 `SEAT_LUMBAR_SET_POSITION`、`STEERING_WHEEL_SET_POSITION`；`DISPLAY_OFF` 移至 legacy/out-of-scope。不存在仅改名而语义不变的 Intent。

### Family → Intent

| capability family | 拆分后的 Intent |
|---|---|
| BODY_MIRROR_HEATING | MIRROR_HEATING_ON, MIRROR_HEATING_OFF |
| BODY_MIRROR_ADJUSTMENT_LOCK | MIRROR_ADJUSTMENT_LOCK, MIRROR_ADJUSTMENT_UNLOCK |
| SEAT_LONGITUDINAL_POSITION | SEAT_LONGITUDINAL_SET_POSITION |
| SEAT_TILT | SEAT_TILT_SET_ANGLE |
| SEAT_BACKREST_RECLINE | SEAT_BACKREST_SET_ANGLE |
| SEAT_HEIGHT | SEAT_HEIGHT_SET_POSITION |
| SEAT_LUMBAR_SUPPORT | SEAT_LUMBAR_SET_HEIGHT, SEAT_LUMBAR_SET_SUPPORT |
| CHASSIS_STEERING_WHEEL_POSITION | STEERING_WHEEL_SET_EXTENSION, STEERING_WHEEL_SET_TILT |
| CABIN_HVAC_DEFROST | DEFROST_ON, DEFROST_OFF |
| BODY_WINDSHIELD_HEATING | WINDSHIELD_HEATING_ON, WINDSHIELD_HEATING_OFF |
| ADAS_ABS_ENABLE | ABS_ENABLE, ABS_DISABLE |
| ADAS_TCS_ENABLE | TCS_ENABLE, TCS_DISABLE |
| ADAS_EBD_ENABLE | EBD_ENABLE, EBD_DISABLE |
| ADAS_EBA_ENABLE | EBA_ENABLE, EBA_DISABLE |
| ADAS_ESC_ENABLE | ESC_ENABLE, ESC_DISABLE |
| BODY_TRUNK_OPENING | TRUNK_OPEN, TRUNK_CLOSE, TRUNK_SET_POSITION |
| BODY_TRUNK_LOCK | TRUNK_LOCK, TRUNK_UNLOCK |
| BODY_HOOD | HOOD_OPEN, HOOD_CLOSE, HOOD_SET_POSITION |
| TRANSMISSION_LOW_RANGE | LOW_RANGE_ENABLE, LOW_RANGE_DISABLE |
| TRANSMISSION_TORQUE_DISTRIBUTION | TORQUE_DISTRIBUTION_SET |
| TRANSMISSION_PERFORMANCE_MODE | TRANSMISSION_PERFORMANCE_MODE_SET |
| TRANSMISSION_DIFF_LOCK | DIFFERENTIAL_LOCK, DIFFERENTIAL_UNLOCK |
| TRANSMISSION_GEAR_SELECTION | GEAR_SET |
| TRANSMISSION_ELECTRICAL_POWERTRAIN_ENGAGEMENT | ELECTRIC_POWERTRAIN_ENGAGE, ELECTRIC_POWERTRAIN_DISENGAGE |
| TRANSMISSION_CLUTCH | CLUTCH_SET_ENGAGEMENT |
| TRANSMISSION_GEAR_CHANGE_MODE | GEAR_CHANGE_MODE_SET |
| TRANSMISSION_PARK_LOCK | PARK_LOCK, PARK_UNLOCK |
| BODY_HORN | HORN_ACTIVATE |
| BODY_MIRROR_FOLD | MIRROR_FOLD, MIRROR_UNFOLD |
| BODY_MIRROR_ADJUSTMENT | MIRROR_SET_ANGLE |
| CABIN_SUNROOF | SUNROOF_OPEN, SUNROOF_CLOSE, SUNROOF_SET_TILT |
| ADAS_CRUISE_CONTROL | CRUISE_ENABLE, CRUISE_DISABLE, CRUISE_SET_SPEED, CRUISE_SET_GAP |
| BODY_MAIN_LIGHT_MODE | HEADLIGHT_ON, HEADLIGHT_OFF, HEADLIGHT_SET_MODE |
| BODY_HAZARD_LIGHT | HAZARD_LIGHT_ON, HAZARD_LIGHT_OFF |
| BODY_TURN_INDICATOR | TURN_INDICATOR_ON, TURN_INDICATOR_OFF |
| BODY_LOW_BEAM | LOW_BEAM_ON, LOW_BEAM_OFF |
| BODY_HIGH_BEAM | HIGH_BEAM_ON, HIGH_BEAM_OFF |
| BODY_FOG_LIGHT | FOG_LIGHT_ON, FOG_LIGHT_OFF |
| BODY_PARKING_LIGHT | PARKING_LIGHT_ON, PARKING_LIGHT_OFF |
| CABIN_WINDOW | WINDOW_OPEN, WINDOW_CLOSE, WINDOW_SET_POSITION |
| CABIN_DOOR_OPENING | DOOR_OPEN, DOOR_CLOSE, DOOR_SET_POSITION |
| CABIN_DOOR_LOCK | DOOR_LOCK, DOOR_UNLOCK |
| BODY_WIPER_USER_CONTROL | WIPER_SET_MODE, WIPER_SET_SENSITIVITY |
| CHASSIS_PARKING_BRAKE | PARKING_BRAKE_APPLY, PARKING_BRAKE_RELEASE, PARKING_BRAKE_AUTO_APPLY_ENABLE, PARKING_BRAKE_AUTO_APPLY_DISABLE |
| PROJECT_LONGITUDINAL_SPEED_CONTROL | ACCELERATE, DECELERATE |
| PROJECT_SERVICE_BRAKING | BRAKE, EMERGENCY_BRAKE |
| PROJECT_LANE_CONTROL | LANE_CHANGE, LANE_KEEP |
| PROJECT_EVASIVE_STEERING | EVASIVE_STEER |
| PROJECT_AUTO_PARK | AUTO_PARK_ENABLE |

`PROJECT_DISPLAY_CONTROL / DISPLAY_OFF` 已移出正式表，单独记录为 `LEGACY_TEST_ONLY / OUT_OF_SCOPE`。现有“大屏”回归测试不修改，但其文本不得作为正式 NLU Intent 训练标签。

### 过度原子化检查

- 仅 AREA 不同产生的重复 Intent：0。
- 仅具体数值不同产生的重复 Intent：0。
- 使用 VALUE/MODE 合并：车窗/车门/行李厢/前舱盖开度、巡航速度/间距、挡位、变速箱模式、换挡模式、主灯模式、雨刮模式，以及腰托支撑区域 `GENERIC/TOP/MID/BOTTOM`。
- 因安全语义不同而保留拆分：OPEN/CLOSE、LOCK/UNLOCK、ENABLE/DISABLE、PARKING_BRAKE_APPLY/RELEASE 等。
- 必要物理维度拆分：方向盘 Extension/Tilt 分为两个 Intent；腰托 mm 高度与 percent 支撑程度分为两个 Intent。
- 数量超过 60 的原因是 44 个已人工批准 family 中包含大量双向物理动作及安全系统开关，并额外保留 8 个正式项目原生 Intent；不是按区域或数值膨胀。

## C. Slot 标签体系

第一版只保留五类：

| Slot | 职责 | 示例 |
|---|---|---|
| AREA | 物理实例/作用区域 | 左后车门 → LEFT_REAR |
| VALUE | 数值、比例、速度、相对步进 | 一半、80公里、调高一点 |
| DIRECTION | 动作方向 | 向左变道 → LEFT |
| MODE | 有限枚举目标 | D挡、运动模式、快速雨刮 |
| NEGATION | 否定动作的文本 span | 不要、别再、无需 |

不增加独立 UNIT：单位包含在 VALUE span，由 ParameterNormalizer 解析。不增加 DEGREE：程度词属于 VALUE；“向上/向左”等空间动作方向属于 DIRECTION。

## D. AREA canonical 规范

Canonical 集合：`LEFT_FRONT`、`RIGHT_FRONT`、`LEFT_REAR`、`RIGHT_REAR`、`FRONT_ROW`、`REAR_ROW`、`LEFT_SIDE`、`RIGHT_SIDE`、`ALL`、`FRONT`、`REAR`。

关键归并：

- 驾驶位/主驾/司机这边/左前 → LEFT_FRONT → `SemanticFrame.area="左前"`。
- 副驾驶/副驾/右前 → RIGHT_FRONT → `"右前"`。
- 左后排 → LEFT_REAR；右后排 → RIGHT_REAR。
- 左边 → LEFT_SIDE；右边 → RIGHT_SIDE。
- 全部/所有/全车 → ALL。

AREA 缺失时不是错误，除非该 Intent 明确要求 AREA，例如 `DOOR_SET_POSITION`、座椅调节。任何 AREA 必须同时通过该 Intent 的 `allowed_areas`。

## E. VALUE 规范

NLU 标注原始 VALUE span；确定性 ParameterNormalizer 执行：

```text
raw span → lexical normalization → number/unit parsing → canonical unit
→ registry range check → capability consistency check
```

主要 contract：

- 百分比/开度：0–100%，例如“一半”→`50%`。
- `SEAT_LONGITUDINAL_SET_POSITION`：VSS `Seat.Position`，unit=`mm`，min=0，max=`VEHICLE_SPECIFIC.seat_longitudinal_max_mm`；不得转换成统一百分比。
- `SEAT_HEIGHT_SET_POSITION`：VSS `Seat.Height`，unit=`mm`，min=0，max=`VEHICLE_SPECIFIC.seat_height_max_mm`。
- `SEAT_LUMBAR_SET_HEIGHT`：VSS `LumbarHeight`，unit=`mm`，min=0，max=`VEHICLE_SPECIFIC.lumbar_height_max_mm`。
- `SEAT_LUMBAR_SET_SUPPORT`：VSS generic/Top/Mid/Bottom lumbar support 均为 percent 0–100；Top/Mid/Bottom 使用 MODE，不拆成四个 Intent。
- `STEERING_WHEEL_SET_EXTENSION` 与 `STEERING_WHEEL_SET_TILT`：两个独立 VSS actuator，均为 percent 0–100，不使用模糊的统一 position contract。
- 巡航速度：canonical `km/h`；最大值引用车型/安全策略，不在标签文件硬编码。
- 座椅整体 Tilt 和 Backrest Recline：VSS unit=`degrees`，范围引用车型 capability limit。
- 挡位：MODE=`P/R/N/D`，保持一个 `GEAR_SET`。
- 变速箱性能：`NORMAL/SPORT/ECONOMY/SNOW/RAIN`。
- 雨刮：`OFF/SLOW/MEDIUM/FAST/INTERVAL/RAIN_SENSOR`。
- 跟车间距：统一 `CRUISE_SET_GAP`，由等级或经批准单位表示。

模型不得做单位换算、范围裁剪或危险数值推断。非法值、缺失 required value、范围越界均由 Validator 拒绝。

## F. NEGATION 规范

“不要打开车门”标注：

```text
intent = DOOR_OPEN
negated = true
NEGATION span = “不要”
```

这样保留“被否定的是哪个动作”的理解能力；但 `negated=true` 或确定性 guard 命中后，Validator 必须返回 `NEGATED_ACTION`，Adapter 进入 existing unknown/diagnostic REVIEW 路径。模型预测不能替代 Parser/Interpreter/Review 现有三层保护；迁移时这些保护改由明确的 `SafetyTextGuard` 接口承接。

顶层 `negated` 的条件语义：

- `SINGLE + IN_SCOPE_CONTROL`：必须为 boolean。
- `MULTI`：必须为 null；每个 segment 分别记录自己的 boolean。
- `AMBIGUOUS`、`NON_CONTROL`、`UNKNOWN_CONTROL`、`AMBIGUOUS_CONTROL`：必须为 null。
- NEGATION 原始 span 继续保存在 slots 中。

## G. SINGLE / MULTI / AMBIGUOUS 规范

- SINGLE：一个控制目的，可带多个参数。
- MULTI：两个及以上独立控制目的；顶层 Intent 必须为 null。
- AMBIGUOUS：无法唯一决定控制目的或关键指代；顶层 Intent 必须为 null。
- MULTI 可在内部 `segments/detected_intents` 保存诊断，但不得形成普通可执行单 Intent。
- “不要打开车门然后加速”标为顶层 `negated=null`；DOOR_OPEN segment 为 `negated=true`，ACCELERATE segment 为 `negated=false`。

Adapter 映射：

```text
MULTI/AMBIGUOUS
→ action=unknown
→ target=unknown（或仅保留无执行意义的诊断 target）
→ retrieval_scope=diagnostic_only
→ REVIEW
→ no Authorization token
```

## H. UNKNOWN / OOD 规范

| 类型 | 含义 | 示例 | 处置 |
|---|---|---|---|
| NON_CONTROL | 非车辆控制 | 帮我写论文 | 永不授权；可直接拒绝或诊断终止 |
| UNKNOWN_CONTROL | 控制形式存在但对象/能力不在 Registry | 打开冰箱 | diagnostic REVIEW；永不授权 |
| AMBIGUOUS_CONTROL | 控制意图不完整 | 打开一下 | REVIEW；请求澄清；永不授权 |

这三类不是 95 个车辆 Intent 中的普通类别。Intent head 可以使用内部 `NO_INTENT` sentinel 训练结构，但运行时 OOD 由校准 confidence、margin、energy/distance、scope head 和 capability consistency 联合产生。本阶段不固定阈值。

## I. Context claim 与 NLU 的边界

Context claim 不成为普通 Intent label。NLU 可以识别主车控 Intent，但“管理员已授权”“模拟器模式”“忽略安全规则”等仍由确定性 adversarial/context scanner 与 AdvancedValidation 处理。模型不得据此改变 role、mode、authorization、risk 或 safety result。

## J. Risk profile deterministic mapping

```text
validated intent_id
→ VehicleCapabilityRegistry entry
→ canonical action/target/domain
→ deterministic risk_level/risk_tags
```

NLU 不预测可被直接信任的 risk。对于 VSS_AND_PROJECT Intent，已存在的更具体项目风险优先，例如 `DEFROST_ON=R2`、`DEFROST_OFF=R3`；其他 VSS Intent 使用人工工作簿 family 风险作为草案基线。任何风险变更都需要单独安全评审，不能由训练数据隐式改变。

以下 R1 仅为当前 DRAFT 值，统一标记 `RISK_REVIEW_REQUIRED`：驾驶员/乘员座椅前后位置、座椅高度、座椅整体倾角、靠背角度、方向盘伸缩、方向盘倾斜。原因是行驶中误调可能影响驾驶控制。该标记不修改运行时 risk profile，也不阻塞七 Intent PoC。

## K. VehicleCapabilityRegistry schema

每个 entry 至少包含：

```yaml
intent_id: DOOR_OPEN
chinese_name: 打开车门
capability_family: CABIN_DOOR_OPENING
canonical_action: 打开
canonical_target: 车门
control_domain: 车身控制
risk_level: R3
risk_review_status: CONFIRMED  # 需要复核时为 RISK_REVIEW_REQUIRED
risk_tags: [车身安全, 运动中误操作]
allowed_areas: [LEFT_FRONT, RIGHT_FRONT, LEFT_REAR, RIGHT_REAR, ...]
value_contract: NONE
required_slots: []
optional_slots: [AREA, NEGATION]
scope_status: IN_SCOPE
capability_origin: VSS_AND_PROJECT
vss_capability_ids: [CABIN_DOOR_OPENING]
vss_relation: DIRECT
scope_authority: BOTH
current_semantic_support: FULL
current_evidence_support: FULL
current_authorization_support: FULL
current_execution_support: FULL
```

Registry 是模型合法输出空间与 canonical mapping，不是安全规则、CARLA 能力表或 Authorization 白名单。加入 Registry 绝不自动授予执行权限。

## L. NLUResult → SemanticFrameAdapter 映射

内部数据流：

```text
NLUResult
→ Deterministic Normalizer
→ SafetyTextGuard
→ VehicleCapabilityValidator
→ SemanticFrameAdapter
→ existing SemanticFrame
```

Validator 状态建议：`VALID_SUPPORTED`、`VALID_NOT_RUNTIME_SUPPORTED`、`INVALID_SLOT`、`NEGATED_ACTION`、`MULTI_INTENT`、`AMBIGUOUS`、`OOD`、`MODEL_UNAVAILABLE`。

`VALID_NOT_RUNTIME_SUPPORTED` 不得因“理解正确”获得执行能力；Adapter 应映射到 diagnostic/unknown 安全形式，直至 evidence/authorization/execution 分别完成独立评审。

### 八个映射例

| 文本 | NLUResult | Validator | SemanticFrame 关键字段 |
|---|---|---|---|
| 打开车门 | DOOR_OPEN, SINGLE | VALID_SUPPORTED | `打开/车门/area=unknown/value=null/R3` |
| 打开左后车门 | DOOR_OPEN + AREA=LEFT_REAR | VALID_SUPPORTED | `打开/车门/左后/null/R3` |
| 不要打开车门 | DOOR_OPEN, negated=true | NEGATED_ACTION | `unknown/车门/unknown/null/R3`，diagnostic REVIEW |
| 把左后车窗开到一半 | WINDOW_SET_POSITION + LEFT_REAR + 50% | VALID_NOT_RUNTIME_SUPPORTED | `unknown/车窗/左后/50%/R2`，diagnostic REVIEW |
| 加速 | ACCELERATE | VALID_SUPPORTED | `加速/速度/unknown/null/R3` |
| 巡航设为80 | CRUISE_SET_SPEED + 80 km/h | VALID_NOT_RUNTIME_SUPPORTED | `unknown/巡航速度/unknown/80 km/h/R3`，diagnostic REVIEW |
| 关闭车门然后加速 | MULTI: DOOR_CLOSE + ACCELERATE | MULTI_INTENT | `unknown/unknown/unknown/null/R3`，diagnostic REVIEW |
| 打开冰箱 | UNKNOWN_CONTROL/OOD | OOD | `unknown/unknown/unknown/null/R1`，无 token |

表中的 confidence/ambiguity 必须由校准框架产生 float；这里不写假阈值。所有 NEGATED/MULTI/OOD/unsupported 结果必须被限制在非 PASS 路径。

## M. Confidence/Ambiguity 内部量设计

内部保留：

- `asr_confidence`：仅 audio 可用，text 为 missing，不伪造 1.0。
- `intent_confidence`：校准后的原子 Intent 概率。
- `slot_confidence`：required slot 的聚合置信度和最低值。
- `ood_confidence`：独立的 OOD/abstention 指标。
- `intent_margin`：top1-top2 间隔。
- `structure_confidence`：SINGLE/MULTI/AMBIGUOUS head 置信度。
- `capability_consistency`：Intent、AREA、VALUE、MODE 与 Registry 的确定性一致性。

未来 `semantic_confidence` 使用验证集拟合的 calibration function，而不是固定加权平均；确定性 violation 可设置上限。`ambiguity_score` 同时考虑 margin、slot completeness、structure、OOD 和 capability consistency，禁止直接使用 `1-softmax_top1`。具体权重和阈值留到验证集阶段。

## N. 数据标注 schema

正式草案：`data/nlu/spec/annotation_schema.json`；操作规范：`data/nlu/spec/annotation_guidelines.md`。

Canonical 标注使用 raw Unicode character offset 半开区间 `[start,end)`；token span/BIO 标签在训练时按具体 tokenizer 投影。这样 tokenizer 变化不会破坏原始标注。

顶层字段包括 `sample_id`、`text`、`registry_version`、`paraphrase_family_id`、`intent_structure`、`scope_label`、`intent`、`segments`、`slots`、`negated`、`ood_label`、`safety_tags`、`split` 和来源/审核状态。

`negated` 类型为 `boolean | null`：SINGLE+IN_SCOPE_CONTROL 必须是 boolean；MULTI/AMBIGUOUS/NON_CONTROL/UNKNOWN_CONTROL/AMBIGUOUS_CONTROL 必须是 null，MULTI 极性写在各 segment。

数据构建必须通过两层 Validator：

1. `annotation schema validation`：JSON 类型、required、枚举、span 和条件字段关系。
2. `registry cross-validation`：intent 存在且 IN_SCOPE、AREA 属于 allowed_areas、MODE 属于对应 mode_contract、VALUE 满足 allowed/required/unit/range、required slot 完整、Registry version 一致，并拒绝 `LEGACY_TEST_ONLY/OUT_OF_SCOPE` 标签。

JSON Schema 单独通过不代表样本可以进入训练。本阶段只定义这两层契约，不实现数据或训练流水线。

## O. train/validation/test/safety_gold 切分规范

- 先按 `paraphrase_family_id` 分组，再做 stratified group split；同模板替词不得跨 split。
- 同 speaker/session、同采集批次、同 ASR 音频派生文本应整体进入一个 split。
- 初始目标比例可为 train/validation/test = 70/15/15；以每个 Intent、Slot 和安全标签最低覆盖为约束调整。
- calibration 只使用 validation。
- test 在模型/阈值选择期间保持锁定。
- safety_gold 独立于 train/validation/test，不训练、不做阈值拟合；覆盖 SYS-001、SYS-003、UNKNOWN/OOD、ASR 易混、多意图、模糊指代、value 边界和 context claim。

## P. 当前 70 条已有文本的人工筛选流程

第一阶段静态盘点得到 70 条去重文本。按当前 Parser 结果统计：

| 当前 action\|target | 数量 | 当前 action\|target | 数量 |
|---|---:|---|---:|
| unknown\|unknown | 19 | unknown\|车门 | 11 |
| unknown\|车窗 | 2 | unknown\|前照灯 | 1 |
| unknown\|速度 | 1 | 关闭\|unknown | 1 |
| 关闭\|前挡风除雾 | 1 | 关闭\|前照灯 | 1 |
| 关闭\|大屏 | 2 | 减速\|速度 | 1 |
| 加速\|速度 | 1 | 变道\|左侧车道 | 1 |
| 变道\|右侧车道 | 1 | 打开\|unknown | 2 |
| 打开\|制动 | 2 | 打开\|大屏 | 1 |
| 打开\|空调 | 1 | 打开\|自动泊车 | 1 |
| 打开\|车窗 | 3 | 打开\|车门 | 9 |
| 播放\|音乐 | 5 | 查询\|速度 | 2 |
| 避险转向\|转向 | 1 |  |  |

处理流程：70/70 全部先进入人工 intake，0 条可未经复核直接进入训练。逐条分类为：Registry 单意图种子、安全金标候选、NON_CONTROL/UNKNOWN/OOD、标注歧义、测试脚手架/非用户语句、OUT_OF_SCOPE 娱乐/普通舒适/查询。包含“大屏”的旧 SYS-003 等测试文本可继续作为多意图安全回归材料，但 `DISPLAY_OFF` 本身只能标记 `LEGACY_TEST_ONLY/OUT_OF_SCOPE`，不能进入正式 Intent 训练标签。确认许可、去重、paraphrase family 和双人复核后才能转成数据记录。本阶段不复制文本、不生成数据集。

## Q. 当前仍需人工确认的 PENDING_SCOPE 能力清单

无。

- HUMAN_APPROVED VSS family：44。
- HUMAN_REJECTED VSS family：69。
- VSS PENDING_SCOPE：0。
- Registry PENDING_SCOPE Intent：0。

后续仍需人工确认的是 95 个 Intent 的车型相关 value limit 与标记为 `RISK_REVIEW_REQUIRED` 的风险基线，不是重新审查这 44 个 capability 是否保留。

## R. 下一阶段 PoC 推荐 Intent

PoC 经 Stage 3B.1 最终语义仲裁固定为 7 个：

1. `DOOR_OPEN`
2. `DOOR_CLOSE`
3. `WINDOW_OPEN`
4. `WINDOW_SET_POSITION`
5. `HEADLIGHT_OFF`
6. `ACCELERATE`
7. `BRAKE`

覆盖目标：相反动作、AREA、VALUE、车身高风险对象、纵向驾驶控制和制动。NEGATION、MULTI、AMBIGUOUS、NON_CONTROL、UNKNOWN_CONTROL 与 OOD 作为结构/安全样本加入 PoC 测试，但不是额外可执行 Intent。

## 阶段结论

```text
NLU_LABEL_DESIGN_READY = YES
VEHICLE_CAPABILITY_REGISTRY_DRAFT_READY = YES
READY_FOR_7_INTENT_POC_DATASET_BUILD = YES
READY_FOR_FULL_94_CLASS_DATASET_BUILD = NO
```

七 Intent PoC 已在 Stage 3B.1 完成语义收尾并补齐 WINDOW_OPEN；仍仅为离线候选数据，未执行训练或正式 split。`READY_FOR_FULL_94_CLASS_DATASET_BUILD` 是按 Stage 2.1 指令保留的历史旗标名称；当前正式 Registry 实际为 95 类。全量构建继续禁止，直到车型 value limits、风险复核、跨文件 Validator 与完整标注覆盖均完成验收。
