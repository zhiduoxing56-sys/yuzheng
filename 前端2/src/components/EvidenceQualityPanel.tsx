import type { EvidenceSubgraph, TurnPresentationResponse } from "../types/contract";
import { formatPercent } from "../utils/formatters";

interface Props { graph: EvidenceSubgraph | null; presentation: TurnPresentationResponse | null; }

export function EvidenceQualityPanel({ graph, presentation }: Props) {
  const quality = graph?.quality_metrics;
  const memory = presentation?.evidence.memory;
  const causal = presentation?.evidence.causal;
  return <div className="evidence-bottom-grid">
    <section><h3>证据质量</h3>{quality ? <dl className="quality-summary-grid">
      <div><dt>ECR</dt><dd>{quality.ecr === null ? "不适用" : formatPercent(quality.ecr)}</dd></div>
      <div><dt>ECS</dt><dd>{formatPercent(quality.ecs)}</dd></div>
      <div><dt>EF</dt><dd>{formatPercent(quality.ef)}</dd></div>
      <div><dt>SAS</dt><dd>{formatPercent(quality.sas)}</dd></div>
      <div><dt>EAS</dt><dd>{formatPercent(quality.eas)}</dd></div>
      <div><dt>冲突数</dt><dd>{quality.conflict_count}</dd></div>
    </dl> : <p className="empty-copy">后端未返回质量指标。</p>}</section>
    <section><h3>记忆支持</h3>{memory && Object.keys(memory).length ? <pre>{JSON.stringify(memory, null, 2)}</pre> : <p className="empty-copy">暂无记忆信息。</p>}</section>
    <section><h3>因果信息</h3>{causal && Object.keys(causal).length ? <pre>{JSON.stringify(causal, null, 2)}</pre> : <p className="empty-copy">暂无因果信息。</p>}</section>
  </div>;
}
