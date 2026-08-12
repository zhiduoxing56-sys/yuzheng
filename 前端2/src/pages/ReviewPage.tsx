import { Link, useParams } from "react-router-dom";
import { AuthorizationPanel } from "../components/AuthorizationPanel";
import { EmptyState } from "../components/EmptyState";
import { ErrorState } from "../components/ErrorState";
import { ExecutionPanel } from "../components/ExecutionPanel";
import { RecognitionResultPanel } from "../components/RecognitionResultPanel";
import { ReviewActionPanel } from "../components/ReviewActionPanel";
import { ReviewReasonPanel } from "../components/ReviewReasonPanel";
import { ReviewResultPanel } from "../components/ReviewResultPanel";
import { ReviewTimelinePanel } from "../components/ReviewTimelinePanel";
import { ReviewTurnHeader } from "../components/ReviewTurnHeader";
import { WorkflowChainPanel } from "../components/WorkflowChainPanel";
import { WorkflowStatusPanel } from "../components/WorkflowStatusPanel";
import { useReviewPageController } from "../hooks/useReviewPageController";

export function ReviewPage() {
  const { turnId: routeTurnId } = useParams<{ turnId?: string }>();
  const controller = useReviewPageController(routeTurnId);
  if (!controller.turnId) return <div className="review-page"><EmptyState title="无法复核" description="地址中没有有效 turnId。请从实时裁决或分层证据页面进入具体轮次。" /></div>;

  const { turn, submission, execution } = controller;
  const primaryFailed = Boolean(turn.presentationError && !turn.presentation && !turn.presentationLoading);
  return <div className="review-page">
    <ReviewTurnHeader turnId={controller.turnId} presentation={turn.presentation} workflow={turn.workflow} refreshing={controller.refreshing} onRefresh={() => { void controller.refreshAll(); }} />
    {(turn.presentationLoading || turn.workflowLoading) && !turn.presentation && <div className="loading-state"><span className="loading-dot" />正在加载轮次展示与真实工作流状态…</div>}
    {primaryFailed && <ErrorState title="轮次不存在或后端不可用" description={turn.presentationError || "轮次展示加载失败"} onRetry={() => { void controller.refreshAll(); }} />}
    {turn.presentation?.decision_result.final_decision === "PASS" && <div className="readonly-turn-banner"><span>本轮无需人工复核，以下为后端裁决、授权和执行状态的只读展示。</span></div>}
    {turn.presentation?.decision_result.final_decision === "BLOCK" && <div className="readonly-turn-banner"><span>本轮已被安全策略阻断，仅允许查看真实裁决与审计信息。</span></div>}
    {turn.workflow && turn.workflow.current_turn_id !== controller.turnId && <div className="readonly-turn-banner"><span>当前地址是来源轮次，只读保留；最新可操作轮次为 {turn.workflow.current_turn_id}。</span><Link className="secondary-button compact" to={`/review/${encodeURIComponent(turn.workflow.current_turn_id)}`} replace>查看最新轮次</Link></div>}
    {controller.activeTurnId !== controller.turnId && <div className="readonly-turn-banner"><span>这是历史或来源轮次，仅供查看。当前会话可写轮次为 {controller.activeTurnId || "尚未建立"}。</span>{controller.activeTurnId && <Link className="secondary-button compact" to={`/review/${encodeURIComponent(controller.activeTurnId)}`}>返回当前轮次</Link>}</div>}
    {turn.presentation && <section className="review-main-grid">
      <div className="review-column">
        <RecognitionResultPanel data={turn.presentation} />
        <ReviewReasonPanel data={turn.presentation} />
      </div>
      <div className="review-column">
        <ReviewActionPanel
          candidates={turn.presentation?.review.candidate_interpretations || []}
          writable={controller.writable}
          action={submission.action}
          selectedCandidateId={submission.selectedCandidateId}
          correctedText={submission.correctedText}
          status={submission.status}
          error={submission.error}
          busy={submission.busy}
          cancellationConfirmationOpen={submission.cancellationConfirmationOpen}
          onActionChange={submission.setAction}
          onCandidateChange={submission.setSelectedCandidateId}
          onCorrectedTextChange={submission.setCorrectedText}
          onSubmit={submission.submit}
          onConfirmCancellation={submission.confirmCancellation}
          onCloseConfirmation={submission.closeConfirmation}
        />
        <ReviewResultPanel presentation={turn.presentation} result={submission.latestResult} />
      </div>
      <div className="review-column">
        <WorkflowStatusPanel workflow={turn.workflow} presentation={turn.presentation} />
        <AuthorizationPanel presentation={turn.presentation} workflow={turn.workflow} hasToken={execution.hasAuthorizationToken} />
        <ExecutionPanel
          presentation={turn.presentation}
          health={controller.health.data}
          eligibility={controller.executionEligibility}
          status={execution.status}
          error={execution.error}
          result={execution.result}
          busy={execution.busy}
          confirmationOpen={execution.confirmationOpen}
          onRequest={controller.requestExecution}
          onConfirm={controller.confirmExecution}
          onCancel={execution.closeConfirmation}
        />
        <WorkflowChainPanel data={controller.chain.data} loading={controller.chain.loading} error={controller.chain.error || turn.workflowError} verifiedAt={controller.chain.verifiedAt} onRefresh={() => { void controller.refreshChain(); }} />
      </div>
    </section>}
    {turn.presentation && <ReviewTimelinePanel data={controller.timeline.data} loading={controller.timeline.loading} error={controller.timeline.error} onRefresh={() => { void controller.refreshAll(); }} />}
  </div>;
}
