import { useMemo, useRef } from "react";
import { listAudits, type AuditListQuery } from "../api/audits";
import { adaptAuditList, type AuditListView } from "../adapters/auditResponseAdapter";
import { readKeys } from "../cache/readCache";
import { sanitizeAuditForDisplay } from "../utils/auditSanitizer";
import { useCachedRead } from "./useCachedRead";

function normalizedQuery(query: AuditListQuery): string {
  return JSON.stringify({
    page: query.page ?? 1,
    page_size: query.page_size ?? 20,
    decision: query.decision ?? "",
    start_time: query.start_time ?? "",
    end_time: query.end_time ?? "",
  });
}

export function useAuditList(query: AuditListQuery | null) {
  const queryRef = useRef(query);
  queryRef.current = query;
  const key = useMemo(() => query ? readKeys.audits(normalizedQuery(query)) : null,
    [query?.page, query?.page_size, query?.decision, query?.start_time, query?.end_time]);
  const cached = useCachedRead<AuditListView>(key, async (signal) => {
    const current = queryRef.current;
    if (!current) throw new Error("审计筛选参数不可用");
    return sanitizeAuditForDisplay(adaptAuditList(await listAudits(current, signal))) as AuditListView;
  }, 10_000);
  return { data: cached.data, loading: cached.loading, error: cached.error?.message ?? null, refresh: cached.refresh };
}
