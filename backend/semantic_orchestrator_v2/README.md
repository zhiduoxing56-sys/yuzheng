# SemanticOrchestratorV2

独立实验层，包装冻结的 Stage1 v1.3、qwen2.5 3B 极简选择器和现有混合门控。

职责：有序控制子句拆分、动作方向冲突降级、信息不足保护、多意图完整性、候选一致性和正交安全声明补充。该层不能创建正式意图，也不能把既有 `REVIEW` 提升为 `OK`。

运行：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe experiments\semantic_orchestrator_v2\run_evaluation.py
```

结果写入 `test-results/semantic-orchestrator-v2/`。正式后端、SemanticFrame、安全裁决链和 CARLA 均未接入。
