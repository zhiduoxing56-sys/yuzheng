import type { AuditVerificationResponse } from "../types/contract";
import { auditVerificationPassed, booleanLabel } from "../utils/auditMapper";
import { formatDateTime } from "../utils/formatters";

interface Props { data: AuditVerificationResponse | null; loading: boolean; error: string | null; verifiedAt: Date | null; onRefresh: () => void; }

export function AuditVerificationPanel({ data, loading, error, verifiedAt, onRefresh }: Props) {
  const passed = auditVerificationPassed(data);
  return <section className={`audit-detail-section audit-verification ${passed === false ? "invalid" : ""}`}><div className="audit-section-heading"><span className="eyebrow">10 · INTEGRITY</span><h2>单条完整性校验</h2></div><div className="audit-verification-heading"><strong>{passed === null ? loading ? "正在请求后端校验" : "暂无校验结果" : passed ? "后端校验项全部通过" : "后端校验报告异常"}</strong><button className="secondary-button compact" onClick={onRefresh} disabled={loading}>{loading ? "校验中…" : "重新校验"}</button></div>{data && <dl className="audit-fact-grid"><div><dt>记录哈希</dt><dd>{booleanLabel(data.record_hash_valid, "有效", "异常")}</dd></div><div><dt>前序记录关联</dt><dd>{booleanLabel(data.previous_link_valid, "有效", "异常")}</dd></div><div><dt>审计链</dt><dd>{booleanLabel(data.audit_chain_valid, "通过", "异常")}</dd></div><div><dt>工作流链</dt><dd>{booleanLabel(data.workflow_chain_valid, "通过", "异常")}</dd></div><div><dt>终态关系</dt><dd>{booleanLabel(data.relationship_valid, "有效", "异常")}</dd></div><div><dt>裁决合并</dt><dd>{booleanLabel(data.merge_decision_valid, "有效", "异常")}</dd></div><div><dt>有效终态</dt><dd>{booleanLabel(data.effective_outcome_valid, "有效", "异常")}</dd></div><div><dt>终态审计编号</dt><dd>{data.terminal_audit_id || "无"}</dd></div></dl>}{data?.failure_reason && <p className="audit-danger-copy">{data.failure_reason}</p>}{error && <p className="inline-error">校验请求失败：{error}</p>}<small className="audit-verified-at">{verifiedAt ? `本次页面校验时间：${formatDateTime(verifiedAt.toISOString())}` : "校验结论完全来自后端；前端不重算哈希。"}</small></section>;
}
