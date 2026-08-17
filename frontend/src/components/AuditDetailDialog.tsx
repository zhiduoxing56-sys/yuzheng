import { useEffect, useRef } from "react";
import { useAuditDetail } from "../hooks/useAuditDetail";
import { useAuditVerification } from "../hooks/useAuditVerification";
import { AuditVerificationPanel } from "./AuditVerificationPanel";
import {
  AuditCommandSection,
  AuditDecisionSection,
  AuditExecutionSection,
  AuditIntegritySection,
  AuditReviewSection,
  AuditSnapshotSection,
  AuditUnderstandingSection,
} from "./AuditDetailSections";

interface AuditDetailDialogProps {
  auditId: string | null;
  onClose: () => void;
}

export function AuditDetailDialog({ auditId, onClose }: AuditDetailDialogProps) {
  const detail = useAuditDetail(auditId);
  const verification = useAuditVerification(auditId);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!auditId) return;
    closeButtonRef.current?.focus();
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [auditId, onClose]);

  if (!auditId) return null;

  return <div className="audit-detail-dialog-backdrop" role="presentation" onMouseDown={onClose}>
    <section className="audit-detail-dialog" role="dialog" aria-modal="true" aria-labelledby="audit-detail-dialog-title" onMouseDown={(event) => event.stopPropagation()}>
      <header className="audit-detail-dialog-header">
        <div>
          <h2 id="audit-detail-dialog-title">审计详情</h2>
        </div>
        <div className="audit-detail-dialog-actions">
          <button type="button" disabled={detail.loading} onClick={detail.refresh}>{detail.loading ? "加载中…" : "刷新"}</button>
          <button ref={closeButtonRef} type="button" onClick={onClose}>关闭</button>
        </div>
      </header>

      <div className="audit-detail-dialog-body">
        {detail.loading && !detail.data && <p className="audit-detail-dialog-status" role="status">正在加载审计详情…</p>}
        {detail.error && !detail.data && <div className="audit-detail-dialog-status is-error" role="alert"><p>审计详情加载失败：{detail.error}</p><button type="button" onClick={detail.refresh}>重试</button></div>}
        {detail.error && detail.data && <p className="audit-detail-dialog-status is-error" role="alert">刷新失败：{detail.error}。当前继续显示最近一次成功结果。</p>}
        {detail.data && <main className="audit-detail-flow">
          <AuditCommandSection data={detail.data} />
          <AuditUnderstandingSection data={detail.data} />
          <AuditSnapshotSection data={detail.data} />
          <AuditDecisionSection data={detail.data} />
          <AuditReviewSection data={detail.data} />
          <AuditExecutionSection data={detail.data} />
          <AuditIntegritySection data={detail.data} />
          <AuditVerificationPanel data={verification.data} loading={verification.loading} error={verification.error} verifiedAt={verification.verifiedAt} onRefresh={verification.refresh} />
        </main>}
      </div>
    </section>
  </div>;
}
