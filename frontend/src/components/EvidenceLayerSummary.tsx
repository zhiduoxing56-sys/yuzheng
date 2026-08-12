import type { AdaptedEvidenceLayer } from "../utils/evidenceLayerAdapter";

export function EvidenceLayerSummary({ layer }: { layer: AdaptedEvidenceLayer }) {
  const stats = [
    ["命中", layer.stats.hitCount, ""], ["TopK", layer.stats.topKCount, ""], ["强制补召", layer.stats.mandatorySupplementCount, "accent"],
    ["关键", layer.stats.criticalCount, ""], ["异常", layer.stats.abnormalCount, "warning"], ["冲突节点", layer.stats.conflictNodeCount, "danger"],
  ] as const;
  return <div className="evidence-layer-summary">
    <div className="evidence-layer-copy"><span className="evidence-layer-index">L{layer.rank}</span><div><h2>{layer.name}</h2><p>{layer.description}</p></div></div>
    <div className="evidence-layer-stats">{stats.map(([label, value, tone]) => <span key={label} className={tone}><small>{label}</small><strong>{value}</strong></span>)}</div>
    <div className="evidence-layer-previews">{layer.previews.length ? layer.previews.map((node) => <span key={node.id} title={node.name}>{node.name}</span>) : <span className="empty">本层暂无证据</span>}</div>
  </div>;
}
