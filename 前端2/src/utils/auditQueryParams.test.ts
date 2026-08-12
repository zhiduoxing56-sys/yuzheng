import { describe, expect, it } from "vitest";
import { buildAuditDetailPath, buildAuditListPath, fromDateTimeLocal, parseAuditQueryParams, serializeAuditQuery, totalAuditPages } from "./auditQueryParams";

describe("auditQueryParams", () => {
  it("restores valid URL state and serializes only public filters", () => {
    const parsed = parseAuditQueryParams(new URLSearchParams("page=3&page_size=50&decision=BLOCK&start_time=2026-08-01T00%3A00%3A00Z&end_time=2026-08-02T00%3A00%3A00Z&turn_id=ignored"));
    expect(parsed.validTimeRange).toBe(true);
    expect(parsed.query).toEqual({ page: 3, page_size: 50, decision: "BLOCK", start_time: "2026-08-01T00:00:00.000Z", end_time: "2026-08-02T00:00:00.000Z" });
    expect(serializeAuditQuery(parsed.query).has("turn_id")).toBe(false);
  });

  it("falls back for invalid page, size, decision and timestamps", () => {
    const parsed = parseAuditQueryParams(new URLSearchParams("page=0&page_size=101&decision=ALLOW&start_time=yesterday"));
    expect(parsed.query).toEqual({ page: 1, page_size: 20 });
    expect(parsed.issues).toHaveLength(4);
  });

  it("blocks a reversed time range without changing the values", () => {
    const parsed = parseAuditQueryParams(new URLSearchParams("start_time=2026-08-02T00%3A00%3A00Z&end_time=2026-08-01T00%3A00%3A00Z"));
    expect(parsed.validTimeRange).toBe(false);
    expect(parsed.query.start_time).toBe("2026-08-02T00:00:00.000Z");
  });

  it("builds refresh-safe list and detail addresses", () => {
    const query = { page: 2, page_size: 20, decision: "PASS" as const };
    expect(buildAuditListPath(query)).toBe("/audits?page=2&page_size=20&decision=PASS");
    expect(buildAuditDetailPath("AUD /1", query)).toBe("/audits/AUD%20%2F1?page=2&page_size=20&decision=PASS");
    expect(buildAuditDetailPath("AUD_1")).toBe("/audits/AUD_1");
  });

  it("handles total pages and local time conversion", () => {
    expect(totalAuditPages(41, 20)).toBe(3);
    expect(totalAuditPages(0, 20)).toBe(1);
    expect(fromDateTimeLocal("2026-08-04T12:00")).toMatch(/^2026-08-04T/);
  });
});
