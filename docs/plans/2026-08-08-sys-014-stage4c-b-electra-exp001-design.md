# SYS-014 Stage 4C-B ELECTRA exp001 设计

## 目标

在冻结的 `sys014-poc7-v2` 数据上，以与 RBT3 exp001 相同的基线协议，从 Stage 4A 固定的原始 ELECTRA-small 预训练快照重新初始化 backbone 和五个联合任务头，完成 Validation-only 微调与 backbone 对照。

## 冻结输入

- 模型：`hfl/chinese-electra-180g-small-discriminator`
- revision：`826a243f3f387450ef8d70de9c3d0706d8d8e924`
- 权重 SHA256：`45c0a4519ee767bd58ddd3573b9ceebb81a2c0fb65919a8b7513b57ee52009b3`
- 数据集：`sys014-poc7-v2`
- dataset manifest SHA256：`122621c0ce5e7a6fbaadbbe97cb3e7e86a32812ee1c69fe5ee27c45d94ac8d42`
- 输出：`data/nlu/experiments/sys014-poc7-electra-exp001/`

## 隔离边界

新增独立入口 `scripts/nlu_training/stage4c_electra_exp001.py`。它复用已验证的模型、损失、trainer 和中立 Validation artifact 生成函数，但不修改或调用 RBT3 exp001/exp002 的训练入口。RBT3 产物仅作为只读比较来源。

## 训练协议

- seed `14031`，并固定 Python、NumPy、Torch 随机状态。
- max length `32`，batch size `16`；只在内存不可承受时降至 `8`。
- AdamW，单一 optimizer parameter group，LR `2e-5`，weight decay `0.01`。
- warmup ratio `0.10`，gradient clip `1.0`，最多 `10` epochs，patience `3`。
- 五项 loss weight 均为 `1.0`。
- scope、structure、negation 使用 capped sqrt inverse frequency；intent、slot 不加权。
- 五个 head 的输入维度从 `backbone.config.hidden_size` 动态取得；句级 head 使用 CLS，slot head 使用完整序列。

## Preflight 与安全边界

创建实验目录和执行任何 backward 之前检查：固定数据 hash、Stage 4A revision/cache/权重 hash、零 span projection failure、max length、head shape、mask/loss、单 optimizer group、随机新 head、非 RBT3 checkpoint 初始化、Validation prediction schema，以及 Test/Safety Gold 未加载。Preflight 只执行一次 forward+loss，明确记录 `TRAINING_STEPS_EXECUTED=0`。

正式训练只读取 Train 与 Validation。Test 和 Safety Gold 不参与推理、选择或报告。

## 选择与停止

每个 epoch 保存完整 Validation predictions。只有满足冻结 gates（UFAR <= 0.05、MULTI false accept = 0、AMBIGUOUS false accept = 0）的 checkpoint 才 eligible；eligible 内按冻结 PRIMARY_QUALITY_SCORE 选 best。若始终无 eligible，则按既定四级排序保存 closest diagnostic，且始终 `BEST=false`、`DEPLOYABLE=false`。

只有出现 eligible best 后，连续 3 epoch 无更高 eligible quality 才 early stop；否则跑满 10 epochs。始终保存 last。

## 健康与决策标志

- `ELECTRA_EXP001_SAFETY_GATE_PASS`：至少一个 epoch 通过全部冻结 safety gates。
- `ELECTRA_EXP001_BASELINE_HEALTHY`：训练完成、loss/gradient 有限、五任务均可计算、slot 未坍缩、backbone 参数发生训练更新、要求产物齐全。
- `BACKBONE_COMPARISON_READY`：baseline healthy，且数据、seed、协议、门槛与 RBT3 exp001 可比。
- `READY_FOR_STAGE_4C_MODEL_DECISION`：comparison ready，且 Test、Safety Gold、runtime 及其他禁止实验均未触碰。

Safety pass 与 baseline health 分离，避免把诊断有效但未过 gate 的实验误报为不可比较，也避免 closest checkpoint 被误标为可部署。

## 报告

生成逐 epoch metrics/predictions、错误样本、best 或 closest、last、训练摘要，以及 `rbt3_exp001_vs_electra_exp001.md`。比较正文仅比较两个 exp001；RBT3 exp002 只允许作为附录背景。Stage 4A 的 RBT3/ELECTRA CPU P95 仅标注为预训练 encoder 画像，不冒充微调后的端到端 runtime。
