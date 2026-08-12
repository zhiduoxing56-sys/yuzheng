import type { TurnPresentationResponse } from "../types/contract";
import type { SafeReviewResult } from "../utils/reviewMapper";
import { decisionPromotionReason, evidenceAlignmentLabel } from "../utils/decisionExplanation";
import { decisionLabel, reviewActionLabel } from "../utils/formatters";

export function ReviewResultPanel({ presentation, result }: { presentation: TurnPresentationResponse | null; result: SafeReviewResult | null }) {
  const decision = presentation?.decision_result;
  const requiredEvidenceCount = presentation?.evidence_demand.intent_demands.reduce((count, item) => count + item.required_types.length, 0) ?? 0;
  const alignmentRoute = presentation?.evidence.quality_metrics.evidence_alignment_route;
  const promotionReason = presentation && decision ? decisionPromotionReason({ scoreDecision: decision.score_decision, finalDecision: decision.final_decision, gateBlocked: presentation.gate_result.blocked, requiredEvidenceCount, evidenceAlignmentRoute: alignmentRoute, decisionSources: decision.decision_sources }) : null;
  return <section className="review-card review-result-card">
    <span className="eyebrow">UPDATED DECISION</span><h2>更新后的裁决结果</h2>
    {!presentation ? <p className="empty-copy">等待后端轮次展示。</p> : <>
      <div className={`review-decision review-decision-${presentation.decision_result.final_decision.toLowerCase()}`}><strong>{decisionLabel(presentation.decision_result.final_decision)}</strong><span>安全评分 {presentation.decision_result.safety_score.toFixed(3)}</span></div>
      <dl className="review-fact-grid compact-grid">
        <div><dt>评分判断</dt><dd>{decisionLabel(presentation.decision_result.score_decision)}</dd></div>
        <div><dt>证据对齐判断</dt><dd>{evidenceAlignmentLabel(requiredEvidenceCount, alignmentRoute)}</dd></div>
        <div><dt>最终裁决</dt><dd>{decisionLabel(presentation.decision_result.final_decision)}</dd></div>
        <div><dt>等级变化</dt><dd>{promotionReason}</dd></div>
        <div><dt>识别文本</dt><dd>{presentation.input.normalized_text}</dd></div>
        <div><dt>语义结果</dt><dd>{presentation.semantic_frame.intents.map((item) => `${item.action} / ${item.target}`).join("；") || "未识别"}</dd></div>
        <div><dt>安全门</dt><dd>{presentation.gate_result.blocked ? "已阻断" : "未阻断"}</dd></div>
        <div><dt>再次复核</dt><dd>{presentation.decision_result.review_required ? "需要" : "不需要"}</dd></div>
      </dl>
      <details className="audit-raw-details"><summary>技术详情</summary><p>{presentation.decision_result.explanation || "后端未提供裁决说明"}</p><p><code>{presentation.decision_result.decision_merge_reason}</code></p></details>
    </>}
    {result && <div className="review-submit-summary"><strong>{reviewActionLabel(result.action)}</strong><span>{result.reason || result.message}</span><small>来源轮次 {result.originalTurnId} → 结果轮次 {result.relatedTurnId}</small></div>}
  </section>;
}
