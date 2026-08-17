# 审计记录 Ed25519 完整性保护设计说明

## 背景与目标

在现有唯一 `audit_records` SQLite 审计表、SHA-256 哈希链和审计页面上增加最小 Ed25519 数字签名保护。不得重算或修改既有历史审计记录，不建立第二套审计模型、数据库或验证接口。

## 现状与约束

- `AuditRepository.save()` 与 `append_review_outcome_with_events()` 是仅有的正式追加入口。
- 现有 `current_hash` 公式、`previous_hash`、`rowid` 排序和 `BEGIN IMMEDIATE` 保持不变。
- 历史审计记录无签名；签名启用边界必须保存在数据库外，且不能在状态丢失时静默重置。

## 推荐方案

采用 `cryptography` 的 Ed25519。审计模型增加可空签名元数据；规范化排除全部完整性字段，因此历史哈希保持可验证。首次签名启动时读取 `MAX(rowid)+1` 并写入数据库外状态文件。此后新记录在同一数据库事务中计算当前哈希、签名哈希并插入。全链验证接口按 `rowid` 同时验证历史哈希链与边界后的强制签名。

## 数据流

`AuditRecord / ReviewOutcomeRecord` → `canonical_json` → 现有 SHA-256 `current_hash` → Ed25519 签名 `bytes.fromhex(current_hash)` → `audit_records`。

## 异常与测试

签名边界后的密钥、状态或签名错误必须阻止写入；历史无签名不算异常。测试覆盖正常新记录、内容/链/签名篡改、缺失签名、删除中间记录、连续追加及历史兼容。
