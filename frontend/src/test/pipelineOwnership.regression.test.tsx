// @vitest-environment jsdom
import { act, cleanup, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { SessionProvider, useSession } from "../stores/sessionStore";
import type { PipelineEvent } from "../types/contract";
import { buildPipelineStageViews } from "../utils/pipelineStageMapper";

function event(turnId: string, sequence: number, stage: string, status = "COMPLETED", payload: Record<string, unknown> = {}): PipelineEvent {
  return {
    event_id: `${turnId}-${sequence}-${stage}`,
    session_id: "session-12345678",
    turn_id: turnId,
    sequence,
    event_type: "pipeline",
    stage,
    status,
    timestamp: `2026-08-04T00:00:${String(sequence).padStart(2, "0")}Z`,
    duration_ms: 1,
    summary: `${turnId}:${stage}`,
    payload,
  };
}

function wrapper({ children }: { children: ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}

beforeEach(() => { localStorage.clear(); sessionStorage.clear(); });
afterEach(() => cleanup());

describe("pipeline ownership and stage regressions", () => {
  it("6. a new submission starts with every stage reset to waiting", () => {
    const { result } = renderHook(() => useSession(), { wrapper });
    act(() => {
      result.current.addPipelineEvent(event("TURN_A", 1, "INPUT_RECEIVED"));
      result.current.addPipelineEvent(event("TURN_A", 2, "SEMANTIC_PARSED"));
      result.current.addPipelineEvent(event("TURN_A", 3, "DECISION_COMPLETED"));
    });
    const stagesAtNewSubmission = buildPipelineStageViews(result.current.getPipelineEvents("TURN_B"), false);
    expect(stagesAtNewSubmission.every((stage) => stage.status === "waiting")).toBe(true);
  });

  it("7. TURN_A late events are not exposed as TURN_B events", () => {
    const { result } = renderHook(() => useSession(), { wrapper });
    act(() => result.current.addPipelineEvent(event("TURN_A", 8, "DECISION_COMPLETED")));
    expect(result.current.getPipelineEvents("TURN_B")).toEqual([]);
    expect(result.current.getPipelineEvents("TURN_A").map((item) => item.turn_id)).toEqual(["TURN_A"]);
  });

  it("8. REVIEW_REQUIRED maps to waiting review instead of completed", () => {
    const review = buildPipelineStageViews([event("TURN_A", 4, "REVIEW_REQUIRED")], false).find((stage) => stage.key === "review");
    expect(review?.status).toBe("review");
  });

  it("9. AUDIT_SAVED represents archive only and does not complete vehicle execution", () => {
    const execution = buildPipelineStageViews([event("TURN_A", 5, "AUDIT_SAVED")], false).find((stage) => stage.key === "execution");
    expect(execution?.status).toBe("waiting");
  });

  it("10. execution remains waiting until VEHICLE_EXECUTED or EXECUTION_SUCCEEDED", () => {
    const execution = buildPipelineStageViews([
      event("TURN_A", 5, "VEHICLE_PRECHECKED"),
      event("TURN_A", 6, "TOKEN_CONSUMED"),
    ], false).find((stage) => stage.key === "execution");
    expect(execution?.status).toBe("waiting");
  });

  it("14. four consecutive turns keep independent event collections", () => {
    const { result } = renderHook(() => useSession(), { wrapper });
    ["TURN_A", "TURN_B", "TURN_C", "TURN_D"].forEach((turnId, index) => {
      act(() => result.current.addPipelineEvent(event(turnId, index + 1, "INPUT_RECEIVED")));
    });
    expect(Object.keys(result.current.eventsByTurn).sort()).toEqual(["TURN_A", "TURN_B", "TURN_C", "TURN_D"]);
    for (const turnId of ["TURN_A", "TURN_B", "TURN_C", "TURN_D"]) {
      expect(result.current.getPipelineEvents(turnId).every((item) => item.turn_id === turnId)).toBe(true);
    }
  });
});
