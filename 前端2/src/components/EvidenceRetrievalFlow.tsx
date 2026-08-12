import type { EvidenceRetrievalFlowData } from "../utils/evidenceLayerAdapter";

export function EvidenceRetrievalFlow({ data }: { data: EvidenceRetrievalFlowData }) {
  const steps = [
    ["语义候选", data.candidateCount],
    ["最终 TopK", data.topKCount],
    ["强制补召", data.mandatorySupplementCount],
    ["四层证据", data.nodeCount],
  ] as const;
  return <section className="evidence-retrieval-flow evidence-panel">
    <div className="card-heading"><div><span className="eyebrow">RETRIEVAL FLOW</span><h2>本轮检索流程</h2></div>{data.degraded && <span className="evidence-warning-badge">已降级</span>}</div>
    <div className="retrieval-flow-steps">{steps.map(([label, value], index) => <div key={label} className="retrieval-flow-step"><span>{label}</span><strong>{value}</strong>{index < steps.length - 1 && <i aria-hidden="true">→</i>}</div>)}</div>
    <dl className="retrieval-flow-meta">
      <div><dt>缺失类型</dt><dd>{data.missingTypeCount}</dd></div>
      <div><dt>真实关系</dt><dd>{data.edgeCount}</dd></div>
      <div><dt>检索耗时</dt><dd>{data.durationMs === null ? "后端未提供" : `${data.durationMs.toFixed(2)} ms`}</dd></div>
      <div><dt>实现</dt><dd>{data.implementation || "后端未提供"}</dd></div>
    </dl>
    {data.degraded && <p className="evidence-degraded-note">{data.degradationReason || "后端未提供降级原因"}</p>}
  </section>;
}
