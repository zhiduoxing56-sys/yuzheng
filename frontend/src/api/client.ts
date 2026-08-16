import { resolveApiBaseUrl } from "../config";
import type { ErrorResponse } from "../types/contract";

export type QueryValue = string | number | boolean | null | undefined;

export interface RequestOptions extends Omit<RequestInit, "body" | "signal"> {
  query?: Record<string, QueryValue>;
  timeoutMs?: number;
  signal?: AbortSignal;
  json?: unknown;
  bytes?: BodyInit;
  form?: FormData;
}

export type ApiErrorKind =
  | "NETWORK_UNAVAILABLE"
  | "TIMEOUT"
  | "CANCELLED"
  | "INVALID_PARAMETERS"
  | "NOT_FOUND"
  | "WORKFLOW_NOT_ALLOWED"
  | "BACKEND_ERROR"
  | "UNKNOWN";

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  readonly errorCode?: string;
  readonly path: string;
  readonly details?: unknown;

  constructor(options: {
    kind: ApiErrorKind;
    message: string;
    path: string;
    status?: number;
    errorCode?: string;
    details?: unknown;
    cause?: unknown;
  }) {
    super(options.message, { cause: options.cause });
    this.name = "ApiError";
    this.kind = options.kind;
    this.path = options.path;
    this.status = options.status;
    this.errorCode = options.errorCode;
    this.details = options.details;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function parseErrorBody(value: unknown): Partial<ErrorResponse> {
  if (!isRecord(value)) return {};
  const validationDetail = Array.isArray(value.detail)
    ? value.detail.filter(isRecord).map((item) => {
      const location = Array.isArray(item.loc) ? item.loc.map(String).join(".") : "请求参数";
      const message = typeof item.msg === "string" ? item.msg : "格式无效";
      return `${location}：${message}`;
    }).join("；")
    : typeof value.detail === "string" ? value.detail : undefined;
  return {
    error_code: typeof value.error_code === "string" ? value.error_code : undefined,
    message: typeof value.message === "string" ? value.message : validationDetail,
    turn_id: typeof value.turn_id === "string" ? value.turn_id : undefined,
    details: isRecord(value.details) ? value.details : undefined,
  };
}

function classify(status?: number, errorCode?: string): ApiErrorKind {
  if (status === 404) return "NOT_FOUND";
  if (status === 409 || errorCode === "TURN_ALREADY_FINALIZED" || errorCode === "REVIEW_NOT_ALLOWED") {
    return "WORKFLOW_NOT_ALLOWED";
  }
  if (status === 400 || status === 422 || errorCode === "INVALID_REQUEST" || errorCode === "INVALID_FILTER") {
    return "INVALID_PARAMETERS";
  }
  if (status && status >= 500) return "BACKEND_ERROR";
  return "UNKNOWN";
}

function makeUrl(base: string, path: string, query?: Record<string, QueryValue>): string {
  const url = new URL(path, `${base}/`);
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, String(value));
  });
  return url.toString();
}

async function readResponse(response: Response): Promise<unknown> {
  if (response.status === 204) return undefined;
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return response.json();
  const text = await response.text();
  return text || undefined;
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const base = await resolveApiBaseUrl();
  const timeoutMs = options.timeoutMs ?? 15_000;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort("timeout"), timeoutMs);
  const signal = options.signal;
  const abortListener = () => controller.abort(signal?.reason);
  signal?.addEventListener("abort", abortListener, { once: true });

  const headers = new Headers(options.headers);
  let body: BodyInit | undefined;
  if (options.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(options.json);
  } else if (options.bytes !== undefined) {
    body = options.bytes;
  } else if (options.form !== undefined) {
    body = options.form;
  }

  const url = makeUrl(base, path, options.query);
  if (import.meta.env.DEV) console.debug("[yuzheng-api]", options.method || "GET", url);

  try {
    const response = await fetch(url, { ...options, headers, body, signal: controller.signal });
    const payload = await readResponse(response);
    if (!response.ok) {
      const parsed = parseErrorBody(payload);
      throw new ApiError({
        kind: classify(response.status, parsed.error_code),
        message: parsed.message || `请求失败（${response.status}）`,
        path,
        status: response.status,
        errorCode: parsed.error_code,
        details: parsed.details ?? payload,
      });
    }
    return payload as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (controller.signal.aborted) {
      const cancelled = signal?.aborted;
      throw new ApiError({
        kind: cancelled ? "CANCELLED" : "TIMEOUT",
        message: cancelled ? "请求已取消" : "请求超时，请稍后重试",
        path,
        cause: error,
      });
    }
    throw new ApiError({ kind: "NETWORK_UNAVAILABLE", message: "后端服务不可达", path, cause: error });
  } finally {
    window.clearTimeout(timeout);
    signal?.removeEventListener("abort", abortListener);
  }
}

export const apiClient = {
  request,
  get<T>(path: string, query?: Record<string, QueryValue>, options?: RequestOptions) {
    return request<T>(path, { ...options, method: "GET", query });
  },
  post<T>(path: string, json?: unknown, options?: RequestOptions) {
    return request<T>(path, { ...options, method: "POST", json });
  },
  patch<T>(path: string, json?: unknown, options?: RequestOptions) {
    return request<T>(path, { ...options, method: "PATCH", json });
  },
  put<T>(path: string, json?: unknown, options?: RequestOptions) {
    return request<T>(path, { ...options, method: "PUT", json });
  },
  postBytes<T>(path: string, bytes: BodyInit, query?: Record<string, QueryValue>, options?: RequestOptions) {
    return request<T>(path, { ...options, method: "POST", bytes, query });
  },
  postForm<T>(path: string, form: FormData, options?: RequestOptions) {
    return request<T>(path, { ...options, method: "POST", form });
  },
};
