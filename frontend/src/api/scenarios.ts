import { apiClient } from "./client";
import type { ScenarioSummary, TextCommandResponse, VehicleState } from "../types/contract";

/** Backend extension endpoints for the demonstration console. */
export function listScenarios(): Promise<ScenarioSummary[]> {
  return apiClient.get<ScenarioSummary[]>("/api/scenarios");
}

export function loadScenario(scenarioId: string): Promise<VehicleState> {
  return apiClient.post<VehicleState>(`/api/scenarios/${encodeURIComponent(scenarioId)}/load`);
}

export function runScenario(scenarioId: string, sessionId?: string): Promise<TextCommandResponse> {
  return apiClient.post<TextCommandResponse>(
    `/api/scenarios/${encodeURIComponent(scenarioId)}/run`,
    undefined,
    { query: { session_id: sessionId } },
  );
}
