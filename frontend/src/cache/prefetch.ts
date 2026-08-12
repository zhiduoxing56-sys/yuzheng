import { adaptAuditDetail } from "../adapters/auditResponseAdapter";
import { adaptTurnPresentation } from "../adapters/turnPresentationAdapter";
import { adaptTimeline, adaptWorkflowStatus } from "../adapters/workflowResponseAdapter";
import { getAudit } from "../api/audits";
import { getTurnEvidence } from "../api/evidence";
import { getTurnPresentation, getTurnTimelineSummary, getTurnWorkflowStatus } from "../api/turns";
import type { AuditDetailResponse } from "../types/contract";
import { containsRawAuditSecretField, sanitizeAuditForDisplay } from "../utils/auditSanitizer";
import { readCache, readKeys } from "./readCache";

export function prefetchPresentation(turnId: string): void {
  readCache.prefetch(readKeys.presentation(turnId), async (signal) => adaptTurnPresentation(await getTurnPresentation(turnId, signal)));
}

export function prefetchEvidence(turnId: string): void {
  prefetchPresentation(turnId);
  readCache.prefetch(readKeys.evidence(turnId), (signal) => getTurnEvidence(turnId, signal), 30_000);
}

export function prefetchReview(turnId: string): void {
  prefetchPresentation(turnId);
  readCache.prefetch(readKeys.workflow(turnId), async (signal) => adaptWorkflowStatus(await getTurnWorkflowStatus(turnId, signal)));
  readCache.prefetch(readKeys.timeline(turnId), async (signal) => adaptTimeline(await getTurnTimelineSummary(turnId, signal)));
}

export function prefetchAudit(auditId: string): void {
  readCache.prefetch(readKeys.audit(auditId), async (signal) => {
    const adapted = adaptAuditDetail(await getAudit(auditId, signal));
    return {
      sensitiveFieldsRemoved: containsRawAuditSecretField(adapted),
      data: sanitizeAuditForDisplay(adapted) as AuditDetailResponse,
    };
  }, 30_000);
}
