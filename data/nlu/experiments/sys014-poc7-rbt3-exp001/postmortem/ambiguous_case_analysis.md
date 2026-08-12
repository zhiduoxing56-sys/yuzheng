# RBT3 exp001 AMBIGUOUS 安全误放分析

## 结论

`SYS014-POC-0731` 是模型失败，不是标签映射、UFAR 或训练流水线失败。它在 10 个 epoch 中有 9 个 epoch 被误放，仅 epoch 2 正确 abstain，并从 epoch 3 至 10 连续误放；在最接近安全门的 epoch 5，它是唯一阻断样本。

- `PIPELINE_BUG_FOUND = NO`
- `LABEL_MAPPING_BUG_FOUND = NO`
- `UFAR_IMPLEMENTATION_BUG_FOUND = NO`
- 轨迹分类：`B_EPOCH_DEPENDENT`
- 误放 epochs：`[1, 3, 4, 5, 6, 7, 8, 9, 10]`

## Epoch 5 confidence 边界

- `EPOCH5_LOGITS_AVAILABLE = NO`
- `EPOCH5_CONFIDENCE_NOT_RECOVERABLE_FROM_EXISTING_ARTIFACTS = YES`

last checkpoint 是 epoch 10，只用于 forward-only 诊断，不能替代或恢复 epoch 5 概率。

## Last checkpoint：重点 AMBIGUOUS 样本

- `SYS014-POC-0731` `速度那个再弄点`：scope=IN_SCOPE_CONTROL (0.878114, margin=0.803189)；structure=SINGLE (0.829300, margin=0.692707)；intent=ACCELERATE (0.962361, margin=0.951254)
- `SYS014-POC-0732` `麻烦速度那个再弄点`：scope=IN_SCOPE_CONTROL (0.835069, margin=0.705365)；structure=SINGLE (0.682007, margin=0.399621)；intent=ACCELERATE (0.944334, margin=0.929852)
- `SYS014-POC-0733` `速度那个再弄点，可以吗`：scope=AMBIGUOUS_CONTROL (0.915717, margin=0.847199)；structure=AMBIGUOUS (0.934222, margin=0.878143)；intent=ACCELERATE (0.823147, margin=0.784617)

`LAST_CHECKPOINT_DIAGNOSTIC_ONLY = YES`，它没有被提升为 best 或 deployment checkpoint。

## 当前 deterministic vague / ambiguity 路径

`0731` 命中配置词 `['那个']`，因此检测结果为 YES。但对象已被解析为“速度”，现有 Parser 的 `vague and target == unknown` 分支没有额外贡献 ambiguity。其动作仍为 `unknown`，DecisionEngine 的 incomplete-frame 路径强制 REVIEW，所以实际 runtime fail-close 为 YES。AdvancedValidation、Interpreter 和 safety gate 没有另一个可覆盖该结果的 vague 放行分支。

## 三层语义必须分离

1. Model semantic hypothesis：scope/structure/intent argmax，例如 ACCELERATE。
2. Model abstention signals：scope/structure confidence 与 top1-top2 margin；argmax 本身不是执行许可。
3. Deterministic safety guard：vague reference、缺失动作/对象、multi-intent、negation 和 context claim。

未来可执行条件只能是三层同时通过，而不是 `Intent argmax == executable`。

## 正常 ACCELERATE 边界与 0731

- `再快一点`：模型 intent=ACCELERATE (0.964920)；Parser action/target=加速/速度；guard abstain=NO；vague=无
- `速度再快一点`：模型 intent=ACCELERATE (0.933372)；Parser action/target=加速/速度；guard abstain=NO；vague=无
- `再提点速度`：模型 intent=ACCELERATE (0.968051)；Parser action/target=unknown/速度；guard abstain=YES；vague=无
- `把速度提上去`：模型 intent=ACCELERATE (0.972576)；Parser action/target=unknown/速度；guard abstain=YES；vague=无
- `稍微加点速`：模型 intent=ACCELERATE (0.972710)；Parser action/target=unknown/unknown；guard abstain=YES；vague=无
- `速度那个再弄点`：模型 intent=ACCELERATE (0.962361)；Parser action/target=unknown/速度；guard abstain=YES；vague=那个

明确样本包含可解释的动作词（快/提/加）且没有模糊代词；`速度那个再弄点` 使用“那个”与泛化谓词“弄”，指代和动作均不充分。当前 deterministic parser 能保守挡住它，但也挡住若干明确同义表达，说明不能把“含速度”直接等价为 ACCELERATE，也不能把现有 parser 当作无损 guard。

## Strategy A/B（epoch 5 hard predictions）

- Model-only UFAR：`0.034483`；AMBIGUOUS false accepts：`1`；valid SINGLE false rejects：`1`。
- Existing deterministic guard adapter UFAR：`0.000000`；AMBIGUOUS false accepts：`0`；valid SINGLE false rejects：`68`。
