import { useCallback, useEffect, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import type { DecisionLabel } from "../types/contract";
import { buildAuditDetailPath, parseAuditQueryParams, serializeAuditQuery, toAuditListQuery, totalAuditPages, type AuditQueryState } from "../utils/auditQueryParams";
import { useAuditList } from "./useAuditList";
import { useGlobalAuditChain } from "./useGlobalAuditChain";

export function useAuditListController() {
  const location = useLocation();
  const navigate = useNavigate();
  const parsed = useMemo(() => parseAuditQueryParams(new URLSearchParams(location.search)), [location.search]);
  const canonicalSearch = useMemo(() => serializeAuditQuery(parsed.query).toString(), [parsed.query.page, parsed.query.page_size, parsed.query.decision, parsed.query.start_time, parsed.query.end_time]);

  useEffect(() => {
    if (location.search.slice(1) !== canonicalSearch) navigate(`/audits?${canonicalSearch}`, { replace: true });
  }, [canonicalSearch, location.search, navigate]);

  const list = useAuditList(parsed.validTimeRange ? toAuditListQuery(parsed.query) : null);
  const chain = useGlobalAuditChain();

  const replaceQuery = useCallback((next: AuditQueryState) => navigate(`/audits?${serializeAuditQuery(next).toString()}`), [navigate]);
  const setPage = useCallback((page: number) => replaceQuery({ ...parsed.query, page }), [parsed.query, replaceQuery]);
  const setPageSize = useCallback((pageSize: number) => replaceQuery({ ...parsed.query, page: 1, page_size: pageSize }), [parsed.query, replaceQuery]);
  const setDecision = useCallback((decision?: DecisionLabel) => replaceQuery({ ...parsed.query, page: 1, decision }), [parsed.query, replaceQuery]);
  const setTimeRange = useCallback((start_time?: string, end_time?: string) => replaceQuery({ ...parsed.query, page: 1, start_time, end_time }), [parsed.query, replaceQuery]);
  const reset = useCallback(() => replaceQuery({ page: 1, page_size: 20 }), [replaceQuery]);

  const totalPages = totalAuditPages(list.data?.total || 0, parsed.query.page_size);
  useEffect(() => {
    if (list.data && list.data.total > 0 && parsed.query.page > totalPages) setPage(totalPages);
  }, [list.data, parsed.query.page, setPage, totalPages]);

  const detailPath = useCallback((auditId: string) => buildAuditDetailPath(auditId, parsed.query), [parsed.query]);
  return { query: parsed.query, queryIssues: parsed.issues, validTimeRange: parsed.validTimeRange, list, chain, totalPages, setPage, setPageSize, setDecision, setTimeRange, reset, detailPath };
}
