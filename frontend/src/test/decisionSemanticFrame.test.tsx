// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, useLocation } from "react-router-dom";
import { submitAudioCommand, submitMicrophoneCommand, submitTextCommand } from "../api/command";
import { getTurnPresentation } from "../api/turns";
import { VisualPageNav } from "../components/VisualPageNav";
import { DecisionPage } from "../pages/DecisionPage";
import type { AudioCommandResponse, EvidenceDemandPresentation, SemanticFrame, TextCommandResponse, TurnPresentationResponse } from "../types/contract";

vi.mock("../api/command", () => ({ submitAudioCommand: vi.fn(), submitMicrophoneCommand: vi.fn(), submitTextCommand: vi.fn() }));
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

function audioCommandResponse(): AudioCommandResponse {
  return {
    turn_id: "TURN_test",
    voice_trust: {},
    spectrum_analysis: {},
    asr_result: { transcribed_text: semanticFrame.raw_text },
    semantic_frame: semanticFrame,
    decision: { final_decision: "PASS" },
    audit: {},
    accepted: true,
    input_type: "audio",
  } as AudioCommandResponse;
}

beforeEach(() => {
  vi.mocked(submitAudioCommand).mockReset();
  vi.mocked(submitMicrophoneCommand).mockReset();
  vi.mocked(submitTextCommand).mockReset();
  vi.mocked(getTurnPresentation).mockReset();
});

afterEach(cleanup);

describe("DecisionPage semantic-frame connection", () => {
  it("submits only text, preserves duplicate intent occurrences, and writes turn_id to the URL", async () => {
    vi.mocked(submitTextCommand).mockResolvedValue(commandResponse());
    render(<MemoryRouter initialEntries={["/decision"]}><DecisionPage /><LocationProbe /></MemoryRouter>);

    await userEvent.type(screen.getByLabelText("文本指令"), semanticFrame.raw_text);
    await userEvent.click(screen.getByRole("button", { name: "提交指令" }));

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

  it("shows an unscored semantic review without presenting the stored compatibility score", async () => {
    vi.mocked(getTurnPresentation).mockResolvedValue({
      turn_id: "TURN_review",
      semantic_frame: {
        ...semanticFrame,
        turn_id: "TURN_review",
        raw_text: "把那个打开",
        normalized_text: "把那个打开",
        semantic_status: "REVIEW",
        semantic_confidence: 0,
        ambiguity_score: 1,
        intents: [],
      },
      score_result: {
        semantic_clarity: null,
        evidence_support: null,
        evidence_trust: null,
        jailbreak_suppression: null,
        scene_necessity: null,
        safety_score: 1,
      },
      decision_result: {
        final_decision: "REVIEW",
        reasons: ["SEMANTIC_REVIEW_TERMINAL"],
        explanation: "语义信息不完整或存在歧义；需要用户复核。",
      },
    } as unknown as TurnPresentationResponse);

    const view = render(<MemoryRouter initialEntries={["/decision?turn_id=TURN_review"]}><DecisionPage /></MemoryRouter>);

    await waitFor(() => expect(screen.getByText("人工复核")).toBeTruthy());
    expect(view.container.querySelector(".decision-score strong")?.textContent).toBe("--");
    const detailCells = Array.from(view.container.querySelectorAll(".decision-dimension-table tbody td:nth-child(2)"));
    expect(detailCells).toHaveLength(5);
    for (const cell of detailCells) expect(cell.textContent).toBe("--");
  });

  it.each(["PASS", "REVIEW", "BLOCK"] as const)("does not alter the semantic frame for a %s command decision", async (finalDecision) => {
    vi.mocked(submitTextCommand).mockResolvedValue(commandResponse(finalDecision));
    render(<MemoryRouter initialEntries={["/decision"]}><DecisionPage /></MemoryRouter>);

    await userEvent.type(screen.getByLabelText("文本指令"), "打开车门");
    await userEvent.click(screen.getByRole("button", { name: "提交指令" }));

    await waitFor(() => expect(screen.getAllByText("WINDOW_OPEN")).toHaveLength(2));
    expect(screen.getAllByText("OPEN")).toHaveLength(2);
  });

  it("uploads a WAV file through the audio endpoint and renders its semantic frame", async () => {
    vi.mocked(submitAudioCommand).mockResolvedValue(audioCommandResponse());
    render(<MemoryRouter initialEntries={["/decision"]}><DecisionPage /><LocationProbe /></MemoryRouter>);

    await userEvent.click(screen.getByRole("tab", { name: "音频上传" }));
    const wav = new File([new Uint8Array([82, 73, 70, 70])], "command.wav", { type: "audio/wav" });
    await userEvent.upload(screen.getByLabelText("WAV 音频文件"), wav);
    await userEvent.click(screen.getByRole("button", { name: "上传 WAV" }));

    await waitFor(() => expect(submitAudioCommand).toHaveBeenCalledTimes(1));
    expect(submitAudioCommand).toHaveBeenCalledWith(wav, {
      audio_source: "browser_upload",
      speaker_zone: "driver",
      speaker_role: "driver",
    }, expect.any(AbortSignal));
    await waitFor(() => expect(screen.getByTestId("location").textContent).toBe("?turn_id=TURN_test"));
    expect(screen.getAllByText("WINDOW_OPEN")).toHaveLength(2);
  });

  it("rejects a non-WAV file before calling the audio endpoint", async () => {
    render(<MemoryRouter initialEntries={["/decision"]}><DecisionPage /></MemoryRouter>);

    await userEvent.click(screen.getByRole("tab", { name: "音频上传" }));
    const mp3 = new File([new Uint8Array([1])], "command.mp3", { type: "audio/mpeg" });
    fireEvent.change(screen.getByLabelText("WAV 音频文件"), { target: { files: [mp3] } });
    await userEvent.click(screen.getByRole("button", { name: "上传 WAV" }));

    expect((await screen.findByRole("alert")).textContent).toContain("当前仅支持未压缩 PCM WAV 文件。");
    expect(submitAudioCommand).not.toHaveBeenCalled();
  });

  it("captures four seconds from the backend laptop microphone", async () => {
    vi.mocked(submitMicrophoneCommand).mockResolvedValue(audioCommandResponse());
    render(<MemoryRouter initialEntries={["/decision"]}><DecisionPage /><LocationProbe /></MemoryRouter>);

    await userEvent.click(screen.getByRole("tab", { name: "麦克风采集" }));
    await userEvent.click(screen.getByRole("button", { name: "采集 4 秒语音" }));

    await waitFor(() => expect(submitMicrophoneCommand).toHaveBeenCalledWith({
      duration_seconds: 4,
      speaker_zone: "driver",
      speaker_role: "driver",
    }, expect.any(AbortSignal)));
    await waitFor(() => expect(screen.getByTestId("location").textContent).toBe("?turn_id=TURN_test"));
    expect(screen.getAllByText("WINDOW_OPEN")).toHaveLength(2);
  });

  it("keeps the current turn_id when navigating among the three white pages", () => {
    render(<MemoryRouter initialEntries={["/decision?turn_id=TURN_test"]}><VisualPageNav /></MemoryRouter>);

    expect(screen.getByRole("link", { name: "裁决" }).getAttribute("href")).toBe("/decision?turn_id=TURN_test");
    expect(screen.getByRole("link", { name: "证据检索" }).getAttribute("href")).toBe("/evidence?turn_id=TURN_test");
    expect(screen.getByRole("link", { name: "审计记录" }).getAttribute("href")).toBe("/audits?turn_id=TURN_test");
  });
});
