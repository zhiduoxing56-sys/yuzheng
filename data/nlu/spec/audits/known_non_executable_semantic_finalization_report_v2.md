# Known Non-Executable Intent 最终收口报告 v2

> 最终语义冻结候选，非运行时资产；旧 v1 资产未覆盖。

## 最终结果

- Formal：71
- Known Non-Executable：78
- 最终稳定已知识别空间：149
- READY：78；NEEDS_ANCHOR_REVIEW / NEEDS_SCHEMA_REVIEW / BOUNDARY_REVIEW / BLOCKED：均为 0
- 13 个产品删除意图已从最终冻结候选彻底排除，独立保留产品移除审计，不建别名、不合并、不删除历史源资产。

## 23 条生成人工审核锚点

- 原样批准：16
- 修改后批准：7
- 拒绝：0
- 总计：23

全部来源均为 `GENERATED_HUMAN_APPROVED`，并保留原生成文本、批准文本和审批动作；没有伪装成历史表达。

## Driving Mode

- 已冻结 15 个整车驾驶风格/路况模式值。
- 智能、纯电、混动、四驱禁止自动通过；相关历史表达共 10 条从活跃锚点移出。
- 3 条缺 MODE 表达改为 REVIEW 验收用例；“仪表切换为驾驶模式”因目标异常隔离。
- `GEAR_CHANGE_MODE_SET` 经真实 Formal 注册表确认仍仅为 `MANUAL/AUTOMATIC`。

## 边界冻结

后视镜调节权限、前舱盖确定开度、方向盘加热、驻车锁、ABS/EBA 对象守卫均已写入最终语义合同。驻车制动真实 Formal ID 为 `PARKING_BRAKE_APPLY/RELEASE` 及自动施加开关；P 挡为 `GEAR_SET`。

## 历史隔离

原 89 条隔离挂靠全部延续为 `CONTINUE_QUARANTINE_BY_PRODUCT_DECISION`，静默恢复权限为 false。香氛位置和空气净化开最大继续走 REVIEW。

## 自动验收

| 校验 | 结果 |
| --- | --- |
| formal_count_is_71 | PASS |
| final_known_count_is_78 | PASS |
| removed_13_occurrence_in_final_freeze_is_zero | PASS |
| known_78_ids_globally_unique | PASS |
| formal_known_id_overlap_is_zero | PASS |
| all_78_ready | PASS |
| approved_generated_anchors_are_16_as_is_7_edited_0_rejected | PASS |
| approved_generated_anchor_texts_match_product_decision | PASS |
| quarantined_89_not_silently_restored | PASS |
| unapproved_1402_hash_candidate_usage_is_zero | PASS |
| driving_mode_forbidden_values_not_auto_pass | PASS |
| gear_change_mode_remains_manual_automatic_only | PASS |
| park_boundaries_use_real_formal_ids | PASS |
| hood_open_close_position_boundary_frozen | PASS |
| abs_eba_object_guards_exist | PASS |
| all_78_non_executable_contract | PASS |
| removed_13_textual_occurrence_in_final_freeze_is_zero | PASS |
| protected_production_file_hashes_unchanged | PASS |
| production_runtime_files_unchanged | PASS |

## 产物

- `data/nlu/spec/audits/known_non_executable_semantic_freeze_final_v2.yaml`
- `data/nlu/spec/audits/known_non_executable_product_removals_v2.yaml`
- `data/nlu/spec/audits/known_non_executable_anchor_quarantine_final_v2.jsonl`
- `data/nlu/spec/audits/known_non_executable_semantic_review_cases_v2.yaml`
- `data/nlu/spec/audits/known_non_executable_semantic_finalization_audit_v2.json`
- `data/nlu/spec/audits/known_non_executable_runtime_migration_readiness_v2.md`

## 生产修改确认

本轮未修改任何生产运行时代码、Formal 注册表、生产 cards/anchors、安全门、授权、令牌、执行、证据链、强制召回、因果图或前端；未开始运行时迁移。
