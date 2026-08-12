import type { GlobalAuditChainView } from "../adapters/auditResponseAdapter";
import { formatDateTime } from "../utils/formatters";

interface Props { data: GlobalAuditChainView | null; loading: boolean; error: string | null; verifiedAt: Date | null; onRefresh: () => void; }

export function AuditChainSummary({ data, loading, error, verifiedAt, onRefresh }: Props) {
  return <section className={`audit-chain-summary ${data?.state === "invalid" ? "invalid" : ""}`}>
    <div><span className="eyebrow">GLOBAL CHAIN</span><strong>{data ? data.state === "valid" ? "全局审计链通过" : data.state === "empty" ? "后端没有可校验记录" : `全局审计链异常（${data.invalidCount} 条）` : loading ? "正在校验全局审计链" : "尚未取得校验结果"}</strong><small>{verifiedAt ? `本次页面校验时间：${formatDateTime(verifiedAt.toISOString())}` : "等待本次页面校验。"}</small></div>
    {error && <p className="inline-error">{error}。审计列表仍可继续使用。</p>}
    <button className="secondary-button compact" onClick={onRefresh} disabled={loading}>{loading ? "校验中…" : data || error ? "重新校验" : "开始校验"}</button>
  </section>;
}
