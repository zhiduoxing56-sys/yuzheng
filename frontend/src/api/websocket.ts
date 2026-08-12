import { resolveWebsocketBaseUrl } from "../config";
import type { ConnectionStatus, PipelineEvent } from "../types/contract";

export interface WebsocketManagerOptions {
  sessionId: string;
  onStatus?: (status: ConnectionStatus) => void;
  onEvent?: (event: PipelineEvent) => void;
  onError?: (error: Error) => void;
  maxReconnectDelayMs?: number;
}

function isPipelineEvent(value: unknown): value is PipelineEvent {
  if (!value || typeof value !== "object") return false;
  const item = value as Record<string, unknown>;
  return typeof item.event_id === "string"
    && typeof item.session_id === "string"
    && typeof item.turn_id === "string"
    && typeof item.sequence === "number"
    && typeof item.stage === "string";
}

export class PipelineWebsocketManager {
  private socket: WebSocket | null = null;
  private disposed = false;
  private reconnectTimer: number | undefined;
  private reconnectAttempt = 0;
  private connectPromise: Promise<void> | undefined;
  private readonly seenEventIds = new Set<string>();
  private readonly maxReconnectDelayMs: number;

  constructor(private readonly options: WebsocketManagerOptions) {
    this.maxReconnectDelayMs = options.maxReconnectDelayMs ?? 15_000;
  }

  async connect(): Promise<void> {
    if (this.disposed || this.socket?.readyState === WebSocket.OPEN || this.socket?.readyState === WebSocket.CONNECTING) return;
    if (this.connectPromise) return this.connectPromise;
    this.connectPromise = this.open().finally(() => { this.connectPromise = undefined; });
    return this.connectPromise;
  }

  close(): void {
    this.disposed = true;
    if (this.reconnectTimer !== undefined) window.clearTimeout(this.reconnectTimer);
    this.reconnectTimer = undefined;
    this.socket?.close(1000, "client closed");
    this.socket = null;
    this.options.onStatus?.("disconnected");
  }

  reset(): void {
    this.seenEventIds.clear();
    this.reconnectAttempt = 0;
  }

  private async open(): Promise<void> {
    this.options.onStatus?.(this.reconnectAttempt ? "reconnecting" : "connecting");
    const base = await resolveWebsocketBaseUrl();
    if (this.disposed) return;
    const url = new URL(`/ws/pipeline/${encodeURIComponent(this.options.sessionId)}`, `${base}/`);
    this.socket = new WebSocket(url);
    this.socket.onopen = () => {
      this.reconnectAttempt = 0;
      this.options.onStatus?.("connected");
    };
    this.socket.onmessage = (message) => {
      try {
        const parsed: unknown = JSON.parse(message.data as string);
        if (!isPipelineEvent(parsed)) {
          if (import.meta.env.DEV) console.warn("[yuzheng-ws] ignored invalid event", parsed);
          return;
        }
        if (parsed.session_id !== this.options.sessionId) return;
        if (this.seenEventIds.has(parsed.event_id)) return;
        this.seenEventIds.add(parsed.event_id);
        this.options.onEvent?.(parsed);
      } catch (error) {
        this.options.onError?.(error instanceof Error ? error : new Error("实时消息解析失败"));
      }
    };
    this.socket.onerror = () => {
      this.options.onStatus?.("failed");
      this.options.onError?.(new Error("实时连接发生错误"));
    };
    this.socket.onclose = () => {
      this.socket = null;
      if (this.disposed) return;
      this.options.onStatus?.("reconnecting");
      const delay = Math.min(500 * (2 ** this.reconnectAttempt), this.maxReconnectDelayMs);
      this.reconnectAttempt += 1;
      this.reconnectTimer = window.setTimeout(() => { void this.connect(); }, delay);
    };
  }
}
