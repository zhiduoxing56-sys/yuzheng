import type { WorkflowChainVerification } from "../types/contract";
import { formatDateTime } from "../utils/formatters";
import { StatusBadge } from "./StatusBadge";

interface Props {
  data: WorkflowChainVerification | null;
  loading: boolean;
  error: string | null;
  verifiedAt: Date | null;
  onRefresh: () => void;
}

export function WorkflowChainPanel({ data, loading, error, verifiedAt, onRefresh }: Props) {
  return <section className={`review-card workflow-chain-card ${data && !data.valid ? "chain-invalid" : ""}`}>
    <div className="card-heading"><div><span className="eyebrow">WORKFLOW CHAIN</span><h2>工作流链完整性</h2></div><StatusBadge tone={data?.valid ? "success" : data ? "danger" : "neutral"} label={data ? data.valid ? "校验通过" : "校验异常" : "尚未校验"} /></div>
    {loading && !data && <p className="loading-copy">正在校验工作流链……</p>}
    {error && <p className="inline-error" role="alert">{error}</p>}
    {data && <dl className="review-fact-grid compact-grid">
      <div><dt>根轮次</dt><dd title={data.root_turn_id}>{data.root_turn_id}</dd></div>
      <div><dt>事件数量</dt><dd>{data.event_count}</dd></div>
      <div><dt>链接关系</dt><dd>{data.valid ? "后端校验有效" : "后端校验失败"}</dd></div>
      <div><dt>失败事件</dt><dd>{data.failure_event_id || "无"}</dd></div>
      <div><dt>校验时间</dt><dd>{formatDateTime(verifiedAt?.toISOString())}</dd></div>
    </dl>}
    {data && !data.valid && <p className="danger-notice">工作流链校验异常。后端未把该字段定义为执行门，因此页面只显示警告，不擅自改写业务资格。</p>}
    <button type="button" className="secondary-button full-width" disabled={loading} onClick={onRefresh}>重新校验全部状态</button>
    {data && <details className="technical-details"><summary>后端校验详情</summary><pre>{JSON.stringify(data, null, 2)}</pre></details>}
  </section>;
}
