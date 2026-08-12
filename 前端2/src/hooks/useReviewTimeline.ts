import { useCallback, useEffect, useState } from "react";
import { getTurnTimeline } from "../api/turns";
import { adaptTimeline } from "../adapters/workflowResponseAdapter";
import { readCache, readKeys } from "../cache/readCache";
import type { TimelineResponse } from "../types/contract";

export function useReviewTimeline(turnId: string | null) {
  const [data, setData] = useState<TimelineResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setData(turnId ? readCache.snapshot<TimelineResponse>(readKeys.timeline(turnId)).data : null);
    setError(null);
  }, [turnId]);

  const load = useCallback(async (targetTurnId: string, parentSignal: AbortSignal, force = false) => {
    setLoading(true);
    setError(null);
    try {
      const result = await readCache.load(
        readKeys.timeline(targetTurnId),
        async (signal) => adaptTimeline(await getTurnTimeline(targetTurnId, signal)),
        { force },
      );
      if (!parentSignal.aborted) setData(result);
      return parentSignal.aborted ? null : result;
    } catch (reason) {
      if (!parentSignal.aborted) setError(reason instanceof Error ? reason.message : "时间线加载失败");
      return null;
    } finally {
      if (!parentSignal.aborted) setLoading(false);
    }
  }, []);

  const cancel = useCallback(() => undefined, []);
  return { data, loading, error, load, cancel };
}
