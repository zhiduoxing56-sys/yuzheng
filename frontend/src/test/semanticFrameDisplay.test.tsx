// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { SemanticFrameDisplay } from "../components/DecisionVisuals";
import type { SemanticFrame } from "../types/contract";

afterEach(cleanup);

function frame(overrides: Partial<SemanticFrame> = {}): SemanticFrame {
  return {
    frame_id: "SEM_display_test",
    turn_id: "TURN_display_test",
    raw_text: "打开车门",
    normalized_text: "打开车门",
    semantic_confidence: 0.95,
    ambiguity_score: 0.05,
    semantic_status: "OK",
    review_reasons: [],
    review_candidates: [],
    unresolved_clauses: [],
    security_signals: [],
    intents: [{
      clause_index: 0,
      clause_text: "打开车门",
      intent_id: "DOOR_OPEN",
      action: "打开",
      target: "车门",
      area: "unknown",
      value: { source: "test", amount: 1 },
      control_domain: "车身控制",
      risk_level: "R3",
      risk_tags: ["车身开闭"],
      semantic_confidence: 0.95,
      ambiguity_score: 0.05,
    }],
    ...overrides,
  };
}

describe("SemanticFrameDisplay", () => {
  it.each(["OK", "REVIEW", "BLOCK"])("keeps the real intent visible for %s semantic status", (semanticStatus) => {
    render(<SemanticFrameDisplay frame={frame({ semantic_status: semanticStatus })} />);

    expect(screen.getByText(semanticStatus)).toBeTruthy();
    expect(screen.getByText("DOOR_OPEN")).toBeTruthy();
    expect(screen.getByText("打开")).toBeTruthy();
    expect(screen.getByText("车门")).toBeTruthy();
    expect(screen.getAllByText("打开车门")).toHaveLength(3);
    expect(screen.getByText("{\"source\":\"test\",\"amount\":1}")).toBeTruthy();
    expect(screen.getByText("车身开闭")).toBeTruthy();
    expect(screen.getByText("0")).toBeTruthy();
  });

  it("shows review reasons, candidates, unresolved clauses, and security signals without turning candidates into intents", () => {
    render(<SemanticFrameDisplay frame={frame({
      semantic_status: "REVIEW",
      review_reasons: ["ASR_REVIEW"],
      review_candidates: ["打开运动模式"],
      unresolved_clauses: ["打开运动魔石"],
      security_signals: ["SECURITY_SIGNAL"],
    })} />);

    expect(screen.getByText("ASR_REVIEW")).toBeTruthy();
    expect(screen.getByText("打开运动模式")).toBeTruthy();
    expect(screen.getByText("打开运动魔石")).toBeTruthy();
    expect(screen.getByText("SECURITY_SIGNAL")).toBeTruthy();
    expect(screen.getAllByText("DOOR_OPEN")).toHaveLength(1);
  });

  it("keeps top-level frame fields visible when there are no formal intents", () => {
    render(<SemanticFrameDisplay frame={frame({
      raw_text: "把那个打开",
      normalized_text: "把那个打开",
      semantic_status: "NO_MATCH",
      semantic_confidence: 0,
      ambiguity_score: 1,
      intents: [],
    })} />);

    expect(screen.getAllByText("把那个打开")).toHaveLength(2);
    expect(screen.getByText("NO_MATCH")).toBeTruthy();
    expect(screen.getByText("当前语义帧没有可展示的子意图")).toBeTruthy();
    expect(screen.queryByText("DOOR_OPEN")).toBeNull();
  });
});
