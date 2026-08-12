import { apiClient } from "./client";

const AUDIT_RECORDS_READ_TIMEOUT_MS = 60_000;

/** Formal first-page read used only by the VisualPageShell audit records page. */
export function listAuditRecords(signal?: AbortSignal): Promise<unknown> {
  return apiClient.get<unknown>("/api/audits", { page: 1, page_size: 20 }, {
    signal,
    timeoutMs: AUDIT_RECORDS_READ_TIMEOUT_MS,
  });
}
