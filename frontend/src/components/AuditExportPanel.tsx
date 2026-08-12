import { formatDateTime } from "../utils/formatters";

interface Props { loading: boolean; error: string | null; downloadedAt: Date | null; onDownload: () => void; }

export function AuditExportPanel({ loading, error, downloadedAt, onDownload }: Props) {
  return <section className="audit-detail-section audit-export"><div className="audit-section-heading"><span className="eyebrow">11 · EXPORT</span><h2>审计导出</h2></div><p>按需获取后端真实 JSON，并在浏览器下载前递归删除名称包含 token 或 secret 的敏感字段。</p><button className="primary-button" onClick={onDownload} disabled={loading}>{loading ? "正在安全导出…" : "导出脱敏 JSON"}</button>{downloadedAt && <small>最近导出完成：{formatDateTime(downloadedAt.toISOString())}</small>}{error && <p className="inline-error">导出失败：{error}</p>}</section>;
}
