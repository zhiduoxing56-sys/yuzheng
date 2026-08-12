import { useEffect, useState } from "react";
import type { FilteredEvidenceLayer } from "../utils/evidenceLayerAdapter";
import { EvidenceLayerSection } from "./EvidenceLayerSection";

export function EvidenceLayerStack({ turnId, layers, onSelectNode }: { turnId: string; layers: FilteredEvidenceLayer[]; onSelectNode: (nodeId: string) => void }) {
  const [expanded, setExpanded] = useState<Set<number>>(() => new Set());
  useEffect(() => setExpanded(new Set()), [turnId]);
  return <section className="evidence-layer-stack" aria-label="四层证据列表">{layers.map((layer) => <EvidenceLayerSection key={layer.rank} layer={layer} expanded={expanded.has(layer.rank)} onSelectNode={onSelectNode} onToggle={() => setExpanded((current) => {
    const next = new Set(current);
    if (next.has(layer.rank)) next.delete(layer.rank); else next.add(layer.rank);
    return next;
  })} />)}</section>;
}
