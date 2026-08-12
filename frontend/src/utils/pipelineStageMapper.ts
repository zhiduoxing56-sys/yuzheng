import type { PipelineEvent } from "../types/contract";

export type PipelineStageStatus = "waiting" | "processing" | "completed" | "review" | "blocked" | "failed";

export interface PipelineStageDefinition {
  key: string;
  label: string;
  stages: readonly string[];
}

export interface PipelineStageView extends PipelineStageDefinition {
  status: PipelineStageStatus;
  latestEvent?: PipelineEvent;
}

export const PIPELINE_STAGES: readonly PipelineStageDefinition[] = [
  { key: "trust", label: "输入可信校验", stages: ["INPUT_RECEIVED", "VOICE_INPUT_RECEIVED", "TRUST_CHECKED", "SPECTRUM_ANALYZED", "LA_CHECKED", "PA_CHECKED", "VOICE_TRUST_DECIDED", "ZONE_PERMISSION_CHECKED"] },
  { key: "semantic", label: "转写与语义解析", stages: ["ASR_COMPLETED", "SEMANTIC_PARSED"] },
  { key: "demand", label: "证据需求生成", stages: ["RUNTIME_CAPABILITY_CHECKED"] },
  { key: "retrieval", label: "分层证据检索", stages: ["EVIDENCE_RETRIEVED", "MANDATORY_SUPPLEMENTED"] },
  { key: "validation", label: "一致性与安全校验", stages: ["EVIDENCE_QUALITY_EVALUATED", "GRAPH_BUILT", "MEMORY_PROPAGATED", "CAUSAL_CORRECTED", "EVIDENCE_VALIDATED", "GATE_CHECKED"] },
  { key: "decision", label: "安全裁决", stages: ["DECISION_COMPLETED", "EXPLANATION_GENERATED"] },
  { key: "review", label: "复核与授权", stages: ["REVIEW_REQUIRED", "REVIEW_REQUESTED", "REVIEW_CONFIRMED", "REVIEW_CORRECTED", "REVIEW_CANCELLED", "TOKEN_ISSUED", "TOKEN_REJECTED", "TOKEN_REVOKED", "TOKEN_EXPIRED"] },
  { key: "execution", label: "执行与审计", stages: ["VEHICLE_PRECHECKED", "TOKEN_CONSUMED", "VEHICLE_EXECUTED", "EXECUTION_SUCCEEDED", "EXECUTION_FAILED", "PIPELINE_FAILED", "AUDIT_SAVED"] },
];

export function stageLabel(value?: string | null): string {
  if (!value) return "其他处理事件";
  const definition = PIPELINE_STAGES.find((item) => item.stages.includes(value));
  return definition?.label || "其他处理事件";
}

function eventStatus(event: PipelineEvent): PipelineStageStatus {
  const status = event.status.toUpperCase();
  const decision = String(event.payload.final_decision || "").toUpperCase();
  if (status.includes("FAIL") || status.includes("REJECT") || event.stage.includes("FAILED")) return "failed";
  if (decision === "BLOCK" || status.includes("BLOCK") || event.payload.blocked === true) return "blocked";
  if (decision === "REVIEW" || event.stage.includes("REVIEW_REQUESTED")) return "review";
  if (status.includes("PROCESS") || status.includes("RUNNING")) return "processing";
  return "completed";
}

export function buildPipelineStageViews(events: PipelineEvent[], processing: boolean): PipelineStageView[] {
  const views = PIPELINE_STAGES.map<PipelineStageView>((definition) => {
    const matches = events.filter((event) => definition.stages.includes(event.stage));
    const latestEvent = matches.at(-1);
    return { ...definition, status: latestEvent ? eventStatus(latestEvent) : "waiting", latestEvent };
  });
  if (processing) {
    const lastCompleted = views.reduce((latest, item, index) => item.latestEvent ? index : latest, -1);
    const nextIndex = Math.min(lastCompleted + 1, views.length - 1);
    if (views[nextIndex] && views[nextIndex].status === "waiting") views[nextIndex] = { ...views[nextIndex], status: "processing" };
  }
  return views;
}

export function unknownPipelineEvents(events: PipelineEvent[]): PipelineEvent[] {
  const known = new Set(PIPELINE_STAGES.flatMap((item) => [...item.stages]));
  return events.filter((event) => !known.has(event.stage));
}
