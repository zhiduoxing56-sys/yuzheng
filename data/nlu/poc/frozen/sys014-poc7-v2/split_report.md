# sys014-poc7-v2 切分报告

## 切分规模

| Split | 样本 | Family | Split group | 比例 |
|---|---|---|---|---|
| TRAIN | 587 | 456 | 329 | 69.14% |
| VALIDATION | 129 | 96 | 60 | 15.19% |
| TEST | 133 | 122 | 82 | 15.67% |

## 7-Intent 覆盖

| Intent | TRAIN + | TRAIN - | TRAIN MULTI | VAL + | VAL - | VAL MULTI | TEST + | TEST - | TEST MULTI |
|---|---|---|---|---|---|---|---|---|---|
| DOOR_OPEN | 51 | 4 | 25 | 11 | 0 | 7 | 10 | 14 | 5 |
| DOOR_CLOSE | 52 | 12 | 27 | 12 | 6 | 3 | 8 | 0 | 12 |
| WINDOW_OPEN | 41 | 11 | 6 | 7 | 2 | 2 | 12 | 2 | 4 |
| WINDOW_SET_POSITION | 48 | 12 | 21 | 13 | 0 | 6 | 7 | 6 | 3 |
| HEADLIGHT_OFF | 53 | 12 | 27 | 11 | 5 | 6 | 8 | 1 | 3 |
| ACCELERATE | 55 | 12 | 24 | 12 | 5 | 4 | 8 | 1 | 3 |
| BRAKE | 47 | 12 | 22 | 10 | 6 | 6 | 8 | 0 | 3 |

## Intent structure

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| AMBIGUOUS | 48 | 9 | 3 |
| MULTI | 76 | 17 | 23 |
| SINGLE | 463 | 103 | 107 |

## Scope

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| AMBIGUOUS_CONTROL | 48 | 9 | 3 |
| IN_SCOPE_CONTROL | 498 | 117 | 95 |
| NON_CONTROL | 17 | 2 | 6 |
| UNKNOWN_CONTROL | 24 | 1 | 29 |

## Slots

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| AREA | 211 | 52 | 29 |
| NEGATION | 76 | 24 | 30 |
| VALUE | 81 | 19 | 16 |

## Source type

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| SYNTHETIC_TEMPLATE | 587 | 129 | 63 |
| TEST_ASSET | 0 | 0 | 70 |

## 语义安全类型

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| mixed_negation_multi | 1 | 0 | 4 |
| negated_single | 75 | 24 | 24 |
| positive_single | 347 | 76 | 61 |

## UNKNOWN_CONTROL 派生类型

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| UNKNOWN_EXTERNAL_CONTROL | 7 | 0 | 1 |
| UNKNOWN_KNOWN_REGISTRY_OUTSIDE_POC | 17 | 1 | 28 |

## Negated 8/2/2 目标与合法 group 约束

| Intent | TRAIN - | VAL - | TEST - | 结论 |
|---|---|---|---|---|
| DOOR_OPEN | 4 | 0 | 14 | BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT；不可拆 group=2*+4+12*（* 为 TEST_ASSET forced TEST） |
| DOOR_CLOSE | 12 | 6 | 0 | BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT；不可拆 group=12+6（* 为 TEST_ASSET forced TEST） |
| WINDOW_OPEN | 11 | 2 | 2 | PASS |
| WINDOW_SET_POSITION | 12 | 0 | 6 | BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT；不可拆 group=12+6（* 为 TEST_ASSET forced TEST） |
| HEADLIGHT_OFF | 12 | 5 | 1 | BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT；不可拆 group=1*+5+12（* 为 TEST_ASSET forced TEST） |
| ACCELERATE | 12 | 5 | 1 | BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT；不可拆 group=12+1*+5（* 为 TEST_ASSET forced TEST） |
| BRAKE | 12 | 6 | 0 | BALANCE_BLOCKED_BY_LEAKAGE_CONSTRAINT；不可拆 group=12+6（* 为 TEST_ASSET forced TEST） |

同一机械模板仅替换 AREA/NEGATION 的样本不得跨 split。因而只有两个不可拆 group 的 Intent 不可能同时覆盖三个 split；此处保留零泄漏，未为满足数字拆组。

## 质量结论

- v1 的 WINDOW_OPEN、HEADLIGHT_OFF、ACCELERATE、BRAKE 极端 split 失衡已通过合法 group 重建修正。
- 每个 Intent 的 positive SINGLE 满足 TRAIN/VALIDATION/TEST 至少 30/5/5。
- negated SINGLE 以 8/2/2 为软目标；不可满足项已逐 Intent 给出真实 group 约束原因。
- WINDOW_SET_POSITION 在 VALIDATION 与 TEST 均有 VALUE；WINDOW_OPEN 的 VALUE slot 为 0。
- TEST_ASSET_IN_TRAIN=0；Safety Gold 未参与切分优化。
