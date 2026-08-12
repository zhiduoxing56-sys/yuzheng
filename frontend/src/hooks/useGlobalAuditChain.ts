import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../api/client";
import { verifyGlobalAuditChain } from "../api/audits";
import { adaptGlobalAuditChain, type GlobalAuditChainView } from "../adapters/auditResponseAdapter";

export function useGlobalAuditChain() {
  const [data, setData] = useState<GlobalAuditChainView | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verifiedAt, setVerifiedAt] = useState<Date | null>(null);
  const requestId = useRef(0);
  const controllerRef = useRef<AbortController | null>(null);
  const runningRef = useRef(false);

  const refresh = useCallback(() => {
    if (runningRef.current) return;
    runningRef.current = true;
    const id = ++requestId.current;
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);
    setError(null);
    void verifyGlobalAuditChain(controller.signal).then((result) => {
      if (!controller.signal.aborted && id === requestId.current) {
        setData(adaptGlobalAuditChain(result));
        setVerifiedAt(new Date());
      }
    }).catch((reason) => {
      if (controller.signal.aborted || reason instanceof ApiError && reason.kind === "CANCELLED") return;
      if (id === requestId.current) setError(reason instanceof Error ? reason.message : "全局审计链校验失败");
    }).finally(() => {
      if (id === requestId.current) {
        runningRef.current = false;
        if (!controller.signal.aborted) setLoading(false);
      }
    });
  }, []);

  useEffect(() => () => controllerRef.current?.abort(), []);

  return { data, loading, error, verifiedAt, refresh };
}
