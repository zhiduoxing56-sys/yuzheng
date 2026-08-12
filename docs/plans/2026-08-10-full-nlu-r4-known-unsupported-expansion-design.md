# Full NLU R4 Known-Unsupported Expansion 设计说明

## 背景与目标

以 `data/nlu/spec/intent_registry_r4_core_draft.yaml` 为只读父版本，基于 MAC-SLU 原始 train/dev/test 的“车载控制”frame 扩展 `KNOWN_UNSUPPORTED_CONTROL` 语义空间，保持 71 项 `FORMAL_EXECUTABLE` 集合及顺序完全不变，生成 R4 full draft、证据报告、候选报告、差异和校验结果。本轮不冻结、不重映射、不扩写、不训练。

## 现状与约束

- R4 core SHA256 为 `8726c6f782f2a57ddfd4c3b1557497349d912d3d06acd97c73983650fd9fc827`。
- R3 SHA256 为 `c3c5338af148d24aa58b702e579abf615af1dffc3c1568c09ed2fcdc88164e06`。
- MAC-SLU 原始 train/dev/test 共 20,542 条；其中 8,057 条记录包含 11,471 个“车载控制”frame。
- `FOLLOWING_GAP_REQUIRED` 没有运行代码、mapping、validator 活跃引用；父版本及历史/审计材料中的文字记录不是活跃依赖。
- 原始数据只支持 `FRUNK_OPEN`；`FRUNK_CLOSE` 样本数为 0。
- baseline 只可作为最低优先级历史信息，不参与语义纳入决策。

## 方案对比

### 方案一：证据清单驱动构建

- 优点：每个新增 Intent 可追溯到原始文件、ID、分句和 frame；纳入决策、候选隔离、registry 构建和验证可重复。
- 缺点：需要新增证据提取、构建和校验逻辑。

### 方案二：构建器内直接扫描并添加

- 优点：文件较少。
- 缺点：证据判断和产物构建耦合，难以独立审计。

### 方案三：只增加 ON/OFF

- 优点：最保守。
- 缺点：无法覆盖已人工批准且原始数据明确支持的温度、风量、模式等语义。

## 推荐方案

采用方案一。一个无歧义真实样本即可支持 Intent，不设置人为频次门槛；任何操作、对象或控制属性不唯一的样本只进入候选报告。所有新增 Intent 均为 `PROJECT_NATIVE`、`vss_relation: NONE`、无伪造 VSS provenance，并强制 `KNOWN_UNSUPPORTED_CONTROL`。

## 详细设计

### 架构

1. 证据提取层只读取 R4 core、R3、source screen 和原始 train/dev/test，并记录 SHA256。
2. 决策层用明确的 frame 字段组合识别已批准家族的实际操作子集，保留原始证据引用。
3. 构建层深复制 R4 core，删除死合同，增补 capability family、Intent、合同、ontology、known projection 和统计字段。
4. 审计层生成 expansion、ADAS candidates、other candidates、core-to-full diff。
5. 校验层独立验证父版本、71 项冻结、新增状态、引用、统计、活跃依赖和 PoC 隔离。

### 关键组件

- 原始证据解析器：按 `意图N` 对齐 `split_sens[N-1]`，输出文件、ID、分句、query 和原始 frame。
- 已批准家族分类器：只接受明确对象、功能、操作及调节内容组合。
- 候选分类器：ADAS 及其他未覆盖控制只写 pending 报告，不进入 registry。
- 确定性 registry builder：固定排序并从内容重算统计。
- R4 full validator：父子语义 diff、合同引用、ontology 和 active dependency 检查。

### 数据与合同原则

- VALUE/MODE 只来自原始 frame 或现有确定性合同。
- 不猜温度范围、最大档位、风向枚举、固定步长或百分比。
- 相对表达允许识别 Intent，但参数状态保持 unresolved/incomplete。
- AREA 只复用现有 `area_catalog`；缺省 AREA 不得推断为 DRIVER_POSITION。
- `FRUNK_OPEN` 纳入；`FRUNK_CLOSE` 以 0 样本、`PENDING_NO_REAL_DATA_EVIDENCE` 进入 other candidates。
- FRUNK/TRUNK/HOOD 词法边界按人工确认值冻结，禁止对称生成其他 FRUNK Intent。

### 异常与边界处理

- 任一父版本或原始数据哈希在构建期间变化时停止。
- 无法形成唯一 action-target-attribute 的批准家族样本进入 other candidates。
- ADAS 长尾全部进入 ADAS candidates，禁止自动进入 registry。
- `FOLLOWING_GAP_REQUIRED` 若出现新的活跃引用则停止删除并报告 `BLOCKED_BY_ACTIVE_REFERENCE`。
- 历史、review、audit 和报告中的文字记录不计为活跃依赖，但必须在报告中列出。

### 测试策略

- 严格 YAML 重复键解析。
- 父版本 SHA256 与字节不变。
- formal count=71，ID 集合和顺序与 core 完全一致。
- 新增 Intent 全部为 known-unsupported，ID 与语义三元组唯一。
- family、value/mode/direction/conditional contract、ontology 引用完整。
- required/optional slots 无交集，MODE enum 全为字符串。
- 统计字段由实际内容重算并一致。
- 活跃 `FOLLOWING_GAP_REQUIRED` 引用为 0，PoC 活跃依赖为 0。
- ADAS/other candidates 不进入 registry。

## 风险与待确认项

- `writing-plans` 技能当前不可用，实施由本任务计划承接。
- 工作区已有大量无关未提交改动，本轮不执行 Git 提交。
