// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { DecisionPage } from "../pages/DecisionPage";
import { SessionProvider } from "../stores/sessionStore";

const mocks = vi.hoisted(() => ({
  submitText: vi.fn(),
  submitAudio: vi.fn(),
  submitMicrophone: vi.fn(),
  getPresentation: vi.fn(),
  submitClarification: vi.fn(),
}));

vi.mock("../api/command", () => ({
  submitCoordinatedTextCommand: mocks.submitText,
  submitAudioCommand: mocks.submitAudio,
  submitMicrophoneCommand: mocks.submitMicrophone,
}));
vi.mock("../api/turns", () => ({
  getTurnPresentation: mocks.getPresentation,
  submitTurnClarification: mocks.submitClarification,
}));

const frame = (turnId: string, rawText: string) => ({
  frame_id: `SEM_${turnId}`,
  turn_id: turnId,
  raw_text: rawText,
  normalized_text: rawText,
  semantic_confidence: 0.5,
  ambiguity_score: 0.5,
  semantic_status: "REVIEW",
  review_reasons: ["ASR_REVIEW"],
  review_candidates: [],
  unresolved_clauses: [rawText],
  security_signals: [],
  intents: [],
});

const decision = (finalDecision: "PASS" | "REVIEW", safetyScore: number, explanation: string) => ({
  final_decision: finalDecision,
  safety_score: safetyScore,
  explanations: [explanation],
  execution_tokens: [],
  intent_safety_assessments: [{
    clause_index: 0,
    intent_id: "MODE_SET",
    score: {
      semantic_clarity: safetyScore,
      evidence_support: safetyScore,
      evidence_trust: safetyScore,
      jailbreak_suppression: safetyScore,
      scene_necessity: safetyScore,
      safety_score: safetyScore,
    },
  }],
});

const clarification = {
  clarification_id: "CLA_1",
  turn_id: "TURN_A",
  clarification_type: "VOICE_CONFIRMATION",
  prompt: "您是否说：",
  original_text: "运动莫斯",
  candidates: [{
    candidate_id: "CAND_1",
    display_text: "运动模式",
    candidate_source: "ASR_NBEST",
    source_rank: 1,
    confidence: 0.9,
  }],
};

beforeEach(() => {
  vi.clearAllMocks();
  mocks.submitText.mockResolvedValue({
    mode: "SINGLE",
    parent_turn_id: "TURN_A",
    parent_frame: frame("TURN_A", "运动莫斯"),
    blocked_by_parent_security: false,
    children: [{ clause_index: 0, clause_text: "运动莫斯", turn_id: "TURN_A", response: {
      turn_id: "TURN_A",
      semantic_frame: frame("TURN_A", "运动莫斯"),
      decision: decision("REVIEW", 0.55, "等待用户确认"),
      clarification_request: clarification,
    }}],
  });
});
afterEach(cleanup);

async function submitOriginal() {
  render(<SessionProvider><MemoryRouter initialEntries={["/decision"]}><DecisionPage /></MemoryRouter></SessionProvider>);
  await userEvent.type(screen.getByRole("textbox", { name: "文本指令" }), "运动莫斯");
  await userEvent.click(screen.getByRole("button", { name: "提交指令" }));
  await screen.findByRole("dialog", { name: "需要确认" });
}

describe("DecisionPage clarification closure", () => {
  it("候选选择只提交 clarification_id + candidate_id，并跟随 child turn", async () => {
    mocks.submitClarification.mockResolvedValue({
      clarification_id: "CLA_1",
      source_turn_id: "TURN_A",
      resolution: "SELECTED",
      selected_candidate_id: "CAND_1",
      selected_candidate_text: "运动模式",
      child_turn_id: "TURN_B",
      command_result: {
        turn_id: "TURN_B",
        semantic_frame: { ...frame("TURN_B", "运动模式"), semantic_status: "OK", review_reasons: [], unresolved_clauses: [] },
        decision: decision("PASS", 0.92, "复核后证据完整并通过"),
        clarification_request: null,
      },
    });
    await submitOriginal();

    await userEvent.click(screen.getByRole("button", { name: "运动模式" }));

    await waitFor(() => expect(mocks.submitClarification).toHaveBeenCalledWith(
      "TURN_A",
      { clarification_id: "CLA_1", candidate_id: "CAND_1" },
      expect.any(AbortSignal),
    ));
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "需要确认" })).toBeNull());
    expect((screen.getByRole("textbox", { name: "文本指令" }) as HTMLTextAreaElement).value).toBe("运动模式");
    expect(screen.getAllByText("92.0%").length).toBeGreaterThan(0);
    expect(screen.getByText("复核后证据完整并通过")).toBeTruthy();
  });

  it("点击遮罩提交 NONE_OF_ABOVE，关闭弹窗并恢复空输入", async () => {
    mocks.submitClarification.mockResolvedValue({
      clarification_id: "CLA_1",
      source_turn_id: "TURN_A",
      resolution: "NONE_OF_ABOVE",
      selected_candidate_id: null,
      selected_candidate_text: null,
      child_turn_id: null,
      command_result: null,
    });
    await submitOriginal();

    fireEvent.mouseDown(screen.getByTestId("clarification-backdrop"));

    await waitFor(() => expect(mocks.submitClarification).toHaveBeenCalledWith(
      "TURN_A",
      { clarification_id: "CLA_1", resolution: "NONE_OF_ABOVE" },
      expect.any(AbortSignal),
    ));
    await waitFor(() => expect(screen.queryByRole("dialog", { name: "需要确认" })).toBeNull());
    expect((screen.getByRole("textbox", { name: "文本指令" }) as HTMLTextAreaElement).value).toBe("");
    expect(screen.getByText("本轮已结束，请重新说一条完整指令。")).not.toBeNull();
  });

  it("REVIEW 但 clarification_request=null 时不弹窗", async () => {
    mocks.submitText.mockResolvedValue({
      mode: "SINGLE",
      parent_turn_id: "TURN_SAFE_REVIEW",
      parent_frame: frame("TURN_SAFE_REVIEW", "打开车门"),
      blocked_by_parent_security: false,
      children: [{ clause_index: 0, clause_text: "打开车门", turn_id: "TURN_SAFE_REVIEW", response: {
        turn_id: "TURN_SAFE_REVIEW",
        semantic_frame: frame("TURN_SAFE_REVIEW", "打开车门"),
        decision: decision("REVIEW", 0.61, "安全复核但无需语义澄清"),
        clarification_request: null,
      }}],
    });
    render(<SessionProvider><MemoryRouter initialEntries={["/decision"]}><DecisionPage /></MemoryRouter></SessionProvider>);
    await userEvent.type(screen.getByRole("textbox", { name: "文本指令" }), "打开车门");
    await userEvent.click(screen.getByRole("button", { name: "提交指令" }));
    await waitFor(() => expect(mocks.submitText).toHaveBeenCalled());
    expect(screen.queryByRole("dialog", { name: "需要确认" })).toBeNull();
  });
});
