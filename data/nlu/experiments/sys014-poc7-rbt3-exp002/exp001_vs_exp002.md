# RBT3 exp001 vs exp002

exp001 使用统一 `2e-5` LR 和五任务等权；exp002 使用 backbone/head `1e-5/5e-5` 与 `1.5/1.5/1/1/2` safety-focused loss。两项策略同时变化，因此只能报告联合变化与结果相关，不能证明任何单项的独立因果效应。

| 指标 | exp001 closest epoch 5 | exp002 CLOSEST_SAFETY_DIAGNOSTIC epoch 5 |
|---|---:|---:|
| Intent Macro F1 | 1.000000 | 0.971939 |
| Scope Macro F1 | 0.899824 | 0.496835 |
| Structure Macro F1 | 0.978782 | 0.978214 |
| Slot Span F1 | 0.905263 | 0.490066 |
| Negation F1 | 0.829268 | 0.956522 |
| NEGATED Recall | 0.708333 | 0.916667 |
| RAW UFAR | 0.034483 | 0.103448 |
| AMBIGUOUS false accepts | 1 | 0 |
| MULTI false accepts | 0 | 0 |
| HEADLIGHT_OFF negated recall | 0.000000 | 0.600000 |
| ACCELERATE negated recall | 0.600000 | 1.000000 |
| CPU mean epoch seconds | 14.330726 | 8.713262 |
| Best eligible epoch | NOT_AVAILABLE | NOT_AVAILABLE |

## 0731 / 0732 / 0733

- SYS014-POC-0731: exp001={'scope': 'IN_SCOPE_CONTROL', 'structure': 'SINGLE', 'intent': 'ACCELERATE', 'final_abstain': False}；exp002={'scope': 'AMBIGUOUS_CONTROL', 'structure': 'AMBIGUOUS', 'intent': 'ACCELERATE', 'final_abstain': True}
- SYS014-POC-0732: exp001={'scope': 'AMBIGUOUS_CONTROL', 'structure': 'AMBIGUOUS', 'intent': 'NOT_AVAILABLE_FROM_EXP001_EPOCH5_ARTIFACTS', 'final_abstain': True}；exp002={'scope': 'AMBIGUOUS_CONTROL', 'structure': 'AMBIGUOUS', 'intent': 'ACCELERATE', 'final_abstain': True}
- SYS014-POC-0733: exp001={'scope': 'AMBIGUOUS_CONTROL', 'structure': 'AMBIGUOUS', 'intent': 'NOT_AVAILABLE_FROM_EXP001_EPOCH5_ARTIFACTS', 'final_abstain': True}；exp002={'scope': 'AMBIGUOUS_CONTROL', 'structure': 'AMBIGUOUS', 'intent': 'ACCELERATE', 'final_abstain': True}

## ACCELERATE 边界 probes

exp002 false reject count：`0/5`。这些文本仅用于 forward probe，不进入 loss、PRIMARY_QUALITY_SCORE 或 checkpoint selection。
