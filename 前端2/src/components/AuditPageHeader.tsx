interface Props {
  total: number;
  visible: number;
  loading: boolean;
  onRefresh: () => void;
}

export function AuditPageHeader({ total, visible, loading, onRefresh }: Props) {
  return <header className="audit-page-header">
    <div><span className="eyebrow">AUDIT TRACE</span><h1>审计记录</h1><p>查询后端持久化审计，核对裁决解释、工作流事件与完整性结论。</p></div>
    <div className="audit-header-stats"><div><span>筛选记录总数</span><strong>{total}</strong></div><div><span>当前页记录</span><strong>{visible}</strong></div><button className="secondary-button" onClick={onRefresh} disabled={loading}>{loading ? "刷新中…" : "刷新列表"}</button></div>
  </header>;
}
