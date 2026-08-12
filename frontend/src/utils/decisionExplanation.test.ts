import { describe, expect, it } from "vitest";
import { decisionPromotionReason, evidenceAlignmentLabel } from "./decisionExplanation";

describe("decision explanation", () => {
  it("marks evidence alignment not applicable when no mandatory evidence exists", () => {
    expect(evidenceAlignmentLabel(0, "EVIDENCE_PASS")).toBe("不适用（本指令没有必查证据）");
  });

  it("names evidence alignment when it upgrades a score verdict", () => {
    expect(decisionPromotionReason({
      scoreDecision: "PASS",
      finalDecision: "REVIEW",
      gateBlocked: false,
      requiredEvidenceCount: 2,
      evidenceAlignmentRoute: "EVIDENCE_REVIEW",
      decisionSources: ["SAFETY_SCORE", "EVIDENCE_ALIGNMENT"],
    })).toContain("证据对齐将评分判断");
  });

  it("does not claim an upgrade when score and final verdict agree", () => {
    expect(decisionPromotionReason({
      scoreDecision: "PASS",
      finalDecision: "PASS",
      gateBlocked: false,
      requiredEvidenceCount: 0,
      evidenceAlignmentRoute: "EVIDENCE_PASS",
    })).toContain("没有额外模块提升等级");
  });
});
