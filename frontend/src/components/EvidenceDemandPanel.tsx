import type { TurnPresentationResponse } from "../types/contract";

export function EvidenceDemandPanel({ data }: { data: TurnPresentationResponse | null }) {
  if (!data) return <section className="evidence-side-card"><h2>指令与证据需求</h2><p className="empty-copy">暂无轮次展示摘要，证据子图仍可独立加载。</p></section>;
  const demand = data.evidence_demand;
  return <section className="evidence-side-card">
    <h2>指令与证据需求</h2>
    <h3>子意图证据需求</h3>
    {demand.intent_demands.map((intent) => <article key={`${intent.clause_index}:${intent.intent_id}`}><p>{intent.clause_index}. {intent.intent_id} · {intent.action}/{intent.target} · {intent.risk_level}</p><ul className="evidence-demand-list">{intent.demand_items.map((item) => <li key={`${intent.clause_index}:${item.evidence_type}:${item.required}`}>
      <div><strong>{item.evidence_type}</strong><span>{item.required ? "必需" : "可选"}</span></div>
      <small>{item.status} · {item.retrieval_origin}</small>
      <p>{item.reason}</p>
    </li>)}</ul></article>)}
    {!demand.intent_demands.length && <p className="empty-copy">后端未返回证据需求项。</p>}
  </section>;
}
