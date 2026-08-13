import { describe, expect, it } from "vitest";
import { adaptAuditDetail, adaptAuditList, adaptGlobalAuditChain } from "./auditResponseAdapter";
import { adaptAudioCommandResponse, adaptTextCommandResponse } from "./commandResponseAdapter";
import { ResponseShapeError } from "./runtime";
import { adaptTurnPresentation } from "./turnPresentationAdapter";
import { resolvePresentationOutcome } from "../hooks/useCommandSubmission";

function command(decision = "PASS") {
  return { turn_id: "TURN_test", decision: { final_decision: decision, safety_score: 0.9 }, semantic_frame: { intents: [{ action: "close", target: "reading_light" }] }, audit: {} };
}

function presentation(decision = "PASS", reviewStatus = "NOT_REQUIRED", candidates: unknown[] = [], auditId: unknown = "AUD_test") {
  const semantic = { frame_id: "F", turn_id: "TURN_test", raw_text: "关闭阅读灯", normalized_text: "关闭阅读灯", semantic_status: "OK", semantic_confidence: 0.9, ambiguity_score: 0.1, security_signals: [], intents: [{ clause_index: 0, action: "close", target: "reading_light", area: "cabin", risk_level: "LOW" }] };
  return {
    turn_id: "TURN_test", created_at: "2026-08-04T00:00:00Z", updated_at: "2026-08-04T00:00:01Z", current_stage: "COMPLETED", processing_status: "COMPLETED", voice_trust_mode: "enforce",
    input: { input_type: "text", asr_raw_text: "关闭阅读灯", normalized_text: "关闭阅读灯", zone_permission_reasons: [], preliminary_reasons: [] },
    semantic_frame: semantic,
    evidence_demand: { intent_demands: [] }, retrieval_summary: { candidate_count: 0, missing_types: [], candidates: [], layers: [], mandatory_recall_count: 0 },
    evidence: {}, gate_result: { blocked: decision === "BLOCK", checks: [] }, score_result: { safety_score: 0.9 },
    validation_result: { jailbreak_flag: false, jailbreak_risk: 0, conflicts: [], grounding_failures: [] },
    decision_result: { initial_decision: decision, score_decision: decision, final_decision: decision, reasons: [], review_required: decision === "REVIEW", execution_allowed: decision === "PASS" },
    review: { status: reviewStatus, candidate_interpretations: candidates }, authorization: {}, execution: {}, audit: auditId === undefined ? {} : { audit_id: auditId },
  };
}

function auditDetail() {
  return { command_summary: { raw_command: "测试", input_type: "text", occurred_at: "2026-08-04T00:00:00Z", final_decision: "PASS", execution_status: "NOT_EXECUTED" }, resolved_operations: [], decision_snapshot: null, decision_summary: { final_decision: "PASS", hit_rules: [], reason_codes: [], reasons: [] }, key_evidence: [], intent_decisions: [], llm_explanation: { status: "FAILED" }, clarification_history: [], authorization_summary: { status: "NOT_AUTHORIZED", authorized: false }, execution_summary: { status: "NOT_EXECUTED" }, execution_before_snapshot: null, execution_after_snapshot: null, execution_changes: [] };
}

describe("command response adapters", () => {
  it("preserves the user's original text and removes secrets", () => {
    const raw = { ...command(), authorization_token: "never-store" };
    const result = adaptTextCommandResponse(raw, "关闭阅读灯");
    expect(result.instructionSummary).toBe("关闭阅读灯");
    expect(result.safeResponse).not.toHaveProperty("authorization_token");
  });

  it("uses a real audio transcription", () => {
    const result = adaptAudioCommandResponse({ ...command("REVIEW"), input_type: "audio", semantic_frame: null, asr_result: { transcribed_text: "打开空调" } });
    expect(result.instructionSummary).toBe("打开空调");
    expect(result.summarySource).toBe("后端真实转写");
  });

  it("reports unknown structures instead of empty data", () => {
    expect(() => adaptTextCommandResponse({}, "测试")).toThrow(ResponseShapeError);
  });
});

describe("presentation adapter", () => {
  it.each([["PASS", "NOT_REQUIRED"], ["REVIEW", "REQUIRED"], ["BLOCK", "NOT_REQUIRED"], ["FUTURE_DECISION", "FUTURE_STATUS"]])("accepts decision/status %s", (decision, status) => {
    expect(adaptTurnPresentation(presentation(decision, status)).decision_result.final_decision).toBe(decision);
  });

  it("supports audio termination and a REVIEW without candidates", () => {
    const raw = presentation("REVIEW", "REQUIRED", []);
    raw.input.input_type = "audio";
    raw.current_stage = "VOICE_TERMINATED";
    expect(adaptTurnPresentation(raw).review.candidate_interpretations).toEqual([]);
  });

  it("normalizes a missing audit id to null", () => {
    const raw = presentation();
    delete (raw.audit as { audit_id?: unknown }).audit_id;
    expect(adaptTurnPresentation(raw).audit.audit_id).toBeNull();
  });

  it("enters partial after the finite presentation wait is exhausted", () => {
    expect(resolvePresentationOutcome("waiting_presentation", false, true, "未找到指定轮次")).toBe("partial");
    expect(resolvePresentationOutcome("partial", false, true, "未找到指定轮次")).toBeNull();
  });
});

describe("audit adapters", () => {
  it.each(["PASS", "BLOCK"])("adapts a %s human-readable audit row", (decision) => {
    const raw = { items: [{ audit_id: `AUD_${decision}`, created_at: "2026-08-04T00:00:00Z", raw_command: "测试", execution_status: "NOT_EXECUTED", final_decision: decision, review_occurred: false }], total: 1, page: 1, page_size: 20 };
    const item = adaptAuditList(raw).items[0];
    expect(item.rawCommand).toBe("测试");
    expect(item.finalDecision).toBe(decision);
  });

  it("accepts audit detail without optional outcome fields", () => {
    expect(adaptAuditDetail(auditDetail()).command_summary.raw_command).toBe("测试");
  });

  it("normalizes real validity and fixed boolean-map responses", () => {
    expect(adaptGlobalAuditChain({ valid: true }).state).toBe("valid");
    expect(adaptGlobalAuditChain({ AUD_a: true, AUD_b: false })).toEqual({ state: "invalid", invalidCount: 1 });
    expect(adaptGlobalAuditChain({})).toEqual({ state: "empty", invalidCount: 0 });
  });
});
