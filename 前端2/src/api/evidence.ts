import { apiClient } from "./client";
import type { EvidenceNodeDetail, EvidenceSubgraph } from "../types/contract";

export function getTurnEvidence(turnId: string, signal?: AbortSignal): Promise<EvidenceSubgraph> {
  return apiClient.get<EvidenceSubgraph>(`/api/evidence/turn/${encodeURIComponent(turnId)}`, undefined, { signal, timeoutMs: 45_000 });
}

export function getEvidenceNode(turnId: string, nodeId: string, signal?: AbortSignal): Promise<EvidenceNodeDetail> {
  return apiClient.get<EvidenceNodeDetail>(
    `/api/turns/${encodeURIComponent(turnId)}/evidence/${encodeURIComponent(nodeId)}`,
    undefined,
    { signal },
  );
}

export function getCurrentEvidence<T = Record<string, unknown>>(): Promise<T> {
  return apiClient.get<T>("/api/evidence/current");
}
