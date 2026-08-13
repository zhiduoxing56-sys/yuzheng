import { useCallback, useState } from "react";
import { clearObstacles, patchVehicleState, resetVehicleState, setTrafficLight, spawnObstacle } from "../api/carla";
import { useVehicleState } from "../hooks/useVehicleState";
import type { VehicleStatePatch } from "../types/contract";

const OBSTACLE_OPTIONS = [
  { value: "pedestrian", label: "行人" },
  { value: "vehicle", label: "车辆" },
  { value: "obstacle", label: "障碍物" },
];

const TRAFFIC_LIGHT_OPTIONS = [
  { value: "RED", label: "红灯" },
  { value: "GREEN", label: "绿灯" },
  { value: "YELLOW", label: "黄灯" },
];

const WEATHER_OPTIONS = [
  { value: "CLEAR", label: "晴朗" },
  { value: "CLOUDY", label: "多云" },
  { value: "RAIN", label: "下雨" },
  { value: "FOG", label: "大雾" },
  { value: "NIGHT", label: "夜间" },
  { value: "SUNSET", label: "黄昏" },
];

const GEAR_OPTIONS = [
  { value: "P", label: "驻车 P" },
  { value: "D", label: "前进 D" },
  { value: "R", label: "倒车 R" },
  { value: "N", label: "空挡 N" },
];

export function CarlaPage() {
  const { data, refresh } = useVehicleState();
  const [weather, setWeather] = useState("CLEAR");
  const [gear, setGear] = useState("P");
  const [speedTarget, setSpeedTarget] = useState("40");
  const [obstacleType, setObstacleType] = useState("pedestrian");
  const [trafficLight, setTrafficLightState] = useState("RED");
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [hasError, setHasError] = useState(false);

  const apply = useCallback(async (patch: VehicleStatePatch, message: string) => {
    setBusy(true);
    setHasError(false);
    setFeedback(`${message}…`);
    try {
      const state = await patchVehicleState(patch);
      setFeedback(`${message} ✓ 当前车速 ${Math.round(state.vehicle_speed ?? 0)} km/h`);
      await refresh();
    } catch (reason) {
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "控制失败");
    } finally {
      setBusy(false);
    }
  }, [refresh]);

  const applyWeather = useCallback(() => void apply({ weather }, `设置天气(${WEATHER_OPTIONS.find((o) => o.value === weather)?.label ?? weather})`), [apply, weather]);
  const applyGear = useCallback(() => void apply({ gear_position: gear }, `设置挡位(${gear})`), [apply, gear]);
  const applySpeed = useCallback(() => {
    const value = Number(speedTarget);
    if (!Number.isFinite(value) || value < 0) {
      setHasError(true);
      setFeedback("车速必须是 ≥0 的数字");
      return;
    }
    void apply({ vehicle_speed: value }, `设置车速 ${value} km/h`);
  }, [apply, speedTarget]);
  const toggleLight = useCallback(() => {
    const next = data?.headlight_state === "ON" ? "OFF" : "ON";
    void apply({ headlight_state: next }, next === "ON" ? "打开前照灯" : "关闭前照灯");
  }, [apply, data]);
  const doReset = useCallback(async () => {
    setBusy(true);
    setHasError(false);
    setFeedback("复位车辆…");
    try {
      const state = await resetVehicleState();
      setFeedback(`车辆已复位 ✓ 当前车速 ${Math.round(state.vehicle_speed ?? 0)} km/h`);
      await refresh();
    } catch (reason) {
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "复位失败");
    } finally {
      setBusy(false);
    }
  }, [refresh]);

  const doSpawnObstacle = useCallback(async () => {
    const label = OBSTACLE_OPTIONS.find((o) => o.value === obstacleType)?.label ?? obstacleType;
    setBusy(true);
    setHasError(false);
    setFeedback(`正在生成${label}…`);
    try {
      const result = await spawnObstacle(obstacleType as "pedestrian" | "vehicle" | "obstacle");
      if (!result.ok) throw new Error("生成失败(CARLA 返回 false)");
      setFeedback(`${label}已生成 ✓ 当前障碍物 ${result.obstacle_count ?? 0} 个`);
    } catch (reason) {
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "生成失败");
    } finally {
      setBusy(false);
    }
  }, [obstacleType]);

  const doClearObstacles = useCallback(async () => {
    setBusy(true);
    setHasError(false);
    setFeedback("清除障碍物…");
    try {
      const result = await clearObstacles();
      setFeedback(`障碍物已清除 ✓(清除 ${result.cleared ?? 0} 个)`);
    } catch (reason) {
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "清除失败");
    } finally {
      setBusy(false);
    }
  }, []);

  const doSetTrafficLight = useCallback(async () => {
    const label = TRAFFIC_LIGHT_OPTIONS.find((o) => o.value === trafficLight)?.label ?? trafficLight;
    setBusy(true);
    setHasError(false);
    setFeedback(`设置交通灯为${label}…`);
    try {
      const result = await setTrafficLight(trafficLight as "RED" | "GREEN" | "YELLOW");
      if (!result.ok) throw new Error("附近无交通灯");
      setFeedback(`交通灯已设为${label} ✓`);
    } catch (reason) {
      setHasError(true);
      setFeedback(reason instanceof Error ? reason.message : "设置失败");
    } finally {
      setBusy(false);
    }
  }, [trafficLight]);

  const state = data;

  const stateItems = [
    ["车速", state?.vehicle_speed != null ? `${Math.round(state.vehicle_speed)} km/h` : "--"],
    ["挡位", state?.gear_position || "--"],
    ["天气", state?.weather || "--"],
    ["前照灯", state?.headlight_state || "--"],
    ["制动", state?.brake_state || "--"],
    ["车门", state?.door_state || "--"],
    ["车窗", state?.window_state || "--"],
    ["音乐", state?.music_state || "--"],
    ["大屏", state?.display_state || "--"],
  ];

  return <section className="visual-page-frame carla-page">
    <h1 className="visual-gradient-title">CARLA 模拟画面</h1>

    <div className="carla-layout">
      <div className="carla-left-column">
        <div className="carla-live-frame">
          <img src="/carla/stream" alt="CARLA 自动驾驶模拟器实时画面" />
        </div>

        <section className="carla-state-panel">
          <div className="carla-panel-heading">
            <h2>当前车辆状态</h2>
            <button type="button" className="carla-button carla-button-secondary" onClick={() => void refresh()}>刷新状态</button>
          </div>
          <dl className="carla-state-grid">
            {stateItems.map(([key, value]) => <div key={key} className="carla-state-item">
              <dt>{key}</dt>
              <dd>{value}</dd>
            </div>)}
          </dl>
        </section>
      </div>

      <div className="carla-controls-grid">
        <section className="carla-control-card">
          <h2>天气环境</h2>
          <div className="carla-control-row">
            <select value={weather} onChange={(event) => setWeather(event.target.value)} aria-label="天气环境">
              {WEATHER_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
            <button type="button" className="carla-button" disabled={busy} onClick={applyWeather}>应用</button>
          </div>
        </section>

        <section className="carla-control-card">
          <h2>车速控制</h2>
          <div className="carla-control-row">
            <div className="carla-speed-input">
              <input type="number" min={0} max={200} value={speedTarget} onChange={(event) => setSpeedTarget(event.target.value)} aria-label="目标车速" />
              <span>km/h</span>
            </div>
            <button type="button" className="carla-button" disabled={busy} onClick={applySpeed}>设置</button>
          </div>
          <div className="carla-control-row carla-control-row-secondary">
            <button type="button" className="carla-button carla-button-secondary" disabled={busy} onClick={() => { setSpeedTarget("30"); void apply({ vehicle_speed: 30 }, "设置车速 30 km/h"); }}>加速至 30</button>
            <button type="button" className="carla-button carla-button-secondary" disabled={busy} onClick={() => { setSpeedTarget("0"); void apply({ vehicle_speed: 0 }, "驻车制动到 0"); }}>驻车 / 制动</button>
          </div>
        </section>

        <section className="carla-control-card">
          <h2>挡位与灯光</h2>
          <div className="carla-control-row">
            <select value={gear} onChange={(event) => setGear(event.target.value)} aria-label="挡位">
              {GEAR_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
            <button type="button" className="carla-button" disabled={busy} onClick={applyGear}>应用</button>
          </div>
          <button type="button" className="carla-button carla-button-secondary carla-full-button" disabled={busy} onClick={toggleLight}>
            前照灯：{state?.headlight_state === "ON" ? "开启" : "关闭"}
          </button>
        </section>

        <section className="carla-control-card">
          <h2>障碍物</h2>
          <div className="carla-control-row">
            <select value={obstacleType} onChange={(event) => setObstacleType(event.target.value)} aria-label="障碍物类型">
              {OBSTACLE_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
            <button type="button" className="carla-button" disabled={busy} onClick={() => void doSpawnObstacle()}>生成</button>
          </div>
          <button type="button" className="carla-button carla-button-secondary carla-full-button" disabled={busy} onClick={() => void doClearObstacles()}>清除全部</button>
        </section>

        <section className="carla-control-card">
          <h2>交通灯</h2>
          <div className="carla-control-row">
            <select value={trafficLight} onChange={(event) => setTrafficLightState(event.target.value)} aria-label="交通灯状态">
              {TRAFFIC_LIGHT_OPTIONS.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
            <button type="button" className="carla-button" disabled={busy} onClick={() => void doSetTrafficLight()}>应用</button>
          </div>
        </section>

        <section className="carla-control-card carla-reset-card">
          <h2>车辆复位</h2>
          <button type="button" className="carla-button carla-full-button" disabled={busy} onClick={doReset}>复位车辆状态</button>
        </section>

        {feedback && <p role={hasError ? "alert" : "status"} className={hasError ? "carla-feedback is-error" : "carla-feedback"}>{feedback}</p>}
      </div>
    </div>
  </section>;
}
