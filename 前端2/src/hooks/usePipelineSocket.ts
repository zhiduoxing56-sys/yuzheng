import { useEffect, useState } from "react";
import { PipelineWebsocketManager } from "../api/websocket";
import { useSession } from "../stores/sessionStore";

const activeManagers = new Map<string, PipelineWebsocketManager>();

export function usePipelineSocket() {
  const { sessionId, addPipelineEvent, setWebsocketStatus } = useSession();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    activeManagers.get(sessionId)?.close();
    const manager = new PipelineWebsocketManager({
      sessionId,
      onStatus: setWebsocketStatus,
      onEvent: addPipelineEvent,
      onError: (reason) => setError(reason.message),
    });
    activeManagers.set(sessionId, manager);
    setError(null);
    void manager.connect();

    return () => {
      if (activeManagers.get(sessionId) === manager) activeManagers.delete(sessionId);
      manager.close();
    };
  }, [sessionId, addPipelineEvent, setWebsocketStatus]);

  return { error };
}
