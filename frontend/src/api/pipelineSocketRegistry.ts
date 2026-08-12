import { PipelineWebsocketManager } from "./websocket";
import type { ConnectionStatus, PipelineEvent } from "../types/contract";

export interface PipelineSocketSubscriber {
  onStatus: (status: ConnectionStatus) => void;
  onEvent: (event: PipelineEvent) => void;
  onError: (error: Error) => void;
}

interface SharedPipelineSocket {
  manager: PipelineWebsocketManager;
  subscribers: Map<symbol, PipelineSocketSubscriber>;
  status: ConnectionStatus;
  closeTimer: number | null;
}

const sharedSockets = new Map<string, SharedPipelineSocket>();

function createSharedSocket(sessionId: string): SharedPipelineSocket {
  const shared = {
    manager: null as unknown as PipelineWebsocketManager,
    subscribers: new Map<symbol, PipelineSocketSubscriber>(),
    status: "disconnected" as ConnectionStatus,
    closeTimer: null,
  };
  shared.manager = new PipelineWebsocketManager({
    sessionId,
    onStatus: (status) => {
      shared.status = status;
      shared.subscribers.forEach((subscriber) => subscriber.onStatus(status));
    },
    onEvent: (event) => shared.subscribers.forEach((subscriber) => subscriber.onEvent(event)),
    onError: (error) => shared.subscribers.forEach((subscriber) => subscriber.onError(error)),
  });
  sharedSockets.set(sessionId, shared);
  return shared;
}

export function subscribePipelineSocket(sessionId: string, subscriber: PipelineSocketSubscriber): () => void {
  const shared = sharedSockets.get(sessionId) ?? createSharedSocket(sessionId);
  if (shared.closeTimer !== null) {
    window.clearTimeout(shared.closeTimer);
    shared.closeTimer = null;
  }
  const subscriptionId = Symbol(sessionId);
  shared.subscribers.set(subscriptionId, subscriber);
  subscriber.onStatus(shared.status);
  void shared.manager.connect();

  let released = false;
  return () => {
    if (released) return;
    released = true;
    shared.subscribers.delete(subscriptionId);
    if (shared.subscribers.size > 0 || shared.closeTimer !== null) return;
    // React StrictMode immediately mounts the same subscriber again. Deferring
    // final disposal by one task lets that remount reuse the existing socket.
    shared.closeTimer = window.setTimeout(() => {
      shared.closeTimer = null;
      if (shared.subscribers.size > 0 || sharedSockets.get(sessionId) !== shared) return;
      sharedSockets.delete(sessionId);
      shared.manager.close();
    }, 0);
  };
}
