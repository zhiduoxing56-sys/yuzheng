# 阶段五音频测试样本

- `public_human_zh.wav`：截取自 Hugging Face 数据集 `Speech-data/Chinese-Speech-Dataset` 的 `chinese.mp3`，CC BY-NC-ND 4.0；用于公开真人中文语音的 LA/PA/ASR 冒烟验证。它不是团队现场录音，测试与文档不得把它描述为团队录音。
- `edge_tts_open_door.wav`：2026-08-01 使用 `edge-tts 7.2.7`、`zh-CN-XiaoxiaoNeural` 实际生成“打开车门”，随后真实解码为 PCM WAV；用于 LA 合成音检测与中文 ASR 验证。
- `speaker_replay_open_door.wav`：将上述合成语音从本机 Realtek 扬声器实际播放，并由本机 Realtek 麦克风阵列重录；用于 PA 重放检测验证。

测试只将这些文件作为真实波形输入，不通过文件名、来源标签或预期结果生成 LA、PA、ASR 或裁决结果。
