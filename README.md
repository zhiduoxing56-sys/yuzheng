# 语证

面向智能座舱高风险车控指令的证据对齐与可解释裁决系统。当前实现范围为阶段五“可信语音输入、LA/PA 检测与 ASR 链路”：阶段一至阶段四点一闭环保持不变，新增 PC 麦克风和模拟车载阵列通道输入、真实频谱分析、离线 LA/PA 模型推理、Whisper 中文转写及区域权限前置过滤。

## 安装与运行

本仓库真实验收固定使用 `D:\software\anaconda\envs\yuzheng311\python.exe`。该环境必须安装 sentence-transformers、`BAAI/bge-base-zh-v1.5`、Whisper、LA/PA 本地模型和 hnswlib 0.8.0：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe -m pip install -r backend\requirements-real-runtime.txt
D:\software\anaconda\envs\yuzheng311\python.exe scripts\preflight_real_runtime.py
D:\software\anaconda\envs\yuzheng311\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8765
```

系统只读取本地 Hugging Face 缓存，不自动联网下载模型。BGE 缺失或加载失败时使用确定性 768 维哈希向量，但会进入 `RESTRICTED`：R3 可执行车控直接 BLOCK，R1/R2 最高 REVIEW，查询返回但 `actionable=false`，且不签发或执行令牌。hnswlib 单独不可用时继续使用真实 BGE + 精确余弦，只降低检索效率，不降低安全裁决能力。所有降级都会进入健康、响应、审计、工作流和 WebSocket，禁止静默降级。

## 已实现链路

```text
PC麦克风/模拟阵列WAV → 频谱 → LA合成音检测 → PA重放检测
     → 语音可信评分 → Whisper ASR → 区域权限过滤
文本/ASR文本 → SemanticFrame → EvidenceDemand/768维向量
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
- `POST /api/command/audio`（PCM WAV 请求体）
- `POST /api/command/microphone`（真实 PC 录音设备）
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
D:\software\anaconda\envs\yuzheng311\python.exe -m pytest -v --durations=50
```

阶段边界和真实/降级实现状态见 [docs/实现状态.md](docs/实现状态.md)。需求唯一基线为仓库中的作品报告 PDF。

## 审计列表摘要迁移与恢复

审计列表使用独立紧凑摘要表进行数据库筛选和分页，原始 `audit_records.record_json` 保持不变。首次部署本优化前应停止后端，然后执行幂等迁移：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe backend\scripts\migrate_audit_list_summaries.py
```

脚本会先在 `data/database/backups` 创建数据库备份并校验 SHA-256，再在事务内回填摘要，最后核对命令审计总数以及 `audit_id`、`turn_id`、`decision`、`created_at`。重复执行会重新核对并安全更新摘要，不删除或改写原审计载荷。迁移异常会自动从本次备份恢复。

手动恢复时先停止后端，再指定脚本输出的备份路径：

```powershell
D:\software\anaconda\envs\yuzheng311\python.exe backend\scripts\migrate_audit_list_summaries.py `
  --restore-from data\database\backups\yuzheng-pre-audit-summary-YYYYMMDDTHHMMSSZ.db
```

性能基线、正确性对比和验收数据见 [docs/audit-performance-baseline-2026-08-04.md](docs/audit-performance-baseline-2026-08-04.md)。

## 阶段五边界

默认车辆数据和执行仍来自确定性模拟器，不代表真实传感器或 CAN 总线。文本接口保持原有语义，不伪造声学检查。PC 麦克风是真实设备采集；多座位来源仅由明确的模拟通道映射给出，不代表已接入真实车载阵列定位。React 前端、CARLA、真实台架和真实 CAN 均未开始。`CanVehicleAdapter` 仍仅提供默认关闭的安全边界。

## 阶段五可信语音语义

- `VoiceTrustResult` 的 LA、PA 分数来自本地模型真实推理；模型加载失败返回明确服务错误，不生成正常分数。综合分严格采用 `1 - dot([0.4,0.4,0.2], [synthetic_risk,replay_risk,zone_risk])` 并裁剪到 0～1。
- LA 使用 `Sara1708/deepfake-audio-wav2vec2` 的单一 ASVspoof LA 检查点；PA 只使用 ASVspoof 2021 官方 PA LFCC-LCNN 权重；ASR 只使用 `openai/whisper-base`。PA 原始 bonafide 方向标量保存在 `pa_raw_score`，`pa_score` 是其 sigmoid 归一化工程可信分数，不表述为校准概率。不存在通用深度伪造 PA 回退、候选切换、模型投票或加权融合。ASVspoof LFCC-LCNN 的 BSD 3-Clause 许可见 `THIRD_PARTY_NOTICES.md`。
- 最小现场验收如实保留限制：当前扬声器重录样本出现 PA 漏检，但 LA 风险和后续安全链仍阻止令牌签发；本地真人“打开车门”录音能生成真实 ASR、SemanticFrame、EvidenceDemand 和证据子图。项目不宣称跨设备、跨语言或通用检测准确率。
- `asr_confidence` 为 `null`：当前 Whisper 适配器没有可校准、可解释为整句置信度的输出，因此不以固定值冒充。
- 语音可信策略默认使用 `enforce`：声学 BLOCK 在 ASR 前终止且不能签发令牌；声学 REVIEW 可转写并进入既有复核语义，但最终不得被后续软评分提升为 PASS。
- 阶段五点一提供临时集成用 `observe` 模式：设置 `YUZHENG_VOICE_TRUST_MODE=observe` 后，LA、PA、频谱、可信评分、审计和实时事件仍真实执行，但纯 LA/PA 风险不再改变后续裁决或授权；静音/无有效语音、ASR 失败、区域权限、安全门、证据缺失和原车辆规则仍照常生效。健康接口、`VoiceTrustResult.model_metadata` 和 `VOICE_TRUST_DECIDED` 会明确返回模式及 `authorization_effect_applied`。界面语义应为“声学防伪结果处于观测模式，当前不参与授权裁决。”该模式仅用于中文座舱域偏移下的联调，不代表模型有效或准确率达标。
- ASR 原文完整保留；SemanticFrame 在解析前使用配置化、字符级的常用繁体转简体映射，再执行既有口语规范化。`播放音樂` 因此解析为 `播放/音乐`，未知动作保持 `unknown`，不会默认成“打开”。
- 审计和 WebSocket 保存 SHA-256 指纹、模型结果和处理事件，不保存原始音频。实际样本、限制和验收结果见 [docs/阶段五验收说明.md](docs/阶段五验收说明.md) 与 [docs/语音可信与ASR实现说明.md](docs/语音可信与ASR实现说明.md)。
- 最小现场冒烟入口：`D:\software\anaconda\envs\yuzheng311\python.exe scripts\stage5_voice_smoke.py --human <真人WAV> --synthetic <合成WAV> --replay <扬声器重录WAV>`。

## 阶段四冻结安全语义

- 授权密钥具备稳定 `key_id`、版本、创建时间、SHA-256 指纹、来源和状态元数据；令牌表保存签发时的 `key_id`。
- 密钥文件固定为 32 字节。文件为空、截断、长度错误或不可读时服务安全失败；密钥丢失或指纹变化时先原子撤销旧 `ISSUED` 令牌，再生成或启用新密钥。旧终态令牌不改变。
- 可用 `YUZHENG_TOKEN_SECRET` 提供环境变量密钥，或用 `YUZHENG_TOKEN_KEY_FILE` 指定本地密钥文件；数据库路径可用 `YUZHENG_DATABASE_PATH` 指定。密钥内容不会通过健康接口、日志或审计返回。
- `SensitiveDataRedactor` 同时按敏感字段和授权令牌格式递归脱敏，覆盖指令、复核、工作流、审计、导出、WebSocket、日志、异常和请求验证错误。
- 执行成功实时尾序列为 `VEHICLE_PRECHECKED → TOKEN_CONSUMED → VEHICLE_EXECUTED → AUDIT_SAVED`；适配器失败使用 `EXECUTION_FAILED`，不冒充 `VEHICLE_EXECUTED`；复检失败在 `VEHICLE_PRECHECKED → AUDIT_SAVED` 后终止。
- 模拟器状态返回 `state_epoch_id/started_at/reset_count/last_reset_at/reset_reason`。时间线分别返回 `historical_execution_state` 和 `current_simulator_state`，服务重启不会把历史执行后状态伪装成当前状态。
- 冻结安全修复后全量测试为 `75 passed, 1 warning in 126.54s`；真实服务验收脚本为 `scripts/run_stage4_freeze_acceptance.py`。

## 阶段四点一运行时边界

- `RuntimeCapabilityStatus` 统一返回嵌入实现/模型/维度/真实推理状态、索引实现、FULL/RESTRICTED/QUERY_ONLY、降级原因与检查时间。
- 语义模型降级由 Safety Gate、决策上限、授权服务和执行前复查共同强制；Cnec、软评分、记忆和因果排序均不能恢复 PASS。
- `EvidenceRepository` 按 `evidence_type + source + entity_id` 保持稳定流，每条动态流最多 16 个快照，轮次映射最多 64 轮；静态规则长期保留，MISSING/冲突派生/解释节点在审计后清理。完整历史仍在 SQLite 审计中。
- 因果输出区分 `posterior_concentration` 与可空 `decision_confidence`。零样本、单节点或少于 20 条合格历史时决策置信度为 null；模型按审计后合格记录计数重建，当前轮不会进入当前轮后验。
- 真实环境预检：`D:\software\anaconda\envs\yuzheng311\python.exe scripts\preflight_real_runtime.py`。安全源码包：`D:\software\anaconda\envs\yuzheng311\python.exe scripts\export_source_package.py`，仅打包 Git 跟踪源文件并排除密钥、数据库与缓存。
- 阶段四点一最终回归为 `87 passed, 1 warning in 226.24s`；1000 轮有界基准脚本为 `scripts/benchmark_stage4_1_retention.py`，实际 HNSW 规范节点 `33→33`、动态流最大 16、轮次映射 64、两条链有效。

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
