import type { DecisionLabel } from "../types/contract";
import { AUDIT_PAGE_SIZE_OPTIONS, fromDateTimeLocal, toDateTimeLocal, type AuditQueryState } from "../utils/auditQueryParams";

interface Props {
  query: AuditQueryState;
  issues: string[];
  validTimeRange: boolean;
  onDecision: (value?: DecisionLabel) => void;
  onTimeRange: (start?: string, end?: string) => void;
  onPageSize: (value: number) => void;
  onReset: () => void;
}

export function AuditFilterBar({ query, issues, validTimeRange, onDecision, onTimeRange, onPageSize, onReset }: Props) {
  return <section className="audit-filter-bar" aria-label="审计筛选">
    <label><span>最终裁决</span><select value={query.decision || ""} onChange={(event) => onDecision(event.target.value as DecisionLabel || undefined)}><option value="">全部</option><option value="PASS">允许执行</option><option value="REVIEW">需要复核</option><option value="BLOCK">安全阻断</option></select></label>
    <label><span>开始时间</span><input type="datetime-local" value={toDateTimeLocal(query.start_time)} onChange={(event) => onTimeRange(fromDateTimeLocal(event.target.value), query.end_time)} /></label>
    <label><span>结束时间</span><input type="datetime-local" value={toDateTimeLocal(query.end_time)} onChange={(event) => onTimeRange(query.start_time, fromDateTimeLocal(event.target.value))} /></label>
    <label><span>每页数量</span><select value={query.page_size} onChange={(event) => onPageSize(Number(event.target.value))}>{AUDIT_PAGE_SIZE_OPTIONS.map((value) => <option value={value} key={value}>{value} 条</option>)}</select></label>
    <button className="secondary-button" type="button" onClick={onReset}>重置筛选</button>
    {issues.length > 0 && <div className={validTimeRange ? "audit-query-note" : "audit-query-error"}>{issues.join("；")}{!validTimeRange && "。修正时间范围前不会发送列表请求。"}</div>}
  </section>;
}
