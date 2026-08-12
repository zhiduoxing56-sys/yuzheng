// @vitest-environment jsdom
import { StrictMode } from "react";
import { cleanup, render, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { usePipelineSocket } from "../hooks/usePipelineSocket";
import { SessionProvider, useSession } from "../stores/sessionStore";

class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
  static instances: MockWebSocket[] = [];

  readonly url: string;
  readyState = MockWebSocket.CONNECTING;
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onerror: (() => void) | null = null;
  onclose: (() => void) | null = null;
  close = vi.fn(() => { this.readyState = MockWebSocket.CLOSED; });

  constructor(url: string | URL) {
    this.url = String(url);
    MockWebSocket.instances.push(this);
  }
}

function SocketProbe() {
  usePipelineSocket();
  return null;
}

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  MockWebSocket.instances = [];
  vi.stubGlobal("WebSocket", MockWebSocket);
});

afterEach(async () => {
  cleanup();
  await new Promise((resolve) => window.setTimeout(resolve, 0));
  vi.unstubAllGlobals();
});

describe("pipeline websocket application singleton", () => {
  it("reuses one connection through React StrictMode mount-cleanup-remount", async () => {
    const view = render(<StrictMode><SessionProvider><SocketProbe /></SessionProvider></StrictMode>);
    await waitFor(() => expect(MockWebSocket.instances).toHaveLength(1));
    view.unmount();
    await waitFor(() => expect(MockWebSocket.instances[0].close).toHaveBeenCalledTimes(1));
  });

  it("shares one connection between multiple subscribers and closes after the last unmount", async () => {
    const view = render(<SessionProvider><SocketProbe /><SocketProbe /></SessionProvider>);
    await waitFor(() => expect(MockWebSocket.instances).toHaveLength(1));
    view.unmount();
    await waitFor(() => expect(MockWebSocket.instances[0].close).toHaveBeenCalledTimes(1));
  });

  it("replaces the old session connection and drops events arriving from it", async () => {
    function Harness() {
      usePipelineSocket();
      const session = useSession();
      return <><button onClick={session.newSession}>new session</button><output data-testid="turns">{Object.keys(session.eventsByTurn).join(",")}</output></>;
    }

    const view = render(<SessionProvider><Harness /></SessionProvider>);
    await waitFor(() => expect(MockWebSocket.instances).toHaveLength(1));
    const oldSocket = MockWebSocket.instances[0];
    await userEvent.click(view.getByRole("button"));
    await waitFor(() => expect(MockWebSocket.instances).toHaveLength(2));
    oldSocket.onmessage?.({ data: JSON.stringify({ event_id: "late-A", session_id: "old-session", turn_id: "TURN_A", sequence: 1, event_type: "pipeline", stage: "INPUT_RECEIVED", status: "COMPLETED", timestamp: "2026-08-05T00:00:00Z", duration_ms: 1, summary: "late", payload: {} }) });
    expect(view.getByTestId("turns").textContent).toBe("");
    await waitFor(() => expect(oldSocket.close).toHaveBeenCalledTimes(1));
  });
});
