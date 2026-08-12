import { describe, expect, it } from "vitest";
import type { AdaptedCommandResponse } from "../adapters/commandResponseAdapter";
import type { PipelineEvent, TurnPresentationResponse } from "../types/contract";
import {
  acceptModelFinalResult,
  acceptModelSubmission,
  addModelEvent,
  beginModelSession,
  beginModelSubmission,
  createDecisionPageStateModel,
} from "./decisionPageStateModel";
import { safeDecisionDiagnostic } from "./safeDecisionDiagnostics";

function immediate(turnId: string): AdaptedCommandResponse {
  return { turnId, inputType: "text", instructionSummary: "帮我打开空调", summarySource: "用户原始输入" as AdaptedCommandResponse["summarySource"], action: "OPEN", target: "CLIMATE", preliminaryDecision: "PASS", safetyScore: 0.92, auditId: null, safeResponse: null };
}

function finalResult(turnId: string): TurnPresentationResponse {
  return { turn_id: turnId } as TurnPresentationResponse;
}

function event(turnId: string, sequence: number): PipelineEvent {
  return { event_id: `${turnId}-${sequence}`, session_id: "session-12345678", turn_id: turnId, sequence, event_type: "pipeline", stage: "INPUT_RECEIVED", status: "COMPLETED", timestamp: "2026-08-04T00:00:00Z", duration_ms: 1, summary: "safe", payload: {} };
}

describe("decision page expected ownership model (test-only)", () => {
  it("increments sessionEpoch and submissionGeneration when a session is replaced", () => {
    const next = beginModelSession(createDecisionPageStateModel());
    expect(next.sessionEpoch).toBe(1);
    expect(next.submissionGeneration).toBe(1);
    expect(next.activeTurnId).toBeNull();
  });

  it("keeps the previous final result while a new submission is awaiting its own result", () => {
    const first = acceptModelFinalResult(acceptModelSubmission(beginModelSubmission(createDecisionPageStateModel()), immediate("TURN_A")), finalResult("TURN_A"));
    const next = beginModelSubmission(first);
    expect(next.previousFinalResult?.turn_id).toBe("TURN_A");
    expect(next.finalResult).toBeNull();
  });

  it("rejects a final result that does not belong to expectedTurnId", () => {
    const state = acceptModelSubmission(beginModelSubmission(createDecisionPageStateModel()), immediate("TURN_B"));
    expect(acceptModelFinalResult(state, finalResult("TURN_A"))).toBe(state);
  });

  it("owns realtime events by turn and ignores events at or below the submission baseline", () => {
    let state = addModelEvent(createDecisionPageStateModel(), event("TURN_A", 4));
    state = beginModelSubmission(state);
    state = addModelEvent(state, event("TURN_A", 3));
    state = addModelEvent(state, event("TURN_B", 5));
    expect(state.eventsByTurn.TURN_A).toHaveLength(1);
    expect(state.eventsByTurn.TURN_B.map((item) => item.sequence)).toEqual([5]);
  });

  it("safe diagnostics only emits the allowlisted fields", () => {
    const emitted: unknown[] = [];
    const input = { sessionId: "12345678-secret-session", submissionGeneration: 3, turnId: "TURN_B", sequence: 9, stage: "SEMANTIC_PARSED", status: "COMPLETED", lifecycle: "request_discard", discardReason: "turn_mismatch", authorizationToken: "must-not-leak", rawAudio: "must-not-leak" } as const;
    const entry = safeDecisionDiagnostic(input, (value) => emitted.push(value));
    expect(entry).toEqual({ sessionIdPrefix: "12345678", submissionGeneration: 3, turnId: "TURN_B", sequence: 9, stage: "SEMANTIC_PARSED", status: "COMPLETED", lifecycle: "request_discard", discardReason: "turn_mismatch" });
    expect(JSON.stringify(emitted)).not.toContain("must-not-leak");
  });
});
