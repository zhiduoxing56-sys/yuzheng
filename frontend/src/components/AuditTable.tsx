import { Link } from "react-router-dom";
import { prefetchAudit } from "../cache/prefetch";
import type { AuditListViewItem } from "../adapters/auditResponseAdapter";
import { auditDecisionLabel, auditDecisionTone } from "../utils/auditMapper";
import { formatDateTime } from "../utils/formatters";

interface Props { items: AuditListViewItem[]; loading: boolean; detailPath: (auditId: string) => string; }

export function AuditTable({ items, loading, detailPath }: Props) {
  return <section className="audit-table-section">
    {loading && <div className="audit-local-loading"><span className="loading-dot" />正在更新列表，当前数据暂时保留…</div>}
    <div className="audit-table-scroll"><table className="audit-table"><thead><tr><th>审计时间</th><th>指令摘要</th><th>动作 / 目标</th><th>风险</th><th>最终裁决</th><th>执行状态</th><th>轮次编号</th><th /></tr></thead><tbody>{items.map((item) => {
      const finalDecision = item.finalDecision;
      const tone = auditDecisionTone(finalDecision);
      return <tr key={item.auditId}><td><time>{formatDateTime(item.createdAt)}</time></td><td className="audit-summary-cell" title={item.instructionSummary}>{item.instructionSummary || "后端未提供"}</td><td>{item.action || "后端未提供"} / {item.target || "后端未提供"}</td><td>{item.riskLevel || "轻量列表未加载"}</td><td><span className={`status-badge status-${tone}`}>{auditDecisionLabel(finalDecision)}</span></td><td>{item.executionStatus || "后端未提供"}</td><td><code title={item.turnId}>{item.turnId}</code></td><td><Link className="primary-link compact" to={detailPath(item.auditId)} onMouseEnter={() => prefetchAudit(item.auditId)} onFocus={() => prefetchAudit(item.auditId)}>查看详情</Link></td></tr>;
    })}</tbody></table></div>
  </section>;
}
