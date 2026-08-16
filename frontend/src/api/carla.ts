import { apiClient } from "./client";
import type { EvidenceObservationInput, VehicleState, VehicleStatePatch } from "../types/contract";

/** 直接修改云服务器 CARLA 车辆状态(控制面板用)。 */
export function patchVehicleState(patch: VehicleStatePatch): Promise<VehicleState> {
  return apiClient.patch<VehicleState>("/api/state", patch, { timeoutMs: 30_000 });
}

/** 复位云服务器 CARLA 车辆状态。 */
export function resetVehicleState(): Promise<VehicleState> {
  return apiClient.post<VehicleState>("/api/state/reset", undefined, { timeoutMs: 30_000 });
}

export function getSimulationContext(): Promise<EvidenceObservationInput[]> {
  return apiClient.get<EvidenceObservationInput[]>("/api/state/simulation-context");
}

export function replaceSimulationContext(
  observations: EvidenceObservationInput[],
): Promise<EvidenceObservationInput[]> {
  return apiClient.put<EvidenceObservationInput[]>("/api/state/simulation-context", observations);
}

export interface CarlaObstacleResult {
  ok: boolean;
  obstacle_count?: number;
  cleared?: number;
}

/** 在自车前方生成障碍物(pedestrian 行人 / vehicle 车辆 / obstacle 静态物)。 */
export function spawnObstacle(type: "pedestrian" | "vehicle" | "obstacle"): Promise<CarlaObstacleResult> {
  return apiClient.post<CarlaObstacleResult>("/api/carla/obstacle", { type }, { timeoutMs: 30_000 });
}

/** 清除全部已生成的障碍物。 */
export function clearObstacles(): Promise<CarlaObstacleResult> {
  return apiClient.post<CarlaObstacleResult>("/api/carla/obstacle/clear", undefined, { timeoutMs: 30_000 });
}

/** 设置离自车最近的交通灯状态(RED / GREEN / YELLOW)。 */
export function setTrafficLight(state: "RED" | "GREEN" | "YELLOW"): Promise<{ ok: boolean }> {
  return apiClient.post<{ ok: boolean }>("/api/carla/traffic-light", { state }, { timeoutMs: 30_000 });
}
