import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../api/client";
import { getTurnReasoning } from "../api/turns";
import type { AdvancedReasoningResult } from "../types/contract";

export function useEvidenceReasoning(turnId: string | null, enabled: boolean) {
  const [data, setData] = useState<AdvancedReasoningResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);
  const retry = useCallback(() => setNonce((value) => value + 1), []);

  useEffect(() => {
    setData(null);
    setError(null);
  }, [turnId]);

  useEffect(() => {
    if (!turnId || !enabled || data) return;
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    void getTurnReasoning(turnId, controller.signal).then((result) => {
      if (!controller.signal.aborted) setData(result);
    }).catch((reason) => {
      if (controller.signal.aborted || (reason instanceof ApiError && reason.kind === "CANCELLED")) return;
      setError(reason instanceof Error ? reason.message : "高级推理暂不可用");
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [turnId, enabled, data, nonce]);

  return { data, loading, error, retry };
}
