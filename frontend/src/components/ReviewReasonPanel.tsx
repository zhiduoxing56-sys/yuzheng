import type { TurnPresentationResponse } from "../types/contract";

export function ReviewReasonPanel({ data }: { data: TurnPresentationResponse | null }) {
  const review = data?.review;
  const reasons = data?.decision_result.reasons || [];
  return <section className="review-card">
    <span className="eyebrow">REVIEW REASON</span><h2>进入复核原因</h2>
    {!review ? <p className="empty-copy">暂无复核信息。</p> : <>
      <p className="review-question">{review.review_question || "后端未提供详细复核原因"}</p>
      {review.recommended_recovery?.message && <p className="notice-box">后端建议：{review.recommended_recovery.message}</p>}
      <dl className="review-fact-grid compact-grid">
        <div><dt>复核状态</dt><dd>{review.status}</dd></div>
        <div><dt>歧义字段</dt><dd>{review.ambiguity_field || "未提供"}</dd></div>
        <div><dt>支持证据</dt><dd>{review.supporting_evidence.length}</dd></div>
        <div><dt>冲突证据</dt><dd>{review.conflicting_evidence.length}</dd></div>
      </dl>
      {reasons.length ? <details className="audit-raw-details"><summary>技术原因详情</summary><ul className="review-reason-list">{reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></details> : <p className="empty-copy">后端未提供裁决原因列表。</p>}
    </>}
  </section>;
}
