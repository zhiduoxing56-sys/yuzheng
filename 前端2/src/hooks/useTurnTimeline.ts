import { getTurnTimeline } from "../api/turns";
import { adaptTimeline } from "../adapters/workflowResponseAdapter";
import { readKeys } from "../cache/readCache";
import { useCachedRead } from "./useCachedRead";

export function useTurnTimeline(turnId: string | null, _refreshKey?: string | null) {
  const cached = useCachedRead(
    turnId ? readKeys.timeline(turnId) : null,
    async (signal) => adaptTimeline(await getTurnTimeline(turnId!, signal)),
  );
  return { data: cached.data, loading: cached.loading, error: cached.error?.message ?? null, refresh: cached.refresh };
}
