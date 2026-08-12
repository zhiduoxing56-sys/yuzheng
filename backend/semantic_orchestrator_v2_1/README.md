# SemanticOrchestratorV2.1

V2.1 是完全独立的实验扩展层，仅增加：

- `ObjectFamilyGuard`
- 扩展后的 `SecurityClaimGuard`

它继承并复用冻结的 V2、Stage1 v1.3、3B 模型与原门控，不修改正式后端、解析器、安全链或 CARLA。

组件测试：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest experiments\semantic_orchestrator_v2_1\test_components.py -v
```

冻结评估入口：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe -m experiments.semantic_orchestrator_v2_1.run_evaluation
```
