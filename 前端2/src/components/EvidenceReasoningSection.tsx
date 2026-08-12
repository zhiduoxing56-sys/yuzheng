import { useState } from "react";
import { useEvidenceReasoning } from "../hooks/useEvidenceReasoning";
import { EvidenceReasoningPanel } from "./EvidenceReasoningPanel";

export function EvidenceReasoningSection({ turnId }: { turnId: string }) {
  const [expanded, setExpanded] = useState(false);
  const reasoning = useEvidenceReasoning(turnId, expanded);
  return <section className="collapsible-panel controlled-collapsible">
    <button type="button" aria-expanded={expanded} onClick={() => setExpanded((value) => !value)}>高级推理（展开后请求扩展接口）</button>
    {expanded && <div><EvidenceReasoningPanel data={reasoning.data} loading={reasoning.loading} error={reasoning.error} onRetry={reasoning.retry} /></div>}
  </section>;
}
