import { MAX_CORRECTED_TEXT_LENGTH } from "../constants";
import type { ReviewAction, ReviewSubmission, ReviewSubmissionResponse, TurnWorkflowStatus } from "../types/contract";

export interface ReviewFormValues {
  selectedCandidateId: string;
  correctedText: string;
}

export interface SafeReviewResult {
  originalTurnId: string;
  reviewTurnId: string;
  action: ReviewAction;
  newDecision: string;
  tokenIssued: boolean;
  executionStatus: string;
  auditId: string;
  accepted: boolean;
  message: string;
  rootTurnId: string;
  relatedTurnId: string;
  reason: string;
  workflowStatus: TurnWorkflowStatus;
}

export type ReviewValidationResult =
  | { valid: true; request: ReviewSubmission }
  | { valid: false; message: string };

export function buildReviewSubmission(action: ReviewAction, values: ReviewFormValues): ReviewValidationResult {
  if (action === "CONFIRM") {
    const selectedCandidateId = values.selectedCandidateId.trim();
    return selectedCandidateId
      ? { valid: true, request: { action, selected_candidate_id: selectedCandidateId } }
      : { valid: false, message: "确认候选前必须选择一个有效候选" };
  }
  if (action === "CORRECT") {
    const correctedText = values.correctedText.trim();
    if (!correctedText) return { valid: false, message: "修正指令不能为空" };
    if (correctedText.length > MAX_CORRECTED_TEXT_LENGTH) {
      return { valid: false, message: `修正指令不能超过 ${MAX_CORRECTED_TEXT_LENGTH} 个字符` };
    }
    return { valid: true, request: { action, corrected_text: correctedText } };
  }
  return { valid: true, request: { action: "CANCEL" } };
}

export function toSafeReviewResult(response: ReviewSubmissionResponse): SafeReviewResult {
  return {
    originalTurnId: response.original_turn_id,
    reviewTurnId: response.review_turn_id,
    action: response.action,
    newDecision: response.new_decision,
    tokenIssued: response.token_issued,
    executionStatus: response.execution_status,
    auditId: response.audit_id,
    accepted: response.accepted,
    message: response.message,
    rootTurnId: response.root_turn_id,
    relatedTurnId: response.related_turn_id,
    reason: response.reason,
    workflowStatus: response.workflow_status,
  };
}

export function getReviewNavigation(result: SafeReviewResult, currentTurnId: string | null) {
  const turnId = result.relatedTurnId || result.reviewTurnId;
  return {
    turnId,
    path: `/review/${encodeURIComponent(turnId)}`,
    replace: true as const,
    changed: Boolean(turnId && turnId !== currentTurnId),
  };
}
