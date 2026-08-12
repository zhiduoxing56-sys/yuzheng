# SYS-014 Stage 4C-A.2 实施计划

1. 以可选参数保持 exp001 单组 trainer 行为，新增 exp002 双参数组与逐 step LR 记录。
2. 新增隔离的 exp002 runner 和 prediction/checkpoint/report helpers。
3. 运行语法、兼容性和无 backward preflight；不创建 exp002。
4. 重复 preflight 后创建不可覆盖 exp002 目录并正式训练最多 10 epochs。
5. 每 epoch 保存完整 Validation predictions 与专项追踪，按冻结规则选择 best/closest。
6. 保存 last、总结、manifest、exp001 对照；核对哈希和禁止项后停止。
