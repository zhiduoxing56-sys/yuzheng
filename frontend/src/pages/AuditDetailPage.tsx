import { useState } from "react";
import { useParams } from "react-router-dom";
import { AuditDetailHeader } from "../components/AuditDetailHeader";
import { AuditCommandSection, AuditDecisionSection, AuditExecutionSection, AuditIntegritySection, AuditReviewSection, AuditSnapshotSection, AuditUnderstandingSection } from "../components/AuditDetailSections";
import { AuditSemanticFrameDialog } from "../components/AuditSemanticFrameDialog";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { useAuditDetailController } from "../hooks/useAuditDetailController";
import { getAuditSemanticFrame } from "../api/audits";
import type { SemanticFrame } from "../types/contract";

export function AuditDetailPage() {
  const { auditId } = useParams<{ auditId: string }>();
  const controller = useAuditDetailController(auditId);
  const [technicalFrame, setTechnicalFrame] = useState<SemanticFrame | null>(null);
  const [technicalError, setTechnicalError] = useState<string | null>(null);
  if (!controller.auditId) return <div className="audit-detail-page"><EmptyState title="缺少审计编号" description="地址中没有有效 auditId，无法请求审计详情。" /></div>;
  const { detail } = controller;
  return <div className="audit-detail-page">
    <AuditDetailHeader returnPath={controller.returnPath} data={detail.data} loading={detail.loading} onRefresh={detail.refresh} />
    {detail.loading && !detail.data && <div className="loading-state"><span className="loading-dot" />正在加载真实审计详情…</div>}
    {detail.error && !detail.data && <ErrorState title="审计记录不存在或后端不可用" description={detail.error} onRetry={detail.refresh} />}
    {detail.error && detail.data && <p className="audit-inline-error">详情刷新失败：{detail.error}。当前继续展示最近一次成功结果。</p>}
    {detail.data && <main className="audit-detail-flow"><AuditCommandSection data={detail.data} /><AuditUnderstandingSection data={detail.data} /><AuditSnapshotSection data={detail.data} /><AuditDecisionSection data={detail.data} /><AuditReviewSection data={detail.data} /><AuditExecutionSection data={detail.data} /><AuditIntegritySection data={detail.data} /><details className="audit-technical-entry"><summary>技术详情</summary><button type="button" className="secondary-button" onClick={() => { setTechnicalError(null); void getAuditSemanticFrame(controller.auditId!).then(setTechnicalFrame).catch((error: unknown) => setTechnicalError(error instanceof Error ? error.message : "语义帧加载失败")); }}>查看语义帧详细结果</button>{technicalError && <p className="audit-inline-error">{technicalError}</p>}</details></main>}
    <AuditSemanticFrameDialog frame={technicalFrame} onClose={() => setTechnicalFrame(null)} />
  </div>;
}
