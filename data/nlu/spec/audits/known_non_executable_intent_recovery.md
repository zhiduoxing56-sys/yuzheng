# Known Non-Executable Intent 历史资产恢复与最终清点

> 状态：审计候选，非 Runtime Registry。结论不修改生产代码、Safety/Evidence/Authorization/Execution、HNSW、数据库 hash 或当前 71 R4。

## 1. 最终结论（A–S）

- **A 原始历史 Known 类别：91。** archive 明确声明 91 条；跨 R1/R3/R4 草案、人工审批表和数据审计复核后，没有发现另一套已批准且稳定的 Known ID。
- **B 历史来源文件：** 见第 2 节；权威链为 R1/93 人工审批 → R3 22 Known → R4 数据扩展 61 + 一致性补丁 8 → 91 条 archive。
- **C 去重后：91。** 多版本重复按稳定 intent_id 合并来源，未重复计数。
- **D 被当前 71 Formal 完整覆盖：0。** 比较 action、target、control_attribute、slots/contracts 与 examples 后，无 exact semantic signature 重合。
- **E 废弃/错误/重复类别：0。** PENDING 哈希候选不是历史批准 Intent，未计入 91，也不算废弃。
- **F 建议恢复 Known Non-Executable：91。** 其中 10 条是 Formal 的词面/目标相邻 capability，81 条完全未覆盖；全部 execution_eligible=false。
- **G–J 完整候选、逐项来源、slots、expression 数：** 见第 3 节和机器可读 YAML。
- **K 当前 bypass 映射覆盖：20/20 = 100%。** 当前 anchor 仅有‘驾驶模式’20 条，全部映射到 DRIVING_MODE_SET。
- **L 无法唯一映射的 bypass expression：0。** 普通‘运动/经济/雪地模式’按现有 anchor 权威归 DRIVING_MODE_SET；显式‘变速箱性能’才进入 TRANSMISSION_PERFORMANCE_MODE_SET。
- **M 与 71 Formal 存在边界相邻的候选：10。** 它们不是 Formal 覆盖项，详见第 5 节。
- **N 驾驶模式边界：** DRIVING_MODE_SET 是整车驾驶风格/路况；TRANSMISSION_PERFORMANCE_MODE_SET 是明确变速箱性能；Formal GEAR_CHANGE_MODE_SET 只接受 MANUAL/AUTOMATIC。
- **O 过度原子化：** 未发现按 SPORT/ECO/SNOW 分裂的批准 Intent；模式、温度、亮度、位置已参数化，因此本轮无强制合并项。ON/OFF 等动作对保持稳定。
- **P 代表性 20 条：** 见第 7 节。
- **Q 是否修改当前 71 R4：否。**
- **R 是否修改生产文件：否。** 本轮仅新增本报告与候选 YAML。
- **S 下一步接入：** 见第 10 节；先做独立只读候选召回/selector 评估，再经单独 migration 评审，不能直接加载本 YAML。

三类语义世界最终为：`FORMAL_R4=71`；`KNOWN_NON_EXECUTABLE=91 candidates`；`UNKNOWN/OOD/INCOMPLETE` 无正式 intent_id 并进入 REVIEW/clarification。`KNOWN_CONTROL_BYPASS` 只保留历史 scope/reference，不再是未来细粒度语义终点。

## 2. 历史来源文件与取舍

| 文件 | 版本 | 用途 |
|---|---|---|
| data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml | sys-014-semantic-hardening-r1 | historical registry/reference |
| data/nlu/spec/intent_registry_draft.yaml | sys-014-semantic-hardening-r2 | historical registry/reference |
| data/nlu/spec/intent_registry_r3.yaml | sys-014-semantic-hardening-r3 | historical registry/reference |
| data/nlu/spec/intent_registry_r4_core_draft.yaml | sys-014-semantic-hardening-r4-core-draft | historical registry/reference |
| data/nlu/spec/intent_registry_r4_full_draft.yaml | sys-014-semantic-hardening-r4-full-draft | historical registry/reference |
| data/nlu/spec/intent_registry_r4_final_candidate.yaml | sys-014-semantic-hardening-r4-final-candidate | historical registry/reference |
| data/nlu/spec/known_control_reference_archive_r4.yaml | known-control-reference-archive-r4 | historical registry/reference |
| data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json | r4_known_unsupported_expansion_report_v1 | 61 approved data-backed intents and evidence |
| intent_anchor_set_v1_2.yaml | v1_2 | current 20 KNOWN_CONTROL_BYPASS expressions |
| 挂靠/intent_anchor_set_v1_3.yaml | v1_3 | anchor history cross-check |
| SYS-014_93意图人工语义审批表_中文辅助版.xlsx | 93-intent human approval | early 22 Known IDs |
| SYS-014_93意图协作人工审查版_全中文.xlsx | 93-intent collaborative review | early 22 Known IDs |
| 新语证_VSS6.0_113能力筛选表_v0.2.xlsx | v0.2 | VSS capability provenance cross-check |
| train_set.jsonl | historical MAC-SLU train | natural-language evidence |
| dev_set.jsonl | historical MAC-SLU dev | natural-language evidence |
| test_set.jsonl | historical MAC-SLU test | natural-language evidence |

补充取舍：`known_unsupported_adas_candidates_v1.json` 的 127 个和 `known_unsupported_other_candidates_v1.json` 的 1,275 个条目均为 `PENDING_ONLY_NOT_AUTO_ADDED_TO_REGISTRY`，且大量 ID 为哈希占位符；它们不是稳定历史 Known Intent，本轮不恢复。XLSX 复核显示两份 93 条人工审批表均命中同一组早期 22 个 Known ID；VSS 113 能力表提供 capability 来源而不新增稳定 intent_id。

## 3. 最终 91 个候选完整清单

| intent_id | 名称 | action/target/attribute | slots | 表达数 | A-D | 历史来源 |
|---|---|---|---|---|---|---|
| MIRROR_ADJUSTMENT_LOCK | 锁定外后视镜调节 | LOCK/MIRROR/ADJUSTMENT_LOCK_STATE | AREA? | 0 | B | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| MIRROR_ADJUSTMENT_UNLOCK | 解锁外后视镜调节 | UNLOCK/MIRROR/ADJUSTMENT_LOCK_STATE | AREA? | 0 | B | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| ABS_ENABLE | 启用防抱死制动系统 | ENABLE/ABS/STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| ABS_DISABLE | 停用防抱死制动系统 | DISABLE/ABS/STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| TCS_ENABLE | 启用牵引力控制系统 | ENABLE/TCS/STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| TCS_DISABLE | 停用牵引力控制系统 | DISABLE/TCS/STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| EBD_ENABLE | 启用电子制动力分配系统 | ENABLE/EBD/STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| EBD_DISABLE | 停用电子制动力分配系统 | DISABLE/EBD/STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| EBA_ENABLE | 启用紧急制动辅助系统 | ENABLE/EBA/STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| EBA_DISABLE | 停用紧急制动辅助系统 | DISABLE/EBA/STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| HOOD_SET_POSITION | 设置前舱盖开度 | ADJUST/HOOD/OPENING_POSITION | VALUE | 0 | B | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| LOW_RANGE_ENABLE | 启用低速四驱或低速挡 | ENABLE/TRANSMISSION/LOW_RANGE_STATE | — | 0 | B | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| LOW_RANGE_DISABLE | 停用低速四驱或低速挡 | DISABLE/TRANSMISSION/LOW_RANGE_STATE | — | 0 | B | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| TORQUE_DISTRIBUTION_SET | 设置前后轴扭矩分配 | SET/TRANSMISSION/TORQUE_DISTRIBUTION | VALUE,DIRECTION? | 0 | B | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| TRANSMISSION_PERFORMANCE_MODE_SET | 设置变速箱性能模式 | SWITCH_MODE/TRANSMISSION/PERFORMANCE_MODE | MODE | 0 | B | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| DIFFERENTIAL_LOCK | 锁定差速器 | LOCK/DIFFERENTIAL/LOCK_STATE | AREA? | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| DIFFERENTIAL_UNLOCK | 解锁差速器 | UNLOCK/DIFFERENTIAL/LOCK_STATE | AREA? | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| ELECTRIC_POWERTRAIN_ENGAGE | 结合电驱动力 | ENGAGE/ELECTRIC_POWERTRAIN/ENGAGEMENT_STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| ELECTRIC_POWERTRAIN_DISENGAGE | 分离电驱动力 | DISENGAGE/ELECTRIC_POWERTRAIN/ENGAGEMENT_STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| CLUTCH_SET_ENGAGEMENT | 设置离合器结合度 | ADJUST/CLUTCH/ENGAGEMENT_LEVEL | VALUE | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| PARK_LOCK | 结合驻车锁 | LOCK/PARK_LOCK/ENGAGEMENT_STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| PARK_UNLOCK | 释放驻车锁 | UNLOCK/PARK_LOCK/ENGAGEMENT_STATE | — | 0 | C | data/nlu/spec/history/intent_registry_R1_b9b5e7dbe421.yaml; data/nlu/spec/intent_registry_draft.yaml; data/nlu/spec/intent_registry_r3.yaml; data/nlu/spec/intent_registry_r4_core_draft.yaml; data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; SYS-014_93意图人工语义审批表_中文辅助版.xlsx; SYS-014_93意图协作人工审查版_全中文.xlsx |
| AIR_PURIFIER_OFF | 关闭空气净化器 | TURN_OFF/AIR_PURIFIER/STATE | — | 5 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; train_set.jsonl |
| AIR_PURIFIER_ON | 开启空气净化器 | TURN_ON/AIR_PURIFIER/STATE | — | 13 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; train_set.jsonl |
| AIR_PURIFIER_SET_MODE | 设置空气净化器模式 | SWITCH_MODE/AIR_PURIFIER/MODE | MODE | 2 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; train_set.jsonl |
| AMBIENT_LIGHT_OFF | 关闭氛围灯 | TURN_OFF/AMBIENT_LIGHT/STATE | AREA? | 13 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| AMBIENT_LIGHT_ON | 开启氛围灯 | TURN_ON/AMBIENT_LIGHT/STATE | AREA? | 13 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| AMBIENT_LIGHT_SET_BRIGHTNESS | 设置氛围灯亮度 | SET/AMBIENT_LIGHT/BRIGHTNESS | VALUE,AREA? | 11 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; train_set.jsonl |
| AMBIENT_LIGHT_SET_COLOR | 设置氛围灯颜色 | SET/AMBIENT_LIGHT/COLOR | VALUE,AREA? | 23 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; train_set.jsonl |
| AMBIENT_LIGHT_SET_MODE | 设置氛围灯模式 | SWITCH_MODE/AMBIENT_LIGHT/MODE | MODE,AREA? | 21 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| ARMREST_SET_POSITION | 设置扶手位置 | ADJUST/ARMREST/POSITION | VALUE | 118 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| BLUETOOTH_OFF | 关闭蓝牙 | TURN_OFF/BLUETOOTH/STATE | — | 11 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; train_set.jsonl |
| BLUETOOTH_ON | 开启蓝牙 | TURN_ON/BLUETOOTH/STATE | — | 10 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| CAMERA_OFF | 关闭车载摄像头 | TURN_OFF/CAMERA/STATE | — | 1 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl |
| CAMERA_ON | 开启车载摄像头 | TURN_ON/CAMERA/STATE | — | 2 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; train_set.jsonl |
| CAMERA_SET_MODE | 设置车载摄像头模式 | SWITCH_MODE/CAMERA/MODE | MODE | 33 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| CHILD_LOCK_OFF | 关闭儿童锁 | TURN_OFF/CHILD_LOCK/STATE | AREA? | 8 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| CHILD_LOCK_ON | 开启儿童锁 | TURN_ON/CHILD_LOCK/STATE | AREA? | 6 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| DISPLAY_OFF | 关闭显示屏 | TURN_OFF/DISPLAY/STATE | AREA? | 38 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| DISPLAY_ON | 开启显示屏 | TURN_ON/DISPLAY/STATE | AREA? | 24 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| DISPLAY_SET_BRIGHTNESS | 设置显示屏亮度 | SET/DISPLAY/BRIGHTNESS | VALUE,AREA? | 57 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| DISPLAY_SET_POSITION | 设置显示屏位置 | ADJUST/DISPLAY/POSITION | VALUE,AREA? | 188 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| DRIVING_MODE_SET | 设置驾驶模式 | SWITCH_MODE/DRIVING_MODE/MODE | MODE | 54 | B | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl; intent_anchor_set_v1_2.yaml; 挂靠/intent_anchor_set_v1_3.yaml |
| DRIVING_RECORDER_ON | 开启行车记录仪 | TURN_ON/DRIVING_RECORDER/STATE | — | 2 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| FRAGRANCE_OFF | 关闭香氛 | TURN_OFF/FRAGRANCE/STATE | — | 4 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| FRAGRANCE_ON | 开启香氛 | TURN_ON/FRAGRANCE/STATE | — | 10 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| FRAGRANCE_SET_LEVEL | 设置香氛档位 | SET/FRAGRANCE/LEVEL | VALUE | 21 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; train_set.jsonl |
| FRUNK_OPEN | 开启前备箱 | OPEN/FRUNK/OPENING_STATE | — | 1 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; train_set.jsonl |
| GLASS_ROOF_SET_TRANSPARENCY | 设置玻璃天幕透光度 | SET/GLASS_ROOF/TRANSPARENCY | VALUE | 46 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; train_set.jsonl |
| HOTSPOT_OFF | 关闭热点 | TURN_OFF/HOTSPOT/STATE | — | 5 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| HOTSPOT_ON | 开启热点 | TURN_ON/HOTSPOT/STATE | — | 6 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| HVAC_OFF | 关闭空调 | TURN_OFF/HVAC/STATE | AREA? | 47 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| HVAC_ON | 开启空调 | TURN_ON/HVAC/STATE | AREA? | 143 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| HVAC_SET_AIRFLOW_DIRECTION | 设置空调风向 | SET/HVAC/AIRFLOW_DIRECTION | VALUE,AREA? | 63 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| HVAC_SET_FAN_SPEED | 设置空调风量 | SET/HVAC/FAN_SPEED | VALUE,AREA? | 164 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| HVAC_SET_MODE | 设置空调模式 | SWITCH_MODE/HVAC/MODE | MODE,AREA? | 49 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| HVAC_SET_TEMPERATURE | 设置空调温度 | SET/HVAC/TEMPERATURE | VALUE,AREA? | 303 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| INTERIOR_LIGHT_OFF | 关闭车内灯 | TURN_OFF/INTERIOR_LIGHT/STATE | AREA? | 4 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; train_set.jsonl |
| INTERIOR_LIGHT_ON | 开启车内灯 | TURN_ON/INTERIOR_LIGHT/STATE | AREA? | 8 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| MEDIA_SOUND_EFFECT_SET | 设置车载媒体音效 | SWITCH_MODE/MEDIA/SOUND_EFFECT | MODE | 88 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| MEDIA_VOLUME_SET | 设置车载媒体音量 | SET/MEDIA/VOLUME | VALUE | 235 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| READING_LIGHT_OFF | 关闭阅读灯 | TURN_OFF/READING_LIGHT/STATE | AREA? | 11 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| READING_LIGHT_ON | 开启阅读灯 | TURN_ON/READING_LIGHT/STATE | AREA? | 12 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; train_set.jsonl |
| READING_LIGHT_SET_BRIGHTNESS | 设置阅读灯亮度 | SET/READING_LIGHT/BRIGHTNESS | VALUE,AREA? | 7 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| REFRIGERATOR_ON | 开启车载冰箱 | TURN_ON/REFRIGERATOR/STATE | — | 6 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| REFRIGERATOR_SET_TEMPERATURE | 设置车载冰箱温度 | SET/REFRIGERATOR/TEMPERATURE | VALUE | 8 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SEAT_HEATING_OFF | 关闭座椅加热 | TURN_OFF/SEAT_HEATING/STATE | AREA? | 26 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SEAT_HEATING_ON | 开启座椅加热 | TURN_ON/SEAT_HEATING/STATE | AREA? | 40 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SEAT_HEATING_SET_LEVEL | 设置座椅加热档位 | SET/SEAT_HEATING/LEVEL | VALUE,AREA? | 23 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| SEAT_HEATING_SET_MODE | 设置座椅加热模式 | SWITCH_MODE/SEAT_HEATING/MODE | MODE,AREA? | 1 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; train_set.jsonl |
| SEAT_MASSAGE_OFF | 关闭座椅按摩 | TURN_OFF/SEAT_MASSAGE/STATE | AREA? | 20 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SEAT_MASSAGE_ON | 开启座椅按摩 | TURN_ON/SEAT_MASSAGE/STATE | AREA? | 69 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SEAT_MASSAGE_SET_LEVEL | 设置座椅按摩档位 | SET/SEAT_MASSAGE/LEVEL | VALUE,AREA? | 10 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; train_set.jsonl |
| SEAT_MASSAGE_SET_MODE | 设置座椅按摩模式 | SWITCH_MODE/SEAT_MASSAGE/MODE | MODE,AREA? | 25 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SEAT_VENTILATION_OFF | 关闭座椅通风 | TURN_OFF/SEAT_VENTILATION/STATE | AREA? | 23 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SEAT_VENTILATION_ON | 开启座椅通风 | TURN_ON/SEAT_VENTILATION/STATE | AREA? | 93 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SEAT_VENTILATION_SET_LEVEL | 设置座椅通风档位 | SET/SEAT_VENTILATION/LEVEL | VALUE,AREA? | 31 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl; train_set.jsonl |
| SEAT_VENTILATION_SET_MODE | 设置座椅通风模式 | SWITCH_MODE/SEAT_VENTILATION/MODE | MODE,AREA? | 1 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; test_set.jsonl |
| SHADE_CLOSE | 关闭遮阳帘 | CLOSE/SHADE/OPENING_STATE | AREA? | 11 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SHADE_OPEN | 开启遮阳帘 | OPEN/SHADE/OPENING_STATE | AREA? | 20 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| SHADE_SET_POSITION | 设置遮阳帘位置 | ADJUST/SHADE/POSITION | VALUE,AREA? | 1 | C | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; train_set.jsonl |
| STEERING_WHEEL_HEATING_OFF | 关闭方向盘加热 | TURN_OFF/STEERING_WHEEL/HEATING_STATE | — | 5 | B | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| STEERING_WHEEL_HEATING_ON | 开启方向盘加热 | TURN_ON/STEERING_WHEEL/HEATING_STATE | — | 4 | B | data/nlu/spec/intent_registry_r4_full_draft.yaml; data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; data/nlu/spec/audits/r4_known_unsupported_expansion_report_v1.json; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| AIR_PURIFIER_SET_FAN_SPEED | 设置空气净化器风速 | SET/AIR_PURIFIER/FAN_SPEED | VALUE | 8 | C | data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; dev_set.jsonl; train_set.jsonl |
| DISPLAY_SET_MODE | 设置显示屏模式 | SWITCH_MODE/DISPLAY/MODE | MODE,AREA? | 30 | C | data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; dev_set.jsonl; train_set.jsonl |
| READING_LIGHT_SET_MODE | 设置阅读灯模式 | SWITCH_MODE/READING_LIGHT/MODE | MODE,AREA? | 2 | C | data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; dev_set.jsonl; train_set.jsonl |
| REFRIGERATOR_SET_MODE | 设置车载冰箱模式 | SWITCH_MODE/REFRIGERATOR/MODE | MODE | 10 | C | data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; dev_set.jsonl; train_set.jsonl |
| FRAGRANCE_SET_SCENT | 设置香氛香型 | SET/FRAGRANCE/SCENT | VALUE | 5 | C | data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; train_set.jsonl |
| INTERIOR_LIGHT_SET_BRIGHTNESS | 设置车内灯亮度 | SET/INTERIOR_LIGHT/BRIGHTNESS | VALUE,AREA? | 26 | C | data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; dev_set.jsonl; test_set.jsonl; train_set.jsonl |
| INTERIOR_LIGHT_SET_COLOR | 设置车内灯颜色 | SET/INTERIOR_LIGHT/COLOR | VALUE,AREA? | 2 | C | data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; train_set.jsonl |
| INTERIOR_LIGHT_SET_MODE | 设置车内灯模式 | SWITCH_MODE/INTERIOR_LIGHT/MODE | MODE,AREA? | 8 | C | data/nlu/spec/intent_registry_r4_final_candidate.yaml; data/nlu/spec/known_control_reference_archive_r4.yaml; train_set.jsonl |

表达恢复汇总：69 个候选有历史自然语言表达，共 2388 条去重表达；22 个早期 VSS 候选只有人工批准 capability、无历史 anchors，已标 `NEEDS_ANCHOR_EXPANSION`，没有用 LLM 补造。

## 4. 当前 KNOWN_CONTROL_BYPASS expression 映射

| 当前 bypass expression | 恢复后 intent_id | 状态 | execution_eligible |
|---|---|---|---|
| 打开运动模式 | DRIVING_MODE_SET | UNIQUE | False |
| 切换到运动模式 | DRIVING_MODE_SET | UNIQUE | False |
| 开启运动模式 | DRIVING_MODE_SET | UNIQUE | False |
| 进入运动模式 | DRIVING_MODE_SET | UNIQUE | False |
| 把驾驶模式切到运动模式 | DRIVING_MODE_SET | UNIQUE | False |
| 打开经济模式 | DRIVING_MODE_SET | UNIQUE | False |
| 切换到经济模式 | DRIVING_MODE_SET | UNIQUE | False |
| 开启舒适模式 | DRIVING_MODE_SET | UNIQUE | False |
| 切换到舒适模式 | DRIVING_MODE_SET | UNIQUE | False |
| 切换驾驶模式 | DRIVING_MODE_SET | UNIQUE | False |
| 驾驶模式改成运动 | DRIVING_MODE_SET | UNIQUE | False |
| 驾驶模式切到经济 | DRIVING_MODE_SET | UNIQUE | False |
| 驾驶模式设成舒适 | DRIVING_MODE_SET | UNIQUE | False |
| 开启越野模式 | DRIVING_MODE_SET | UNIQUE | False |
| 切换到雪地模式 | DRIVING_MODE_SET | UNIQUE | False |
| 开启沙地模式 | DRIVING_MODE_SET | UNIQUE | False |
| 切换到个性化驾驶模式 | DRIVING_MODE_SET | UNIQUE | False |
| 运动模式激活 | DRIVING_MODE_SET | UNIQUE | False |
| 切换车辆驾驶模式 | DRIVING_MODE_SET | UNIQUE | False |
| 调整驾驶模式 | DRIVING_MODE_SET | UNIQUE | False |

无 `AMBIGUOUS_KNOWN_MAPPING`。但接入规则必须要求‘变速箱/传动性能’显式词面才能选择 TRANSMISSION_PERFORMANCE_MODE_SET，避免与普通驾驶模式混淆。

## 5. 与 Formal 的边界相邻项与错误合并防护

| Known candidate | Formal 邻居 | 不得合并原因 |
|---|---|---|
| MIRROR_ADJUSTMENT_LOCK | ["MIRROR_HEATING_ON","MIRROR_HEATING_OFF","MIRROR_FOLD","MIRROR_UNFOLD","MIRROR_SET_ANGLE"] | 同 target 不同 control_attribute/action |
| MIRROR_ADJUSTMENT_UNLOCK | ["MIRROR_HEATING_ON","MIRROR_HEATING_OFF","MIRROR_FOLD","MIRROR_UNFOLD","MIRROR_SET_ANGLE"] | 同 target 不同 control_attribute/action |
| HOOD_SET_POSITION | ["HOOD_OPEN","HOOD_CLOSE"] | 同 target 不同 control_attribute/action |
| LOW_RANGE_ENABLE | ["GEAR_SET","GEAR_CHANGE_MODE_SET"] | 同 target 不同 control_attribute/action |
| LOW_RANGE_DISABLE | ["GEAR_SET","GEAR_CHANGE_MODE_SET"] | 同 target 不同 control_attribute/action |
| TORQUE_DISTRIBUTION_SET | ["GEAR_SET","GEAR_CHANGE_MODE_SET"] | 同 target 不同 control_attribute/action |
| TRANSMISSION_PERFORMANCE_MODE_SET | ["GEAR_SET","GEAR_CHANGE_MODE_SET"] | 同 target 不同 control_attribute/action |
| DRIVING_MODE_SET | ["GEAR_CHANGE_MODE_SET"] | ‘模式’词面相似但 capability/target/mode contract 不同 |
| STEERING_WHEEL_HEATING_OFF | ["STEERING_WHEEL_SET_EXTENSION","STEERING_WHEEL_SET_TILT"] | 同 target 不同 control_attribute/action |
| STEERING_WHEEL_HEATING_ON | ["STEERING_WHEEL_SET_EXTENSION","STEERING_WHEEL_SET_TILT"] | 同 target 不同 control_attribute/action |

特别是：`GEAR_CHANGE_MODE_SET` 的 target=`TRANSMISSION`、attribute=`GEAR_CHANGE_MODE`、MODE=`MANUAL|AUTOMATIC`；`DRIVING_MODE_SET` 的 target=`DRIVING_MODE`、attribute=`MODE`，表达为运动/舒适/雪地等驾驶风格；二者不能因为都叫“模式”而合并。`TRANSMISSION_PERFORMANCE_MODE_SET` 只接受显式变速箱性能语义。

历史 driving-mode anchors 包含“经济/雪地/越野”，但 archive 的 `KNOWN_DRIVING_MODE_SOURCE_MODE` 没有完整列出这些值。这是历史资产内部合同缺口，候选仍能稳定识别为 DRIVING_MODE_SET，但未来接入前必须单独评审 MODE 合同；本轮没有静默扩展生产 contract。

## 6. Unknown / OOD / Incomplete 边界

1. 明确本地车控且命中 71 Formal：FORMAL；是否执行继续由缺槽、Evidence/Safety/Decision 决定。
2. 明确本地车控且命中 91 候选：KNOWN_NON_EXECUTABLE；最终行为 PASS，execution_eligible=false，永不签 token、永不进真实车辆执行。
3. 车辆知识问答、状态解释、闲聊、天气等：NON_CONTROL/信息类；不能因为提到汽车就硬分到 Known Control。
4. 能力无法命中 Formal/Known：UNKNOWN/OOD → REVIEW。能力可识别但参数不足：保留该 intent 类别并进入 clarification；不得降级或抢占 Formal。

## 7. 代表性 20 条输入分类

| raw_text | target_intent_id | 分类 | slots | execution_eligible |
|---|---|---|---|---|
| 打开运动模式 | DRIVING_MODE_SET | KNOWN_NON_EXECUTABLE | {"MODE":"运动"} | False |
| 切换到经济模式 | DRIVING_MODE_SET | KNOWN_NON_EXECUTABLE | {"MODE":"经济"} | False |
| 切换到雪地模式 | DRIVING_MODE_SET | KNOWN_NON_EXECUTABLE | {"MODE":"雪地"} | False |
| 空调调到22度 | HVAC_SET_TEMPERATURE | KNOWN_NON_EXECUTABLE | {"VALUE":"22°C"} | False |
| 打开座椅按摩 | SEAT_MASSAGE_ON | KNOWN_NON_EXECUTABLE | {} | False |
| 座椅加热开大一点 | SEAT_HEATING_SET_LEVEL | KNOWN_NON_EXECUTABLE | {"VALUE":"开大一点"} | False |
| 屏幕调亮 | DISPLAY_SET_BRIGHTNESS | KNOWN_NON_EXECUTABLE | {"VALUE":"调亮"} | False |
| 打开方向盘加热 | STEERING_WHEEL_HEATING_ON | KNOWN_NON_EXECUTABLE | {} | False |
| 打开香氛 | FRAGRANCE_ON | KNOWN_NON_EXECUTABLE | {} | False |
| 打开车载冰箱 | REFRIGERATOR_ON | KNOWN_NON_EXECUTABLE | {} | False |
| 关闭空气净化功能 | AIR_PURIFIER_OFF | KNOWN_NON_EXECUTABLE | {} | False |
| 氛围灯调到红色 | AMBIENT_LIGHT_SET_COLOR | KNOWN_NON_EXECUTABLE | {"VALUE":"红色"} | False |
| 打开自动阅读灯 | READING_LIGHT_SET_MODE | KNOWN_NON_EXECUTABLE | {"MODE":"自动"} | False |
| 把空气净化器风速调低 | AIR_PURIFIER_SET_FAN_SPEED | KNOWN_NON_EXECUTABLE | {"VALUE":"调低"} | False |
| 屏幕调成夜间模式 | DISPLAY_SET_MODE | KNOWN_NON_EXECUTABLE | {"MODE":"夜间模式"} | False |
| 车载冰箱调到热饮 | REFRIGERATOR_SET_MODE | KNOWN_NON_EXECUTABLE | {"MODE":"热饮"} | False |
| 香氛位置调到2 | FRAGRANCE_SET_SCENT | KNOWN_NON_EXECUTABLE | {"VALUE":"2"} | False |
| 调低装饰灯的亮度 | INTERIOR_LIGHT_SET_BRIGHTNESS | KNOWN_NON_EXECUTABLE | {"VALUE":"调低"} | False |
| 阅读灯亮度调低 | READING_LIGHT_SET_BRIGHTNESS | KNOWN_NON_EXECUTABLE | {"VALUE":"调低"} | False |
| 空气净化器变成自动模式 | AIR_PURIFIER_SET_MODE | KNOWN_NON_EXECUTABLE | {"MODE":"自动"} | False |

## 8. Formal 不被 Known 抢占的反向检查

| raw_text | Formal intent | 分类 | slots | 当前输入可进入执行条件判断 |
|---|---|---|---|---|
| 打开右前车门 | DOOR_OPEN | FORMAL | {"AREA":"RIGHT_FRONT"} | True |
| 关闭前照灯 | HEADLIGHT_SET_MODE | FORMAL | {"MODE":"OFF"} | True |
| 加速 | ACCELERATE | FORMAL | {} | True |
| 减速 | DECELERATE | FORMAL | {} | True |
| 打开车窗 | WINDOW_OPEN | FORMAL | {} | True |
| 设置车窗位置 | WINDOW_SET_POSITION | FORMAL | {"VALUE":null} | False |
| 按P挡 | GEAR_SET | FORMAL | {"MODE":"P"} | True |
| 自动泊车 | AUTO_PARK_ENABLE | FORMAL | {} | True |

`设置车窗位置` 缺少必需 VALUE，因此 execution_eligible=false 并进入 clarification，但 intent 仍是 Formal `WINDOW_SET_POSITION`；这正是“Formal 暂时不能执行不能误降级”的边界。

## 9. 过度原子化复核

- archive 未出现 `SPORT_MODE_ON`、`ECO_MODE_ON`、`SNOW_MODE_ON`；统一使用 `DRIVING_MODE_SET + MODE`。
- 温度、亮度、等级、位置分别使用 VALUE/MODE/AREA 与历史 contract，没有按具体数字或枚举值拆成 Intent。
- ON/OFF、LOCK/UNLOCK、OPEN/CLOSE 是 action 语义边界，并与 Formal Registry 命名一致；本轮不建议合并。
- 因而合并建议为：**无强制合并项**。后续可讨论 action-state 参数化，但那属于跨 Formal/Known 的命名体系迁移，不在本轮权限内。

## 10. 下一步接入 Stage1 Top8 / 3B selector（仅建议）

1. 先冻结本候选 YAML 的人工评审版与 hash；它当前明确 `runtime_registry=false`，不能直接加载。
2. Stage1 建立两个只读召回域：71 Formal 与 91 Known；候选携带 `semantic_class`，Top8 可以混合召回但不得丢失来源域。
3. 3B selector 输出 `intent_id + semantic_class + slots + confidence`。Formal 继续走既有 Evidence/Safety/Decision；Known 只到语义 PASS，强制 execution_eligible=false；Unknown/低置信度进入 REVIEW/clarification。
4. 增加冲突优先级：完整 Formal capability match 优先；同 target 时比较 control_attribute；驾驶模式按第 5 节词面边界；禁止仅靠 target/name 合并。
5. 离线验收至少覆盖本报告 20 条、8 条 Formal 反向样例、20 条当前 bypass anchors、所有无 anchor 的 22 个 NEEDS_ANCHOR_EXPANSION 项。未补足真实 anchors 前，后 22 项不得宣称可稳定自然语言召回。
6. 另开 Runtime migration 变更，单独评审 orchestrator、selector contract 和审计字段；不得在本轮顺手修改 SafetyGate、Authorization、Execution、HNSW 或 71 R4。

## 11. 本轮变更声明

仅新增：

- `data/nlu/spec/audits/known_non_executable_intent_recovery.md`
- `data/nlu/spec/audits/known_non_executable_intents_candidate.yaml`

未实施 Runtime migration；未修改当前 71 R4；未修改任何生产文件。
