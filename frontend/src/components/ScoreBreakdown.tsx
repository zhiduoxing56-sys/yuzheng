import type { TurnPresentationResponse } from "../types/contract";
import { formatPercent } from "../utils/formatters";

export function ScoreBreakdown({ data }: { data: TurnPresentationResponse | null }) {
  const metrics = data ? [
    ["语义清晰度", data.score_result.semantic_clarity, false],
    ["证据覆盖度", data.evidence.quality_metrics.ecr, false],
    ["证据可信度", data.score_result.evidence_trust, false],
    ["越狱风险", data.validation_result.jailbreak_risk, true],
    ["场景必要性", data.score_result.scene_necessity, false],
  ] as const : [];
  return <section className="detail-section"><div className="card-heading"><div><span className="eyebrow">SCORE</span><h2>五维评分</h2></div><small>后端返回值 · 0–1</small></div>
    {!data ? <p className="empty-copy">暂无评分数据</p> : <div className="score-list">{metrics.map(([label, value, risk]) => <div key={label} className={risk ? "risk-metric" : ""}><div><span>{label}</span><strong>{formatPercent(value)}</strong></div><progress max="1" value={value ?? 0} aria-label={label} /></div>)}</div>}
  </section>;
}
