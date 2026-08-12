// @vitest-environment jsdom
import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { MemoryRouter } from "react-router-dom";
import type { AdaptedCommandResponse } from "../adapters/commandResponseAdapter";
import { DecisionResultPanel } from "../components/DecisionResultPanel";

const immediate: AdaptedCommandResponse = {
  turnId: "TURN_immediate",
  inputType: "text",
  instructionSummary: "帮我打开空调",
  summarySource: "用户原始输入" as AdaptedCommandResponse["summarySource"],
  action: "OPEN",
  target: "CLIMATE",
  preliminaryDecision: "PASS",
  safetyScore: 0.923,
  auditId: null,
  safeResponse: null,
};

afterEach(() => cleanup());

describe("immediate decision result", () => {
  it("shows the command result without waiting for presentation", () => {
    const view = render(<MemoryRouter><DecisionResultPanel data={null} immediate={immediate} loading error={null} onRetry={() => undefined} /></MemoryRouter>);
    for (const value of ["帮我打开空调", "OPEN", "CLIMATE", "TURN_immediate", "安全评分 0.923", "完整证据与审计信息加载中"]) {
      expect(view.queryByText(value)).not.toBeNull();
    }
  });

  it("keeps the immediate result visible when presentation fails", () => {
    const view = render(<MemoryRouter><DecisionResultPanel data={null} immediate={immediate} loading={false} error="presentation timeout" onRetry={() => undefined} /></MemoryRouter>);
    expect(view.queryByText("帮我打开空调")).not.toBeNull();
    expect(view.queryByText(/即时裁决结果已保留/)).not.toBeNull();
  });
});
