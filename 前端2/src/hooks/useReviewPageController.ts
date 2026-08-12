import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../stores/sessionStore";
import { getExecutionEligibility } from "../utils/executionMapper";
import { isCurrentTurnWritable } from "../utils/workflowMapper";
import { getReviewNavigation, type SafeReviewResult } from "../utils/reviewMapper";
import { useHealthStatus } from "./useHealthStatus";
import { useReviewSubmission } from "./useReviewSubmission";
import { useReviewTimeline } from "./useReviewTimeline";
import { useReviewTurn } from "./useReviewTurn";
import { useTurnExecution } from "./useTurnExecution";
import { useWorkflowChainVerification } from "./useWorkflowChainVerification";

export function useReviewPageController(routeTurnId?: string) {
  const turnId = routeTurnId?.trim() || null;
  const navigate = useNavigate();
  const { sessionId, activeTurnId, setActiveTurn } = useSession();
  const turn = useReviewTurn(turnId);
  const timeline = useReviewTimeline(turnId);
  const chain = useWorkflowChainVerification(turnId);
  const health = useHealthStatus();
  const readController = useRef<AbortController | null>(null);
  const activeTurn = useRef(turnId);
  const [refreshing, setRefreshing] = useState(false);
  activeTurn.current = turnId;

  const cancelReads = useCallback(() => {
    readController.current?.abort();
    turn.cancel();
    timeline.cancel();
    chain.cancel();
  }, [turn.cancel, timeline.cancel, chain.cancel]);

  const loadCore = useCallback(async (targetTurnId: string, force: boolean) => {
    readController.current?.abort();
    const controller = new AbortController();
    readController.current = controller;
    await Promise.allSettled([
      turn.loadPresentation(targetTurnId, controller.signal, force),
      turn.loadWorkflow(targetTurnId, controller.signal, force),
      timeline.load(targetTurnId, controller.signal, force),
    ]);
  }, [timeline.load, turn.loadPresentation, turn.loadWorkflow]);

  const refreshAll = useCallback(async (targetTurnId = turnId) => {
    if (!targetTurnId) return;
    setRefreshing(true);
    try {
      await loadCore(targetTurnId, true);
    } finally {
      if (activeTurn.current === targetTurnId) setRefreshing(false);
    }
  }, [loadCore, turnId]);

  useEffect(() => {
    if (!turnId) {
      cancelReads();
      setRefreshing(false);
      return;
    }
    setRefreshing(true);
    void loadCore(turnId, false).finally(() => {
      if (activeTurn.current === turnId) setRefreshing(false);
    });
    return cancelReads;
  }, [turnId, loadCore, cancelReads]);

  const execution = useTurnExecution({
    turnId,
    sessionId,
    onSettled: refreshAll,
    onResultUnknown: refreshAll,
  });

  const handleReviewCompleted = useCallback(async (result: SafeReviewResult) => {
    const navigation = getReviewNavigation(result, turnId);
    if (navigation.changed) {
      setActiveTurn(navigation.turnId, { instructionSummary: null, decision: result.newDecision === "PASS" || result.newDecision === "REVIEW" || result.newDecision === "BLOCK" ? result.newDecision : null, createdAt: new Date().toISOString() });
      navigate(navigation.path, { replace: navigation.replace });
      cancelReads();
      return;
    }
    await refreshAll(turnId);
  }, [cancelReads, navigate, refreshAll, setActiveTurn, turnId]);

  const writable = Boolean(turnId && activeTurnId === turnId && isCurrentTurnWritable(turnId, turn.presentation, turn.workflow));
  const submission = useReviewSubmission({
    turnId,
    writable,
    onAuthorizationToken: execution.acceptAuthorization,
    onCompleted: handleReviewCompleted,
  });

  const executionEligibility = useMemo(() => getExecutionEligibility({
    turnId: turnId || "",
    presentation: turn.presentation,
    workflow: turn.workflow,
    hasAuthorizationToken: execution.hasAuthorizationToken,
    writeBusy: submission.busy || execution.busy,
  }), [turnId, turn.presentation, turn.workflow, execution.hasAuthorizationToken, submission.busy, execution.busy]);

  const requestExecution = useCallback(() => execution.requestConfirmation(executionEligibility.allowed), [execution, executionEligibility.allowed]);
  const confirmExecution = useCallback(() => { void execution.confirmExecution(executionEligibility.allowed); }, [execution, executionEligibility.allowed]);

  return {
    turnId,
    turn,
    timeline,
    chain,
    health,
    submission,
    execution,
    executionEligibility,
    writable,
    activeTurnId,
    refreshing,
    refreshAll: () => refreshAll(turnId),
    refreshChain: () => {
      if (!turnId) return Promise.resolve(null);
      const controller = new AbortController();
      return chain.load(turnId, controller.signal);
    },
    requestExecution,
    confirmExecution,
  };
}
