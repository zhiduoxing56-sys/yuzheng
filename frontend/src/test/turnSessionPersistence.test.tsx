// @vitest-environment jsdom

import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { SessionProvider, useSession } from "../stores/sessionStore";

function SessionProbe() {
  const { activeTurnId, setActiveTurn } = useSession();
  return <div>
    <output aria-label="current turn">{activeTurnId || "--"}</output>
    <button onClick={() => setActiveTurn("TURN_PERSISTED")}>set turn</button>
  </div>;
}

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  localStorage.setItem("yuzheng.v2.session.id", "session-persistence-test");
  localStorage.setItem("yuzheng.v2.migration.complete", "1");
  localStorage.setItem("yuzheng.v2.recent-migration.complete", "1");
});

afterEach(cleanup);

describe("current turn session persistence", () => {
  it("restores the current turn after page remount without persisting it across browser sessions", async () => {
    const first = render(<SessionProvider><SessionProbe /></SessionProvider>);
    await userEvent.click(screen.getByRole("button", { name: "set turn" }));
    expect(sessionStorage.getItem("yuzheng.v2.turn.active")).toBe("TURN_PERSISTED");
    expect(localStorage.getItem("yuzheng.v2.turn.active")).toBeNull();
    first.unmount();

    render(<SessionProvider><SessionProbe /></SessionProvider>);

    expect(screen.getByLabelText("current turn").textContent).toBe("TURN_PERSISTED");
  });
});
