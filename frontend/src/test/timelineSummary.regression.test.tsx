// @vitest-environment jsdom
import { act, cleanup, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { getTurnTimeline, getTurnTimelineSummary } from "../api/turns";
import { readCache } from "../cache/readCache";
import { useReviewTimeline } from "../hooks/useReviewTimeline";
import { useTurnTimeline } from "../hooks/useTurnTimeline";

vi.mock("../api/turns", () => ({
  getTurnTimeline: vi.fn(),
  getTurnTimelineSummary: vi.fn(),
}));

beforeEach(() => {
  readCache.clear();
  vi.mocked(getTurnTimeline).mockReset();
  vi.mocked(getTurnTimelineSummary).mockReset();
});

afterEach(() => {
  cleanup();
  readCache.clear();
});

it("decision timeline exposes a summary error without falling back to full timeline", async () => {
  vi.mocked(getTurnTimelineSummary).mockRejectedValue(new Error("summary unavailable"));

  const { result } = renderHook(() => useTurnTimeline("TURN_A"));

  await waitFor(() => expect(result.current.error).toBe("summary unavailable"));
  expect(result.current.data).toBeNull();
  expect(getTurnTimelineSummary).toHaveBeenCalledTimes(1);
  expect(getTurnTimeline).not.toHaveBeenCalled();
});

it("review timeline exposes a summary error without falling back to full timeline", async () => {
  vi.mocked(getTurnTimelineSummary).mockRejectedValue(new Error("summary unavailable"));
  const { result } = renderHook(() => useReviewTimeline("TURN_A"));
  const controller = new AbortController();

  await act(async () => {
    await result.current.load("TURN_A", controller.signal);
  });

  expect(result.current.error).toBe("summary unavailable");
  expect(result.current.data).toBeNull();
  expect(getTurnTimelineSummary).toHaveBeenCalledTimes(1);
  expect(getTurnTimeline).not.toHaveBeenCalled();
});
