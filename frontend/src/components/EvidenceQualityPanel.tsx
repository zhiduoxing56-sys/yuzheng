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
    <section><h3>因果修正</h3>{causal?.node_weights.length ? <>
      <p className="empty-copy">确定性领域支持 · 不使用历史学习 · 模型 {causal.model_build_id || "暂无"} · 节点图权重 {causal.corrected_weights_projection}</p>
      <ul className="plain-detail-list">{causal.node_weights.map((weight) => {
        const component = causal.prior_components.find((item) => item.node_id === weight.node_id && item.clause_index === weight.clause_index && item.intent_id === weight.intent_id);
        return <li key={`${weight.clause_index}:${weight.intent_id}:${weight.node_id}`}>
          <strong>{weight.clause_index}:{weight.intent_id}</strong> → {weight.causal_variable} ({weight.node_id})
          <br />binding {formatPercent(component?.binding_similarity ?? null)} · memory {formatPercent(component?.memory_initial_confidence ?? null)} → {formatPercent(component?.layer_confidence_component ?? null)}
          <br />freshness {formatPercent(component?.freshness_component ?? null)} · availability {formatPercent(component?.availability_component ?? null)} · {component?.requirement_level || "UNKNOWN"}
          <br />support {formatPercent(weight.causal_support)} · prior {formatPercent(weight.prior_probability)} · corrected {formatPercent(weight.corrected_weight)}
        </li>;
      })}</ul>
    </> : <p className="empty-copy">暂无因果信息。</p>}</section>
  </div>;
}
