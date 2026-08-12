import { getAudit } from "../api/audits";
import { adaptAuditDetail } from "../adapters/auditResponseAdapter";
import { readKeys } from "../cache/readCache";
import type { AuditDetailResponse } from "../types/contract";
import { containsRawAuditSecretField, sanitizeAuditForDisplay } from "../utils/auditSanitizer";
import { useCachedRead } from "./useCachedRead";

interface CachedAuditDetail {
  data: AuditDetailResponse;
  sensitiveFieldsRemoved: boolean;
}

export function useAuditDetail(auditId: string | null) {
  const cached = useCachedRead<CachedAuditDetail>(
    auditId ? readKeys.audit(auditId) : null,
    async (signal) => {
      const adapted = adaptAuditDetail(await getAudit(auditId!, signal));
      return {
        sensitiveFieldsRemoved: containsRawAuditSecretField(adapted),
        data: sanitizeAuditForDisplay(adapted) as AuditDetailResponse,
      };
    },
    30_000,
  );
  return {
    data: cached.data?.data ?? null,
    loading: cached.loading,
    error: cached.error?.message ?? null,
    sensitiveFieldsRemoved: cached.data?.sensitiveFieldsRemoved ?? false,
    refresh: cached.refresh,
  };
}
