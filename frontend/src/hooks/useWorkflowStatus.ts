import { getTurnWorkflowStatus } from "../api/turns";
import { adaptWorkflowStatus } from "../adapters/workflowResponseAdapter";
import { readKeys } from "../cache/readCache";
import { useCachedRead } from "./useCachedRead";

export function useWorkflowStatus(turnId: string | null, _refreshKey?: string | null) {
  const cached = useCachedRead(
    turnId ? readKeys.workflow(turnId) : null,
    async (signal) => adaptWorkflowStatus(await getTurnWorkflowStatus(turnId!, signal)),
  );
  return { data: cached.data, loading: cached.loading, error: cached.error?.message ?? null, refresh: cached.refresh };
}
