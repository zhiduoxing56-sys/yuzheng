import type { TimelineResponse } from "../types/contract";
import { formatDateTime } from "../utils/formatters";

const eventLabels: Record<string, string> = {
  AUDIT_SAVED: "裁决审计已保存",
  REVIEW_REQUESTED: "进入人工复核",
  REVIEW_CONFIRM_REJECTED: "候选确认被拒绝",
  REVIEW_CONFIRMED: "已确认候选",
  REVIEW_CORRECTED: "已提交文本修正",
  REVIEW_CANCELLED: "已取消操作",
  FINAL_DECISION_UPDATED: "最终裁决已更新",
  AUDIT_OUTCOME_APPENDED: "终态审计已追加",
  REDECISION_STARTED: "重新裁决开始",
  REDECISION_COMPLETED: "重新裁决完成",
  TOKEN_ISSUED: "授权令牌已签发",
  TOKEN_REJECTED: "授权令牌被拒绝",
  TOKEN_EXPIRED: "授权令牌已过期",
  TOKEN_CONSUMED: "授权令牌已消费",
  TOKEN_REVOKED: "授权令牌已撤销",
  EXECUTION_REQUESTED: "已请求车辆执行",
  PRE_EXECUTION_CHECK_PASSED: "执行前复查通过",
  PRE_EXECUTION_CHECK_FAILED: "执行前复查失败",
  EXECUTION_SUCCEEDED: "车辆执行成功",
  EXECUTION_FAILED: "车辆执行失败",
};

interface Props { data: TimelineResponse | null; loading: boolean; error: string | null; onRefresh: () => void; }

export function ReviewTimelinePanel({ data, loading, error, onRefresh }: Props) {
  const events = [...(data?.items || [])].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  return <section className="review-timeline-section">
    <div className="card-heading"><div><span className="eyebrow">PERSISTED TIMELINE</span><h2>复核、授权与执行时间线</h2></div><button type="button" className="secondary-button compact" disabled={loading} onClick={onRefresh}>刷新状态</button></div>
    {loading && !data && <p className="loading-copy">正在加载轻量时间线……</p>}
    {error && <p className="inline-error" role="alert">{error}</p>}
    {!loading && !events.length ? <p className="empty-copy">当前工作流没有持久化事件。</p> : <ol className="timeline-list review-timeline-list">{events.map((event) => <li key={`${event.sequence}-${event.event_id || event.stage}`}><span className="timeline-marker" /><div><strong>{eventLabels[event.stage] || event.stage}</strong><span>序号 {event.sequence}</span><p>{typeof event.summary === "string" ? event.summary : JSON.stringify(event.summary)}</p><time>{formatDateTime(event.timestamp)}</time></div></li>)}</ol>}
  </section>;
}
