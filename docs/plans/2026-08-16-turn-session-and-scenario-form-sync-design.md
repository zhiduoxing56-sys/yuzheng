# 当前轮次会话恢复与场景表单同步设计

## 背景与目标

解决跨页返回裁决/证据检索时当前轮次丢失，以及激活模拟器预设后 CARLA 控件与仿真补充表单仍显示旧值的问题。

## 现状与约束

- 不改裁决、HNSW、EvidenceDemand 与 KnowledgeNode。
- 后端 VehicleState 和 simulation-context 仍是场景真值源。
- 不把前端表单值当作传感器回读。

## 方案对比

### 方案一：仅保留内存状态

- 优点：改动小。
- 缺点：页面重新挂载或刷新后仍丢失。

### 方案二：会话级当前轮次（采用）

- 优点：跨页和刷新均可恢复；关闭会话后自然清理。
- 缺点：需要统一 SessionProvider 的初始化和更新逻辑。

### 方案三：永久保留最后轮次

- 优点：重开浏览器也可恢复。
- 缺点：旧轮次容易被误认为当前车辆状态，不采用。

## 详细设计

### 当前轮次

- SessionProvider 从 `sessionStorage` 读取当前 `turn_id`。
- `setActiveTurn` 同时更新 React 状态和 `sessionStorage`。
- 裁决页优先使用 URL `turn_id`，其次使用会话当前轮次，并通过 presentation API 恢复展示。
- 顶部四页导航携带当前 `turn_id`；无轮次时保持简洁路径。

### 模拟器场景同步

- 应用预设后同时重新读取 `VehicleState` 与 `/api/state/simulation-context`。
- CARLA 支持区从 VehicleState 回填天气、车速、挡位等控件。
- CARLA 不支持区从正式 simulation evidence 回填能见度、降水、雾、目标、道路附着、系统和授权字段。
- 缺失字段显示空值或正式默认值，不从上一场景残留。

## 异常与边界

- 保存的 `turn_id` 在后端不存在时，页面显示读取失败，不伪造结果。
- 场景加载失败时不更新本地表单为成功状态。
- 手动更改 CARLA 物理状态后，完成回读再更新控件。

## 测试策略

- SessionProvider 会话存储单测试。
- 裁决→模拟器→裁决/证据检索跨页恢复测试。
- 夜间、雨天和右后自行车预设的控件/表单回填测试。
- TypeScript、生产构建、后端场景回归与浏览器视觉验收。
