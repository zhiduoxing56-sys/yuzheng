import { beforeEach, describe, expect, it } from "vitest";
import { readCache } from "./readCache";

beforeEach(() => readCache.clear());

describe("application read cache", () => {
  it("deduplicates concurrent requests for the same key", async () => {
    let calls = 0;
    let release!: () => void;
    const gate = new Promise<void>((resolve) => { release = resolve; });
    const loader = async () => { calls += 1; await gate; return "ready"; };
    const first = readCache.load("presentation:TURN_1", loader);
    const second = readCache.load("presentation:TURN_1", loader);
    release();
    await expect(Promise.all([first, second])).resolves.toEqual(["ready", "ready"]);
    expect(calls).toBe(1);
  });

  it("keeps old data visible while a stale refresh runs", async () => {
    await readCache.load("workflow:TURN_1", async () => "old");
    let release!: () => void;
    const gate = new Promise<void>((resolve) => { release = resolve; });
    const refreshing = readCache.load("workflow:TURN_1", async () => { await gate; return "new"; }, { force: true });
    expect(readCache.snapshot("workflow:TURN_1")).toMatchObject({ data: "old", loading: true });
    release();
    await refreshing;
    expect(readCache.snapshot("workflow:TURN_1")).toMatchObject({ data: "new", loading: false });
  });

  it("does not let an invalidated late response replace fresh data", async () => {
    let releaseOld!: () => void;
    const oldGate = new Promise<void>((resolve) => { releaseOld = resolve; });
    const oldRequest = readCache.load("audit:AUD_1", async () => { await oldGate; return "old"; });
    readCache.invalidate("audit:AUD_1");
    await readCache.load("audit:AUD_1", async () => "fresh");
    releaseOld();
    await oldRequest;
    expect(readCache.snapshot("audit:AUD_1").data).toBe("fresh");
  });
});
