export class ResponseShapeError extends Error {
  constructor(path: string) {
    super(`响应结构异常：${path}`);
    this.name = "ResponseShapeError";
  }
}

export type JsonRecord = Record<string, unknown>;

export function record(value: unknown, path: string): JsonRecord {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new ResponseShapeError(path);
  return value as JsonRecord;
}

export function string(value: unknown, path: string): string {
  if (typeof value !== "string") throw new ResponseShapeError(path);
  return value;
}

export function nonEmptyString(value: unknown, path: string): string {
  const result = string(value, path).trim();
  if (!result) throw new ResponseShapeError(path);
  return result;
}

export function number(value: unknown, path: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) throw new ResponseShapeError(path);
  return value;
}

export function boolean(value: unknown, path: string): boolean {
  if (typeof value !== "boolean") throw new ResponseShapeError(path);
  return value;
}

export function array(value: unknown, path: string): unknown[] {
  if (!Array.isArray(value)) throw new ResponseShapeError(path);
  return value;
}

export function stringArray(value: unknown, path: string): string[] {
  return array(value, path).map((item, index) => string(item, `${path}[${index}]`));
}

export function nullableString(value: unknown, path: string): string | null {
  return value == null ? null : string(value, path);
}

const SECRET_KEY = /(authorization.?token|access.?token|refresh.?token|secret|password|credential)/i;

/** Build a new display-safe object. The input is never mutated or logged. */
export function stripSensitiveFields(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stripSensitiveFields);
  if (!value || typeof value !== "object") return value;
  return Object.fromEntries(Object.entries(value as JsonRecord)
    .filter(([key]) => !SECRET_KEY.test(key))
    .map(([key, item]) => [key, stripSensitiveFields(item)]));
}

