# sys014-poc7-v1

这是 SYS-014 的 7-Intent PoC 冻结数据集，包含 849 条 candidate 切分记录和 60 条独立 Safety Gold。

## 重要边界

1. 本数据集仅覆盖 `DOOR_OPEN`、`DOOR_CLOSE`、`WINDOW_OPEN`、`WINDOW_SET_POSITION`、`HEADLIGHT_OFF`、`ACCELERATE`、`BRAKE`，不是完整 95 类最终模型数据集。
2. 来源包含 `TEST_ASSET` 与 `SYNTHETIC_TEMPLATE`；不得宣称为真实驾驶员大规模实采语料。
3. Safety Gold 完全独立于训练、验证和测试，不得用于训练、early stopping、超参数/阈值选择、confidence calibration 或模型选择；只用于方案基本确定后的最终安全回归。
4. PoC 中 `UNKNOWN_CONTROL` 表示“当前 7-Intent 模型必须 abstain 的控制请求”。它既可能是完整 Registry 已知但 PoC 未覆盖的车辆能力，也可能是 Registry 外的外域控制；不表示完整 95-Intent Registry 永远不知道该能力。
5. TRAIN/VALIDATION/TEST 按确定性 split group 切分，不按单条样本随机切分。group 由 paraphrase family、slot-aware template signature 与机械近重复 signature 合并得到。
6. 所有 TEST_ASSET 及其整个 group 均固定在 TEST。
7. `split_seed=14031`；生成与审计工具位于 `scripts/freeze_sys014_poc7.py` 和 `scripts/validate_sys014_frozen.py`。
8. 本目录是不可变 v1，禁止原地修改；未来数据变化必须创建 `sys014-poc7-v2`。

## 文件

- `train.jsonl`、`validation.jsonl`、`test.jsonl`：冻结后的 candidate split。
- `safety_gold.jsonl`：完全隔离的安全回归集。
- `dataset_manifest.json`：版本、策略、覆盖、计数和 SHA256。
- `split_report.md`：按 split 的覆盖统计。
- `leakage_audit.md`：泄漏与隔离审计。
