import { Link } from "react-router-dom";
import { prefetchAudit, prefetchEvidence, prefetchReview } from "../cache/prefetch";
import type { TurnPresentationResponse } from "../types/contract";
import { decisionPromotionReason, evidenceAlignmentLabel } from "../utils/decisionExplanation";
import { executionStatusLabel } from "../utils/executionMapper";
import { decisionLabel } from "../utils/formatters";
import type { AdaptedCommandResponse } from "../adapters/commandResponseAdapter";

interface Props { data: TurnPresentationResponse | null; immediate: AdaptedCommandResponse | null; loading: boolean; error: string | null; onRetry: () => void; }

export function DecisionResultPanel({ data, immediate, loading, error, onRetry }: Props) {
  if (!data && immediate) return <section className={`decision-card result-panel decision-${immediate.preliminaryDecision.toLowerCase()}`} aria-label="即时裁决结果">
    <span className="eyebrow">IMMEDIATE DECISION</span>
    <div className="decision-title"><h2>{decisionLabel(immediate.preliminaryDecision)}</h2><strong>安全评分 {immediate.safetyScore.toFixed(3)}</strong></div>
    <p className="decision-explanation">{immediate.instructionSummary}</p>
    <div className="decision-judgement-grid">
      <div><span>动作</span><strong>{immediate.action}</strong></div>
      <div><span>目标</span><strong>{immediate.target}</strong></div>
      <div><span>轮次</span><strong>{immediate.turnId}</strong></div>
    </div>
    <p className="loading-copy">{loading ? "完整证据与审计信息加载中" : "完整证据与审计信息尚未补齐"}</p>
    {error && <p className="inline-error">完整展示加载失败：{error}。即时裁决结果已保留。</p>}
    <div className="decision-action-links"><Link className="primary-link evidence-link" to={`/evidence/${encodeURIComponent(immediate.turnId)}`} onMouseEnter={() => prefetchEvidence(immediate.turnId)} onFocus={() => prefetchEvidence(immediate.turnId)}>查看分层证据</Link><button type="button" className="secondary-button compact" onClick={onRetry}>重试完整展示</button></div>
  </section>;
  if (loading && !data) return <section className="decision-card result-panel"><p className="loading-copy">正在获取后端轮次展示……</p></section>;
  if (error && !data) return <section className="decision-card result-panel"><p className="inline-error">{error}</p><button className="secondary-button" onClick={onRetry}>重试轮次展示</button></section>;
  if (!data) return <section className="decision-card result-panel empty-result"><span>DECISION</span><h2>等待真实裁决</h2><p>提交指令后，这里将展示后端持久化的最终结果。</p></section>;
  const decision = data.decision_result;
  const requiredEvidenceCount = data.evidence_demand.intent_demands.reduce((count, item) => count + item.required_types.length, 0);
  const alignmentRoute = data.evidence.quality_metrics.evidence_alignment_route;
  const promotionReason = decisionPromotionReason({
    scoreDecision: decision.score_decision,
    finalDecision: decision.final_decision,
    gateBlocked: data.gate_result.blocked,
    requiredEvidenceCount,
    evidenceAlignmentRoute: alignmentRoute,
    decisionSources: decision.decision_sources,
  });
  const showWorkflowLink = decision.review_required || data.review.status !== "NOT_REQUIRED" || data.authorization.token_issued || data.execution.execution_status !== "NOT_EXECUTED";
  const workflowLinkLabel = decision.review_required ? "进入复核" : data.execution.execution_status !== "NOT_EXECUTED" ? "查看执行结果" : data.authorization.token_issued ? "查看授权状态" : "查看复核结果";
  return <section className={`decision-card result-panel decision-${decision.final_decision.toLowerCase()}`}>
    <span className="eyebrow">FINAL DECISION</span><div className="decision-title"><h2>{decisionLabel(decision.final_decision)}</h2><strong>安全评分 {decision.safety_score.toFixed(3)}</strong></div>
    <div className="decision-judgement-grid">
      <div><span>评分判断</span><strong>{decisionLabel(decision.score_decision)}</strong></div>
      <div><span>证据对齐判断</span><strong>{evidenceAlignmentLabel(requiredEvidenceCount, alignmentRoute)}</strong></div>
      <div><span>最终裁决</span><strong>{decisionLabel(decision.final_decision)}</strong></div>
    </div>
    <p className="decision-explanation">{promotionReason}</p>
    {data.evidence_demand.intent_demands.some((item) => item.knowledge_augmented_types?.length) ? <div className="knowledge-augmented-block">
      {data.evidence_demand.intent_demands.map((intent) => intent.knowledge_augmented_types?.length ? <p key={intent.intent_id}><strong>📚 知识库追加（{intent.intent_id}）</strong>：{intent.knowledge_augmented_types.join("、")}{intent.knowledge_hits?.length ? <span> · 命中 {intent.knowledge_hits.map((hit) => hit.title ?? hit.node_id).join("；")}</span> : null}</p> : null)}
    </div> : null}
    <details className="decision-technical-details"><summary>技术详情</summary><p>{decision.explanation}</p><p><code>{decision.decision_merge_reason}</code></p><ul className="reason-list">{decision.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></details>
    <div className="decision-flags"><span>安全门：{data.gate_result.blocked ? "已阻断" : "已通过"}</span><span>复核：{decision.review_required ? "需要" : "不需要"}</span><span>授权：{data.authorization.token_status || (data.authorization.token_issued ? "已签发" : "未签发")}</span><span>执行：{executionStatusLabel(data.execution.execution_status)}</span></div>
    <div className="decision-action-links">
      <Link className="primary-link evidence-link" to={`/evidence/${encodeURIComponent(data.turn_id)}`} onMouseEnter={() => prefetchEvidence(data.turn_id)} onFocus={() => prefetchEvidence(data.turn_id)}>查看分层证据</Link>
      {showWorkflowLink && <Link className="primary-link review-link" to={`/review/${encodeURIComponent(data.turn_id)}`} onMouseEnter={() => prefetchReview(data.turn_id)} onFocus={() => prefetchReview(data.turn_id)}>{workflowLinkLabel}</Link>}
      {data.audit.audit_id ? <Link className="primary-link audit-link" to={`/audits/${encodeURIComponent(data.audit.audit_id)}`} onMouseEnter={() => prefetchAudit(data.audit.audit_id!)} onFocus={() => prefetchAudit(data.audit.audit_id!)}>查看本轮审计记录</Link> : <button type="button" className="secondary-button compact" onClick={onRetry}>审计尚未归档，刷新当前轮次</button>}
    </div>
  </section>;
}
