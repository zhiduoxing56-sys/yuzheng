import type { TimelineResponse } from "../types/contract";
import { formatDateTime } from "../utils/formatters";
import { stageLabel } from "../utils/pipelineStageMapper";

interface Props { data: TimelineResponse | null; loading: boolean; error: string | null; onRefresh: () => void; }

export function TimelinePanel({ data, loading, error, onRefresh }: Props) {
  const items = [...(data?.items || [])].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  return <section className="detail-section"><div className="card-heading"><div><span className="eyebrow">TIMELINE</span><h2>持久化时间线</h2></div><button className="secondary-button compact" onClick={onRefresh} disabled={loading}>刷新</button></div>
    {loading && !data && <p className="loading-copy">正在加载时间线……</p>}{error && <p className="inline-error">{error}</p>}
    {!loading && !items.length ? <p className="empty-copy">当前轮次没有持久化时间线。</p> : <ol className="timeline-list">{items.map((item) => <li key={`${item.sequence}-${item.event_id || item.audit_id || item.stage}`}><span className="timeline-marker" /><div><strong>{stageLabel(item.stage)}</strong><span>{item.status}</span><p>{typeof item.summary === "string" ? item.summary : JSON.stringify(item.summary)}</p><time>{formatDateTime(item.timestamp)}</time>{import.meta.env.DEV && <details><summary>原始记录</summary><pre>{JSON.stringify(item, null, 2)}</pre></details>}</div></li>)}</ol>}
  </section>;
}
