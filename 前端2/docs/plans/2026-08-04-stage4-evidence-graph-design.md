# 阶段四证据检索与图谱导航设计

## 背景与目标

本阶段仅修改 `frontend`，实现连接真实 presentation、证据子图、节点详情和高级推理接口的证据导航页。页面提供四层分层图谱、节点详情、筛选、当前子图搜索、二维/三维切换、全屏和刷新恢复，不重新计算裁决、质量或因果结论。

不实现复核提交、审计详情、场景控制台、系统维护，也不修改后端业务代码和冻结契约。

## 只读核对结论

- `EvidenceSubgraph` 使用 `graph_id`、`turn_id`、`nodes`、`edges`、`required_types`、`retrieved_types`、`mandatory_recalled_types`、`missing_types`、`quality_metrics`、`retrieval_metadata`、`corrected_weights`、`decision_confidence`、`advanced_reasoning_applied` 和 `advanced_reasoning_status`。
- 节点唯一编号为 `node_id`，层级权威字段为 `security_rank`（0–3），`layer` 为后端业务标签。
- 节点真实状态为 `VALID`、`SUSPICIOUS`、`STALE`、`TAMPERED`、`MISSING`。冲突不是节点状态，而由 `CONFLICTS` 边和冲突记录表达。
- 边使用 `edge_id`、`source`、`target`、`relation`、`weight`、`reason`。
- 节点详情包含入边、出边、安全分层、规范化、记忆传播和因果权重等真实字段。
- 后端没有定义完整最终裁决路径。页面只能根据后端明确返回的引用、强制证据、冲突、规则边和推理支持字段展示“关键裁决证据”。
- 指定的 `backend/app/services/retrieval` 和 `backend/app/services/recall` 目录不存在；真实实现位于 `services/index/hnsw.py` 与 `services/evidence/recall.py`。

## 方案对比

### 方案一：双图谱库独立懒加载（采用）

- 三维使用 `react-force-graph-3d` 与 `three`，二维使用 `react-force-graph-2d`。
- 优点：交互能力完整、降级边界清晰、维护风险较低。
- 缺点：证据页面异步包较大，需要严格路由分包。

### 方案二：三维库加自研 Canvas 二维降级

- 优点：二维依赖较少。
- 缺点：交互和资源生命周期重复实现，风险较高。

### 方案三：完全自研 Three.js 与 Canvas

- 优点：控制力最高。
- 缺点：超出本阶段功能优先边界。

## 详细设计

### 架构与依赖

```text
App 路由懒加载
  -> EvidencePage（轮次、筛选、搜索、模式、选中节点）
    -> 专用数据 Hooks -> API
    -> evidenceGraphAdapter（唯一业务字段解释层）
    -> EvidenceGraphPanel（懒加载）
      -> EvidenceGraph3D（默认异步加载）
      -> EvidenceGraph2D（失败降级或手动选择）
```

二维和三维渲染器只消费同一个适配结果，不解释后端业务字段。实时裁决页仅生成普通路由链接，不引用图谱模块。

### 数据流与状态归属

1. 地址参数优先确定轮次；无参数时依次使用 `currentTurnId` 和最近轮次第一项。
2. `useEvidenceTurn`、`useEvidenceSubgraph` 并行加载文字摘要和子图，互不阻塞。
3. 子图经过唯一适配器校验、去重、过滤悬空边并产生纯展示字段。
4. 筛选和搜索仅改变可见图数据，不修改原始响应。
5. 节点点击触发独立节点详情请求；新节点、关闭详情、切换轮次和卸载都会取消旧请求。
6. 高级推理仅在首次展开时请求。
7. 切换轮次保留用户手动图谱模式，重置筛选、搜索和节点选择。

`sessionStore` 继续只保存阶段三定义的长期状态。证据页局部状态不进入全局存储。

### 图谱渲染与生命周期

- 默认异步加载三维；依赖加载、初始化或运行失败时自动降级二维。
- 单次页面生命周期最多自动降级一次，禁止二维/三维循环切换。
- 用户手动切换模式后在当前浏览器会话中保存；它不随轮次重置。
- 两个渲染器自行持有图形引用、动画循环和监听器，并在卸载时停止动画、清理场景和释放资源。
- 四层以 `security_rank` 固定纵轴/深度轴，未分类节点进入独立未分类区域，不能伪装为四层之一。
- 不自动旋转，不添加粒子背景或无业务含义动画。

### 关键裁决证据

关键节点集合只合并后端明确引用：裁决说明引用、门控 `evidence_refs`、高级推理 `supporting_evidence_ids`/`conflicting_evidence_ids`、强制节点、冲突边端点和规则约束边端点。页面明确说明这不是完整因果路径；若没有任何明确引用则禁用筛选。

### 异常与降级

- presentation、子图、节点详情和高级推理错误均局部展示。
- 重复节点保留首个合法节点并记录适配错误；悬空边忽略并记录警告。
- 空子图显示空状态，不启动渲染器。
- 三维失败自动降级二维；二维失败仅显示图谱局部错误，文字摘要仍可用。
- 无效 turnId 留在证据页显示错误，不自动跳转。

### 测试策略

使用轻量单元测试覆盖层级映射、状态映射、图适配、重复节点、悬空边、筛选、搜索、关键证据、长标签和空图。随后运行真实 PASS、REVIEW、BLOCK、缺失、冲突和强制召回场景，验证刷新、轮次切换、节点详情、二维/三维、全屏、1366×768、浏览器控制台、路由分包与构建体积。

## 风险

- 三维依赖包体积较大，必须保持证据路由和渲染器独立懒加载。
- WebGL 能力因设备而异，二维降级必须可独立工作。
- 高级推理和整轮子图为扩展接口，不保证与冻结接口相同稳定性。
