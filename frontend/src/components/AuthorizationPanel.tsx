import type { TurnPresentationResponse, TurnWorkflowStatus } from "../types/contract";
import { formatDateTime } from "../utils/formatters";
import { tokenStatusLabel } from "../utils/workflowMapper";
import { StatusBadge } from "./StatusBadge";

export function AuthorizationPanel({ presentation, workflow, hasToken }: { presentation: TurnPresentationResponse | null; workflow: TurnWorkflowStatus | null; hasToken: boolean }) {
  const authorization = presentation?.authorization;
  const tone = authorization?.token_status === "ISSUED" ? "success" : authorization?.token_status ? "warning" : "neutral";
  return <section className="review-card">
    <div className="card-heading"><div><span className="eyebrow">AUTHORIZATION</span><h2>授权状态</h2></div><StatusBadge tone={tone} label={tokenStatusLabel(workflow?.token_status || authorization?.token_status)} /></div>
    {!authorization ? <p className="empty-copy">暂无授权信息。</p> : <dl className="review-fact-grid compact-grid">
      <div><dt>是否签发</dt><dd>{authorization.token_issued ? "是" : "否"}</dd></div>
      <div><dt>后端允许执行</dt><dd>{authorization.execution_allowed ? "是" : "否"}</dd></div>
      <div><dt>是否已使用</dt><dd>{authorization.consumed ? "是" : "否"}</dd></div>
      <div><dt>过期时间</dt><dd>{formatDateTime(authorization.expires_at)}</dd></div>
      <div><dt>授权动作</dt><dd>{presentation?.semantic_frame.intents[0]?.action || "未提供"}</dd></div>
      <div><dt>授权目标</dt><dd>{presentation?.semantic_frame.intents[0]?.target || "未提供"}</dd></div>
    </dl>}
    <p className="token-security-note">原始授权令牌不会显示、复制或持久化。当前页面内存令牌：{hasToken ? "可用于一次执行" : "不可用或无法恢复"}。</p>
  </section>;
}
