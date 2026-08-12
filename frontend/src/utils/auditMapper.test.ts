import { describe, expect, it } from "vitest";
import type { AuditDetailResponse, AuditVerificationResponse } from "../types/contract";
import { auditDecisionLabel, auditDecisionTone, auditVerificationPassed, collectAuditRelatedTurns, collectAuditSecurityAlerts } from "./auditMapper";

function detailFixture(): AuditDetailResponse {
  return {
    audit_id: "AUD_ROOT", turn_id: "TURN_ROOT", created_at: "2026-08-04T00:00:00Z",
    input_summary: { input_type: "text", input_source: "api", speaker_zone: "driver", speaker_role: "driver", input_trust_label: "TRUSTED", authorization_effect_applied: false, asr_raw_text: "打开车门", normalized_text: "打开车门", zone_permission_reasons: [], preliminary_reasons: [] },
    voice_trust: {}, transcription: { turn_id: "TURN_ROOT", text: "打开车门", adapter: "none", model_inference_performed: false, transcribed_text: "打开车门", confidence_token_count: 0, model_name: "none", inference_duration: 0, created_at: "2026-08-04T00:00:00Z" },
    semantic_frame: { frame_id: "F1", turn_id: "TURN_ROOT", raw_text: "打开车门", normalized_text: "打开车门", semantic_confidence: .9, ambiguity_score: .1, semantic_status: "OK", review_reasons: [], review_candidates: [], unresolved_clauses: [], security_signals: [], intents: [{ clause_index: 0, clause_text: "打开车门", intent_id: "DOOR_OPEN", action: "打开", target: "车门", area: "左侧", control_domain: "body", semantic_confidence: .9, ambiguity_score: .1, risk_level: "HIGH", risk_tags: [] }] },
    evidence_demand: { demand_id: "D1", turn_id: "TURN_ROOT", intent_demands: [{ intent_id: "DOOR_OPEN", clause_index: 0, action: "打开", target: "车门", area: "左侧", risk_level: "HIGH", query_text: "", required_types: [], optional_types: [], priority: 1, retrieval_scope: "runtime", demand_items: [{ evidence_type: "speed", required: true, status: "TAMPERED", node_ids: [], retrieval_origin: "NONE", reason: "hash mismatch" }] }] },
    retrieval_summary: { candidate_count: 0, candidates: [], layers: [], mandatory_recall_count: 0, mandatory_recall: [], missing_types: [], security_layer_count: 0, security_layers: [], per_layer_node_count: {}, unclassified_types: [], retrieval_visualization_path: [], final_top_k_node_ids: [], mandatory_supplemented_node_ids: [], internal_hnsw_trace_available: false, availability: "AVAILABLE" }, mandatory_recall: [], evidence_graph_summary: {}, quality_metrics: { availability: {} }, memory: {}, causal: {},
    validation_result: { grounding_failures: [], conflicts: [], jailbreak_flag: false, jailbreak_risk: 0 }, gate_result: { blocked: false, overall_status: "PASSED", checks: [] }, score_factors: { safety_score: .8 }, initial_decision: "PASS", original_decision: { audit_id: "AUD_ROOT", score_decision: "PASS", final_decision: "PASS", record_hash: "hash" }, effective_outcome: null,
    review_process: { status: "NOT_REQUIRED", original_instruction: "打开车门", candidate_interpretations: [], candidate_availability: "NO_VALID_CANDIDATES", supporting_evidence: [], conflicting_evidence: [] }, final_decision: { initial_decision: "PASS", score_decision: "PASS", final_decision: "PASS", decision_sources: [], decision_merge_reason: "score", safety_score: .8, reasons: [], explanation: "允许", review_required: false, execution_allowed: true },
    authorization_status: { token_issued: false, consumed: false, execution_allowed: false }, execution_status: { request_status: "NOT_REQUESTED", execution_status: "NOT_EXECUTED" },
    workflow_events: [{ event_id: "E1", root_turn_id: "TURN_ROOT", related_turn_id: "TURN_CHILD", parent_turn_id: "TURN_ROOT", sequence_no: 1, event_type: "REVIEW_CORRECTED", payload: {}, previous_event_hash: "", current_event_hash: "h", created_at: "2026-08-04T00:01:00Z" }], previous_hash: "", record_hash: "hash", audit_chain_valid: true, workflow_chain_valid: true,
  };
}

describe("auditMapper", () => {
  it("maps known and unknown decisions safely", () => {
    expect(auditDecisionLabel("PASS")).toBe("允许执行");
    expect(auditDecisionLabel("FUTURE")).toBe("FUTURE");
    expect(auditDecisionTone("FUTURE")).toBe("neutral");
  });

  it("extracts only real relation fields and real alerts", () => {
    const detail = detailFixture();
    expect(collectAuditRelatedTurns(detail).map((item) => item.turnId)).toEqual(["TURN_ROOT", "TURN_CHILD"]);
    expect(collectAuditSecurityAlerts(detail)).toEqual([{ key: "evidence-speed", title: "篡改证据", detail: "speed：hash mismatch" }]);
  });

  it("summarizes backend verification booleans without hashing", () => {
    const passed: AuditVerificationResponse = { audit_id: "A", record_hash_valid: true, previous_link_valid: true, audit_chain_valid: true, workflow_chain_valid: true, relationship_valid: true, merge_decision_valid: true, effective_outcome_valid: true };
    expect(auditVerificationPassed(passed)).toBe(true);
    expect(auditVerificationPassed({ ...passed, workflow_chain_valid: false })).toBe(false);
    expect(auditVerificationPassed(null)).toBe(null);
  });
});
