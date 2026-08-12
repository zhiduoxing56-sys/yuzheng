import { useCallback, useEffect, useState } from "react";
import { getTurnPresentation, getTurnWorkflowStatus } from "../api/turns";
import { adaptTurnPresentation } from "../adapters/turnPresentationAdapter";
import { adaptWorkflowStatus } from "../adapters/workflowResponseAdapter";
import { readCache, readKeys } from "../cache/readCache";
import type { TurnPresentationResponse, TurnWorkflowStatus } from "../types/contract";

function message(reason: unknown, fallback: string): string {
  return reason instanceof Error ? reason.message : fallback;
}

export function useReviewTurn(turnId: string | null) {
  const [presentation, setPresentation] = useState<TurnPresentationResponse | null>(null);
  const [workflow, setWorkflow] = useState<TurnWorkflowStatus | null>(null);
  const [presentationLoading, setPresentationLoading] = useState(false);
  const [workflowLoading, setWorkflowLoading] = useState(false);
  const [presentationError, setPresentationError] = useState<string | null>(null);
  const [workflowError, setWorkflowError] = useState<string | null>(null);

  useEffect(() => {
    setPresentation(turnId ? readCache.snapshot<TurnPresentationResponse>(readKeys.presentation(turnId)).data : null);
    setWorkflow(turnId ? readCache.snapshot<TurnWorkflowStatus>(readKeys.workflow(turnId)).data : null);
    setPresentationError(null);
    setWorkflowError(null);
  }, [turnId]);

  const loadPresentation = useCallback(async (targetTurnId: string, parentSignal: AbortSignal, force = false) => {
    setPresentationLoading(true);
    setPresentationError(null);
    try {
      const result = await readCache.load(
        readKeys.presentation(targetTurnId),
        async (signal) => adaptTurnPresentation(await getTurnPresentation(targetTurnId, signal)),
        { force },
      );
      if (!parentSignal.aborted) setPresentation(result);
      return parentSignal.aborted ? null : result;
    } catch (reason) {
      if (!parentSignal.aborted) setPresentationError(message(reason, "轮次展示加载失败"));
      return null;
    } finally {
      if (!parentSignal.aborted) setPresentationLoading(false);
    }
  }, []);

  const loadWorkflow = useCallback(async (targetTurnId: string, parentSignal: AbortSignal, force = false) => {
    setWorkflowLoading(true);
    setWorkflowError(null);
    try {
      const result = await readCache.load(
        readKeys.workflow(targetTurnId),
        async (signal) => adaptWorkflowStatus(await getTurnWorkflowStatus(targetTurnId, signal)),
        { force },
      );
      if (!parentSignal.aborted) setWorkflow(result);
      return parentSignal.aborted ? null : result;
    } catch (reason) {
      if (!parentSignal.aborted) setWorkflowError(message(reason, "工作流状态加载失败"));
      return null;
    } finally {
      if (!parentSignal.aborted) setWorkflowLoading(false);
    }
  }, []);

  const cancel = useCallback(() => undefined, []);
  return { presentation, workflow, presentationLoading, workflowLoading, presentationError, workflowError, loadPresentation, loadWorkflow, cancel };
}
