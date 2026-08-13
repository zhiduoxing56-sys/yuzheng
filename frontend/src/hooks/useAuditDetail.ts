import { getAudit } from "../api/audits";
import { adaptAuditDetail } from "../adapters/auditResponseAdapter";
import { readKeys } from "../cache/readCache";
import type { AuditDetailView } from "../types/contract";
import { useCachedRead } from "./useCachedRead";

interface CachedAuditDetail {
  data: AuditDetailView;
}

export function useAuditDetail(auditId: string | null) {
  const cached = useCachedRead<CachedAuditDetail>(
    auditId ? readKeys.audit(auditId) : null,
    async (signal) => {
      const adapted = adaptAuditDetail(await getAudit(auditId!, signal));
      return { data: adapted };
    },
    30_000,
  );
  return {
    data: cached.data?.data ?? null,
    loading: cached.loading,
    error: cached.error?.message ?? null,
    refresh: cached.refresh,
  };
}
