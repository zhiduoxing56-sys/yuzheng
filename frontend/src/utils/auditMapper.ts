import type { AuditVerificationResponse, DecisionLabel } from "../types/contract";
import { decisionLabel, reviewActionLabel } from "./formatters";

export function auditDecisionLabel(value?: string | null): string {
  return decisionLabel(value);
}

export function auditDecisionTone(value?: string | null): "success" | "warning" | "danger" | "neutral" {
  if (value === "PASS") return "success";
  if (value === "REVIEW") return "warning";
  if (value === "BLOCK") return "danger";
  return "neutral";
}

export function auditReviewActionLabel(value?: string | null): string {
  return reviewActionLabel(value);
}

export function booleanLabel(value?: boolean | null, yes = "是", no = "否"): string {
  return value === true ? yes : value === false ? no : "暂无数据";
}

export function auditVerificationPassed(data: AuditVerificationResponse | null): boolean | null {
  if (!data) return null;
  const required = [data.record_hash_valid, data.previous_link_valid, data.audit_chain_valid, data.workflow_chain_valid, data.relationship_valid, data.merge_decision_valid, data.effective_outcome_valid];
  const terminal = [data.terminal_record_hash_valid, data.terminal_previous_link_valid].filter((value): value is boolean => typeof value === "boolean");
  return [...required, ...terminal].every(Boolean);
}

export function asDecisionLabel(value: string): DecisionLabel | null {
  return value === "PASS" || value === "REVIEW" || value === "BLOCK" ? value : null;
}
