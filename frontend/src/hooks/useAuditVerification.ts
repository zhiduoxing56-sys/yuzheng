import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../api/client";
import { verifyAudit } from "../api/audits";
import type { AuditVerificationResponse } from "../types/contract";
import { adaptAuditVerification } from "../adapters/auditResponseAdapter";

export function useAuditVerification(auditId: string | null) {
  const [data, setData] = useState<AuditVerificationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verifiedAt, setVerifiedAt] = useState<Date | null>(null);
  const [nonce, setNonce] = useState(0);
  const requestId = useRef(0);
  const refresh = useCallback(() => setNonce((value) => value + 1), []);

  useEffect(() => {
    const id = ++requestId.current;
    setData(null);
    setError(null);
    setVerifiedAt(null);
    if (!auditId) { setLoading(false); return; }
    const controller = new AbortController();
    setLoading(true);
    void verifyAudit(auditId, controller.signal).then((result) => {
      if (!controller.signal.aborted && id === requestId.current) {
        setData(adaptAuditVerification(result));
        setVerifiedAt(new Date());
      }
    }).catch((reason) => {
      if (controller.signal.aborted || reason instanceof ApiError && reason.kind === "CANCELLED") return;
      if (id === requestId.current) setError(reason instanceof Error ? reason.message : "单条审计校验失败");
    }).finally(() => {
      if (!controller.signal.aborted && id === requestId.current) setLoading(false);
    });
    return () => controller.abort();
  }, [auditId, nonce]);

  return { data, loading, error, verifiedAt, refresh };
}
