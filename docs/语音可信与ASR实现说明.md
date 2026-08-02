# 语音可信与 ASR 实现说明

## 最小处理链

PC 麦克风或 PCM WAV 输入依次经过格式校验、16 kHz 单声道重采样、频谱异常分析、单一 LA 合成音检测、单一 PA 重放检测、语音可信评分、中文 ASR 和区域权限过滤；真实转写随后进入既有语义帧、证据图和安全裁决链。模拟车载阵列只通过显式通道映射产生 `speaker_zone`，不声称物理声源定位。

## 模型与输入

- LA：完整 ID 为 `Sara1708/deepfake-audio-wav2vec2`，revision `6c43629c953d6ff008501bf5f3eb983ac2321ad6`，来源为 <https://huggingface.co/Sara1708/deepfake-audio-wav2vec2>，使用其 `stage2_best.pt` 单一检查点。仓库缓存不含独立 `config.json`，运行配置显式固定 `id2label={0:bonafide,1:spoof}`、`label2id={bonafide:0,spoof:1}`；映射依据为项目推理代码。该模型只作为原型 LA 能力，不宣称跨设备、跨语言或通用准确率。
- PA：`ASVspoof-2021-PA-LFCC-LCNN-official`，系统唯一 PA。结构和权重来自 <https://github.com/asvspoof-challenge/2021/tree/main/PA/Baseline-LFCC-LCNN> 与 <https://www.asvspoof.org/asvspoof2021/pre_trained_PA_LFCC-LCNN.zip>；训练任务为 ASVspoof 2019 PA。权重路径 `data/models/asvspoof2021_pa_lfcc_lcnn.pt`，SHA-256 `1c6d6f30ed1042e584508a9adecc0e514983fff64cdfb3ae3de848064b6e91e0`。训练标签为 `0=spoof、1=bonafide`，官方输出是越高越接近 bonafide 的未校准标量。BSD 3-Clause 版权与许可全文保留在 `THIRD_PARTY_NOTICES.md`。
- ASR：`openai/whisper-base@e37978b`，显式 `language=zh`、`task=transcribe`。

LA/ASR 只读加载本地缓存，PA 加载仓库内固定权重；三者均在进程内复用。加载、摘要校验或推理失败会返回明确服务错误，不生成固定正常分数。PA 不回退到通用深度伪造模型。没有候选模型切换、模型投票、加权融合或替代 ASR 框架。

输入必须是 PCM WAV；服务执行采样宽度校验、单声道转换和 16 kHz 重采样。PA LFCC 使用预加重 0.97、1024 点 FFT、320 点 Hamming 窗、160 点 hop、20 个线性滤波器、20 个 LFCC 系数及一/二阶差分。频谱服务从真实波形计算 RMS、频带能量、高频异常、静音和削波。频谱异常分数独立记录，不改写 LA 或 PA 模型分数。

## 分数方向与报告公式

`la_score` 是 LA 模型给出的真人/非合成可信概率，`synthetic_risk = 1 - la_score`。PA 三个字段严格区分：`pa_raw_score` 是官方 PA 模型原始、未校准的 bonafide 方向标量；`pa_score = sigmoid(pa_raw_score)` 是映射到 0～1 的归一化真人可信分数，不是经过概率校准的 `P(bonafide)`；`replay_risk = 1 - pa_score` 是由归一化分数生成的工程风险值。

可信分严格使用报告代码 2：

```text
risk_vec = [1 - la_score, 1 - pa_score, zone_risk]
trust_score = clip(1 - dot([0.4, 0.4, 0.2], risk_vec), 0, 1)
```

当前配置阈值为 PASS `0.90`、REVIEW `0.45`、BLOCK `0`。默认 `voice_trust_mode=enforce`，此时声学 REVIEW/BLOCK 不签发授权令牌，也不能被后续软评分提升为 PASS。

阶段五点一增加 `observe` 作为临时联调模式。它不改变任何 LA/PA 模型、阈值或报告公式：所有声学推理、最终分数、模型状态、音频指纹、审计与实时事件均保留，只令纯 LA/PA 结果不再参与后续授权裁决。该模式通过启动环境变量选择，健康接口及每轮 `model_metadata` 明确标识；区域权限和既有硬安全门完全独立。对外说明必须使用“声学防伪结果处于观测模式，当前不参与授权裁决。”不能把观测结果称为准确率、放行置信度或有效检测结论。

引入该模式的原因是当前公开 LA/PA 模型的训练域与中文座舱录音存在明显偏移：既有真人录音的 LA 分数接近零，而已知重放样本也出现 PA 漏检。`observe` 只保证软件链持续采集真实观测和验证下游集成，不修正或美化这些模型限制。

## 区域权限

区域权限严格使用报告代码 3：

```text
risk = 0.55 * zone_weight[speaker_zone]
     + 0.30 * target_risk
     + 0.15 * action_weight[action]
permission_score = clip(1 - risk, 0, 1)
```

区域 BLOCK 进入既有安全门；区域 REVIEW 不产生直接车辆授权。

## 数据与适用边界

SQLite、日志、异常和 WebSocket 不保存原始音频，只保存 SHA-256、最终 LA/PA 风险、频谱派生指标、ASR 文本与置信度、区域结果、模型名和推理状态。当前仅以一条公开真人音频、一条合成音频、一条真实扬声器重放音频及程序生成的静音/损坏输入证明软件闭环，不宣称通用准确率、多说话人或多距离泛化。`asr_confidence=null` 表示当前适配器没有可解释为整句概率的输出。
