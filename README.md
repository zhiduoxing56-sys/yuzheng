# 语证

面向智能座舱高风险车控指令的证据对齐与可解释裁决系统。

当前仓库只完成阶段一“最小安全闭环”：文本指令经配置化语义解析、动作—证据需求、模拟车辆状态证据、确定性硬规则安全门和简化两因子评分后，输出 `PASS`、`REVIEW` 或 `BLOCK`，并写入 SQLite 哈希链审计记录。

## 运行

```powershell
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

健康检查：`GET http://127.0.0.1:8000/api/health`

文本接口：`POST http://127.0.0.1:8000/api/command/text`

## 测试

```powershell
python -m pytest -v
```

后续阶段范围与未实现项见 `docs/实现状态.md`。需求唯一基线为 `docs/语证：面向智能座舱高风险车控指令的证据对齐与可解释裁决系统.pdf`。
