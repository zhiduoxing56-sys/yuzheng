import type { TurnPresentationResponse } from "../types/contract";

export function EvidenceDemandPanel({ data }: { data: TurnPresentationResponse | null }) {
  if (!data) return <section className="evidence-side-card"><h2>指令与证据需求</h2><p className="empty-copy">暂无轮次展示摘要，证据子图仍可独立加载。</p></section>;
  const demand = data.evidence_demand;
  return <section className="evidence-side-card">
    <h2>指令与证据需求</h2>
    <h3>子意图证据需求</h3>
    {demand.intent_demands.map((intent) => <article key={`${intent.clause_index}:${intent.intent_id}`}><p>{intent.clause_index}. {intent.intent_id} · {intent.action}/{intent.target} · {intent.risk_level}</p>
      {(intent.knowledge_augmented_types?.length || intent.knowledge_hits?.length) ? <div className="knowledge-augmented-block">
        {intent.knowledge_augmented_types?.length ? <p><strong>📚 知识库追加证据</strong>：{intent.knowledge_augmented_types.join("、")}</p> : null}
        {intent.knowledge_hits?.length ? <p><strong>命中知识</strong>：{intent.knowledge_hits.map((hit) => hit.title ?? hit.node_id).join("；")}</p> : null}
      </div> : null}
      <ul className="evidence-demand-list">{intent.demand_items.map((item) => <li key={`${intent.clause_index}:${item.evidence_type}:${item.required}`}>
      <div><strong>{item.evidence_type}</strong><span>{item.requirement_level === "KNOWLEDGE_REQUIRED" ? "知识检索·缺失需复核" : item.requirement_level === "ASSESSMENT" ? "评估佐证·影响评分" : item.required ? "硬前置·缺失拒绝" : "评估佐证"}</span></div>
      <small>{item.status} · {item.retrieval_origin}</small>
      <p>{item.reason}</p>
    </li>)}</ul></article>)}
    {!demand.intent_demands.length && <p className="empty-copy">后端未返回证据需求项。</p>}
  </section>;
}
