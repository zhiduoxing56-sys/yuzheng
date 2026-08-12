import { useEffect, useState } from "react";
import { subscribePipelineSocket } from "../api/pipelineSocketRegistry";
import { useSession } from "../stores/sessionStore";

export function usePipelineSocket() {
  const { sessionId, addPipelineEvent, setWebsocketStatus } = useSession();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setError(null);
    return subscribePipelineSocket(sessionId, {
      onStatus: setWebsocketStatus,
      onEvent: addPipelineEvent,
      onError: (reason) => setError(reason.message),
    });
  }, [sessionId, addPipelineEvent, setWebsocketStatus]);

  return { error };
}
