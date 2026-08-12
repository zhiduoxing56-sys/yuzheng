# SYS-014 Stage 3C 数据冻结覆盖报告

## Source dataset

- Registry version：`sys-014-stage2.1-draft-2`
- candidate：**849**，原文件继续保持 `UNASSIGNED`
- Safety Gold：**60**，保持 `SAFETY_GOLD`
- Source 总记录：**909**
- train/validation/test 只存在于不可变冻结目录；未训练模型。

### 7-Intent source 覆盖

| Intent | positive SINGLE | negated SINGLE | MULTI mentions |
|---|---:|---:|---:|
| DOOR_OPEN | 72 | 20 | 42 |
| DOOR_CLOSE | 72 | 20 | 46 |
| WINDOW_OPEN | 60 | 15 | 12 |
| WINDOW_SET_POSITION | 78 | 20 | 34 |
| HEADLIGHT_OFF | 73 | 20 | 41 |
| ACCELERATE | 75 | 20 | 36 |
| BRAKE | 65 | 20 | 36 |

### Source 汇总

| 维度 | 数量 |
|---|---:|
| SINGLE | 708 |
| MULTI | 130 |
| AMBIGUOUS | 71 |
| IN_SCOPE_CONTROL | 747 |
| UNKNOWN_CONTROL | 62 |
| NON_CONTROL | 29 |
| AMBIGUOUS_CONTROL | 71 |
| AREA | 313 |
| VALUE | 132 |
| NEGATION | 149 |
| TEST_ASSET | 70 |
| SYNTHETIC_TEMPLATE | 839 |
| paraphrase family | 465 |

## Frozen dataset

- dataset version：`sys014-poc7-v1`
- split seed：`14031`
- frozen path：`data/nlu/poc/frozen/sys014-poc7-v1/`

| Split | 样本 | Family | Split group | 比例 |
|---|---:|---:|---:|---:|
| TRAIN | 582 | 252 | 158 | 68.55% |
| VALIDATION | 126 | 60 | 50 | 14.84% |
| TEST | 141 | 93 | 61 | 16.61% |
| SAFETY_GOLD | 60 | — | — | 完全隔离 |

详细 7-Intent split 覆盖见 `frozen/sys014-poc7-v1/split_report.md`。

## 冻结与泄漏校验

```text
TEST_ASSET_IN_TRAIN = 0
exact_cross_split_duplicates = 0
normalized_cross_split_duplicates = 0
template_signature_cross_split_duplicates = 0
mechanical_near_duplicate_cross_split_failures = 0
family_leakage_failures = 0
split_group_leakage_failures = 0
span_validation_failures = 0
registry_validation_failures = 0
structure_failures = 0
manifest_hash_failures = 0
UNASSIGNED_COUNT_IN_FROZEN = 0
```

```text
POC_DATASET_FROZEN = YES
POC_SPLIT_REPRODUCIBLE = YES
POC_LEAKAGE_AUDIT_PASS = YES
READY_FOR_MODEL_SELECTION = YES
READY_FOR_MODEL_TRAINING = NO
```
