import type { MouseEvent } from "react";
import type { ClarificationRequest } from "../types/contract";

interface Props {
  request: ClarificationRequest;
  submitting: boolean;
  error: string | null;
  onSelect: (candidateId: string) => void;
  onNoneOfAbove: () => void;
}

export function ClarificationModal({ request, submitting, error, onSelect, onNoneOfAbove }: Props) {
  const rejectFromBackdrop = (event: MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget && !submitting) onNoneOfAbove();
  };

  return <div
    className="clarification-modal-backdrop"
    data-testid="clarification-backdrop"
    onMouseDown={rejectFromBackdrop}
  >
    <section
      aria-busy={submitting}
      aria-describedby="clarification-prompt"
      aria-labelledby="clarification-title"
      aria-modal="true"
      className="clarification-modal"
      role="dialog"
    >
      <header>
        <span>REVIEW CLARIFICATION</span>
        <h2 id="clarification-title">需要确认</h2>
        <p id="clarification-prompt">{request.prompt}</p>
      </header>
      {request.candidates.length ? <div className="clarification-candidates">
        {request.candidates.slice(0, 4).map((candidate) => <button
          className="clarification-candidate"
          disabled={submitting}
          key={candidate.candidate_id}
          onClick={() => onSelect(candidate.candidate_id)}
          type="button"
        ><span aria-hidden="true" />{candidate.display_text}</button>)}
      </div> : <p className="clarification-empty">暂未找到可靠候选，请重新说一次</p>}
      {error ? <p className="clarification-error" role="alert">{error}</p> : null}
      <button
        className="clarification-none"
        disabled={submitting}
        onClick={onNoneOfAbove}
        type="button"
      >{submitting ? "正在提交…" : "都不是，再说一次"}</button>
    </section>
  </div>;
}
