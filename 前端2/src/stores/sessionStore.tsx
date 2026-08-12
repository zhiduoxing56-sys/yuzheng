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
const MAX_PIPELINE_EVENTS = 300;

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

function readRecentTurns(sessionId: string): RecentTurnSummary[] {
  try {
    const parsed: unknown = JSON.parse(window.sessionStorage.getItem(recentTurnsKey(sessionId)) || "[]");
    return Array.isArray(parsed) ? parsed.filter((item): item is RecentTurnSummary => Boolean(item) && typeof item === "object" && validTurnId((item as RecentTurnSummary).turnId)).slice(0, MAX_RECENT_TURNS) : [];
  } catch { return []; }
}

function writeRecentTurns(sessionId: string, value: RecentTurnSummary[]): void { try { window.sessionStorage.setItem(recentTurnsKey(sessionId), JSON.stringify(value)); } catch { /* optional */ } }

export interface SessionState {
  sessionId: string;
  activeTurnId: string | null;
  recentTurnIds: string[];
  recentTurns: RecentTurnSummary[];
  websocketStatus: ConnectionStatus;
  pipelineEvents: PipelineEvent[];
  newSession: () => void;
  setActiveTurn: (turnId: string | null, summary?: Omit<RecentTurnSummary, "turnId">) => void;
  addPipelineEvent: (event: PipelineEvent) => void;
  clearPipelineEvents: () => void;
  setWebsocketStatus: (status: ConnectionStatus) => void;
}

const SessionContext = createContext<SessionState | null>(null);

export function SessionProvider({ children }: PropsWithChildren) {
  migrateLegacyState();
  const [sessionId, setSessionId] = useState(readSessionId);
  const [activeTurnId, setActiveTurnIdState] = useState<string | null>(() => {
    const stored = readStoredString(ACTIVE_TURN_STORAGE_KEY);
    return validTurnId(stored) ? stored : null;
  });
  const [recentTurns, setRecentTurns] = useState<RecentTurnSummary[]>(() => readRecentTurns(readSessionId()));
  const recentTurnIds = useMemo(() => recentTurns.map((item) => item.turnId), [recentTurns]);
  const [websocketStatus, setWebsocketStatus] = useState<ConnectionStatus>("disconnected");
  const [pipelineEvents, setPipelineEvents] = useState<PipelineEvent[]>([]);

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
    setSessionId(created);
    setActiveTurnIdState(null);
    setRecentTurns([]);
    setPipelineEvents([]);
    setWebsocketStatus("disconnected");
  }, [sessionId]);

  const addPipelineEvent = useCallback((event: PipelineEvent) => {
    setPipelineEvents((items) => {
      if (items.some((item) => item.event_id === event.event_id)) return items;
      return [...items, event].sort((a, b) => a.sequence - b.sequence).slice(-MAX_PIPELINE_EVENTS);
    });
  }, []);

  const clearPipelineEvents = useCallback(() => setPipelineEvents([]), []);

  const value = useMemo<SessionState>(() => ({
    sessionId,
    activeTurnId,
    recentTurnIds,
    recentTurns,
    websocketStatus,
    pipelineEvents,
    newSession,
    setActiveTurn,
    addPipelineEvent,
    clearPipelineEvents,
    setWebsocketStatus,
  }), [sessionId, activeTurnId, recentTurnIds, recentTurns, websocketStatus, pipelineEvents, newSession, setActiveTurn, addPipelineEvent, clearPipelineEvents]);

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionState {
  const value = useContext(SessionContext);
  if (!value) throw new Error("useSession 必须在 SessionProvider 内使用");
  return value;
}
