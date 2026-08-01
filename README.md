# 语证

面向智能座舱高风险车控指令的证据对齐与可解释裁决系统。当前实现范围为阶段三“高级推理、越狱防护与完整安全裁决闭环”：在阶段二真实 BGE/HNSW 证据闭环之上，增加双重记忆、因果贝叶斯修正、上下文声明对齐、越狱风险聚合、16 项硬性安全门、五维动态评分和审计样本质量隔离。

## 安装与运行

本仓库阶段三验收固定使用 `D:\software\anaconda\envs\yuzheng311\python.exe`。该环境已安装 sentence-transformers、`BAAI/bge-base-zh-v1.5` 本地模型和 hnswlib 0.8.0：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe -m pip install -r backend\requirements.txt
D:\software\anaconda\envs\yuzheng311\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765
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
- EAS 是证据对齐质量指标，不替代阶段三五维安全评分；阶段三五维评分已实现并独立接受硬门覆盖。

## 测试

```powershell
python -m compileall -q backend\app backend\tests
python -m pytest -v --durations=30
```

阶段边界和真实/降级实现状态见 [docs/实现状态.md](docs/实现状态.md)。需求唯一基线为仓库中的作品报告 PDF。

## 阶段三边界

默认车辆数据来自确定性模拟器，不代表真实传感器或 CAN 总线。文本输入不执行声学可信检查或 ASR。前端、WebSocket、复核重跑、授权令牌、车辆动作执行、音频和真实车机总线不属于阶段三，均未开始。

## 阶段三核心语义

- 双重记忆只允许高安全层向低安全层传播，默认 `alpha=0.3`；冲突证据只会抑制，不会被横向传播抬高。
- 因果统计只读取 `record_quality=VALID` 且 `eligible_for_learning=true` 的审计记录；历史不足时仍返回归一化的拉普拉斯平滑先验并标记 `insufficient`。
- `soft_safety_score` 是硬门前五维评分；`final_decision` 是硬门覆盖后的结果。任何硬门命中都强制 `BLOCK`，高软评分不能抵消。
- 无强制证据时 `Ccov=null`、`applicable=false`，其权重被剔除后重新归一化；模糊指令使用 `diagnostic_only`，不执行强制补召。
- 审计质量侧表不参与原审计摘要计算，更新分类不会改变旧哈希链；篡改审计正文仍会导致验链失败。

阶段三新增接口：`GET /api/turns/{turn_id}`、`GET /api/reasoning/turn/{turn_id}`、`GET /api/causal/status`、`POST /api/causal/rebuild`、`GET /api/audits/learning-status`、`GET /api/audits/verify-chain`。

阶段三验收命令：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe -m compileall -q backend\app backend\tests
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest -v --durations=40
D:\software\anaconda\envs\yuzheng311\python.exe scripts\benchmark_stage3.py
```
