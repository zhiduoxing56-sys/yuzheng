import type { DecisionLabel, TurnPresentationResponse } from "../types/contract";
import { formatDateTime } from "../utils/formatters";

interface Props { data: TurnPresentationResponse | null; loading: boolean; processing: boolean; error: string | null; onRetry: () => void; }
interface DecisionCopy { label: string; description: string; tone: "pass" | "review" | "block"; }

const SCORE_ROWS = [
  { key: "C_sem", label: "语义清晰度", value: (data: TurnPresentationResponse) => data.score_result.semantic_clarity },
  { key: "C_cov", label: "证据覆盖度", value: (data: TurnPresentationResponse) => data.evidence.quality_metrics.ecr },
  { key: "C_trust", label: "证据可信度", value: (data: TurnPresentationResponse) => data.score_result.evidence_trust },
  { key: "C_jb", label: "越狱抑制能力", value: (data: TurnPresentationResponse) => data.score_result.jailbreak_suppression },
  { key: "C_nec", label: "场景必要性", value: (data: TurnPresentationResponse) => data.score_result.scene_necessity },
] as const;

function decisionCopy(value: DecisionLabel): DecisionCopy {
  if (value === "PASS") return { label: "通过", description: "指令通过安全审查，可执行", tone: "pass" };
  if (value === "REVIEW") return { label: "人工复核", description: "指令需要人工确认，暂不执行", tone: "review" };
  return { label: "拒绝", description: "指令未通过安全审查，已阻断", tone: "block" };
}

function percent(value?: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const normalized = value <= 1 ? value * 100 : value;
  return normalized.toFixed(1).replace(/\.0$/, "");
}

function GavelIcon() { return <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m14.5 5.5 4 4M6.8 13.2l4 4m-2.3-6.3 5.6-5.6 4.6 4.6-5.6 5.6-4.6-4.6ZM4 20h11M5.4 14.6l2.8 2.8-1.9 1.9-2.8-2.8 1.9-1.9Z" /></svg>; }
function ShieldIcon({ tone }: { tone: DecisionCopy["tone"] }) {
  return <svg viewBox="0 0 24 24" aria-hidden="true" className={`decision-shield-icon ${tone}`}><path d="M12 2.7 20 6v5.4c0 5.1-3.4 8.6-8 10-4.6-1.4-8-4.9-8-10V6l8-3.3Z" />{tone === "pass" ? <path d="m8.4 12 2.2 2.2 5-5" /> : tone === "review" ? <><path d="M12 8v5" /><path d="M12 16.5h.01" /></> : <path d="m9 9 6 6m0-6-6 6" />}</svg>;
}

export function SafetyDecisionPanel({ data, loading, processing, error, onRetry }: Props) {
  const result = data ? decisionCopy(data.decision_result.final_decision) : null;
  const reasons = data?.decision_result.reasons.filter(Boolean) || [];
  const summary = data?.decision_result.decision_explanation?.summary || data?.decision_result.explanation;
  return <section className="decision-surface safety-decision-card" aria-labelledby="safety-decision-title">
    <div className="decision-section-heading result-heading"><span className="decision-heading-icon solid"><GavelIcon /></span><h2 id="safety-decision-title">裁决结果</h2><time>{data ? formatDateTime(data.updated_at || data.created_at) : "等待裁决"}</time></div>
    {!data ? (error ? <div className="decision-result-empty error" role="alert"><strong>裁决结果读取失败</strong><p>{error}</p><button type="button" onClick={onRetry}>重新读取</button></div>
      : <div className={`decision-result-empty ${loading || processing ? "loading" : ""}`}><span><ShieldIcon tone="pass" /></span><strong>{loading || processing ? "正在进行安全裁决" : "等待真实裁决"}</strong><p>提交指令后，这里将展示后端持久化的最终裁决结果。</p></div>) : <>
      <div className={`decision-outcome-banner ${result!.tone}`}><ShieldIcon tone={result!.tone} /><div><strong>{result!.label}</strong><p>{result!.description}</p></div></div>
      <div className="decision-total-score"><span>裁决得分：</span><strong>{percent(data.decision_result.safety_score)} / 100</strong></div>
      <section className="decision-score-section" aria-labelledby="dimension-score-title"><h3 id="dimension-score-title">维度评分</h3><div className="decision-score-table-wrap"><table className="decision-score-table"><thead><tr><th>维度</th><th>得分</th><th>说明</th></tr></thead><tbody>{SCORE_ROWS.map((row) => <tr key={row.key}><td>{row.key}</td><td>{percent(row.value(data))}</td><td>{row.label}</td></tr>)}</tbody></table></div></section>
      <section className="decision-reason-section" aria-labelledby="decision-reason-title"><h3 id="decision-reason-title">具体原因</h3><div className={`decision-reason-box ${result!.tone}`}><span aria-hidden="true">{result!.tone === "pass" ? "✓" : result!.tone === "review" ? "!" : "×"}</span><div>{summary && <p>{summary}</p>}{reasons.length > 0 && <ul>{reasons.map((reason, index) => <li key={`${reason}-${index}`}>{reason}</li>)}</ul>}{!summary && reasons.length === 0 && <p>后端未返回补充说明。</p>}</div></div></section>
      <div className="decision-method-note"><span aria-hidden="true">i</span><p>系统基于后端返回的五维评分与安全门结果进行综合裁决，页面不使用示例数据。</p></div>
    </>}
  </section>;
}
