# SYS-014 Stage 4C-B.1 ELECTRA Slot 欠拟合诊断与 Backbone 路线决策

## 结论

- `ELECTRA_SLOT_PIPELINE_BUG = NO`
- `TOKEN_PROJECTION_FAILURES = 0`
- `SLOT_LABEL_MAPPING_BUG = NO`
- `SLOT_LEARNING_PATTERN = D`（VALUE 全 10 epoch 为 0；AREA 后期学习，NEGATION 到 epoch 10 才出现）
- `SLOT_O_CLASS_COLLAPSE = NO`
- `RECOMMENDED_NEXT_PATH = PATH_E1`

Pipeline、projection、mask 与标签顺序均正确。ELECTRA 的问题不是实现 Bug，也不是全部 O；它表现为 VALUE 类持续塌缩、其他实体学习很慢。Train 的 O:non-O 为 `4.460:1`，unweighted CE 对 O 的支配与 256-hidden token representation 的学习效率共同构成风险。由于 ELECTRA 已过 frozen safety gates，建议只进行一次隔离变量的 Slot class-weight 实验，再决定是否彻底回到 RBT3；本阶段不启动该实验。

## Slot 学习轨迹

| Epoch | AREA F1 | VALUE F1 | NEGATION span F1 | Overall F1 | Train slot loss | Validation slot loss |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 1.7895 | 1.3430 |
| 2 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.9338 | 0.7487 |
| 3 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.6907 | 0.6386 |
| 4 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.6155 | 0.5742 |
| 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.5709 | 0.5253 |
| 6 | 0.0625 | 0.0000 | 0.0000 | 0.0360 | 0.5392 | 0.4888 |
| 7 | 0.2892 | 0.0000 | 0.0000 | 0.1846 | 0.5089 | 0.4607 |
| 8 | 0.3516 | 0.0000 | 0.0000 | 0.2319 | 0.4821 | 0.4420 |
| 9 | 0.3469 | 0.0000 | 0.0000 | 0.2282 | 0.4687 | 0.4305 |
| 10 | 0.3333 | 0.0000 | 0.1290 | 0.2468 | 0.4654 | 0.4267 |

## Best epoch token 分布

```json
{
  "gold_label_distribution": {
    "O": 804,
    "B-AREA": 52,
    "I-AREA": 76,
    "B-VALUE": 19,
    "I-VALUE": 21,
    "B-NEGATION": 24,
    "I-NEGATION": 21
  },
  "predicted_label_distribution": {
    "O": 921,
    "B-AREA": 40,
    "I-AREA": 45,
    "B-VALUE": 2,
    "I-VALUE": 0,
    "B-NEGATION": 6,
    "I-NEGATION": 3
  },
  "PREDICTED_O_RATE": 0.9056047197640118,
  "gold_AREA_token_count": 128,
  "predicted_AREA_token_count": 85,
  "gold_VALUE_token_count": 40,
  "predicted_VALUE_token_count": 2,
  "gold_NEGATION_token_count": 45,
  "predicted_NEGATION_token_count": 9,
  "SLOT_O_CLASS_COLLAPSE": false,
  "collapse_definition": "predicted_non_o=0 OR PREDICTED_O_RATE>=0.98",
  "raw_bio_continuity_error_count": 11
}
```

## Pipeline 投影抽样（Train，每类随机 10 条）

| Audit type | Sample | Text | Token → BIO |
|---|---|---|---|
| AREA | SYS014-POC-0797 | 请打开司机这边的窗 | [CLS][IGNORE_INDEX] 请[O] 打[O] 开[O] 司[B-AREA] 机[I-AREA] 这[I-AREA] 边[I-AREA] 的[O] 窗[O] [SEP][IGNORE_INDEX] |
| AREA | SYS014-POC-0816 | 开一下后排右边的窗 | [CLS][IGNORE_INDEX] 开[O] 一[O] 下[O] 后[B-AREA] 排[I-AREA] 右[I-AREA] 边[I-AREA] 的[O] 窗[O] [SEP][IGNORE_INDEX] |
| AREA | SYS014-POC-0096 | 主驾门开一下 | [CLS][IGNORE_INDEX] 主[B-AREA] 驾[I-AREA] 门[O] 开[O] 一[O] 下[O] [SEP][IGNORE_INDEX] |
| AREA | SYS014-POC-0224 | 左前车窗开到50% | [CLS][IGNORE_INDEX] 左[B-AREA] 前[I-AREA] 车[O] 窗[O] 开[O] 到[O] 50[B-VALUE] %[I-VALUE] [SEP][IGNORE_INDEX] |
| AREA | SYS014-POC-0121 | 帮我开一下右前车门 | [CLS][IGNORE_INDEX] 帮[O] 我[O] 开[O] 一[O] 下[O] 右[B-AREA] 前[I-AREA] 车[O] 门[O] [SEP][IGNORE_INDEX] |
| AREA | SYS014-POC-0231 | 把左前车窗降一点 | [CLS][IGNORE_INDEX] 把[O] 左[B-AREA] 前[I-AREA] 车[O] 窗[O] 降[O] 一[B-VALUE] 点[I-VALUE] [SEP][IGNORE_INDEX] |
| AREA | SYS014-POC-0114 | 先开一下司机这边的门 | [CLS][IGNORE_INDEX] 先[O] 开[O] 一[O] 下[O] 司[B-AREA] 机[I-AREA] 这[I-AREA] 边[I-AREA] 的[O] 门[O] [SEP][IGNORE_INDEX] |
| AREA | SYS014-POC-0799 | 帮我把主驾窗打开 | [CLS][IGNORE_INDEX] 帮[O] 我[O] 把[O] 主[B-AREA] 驾[I-AREA] 窗[O] 打[O] 开[O] [SEP][IGNORE_INDEX] |
| AREA | SYS014-POC-0128 | 给我把右前车门开了 | [CLS][IGNORE_INDEX] 给[O] 我[O] 把[O] 右[B-AREA] 前[I-AREA] 车[O] 门[O] 开[O] 了[O] [SEP][IGNORE_INDEX] |
| AREA | SYS014-POC-0132 | 副驾驶门开一下 | [CLS][IGNORE_INDEX] 副[B-AREA] 驾[I-AREA] 驶[I-AREA] 门[O] 开[O] 一[O] 下[O] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0600 | 左后车窗开到一半然后踩下刹车 | [CLS][IGNORE_INDEX] 左[B-AREA] 后[I-AREA] 车[O] 窗[O] 开[O] 到[O] 一[B-VALUE] 半[I-VALUE] 然[O] 后[O] 踩[O] 下[O] 刹[O] 车[O] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0273 | 把右前车窗开到三成 | [CLS][IGNORE_INDEX] 把[O] 右[B-AREA] 前[I-AREA] 车[O] 窗[O] 开[O] 到[O] 三[B-VALUE] 成[I-VALUE] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0523 | 可别把车窗开到一半 | [CLS][IGNORE_INDEX] 可[B-NEGATION] 别[I-NEGATION] 把[O] 车[O] 窗[O] 开[O] 到[O] 一[B-VALUE] 半[I-VALUE] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0608 | 继续加速然后把车窗调到30% | [CLS][IGNORE_INDEX] 继[O] 续[O] 加[O] 速[O] 然[O] 后[O] 把[O] 车[O] 窗[O] 调[O] 到[O] 30[B-VALUE] %[I-VALUE] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0622 | 关闭右后车门再把车窗调到30% | [CLS][IGNORE_INDEX] 关[O] 闭[O] 右[B-AREA] 后[I-AREA] 车[O] 门[O] 再[O] 把[O] 车[O] 窗[O] 调[O] 到[O] 30[B-VALUE] %[I-VALUE] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0241 | 把主驾车窗开到三成 | [CLS][IGNORE_INDEX] 把[O] 主[B-AREA] 驾[I-AREA] 车[O] 窗[O] 开[O] 到[O] 三[B-VALUE] 成[I-VALUE] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0272 | 右前车窗开到50% | [CLS][IGNORE_INDEX] 右[B-AREA] 前[I-AREA] 车[O] 窗[O] 开[O] 到[O] 50[B-VALUE] %[I-VALUE] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0221 | 把左前车窗开到一半 | [CLS][IGNORE_INDEX] 把[O] 左[B-AREA] 前[I-AREA] 车[O] 窗[O] 开[O] 到[O] 一[B-VALUE] 半[I-VALUE] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0236 | 左前车窗再开大一点 | [CLS][IGNORE_INDEX] 左[B-AREA] 前[I-AREA] 车[O] 窗[O] 再[O] 开[O] 大[B-VALUE] 一[I-VALUE] 点[I-VALUE] [SEP][IGNORE_INDEX] |
| VALUE | SYS014-POC-0627 | 左后车窗开到一半再把车门关上 | [CLS][IGNORE_INDEX] 左[B-AREA] 后[I-AREA] 车[O] 窗[O] 开[O] 到[O] 一[B-VALUE] 半[I-VALUE] 再[O] 把[O] 车[O] 门[O] 关[O] 上[O] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0498 | 不要关闭车门 | [CLS][IGNORE_INDEX] 不[B-NEGATION] 要[I-NEGATION] 关[O] 闭[O] 车[O] 门[O] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0517 | 别把车窗开到一半 | [CLS][IGNORE_INDEX] 别[B-NEGATION] 把[O] 车[O] 窗[O] 开[O] 到[O] 一[B-VALUE] 半[I-VALUE] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0556 | 暂时别加速 | [CLS][IGNORE_INDEX] 暂[B-NEGATION] 时[I-NEGATION] 别[I-NEGATION] 加[O] 速[O] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0536 | 先别关闭大灯 | [CLS][IGNORE_INDEX] 先[B-NEGATION] 别[I-NEGATION] 关[O] 闭[O] 大[O] 灯[O] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0570 | 先别刹车 | [CLS][IGNORE_INDEX] 先[B-NEGATION] 别[I-NEGATION] 刹[O] 车[O] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0543 | 无需关闭大灯 | [CLS][IGNORE_INDEX] 无[B-NEGATION] 需[I-NEGATION] 关[O] 闭[O] 大[O] 灯[O] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0545 | 先不要关闭大灯 | [CLS][IGNORE_INDEX] 先[B-NEGATION] 不[I-NEGATION] 要[I-NEGATION] 关[O] 闭[O] 大[O] 灯[O] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0560 | 无需加速 | [CLS][IGNORE_INDEX] 无[B-NEGATION] 需[I-NEGATION] 加[O] 速[O] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0525 | 无需把车窗开到一半 | [CLS][IGNORE_INDEX] 无[B-NEGATION] 需[I-NEGATION] 把[O] 车[O] 窗[O] 开[O] 到[O] 一[B-VALUE] 半[I-VALUE] [SEP][IGNORE_INDEX] |
| NEGATION | SYS014-POC-0499 | 别关闭车门 | [CLS][IGNORE_INDEX] 别[B-NEGATION] 关[O] 闭[O] 车[O] 门[O] [SEP][IGNORE_INDEX] |

## VALUE 全量 Validation 错误

```json
{
  "1_NO_VALUE_OUTPUT": 17,
  "2_OUTPUT_AS_AREA": 0,
  "3_OUTPUT_AS_NEGATION": 0,
  "4_VALUE_SPAN_BOUNDARY_ERROR": 2,
  "5_BIO_CONTINUITY_ERROR": 0,
  "6_TOKENIZER_SUBWORD_PROBLEM": 0
}
```

| Sample | Text | Gold VALUE | Predicted spans | Token-level predicted labels | Error types |
|---|---|---|---|---|---|
| SYS014-POC-0205 | 把车窗开到一半 | 一半(5:7) | NONE | 把[O] 车[O] 窗[O] 开[O] 到[O] 一[O] 半[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0207 | 把车窗开到50% | 50%(5:8) | VALUE:50 | 把[O] 车[O] 窗[O] 开[O] 到[O] 50[B-VALUE] %[O] | 4_VALUE_SPAN_BOUNDARY_ERROR |
| SYS014-POC-0209 | 把车窗开到三成 | 三成(5:7) | NONE | 把[O] 车[O] 窗[O] 开[O] 到[O] 三[O] 成[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0211 | 把车窗开到30% | 30%(5:8) | VALUE:30 | 把[O] 车[O] 窗[O] 开[O] 到[O] 30[B-VALUE] %[O] | 4_VALUE_SPAN_BOUNDARY_ERROR |
| SYS014-POC-0213 | 把车窗开到最大 | 最大(5:7) | NONE | 把[O] 车[O] 窗[O] 开[O] 到[O] 最[O] 大[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0216 | 车窗再开一点 | 一点(4:6) | NONE | 车[O] 窗[O] 再[O] 开[O] 一[O] 点[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0218 | 车窗再开小一点 | 小一点(4:7) | NONE | 车[O] 窗[O] 再[O] 开[O] 小[O] 一[O] 点[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0220 | 车窗再开大一点 | 大一点(4:7) | NONE | 车[O] 窗[O] 再[O] 开[O] 大[O] 一[O] 点[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0254 | 司机这边的窗开到一半 | 一半(8:10) | AREA:司机这边 | 司[B-AREA] 机[I-AREA] 这[I-AREA] 边[I-AREA] 的[O] 窗[O] 开[O] 到[O] 一[O] 半[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0256 | 司机这边的窗开到50% | 50%(8:11) | AREA:司机这边 | 司[B-AREA] 机[I-AREA] 这[I-AREA] 边[I-AREA] 的[O] 窗[O] 开[O] 到[O] 50[O] %[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0258 | 司机这边的窗开到三成 | 三成(8:10) | AREA:司机这边 | 司[B-AREA] 机[I-AREA] 这[I-AREA] 边[I-AREA] 的[O] 窗[O] 开[O] 到[O] 三[O] 成[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0260 | 司机这边的窗开到30% | 30%(8:11) | AREA:司机这边 | 司[B-AREA] 机[I-AREA] 这[I-AREA] 边[I-AREA] 的[O] 窗[O] 开[O] 到[O] 30[O] %[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0262 | 司机这边的窗开到最大 | 最大(8:10) | AREA:司机这边 | 司[B-AREA] 机[I-AREA] 这[I-AREA] 边[I-AREA] 的[O] 窗[O] 开[O] 到[O] 最[O] 大[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0598 | 左后车窗开到一半然后把前照灯关了 | 一半(6:8) | AREA:左 | 左[B-AREA] 后[O] 车[O] 窗[O] 开[O] 到[O] 一[O] 半[O] 然[O] 后[O] 把[O] 前[O] 照[O] 灯[O] 关[O] 了[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0599 | 左后车窗开到一半然后再提点速度 | 一半(6:8) | AREA:左 | 左[B-AREA] 后[O] 车[O] 窗[O] 开[O] 到[O] 一[O] 半[O] 然[O] 后[O] 再[O] 提[O] 点[O] 速[O] 度[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0628 | 左后车窗开到一半再把前照灯关了 | 一半(6:8) | AREA:左 | 左[B-AREA] 后[O] 车[O] 窗[O] 开[O] 到[O] 一[O] 半[O] 再[O] 把[O] 前[O] 照[O] 灯[O] 关[O] 了[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0629 | 左后车窗开到一半再提点速度 | 一半(6:8) | AREA:左后 | 左[B-AREA] 后[I-AREA] 车[O] 窗[O] 开[O] 到[O] 一[O] 半[O] 再[O] 提[O] 点[O] 速[O] 度[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0658 | 左后车窗开到一半接着把前照灯关了 | 一半(6:8) | AREA:左 | 左[B-AREA] 后[O] 车[O] 窗[O] 开[O] 到[O] 一[O] 半[O] 接[O] 着[O] 把[O] 前[O] 照[O] 灯[O] 关[O] 了[O] | 1_NO_VALUE_OUTPUT |
| SYS014-POC-0659 | 左后车窗开到一半接着再提点速度 | 一半(6:8) | AREA:左后 | 左[B-AREA] 后[I-AREA] 车[O] 窗[O] 开[O] 到[O] 一[O] 半[O] 接[O] 着[O] 再[O] 提[O] 点[O] 速[O] 度[O] | 1_NO_VALUE_OUTPUT |

Tokenizer projection failure 为 0，未发现 subword coverage 问题或标签映射错位。VALUE F1=0 的直接原因是没有任何 exact VALUE span：17 条完全不输出 VALUE，2 条 VALUE 输出为边界错误。全体验证序列存在 11 个 raw BIO continuity violation，但 VALUE 样本未因此形成主错误类型。

## Slot 类别不平衡与 loss 方案

```json
{
  "train_token_distribution": {
    "O": 3760,
    "B-AREA": 211,
    "I-AREA": 287,
    "B-VALUE": 81,
    "I-VALUE": 87,
    "B-NEGATION": 76,
    "I-NEGATION": 101
  },
  "O_token_count": 3760,
  "non_O_token_count": 843,
  "O_to_non_O_ratio": 4.460260972716489,
  "entity_token_support": {
    "AREA": 498,
    "VALUE": 168,
    "NEGATION": 177
  },
  "A_NONE": {
    "O": 1.0,
    "B-AREA": 1.0,
    "I-AREA": 1.0,
    "B-VALUE": 1.0,
    "I-VALUE": 1.0,
    "B-NEGATION": 1.0,
    "I-NEGATION": 1.0
  },
  "B_SQRT_INVERSE_FREQ_CAP_3": {
    "O": 0.19794488,
    "B-AREA": 0.8355972,
    "I-AREA": 0.71646876,
    "B-VALUE": 1.34863894,
    "I-VALUE": 1.30130344,
    "B-NEGATION": 1.39229546,
    "I-NEGATION": 1.20775131
  },
  "C_INVERSE_FREQ_CAP_3": {
    "O": 0.03361175,
    "B-AREA": 0.59895821,
    "I-AREA": 0.44034907,
    "B-VALUE": 1.56024916,
    "I-VALUE": 1.45264577,
    "B-NEGATION": 1.66289713,
    "I-NEGATION": 1.25128893
  },
  "RECOMMENDED_SLOT_WEIGHT_POLICY": "SQRT_INVERSE_FREQ_CAP_3",
  "recommendation_reason": "It is the simplest frozen-loss-compatible change, reduces O dominance, and gives VALUE/NEGATION moderate relative emphasis without any weight exceeding 3.0."
}
```

推荐 `SQRT_INVERSE_FREQ_CAP_3`。它只改变 Slot CE 的 class weights，不改变 Slot task weight；比固定 entity 权重更可复现，比 focal loss 更简单可解释。暂不引入 CRF/BiLSTM。

下一实验设计（仅设计，不执行）：ELECTRA exp002 保持 exp001 的 pretrained revision、seed、单 LR 2e-5、batch 16、所有 task loss weight 1.0、scheduler、10 epochs 与 safety gates，仅把 Slot class-weight 从 NONE 改为上述 SQRT_INVERSE_FREQ cap=3。每 epoch 继续选择 eligible checkpoint；重点观察 VALUE/Overall Slot 是否改善且 UFAR/MULTI/AMBIGUOUS gates 不退化。

## Scope 诊断

- IN_SCOPE_CONTROL F1：`0.983193`
- NON_CONTROL F1 / recall：`0.666667` / `0.500000`
- UNKNOWN_CONTROL F1 / recall：`0.000000` / `0.000000`
- AMBIGUOUS_CONTROL F1：`0.875000`
- Confusion matrix：`[[117, 0, 0, 0], [1, 1, 0, 0], [1, 0, 0, 0], [2, 0, 0, 7]]`
- 0748 scope top1/top2 margin：`0.063002`
- `ELECTRA_SCOPE_DIAGNOSIS_REQUIRED = YES`

0748 是低 margin hard case（IN_SCOPE_CONTROL 0.3954 vs NON_CONTROL 0.3324），不是高置信错误。但 Validation 只有 2 个 NON_CONTROL、1 个 UNKNOWN_CONTROL，且 UNKNOWN recall=0，因此证据不足以宣称普遍 NON_CONTROL 失败，也不足以关闭 Scope 诊断。

## 模型决策矩阵

RBT3 exp002 仅作上下文；公平 backbone 对照只使用两个 exp001。

| Model | Intent | Scope | Structure | Slot | VALUE | Neg F1 | Neg recall | UFAR | Ambig FA | Multi FA | Gate | Params | Hidden | Train sec | Stage4A RAM MB | Stage4A CPU P95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| RBT3 exp001 | 1.0000 | 0.8998 | 0.9788 | 0.9053 | 0.8649 | 0.8293 | 0.7083 | 0.0345 | 1 | 0 | FAIL | 38494487 | 768 | 143.352 | 165.512 | 7.883 |
| RBT3 exp002 | 0.9719 | 0.4968 | 0.9782 | 0.4901 | 0.1739 | 0.9565 | 0.9167 | 0.1034 | 0 | 0 | FAIL | 38494487 | 768 | 88.649 | 165.512 | 7.883 |
| ELECTRA exp001 | 0.9821 | 0.6312 | 0.9782 | 0.2468 | 0.0000 | 0.9787 | 0.9583 | 0.0345 | 0 | 0 | PASS | 12286487 | 256 | 137.838 | 64.391 | 14.785 |

- 当前最佳安全模型：ELECTRA exp001。
- 当前最佳语义模型：RBT3 exp001。
- 当前最佳 Slot 模型：RBT3 exp001。
- 当前最佳综合候选：没有无条件胜者；ELECTRA 是唯一 safety-eligible 候选，RBT3 exp001 是最强语义/Slot 开发候选但仍有 abstention safety blocker。

Safety Gate PASS 只是进入候选集合的必要条件，不证明 ELECTRA 已最终胜出。

## 最终字段

```text
ELECTRA_SLOT_PIPELINE_BUG=NO
TOKEN_PROJECTION_FAILURES=0
SLOT_LABEL_MAPPING_BUG=NO
SLOT_LEARNING_PATTERN=D
SLOT_O_CLASS_COLLAPSE=NO
ELECTRA_VALUE_F1=0.000000
ELECTRA_AREA_F1=0.333333
ELECTRA_NEGATION_SPAN_F1=0.129032
RBT3_EXP001_VALUE_F1=0.864865
RBT3_EXP001_AREA_F1=0.917431
RBT3_EXP001_NEGATION_SPAN_F1=0.909091
ELECTRA_SCOPE_MACRO_F1=0.631215
ELECTRA_UNKNOWN_RECALL=0.000000
ELECTRA_NON_CONTROL_RECALL=0.500000
RECOMMENDED_SLOT_WEIGHT_POLICY=SQRT_INVERSE_FREQ_CAP_3
RECOMMENDED_NEXT_PATH=PATH_E1
BACKBONE_DIAGNOSIS_COMPLETE=YES
READY_FOR_NEXT_MODEL_EXPERIMENT=YES
TRAINING_STEPS_EXECUTED_THIS_STAGE=0
TEST_EVALUATION_EXECUTED=NO
SAFETY_GOLD_EVALUATION_EXECUTED=NO
```
