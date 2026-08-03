# 语证后端前端契约 v1

状态：`FROZEN`；版本：`1.0.0`；`frozen=true`。

前端实现以 `frontend-contract-v1.json` 为语义入口，以 `openapi-public-v1.json` 为 HTTP 传输结构依据，以 `frontend-contract-v1.md` 为人工可读说明。`manifest.json` 用于完整性校验。

本目录由 `scripts/generate_backend_contract.py` 从生产 Schema 与 FastAPI OpenAPI 生成，不得手工编辑生成文件。相同源码生成的五个文件必须字节一致。

冻结范围仅含九条 HTTP 路径和 `/ws/pipeline/{session_id}`。内部调试、状态写入、执行、场景和模型维护路径不属于 v1 前端契约。

外部 LLM provider 当前未配置；前端必须展示确定性 fallback 的真实状态，不得显示 provider 已验证。旧审计缺少 Step2/Step5 字段时显示 `LEGACY_NOT_RECORDED`，不得触发重算。

兼容性：破坏性修改必须发布新版本，不得覆盖本目录中的 v1 冻结文件。
