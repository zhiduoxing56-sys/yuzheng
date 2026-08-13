import { useMemo } from "react";
import { useLocation } from "react-router-dom";
import { buildAuditListPath, parseAuditQueryParams } from "../utils/auditQueryParams";
import { useAuditDetail } from "./useAuditDetail";

const LIST_KEYS = ["page", "page_size", "decision", "start_time", "end_time"];

export function useAuditDetailController(routeAuditId?: string) {
  const auditId = routeAuditId?.trim() || null;
  const location = useLocation();
  const params = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const hasListContext = LIST_KEYS.some((key) => params.has(key));
  const parsedReturnQuery = useMemo(() => parseAuditQueryParams(params), [params]);
  const returnPath = hasListContext ? buildAuditListPath(parsedReturnQuery.query) : "/audits";
  const detail = useAuditDetail(auditId);
  return { auditId, returnPath, returnQueryIssues: hasListContext ? parsedReturnQuery.issues : [], detail };
}
