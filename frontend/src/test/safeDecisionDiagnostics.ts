export type DiagnosticLifecycle = "request_start" | "request_complete" | "request_cancel" | "request_discard";
export type DiagnosticDiscardReason = "aborted" | "generation_changed" | "key_changed" | "session_changed" | "superseded" | "turn_mismatch" | "unmounted";

export interface SafeDecisionDiagnosticInput {
  sessionId: string;
  submissionGeneration: number;
  turnId: string | null;
  sequence: number | null;
  stage: string | null;
  status: string | null;
  lifecycle: DiagnosticLifecycle;
  discardReason?: DiagnosticDiscardReason;
}

export interface SafeDecisionDiagnosticEntry {
  sessionIdPrefix: string;
  submissionGeneration: number;
  turnId: string | null;
  sequence: number | null;
  stage: string | null;
  status: string | null;
  lifecycle: DiagnosticLifecycle;
  discardReason?: DiagnosticDiscardReason;
}

export function safeDecisionDiagnostic(
  input: SafeDecisionDiagnosticInput,
  sink: (entry: SafeDecisionDiagnosticEntry) => void = (entry) => console.debug("[decision-diagnostic]", entry),
): SafeDecisionDiagnosticEntry | null {
  if (!import.meta.env.DEV) return null;
  const entry: SafeDecisionDiagnosticEntry = {
    sessionIdPrefix: input.sessionId.slice(0, 8),
    submissionGeneration: input.submissionGeneration,
    turnId: input.turnId,
    sequence: input.sequence,
    stage: input.stage,
    status: input.status,
    lifecycle: input.lifecycle,
    ...(input.discardReason ? { discardReason: input.discardReason } : {}),
  };
  sink(entry);
  return entry;
}
