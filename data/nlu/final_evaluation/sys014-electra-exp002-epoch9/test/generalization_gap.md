# Validation → Locked Test 泛化差距

| Metric | Validation | Test | Test - Validation | Absolute difference |
|---|---:|---:|---:|---:|
| intent_macro_f1 | 0.991063 | 0.791474 | -0.199589 | 0.199589 |
| scope_macro_f1 | 0.733175 | 0.502429 | -0.230746 | 0.230746 |
| structure_macro_f1 | 1.000000 | 0.743081 | -0.256919 | 0.256919 |
| area_span_f1 | 0.890909 | 0.896552 | +0.005643 | 0.005643 |
| value_span_f1 | 0.842105 | 0.250000 | -0.592105 | 0.592105 |
| negation_span_f1 | 1.000000 | 0.830769 | -0.169231 | 0.169231 |
| overall_slot_span_f1 | 0.908163 | 0.735484 | -0.172679 | 0.172679 |
| sentence_negated_f1 | 0.933333 | 0.837209 | -0.096124 | 0.096124 |
| negated_recall | 0.875000 | 0.750000 | -0.125000 | 0.125000 |
| raw_ufar | 0.034483 | 0.479167 | +0.444684 | 0.444684 |

`GENERALIZATION_DEGRADATION_WARNING=YES`

该差距只用于一次性泛化报告，不用于重选模型、调参或补训练。
