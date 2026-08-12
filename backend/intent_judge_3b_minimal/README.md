# qwen2.5 3B 极简候选多选实验

该目录只复用 v1.1 第一阶段召回和上一轮 60 条测试输入。生成模型原始输出只有 `intent_ids`，状态、空参数、拼音确认及安全信号均由程序派生。该目录不被正式后端导入。

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_judge_3b_minimal\cli.py "打开车门"
D:\software\anaconda\envs\yuzheng311\python.exe experiments\intent_judge_3b_minimal\evaluate.py --hot-runs 50
```

正式结果写入 `test-results/intent-judge-3b-minimal/`。本轮 3B 多意图明显提升且延迟达标，但单意图、空数组拒识和错误强制归类未通过语义生死门，因此不接入正式系统，也不继续测试 7B。
