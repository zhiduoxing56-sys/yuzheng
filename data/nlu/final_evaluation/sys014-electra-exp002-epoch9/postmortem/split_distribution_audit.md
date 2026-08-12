# SYS-014 Stage 4D-A.1 Split Distribution Audit

本报告只读取 frozen v2 标签和已保存 prediction artifacts；没有模型推理、训练或 Safety Gold 访问。

## Scope

| Label | Train | Validation | Test |
|---|---:|---:|---:|
| IN_SCOPE_CONTROL | 498 (84.84%) | 117 (90.70%) | 95 (71.43%) |
| NON_CONTROL | 17 (2.90%) | 2 (1.55%) | 6 (4.51%) |
| UNKNOWN_CONTROL | 24 (4.09%) | 1 (0.78%) | 29 (21.80%) |
| AMBIGUOUS_CONTROL | 48 (8.18%) | 9 (6.98%) | 3 (2.26%) |

## Structure

| Label | Train | Validation | Test |
|---|---:|---:|---:|
| SINGLE | 463 (78.88%) | 103 (79.84%) | 107 (80.45%) |
| MULTI | 76 (12.95%) | 17 (13.18%) | 23 (17.29%) |
| AMBIGUOUS | 48 (8.18%) | 9 (6.98%) | 3 (2.26%) |

## Intent

| Label | Train | Validation | Test |
|---|---:|---:|---:|
| DOOR_OPEN | 55 (9.37%) | 11 (8.53%) | 24 (18.05%) |
| DOOR_CLOSE | 64 (10.90%) | 18 (13.95%) | 8 (6.02%) |
| WINDOW_OPEN | 52 (8.86%) | 9 (6.98%) | 14 (10.53%) |
| WINDOW_SET_POSITION | 60 (10.22%) | 13 (10.08%) | 13 (9.77%) |
| HEADLIGHT_OFF | 65 (11.07%) | 16 (12.40%) | 9 (6.77%) |
| ACCELERATE | 67 (11.41%) | 17 (13.18%) | 9 (6.77%) |
| BRAKE | 59 (10.05%) | 16 (12.40%) | 8 (6.02%) |
| null | 165 (28.11%) | 29 (22.48%) | 48 (36.09%) |

## Sentence Negation

| Label | Train | Validation | Test |
|---|---:|---:|---:|
| NEGATED | 75 (12.78%) | 24 (18.60%) | 24 (18.05%) |
| NOT_NEGATED | 347 (59.11%) | 76 (58.91%) | 61 (45.86%) |
| NOT_APPLICABLE | 165 (28.11%) | 29 (22.48%) | 48 (36.09%) |

## Slot spans

| Slot | Train | Validation | Test |
|---|---:|---:|---:|
| AREA | 211 (57.34% of spans) | 52 (54.74% of spans) | 29 (38.67% of spans) |
| VALUE | 81 (22.01% of spans) | 19 (20.00% of spans) | 16 (21.33% of spans) |
| NEGATION | 76 (20.65% of spans) | 24 (25.26% of spans) | 30 (40.00% of spans) |

## Should-abstain

| Split | Count | Ratio |
|---|---:|---:|
| TRAIN | 165 | 28.11% |
| VALIDATION | 29 | 22.48% |
| TEST | 48 | 36.09% |

## Critical shift

- Validation UNKNOWN_CONTROL: 1/129 (0.007752).
- Test UNKNOWN_CONTROL: 29/133 (0.218045).
- Count support ratio: 29.0x; prevalence ratio: 28.127820x; prevalence gap: 0.210293.
- Test UNKNOWN_CONTROL 全部来自 TEST_ASSET；Validation 的唯一 UNKNOWN_CONTROL 来自 SYNTHETIC_TEMPLATE。
- leakage audit 与重建 group 检查均显示 family/template/mechanical/split_group 跨 split 重叠为 0。

## Family coverage summary

| Category | Split | Samples | Families | Templates | Mechanical | Groups |
|---|---|---:|---:|---:|---:|---:|
| UNKNOWN_CONTROL | TRAIN | 24 | 24 | 24 | 24 | 24 |
| UNKNOWN_CONTROL | VALIDATION | 1 | 1 | 1 | 1 | 1 |
| UNKNOWN_CONTROL | TEST | 29 | 29 | 29 | 24 | 24 |
| MULTI | TRAIN | 76 | 29 | 76 | 29 | 29 |
| MULTI | VALIDATION | 17 | 7 | 17 | 7 | 7 |
| MULTI | TEST | 23 | 19 | 23 | 14 | 14 |
| VALUE | TRAIN | 81 | 59 | 28 | 14 | 14 |
| VALUE | VALIDATION | 19 | 15 | 9 | 5 | 5 |
| VALUE | TEST | 16 | 10 | 7 | 5 | 5 |
| NEGATION | TRAIN | 76 | 33 | 14 | 14 | 14 |
| NEGATION | VALIDATION | 24 | 10 | 6 | 6 | 6 |
| NEGATION | TEST | 30 | 24 | 11 | 10 | 10 |

结论：v2 成功实现零 family leakage，但把独立 TEST_ASSET families 整组强制放入 Test；在 UNKNOWN_CONTROL 上形成了 Validation=1、Test=29 的严重选择分布偏移。
