# SYS-014 Stage 4B 联合 NLU 训练协议与 Dry-Run 设计

> 状态：APPROVED / PROTOCOL FREEZE / FORWARD-ONLY DRY-RUN  
> 日期：2026-08-08

## 背景与目标

基于不可变 `sys014-poc7-v2`，为固定 revision 的 `hfl/rbt3` 实现可替换 backbone 的离线联合 NLU 训练流水线、评价协议、实验 manifest 与无更新 dry-run。Stage 4B 不训练、不生成正式 checkpoint、不修改 runtime。

## 方案对比与选择

采用 device-agnostic、当前 CPU 可运行、正式训练优先 GPU 的方案。CPU-only 会把当前机器性能偶然固化到协议；GPU-required 又无法验证当前环境的完整数据与 loss 路径。由于禁止通过 backward/optimizer.step 估时，`CPU_EPOCH_TIME_ESTIMATE = NOT_MEASURED`。

## 架构与组件

`scripts/nlu_training/` 包含 labels、frozen validation、projection、Dataset、Collator、JointNLUModel、masked loss、metrics、config、manifest、Stage 4C trainer 与 Stage 4B dry-run。Dry-run 不导入 trainer，不创建 optimizer，只用 `eval()` 与 `torch.inference_mode()`。

模型共享一个 Transformer backbone，first-token 表示进入 Scope(4)、Structure(3)、Intent(7)、Sentence Negation(2)；token 表示进入 BIO Slot(7)。Intent 与 Negation 严格按 eligible 条件 mask，Slot 的特殊 token/padding 使用 `-100`。

## 数据流

```text
frozen manifest/hash/schema/registry verification
→ raw JSONL record
→ tokenizer offset_mapping
→ dynamic BIO + sentence labels/masks
→ collator padding
→ shared backbone + five heads
→ masked loss / metric inputs
```

Safety Gold 只校验文件 hash，不进入 loss、early stopping、阈值、模型或超参数选择。raw character span 始终权威，token label 不回写 frozen JSON。

## Baseline 协议

- loss weights：五任务均为 1.0；仅作为各自 mean-reduced CE 的初始基线。
- class weights：Intent/Slot=`NONE`；Scope/Structure/Negation=`SQRT_INVERSE_FREQ`，均值归一化并 cap=3.0。
- AdamW；baseline LR=2e-5，候选仅 1e-5/2e-5/3e-5/5e-5。
- seed=14032；默认 epoch=10，候选 5–15；validation patience=3。
- CPU batch=16、CUDA batch=32；实际 Stage 4C 可在显存/RAM约束内下调。
- max_length 从 32/48/64 中选择覆盖 train/validation/test 的最小值，不机械使用 512。

Stage 4C 正式主结果至少 3 seeds；时间紧时允许单 seed 选方案，再对最终主模型复验。

## 指标与安全门

`PRIMARY_QUALITY_SCORE = 0.30 Intent Macro F1 + 0.20 Scope Macro F1 + 0.20 Structure Macro F1 + 0.20 Slot Span F1 + 0.10 Negation F1`。

Best checkpoint 必须同时满足 validation `UFAR <= 0.05`、`MULTI false accept = 0`、`AMBIGUOUS false accept = 0`。Safety Gold 不参与阈值选择。无可估样本的 split × intent negation 指标标记 `NOT_ESTIMABLE`。

## Dry-Run 与异常处理

Dry-run 选择覆盖全部 label/mask 的少量 TRAIN batch，检查 logits shape、五项 finite loss、监督计数和 metric input。运行前后对 backbone 与 joint heads 的代表 tensor 做 SHA256；任一变化、projection failure、manifest failure 或非 finite loss均阻止 Stage 4C readiness。

## 测试策略

离线测试覆盖 frozen hash、span→BIO、五类 mask、MULTI/UNKNOWN intent mask、padding ignore、finite loss、forward shape、分类/span/UFAR 指标、dry-run 无 optimizer、参数不变。最终再次运行官方 frozen v2 validator。

## 完成边界

本阶段可以把 `READY_FOR_MODEL_TRAINING` 置为 YES，含义仅是 Stage 4C 获准开始；Stage 4B 自身仍保持 `TRAINING_STEPS_EXECUTED = 0`，不得调用正式训练入口。
