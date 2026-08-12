import type { TurnPresentationResponse } from "../types/contract";
import { decisionLabel } from "../utils/formatters";

export function EvidenceDecisionSummary({ data }: { data: TurnPresentationResponse | null }) {
  if (!data) return <section className="evidence-decision-summary evidence-panel"><p className="empty-copy">轮次摘要尚未加载，证据列表仍可独立显示。</p></section>;
  const instruction = data.review.original_instruction || data.input.asr_raw_text || data.input.normalized_text;
  return <section className="evidence-decision-summary evidence-panel">
    <div><span>本轮真实指令</span><strong>{instruction || "后端未返回指令文本"}</strong></div>
    <div><span>最终裁决</span><strong className={`decision-text-${data.decision_result.final_decision.toLowerCase()}`}>{decisionLabel(data.decision_result.final_decision)}</strong></div>
    <div><span>安全分数</span><strong>{Number.isFinite(data.decision_result.safety_score) ? data.decision_result.safety_score.toFixed(3) : "暂无"}</strong></div>
    <div><span>裁决说明</span><p>{data.decision_result.explanation || data.decision_result.decision_merge_reason || "后端未提供裁决说明"}</p></div>
  </section>;
}
