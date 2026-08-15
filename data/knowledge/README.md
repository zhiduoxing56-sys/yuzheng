# Trusted 安全知识库（Knowledge Base）

本目录存放**知识库辅助证据需求**模块的数据与说明。主系统裁决时检索知识库，把命中知识节点的 `required_evidence` 并集追加进对应意图的证据需求（`required_types`），使需求变严、更安全。

## 一、数据文件

| 文件 | 说明 |
|---|---|
| `trusted_nodes.jsonl` | **真实/生产知识库**（默认加载）。队友放置或更新该文件即生效 |
| `trusted_nodes.mock.jsonl` | mock 演示数据（默认不加载，测试/演示用） |

## 二、数据格式（每行一个 JSON，UTF-8）

KnowledgeNode v2 核心字段：

```jsonc
{
  "node_id": "知识.安全知识.WINDOW.001",
  "node_type": "安全知识",              // Trusted 判定见下
  "title": "安全: 车窗防误开约束",
  "semantic_description": "自然语言描述（用于向量化检索）",
  "canonical_action": "WINDOW_OPEN",   // ★ 存主系统 intent_id（如 HEADLIGHT_SET_MODE/WINDOW_OPEN/BRAKE）
  "conditions": ["OCCUPANT_PRESENT"],
  "required_evidence": ["OCCUPANT_STATE", "WINDOW_STATE"],  // 32 类 canonical 证据类型
  "optional_evidence": ["ENVIRONMENT_CONDITIONS"],
  "source": "INTEL",
  "chapter": "",
  "clause": "",
  "trust_level": "L2",
  "vector": null,                      // 可选：情报侧预计算向量（768 维，命中则免重嵌入）
  "metadata": { "review_status": "TRUSTED" }
}
```

## 三、Trusted 过滤规则（兼容两种表示）

只保留 Trusted 节点（候选/未审核节点不参与在线裁决，Leakage=0）：

| node_type | metadata 条件 | 是否 Trusted |
|---|---|---|
| `安全知识` | `metadata.review_status == "TRUSTED"` | ✅ |
| `Trusted` | `metadata.status == "ACTIVE"` | ✅ |
| `候选风险` / 其他 | `PENDING_REVIEW` / 无 | ❌ 跳过 |

## 四、如何更新知识库

1. **直接替换/追加** `data/knowledge/trusted_nodes.jsonl`（按上述格式每行一个节点）
2. 生效方式二选一：
   - **重启后端**（自动重新加载）
   - **调用接口热重载**（无需重启）：`POST /api/knowledge/reload`
3. 检查是否生效：`GET /api/knowledge/status`（返回 `ready` / `node_count` / `load_error`）

> 也可用环境变量 `YUZHENG_KNOWLEDGE_DATA_PATH` 覆盖数据路径（如指向 mock）。

## 五、相关接口

| 接口 | 方法 | 说明 |
|---|---|---|
| `/api/knowledge/status` | GET | 知识库状态（ready/enabled/node_count/degraded/load_error） |
| `/api/knowledge/reload` | POST | 热重载知识库（更新后无需重启） |
| `/api/index/status` | GET | 证据索引状态 |
| `/api/command/text` | POST | 提交指令（响应 `evidence_demand` 可看到知识库追加的证据） |

## 六、关键约束

- **`canonical_action` 必须是主系统 intent_id**（对齐 `data/nlu/spec/intent_registry_unified_v1.yaml`）
- **`required_evidence` 必须是主系统 32 类 canonical 证据类型**（加载时自动过滤非标准类型）
  - 可达类型清单见项目根 `证据/evidence_runtime_mapping_v1.yaml`（13 类 SIMULATED 可用）
  - 避免使用 `OCCUPANT_STATE`/`LANE_STATE`/`ESC_STATE` 等 UNAVAILABLE 类型，否则会常态 BLOCK
- **配置**：`config/knowledge.yaml`（`top_k=5` / `min_similarity=0.6` / 索引参数）
- **检索精准度**：`augment` 优先取 `canonical_action == intent_id` 的命中节点，无精确匹配时取相似度 ≥ `min_similarity` 的节点

## 七、相关代码

- `backend/app/models/knowledge.py`（模型 + 加载/过滤）
- `backend/app/services/index/trusted_knowledge.py`（索引 + augment）
- `backend/app/core/pipeline.py`（加载 + 裁决链集成）
- 测试：`backend/tests/unit/test_trusted_knowledge.py`、`backend/tests/integration/test_knowledge_augmented_demand.py`

详细设计见 `C:\Users\28656\Desktop\知识库辅助证据需求接入文档.md` 与 `C:\Users\28656\Desktop\系统证据可达性清单.md`。
