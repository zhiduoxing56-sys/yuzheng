# 本地 PA 模型权重

`asvspoof2021_pa_lfcc_lcnn.pt` 是系统唯一 PA 模型权重。

- 结构：ASVspoof 2021 官方 PA LFCC-LCNN baseline
- 官方仓库路径：`asvspoof-challenge/2021/PA/Baseline-LFCC-LCNN`
- 官方代码来源：<https://github.com/asvspoof-challenge/2021/tree/main/PA/Baseline-LFCC-LCNN>
- 官方预训练模型下载来源：<https://www.asvspoof.org/asvspoof2021/pre_trained_PA_LFCC-LCNN.zip>
- 官方下载脚本来源：<https://github.com/asvspoof-challenge/2021/blob/main/PA/Baseline-LFCC-LCNN/project/00_download.sh>
- 本地文件名：`data/models/asvspoof2021_pa_lfcc_lcnn.pt`
- 训练任务：ASVspoof 2019 Physical Access replay attack
- 训练标签：`0=spoof`、`1=bonafide`
- `pa_raw_score`：官方 PA 模型原始、未校准的 bonafide 方向标量；分数越高越接近 bonafide
- `pa_score`：`sigmoid(pa_raw_score)` 映射到 0～1 的归一化真人可信分数，不表述为经过概率校准的 `P(bonafide)`
- `replay_risk`：由归一化分数生成的工程风险值，`1 - pa_score`
- 输入：16 kHz 单声道波形，经 LFCC 前处理后进入 LCNN/BLSTM
- SHA-256：`1c6d6f30ed1042e584508a9adecc0e514983fff64cdfb3ae3de848064b6e91e0`
- 许可：BSD 3-Clause
- 版权所有：Copyright (c) 2020, Xin Wang, National Institute of Informatics

运行时先校验文件摘要；权重缺失、损坏或加载失败会安全拒绝，不回退到固定分数或通用深度伪造模型。
二进制分发时必须同时保留仓库根目录 `THIRD_PARTY_NOTICES.md` 中的版权声明、许可条件和免责声明。
