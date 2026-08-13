import { createContext, useCallback, useContext, useMemo, useState, type PropsWithChildren } from "react";
import type { ConnectionStatus, DecisionLabel, PipelineEvent } from "../types/contract";
import { clearCommandSession } from "../utils/commandSessionStorage";

const SESSION_STORAGE_KEY = "yuzheng.v2.session.id";
const ACTIVE_TURN_STORAGE_KEY = "yuzheng.v2.turn.active";
const LEGACY_SESSION_KEY = "yuzheng.session.id";
const LEGACY_CURRENT_TURN_KEY = "yuzheng.turn.current";
const LEGACY_RECENT_TURNS_KEY = "yuzheng.turn.recent";
const MIGRATION_KEY = "yuzheng.v2.migration.complete";
const RECENT_MIGRATION_KEY = "yuzheng.v2.recent-migration.complete";
const MAX_RECENT_TURNS = 8;
const MAX_PIPELINE_EVENTS_PER_TURN = 120;
const MAX_PIPELINE_EVENT_TURNS = 12;
const MAX_PIPELINE_EVENTS_TOTAL = 600;

export interface CoordinatedTurnChild {
  clauseIndex: number;
  clauseText: string;
  turnId: string;
}

export interface CoordinatedTurnGroup {
  parentTurnId: string;
  children: CoordinatedTurnChild[];
}

function createSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `session-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

function readStoredString(key: string): string | null {
  try { return window.localStorage.getItem(key); } catch { return null; }
}

function writeStoredString(key: string, value: string | null): void {
  try {
    if (value === null) window.localStorage.removeItem(key);
    else window.localStorage.setItem(key, value);
  } catch { /* localStorage is optional */ }
}

function readSessionId(): string {
  const stored = readStoredString(SESSION_STORAGE_KEY);
  if (stored) return stored;
  const legacy = readStoredString(LEGACY_SESSION_KEY)?.trim();
  const created = legacy || createSessionId();
  writeStoredString(SESSION_STORAGE_KEY, created);
  return created;
}

function validTurnId(value: unknown): value is string {
  return typeof value === "string" && /^TURN_[A-Za-z0-9_-]+$/.test(value.trim());
}

function migrateLegacyState(): void {
  if (!readStoredString(MIGRATION_KEY)) {
    const legacyCurrent = readStoredString(LEGACY_CURRENT_TURN_KEY);
    if (!readStoredString(ACTIVE_TURN_STORAGE_KEY) && validTurnId(legacyCurrent)) writeStoredString(ACTIVE_TURN_STORAGE_KEY, legacyCurrent.trim());
    writeStoredString(MIGRATION_KEY, "1");
  }
  if (!readStoredString(RECENT_MIGRATION_KEY)) {
    try {
      const parsed: unknown = JSON.parse(readStoredString(LEGACY_RECENT_TURNS_KEY) || "[]");
      if (Array.isArray(parsed)) writeRecentTurns(readSessionId(), parsed.filter(validTurnId).slice(0, MAX_RECENT_TURNS).map((turnId) => ({ turnId, instructionSummary: null, decision: null, createdAt: null })));
    } catch { /* discard unsafe legacy value */ }
    writeStoredString(RECENT_MIGRATION_KEY, "1");
  }
  writeStoredString(LEGACY_SESSION_KEY, null);
  writeStoredString(LEGACY_CURRENT_TURN_KEY, null);
  writeStoredString(LEGACY_RECENT_TURNS_KEY, null);
}

export interface RecentTurnSummary { turnId: string; instructionSummary: string | null; decision: DecisionLabel | null; createdAt: string | null; }

function recentTurnsKey(sessionId: string): string { return `yuzheng.v2.turn.recent.${sessionId}`; }
function coordinatedTurnGroupKey(sessionId: string): string { return `yuzheng.v2.turn.coordinated.${sessionId}`; }

function readCoordinatedTurnGroup(sessionId: string): CoordinatedTurnGroup | null {
  try {
    const parsed: unknown = JSON.parse(window.sessionStorage.getItem(coordinatedTurnGroupKey(sessionId)) || "null");
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return null;
    const group = parsed as { parentTurnId?: unknown; children?: unknown };
    if (typeof group.parentTurnId !== "string" || !Array.isArray(group.children)) return null;
    const children = group.children.filter((item): item is CoordinatedTurnChild => Boolean(item)
      && typeof item === "object"
      && Number.isInteger((item as CoordinatedTurnChild).clauseIndex)
      && typeof (item as CoordinatedTurnChild).clauseText === "string"
      && validTurnId((item as CoordinatedTurnChild).turnId));
    return children.length ? { parentTurnId: group.parentTurnId, children } : null;
  } catch { return null; }
}

function writeCoordinatedTurnGroup(sessionId: string, group: CoordinatedTurnGroup | null): void {
  try {
    if (group) window.sessionStorage.setItem(coordinatedTurnGroupKey(sessionId), JSON.stringify(group));
    else window.sessionStorage.removeItem(coordinatedTurnGroupKey(sessionId));
  } catch { /* sessionStorage is optional */ }
}

function readRecentTurns(sessionId: string): RecentTurnSummary[] {
  try {
    const parsed: unknown = JSON.parse(window.sessionStorage.getItem(recentTurnsKey(sessionId)) || "[]");
    return Array.isArray(parsed) ? parsed.filter((item): item is RecentTurnSummary => Boolean(item) && typeof item === "object" && validTurnId((item as RecentTurnSummary).turnId)).slice(0, MAX_RECENT_TURNS) : [];
  } catch { return []; }
}

function writeRecentTurns(sessionId: string, value: RecentTurnSummary[]): void { try { window.sessionStorage.setItem(recentTurnsKey(sessionId), JSON.stringify(value)); } catch { /* optional */ } }

export interface SessionState {
  sessionId: string;
  sessionEpoch: number;
  activeTurnId: string | null;
  recentTurnIds: string[];
  recentTurns: RecentTurnSummary[];
  websocketStatus: ConnectionStatus;
  eventsByTurn: Record<string, PipelineEvent[]>;
  coordinatedTurnGroup: CoordinatedTurnGroup | null;
  newSession: () => void;
  setActiveTurn: (turnId: string | null, summary?: Omit<RecentTurnSummary, "turnId">) => void;
  setCoordinatedTurnGroup: (group: CoordinatedTurnGroup | null) => void;
  updateCoordinatedTurnChild: (clauseIndex: number, child: Omit<CoordinatedTurnChild, "clauseIndex">) => void;
  getPipelineEvents: (turnId: string) => PipelineEvent[];
  addPipelineEvent: (event: PipelineEvent) => void;
  clearPipelineEventsForTurn: (turnId: string) => void;
  clearAllPipelineEvents: () => void;
  setWebsocketStatus: (status: ConnectionStatus) => void;
}

const SessionContext = createContext<SessionState | null>(null);

export function SessionProvider({ children }: PropsWithChildren) {
  migrateLegacyState();
  const [sessionId, setSessionId] = useState(readSessionId);
  const [sessionEpoch, setSessionEpoch] = useState(0);
  const [activeTurnId, setActiveTurnIdState] = useState<string | null>(() => {
    const stored = readStoredString(ACTIVE_TURN_STORAGE_KEY);
    return validTurnId(stored) ? stored : null;
  });
  const [recentTurns, setRecentTurns] = useState<RecentTurnSummary[]>(() => readRecentTurns(readSessionId()));
  const recentTurnIds = useMemo(() => recentTurns.map((item) => item.turnId), [recentTurns]);
  const [websocketStatus, setWebsocketStatus] = useState<ConnectionStatus>("disconnected");
  const [eventsByTurn, setEventsByTurn] = useState<Record<string, PipelineEvent[]>>({});
  const [coordinatedTurnGroup, setCoordinatedTurnGroupState] = useState<CoordinatedTurnGroup | null>(() => readCoordinatedTurnGroup(readSessionId()));

  const setCoordinatedTurnGroup = useCallback((group: CoordinatedTurnGroup | null) => {
    setCoordinatedTurnGroupState(group);
    writeCoordinatedTurnGroup(sessionId, group);
  }, [sessionId]);

  const updateCoordinatedTurnChild = useCallback((clauseIndex: number, child: Omit<CoordinatedTurnChild, "clauseIndex">) => {
    setCoordinatedTurnGroupState((current) => {
      if (!current) return current;
      const next = {
        ...current,
        children: current.children.map((item) => item.clauseIndex === clauseIndex ? { clauseIndex, ...child } : item),
      };
      writeCoordinatedTurnGroup(sessionId, next);
      return next;
    });
  }, [sessionId]);

  const setActiveTurn = useCallback((turnId: string | null, summary?: Omit<RecentTurnSummary, "turnId">) => {
    if (turnId !== null && !validTurnId(turnId)) return;
    setActiveTurnIdState(turnId);
    writeStoredString(ACTIVE_TURN_STORAGE_KEY, turnId);
    if (!turnId) return;
    setRecentTurns((items) => {
      const existing = items.find((item) => item.turnId === turnId);
      const nextItem: RecentTurnSummary = { turnId, instructionSummary: summary?.instructionSummary ?? existing?.instructionSummary ?? null, decision: summary?.decision ?? existing?.decision ?? null, createdAt: summary?.createdAt ?? existing?.createdAt ?? null };
      const next = [nextItem, ...items.filter((item) => item.turnId !== turnId)].slice(0, MAX_RECENT_TURNS);
      writeRecentTurns(sessionId, next);
      return next;
    });
  }, [sessionId]);

  const newSession = useCallback(() => {
    clearCommandSession(sessionId);
    const created = createSessionId();
    writeStoredString(SESSION_STORAGE_KEY, created);
    writeStoredString(ACTIVE_TURN_STORAGE_KEY, null);
    try { window.sessionStorage.removeItem(recentTurnsKey(sessionId)); } catch { /* optional */ }
    writeCoordinatedTurnGroup(sessionId, null);
    setSessionId(created);
    setSessionEpoch((value) => value + 1);
    setActiveTurnIdState(null);
    setRecentTurns([]);
    setEventsByTurn({});
    setCoordinatedTurnGroupState(null);
    setWebsocketStatus("disconnected");
  }, [sessionId]);

  const addPipelineEvent = useCallback((event: PipelineEvent) => {
    if (!event.turn_id) return;
    setEventsByTurn((current) => {
      const existing = current[event.turn_id] ?? [];
      if (existing.some((item) => item.event_id === event.event_id)) return current;
      const nextForTurn = [...existing, event]
        .sort((left, right) => left.sequence - right.sequence)
        .slice(-MAX_PIPELINE_EVENTS_PER_TURN);
      const next = { ...current, [event.turn_id]: nextForTurn };
      const retainedTurns = Object.entries(next)
        .sort(([, left], [, right]) => {
          const leftTime = Date.parse(left.at(-1)?.timestamp ?? "") || left.at(-1)?.sequence || 0;
          const rightTime = Date.parse(right.at(-1)?.timestamp ?? "") || right.at(-1)?.sequence || 0;
          return rightTime - leftTime;
        })
        .slice(0, MAX_PIPELINE_EVENT_TURNS);
      const bounded = Object.fromEntries(retainedTurns);
      const flattened = Object.entries(bounded)
        .flatMap(([turnId, events]) => events.map((item) => ({ turnId, item })))
        .sort((left, right) => {
          const leftTime = Date.parse(left.item.timestamp) || left.item.sequence;
          const rightTime = Date.parse(right.item.timestamp) || right.item.sequence;
          return rightTime - leftTime;
        })
        .slice(0, MAX_PIPELINE_EVENTS_TOTAL);
      const retainedIds = new Set(flattened.map(({ turnId, item }) => `${turnId}\u0000${item.event_id}`));
      return Object.fromEntries(Object.entries(bounded)
        .map(([turnId, events]) => [turnId, events.filter((item) => retainedIds.has(`${turnId}\u0000${item.event_id}`))])
        .filter(([, events]) => (events as PipelineEvent[]).length > 0));
    });
  }, []);

  const getPipelineEvents = useCallback((turnId: string) => eventsByTurn[turnId] ?? [], [eventsByTurn]);
  const clearPipelineEventsForTurn = useCallback((turnId: string) => setEventsByTurn((current) => {
    if (!(turnId in current)) return current;
    const next = { ...current };
    delete next[turnId];
    return next;
  }), []);
  const clearAllPipelineEvents = useCallback(() => setEventsByTurn({}), []);

  const value = useMemo<SessionState>(() => ({
    sessionId,
    sessionEpoch,
    activeTurnId,
    recentTurnIds,
    recentTurns,
    websocketStatus,
    eventsByTurn,
    coordinatedTurnGroup,
    newSession,
    setActiveTurn,
    setCoordinatedTurnGroup,
    updateCoordinatedTurnChild,
    getPipelineEvents,
    addPipelineEvent,
    clearPipelineEventsForTurn,
    clearAllPipelineEvents,
    setWebsocketStatus,
  }), [sessionId, sessionEpoch, activeTurnId, recentTurnIds, recentTurns, websocketStatus, eventsByTurn, coordinatedTurnGroup, newSession, setActiveTurn, setCoordinatedTurnGroup, updateCoordinatedTurnChild, getPipelineEvents, addPipelineEvent, clearPipelineEventsForTurn, clearAllPipelineEvents]);

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionState {
  const value = useContext(SessionContext);
  if (!value) throw new Error("useSession 必须在 SessionProvider 内使用");
  return value;
}
