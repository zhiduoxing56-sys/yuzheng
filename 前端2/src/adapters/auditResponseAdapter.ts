import type { AuditDetailResponse, AuditVerificationResponse } from "../types/contract";
import { array, boolean, nonEmptyString, number, record, string } from "./runtime";

export interface AuditListViewItem {
  auditId: string; turnId: string; createdAt: string; instructionSummary: string;
  action: string; target: string; riskLevel: string; finalDecision: string; executionStatus: string;
}
export interface AuditListView { items: AuditListViewItem[]; total: number; page: number; pageSize: number; }

export function adaptAuditList(raw: unknown): AuditListView {
  const root = record(raw, "audits");
  const items = array(root.items, "audits.items");
  const adapted = items.map((value, index) => {
    const item = record(value, `audits.items[${index}]`);
    for (const key of ["audit_id", "turn_id", "created_at", "instruction_summary", "execution_status"])
      string(item[key], `audits.items[${index}].${key}`);
    const auditId = nonEmptyString(item.audit_id, `audits.items[${index}].audit_id`);
    if ("decision" in item) {
      for (const key of ["action", "target", "decision", "review_status", "authorization_status"])
        string(item[key], `audits.items[${index}].${key}`);
      record(item.integrity_summary, `audits.items[${index}].integrity_summary`);
      return {
        auditId,
        turnId: nonEmptyString(item.turn_id, `audits.items[${index}].turn_id`),
        createdAt: string(item.created_at, `audits.items[${index}].created_at`),
        instructionSummary: string(item.instruction_summary, `audits.items[${index}].instruction_summary`),
        action: string(item.action, `audits.items[${index}].action`),
        target: string(item.target, `audits.items[${index}].target`),
        riskLevel: "",
        finalDecision: string(item.decision, `audits.items[${index}].decision`),
        executionStatus: string(item.execution_status, `audits.items[${index}].execution_status`),
      };
    }
    const finalDecision = record(item.final_decision, `audits.items[${index}].final_decision`);
    string(finalDecision.final_decision, `audits.items[${index}].final_decision.final_decision`);
    const semantic = record(item.semantic_frame, `audits.items[${index}].semantic_frame`);
    const intents = array(semantic.intents, `audits.items[${index}].semantic_frame.intents`);
    const firstIntent = intents.length ? record(intents[0], `audits.items[${index}].semantic_frame.intents[0]`) : null;
    return {
      auditId,
      turnId: nonEmptyString(item.turn_id, `audits.items[${index}].turn_id`),
      createdAt: string(item.created_at, `audits.items[${index}].created_at`),
      instructionSummary: string(item.instruction_summary, `audits.items[${index}].instruction_summary`),
      action: firstIntent ? string(firstIntent.action, `audits.items[${index}].semantic_frame.intents[0].action`) : "",
      target: firstIntent ? string(firstIntent.target, `audits.items[${index}].semantic_frame.intents[0].target`) : "",
      riskLevel: firstIntent ? string(firstIntent.risk_level, `audits.items[${index}].semantic_frame.intents[0].risk_level`) : "",
      finalDecision: string(finalDecision.final_decision, `audits.items[${index}].final_decision.final_decision`),
      executionStatus: string(item.execution_status, `audits.items[${index}].execution_status`),
    };
  });
  return { items: adapted, total: number(root.total, "audits.total"), page: number(root.page, "audits.page"), pageSize: number(root.page_size, "audits.page_size") };
}

export function adaptAuditDetail(raw: unknown): AuditDetailResponse {
  const root = record(raw, "audit");
  for (const key of ["audit_id", "turn_id", "created_at", "previous_hash", "record_hash"]) string(root[key], `audit.${key}`);
  nonEmptyString(root.audit_id, "audit.audit_id");
  for (const key of ["input_summary", "transcription", "semantic_frame", "evidence_demand", "retrieval_summary", "quality_metrics", "validation_result", "gate_result", "score_factors", "original_decision", "review_process", "final_decision", "authorization_status", "execution_status"])
    record(root[key], `audit.${key}`);
  array(root.workflow_events, "audit.workflow_events");
  boolean(root.audit_chain_valid, "audit.audit_chain_valid");
  boolean(root.workflow_chain_valid, "audit.workflow_chain_valid");
  return raw as AuditDetailResponse;
}

export function adaptAuditVerification(raw: unknown): AuditVerificationResponse {
  const root = record(raw, "auditVerification");
  nonEmptyString(root.audit_id, "auditVerification.audit_id");
  for (const key of ["record_hash_valid", "previous_link_valid", "audit_chain_valid", "workflow_chain_valid", "relationship_valid", "merge_decision_valid", "effective_outcome_valid"])
    boolean(root[key], `auditVerification.${key}`);
  return raw as AuditVerificationResponse;
}

export interface GlobalAuditChainView { state: "valid" | "invalid" | "empty"; invalidCount: number; }

export function adaptGlobalAuditChain(raw: unknown): GlobalAuditChainView {
  const root = record(raw, "globalAuditChain");
  if ("valid" in root) return boolean(root.valid, "globalAuditChain.valid") ? { state: "valid", invalidCount: 0 } : { state: "invalid", invalidCount: 1 };
  const values = Object.entries(root);
  if (!values.length) return { state: "empty", invalidCount: 0 };
  const flags = values.map(([key, value]) => boolean(value, `globalAuditChain.${key}`));
  const invalidCount = flags.filter((value) => !value).length;
  return { state: invalidCount ? "invalid" : "valid", invalidCount };
}
