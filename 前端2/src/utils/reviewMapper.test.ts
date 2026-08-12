import { describe, expect, it, vi } from "vitest";
import type { ReviewSubmissionResponse } from "../types/contract";
import { buildReviewSubmission, getReviewNavigation, toSafeReviewResult } from "./reviewMapper";

describe("reviewMapper", () => {
  it("构造只有 action 和 selected_candidate_id 的 CONFIRM 请求", () => {
    const result = buildReviewSubmission("CONFIRM", { selectedCandidateId: " CAND_1 ", correctedText: "不应发送" });
    expect(result).toEqual({ valid: true, request: { action: "CONFIRM", selected_candidate_id: "CAND_1" } });
    if (result.valid) expect(Object.keys(result.request).sort()).toEqual(["action", "selected_candidate_id"]);
  });

  it("构造只有 action 和 trimmed corrected_text 的 CORRECT 请求", () => {
    const result = buildReviewSubmission("CORRECT", { selectedCandidateId: "不应发送", correctedText: "  打开左侧车窗  " });
    expect(result).toEqual({ valid: true, request: { action: "CORRECT", corrected_text: "打开左侧车窗" } });
    if (result.valid) expect(Object.keys(result.request).sort()).toEqual(["action", "corrected_text"]);
  });

  it("构造不带额外字段的 CANCEL 请求", () => {
    const result = buildReviewSubmission("CANCEL", { selectedCandidateId: "不应发送", correctedText: "不应发送" });
    expect(result).toEqual({ valid: true, request: { action: "CANCEL" } });
  });

  it("拒绝未选择候选、空修正和超过后端限制的文本", () => {
    expect(buildReviewSubmission("CONFIRM", { selectedCandidateId: " ", correctedText: "" }).valid).toBe(false);
    expect(buildReviewSubmission("CORRECT", { selectedCandidateId: "", correctedText: " \n " }).valid).toBe(false);
    expect(buildReviewSubmission("CORRECT", { selectedCandidateId: "", correctedText: "x".repeat(2049) }).valid).toBe(false);
    expect(buildReviewSubmission("CORRECT", { selectedCandidateId: "", correctedText: "x".repeat(2048) }).valid).toBe(true);
  });

  it("安全结果不包含原始令牌，也不写日志", () => {
    const rawToken = "secret-token-that-must-never-leak";
    const debug = vi.spyOn(console, "debug").mockImplementation(() => undefined);
    const response = {
      original_turn_id: "TURN_PARENT", review_turn_id: "TURN_CHILD", user_action: "CORRECT", new_decision: "PASS",
      token_issued: true, execution_status: "AUTHORIZED", audit_id: "AUDIT_1", accepted: true, message: "ok",
      root_turn_id: "TURN_PARENT", related_turn_id: "TURN_CHILD", action: "CORRECT", reason: "ok",
      workflow_status: { root_turn_id: "TURN_PARENT", current_turn_id: "TURN_CHILD", status: "AUTHORIZED", review_attempts: 1, max_review_attempts: 3, latest_decision: "PASS", token_status: "ISSUED", event_count: 5, terminal: false },
      decision: { authorization_token: rawToken }, command_result: { decision: { authorization_token: rawToken } },
    } as unknown as ReviewSubmissionResponse;
    const safe = toSafeReviewResult(response);
    expect(JSON.stringify(safe)).not.toContain(rawToken);
    expect(safe).not.toHaveProperty("authorizationToken");
    expect(debug).not.toHaveBeenCalled();
    debug.mockRestore();
  });

  it("新子轮次使用 replace 路由", () => {
    const result = { relatedTurnId: "TURN_CHILD", reviewTurnId: "TURN_CHILD" } as ReturnType<typeof toSafeReviewResult>;
    expect(getReviewNavigation(result, "TURN_PARENT")).toEqual({ turnId: "TURN_CHILD", path: "/review/TURN_CHILD", replace: true, changed: true });
  });
});
