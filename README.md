# 语证

面向智能座舱高风险车控指令的证据对齐与可解释裁决系统。当前冻结范围为阶段二“完整证据闭环”：文本指令依次经过配置化语义解析、768 维需求向量、语义候选检索、强制证据补召、证据质量评估、运行时证据子图、阶段一安全门与三态裁决，并写入 SQLite 哈希链审计。

## 安装与运行

要求 Python 3.10+。核心依赖不会下载模型，也不要求 hnswlib：

```powershell
python -m pip install -r backend\requirements.txt
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

若本机具备兼容的本地模型或希望启用 hnswlib，可额外安装：

```powershell
python -m pip install -r backend\requirements-optional.txt
```

系统只读取本地 Hugging Face 缓存，不自动联网下载模型。模型缺失或二进制依赖不兼容时自动使用确定性 768 维哈希向量；hnswlib 不可用时自动使用精确余弦检索。两种降级都会在响应和审计中明确记录，不会伪装成真实模型或 HNSW 推理。

## 已实现链路

```text
文本 → SemanticFrame → EvidenceDemand/768维向量
     → 语义候选检索 → 强制覆盖检查/补召/MISSING
     → ECR/ECS/EF/SAS/EAS → 运行时证据子图
     → 阶段一硬门 → PASS/REVIEW/BLOCK → SQLite 哈希链
```

证据仓库维护车辆状态历史、环境、乘员身份与权限、系统模式、传感器健康和安全规则。运行时图直接由本轮真实证据构建，支持 `REQUIRES`、`SUPPORTS`、`RULE_CONSTRAINED`、`PERMISSION_BOUND`、`CONFLICTS`、`TEMPORAL` 和 `DERIVED_FROM` 边，不返回固定演示图。

## 接口

- `GET /api/health`
- `POST /api/command/text`
- `GET /api/evidence/current`
- `GET /api/evidence/turn/{turn_id}`
- `POST /api/index/rebuild`（仅本地开发/演示）
- `GET /api/index/status`

完整字段和请求示例见 [docs/接口说明.md](docs/接口说明.md)。

## 裁决字段语义

- `soft_safety_score` 是阶段一硬门介入前的兼容软评分；`safety_score` 与其值相同。
- `final_decision` 是最终裁决；兼容字段 `decision` 与其值相同。
- `gate_blocked` 和 `gate_reasons` 表示硬规则是否覆盖软评分；其他分数不能抵消硬门。
- 有强制证据时 `evidence_coverage_applicable=true`，ECR/覆盖率按实际可用强制类型计算。
- 无强制证据时 `evidence_coverage_applicable=false`、ECR/覆盖率为 `null`，该因子从相应评分中剔除并重新归一化。
- 阶段二的 EAS 是证据对齐质量指标，不替代阶段一裁决评分。五维动态评分属于后续阶段，本阶段未实现。

## 测试

```powershell
python -m compileall -q backend\app backend\tests
python -m pytest -v --durations=30
```

阶段边界和真实/降级实现状态见 [docs/实现状态.md](docs/实现状态.md)。需求唯一基线为仓库中的作品报告 PDF。

## 阶段二边界

默认车辆数据来自确定性模拟器，不代表真实传感器或 CAN 总线。文本输入不执行声学可信检查或 ASR。`corrected_weights={}`、`decision_confidence=null` 且 `advanced_reasoning_applied=false` 明确表示尚未进入双重记忆、因果修正、完整越狱聚合和五维动态评分。前端、WebSocket、复核重跑、授权令牌、音频和真实车机总线也未开始。
