# 语音可信与 ASR 实现说明

## 处理顺序

阶段五按报告固定顺序执行：读取 PC 麦克风或模拟阵列 WAV、计算 SHA-256、频谱分析、LA 检测、PA 检测、可信评分、ASR、区域权限过滤，随后将真实转写文本交给既有 `CommandPipeline`。整轮使用同一 `turn_id`。声学 BLOCK 在 ASR 前终止；声学 REVIEW 允许转写和解释，但不能被后续软评分提升为 PASS。

## 音频与频谱

输入必须为 PCM WAV。适配器将音频解码为单声道浮点波形并重采样到 16 kHz；PC 麦克风由 sounddevice 真实采集。模拟阵列只用显式通道映射提供 `speaker_zone`，不是物理声源定位。

频谱服务直接计算 RMS、80 Hz 以下能量、80～4000 Hz 语音频带能量、6000 Hz 以上能量、静音、削波比例和异常峰值。参数均在 `config/voice.yaml`，没有按文件名或测试期望返回分数。

## LA 与 PA

- LA：`MelodyMachine/Deepfake-audio-detection-V2`，revision `de3cde5a29c449bb5268814e421b46bf6ebdcd72`，来源为 Hugging Face 公共模型仓库，输入为 16 kHz 单声道波形。
- PA：`Vansh180/deepfake-audio-wav2vec2`，revision `e1197e2063deb056b0a6a348f3913d27de7f3d83`，来源为 Hugging Face 公共模型仓库，输入为 16 kHz 单声道波形；模型说明标注其任务为 ASVspoof 2021 PA。

两个模型均用 transformers 本地缓存离线加载、进程内复用实例并返回分类概率。模型缺失或推理失败会明确返回 503，不降级为固定正常分数。LA 模型对本次 Edge TTS 样本单独推理出现假阴性，因此实现透明保留报告允许的频谱辅助：帧静音比例、数字零比例、频谱平坦度和过零率形成配置化辅助风险，再与模型真实概率保守合并。该工程处理只在本次实际样本上验证，不代表覆盖全部合成音或重放条件。

`synthetic_risk = 1 - la_score`，`replay_risk = 1 - pa_score`。综合分严格为：

```text
risk_vec = [synthetic_risk, replay_risk, zone_risk]
trust_score = clip(1 - dot([0.4, 0.4, 0.2], risk_vec), 0, 1)
```

PASS、REVIEW、BLOCK 阈值分别为 0.79、0.45、0，均从配置读取并进入审计。

## ASR

ASR 使用 `openai/whisper-base`，revision `e37978b90ca9030d5170a5c07aadb050351a65bb`，中文转写、本地缓存、进程内复用。文本来自真实模型推理，不从文件名或样本标签生成。当前适配器没有经过校准的整句概率，因此 `asr_confidence=null`，不会固定填写 1.0。空结果会明确记录并安全结束。

## 区域权限

区域标签包括 `driver/front_passenger/rear_left/rear_right/outside/unknown`。权限分按报告计算：

```text
risk = 0.55 * zone_weight[speaker_zone]
     + 0.30 * target_risk
     + 0.15 * action_weight[action]
permission_score = clip(1 - risk, 0, 1)
```

权重、危险对象、动作权重和阈值全部位于 `config/voice.yaml`。区域 BLOCK 会进入既有硬门语义；区域 REVIEW 不能产生直接车辆授权。

## 数据边界

审计、工作流和 WebSocket 只保存输入来源、座位、角色、音频 SHA-256、频谱派生指标、LA/PA/ASR/区域结果及后续裁决。原始音频字节只在请求处理内存中短暂存在，不进入 SQLite、日志、异常或 WebSocket。
