// @vitest-environment jsdom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { getActiveScenario, getSimulationContext, patchVehicleState, replaceSimulationContext } from "../api/carla";
import { loadScenario } from "../api/scenarios";
import { CarlaPage } from "../pages/CarlaPage";

vi.mock("../hooks/useVehicleState", () => ({ useVehicleState: () => ({ data: { vehicle_speed: 0, gear_position: "P", weather: "CLEAR", headlight_state: "OFF", surrounding_objects: [] }, refresh: vi.fn().mockResolvedValue(undefined) }) }));
vi.mock("../api/carla", () => ({
  patchVehicleState: vi.fn().mockResolvedValue({}), resetVehicleState: vi.fn().mockResolvedValue({}), spawnObstacle: vi.fn().mockResolvedValue({ ok: true }), clearObstacles: vi.fn().mockResolvedValue({ ok: true }), setTrafficLight: vi.fn().mockResolvedValue({ ok: true }),
  getActiveScenario: vi.fn().mockResolvedValue({ active: false, scenario_id: null, name: null, version: 0, activated_at: null, evidence_count: 0, evidence_types: [] }),
  getSimulationContext: vi.fn().mockResolvedValue([]), replaceSimulationContext: vi.fn().mockResolvedValue([]),
}));
vi.mock("../api/scenarios", () => ({ listScenarios: vi.fn().mockResolvedValue([{
  scenario_id: "risk",
  name: "右后自行车接近",
  text: "打开右后车门",
  conditions: ["车速：42 km/h", "挡位：D（前进）", "天气：晴朗", "周边目标：右后方自行车距离3 m接近高风险"],
}]), loadScenario: vi.fn().mockResolvedValue({}) }));

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(getSimulationContext).mockResolvedValue([]);
  vi.mocked(getActiveScenario).mockResolvedValue({ active: false, scenario_id: null, name: null, version: 0, activated_at: null, evidence_count: 0, evidence_types: [] });
  vi.mocked(loadScenario).mockResolvedValue({} as Awaited<ReturnType<typeof loadScenario>>);
});
afterEach(cleanup);

describe("CARLA 场景与补充上下文", () => {
  it("把车辆状态和上下文合并到一张表且只有一个应用按钮", async () => {
    render(<MemoryRouter><CarlaPage /></MemoryRouter>);
    expect(screen.getByRole("heading", { name: "车辆与场景状态" })).toBeTruthy();
    expect(screen.getByRole("table")).toBeTruthy();
    expect(screen.queryByRole("heading", { name: "物理场景控制" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "仿真补充上下文" })).toBeNull();
    expect(screen.getAllByRole("button", { name: "应用全部设置" })).toHaveLength(1);
    expect(await screen.findByRole("option", { name: "右后自行车接近｜车速：42 km/h · 挡位：D（前进） · 天气：晴朗 · 周边目标：右后方自行车距离3 m接近高风险｜指令：“打开右后车门”" })).toBeTruthy();
  });

  it("场景预设通过正式 load 接口激活", async () => {
    const user = userEvent.setup(); render(<MemoryRouter><CarlaPage /></MemoryRouter>);
    await screen.findByRole("option", { name: /右后自行车接近.*车速：42 km\/h.*指令：“打开右后车门”/ });
    await user.click(screen.getByRole("button", { name: "载入场景" }));
    await waitFor(() => expect(loadScenario).toHaveBeenCalledWith("risk"));
  });

  it("载入成功后只展示大字号场景名和非空条件", async () => {
    vi.mocked(getActiveScenario)
      .mockResolvedValueOnce({ active: false, scenario_id: null, name: null, version: 0, activated_at: null, evidence_count: 0, evidence_types: [] })
      .mockResolvedValue({ active: true, scenario_id: "risk", name: "右后自行车接近", version: 2, activated_at: "2026-08-18T12:00:00Z", evidence_count: 3, evidence_types: ["VEHICLE_SPEED"] });
    const user = userEvent.setup();
    render(<MemoryRouter><CarlaPage /></MemoryRouter>);
    await screen.findByRole("option", { name: /右后自行车接近/ });
    await user.click(screen.getByRole("button", { name: "载入场景" }));

    const display = await screen.findByLabelText("当前激活场景");
    await waitFor(() => expect(display.textContent).toContain("当前场景：右后自行车接近"));
    expect(display.textContent).toContain("车速：42 km/h");
    expect(display.textContent).toContain("周边目标：右后方自行车距离3 m接近高风险");
    expect(display.textContent).not.toContain("版本");
    expect(display.textContent).not.toContain("覆盖证据");
    expect(display.querySelector("small")).toBeNull();
  });

  it("场景激活后回填 CARLA 控件和仿真补充表单", async () => {
    vi.mocked(loadScenario).mockResolvedValue({
      vehicle_speed: 42,
      gear_position: "D",
      weather: "CLEAR",
      updated_at: "2026-08-16T12:00:00Z",
    } as Awaited<ReturnType<typeof loadScenario>>);
    vi.mocked(getSimulationContext)
      .mockResolvedValueOnce([])
      .mockResolvedValue([
        { evidence_type: "ENVIRONMENT_CONDITIONS", source: "SIMULATION", value: { time_of_day: "NIGHT", ambient_illumination: 5, visibility: 60, precipitation: "NONE", fog: "NONE" } },
        { evidence_type: "SURROUNDING_OBJECT_STATE", source: "SIMULATION", value: { objects: [{ region: "REAR_RIGHT", entity_kind: "BICYCLE", distance: 3, relative_speed: -5, motion_state: "APPROACHING", risk_level: "HIGH" }] } },
        { evidence_type: "ROAD_FRICTION_STATE", source: "SIMULATION", value: { road_condition: "WET", wetness: "WET", friction_scale_factor: 0.4 } },
      ]);

    const user = userEvent.setup();
    render(<MemoryRouter><CarlaPage /></MemoryRouter>);
    await screen.findByRole("option", { name: /右后自行车接近.*车速：42 km\/h.*指令：“打开右后车门”/ });
    await user.click(screen.getByRole("button", { name: "载入场景" }));

    expect(await screen.findByDisplayValue("夜间")).toBeTruthy();
    expect((screen.getByLabelText("挡位") as HTMLSelectElement).value).toBe("D");
    expect((screen.getByLabelText("车速（km/h）") as HTMLInputElement).value).toBe("42");
    expect((screen.getByLabelText("能见度（米）") as HTMLInputElement).value).toBe("60");
    expect((screen.getByLabelText("时段") as HTMLSelectElement).value).toBe("NIGHT");
    expect((screen.getByLabelText("环境照度（lux）") as HTMLInputElement).value).toBe("5");
    expect((screen.getByLabelText("目标类型") as HTMLSelectElement).value).toBe("BICYCLE");
    expect((screen.getByLabelText("摩擦系数") as HTMLInputElement).value).toBe("0.4");
  });

  it("将 CARLA 不支持字段保存为 SIMULATION Evidence", async () => {
    const user = userEvent.setup(); render(<MemoryRouter><CarlaPage /></MemoryRouter>);
    await user.selectOptions(screen.getByLabelText("目标类型"), "BICYCLE");
    await user.type(screen.getByLabelText("目标距离（米）"), "3");
    await user.type(screen.getByLabelText("相对速度（米/秒）"), "-5");
    await user.click(screen.getByRole("button", { name: "应用全部设置" }));
    await waitFor(() => expect(replaceSimulationContext).toHaveBeenCalled());
    const observations = vi.mocked(replaceSimulationContext).mock.calls[0][0];
    const surrounding = observations.find((item) => item.evidence_type === "SURROUNDING_OBJECT_STATE");
    expect(surrounding?.source).toBe("SIMULATION");
    expect(surrounding?.value).toMatchObject({ objects: [{ region: "REAR_RIGHT", entity_kind: "BICYCLE", distance: 3, relative_speed: -5 }] });
  });

  it("一次应用同时提交 CARLA 物理字段和补充上下文", async () => {
    const user = userEvent.setup(); render(<MemoryRouter><CarlaPage /></MemoryRouter>);
    await user.clear(screen.getByLabelText("车速（km/h）"));
    await user.type(screen.getByLabelText("车速（km/h）"), "36");
    await user.selectOptions(screen.getByLabelText("目标类型"), "PEDESTRIAN");
    await user.click(screen.getByRole("button", { name: "应用全部设置" }));
    await waitFor(() => expect(patchVehicleState).toHaveBeenCalledWith({ vehicle_speed: 36 }));
    expect(replaceSimulationContext).toHaveBeenCalled();
  });
});
