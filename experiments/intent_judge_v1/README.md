# 本地候选意图裁决实验 v1

该目录只连接第一阶段 v1.1 和本机 `qwen2.5:1.5b`，不被正式后端导入。

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_judge_v1\cli.py "打开车门"
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_judge_v1\cli.py "打开运动莫斯" --debug
```

默认 CLI 只输出 `status`、`sub_intents`、`confirmation` 和正交保留的 `security_signals`。`--debug` 额外显示 Ollama 原始 JSON、校验错误和延迟/token 指标。

完整离线验收命令：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_judge_v1\evaluate.py --hot-runs 50
```

评测会先显式卸载模型并记录一次冷请求，然后预热并执行 60 条能力用例和 50 次真实热请求。结果写入 `test-results/intent-judge-v1/`。当前 `qwen2.5:1.5b` 的延迟门通过，但多意图和拒识能力门未通过，因此本实验不接入正式系统。
