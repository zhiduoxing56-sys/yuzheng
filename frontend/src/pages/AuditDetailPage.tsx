import { useParams } from "react-router-dom";
import { AuditDetailHeader } from "../components/AuditDetailHeader";
import { AuditAuthorizationSection, AuditCommandSection, AuditDecisionSection, AuditEvidenceSection, AuditExecutionSection, AuditRelationSection, AuditReviewSection, AuditSecurityAlertSection, AuditTimelineSection } from "../components/AuditDetailSections";
import { AuditExportPanel } from "../components/AuditExportPanel";
import { AuditVerificationPanel } from "../components/AuditVerificationPanel";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { useAuditDetailController } from "../hooks/useAuditDetailController";

export function AuditDetailPage() {
  const { auditId } = useParams<{ auditId: string }>();
  const controller = useAuditDetailController(auditId);
  if (!controller.auditId) return <div className="audit-detail-page"><EmptyState title="缺少审计编号" description="地址中没有有效 auditId，无法请求审计详情。" /></div>;
  const { detail, verification, auditExport } = controller;
  return <div className="audit-detail-page">
    <AuditDetailHeader requestedAuditId={controller.auditId} returnPath={controller.returnPath} data={detail.data} loading={detail.loading} onRefresh={detail.refresh} />
    {controller.returnQueryIssues.length > 0 && <p className="audit-query-note">返回列表参数已规范化：{controller.returnQueryIssues.join("；")}</p>}
    {controller.containsSensitiveFields && <p className="audit-sensitive-warning">后端详情包含敏感命名字段；前端已禁止渲染这些原始字段，导出时还会递归删除。</p>}
    {detail.loading && !detail.data && <div className="loading-state"><span className="loading-dot" />正在加载真实审计详情…</div>}
    {detail.error && !detail.data && <ErrorState title="审计记录不存在或后端不可用" description={detail.error} onRetry={detail.refresh} />}
    {detail.error && detail.data && <p className="audit-inline-error">详情刷新失败：{detail.error}。当前继续展示最近一次成功结果。</p>}
    {detail.data && <main className="audit-detail-flow"><AuditCommandSection data={detail.data} /><AuditEvidenceSection data={detail.data} /><AuditDecisionSection data={detail.data} /><AuditSecurityAlertSection data={detail.data} /><AuditReviewSection data={detail.data} /><AuditAuthorizationSection data={detail.data} /><AuditExecutionSection data={detail.data} /><AuditRelationSection data={detail.data} /><AuditTimelineSection data={detail.data} /><AuditVerificationPanel data={verification.data} loading={verification.loading} error={verification.error} verifiedAt={verification.verifiedAt} onRefresh={verification.refresh} /><AuditExportPanel loading={auditExport.loading} error={auditExport.error} downloadedAt={auditExport.downloadedAt} onDownload={() => { void auditExport.download(); }} /></main>}
  </div>;
}
