const SENSITIVE_KEY_PARTS = ["token", "authorization_token", "secret"];

export function isSensitiveAuditKey(key: string): boolean {
  const normalized = key.toLowerCase();
  return SENSITIVE_KEY_PARTS.some((part) => normalized.includes(part));
}

export function containsSensitiveAuditField(value: unknown): boolean {
  if (Array.isArray(value)) return value.some(containsSensitiveAuditField);
  if (!value || typeof value !== "object") return false;
  return Object.entries(value as Record<string, unknown>).some(([key, child]) => isSensitiveAuditKey(key) || containsSensitiveAuditField(child));
}

function isRawSecretKey(key: string): boolean {
  const normalized = key.toLowerCase();
  return normalized === "token" || normalized.endsWith("_token") || normalized.includes("authorization_token") || normalized.includes("secret");
}

export function containsRawAuditSecretField(value: unknown): boolean {
  if (Array.isArray(value)) return value.some(containsRawAuditSecretField);
  if (!value || typeof value !== "object") return false;
  return Object.entries(value as Record<string, unknown>).some(([key, child]) => isRawSecretKey(key) || containsRawAuditSecretField(child));
}

/** Removes raw secret-bearing fields before audit responses enter React display state. */
export function sanitizeAuditForDisplay<T>(value: T): T {
  if (Array.isArray(value)) return value.map((item) => sanitizeAuditForDisplay(item)) as T;
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(
    Object.entries(value as Record<string, unknown>)
      .filter(([key]) => !isRawSecretKey(key))
      .map(([key, child]) => [key, sanitizeAuditForDisplay(child)]),
  ) as T;
}

export function sanitizeAuditExport(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sanitizeAuditExport);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(
    Object.entries(value as Record<string, unknown>)
      .filter(([key]) => !isSensitiveAuditKey(key))
      .map(([key, child]) => [key, sanitizeAuditExport(child)]),
  );
}

export function safeAuditExportFilename(auditId: string, now = new Date()): string {
  const safeId = auditId.replace(/[^a-zA-Z0-9_-]+/g, "_").slice(0, 64) || "audit";
  const stamp = now.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}Z$/, "Z");
  return `audit-${safeId}-${stamp}.json`;
}
