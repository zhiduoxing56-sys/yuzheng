# sys014-poc7-v1 切分报告

## 切分规模

| Split | 样本 | Family | Split group | 比例 |
|---|---|---|---|---|
| TRAIN | 582 | 252 | 158 | 68.55% |
| VALIDATION | 126 | 60 | 50 | 14.84% |
| TEST | 141 | 93 | 61 | 16.61% |

## 7-Intent 覆盖

| Intent | TRAIN + | TRAIN - | TRAIN MULTI | VAL + | VAL - | VAL MULTI | TEST + | TEST - | TEST MULTI |
|---|---|---|---|---|---|---|---|---|---|
| DOOR_OPEN | 59 | 4 | 26 | 3 | 0 | 6 | 10 | 14 | 5 |
| DOOR_CLOSE | 66 | 12 | 23 | 3 | 6 | 10 | 3 | 0 | 9 |
| WINDOW_OPEN | 4 | 10 | 4 | 2 | 3 | 3 | 54 | 2 | 5 |
| WINDOW_SET_POSITION | 58 | 12 | 24 | 5 | 6 | 3 | 5 | 0 | 3 |
| HEADLIGHT_OFF | 50 | 12 | 20 | 21 | 5 | 13 | 1 | 1 | 3 |
| ACCELERATE | 60 | 12 | 27 | 13 | 5 | 3 | 2 | 1 | 1 |
| BRAKE | 60 | 12 | 24 | 3 | 6 | 4 | 2 | 0 | 3 |

## Intent structure

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| AMBIGUOUS | 48 | 9 | 3 |
| MULTI | 74 | 21 | 21 |
| SINGLE | 460 | 96 | 117 |

## Scope

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| AMBIGUOUS_CONTROL | 48 | 9 | 3 |
| IN_SCOPE_CONTROL | 505 | 102 | 103 |
| NON_CONTROL | 14 | 5 | 6 |
| UNKNOWN_CONTROL | 15 | 10 | 29 |

## Slots

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| AREA | 209 | 23 | 60 |
| NEGATION | 75 | 31 | 24 |
| VALUE | 94 | 14 | 8 |

## Source type

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| SYNTHETIC_TEMPLATE | 582 | 126 | 71 |
| TEST_ASSET | 0 | 0 | 70 |

## 语义安全类型

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| mixed_negation_multi | 1 | 0 | 4 |
| negated_single | 74 | 31 | 18 |
| positive_single | 357 | 50 | 77 |

## UNKNOWN_CONTROL 派生类型

| 类别 | TRAIN | VALIDATION | TEST |
|---|---|---|---|
| UNKNOWN_EXTERNAL_CONTROL | 4 | 3 | 1 |
| UNKNOWN_KNOWN_REGISTRY_OUTSIDE_POC | 11 | 7 | 28 |

## 说明

- TEST_ASSET 所在 split group 全部进入 TEST。
- WINDOW_SET_POSITION 在 VALIDATION 与 TEST 均包含 VALUE 样本。
- MODE 为 0，未人工制造 MODE 样本。
- UNKNOWN_CONTROL 表示当前 7-Intent PoC 必须 abstain；不等价于完整 95-Intent Registry 永远未知。
