import { useMemo, useState } from "react";
import type { MouseEvent } from "react";
import type { ClarificationCandidate, ClarificationRequest } from "../types/contract";

interface Props {
  request: ClarificationRequest;
  submitting: boolean;
  error: string | null;
  onSelect: (candidateIds: string[]) => void;
  onNoneOfAbove: () => void;
}

export function ClarificationModal({ request, submitting, error, onSelect, onNoneOfAbove }: Props) {
  const [selected, setSelected] = useState<Record<string, string>>({});
  const rejectFromBackdrop = (event: MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget && !submitting) onNoneOfAbove();
  };

  // 分组候选：candidate.group 非空 → 按 group 分组展示（多意图复核）
  const groups = useMemo(() => {
    const map = new Map<string, { label: string; candidates: ClarificationCandidate[] }>();
    for (const candidate of request.candidates) {
      if (candidate.group) {
        const entry = map.get(candidate.group) ?? {
          label: candidate.group_label ?? candidate.group,
          candidates: [],
        };
        entry.candidates.push(candidate);
        map.set(candidate.group, entry);
      }
    }
    return [...map.entries()].map(([group, entry]) => ({ group, ...entry }));
  }, [request.candidates]);

  const hasGroups = groups.length > 0;
  const allSelected = hasGroups && groups.every((g) => Boolean(selected[g.group]));
  const confirmGrouped = () => {
    if (!allSelected) return;
    const ids = groups.map((g) => selected[g.group]).filter(Boolean) as string[];
    onSelect(ids);
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
      {hasGroups ? <div className="clarification-groups">
        {groups.map((g) => <div className="clarification-group" key={g.group}>
          <div className="clarification-group-label">{g.label}</div>
          <div className="clarification-candidates">
            {g.candidates.slice(0, 4).map((candidate) => <button
              className={`clarification-candidate${selected[g.group] === candidate.candidate_id ? " is-selected" : ""}`}
              disabled={submitting}
              key={candidate.candidate_id}
              onClick={() => setSelected((prev) => ({ ...prev, [g.group]: candidate.candidate_id }))}
              type="button"
            ><span aria-hidden="true" />{candidate.display_text}</button>)}
          </div>
        </div>)}
        <button
          className="clarification-none"
          disabled={submitting || !allSelected}
          onClick={confirmGrouped}
          type="button"
        >{submitting ? "正在提交…" : allSelected ? "确认选择" : "请为每个操作选择一个选项"}</button>
        <button
          className="clarification-none"
          disabled={submitting}
          onClick={onNoneOfAbove}
          type="button"
        >都不是，再说一次</button>
      </div> : request.candidates.length ? <div className="clarification-candidates">
        {request.candidates.slice(0, 4).map((candidate) => <button
          className="clarification-candidate"
          disabled={submitting}
          key={candidate.candidate_id}
          onClick={() => onSelect([candidate.candidate_id])}
          type="button"
        ><span aria-hidden="true" />{candidate.display_text}</button>)}
      </div> : <p className="clarification-empty">暂未找到可靠候选，请重新说一次</p>}
      {error ? <p className="clarification-error" role="alert">{error}</p> : null}
      {!hasGroups ? <button
        className="clarification-none"
        disabled={submitting}
        onClick={onNoneOfAbove}
        type="button"
      >{submitting ? "正在提交…" : "都不是，再说一次"}</button> : null}
    </section>
  </div>;
}
