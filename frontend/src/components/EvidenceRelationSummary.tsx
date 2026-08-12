import type { EvidenceRelationItem, EvidenceRelationSummary as RelationSummary } from "../utils/evidenceLayerAdapter";

function RelationList({ title, items, tone, onSelectNode }: { title: string; items: EvidenceRelationItem[]; tone: string; onSelectNode: (nodeId: string) => void }) {
  return <section className={`evidence-relation-list ${tone}`}><h3>{title}</h3>{items.length ? <ul>{items.map((item) => <li key={item.id}>
    <div><button type="button" onClick={() => onSelectNode(item.sourceId)}>{item.sourceName}</button><span>→</span><button type="button" onClick={() => onSelectNode(item.targetId)}>{item.targetName}</button></div>
    <p>{item.reason}</p><small>权重：{Number.isFinite(item.weight) ? item.weight.toFixed(3) : "后端未提供"}</small>
  </li>)}</ul> : <p className="empty-copy">本轮无此类真实关系。</p>}</section>;
}

export function EvidenceRelationSummary({ data, onSelectNode }: { data: RelationSummary; onSelectNode: (nodeId: string) => void }) {
  const counts = [["支持", data.counts.supports], ["依赖", data.counts.requires], ["规则约束", data.counts.ruleConstrained], ["冲突", data.counts.conflicts], ["其他", data.counts.other]] as const;
  return <details className="evidence-relation-summary evidence-panel">
    <summary><span><strong>真实关系摘要</strong><small>只展开冲突与规则约束，不推导新的关系。</small></span><span className="relation-counts">{counts.map(([label, count]) => <i key={label}>{label} {count}</i>)}</span></summary>
    <div className="evidence-relation-grid"><RelationList title="冲突关系" items={data.conflicts} tone="danger" onSelectNode={onSelectNode} /><RelationList title="规则约束" items={data.ruleConstraints} tone="warning" onSelectNode={onSelectNode} /></div>
  </details>;
}
