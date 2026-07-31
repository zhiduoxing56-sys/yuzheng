# 语证

面向智能座舱高风险车控指令的证据对齐与可解释裁决系统。

当前仓库只完成阶段一“最小安全闭环”：文本指令经配置化语义解析、动作—证据需求、模拟车辆状态证据、确定性硬规则安全门和简化两因子评分后，输出 `PASS`、`REVIEW` 或 `BLOCK`，并写入 SQLite 哈希链审计记录。

## 运行

```powershell
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

健康检查：`GET http://127.0.0.1:8000/api/health`

文本接口：`POST http://127.0.0.1:8000/api/command/text`

## 阶段一裁决字段语义

- `soft_safety_score` 是硬门介入前的软评分；兼容字段 `safety_score` 与其值相同。
- `final_decision` 是硬门和语义完整性检查后的最终裁决；兼容字段 `decision` 与其值相同。
- `gate_blocked` 和 `gate_reasons` 明确表示硬规则是否覆盖软评分。软评分较高不能抵消硬门，例如行驶中打开车门仍然是 `BLOCK`。
- 有强制证据时，`evidence_coverage_applicable=true` 且 `evidence_coverage` 为实际覆盖率。
- 无强制证据时，`evidence_coverage_applicable=false`、`evidence_coverage=null`，该因子从软评分中剔除，剩余权重重新归一化。
- `mandatory_evidence_missing=true` 表示至少一个强制证据节点为 `MISSING`，并直接触发安全门。

## 测试

```powershell
python -m pytest -v
```

后续阶段范围与未实现项见 `docs/实现状态.md`。需求唯一基线为 `docs/语证：面向智能座舱高风险车控指令的证据对齐与可解释裁决系统.pdf`。
