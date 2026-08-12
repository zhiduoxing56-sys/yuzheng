# sys014-poc7-v2

这是 SYS-014 的第二个不可变 7-Intent PoC 冻结版本，parent 为 `sys014-poc7-v1`。它使用同一批 849 条 candidate 和 60 条独立 Safety Gold，主要修正 v1 的 split group 粗粒度与类别失衡；不是一次重新人工标注。

## 不可变与用途边界

1. v1 永久保留且未修改；v2 也禁止原地覆盖。
2. text、sample_id、intent、scope、structure、slots、segments、negated、safety_tags 均与 Stage 3B.1 source candidate 一致。
3. 仅有 444 条 `SYNTHETIC_TEMPLATE` 的 `paraphrase_family_id` 因过粗 family 被确定性细分；所有变化见 `v1_to_v2_split_diff.md`。
4. `TEST_ASSET` 不进入 TRAIN，其 source_type 与 family 未修改。
5. Safety Gold 未参与 split optimization，不得用于训练、early stopping、模型/阈值选择或校准。
6. split 单位为 refined family + template signature + mechanical signature 的 DSU 连通分量，固定 `split_seed=14032`。
7. 生成工具为 `scripts/freeze_sys014_poc7_v2.py`，验证工具为 `scripts/validate_sys014_frozen_v2.py`。
8. 本阶段不训练、不切分 Safety Gold、不修改 runtime；`READY_FOR_MODEL_TRAINING` 固定为 `NO`。

## 文件

- `train.jsonl`、`validation.jsonl`、`test.jsonl`
- `safety_gold.jsonl`
- `dataset_manifest.json`
- `split_report.md`
- `leakage_audit.md`
- `split_group_balance_diagnosis.md`
- `v1_to_v2_split_diff.md`
- `README.md`
