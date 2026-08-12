import { MAX_CORRECTED_TEXT_LENGTH } from "../constants";
import type { ReviewAction, ReviewCandidate, ReviewSubmissionStatus } from "../types/contract";
import { ConfirmDialog } from "./ConfirmDialog";

interface Props {
  candidates: ReviewCandidate[];
  writable: boolean;
  action: ReviewAction;
  selectedCandidateId: string;
  correctedText: string;
  status: ReviewSubmissionStatus;
  error: string | null;
  busy: boolean;
  cancellationConfirmationOpen: boolean;
  onActionChange: (action: ReviewAction) => void;
  onCandidateChange: (candidateId: string) => void;
  onCorrectedTextChange: (text: string) => void;
  onSubmit: (action?: ReviewAction) => void;
  onConfirmCancellation: () => void;
  onCloseConfirmation: () => void;
}

const statusLabels: Record<ReviewSubmissionStatus, string> = {
  idle: "等待复核", validating: "正在校验", confirming: "等待确认", submitting: "正在提交",
  refreshing: "正在刷新后端状态", completed: "复核完成", failed: "复核未完成",
};

export function ReviewActionPanel(props: Props) {
  const validCandidates = props.candidates.filter((candidate) => candidate.validation_status === "VALID");
  const disabled = !props.writable || props.busy;
  const statusLabel = props.status === "idle" && !props.writable ? "只读" : statusLabels[props.status];
  return <section className="review-card review-action-card">
    <div className="card-heading"><div><span className="eyebrow">REVIEW ACTION</span><h2>人工复核操作</h2></div><span className={`submission-status submission-${props.status}`}>{statusLabel}</span></div>
    {!props.writable && <p className="notice-box">当前地址不是可写的最新待复核轮次，仅允许只读查看。</p>}
    <div className="review-action-tabs" role="tablist">
      {(["CONFIRM", "CORRECT", "CANCEL"] as const).map((action) => <button key={action} type="button" className={props.action === action ? "active" : ""} disabled={disabled} onClick={() => props.onActionChange(action)}>{action === "CONFIRM" ? "确认候选" : action === "CORRECT" ? "修正指令" : "取消操作"}</button>)}
    </div>
    {props.action === "CONFIRM" && <div className="candidate-command-list">
      {!validCandidates.length ? <p className="empty-copy">当前没有可确认候选；可改用修正指令或取消操作。</p> : validCandidates.map((candidate) => <label key={candidate.candidate_id} className={props.selectedCandidateId === candidate.candidate_id ? "selected" : ""}>
        <input type="radio" name="review-candidate" value={candidate.candidate_id} checked={props.selectedCandidateId === candidate.candidate_id} disabled={disabled} onChange={() => props.onCandidateChange(candidate.candidate_id)} />
        <span><strong>{candidate.canonical_text}</strong><small>{candidate.candidate_id}</small><em>{candidate.action} / {candidate.target} · {candidate.risk_level}</em><p>{candidate.why_possible}</p></span>
      </label>)}
    </div>}
    {props.action === "CORRECT" && <label className="correction-editor"><span>修正后的明确指令</span><textarea value={props.correctedText} maxLength={MAX_CORRECTED_TEXT_LENGTH} disabled={disabled} placeholder="输入后端应重新裁决的完整指令" onChange={(event) => props.onCorrectedTextChange(event.target.value)} /><small>{props.correctedText.length}/{MAX_CORRECTED_TEXT_LENGTH}</small></label>}
    {props.action === "CANCEL" && <p className="danger-notice">取消会终止本轮工作流，不会签发授权，也不会执行车辆动作。</p>}
    {props.error && <p className="inline-error" role="alert">{props.error}</p>}
    <button type="button" className={props.action === "CANCEL" ? "danger-button full-width" : "primary-button full-width"} disabled={disabled || (props.action === "CONFIRM" && !validCandidates.length)} onClick={() => props.onSubmit()}>{props.action === "CONFIRM" ? "提交候选确认" : props.action === "CORRECT" ? "提交修正并重新裁决" : "取消本轮操作"}</button>
    <ConfirmDialog open={props.cancellationConfirmationOpen} title="确认取消当前操作" confirmLabel="确认取消并终止" danger pending={props.status === "submitting"} onConfirm={props.onConfirmCancellation} onCancel={props.onCloseConfirmation}><p>取消成功后，本轮指令不会执行，且不能再次提交复核操作。</p></ConfirmDialog>
  </section>;
}
