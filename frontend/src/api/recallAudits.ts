import { apiClient } from "./client";
import type { RecallAIAuditResponse, RecallAuditRecentResponse } from "../types/contract";

export function getRecentRecallAudits(signal?: AbortSignal): Promise<RecallAuditRecentResponse> {
  return apiClient.get<RecallAuditRecentResponse>("/api/recall-audits/recent", { limit: 20 }, { signal });
}

export function analyzeRecallAudit(turnId: string): Promise<RecallAIAuditResponse> {
  return apiClient.post<RecallAIAuditResponse>(`/api/recall-audits/${encodeURIComponent(turnId)}/analyze`, undefined, { timeoutMs: 60_000 });
}
