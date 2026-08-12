import { describe, expect, it } from "vitest";
import type { VehicleState } from "../types/contract";
import { relevantVehicleStateEntries, vehicleStateAvailabilityMessage } from "./vehicleStateMapper";

const state = {
  vehicle_speed: 30,
  gear_position: "D",
  door_state: "CLOSED",
  weather: "CLEAR",
  music_state: "STOPPED",
} as VehicleState;

describe("vehicle state relevance", () => {
  it("does not fill an air-conditioning command with unrelated state", () => {
    expect(relevantVehicleStateEntries(state, "空调")).toEqual([]);
    expect(vehicleStateAvailabilityMessage("空调")).toContain("空调状态未接入");
  });

  it("selects only state fields related to the current target", () => {
    expect(relevantVehicleStateEntries(state, "车门").map(([key]) => key)).toEqual([
      "vehicle_speed",
      "gear_position",
      "door_state",
    ]);
  });
});
