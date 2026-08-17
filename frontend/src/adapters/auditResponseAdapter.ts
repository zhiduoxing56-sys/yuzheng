import type { AuditDetailView, AuditVerificationResponse } from "../types/contract";
import { array, boolean, nonEmptyString, number, record, string } from "./runtime";

export interface AuditListViewItem {
  auditId: string; createdAt: string; rawCommand: string; finalDecision: string; executionStatus: string; reviewOccurred: boolean;
}
export interface AuditListView { items: AuditListViewItem[]; total: number; page: number; pageSize: number; }

export function adaptAuditList(raw: unknown): AuditListView {
  const root = record(raw, "audits");
  const items = array(root.items, "audits.items");
  const adapted = items.map((value, index) => {
    const item = record(value, `audits.items[${index}]`);
    for (const key of ["audit_id", "created_at", "raw_command", "final_decision", "execution_status"])
      string(item[key], `audits.items[${index}].${key}`);
    const auditId = nonEmptyString(item.audit_id, `audits.items[${index}].audit_id`);
    return {
      auditId,
      createdAt: string(item.created_at, `audits.items[${index}].created_at`),
      rawCommand: string(item.raw_command, `audits.items[${index}].raw_command`),
      finalDecision: string(item.final_decision, `audits.items[${index}].final_decision`),
      executionStatus: string(item.execution_status, `audits.items[${index}].execution_status`),
      reviewOccurred: boolean(item.review_occurred, `audits.items[${index}].review_occurred`),
    };
  });
  return { items: adapted, total: number(root.total, "audits.total"), page: number(root.page, "audits.page"), pageSize: number(root.page_size, "audits.page_size") };
}

export function adaptAuditDetail(raw: unknown): AuditDetailView {
  const root = record(raw, "audit");
  for (const key of ["command_summary", "decision_summary", "llm_explanation", "authorization_summary", "execution_summary"])
    record(root[key], `audit.${key}`);
  for (const key of ["resolved_operations", "key_evidence", "intent_decisions", "clarification_history", "execution_changes"])
    array(root[key], `audit.${key}`);
  return raw as AuditDetailView;
}

export function adaptAuditVerification(raw: unknown): AuditVerificationResponse {
  const root = record(raw, "auditVerification");
  nonEmptyString(root.audit_id, "auditVerification.audit_id");
  for (const key of ["record_hash_valid", "previous_link_valid", "audit_chain_valid", "workflow_chain_valid", "relationship_valid", "merge_decision_valid", "effective_outcome_valid"])
    boolean(root[key], `auditVerification.${key}`);
  return raw as AuditVerificationResponse;
}

export interface GlobalAuditChainView {
  state: "valid" | "invalid" | "empty";
  invalidCount: number;
  totalRecords: number;
  legacyUnsignedRecords: number;
  signatureProtectedRecords: number;
  signatureVerifiedRecords: number;
  hashChainStatus: string;
  signatureStatus: string;
  firstAnomaly: { auditId: string; type: string; message: string } | null;
}

export function adaptGlobalAuditChain(raw: unknown): GlobalAuditChainView {
  const root = record(raw, "globalAuditChain");
  if ("valid" in root) {
    const valid = boolean(root.valid, "globalAuditChain.valid");
    const count = (value: unknown) => typeof value === "number" ? value : 0;
    const anomaly = record(root.first_anomaly ?? {}, "globalAuditChain.first_anomaly");
    return {
      state: valid ? "valid" : "invalid",
      invalidCount: count(root.anomaly_count) || (valid ? 0 : 1),
      totalRecords: count(root.total_records),
      legacyUnsignedRecords: count(root.legacy_unsigned_records),
      signatureProtectedRecords: count(root.signature_protected_records),
      signatureVerifiedRecords: count(root.signature_verified_records),
      hashChainStatus: typeof root.hash_chain_status === "string" ? root.hash_chain_status : "NOT_CHECKED",
      signatureStatus: typeof root.signature_status === "string" ? root.signature_status : "NOT_ENABLED",
      firstAnomaly: typeof anomaly.audit_id === "string" && typeof anomaly.anomaly_type === "string" && typeof anomaly.message === "string"
        ? { auditId: anomaly.audit_id, type: anomaly.anomaly_type, message: anomaly.message } : null,
    };
  }
  const values = Object.entries(root);
  if (!values.length) return { state: "empty", invalidCount: 0, totalRecords: 0, legacyUnsignedRecords: 0, signatureProtectedRecords: 0, signatureVerifiedRecords: 0, hashChainStatus: "NOT_CHECKED", signatureStatus: "NOT_ENABLED", firstAnomaly: null };
  const flags = values.map(([key, value]) => boolean(value, `globalAuditChain.${key}`));
  const invalidCount = flags.filter((value) => !value).length;
  return { state: invalidCount ? "invalid" : "valid", invalidCount, totalRecords: 0, legacyUnsignedRecords: 0, signatureProtectedRecords: 0, signatureVerifiedRecords: 0, hashChainStatus: "NOT_CHECKED", signatureStatus: "NOT_ENABLED", firstAnomaly: null };
}
