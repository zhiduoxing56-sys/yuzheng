# SYS-014 Full Registry Post-Approval Audit

- audit_status: **PASS**
- timestamp: `2026-08-09T09:17:53+08:00`
- registry_version: `sys-014-stage2.1-draft-3`
- NEW_REGISTRY_SHA256: `0127af1d64b33a9e517537ccd458905fcc6af3414cc70701fc362474a4ec2739`
- runtime_loading_allowed: `false`

## Summary

| Metric | Value |
|---|---:|
| HUMAN_DECISIONS_APPLIED | `YES` |
| FRR_APPROVE_COUNT | `9` |
| FRR_REJECT_COUNT | `2` |
| FRR_MODIFY_COUNT | `1` |
| OLD_INTENT_COUNT | `95` |
| NEW_INTENT_COUNT | `93` |
| OLD_VSS_INTENT_COUNT | `87` |
| NEW_VSS_INTENT_COUNT | `85` |
| FINAL_PROJECT_NATIVE_INTENT_COUNT | `8` |
| FINAL_APPROVED_VSS_CAPABILITY_COUNT | `44` |
| REMOVED_INTENTS | `HEADLIGHT_ON, HEADLIGHT_OFF` |
| ADDED_INTENTS | `` |
| CONTRACT_CHANGED_INTENTS | `SEAT_LONGITUDINAL_SET_POSITION, SEAT_TILT_SET_ANGLE, SEAT_BACKREST_SET_ANGLE, SEAT_HEIGHT_SET_POSITION, SEAT_LUMBAR_SET_HEIGHT, SEAT_LUMBAR_SET_SUPPORT, GEAR_SET, CRUISE_SET_GAP, HEADLIGHT_SET_MODE, WIPER_SET_SENSITIVITY` |
| CONSISTENCY_LINKAGE_REPAIRS | `WIPER_SET_SENSITIVITY: mode_contract=WIPER` |
| NEW_REGISTRY_SHA256 | `0127af1d64b33a9e517537ccd458905fcc6af3414cc70701fc362474a4ec2739` |
| LEGACY_REFERENCE_COUNT | `8330` |
| LEGACY_REFERENCE_FILE_COUNT | `182` |
| UNRESOLVED_BLOCKER_COUNT | `0` |
| REGISTRY_CONSISTENCY_PASS | `YES` |
| RUNTIME_LOADING_ALLOWED | `NO` |
| DATASET_GENERATED | `NO` |
| MODEL_TRAINING_EXECUTED | `NO` |
| RUNTIME_MODIFIED | `NO` |
| SAFETY_GOLD_OPENED | `NO` |
| FULL_REGISTRY_READY_FOR_DATASET_DESIGN | `YES` |

## Human decisions

| CHANGE_ID | Decision |
|---|---|
| FRR-001 | **REJECT** |
| FRR-002 | **REJECT** |
| FRR-003 | **APPROVE** |
| FRR-004 | **APPROVE** |
| FRR-005 | **APPROVE** |
| FRR-006 | **APPROVE** |
| FRR-007 | **APPROVE** |
| FRR-008 | **APPROVE** |
| FRR-009 | **APPROVE** |
| FRR-010 | **MODIFY** |
| FRR-011 | **APPROVE** |
| FRR-012 | **APPROVE** |

## Consistency checks

| # | Check | Status | Evidence |
|---:|---|---|---|
| 1 | intent_id unique | **PASS** | `{"count":93}` |
| 2 | total Intent = 93 | **PASS** | `{"actual":93}` |
| 3 | VSS-derived Intent = 85 | **PASS** | `{"actual":85}` |
| 4 | Project-native Intent = 8 | **PASS** | `{"actual":8}` |
| 5 | Approved VSS capability = 44 | **PASS** | `{"audit":44,"registry":44}` |
| 6 | User objects remain based on approved-44 audit | **PASS** | `{"DISTINCT_USER_CONTROL_OBJECT_COUNT":35,"source":"approved44_intent_expansion_audit.json"}` |
| 7 | All VSS-derived Intents trace to HUMAN_APPROVED capability | **PASS** | `{"failures":[]}` |
| 8 | No HUMAN_REJECTED source Intent | **PASS** | `{"basis":"Every VSS capability id is in the approved-44 set and authority is HUMAN_APPROVED_VSS/BOTH"}` |
| 9 | HEADLIGHT_ON absent from active intents | **PASS** | `{"active":false}` |
| 10 | HEADLIGHT_OFF absent from active intents | **PASS** | `{"active":false,"historical_poc_metadata_preserved":true}` |
| 11 | HEADLIGHT_SET_MODE contains full five-value MODE | **PASS** | `{"actual":["OFF","POSITION","DAYTIME_RUNNING_LIGHTS","AUTO","BEAM"]}` |
| 12 | LOW/HIGH/FOG beam intents remain independent | **PASS** | `{"required":["LOW_BEAM_ON","LOW_BEAM_OFF","HIGH_BEAM_ON","HIGH_BEAM_OFF","FOG_LIGHT_ON","FOG_LIGHT_OFF"],"missing":[]}` |
| 13 | GEAR_SET does not hardcode R -> REVERSE_GEAR_1 | **PASS** | `{"mapping":{"canonical_modes":["P","N","D","FORWARD_GEAR_N","REVERSE_GEAR_N"],"lexical_aliases":{"R":"VEHICLE_SPECIFIC_REVERSE_GEAR","倒挡":"VEHICLE_SPECIFIC_REVERSE_GEAR"},"vss_code_rules":{"P":126,"N":0,"D":127,"FORWARD_GEAR_N":"POSITIVE_INTEGER_N","REVERSE_GEAR_N":"NEGATIVE_INTEGER_N"},"physical_mapping_authority":"VehicleCapabilityMapping","vehicle_specific_validation_required":true,"prohibited_generic_mapping":"R -> REVERSE_GEAR_1"}}` |
| 14 | Five seat review items / six seat intents match approval | **PASS** | `{"checked_intents":["SEAT_LONGITUDINAL_SET_POSITION","SEAT_TILT_SET_ANGLE","SEAT_BACKREST_SET_ANGLE","SEAT_HEIGHT_SET_POSITION","SEAT_LUMBAR_SET_HEIGHT","SEAT_LUMBAR_SET_SUPPORT"],"failures":[]}` |
| 15 | CRUISE_SET_GAP matches VALUE XOR MODE | **PASS** | `{"actual":{"intent_id":"CRUISE_SET_GAP","chinese_name":"设置巡航跟车距离","capability_family":"ADAS_CRUISE_CONTROL","canonical_action":"设置","canonical_target":"巡航跟车距离","control_domain":"驾驶控制","risk_level":"R3","risk_tags":["巡航控制","跟车安全"],"allowed_areas":[],"value_contract":"FOLLOWING_GAP_VALUE_OPTIONAL","mode_contract":"CRUISE_GAP_LEVEL","conditional_slot_contract":"VALUE_XOR_MODE","required_slots":[],"optional_slots":["VALUE","MODE","NEGATION"],"scope_status":"IN_SCOPE","capability_origin":"VSS_AND_PROJECT","vss_capability_ids":["ADAS_CRUISE_CONTROL"],"vss_relation":"DIRECT","scope_authority":"BOTH","current_semantic_support":"NONE","current_evidence_support":"NONE","current_authorization_support":"NONE","current_execution_support":"NONE"}}` |
| 16 | Required/optional/conditional slots have no contradiction | **PASS** | `{"failures":[]}` |
| 17 | DIRECTION/MODE contracts are expressible by later Full NLU schema | **PASS** | `{"slot_types":["AREA","VALUE","DIRECTION","MODE","NEGATION"],"direction_contracts":{"SEAT_FORWARD_BACKWARD":["FORWARD","BACKWARD"],"SEAT_UP_DOWN":["UP","DOWN"],"LUMBAR_SUPPORT_MORE_LESS":["MORE","LESS"]},"conditional_slot_contracts":{"VALUE_OR_DIRECTION":{"rule":"AT_LEAST_ONE_OF","slots":["VALUE","DIRECTION"],"same_text_span_policy":"DISALLOW_SHARED_SPAN"},"VALUE_XOR_MODE":{"rule":"XOR","slots":["VALUE","MODE"],"jointly_present_exception":"ALLOW_ONLY_IF_DETERMINISTICALLY_CONSISTENT"}},"mode_mapping_contracts":["GEAR_VEHICLE_SPECIFIC","HEADLIGHT_MAIN_SWITCH"]}` |

## LEGACY_REFERENCE_AUDIT

- LEGACY_REFERENCE_COUNT: `8330`
- LEGACY_REFERENCE_FILE_COUNT: `182`
- token_counts: `{"HEADLIGHT_ON": 14, "HEADLIGHT_OFF": 8316}`
- action: `AUDIT_ONLY_NO_LEGACY_REWRITE`
- Current approval records, this audit, and the freeze manifest are excluded to prevent self-counting.

| Path | Classification | HEADLIGHT_ON | HEADLIGHT_OFF | Total | Modified |
|---|---|---:|---:|---:|---|
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_02_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 283 | 283 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_03_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 258 | 258 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_02_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 258 | 258 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/metrics_by_epoch.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 251 | 251 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_05_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 230 | 230 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_04_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 227 | 227 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_09_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 227 | 227 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_08_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 226 | 226 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_10_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 225 | 225 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_07_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 222 | 222 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_06_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 221 | 221 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_06_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 219 | 219 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_05_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 218 | 218 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_07_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 216 | 216 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_03_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 215 | 215 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_09_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 214 | 214 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_10_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 212 | 212 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_08_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 208 | 208 | NO |
| `data/nlu/final_evaluation/sys014-electra-exp002-epoch9/test/predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 206 | 206 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_04_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 203 | 203 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_05_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 197 | 197 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_06_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 193 | 193 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_07_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 192 | 192 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_08_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 192 | 192 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_09_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 192 | 192 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_10_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 192 | 192 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_04_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 191 | 191 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/metrics_by_epoch.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 186 | 186 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_03_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 185 | 185 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_02_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 180 | 180 | NO |
| `data/nlu/poc/candidate_pool.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 179 | 179 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/metrics_by_epoch.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 167 | 167 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/epoch_01_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 154 | 154 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/epoch_01_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 150 | 150 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/epoch_01_predictions.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 145 | 145 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v2/train.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 134 | 134 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v1/train.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 117 | 117 | NO |
| `data/nlu/poc/review_queue.md` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 93 | 93 | NO |
| `data/nlu/final_evaluation/sys014-electra-exp002-epoch9/postmortem/unknown_false_accept_analysis.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 87 | 87 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v1/validation.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 57 | 57 | NO |
| `data/nlu/final_evaluation/sys014-electra-exp002-epoch9/postmortem/multi_failure_analysis.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 48 | 48 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/training_log.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 35 | 35 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v2/validation.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 33 | 33 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/training_summary.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 21 | 21 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/training_summary.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 21 | 21 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp001/metrics_by_epoch.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 20 | 20 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/reporting_metrics.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 20 | 20 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/reporting_metrics.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 17 | 17 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/evaluation/validation/error_cases.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 14 | 14 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v2/dataset_manifest.json` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 14 | 14 | NO |
| `data/nlu/spec/audits/approved44_intent_expansion_audit.json` | HISTORICAL_AUDIT_REFERENCE | 6 | 8 | 14 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/evaluation/validation/error_cases.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 12 | 12 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp001/postmortem/negation_case_analysis.md` | LEGACY_DOC_REFERENCE | 0 | 12 | 12 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v1/safety_gold.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 12 | 12 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v2/safety_gold.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 12 | 12 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v2/test.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 12 | 12 | NO |
| `data/nlu/poc/safety_gold_candidates.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 12 | 12 | NO |
| `data/nlu/spec/audits/approved44_intent_expansion_audit.md` | HISTORICAL_AUDIT_REFERENCE | 5 | 6 | 11 | NO |
| `data/nlu/final_evaluation/sys014-electra-exp002-epoch9/test/error_cases.jsonl` | LEGACY_TEST_REFERENCE | 0 | 10 | 10 | NO |
| `tmp/step1-alignment/real_scenario_results.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 10 | 10 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/training_summary.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 7 | 7 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/reporting_metrics.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 6 | 6 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp001/postmortem/safety_error_trajectory.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 6 | 6 | NO |
| `scripts/apply_sys014_stage3b1.py` | LEGACY_CODE_REFERENCE | 0 | 6 | 6 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp001/postmortem/abstention_strategy_comparison.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 5 | 5 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v1/test.jsonl` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 5 | 5 | NO |
| `data/nlu/spec/audits/approved44_intent_expansion_audit.csv` | HISTORICAL_AUDIT_REFERENCE | 2 | 3 | 5 | NO |
| `scripts/nlu_training/stage4c_exp002.py` | LEGACY_CODE_REFERENCE | 0 | 5 | 5 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v1/dataset_manifest.json` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 4 | 4 | NO |
| `tmp/full-software-audit/live-api/07_review_correct_child/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 4 | 4 | NO |
| `data/nlu/final_evaluation/sys014-electra-exp002-epoch9/postmortem/split_distribution_audit.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 3 | 3 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v2/split_group_balance_diagnosis.md` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 3 | 3 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v2/split_report.md` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 3 | 3 | NO |
| `data/nlu/poc/human_review_applied_report.md` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 3 | 3 | NO |
| `docs/plans/2026-08-08-sys-014-nlu-label-design.md` | LEGACY_DOC_REFERENCE | 1 | 2 | 3 | NO |
| `scripts/nlu_training/stage4c_a1_postmortem.py` | LEGACY_CODE_REFERENCE | 0 | 3 | 3 | NO |
| `test-results/raw/20260804T232248Z/ambiguous_open-command.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 3 | 3 | NO |
| `test-results/raw/20260804T232248Z/comfort_ac_on-command.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 3 | 3 | NO |
| `test-results/raw/20260804T232248Z/door_open_moving-command.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 3 | 3 | NO |
| `test-results/raw/20260804T232248Z/door_open_stationary-command.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 3 | 3 | NO |
| `test-results/raw/20260804T232248Z/non_control_greeting-command.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 3 | 3 | NO |
| `tmp/full-software-audit/live-api/07_review_ambiguous/review_correct_response.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 3 | 3 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/training_log.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/exp001_vs_exp002_config_diff.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/manifest.json` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 2 | 2 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/preflight.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp001/best_validation_metrics.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp001/evaluation/validation/metrics.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `data/nlu/final_evaluation/sys014-electra-exp002-epoch9/test/metrics.json` | LEGACY_TEST_REFERENCE | 0 | 2 | 2 | NO |
| `scripts/freeze_sys014_poc7.py` | LEGACY_CODE_REFERENCE | 0 | 2 | 2 | NO |
| `scripts/nlu_training/stage4c_electra_exp001.py` | LEGACY_CODE_REFERENCE | 0 | 2 | 2 | NO |
| `scripts/nlu_training/stage4c_electra_exp002.py` | LEGACY_CODE_REFERENCE | 0 | 2 | 2 | NO |
| `test-results/raw/20260804T232248Z/ambiguous_open-presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `test-results/raw/20260804T232248Z/comfort_ac_on-presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `test-results/raw/20260804T232248Z/door_open_moving-presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `test-results/raw/20260804T232248Z/door_open_stationary-presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `test-results/raw/20260804T232248Z/non_control_greeting-presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/01_query_speed/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/01_query_speed/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/01_query_speed/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/01_query_speed/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/02_play_music/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/02_play_music/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/02_play_music/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/02_play_music/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/03_parked_open_door/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/03_parked_open_door/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/03_parked_open_door/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/03_parked_open_door/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/04_moving_open_door/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/04_moving_open_door/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/04_moving_open_door/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/04_moving_open_door/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/05_bypass_open_door/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/05_bypass_open_door/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/05_bypass_open_door/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/05_bypass_open_door/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/06_change_lane_left/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/06_change_lane_left/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/06_change_lane_left/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/06_change_lane_left/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_ambiguous/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_ambiguous/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_ambiguous/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_ambiguous/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_confirm_child/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_confirm_child/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_confirm_child/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_confirm_child/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_correct_child/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_correct_child/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/07_review_correct_child/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/08_real_wav/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/08_real_wav/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/08_real_wav/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/08_real_wav/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/09_review_cancel_source/audit_detail.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/09_review_cancel_source/presentation.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/09_review_cancel_source/presentation_after_cancel.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/09_review_cancel_source/presentation_second.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `tmp/full-software-audit/live-api/09_review_cancel_source/timeline.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 2 | 2 | NO |
| `SYSTEM_CORRECTNESS_BASELINE_AUDIT.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |
| `backend/tests/stage3/test_stage3_scenarios.py` | LEGACY_TEST_REFERENCE | 0 | 1 | 1 | NO |
| `config/safety_rules.yaml` | LEGACY_CONFIG_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/checkpoints/best/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/checkpoints/closest_safety_diagnostic/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/checkpoints/last/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp001/diagnostics/stage4c_b1/stage4c_b1_diagnosis.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/checkpoints/best/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/checkpoints/closest_exp002_diagnostic/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/checkpoints/closest_safety_diagnostic/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/checkpoints/last/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/evaluation/validation/error_cases.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-electra-exp002/training_log.jsonl` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp001/checkpoints/last/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/checkpoints/closest_safety_diagnostic/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/checkpoints/last/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/experiments/sys014-poc7-rbt3-exp002/exp001_vs_exp002.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/final_evaluation/sys014-electra-exp002-epoch9/postmortem/split_distribution_audit.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/final_evaluation/sys014-electra-exp002-epoch9/postmortem/stage4d_a1_postmortem.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/poc/coverage_report.md` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 1 | 1 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v1/README.md` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 1 | 1 | NO |
| `data/nlu/poc/frozen/sys014-poc7-v1/split_report.md` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 1 | 1 | NO |
| `data/nlu/poc/stage3b1_semantic_cleanup_report.md` | PROTECTED_HISTORICAL_ARTIFACT | 0 | 1 | 1 | NO |
| `data/nlu/spec/intent_registry_draft.yaml` | REGISTRY_HISTORICAL_POC_METADATA | 0 | 1 | 1 | NO |
| `data/nlu/training_design/dry_run_report.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/training_design/label_mapping.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `data/nlu/training_design/train_distribution.json` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `docs/阶段三验收说明.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |
| `docs/阶段四验收说明.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |
| `scripts/freeze_sys014_poc7_v2.py` | LEGACY_CODE_REFERENCE | 0 | 1 | 1 | NO |
| `scripts/nlu_training/labels.py` | LEGACY_CODE_REFERENCE | 0 | 1 | 1 | NO |
| `scripts/nlu_training/stage4d_a1_postmortem.py` | LEGACY_CODE_REFERENCE | 0 | 1 | 1 | NO |
| `scripts/validate_nlu_dataset.py` | LEGACY_CODE_REFERENCE | 0 | 1 | 1 | NO |
| `tmp/stage4_1_package_final/backend/tests/stage3/test_stage3_scenarios.py` | LEGACY_TEST_REFERENCE | 0 | 1 | 1 | NO |
| `tmp/stage4_1_package_final/config/safety_rules.yaml` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `tmp/stage4_1_package_final/docs/阶段三验收说明.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |
| `tmp/stage4_1_package_final/docs/阶段四验收说明.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |
| `tmp/stage4_1_package_scan/backend/tests/stage3/test_stage3_scenarios.py` | LEGACY_TEST_REFERENCE | 0 | 1 | 1 | NO |
| `tmp/stage4_1_package_scan/config/safety_rules.yaml` | LEGACY_DATA_OR_MANIFEST_REFERENCE | 0 | 1 | 1 | NO |
| `tmp/stage4_1_package_scan/docs/阶段三验收说明.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |
| `tmp/stage4_1_package_scan/docs/阶段四验收说明.md` | LEGACY_DOC_REFERENCE | 0 | 1 | 1 | NO |

## Freeze result

- status: `FROZEN_FOR_FULL_DATASET_BUILD`
- FULL_REGISTRY_READY_FOR_DATASET_DESIGN: `YES`
- This freeze does not authorize runtime loading, dataset generation, model training, Validator implementation, HTTP changes, or Safety Gold access.
