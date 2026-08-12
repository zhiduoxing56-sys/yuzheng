import { getTurnEvidence } from "../api/evidence";
import { readKeys } from "../cache/readCache";
import { useCachedRead } from "./useCachedRead";

export function useEvidenceSubgraph(turnId: string | null) {
  const cached = useCachedRead(
    turnId ? readKeys.evidence(turnId) : null,
    (signal) => getTurnEvidence(turnId!, signal),
    30_000,
  );
  return { data: cached.data, loading: cached.loading, error: cached.error?.message ?? null, retry: cached.refresh };
}
