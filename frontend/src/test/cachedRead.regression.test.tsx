// @vitest-environment jsdom
import { act, cleanup, render, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { readCache } from "../cache/readCache";
import { useCachedRead } from "../hooks/useCachedRead";

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((resolvePromise) => { resolve = resolvePromise; });
  return { promise, resolve };
}

interface Observation { key: string; data: string | null; loading: boolean }

function CachedProbe({ cacheKey, load, observations }: { cacheKey: string; load: (key: string, signal: AbortSignal) => Promise<string>; observations: Observation[] }) {
  const snapshot = useCachedRead(cacheKey, (signal) => load(cacheKey, signal), 60_000);
  observations.push({ key: cacheKey, data: snapshot.data, loading: snapshot.loading });
  return <output data-testid="value">{snapshot.data ?? "empty"}</output>;
}

beforeEach(() => readCache.clear());
afterEach(() => { cleanup(); readCache.clear(); });

describe("read cache key ownership regressions", () => {
  it("4. never exposes TURN_A data during a render owned by TURN_B", async () => {
    const b = deferred<string>();
    const observations: Observation[] = [];
    const load = (key: string) => key === "presentation:TURN_A" ? Promise.resolve("TURN_A") : b.promise;
    const view = render(<CachedProbe cacheKey="presentation:TURN_A" load={load} observations={observations} />);
    await waitFor(() => expect(view.getByTestId("value").textContent).toBe("TURN_A"));
    view.rerender(<CachedProbe cacheKey="presentation:TURN_B" load={load} observations={observations} />);
    expect(observations.some((item) => item.key === "presentation:TURN_B" && item.data === "TURN_A")).toBe(false);
    b.resolve("TURN_B");
  });

  it("5. ignores a late TURN_A presentation after the key changes to TURN_B", async () => {
    const a = deferred<string>();
    const b = deferred<string>();
    const observations: Observation[] = [];
    const load = (key: string) => key === "presentation:TURN_A" ? a.promise : b.promise;
    const view = render(<CachedProbe cacheKey="presentation:TURN_A" load={load} observations={observations} />);
    view.rerender(<CachedProbe cacheKey="presentation:TURN_B" load={load} observations={observations} />);
    await act(async () => { b.resolve("TURN_B"); await b.promise; });
    await waitFor(() => expect(view.getByTestId("value").textContent).toBe("TURN_B"));
    await act(async () => { a.resolve("TURN_A"); await a.promise; });
    expect(view.getByTestId("value").textContent).toBe("TURN_B");
  });

  it("15. a final result for the current turn does not regress after a stale request completes", async () => {
    const stale = deferred<string>();
    const current = deferred<string>();
    const observations: Observation[] = [];
    const load = (key: string) => key === "presentation:TURN_OLD" ? stale.promise : current.promise;
    const view = render(<CachedProbe cacheKey="presentation:TURN_OLD" load={load} observations={observations} />);
    view.rerender(<CachedProbe cacheKey="presentation:TURN_CURRENT" load={load} observations={observations} />);
    await act(async () => { current.resolve("TURN_CURRENT"); await current.promise; });
    await waitFor(() => expect(view.getByTestId("value").textContent).toBe("TURN_CURRENT"));
    const currentEstablishedAt = observations.length;
    await act(async () => { stale.resolve("TURN_OLD"); await stale.promise; });
    expect(observations.slice(currentEstablishedAt).every((item) => item.data === "TURN_CURRENT")).toBe(true);
    expect(view.getByTestId("value").textContent).toBe("TURN_CURRENT");
  });
});
