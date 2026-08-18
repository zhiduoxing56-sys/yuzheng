// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
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

  it("isolates the asynchronous explanation loading state inside the reason box", () => {
    const { container } = render(<DecisionResultDisplay result={result("reject")} explanation={{ status: "PENDING", text: null, retryable: false }} />);
    expect(screen.getByLabelText("具体原因生成中")).toBeTruthy();
    expect(container.querySelector(".decision-reason-spinner")).not.toBeNull();
    expect(screen.queryByText("正在生成")).toBeNull();
  });

  it("shows the generated explanation or a retry action without changing the decision", async () => {
    const retry = vi.fn();
    const view = render(<DecisionResultDisplay result={result("reject")} explanation={{ status: "FAILED", text: null, retryable: true }} onExplanationRetry={retry} />);
    await userEvent.click(screen.getByRole("button", { name: "重试" }));
    expect(retry).toHaveBeenCalledOnce();
    view.rerender(<DecisionResultDisplay result={result("reject")} explanation={{ status: "AVAILABLE", text: "车辆行驶中开启车门风险较高，因此本次指令被拒绝", retryable: false }} />);
    expect(screen.getByText("车辆行驶中开启车门风险较高，因此本次指令被拒绝")).toBeTruthy();
    expect(screen.getByRole("status").textContent).toContain("拒绝");
  });

  it("places the compact Bayesian risk row between basis and diagnostic score", async () => {
    const { container } = render(<DecisionResultDisplay
      result={{ ...result("reject"), dimensions: [{ id: "C_sem", dimension: "语义清晰度", detail: "0.9000" }] }}
      explanation={{ status: "AVAILABLE", text: "风险较高", retryable: false, facts: { key_runtime_state: { speed_kmh: 80 } } }}
      bayesian={{
        clause_index: 0,
        intent_id: "HEADLIGHT_SET_MODE",
        action: "设置",
        target: "前照灯",
        supported: true,
        profile_id: "HEADLIGHT_OFF",
        model_version: "display-noisy-or-v1",
        risk_probability: 0.833972,
        safe_probability: 0.166028,
        entropy: 0.648537,
        estimate_mode: "FULL_EVIDENCE",
        base_risk: 0.01,
        missing_evidence_types: [],
        evidence_inputs: [],
        factor_contributions: [
          { factor_id: "vehicle_speed", label: "车辆速度", risk_with_factor: 0.833972, risk_without_factor: 0.755841, contribution: 0.078131 },
          { factor_id: "low_light", label: "低照度", risk_with_factor: 0.833972, risk_without_factor: 0.335888, contribution: 0.498084 },
          { factor_id: "poor_visibility", label: "低能见度", risk_with_factor: 0.833972, risk_without_factor: 0.8317, contribution: 0.002272 },
        ],
        explanation: "全部配置因素均由本轮可用证据计算。",
      }}
    />);

    expect([...container.querySelectorAll("details > summary")].map((item) => item.textContent)).toEqual([
      "查看裁决依据",
      "贝叶斯风险",
      "诊断评分（不覆盖安全门）",
    ]);
    await userEvent.click(screen.getByText("贝叶斯风险"));
    const row = container.querySelector(".decision-bayesian-inline");
    expect(row?.textContent).toBe("贝叶斯风险概率 83.40%｜风险因素：低照度 49.81% · 车辆速度 7.81% · 低能见度 0.23%");
    expect(row?.textContent).not.toContain("安全概率");
    expect(row?.textContent).not.toContain("熵");
  });

  it("keeps the Bayesian row minimal when no data is available", async () => {
    const { container } = render(<DecisionResultDisplay result={result(null)} bayesian={null} />);
    await userEvent.click(screen.getByText("贝叶斯风险"));
    expect(container.querySelector(".decision-bayesian-inline")?.textContent).toBe("贝叶斯风险概率 --｜风险因素：--");
  });
});
