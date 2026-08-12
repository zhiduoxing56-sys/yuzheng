# 精度优先混合置信门控实验

该目录只组合冻结的 v1.1 三路召回器和冻结的 3B 极简候选多选器，不被正式后端导入。

执行顺序：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_hybrid_gate\diagnose_recall.py
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_hybrid_gate\calibrate_gate.py
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_hybrid_gate\evaluate.py
```

`gate_config.yaml` 的 SHA256 在校准后冻结；运行门控或评测时若摘要变化会直接报错。新外测集只在阈值冻结后创建和运行，外测结果不用于回调阈值。
