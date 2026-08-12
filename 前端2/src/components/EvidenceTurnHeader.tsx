import { Link } from "react-router-dom";
import { prefetchAudit, prefetchReview } from "../cache/prefetch";
import type { TurnPresentationResponse } from "../types/contract";
import { decisionLabel } from "../utils/formatters";
import { TurnSelector } from "./TurnSelector";

interface Props {
  turnId: string;
  turnIds: string[];
  presentation: TurnPresentationResponse | null;
  loading: boolean;
  error: string | null;
  onSelectTurn: (turnId: string) => void;
  onRetry: () => void;
}

export function EvidenceTurnHeader({ turnId, turnIds, presentation, loading, error, onSelectTurn, onRetry }: Props) {
  return <header className="evidence-turn-header">
    <div className="evidence-title-block">
      <span className="eyebrow">EVIDENCE NAVIGATION</span>
      <h1>证据检索与分层查看</h1>
      <p>按后端真实安全层级查看本轮证据、缺失项和关系，不推导新的裁决结论。</p>
    </div>
    <div className="evidence-turn-summary">
      <div><span>当前轮次</span><strong title={turnId}>{turnId}</strong></div>
      <div><span>当前指令</span><strong>{presentation?.input.normalized_text || (loading ? "正在加载…" : "暂无摘要")}</strong></div>
      <div><span>最终裁决</span><strong className={presentation ? `decision-text-${presentation.decision_result.final_decision.toLowerCase()}` : ""}>{presentation ? decisionLabel(presentation.decision_result.final_decision) : "暂无"}</strong></div>
      <TurnSelector currentTurnId={turnId} turnIds={turnIds} onChange={onSelectTurn} />
      <div className="evidence-header-links">
        {presentation && (presentation.decision_result.review_required || presentation.review.status !== "NOT_REQUIRED" || presentation.authorization.token_issued || presentation.execution.execution_status !== "NOT_EXECUTED") && <Link className="primary-link evidence-back-link" to={`/review/${encodeURIComponent(turnId)}`} onMouseEnter={() => prefetchReview(turnId)} onFocus={() => prefetchReview(turnId)}>{presentation.decision_result.review_required ? "进入复核" : presentation.execution.execution_status !== "NOT_EXECUTED" ? "查看执行结果" : presentation.authorization.token_issued ? "查看授权与执行" : "查看复核结果"}</Link>}
        {presentation?.audit.audit_id ? <Link className="primary-link evidence-back-link" to={`/audits/${encodeURIComponent(presentation.audit.audit_id)}`} onMouseEnter={() => prefetchAudit(presentation.audit.audit_id!)} onFocus={() => prefetchAudit(presentation.audit.audit_id!)}>查看本轮审计</Link> : presentation ? <button className="secondary-button evidence-back-link" onClick={onRetry}>审计尚未归档，刷新轮次</button> : null}
        <Link className="secondary-button evidence-back-link" to="/decision">返回实时裁决</Link>
      </div>
    </div>
    {error && <div className="evidence-header-error"><span>轮次摘要加载失败：{error}</span><button className="secondary-button compact" onClick={onRetry}>重试摘要</button></div>}
  </header>;
}
