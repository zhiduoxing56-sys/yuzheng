// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { DecisionResultDisplay } from "../components/DecisionVisuals";
import type { DecisionResultView, DecisionVisualState } from "../types/visualModels";

afterEach(cleanup);

function result(state: DecisionVisualState | null): DecisionResultView {
  return { state, dimensions: [], score: null, reason: null };
}

describe("DecisionResultDisplay", () => {
  it("renders a neutral result without an icon when no decision data exists", () => {
    const { container } = render(<DecisionResultDisplay result={result(null)} />);
    const banner = screen.getByRole("status");
    expect(banner.textContent).toBe("--");
    expect(banner.querySelector("span")).toBeNull();
    expect(container.querySelector(".state-empty")).not.toBeNull();
  });

  it.each([
    ["pass", "通过", "✓", "state-pass"],
    ["review", "人工复核", "✓", "state-review"],
    ["reject", "拒绝", "×", "state-reject"],
  ] as const)("renders %s with its visual label and symbol", (state, label, symbol, className) => {
    const { container } = render(<DecisionResultDisplay result={result(state)} />);
    expect(screen.getByRole("status").textContent).toBe(`${symbol}${label}`);
    expect(container.querySelector(`.${className}`)).not.toBeNull();
    expect(container.querySelector("i")?.classList.contains("is-partial")).toBe(state === "review");
  });

  it("translates all primary decision values into Chinese", () => {
    render(<DecisionResultDisplay result={{
      ...result("review"), gateBlocked: false, evidenceAlignment: "EVIDENCE_REVIEW", scoreDecision: "PASS", finalDecision: "REVIEW",
      decisionSources: ["SAFETY_GATE", "EVIDENCE_ALIGNMENT", "SAFETY_SCORE"],
      mergeReason: "EVIDENCE_ALIGNMENT raised PASS to REVIEW",
    }} />);
    expect(screen.getByText("已通过")).toBeTruthy();
    expect(screen.getAllByText("需要人工复核")).toHaveLength(2);
    expect(screen.getByText("允许执行")).toBeTruthy();
    expect(screen.getByText("硬性安全门、证据对齐、安全评分")).toBeTruthy();
    expect(screen.getByText("证据对齐 raised 允许执行 to 需要人工复核")).toBeTruthy();
    expect(screen.queryByText("SAFETY_GATE")).toBeNull();
  });

  it("translates the aggregate merge reason into a complete Chinese sentence", () => {
    render(<DecisionResultDisplay result={{ ...result("reject"), mergeReason: "Intent safety aggregate=BLOCK; top-level score is conservative projection from 2 occurrence assessments" }} />);
    expect(screen.getByText("各意图安全评价汇总为拒绝执行；顶层评分采用 2 个意图评价的保守投影")).toBeTruthy();
  });
});
