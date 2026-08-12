import { apiClient, type QueryValue } from "./client";
import type { AuditExportPayload } from "../types/contract";

const AUDIT_READ_TIMEOUT_MS = 60_000;

export interface AuditListQuery {
  page?: number;
  page_size?: number;
  decision?: string;
  start_time?: string;
  end_time?: string;
}

export function listAudits(query: AuditListQuery = {}, signal?: AbortSignal): Promise<unknown> {
  return apiClient.get<unknown>("/api/audits/compact", query as Record<string, QueryValue>, { signal, timeoutMs: AUDIT_READ_TIMEOUT_MS });
}

export function getAudit(auditId: string, signal?: AbortSignal): Promise<unknown> {
  return apiClient.get<unknown>(`/api/audits/${encodeURIComponent(auditId)}`, undefined, { signal, timeoutMs: AUDIT_READ_TIMEOUT_MS });
}

export function verifyAudit(auditId: string, signal?: AbortSignal): Promise<unknown> {
  return apiClient.get<unknown>(`/api/audits/${encodeURIComponent(auditId)}/verify`, undefined, { signal, timeoutMs: AUDIT_READ_TIMEOUT_MS });
}

/** Backend extension: export is intentionally kept out of the frozen public API types. */
export function exportAudit(auditId: string, signal?: AbortSignal): Promise<AuditExportPayload> {
  return apiClient.get<AuditExportPayload>(`/api/audits/${encodeURIComponent(auditId)}/export`, undefined, { signal, timeoutMs: AUDIT_READ_TIMEOUT_MS });
}

/** Backend extension: the current endpoint returns only the aggregate validity flag. */
export function verifyGlobalAuditChain(signal?: AbortSignal): Promise<unknown> {
  return apiClient.get<unknown>("/api/audits/verify-chain", undefined, { signal, timeoutMs: AUDIT_READ_TIMEOUT_MS });
}
