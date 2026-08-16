// @vitest-environment jsdom

import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import { App } from "../App";
import { getRecentRecallAudits } from "../api/recallAudits";
import { getIndexStatus } from "../api/system";
import { getTurnPresentation } from "../api/turns";
import { SessionProvider } from "../stores/sessionStore";

vi.mock("../api/system", () => ({ getIndexStatus: vi.fn(), updateIndexParameters: vi.fn() }));
vi.mock("../api/turns", () => ({ getTurnPresentation: vi.fn() }));
vi.mock("../api/recallAudits", () => ({ getRecentRecallAudits: vi.fn(), analyzeRecallAudit: vi.fn() }));

beforeEach(() => {
  window.localStorage.clear();
  window.sessionStorage.clear();
  vi.mocked(getIndexStatus).mockResolvedValue({ M: 16, ef_construction: 200, ef_search: 30, layer_count: 4, top_k: 20 });
  vi.mocked(getRecentRecallAudits).mockResolvedValue({ items: [] });
  vi.mocked(getTurnPresentation).mockResolvedValue({
    retrieval_summary: { top_k: 20, candidate_count: 1, mandatory_recall_count: 0, elapsed_ms: 1, layers: [] },
  } as never);
});

afterEach(cleanup);

it("mounts the real evidence route under the application session provider", async () => {
  render(<MemoryRouter initialEntries={["/evidence/TURN_MOUNT"]}><SessionProvider><App /></SessionProvider></MemoryRouter>);
  await waitFor(() => expect(getTurnPresentation).toHaveBeenCalledWith("TURN_MOUNT", expect.any(AbortSignal)));
  expect(screen.getByRole("heading", { name: "安全知识检索" })).toBeTruthy();
});
