import { Link } from "react-router-dom";
import { prefetchAudit } from "../cache/prefetch";
import type { AuditListViewItem } from "../adapters/auditResponseAdapter";
import { auditDecisionLabel, auditDecisionTone } from "../utils/auditMapper";
import { formatDateTime } from "../utils/formatters";

interface Props { items: AuditListViewItem[]; loading: boolean; detailPath: (auditId: string) => string; }

export function AuditTable({ items, loading, detailPath }: Props) {
  return <section className="audit-table-section">
    {loading && <div className="audit-local-loading"><span className="loading-dot" />正在更新列表，当前数据暂时保留…</div>}
    <div className="audit-table-scroll"><table className="audit-table"><thead><tr><th>时间</th><th>原始指令</th><th>最终裁决</th><th>执行结果</th><th>是否复核</th><th /></tr></thead><tbody>{items.map((item) => {
      const finalDecision = item.finalDecision;
      const tone = auditDecisionTone(finalDecision);
      return <tr key={item.auditId}><td><time>{formatDateTime(item.createdAt)}</time></td><td className="audit-summary-cell">{item.rawCommand}</td><td><span className={`status-badge status-${tone}`}>{auditDecisionLabel(finalDecision)}</span></td><td>{item.executionStatus}</td><td>{item.reviewOccurred ? "是" : "否"}</td><td><Link className="primary-link compact" to={detailPath(item.auditId)} onMouseEnter={() => prefetchAudit(item.auditId)} onFocus={() => prefetchAudit(item.auditId)}>查看详情</Link></td></tr>;
    })}</tbody></table></div>
  </section>;
}
