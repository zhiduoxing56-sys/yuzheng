# ELECTRA exp001 vs exp002

本轮唯一有意改变的变量是 Slot class weighting：`NONE` → `SQRT_INVERSE_FREQ_CAP_3`。其余训练协议与 checkpoint score 均保持一致。因此 Slot 差异可作为 class-imbalance treatment 有帮助的工程证据，但不是严格因果证明。

| Metric | ELECTRA exp001 | ELECTRA exp002 |
|---|---:|---:|
| Intent Macro F1 | 0.982073 | 0.991063 |
| Scope Macro F1 | 0.631215 | 0.733175 |
| Structure Macro F1 | 0.978214 | 1.000000 |
| AREA F1 | 0.333333 | 0.890909 |
| VALUE F1 | 0.000000 | 0.842105 |
| NEGATION span F1 | 0.129032 | 1.000000 |
| Overall Slot F1 | 0.246753 | 0.908163 |
| Sentence Negation F1 | 0.978723 | 0.933333 |
| Negated Recall | 0.958333 | 0.875000 |
| UFAR | 0.034483 | 0.034483 |
| AMBIGUOUS FA | 0.000000 | 0.000000 |
| MULTI FA | 0.000000 | 0.000000 |
| UNKNOWN FA | 0.000000 | 1.000000 |
| NON_CONTROL FA | 1.000000 | 0.000000 |
| PREDICTED_O_RATE | 0.905605 | 0.771878 |
| Training seconds | 137.837766 | 89.699016 |
| Best epoch | 10.000000 | 9.000000 |

## 验收

```json
{
  "safety_gates_pass": true,
  "slot_improved": true,
  "value_diagnostic_target_met": true,
  "baseline": {
    "intent_macro_f1": 0.9820728291316527,
    "scope_macro_f1": 0.6312149859943977,
    "structure_macro_f1": 0.9782135076252724,
    "negation_f1": 0.9787234042553191,
    "in_scope_control_recall": 1.0,
    "slot_f1": 0.24675324675324675,
    "value_f1": 0.0
  },
  "current": {
    "intent_macro_f1": 0.9910627007401202,
    "scope_macro_f1": 0.7331754735792622,
    "structure_macro_f1": 1.0,
    "negation_f1": 0.9333333333333333,
    "in_scope_control_recall": 1.0
  },
  "degradation": {
    "intent_macro_f1": -0.008989871608467426,
    "scope_macro_f1": -0.10196048758486442,
    "structure_macro_f1": -0.02178649237472763,
    "negation_f1": 0.04539007092198577,
    "in_scope_control_recall": 0.0
  },
  "degradation_limits": {
    "intent_macro_f1": 0.03,
    "scope_macro_f1": 0.03,
    "structure_macro_f1": 0.02,
    "negation_f1": 0.03,
    "in_scope_control_recall": 0.03
  },
  "degradation_pass": {
    "intent_macro_f1": true,
    "scope_macro_f1": true,
    "structure_macro_f1": true,
    "negation_f1": false,
    "in_scope_control_recall": true
  },
  "ELECTRA_EXP002_PASS": false
}
```

- ELECTRA_EXP002_SAFETY_GATE_PASS=`YES`
- ELECTRA_EXP002_SLOT_IMPROVED=`YES`
- ELECTRA_EXP002_PASS=`NO`
- DEPLOYABLE=`NO`
