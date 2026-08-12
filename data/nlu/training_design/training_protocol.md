# SYS-014 Stage 4B 冻结训练协议

## 输入与模型

- dataset：`sys014-poc7-v2`，仅 train/validation/test；Safety Gold 只校验完整性。
- primary backbone：`hfl/rbt3` @ `0aa0527ff4170f29e1dfd3eb6ef60dc67e1bf75c`。
- device：device-agnostic、CPU-capable、GPU-preferred。
- max_length：`32`；全量最大 token length=`23`，无截断。
- baseline seed：`14032`；最终主结果建议至少 3 seeds。

## Loss 与类别不平衡

`L_total = L_scope + L_structure + L_intent(masked) + L_slot(masked) + L_negation(masked)`。五项 baseline 权重均为 1.0，这是 mean-reduced CE 的工程初值，不宣称最优。

Scope/Structure/Negation 使用均值归一、cap=3 的 `SQRT_INVERSE_FREQ`；Intent/Slot 使用 `NONE`。`NO_INTENT_CLASS_WEIGHT_REQUIRED = YES`。Stage 4C 只允许比较 NONE/INVERSE_FREQ/SQRT_INVERSE_FREQ，禁止 Safety Gold 调权。

## Stage 4C 候选

- AdamW；baseline LR=2e-5；候选仅 1e-5/2e-5/3e-5/5e-5。
- CPU batch=16；CUDA batch=32，可因内存下调。
- baseline epoch=10；候选 5–15；validation early stopping patience=3。
- `CPU_EPOCH_TIME_ESTIMATE = NOT_MEASURED`：未执行 backward 或 parameter update，不从 forward 延迟伪推训练时间。

## Best checkpoint 协议

`PRIMARY_QUALITY_SCORE = 0.30 Intent Macro F1 + 0.20 Scope Macro F1 + 0.20 Structure Macro F1 + 0.20 Slot Span F1 + 0.10 Negation F1`。

候选 checkpoint 还必须满足 validation：UFAR<=5%、MULTI false accept=0、AMBIGUOUS false accept=0。Safety Gold 不参与训练、early stopping、阈值、loss、超参数或 checkpoint 选择。

## 实验目录

每个 Stage 4C experiment 必须含 experiment_config、metrics、training_log、checkpoints、evaluation、manifest，并记录 dataset/manifest hash、registry、model revision、seed、hyperparameters、Git commit、device 和 Torch version。
