import type { DecisionLabel } from "../types/contract";
import { decisionLabel } from "./formatters";

export function evidenceAlignmentLabel(requiredEvidenceCount: number, route?: string | null): string {
  if (requiredEvidenceCount === 0) return "不适用（本指令没有必查证据）";
  if (route === "EVIDENCE_PASS") return "通过";
  if (route === "EVIDENCE_REVIEW") return "需要复核";
  if (route === "EVIDENCE_BLOCK") return "阻断";
  return "后端未提供判断";
}

export function decisionPromotionReason(options: {
  scoreDecision: DecisionLabel;
  finalDecision: DecisionLabel;
  gateBlocked: boolean;
  requiredEvidenceCount: number;
  evidenceAlignmentRoute?: string | null;
  decisionSources?: string[];
}): string {
  const { scoreDecision, finalDecision, gateBlocked, requiredEvidenceCount, evidenceAlignmentRoute } = options;
  const sources = new Set(options.decisionSources ?? []);
  if (scoreDecision === finalDecision) return `没有额外模块提升等级，最终裁决沿用评分判断“${decisionLabel(scoreDecision)}”。`;
  if (gateBlocked) return `安全门将评分判断“${decisionLabel(scoreDecision)}”提升为“${decisionLabel(finalDecision)}”。`;
  if (requiredEvidenceCount > 0 && evidenceAlignmentRoute === "EVIDENCE_REVIEW") return `证据对齐将评分判断“${decisionLabel(scoreDecision)}”提升为“需要复核”。`;
  if (requiredEvidenceCount > 0 && evidenceAlignmentRoute === "EVIDENCE_BLOCK") return `证据对齐将评分判断“${decisionLabel(scoreDecision)}”提升为“安全阻断”。`;
  if (sources.has("VOICE_TRUST")) return `语音可信检查将评分判断“${decisionLabel(scoreDecision)}”提升为“${decisionLabel(finalDecision)}”。`;
  if (sources.has("ZONE_PERMISSION")) return `发声区域权限将评分判断“${decisionLabel(scoreDecision)}”提升为“${decisionLabel(finalDecision)}”。`;
  if (sources.has("RUNTIME_CAPABILITY")) return `运行能力约束将评分判断“${decisionLabel(scoreDecision)}”提升为“${decisionLabel(finalDecision)}”。`;
  if (sources.has("USER_REVIEW")) return `人工复核结果将评分判断“${decisionLabel(scoreDecision)}”更新为“${decisionLabel(finalDecision)}”。`;
  return `独立安全约束将评分判断“${decisionLabel(scoreDecision)}”提升为“${decisionLabel(finalDecision)}”。`;
}
