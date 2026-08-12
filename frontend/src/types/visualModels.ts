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
  turnId: string;
  createdAt: string;
  rawText: EmptyDisplayValue;
  semanticFrame: SemanticFrame | null;
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
}
import type { SemanticFrame } from "./contract";
