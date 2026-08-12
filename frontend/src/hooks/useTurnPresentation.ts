import { ApiError } from "../api/client";
import { getTurnPresentation } from "../api/turns";
import { adaptTurnPresentation } from "../adapters/turnPresentationAdapter";
import { readKeys } from "../cache/readCache";
import { useCachedRead } from "./useCachedRead";

export function useTurnPresentation(turnId: string | null) {
  const cached = useCachedRead(
    turnId ? readKeys.presentation(turnId) : null,
    async (signal) => adaptTurnPresentation(await getTurnPresentation(turnId!, signal)),
  );
  return {
    data: cached.data,
    loading: cached.loading,
    error: cached.error?.message ?? null,
    exhausted: cached.error instanceof ApiError && cached.error.kind === "NOT_FOUND",
    retry: cached.refresh,
  };
}
