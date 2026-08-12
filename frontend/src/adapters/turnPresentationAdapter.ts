import type { TurnPresentationResponse } from "../types/contract";
import { array, boolean, nonEmptyString, number, record, string, stringArray } from "./runtime";

function decision(value: unknown, path: string): void {
  string(value, path);
}

/** Validates the contract fields consumed by all current presentation regions. */
export function adaptTurnPresentation(raw: unknown): TurnPresentationResponse {
  const root = record(raw, "presentation");
  nonEmptyString(root.turn_id, "presentation.turn_id");
  string(root.created_at, "presentation.created_at");
  string(root.updated_at, "presentation.updated_at");
  string(root.current_stage, "presentation.current_stage");
  string(root.processing_status, "presentation.processing_status");

  const input = record(root.input, "presentation.input");
  string(input.input_type, "presentation.input.input_type");
  string(input.asr_raw_text, "presentation.input.asr_raw_text");
  string(input.normalized_text, "presentation.input.normalized_text");
  stringArray(input.zone_permission_reasons, "presentation.input.zone_permission_reasons");
  stringArray(input.preliminary_reasons, "presentation.input.preliminary_reasons");

  const semantic = record(root.semantic_frame, "presentation.semantic_frame");
  for (const key of ["frame_id", "turn_id", "raw_text", "normalized_text", "semantic_status"])
    string(semantic[key], `presentation.semantic_frame.${key}`);
  number(semantic.semantic_confidence, "presentation.semantic_frame.semantic_confidence");
  number(semantic.ambiguity_score, "presentation.semantic_frame.ambiguity_score");
  stringArray(semantic.security_signals, "presentation.semantic_frame.security_signals");
  array(semantic.intents, "presentation.semantic_frame.intents");

  const demand = record(root.evidence_demand, "presentation.evidence_demand");
  array(demand.intent_demands, "presentation.evidence_demand.intent_demands");
  const retrieval = record(root.retrieval_summary, "presentation.retrieval_summary");
  number(retrieval.candidate_count, "presentation.retrieval_summary.candidate_count");
  stringArray(retrieval.missing_types, "presentation.retrieval_summary.missing_types");
  array(retrieval.candidates, "presentation.retrieval_summary.candidates");
  array(retrieval.layers, "presentation.retrieval_summary.layers");
  number(retrieval.mandatory_recall_count, "presentation.retrieval_summary.mandatory_recall_count");

  const gate = record(root.gate_result, "presentation.gate_result");
  boolean(gate.blocked, "presentation.gate_result.blocked");
  array(gate.checks, "presentation.gate_result.checks");
  const score = record(root.score_result, "presentation.score_result");
  number(score.safety_score, "presentation.score_result.safety_score");
  const validation = record(root.validation_result, "presentation.validation_result");
  boolean(validation.jailbreak_flag, "presentation.validation_result.jailbreak_flag");
  number(validation.jailbreak_risk, "presentation.validation_result.jailbreak_risk");

  const result = record(root.decision_result, "presentation.decision_result");
  decision(result.initial_decision, "presentation.decision_result.initial_decision");
  decision(result.final_decision, "presentation.decision_result.final_decision");
  stringArray(result.reasons, "presentation.decision_result.reasons");
  boolean(result.review_required, "presentation.decision_result.review_required");
  boolean(result.execution_allowed, "presentation.decision_result.execution_allowed");
  record(root.review, "presentation.review");
  record(root.authorization, "presentation.authorization");
  record(root.execution, "presentation.execution");
  const audit = record(root.audit, "presentation.audit");
  if (audit.audit_id != null) string(audit.audit_id, "presentation.audit.audit_id");

  return { ...root, audit: { ...audit, audit_id: audit.audit_id ?? null } } as unknown as TurnPresentationResponse;
}
