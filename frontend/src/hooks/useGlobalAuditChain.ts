import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../api/client";
import { verifyGlobalAuditChain } from "../api/audits";
import { adaptGlobalAuditChain, type GlobalAuditChainView } from "../adapters/auditResponseAdapter";

interface AuditChainSessionSnapshot {
  data: GlobalAuditChainView | null;
  error: string | null;
  verifiedAt: Date | null;
}

let sessionSnapshot: AuditChainSessionSnapshot = {
  data: null,
  error: null,
  verifiedAt: null,
};

export function useGlobalAuditChain() {
  const [data, setData] = useState<GlobalAuditChainView | null>(sessionSnapshot.data);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(sessionSnapshot.error);
  const [verifiedAt, setVerifiedAt] = useState<Date | null>(sessionSnapshot.verifiedAt);
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
    sessionSnapshot = { ...sessionSnapshot, error: null };
    setError(null);
    void verifyGlobalAuditChain(controller.signal).then((result) => {
      if (!controller.signal.aborted && id === requestId.current) {
        const verifiedAt = new Date();
        const data = adaptGlobalAuditChain(result);
        sessionSnapshot = { data, error: null, verifiedAt };
        setData(data);
        setVerifiedAt(verifiedAt);
      }
    }).catch((reason) => {
      if (controller.signal.aborted || reason instanceof ApiError && reason.kind === "CANCELLED") return;
      if (id === requestId.current) {
        const error = reason instanceof Error ? reason.message : "全局审计链校验失败";
        sessionSnapshot = { ...sessionSnapshot, error };
        setError(error);
      }
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
