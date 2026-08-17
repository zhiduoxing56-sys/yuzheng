import type { GlobalAuditChainView } from "../adapters/auditResponseAdapter";
import { formatDateTime } from "../utils/formatters";

interface Props { data: GlobalAuditChainView | null; loading: boolean; error: string | null; verifiedAt: Date | null; onRefresh: () => void; }

export function AuditChainSummary({ data, loading, error, verifiedAt, onRefresh }: Props) {
  const status = loading
    ? "正在验证"
    : !data
      ? "等待验证"
      : data.state === "valid"
        ? "审计链正常"
        : data.firstAnomaly
          ? `检测到异常：${data.firstAnomaly.auditId}（${data.firstAnomaly.type}）`
          : "检测到审计记录完整性异常";
  return <section className={`audit-chain-summary audit-integrity-summary ${data?.state === "invalid" ? "invalid" : ""}`}>
    <div className="audit-integrity-status"><strong>{status}</strong>{verifiedAt && <small>本次页面验证时间：{formatDateTime(verifiedAt.toISOString())}</small>}</div>
    <button className="audit-integrity-verify" onClick={onRefresh} disabled={loading}>{loading ? "验证中" : "验证"}</button>
    {data && <dl className="audit-integrity-metrics"><div><dt>总记录</dt><dd>{data.totalRecords}</dd></div><div><dt>历史记录</dt><dd>{data.legacyUnsignedRecords}</dd></div><div><dt>签名保护</dt><dd>{data.signatureProtectedRecords}</dd></div><div><dt>签名通过</dt><dd>{data.signatureVerifiedRecords}</dd></div><div><dt>哈希链</dt><dd>{data.hashChainStatus === "VALID" ? "正常" : "异常"}</dd></div><div><dt>数字签名</dt><dd>{data.signatureStatus === "VALID" ? "有效" : data.signatureStatus === "NOT_ENABLED" ? "暂无" : "异常"}</dd></div></dl>}
    {error && <p className="inline-error">{error}</p>}
  </section>;
}
