# SYS-014 Stage 4C-B ELECTRA exp001 实施清单

1. 新增隔离 ELECTRA exp001 runner，固定 Stage 4A model provenance 与基线协议。
2. 增加只读 preflight：数据/模型 hash、head shape、mask、projection、prediction schema、初始化来源和单参数组审计。
3. 增加正式训练循环、逐 epoch Validation artifact、冻结 safety gate 选择和 early stopping。
4. 增加 checkpoint、summary、error cases 与 RBT3 exp001 对照报告。
5. 使用指定 Python 环境运行编译和针对性测试。
6. 先运行 `--preflight-only`；确认零 backward/optimizer step 后再运行正式训练。
7. 核验目录、epoch 数、checkpoint flags、禁止项以及最终四个决策字段。
