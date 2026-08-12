export interface ReadSnapshot<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  updatedAt: number;
}

interface CacheEntry<T = unknown> {
  data?: T;
  error: Error | null;
  updatedAt: number;
  touchedAt: number;
  revision: number;
  promise: Promise<T> | null;
  controller: AbortController | null;
  listeners: Set<() => void>;
}

type Loader<T> = (signal: AbortSignal) => Promise<T>;

const MAX_ENTRIES = 64;
const entries = new Map<string, CacheEntry>();

function entryFor<T>(key: string): CacheEntry<T> {
  let entry = entries.get(key) as CacheEntry<T> | undefined;
  if (!entry) {
    entry = { error: null, updatedAt: 0, touchedAt: Date.now(), revision: 0, promise: null, controller: null, listeners: new Set() };
    entries.set(key, entry);
  }
  entry.touchedAt = Date.now();
  return entry;
}

function notify(entry: CacheEntry): void {
  entry.listeners.forEach((listener) => listener());
}

function trim(): void {
  if (entries.size <= MAX_ENTRIES) return;
  const candidates = [...entries.entries()]
    .filter(([, entry]) => !entry.promise && entry.listeners.size === 0)
    .sort((a, b) => a[1].touchedAt - b[1].touchedAt);
  while (entries.size > MAX_ENTRIES && candidates.length) entries.delete(candidates.shift()![0]);
}

export const readCache = {
  snapshot<T>(key: string): ReadSnapshot<T> {
    const entry = entryFor<T>(key);
    return { data: entry.data ?? null, loading: Boolean(entry.promise), error: entry.error, updatedAt: entry.updatedAt };
  },

  subscribe(key: string, listener: () => void): () => void {
    const entry = entryFor(key);
    entry.listeners.add(listener);
    return () => entry.listeners.delete(listener);
  },

  async load<T>(key: string, loader: Loader<T>, options: { force?: boolean; staleMs?: number } = {}): Promise<T> {
    const entry = entryFor<T>(key);
    const staleMs = options.staleMs ?? 15_000;
    if (entry.promise) return entry.promise;
    if (!options.force && entry.data !== undefined && Date.now() - entry.updatedAt < staleMs) return entry.data;

    const revision = ++entry.revision;
    const controller = new AbortController();
    entry.controller = controller;
    entry.error = null;
    const promise = loader(controller.signal);
    entry.promise = promise;
    notify(entry);
    try {
      const value = await promise;
      if (entry.revision === revision) {
        entry.data = value;
        entry.updatedAt = Date.now();
        entry.error = null;
      }
      return value;
    } catch (reason) {
      const error = reason instanceof Error ? reason : new Error("只读数据加载失败");
      if (entry.revision === revision && !controller.signal.aborted) entry.error = error;
      throw error;
    } finally {
      if (entry.revision === revision) {
        entry.promise = null;
        entry.controller = null;
        notify(entry);
      }
      trim();
    }
  },

  prefetch<T>(key: string, loader: Loader<T>, staleMs = 15_000): void {
    void this.load(key, loader, { staleMs }).catch(() => undefined);
  },

  invalidate(key: string): void {
    const entry = entries.get(key);
    if (!entry) return;
    entry.revision += 1;
    entry.updatedAt = 0;
    entry.controller?.abort("invalidated");
    entry.promise = null;
    entry.controller = null;
    notify(entry);
  },

  invalidatePrefix(prefix: string): void {
    [...entries.keys()].filter((key) => key.startsWith(prefix)).forEach((key) => this.invalidate(key));
  },

  clear(): void {
    [...entries.values()].forEach((entry) => entry.controller?.abort("cache cleared"));
    entries.clear();
  },
};

export const readKeys = {
  presentation: (turnId: string) => `presentation:${turnId}`,
  workflow: (turnId: string) => `workflow:${turnId}`,
  timeline: (turnId: string) => `timeline:${turnId}`,
  evidence: (turnId: string) => `evidence:${turnId}`,
  audits: (query: string) => `audits:${query}`,
  audit: (auditId: string) => `audit:${auditId}`,
};

export function invalidateTurnReads(turnId: string): void {
  readCache.invalidate(readKeys.presentation(turnId));
  readCache.invalidate(readKeys.workflow(turnId));
  readCache.invalidate(readKeys.timeline(turnId));
  readCache.invalidate(readKeys.evidence(turnId));
}
