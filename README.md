# 语证

面向智能座舱高风险车控指令的证据对齐与可解释裁决系统。当前实现范围为阶段四“复核恢复、一次性授权、车辆模拟执行与实时交互闭环”：在冻结的真实 BGE/HNSW、安全门、五维评分和高级推理链路之上，增加追加式工作流审计、复核重裁决、HMAC 一次性授权、执行前完整复查、安全模拟执行、状态/场景/审计接口和 WebSocket 实时事件。

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
     → 双重记忆/因果修正/声明对齐 → 完整硬门/五维评分
     → PASS/REVIEW/BLOCK → SQLite 原审计哈希链
     → REVIEW: 确认/修正/取消 → 完整重新裁决
     → PASS: 一次性授权 → 最新状态复查 → 模拟车辆执行
     → 独立工作流事件哈希链 + WebSocket 真实阶段
```

证据仓库维护车辆状态历史、环境、乘员身份与权限、系统模式、传感器健康和安全规则。运行时图直接由本轮真实证据构建，支持 `REQUIRES`、`SUPPORTS`、`RULE_CONSTRAINED`、`PERMISSION_BOUND`、`CONFLICTS`、`TEMPORAL` 和 `DERIVED_FROM` 边，不返回固定演示图。

## 接口

- `GET /api/health`
- `POST /api/command/text`
- `GET /api/evidence/current`
- `GET /api/evidence/turn/{turn_id}`
- `POST /api/index/rebuild`（仅本地开发/演示）
- `GET /api/index/status`
- `GET/PATCH /api/state`、`POST /api/state/reset`
- `POST /api/turns/{turn_id}/review`
- `POST /api/turns/{turn_id}/execute`
- `GET /api/scenarios`、`POST /api/scenarios/{scenario_id}/load|run`
- `GET /api/audits`、详情、导出、时间线与双链校验
- `WS /ws/pipeline/{session_id}`

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
D:\software\anaconda\envs\yuzheng311\python.exe -m compileall -q backend\app backend\tests
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest -v --durations=40
```

阶段边界和真实/降级实现状态见 [docs/实现状态.md](docs/实现状态.md)。需求唯一基线为仓库中的作品报告 PDF。

## 阶段四边界

默认车辆数据和执行来自确定性模拟器，不代表真实传感器或 CAN 总线。文本输入不执行声学可信检查或 ASR。React 前端、音频、麦克风、ASR、合成/重放检测、真实台架控制和真实 CAN 报文不属于阶段四，均未开始。`CanVehicleAdapter` 只提供默认关闭的安全边界，不含报文标识符或发送逻辑。

## 阶段三核心语义

- 双重记忆只允许高安全层向低安全层传播，默认 `alpha=0.3`；冲突证据只会抑制，不会被横向传播抬高。
- 纵向传播显式记录 `support_adjustment`、`risk_adjustment` 和 `final_adjustment`，公式为 `clamp(before + support_adjustment + risk_adjustment, 0, 1)`。
- 因果统计只读取 `record_quality=VALID` 且 `eligible_for_learning=true` 的审计记录；历史不足时仍返回归一化的拉普拉斯平滑先验并标记 `insufficient`。
- 因果当前轮只使用 `feature_cutoff=pre_decision` 列出的裁决前特征；当前轮裁决和车辆执行结果不进入当前轮后验。
- 五维权重为 Csem=0.210、Ccov=0.255、Ctrust=0.255、Cjb=0.255、Cnec=0.025。Cnec 仅由紧急标志、碰撞、障碍距离或制动必要性等真实证据提高，紧急措辞本身不加分。
- `soft_safety_score` 是五维软评分；`final_decision` 是硬门优先后的结果。硬门命中时 `score_evaluation_mode=diagnostic_after_gate`，该分数仅供诊断，不能抵消硬门或作为放行置信度。
- 无强制证据时 `Ccov=null`、`applicable=false`，其权重被剔除后重新归一化；模糊指令使用 `diagnostic_only`，不执行强制补召。
- HNSW 只保存按类型、来源和实体稳定键去重的当前规范证据；MISSING 和运行时派生节点不入索引，本轮图和审计仍保留完整节点。`GET /api/index/status` 可观察更新、重建、去重和临时节点计数。
- 审计质量侧表不参与原审计摘要计算，更新分类不会改变旧哈希链；篡改审计正文仍会导致验链失败。

阶段三新增接口：`GET /api/turns/{turn_id}`、`GET /api/reasoning/turn/{turn_id}`、`GET /api/causal/status`、`POST /api/causal/rebuild`、`GET /api/audits/learning-status`、`GET /api/audits/verify-chain`。

## 阶段四授权与工作流语义

- 原 `audit_records.record_json` 永不修改；复核和执行事件进入 `turn_workflow_events` 的逐 root_turn_id 追加式 SHA-256 链，车辆执行结果进入独立表。
- 只有 PASS、未命中硬门、actionable 且位于动作白名单的轮次签发令牌；查询、REVIEW、BLOCK 和已取消工作流不签发。
- 令牌由 `secrets` 随机 nonce 和 HMAC-SHA256 生成，数据库只保存摘要。密钥优先取 `YUZHENG_TOKEN_SECRET`，否则生成到已忽略提交的 `data/secrets/authorization.key`。
- 原始令牌只出现在首次签发响应；不会进入原审计、工作流事件、日志、数据库或内存轮次缓存。
- 执行前以最新状态重新经过语义解析、证据召回、证据图、校验、硬门和五维评分；状态摘要变化或新硬门会拒绝并使令牌不可用。
- `SimulatorVehicleAdapter` 依据 `config/vehicle_actions.yaml` 修改内存状态；`MockBenchAdapter` 返回确定性模拟反馈；CAN 适配器默认 DISABLED。
- WebSocket 事件来自同一 CommandPipeline 的真实处理位置，无固定延时；session 隔离，断线不影响命令处理，事件载荷不含原始令牌。

阶段三验收命令：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe -m compileall -q backend\app backend\tests
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest -v --durations=40
D:\software\anaconda\envs\yuzheng311\python.exe scripts\benchmark_stage3.py
D:\software\anaconda\envs\yuzheng311\python.exe scripts\run_stage4_acceptance.py --base-url http://127.0.0.1:8765
```
