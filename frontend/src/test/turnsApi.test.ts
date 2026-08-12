import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../api/client";
import { getTurnTimeline, getTurnTimelineSummary } from "../api/turns";

vi.mock("../api/client", () => ({ apiClient: { get: vi.fn(), post: vi.fn(), postBytes: vi.fn(), postForm: vi.fn(), patch: vi.fn() } }));

describe("turn timeline routes", () => {
  beforeEach(() => vi.mocked(apiClient.get).mockReset());

  it("test_decision_page_uses_timeline_summary", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ root_turn_id: "TURN_A", items: [] });
    await getTurnTimelineSummary("TURN_A");
    expect(apiClient.get).toHaveBeenCalledTimes(1);
    expect(apiClient.get).toHaveBeenCalledWith("/api/turns/TURN_A/timeline-summary", undefined, { signal: undefined });
  });

  it("test_decision_page_does_not_fetch_full_timeline", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ root_turn_id: "TURN_A", items: [] });
    await getTurnTimelineSummary("TURN_A");
    expect(apiClient.get).toHaveBeenCalledTimes(1);
    expect(vi.mocked(apiClient.get).mock.calls.map(([path]) => path)).not.toContain("/api/turns/TURN_A/timeline");
  });

  it("keeps the complete timeline available for an explicit detail read", async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ root_turn_id: "TURN_A", audits: [], items: [] });
    await getTurnTimeline("TURN_A");
    expect(apiClient.get).toHaveBeenCalledTimes(1);
    expect(apiClient.get).toHaveBeenCalledWith("/api/turns/TURN_A/timeline", undefined, { signal: undefined });
  });
});
