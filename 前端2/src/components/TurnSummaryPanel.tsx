import type { TurnPresentationResponse, TurnWorkflowStatus } from "../types/contract";

interface Props { presentation: TurnPresentationResponse | null; workflow: TurnWorkflowStatus | null; workflowLoading: boolean; workflowError: string | null; onRefresh: () => void; }

export function TurnSummaryPanel({ presentation, workflow, workflowLoading, workflowError, onRefresh }: Props) {
  return <section className="detail-section"><div className="card-heading"><div><span className="eyebrow">TURN</span><h2>轮次与语义摘要</h2></div><button className="secondary-button compact" onClick={onRefresh} disabled={!presentation || workflowLoading}>刷新当前轮次</button></div>
    {!presentation ? <p className="empty-copy">暂无轮次数据</p> : <dl className="summary-grid"><div><dt>轮次编号</dt><dd>{presentation.turn_id}</dd></div><div><dt>规范化指令</dt><dd>{presentation.input.normalized_text}</dd></div><div><dt>动作 / 目标</dt><dd>{presentation.semantic_frame.intents.map((item) => `${item.action} / ${item.target}`).join("；") || "未识别"}</dd></div><div><dt>风险等级</dt><dd>{presentation.semantic_frame.intents.map((item) => item.risk_level).join("；") || "未提供"}</dd></div><div><dt>工作流阶段</dt><dd>{workflow?.status || "暂无数据"}</dd></div><div><dt>复核次数</dt><dd>{workflow ? `${workflow.review_attempts}/${workflow.max_review_attempts}` : "暂无数据"}</dd></div><div><dt>授权状态</dt><dd>{workflow?.token_status || presentation.authorization.token_status || "未授权"}</dd></div><div><dt>执行状态</dt><dd>{presentation.execution.execution_status}</dd></div></dl>}
    {workflowError && <p className="inline-error">{workflowError}</p>}
  </section>;
}
