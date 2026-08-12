import { apiClient } from "./client";
import type { HealthResponse, IndexParametersRequest, IndexStatus, VehicleState } from "../types/contract";

export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiClient.get<HealthResponse>("/api/health", undefined, { signal });
}

/** Backend extension and maintenance endpoints, not frozen public contract paths. */
export function getVehicleState(signal?: AbortSignal): Promise<VehicleState> {
  return apiClient.get<VehicleState>("/api/state", undefined, { signal });
}

export function getIndexStatus(signal?: AbortSignal): Promise<IndexStatus> {
  return apiClient.get<IndexStatus>("/api/index/status", undefined, { signal });
}

export function updateIndexParameters(parameters: IndexParametersRequest): Promise<IndexStatus> {
  return apiClient.patch<IndexStatus>("/api/index/parameters", parameters, { timeoutMs: 120_000 });
}

export function rebuildIndex<T = Record<string, unknown>>(excludeTypes: string[] = []): Promise<T> {
  return apiClient.post<T>("/api/index/rebuild", { exclude_types: excludeTypes });
}

export function getCausalStatus<T = Record<string, unknown>>(): Promise<T> {
  return apiClient.get<T>("/api/causal/status");
}

export function rebuildCausal<T = Record<string, unknown>>(): Promise<T> {
  return apiClient.post<T>("/api/causal/rebuild");
}

export function getAuditLearningStatus<T = Record<string, unknown>>(): Promise<T> {
  return apiClient.get<T>("/api/audits/learning-status");
}

export function verifyAuditChain<T = { valid: boolean }>(): Promise<T> {
  return apiClient.get<T>("/api/audits/verify-chain");
}
