import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../api/client";
import { getTurnPresentation } from "../api/turns";
import type { TurnPresentationResponse } from "../types/contract";
import { adaptTurnPresentation } from "../adapters/turnPresentationAdapter";

export function useEvidenceTurn(turnId: string | null) {
  const [data, setData] = useState<TurnPresentationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);
  const retry = useCallback(() => setNonce((value) => value + 1), []);

  useEffect(() => {
    if (!turnId) {
      setData(null);
      setLoading(false);
      setError(null);
      return;
    }
    const controller = new AbortController();
    setData(null);
    setLoading(true);
    setError(null);
    void getTurnPresentation(turnId, controller.signal).then((result) => {
      if (!controller.signal.aborted) setData(adaptTurnPresentation(result));
    }).catch((reason) => {
      if (controller.signal.aborted || (reason instanceof ApiError && reason.kind === "CANCELLED")) return;
      setError(reason instanceof Error ? reason.message : "轮次展示加载失败");
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [turnId, nonce]);

  return { data, loading, error, retry };
}
