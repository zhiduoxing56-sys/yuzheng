import { apiClient } from "./client";
import type {
  AuditDetailResponse,
  AdvancedReasoningResult,
  ExecuteResult,
  ReviewSubmission,
  ReviewSubmissionResponse,
  TimelineResponse,
  TurnWorkflowStatus,
  TurnPresentationResponse,
  WorkflowChainVerification,
} from "../types/contract";

export function getTurnPresentation(turnId: string, signal?: AbortSignal): Promise<unknown> {
  return apiClient.get<unknown>(`/api/turns/${encodeURIComponent(turnId)}/presentation`, undefined, { signal, timeoutMs: 45_000 });
}

export function submitTurnReview(turnId: string, request: ReviewSubmission): Promise<unknown> {
  return apiClient.post<unknown>(`/api/turns/${encodeURIComponent(turnId)}/review`, request);
}

export function getTurnTimeline(turnId: string, signal?: AbortSignal): Promise<unknown> {
  return apiClient.get<unknown>(`/api/turns/${encodeURIComponent(turnId)}/timeline-summary`, undefined, { signal });
}

/** Backend extension endpoints used by later workflow pages. */
export function getTurnWorkflowStatus(turnId: string, signal?: AbortSignal): Promise<unknown> {
  return apiClient.get<unknown>(`/api/turns/${encodeURIComponent(turnId)}/workflow-status`, undefined, { signal });
}

export function verifyTurnWorkflowChain(turnId: string, signal?: AbortSignal): Promise<WorkflowChainVerification> {
  return apiClient.get<WorkflowChainVerification>(`/api/turns/${encodeURIComponent(turnId)}/verify-workflow-chain`, undefined, { signal });
}

export function getTurnReasoning(turnId: string, signal?: AbortSignal): Promise<AdvancedReasoningResult> {
  return apiClient.get<AdvancedReasoningResult>(`/api/turns/${encodeURIComponent(turnId)}/reasoning`, undefined, { signal, timeoutMs: 45_000 });
}

export function executeTurn(
  turnId: string,
  authorizationToken: string,
  sessionId?: string,
): Promise<ExecuteResult> {
  return apiClient.post<ExecuteResult>(`/api/turns/${encodeURIComponent(turnId)}/execute`, {
    authorization_token: authorizationToken,
    session_id: sessionId,
  });
}

export type { AuditDetailResponse };
