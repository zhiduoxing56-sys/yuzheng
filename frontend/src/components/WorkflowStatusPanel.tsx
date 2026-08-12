import type { TurnPresentationResponse, TurnWorkflowStatus } from "../types/contract";
import { tokenStatusLabel, workflowStatusLabel } from "../utils/workflowMapper";

export function WorkflowStatusPanel({ workflow, presentation }: { workflow: TurnWorkflowStatus | null; presentation: TurnPresentationResponse | null }) {
  return <section className="review-card">
    <span className="eyebrow">WORKFLOW</span><h2>工作流状态</h2>
    {!workflow ? <p className="empty-copy">暂无工作流状态。</p> : <dl className="review-fact-grid compact-grid">
      <div><dt>当前阶段</dt><dd>{workflowStatusLabel(workflow.status)}</dd></div>
      <div><dt>最新轮次</dt><dd title={workflow.current_turn_id}>{workflow.current_turn_id}</dd></div>
      <div><dt>复核次数</dt><dd>{workflow.review_attempts}/{workflow.max_review_attempts}</dd></div>
      <div><dt>最新裁决</dt><dd>{workflow.latest_decision}</dd></div>
      <div><dt>授权状态</dt><dd>{tokenStatusLabel(workflow.token_status)}</dd></div>
      <div><dt>是否终态</dt><dd>{workflow.terminal ? "是" : "否"}</dd></div>
      <div><dt>是否允许执行</dt><dd>{presentation?.authorization.execution_allowed ? "后端允许" : "后端未允许"}</dd></div>
      <div><dt>事件数量</dt><dd>{workflow.event_count}</dd></div>
    </dl>}
  </section>;
}
