import type { ReviewAction, ReviewSubmissionResponse } from "../types/contract";
import { boolean, nonEmptyString, record, string } from "./runtime";

export function adaptReviewResponse(raw: unknown): ReviewSubmissionResponse {
  const root = record(raw, "review");
  for (const key of ["original_turn_id", "review_turn_id", "root_turn_id", "related_turn_id", "message", "reason", "execution_status"])
    string(root[key], `review.${key}`);
  nonEmptyString(root.related_turn_id, "review.related_turn_id");
  const action = string(root.action, "review.action") as ReviewAction;
  if (!["CONFIRM", "CORRECT", "CANCEL"].includes(action)) throw new Error("响应结构异常：review.action");
  boolean(root.token_issued, "review.token_issued");
  boolean(root.accepted, "review.accepted");
  record(root.workflow_status, "review.workflow_status");
  const decision = record(root.decision, "review.decision");
  string(decision.final_decision, "review.decision.final_decision");
  if (decision.authorization_token != null) string(decision.authorization_token, "review.decision.authorization_token");
  return raw as ReviewSubmissionResponse;
}

