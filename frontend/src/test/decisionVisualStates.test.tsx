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
});
