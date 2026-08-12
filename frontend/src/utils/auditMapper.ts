import type { AuditDetailResponse, AuditVerificationResponse, DecisionLabel, WorkflowEvent } from "../types/contract";
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

export interface AuditSecurityAlert {
  key: string;
  title: string;
  detail: string;
}

export function collectAuditSecurityAlerts(detail: AuditDetailResponse): AuditSecurityAlert[] {
  const alerts: AuditSecurityAlert[] = [];
  if (detail.validation_result.jailbreak_flag) alerts.push({ key: "jailbreak", title: "提示注入风险", detail: `后端风险值：${detail.validation_result.jailbreak_risk}` });
  detail.validation_result.conflicts.forEach((item, index) => alerts.push({ key: `conflict-${index}`, title: "多源状态冲突", detail: typeof item === "string" ? item : "后端返回结构化冲突记录" }));
  detail.validation_result.grounding_failures.forEach((item, index) => alerts.push({ key: `grounding-${index}`, title: "可信输入或证据落地异常", detail: typeof item === "string" ? item : "后端返回结构化异常记录" }));
  detail.evidence_demand.intent_demands.flatMap((intent) => intent.demand_items).filter((item) => item.status === "TAMPERED" || item.status === "CONFLICT").forEach((item) => alerts.push({ key: `evidence-${item.evidence_type}`, title: item.status === "TAMPERED" ? "篡改证据" : "证据冲突", detail: `${item.evidence_type}：${item.reason}` }));
  detail.gate_result.checks.filter((item) => item.hit && item.severity !== "INFO").forEach((item) => alerts.push({ key: `gate-${item.rule_id}`, title: item.rule_name, detail: item.reason }));
  return alerts;
}

export interface AuditRelatedTurn {
  turnId: string;
  roles: string[];
}

function addRole(map: Map<string, Set<string>>, turnId: string | null | undefined, role: string) {
  if (!turnId) return;
  const roles = map.get(turnId) || new Set<string>();
  roles.add(role);
  map.set(turnId, roles);
}

export function collectAuditRelatedTurns(detail: AuditDetailResponse): AuditRelatedTurn[] {
  const related = new Map<string, Set<string>>();
  addRole(related, detail.turn_id, "当前审计轮次");
  detail.workflow_events.forEach((event) => {
    addRole(related, event.root_turn_id, "根轮次");
    addRole(related, event.parent_turn_id, "父轮次");
    addRole(related, event.related_turn_id, event.related_turn_id === detail.turn_id ? "当前轮次" : "关联或子轮次");
  });
  if (detail.review_process.review_turn_id) addRole(related, detail.review_process.review_turn_id, "复核轮次");
  return [...related.entries()].map(([turnId, roles]) => ({ turnId, roles: [...roles] }));
}

export function auditEventSummary(event: WorkflowEvent): string {
  const payload = event.payload;
  for (const key of ["summary", "reason", "status", "message"]) {
    if (typeof payload[key] === "string" && payload[key]) return payload[key] as string;
  }
  return `${event.event_type} 工作流事件`;
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
