import { useCallback, useEffect, useRef, useState } from "react";
import { readCache, type ReadSnapshot } from "../cache/readCache";

export function useCachedRead<T>(
  key: string | null,
  loader: (signal: AbortSignal) => Promise<T>,
  staleMs = 15_000,
) {
  const loaderRef = useRef(loader);
  loaderRef.current = loader;
  const [snapshot, setSnapshot] = useState<ReadSnapshot<T>>(
    () => key ? readCache.snapshot<T>(key) : { data: null, loading: false, error: null, updatedAt: 0 },
  );

  useEffect(() => {
    if (!key) {
      setSnapshot({ data: null, loading: false, error: null, updatedAt: 0 });
      return;
    }
    const update = () => setSnapshot(readCache.snapshot<T>(key));
    update();
    const unsubscribe = readCache.subscribe(key, update);
    void readCache.load(key, (signal) => loaderRef.current(signal), { staleMs }).catch(() => undefined);
    return unsubscribe;
  }, [key, staleMs]);

  const refresh = useCallback(() => {
    if (!key) return Promise.resolve(null);
    return readCache.load(key, (signal) => loaderRef.current(signal), { force: true, staleMs });
  }, [key, staleMs]);

  return { ...snapshot, refresh };
}
