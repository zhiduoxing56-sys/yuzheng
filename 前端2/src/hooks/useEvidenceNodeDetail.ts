import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../api/client";
import { getEvidenceNode } from "../api/evidence";
import type { EvidenceNodeDetail } from "../types/contract";

export function useEvidenceNodeDetail(turnId: string | null, nodeId: string | null) {
  const [data, setData] = useState<EvidenceNodeDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);
  const retry = useCallback(() => setNonce((value) => value + 1), []);

  useEffect(() => {
    if (!turnId || !nodeId) {
      setData(null);
      setLoading(false);
      setError(null);
      return;
    }
    const controller = new AbortController();
    setData(null);
    setLoading(true);
    setError(null);
    void getEvidenceNode(turnId, nodeId, controller.signal).then((result) => {
      if (!controller.signal.aborted) setData(result);
    }).catch((reason) => {
      if (controller.signal.aborted || (reason instanceof ApiError && reason.kind === "CANCELLED")) return;
      setError(reason instanceof Error ? reason.message : "节点详情加载失败");
    }).finally(() => {
      if (!controller.signal.aborted) setLoading(false);
    });
    return () => controller.abort();
  }, [turnId, nodeId, nonce]);

  return { data, loading, error, retry };
}
