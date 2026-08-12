import type { FilteredEvidenceLayer } from "../utils/evidenceLayerAdapter";
import { EvidenceLayerSummary } from "./EvidenceLayerSummary";
import { EvidenceNodeTable } from "./EvidenceNodeTable";

interface Props { layer: FilteredEvidenceLayer; expanded: boolean; onToggle: () => void; onSelectNode: (nodeId: string) => void; }

export function EvidenceLayerSection({ layer, expanded, onToggle, onSelectNode }: Props) {
  const contentId = `evidence-layer-${layer.rank}`;
  return <section className={`evidence-layer-section layer-${layer.rank}`}>
    <button type="button" className="evidence-layer-toggle" aria-expanded={expanded} aria-controls={contentId} onClick={onToggle}>
      <EvidenceLayerSummary layer={layer} />
      <span className="evidence-layer-action">{expanded ? "收起" : "展开"}<i aria-hidden="true">⌄</i></span>
    </button>
    {expanded && <div id={contentId} className="evidence-layer-content"><div className="evidence-layer-visible-count">筛选后 {layer.visibleCount} 条 / 本层原始 {layer.originalCount} 条</div><EvidenceNodeTable nodes={layer.visibleNodes} onSelectNode={onSelectNode} /></div>}
  </section>;
}
