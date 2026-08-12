import { Link } from "react-router-dom";
import type { AuditDetailResponse } from "../types/contract";
import { auditDecisionLabel, auditDecisionTone } from "../utils/auditMapper";
import { formatDateTime } from "../utils/formatters";

interface Props { requestedAuditId: string; returnPath: string; data: AuditDetailResponse | null; loading: boolean; onRefresh: () => void; }

export function AuditDetailHeader({ requestedAuditId, returnPath, data, loading, onRefresh }: Props) {
  const decision = data?.final_decision.final_decision;
  return <header className="audit-detail-header">
    <div><span className="eyebrow">AUDIT DETAIL</span><h1>审计详情</h1><p>按后端持久化记录还原指令、证据、裁决和工作流完整性。</p></div>
    <dl><div><dt>地址审计编号</dt><dd title={requestedAuditId}>{requestedAuditId}</dd></div><div><dt>轮次编号</dt><dd title={data?.turn_id}>{data?.turn_id || "正在加载…"}</dd></div><div><dt>审计时间</dt><dd>{formatDateTime(data?.created_at)}</dd></div><div><dt>最终裁决</dt><dd><span className={`status-badge status-${auditDecisionTone(decision)}`}>{auditDecisionLabel(decision)}</span></dd></div><div><dt>记录链 / 工作流链</dt><dd>{data ? `${data.audit_chain_valid ? "通过" : "异常"} / ${data.workflow_chain_valid ? "通过" : "异常"}` : "暂无"}</dd></div></dl>
    <div className="audit-detail-actions"><button className="secondary-button" onClick={onRefresh} disabled={loading}>{loading ? "刷新中…" : "刷新详情"}</button><Link className="secondary-button" to={returnPath}>返回审计列表</Link>{data && <><Link className="secondary-button" to="/decision">查看实时裁决</Link><Link className="secondary-button" to={`/evidence/${encodeURIComponent(data.turn_id)}`}>查看分层证据</Link><Link className="secondary-button" to={`/review/${encodeURIComponent(data.turn_id)}`}>查看复核与执行</Link></>}</div>
  </header>;
}
