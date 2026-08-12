# SYS-014 Stage 4C-A.1 实施计划

1. 只读审计 exp001 历史、标签映射、loss masking、UFAR 和冻结安全门。
2. 新增独立 postmortem runner，加入禁止训练与数据边界断言。
3. 用 last checkpoint 对冻结 Validation 做 forward-only，采集概率、margin 和错误明细。
4. 直接复用现有 `SemanticFrameParser` 和 `semantic_rules.yaml` 评估 vague guard。
5. 比较 Strategy A/B/C，并单独诊断正常 ACCELERATE 与 negation 短板。
6. 生成五份冻结产物，运行验证并报告唯一推荐路径。
