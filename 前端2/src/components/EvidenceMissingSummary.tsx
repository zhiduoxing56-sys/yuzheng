import type { EvidenceMissingItem } from "../utils/evidenceLayerAdapter";

export function EvidenceMissingSummary({ items }: { items: EvidenceMissingItem[] }) {
  return <section className={`evidence-missing-summary evidence-panel ${items.length ? "has-missing" : ""}`}>
    <div className="card-heading"><div><span className="eyebrow">MISSING EVIDENCE</span><h2>缺失证据摘要</h2></div><strong>{items.length}</strong></div>
    {items.length ? <div className="evidence-missing-list">{items.map((item) => <article key={item.evidenceType}><div><strong>{item.evidenceType}</strong>{item.mandatory && <span>必查</span>}</div><p>{item.reason}</p><small>裁决影响：{item.decisionImpact}</small></article>)}</div> : <p className="empty-copy">后端未报告缺失证据类型。</p>}
  </section>;
}
