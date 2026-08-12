import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../api/client";
import { submitTurnReview } from "../api/turns";
import type { ReviewAction, ReviewSubmission, ReviewSubmissionResponse, ReviewSubmissionStatus } from "../types/contract";
import { mapApiErrorMessage } from "../utils/mappers";
import { buildReviewSubmission, toSafeReviewResult, type SafeReviewResult } from "../utils/reviewMapper";
import { adaptReviewResponse } from "../adapters/reviewResponseAdapter";
import { invalidateTurnReads, readCache, readKeys } from "../cache/readCache";

interface Options {
  turnId: string | null;
  writable: boolean;
  onAuthorizationToken: (turnId: string, token: string) => void;
  onCompleted: (result: SafeReviewResult) => Promise<void>;
}

export function useReviewSubmission({ turnId, writable, onAuthorizationToken, onCompleted }: Options) {
  const [action, setActionState] = useState<ReviewAction>("CONFIRM");
  const [selectedCandidateId, setSelectedCandidateId] = useState("");
  const [correctedText, setCorrectedText] = useState("");
  const [status, setStatus] = useState<ReviewSubmissionStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [latestResult, setLatestResult] = useState<SafeReviewResult | null>(null);
  const pendingRequest = useRef<ReviewSubmission | null>(null);
  const writeLock = useRef(false);
  const mounted = useRef(true);
  const activeTurn = useRef(turnId);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);
  useEffect(() => {
    activeTurn.current = turnId;
    pendingRequest.current = null;
    setSelectedCandidateId("");
    setCorrectedText("");
    setError(null);
    if (!writeLock.current) setStatus("idle");
  }, [turnId]);

  const busy = status === "validating" || status === "confirming" || status === "submitting" || status === "refreshing";

  const setAction = useCallback((nextAction: ReviewAction) => {
    if (!writeLock.current) {
      setActionState(nextAction);
      setError(null);
    }
  }, []);

  const perform = useCallback(async (request: ReviewSubmission) => {
    const requestTurnId = turnId;
    if (!requestTurnId || writeLock.current || !writable) return;
    writeLock.current = true;
    pendingRequest.current = null;
    setStatus("submitting");
    setError(null);

    let response: ReviewSubmissionResponse | null = null;
    let authorizationToken: string | null | undefined;
    try {
      response = adaptReviewResponse(await submitTurnReview(requestTurnId, request));
      if (!mounted.current || activeTurn.current !== requestTurnId) return;

      invalidateTurnReads(requestTurnId);
      invalidateTurnReads(response.related_turn_id);
      readCache.invalidate(readKeys.audit(response.audit_id));
      readCache.invalidatePrefix("audits:");

      authorizationToken = response.decision.authorization_token;
      if (authorizationToken) onAuthorizationToken(response.related_turn_id, authorizationToken);
      authorizationToken = null;

      const safeResult = toSafeReviewResult(response);
      response = null;
      setStatus("refreshing");
      await onCompleted(safeResult);
      if (!mounted.current) return;
      setLatestResult(safeResult);
      setSelectedCandidateId("");
      setCorrectedText("");
      setStatus("completed");
    } catch (reason) {
      authorizationToken = null;
      response = null;
      if (!mounted.current || activeTurn.current !== requestTurnId) return;
      const apiError = reason instanceof ApiError ? reason : null;
      setError(mapApiErrorMessage(reason instanceof Error ? reason.message : "复核提交失败", apiError?.errorCode));
      setStatus("failed");
    } finally {
      authorizationToken = null;
      response = null;
      writeLock.current = false;
    }
  }, [turnId, writable, onAuthorizationToken, onCompleted]);

  const submit = useCallback((requestedAction: ReviewAction = action) => {
    if (!turnId || writeLock.current || busy || !writable) return;
    setStatus("validating");
    setError(null);
    const validation = buildReviewSubmission(requestedAction, { selectedCandidateId, correctedText });
    if (!validation.valid) {
      setError(validation.message);
      setStatus("failed");
      return;
    }
    if (requestedAction === "CANCEL") {
      pendingRequest.current = validation.request;
      setStatus("confirming");
      return;
    }
    void perform(validation.request);
  }, [action, busy, correctedText, perform, selectedCandidateId, turnId, writable]);

  const confirmCancellation = useCallback(() => {
    const request = pendingRequest.current;
    if (request?.action !== "CANCEL") return;
    void perform(request);
  }, [perform]);

  const closeConfirmation = useCallback(() => {
    if (writeLock.current) return;
    pendingRequest.current = null;
    setStatus("idle");
  }, []);

  return {
    action,
    selectedCandidateId,
    correctedText,
    status,
    error,
    latestResult,
    busy,
    cancellationConfirmationOpen: status === "confirming" && pendingRequest.current?.action === "CANCEL",
    setAction,
    setSelectedCandidateId,
    setCorrectedText,
    submit,
    confirmCancellation,
    closeConfirmation,
  };
}
