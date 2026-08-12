import type { DecisionLabel, InputType } from "../types/contract";
import type { SubmissionSummarySource } from "../adapters/commandResponseAdapter";

export interface CommandDraft { text: string; speakerZone: string; speakerRole: string; }
export interface LastSubmissionSummary {
  text: string;
  inputType: InputType;
  source: SubmissionSummarySource;
  turnId: string;
  submittedAt: string;
  preliminaryDecision: DecisionLabel;
}

const prefix = "yuzheng.v2";
const key = (kind: string, sessionId: string) => `${prefix}.${kind}.${sessionId}`;

function read<T>(storageKey: string, guard: (value: unknown) => value is T): T | null {
  try { const value: unknown = JSON.parse(sessionStorage.getItem(storageKey) || "null"); return guard(value) ? value : null; } catch { return null; }
}
function write(storageKey: string, value: unknown): void { try { sessionStorage.setItem(storageKey, JSON.stringify(value)); } catch { /* optional */ } }
function object(value: unknown): value is Record<string, unknown> { return Boolean(value) && typeof value === "object" && !Array.isArray(value); }

export function loadCommandDraft(sessionId: string): CommandDraft | null {
  return read(key("commandDraft", sessionId), (value): value is CommandDraft => object(value) && typeof value.text === "string" && typeof value.speakerZone === "string" && typeof value.speakerRole === "string");
}
export function saveCommandDraft(sessionId: string, draft: CommandDraft): void { write(key("commandDraft", sessionId), draft); }
export function clearCommandDraft(sessionId: string): void { try { sessionStorage.removeItem(key("commandDraft", sessionId)); } catch { /* optional */ } }

export function loadLastSubmission(sessionId: string): LastSubmissionSummary | null {
  return read(key("lastSubmission", sessionId), (value): value is LastSubmissionSummary => object(value) && typeof value.text === "string" && ["text", "audio"].includes(String(value.inputType)) && typeof value.source === "string" && typeof value.turnId === "string" && typeof value.submittedAt === "string" && ["PASS", "REVIEW", "BLOCK"].includes(String(value.preliminaryDecision)));
}
export function saveLastSubmission(sessionId: string, summary: LastSubmissionSummary): void { write(key("lastSubmission", sessionId), summary); }
export function clearLastSubmission(sessionId: string): void { try { sessionStorage.removeItem(key("lastSubmission", sessionId)); } catch { /* optional */ } }
export function clearCommandSession(sessionId: string): void { clearCommandDraft(sessionId); clearLastSubmission(sessionId); }

