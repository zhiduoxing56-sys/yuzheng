# 独立候选意图召回实验 v1

该目录不被正式后端导入，不生成 `SemanticFrame`，也不执行安全裁决。

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_recall_v1\cli.py "打开车门"
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_recall_v1\cli.py "打开车门" --top-n 12
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_recall_v1\run_acceptance.py
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest -q experiments\intent_recall_v1\test_recaller.py
```

首次启动批量编码锚点并在 `tmp/intent_recall_v1` 创建最小 `.npz` 缓存；后续启动直接读取缓存。CLI 的召回耗时不包含模型和缓存启动耗时。

