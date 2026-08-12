// @vitest-environment jsdom
import { act, cleanup, render, renderHook, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { CommandInputPanel } from "../components/CommandInputPanel";
import { TopNav } from "../components/TopNav";
import { useCommandSubmission, type TextSubmissionInput } from "../hooks/useCommandSubmission";
import { SessionProvider, useSession } from "../stores/sessionStore";
import { submitTextCommand } from "../api/command";
import type { TextCommandResponse } from "../types/contract";

vi.mock("../api/command", () => ({
  submitTextCommand: vi.fn(),
  submitAudioCommand: vi.fn(),
  submitMicrophoneCommand: vi.fn(),
}));

const textInput: TextSubmissionInput = {
  text: "帮我打开空调",
  speakerZone: "driver",
  speakerRole: "driver",
  stateOverridesJson: "",
  evidenceOverridesJson: "",
};

function acceptedResponse(turnId = "TURN_B"): TextCommandResponse {
  return {
    turn_id: turnId,
    input_type: "text",
    decision: {
      turn_id: turnId,
      decision: "PASS",
      score_decision: "PASS",
      final_decision: "PASS",
      decision_sources: [],
      decision_merge_reason: "test",
      safety_score: 0.92,
      gate_blocked: false,
      gate_reasons: [],
      explanations: [],
      reason_codes: [],
    },
    semantic_frame: {
      frame_id: "SEM_test",
      turn_id: turnId,
      raw_text: "帮我打开空调",
      normalized_text: "帮我打开空调",
      semantic_confidence: 0.95,
      ambiguity_score: 0.05,
      semantic_status: "OK",
      review_reasons: [],
      review_candidates: [],
      unresolved_clauses: [],
      security_signals: [],
      intents: [{
        clause_index: 0,
        clause_text: "帮我打开空调",
        intent_id: "CLIMATE_OPEN",
        action: "OPEN",
        target: "CLIMATE",
        area: "CABIN",
        control_domain: "COMFORT",
        risk_level: "R1",
        risk_tags: [],
        semantic_confidence: 0.95,
        ambiguity_score: 0.05,
      }],
    },
    evidence_demand: { demand_id: "DEM_test", turn_id: turnId, intent_demands: [] },
    audit: { audit_id: null },
  };
}

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => { resolve = resolvePromise; reject = rejectPromise; });
  return { promise, resolve, reject };
}

function panelProps() {
  return {
    sessionId: "session-panel",
    status: "idle" as const,
    busy: false,
    error: null,
    draftResetVersion: null as string | null,
    onSubmitText: vi.fn(async () => undefined),
    onSubmitAudio: vi.fn(async () => undefined),
    onSubmitMicrophone: vi.fn(async () => undefined),
  };
}

afterEach(() => cleanup());
beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  vi.mocked(submitTextCommand).mockReset();
});

describe("real-time decision command regressions", () => {
  it("1. keeps the original text after the backend accepts the command", async () => {
    const props = panelProps();
    const user = userEvent.setup();
    const view = render(<CommandInputPanel {...props} />);
    const textarea = view.container.querySelector("textarea.command-textarea") as HTMLTextAreaElement;
    await user.type(textarea, "帮我打开空调");
    view.rerender(<CommandInputPanel {...props} status="waiting_presentation" draftResetVersion="TURN_B" />);
    expect(textarea.value).toBe("帮我打开空调");
  });

  it("2. allows editing while waiting for presentation", async () => {
    vi.mocked(submitTextCommand).mockResolvedValue(acceptedResponse());
    const { result } = renderHook(() => useCommandSubmission({ sessionId: "session-A", sessionEpoch: 0, backendAvailable: true, onAccepted: vi.fn(), onBeforeSubmit: vi.fn() }));
    await act(async () => { await result.current.submitText(textInput); });
    expect(result.current.status).toBe("waiting_presentation");
    expect(result.current.busy).toBe(false);
  });

  it("3. prevents another submit for the current task while waiting for presentation", async () => {
    vi.mocked(submitTextCommand).mockResolvedValue(acceptedResponse());
    const { result } = renderHook(() => useCommandSubmission({ sessionId: "session-A", sessionEpoch: 0, backendAvailable: true, onAccepted: vi.fn(), onBeforeSubmit: vi.fn() }));
    await act(async () => { await result.current.submitText(textInput); });
    expect(result.current.status).toBe("waiting_presentation");
    expect(result.current.busy).toBe(true);
  });

  it("11. reset at the new-session boundary cancels the in-flight command request", async () => {
    const pending = deferred<TextCommandResponse>();
    let requestSignal: AbortSignal | undefined;
    vi.mocked(submitTextCommand).mockImplementation((_request, signal) => { requestSignal = signal; return pending.promise; });
    const { result } = renderHook(() => useCommandSubmission({ sessionId: "session-A", sessionEpoch: 0, backendAvailable: true, onAccepted: vi.fn(), onBeforeSubmit: vi.fn() }));
    let request!: Promise<void>;
    act(() => { request = result.current.submitText(textInput); });
    await waitFor(() => expect(requestSignal).toBeDefined());
    act(() => result.current.reset());
    expect(requestSignal?.aborted).toBe(true);
    pending.resolve(acceptedResponse("TURN_OLD"));
    await act(async () => { await request; });
  });

  it("12. an old request cannot update activeTurnId after TopNav creates a new session", async () => {
    const pending = deferred<TextCommandResponse>();
    vi.mocked(submitTextCommand).mockReturnValue(pending.promise);

    function Harness() {
      const session = useSession();
      const submission = useCommandSubmission({
        sessionId: session.sessionId,
        sessionEpoch: session.sessionEpoch,
        backendAvailable: true,
        onBeforeSubmit: () => undefined,
        onAccepted: (value) => session.setActiveTurn(value.turnId),
      });
      return <><TopNav /><button data-testid="submit" onClick={() => void submission.submitText(textInput)}>submit</button><output data-testid="active-turn">{session.activeTurnId ?? "none"}</output></>;
    }

    const view = render(<MemoryRouter initialEntries={["/decision"]}><SessionProvider><Harness /></SessionProvider></MemoryRouter>);
    await userEvent.click(view.getByTestId("submit"));
    const newSessionButton = view.container.querySelector(".assist-menu-panel button") as HTMLButtonElement;
    await userEvent.click(newSessionButton);
    await act(async () => {
      pending.resolve(acceptedResponse("TURN_OLD"));
      await pending.promise;
      await Promise.resolve();
    });
    expect(view.getByTestId("active-turn").textContent).toBe("none");
  });
});

export function TestSessionWrapper({ children }: { children: ReactNode }) {
  return <MemoryRouter initialEntries={["/decision"]}><SessionProvider>{children}</SessionProvider></MemoryRouter>;
}
