# SYS-014 NLU 实验目录（Stage 4C 预留）

Stage 4B 不创建正式 experiment 或 checkpoint。Stage 4C 每次实验必须使用独立目录：

```text
sys014-poc7-rbt3-exp001/
├── experiment_config.json
├── metrics.json
├── training_log.jsonl
├── checkpoints/
├── evaluation/
└── manifest.json
```

目录只能由 `training_enabled=true` 的 Stage 4C 入口创建，并必须记录 dataset/manifest hash、registry、model revision、seed、超参数、Git commit、device 与 Torch version。
