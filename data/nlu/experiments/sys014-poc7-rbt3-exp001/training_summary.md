# SYS-014 RBT3 exp001 训练总结

## 训练事实

- CPU、batch=16、lr=2e-5、seed=14031；完成 10 epoch / 370 optimizer steps。
- mean epoch=14.331s；total training=143.352s。
- train total loss：6.333262 → 0.325891。
- 参数已更新、loss/gradient 全部 finite、无自动改数据或超参数。

## 最接近 safety gates 的 validation 候选（epoch 5，未选为 best）

- quality score=0.939701；validation loss=0.662609。
- Intent macro F1=1.000000。
- Scope macro F1=0.899824；UNKNOWN recall=1.000000。
- Structure macro F1=0.978782；MULTI recall=1.000000；AMBIGUOUS recall=0.888889。
- Slot overall F1=0.905263；AREA=0.917431；VALUE=0.864865；NEGATION=0.909091。
- Sentence NEGATED F1=0.829268；recall=0.708333。
- RAW UFAR=0.034483；UNKNOWN/MULTI/NON_CONTROL false accept=0。

## 阻断结论

AMBIGUOUS false accept 为 1/9，阻断样本为 `SYS014-POC-0731: 速度那个再弄点`。因此严格保留：

- `BEST_EPOCH = NOT_AVAILABLE`
- `BEST_CHECKPOINT_SAVED = NO`
- `RBT3_BASELINE_TRAINING_PASS = NO`
- `READY_FOR_STAGE_4C_NEXT_DECISION = NO`
- `TEST_EVALUATION_EXECUTED = NO`
- `SAFETY_GOLD_EVALUATION_EXECUTED = NO`

完整诊断见 `training_summary.json`。没有训练 ELECTRA，也没有放宽 safety gates。
