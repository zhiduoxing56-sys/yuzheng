# 项目环境约束

本项目必须使用：

D:\software\anaconda\envs\yuzheng311\python.exe

禁止使用：
- 系统 Python
- conda base
- 其他虚拟环境

执行 Python 命令必须使用：

D:\software\anaconda\envs\yuzheng311\python.exe

例如：

测试：
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest -v

启动：
D:\software\anaconda\envs\yuzheng311\python.exe -m uvicorn app.main:app --app-dir backend

检查环境：

D:\software\anaconda\envs\yuzheng311\python.exe -c "import hnswlib, sentence_transformers; print('ok')"