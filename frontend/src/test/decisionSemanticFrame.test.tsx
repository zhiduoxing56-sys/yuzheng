// @vitest-environment jsdom

import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, useLocation } from "react-router-dom";
import { submitTextCommand } from "../api/command";
import { getTurnPresentation } from "../api/turns";
import { VisualPageNav } from "../components/VisualPageNav";
import { DecisionPage } from "../pages/DecisionPage";
import type { EvidenceDemandPresentation, SemanticFrame, TextCommandResponse, TurnPresentationResponse } from "../types/contract";

vi.mock("../api/command", () => ({ submitTextCommand: vi.fn() }));
vi.mock("../api/turns", () => ({ getTurnPresentation: vi.fn() }));

const semanticFrame: SemanticFrame = {
  frame_id: "SEM_test",
  turn_id: "TURN_test",
  raw_text: "打开左前车窗，然后打开右后车窗",
  normalized_text: "打开左前车窗，然后打开右后车窗",
  semantic_confidence: 0.94,
  ambiguity_score: 0.06,
  semantic_status: "OK",
  review_reasons: [],
  review_candidates: [],
  unresolved_clauses: [],
  security_signals: ["MULTI_INTENT"],
  intents: [
    {
      clause_index: 0,
      clause_text: "打开左前车窗",
      intent_id: "WINDOW_OPEN",
      action: "OPEN",
      target: "WINDOW",
      area: "FRONT_LEFT",
      value: { percent: 50 },
      control_domain: "BODY",
      risk_level: "R1",
      risk_tags: [],
      semantic_confidence: 0.95,
      ambiguity_score: 0.05,
    },
    {
      clause_index: 1,
      clause_text: "打开右后车窗",
      intent_id: "WINDOW_OPEN",
      action: "OPEN",
      target: "WINDOW",
      area: "REAR_RIGHT",
      value: true,
      control_domain: "BODY",
      risk_level: "R1",
      risk_tags: ["OCCURRENCE_TEST"],
      semantic_confidence: 0.93,
      ambiguity_score: 0.07,
    },
  ],
};

const evidenceDemand: EvidenceDemandPresentation = {
  demand_id: "DEM_test",
  turn_id: "TURN_test",
  intent_demands: [],
};

function LocationProbe() {
  return <output data-testid="location">{useLocation().search}</output>;
}

function commandResponse(finalDecision: "PASS" | "REVIEW" | "BLOCK" = "PASS"): TextCommandResponse {
  return {
    turn_id: "TURN_test",
    semantic_frame: semanticFrame,
    evidence_demand: evidenceDemand,
    decision: { final_decision: finalDecision },
  } as unknown as TextCommandResponse;
}

beforeEach(() => {
  vi.mocked(submitTextCommand).mockReset();
  vi.mocked(getTurnPresentation).mockReset();
});

afterEach(cleanup);

describe("DecisionPage semantic-frame connection", () => {
  it("submits only text, preserves duplicate intent occurrences, and writes turn_id to the URL", async () => {
    vi.mocked(submitTextCommand).mockResolvedValue(commandResponse());
    render(<MemoryRouter initialEntries={["/decision"]}><DecisionPage /><LocationProbe /></MemoryRouter>);

    await userEvent.type(screen.getByLabelText("文本指令"), semanticFrame.raw_text);
    await userEvent.click(screen.getByRole("button", { name: "提交/上传" }));

    await waitFor(() => expect(submitTextCommand).toHaveBeenCalledTimes(1));
    expect(submitTextCommand).toHaveBeenCalledWith({ text: semanticFrame.raw_text }, expect.any(AbortSignal));
    await waitFor(() => expect(screen.getByTestId("location").textContent).toBe("?turn_id=TURN_test"));

    const cards = document.querySelectorAll(".semantic-intent-card");
    expect(cards).toHaveLength(2);
    expect(within(cards[0] as HTMLElement).getByText("FRONT_LEFT")).toBeTruthy();
    expect(within(cards[1] as HTMLElement).getByText("REAR_RIGHT")).toBeTruthy();
    expect(screen.getAllByText("WINDOW_OPEN")).toHaveLength(2);
    expect(screen.getByText('{"percent":50}')).toBeTruthy();
    expect(screen.getByText("true")).toBeTruthy();
    expect(screen.queryByText("通过")).toBeNull();
  });

  it("restores the semantic frame from turn_id without submitting a command", async () => {
    vi.mocked(getTurnPresentation).mockResolvedValue({
      turn_id: "TURN_test",
      semantic_frame: semanticFrame,
      evidence_demand: evidenceDemand,
    } as TurnPresentationResponse);

    render(<MemoryRouter initialEntries={["/decision?turn_id=TURN_test"]}><DecisionPage /></MemoryRouter>);

    await waitFor(() => expect(getTurnPresentation).toHaveBeenCalledWith("TURN_test", expect.any(AbortSignal)));
    await waitFor(() => expect(screen.getAllByText("WINDOW_OPEN")).toHaveLength(2));
    expect((screen.getByLabelText("文本指令") as HTMLTextAreaElement).value).toBe(semanticFrame.raw_text);
    expect(submitTextCommand).not.toHaveBeenCalled();
  });

  it.each(["PASS", "REVIEW", "BLOCK"] as const)("does not alter the semantic frame for a %s command decision", async (finalDecision) => {
    vi.mocked(submitTextCommand).mockResolvedValue(commandResponse(finalDecision));
    render(<MemoryRouter initialEntries={["/decision"]}><DecisionPage /></MemoryRouter>);

    await userEvent.type(screen.getByLabelText("文本指令"), "打开车门");
    await userEvent.click(screen.getByRole("button", { name: "提交/上传" }));

    await waitFor(() => expect(screen.getAllByText("WINDOW_OPEN")).toHaveLength(2));
    expect(screen.getAllByText("OPEN")).toHaveLength(2);
  });

  it("keeps the current turn_id when navigating among the three white pages", () => {
    render(<MemoryRouter initialEntries={["/decision?turn_id=TURN_test"]}><VisualPageNav /></MemoryRouter>);

    expect(screen.getByRole("link", { name: "裁决" }).getAttribute("href")).toBe("/decision?turn_id=TURN_test");
    expect(screen.getByRole("link", { name: "证据检索" }).getAttribute("href")).toBe("/evidence?turn_id=TURN_test");
    expect(screen.getByRole("link", { name: "审计记录" }).getAttribute("href")).toBe("/audits?turn_id=TURN_test");
  });
});
