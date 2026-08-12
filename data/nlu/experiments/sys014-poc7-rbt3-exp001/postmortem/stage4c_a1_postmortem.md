# SYS-014 Stage 4C-A.1 Postmortem

## 最终结论

exp001 的安全误放是模型泛化/abstention 失败，不是流水线、标签映射或 UFAR 实现错误。`SYS014-POC-0731` 在 9/10 epochs 误放，epoch 5 是其唯一安全门阻断样本。现有 deterministic 路径能因动作缺失而 fail-close 0731，但对正常明确 SINGLE 的附加误拒过高；同时 epoch 5 negation 仍有 7/24 漏判。

推荐：`PATH_B`。

理由：The current guard catches 0731 but adds substantial valid-SINGLE rejection, while the model shows a persistent AMBIGUOUS shortcut and material negation weakness. Use a limited RBT3 safety optimization without changing frozen data.

不推荐直接进入 PATH_A，因为当前 guard 不是无损补丁；不直接进入 PATH_C，因为尚未先验证有限 RBT3 安全优化能否修复 persistent ambiguity 与 negation 短板。

## 冻结输出

```text
PIPELINE_BUG_FOUND=NO
LABEL_MAPPING_BUG_FOUND=NO
UFAR_IMPLEMENTATION_BUG_FOUND=NO
EPOCH5_LOGITS_AVAILABLE=NO
CURRENT_VAGUE_GUARD_DETECTS_0731=YES
CURRENT_VAGUE_GUARD_FAIL_CLOSES_0731=YES
MODEL_ONLY_VALIDATION_UFAR=0.034482758620689655
GUARDED_VALIDATION_UFAR=0.0
MODEL_ONLY_AMBIGUOUS_FALSE_ACCEPT=1
GUARDED_AMBIGUOUS_FALSE_ACCEPT=0
GUARD_FALSE_REJECT_COUNT_ON_VALID_SINGLE=68
NEGATION_DIAGNOSIS_REQUIRED=YES
RECOMMENDED_NEXT_PATH=PATH_B
EXP001_POSTMORTEM_COMPLETE=YES
READY_FOR_NEXT_SAFETY_DECISION=YES
TRAINING_STEPS_EXECUTED_THIS_STAGE=0
TEST_EVALUATION_EXECUTED=NO
SAFETY_GOLD_EVALUATION_EXECUTED=NO
LAST_CHECKPOINT_DIAGNOSTIC_ONLY=YES
```

## 重要边界

- Epoch 5 未保存 logits/probabilities，不能从现有 artifact 恢复其 confidence。
- last checkpoint 仅在 129 条 Validation 上执行 forward-only，没有成为 best/deployment checkpoint。
- Strategy C 仅输出通用候选阈值的 tradeoff，不选择或写入 runtime threshold。
- 本阶段没有读取 Test 或 Safety Gold，没有训练，没有修改 runtime、冻结数据或 safety gate。
