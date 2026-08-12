import type { AuditListQuery } from "../api/audits";
import type { DecisionLabel } from "../types/contract";

export const DEFAULT_AUDIT_PAGE = 1;
export const DEFAULT_AUDIT_PAGE_SIZE = 20;
export const AUDIT_PAGE_SIZE_OPTIONS = [10, 20, 50, 100] as const;
const DECISIONS = new Set<DecisionLabel>(["PASS", "REVIEW", "BLOCK"]);

export interface AuditQueryState {
  page: number;
  page_size: number;
  decision?: DecisionLabel;
  start_time?: string;
  end_time?: string;
}

export interface ParsedAuditQuery {
  query: AuditQueryState;
  validTimeRange: boolean;
  issues: string[];
}

function positiveInteger(value: string | null, fallback: number, maximum?: number): number {
  if (!value || !/^\d+$/.test(value)) return fallback;
  const parsed = Number(value);
  return parsed >= 1 && (!maximum || parsed <= maximum) ? parsed : fallback;
}

function standardDateTime(value: string | null): string | undefined {
  if (!value || !/(?:Z|[+-]\d{2}:\d{2})$/i.test(value)) return undefined;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString();
}

export function parseAuditQueryParams(params: URLSearchParams): ParsedAuditQuery {
  const issues: string[] = [];
  const rawPage = params.get("page");
  const rawPageSize = params.get("page_size");
  const rawDecision = params.get("decision");
  const rawStart = params.get("start_time");
  const rawEnd = params.get("end_time");
  const page = positiveInteger(rawPage, DEFAULT_AUDIT_PAGE);
  const pageSize = positiveInteger(rawPageSize, DEFAULT_AUDIT_PAGE_SIZE, 100);
  const decision = rawDecision && DECISIONS.has(rawDecision as DecisionLabel) ? rawDecision as DecisionLabel : undefined;
  const startTime = standardDateTime(rawStart);
  const endTime = standardDateTime(rawEnd);
  if (rawPage && page === DEFAULT_AUDIT_PAGE && rawPage !== String(DEFAULT_AUDIT_PAGE)) issues.push("页码无效，已恢复为第一页");
  if (rawPageSize && pageSize === DEFAULT_AUDIT_PAGE_SIZE && rawPageSize !== String(DEFAULT_AUDIT_PAGE_SIZE)) issues.push("每页数量无效，已恢复默认值");
  if (rawDecision && !decision) issues.push("裁决筛选无效，已恢复为全部");
  if (rawStart && !startTime) issues.push("开始时间格式无效，已清除");
  if (rawEnd && !endTime) issues.push("结束时间格式无效，已清除");
  const validTimeRange = !(startTime && endTime && Date.parse(startTime) > Date.parse(endTime));
  if (!validTimeRange) issues.push("开始时间不得晚于结束时间");
  return {
    query: { page, page_size: pageSize, ...(decision && { decision }), ...(startTime && { start_time: startTime }), ...(endTime && { end_time: endTime }) },
    validTimeRange,
    issues,
  };
}

export function serializeAuditQuery(query: AuditQueryState): URLSearchParams {
  const params = new URLSearchParams();
  params.set("page", String(query.page));
  params.set("page_size", String(query.page_size));
  if (query.decision) params.set("decision", query.decision);
  if (query.start_time) params.set("start_time", query.start_time);
  if (query.end_time) params.set("end_time", query.end_time);
  return params;
}

export function toAuditListQuery(query: AuditQueryState): AuditListQuery {
  return { ...query };
}

export function buildAuditListPath(query: AuditQueryState): string {
  return `/audits?${serializeAuditQuery(query).toString()}`;
}

export function buildAuditDetailPath(auditId: string, query?: AuditQueryState): string {
  const path = `/audits/${encodeURIComponent(auditId)}`;
  return query ? `${path}?${serializeAuditQuery(query).toString()}` : path;
}

export function toDateTimeLocal(value?: string): string {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const shifted = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return shifted.toISOString().slice(0, 16);
}

export function fromDateTimeLocal(value: string): string | undefined {
  if (!value) return undefined;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? undefined : date.toISOString();
}

export function totalAuditPages(total: number, pageSize: number): number {
  return Math.max(1, Math.ceil(total / pageSize));
}
