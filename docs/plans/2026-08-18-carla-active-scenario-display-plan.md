# CARLA 当前场景大字号展示实施计划

## 目标

在 CARLA 实时画面下方，以大字号展示成功载入的场景名称和该预设实际配置的非空条件。

## 实施步骤

1. 收紧后端场景摘要空值规则
   - 修改 `backend/app/services/vehicle/scenario_summary.py`。
   - 增加统一的有效展示值判断。
   - 状态、环境、道路、周边目标、系统和通用证据摘要均跳过空值。
   - 复合条件没有任何有效子字段时不返回空标题。

2. 扩充后端单元测试
   - 修改 `backend/tests/unit/test_scenario_summary.py`。
   - 覆盖 `None`、空字符串、空数组、空对象以及复合对象部分为空的情况。
   - 保留 `0` 和 `False` 等有业务意义的值。

3. 计算前端当前已载入场景
   - 修改 `frontend/src/pages/CarlaPage.tsx`。
   - 使用 `activeScenario.scenario_id` 从 `scenarios` 中匹配场景摘要。
   - 不使用下拉框当前选择值决定展示内容。
   - 对条件数组执行防御性非空过滤。

4. 重构画面下方展示区
   - 保留“当前场景”语义区域和无障碍标签。
   - 展示大字号场景名称和条件标签。
   - 移除版本、证据数量和证据类型文案。
   - 未激活时展示“当前未载入场景”。

5. 增加响应式视觉样式
   - 修改 `frontend/src/styles/visual-pages.css`。
   - 为当前场景容器、标题和条件标签增加蓝白体系样式。
   - 桌面端使用醒目字号，移动端降低字号并自动换行。

6. 扩充前端组件测试
   - 修改 `frontend/src/test/carlaScenarioContext.test.tsx`。
   - 补齐 `getActiveScenario` mock。
   - 验证载入成功、非空字段显示、空字段隐藏、未提交选择不生效及重置后的状态。

7. 验证与范围检查
   - 使用项目指定 Python 环境运行场景摘要测试。
   - 运行 CARLA 页面相关前端测试、TypeScript 检查和生产构建。
   - 检查 Git diff，确保没有覆盖工作区内的无关改动。

## 预计修改文件

- `backend/app/services/vehicle/scenario_summary.py`
- `backend/tests/unit/test_scenario_summary.py`
- `frontend/src/pages/CarlaPage.tsx`
- `frontend/src/styles/visual-pages.css`
- `frontend/src/test/carlaScenarioContext.test.tsx`

## 验收示例

载入“右后自行车接近”后，实时画面下方显示：

- 当前场景：右后自行车接近
- 车速：42 km/h
- 挡位：D（前进）
- 周边目标：右后方自行车距离 3 m、接近、高风险

该预设未填写的字段不占位、不显示“未提供”，也不从右侧表格默认值中补齐。
