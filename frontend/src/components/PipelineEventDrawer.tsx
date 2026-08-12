import { CollapsiblePanel } from "./CollapsiblePanel";
import type { PipelineEvent } from "../types/contract";
import { formatDateTime } from "../utils/formatters";
import { stageLabel, unknownPipelineEvents } from "../utils/pipelineStageMapper";

export function PipelineEventDrawer({ events }: { events: PipelineEvent[] }) {
  const unknownCount = unknownPipelineEvents(events).length;
  return <CollapsiblePanel title={`实时事件详情（${events.length}${unknownCount ? `，其他 ${unknownCount}` : ""}）`}>
    {!events.length ? <p className="empty-copy">本会话暂无实时事件；刷新恢复的历史过程无法通过 WebSocket 回放。</p> : <ol className="event-list">{events.map((event) => <li key={event.event_id}>
      <div><strong>#{event.sequence} {stageLabel(event.stage)}</strong><span>{event.stage} · {event.status}</span></div>
      <p>{event.summary}</p><time>{formatDateTime(event.timestamp)} · {event.duration_ms.toFixed(1)} ms</time>
      {import.meta.env.DEV && <details><summary>原始载荷</summary><pre>{JSON.stringify(event.payload, null, 2)}</pre></details>}
    </li>)}</ol>}
  </CollapsiblePanel>;
}
