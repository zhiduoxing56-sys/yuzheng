# SYS-014 Stage 4C-B.2 ELECTRA exp002 实施清单

1. 新增隔离 runner，读取 B.1 权重资产并冻结 exp001 基线。
2. 实现 config diff、weight wiring unit test 和 fresh initialization preflight。
3. 实现逐 epoch rich Slot token artifacts、VALUE 19 条专项与安全/Scope/negation 监控。
4. 实现 frozen gate + primary quality checkpoint 选择及 exp002 验收阈值。
5. 实现 best、closest diagnostics、last、summary 与 exp001 对照报告。
6. 使用项目指定 Python 执行编译、既有回归测试和 `--preflight-only`。
7. 仅在两个 preflight gate 均为 YES 时启动训练。
8. 完成后核验 artifact 数量、checkpoint flags、最终字段和所有禁止项。
