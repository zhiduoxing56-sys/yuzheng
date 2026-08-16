import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../api/client";
import { executeTurn } from "../api/turns";
import type { ExecuteResult, ExecutionSubmissionStatus } from "../types/contract";
import { redactAuthorizationToken, requiresExecutionReconciliation } from "../utils/executionMapper";
import { invalidateTurnReads, readCache } from "../cache/readCache";

interface TokenHandle {
  turnId: string;
  value: string;
}

interface Options {
  turnId: string | null;
  sessionId: string;
  onSettled: () => Promise<void>;
  onResultUnknown: () => Promise<void>;
}

export function useTurnExecution({ turnId, sessionId, onSettled, onResultUnknown }: Options) {
  const tokenRef = useRef<TokenHandle | null>(null);
  const [tokenTurnId, setTokenTurnId] = useState<string | null>(null);
  const [status, setStatus] = useState<ExecutionSubmissionStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExecuteResult | null>(null);
  const writeLock = useRef(false);
  const mounted = useRef(true);
  const activeTurn = useRef(turnId);

  const clearAuthorization = useCallback(() => {
    tokenRef.current = null;
    if (mounted.current) setTokenTurnId(null);
  }, []);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
      tokenRef.current = null;
    };
  }, []);

  useEffect(() => {
    activeTurn.current = turnId;
    if (tokenRef.current && tokenRef.current.turnId !== turnId) clearAuthorization();
    setError(null);
    setResult(null);
    if (!writeLock.current) setStatus("idle");
  }, [turnId, clearAuthorization]);

  const acceptAuthorization = useCallback((authorizedTurnId: string, token: string) => {
    if (!mounted.current || !token) return;
    tokenRef.current = { turnId: authorizedTurnId, value: token };
    setTokenTurnId(authorizedTurnId);
  }, []);

  const requestConfirmation = useCallback((eligible: boolean) => {
    if (!eligible || writeLock.current) return;
    setError(null);
    setStatus("confirming");
  }, []);

  const closeConfirmation = useCallback(() => {
    if (!writeLock.current) setStatus("idle");
  }, []);

  const confirmExecution = useCallback(async (eligible: boolean) => {
    const requestTurnId = turnId;
    if (!eligible || !requestTurnId || tokenRef.current?.turnId !== requestTurnId || writeLock.current) return;
    let rawAuthorizationToken: string | null = tokenRef.current.value;
    writeLock.current = true;
    setStatus("submitting");
    setError(null);
    try {
      // Historical pages never manufacture an execution confirmation.  The
      // backend rejects this path until the active unified interaction has
      // supplied its identifier.
      const executionResult = await executeTurn(requestTurnId, rawAuthorizationToken, "", undefined, sessionId);
      rawAuthorizationToken = null;
      if (!mounted.current || activeTurn.current !== requestTurnId) return;
      invalidateTurnReads(requestTurnId);
      readCache.invalidatePrefix("audits:");
      if (executionResult.accepted || executionResult.token_status !== "ISSUED") clearAuthorization();
      setResult(executionResult);
      await onSettled();
      if (!mounted.current) return;
      setStatus(executionResult.accepted ? "completed" : "failed");
      if (!executionResult.accepted) setError(executionResult.reason);
    } catch (reason) {
      if (!mounted.current || activeTurn.current !== requestTurnId) return;
      const apiError = reason instanceof ApiError ? reason : null;
      if (requiresExecutionReconciliation(apiError?.kind)) {
        rawAuthorizationToken = null;
        setStatus("reconciling");
        await onResultUnknown();
        if (mounted.current) {
          setStatus("uncertain");
          setError("执行请求结果待确认，页面已重新查询后端工作流与时间线；请以最新状态为准。");
        }
      } else {
        const safeMessage = redactAuthorizationToken(reason instanceof Error ? reason.message : "执行请求失败", rawAuthorizationToken);
        rawAuthorizationToken = null;
        if (apiError?.status === 409) clearAuthorization();
        setError(safeMessage);
        setStatus("failed");
        await onSettled();
      }
    } finally {
      rawAuthorizationToken = null;
      writeLock.current = false;
    }
  }, [clearAuthorization, onResultUnknown, onSettled, sessionId, turnId]);

  const busy = status === "confirming" || status === "submitting" || status === "reconciling";
  return {
    status,
    error,
    result,
    busy,
    confirmationOpen: status === "confirming",
    hasAuthorizationToken: Boolean(turnId && tokenTurnId === turnId && tokenRef.current?.turnId === turnId),
    acceptAuthorization,
    requestConfirmation,
    closeConfirmation,
    confirmExecution,
  };
}
