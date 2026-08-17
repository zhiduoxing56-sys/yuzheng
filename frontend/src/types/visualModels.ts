export type EmptyDisplayValue = string | null;

export interface EvidenceParameterValues {
  M: string;
  ef_construction: string;
  ef_search: string;
  layer_count: string;
}

export interface EvidenceLayerView {
  id: string;
  label: string;
  hitCount: number;
  nodes: import("./contract").RetrievalLayerNode[];
}

export interface EvidenceStatisticsView {
  returnedItems: EmptyDisplayValue;
  semanticCandidates: EmptyDisplayValue;
  forcedRecallItems: EmptyDisplayValue;
}

export interface RecallAuditRowView {
  id: string;
  voiceCommand: EmptyDisplayValue;
  forcedRecallEvidence: EmptyDisplayValue;
  aiAuditAvailable: boolean;
}

export interface AuditRecordView {
  auditId: string;
  createdAt: string;
  rawCommand: string;
  finalDecision: string;
  executionStatus: string;
  reviewOccurred: boolean;
}

export type CommandInputMode = "text" | "audio" | "microphone";

export type DecisionVisualState = "pass" | "reject" | "review";

export interface DecisionDimensionView {
  id: string;
  dimension: string;
  detail: EmptyDisplayValue;
}

export interface DecisionResultView {
  state: DecisionVisualState | null;
  dimensions: DecisionDimensionView[];
  score: EmptyDisplayValue;
  reason: EmptyDisplayValue;
  scoreDecision?: string | null;
  finalDecision?: string | null;
  gateBlocked?: boolean | null;
  evidenceAlignment?: string | null;
  decisionSources?: string[];
  mergeReason?: string | null;
}

export interface DecisionExplanationView {
  status: "IDLE" | "PENDING" | "AVAILABLE" | "FAILED";
  text: string | null;
  retryable: boolean;
  facts?: Record<string, unknown>;
}
