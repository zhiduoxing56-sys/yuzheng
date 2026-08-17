import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { clearObstacles, getActiveScenario, getSimulationContext, patchVehicleState, replaceSimulationContext, resetVehicleState, setTrafficLight, spawnObstacle } from "../api/carla";
import { listScenarios, loadScenario } from "../api/scenarios";
import { useVehicleState } from "../hooks/useVehicleState";
import type { ActiveScenarioSummary, EvidenceObservationInput, ScenarioSummary, VehicleState, VehicleStatePatch } from "../types/contract";

const WEATHER_OPTIONS = [["CLEAR", "晴朗"], ["CLOUDY", "多云"], ["RAIN", "下雨"], ["FOG", "大雾"], ["NIGHT", "夜间"], ["SUNSET", "黄昏"]];
const GEAR_OPTIONS = [["P", "驻车 P"], ["D", "前进 D"], ["R", "倒车 R"], ["N", "空挡 N"]];
const HEADLIGHT_OPTIONS = [["OFF", "关闭"], ["ON", "开启"]];
const OBSTACLE_OPTIONS = [["NONE", "无"], ["pedestrian", "行人"], ["vehicle", "车辆"], ["obstacle", "静态障碍物"]];
const TRAFFIC_LIGHT_OPTIONS = [["RED", "红灯"], ["GREEN", "绿灯"], ["YELLOW", "黄灯"]];

interface ContextDraft {
  timeOfDay: string; ambientIllumination: string; visibility: string; precipitation: string; fog: string;
  region: string; entityKind: string; distance: string; relativeSpeed: string; motionState: string; riskLevel: string;
  roadCondition: string; wetness: string; friction: string; systemMode: string; authorized: string;
}

interface SimulatorDraft extends ContextDraft {
  weather: string; speed: string; gear: string; headlight: string; trafficLight: string; obstacleMode: string;
}

type DraftKey = keyof SimulatorDraft;
const EMPTY_CONTEXT: ContextDraft = {
  timeOfDay: "DAY", ambientIllumination: "", visibility: "", precipitation: "NONE", fog: "NONE",
  region: "REAR_RIGHT", entityKind: "", distance: "", relativeSpeed: "", motionState: "APPROACHING", riskLevel: "HIGH",
  roadCondition: "DRY", wetness: "DRY", friction: "", systemMode: "REAL_DRIVING", authorized: "",
};
const INITIAL_DRAFT: SimulatorDraft = { ...EMPTY_CONTEXT, weather: "CLEAR", speed: "0", gear: "P", headlight: "OFF", trafficLight: "RED", obstacleMode: "NONE" };
const PHYSICAL_KEYS: DraftKey[] = ["weather", "speed", "gear", "headlight"];
const CONTEXT_KEYS: Array<keyof ContextDraft> = ["timeOfDay", "ambientIllumination", "visibility", "precipitation", "fog", "region", "entityKind", "distance", "relativeSpeed", "motionState", "riskLevel", "roadCondition", "wetness", "friction", "systemMode", "authorized"];

function numberOrUndefined(value: string): number | undefined {
  if (!value.trim()) return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function contextObservations(draft: ContextDraft): EvidenceObservationInput[] {
  const observations: EvidenceObservationInput[] = [];
  const environment: Record<string, unknown> = {};
  if (draft.timeOfDay) environment.time_of_day = draft.timeOfDay;
  const ambient = numberOrUndefined(draft.ambientIllumination); if (ambient !== undefined) environment.ambient_illumination = ambient;
  const visibility = numberOrUndefined(draft.visibility); if (visibility !== undefined) environment.visibility = visibility;
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
  const friction = numberOrUndefined(draft.friction); if (friction !== undefined) road.friction_scale_factor = friction;
  observations.push({ evidence_type: "ROAD_FRICTION_STATE", source: "SIMULATION", value: road });
  if (draft.systemMode) observations.push({ evidence_type: "SYSTEM_MODE", source: "SIMULATION", value: { vehicle_mode: draft.systemMode, simulation: true } });
  if (draft.authorized) observations.push({ evidence_type: "AUTHORIZATION_STATE", source: "SIMULATION", value: { authorized_for_request: draft.authorized === "YES" } });
  return observations;
}

function observationValue(observations: EvidenceObservationInput[], evidenceType: string): Record<string, unknown> | null {
  const value = observations.find((item) => item.evidence_type === evidenceType)?.value;
  return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null;
}
function stringValue(value: unknown, fallback = ""): string { return value == null ? fallback : String(value); }

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
    timeOfDay: stringValue(environment?.time_of_day, "DAY"), ambientIllumination: stringValue(environment?.ambient_illumination), visibility: stringValue(environment?.visibility),
    precipitation: stringValue(environment?.precipitation_type ?? environment?.precipitation, "NONE"), fog: stringValue(environment?.fog ?? environment?.fog_visibility, "NONE"),
    region: stringValue(target?.region, "REAR_RIGHT"), entityKind: stringValue(target?.entity_kind), distance: stringValue(target?.distance), relativeSpeed: stringValue(target?.relative_speed),
    motionState: stringValue(target?.motion_state, "APPROACHING"), riskLevel: stringValue(target?.risk_level, "HIGH"), roadCondition: stringValue(road?.road_condition, "DRY"), wetness: stringValue(road?.wetness, "DRY"),
    friction: stringValue(road?.friction_scale_factor ?? road?.most_probable), systemMode: stringValue(system?.vehicle_mode, "REAL_DRIVING"), authorized: authorized === true ? "YES" : authorized === false ? "NO" : "",
  };
}

function obstacleModeFromState(state: VehicleState): string {
  const type = state.surrounding_objects?.[0]?.type?.toLowerCase();
  if (type?.includes("pedestrian") || type?.includes("walker")) return "pedestrian";
  if (type?.includes("vehicle")) return "vehicle";
  return type ? "obstacle" : "NONE";
}
function physicalDraftFromState(state: VehicleState) {
  return { weather: stringValue(state.weather, "CLEAR"), speed: stringValue(state.vehicle_speed, "0"), gear: stringValue(state.gear_position, "P"), headlight: stringValue(state.headlight_state, "OFF"), obstacleMode: obstacleModeFromState(state) };
}

function SelectControl({ label, value, options, disabled, onChange }: { label: string; value: string; options: string[][]; disabled: boolean; onChange: (value: string) => void }) {
  return <select aria-label={label} value={value} disabled={disabled} onChange={(event) => onChange(event.target.value)}>{options.map(([option, text]) => <option key={option} value={option}>{text}</option>)}</select>;
}
function StateRow({ label, source, dirty, error, children }: { label: string; source: string; dirty?: boolean; error?: string; children: ReactNode }) {
  return <tr className={dirty ? "is-dirty" : ""}><th scope="row">{label}</th><td>{children}{error ? <small className="carla-field-error">{error}</small> : null}</td><td><span className="carla-source-badge">{source}</span>{dirty ? <small className="carla-pending-badge">待应用</small> : null}</td></tr>;
}
function GroupRow({ children }: { children: ReactNode }) { return <tr className="carla-state-group"><th colSpan={3}>{children}</th></tr>; }

function scenarioOptionText(item: ScenarioSummary): string {
  const name = item.name || item.scenario_id;
  const conditions = item.conditions?.filter(Boolean).join(" · ");
  const instruction = item.text?.trim();
  return [
    name,
    conditions,
    instruction ? `指令：“${instruction}”` : undefined,
  ].filter(Boolean).join("｜");
}

export function CarlaPage() {
  const navigate = useNavigate(); const { data: state, refresh } = useVehicleState();
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]); const [scenarioId, setScenarioId] = useState(""); const [activeScenario, setActiveScenario] = useState<ActiveScenarioSummary | null>(null);
  const [draft, setDraft] = useState<SimulatorDraft>(INITIAL_DRAFT); const [dirtyFields, setDirtyFields] = useState<Set<DraftKey>>(() => new Set());
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<DraftKey, string>>>({}); const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null); const [error, setError] = useState(false);
  const suppressedPhysicalSignature = useRef<string | null>(null);

  const physicalSignature = useCallback((value: VehicleState) => JSON.stringify([
    value.updated_at, value.vehicle_speed, value.gear_position, value.weather, value.headlight_state,
    value.surrounding_objects?.map((item) => [item.type, item.actor_id]),
  ]), []);

  const replaceAll = useCallback((nextState: VehicleState, observations: EvidenceObservationInput[]) => {
    suppressedPhysicalSignature.current = state ? physicalSignature(state) : "";
    setDraft((current) => ({ ...current, ...physicalDraftFromState(nextState), ...contextDraftFromObservations(observations) }));
    setDirtyFields(new Set()); setFieldErrors({});
  }, [physicalSignature, state]);
  useEffect(() => {
    void listScenarios().then((items) => { setScenarios(items); if (items[0]) setScenarioId(items[0].scenario_id); });
    void getSimulationContext().then((observations) => setDraft((current) => ({ ...current, ...contextDraftFromObservations(observations) }))).catch(() => undefined);
    void getActiveScenario().then(setActiveScenario).catch(() => undefined);
  }, []);
  useEffect(() => {
    if (!state) return;
    const signature = physicalSignature(state);
    if (suppressedPhysicalSignature.current === signature) return;
    suppressedPhysicalSignature.current = null;
    const physical = physicalDraftFromState(state);
    setDraft((current) => {
      const next = { ...current };
      for (const key of [...PHYSICAL_KEYS, "obstacleMode" as DraftKey]) if (!dirtyFields.has(key)) (next[key] as string) = physical[key as keyof typeof physical];
      return next;
    });
  }, [dirtyFields, physicalSignature, state?.updated_at]);

  const edit = useCallback((key: DraftKey, value: string) => {
    setDraft((current) => ({ ...current, [key]: value })); setDirtyFields((current) => new Set(current).add(key)); setFieldErrors((current) => ({ ...current, [key]: undefined }));
  }, []);
  const runWholeTableAction = useCallback(async (label: string, action: () => Promise<VehicleState>) => {
    setBusy(true); setError(false); setFeedback(`${label}…`);
    try { const nextState = await action(); const observations = await getSimulationContext(); replaceAll(nextState, observations); setActiveScenario(await getActiveScenario()); await refresh(); setFeedback(`${label}完成`); }
    catch (reason) { setError(true); setFeedback(reason instanceof Error ? reason.message : `${label}失败`); }
    finally { setBusy(false); }
  }, [refresh, replaceAll]);
  const activateScenario = useCallback(() => { if (scenarioId) void runWholeTableAction("载入场景", () => loadScenario(scenarioId)); }, [runWholeTableAction, scenarioId]);
  const resetAll = useCallback(() => {
    if (!window.confirm("确定要重置车辆状态和全部补充上下文吗？")) return;
    void runWholeTableAction("一键重置", async () => { const nextState = await resetVehicleState(); await replaceSimulationContext([]); return nextState; });
  }, [runWholeTableAction]);

  const validationErrors = useMemo(() => {
    const next: Partial<Record<DraftKey, string>> = {}; const speed = Number(draft.speed);
    if (!Number.isFinite(speed) || speed < 0 || speed > 200) next.speed = "请输入 0–200 km/h";
    const friction = draft.friction.trim() ? Number(draft.friction) : null;
    if (friction != null && (!Number.isFinite(friction) || friction < 0 || friction > 1)) next.friction = "请输入 0–1";
    for (const key of ["ambientIllumination", "visibility", "distance"] as DraftKey[]) { const value = draft[key].trim() ? Number(draft[key]) : null; if (value != null && (!Number.isFinite(value) || value < 0)) next[key] = "请输入非负数"; }
    return next;
  }, [draft]);

  const applyAll = useCallback(async () => {
    if (!dirtyFields.size) { setFeedback("当前没有待应用的设置"); setError(false); return; }
    const activeErrors = Object.fromEntries(Object.entries(validationErrors).filter(([key]) => dirtyFields.has(key as DraftKey)));
    if (Object.keys(activeErrors).length) { setFieldErrors(activeErrors); setError(true); setFeedback("请先修正表格中的输入"); return; }
    setBusy(true); setError(false); setFeedback("正在应用全部设置…"); setFieldErrors({});
    const tasks: Array<{ label: string; keys: DraftKey[]; run: () => Promise<unknown> }> = [];
    const physicalDirty = PHYSICAL_KEYS.filter((key) => dirtyFields.has(key));
    if (physicalDirty.length) {
      const patch: VehicleStatePatch = {};
      if (dirtyFields.has("weather")) patch.weather = draft.weather; if (dirtyFields.has("speed")) patch.vehicle_speed = Number(draft.speed);
      if (dirtyFields.has("gear")) patch.gear_position = draft.gear; if (dirtyFields.has("headlight")) patch.headlight_state = draft.headlight;
      tasks.push({ label: "车辆物理状态", keys: physicalDirty, run: () => patchVehicleState(patch) });
    }
    if (dirtyFields.has("trafficLight")) tasks.push({ label: "交通灯", keys: ["trafficLight"], run: () => setTrafficLight(draft.trafficLight as "RED" | "GREEN" | "YELLOW") });
    if (dirtyFields.has("obstacleMode")) tasks.push({ label: "障碍物", keys: ["obstacleMode"], run: async () => { await clearObstacles(); if (draft.obstacleMode !== "NONE") await spawnObstacle(draft.obstacleMode as "pedestrian" | "vehicle" | "obstacle"); } });
    const contextDirty = CONTEXT_KEYS.filter((key) => dirtyFields.has(key));
    if (contextDirty.length) tasks.push({ label: "仿真补充上下文", keys: contextDirty, run: () => replaceSimulationContext(contextObservations(draft)) });
    const results = await Promise.allSettled(tasks.map((task) => task.run())); const successful = new Set<DraftKey>(); const failed: string[] = [];
    results.forEach((result, index) => { const task = tasks[index]; if (result.status === "fulfilled") task.keys.forEach((key) => successful.add(key)); else failed.push(task.label); });
    setDirtyFields((current) => new Set([...current].filter((key) => !successful.has(key))));
    if (failed.length) {
      const errors: Partial<Record<DraftKey, string>> = {}; tasks.filter((_, index) => results[index].status === "rejected").forEach((task) => task.keys.forEach((key) => { errors[key] = "应用失败"; }));
      setFieldErrors(errors); setError(true); setFeedback(`部分设置失败：${failed.join("、")}`);
    } else setFeedback("全部设置已应用");
    await refresh().catch(() => undefined);
    if (contextDirty.length && !failed.includes("仿真补充上下文")) { const observations = await getSimulationContext().catch(() => null); if (observations) setDraft((current) => ({ ...current, ...contextDraftFromObservations(observations) })); }
    setBusy(false);
  }, [dirtyFields, draft, refresh, validationErrors]);

  const select = (key: DraftKey, label: string, options: string[][]) => <SelectControl label={label} value={draft[key]} options={options} disabled={busy} onChange={(value) => edit(key, value)} />;
  const input = (key: DraftKey, label: string, props: { min?: string; max?: string; step?: string } = {}) => <input aria-label={label} type="number" value={draft[key]} disabled={busy} {...props} onChange={(event) => edit(key, event.target.value)} />;
  const row = (key: DraftKey, label: string, source: string, control: ReactNode) => <StateRow label={label} source={source} dirty={dirtyFields.has(key)} error={fieldErrors[key]}>{control}</StateRow>;

  return <section className="visual-page-frame carla-page">
    <header className="carla-page-header"><div><h1 className="visual-gradient-title">CARLA 模拟画面</h1><p>车辆真实状态与下一次指令上下文统一管理</p></div><button className="carla-button" onClick={() => navigate("/decision")}>前往裁决页</button></header>
    <div className="carla-scenario-strip"><label><span>场景预设</span><select value={scenarioId} disabled={busy} onChange={(event) => setScenarioId(event.target.value)}>{scenarios.map((item) => { const optionText = scenarioOptionText(item); return <option key={item.scenario_id} value={item.scenario_id} title={optionText}>{optionText}</option>; })}</select></label><button className="carla-button carla-button-secondary" disabled={busy || !scenarioId} onClick={activateScenario}>载入场景</button><button className="carla-button carla-button-secondary" disabled={busy} onClick={() => void refresh()}>刷新状态</button><button className="carla-button carla-button-secondary" disabled={busy} onClick={resetAll}>一键重置</button></div>
    <div className="carla-unified-layout"><div><div className="carla-live-frame"><img src="/carla/stream" alt="CARLA 自动驾驶模拟器实时画面" /></div><section className="carla-active-scenario" aria-label="当前激活场景">{activeScenario?.active ? <><strong>当前场景：{activeScenario.name}</strong><span>版本 {activeScenario.version} · 覆盖证据 {activeScenario.evidence_count} 条</span><small>{activeScenario.evidence_types.join("、")}</small></> : <span>当前未激活场景</span>}</section></div><section className="carla-unified-state-panel"><div className="carla-panel-heading"><div><h2>车辆与场景状态</h2><p>修改后的字段会标记为待应用；补充上下文用于下一次新指令。</p></div></div>
      <div className="carla-unified-table-wrap"><table className="carla-unified-table"><thead><tr><th>状态</th><th>当前值 / 待应用值</th><th>数据来源</th></tr></thead><tbody>
        <GroupRow>车辆控制</GroupRow>
        {row("speed", "车速（km/h）", "CARLA 控制", input("speed", "车速（km/h）", { min: "0", max: "200" }))}
        {row("gear", "挡位", "CARLA 控制", select("gear", "挡位", GEAR_OPTIONS))}{row("weather", "天气", "CARLA 控制", select("weather", "天气", WEATHER_OPTIONS))}
        {row("headlight", "前照灯", "CARLA 控制", select("headlight", "前照灯", HEADLIGHT_OPTIONS))}{row("trafficLight", "交通灯", "CARLA 控制", select("trafficLight", "交通灯", TRAFFIC_LIGHT_OPTIONS))}
        {row("obstacleMode", "场景障碍物", "CARLA 控制", select("obstacleMode", "场景障碍物", OBSTACLE_OPTIONS))}
        <GroupRow>实时传感器</GroupRow>
        <StateRow label="制动状态" source="CARLA 回传"><output>{stringValue(state?.brake_state, "--")}</output></StateRow><StateRow label="前方障碍距离" source="CARLA 回传"><output>{state?.front_obstacle_distance == null || state.front_obstacle_distance > 150 ? "无障碍" : `${state.front_obstacle_distance} m`}</output></StateRow>
        <StateRow label="后方障碍距离" source="CARLA 回传"><output>{state?.rear_obstacle_distance == null || state.rear_obstacle_distance > 150 ? "无障碍" : `${state.rear_obstacle_distance} m`}</output></StateRow><StateRow label="碰撞状态" source="CARLA 回传"><output>{stringValue(state?.collision_state, "NONE")}</output></StateRow>
        <StateRow label="周边目标数量" source="CARLA 回传"><output>{state?.surrounding_objects?.length || 0} 个</output></StateRow><StateRow label="车门状态" source="CARLA 回传"><output>{stringValue(state?.door_state, "--")}</output></StateRow><StateRow label="车窗状态" source="CARLA 回传"><output>{stringValue(state?.window_state, "--")}</output></StateRow><StateRow label="车辆模式" source="CARLA 回传"><output>{stringValue(state?.vehicle_mode, "--")}</output></StateRow>
        <GroupRow>环境上下文</GroupRow>
        {row("timeOfDay", "时段", "仿真上下文", select("timeOfDay", "时段", [["DAY", "白天"], ["NIGHT", "夜间"], ["SUNSET", "黄昏"]]))}{row("ambientIllumination", "环境照度（lux）", "仿真上下文", input("ambientIllumination", "环境照度（lux）", { min: "0" }))}
        {row("visibility", "能见度（米）", "仿真上下文", input("visibility", "能见度（米）", { min: "0" }))}{row("precipitation", "降水", "仿真上下文", select("precipitation", "降水", [["NONE", "无"], ["RAIN", "雨"], ["SNOW", "雪"]]))}{row("fog", "雾", "仿真上下文", select("fog", "雾", [["NONE", "无"], ["LIGHT", "轻雾"], ["DENSE", "浓雾"]]))}
        <GroupRow>周边目标上下文</GroupRow>
        {row("region", "目标区域", "仿真上下文", select("region", "目标区域", [["FRONT", "前方"], ["REAR", "后方"], ["FRONT_LEFT", "左前"], ["FRONT_RIGHT", "右前"], ["REAR_LEFT", "左后"], ["REAR_RIGHT", "右后"]]))}{row("entityKind", "目标类型", "仿真上下文", select("entityKind", "目标类型", [["", "无目标"], ["BICYCLE", "自行车"], ["PEDESTRIAN", "行人"], ["VEHICLE", "车辆"]]))}
        {row("distance", "目标距离（米）", "仿真上下文", input("distance", "目标距离（米）", { min: "0" }))}{row("relativeSpeed", "相对速度（米/秒）", "仿真上下文", input("relativeSpeed", "相对速度（米/秒）"))}{row("motionState", "运动状态", "仿真上下文", select("motionState", "运动状态", [["STATIONARY", "静止"], ["APPROACHING", "接近"], ["RECEDING", "远离"]]))}{row("riskLevel", "风险等级", "仿真上下文", select("riskLevel", "风险等级", [["LOW", "低"], ["MEDIUM", "中"], ["HIGH", "高"], ["CRITICAL", "严重"]]))}
        <GroupRow>道路、系统与授权</GroupRow>
        {row("roadCondition", "道路状态", "仿真上下文", select("roadCondition", "道路状态", [["DRY", "干燥"], ["WET", "湿滑"], ["SNOW", "积雪"], ["ICE", "结冰"]]))}{row("wetness", "道路湿度", "仿真上下文", select("wetness", "道路湿度", [["DRY", "干燥"], ["WET", "潮湿"]]))}{row("friction", "摩擦系数", "仿真上下文", input("friction", "摩擦系数", { min: "0", max: "1", step: "0.1" }))}
        {row("systemMode", "系统模式声明", "仿真上下文", select("systemMode", "系统模式声明", [["REAL_DRIVING", "真实驾驶"], ["SIMULATION", "模拟"], ["MAINTENANCE", "维护"]]))}{row("authorized", "授权声明", "仿真上下文", select("authorized", "授权声明", [["", "不设置"], ["YES", "已授权"], ["NO", "未授权"]]))}
      </tbody></table></div><div className="carla-unified-actions"><button className="carla-button" disabled={busy} onClick={() => void applyAll()}>{busy ? "正在处理…" : "应用全部设置"}</button><span>{dirtyFields.size ? `还有 ${dirtyFields.size} 项待应用` : "所有设置均已同步"}</span></div>
    </section></div>{feedback && <p className={error ? "carla-feedback is-error" : "carla-feedback"} role={error ? "alert" : "status"}>{feedback}</p>}
  </section>;
}
