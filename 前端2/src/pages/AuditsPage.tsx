import { AuditChainSummary } from "../components/AuditChainSummary";
import { AuditFilterBar } from "../components/AuditFilterBar";
import { AuditPageHeader } from "../components/AuditPageHeader";
import { AuditPagination } from "../components/AuditPagination";
import { AuditTable } from "../components/AuditTable";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { useAuditListController } from "../hooks/useAuditListController";

export function AuditsPage() {
  const controller = useAuditListController();
  const { list } = controller;
  const firstLoadFailed = Boolean(list.error && !list.data);
  const empty = Boolean(list.data && list.data.total === 0);
  const filtered = Boolean(controller.query.decision || controller.query.start_time || controller.query.end_time);
  return <div className="audits-page">
    <AuditPageHeader total={list.data?.total || 0} visible={list.data?.items.length || 0} loading={list.loading} onRefresh={list.refresh} />
    <AuditChainSummary data={controller.chain.data} loading={controller.chain.loading} error={controller.chain.error} verifiedAt={controller.chain.verifiedAt} onRefresh={controller.chain.refresh} />
    <AuditFilterBar query={controller.query} issues={controller.queryIssues} validTimeRange={controller.validTimeRange} onDecision={controller.setDecision} onTimeRange={controller.setTimeRange} onPageSize={controller.setPageSize} onReset={controller.reset} />
    {firstLoadFailed && <ErrorState title="审计列表加载失败" description={list.error || "后端不可用"} onRetry={list.refresh} />}
    {list.error && list.data && <p className="audit-inline-error">本次刷新失败：{list.error}。页面继续保留最近一次成功列表。</p>}
    {!firstLoadFailed && empty && <EmptyState title={filtered ? "当前筛选没有审计记录" : "尚无审计记录"} description={filtered ? "请调整裁决或时间范围后重试。" : "后端当前没有持久化审计记录，页面不会生成占位数据。"} />}
    {list.data && list.data.items.length > 0 && <><AuditTable items={list.data.items} loading={list.loading} detailPath={controller.detailPath} /><AuditPagination page={controller.query.page} totalPages={controller.totalPages} total={list.data.total} disabled={list.loading} onPage={controller.setPage} /></>}
    {list.loading && !list.data && <div className="loading-state"><span className="loading-dot" />正在加载真实审计记录…</div>}
  </div>;
}
