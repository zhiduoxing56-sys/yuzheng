import { useCallback, useEffect, useRef, useState } from "react";
import { verifyTurnWorkflowChain } from "../api/turns";
import type { WorkflowChainVerification } from "../types/contract";

export function useWorkflowChainVerification(turnId: string | null) {
  const [data, setData] = useState<WorkflowChainVerification | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verifiedAt, setVerifiedAt] = useState<Date | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const cancel = useCallback(() => controllerRef.current?.abort(), []);
  useEffect(() => { cancel(); setData(null); setError(null); setVerifiedAt(null); }, [turnId, cancel]);
  useEffect(() => cancel, [cancel]);

  const load = useCallback(async (targetTurnId: string, parentSignal: AbortSignal) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    const abort = () => controller.abort(parentSignal.reason);
    parentSignal.addEventListener("abort", abort, { once: true });
    setLoading(true);
    setError(null);
    try {
      const result = await verifyTurnWorkflowChain(targetTurnId, controller.signal);
      if (!controller.signal.aborted) {
        setData(result);
        setVerifiedAt(new Date());
      }
      return controller.signal.aborted ? null : result;
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "工作流链校验失败");
      return null;
    } finally {
      parentSignal.removeEventListener("abort", abort);
      if (!controller.signal.aborted) setLoading(false);
    }
  }, []);

  return { data, loading, error, verifiedAt, load, cancel };
}
