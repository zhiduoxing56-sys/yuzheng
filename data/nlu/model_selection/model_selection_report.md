# SYS-014 Stage 4A 模型选择报告

## 实测矩阵

| Model | Params | Weight MiB | RSS Δ MiB | Align | Tok P50/P95 ms | Encoder P50/P95 ms | Total P50/P95 ms | Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hfl/chinese-electra-180g-small-discriminator | 12,280,576 | 47.15 | 64.39 | 0 | 0.194/0.262 | 12.483/14.262 | 12.532/14.785 | 78.56 |
| hfl/rbt3 | 38,476,800 | 149.14 | 165.51 | 0 | 0.194/0.267 | 5.954/7.237 | 6.407/7.883 | 87.07 |
| hfl/chinese-macbert-base | 102,267,648 | 392.52 | 410.65 | 0 | 0.191/0.288 | 21.274/25.768 | 21.352/25.764 | REFERENCE |

评分只覆盖架构、资源、兼容性和部署复杂度，不包含训练准确率，也不声称任一候选准确率必然更高。

## 选择

- `PRIMARY_MODEL_CANDIDATE = hfl/rbt3`
- `SECONDARY_MODEL_CANDIDATE = hfl/chinese-electra-180g-small-discriminator`
- `UPPER_BOUND_REFERENCE = hfl/chinese-macbert-base`

主选在本机轻量候选部署评分中更高。其 total P95 为 `7.883 ms`，较备用 `14.785 ms` 低 `46.7%`；代价是 RSS Δ `165.51 MiB`，高于备用的 `64.39 MiB`。本阶段把单条 CPU 延迟列为关键部署指标，因此接受该内存代价；ELECTRA 仍是更低参数、磁盘和 RAM 的重要备用。MacBERT-base 保留为 representation/resource upper-bound，不默认作为最终部署模型。Stage 4B 最多训练主选与一个备用/参考实验，且必须继续锁定本文 revision。

三者以 `AutoModel` 加载时均无 encoder missing keys、mismatched keys 或 error；unexpected keys 仅来自 checkpoint 自带的 ELECTRA discriminator prediction head 或 BERT MLM/NSP pretraining heads，这些头不进入共享 encoder 与未来联合任务头。

## 安全与完整性结论

- `LOCAL_ENVIRONMENT_AUDITED = YES`
- `JOINT_NLU_ARCHITECTURE_READY = YES`
- `MODEL_SELECTION_READY = YES`
- `READY_FOR_STAGE_4B_TRAINING_DESIGN = YES`
- `READY_FOR_MODEL_TRAINING = NO`
- `TRAINING_STEPS_EXECUTED = 0`
- `DO_NOT_FINE_TUNE_SHARED_HNSW_ENCODER_IN_PLACE = YES`

本阶段未修改 runtime、Legacy Parser、SemanticFrame、安全门、授权、执行、审计或冻结数据。
