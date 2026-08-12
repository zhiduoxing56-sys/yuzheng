import { describe, expect, it } from "vitest";
import { containsRawAuditSecretField, containsSensitiveAuditField, safeAuditExportFilename, sanitizeAuditExport, sanitizeAuditForDisplay } from "./auditSanitizer";

describe("auditSanitizer", () => {
  it("recursively removes sensitive keys without mutating the source", () => {
    const source = { audit_id: "AUD_1", authorization_token: "raw", nested: [{ token_status: "ISSUED", value: 1 }, { clientSecret: "hidden" }] };
    const protectedValue = sanitizeAuditExport(source);
    expect(protectedValue).toEqual({ audit_id: "AUD_1", nested: [{ value: 1 }, {}] });
    expect(source.authorization_token).toBe("raw");
    expect(containsSensitiveAuditField(protectedValue)).toBe(false);
    expect(containsSensitiveAuditField(source)).toBe(true);
  });

  it("removes raw tokens from display state while preserving safe authorization metadata", () => {
    const result = sanitizeAuditForDisplay({ authorization_token: "raw", token_status: "ISSUED", token_issued: true, nested: { access_token: "raw" } });
    expect(result).toEqual({ token_status: "ISSUED", token_issued: true, nested: {} });
    expect(containsRawAuditSecretField(result)).toBe(false);
  });

  it("creates a safe deterministic JSON filename", () => {
    expect(safeAuditExportFilename("AUD /中文:1", new Date("2026-08-04T01:02:03Z"))).toBe("audit-AUD_1-20260804T010203Z.json");
  });
});
