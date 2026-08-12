import { Link } from "react-router-dom";
import { prefetchAudit, prefetchEvidence } from "../cache/prefetch";
import type { TurnPresentationResponse, TurnWorkflowStatus } from "../types/contract";
import { decisionLabel } from "../utils/formatters";
import { workflowStatusLabel } from "../utils/workflowMapper";

interface Props {
  turnId: string;
  presentation: TurnPresentationResponse | null;
  workflow: TurnWorkflowStatus | null;
  refreshing: boolean;
  onRefresh: () => void;
}

export function ReviewTurnHeader({ turnId, presentation, workflow, refreshing, onRefresh }: Props) {
  return <header className="review-turn-header">
    <div className="review-title-block">
      <span className="eyebrow">REVIEW · AUTHORIZATION · EXECUTION</span>
      <h1>复核、授权与执行闭环</h1>
      <p>所有裁决、授权和执行状态均来自后端真实工作流。</p>
    </div>
    <div className="review-header-facts">
      <div><span>当前地址轮次</span><strong title={turnId}>{turnId}</strong></div>
      <div><span>来源根轮次</span><strong title={workflow?.root_turn_id}>{workflow?.root_turn_id || "正在加载…"}</strong></div>
      <div><span>最终裁决</span><strong className={presentation ? `decision-text-${presentation.decision_result.final_decision.toLowerCase()}` : ""}>{decisionLabel(presentation?.decision_result.final_decision)}</strong></div>
      <div><span>工作流</span><strong>{workflowStatusLabel(workflow?.status)}</strong></div>
    </div>
    <div className="review-header-actions">
      <button type="button" className="secondary-button" onClick={onRefresh} disabled={refreshing}>{refreshing ? "刷新中…" : "刷新全部状态"}</button>
      <Link className="secondary-button review-nav-link" to={`/evidence/${encodeURIComponent(turnId)}`} onMouseEnter={() => prefetchEvidence(turnId)} onFocus={() => prefetchEvidence(turnId)}>查看分层证据</Link>
      {presentation?.audit.audit_id ? <Link className="secondary-button review-nav-link" to={`/audits/${encodeURIComponent(presentation.audit.audit_id)}`} onMouseEnter={() => prefetchAudit(presentation.audit.audit_id!)} onFocus={() => prefetchAudit(presentation.audit.audit_id!)}>查看审计记录</Link> : presentation ? <button className="secondary-button review-nav-link" onClick={onRefresh}>审计尚未归档，刷新</button> : null}
      <Link className="secondary-button review-nav-link" to="/decision">返回实时裁决</Link>
    </div>
  </header>;
}
