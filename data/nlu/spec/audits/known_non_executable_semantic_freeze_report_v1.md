# Known Non-Executable Intent 语义合同冻结与锚点补齐报告 v1

> 状态：审计/冻结候选，**非运行时资产**。本报告及同批产物未接入生产。

## 1. 91 个意图完整性结果

- 已逐项冻结 91 个稳定 `intent_id`，均补齐/保留控制域、规范动作、规范目标、控制属性、参数结构、Formal 边界、锚点统计和非执行合同。
- 执行身份统一为 `KNOWN_NON_EXECUTABLE`；允许语义成功与通过，但禁止执行授权、执行令牌和车辆控制调用。
- 状态分布：READY 68，NEEDS_ANCHOR_REVIEW 13，NEEDS_SCHEMA_REVIEW 2，BOUNDARY_REVIEW 8，BLOCKED 0。
- 两项 schema 复核：`TORQUE_DISTRIBUTION_SET` 的方向/带符号百分比双重编码；`DRIVING_MODE_SET` 的历史枚举与已确认旁路表达覆盖不一致。

## 2. 22 个原缺锚点意图处理结果

在历史意图表、规则/审批表、训练评测语料、审计数据、测试、归档配置和 source-screen shards 中重新检索。`TCS_ENABLE` 找回 2 条、`TCS_DISABLE` 找回 3 条真实单意图表达；其余 20 个未发现可证明归属的自然语言历史表达，生成少量待人工审核候选。所有新表达均单独标记 `GENERATED_REVIEW_REQUIRED`。

| intent_id | 缺失原因 | 找回历史 | 生成候选 | 当前状态 | 进入统一注册表条件 |
| --- | --- | --- | --- | --- | --- |
| MIRROR_ADJUSTMENT_LOCK | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | BOUNDARY_REVIEW | YES_AFTER_REVIEW |
| MIRROR_ADJUSTMENT_UNLOCK | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | BOUNDARY_REVIEW | YES_AFTER_REVIEW |
| ABS_ENABLE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 2 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| ABS_DISABLE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 2 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| TCS_ENABLE | B_OR_C_RECOVERY_ASSOCIATION_MISSED | 2 | 0 | READY | YES |
| TCS_DISABLE | B_OR_C_RECOVERY_ASSOCIATION_MISSED | 3 | 0 | READY | YES |
| EBD_ENABLE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 2 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| EBD_DISABLE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 2 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| EBA_ENABLE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 2 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| EBA_DISABLE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 2 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| HOOD_SET_POSITION | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | BOUNDARY_REVIEW | YES_AFTER_REVIEW |
| LOW_RANGE_ENABLE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | BOUNDARY_REVIEW | YES_AFTER_REVIEW |
| LOW_RANGE_DISABLE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | BOUNDARY_REVIEW | YES_AFTER_REVIEW |
| TORQUE_DISTRIBUTION_SET | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 2 | NEEDS_SCHEMA_REVIEW | YES_AFTER_REVIEW |
| TRANSMISSION_PERFORMANCE_MODE_SET | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | BOUNDARY_REVIEW | YES_AFTER_REVIEW |
| DIFFERENTIAL_LOCK | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| DIFFERENTIAL_UNLOCK | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| ELECTRIC_POWERTRAIN_ENGAGE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| ELECTRIC_POWERTRAIN_DISENGAGE | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| CLUTCH_SET_ENGAGEMENT | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| PARK_LOCK | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |
| PARK_UNLOCK | A_NO_NATURAL_LANGUAGE_FOUND_IN_SEARCHED_HISTORY | 0 | 3 | NEEDS_ANCHOR_REVIEW | YES_AFTER_REVIEW |

## 3. 10 个 Formal/Known 相邻边界检查

| Known | 最近 Formal | 共享词/对象 | 能力差异 | Formal 表达 | Known 表达 | 歧义表达 | 守卫要求 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MIRROR_ADJUSTMENT_LOCK | MIRROR_HEATING_ON, MIRROR_HEATING_OFF, MIRROR_FOLD, MIRROR_UNFOLD, MIRROR_SET_ANGLE | 外后视镜/后视镜 | 锁定的是调节权限/调节锁状态；Formal 分别控制加热、折叠和镜面角度。 | 打开后视镜加热；折叠后视镜；把后视镜往下调 | 锁定外后视镜调节；别让右侧后视镜再被调节 | 把后视镜锁住 | 必须同时识别锁定动作与‘调节/权限’属性；仅出现折叠、加热或角度时不得路由至本意图。 |
| MIRROR_ADJUSTMENT_UNLOCK | MIRROR_HEATING_ON, MIRROR_HEATING_OFF, MIRROR_FOLD, MIRROR_UNFOLD, MIRROR_SET_ANGLE | 外后视镜/后视镜 | 解锁的是调节权限；Formal 控制加热、展开或实际角度。 | 关闭后视镜加热；展开后视镜；调高后视镜角度 | 解锁外后视镜调节；允许右侧后视镜继续调节 | 把后视镜解锁 | 要求解锁动作和调节权限属性共现；‘展开’不能等同于‘解锁调节’。 |
| HOOD_SET_POSITION | HOOD_OPEN, HOOD_CLOSE | 前舱盖/引擎盖/开 | 本意图设置部分开度 VALUE；Formal 只表达完全打开或完全关闭。 | 打开前舱盖；关闭引擎盖 | 前舱盖开到一半；引擎盖开度调到30% | 前舱盖开一点 | 出现明确百分比/部分开度时归本意图；无开度值的开/关归 Formal；相对模糊开度进入复核。 |
| LOW_RANGE_ENABLE | GEAR_SET, GEAR_CHANGE_MODE_SET | 挡/模式/变速箱/传动 | 本意图启用低速传动范围；Formal 分别设置 P/R/N/D 目标挡位或手动/自动换挡工作模式。 | 挂D挡；切换自动换挡模式 | 挂上低速挡；启用低速四驱 | 切到低速模式 | 检查 LOW_RANGE/低速四驱语义，不可仅凭‘挡’或‘模式’路由。 |
| LOW_RANGE_DISABLE | GEAR_SET, GEAR_CHANGE_MODE_SET | 挡/模式/变速箱/传动 | 本意图退出低速传动范围；Formal 不控制低速范围开关。 | 挂N挡；切换手动换挡模式 | 退出低速挡；关闭低速四驱 | 退出低速模式 | 要求低速范围目标和停用动作；手动/自动/P/R/N/D 明示时归 Formal。 |
| TORQUE_DISTRIBUTION_SET | GEAR_SET, GEAR_CHANGE_MODE_SET | 传动/动力/变速箱 | 本意图分配前后轴扭矩比例；Formal 只选挡位或换挡工作模式。 | 挂R挡；换成自动换挡 | 前轴扭矩分配到60%；后轴扭矩分配到60% | 动力往后调一点 | 必须识别轴向目标与比例；只有传动/动力词而无轴向和分配动作时进入复核。 |
| TRANSMISSION_PERFORMANCE_MODE_SET | GEAR_SET, GEAR_CHANGE_MODE_SET | 变速箱/传动/模式 | 本意图设置变速箱性能标定（运动/经济/雪地等）；Formal 换挡模式仅为手动/自动。 | 挂P挡；换成手动换挡模式 | 变速箱切到运动性能模式；变速器性能模式调成经济 | 变速箱切换模式 | 模式值为 MANUAL/AUTOMATIC 时归 GEAR_CHANGE_MODE_SET；性能/路况值且明确变速箱目标时归本意图。 |
| DRIVING_MODE_SET | GEAR_CHANGE_MODE_SET | 模式/切换 | DRIVING_MODE_SET 控制整车驾驶风格或路况模式（运动、经济、雪地、越野等）；GEAR_CHANGE_MODE_SET 仅控制手动/自动换挡工作模式。 | 切换到手动换挡模式；变成自动换挡 | 打开运动模式；驾驶模式切到经济；切换到雪地模式 | 切换模式；换成运动模式（未说明整车还是变速箱） | 同时检查目标层级和模式枚举；MANUAL/AUTOMATIC 只归换挡模式，驾驶风格/路况值归驾驶模式，目标缺失时复核。 |
| STEERING_WHEEL_HEATING_OFF | STEERING_WHEEL_SET_EXTENSION, STEERING_WHEEL_SET_TILT | 方向盘/调节 | 本意图关闭方向盘加热；Formal 调整方向盘前后伸缩或上下倾斜。 | 方向盘往前调；方向盘往下调 | 关闭方向盘加热；方向盘加热关掉 | 方向盘太热了 | 必须识别 HEATING 属性；位置方向词归几何调节，只有状态抱怨而无动作时复核。 |
| STEERING_WHEEL_HEATING_ON | STEERING_WHEEL_SET_EXTENSION, STEERING_WHEEL_SET_TILT | 方向盘/调节 | 本意图开启方向盘加热；Formal 调整方向盘几何位置。 | 方向盘拉近一点；方向盘抬高一点 | 打开方向盘加热；方向盘加热开一下 | 方向盘有点冷 | 必须识别 HEATING 属性和开启动作；伸缩/倾斜方向词不得触发本意图。 |

`DRIVING_MODE_SET` 与 `GEAR_CHANGE_MODE_SET` 明确保留为不同能力：前者是整车驾驶风格/路况模式，后者仅是手动/自动换挡工作模式，不因“模式”共词合并。

## 4. 历史表达冲突和污染检查

- 2388 条历史挂靠经全量精确与 NFKC 标准化检查：2356 个精确唯一文本、2356 个标准化唯一文本。
- 发现 27 个标准化表达跨 Known 意图重复；发现 6 个表达与 Formal 生产锚点精确重合。
- 隔离清单共 89 条“意图-表达挂靠记录”。未删除、未改写任何历史源资产。
- 隔离原因计数（同一记录可多因）：跨 Known 重复 59，抢占 Formal 6，目标词无动作 7，残缺/不可解释 5，非车辆/错域 4，目标或控制属性错误 19；乱码或控制字符 0。
- 明确抢占 Formal 的 6 组：`关闭空调除霜`→DEFROST_OFF；`打开车窗`→WINDOW_OPEN；`关闭所有车窗`→WINDOW_CLOSE；`打开后尾门`→TRUNK_OPEN；`打开/关闭天窗`→SUNROOF_OPEN/CLOSE。
- 稳定双指向守卫需求：香氛“位置2/3”需要区分等级与香型编号；“空气净化开最大”需要区分状态开启与最大风量（可含隐式开启）。其余重复主要是错误挂靠或多目标污染。
- 已对冲突组及短文本/单目标词/乱码/宽泛文本做针对性抽样；风险项仅进入隔离清单。

## 5. 当前可直接迁移数量

- 可直接迁移（`READY`）：68。
- 待锚点人工审核：13。
- 待 schema 审核：2。
- 待边界/守卫审核：8。
- 阻塞：0。

这里“可迁移”仅指候选定义已具备进入下一阶段统一注册表的材料，不代表已经接入运行时。

## 6. 仍需人工决定的项目

1. 审核 20 个意图的全部 `GENERATED_REVIEW_REQUIRED` 锚点；通过前不得进入生产。
2. 决定 `TORQUE_DISTRIBUTION_SET` 的轴向与百分比唯一规范化方式。
3. 确认 `DRIVING_MODE_SET` 与 `TRANSMISSION_PERFORMANCE_MODE_SET` 的模式枚举及目标层级守卫。
4. 审核 10 组相邻边界及歧义表达的 REVIEW 条件。
5. 审核隔离清单，尤其 6 个 Formal 抢占项和两类稳定双指向表达。
6. `PARK_LOCK/PARK_UNLOCK` 与 P 挡、电子驻车制动的词面边界应在迁移实现时加入对象/控制属性守卫。

## 7. 本轮新生成的审计文件

- `data/nlu/spec/audits/known_non_executable_semantic_freeze_candidate_v1.yaml`：91 个冻结候选定义。
- `data/nlu/spec/audits/known_non_executable_semantic_freeze_audit_v1.json`：机器可读完整审计、状态、校验和迁移影响面。
- `data/nlu/spec/audits/known_non_executable_anchor_quarantine_v1.jsonl`：冲突/污染挂靠隔离清单。
- `data/nlu/spec/audits/known_non_executable_semantic_freeze_report_v1.md`：本报告。

原 `known_non_executable_intents_candidate.yaml` 与所有历史资产保持不变。

## 8. 自动校验结果

| 校验 | 结果 |
| --- | --- |
| formal_intent_count_is_71 | PASS |
| known_non_executable_count_is_91 | PASS |
| known_intent_ids_globally_unique | PASS |
| formal_and_known_intent_ids_zero_overlap | PASS |
| all_known_marked_non_executable | PASS |
| all_known_execution_forbidden | PASS |
| all_known_intent_ids_non_empty | PASS |
| historical_and_generated_anchor_sources_distinguishable | PASS |
| unapproved_hash_candidate_usage_is_zero | PASS |
| unapproved_1402_candidate_source_usage_is_zero | PASS |
| current_bypass_anchor_count_is_20 | PASS |
| current_bypass_unique_mapping_is_20_of_20 | PASS |
| all_91_have_control_domain | PASS |
| all_91_have_action_target_and_parameter_schema | PASS |
| all_91_have_formal_boundary | PASS |

| no_production_runtime_file_modified_by_generation | PASS |

## 9. 下一阶段统一语义注册表迁移预计涉及的生产文件（只读探测）

| 文件 | 预计原因 |
| --- | --- |
| 挂靠/intent_cards_v1.yaml | 统一注册表/卡片需表达 91 个稳定语义合同及执行类别。 |
| 挂靠/intent_anchor_set_v1_3.yaml | 人工批准后接收历史锚点和通过审核的新增锚点；当前不得写入。 |
| backend/intent_recall_v1/config.yaml | 召回器统一注册表/锚点路径及类别配置。 |
| backend/intent_recall_v1/recaller.py | 召回结果需保留 Formal 与 KNOWN_NON_EXECUTABLE 身份，不再压成旁路标签。 |
| backend/intent_judge_3b_minimal/config.yaml | 判定输出与候选提示需支持统一语义身份。 |
| backend/intent_judge_3b_minimal/judge.py | 语义通过与执行资格分离。 |
| backend/semantic_orchestrator_v2/orchestrator.py | 编排层需让 Known 语义成功通过但禁止授权、令牌与车辆调用。 |
| backend/semantic_orchestrator_v2/action_direction_guard.py | 新增动作/方向边界与冲突表达守卫。 |
| backend/semantic_orchestrator_v2/candidate_consistency_guard.py | Formal/Known 候选一致性和双指向复核。 |
| backend/semantic_orchestrator_v2_1/object_family_guard.py | 补齐 Known 对象族与控制属性边界。 |
| backend/semantic_orchestrator_v2_1/orchestrator.py | v2.1 同步统一身份与非执行语义。 |
| 相关 recall/judge/orchestrator tests 与 acceptance cases | 覆盖 91 数量、22 锚点、10 边界、非授权和非调用行为。 |

这只是预计影响范围，本轮没有实施任何修改。

## 10. 生产代码修改确认

本轮未修改任何生产代码、Formal 注册表、生产锚点、安全门、授权、令牌、执行、证据、强制召回、因果图或审计前端；未开始统一注册表运行时迁移。
