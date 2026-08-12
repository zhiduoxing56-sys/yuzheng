interface Props { page: number; totalPages: number; total: number; disabled: boolean; onPage: (page: number) => void; }

export function AuditPagination({ page, totalPages, total, disabled, onPage }: Props) {
  return <nav className="audit-pagination" aria-label="审计列表分页"><span>第 {page} / {totalPages} 页，共 {total} 条</span><div><button className="secondary-button compact" disabled={disabled || page <= 1} onClick={() => onPage(page - 1)}>上一页</button><button className="secondary-button compact" disabled={disabled || page >= totalPages} onClick={() => onPage(page + 1)}>下一页</button></div></nav>;
}
