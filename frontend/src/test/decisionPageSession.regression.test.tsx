// @vitest-environment jsdom
import { cleanup, render, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { DecisionPage } from "../pages/DecisionPage";
import { TopNav } from "../components/TopNav";
import { SessionProvider } from "../stores/sessionStore";

const presentationCalls = vi.hoisted(() => [] as Array<string | null>);

vi.mock("../hooks/useHealthStatus", () => ({ useHealthStatus: () => ({ data: null, loading: false, error: null, lastUpdatedAt: null, available: true, refresh: vi.fn(async () => undefined) }) }));
vi.mock("../hooks/usePipelineSocket", () => ({ usePipelineSocket: () => ({ error: null }) }));
vi.mock("../hooks/useTurnPresentation", () => ({
  useTurnPresentation: (turnId: string | null) => {
    presentationCalls.push(turnId);
    return { data: null, loading: false, error: null, exhausted: false, retry: vi.fn(async () => null) };
  },
}));
vi.mock("../hooks/useTurnTimeline", () => ({ useTurnTimeline: () => ({ data: null, loading: false, error: null, refresh: vi.fn(async () => null) }) }));
vi.mock("../hooks/useWorkflowStatus", () => ({ useWorkflowStatus: () => ({ data: null, loading: false, error: null, refresh: vi.fn(async () => null) }) }));
vi.mock("../hooks/useVehicleState", () => ({ useVehicleState: () => ({ data: null, loading: false, error: null, refresh: vi.fn(async () => null) }) }));

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  presentationCalls.length = 0;
  localStorage.setItem("yuzheng.v2.session.id", "session-old-12345678");
  localStorage.setItem("yuzheng.v2.turn.active", "TURN_A");
  localStorage.setItem("yuzheng.v2.migration.complete", "1");
  localStorage.setItem("yuzheng.v2.recent-migration.complete", "1");
  sessionStorage.setItem("yuzheng.v2.lastSubmission.session-old-12345678", JSON.stringify({
    text: "OLD_SUBMISSION_SHOULD_DISAPPEAR",
    inputType: "text",
    source: "user input",
    turnId: "TURN_A",
    submittedAt: "2026-08-04T00:00:00Z",
    preliminaryDecision: "PASS",
  }));
});

afterEach(() => cleanup());

describe("DecisionPage session replacement regression", () => {
  it("13. TopNav new session resets DecisionPage viewTurnId and restored submission", async () => {
    const view = render(<MemoryRouter initialEntries={["/decision"]}><SessionProvider><TopNav /><DecisionPage /></SessionProvider></MemoryRouter>);
    expect(view.queryByText("OLD_SUBMISSION_SHOULD_DISAPPEAR")).not.toBeNull();
    const newSessionButton = view.container.querySelector(".assist-menu-panel button") as HTMLButtonElement;
    await userEvent.click(newSessionButton);
    await waitFor(() => expect(localStorage.getItem("yuzheng.v2.turn.active")).toBeNull());
    expect.soft(presentationCalls.at(-1)).toBeNull();
    expect.soft(view.queryByText("OLD_SUBMISSION_SHOULD_DISAPPEAR")).toBeNull();
  });
});
