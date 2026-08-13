import { describe, expect, it } from "vitest";
import type { AuditVerificationResponse } from "../types/contract";
import { auditDecisionLabel, auditDecisionTone, auditVerificationPassed } from "./auditMapper";

describe("audit mapper", () => {
  it("maps public decision labels and tones", () => {
    expect(auditDecisionLabel("BLOCK")).toBe("安全阻断");
    expect(auditDecisionTone("PASS")).toBe("success");
    expect(auditDecisionTone("REVIEW")).toBe("warning");
  });

  it("keeps hash verification independent from AuditDetailView", () => {
    const verification: AuditVerificationResponse = {
      audit_id: "AUD",
      record_hash_valid: true,
      previous_link_valid: true,
      audit_chain_valid: true,
      workflow_chain_valid: true,
      terminal_audit_id: null,
      terminal_record_hash_valid: null,
      terminal_previous_link_valid: null,
      relationship_valid: true,
      merge_decision_valid: true,
      effective_outcome_valid: true,
      failure_reason: null,
    };
    expect(auditVerificationPassed(verification)).toBe(true);
  });
});
