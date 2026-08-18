# 中文安全知识库 V1 扩充包 —— 队友使用说明

> 交付日期：2026-08-18 ｜ 交付分支：`knowledge-constraint-v1-delivery`
> 定位：5 个演示场景（夜间关灯 / 雨天关雨刮 / 左后障碍变道 / 无空间泊车 / 突发障碍变道）的中文可读安全规则库 + 检索演示链路

---

## 1. 交付内容

| 路径 | 说明 |
|---|---|
| `knowledge-contract-v1/acceptance/knowledge_constraints_v1_merged.jsonl` | **169 条知识节点（合并单文件，推荐直接使用）** |
| `knowledge-contract-v1/acceptance/knowledge_constraints_v1.jsonl` | V1 冻结 5 条（safety_rules 原版） |
| `knowledge-contract-v1/acceptance/knowledge_constraints_v1_demo.jsonl` | 演示场景 4 条 |
| `knowledge-contract-v1/acceptance/knowledge_constraints_v1_shishitiaoli_v2.jsonl` | 实施条例 25 条（条例 44-84 条） |
| `knowledge-contract-v1/acceptance/knowledge_constraints_v1_batch1.jsonl` | 批量扩充第一批 96 条 |
| `knowledge-contract-v1/acceptance/knowledge_constraints_v1_batch2.jsonl` | 批量扩充第二批 39 条 |
| `knowledge-contract-v1/scripts/v2_demo_retrieval_standalone.py` | **自包含检索演示脚本（直接可跑）** |
| `knowledge-contract-v1/freezes/*.yaml` | 冻结合同：intent 注册表 / 证据类型目录 / 证据运行时映射（字段合法性依据） |
| `scripts/v2_validate_full.py` | 全量结构校验脚本（新增节点后必跑） |

## 2. 环境准备

```
pip install sentence-transformers hnswlib numpy
```

- 嵌入模型：`BAAI/bge-base-zh-v1.5`（768 维）。首次运行脚本会自动下载；
  若内网无网，可先在联网机器下载后拷贝到目标机，并用 `HF_HOME` 环境变量指定缓存目录。
- Python ≥ 3.9（建议 3.11）。

## 3. 运行演示检索（队友在你们环境跑）

```bash
python v2_demo_retrieval_standalone.py --kb knowledge_constraints_v1_merged.jsonl --top-k 20
```

脚本自动完成：加载知识库 → 加载 bge 模型 → 编码建索引（hnswlib cosine）→
对 5 个演示场景（语音指令 + NLU 意图先验词融合查询）输出 Top-20 命中。

结果写入 `demo_retrieval_report.txt`，并打印汇总：

```
① 夜间关闭大灯: 核心命中 2/2 [(1, '知识.灯光.夜间关闭限制.001'), ...] | Top20 BLOCK=6 意图相关=15/20
② 雨天关闭雨刮: 核心命中 3/3 [...] | Top20 BLOCK=8 意图相关=11/20
③ 左后障碍向左变道: 核心命中 3/3 [...] | Top20 BLOCK=13 意图相关=17/20
④ 无空间自动泊车: 核心命中 2/2 [...] | Top20 BLOCK=8 意图相关=12/20
⑤ 突发障碍变道避让: 核心命中 3/3 [...] | Top20 BLOCK=12 意图相关=16/20
```

每行含义：
- `核心命中 x/y`：验证集节点（人工标注的该场景必须出现的规则）出现在 Top-20 中的数量
- `BLOCK=n`：Top-20 中拦截类规则（⛔）数量，演示页可直接突出展示
- `意图相关 n/20`：Top-20 中与本场景意图集合一致的节点占比

## 4. 数据结构（V1 格式，每行一个 JSON）

```json
{
  "node_id": "知识.灯光.夜间关闭限制.001",
  "title": "行驶且低照度时禁止关闭前照灯",
  "semantic_description": "行驶且环境照度低于20 lux时，关闭前照灯会降低驾驶视野安全性。",
  "canonical_action": "HEADLIGHT_SET_MODE",
  "required_evidence": ["ENVIRONMENT_CONDITIONS", "VEHICLE_SPEED"],
  "source": "safety_rules.yaml",
  "chapter": "NIGHT_LIGHTING_OFF_PROHIBITED",
  "clause": "night_low_illumination",
  "trust_level": "L1",
  "command": {"intent_id": "HEADLIGHT_SET_MODE", "action": "SWITCH_MODE", "target": "HEADLIGHT", "area": "ANY", "mode": "OFF"},
  "evidence": {"light": {"type": "ENVIRONMENT_CONDITIONS", "field": "ambient_illumination"},
               "speed": {"type": "VEHICLE_SPEED", "field": "value"}},
  "when": {"all": [{"field": "light", "op": "LT", "value": 20}, {"field": "speed", "op": "GT", "value": 0}]},
  "effect": {"then": "BLOCK", "else": "ALLOW",
             "reason_code": "NIGHT_LIGHTING_OFF_PROHIBITED",
             "reason": "行驶且低照度时关闭前照灯会降低驾驶视野安全性。"}
}
```

关键约定：
- `command.intent_id` 必须为冻结注册表中 **FORMAL** 意图（`freezes/intent_registry_unified_v1.yaml`）
- `evidence.*.type` 必须来自 `freezes/evidence_type_catalog_v1.yaml`；`field` 必须来自
  `freezes/evidence_runtime_mapping_v1.yaml` 对应类型的 value_schema
- `when.all[]` 引用的 `field` 必须是 `evidence` 中的别名；op ∈ EQ/NEQ/NE/GT/GTE/LT/LTE/IN
- `required_evidence` = evidence 中 type 的去重集合（与线上 trusted_knowledge 增强逻辑一致）
- `effect.then` ∈ BLOCK（拦截）/ REVIEW（复核提示）/ ALLOW（允许）

## 5. 检索文本拼接（与线上一致）

```python
parts = [node.title, node.semantic_description, node.canonical_action,
         *[f"REQUIRED {e}" for e in node.required_evidence]]
text = " ".join(parts)
```

## 6. 接入你们系统的建议（重要）

线上裁决侧的等价机制在 `backend/app/services/index/trusted_knowledge.py` 的 `augment()`：
1. 对每个意图候选，用 `query_text`（意图语义）向量检索 Top-K
2. **优先取 canonical_action 与意图精确匹配的节点**（`exact_matches`），避免跨意图串扰；
   无精确匹配时才回退到相似度 ≥ min_similarity 的命中
3. 把命中节点的 `required_evidence` 并集追加进该意图的证据需求（`knowledge_augmented_types`），
   并记录 `knowledge_hits`（node_id/title/trust_level）供前端展示

演示页"Top-20 中文规则展示"可直接复用 `v2_demo_retrieval_standalone.py` 的检索结果；
若要与语音意图结合，把 NLU 解析出的 intent_id 加入查询文本（即脚本中的"意图先验词"机制）。

## 7. 常见问题

- **模型下载失败**：设置 `HF_ENDPOINT=https://hf-mirror.com` 走国内镜像；
  或 `HF_HOME` 指向已含 `models--BAAI--bge-base-zh-v1.5` 的缓存目录
- **想换自己的指令测试**：编辑脚本 `DEMO_SCENES` 列表（name/语音指令/意图先验词/验证集/相关意图）
- **新增节点后**：先跑 `scripts/v2_validate_full.py` 通过（0 错误），再重跑检索脚本
- **Windows 控制台中文乱码**：设 `PYTHONIOENCODING=utf-8`；脚本已内嵌 stdout 重配置

## 8. 知识规模与来源分布（169 条）

| 来源 | 条数 |
|---|---|
| 道路交通安全法实施条例 | 61 |
| 防御性驾驶通用规则 | 54 |
| 驾考知识（科目一/四） | 34 |
| 道路交通安全法 | 9 |
| safety_rules.yaml（冻结 V1） | 5 |
| 让速不让道官方解读 | 4 |
| GB/T 40429-2021 / 公安部交管局安全提示 | 2 |

效果分布：BLOCK 107 / REVIEW 31 / ALLOW 31。
