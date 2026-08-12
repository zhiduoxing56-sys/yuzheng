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

const panelStyle: React.CSSProperties = {
  background: "#0f1420",
  border: "1px solid #232b3b",
  borderRadius: 12,
  padding: "1rem 1.25rem",
  marginBottom: "1rem",
};

const labelStyle: React.CSSProperties = {
  fontSize: "0.8rem",
  color: "#8a94a6",
  display: "block",
  marginBottom: "0.35rem",
};

const controlStyle: React.CSSProperties = {
  display: "flex",
  gap: "0.5rem",
  alignItems: "center",
  flexWrap: "wrap",
};

const buttonStyle: React.CSSProperties = {
  background: "#1b7cff",
  color: "#fff",
  border: "none",
  borderRadius: 8,
  padding: "0.45rem 0.9rem",
  cursor: "pointer",
  fontWeight: 600,
};

const buttonDisabled: React.CSSProperties = { ...buttonStyle, opacity: 0.5, cursor: "not-allowed" };

const selectStyle: React.CSSProperties = {
  background: "#1a2230",
  color: "#e6ecf5",
  border: "1px solid #2c3850",
  borderRadius: 8,
  padding: "0.45rem 0.6rem",
};

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

  return <section className="carla-page" style={{ padding: "1.5rem", maxWidth: 1400, margin: "0 auto" }}>
    <h1 className="visual-gradient-title" style={{ fontSize: "1.5rem", marginBottom: "0.25rem" }}>CARLA 自动驾驶模拟器 · 实时画面与车辆控制</h1>
    <p style={{ color: "#8a94a6", marginTop: 0, marginBottom: "1rem" }}>画面由云服务器 CARLA 实时推流；右侧控制面板直接驱动车辆状态（天气 / 车速 / 灯光 / 挡位）。</p>

    <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
      {/* 左：动画 */}
      <div style={{ flex: "1 1 620px", minWidth: 360 }}>
        <div className="carla-live-frame" style={{
          background: "#000", borderRadius: 12, overflow: "hidden",
          aspectRatio: "16 / 9", display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 8px 30px rgba(0,0,0,0.35)",
        }}>
          <img src="/carla/stream" alt="CARLA 自动驾驶模拟器实时画面"
            style={{ width: "100%", height: "100%", objectFit: "contain" }} />
        </div>
        <p className="carla-hint" style={{ color: "#5c6675", fontSize: "0.85rem", marginTop: "0.75rem" }}>
          分辨率 640×360 · 约 10 帧/秒 · 云服务器 CARLA 引擎实时推流
        </p>
      </div>

      {/* 右：控制面板 + 状态 */}
      <div style={{ flex: "0 1 360px", minWidth: 300 }}>
        {/* 天气 */}
        <div style={panelStyle}>
          <label style={labelStyle}>天气环境</label>
          <div style={controlStyle}>
            <select value={weather} onChange={(e) => setWeather(e.target.value)} style={selectStyle}>
              {WEATHER_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <button type="button" style={busy ? buttonDisabled : buttonStyle} disabled={busy} onClick={applyWeather}>应用</button>
          </div>
        </div>

        {/* 车速 */}
        <div style={panelStyle}>
          <label style={labelStyle}>车速控制（km/h）</label>
          <div style={controlStyle}>
            <input type="number" min={0} max={200} value={speedTarget}
              onChange={(e) => setSpeedTarget(e.target.value)}
              style={{ ...selectStyle, width: 90 }} aria-label="目标车速" />
            <button type="button" style={busy ? buttonDisabled : buttonStyle} disabled={busy} onClick={applySpeed}>设置车速</button>
          </div>
          <div style={{ ...controlStyle, marginTop: "0.5rem" }}>
            <button type="button" style={busy ? buttonDisabled : buttonStyle} disabled={busy} onClick={() => { setSpeedTarget("30"); void apply({ vehicle_speed: 30 }, "设置车速 30 km/h"); }}>加速(30)</button>
            <button type="button" style={busy ? buttonDisabled : buttonStyle} disabled={busy} onClick={() => { setSpeedTarget("0"); void apply({ vehicle_speed: 0 }, "驻车制动到 0"); }}>驻车/制动(0)</button>
          </div>
          <p style={{ color: "#5c6675", fontSize: "0.75rem", margin: "0.5rem 0 0" }}>
            提示：执行「裁决页」的指令前，先点「驻车/制动(0)」让状态稳定，执行结果才会真正反映到 CARLA 车辆上。
          </p>
        </div>

        {/* 挡位 / 灯光 */}
        <div style={panelStyle}>
          <label style={labelStyle}>挡位</label>
          <div style={controlStyle}>
            <select value={gear} onChange={(e) => setGear(e.target.value)} style={selectStyle}>
              {GEAR_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <button type="button" style={busy ? buttonDisabled : buttonStyle} disabled={busy} onClick={applyGear}>应用</button>
            <button type="button" style={busy ? buttonDisabled : buttonStyle} disabled={busy} onClick={toggleLight}>
              前照灯{state?.headlight_state === "ON" ? " 开" : " 关"}
            </button>
          </div>
        </div>

        {/* 障碍物生成 */}
        <div style={panelStyle}>
          <label style={labelStyle}>生成障碍物（在自车前方）</label>
          <div style={controlStyle}>
            <select value={obstacleType} onChange={(e) => setObstacleType(e.target.value)} style={selectStyle}>
              {OBSTACLE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <button type="button" style={busy ? buttonDisabled : buttonStyle} disabled={busy} onClick={() => void doSpawnObstacle()}>生成</button>
            <button type="button" style={busy ? buttonDisabled : { ...buttonStyle, background: "#2c3850" }} disabled={busy} onClick={() => void doClearObstacles()}>清除全部</button>
          </div>
        </div>

        {/* 交通灯 */}
        <div style={panelStyle}>
          <label style={labelStyle}>交通灯控制（全部）</label>
          <div style={controlStyle}>
            <select value={trafficLight} onChange={(e) => setTrafficLightState(e.target.value)} style={selectStyle}>
              {TRAFFIC_LIGHT_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <button type="button" style={busy ? buttonDisabled : buttonStyle} disabled={busy} onClick={() => void doSetTrafficLight()}>应用</button>
          </div>
        </div>

        {/* 复位 */}
        <div style={panelStyle}>
          <button type="button" style={busy ? buttonDisabled : buttonStyle} disabled={busy} onClick={doReset}>复位车辆状态</button>
        </div>

        {/* 反馈 */}
        {feedback && <p role={hasError ? "alert" : "status"} style={{
          padding: "0.6rem 0.8rem", borderRadius: 8, fontSize: "0.85rem",
          background: hasError ? "rgba(220,60,60,0.15)" : "rgba(27,124,255,0.12)",
          color: hasError ? "#ff8b8b" : "#7cc4ff",
          marginTop: "0.5rem",
        }}>{feedback}</p>}

        {/* 当前状态 */}
        <div style={panelStyle}>
          <label style={{ ...labelStyle, fontSize: "0.9rem" }}>当前车辆状态（CARLA 实时）</label>
          <dl style={{ margin: 0, display: "grid", gridTemplateColumns: "auto 1fr", gap: "0.35rem 0.8rem", fontSize: "0.85rem" }}>
            {[
              ["车速", state?.vehicle_speed != null ? `${Math.round(state.vehicle_speed)} km/h` : "--"],
              ["挡位", state?.gear_position || "--"],
              ["天气", state?.weather || "--"],
              ["前照灯", state?.headlight_state || "--"],
              ["制动", state?.brake_state || "--"],
              ["车门", state?.door_state || "--"],
              ["车窗", state?.window_state || "--"],
              ["音乐", state?.music_state || "--"],
              ["大屏", state?.display_state || "--"],
            ].map(([k, v]) => (
              <div key={k} style={{ display: "contents" }}>
                <dt style={{ color: "#8a94a6" }}>{k}</dt>
                <dd style={{ margin: 0, color: "#e6ecf5", textAlign: "right" }}>{v}</dd>
              </div>
            ))}
          </dl>
          <button type="button" onClick={() => void refresh()} style={{ ...buttonStyle, marginTop: "0.6rem", background: "#2c3850" }}>刷新状态</button>
        </div>
      </div>
    </div>
  </section>;
}
