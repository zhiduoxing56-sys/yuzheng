import { apiClient } from "./client";
import type {
  AdvancedReasoningResult,
  ExecuteResult,
  TimelineResponse,
  TurnWorkflowStatus,
  TurnPresentationResponse,
  WorkflowChainVerification,
  InteractionAction,
  DecisionExplanationStatusResponse,
  BayesianDiagnosticResponse,
} from "../types/contract";

export function getTurnPresentation(turnId: string, signal?: AbortSignal): Promise<TurnPresentationResponse> {
  return apiClient.get<TurnPresentationResponse>(`/api/turns/${encodeURIComponent(turnId)}/presentation`, undefined, { signal, timeoutMs: 45_000 });
}

export function getBayesianDiagnostic(
  turnId: string,
  signal?: AbortSignal,
): Promise<BayesianDiagnosticResponse> {
  return apiClient.get<BayesianDiagnosticResponse>(
    `/api/turns/${encodeURIComponent(turnId)}/bayesian-diagnostic`,
    undefined,
    { signal, timeoutMs: 10_000 },
  );
}

export function getDecisionExplanation(
  turnId: string,
  signal?: AbortSignal,
): Promise<DecisionExplanationStatusResponse> {
  return apiClient.get<DecisionExplanationStatusResponse>(
    `/api/turns/${encodeURIComponent(turnId)}/decision-explanation`,
    undefined,
    { signal, timeoutMs: 10_000 },
  );
}

export function retryDecisionExplanation(
  turnId: string,
): Promise<DecisionExplanationStatusResponse> {
  return apiClient.post<DecisionExplanationStatusResponse>(
    `/api/turns/${encodeURIComponent(turnId)}/decision-explanation/retry`,
    {},
    { timeoutMs: 10_000 },
  );
}

export function submitTurnInteraction(turnId: string, request: { interaction_id: string; action: InteractionAction; candidate_id?: string; text?: string; parameters?: Record<string, unknown>; }): Promise<{ interaction_id: string; command_result: import("../types/contract").TextCommandResponse | null }> {
  return apiClient.post(`/api/turns/${encodeURIComponent(turnId)}/interaction`, request, { timeoutMs: 60_000 });
}


export function getTurnTimeline(turnId: string, signal?: AbortSignal): Promise<unknown> {
  return apiClient.get<unknown>(`/api/turns/${encodeURIComponent(turnId)}/timeline`, undefined, { signal });
}

export function getTurnTimelineSummary(turnId: string, signal?: AbortSignal): Promise<unknown> {
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
  interactionId: string,
  intentId?: string,
  sessionId?: string,
): Promise<ExecuteResult> {
  return apiClient.post<ExecuteResult>(`/api/turns/${encodeURIComponent(turnId)}/execute`, {
    authorization_token: authorizationToken,
    interaction_id: interactionId,
    intent_id: intentId,
    session_id: sessionId,
  });
}
