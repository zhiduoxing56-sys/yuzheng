import type { RequestRouting } from "../types/contract";

const labels: Record<string, string> = {
  VEHICLE_CONTROL: "车辆控制",
  CONTEXT: "上下文声明",
  ASSISTANT: "助手请求",
  UNCERTAIN: "待复核",
};

export function RequestRoutingDisplay({ routing }: { routing?: RequestRouting | null }) {
  if (!routing) return null;
  const onlyAssistant = !routing.contains_vehicle_control;
  return <details className={`request-routing-section${onlyAssistant ? " is-assistant" : ""}`} aria-label="理解过程">
    <summary><span>理解过程</span><small>{routing.units.length} 项，按原话顺序保留</small></summary>
    <p className="request-routing-summary">这里展示系统如何区分上下文、车辆控制、普通助手和待复核内容。</p>
    <ol className="request-routing-list">
      {routing.units.map((unit) => <li key={`${unit.unit_index}:${unit.normalized_text}`}>
        <strong>{labels[unit.kind]}</strong>
        <span>{unit.normalized_text}</span>
        <em>原始顺序 {unit.unit_index}</em>
        <small>{unit.kind === "VEHICLE_CONTROL" ? "进入本地语义核心" : unit.kind === "UNCERTAIN" ? "整轮进入语义复核" : "不生成车辆语义意图"}</small>
      </li>)}
    </ol>
  </details>;
}
