import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  clearObstacles,
  getSimulationContext,
  patchVehicleState,
  replaceSimulationContext,
  resetVehicleState,
  setTrafficLight,
  spawnObstacle,
} from "../api/carla";
import { listScenarios, loadScenario } from "../api/scenarios";
import { useVehicleState } from "../hooks/useVehicleState";
import type { EvidenceObservationInput, ScenarioSummary, VehicleState, VehicleStatePatch } from "../types/contract";

const WEATHER_OPTIONS = [["CLEAR", "晴朗"], ["CLOUDY", "多云"], ["RAIN", "下雨"], ["FOG", "大雾"], ["NIGHT", "夜间"], ["SUNSET", "黄昏"]];
const GEAR_OPTIONS = [["P", "驻车 P"], ["D", "前进 D"], ["R", "倒车 R"], ["N", "空挡 N"]];
const OBSTACLE_OPTIONS = [["pedestrian", "行人"], ["vehicle", "车辆"], ["obstacle", "障碍物"]];
const TRAFFIC_LIGHT_OPTIONS = [["RED", "红灯"], ["GREEN", "绿灯"], ["YELLOW", "黄灯"]];

interface ContextDraft {
  timeOfDay: string; ambientIllumination: string; visibility: string; precipitation: string; fog: string;
  region: string; entityKind: string; distance: string; relativeSpeed: string; motionState: string; riskLevel: string;
  roadCondition: string; wetness: string; friction: string;
  systemMode: string; authorized: string;
}

const EMPTY_CONTEXT: ContextDraft = {
  timeOfDay: "DAY", ambientIllumination: "", visibility: "", precipitation: "NONE", fog: "NONE",
  region: "REAR_RIGHT", entityKind: "BICYCLE", distance: "", relativeSpeed: "", motionState: "APPROACHING", riskLevel: "HIGH",
  roadCondition: "DRY", wetness: "DRY", friction: "",
  systemMode: "REAL_DRIVING", authorized: "",
};

function numberOrUndefined(value: string): number | undefined {
  if (!value.trim()) return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function contextObservations(draft: ContextDraft): EvidenceObservationInput[] {
  const observations: EvidenceObservationInput[] = [];
  const environment: Record<string, unknown> = {};
  if (draft.timeOfDay) environment.time_of_day = draft.timeOfDay;
  const ambientIllumination = numberOrUndefined(draft.ambientIllumination);
  if (ambientIllumination !== undefined) environment.ambient_illumination = ambientIllumination;
  const visibility = numberOrUndefined(draft.visibility);
  if (visibility !== undefined) environment.visibility = visibility;
  if (draft.precipitation) environment.precipitation = draft.precipitation;
  if (draft.fog) environment.fog = draft.fog;
  if (Object.keys(environment).length) observations.push({ evidence_type: "ENVIRONMENT_CONDITIONS", source: "SIMULATION", value: environment });

  if (draft.entityKind) {
    const target: Record<string, unknown> = { object_id: "manual-context-target", exists: true, source_kind: "SIMULATION", ground_truth: true, entity_kind: draft.entityKind, region: draft.region, motion_state: draft.motionState, risk_level: draft.riskLevel };
    const distance = numberOrUndefined(draft.distance); const relativeSpeed = numberOrUndefined(draft.relativeSpeed);
    if (distance !== undefined) target.distance = distance;
    if (relativeSpeed !== undefined) target.relative_speed = relativeSpeed;
    observations.push({ evidence_type: "SURROUNDING_OBJECT_STATE", source: "SIMULATION", value: { objects: [target], collision_state: "NONE" } });
  }

  const road: Record<string, unknown> = { road_condition: draft.roadCondition, wetness: draft.wetness };
  const friction = numberOrUndefined(draft.friction);
  if (friction !== undefined) road.friction_scale_factor = friction;
  observations.push({ evidence_type: "ROAD_FRICTION_STATE", source: "SIMULATION", value: road });
  if (draft.systemMode) observations.push({ evidence_type: "SYSTEM_MODE", source: "SIMULATION", value: { vehicle_mode: draft.systemMode, simulation: true } });
  if (draft.authorized) observations.push({ evidence_type: "AUTHORIZATION_STATE", source: "SIMULATION", value: { authorized_for_request: draft.authorized === "YES" } });
  return observations;
}

function displayValue(value: unknown): string {
  return typeof value === "object" ? JSON.stringify(value) : String(value ?? "--");
}

function observationValue(
  observations: EvidenceObservationInput[],
  evidenceType: string,
): Record<string, unknown> | null {
  const value = observations.find((item) => item.evidence_type === evidenceType)?.value;
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null;
}

function stringValue(value: unknown, fallback = ""): string {
  return value == null ? fallback : String(value);
}

function contextDraftFromObservations(observations: EvidenceObservationInput[]): ContextDraft {
  const environment = observationValue(observations, "ENVIRONMENT_CONDITIONS");
  const surrounding = observationValue(observations, "SURROUNDING_OBJECT_STATE");
  const road = observationValue(observations, "ROAD_FRICTION_STATE");
  const system = observationValue(observations, "SYSTEM_MODE");
  const authorization = observationValue(observations, "AUTHORIZATION_STATE");
  const objects = Array.isArray(surrounding?.objects) ? surrounding.objects : [];
  const target = objects.find((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object" && !Array.isArray(item)) || null;
  const authorized = authorization?.authorized_for_request;
  return {
    timeOfDay: stringValue(environment?.time_of_day, "DAY"),
    ambientIllumination: stringValue(environment?.ambient_illumination),
    visibility: stringValue(environment?.visibility),
    precipitation: stringValue(environment?.precipitation_type ?? environment?.precipitation, "NONE"),
    fog: stringValue(environment?.fog ?? environment?.fog_visibility, "NONE"),
    region: stringValue(target?.region, "REAR_RIGHT"),
    entityKind: stringValue(target?.entity_kind),
    distance: stringValue(target?.distance),
    relativeSpeed: stringValue(target?.relative_speed),
    motionState: stringValue(target?.motion_state, "STATIONARY"),
    riskLevel: stringValue(target?.risk_level, "LOW"),
    roadCondition: stringValue(road?.road_condition, "DRY"),
    wetness: stringValue(road?.wetness, "DRY"),
    friction: stringValue(road?.friction_scale_factor ?? road?.most_probable),
    systemMode: stringValue(system?.vehicle_mode, "REAL_DRIVING"),
    authorized: authorized === true ? "YES" : authorized === false ? "NO" : "",
  };
}

function displayedWeather(state: VehicleState, observations: EvidenceObservationInput[]): string {
  const environment = observationValue(observations, "ENVIRONMENT_CONDITIONS");
  const timeOfDay = stringValue(environment?.time_of_day).toUpperCase();
  if (timeOfDay === "NIGHT") return "NIGHT";
  if (timeOfDay === "SUNSET" || timeOfDay === "DUSK") return "SUNSET";
  return stringValue(state.weather, "CLEAR");
}

export function CarlaPage() {
  const navigate = useNavigate();
  const { data: state, refresh } = useVehicleState();
  const [weather, setWeather] = useState("CLEAR"); const [gear, setGear] = useState("P"); const [speed, setSpeed] = useState("40");
  const [obstacle, setObstacle] = useState("pedestrian"); const [trafficLightValue, setTrafficLightValue] = useState("RED");
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]); const [scenarioId, setScenarioId] = useState("");
  const [context, setContext] = useState<ContextDraft>(EMPTY_CONTEXT); const [activeContext, setActiveContext] = useState<EvidenceObservationInput[]>([]);
  const [busy, setBusy] = useState(false); const [feedback, setFeedback] = useState<string | null>(null); const [error, setError] = useState(false);

  const reloadContext = useCallback(async () => {
    const observations = await getSimulationContext();
    setActiveContext(observations);
    setContext(contextDraftFromObservations(observations));
    return observations;
  }, []);
  useEffect(() => { void listScenarios().then((items) => { setScenarios(items); if (items[0]) setScenarioId(items[0].scenario_id); }); void reloadContext().catch(() => undefined); }, [reloadContext]);
  useEffect(() => { const timer = window.setInterval(() => void refresh(), 2000); return () => window.clearInterval(timer); }, [refresh]);
  useEffect(() => {
    if (!state) return;
    setWeather(displayedWeather(state, activeContext));
    setGear(stringValue(state.gear_position, "P"));
    setSpeed(stringValue(state.vehicle_speed, "0"));
  }, [state?.updated_at]);
  useEffect(() => {
    if (state) setWeather(displayedWeather(state, activeContext));
  }, [activeContext]);

  const run = useCallback(async (message: string, action: () => Promise<unknown>) => {
    setBusy(true); setError(false); setFeedback(`${message}…`);
    try { await action(); await refresh(); await reloadContext(); setFeedback(`${message} ✓`); }
    catch (reason) { setError(true); setFeedback(reason instanceof Error ? reason.message : `${message}失败`); }
    finally { setBusy(false); }
  }, [refresh, reloadContext]);
  const apply = useCallback((patch: VehicleStatePatch, label: string) => void run(label, () => patchVehicleState(patch)), [run]);
  const activateScenario = useCallback(() => void run("应用场景预设", async () => {
    const nextState = await loadScenario(scenarioId);
    const observations = await reloadContext();
    setWeather(displayedWeather(nextState, observations));
    setGear(stringValue(nextState.gear_position, "P"));
    setSpeed(stringValue(nextState.vehicle_speed, "0"));
  }), [reloadContext, run, scenarioId]);
  const updateContext = (key: keyof ContextDraft, value: string) => setContext((current) => ({ ...current, [key]: value }));

  const stateItems: Array<[string, unknown]> = [
    ["车速", state?.vehicle_speed != null ? `${Math.round(state.vehicle_speed)} km/h` : "--"], ["挡位", state?.gear_position], ["场景环境", state ? displayedWeather(state, activeContext) : "--"], ["前照灯", state?.headlight_state],
    ["制动", state?.brake_state], ["前方障碍", state?.front_obstacle_distance != null && state.front_obstacle_distance <= 150 ? `${state.front_obstacle_distance} m` : "无障碍"],
    ["后方障碍", state?.rear_obstacle_distance != null && state.rear_obstacle_distance <= 150 ? `${state.rear_obstacle_distance} m` : "无障碍"], ["碰撞状态", state?.collision_state || "NONE"],
    ["周边目标", `${state?.surrounding_objects?.length || 0} 个`], ["车门", state?.door_state], ["车窗", state?.window_state], ["系统模式", state?.vehicle_mode],
  ];

  return <section className="visual-page-frame carla-page"><header className="carla-page-header"><div><h1 className="visual-gradient-title">CARLA 模拟画面</h1></div><button className="carla-button" onClick={() => navigate("/decision")}>前往裁决页</button></header>
    <div className="carla-scenario-strip"><label><span>场景预设</span><select value={scenarioId} onChange={(event) => setScenarioId(event.target.value)}>{scenarios.map((item) => <option key={item.scenario_id} value={item.scenario_id}>{item.name || item.scenario_id}</option>)}</select></label><button className="carla-button" disabled={busy || !scenarioId} onClick={activateScenario}>应用到当前仿真状态</button></div>
    <div className="carla-layout carla-three-column-layout">
      <div className="carla-left-column"><div className="carla-live-frame"><img src="/carla/stream" alt="CARLA 自动驾驶模拟器实时画面" /></div><section className="carla-state-panel"><div className="carla-panel-heading"><h2>当前车辆与传感器状态</h2><button className="carla-button carla-button-secondary" onClick={() => void refresh()}>刷新</button></div><dl className="carla-state-grid">{stateItems.map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{displayValue(value)}</dd></div>)}</dl></section></div>

      <div className="carla-control-column"><header><span>CARLA 支持</span><h2>物理场景控制</h2></header>
        <section className="carla-control-card"><h3>天气环境</h3><div className="carla-control-row"><select value={weather} onChange={(event) => setWeather(event.target.value)}>{WEATHER_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><button disabled={busy} onClick={() => apply({ weather }, "设置天气")}>应用</button></div></section>
        <section className="carla-control-card"><h3>车速</h3><div className="carla-control-row"><input type="number" min="0" max="200" value={speed} onChange={(event) => setSpeed(event.target.value)} /><button disabled={busy} onClick={() => apply({ vehicle_speed: Number(speed) }, "设置车速")}>设置</button></div><div className="carla-control-row"><button className="carla-button-secondary" onClick={() => apply({ vehicle_speed: 30 }, "加速至30")}>加速至 30</button><button className="carla-button-secondary" onClick={() => apply({ vehicle_speed: 0 }, "驻车制动")}>驻车</button></div></section>
        <section className="carla-control-card"><h3>挡位与灯光</h3><div className="carla-control-row"><select value={gear} onChange={(event) => setGear(event.target.value)}>{GEAR_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><button onClick={() => apply({ gear_position: gear }, "设置挡位")}>应用</button></div><button className="carla-full-button carla-button-secondary" onClick={() => apply({ headlight_state: state?.headlight_state === "ON" ? "OFF" : "ON" }, "切换前照灯")}>前照灯：{state?.headlight_state === "ON" ? "开启" : "关闭"}</button></section>
        <section className="carla-control-card"><h3>障碍物</h3><div className="carla-control-row"><select value={obstacle} onChange={(event) => setObstacle(event.target.value)}>{OBSTACLE_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><button onClick={() => void run("生成障碍物", () => spawnObstacle(obstacle as "pedestrian" | "vehicle" | "obstacle"))}>生成</button></div><button className="carla-full-button carla-button-secondary" onClick={() => void run("清除障碍物", clearObstacles)}>清除全部</button></section>
        <section className="carla-control-card"><h3>交通灯</h3><div className="carla-control-row"><select value={trafficLightValue} onChange={(event) => setTrafficLightValue(event.target.value)}>{TRAFFIC_LIGHT_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><button onClick={() => void run("设置交通灯", () => setTrafficLight(trafficLightValue as "RED" | "GREEN" | "YELLOW"))}>应用</button></div></section>
        <button className="carla-button carla-full-button" disabled={busy} onClick={() => void run("复位车辆", resetVehicleState)}>复位车辆与上下文</button>
      </div>

      <div className="carla-control-column carla-context-column"><header><span>CARLA 暂不支持</span><h2>仿真补充上下文</h2></header>
        <section className="carla-control-card"><h3>环境条件</h3><label>时段<select value={context.timeOfDay} onChange={(e) => updateContext("timeOfDay", e.target.value)}><option>DAY</option><option>NIGHT</option><option>SUNSET</option></select></label><label>环境照度（lux）<input type="number" value={context.ambientIllumination} onChange={(e) => updateContext("ambientIllumination", e.target.value)} /></label><label>能见度（米）<input type="number" value={context.visibility} onChange={(e) => updateContext("visibility", e.target.value)} /></label><label>降水<select value={context.precipitation} onChange={(e) => updateContext("precipitation", e.target.value)}><option>NONE</option><option>RAIN</option><option>SNOW</option></select></label><label>雾<select value={context.fog} onChange={(e) => updateContext("fog", e.target.value)}><option>NONE</option><option>LIGHT</option><option>DENSE</option></select></label></section>
        <section className="carla-control-card"><h3>周边目标</h3><label>目标区域<select value={context.region} onChange={(e) => updateContext("region", e.target.value)}><option>FRONT</option><option>REAR</option><option>FRONT_LEFT</option><option>FRONT_RIGHT</option><option>REAR_LEFT</option><option>REAR_RIGHT</option></select></label><label>目标类型<select value={context.entityKind} onChange={(e) => updateContext("entityKind", e.target.value)}><option value="">无目标</option><option>BICYCLE</option><option>PEDESTRIAN</option><option>VEHICLE</option></select></label><div className="carla-context-pair"><label>距离（米）<input type="number" value={context.distance} onChange={(e) => updateContext("distance", e.target.value)} /></label><label>相对速度（米/秒）<input type="number" value={context.relativeSpeed} onChange={(e) => updateContext("relativeSpeed", e.target.value)} /></label></div><label>运动状态<select value={context.motionState} onChange={(e) => updateContext("motionState", e.target.value)}><option>STATIONARY</option><option>APPROACHING</option><option>RECEDING</option></select></label><label>风险等级<select value={context.riskLevel} onChange={(e) => updateContext("riskLevel", e.target.value)}><option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>CRITICAL</option></select></label></section>
        <section className="carla-control-card"><h3>道路附着</h3><label>道路状态<select value={context.roadCondition} onChange={(e) => updateContext("roadCondition", e.target.value)}><option>DRY</option><option>WET</option><option>SNOW</option><option>ICE</option></select></label><label>道路湿度<select value={context.wetness} onChange={(e) => updateContext("wetness", e.target.value)}><option>DRY</option><option>WET</option></select></label><label>摩擦系数<input type="number" min="0" max="1" step="0.1" value={context.friction} onChange={(e) => updateContext("friction", e.target.value)} /></label></section>
        <section className="carla-control-card"><h3>系统与授权</h3><label>系统模式<select value={context.systemMode} onChange={(e) => updateContext("systemMode", e.target.value)}><option>REAL_DRIVING</option><option>SIMULATION</option><option>MAINTENANCE</option></select></label><label>授权声明<select value={context.authorized} onChange={(e) => updateContext("authorized", e.target.value)}><option value="">不设置</option><option value="YES">已授权</option><option value="NO">未授权</option></select></label></section>
        <button className="carla-button carla-full-button" disabled={busy} onClick={() => void run("保存仿真补充上下文", () => replaceSimulationContext(contextObservations(context)))}>保存为当前指令上下文</button><button className="carla-button carla-button-secondary carla-full-button" disabled={busy} onClick={() => void run("清空仿真补充上下文", () => replaceSimulationContext([]))}>清空补充上下文</button>
        <section className="carla-active-context"><h3>当前已生效的补充证据</h3>{activeContext.length ? activeContext.map((item) => <div key={item.evidence_type}><strong>{item.evidence_type}</strong><code>{displayValue(item.value)}</code><small>来源：{item.source}</small></div>) : <p>当前没有仿真补充上下文。</p>}</section>
      </div>
    </div>{feedback && <p className={error ? "carla-feedback is-error" : "carla-feedback"} role={error ? "alert" : "status"}>{feedback}</p>}
  </section>;
}
